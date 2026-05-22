from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable, Protocol

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

_ALLOWED_ACTION_SET = set(ALLOWED_ACTION_IDS)
POLICY_SENSITIVE_ACTION_IDS: tuple[str, ...] = (
    "apply_patch",
    "reject_patch",
    "run_agent",
    "refresh_license",
    "export_document",
)
_POLICY_SENSITIVE_ACTION_SET = set(POLICY_SENSITIVE_ACTION_IDS)

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
    policy_sensitive = action.policy_sensitive or is_policy_sensitive_action(action.id)
    gated_action = replace(action, policy_sensitive=policy_sensitive)
    if not policy_gate.allow_action(action.id, action.payload, policy_sensitive=policy_sensitive):
        raise PermissionError("PolicyGate blocked action")
    return executor(gated_action)


def is_policy_sensitive_action(action_id: str) -> bool:
    return action_id in _POLICY_SENSITIVE_ACTION_SET


def _validate_action_payload(action_id: str, payload: dict[str, Any]) -> None:
    schema = _ACTION_SCHEMAS.get(action_id)
    if schema is None:
        raise ValueError(f"Unsupported action id: {action_id}")
    for key, value_type in schema.items():
        if key not in payload:
            raise ValueError(f"Missing payload field '{key}' for action '{action_id}'")
        if not isinstance(payload[key], value_type):
            raise ValueError(f"Payload field '{key}' must be of type {value_type.__name__}")
