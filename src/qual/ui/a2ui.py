from __future__ import annotations

import json
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


def build_unknown_card(payload: dict[str, Any]) -> dict[str, Any]:
    card_type = str(payload.get("type", "unknown"))
    preview = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return {
        "type": UNKNOWN_CARD_TYPE,
        "title": f"Unsupported card type: {card_type}",
        "blocks": [{"type": "CodeBlock", "language": "json", "code": preview}],
        "actions": [{"id": "copy_to_clipboard", "label": "Copy JSON", "payload": {"text": preview}}],
    }


def engine_prepare_card(payload: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    validate_capabilities(capabilities)
    card_type = str(payload.get("type", GENERIC_CARD_TYPE))
    if card_type in capabilities.cards_supported or card_type == GENERIC_CARD_TYPE:
        return dict(payload)
    return {
        "type": GENERIC_CARD_TYPE,
        "title": f"Fallback view for {card_type}",
        "blocks": [
            {
                "type": "AlertBlock",
                "severity": "info",
                "message": f"{card_type} is not supported by this client.",
            }
        ],
        "actions": [],
    }


def studio_materialize_card(payload: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    validate_capabilities(capabilities)
    card_type = str(payload.get("type", ""))
    if card_type not in capabilities.cards_supported and card_type != GENERIC_CARD_TYPE:
        return build_unknown_card(payload)
    card = dict(payload)
    actions = []
    for action in card.get("actions", []):
        if not isinstance(action, dict):
            continue
        try:
            validated = validate_action_ref(action, capabilities)
        except ValueError:
            continue
        actions.append(
            {
                "id": validated.id,
                "label": validated.label,
                "payload": dict(validated.payload),
                **({"confirm": validated.confirm} if validated.confirm is not None else {}),
                **({"policy_sensitive": True} if validated.policy_sensitive else {}),
            }
        )
    card["actions"] = sorted(actions, key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    return card


def render_terminal_card(card: dict[str, Any]) -> str:
    title = str(card.get("title", "<untitled>"))
    card_type = str(card.get("type", "Card"))
    lines = [f"[{card_type}] {title}"]
    for block in card.get("blocks", []):
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type == "MarkdownBlock":
            lines.append(str(block.get("markdown", "")))
        elif block_type == "AlertBlock":
            lines.append(f"{block.get('severity', 'info').upper()}: {block.get('message', '')}")
        elif block_type == "CodeBlock":
            lines.append(str(block.get("code", "")))
        elif block_type == "ProgressBlock":
            lines.append(f"{block.get('title', 'progress')}: {block.get('status_text', '')}")
        elif block_type == "KeyValueBlock":
            items = block.get("items", [])
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        lines.append(f"- {item.get('key', '')}: {item.get('value', '')}")
        elif block_type == "ListBlock":
            items = block.get("items", [])
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, str):
                        lines.append(f"- {item}")
                    elif isinstance(item, dict):
                        lines.append(f"- {item.get('label', '')}")
        elif block_type == "TableBlock":
            columns = block.get("columns", [])
            rows = block.get("rows", [])
            if isinstance(columns, list):
                lines.append(" | ".join(str(value) for value in columns))
            if isinstance(rows, list):
                for row in rows:
                    if isinstance(row, list):
                        lines.append(" | ".join(str(value) for value in row))
    for action in card.get("actions", []):
        if isinstance(action, dict):
            lines.append(f"* {action.get('label', action.get('id', 'action'))}")
    return "\n".join(lines)


__all__ = [
    "ActionRef",
    "A2UICapabilities",
    "A2UISessionStore",
    "A2UI_VERSION",
    "GENERIC_CARD_TYPE",
    "PolicyGate",
    "REQUIRED_PRIMITIVE_BLOCKS",
    "UNKNOWN_CARD_TYPE",
    "build_unknown_card",
    "engine_prepare_card",
    "execute_action_with_policy_gate",
    "render_terminal_card",
    "studio_materialize_card",
    "validate_action_ref",
    "validate_capabilities",
    "validate_generic_card",
    "validate_primitive_block",
]
