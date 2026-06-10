from __future__ import annotations

from typing import Any

from exegesis_shared.contracts.actions import (
    ACTION_SELECTION_CONTRACT_VERSION,
    ALLOWED_ACTION_IDS,
    CANONICAL_ACTION_ORDER,
    ENGINE_NORMALIZED_ACTION_PAYLOAD_FIELDS,
    POLICY_SENSITIVE_ACTION_IDS,
    ActionRef,
    CompletePatchReviewActions,
    PATCH_DECISION_ACTION_IDS,
    PATCH_DECISION_BY_ACTION_ID,
    PATCH_DECISION_CONTRACT_VERSION,
    PATCH_PREVIEW_CONTRACT_VERSION,
    PATCH_REVIEW_ACTION_AUTHORITY,
    PATCH_REVIEW_CONFIRMATION_TITLES,
    PATCH_REVIEW_CLI_COMMAND_ALIASES,
    PATCH_REVIEW_CONTRACT_VERSION,
    PATCH_REVIEW_DECISION_GROUP,
    PATCH_REVIEW_DECISION_POLICY,
    PATCH_REVIEW_DEMO_PATH_STEP,
    PATCH_REVIEW_EXECUTION_PRECONDITIONS,
    PATCH_REVIEW_EXECUTION_POLICY,
    PATCH_REVIEW_FLOW,
    PATCH_REVIEW_CONTROL_KINDS,
    PATCH_REVIEW_REQUIRED_PARTS,
    PATCH_REVIEW_RESOLVED_STATUSES,
    PatchReviewActionSelection,
    PolicyGate,
    advance_patch_review_state,
    advance_patch_review_state_typed,
    action_ref_from_selection,
    build_patch_decision_from_engine_loop_outcome,
    build_patch_decision_selection,
    build_complete_patch_review_contract,
    build_patch_preview_selection,
    build_patch_review_availability,
    build_patch_review_contract,
    build_patch_review_selection,
    canonicalize_action_order,
    complete_patch_review_decision_action_ref_from_cli_command,
    complete_patch_review_action_ref_from_cli_command,
    validate_patch_review_contract,
    complete_patch_review_action_from_card,
    complete_patch_review_available_controls_from_state,
    complete_patch_review_actions_from_contract,
    complete_patch_review_actions_from_card,
    complete_patch_review_action_refs_from_contract,
    execute_basket_create_context_set_with_policy_gate,
    execute_basket_gather_context_with_policy_gate,
    execute_card_selection_with_policy_gate,
    execute_context_set_open_corpus_item_with_policy_gate,
    execute_context_set_pin_with_policy_gate,
    execute_context_set_promote_to_basket_with_policy_gate,
    execute_complete_patch_review_cli_command_with_policy_gate,
    execute_complete_patch_review_decision_cli_command_with_policy_gate,
    execute_patch_review_cli_command_with_policy_gate,
    execute_patch_review_control_with_policy_gate,
    execute_complete_patch_review_action_with_policy_gate,
    execute_complete_patch_review_control_with_policy_gate,
    execute_complete_patch_review_selection_with_policy_gate,
    execute_action_with_policy_gate,
    is_policy_sensitive_action,
    execute_patch_review_selection_with_policy_gate,
    execute_patch_review_decision_cli_command_with_policy_gate,
    execute_retrieval_open_corpus_item_with_policy_gate,
    execute_retrieval_pin_to_context_set_with_policy_gate,
    execute_retrieval_promote_with_policy_gate,
    engine_authoritative_action_ref,
    validate_engine_authoritative_action_ref,
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
    patch_review_action_ref_from_cli_command,
    patch_review_action_refs_from_contract,
    patch_review_cli_command_lookup_from_contract,
    patch_review_cli_control_map_from_contract,
    patch_review_control_actions_from_contract,
    patch_review_decision_cli_command_lookup_from_contract,
    patch_review_decision_controls_from_contract,
    patch_review_next_control_from_contract,
    patch_review_control_plan_from_contract,
    patch_review_control_summary_from_contract,
    patch_review_control_slots_from_contract,
    patch_review_execution_preconditions,
    patch_review_resolved_status,
    patch_review_selection_from_cli_command,
    resolve_patch_review_execution_state,
    resolve_card_selection,
    resolve_card_selection_contract,
    resolve_card_selection_by_index,
    resolve_card_selection_execution,
    resolve_patch_decision_action,
    resolve_patch_decision_selection,
    resolve_patch_preview_action,
    resolve_patch_preview_selection,
    resolve_complete_patch_review_control_execution,
    resolve_complete_patch_review_cli_command_execution,
    resolve_complete_patch_review_decision_cli_command_execution,
    resolve_patch_review_contract,
    resolve_patch_review_cli_command_execution,
    resolve_patch_review_control_execution,
    resolve_patch_review_decision_cli_command_execution,
    resolve_patch_review_selection,
    validate_action_capabilities,
    validate_action_ref,
    validate_complete_patch_review_capabilities,
    validate_patch_review_contract,
    validate_patch_review_execution_state,
)
from exegesis_shared.contracts.cards import (
    A2UICapabilities,
    A2UISessionStore,
    PatchReviewExecutionOutcome,
    A2UI_VERSION,
    BASKET_CARD_TYPE,
    CONTEXT_SET_CARD_TYPE,
    DEMO_CONTEXT_ACTION_IDS,
    DEMO_CONTEXT_CARD_TYPES,
    GENERIC_CARD_TYPE,
    KNOWN_CARD_TYPES,
    PROPOSED_EDIT_CARD_TYPE,
    REQUIRED_PRIMITIVE_BLOCKS,
    RETRIEVAL_RESULTS_CARD_TYPE,
    UNKNOWN_CARD_TYPE,
    build_basket_card,
    build_context_set_card,
    build_generic_card,
    build_proposed_edit_card,
    build_retrieval_results_card,
    build_unknown_card,
    engine_prepare_card,
    execute_complete_patch_review_action_and_advance_state,
    execute_complete_patch_review_cli_command_and_advance_state,
    execute_patch_review_action,
    execute_patch_review_action_and_advance_state,
    materialize_action_slots,
    materialize_patch_selection_envelope,
    materialize_proposed_edit_card,
    resolve_action_selection,
    resolve_action_from_selection_model,
    execute_card_action_from_typed_selection_with_policy_gate,
    execute_patch_review_from_typed_selection_with_policy_gate,
    execute_patch_review_from_typed_selection_and_advance_state,
    resolve_complete_patch_review_card_cli_command_execution,
    resolve_complete_patch_review_card_control_execution,
    resolve_complete_patch_review_card_decision_cli_command_execution,
    studio_materialize_card as _studio_materialize_card,
    validate_card_payload_size,
    validate_capabilities,
    validate_basket_card,
    validate_complete_patch_review_card_capabilities,
    validate_context_set_card,
    validate_demo_context_card_capabilities,
    validate_engine_demo_path_capabilities,
    supports_engine_demo_path,
    validate_generic_card,
    validate_known_card,
    validate_proposed_edit_card,
    validate_primitive_block,
    validate_retrieval_results_card,
    validate_unknown_card,
)
from exegesis_shared.contracts.events import (
    A2UI_EVENT_CONTRACT_VERSION,
    A2UI_STREAM_EVENT_TYPES,
    CONTEXT_BASKET_ACTION_IDS,
    build_action_resolved_event,
    build_action_resolved_event_from_selection,
    build_action_selected_event,
    build_action_selected_event_from_selection,
    build_card_published_event,
    build_complete_patch_review_action_resolved_event,
    build_complete_patch_review_action_resolved_event_from_outcome,
    build_complete_patch_review_action_selected_event,
    build_patch_review_action_resolved_event_from_outcome,
    build_patch_review_action_selected_event,
    action_ref_from_next_action_hint,
    engine_loop_outcome_next_action_hints,
    execute_patch_review_from_hint_with_policy_gate_and_advance_state,
    execute_patch_review_from_hint_with_policy_gate_and_advance_state_typed,
    is_engine_loop_outcome_terminal,
    stream_event_key,
    summarize_engine_loop_sequence_outcome,
    validate_engine_loop_event_sequence,
    validate_engine_loop_outcome,
    validate_stream_event,
)
from exegesis_shared.models.engine_loop_outcome import ContextBasketOutcome, EngineLoopOutcome
from exegesis_shared.contracts import validate_patch_review_state_consistency
from exegesis_shared.models.patch_review_state import PatchReviewState
from exegesis_shared.models.selection import Selection
from exegesis_shared.types.object_types import OBJECT_TYPES, SelectionObjectType


def _deduped_sorted_actions(card: dict[str, Any]) -> list[dict[str, Any]]:
    """Backward-compatible alias for canonical card action materialization."""
    return materialize_card_actions(card)


def materialize_terminal_card(card: dict[str, Any]) -> dict[str, Any]:
    """Materialize the A2UI card shape consumed by CLI fallback renderers."""
    if not isinstance(card, dict):
        raise ValueError("Card must be a dictionary")
    return materialize_cli_fallback_card(card)


def studio_materialize_card(payload: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Card payload must be a dictionary")
    return materialize_terminal_card(_studio_materialize_card(payload, capabilities))


def _render_terminal_card_type_context(materialized: dict[str, Any]) -> list[str]:
    """Render card-type-specific context fields for CLI fallback display."""
    if not isinstance(materialized, dict):
        raise ValueError("Materialized card must be a dictionary")
    card_type = materialized.get("type")
    lines: list[str] = []
    if card_type == RETRIEVAL_RESULTS_CARD_TYPE:
        query = materialized.get("query")
        if isinstance(query, str) and query.strip():
            lines.append(f"Query: {query.strip()}")
        results = materialized.get("results")
        if isinstance(results, list):
            lines.append(f"Results: {len(results)}")
            for result in results:
                if isinstance(result, dict):
                    item_title = result.get("title", result.get("item_id", ""))
                    snippet = result.get("snippet", "")
                    score = result.get("score")
                    source_ref = result.get("source_ref")
                    parts: list[str] = []
                    if isinstance(snippet, str) and snippet.strip():
                        parts.append(snippet.strip())
                    if score is not None:
                        parts.append(f"score={score}")
                    if isinstance(source_ref, str) and source_ref.strip():
                        parts.append(f"ref={source_ref.strip()}")
                    if parts:
                        lines.append(f"  - {item_title}: {'; '.join(parts)}")
                    else:
                        lines.append(f"  - {item_title}")
    elif card_type == BASKET_CARD_TYPE:
        basket_id = materialized.get("basket_id")
        if isinstance(basket_id, str) and basket_id.strip():
            lines.append(f"Basket: {basket_id.strip()}")
        items = materialized.get("items")
        if isinstance(items, list):
            lines.append(f"Items: {len(items)}")
            for item in items:
                if isinstance(item, dict):
                    lines.append(f"  - {item.get('title', item.get('item_id', ''))}")
    elif card_type == CONTEXT_SET_CARD_TYPE:
        context_set_id = materialized.get("context_set_id")
        if isinstance(context_set_id, str) and context_set_id.strip():
            lines.append(f"Context set: {context_set_id.strip()}")
        items = materialized.get("items")
        if isinstance(items, list):
            lines.append(f"Pinned items: {len(items)}")
            for item in items:
                if isinstance(item, dict):
                    lines.append(f"  - {item.get('title', item.get('item_id', ''))}")
    elif card_type in {GENERIC_CARD_TYPE, PROPOSED_EDIT_CARD_TYPE, UNKNOWN_CARD_TYPE}:
        patch_id = materialized.get("patch_id")
        if isinstance(patch_id, str) and patch_id.strip():
            lines.append(f"Patch: {patch_id.strip()}")
    return lines


def render_terminal_card(card: dict[str, Any]) -> str:
    if not isinstance(card, dict):
        raise ValueError("Card must be a dictionary")
    materialized = materialize_terminal_card(card)
    title = str(materialized.get("title", "<untitled>"))
    card_type = str(materialized.get("type", "Card"))
    lines = [f"[{card_type}] {title}"]
    lines.extend(_render_terminal_card_type_context(materialized))
    blocks = materialized.get("blocks", [])
    if isinstance(blocks, list):
        for block in blocks:
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
        lines.append(f"Patch review decision group: {PATCH_REVIEW_DECISION_GROUP}")
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
                decision_lookup = patch_review_decision_cli_command_lookup_from_contract(
                    materialized,
                    review,
                    patch_id=patch_id,
                )
                decision_lookup_map = [
                    f"{command}->{entry['control']}"
                    for command, entry in sorted(decision_lookup["commands"].items())
                    if isinstance(entry, dict)
                ]
                if decision_lookup_map:
                    lines.append(
                        "Patch review decision command lookup: "
                        f"{', '.join(decision_lookup_map)}"
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
        complete_actions = materialized.get("complete_patch_review_actions")
        if isinstance(complete_actions, dict):
            preview_action = complete_actions.get("preview", {})
            decisions = complete_actions.get("decisions", {})
            apply_action = decisions.get("apply", {}) if isinstance(decisions, dict) else {}
            reject_action = decisions.get("reject", {}) if isinstance(decisions, dict) else {}
            complete_labels = []
            if isinstance(preview_action, dict) and preview_action.get("id"):
                complete_labels.append(f"preview={preview_action['id']}")
            if isinstance(apply_action, dict) and apply_action.get("id"):
                complete_labels.append(f"apply={apply_action['id']}")
            if isinstance(reject_action, dict) and reject_action.get("id"):
                complete_labels.append(f"reject={reject_action['id']}")
            if complete_labels:
                lines.append(f"Complete patch review actions: {', '.join(complete_labels)}")
    elif isinstance(patch_id, str) and patch_id.strip():
        decision = materialized.get("patch_decision")
        decisions = decision.get("decisions") if isinstance(decision, dict) else None
        if isinstance(decisions, list):
            decision_controls = [
                f"{entry['decision']}={entry['slot']}"
                for entry in decisions
                if isinstance(entry, dict) and "decision" in entry and "slot" in entry
            ]
            if decision_controls:
                lines.append(
                    "Partial patch decision actions: "
                    f"{', '.join(decision_controls)} (preview missing)"
                )
    actions = materialized.get("actions", [])
    if isinstance(actions, list):
        for slot, action in enumerate(actions, start=1):
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
    if isinstance(slot, int) and not isinstance(slot, bool):
        parts.append(f"slot {slot}")
    aliases = entry.get("command_aliases")
    if isinstance(aliases, list) and aliases:
        parts.append(f"aliases {'/'.join(str(alias) for alias in aliases)}")
    policy = entry.get("execution_policy")
    if isinstance(policy, dict):
        if policy.get("requires_confirmation"):
            parts.append("confirm")
        if policy.get("requires_preview"):
            parts.append("requires-preview")
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


def render_patch_review_session_state(state: "PatchReviewState | dict[str, Any]") -> str:
    """Render a PatchReviewState as CLI-displayable session progress text.

    Accepts either a PatchReviewState instance or the dict produced by
    advance_patch_review_state.  Shows session progress (pending / previewed /
    resolved) and the next available controls, distinct from the contract-level
    completeness shown by render_terminal_card.
    """
    if not isinstance(state, (dict, PatchReviewState)):
        raise ValueError("state must be a PatchReviewState or a dictionary")
    if isinstance(state, dict):
        state = PatchReviewState.from_dict(state)
    lines: list[str] = [f"Patch review session: {state.patch_id}"]
    if state.is_pending():
        lines.append("Session status: pending")
        lines.append("Next: preview")
    elif state.is_previewed():
        lines.append("Session status: previewed")
        lines.append("Next: apply or reject")
    elif state.is_resolved():
        lines.append("Session status: resolved")
        decision = state.resolved_control()
        if decision is not None:
            lines.append(f"Decision: {decision}")
    available_ids = state.available_action_ids()
    if available_ids:
        lines.append(f"Available actions: {', '.join(available_ids)}")
    return "\n".join(lines)


def render_engine_loop_outcome(outcome: dict[str, Any]) -> str:
    """Render a typed engine loop sequence outcome as CLI-displayable text.

    Accepts the dict returned by summarize_engine_loop_sequence_outcome
    and formats it for the CLI fallback surface without re-validating the
    sequence.
    """
    if not isinstance(outcome, dict):
        raise ValueError("outcome must be a dictionary")
    lines: list[str] = []
    run_id = outcome.get("run_id")
    patch_id = outcome.get("patch_id")
    patch_outcome = outcome.get("patch_outcome")
    inflight_action_id = outcome.get("inflight_action_id")
    event_count = outcome.get("event_count", 0)
    last_sequence = outcome.get("last_sequence")

    if run_id is not None:
        lines.append(f"Engine run: {run_id}")
    lines.append(f"Events processed: {event_count}")
    if last_sequence is not None:
        lines.append(f"Last sequence: {last_sequence}")
    if patch_id is not None:
        lines.append(f"Patch: {patch_id}")
    if patch_outcome is not None:
        lines.append(f"Patch outcome: {patch_outcome}")
    elif patch_id is not None:
        lines.append("Patch outcome: pending")
    if inflight_action_id is not None:
        lines.append(f"In-flight action: {inflight_action_id}")
    next_hints = engine_loop_outcome_next_action_hints(outcome)
    if next_hints:
        hint_labels = [h.get("label", h["action_id"]).lower() for h in next_hints]
        lines.append("Next: " + " or ".join(hint_labels))
    context_basket_outcomes = outcome.get("context_basket_outcomes") or []
    for entry in context_basket_outcomes:
        action_id = entry.get("action_id", "")
        entry_status = entry.get("status", "")
        seq = entry.get("sequence")
        seq_label = f" (seq {seq})" if seq is not None else ""
        lines.append(f"Context/basket action: {action_id} -> {entry_status}{seq_label}")
    outcome_status = outcome.get("status")
    if outcome_status is not None:
        lines.append(f"Status: {outcome_status}")
    if is_engine_loop_outcome_terminal(outcome):
        lines.append("Run: complete")
    return "\n".join(lines)


__all__ = [
    "ActionRef",
    "CompletePatchReviewActions",
    "A2UICapabilities",
    "A2UI_EVENT_CONTRACT_VERSION",
    "A2UI_STREAM_EVENT_TYPES",
    "CONTEXT_BASKET_ACTION_IDS",
    "A2UISessionStore",
    "ContextBasketOutcome",
    "EngineLoopOutcome",
    "PatchReviewExecutionOutcome",
    "PatchReviewState",
    "A2UI_VERSION",
    "ACTION_SELECTION_CONTRACT_VERSION",
    "ALLOWED_ACTION_IDS",
    "CANONICAL_ACTION_ORDER",
    "ENGINE_NORMALIZED_ACTION_PAYLOAD_FIELDS",
    "POLICY_SENSITIVE_ACTION_IDS",
    "BASKET_CARD_TYPE",
    "CONTEXT_SET_CARD_TYPE",
    "DEMO_CONTEXT_ACTION_IDS",
    "DEMO_CONTEXT_CARD_TYPES",
    "PATCH_DECISION_ACTION_IDS",
    "PATCH_DECISION_BY_ACTION_ID",
    "PATCH_DECISION_CONTRACT_VERSION",
    "PATCH_REVIEW_CONFIRMATION_TITLES",
    "PATCH_PREVIEW_CONTRACT_VERSION",
    "PATCH_REVIEW_ACTION_AUTHORITY",
    "PATCH_REVIEW_CLI_COMMAND_ALIASES",
    "PATCH_REVIEW_CONTROL_KINDS",
    "PATCH_REVIEW_CONTRACT_VERSION",
    "PATCH_REVIEW_DECISION_GROUP",
    "PATCH_REVIEW_DECISION_POLICY",
    "PATCH_REVIEW_DEMO_PATH_STEP",
    "PATCH_REVIEW_EXECUTION_PRECONDITIONS",
    "PATCH_REVIEW_EXECUTION_POLICY",
    "PATCH_REVIEW_FLOW",
    "PATCH_REVIEW_REQUIRED_PARTS",
    "PATCH_REVIEW_RESOLVED_STATUSES",
    "GENERIC_CARD_TYPE",
    "KNOWN_CARD_TYPES",
    "PatchReviewActionSelection",
    "PolicyGate",
    "PROPOSED_EDIT_CARD_TYPE",
    "REQUIRED_PRIMITIVE_BLOCKS",
    "RETRIEVAL_RESULTS_CARD_TYPE",
    "UNKNOWN_CARD_TYPE",
    "advance_patch_review_state",
    "advance_patch_review_state_typed",
    "action_ref_from_selection",
    "build_patch_decision_from_engine_loop_outcome",
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
    "build_complete_patch_review_action_resolved_event_from_outcome",
    "build_complete_patch_review_action_selected_event",
    "build_patch_review_action_resolved_event_from_outcome",
    "build_patch_review_action_selected_event",
    "canonicalize_action_order",
    "build_basket_card",
    "build_context_set_card",
    "build_generic_card",
    "build_proposed_edit_card",
    "build_retrieval_results_card",
    "build_unknown_card",
    "complete_patch_review_decision_action_ref_from_cli_command",
    "complete_patch_review_action_ref_from_cli_command",
    "complete_patch_review_action_from_card",
    "complete_patch_review_available_controls_from_state",
    "complete_patch_review_actions_from_contract",
    "complete_patch_review_actions_from_card",
    "complete_patch_review_action_refs_from_contract",
    "execute_basket_create_context_set_with_policy_gate",
    "execute_basket_gather_context_with_policy_gate",
    "execute_card_selection_with_policy_gate",
    "execute_context_set_open_corpus_item_with_policy_gate",
    "execute_context_set_pin_with_policy_gate",
    "execute_context_set_promote_to_basket_with_policy_gate",
    "execute_patch_review_cli_command_with_policy_gate",
    "execute_patch_review_control_with_policy_gate",
    "execute_patch_review_decision_cli_command_with_policy_gate",
    "engine_prepare_card",
    "engine_authoritative_action_ref",
    "validate_engine_authoritative_action_ref",
    "execute_complete_patch_review_cli_command_with_policy_gate",
    "execute_complete_patch_review_decision_cli_command_with_policy_gate",
    "execute_complete_patch_review_action_with_policy_gate",
    "execute_complete_patch_review_control_with_policy_gate",
    "execute_complete_patch_review_selection_with_policy_gate",
    "execute_action_with_policy_gate",
    "is_policy_sensitive_action",
    "execute_patch_review_selection_with_policy_gate",
    "execute_retrieval_open_corpus_item_with_policy_gate",
    "execute_retrieval_pin_to_context_set_with_policy_gate",
    "execute_retrieval_promote_with_policy_gate",
    "execute_complete_patch_review_action_and_advance_state",
    "execute_complete_patch_review_cli_command_and_advance_state",
    "execute_patch_review_action",
    "execute_patch_review_action_and_advance_state",
    "materialize_action_slots",
    "materialize_action_selection_contract",
    "materialize_cli_fallback_card",
    "materialize_patch_selection_envelope",
    "materialize_patch_decision_contract",
    "materialize_patch_preview_contract",
    "materialize_proposed_edit_card",
    "patch_decision_action_ref_from_selection",
    "patch_preview_action_ref_from_selection",
    "patch_review_action_ref_from_selection",
    "patch_review_action_selection_from_selection",
    "patch_review_availability_from_contract",
    "patch_review_action_ref_from_cli_command",
    "patch_review_action_refs_from_contract",
    "patch_review_cli_command_lookup_from_contract",
    "patch_review_cli_control_map_from_contract",
    "patch_review_control_actions_from_contract",
    "patch_review_decision_cli_command_lookup_from_contract",
    "patch_review_decision_controls_from_contract",
    "patch_review_next_control_from_contract",
    "patch_review_control_plan_from_contract",
    "patch_review_selection_from_cli_command",
    "patch_review_control_summary_from_contract",
    "patch_review_control_slots_from_contract",
    "patch_review_execution_preconditions",
    "patch_review_resolved_status",
    "resolve_patch_review_execution_state",
    "materialize_card_actions",
    "materialize_terminal_card",
    "render_engine_loop_outcome",
    "render_patch_review_session_state",
    "render_terminal_card",
    "resolve_action_selection",
    "resolve_action_from_selection_model",
    "execute_card_action_from_typed_selection_with_policy_gate",
    "execute_patch_review_from_typed_selection_with_policy_gate",
    "execute_patch_review_from_typed_selection_and_advance_state",
    "resolve_card_selection",
    "resolve_card_selection_contract",
    "resolve_card_selection_by_index",
    "resolve_card_selection_execution",
    "resolve_complete_patch_review_card_cli_command_execution",
    "resolve_complete_patch_review_card_control_execution",
    "resolve_complete_patch_review_card_decision_cli_command_execution",
    "resolve_patch_decision_action",
    "resolve_patch_decision_selection",
    "resolve_patch_preview_action",
    "resolve_patch_preview_selection",
    "resolve_complete_patch_review_control_execution",
    "resolve_complete_patch_review_cli_command_execution",
    "resolve_complete_patch_review_decision_cli_command_execution",
    "resolve_patch_review_contract",
    "resolve_patch_review_cli_command_execution",
    "resolve_patch_review_control_execution",
    "resolve_patch_review_decision_cli_command_execution",
    "resolve_patch_review_selection",
    "studio_materialize_card",
    "stream_event_key",
    "validate_action_ref",
    "validate_action_capabilities",
    "validate_complete_patch_review_capabilities",
    "validate_patch_review_contract",
    "validate_patch_review_execution_state",
    "validate_patch_review_state_consistency",
    "validate_complete_patch_review_card_capabilities",
    "validate_basket_card",
    "validate_card_payload_size",
    "validate_capabilities",
    "validate_context_set_card",
    "validate_demo_context_card_capabilities",
    "validate_engine_demo_path_capabilities",
    "supports_engine_demo_path",
    "validate_generic_card",
    "validate_known_card",
    "validate_proposed_edit_card",
    "validate_primitive_block",
    "validate_retrieval_results_card",
    "validate_unknown_card",
    "action_ref_from_next_action_hint",
    "engine_loop_outcome_next_action_hints",
    "execute_patch_review_from_hint_with_policy_gate_and_advance_state",
    "execute_patch_review_from_hint_with_policy_gate_and_advance_state_typed",
    "is_engine_loop_outcome_terminal",
    "summarize_engine_loop_sequence_outcome",
    "validate_engine_loop_event_sequence",
    "validate_engine_loop_outcome",
    "validate_stream_event",
    "OBJECT_TYPES",
    "Selection",
    "SelectionObjectType",
]
