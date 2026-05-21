from __future__ import annotations

from typing import Any

from exegesis_shared.contracts.actions import (
    ACTION_SELECTION_CONTRACT_VERSION,
    ALLOWED_ACTION_IDS,
    ActionRef,
    PolicyGate,
    canonicalize_action_order,
    execute_action_with_policy_gate,
    materialize_action_selection_contract,
    materialize_card_actions,
    materialize_cli_fallback_card,
    resolve_card_selection,
    resolve_card_selection_contract,
    resolve_card_selection_by_index,
    validate_action_ref,
)
from exegesis_shared.contracts.cards import (
    A2UICapabilities,
    A2UISessionStore,
    A2UI_VERSION,
    GENERIC_CARD_TYPE,
    PROPOSED_EDIT_CARD_TYPE,
    REQUIRED_PRIMITIVE_BLOCKS,
    UNKNOWN_CARD_TYPE,
    build_unknown_card,
    engine_prepare_card,
    materialize_proposed_edit_card,
    studio_materialize_card as _studio_materialize_card,
    validate_card_payload_size,
    validate_capabilities,
    validate_generic_card,
    validate_proposed_edit_card,
    validate_primitive_block,
)


def _deduped_sorted_actions(card: dict[str, Any]) -> list[dict[str, Any]]:
    """Backward-compatible alias for canonical card action materialization."""
    return materialize_card_actions(card)


def materialize_terminal_card(card: dict[str, Any]) -> dict[str, Any]:
    """Materialize the A2UI card shape consumed by CLI fallback renderers."""
    return materialize_cli_fallback_card(card)


def studio_materialize_card(payload: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    return materialize_terminal_card(_studio_materialize_card(payload, capabilities))


def render_terminal_card(card: dict[str, Any]) -> str:
    materialized = materialize_terminal_card(card)
    title = str(materialized.get("title", "<untitled>"))
    card_type = str(materialized.get("type", "Card"))
    lines = [f"[{card_type}] {title}"]
    for block in materialized.get("blocks", []):
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
    for slot, action in enumerate(materialized.get("actions", []), start=1):
        if isinstance(action, dict):
            lines.append(f"* {slot}. {action.get('label', action.get('id', 'action'))}")
    return "\n".join(lines)


__all__ = [
    "ActionRef",
    "A2UICapabilities",
    "A2UISessionStore",
    "A2UI_VERSION",
    "ACTION_SELECTION_CONTRACT_VERSION",
    "ALLOWED_ACTION_IDS",
    "GENERIC_CARD_TYPE",
    "PolicyGate",
    "PROPOSED_EDIT_CARD_TYPE",
    "REQUIRED_PRIMITIVE_BLOCKS",
    "UNKNOWN_CARD_TYPE",
    "canonicalize_action_order",
    "build_unknown_card",
    "engine_prepare_card",
    "execute_action_with_policy_gate",
    "materialize_action_selection_contract",
    "materialize_cli_fallback_card",
    "materialize_proposed_edit_card",
    "materialize_card_actions",
    "materialize_terminal_card",
    "render_terminal_card",
    "resolve_card_selection",
    "resolve_card_selection_contract",
    "resolve_card_selection_by_index",
    "studio_materialize_card",
    "validate_action_ref",
    "validate_card_payload_size",
    "validate_capabilities",
    "validate_generic_card",
    "validate_proposed_edit_card",
    "validate_primitive_block",
]
