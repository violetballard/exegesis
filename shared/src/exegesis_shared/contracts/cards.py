from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from exegesis_shared.contracts.actions import ALLOWED_ACTION_IDS, validate_action_ref

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

_PRIMITIVE_BLOCK_SET = set(REQUIRED_PRIMITIVE_BLOCKS)
_ALLOWED_ACTION_SET = set(ALLOWED_ACTION_IDS)


@dataclass(frozen=True)
class A2UICapabilities:
    a2ui_version: int
    client_name: str
    cards_supported: tuple[str, ...]
    primitive_blocks_supported: tuple[str, ...]
    actions_supported: tuple[str, ...]
    max_payload_bytes: int
    supports_streaming: bool


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


def _studio_filter_actions(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    filtered = dict(card)
    actions = []
    for action in card.get("actions", []):
        try:
            validate_action_ref(action)
        except ValueError:
            continue
        if action.get("id") not in set(capabilities.actions_supported):
            continue
        actions.append(action)
    filtered["actions"] = sorted(
        actions,
        key=lambda action: json.dumps(action, sort_keys=True, separators=(",", ":"), ensure_ascii=True),
    )
    return filtered
