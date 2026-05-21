from __future__ import annotations

from typing import Any

from exegesis_shared.contracts.actions import (
    ACTION_SELECTION_CONTRACT_VERSION,
    ALLOWED_ACTION_IDS,
    ActionRef,
    CompletePatchReviewActions,
    PATCH_DECISION_CONTRACT_VERSION,
    PATCH_PREVIEW_CONTRACT_VERSION,
    PATCH_REVIEW_ACTION_AUTHORITY,
    PATCH_REVIEW_CONTRACT_VERSION,
    PATCH_REVIEW_DECISION_POLICY,
    PATCH_REVIEW_DEMO_PATH_STEP,
    PATCH_REVIEW_EXECUTION_POLICY,
    PATCH_REVIEW_FLOW,
    PATCH_REVIEW_REQUIRED_PARTS,
    PatchReviewActionSelection,
    PolicyGate,
    action_ref_from_selection,
    build_patch_decision_selection,
    build_complete_patch_review_contract,
    build_patch_preview_selection,
    build_patch_review_availability,
    build_patch_review_contract,
    build_patch_review_selection,
    canonicalize_action_order,
    complete_patch_review_action_from_card,
    complete_patch_review_actions_from_contract,
    complete_patch_review_actions_from_card,
    complete_patch_review_action_refs_from_contract,
    execute_complete_patch_review_action_with_policy_gate,
    execute_action_with_policy_gate,
    execute_patch_review_selection_with_policy_gate,
    engine_authoritative_action_ref,
    materialize_action_selection_contract,
    materialize_card_actions,
    materialize_cli_fallback_card,
    materialize_patch_decision_contract,
    materialize_patch_preview_contract,
    patch_decision_action_ref_from_selection,
    patch_preview_action_ref_from_selection,
    patch_review_action_ref_from_selection,
    patch_review_action_selection_from_selection,
    patch_review_availability_from_contract,
    patch_review_action_refs_from_contract,
    patch_review_cli_command_lookup_from_contract,
    patch_review_cli_control_map_from_contract,
    patch_review_control_actions_from_contract,
    patch_review_decision_controls_from_contract,
    patch_review_next_control_from_contract,
    patch_review_control_plan_from_contract,
    patch_review_control_summary_from_contract,
    patch_review_control_slots_from_contract,
    patch_review_selection_from_cli_command,
    resolve_card_selection,
    resolve_card_selection_contract,
    resolve_card_selection_by_index,
    resolve_patch_decision_action,
    resolve_patch_decision_selection,
    resolve_patch_preview_action,
    resolve_patch_preview_selection,
    resolve_patch_review_contract,
    resolve_patch_review_selection,
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
from exegesis_shared.contracts.events import (
    A2UI_EVENT_CONTRACT_VERSION,
    A2UI_STREAM_EVENT_TYPES,
    build_action_resolved_event,
    build_action_resolved_event_from_selection,
    build_action_selected_event,
    build_action_selected_event_from_selection,
    build_card_published_event,
    build_complete_patch_review_action_resolved_event,
    build_complete_patch_review_action_selected_event,
    stream_event_key,
    validate_stream_event,
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
    review = materialized.get("patch_review")
    patch_id = materialized.get("patch_id")
    if isinstance(review, dict) and isinstance(patch_id, str) and patch_id.strip():
        summary = patch_review_control_summary_from_contract(
            materialized,
            review,
            patch_id=patch_id,
        )
        lines.append(f"Patch review flow: {summary['flow']}")
        lines.append(f"Patch review decision policy: {summary['decision_policy']}")
        lines.append(f"Patch review action authority: {summary['action_authority']}")
        lines.append(f"Patch review demo path step: {summary['demo_path_step']}")
        lines.append(
            "Patch review status: "
            f"{'complete' if summary['is_complete'] else 'incomplete'}"
        )
        ordered_controls = [
            f"{entry['control']}={entry['slot']}"
            for entry in summary["order"]
            if isinstance(entry, dict) and "control" in entry and "slot" in entry
        ]
        if ordered_controls:
            lines.append(f"Patch review controls: {', '.join(ordered_controls)}")
            cli_controls = patch_review_cli_control_map_from_contract(
                materialized,
                review,
                patch_id=patch_id,
            )
            command_map = [
                _format_patch_review_cli_command_entry(entry)
                for entry in cli_controls["controls"]
                if isinstance(entry, dict)
            ]
            if command_map:
                lines.append(f"Patch review CLI commands: {', '.join(command_map)}")
            alias_map = [
                _format_patch_review_cli_alias_entry(entry)
                for entry in cli_controls["controls"]
                if isinstance(entry, dict)
            ]
            if alias_map:
                lines.append(f"Patch review CLI aliases: {', '.join(alias_map)}")
            command_lookup = patch_review_cli_command_lookup_from_contract(
                materialized,
                review,
                patch_id=patch_id,
            )
            if command_lookup["commands"]:
                lookup_map = [
                    f"{command}->{entry['control']}"
                    for command, entry in sorted(command_lookup["commands"].items())
                    if isinstance(entry, dict)
                ]
                lines.append(f"Patch review CLI command lookup: {', '.join(lookup_map)}")
            next_control = patch_review_next_control_from_contract(
                materialized,
                review,
                patch_id=patch_id,
            )
            if isinstance(next_control, dict):
                next_label = next_control["control"]
                next_command = next_control.get("command")
                if isinstance(next_command, str) and next_command:
                    lines.append(f"Patch review next control: {next_label}={next_command}")
                else:
                    lines.append(f"Patch review next control: {next_label}=missing")
            decision_controls = patch_review_decision_controls_from_contract(
                materialized,
                review,
                patch_id=patch_id,
            )
            decision_command_map = [
                _format_patch_review_cli_command_entry(entry)
                for entry in decision_controls["controls"]
                if isinstance(entry, dict)
            ]
            if decision_command_map:
                lines.append(
                    "Patch review decision controls: "
                    f"{', '.join(decision_command_map)}"
                )
            gated_controls = [
                entry["control"]
                for entry in summary["order"]
                if isinstance(entry, dict)
                and entry.get("execution_policy", {}).get("policy_gate") == "required"
            ]
            if gated_controls:
                lines.append(f"Policy-gated patch controls: {', '.join(gated_controls)}")
        control_plan = [
            _format_patch_review_control_plan_entry(entry)
            for entry in summary["control_plan"]
            if isinstance(entry, dict)
        ]
        if control_plan:
            lines.append(f"Patch review control plan: {', '.join(control_plan)}")
        if summary["missing"]:
            lines.append(f"Patch review missing controls: {', '.join(summary['missing'])}")
            next_required = summary.get("next_required")
            if isinstance(next_required, str) and next_required:
                lines.append(f"Patch review next required control: {next_required}")
                aliases = summary.get("next_required_command_aliases", [])
                if isinstance(aliases, list) and aliases:
                    lines.append(
                        "Patch review next required CLI aliases: "
                        f"{'/'.join(str(alias) for alias in aliases)}"
                    )
    for slot, action in enumerate(materialized.get("actions", []), start=1):
        if isinstance(action, dict):
            label = str(action.get("label", action.get("id", "action")))
            confirm = action.get("confirm")
            if isinstance(confirm, dict):
                title = confirm.get("title")
                if isinstance(title, str) and title.strip():
                    label = f"{label} [confirm: {title.strip()}]"
            lines.append(f"* {slot}. {label}")
    return "\n".join(lines)


def _format_patch_review_control_plan_entry(entry: dict[str, Any]) -> str:
    control = str(entry.get("control", "control"))
    status = str(entry.get("status", "missing"))
    if status != "available":
        return f"{control}=missing"
    parts = [f"{control}=available"]
    slot = entry.get("slot")
    if isinstance(slot, int):
        parts.append(f"slot {slot}")
    aliases = entry.get("command_aliases")
    if isinstance(aliases, list) and aliases:
        parts.append(f"aliases {'/'.join(str(alias) for alias in aliases)}")
    policy = entry.get("execution_policy")
    if isinstance(policy, dict):
        if policy.get("requires_confirmation"):
            parts.append("confirm")
        if policy.get("policy_gate") == "required":
            parts.append("policy-gated")
    return f"{parts[0]}({', '.join(parts[1:])})" if len(parts) > 1 else parts[0]


def _format_patch_review_cli_command_entry(entry: dict[str, Any]) -> str:
    control = str(entry.get("control", "control"))
    command = str(entry.get("command", ""))
    return f"{control}={command}"


def _format_patch_review_cli_alias_entry(entry: dict[str, Any]) -> str:
    control = str(entry.get("control", "control"))
    aliases = entry.get("command_aliases", [])
    if not isinstance(aliases, list) or not aliases:
        return f"{control}=none"
    return f"{control}={'/'.join(str(alias) for alias in aliases)}"


__all__ = [
    "ActionRef",
    "CompletePatchReviewActions",
    "A2UICapabilities",
    "A2UI_EVENT_CONTRACT_VERSION",
    "A2UI_STREAM_EVENT_TYPES",
    "A2UISessionStore",
    "A2UI_VERSION",
    "ACTION_SELECTION_CONTRACT_VERSION",
    "ALLOWED_ACTION_IDS",
    "PATCH_DECISION_CONTRACT_VERSION",
    "PATCH_PREVIEW_CONTRACT_VERSION",
    "PATCH_REVIEW_ACTION_AUTHORITY",
    "PATCH_REVIEW_CONTRACT_VERSION",
    "PATCH_REVIEW_DECISION_POLICY",
    "PATCH_REVIEW_DEMO_PATH_STEP",
    "PATCH_REVIEW_EXECUTION_POLICY",
    "PATCH_REVIEW_FLOW",
    "PATCH_REVIEW_REQUIRED_PARTS",
    "GENERIC_CARD_TYPE",
    "PatchReviewActionSelection",
    "PolicyGate",
    "PROPOSED_EDIT_CARD_TYPE",
    "REQUIRED_PRIMITIVE_BLOCKS",
    "UNKNOWN_CARD_TYPE",
    "action_ref_from_selection",
    "build_patch_decision_selection",
    "build_complete_patch_review_contract",
    "build_patch_preview_selection",
    "build_patch_review_availability",
    "build_patch_review_contract",
    "build_patch_review_selection",
    "build_action_resolved_event",
    "build_action_resolved_event_from_selection",
    "build_action_selected_event",
    "build_action_selected_event_from_selection",
    "build_card_published_event",
    "build_complete_patch_review_action_resolved_event",
    "build_complete_patch_review_action_selected_event",
    "canonicalize_action_order",
    "build_unknown_card",
    "complete_patch_review_action_from_card",
    "complete_patch_review_actions_from_contract",
    "complete_patch_review_actions_from_card",
    "complete_patch_review_action_refs_from_contract",
    "engine_prepare_card",
    "engine_authoritative_action_ref",
    "execute_complete_patch_review_action_with_policy_gate",
    "execute_action_with_policy_gate",
    "execute_patch_review_selection_with_policy_gate",
    "materialize_action_selection_contract",
    "materialize_cli_fallback_card",
    "materialize_patch_decision_contract",
    "materialize_patch_preview_contract",
    "materialize_proposed_edit_card",
    "patch_decision_action_ref_from_selection",
    "patch_preview_action_ref_from_selection",
    "patch_review_action_ref_from_selection",
    "patch_review_action_selection_from_selection",
    "patch_review_availability_from_contract",
    "patch_review_action_refs_from_contract",
    "patch_review_cli_command_lookup_from_contract",
    "patch_review_cli_control_map_from_contract",
    "patch_review_control_actions_from_contract",
    "patch_review_decision_controls_from_contract",
    "patch_review_next_control_from_contract",
    "patch_review_control_plan_from_contract",
    "patch_review_selection_from_cli_command",
    "patch_review_control_summary_from_contract",
    "patch_review_control_slots_from_contract",
    "materialize_card_actions",
    "materialize_terminal_card",
    "render_terminal_card",
    "resolve_card_selection",
    "resolve_card_selection_contract",
    "resolve_card_selection_by_index",
    "resolve_patch_decision_action",
    "resolve_patch_decision_selection",
    "resolve_patch_preview_action",
    "resolve_patch_preview_selection",
    "resolve_patch_review_contract",
    "resolve_patch_review_selection",
    "studio_materialize_card",
    "stream_event_key",
    "validate_action_ref",
    "validate_card_payload_size",
    "validate_capabilities",
    "validate_generic_card",
    "validate_proposed_edit_card",
    "validate_primitive_block",
    "validate_stream_event",
]
