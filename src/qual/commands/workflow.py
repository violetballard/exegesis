"""Public wrappers for the stable current-MVP command workflow surface."""

from __future__ import annotations

from src.qual.commands.catalog import (
    CommandDemoLoopContract,
    CommandDemoBranchContract,
    CommandDemoNextActionContract,
    CommandDemoWorkflowInvocationEntry,
    CommandDemoPathContract,
    CommandTrustedSurfaceContract,
    CommandTrustedSurfaceEntry,
    CommandInvocationPlanEntry,
    command_mvp_branch_contract,
    command_mvp_branch_invocation_table,
    command_mvp_branch_trusted_invocation_table,
    command_mvp_loop_contract,
    command_mvp_loop_invocation_plan,
    command_mvp_loop_tokens,
    command_mvp_next_action_contract,
    command_mvp_next_action_invocation_table,
    command_mvp_next_action_preferred_invocation_table,
    command_mvp_path_contract,
    command_mvp_path_invocation_plan,
    command_mvp_trusted_surface_contract,
    command_mvp_trusted_surface_tokens,
    command_mvp_workflow_branch_tokens,
    command_mvp_workflow_invocation_plan,
    command_mvp_workflow_trusted_invocation_plan,
)


def command_workflow_surface_contract() -> CommandTrustedSurfaceContract:
    """Return the stable trusted command surface for the current MVP."""
    return command_mvp_trusted_surface_contract()


def command_workflow_surface_tokens() -> tuple[str, ...]:
    """Return the trusted current-MVP command tokens in deterministic order."""
    return command_mvp_trusted_surface_tokens()


def command_workflow_path_contract() -> CommandDemoPathContract:
    """Return the canonical current-MVP demo path for the stable CLI loop."""
    return command_mvp_path_contract()


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


def command_workflow_next_action_surface_invocation_table(
    source_token: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return the trusted current-MVP follow-up action invocation table."""
    return command_mvp_next_action_preferred_invocation_table(source_token)


__all__ = [
    "command_workflow_surface_contract",
    "command_workflow_surface_tokens",
    "command_workflow_path_contract",
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
    "command_workflow_next_action_contract",
    "command_workflow_next_action_tokens",
    "command_workflow_next_action_invocation_table",
    "command_workflow_next_action_surface_invocation_table",
]
