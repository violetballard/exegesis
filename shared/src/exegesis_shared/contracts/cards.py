from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from exegesis_shared.contracts.actions import (
    ALLOWED_ACTION_IDS,
    materialize_cli_fallback_card,
    validate_action_ref,
)

A2UI_VERSION = 1
GENERIC_CARD_TYPE = "GenericCard"
UNKNOWN_CARD_TYPE = "UnknownCard"
PROPOSED_EDIT_CARD_TYPE = "ProposedEditCard"

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
    if card_type == PROPOSED_EDIT_CARD_TYPE:
        prepared = materialize_proposed_edit_card(card)
        if card_type in set(capabilities.cards_supported):
            return prepared
        card = prepared
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
        return materialize_cli_fallback_card(_studio_filter_actions(card, capabilities))
    if card_type == PROPOSED_EDIT_CARD_TYPE:
        card = materialize_proposed_edit_card(card)
        return materialize_cli_fallback_card(_studio_filter_actions(card, capabilities))
    if card_type in set(capabilities.cards_supported):
        return materialize_cli_fallback_card(_studio_filter_actions(card, capabilities))
    return materialize_cli_fallback_card(_studio_filter_actions(build_unknown_card(card), capabilities))


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


def materialize_proposed_edit_card(card: dict[str, Any]) -> dict[str, Any]:
    validate_proposed_edit_card(card, strict_actions=False)
    materialized = dict(card)
    patch_id = str(materialized["patch_id"]).strip()
    materialized["patch_id"] = patch_id
    actions = list(materialized.get("actions", []))
    if not _has_patch_action(actions, "apply_patch", patch_id):
        actions.append({"id": "apply_patch", "label": "Apply patch", "payload": {"patch_id": patch_id}})
    if not _has_patch_action(actions, "reject_patch", patch_id):
        actions.append({"id": "reject_patch", "label": "Reject patch", "payload": {"patch_id": patch_id}})
    materialized["actions"] = actions
    validate_proposed_edit_card(materialized)
    return materialized


def validate_proposed_edit_card(card: dict[str, Any], *, strict_actions: bool = True) -> None:
    if card.get("type") != PROPOSED_EDIT_CARD_TYPE:
        raise ValueError("Card type must be ProposedEditCard")
    patch_id = card.get("patch_id")
    if not isinstance(patch_id, str) or not patch_id.strip():
        raise ValueError("ProposedEditCard patch_id is required")
    title = card.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("ProposedEditCard title is required")
    blocks = card.get("blocks")
    if not isinstance(blocks, list):
        raise ValueError("ProposedEditCard blocks must be a list")
    for block in blocks:
        validate_primitive_block(block)
    actions = card.get("actions", [])
    if not isinstance(actions, list):
        raise ValueError("ProposedEditCard actions must be a list")
    expected_patch_id = patch_id.strip()
    for action in actions:
        if not isinstance(action, dict):
            if strict_actions:
                validate_action_ref(action)
            continue
        action_id = action.get("id")
        if action_id in {"apply_patch", "reject_patch"}:
            payload = action.get("payload")
            action_patch_id = payload.get("patch_id") if isinstance(payload, dict) else None
            if action_patch_id != expected_patch_id:
                raise ValueError(f"{action_id} payload patch_id must match ProposedEditCard patch_id")
        if strict_actions:
            validate_action_ref(action)


def validate_primitive_block(block: Any) -> None:
    if not isinstance(block, dict):
        raise ValueError("Primitive block must be an object")
    block_type = str(block.get("type", ""))
    if block_type not in _PRIMITIVE_BLOCK_SET:
        raise ValueError(f"Unsupported primitive block: {block_type}")


def _has_patch_action(actions: list[Any], action_id: str, patch_id: str) -> bool:
    for action in actions:
        if not isinstance(action, dict) or action.get("id") != action_id:
            continue
        payload = action.get("payload")
        if isinstance(payload, dict) and payload.get("patch_id") == patch_id:
            return True
    return False


def _studio_filter_actions(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    filtered = dict(card)
    actions = []
    seen_actions: set[str] = set()
    for action in card.get("actions", []):
        try:
            validate_action_ref(action)
        except ValueError:
            continue
        if action.get("id") not in set(capabilities.actions_supported):
            continue
        action_key = json.dumps(action, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        if action_key in seen_actions:
            continue
        seen_actions.add(action_key)
        actions.append(action)
    filtered["actions"] = sorted(
        actions,
        key=lambda action: json.dumps(action, sort_keys=True, separators=(",", ":"), ensure_ascii=True),
    )
    return filtered
