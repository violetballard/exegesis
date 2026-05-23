from __future__ import annotations

from copy import deepcopy
import json
from typing import Any

from exegesis_shared.contracts.actions import (
    ACTION_SELECTION_CONTRACT_VERSION,
    ALLOWED_ACTION_IDS,
    PATCH_DECISION_CONTRACT_VERSION,
    PATCH_PREVIEW_CONTRACT_VERSION,
    PATCH_REVIEW_ACTION_AUTHORITY,
    PATCH_REVIEW_DECISION_GROUP,
    PATCH_REVIEW_DEMO_PATH_STEP,
    PATCH_REVIEW_EXECUTION_POLICY,
    action_ref_from_selection,
    build_complete_patch_review_contract,
    build_patch_review_selection,
    patch_review_resolved_status,
)
from exegesis_shared.contracts.cards import (
    A2UICapabilities,
    engine_prepare_card,
    materialize_cli_fallback_card,
    validate_card_payload_size,
)

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
    expected_status = patch_review_resolved_status(normalized_control)
    resolved_status = status or expected_status
    if resolved_status != expected_status:
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
    if event.get("contract_version") != A2UI_EVENT_CONTRACT_VERSION:
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
            raise ValueError("card_published card requires a non-blank type")
        card_title = card.get("title")
        if not isinstance(card_title, str) or not card_title.strip():
            raise ValueError("card_published card requires a non-blank title")
        if capabilities is not None:
            validate_card_payload_size(card, capabilities)
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
        if status not in {"previewed", "applied", "rejected", "blocked", "failed", "completed"}:
            raise ValueError("Unsupported action_resolved status")
        _validate_action_resolved_status_for_action(action_id, str(status))
        message = event.get("message")
        if message is not None and (not isinstance(message, str) or not message.strip()):
            raise ValueError("action_resolved event message must be a non-empty string")
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
    if capabilities is not None and action_id not in set(capabilities.actions_supported):
        raise ValueError(f"Client does not support A2UI stream event action id: {action_id}")
    return action_id


def _validate_action_resolved_status_for_action(action_id: str, status: str) -> None:
    if status in {"blocked", "failed"}:
        return
    expected_by_action_id = {
        "preview_patch": "previewed",
        "apply_patch": "applied",
        "reject_patch": "rejected",
    }
    expected_status = expected_by_action_id.get(action_id)
    if expected_status is not None and status != expected_status:
        raise ValueError("Patch review resolved status does not match action id")
    _CONTEXT_BASKET_ACTION_IDS = {"promote_to_basket", "pin_to_context_set", "create_context_set", "gather_context"}
    if action_id in _CONTEXT_BASKET_ACTION_IDS and status != "completed":
        raise ValueError("Context and basket action resolved status must be 'completed'")
    _PATCH_REVIEW_ACTION_IDS = {"preview_patch", "apply_patch", "reject_patch"}
    _SPECIAL_ACTION_IDS = _PATCH_REVIEW_ACTION_IDS | _CONTEXT_BASKET_ACTION_IDS
    if action_id not in _SPECIAL_ACTION_IDS and status != "completed":
        raise ValueError("Generic action resolved status must be 'completed'")


def _validate_action_selection(selection: dict[str, Any], action_id: str) -> None:
    if selection.get("contract_version") != ACTION_SELECTION_CONTRACT_VERSION:
        raise ValueError("Unsupported action selection contract version")
    if selection.get("selection_model") != "one_based_action_slot":
        raise ValueError("Unsupported action selection model")
    slot = selection.get("slot")
    if not isinstance(slot, int) or isinstance(slot, bool) or slot < 1:
        raise ValueError("Action selection slot must be a positive integer")
    action_identity = selection.get("action_identity")
    if not isinstance(action_identity, str) or not action_identity.strip():
        raise ValueError("Action selection identity is required")

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
        if selection.get("action_authority") != PATCH_REVIEW_ACTION_AUTHORITY:
            raise ValueError("Patch review selection must be engine-authoritative")
        if selection.get("demo_path_step") != PATCH_REVIEW_DEMO_PATH_STEP:
            raise ValueError("Patch review selection does not match the demo path step")
        if selection.get("patch_decision_contract_version") != PATCH_DECISION_CONTRACT_VERSION:
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
        if selection.get("action_authority") != PATCH_REVIEW_ACTION_AUTHORITY:
            raise ValueError("Patch review selection must be engine-authoritative")
        if selection.get("demo_path_step") != PATCH_REVIEW_DEMO_PATH_STEP:
            raise ValueError("Patch review selection does not match the demo path step")
        if selection.get("patch_preview_contract_version") != PATCH_PREVIEW_CONTRACT_VERSION:
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
