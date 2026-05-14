from __future__ import annotations

from typing import Any

from exegesis_shared.contracts.actions import ActionRef, PolicyGate, execute_action_with_policy_gate, validate_action_ref
from exegesis_shared.contracts.cards import (
    A2UICapabilities,
    A2UISessionStore,
    A2UI_VERSION,
    GENERIC_CARD_TYPE,
    REQUIRED_PRIMITIVE_BLOCKS,
    UNKNOWN_CARD_TYPE,
    build_unknown_card,
    engine_prepare_card,
    studio_materialize_card,
    validate_capabilities,
    validate_generic_card,
    validate_primitive_block,
)


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
