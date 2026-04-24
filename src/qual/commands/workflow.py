"""Public wrappers for the stable current-MVP command workflow surface."""

from __future__ import annotations

from src.qual.commands.catalog import (
    CommandDemoWorkflowContract,
    CommandDemoWorkflowEntry,
    CommandDemoLoopContract,
    CommandDemoBranchContract,
    CommandDemoWorkflowTrustedContract,
    CommandDemoNextActionContract,
    CommandDemoWorkflowInvocationEntry,
    CommandDemoPathContract,
    CommandTrustedSurfaceContract,
    CommandTrustedSurfaceEntry,
    CommandInvocationPlanEntry,
    command_mvp_workflow_contract,
    command_mvp_workflow_entry,
    command_mvp_workflow_tokens,
    command_mvp_workflow_lookup_table,
    command_mvp_workflow_invocation_table,
    command_mvp_workflow_transition_targets,
    command_mvp_transition_targets_by_source,
    command_mvp_transition_targets,
    command_mvp_transition_argv,
    command_mvp_workflow_compatibility_lookup_table,
    command_mvp_workflow_compatibility_invocation_table,
    command_mvp_branch_contract,
    command_mvp_branch_invocation_table,
    command_mvp_branch_trusted_invocation_table,
    command_mvp_loop_contract,
    command_mvp_loop_invocation_plan,
    command_mvp_loop_tokens,
    command_mvp_next_action_contract,
    command_mvp_next_action_lookup_table,
    command_mvp_next_action_invocation_table,
    command_mvp_next_action_compatibility_lookup_table,
    command_mvp_next_action_compatibility_invocation_table,
    command_mvp_next_action_preferred_invocation_table,
    command_mvp_path_contract,
    command_mvp_path_entry,
    command_mvp_path_invocation_plan,
    command_mvp_surface_invocation_table,
    command_mvp_trusted_surface_entry,
    command_mvp_trusted_surface_contract,
    command_mvp_trusted_surface_flow_lookup_table,
    command_mvp_trusted_surface_tokens,
    command_mvp_workflow_trusted_contract,
    command_mvp_workflow_branch_tokens,
    command_mvp_workflow_invocation_plan,
    command_mvp_workflow_trusted_invocation_plan,
    command_mvp_workflow_trusted_invocation_table,
    command_mvp_workflow_trusted_tokens,
)


def command_workflow_surface_contract() -> CommandTrustedSurfaceContract:
    """Return the stable trusted command surface for the current MVP."""
    return command_mvp_trusted_surface_contract()


def command_workflow_surface_tokens() -> tuple[str, ...]:
    """Return the trusted current-MVP command tokens in deterministic order."""
    return command_mvp_trusted_surface_tokens()


def command_workflow_surface_flow_lookup_table() -> tuple[tuple[str, str], ...]:
    """Return trusted current-MVP tokens mapped to their canonical workflow steps."""
    return command_mvp_trusted_surface_flow_lookup_table()


def command_workflow_surface_invocation_table() -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return parser-ready argv for the trusted current-MVP command surface."""
    return command_mvp_surface_invocation_table()


def command_workflow_contract() -> CommandDemoWorkflowContract:
    """Return the stable current-MVP workflow contract for the canonical CLI loop."""
    return command_mvp_workflow_contract()


def command_workflow_entry(token: str) -> CommandDemoWorkflowEntry | None:
    """Return one current-MVP workflow entry resolved from any known workflow token."""
    return command_mvp_workflow_entry(token)


def command_workflow_entry_for(token: str) -> CommandDemoWorkflowEntry | None:
    """Return one current-MVP workflow entry resolved from any known workflow token."""
    return command_mvp_workflow_entry(token)


def command_workflow_tokens() -> tuple[str, ...]:
    """Return the canonical current-MVP workflow tokens in deterministic order."""
    return command_mvp_workflow_tokens()


def command_workflow_lookup_table() -> tuple[tuple[str, str], ...]:
    """Return the stable workflow token to canonical command lookup table."""
    return command_mvp_workflow_lookup_table()


def command_workflow_invocation_table() -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return the parser-ready invocation table for the canonical CLI loop."""
    return command_mvp_workflow_invocation_table()


def command_workflow_transition_targets() -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return the canonical next-step transitions for the current MVP workflow."""
    return command_mvp_workflow_transition_targets()


def command_workflow_transition_targets_by_source() -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return current-MVP transitions grouped by canonical source token."""
    return command_mvp_transition_targets_by_source()


def command_workflow_transition_targets_for(source_token: str) -> tuple[str, ...]:
    """Return canonical follow-up workflow tokens for one current-MVP source token."""
    return command_mvp_transition_targets(source_token)


def command_workflow_transition_argv(
    source_token: str,
    target_token: str,
) -> tuple[str, ...]:
    """Return parser-ready argv for one current-MVP workflow transition."""
    return command_mvp_transition_argv(source_token, target_token)


def command_workflow_transition_argv_for(
    source_token: str,
    target_token: str,
) -> tuple[str, ...]:
    """Return parser-ready argv for one current-MVP workflow transition alias pair."""
    return command_mvp_transition_argv(source_token, target_token)


def command_workflow_compatibility_lookup_table() -> tuple[tuple[str, str], ...]:
    """Return legacy workflow verbs mapped onto the stable current-MVP loop."""
    return command_mvp_workflow_compatibility_lookup_table()


def command_workflow_compatibility_invocation_table() -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return parser-ready argv for legacy workflow verbs mapped to the stable loop."""
    return command_mvp_workflow_compatibility_invocation_table()


def command_workflow_path_contract() -> CommandDemoPathContract:
    """Return the canonical current-MVP demo path for the stable CLI loop."""
    return command_mvp_path_contract()


def command_workflow_path_entry(flow_step: str) -> CommandDemoPathEntry | None:
    """Return one current-MVP demo-path entry resolved from a canonical flow step."""
    return command_mvp_path_entry(flow_step)


def command_workflow_path_entry_for(flow_step: str) -> CommandDemoPathEntry | None:
    """Return one current-MVP demo-path entry resolved from a canonical flow step."""
    return command_mvp_path_entry(flow_step)


def command_workflow_path_tokens() -> tuple[str, ...]:
    """Return the canonical current-MVP demo-path tokens in workflow order."""
    return command_workflow_path_contract().flow_steps


def command_workflow_path_invocation_plan() -> tuple[CommandInvocationPlanEntry, ...]:
    """Return the parser-ready current-MVP demo-path invocation plan."""
    return command_mvp_path_invocation_plan()


def command_workflow_loop_contract() -> CommandDemoLoopContract:
    """Return the stable current-MVP review/apply-or-reject/persist/export loop."""
    return command_mvp_loop_contract()


def command_workflow_loop_tokens() -> tuple[str, ...]:
    """Return the current-MVP workflow loop tokens in deterministic order."""
    return command_mvp_loop_tokens()


def command_workflow_loop_invocation_plan() -> tuple[CommandInvocationPlanEntry, ...]:
    """Return the parser-ready current-MVP workflow loop invocation plan."""
    return command_mvp_loop_invocation_plan()


def command_workflow_branch_contract(decision_token: str) -> CommandDemoBranchContract:
    """Return the current-MVP apply/reject branch contract for one workflow decision."""
    return command_mvp_branch_contract(decision_token)


def command_workflow_branch_tokens(decision_token: str) -> tuple[str, ...]:
    """Return the canonical current-MVP apply/reject branch tokens."""
    return command_mvp_workflow_branch_tokens(decision_token)


def command_workflow_branch_invocation_plan(
    decision_token: str,
) -> tuple[CommandDemoWorkflowInvocationEntry, ...]:
    """Return the parser-ready current-MVP apply/reject branch invocation plan."""
    return command_mvp_workflow_invocation_plan(decision_token)


def command_workflow_branch_surface(
    decision_token: str,
) -> tuple[CommandTrustedSurfaceEntry, ...]:
    """Return the trusted current-MVP apply/reject branch surface entries."""
    return command_mvp_workflow_trusted_invocation_plan(decision_token)


def command_workflow_branch_invocation_table(
    decision_token: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return the parser-ready current-MVP apply/reject branch invocation table."""
    return command_mvp_branch_invocation_table(decision_token)


def command_workflow_branch_surface_invocation_table(
    decision_token: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return the trusted current-MVP apply/reject branch invocation table."""
    return command_mvp_branch_trusted_invocation_table(decision_token)


def command_workflow_trusted_contract(
    decision_token: str,
) -> CommandDemoWorkflowTrustedContract:
    """Return the trusted current-MVP apply/reject branch contract."""
    return command_mvp_workflow_trusted_contract(decision_token)


def command_workflow_surface_entry(token: str) -> CommandTrustedSurfaceEntry | None:
    """Return one trusted current-MVP surface entry resolved from any known surface token."""
    return command_mvp_trusted_surface_entry(token)


def command_workflow_surface_entry_for(token: str) -> CommandTrustedSurfaceEntry | None:
    """Return one trusted current-MVP surface entry resolved from any known surface token."""
    return command_mvp_trusted_surface_entry(token)


def command_workflow_trusted_tokens(decision_token: str) -> tuple[str, ...]:
    """Return the trusted current-MVP apply/reject branch tokens."""
    return command_mvp_workflow_trusted_tokens(decision_token)


def command_workflow_trusted_invocation_plan(
    decision_token: str,
) -> tuple[CommandTrustedSurfaceEntry, ...]:
    """Return the trusted current-MVP apply/reject branch invocation plan."""
    return command_mvp_workflow_trusted_invocation_plan(decision_token)


def command_workflow_trusted_invocation_table(
    decision_token: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return the trusted current-MVP apply/reject branch invocation table."""
    return command_mvp_workflow_trusted_invocation_table(decision_token)


def command_workflow_next_action_contract(source_token: str) -> CommandDemoNextActionContract:
    """Return the trusted current-MVP follow-up actions for one workflow step."""
    return command_mvp_next_action_contract(source_token)


def command_workflow_next_action_tokens(source_token: str) -> tuple[str, ...]:
    """Return the canonical current-MVP follow-up action tokens for one workflow step."""
    return tuple(entry.target_token for entry in command_workflow_next_action_contract(source_token).entries)


def command_workflow_next_action_invocation_table(
    source_token: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return the parser-ready current-MVP follow-up action invocation table."""
    return command_mvp_next_action_invocation_table(source_token)


def command_workflow_next_action_lookup_table(
    source_token: str,
) -> tuple[tuple[str, str], ...]:
    """Return follow-up workflow actions resolved to canonical command names."""
    return command_mvp_next_action_lookup_table(source_token)


def command_workflow_next_action_compatibility_lookup_table(
    source_token: str,
) -> tuple[tuple[str, str], ...]:
    """Return legacy follow-up verbs mapped to canonical workflow actions."""
    return command_mvp_next_action_compatibility_lookup_table(source_token)


def command_workflow_next_action_compatibility_invocation_table(
    source_token: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return parser-ready argv for legacy follow-up workflow verbs."""
    return command_mvp_next_action_compatibility_invocation_table(source_token)


def command_workflow_next_action_surface_invocation_table(
    source_token: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return the trusted current-MVP follow-up action invocation table."""
    return command_mvp_next_action_preferred_invocation_table(source_token)


__all__ = [
    "command_workflow_surface_contract",
    "command_workflow_surface_entry",
    "command_workflow_surface_entry_for",
    "command_workflow_surface_tokens",
    "command_workflow_entry",
    "command_workflow_entry_for",
    "command_workflow_contract",
    "command_workflow_tokens",
    "command_workflow_lookup_table",
    "command_workflow_invocation_table",
    "command_workflow_transition_targets",
    "command_workflow_transition_targets_by_source",
    "command_workflow_transition_targets_for",
    "command_workflow_transition_argv",
    "command_workflow_transition_argv_for",
    "command_workflow_compatibility_lookup_table",
    "command_workflow_compatibility_invocation_table",
    "command_workflow_path_contract",
    "command_workflow_path_entry",
    "command_workflow_path_entry_for",
    "command_workflow_path_tokens",
    "command_workflow_path_invocation_plan",
    "command_workflow_loop_contract",
    "command_workflow_loop_tokens",
    "command_workflow_loop_invocation_plan",
    "command_workflow_branch_contract",
    "command_workflow_branch_tokens",
    "command_workflow_branch_invocation_plan",
    "command_workflow_branch_surface",
    "command_workflow_branch_invocation_table",
    "command_workflow_branch_surface_invocation_table",
    "command_workflow_trusted_contract",
    "command_workflow_trusted_tokens",
    "command_workflow_trusted_invocation_plan",
    "command_workflow_trusted_invocation_table",
    "command_workflow_next_action_contract",
    "command_workflow_next_action_tokens",
    "command_workflow_next_action_lookup_table",
    "command_workflow_next_action_invocation_table",
    "command_workflow_next_action_compatibility_lookup_table",
    "command_workflow_next_action_compatibility_invocation_table",
    "command_workflow_next_action_surface_invocation_table",
]
