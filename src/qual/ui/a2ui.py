from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Protocol

A2UI_VERSION = 1
GENERIC_CARD_TYPE = "GenericCard"
UNKNOWN_CARD_TYPE = "UnknownCard"

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

REQUIRED_PRIMITIVE_BLOCKS: tuple[str, ...] = (
    "MarkdownBlock",
    "KeyValueBlock",
    "ListBlock",
    "TableBlock",
    "AlertBlock",
    "ProgressBlock",
    "CodeBlock",
)

_PRIMITIVE_BLOCK_SET = set(REQUIRED_PRIMITIVE_BLOCKS)
_ALLOWED_ACTION_SET = set(ALLOWED_ACTION_IDS)

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
        if capabilities.a2ui_version < 1:
            raise ValueError("Unsupported a2ui version")
        self._by_session[session_id] = capabilities

    def get(self, session_id: str) -> A2UICapabilities:
        if session_id not in self._by_session:
            raise KeyError(f"Unknown session: {session_id}")
        return self._by_session[session_id]


def validate_capabilities(capabilities: A2UICapabilities) -> None:
    if capabilities.a2ui_version < 1:
        raise ValueError("Unsupported a2ui version")
    if not capabilities.client_name.strip():
        raise ValueError("client_name is required")
    if capabilities.max_payload_bytes <= 0:
        raise ValueError("max_payload_bytes must be positive")
    if not _PRIMITIVE_BLOCK_SET.issubset(set(capabilities.primitive_blocks_supported)):
        raise ValueError("Missing required primitive block support")
    for action_id in capabilities.actions_supported:
        if action_id not in _ALLOWED_ACTION_SET:
            raise ValueError(f"Unknown action in capabilities: {action_id}")


def engine_prepare_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    card_type = str(card.get("type", "")).strip()
    if card_type == GENERIC_CARD_TYPE:
        validate_generic_card(card)
        return card

    if card_type in set(capabilities.cards_supported):
        return card

    # Safe fallback for unsupported specialized cards.
    return {
        "type": GENERIC_CARD_TYPE,
        "title": f"Fallback view for {card_type or 'Unknown'}",
        "blocks": [
            {
                "type": "AlertBlock",
                "severity": "info",
                "title": "Card fallback",
                "message": "Rendered as GenericCard because client does not support this specialized card.",
            },
            {
                "type": "CodeBlock",
                "language": "json",
                "code": json.dumps(card, separators=(",", ":"), ensure_ascii=True),
            },
        ],
        "actions": [],
    }


def studio_materialize_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    card_type = str(card.get("type", "")).strip()
    if card_type == GENERIC_CARD_TYPE:
        validate_generic_card(card, strict_actions=False)
        return _studio_filter_actions(card, capabilities)
    if card_type in set(capabilities.cards_supported):
        return _studio_filter_actions(card, capabilities)
    return build_unknown_card(card)


def build_unknown_card(raw_card: dict[str, Any]) -> dict[str, Any]:
    type_name = str(raw_card.get("type", "<missing>"))
    nested_blocks = raw_card.get("blocks")
    blocks: list[dict[str, Any]] = []
    if isinstance(nested_blocks, list):
        for block in nested_blocks:
            if isinstance(block, dict) and str(block.get("type", "")) in _PRIMITIVE_BLOCK_SET:
                blocks.append(block)
    blocks.append(
        {
            "type": "CodeBlock",
            "language": "json",
            "code": json.dumps(raw_card, indent=2, sort_keys=True, ensure_ascii=True),
            "collapsed": True,
        }
    )
    return {
        "type": UNKNOWN_CARD_TYPE,
        "title": f"Unsupported card type: {type_name}",
        "blocks": blocks,
        "actions": [
            {"id": "copy_to_clipboard", "label": "Copy JSON", "payload": {"text": json.dumps(raw_card)}}
        ],
    }


def validate_generic_card(card: dict[str, Any], *, strict_actions: bool = True) -> None:
    if card.get("type") != GENERIC_CARD_TYPE:
        raise ValueError("Card type must be GenericCard")
    title = card.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("GenericCard title is required")
    blocks = card.get("blocks")
    if not isinstance(blocks, list):
        raise ValueError("GenericCard blocks must be a list")
    for block in blocks:
        validate_primitive_block(block)
    actions = card.get("actions", [])
    if not isinstance(actions, list):
        raise ValueError("GenericCard actions must be a list")
    if strict_actions:
        for action in actions:
            validate_action_ref(action)


def validate_primitive_block(block: Any) -> None:
    if not isinstance(block, dict):
        raise ValueError("Primitive block must be an object")
    block_type = str(block.get("type", ""))
    if block_type not in _PRIMITIVE_BLOCK_SET:
        raise ValueError(f"Unsupported primitive block: {block_type}")


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
    capabilities: A2UICapabilities,
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
            lines.append("[table]")
    return "\n".join(lines)


def _studio_filter_actions(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    actions = card.get("actions")
    if not isinstance(actions, list):
        return card
    supported = set(capabilities.actions_supported)
    filtered: list[dict[str, Any]] = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        action_id = str(action.get("id", ""))
        payload = action.get("payload")
        if action_id not in supported or not isinstance(payload, dict):
            continue
        try:
            _validate_action_payload(action_id, payload)
        except ValueError:
            continue
        filtered.append(action)
    out = dict(card)
    out["actions"] = filtered
    return out


def _validate_action_payload(action_id: str, payload: dict[str, Any]) -> None:
    schema = _ACTION_SCHEMAS.get(action_id)
    if schema is None:
        raise ValueError(f"No schema for action id: {action_id}")
    for key, value_type in schema.items():
        if key not in payload:
            raise ValueError(f"Missing payload field for {action_id}: {key}")
        if not isinstance(payload[key], value_type):
            raise ValueError(f"Invalid payload type for {action_id}:{key}")
