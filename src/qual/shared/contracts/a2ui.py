from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Callable, Protocol

A2UI_VERSION = 1
GENERIC_CARD_TYPE = "GenericCard"
UNKNOWN_CARD_TYPE = "UnknownCard"
REQUIRED_PRIMITIVE_BLOCKS: tuple[str, ...] = (
    "MarkdownBlock",
    "KeyValueBlock",
    "ListBlock",
    "TableBlock",
    "AlertBlock",
    "ProgressBlock",
    "CodeBlock",
)

_ALLOWED_ACTION_IDS: dict[str, dict[str, type]] = {
    "apply_patch": {"patch_id": str},
    "reject_patch": {"patch_id": str},
    "open_section": {"section_id": str},
    "open_corpus_item": {"item_id": str},
    "pin_to_context_set": {"item_id": str},
    "create_context_set": {"name": str},
    "run_agent": {"operation": str},
    "refresh_license": {},
    "export_document": {"format": str},
    "copy_to_clipboard": {},
}


@dataclass(frozen=True)
class A2UICapabilities:
    a2ui_version: int
    client_name: str
    cards_supported: tuple[str, ...]
    primitive_blocks_supported: tuple[str, ...]
    actions_supported: tuple[str, ...]
    max_payload_bytes: int
    supports_streaming: bool


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


class A2UISessionStore:
    def __init__(self) -> None:
        self._by_session: dict[str, A2UICapabilities] = {}

    def register(self, session_id: str, capabilities: A2UICapabilities) -> None:
        validate_capabilities(capabilities)
        self._by_session[session_id] = capabilities

    def get(self, session_id: str) -> A2UICapabilities:
        if session_id not in self._by_session:
            raise KeyError(f"Unknown session: {session_id}")
        return self._by_session[session_id]


def validate_capabilities(capabilities: A2UICapabilities) -> None:
    if capabilities.a2ui_version != A2UI_VERSION:
        raise ValueError("Unsupported A2UI version")
    if not capabilities.client_name:
        raise ValueError("client_name is required")
    if capabilities.max_payload_bytes <= 0:
        raise ValueError("max_payload_bytes must be positive")
    unsupported_blocks = set(capabilities.primitive_blocks_supported) - set(REQUIRED_PRIMITIVE_BLOCKS)
    if unsupported_blocks:
        raise ValueError(f"Unsupported primitive blocks: {sorted(unsupported_blocks)}")


def validate_primitive_block(block: dict[str, Any]) -> None:
    if block.get("type") not in REQUIRED_PRIMITIVE_BLOCKS:
        raise ValueError("Unsupported primitive block")


def validate_action_ref(action: ActionRef | dict[str, Any], capabilities: A2UICapabilities) -> ActionRef:
    if isinstance(action, dict):
        action = ActionRef(
            id=str(action.get("id", "")),
            label=str(action.get("label", action.get("id", ""))),
            payload=action.get("payload") if isinstance(action.get("payload"), dict) else {},
            confirm=action.get("confirm") if isinstance(action.get("confirm"), dict) else None,
            policy_sensitive=bool(action.get("policy_sensitive", False)),
        )
    if action.id not in capabilities.actions_supported:
        raise ValueError(f"Unsupported action: {action.id}")
    schema = _ALLOWED_ACTION_IDS.get(action.id)
    if schema is None:
        raise ValueError(f"Unknown action: {action.id}")
    for field_name, field_type in schema.items():
        if not isinstance(action.payload.get(field_name), field_type):
            raise ValueError(f"Invalid payload for action: {action.id}")
    return action


def execute_action_with_policy_gate(
    *,
    action: ActionRef,
    capabilities: A2UICapabilities,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    action = validate_action_ref(action, capabilities)
    if action.policy_sensitive and not policy_gate.allow_action(
        action.id,
        action.payload,
        policy_sensitive=action.policy_sensitive,
    ):
        raise PermissionError(f"Action blocked by policy gate: {action.id}")
    return executor(action)


def validate_generic_card(card: dict[str, Any]) -> None:
    if card.get("type") != GENERIC_CARD_TYPE:
        raise ValueError("Expected GenericCard")
    for block in card.get("blocks", []):
        if isinstance(block, dict):
            validate_primitive_block(block)


__all__ = [
    "ActionRef",
    "A2UICapabilities",
    "A2UISessionStore",
    "A2UI_VERSION",
    "GENERIC_CARD_TYPE",
    "PolicyGate",
    "REQUIRED_PRIMITIVE_BLOCKS",
    "UNKNOWN_CARD_TYPE",
    "execute_action_with_policy_gate",
    "validate_action_ref",
    "validate_capabilities",
    "validate_generic_card",
    "validate_primitive_block",
]
