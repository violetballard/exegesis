from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from typing import Any, Callable, Protocol

ACTION_SELECTION_CONTRACT_VERSION = 1
ALLOWED_ACTION_IDS: tuple[str, ...] = (
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

CANONICAL_ACTION_ORDER: tuple[str, ...] = (
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


def materialize_cli_fallback_card(card: dict[str, Any]) -> dict[str, Any]:
    materialized = deepcopy(card)
    materialized["actions"] = materialize_card_actions(card)
    materialized["action_selection"] = materialize_action_selection_contract(card)
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
    for key, value_type in schema.items():
        if key not in payload:
            raise ValueError(f"Missing payload field '{key}' for action '{action_id}'")
        if not isinstance(payload[key], value_type):
            raise ValueError(f"Payload field '{key}' must be of type {value_type.__name__}")
        if value_type is str and not payload[key].strip():
            raise ValueError(f"Payload field '{key}' is required for action '{action_id}'")
