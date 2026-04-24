"""Public wrappers for the stable current-MVP command workflow surface."""

from __future__ import annotations

from src.qual.commands.catalog import (
    CommandDemoBranchContract,
    CommandDemoWorkflowInvocationEntry,
    CommandTrustedSurfaceContract,
    CommandTrustedSurfaceEntry,
    command_mvp_branch_contract,
    command_mvp_branch_invocation_table,
    command_mvp_branch_trusted_invocation_table,
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


__all__ = [
    "command_workflow_surface_contract",
    "command_workflow_surface_tokens",
    "command_workflow_branch_contract",
    "command_workflow_branch_tokens",
    "command_workflow_branch_invocation_plan",
    "command_workflow_branch_surface",
    "command_workflow_branch_invocation_table",
    "command_workflow_branch_surface_invocation_table",
]
