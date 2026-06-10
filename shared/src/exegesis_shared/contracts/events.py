from __future__ import annotations

from copy import deepcopy
import json
from typing import Any, Callable, Literal

from exegesis_shared.contracts.actions import (
    ACTION_SELECTION_CONTRACT_VERSION,
    ALLOWED_ACTION_IDS,
    PATCH_DECISION_CONTRACT_VERSION,
    PATCH_PREVIEW_CONTRACT_VERSION,
    PATCH_REVIEW_ACTION_AUTHORITY,
    PATCH_REVIEW_DECISION_GROUP,
    PATCH_REVIEW_DEMO_PATH_STEP,
    PATCH_REVIEW_EXECUTION_POLICY,
    ActionRef,
    PolicyGate,
    action_ref_from_selection,
    advance_patch_review_state,
    advance_patch_review_state_typed,
    build_complete_patch_review_contract,
    build_patch_review_selection,
    execute_action_with_policy_gate,
    is_policy_sensitive_action,
    patch_review_resolved_status,
)
from exegesis_shared.contracts.cards import (
    A2UICapabilities,
    GENERIC_CARD_TYPE,
    PROPOSED_EDIT_CARD_TYPE,
    PatchReviewExecutionOutcome,
    UNKNOWN_CARD_TYPE,
    engine_prepare_card,
    materialize_cli_fallback_card,
    validate_card_payload_size,
)
from exegesis_shared.models.engine_loop_outcome import ContextBasketOutcome, EngineLoopOutcome
from exegesis_shared.models.patch_review_state import PatchReviewState

A2UI_EVENT_CONTRACT_VERSION = 1
A2UI_STREAM_EVENT_TYPES: tuple[str, ...] = (
    "card_published",
    "action_selected",
    "action_resolved",
)
_A2UI_STREAM_EVENT_SET = set(A2UI_STREAM_EVENT_TYPES)
_ALLOWED_ACTION_SET = set(ALLOWED_ACTION_IDS)
_BASE_EVENT_FIELDS: frozenset[str] = frozenset(
    {"contract_version", "event_id", "run_id", "sequence", "event_type"}
)
_EVENT_FIELDS_BY_TYPE: dict[str, frozenset[str]] = {
    "card_published": _BASE_EVENT_FIELDS | {"card"},
    "action_selected": _BASE_EVENT_FIELDS | {"action_id", "selection"},
    "action_resolved": _BASE_EVENT_FIELDS | {"action_id", "status", "selection", "message"},
}
_PATCH_PREVIEW_SELECTION_FIELDS: frozenset[str] = frozenset(
    {
        "contract_version",
        "selection_model",
        "slot",
        "action_identity",
        "action_authority",
        "demo_path_step",
        "execution_policy",
        "patch_preview_contract_version",
        "patch_id",
    }
)
_PATCH_DECISION_SELECTION_FIELDS: frozenset[str] = frozenset(
    {
        "contract_version",
        "selection_model",
        "slot",
        "action_identity",
        "action_authority",
        "demo_path_step",
        "execution_policy",
        "patch_decision_contract_version",
        "decision_group",
        "patch_decision",
        "patch_id",
    }
)
_ACTION_SELECTION_FIELDS: frozenset[str] = frozenset(
    {"contract_version", "selection_model", "slot", "action_identity"}
)
_PATCH_REVIEW_METADATA_FIELDS: frozenset[str] = (
    _PATCH_PREVIEW_SELECTION_FIELDS | _PATCH_DECISION_SELECTION_FIELDS
) - _ACTION_SELECTION_FIELDS


def build_card_published_event(
    *,
    event_id: str,
    run_id: str,
    sequence: int,
    card: dict[str, Any],
    capabilities: A2UICapabilities,
) -> dict[str, Any]:
    if not isinstance(card, dict):
        raise ValueError("card must be a dictionary")
    prepared_card = materialize_cli_fallback_card(engine_prepare_card(card, capabilities))
    event = _base_event(event_id=event_id, run_id=run_id, sequence=sequence, event_type="card_published")
    event["card"] = prepared_card
    validate_stream_event(event, capabilities)
    return event


def build_action_selected_event(
    *,
    event_id: str,
    run_id: str,
    sequence: int,
    selection: dict[str, Any],
    action_id: str,
    capabilities: A2UICapabilities | None = None,
) -> dict[str, Any]:
    if not isinstance(selection, dict):
        raise ValueError("action selection must be an object")
    event = _base_event(event_id=event_id, run_id=run_id, sequence=sequence, event_type="action_selected")
    event["action_id"] = action_id
    event["selection"] = deepcopy(selection)
    validate_stream_event(event, capabilities)
    return event


def build_action_selected_event_from_selection(
    *,
    event_id: str,
    run_id: str,
    sequence: int,
    card: dict[str, Any],
    selection: dict[str, Any],
    capabilities: A2UICapabilities | None = None,
) -> dict[str, Any]:
    if not isinstance(card, dict):
        raise ValueError("card must be a dictionary")
    if not isinstance(selection, dict):
        raise ValueError("action selection must be an object")
    action = action_ref_from_selection(card, selection)
    return build_action_selected_event(
        event_id=event_id,
        run_id=run_id,
        sequence=sequence,
        action_id=action.id,
        selection=selection,
        capabilities=capabilities,
    )


def build_complete_patch_review_action_selected_event(
    *,
    event_id: str,
    run_id: str,
    sequence: int,
    card: dict[str, Any],
    patch_id: str,
    control: str,
    capabilities: A2UICapabilities | None = None,
) -> dict[str, Any]:
    if not isinstance(card, dict):
        raise ValueError("card must be a dictionary")
    review = build_complete_patch_review_contract(card, patch_id=patch_id)
    selection = build_patch_review_selection(
        card,
        review,
        patch_id=patch_id,
        control=control,
    )
    return build_action_selected_event_from_selection(
        event_id=event_id,
        run_id=run_id,
        sequence=sequence,
        card=card,
        selection=selection,
        capabilities=capabilities,
    )


def build_complete_patch_review_action_resolved_event(
    *,
    event_id: str,
    run_id: str,
    sequence: int,
    card: dict[str, Any],
    patch_id: str,
    control: str,
    status: str | None = None,
    message: str | None = None,
    capabilities: A2UICapabilities | None = None,
) -> dict[str, Any]:
    if not isinstance(card, dict):
        raise ValueError("card must be a dictionary")
    review = build_complete_patch_review_contract(card, patch_id=patch_id)
    normalized_control = control.strip().lower()
    if normalized_control not in {"preview", "apply", "reject"}:
        raise ValueError("Patch review control must be 'preview', 'apply', or 'reject'")
    selection = build_patch_review_selection(
        card,
        review,
        patch_id=patch_id,
        control=normalized_control,
    )
    _TERMINAL_OVERRIDE_STATUSES: frozenset[str] = frozenset({"blocked", "failed"})
    expected_status = patch_review_resolved_status(normalized_control)
    resolved_status = status or expected_status
    if resolved_status not in _TERMINAL_OVERRIDE_STATUSES and resolved_status != expected_status:
        raise ValueError("Patch review resolved status does not match the selected control")
    return build_action_resolved_event_from_selection(
        event_id=event_id,
        run_id=run_id,
        sequence=sequence,
        card=card,
        selection=selection,
        status=resolved_status,
        message=message,
        capabilities=capabilities,
    )


def build_complete_patch_review_action_resolved_event_from_outcome(
    *,
    event_id: str,
    run_id: str,
    sequence: int,
    card: dict[str, Any],
    outcome: PatchReviewExecutionOutcome,
    message: str | None = None,
    capabilities: A2UICapabilities | None = None,
) -> dict[str, Any]:
    """Build an action_resolved event directly from a PatchReviewExecutionOutcome.

    Convenience builder for callers that already hold an outcome from
    execute_complete_patch_review_action_and_advance_state and don't want to
    re-extract patch_id, control, and status fields separately.
    """
    return build_complete_patch_review_action_resolved_event(
        event_id=event_id,
        run_id=run_id,
        sequence=sequence,
        card=card,
        patch_id=outcome.patch_id,
        control=outcome.control,
        status=outcome.status,
        message=message,
        capabilities=capabilities,
    )


def build_patch_review_action_resolved_event_from_outcome(
    *,
    event_id: str,
    run_id: str,
    sequence: int,
    outcome: PatchReviewExecutionOutcome,
    message: str | None = None,
    capabilities: A2UICapabilities | None = None,
) -> dict[str, Any]:
    """Build an action_resolved event from a basic PatchReviewExecutionOutcome.

    Convenience builder for the basic ``execute_patch_review_action_and_advance_state``
    flow.  Unlike the ``complete`` variant, no ``card`` argument is needed because the
    basic path does not require reconstructing a full selection envelope — the engine
    loop emits the event using the outcome's own patch_id, control, and status fields.
    """
    _control_to_action_id = {
        "preview": "preview_patch",
        "apply": "apply_patch",
        "reject": "reject_patch",
    }
    action_id = _control_to_action_id.get(outcome.control)
    if action_id is None:
        raise ValueError(
            f"PatchReviewExecutionOutcome.control must be one of "
            f"{sorted(_control_to_action_id)!r}, got {outcome.control!r}"
        )
    return build_action_resolved_event(
        event_id=event_id,
        run_id=run_id,
        sequence=sequence,
        action_id=action_id,
        status=outcome.status,
        message=message,
        capabilities=capabilities,
    )


def build_patch_review_action_selected_event(
    *,
    event_id: str,
    run_id: str,
    sequence: int,
    patch_id: str,
    control: str,
    capabilities: A2UICapabilities | None = None,
) -> dict[str, Any]:
    """Build an action_selected event for the basic patch review path.

    Convenience builder symmetric with
    ``build_patch_review_action_resolved_event_from_outcome``.  No ``card``
    argument is needed; the selection envelope is a minimal generic action
    selection that encodes the patch_id and control via action_identity so
    the engine loop can correlate the selection with its prior card_published
    event without requiring the full card to be re-passed.
    """
    _control_to_action_id = {
        "preview": "preview_patch",
        "apply": "apply_patch",
        "reject": "reject_patch",
    }
    action_id = _control_to_action_id.get(control)
    if action_id is None:
        raise ValueError(
            f"control must be one of {sorted(_control_to_action_id)!r}, got {control!r}"
        )
    if not isinstance(patch_id, str) or not patch_id.strip():
        raise ValueError("patch_id is required")
    action_identity = json.dumps(
        {"id": action_id, "patch_id": patch_id, "control": control},
        sort_keys=True,
        separators=(",", ":"),
    )
    selection = {
        "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
        "selection_model": "one_based_action_slot",
        "slot": 1,
        "action_identity": action_identity,
    }
    return build_action_selected_event(
        event_id=event_id,
        run_id=run_id,
        sequence=sequence,
        action_id=action_id,
        selection=selection,
        capabilities=capabilities,
    )


def build_action_resolved_event(
    *,
    event_id: str,
    run_id: str,
    sequence: int,
    action_id: str,
    status: str,
    selection: dict[str, Any] | None = None,
    message: str | None = None,
    capabilities: A2UICapabilities | None = None,
) -> dict[str, Any]:
    if selection is not None and not isinstance(selection, dict):
        raise ValueError("action selection must be an object")
    event = _base_event(event_id=event_id, run_id=run_id, sequence=sequence, event_type="action_resolved")
    event["action_id"] = action_id
    event["status"] = status
    if selection is not None:
        event["selection"] = deepcopy(selection)
    if message is not None:
        event["message"] = message
    validate_stream_event(event, capabilities)
    return event


def build_action_resolved_event_from_selection(
    *,
    event_id: str,
    run_id: str,
    sequence: int,
    card: dict[str, Any],
    selection: dict[str, Any],
    status: str,
    message: str | None = None,
    capabilities: A2UICapabilities | None = None,
) -> dict[str, Any]:
    if not isinstance(card, dict):
        raise ValueError("card must be a dictionary")
    if not isinstance(selection, dict):
        raise ValueError("action selection must be an object")
    action = action_ref_from_selection(card, selection)
    return build_action_resolved_event(
        event_id=event_id,
        run_id=run_id,
        sequence=sequence,
        action_id=action.id,
        status=status,
        selection=selection,
        message=message,
        capabilities=capabilities,
    )


def validate_stream_event(
    event: dict[str, Any],
    capabilities: A2UICapabilities | None = None,
) -> None:
    if not isinstance(event, dict):
        raise ValueError("A2UI stream event must be an object")
    event_ver = event.get("contract_version")
    if event_ver != A2UI_EVENT_CONTRACT_VERSION or isinstance(event_ver, bool):
        raise ValueError("Unsupported A2UI stream event contract version")
    event_type = event.get("event_type")
    if event_type not in _A2UI_STREAM_EVENT_SET:
        raise ValueError(f"Unsupported A2UI stream event type: {event_type}")
    _validate_event_fields(event, str(event_type))
    _validate_required_text(event, "event_id")
    _validate_required_text(event, "run_id")
    sequence = event.get("sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        raise ValueError("A2UI stream event sequence must be a positive integer")
    if capabilities is not None and not capabilities.supports_streaming:
        raise ValueError("Client does not support A2UI streaming events")

    if event_type == "card_published":
        card = event.get("card")
        if not isinstance(card, dict):
            raise ValueError("card_published event requires a card object")
        card_type = card.get("type")
        if not isinstance(card_type, str) or not card_type.strip():
            raise ValueError("card_published event card must have a non-empty type")
        card_title = card.get("title")
        if not isinstance(card_title, str) or not card_title.strip():
            raise ValueError("card_published event card must have a non-empty title")
        if card_type == PROPOSED_EDIT_CARD_TYPE:
            patch_id = card.get("patch_id")
            if not isinstance(patch_id, str) or not patch_id.strip():
                raise ValueError(
                    "card_published event ProposedEditCard must have a non-empty patch_id"
                )
            if patch_id != patch_id.strip():
                raise ValueError(
                    "card_published event ProposedEditCard patch_id must be normalized"
                )
        if capabilities is not None:
            validate_card_payload_size(card, capabilities)
            if card_type not in {UNKNOWN_CARD_TYPE, GENERIC_CARD_TYPE} and not capabilities.supports_card(card_type):
                raise ValueError(f"Client does not support card type: {card_type}")
        return
    if event_type == "action_selected":
        _validate_required_text(event, "action_id")
        action_id = _validate_action_id(event, capabilities)
        selection = event.get("selection")
        if not isinstance(selection, dict):
            raise ValueError("action_selected event requires a selection object")
        _validate_action_selection(selection, action_id)
        return
    if event_type == "action_resolved":
        _validate_required_text(event, "action_id")
        action_id = _validate_action_id(event, capabilities)
        status = event.get("status")
        if status not in {"previewed", "applied", "rejected", "completed", "blocked", "failed"}:
            raise ValueError("Unsupported action_resolved status")
        _validate_action_resolved_status_for_action(action_id, str(status))
        message = event.get("message")
        if message is not None:
            if not isinstance(message, str) or not message.strip():
                raise ValueError("action_resolved event message must be a non-empty string")
            if message != message.strip():
                raise ValueError("action_resolved event message must be normalized")
        selection = event.get("selection")
        if selection is not None:
            if not isinstance(selection, dict):
                raise ValueError("action_resolved event selection must be an object")
            _validate_action_selection(selection, action_id)


def _base_event(*, event_id: str, run_id: str, sequence: int, event_type: str) -> dict[str, Any]:
    return {
        "contract_version": A2UI_EVENT_CONTRACT_VERSION,
        "event_id": event_id,
        "run_id": run_id,
        "sequence": sequence,
        "event_type": event_type,
    }


def _validate_required_text(event: dict[str, Any], key: str) -> None:
    value = event.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"A2UI stream event {key} is required")
    if value != value.strip():
        formatted_key = key.replace("_", " ")
        raise ValueError(f"A2UI stream event {formatted_key} must be normalized")


def _validate_event_fields(event: dict[str, Any], event_type: str) -> None:
    allowed_fields = _EVENT_FIELDS_BY_TYPE[event_type]
    unexpected_fields = set(event) - allowed_fields
    if unexpected_fields:
        field_list = ", ".join(sorted(unexpected_fields))
        raise ValueError(f"Unsupported A2UI stream event field(s): {field_list}")


def _validate_action_id(event: dict[str, Any], capabilities: A2UICapabilities | None) -> str:
    raw_action_id = str(event.get("action_id", ""))
    action_id = raw_action_id.strip()
    if raw_action_id != action_id:
        raise ValueError("A2UI stream event action id must be normalized")
    if action_id not in _ALLOWED_ACTION_SET:
        raise ValueError(f"Unsupported A2UI stream event action id: {action_id}")
    if capabilities is not None and not capabilities.supports_action(action_id):
        raise ValueError(f"Client does not support A2UI stream event action id: {action_id}")
    return action_id


CONTEXT_BASKET_ACTION_IDS: frozenset[str] = frozenset(
    {"promote_to_basket", "pin_to_context_set", "create_context_set", "gather_context"}
)
_CONTEXT_BASKET_ACTION_IDS = CONTEXT_BASKET_ACTION_IDS


def _validate_action_resolved_status_for_action(action_id: str, status: str) -> None:
    if status in {"blocked", "failed"}:
        return
    patch_review_expected: dict[str, str] = {
        "preview_patch": "previewed",
        "apply_patch": "applied",
        "reject_patch": "rejected",
    }
    expected_patch_status = patch_review_expected.get(action_id)
    if expected_patch_status is not None and status != expected_patch_status:
        raise ValueError("Patch review resolved status does not match action id")
    if action_id in _CONTEXT_BASKET_ACTION_IDS and status != "completed":
        raise ValueError("Context and basket action resolved status must be 'completed'")
    if action_id not in patch_review_expected and action_id not in _CONTEXT_BASKET_ACTION_IDS:
        if status != "completed":
            raise ValueError(f"Generic action resolved status must be 'completed', got: {status!r}")


def _validate_action_selection(selection: dict[str, Any], action_id: str) -> None:
    contract_ver = selection.get("contract_version")
    if contract_ver != ACTION_SELECTION_CONTRACT_VERSION or isinstance(contract_ver, bool):
        raise ValueError("Unsupported action selection contract version")
    if selection.get("selection_model") != "one_based_action_slot":
        raise ValueError("Unsupported action selection model")
    slot = selection.get("slot")
    if not isinstance(slot, int) or isinstance(slot, bool) or slot < 1:
        raise ValueError("Action selection slot must be a positive integer")
    action_identity = selection.get("action_identity")
    if not isinstance(action_identity, str) or not action_identity.strip():
        raise ValueError("Action selection identity is required")
    if action_identity != action_identity.strip():
        raise ValueError("Action selection identity must be normalized")

    patch_decision = selection.get("patch_decision")
    if patch_decision is not None:
        _validate_selection_fields(
            selection,
            _PATCH_DECISION_SELECTION_FIELDS,
            "patch decision selection",
        )
        patch_id = selection.get("patch_id")
        if not isinstance(patch_id, str) or not patch_id.strip():
            raise ValueError("Patch review selection patch_id is required")
        if patch_id != patch_id.strip():
            raise ValueError("Patch review selection patch_id must be normalized")
        if selection.get("action_authority") != PATCH_REVIEW_ACTION_AUTHORITY:
            raise ValueError("Patch review selection must be engine-authoritative")
        if selection.get("demo_path_step") != PATCH_REVIEW_DEMO_PATH_STEP:
            raise ValueError("Patch review selection does not match the demo path step")
        decision_ver = selection.get("patch_decision_contract_version")
        if decision_ver != PATCH_DECISION_CONTRACT_VERSION or isinstance(decision_ver, bool):
            raise ValueError("Unsupported patch decision selection contract version")
        if selection.get("decision_group") != PATCH_REVIEW_DECISION_GROUP:
            raise ValueError("Patch decision selection does not match the decision group")
        expected_action_id = {"apply": "apply_patch", "reject": "reject_patch"}.get(str(patch_decision))
        if expected_action_id is None:
            raise ValueError("Unsupported patch decision selection")
        if action_id != expected_action_id:
            raise ValueError("Action id does not match patch decision selection")
        expected_policy = PATCH_REVIEW_EXECUTION_POLICY[str(patch_decision)]
        if selection.get("execution_policy") != expected_policy:
            raise ValueError("Patch review selection execution policy does not match engine policy")
        return

    if "patch_preview_contract_version" in selection:
        _validate_selection_fields(
            selection,
            _PATCH_PREVIEW_SELECTION_FIELDS,
            "patch preview selection",
        )
        patch_id = selection.get("patch_id")
        if not isinstance(patch_id, str) or not patch_id.strip():
            raise ValueError("Patch review selection patch_id is required")
        if patch_id != patch_id.strip():
            raise ValueError("Patch review selection patch_id must be normalized")
        if selection.get("action_authority") != PATCH_REVIEW_ACTION_AUTHORITY:
            raise ValueError("Patch review selection must be engine-authoritative")
        if selection.get("demo_path_step") != PATCH_REVIEW_DEMO_PATH_STEP:
            raise ValueError("Patch review selection does not match the demo path step")
        preview_ver = selection.get("patch_preview_contract_version")
        if preview_ver != PATCH_PREVIEW_CONTRACT_VERSION or isinstance(preview_ver, bool):
            raise ValueError("Unsupported patch preview selection contract version")
        if action_id != "preview_patch":
            raise ValueError("Action id does not match patch preview selection")
        if selection.get("execution_policy") != PATCH_REVIEW_EXECUTION_POLICY["preview"]:
            raise ValueError("Patch review selection execution policy does not match engine policy")
        return

    if set(selection) & _PATCH_REVIEW_METADATA_FIELDS:
        raise ValueError("Patch review selection must identify preview or decision policy")
    _validate_selection_identity_action_id(action_identity, action_id)
    _validate_selection_fields(selection, _ACTION_SELECTION_FIELDS, "action selection")


def _validate_selection_identity_action_id(action_identity: str, action_id: str) -> None:
    try:
        identity = json.loads(action_identity)
    except json.JSONDecodeError:
        return
    if not isinstance(identity, dict):
        return
    identity_action_id = identity.get("id")
    if identity_action_id is not None and identity_action_id != action_id:
        raise ValueError("Action id does not match action selection identity")


def _validate_selection_fields(
    selection: dict[str, Any],
    allowed_fields: frozenset[str],
    selection_label: str,
) -> None:
    unexpected_fields = set(selection) - allowed_fields
    if unexpected_fields:
        field_list = ", ".join(sorted(unexpected_fields))
        raise ValueError(f"Unsupported {selection_label} field(s): {field_list}")


def stream_event_key(event: dict[str, Any]) -> str:
    validate_stream_event(event)
    return json.dumps(
        {
            "contract_version": event["contract_version"],
            "event_id": event["event_id"],
            "run_id": event["run_id"],
            "sequence": event["sequence"],
            "event_type": event["event_type"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def validate_engine_loop_event_sequence(
    events: list[dict[str, Any]],
    capabilities: A2UICapabilities | None = None,
) -> None:
    """Validate a sequence of engine-loop stream events for cross-event consistency.

    Each event must individually pass ``validate_stream_event``.  In addition:

    - Sequences must be strictly monotonically increasing integers.
    - All events must share the same ``run_id``.
    - All ``event_id`` values must be unique within the sequence.
    - Paired ``action_selected`` / ``action_resolved`` events (adjacent pairs
      where the first is ``action_selected``) must carry the same ``action_id``.

    Raises ``ValueError`` on any violation.  Designed for engine-loop logging,
    test assertions, and CLI fallback pre-submission checks.
    """
    if not isinstance(events, list):
        raise ValueError("events must be a list")
    if not events:
        return

    run_ids: set[str] = set()
    event_ids: list[str] = []
    sequences: list[int] = []

    for event in events:
        validate_stream_event(event, capabilities)
        run_ids.add(event["run_id"])
        event_ids.append(event["event_id"])
        sequences.append(event["sequence"])

    if len(run_ids) > 1:
        raise ValueError(
            f"All events in a loop sequence must share the same run_id; "
            f"found {len(run_ids)} distinct run_ids"
        )

    for i in range(1, len(sequences)):
        if sequences[i] <= sequences[i - 1]:
            raise ValueError(
                f"Event sequences must be strictly monotonically increasing; "
                f"sequence {sequences[i]} at position {i} is not greater than "
                f"{sequences[i - 1]} at position {i - 1}"
            )

    if len(set(event_ids)) != len(event_ids):
        seen: set[str] = set()
        for eid in event_ids:
            if eid in seen:
                raise ValueError(f"Duplicate event_id in sequence: {eid!r}")
            seen.add(eid)

    _PATCH_REVIEW_ACTION_IDS: frozenset[str] = frozenset(
        {"preview_patch", "apply_patch", "reject_patch"}
    )
    _PATCH_TERMINAL_ACTION_IDS: frozenset[str] = frozenset({"apply_patch", "reject_patch"})

    # Enforce patch_id consistency: all patch review events in a sequence must
    # reference the same patch.  Mixing patch_ids (e.g. preview for patch-1 then
    # apply for patch-2) is incoherent and indicates a stale or misrouted event.
    # patch_id is encoded in the JSON action_identity string; check both that
    # field and any top-level selection.patch_id for completeness.
    _observed_patch_ids: dict[str, int] = {}
    for event in events:
        pid: str | None = None
        if event.get("event_type") == "card_published":
            # A card_published carrying a ProposedEditCard embeds a patch_id that
            # must be consistent with any patch review actions in the same sequence.
            card = event.get("card")
            if isinstance(card, dict) and card.get("type") == PROPOSED_EDIT_CARD_TYPE:
                card_pid = card.get("patch_id")
                if isinstance(card_pid, str) and card_pid.strip():
                    pid = card_pid.strip()
        elif event.get("action_id") in _PATCH_REVIEW_ACTION_IDS:
            selection = event.get("selection")
            if isinstance(selection, dict):
                # Top-level patch_id (present in some selection models)
                top_pid = selection.get("patch_id")
                if isinstance(top_pid, str) and top_pid.strip():
                    pid = top_pid.strip()
                # Fallback: patch_id encoded inside action_identity JSON
                if pid is None:
                    action_identity = selection.get("action_identity")
                    if isinstance(action_identity, str):
                        try:
                            identity_obj = json.loads(action_identity)
                            if isinstance(identity_obj, dict):
                                id_pid = identity_obj.get("patch_id")
                                if isinstance(id_pid, str) and id_pid.strip():
                                    pid = id_pid.strip()
                        except (json.JSONDecodeError, ValueError):
                            pass
        if pid is None:
            continue
        if pid not in _observed_patch_ids:
            _observed_patch_ids[pid] = event["sequence"]
    if len(_observed_patch_ids) > 1:
        pid_list = ", ".join(
            f"{pid!r} (first seen at sequence {seq})"
            for pid, seq in sorted(_observed_patch_ids.items(), key=lambda kv: kv[1])
        )
        raise ValueError(
            f"All patch review events in a loop sequence must reference the same "
            f"patch_id; found {len(_observed_patch_ids)} distinct patch_ids: {pid_list}"
        )

    terminal_patch_resolved_at: int | None = None
    for i, event in enumerate(events):
        if (
            event.get("event_type") == "action_resolved"
            and event.get("action_id") in _PATCH_TERMINAL_ACTION_IDS
        ):
            status = event.get("status")
            if status in {"applied", "rejected"}:
                terminal_patch_resolved_at = i
                break

    if terminal_patch_resolved_at is not None:
        for j in range(terminal_patch_resolved_at + 1, len(events)):
            later = events[j]
            if later.get("action_id") in _PATCH_REVIEW_ACTION_IDS:
                raise ValueError(
                    f"Patch review action {later.get('action_id')!r} at sequence "
                    f"{later['sequence']} appears after a terminal patch decision was "
                    f"resolved at sequence {events[terminal_patch_resolved_at]['sequence']}"
                )

    # Enforce preview-before-decision: apply_patch or reject_patch may only be
    # selected after preview_patch has been resolved with status "previewed".
    _DECISION_ACTION_IDS: frozenset[str] = frozenset({"apply_patch", "reject_patch"})
    preview_resolved = False
    for event in events:
        action_id = event.get("action_id")
        if (
            event.get("event_type") == "action_resolved"
            and action_id == "preview_patch"
            and event.get("status") == "previewed"
        ):
            preview_resolved = True
        elif (
            event.get("event_type") == "action_selected"
            and action_id in _DECISION_ACTION_IDS
            and not preview_resolved
        ):
            raise ValueError(
                f"Patch decision action {action_id!r} at sequence "
                f"{event['sequence']} was selected before preview_patch was resolved; "
                f"preview must complete before a patch decision can be made"
            )

    # State-machine pass: track in-flight action_selected events across
    # card_published interleaving.  A card_published is allowed anywhere
    # (the engine may publish a new card immediately after resolving one action
    # and before the next action is dispatched, or even between a selected and
    # its resolved in erroneous replays).  All other event types are unknown to
    # the state machine and pass through without affecting dispatch state.
    #
    # Invariants enforced here:
    #   1. action_resolved must follow an in-flight action_selected and carry
    #      the same action_id — even if card_published events appear between them.
    #   2. A second action_selected must not appear while another is in-flight —
    #      card_published events between two action_selected events do not
    #      constitute a valid resolution.
    _inflight_selected: dict[str, Any] | None = None
    for event in events:
        etype = event.get("event_type")
        if etype == "card_published":
            continue
        if etype == "action_selected":
            if _inflight_selected is not None:
                raise ValueError(
                    f"action_selected event at sequence {event['sequence']} was "
                    f"dispatched while action {_inflight_selected.get('action_id')!r} "
                    f"selected at sequence {_inflight_selected['sequence']} was still "
                    f"in-flight; an action_resolved must separate each dispatched action"
                )
            _inflight_selected = event
        elif etype == "action_resolved":
            if _inflight_selected is not None:
                if _inflight_selected.get("action_id") != event.get("action_id"):
                    raise ValueError(
                        f"action_selected event at sequence {_inflight_selected['sequence']} "
                        f"has action_id {_inflight_selected.get('action_id')!r} but the "
                        f"following action_resolved at sequence {event['sequence']} has "
                        f"action_id {event.get('action_id')!r}"
                    )
            _inflight_selected = None


def summarize_engine_loop_sequence_outcome(
    events: list[dict[str, Any]],
    capabilities: A2UICapabilities | None = None,
) -> EngineLoopOutcome:
    """Validate a sequence of engine-loop events and return a typed outcome summary.

    Runs the same validation as ``validate_engine_loop_event_sequence`` and
    additionally extracts the observable outcome of the sequence for use by
    the CLI fallback and engine consumers without re-scanning events.

    Returns a dict with the following keys:

    - ``run_id`` (str | None): the shared run_id for the sequence, or None if empty.
    - ``patch_id`` (str | None): the patch_id observed in the sequence, or None.
    - ``patch_outcome`` (str | None): one of ``"previewed"``, ``"applied"``,
      ``"rejected"``, or None if no terminal patch action was resolved.
    - ``inflight_action_id`` (str | None): the action_id of the most recently
      selected action that has not yet been resolved, or None.
    - ``event_count`` (int): the number of events in the sequence.
    - ``last_sequence`` (int | None): the sequence number of the last event, or None.
    - ``context_basket_outcomes`` (list[dict]): resolved context/basket action
      outcomes in sequence order.  Each entry has ``action_id`` (str),
      ``status`` (str), and ``sequence`` (int).

    Raises ``ValueError`` on any validation violation.
    """
    validate_engine_loop_event_sequence(events, capabilities)

    if not events:
        return {
            "run_id": None,
            "patch_id": None,
            "patch_outcome": None,
            "inflight_action_id": None,
            "event_count": 0,
            "last_sequence": None,
            "context_basket_outcomes": [],
            "status": "pending",
        }

    run_id: str = events[0]["run_id"]
    last_sequence: int = events[-1]["sequence"]

    _PATCH_REVIEW_ACTION_IDS: frozenset[str] = frozenset(
        {"preview_patch", "apply_patch", "reject_patch"}
    )
    _PATCH_TERMINAL_ACTION_IDS: frozenset[str] = frozenset({"apply_patch", "reject_patch"})

    # Extract observed patch_id (first seen wins — validated for consistency above).
    patch_id: str | None = None
    for event in events:
        if patch_id is not None:
            break
        if event.get("event_type") == "card_published":
            card = event.get("card")
            if isinstance(card, dict) and card.get("type") == PROPOSED_EDIT_CARD_TYPE:
                pid = card.get("patch_id")
                if isinstance(pid, str) and pid.strip():
                    patch_id = pid.strip()
        elif event.get("action_id") in _PATCH_REVIEW_ACTION_IDS:
            selection = event.get("selection")
            if isinstance(selection, dict):
                top_pid = selection.get("patch_id")
                if isinstance(top_pid, str) and top_pid.strip():
                    patch_id = top_pid.strip()
                elif patch_id is None:
                    action_identity = selection.get("action_identity")
                    if isinstance(action_identity, str):
                        try:
                            identity_obj = json.loads(action_identity)
                            if isinstance(identity_obj, dict):
                                id_pid = identity_obj.get("patch_id")
                                if isinstance(id_pid, str) and id_pid.strip():
                                    patch_id = id_pid.strip()
                        except (json.JSONDecodeError, ValueError):
                            pass

    # Determine the final patch outcome from resolved terminal actions.
    patch_outcome: str | None = None
    for event in events:
        if (
            event.get("event_type") == "action_resolved"
            and event.get("action_id") in _PATCH_REVIEW_ACTION_IDS
        ):
            status = event.get("status")
            if isinstance(status, str) and status in {"previewed", "applied", "rejected"}:
                patch_outcome = status
            # Do not break — a later resolution overrides earlier ones if the
            # sequence contains a preview followed by a terminal decision.

    # Determine the in-flight action_id (selected but not yet resolved).
    inflight_action_id: str | None = None
    _inflight: dict[str, Any] | None = None
    for event in events:
        etype = event.get("event_type")
        if etype == "card_published":
            continue
        if etype == "action_selected":
            _inflight = event
        elif etype == "action_resolved":
            _inflight = None
    if _inflight is not None:
        inflight_action_id = _inflight.get("action_id")

    # Collect resolved context/basket action outcomes in sequence order.
    context_basket_outcomes: list[dict[str, Any]] = []
    for event in events:
        if (
            event.get("event_type") == "action_resolved"
            and event.get("action_id") in CONTEXT_BASKET_ACTION_IDS
        ):
            status = event.get("status")
            if isinstance(status, str):
                context_basket_outcomes.append(
                    {
                        "action_id": event["action_id"],
                        "status": status,
                        "sequence": event["sequence"],
                    }
                )

    return {
        "run_id": run_id,
        "patch_id": patch_id,
        "patch_outcome": patch_outcome,
        "inflight_action_id": inflight_action_id,
        "event_count": len(events),
        "last_sequence": last_sequence,
        "context_basket_outcomes": context_basket_outcomes,
        "status": _compute_engine_loop_status(
            inflight_action_id=inflight_action_id,
            patch_id=patch_id,
            patch_outcome=patch_outcome,
        ),
    }


def _compute_engine_loop_status(
    *,
    inflight_action_id: "str | None",
    patch_id: "str | None",
    patch_outcome: "str | None",
) -> Literal["waiting_for_action", "waiting_for_resolution", "complete"]:
    """Derive a human-readable status string from engine-loop outcome fields."""
    if inflight_action_id is not None:
        return "waiting_for_resolution"
    if patch_id is not None and patch_outcome not in {"applied", "rejected"}:
        return "waiting_for_action"
    return "complete"


def is_engine_loop_outcome_terminal(outcome: EngineLoopOutcome) -> bool:
    """Return True if the engine-loop outcome represents a fully-resolved state.

    A terminal outcome satisfies ALL of:
    - No action is currently in-flight (inflight_action_id is None).
    - If a patch was published, it has been applied or rejected.

    An outcome with no patch and no in-flight action is also terminal (e.g. a
    retrieval-only run that completed all basket/context actions).  Engine-runs
    can poll this helper to decide when to stop waiting for further events.
    """
    if not isinstance(outcome, dict):
        raise ValueError("outcome must be a dictionary")
    if outcome.get("inflight_action_id") is not None:
        return False
    patch_id = outcome.get("patch_id")
    if patch_id is not None:
        return outcome.get("patch_outcome") in {"applied", "rejected"}
    return True


_VALID_PATCH_OUTCOMES: frozenset[str | None] = frozenset(
    {None, "previewed", "applied", "rejected"}
)
_VALID_LOOP_STATUSES: frozenset[str] = frozenset(
    {"pending", "waiting_for_action", "waiting_for_resolution", "complete"}
)
_ENGINE_LOOP_OUTCOME_FIELDS: frozenset[str] = frozenset(
    {
        "run_id",
        "patch_id",
        "patch_outcome",
        "inflight_action_id",
        "event_count",
        "last_sequence",
        "context_basket_outcomes",
        "status",
    }
)


def validate_engine_loop_outcome(outcome: "dict[str, Any]") -> None:
    """Validate that *outcome* is a well-formed EngineLoopOutcome dict.

    Useful when an outcome is received across a serialization boundary (e.g. from
    a queue, IPC, or cache) rather than produced directly by
    ``summarize_engine_loop_sequence_outcome``.

    Accepts both plain dicts and EngineLoopOutcome TypedDict instances (TypedDict
    is a dict subtype). All access is via .get() so the typed interface is not
    required; callers should pass a deserialized dict at a serialization boundary.

    Raises ``ValueError`` with a descriptive message on any contract violation.
    Does not mutate the input.
    """
    if not isinstance(outcome, dict):
        raise ValueError(
            f"EngineLoopOutcome must be a dict, got {type(outcome).__name__!r}"
        )
    unexpected_fields = set(outcome) - _ENGINE_LOOP_OUTCOME_FIELDS
    if unexpected_fields:
        field_list = ", ".join(sorted(unexpected_fields))
        raise ValueError(f"Unsupported EngineLoopOutcome field(s): {field_list}")
    event_count = outcome.get("event_count")
    if not isinstance(event_count, int) or isinstance(event_count, bool) or event_count < 0:
        raise ValueError(
            f"EngineLoopOutcome.event_count must be a non-negative int, got {event_count!r}"
        )
    for field in ("run_id", "patch_id", "patch_outcome", "inflight_action_id"):
        val = outcome.get(field)
        if val is not None and not isinstance(val, str):
            raise ValueError(
                f"EngineLoopOutcome.{field} must be a string or None, got {type(val).__name__!r}"
            )
    run_id = outcome.get("run_id")
    if isinstance(run_id, str):
        if not run_id.strip():
            raise ValueError("EngineLoopOutcome.run_id must be non-empty when present")
        if run_id != run_id.strip():
            raise ValueError("EngineLoopOutcome.run_id must be normalized")
    patch_id = outcome.get("patch_id")
    if isinstance(patch_id, str):
        if not patch_id.strip():
            raise ValueError("EngineLoopOutcome.patch_id must be non-empty when present")
        if patch_id != patch_id.strip():
            raise ValueError("EngineLoopOutcome.patch_id must be normalized")
    inflight_action_id = outcome.get("inflight_action_id")
    if isinstance(inflight_action_id, str):
        if not inflight_action_id.strip():
            raise ValueError(
                "EngineLoopOutcome.inflight_action_id must be non-empty when present"
            )
        if inflight_action_id != inflight_action_id.strip():
            raise ValueError("EngineLoopOutcome.inflight_action_id must be normalized")
    patch_outcome = outcome.get("patch_outcome")
    if patch_outcome not in _VALID_PATCH_OUTCOMES:
        raise ValueError(
            f"EngineLoopOutcome.patch_outcome {patch_outcome!r} is not a recognised value; "
            f"expected one of {sorted(str(v) for v in _VALID_PATCH_OUTCOMES if v is not None)!r} "
            "or None"
        )
    if patch_outcome is not None and patch_id is None:
        raise ValueError(
            "EngineLoopOutcome.patch_outcome cannot be set when patch_id is missing"
        )
    if patch_outcome in {"applied", "rejected"} and inflight_action_id is not None:
        raise ValueError(
            "EngineLoopOutcome cannot have an in-flight action after a terminal patch_outcome"
        )
    last_sequence = outcome.get("last_sequence")
    if last_sequence is not None and (not isinstance(last_sequence, int) or isinstance(last_sequence, bool) or last_sequence < 1):
        raise ValueError(
            f"EngineLoopOutcome.last_sequence must be a positive int or None, got {last_sequence!r}"
        )
    cbo = outcome.get("context_basket_outcomes")
    if cbo is not None:
        if not isinstance(cbo, list):
            raise ValueError(
                f"EngineLoopOutcome.context_basket_outcomes must be a list, got {type(cbo).__name__!r}"
            )
        for i, entry in enumerate(cbo):
            if not isinstance(entry, dict):
                raise ValueError(
                    f"EngineLoopOutcome.context_basket_outcomes[{i}] must be a dict"
                )
            unexpected_entry_fields = set(entry) - {"action_id", "status", "sequence"}
            if unexpected_entry_fields:
                field_list = ", ".join(sorted(unexpected_entry_fields))
                raise ValueError(
                    f"Unsupported EngineLoopOutcome.context_basket_outcomes[{i}] field(s): {field_list}"
                )
            for key in ("action_id", "status"):
                v = entry.get(key)
                if not isinstance(v, str) or not v.strip():
                    raise ValueError(
                        f"EngineLoopOutcome.context_basket_outcomes[{i}].{key} must be a non-empty string"
                    )
                if v != v.strip():
                    raise ValueError(
                        f"EngineLoopOutcome.context_basket_outcomes[{i}].{key} must be normalized"
                    )
            seq = entry.get("sequence")
            if not isinstance(seq, int) or isinstance(seq, bool) or seq < 1:
                raise ValueError(
                    f"EngineLoopOutcome.context_basket_outcomes[{i}].sequence must be a positive int"
                )
    status = outcome.get("status")
    if status is not None and status not in _VALID_LOOP_STATUSES:
        raise ValueError(
            f"EngineLoopOutcome.status {status!r} is not a recognised value; "
            f"expected one of {sorted(_VALID_LOOP_STATUSES)!r}"
        )
    if status is not None:
        expected_status = (
            "pending"
            if event_count == 0
            else _compute_engine_loop_status(
                inflight_action_id=inflight_action_id,
                patch_id=patch_id,
                patch_outcome=patch_outcome,
            )
        )
        if status != expected_status:
            raise ValueError(
                f"EngineLoopOutcome.status {status!r} is inconsistent with "
                f"patch_id={patch_id!r}, patch_outcome={patch_outcome!r}, "
                f"inflight_action_id={inflight_action_id!r}; expected {expected_status!r}"
            )


def engine_loop_outcome_next_action_hints(
    outcome: "EngineLoopOutcome | dict[str, Any]",
) -> "list[dict[str, Any]]":
    """Return structured next-action hints for a given engine-loop outcome.

    Returns a list of ``{"action_id": str, "label": str}`` dicts representing
    the actions a client (CLI or Textual) should surface to the user next.

    Rules:
    - If an action is in-flight, no hints are returned (already waiting).
    - If no patch is involved, no hints are returned (nothing to decide).
    - If a patch is pending preview, return ``preview_patch``.
    - If a patch has been previewed and is awaiting decision, return
      ``apply_patch`` and ``reject_patch`` in canonical order.
    - If the patch is already resolved (applied/rejected), return no hints.

    This is the structured counterpart to the ``Next:`` lines in
    ``render_engine_loop_outcome`` and is intended for UI clients that build
    action buttons rather than parse rendered text.
    """
    if not isinstance(outcome, dict):
        raise ValueError("outcome must be a dictionary")
    if outcome.get("inflight_action_id") is not None:
        return []
    patch_id = outcome.get("patch_id")
    if patch_id is None:
        return []
    patch_outcome = outcome.get("patch_outcome")
    if patch_outcome in {"applied", "rejected"}:
        return []
    if patch_outcome is None:
        return [{"action_id": "preview_patch", "label": "Preview"}]
    if patch_outcome == "previewed":
        return [
            {"action_id": "apply_patch", "label": "Apply"},
            {"action_id": "reject_patch", "label": "Reject"},
        ]
    return []


# Confirm dialogs for canonical patch-review actions.
_PATCH_ACTION_CONFIRM: dict[str, dict[str, str]] = {
    "apply_patch": {"title": "Apply patch?"},
    "reject_patch": {"title": "Reject patch?"},
}


def action_ref_from_next_action_hint(
    hint: dict[str, Any],
    outcome: "EngineLoopOutcome | dict[str, Any]",
) -> ActionRef:
    """Build a fully-formed ActionRef from a next-action hint and an engine loop outcome.

    Bridges ``engine_loop_outcome_next_action_hints`` to
    ``execute_action_with_policy_gate``: callers iterate the hint list, pick a
    hint, and pass it here together with the same outcome to get an ActionRef
    ready for policy-gated dispatch — without manually extracting patch_id or
    hard-coding confirm/policy_sensitive values.

    Raises ValueError if the outcome has no patch_id, the hint action_id is
    not a supported patch-review action, or the hint is stale for the supplied
    engine outcome.
    """
    if not isinstance(hint, dict):
        raise ValueError("hint must be a dictionary")
    if not isinstance(outcome, dict):
        raise ValueError("outcome must be a dictionary")
    label_val = hint.get("label")
    if label_val is not None and not isinstance(label_val, str):
        raise ValueError("hint label must be a string")
    action_id: str | None = hint.get("action_id")
    if not isinstance(action_id, str) or action_id not in {"preview_patch", "apply_patch", "reject_patch"}:
        raise ValueError(
            f"hint action_id {action_id!r} is not a supported patch-review action; "
            "expected one of 'preview_patch', 'apply_patch', 'reject_patch'"
        )
    available_action_ids = {
        available_hint["action_id"]
        for available_hint in engine_loop_outcome_next_action_hints(outcome)
        if isinstance(available_hint.get("action_id"), str)
    }
    if action_id not in available_action_ids:
        available = ", ".join(sorted(available_action_ids)) or "<none>"
        raise ValueError(
            f"hint action_id {action_id!r} is not available for the current engine outcome; "
            f"available actions: {available}"
        )
    patch_id: str | None = outcome.get("patch_id")
    if not isinstance(patch_id, str):
        raise ValueError(
            "outcome has no patch_id; cannot build an ActionRef from the hint"
        )
    label: str = hint.get("label") or action_id
    return ActionRef(
        id=action_id,
        label=label,
        payload={"patch_id": patch_id},
        confirm=deepcopy(_PATCH_ACTION_CONFIRM.get(action_id)),
        policy_sensitive=is_policy_sensitive_action(action_id),
    )


def execute_patch_review_from_hint_with_policy_gate_and_advance_state(
    *,
    hint: dict[str, Any],
    outcome: "EngineLoopOutcome | dict[str, Any]",
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
    current_state: "dict[str, Any] | None" = None,
) -> dict[str, Any]:
    """Execute a patch-review hint through the policy gate and return the advanced state.

    Integrates the canonical demo-path pipeline for UI clients (CLI and Textual):
    ``engine_loop_outcome_next_action_hints`` → ``action_ref_from_next_action_hint``
    → ``advance_patch_review_state`` → ``execute_action_with_policy_gate``.

    The caller picks a hint from ``engine_loop_outcome_next_action_hints``, passes
    it here with the same ``outcome``, and receives the updated ``PatchReviewState``
    dict — without manually extracting ``patch_id`` or calling each step in sequence.

    Returns the dict returned by ``advance_patch_review_state`` (keys:
    ``patch_id``, ``previewed``, and optionally ``resolved``/``resolved_as``).

    Raises:
    - ``ValueError`` if the hint action_id is not a supported patch-review action
      or the outcome carries no ``patch_id``.
    - ``PermissionError`` if the policy gate blocks the action, or the state
      precondition for a decision action (apply/reject) is not met.
    """
    ref = action_ref_from_next_action_hint(hint, outcome)
    patch_id: str = ref.payload["patch_id"]
    control_map = {"preview_patch": "preview", "apply_patch": "apply", "reject_patch": "reject"}
    control = control_map[ref.id]
    next_state = advance_patch_review_state(
        patch_id=patch_id,
        control=control,
        current_state=current_state,
    )
    execute_action_with_policy_gate(
        action=ref,
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )
    return next_state


def execute_patch_review_from_hint_with_policy_gate_and_advance_state_typed(
    *,
    hint: dict[str, Any],
    outcome: "EngineLoopOutcome | dict[str, Any]",
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
    current_state: "PatchReviewState | None" = None,
) -> PatchReviewState:
    """Execute a patch-review hint through the policy gate and return a typed PatchReviewState.

    Typed variant of ``execute_patch_review_from_hint_with_policy_gate_and_advance_state``.
    Accepts an optional ``PatchReviewState`` as ``current_state`` and returns a new
    ``PatchReviewState`` reflecting the transition.  Delegates to
    ``advance_patch_review_state_typed`` for the state update so callers (CLI and
    future Textual client) receive a typed object rather than a raw dict.

    Raises:
    - ``ValueError`` if the hint action_id is not a supported patch-review action,
      the outcome carries no ``patch_id``, or ``current_state`` is not a
      ``PatchReviewState``.
    - ``PermissionError`` if the policy gate blocks the action or a precondition
      for a decision action (apply/reject) is not satisfied.
    """
    if current_state is not None and not isinstance(current_state, PatchReviewState):
        raise ValueError(
            "execute_patch_review_from_hint_with_policy_gate_and_advance_state_typed: "
            "current_state must be a PatchReviewState or None"
        )
    ref = action_ref_from_next_action_hint(hint, outcome)
    patch_id: str = ref.payload["patch_id"]
    control_map = {"preview_patch": "preview", "apply_patch": "apply", "reject_patch": "reject"}
    control = control_map[ref.id]
    next_state = advance_patch_review_state_typed(
        patch_id=patch_id,
        control=control,
        current_state=current_state,
    )
    execute_action_with_policy_gate(
        action=ref,
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )
    return next_state
