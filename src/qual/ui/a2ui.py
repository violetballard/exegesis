from __future__ import annotations

import json
from typing import Any

from src.qual.shared.contracts.a2ui import A2UICapabilities
from src.qual.shared.contracts.a2ui import A2UISessionStore
from src.qual.shared.contracts.a2ui import A2UI_VERSION
from src.qual.shared.contracts.a2ui import ActionRef
from src.qual.shared.contracts.a2ui import GENERIC_CARD_TYPE
from src.qual.shared.contracts.a2ui import PolicyGate
from src.qual.shared.contracts.a2ui import REQUIRED_PRIMITIVE_BLOCKS
from src.qual.shared.contracts.a2ui import UNKNOWN_CARD_TYPE
from src.qual.shared.contracts.a2ui import execute_action_with_policy_gate
from src.qual.shared.contracts.a2ui import validate_action_ref
from src.qual.shared.contracts.a2ui import validate_capabilities
from src.qual.shared.contracts.a2ui import validate_generic_card
from src.qual.shared.contracts.a2ui import validate_primitive_block


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
