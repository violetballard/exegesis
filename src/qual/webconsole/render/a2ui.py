from __future__ import annotations

from typing import Any

from src.qual.webconsole.render.safe_html import json_pretty

GENERIC_CARD_TYPE = "GenericCard"
UNKNOWN_CARD_TYPE = "UnknownCard"

PRIMITIVE_BLOCK_TYPES: tuple[str, ...] = (
    "MarkdownBlock",
    "KeyValueBlock",
    "ListBlock",
    "TableBlock",
    "AlertBlock",
    "ProgressBlock",
    "CodeBlock",
)

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

_BLOCK_SET = set(PRIMITIVE_BLOCK_TYPES)
_ACTION_SET = set(ALLOWED_ACTION_IDS)
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


def materialize_card(raw_card: dict[str, Any]) -> dict[str, Any]:
    """Return a client-renderable safe card shape for web console rendering."""
    card_type = str(raw_card.get("type", "")).strip()
    if card_type != GENERIC_CARD_TYPE:
        return build_unknown_card(raw_card)

    title = str(raw_card.get("title", "")).strip() or "Untitled"
    subtitle = raw_card.get("subtitle")
    blocks = _safe_blocks(raw_card.get("blocks"))
    actions = _safe_actions(raw_card.get("actions"))

    materialized: dict[str, Any] = {
        "type": GENERIC_CARD_TYPE,
        "title": title,
        "blocks": blocks,
        "actions": actions,
    }
    if isinstance(subtitle, str) and subtitle.strip():
        materialized["subtitle"] = subtitle
    return materialized


def build_unknown_card(raw_card: dict[str, Any]) -> dict[str, Any]:
    card_type = str(raw_card.get("type", "<missing>"))
    blocks = _discover_nested_primitive_blocks(raw_card)
    blocks.append(
        {
            "type": "CodeBlock",
            "language": "json",
            "code": json_pretty(raw_card),
            "collapsed": True,
        }
    )
    return {
        "type": UNKNOWN_CARD_TYPE,
        "title": f"Unsupported card type: {card_type}",
        "blocks": blocks,
        "actions": [
            {
                "id": "copy_to_clipboard",
                "label": "Copy JSON",
                "payload": {"text": json_pretty(raw_card)},
            }
        ],
    }


def _safe_blocks(raw_blocks: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_blocks, list):
        return []
    safe: list[dict[str, Any]] = []
    for block in raw_blocks:
        if not isinstance(block, dict):
            continue
        block_type = str(block.get("type", ""))
        if block_type not in _BLOCK_SET:
            continue
        safe.append(block)
    return safe


def _safe_actions(raw_actions: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_actions, list):
        return []
    safe: list[dict[str, Any]] = []
    for action in raw_actions:
        if not isinstance(action, dict):
            continue
        action_id = str(action.get("id", ""))
        label = action.get("label")
        payload = action.get("payload")
        if action_id not in _ACTION_SET:
            continue
        if not isinstance(label, str) or not label.strip():
            continue
        if not isinstance(payload, dict):
            continue
        if not _payload_matches_schema(action_id, payload):
            continue
        safe.append(action)
    return safe


def _discover_nested_primitive_blocks(raw_card: dict[str, Any]) -> list[dict[str, Any]]:
    nested = raw_card.get("blocks")
    if not isinstance(nested, list):
        return []
    blocks: list[dict[str, Any]] = []
    for block in nested:
        if not isinstance(block, dict):
            continue
        if str(block.get("type", "")) in _BLOCK_SET:
            blocks.append(block)
    return blocks


def _payload_matches_schema(action_id: str, payload: dict[str, Any]) -> bool:
    schema = _ACTION_SCHEMAS.get(action_id)
    if schema is None:
        return False
    for key, value_type in schema.items():
        if key not in payload:
            return False
        if not isinstance(payload[key], value_type):
            return False
    return True
