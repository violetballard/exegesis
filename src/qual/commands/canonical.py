from __future__ import annotations

from src.qual.commands.catalog import (
    canonical_command as _canonical_command,
    command_mvp_demo_action_demo_path_lookup_table as _action_demo_path_lookup_table,
    command_mvp_demo_action_demo_path_step as _action_demo_path_step,
    command_mvp_demo_action_flow_lookup_table as _action_flow_lookup_table,
    command_mvp_demo_action_flow_step as _action_flow_step,
    command_mvp_demo_command_action_lookup_table as _command_action_lookup_table,
    command_mvp_demo_readiness_action_argv_lookup_table as _readiness_action_argv_lookup_table,
    command_mvp_demo_readiness_action_summary as _readiness_action_summary,
    command_mvp_demo_readiness_argv_for_engine_action as _readiness_argv_for_engine_action,
    command_mvp_demo_readiness_argv_for_flow_step as _readiness_argv_for_flow_step,
    command_mvp_demo_readiness_command_for_engine_action as _readiness_command_for_engine_action,
    command_mvp_demo_readiness_command_for_flow_step as _readiness_command_for_flow_step,
    command_mvp_demo_readiness_lookup_table as _readiness_lookup_table,
    command_mvp_demo_readiness_summary as _readiness_summary,
)

__all__ = [
    "canonical_command",
    "canonical_command_action_argv_lookup_table",
    "canonical_command_action_demo_path_lookup_table",
    "canonical_command_action_lookup_table",
    "canonical_command_action_readiness_summary",
    "canonical_command_action_flow_lookup_table",
    "canonical_command_demo_path_step_for_engine_action",
    "canonical_command_argv_for_engine_action",
    "canonical_command_argv_for_flow_step",
    "canonical_command_engine_actions",
    "canonical_command_engine_actions_for_flow_step",
    "canonical_command_flow_step_for_engine_action",
    "canonical_command_for_engine_action",
    "canonical_command_for_flow_step",
    "canonical_command_readiness_lookup_table",
    "canonical_command_readiness_summary",
]


def canonical_command(name: str) -> str:
    return _canonical_command(name)


def canonical_command_readiness_summary() -> tuple[
    tuple[int, str, str, tuple[str, ...], str, tuple[str, ...], tuple[tuple[str, tuple[str, ...]], ...]],
    ...,
]:
    return _readiness_summary()


def canonical_command_readiness_lookup_table() -> tuple[tuple[str, tuple[str, ...]], ...]:
    return _readiness_lookup_table()


def canonical_command_action_readiness_summary() -> tuple[
    tuple[str, str, str, tuple[str, ...], tuple[str, ...], str],
    ...,
]:
    return _readiness_action_summary()


def canonical_command_action_argv_lookup_table() -> tuple[tuple[str, tuple[str, ...]], ...]:
    return _readiness_action_argv_lookup_table()


def canonical_command_action_lookup_table() -> tuple[tuple[str, tuple[str, ...]], ...]:
    return _command_action_lookup_table()


def canonical_command_action_flow_lookup_table() -> tuple[tuple[str, str], ...]:
    return _action_flow_lookup_table()


def canonical_command_action_demo_path_lookup_table() -> tuple[tuple[str, str], ...]:
    return _action_demo_path_lookup_table()


def canonical_command_engine_actions(command_name: str) -> tuple[str, ...]:
    requested_command = canonical_command(command_name)
    return dict(canonical_command_action_lookup_table()).get(requested_command, ())


def canonical_command_for_engine_action(engine_action: str) -> str | None:
    return _readiness_command_for_engine_action(engine_action)


def canonical_command_argv_for_engine_action(engine_action: str) -> tuple[str, ...]:
    return _readiness_argv_for_engine_action(engine_action)


def canonical_command_flow_step_for_engine_action(engine_action: str) -> str | None:
    return _action_flow_step(engine_action)


def canonical_command_demo_path_step_for_engine_action(engine_action: str) -> str | None:
    return _action_demo_path_step(engine_action)


def canonical_command_for_flow_step(flow_step: str) -> str | None:
    return _readiness_command_for_flow_step(flow_step)


def canonical_command_argv_for_flow_step(flow_step: str) -> tuple[str, ...]:
    return _readiness_argv_for_flow_step(flow_step)


def canonical_command_engine_actions_for_flow_step(flow_step: str) -> tuple[str, ...]:
    requested_command = canonical_command_for_flow_step(flow_step)
    if requested_command is None:
        return ()
    return canonical_command_engine_actions(requested_command)
