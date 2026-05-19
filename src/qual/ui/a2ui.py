from __future__ import annotations

from typing import Any

from exegesis_shared.contracts.actions import (
    ACTION_SELECTION_CONTRACT_VERSION,
    ALLOWED_ACTION_IDS,
    CANONICAL_ACTION_GROUPS,
    CANONICAL_ACTION_ORDER,
    CANONICAL_ACTION_PRIORITY,
    CANONICAL_AGENT_ACTIONS,
    CANONICAL_NAVIGATION_ACTIONS,
    CANONICAL_PATCH_WORKFLOW_ACTIONS,
    CANONICAL_UTILITY_ACTIONS,
    UNKNOWN_ACTION_PRIORITY,
    ActionRef,
    PolicyGate,
    canonical_action_identity_key as _canonical_action_identity_key,
    canonical_action_key as _canonical_action_key,
    canonicalize_action_order,
    execute_action_with_policy_gate,
    materialize_action_order,
    materialize_action_selection_contract,
    materialize_action_sequence,
    materialize_action_slots,
    materialize_card_actions,
    materialize_cli_fallback_card,
    resolve_card_selection,
    resolve_card_selection_by_index,
    validate_action_ref,
)
from exegesis_shared.contracts.cards import (
    A2UICapabilities,
    A2UISessionStore,
    A2UI_VERSION,
    GENERIC_CARD_TYPE,
    REQUIRED_PRIMITIVE_BLOCKS,
    UNKNOWN_CARD_TYPE,
    build_unknown_card,
    engine_prepare_card,
    studio_materialize_card as _studio_materialize_card,
    validate_capabilities,
    validate_generic_card,
    validate_primitive_block,
)


def _deduped_sorted_actions(card: dict[str, Any]) -> list[dict[str, Any]]:
    """Backward-compatible alias for canonical card action materialization."""
    return materialize_card_actions(card)


def studio_materialize_card(payload: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    return materialize_cli_fallback_card(_studio_materialize_card(payload, capabilities))


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
    for slot in materialize_action_slots(card):
        action = slot["action"]
        lines.append(f"* {slot['slot']}. {action.get('label', action.get('id', 'action'))}")
    return "\n".join(lines)


__all__ = [
    "ActionRef",
    "A2UICapabilities",
    "A2UISessionStore",
    "A2UI_VERSION",
    "ACTION_SELECTION_CONTRACT_VERSION",
    "ALLOWED_ACTION_IDS",
    "CANONICAL_ACTION_GROUPS",
    "CANONICAL_ACTION_PRIORITY",
    "CANONICAL_ACTION_ORDER",
    "CANONICAL_AGENT_ACTIONS",
    "CANONICAL_NAVIGATION_ACTIONS",
    "CANONICAL_PATCH_WORKFLOW_ACTIONS",
    "CANONICAL_UTILITY_ACTIONS",
    "GENERIC_CARD_TYPE",
    "PolicyGate",
    "REQUIRED_PRIMITIVE_BLOCKS",
    "UNKNOWN_CARD_TYPE",
    "UNKNOWN_ACTION_PRIORITY",
    "canonicalize_action_order",
    "_canonical_action_identity_key",
    "_canonical_action_key",
    "build_unknown_card",
    "engine_prepare_card",
    "execute_action_with_policy_gate",
    "materialize_action_order",
    "materialize_action_selection_contract",
    "materialize_action_sequence",
    "materialize_action_slots",
    "materialize_cli_fallback_card",
    "materialize_card_actions",
    "render_terminal_card",
    "resolve_card_selection",
    "resolve_card_selection_by_index",
    "studio_materialize_card",
    "validate_action_ref",
    "validate_capabilities",
    "validate_generic_card",
    "validate_primitive_block",
]
