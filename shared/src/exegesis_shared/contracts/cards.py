from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from exegesis_shared.contracts.actions import ALLOWED_ACTION_IDS, ActionRef, validate_action_ref

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
    fallback = {
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
    fallback["actions"] = _canonicalize_actions(_valid_supported_actions(card.get("actions", []), capabilities))
    return fallback


def studio_materialize_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    card_type = str(card.get("type", "")).strip()
    if card_type == GENERIC_CARD_TYPE:
        validate_generic_card(card, strict_actions=False)
        return _studio_filter_actions(card, capabilities)
    if card_type in set(capabilities.cards_supported):
        return _studio_filter_actions(card, capabilities)
    return build_unknown_card(card, capabilities)


def build_unknown_card(raw_card: dict[str, Any], capabilities: A2UICapabilities | None = None) -> dict[str, Any]:
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
    actions = [{"id": "copy_to_clipboard", "label": "Copy JSON", "payload": {"text": json.dumps(raw_card)}}]
    if capabilities is not None:
        actions = _valid_supported_actions(actions, capabilities)
    return {
        "type": UNKNOWN_CARD_TYPE,
        "title": f"Unsupported card type: {type_name}",
        "blocks": blocks,
        "actions": actions,
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
    actions = _valid_supported_actions(card.get("actions", []), capabilities)
    filtered["actions"] = _canonicalize_actions(actions)
    return filtered


def _valid_supported_actions(raw_actions: Any, capabilities: A2UICapabilities) -> list[dict[str, Any]]:
    if not isinstance(raw_actions, list):
        return []
    actions = []
    supported = set(capabilities.actions_supported)
    for action in raw_actions:
        if not isinstance(action, dict):
            continue
        try:
            validate_action_ref(action)
        except ValueError:
            continue
        if action.get("id") not in supported:
            continue
        actions.append(action)
    return actions


def _canonicalize_actions(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen_actions: set[str] = set()
    canonical = []
    for action in actions:
        action_key = json.dumps(action, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        if action_key in seen_actions:
            continue
        seen_actions.add(action_key)
        canonical.append(action)
    return sorted(
        canonical,
        key=_action_sort_key,
    )


def materialize_action_slots(card: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    slots: list[dict[str, Any]] = []
    for index, action in enumerate(_canonicalize_actions(_valid_actions(card.get("actions", []))), start=1):
        slots.append(
            {
                "slot": index,
                "command": str(index),
                "action": action,
                "aliases": _action_aliases(action),
            }
        )
    return tuple(slots)


def resolve_action_selection(card: dict[str, Any], selection: str | int) -> ActionRef:
    token = str(selection).strip()
    for slot in materialize_action_slots(card):
        action = slot["action"]
        aliases = {slot["command"], *slot["aliases"]}
        if token in aliases:
            return ActionRef(
                id=str(action["id"]),
                label=str(action["label"]),
                payload=dict(action["payload"]),
                confirm=action.get("confirm") if isinstance(action.get("confirm"), dict) else None,
                policy_sensitive=bool(action.get("policy_sensitive", False)),
            )
    raise KeyError(f"Unknown action selection: {selection}")


def materialize_patch_selection_envelope(card: dict[str, Any]) -> dict[str, Any]:
    preview_slots = []
    decision_slots = []
    for slot in materialize_action_slots(card):
        action = slot["action"]
        action_id = action.get("id")
        if action_id == "preview_patch":
            preview_slots.append(slot)
        elif action_id in {"apply_patch", "reject_patch"}:
            decision_slots.append(slot)
    if not preview_slots and not decision_slots:
        raise ValueError("Patch selection requires preview_patch, apply_patch, or reject_patch actions")
    return {
        "type": "PatchActionSelection",
        "preview": {
            "command": "preview",
            "actions": [slot["command"] for slot in preview_slots],
        },
        "decision": {
            "actions": [slot["command"] for slot in decision_slots],
        },
        "actions": [*preview_slots, *decision_slots],
    }


def _valid_actions(raw_actions: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_actions, list):
        return []
    actions = []
    for action in raw_actions:
        if not isinstance(action, dict):
            continue
        try:
            validate_action_ref(action)
        except ValueError:
            continue
        actions.append(action)
    return actions


def _action_aliases(action: dict[str, Any]) -> tuple[str, ...]:
    action_id = str(action.get("id", ""))
    aliases = [action_id]
    if action_id == "preview_patch":
        aliases.append("preview")
    elif action_id == "apply_patch":
        aliases.append("apply")
    elif action_id == "reject_patch":
        aliases.append("reject")
    return tuple(aliases)


def _action_sort_key(action: dict[str, Any]) -> tuple[int, str]:
    patch_order = {
        "preview_patch": 0,
        "apply_patch": 1,
        "reject_patch": 2,
    }
    action_id = str(action.get("id", ""))
    if action_id in patch_order:
        return (patch_order[action_id], "")
    return (10, json.dumps(action, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
