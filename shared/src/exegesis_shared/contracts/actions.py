from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from typing import Any, Callable, Protocol

ACTION_SELECTION_CONTRACT_VERSION = 1
PATCH_DECISION_CONTRACT_VERSION = 1
ALLOWED_ACTION_IDS: tuple[str, ...] = (
    "preview_patch",
    "apply_patch",
    "reject_patch",
    "open_section",
    "open_corpus_item",
    "pin_to_context_set",
    "create_context_set",
    "run_agent",
    "refresh_license",
    "export_document",
    "copy_to_clipboard",
)
PATCH_DECISION_ACTION_IDS: tuple[str, ...] = ("apply_patch", "reject_patch")
PATCH_DECISION_BY_ACTION_ID: dict[str, str] = {
    "apply_patch": "apply",
    "reject_patch": "reject",
}

CANONICAL_ACTION_ORDER: tuple[str, ...] = (
    "preview_patch",
    "apply_patch",
    "reject_patch",
    "open_section",
    "open_corpus_item",
    "pin_to_context_set",
    "create_context_set",
    "copy_to_clipboard",
    "export_document",
    "refresh_license",
    "run_agent",
)
CANONICAL_ACTION_PRIORITY: dict[str, int] = {
    action_id: index for index, action_id in enumerate(CANONICAL_ACTION_ORDER)
}
_ALLOWED_ACTION_SET = set(ALLOWED_ACTION_IDS)
if set(CANONICAL_ACTION_ORDER) != _ALLOWED_ACTION_SET:
    raise RuntimeError("A2UI canonical action order must match allowed action IDs")

_ACTION_SCHEMAS: dict[str, dict[str, type]] = {
    "preview_patch": {"patch_id": str},
    "apply_patch": {"patch_id": str},
    "reject_patch": {"patch_id": str},
    "open_section": {"section_id": str},
    "open_corpus_item": {"item_id": str},
    "pin_to_context_set": {"item_id": str},
    "create_context_set": {"name": str},
    "run_agent": {"operation": str},
    "refresh_license": {},
    "export_document": {"format": str},
    "copy_to_clipboard": {"text": str},
}


@dataclass(frozen=True)
class ActionRef:
    id: str
    label: str
    payload: dict[str, Any]
    confirm: dict[str, str] | None = None
    policy_sensitive: bool = False


class PolicyGate(Protocol):
    def allow_action(self, action_id: str, payload: dict[str, Any], *, policy_sensitive: bool) -> bool:
        ...


def canonical_action_key(action: dict[str, Any]) -> str:
    return json.dumps(action, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def canonical_action_identity_key(action: dict[str, Any]) -> str:
    identity = {
        "confirm": action.get("confirm"),
        "id": action.get("id"),
        "payload": action.get("payload"),
        "policy_sensitive": action.get("policy_sensitive", False),
    }
    return json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def action_priority(action: dict[str, Any]) -> tuple[int, str, str, str]:
    action_id = str(action.get("id", ""))
    priority = CANONICAL_ACTION_PRIORITY.get(action_id, len(CANONICAL_ACTION_ORDER))
    return (priority, action_id, canonical_action_identity_key(action), canonical_action_key(action))


def canonicalize_action_order(actions: list[Any]) -> list[dict[str, Any]]:
    valid_actions: list[dict[str, Any]] = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        try:
            validate_action_ref(action)
        except ValueError:
            continue
        valid_actions.append(action)
    return [deepcopy(action) for action in sorted(valid_actions, key=action_priority)]


def materialize_card_actions(card: dict[str, Any]) -> list[dict[str, Any]]:
    raw_actions = card.get("actions", [])
    if not isinstance(raw_actions, list):
        return []

    by_identity: dict[str, dict[str, Any]] = {}
    for action in raw_actions:
        if not isinstance(action, dict):
            continue
        try:
            validate_action_ref(action)
        except ValueError:
            continue
        identity_key = canonical_action_identity_key(action)
        current = by_identity.get(identity_key)
        if current is None or canonical_action_key(action) < canonical_action_key(current):
            by_identity[identity_key] = deepcopy(action)
    return canonicalize_action_order(list(by_identity.values()))


def materialize_action_selection_contract(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
        "selection_model": "one_based_action_slot",
        "order": [
            {
                "slot": slot,
                "action_id": str(action["id"]),
                "action_identity": canonical_action_identity_key(action),
            }
            for slot, action in enumerate(materialize_card_actions(card), start=1)
        ],
    }


def materialize_patch_decision_contract(card: dict[str, Any], patch_id: str) -> dict[str, Any]:
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch decision patch_id is required")

    decisions: list[dict[str, Any]] = []
    for slot, action in enumerate(materialize_card_actions(card), start=1):
        action_id = action.get("id")
        if action_id not in PATCH_DECISION_ACTION_IDS:
            continue
        payload = action.get("payload")
        action_patch_id = payload.get("patch_id") if isinstance(payload, dict) else None
        if action_patch_id != expected_patch_id:
            continue
        decision = "apply" if action_id == "apply_patch" else "reject"
        selection = {
            "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
            "selection_model": "one_based_action_slot",
            "slot": slot,
            "action_identity": canonical_action_identity_key(action),
            "patch_decision_contract_version": PATCH_DECISION_CONTRACT_VERSION,
            "patch_decision": decision,
            "patch_id": expected_patch_id,
        }
        decisions.append(
            {
                "decision": decision,
                "slot": slot,
                "action_id": str(action_id),
                "action_identity": canonical_action_identity_key(action),
                "selection": selection,
            }
        )

    return {
        "contract_version": PATCH_DECISION_CONTRACT_VERSION,
        "patch_id": expected_patch_id,
        "decisions": decisions,
    }


def materialize_cli_fallback_card(card: dict[str, Any]) -> dict[str, Any]:
    materialized = deepcopy(card)
    materialized["actions"] = materialize_card_actions(card)
    materialized["action_selection"] = materialize_action_selection_contract(card)
    patch_id = card.get("patch_id")
    if isinstance(patch_id, str) and patch_id.strip():
        patch_decision = materialize_patch_decision_contract(materialized, patch_id)
        if patch_decision["decisions"]:
            materialized["patch_decision"] = patch_decision
    return materialized


def resolve_card_selection(card: dict[str, Any], selected_action_id: str) -> dict[str, Any]:
    actions = materialize_card_actions(card)
    matches = [action for action in actions if action.get("id") == selected_action_id]
    if len(matches) == 1:
        action = matches[0]
        validate_action_ref(action)
        return action
    if len(matches) > 1:
        raise ValueError(
            f"Action '{selected_action_id}' is ambiguous on card. "
            "Use one-based action selection for duplicate action IDs."
        )
    action_ids = [a.get("id", "<unknown>") for a in actions]
    raise ValueError(f"Action '{selected_action_id}' not found on card. Available: {action_ids}")


def resolve_card_selection_by_index(card: dict[str, Any], selected_action_index: int) -> dict[str, Any]:
    if not isinstance(selected_action_index, int) or isinstance(selected_action_index, bool):
        raise TypeError("Action selection index must be an integer")
    if selected_action_index < 1:
        raise ValueError("Action selection index must be one-based")

    action_sequence = materialize_card_actions(card)
    try:
        action = action_sequence[selected_action_index - 1]
    except IndexError as exc:
        raise ValueError(
            f"Action selection index {selected_action_index} not found. "
            f"Available range: 1..{len(action_sequence)}"
        ) from exc
    validate_action_ref(action)
    return action


def resolve_card_selection_contract(card: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(selection, dict):
        raise ValueError("Action selection must be an object")
    if selection.get("contract_version") != ACTION_SELECTION_CONTRACT_VERSION:
        raise ValueError("Unsupported action selection contract version")
    if selection.get("selection_model") != "one_based_action_slot":
        raise ValueError("Unsupported action selection model")

    slot = selection.get("slot")
    action = resolve_card_selection_by_index(card, slot)
    expected_identity = canonical_action_identity_key(action)
    submitted_identity = selection.get("action_identity")
    if submitted_identity != expected_identity:
        raise ValueError("Action selection identity does not match the current card")
    return action


def resolve_patch_decision_selection(
    card: dict[str, Any],
    selection: dict[str, Any],
    *,
    patch_id: str,
) -> dict[str, Any]:
    action = resolve_card_selection_contract(card, selection)
    if action.get("id") not in {"apply_patch", "reject_patch"}:
        raise ValueError("Action selection is not a patch decision")
    payload = action.get("payload")
    action_patch_id = payload.get("patch_id") if isinstance(payload, dict) else None
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch decision patch_id is required")
    if selection.get("patch_id") != expected_patch_id:
        raise ValueError("Patch decision selection does not match the current patch")
    expected_decision = PATCH_DECISION_BY_ACTION_ID[str(action["id"])]
    if selection.get("patch_decision_contract_version") != PATCH_DECISION_CONTRACT_VERSION:
        raise ValueError("Unsupported patch decision contract version")
    submitted_decision = selection.get("patch_decision")
    if submitted_decision not in {"apply", "reject"}:
        raise ValueError("Patch decision selection must include patch_decision")
    if submitted_decision != expected_decision:
        raise ValueError("Patch decision selection does not match the selected action")
    if action_patch_id != expected_patch_id:
        raise ValueError("Patch decision selection does not match the current patch")
    return action


def resolve_patch_decision_action(
    card: dict[str, Any],
    *,
    patch_id: str,
    decision: str,
) -> dict[str, Any]:
    selection = build_patch_decision_selection(card, patch_id=patch_id, decision=decision)
    expected_patch_id = patch_id.strip()
    return resolve_patch_decision_selection(card, selection, patch_id=expected_patch_id)


def build_patch_decision_selection(
    card: dict[str, Any],
    *,
    patch_id: str,
    decision: str,
) -> dict[str, Any]:
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch decision patch_id is required")

    normalized_decision = decision.strip().lower()
    if normalized_decision not in {"apply", "reject"}:
        raise ValueError("Patch decision must be 'apply' or 'reject'")

    patch_decision = card.get("patch_decision")
    if not isinstance(patch_decision, dict) or patch_decision.get("patch_id") != expected_patch_id:
        patch_decision = materialize_patch_decision_contract(card, expected_patch_id)
    if patch_decision.get("contract_version") != PATCH_DECISION_CONTRACT_VERSION:
        raise ValueError("Unsupported patch decision contract version")

    matching_entries = [
        entry
        for entry in patch_decision.get("decisions", [])
        if isinstance(entry, dict) and entry.get("decision") == normalized_decision
    ]
    if len(matching_entries) != 1:
        raise ValueError(f"Patch decision '{normalized_decision}' is not available for the current patch")

    entry = matching_entries[0]
    selection = entry.get("selection")
    if isinstance(selection, dict):
        if selection.get("contract_version") != ACTION_SELECTION_CONTRACT_VERSION:
            raise ValueError("Unsupported action selection contract version")
        if selection.get("selection_model") != "one_based_action_slot":
            raise ValueError("Unsupported action selection model")
        if selection.get("action_identity") != entry.get("action_identity"):
            raise ValueError("Patch decision selection does not match the current card")
        if selection.get("slot") != entry.get("slot"):
            raise ValueError("Patch decision selection does not match the current card")
        if selection.get("patch_decision_contract_version") != PATCH_DECISION_CONTRACT_VERSION:
            raise ValueError("Unsupported patch decision contract version")
        if selection.get("patch_decision") != normalized_decision:
            raise ValueError("Patch decision selection does not match the selected action")
        if selection.get("patch_id") != expected_patch_id:
            raise ValueError("Patch decision selection does not match the current patch")
        resolve_patch_decision_selection(card, selection, patch_id=expected_patch_id)
        return deepcopy(selection)
    selection = {
        "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
        "selection_model": "one_based_action_slot",
        "slot": entry.get("slot"),
        "action_identity": entry.get("action_identity"),
        "patch_decision_contract_version": PATCH_DECISION_CONTRACT_VERSION,
        "patch_decision": normalized_decision,
        "patch_id": expected_patch_id,
    }
    resolve_patch_decision_selection(card, selection, patch_id=expected_patch_id)
    return selection


def validate_action_ref(action: Any) -> None:
    if not isinstance(action, dict):
        raise ValueError("ActionRef must be an object")
    action_id = str(action.get("id", ""))
    if action_id not in _ALLOWED_ACTION_SET:
        raise ValueError(f"Unsupported action id: {action_id}")
    label = action.get("label")
    if not isinstance(label, str) or not label.strip():
        raise ValueError("Action label is required")
    payload = action.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("Action payload must be an object")
    _validate_action_payload(action_id, payload)


def execute_action_with_policy_gate(
    *,
    action: ActionRef,
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    if action.id not in _ALLOWED_ACTION_SET:
        raise ValueError("Unknown action id")
    if action.id not in set(capabilities.actions_supported):
        raise ValueError("Action not supported by client")
    _validate_action_payload(action.id, action.payload)
    if not policy_gate.allow_action(action.id, action.payload, policy_sensitive=action.policy_sensitive):
        raise PermissionError("PolicyGate blocked action")
    return executor(action)


def _validate_action_payload(action_id: str, payload: dict[str, Any]) -> None:
    schema = _ACTION_SCHEMAS.get(action_id)
    if schema is None:
        raise ValueError(f"Unsupported action id: {action_id}")
    unexpected_fields = set(payload) - set(schema)
    if unexpected_fields:
        field_list = ", ".join(sorted(unexpected_fields))
        raise ValueError(f"Unsupported payload field(s) for action '{action_id}': {field_list}")
    for key, value_type in schema.items():
        if key not in payload:
            raise ValueError(f"Missing payload field '{key}' for action '{action_id}'")
        if not isinstance(payload[key], value_type):
            raise ValueError(f"Payload field '{key}' must be of type {value_type.__name__}")
        if value_type is str and not payload[key].strip():
            raise ValueError(f"Payload field '{key}' is required for action '{action_id}'")
