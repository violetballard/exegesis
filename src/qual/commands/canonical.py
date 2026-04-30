from __future__ import annotations

from collections.abc import Sequence

from src.qual.commands.catalog import (
    CommandDemoReadinessGate,
    CommandDemoReadinessActionEntry,
    CommandDemoReadinessEntry,
    canonical_command as _canonical_command,
    command_mvp_demo_path_readiness_contract as _path_readiness_contract,
    command_mvp_demo_path_readiness_summary as _path_readiness_summary,
    command_mvp_demo_action_smoke_script_argv as _action_smoke_script_argv,
    command_mvp_demo_action_smoke_script_lines as _action_smoke_script_lines,
    command_mvp_demo_action_smoke_script_lookup_table as _action_smoke_script_lookup_table,
    command_mvp_demo_action_smoke_script_summary as _action_smoke_script_summary,
    command_mvp_demo_smoke_cli_script_argv as _smoke_cli_script_argv,
    command_mvp_demo_smoke_cli_script_lines as _smoke_cli_script_lines,
    command_mvp_demo_smoke_cli_script_lookup_table as _smoke_cli_script_lookup_table,
    command_mvp_demo_smoke_cli_script_summary as _smoke_cli_script_summary,
    command_mvp_demo_action_demo_path_lookup_table as _action_demo_path_lookup_table,
    command_mvp_demo_action_demo_path_step as _action_demo_path_step,
    command_mvp_demo_action_flow_lookup_table as _action_flow_lookup_table,
    command_mvp_demo_action_flow_step as _action_flow_step,
    command_mvp_demo_engine_actions as _demo_engine_actions,
    command_mvp_demo_command_action_lookup_table as _command_action_lookup_table,
    command_mvp_demo_readiness_action_line_lookup_table as _readiness_action_line_lookup_table,
    command_mvp_demo_readiness_action_argv_lookup_table as _readiness_action_argv_lookup_table,
    command_mvp_demo_readiness_action_entry as _readiness_action_entry,
    command_mvp_demo_readiness_action_smoke_summary as _readiness_action_smoke_summary,
    command_mvp_demo_readiness_action_summary as _readiness_action_summary,
    command_mvp_demo_readiness_gate as _readiness_gate,
    command_mvp_demo_readiness_gate_summary as _readiness_gate_summary,
    command_mvp_demo_readiness_smoke_plan_summary as _readiness_smoke_plan_summary,
    command_mvp_demo_readiness_is_complete as _readiness_is_complete,
    command_mvp_demo_readiness_missing_engine_actions as _readiness_missing_engine_actions,
    require_command_mvp_demo_readiness_complete as _require_readiness_complete,
    command_mvp_demo_readiness_entry_for_argv as _readiness_entry_for_argv,
    command_mvp_demo_readiness_entry_for_command as _readiness_entry_for_command,
    command_mvp_demo_readiness_entry_for_demo_path_step as _readiness_entry_for_demo_path_step,
    command_mvp_demo_readiness_entry_for_engine_action as _readiness_entry_for_engine_action,
    command_mvp_demo_readiness_entry_for_flow_step as _readiness_entry_for_flow_step,
    command_mvp_demo_readiness_argv_for_command as _readiness_argv_for_command,
    command_mvp_demo_readiness_argv_for_demo_path_step as _readiness_argv_for_demo_path_step,
    command_mvp_demo_readiness_argv_for_engine_action as _readiness_argv_for_engine_action,
    command_mvp_demo_readiness_argv_for_flow_step as _readiness_argv_for_flow_step,
    command_mvp_demo_readiness_command_for_argv as _readiness_command_for_argv,
    command_mvp_demo_readiness_command_for_demo_path_step as _readiness_command_for_demo_path_step,
    command_mvp_demo_readiness_command_for_engine_action as _readiness_command_for_engine_action,
    command_mvp_demo_readiness_command_for_flow_step as _readiness_command_for_flow_step,
    command_mvp_demo_readiness_demo_path_step_for_command as _readiness_demo_path_step_for_command,
    command_mvp_demo_readiness_demo_path_step_for_argv as _readiness_demo_path_step_for_argv,
    command_mvp_demo_readiness_engine_actions_for_demo_path_step as _readiness_engine_actions_for_demo_path_step,
    command_mvp_demo_readiness_engine_actions_for_argv as _readiness_engine_actions_for_argv,
    command_mvp_demo_readiness_flow_step_for_command as _readiness_flow_step_for_command,
    command_mvp_demo_readiness_flow_step_for_demo_path_step as _readiness_flow_step_for_demo_path_step,
    command_mvp_demo_readiness_flow_step_for_argv as _readiness_flow_step_for_argv,
    command_mvp_demo_readiness_argv_for_argv as _readiness_argv_for_argv,
    command_mvp_demo_readiness_line_for_argv as _readiness_line_for_argv,
    command_mvp_demo_readiness_line_for_command as _readiness_line_for_command,
    command_mvp_demo_readiness_line_for_demo_path_step as _readiness_line_for_demo_path_step,
    command_mvp_demo_readiness_line_for_engine_action as _readiness_line_for_engine_action,
    command_mvp_demo_readiness_line_for_flow_step as _readiness_line_for_flow_step,
    command_mvp_demo_readiness_lookup_table as _readiness_lookup_table,
    command_mvp_demo_readiness_summary as _readiness_summary,
)

__all__ = [
    "canonical_command",
    "canonical_command_action_argv_lookup_table",
    "canonical_command_action_demo_path_lookup_table",
    "canonical_command_action_lookup_table",
    "canonical_command_action_readiness_entry",
    "canonical_command_action_readiness_entry_for_engine_action",
    "canonical_command_action_readiness_summary",
    "canonical_command_readiness_gate",
    "canonical_command_readiness_gate_summary",
    "canonical_command_demo_path_readiness_contract",
    "canonical_command_demo_path_readiness_summary",
    "canonical_command_readiness_smoke_plan_summary",
    "canonical_command_require_readiness_complete",
    "canonical_command_action_line_lookup_table",
    "canonical_command_action_smoke_summary",
    "canonical_command_readiness_is_complete",
    "canonical_command_readiness_missing_engine_actions",
    "canonical_command_action_flow_lookup_table",
    "canonical_command_demo_path_step_for_engine_action",
    "canonical_command_action_smoke_cli_argv",
    "canonical_command_action_smoke_cli_lines",
    "canonical_command_action_smoke_cli_lookup_table",
    "canonical_command_action_smoke_cli_summary",
    "canonical_command_demo_path_step",
    "canonical_command_demo_smoke_cli_argv",
    "canonical_command_demo_smoke_cli_lines",
    "canonical_command_demo_smoke_cli_lookup_table",
    "canonical_command_demo_smoke_cli_summary",
    "canonical_command_demo_engine_actions",
    "canonical_command_demo_path_step_for_argv",
    "canonical_command_argv",
    "canonical_command_argv_for_demo_path_step",
    "canonical_command_argv_for_engine_action",
    "canonical_command_argv_for_flow_step",
    "canonical_command_argv_for_argv",
    "canonical_command_command_for_argv",
    "canonical_command_engine_actions",
    "canonical_command_engine_actions_for_demo_path_step",
    "canonical_command_engine_actions_for_argv",
    "canonical_command_engine_actions_for_flow_step",
    "canonical_command_flow_step",
    "canonical_command_flow_step_for_demo_path_step",
    "canonical_command_flow_step_for_argv",
    "canonical_command_flow_step_for_engine_action",
    "canonical_command_for_demo_path_step",
    "canonical_command_for_engine_action",
    "canonical_command_for_flow_step",
    "canonical_command_line",
    "canonical_command_line_for_demo_path_step",
    "canonical_command_line_for_argv",
    "canonical_command_line_for_engine_action",
    "canonical_command_line_for_flow_step",
    "canonical_command_readiness_entry_for_argv",
    "canonical_command_readiness_entry_for_command",
    "canonical_command_readiness_entry_for_demo_path_step",
    "canonical_command_readiness_entry_for_engine_action",
    "canonical_command_readiness_entry_for_flow_step",
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


def canonical_command_action_smoke_summary() -> tuple[tuple[str, str, str, str, str], ...]:
    return _readiness_action_smoke_summary()


def canonical_command_readiness_gate() -> CommandDemoReadinessGate:
    return _readiness_gate()


def canonical_command_readiness_gate_summary() -> tuple[
    bool,
    tuple[str, ...],
    tuple[str, ...],
    tuple[tuple[str, str], ...],
]:
    return _readiness_gate_summary()


def canonical_command_demo_path_readiness_contract():
    return _path_readiness_contract()


def canonical_command_demo_path_readiness_summary() -> tuple[
    tuple[int, str, str, str, str, tuple[str, ...], tuple[tuple[str, str], ...]],
    ...,
]:
    return _path_readiness_summary()


def canonical_command_require_readiness_complete() -> CommandDemoReadinessGate:
    return _require_readiness_complete()


def canonical_command_readiness_smoke_plan_summary() -> tuple[
    tuple[int, str, str, str, str, tuple[tuple[str, str], ...]],
    ...,
]:
    return _readiness_smoke_plan_summary()


def canonical_command_readiness_missing_engine_actions() -> tuple[str, ...]:
    return _readiness_missing_engine_actions()


def canonical_command_readiness_is_complete() -> bool:
    return _readiness_is_complete()


def canonical_command_readiness_entry_for_flow_step(flow_step: str) -> CommandDemoReadinessEntry | None:
    return _readiness_entry_for_flow_step(flow_step)


def canonical_command_readiness_entry_for_command(command_name: str) -> CommandDemoReadinessEntry | None:
    return _readiness_entry_for_command(command_name)


def canonical_command_readiness_entry_for_demo_path_step(
    demo_path_step: str,
) -> CommandDemoReadinessEntry | None:
    return _readiness_entry_for_demo_path_step(demo_path_step)


def canonical_command_readiness_entry_for_argv(argv: Sequence[str]) -> CommandDemoReadinessEntry | None:
    return _readiness_entry_for_argv(argv)


def canonical_command_action_readiness_entry_for_engine_action(
    engine_action: str,
) -> CommandDemoReadinessActionEntry | None:
    return _readiness_action_entry(engine_action)


def canonical_command_action_readiness_entry(
    engine_action: str,
) -> CommandDemoReadinessActionEntry | None:
    return canonical_command_action_readiness_entry_for_engine_action(engine_action)


def canonical_command_readiness_entry_for_engine_action(
    engine_action: str,
) -> CommandDemoReadinessEntry | None:
    return _readiness_entry_for_engine_action(engine_action)


def canonical_command_demo_smoke_cli_summary() -> tuple[
    tuple[int, str, str, tuple[str, ...], str, tuple[str, ...]],
    ...,
]:
    return _smoke_cli_script_summary()


def canonical_command_demo_smoke_cli_lookup_table() -> tuple[tuple[int, tuple[str, ...]], ...]:
    return _smoke_cli_script_lookup_table()


def canonical_command_demo_smoke_cli_lines() -> tuple[tuple[int, str, str, str], ...]:
    return _smoke_cli_script_lines()


def canonical_command_demo_smoke_cli_argv(ordinal: int) -> tuple[str, ...]:
    return _smoke_cli_script_argv(ordinal)


def canonical_command_action_smoke_cli_summary() -> tuple[
    tuple[int, str, str, str, tuple[str, ...], str],
    ...,
]:
    return _action_smoke_script_summary()


def canonical_command_action_smoke_cli_lookup_table() -> tuple[
    tuple[int, str, tuple[str, ...]],
    ...,
]:
    return _action_smoke_script_lookup_table()


def canonical_command_action_smoke_cli_lines() -> tuple[tuple[int, str, str, str, str], ...]:
    return _action_smoke_script_lines()


def canonical_command_action_smoke_cli_argv(ordinal: int) -> tuple[str, ...]:
    return _action_smoke_script_argv(ordinal)


def canonical_command_action_argv_lookup_table() -> tuple[tuple[str, tuple[str, ...]], ...]:
    return _readiness_action_argv_lookup_table()


def canonical_command_action_line_lookup_table() -> tuple[tuple[str, str], ...]:
    return _readiness_action_line_lookup_table()


def canonical_command_action_lookup_table() -> tuple[tuple[str, tuple[str, ...]], ...]:
    return _command_action_lookup_table()


def canonical_command_demo_engine_actions() -> tuple[str, ...]:
    return _demo_engine_actions()


def canonical_command_action_flow_lookup_table() -> tuple[tuple[str, str], ...]:
    return _action_flow_lookup_table()


def canonical_command_action_demo_path_lookup_table() -> tuple[tuple[str, str], ...]:
    return _action_demo_path_lookup_table()


def canonical_command_engine_actions(command_name: str) -> tuple[str, ...]:
    requested_command = canonical_command(command_name)
    return dict(canonical_command_action_lookup_table()).get(requested_command, ())


def canonical_command_argv_for_demo_path_step(demo_path_step: str) -> tuple[str, ...]:
    return _readiness_argv_for_demo_path_step(demo_path_step)


def canonical_command_argv(command_name: str) -> tuple[str, ...]:
    return _readiness_argv_for_command(command_name)


def canonical_command_line(command_name: str) -> str:
    return _readiness_line_for_command(command_name)


def canonical_command_line_for_demo_path_step(demo_path_step: str) -> str:
    return _readiness_line_for_demo_path_step(demo_path_step)


def canonical_command_flow_step(command_name: str) -> str | None:
    return _readiness_flow_step_for_command(command_name)


def canonical_command_flow_step_for_demo_path_step(demo_path_step: str) -> str | None:
    return _readiness_flow_step_for_demo_path_step(demo_path_step)


def canonical_command_demo_path_step(command_name: str) -> str | None:
    return _readiness_demo_path_step_for_command(command_name)


def canonical_command_for_engine_action(engine_action: str) -> str | None:
    return _readiness_command_for_engine_action(engine_action)


def canonical_command_argv_for_engine_action(engine_action: str) -> tuple[str, ...]:
    return _readiness_argv_for_engine_action(engine_action)


def canonical_command_line_for_engine_action(engine_action: str) -> str:
    return _readiness_line_for_engine_action(engine_action)


def canonical_command_flow_step_for_engine_action(engine_action: str) -> str | None:
    return _action_flow_step(engine_action)


def canonical_command_demo_path_step_for_engine_action(engine_action: str) -> str | None:
    return _action_demo_path_step(engine_action)


def canonical_command_flow_step_for_argv(argv: Sequence[str]) -> str | None:
    return _readiness_flow_step_for_argv(argv)


def canonical_command_command_for_argv(argv: Sequence[str]) -> str | None:
    return _readiness_command_for_argv(argv)


def canonical_command_demo_path_step_for_argv(argv: Sequence[str]) -> str | None:
    return _readiness_demo_path_step_for_argv(argv)


def canonical_command_engine_actions_for_argv(argv: Sequence[str]) -> tuple[str, ...]:
    return _readiness_engine_actions_for_argv(argv)


def canonical_command_line_for_argv(argv: Sequence[str]) -> str:
    return _readiness_line_for_argv(argv)


def canonical_command_argv_for_argv(argv: Sequence[str]) -> tuple[str, ...]:
    return _readiness_argv_for_argv(argv)


def canonical_command_for_flow_step(flow_step: str) -> str | None:
    return _readiness_command_for_flow_step(flow_step)


def canonical_command_for_demo_path_step(demo_path_step: str) -> str | None:
    return _readiness_command_for_demo_path_step(demo_path_step)


def canonical_command_argv_for_flow_step(flow_step: str) -> tuple[str, ...]:
    return _readiness_argv_for_flow_step(flow_step)


def canonical_command_line_for_flow_step(flow_step: str) -> str:
    return _readiness_line_for_flow_step(flow_step)


def canonical_command_engine_actions_for_flow_step(flow_step: str) -> tuple[str, ...]:
    requested_command = canonical_command_for_flow_step(flow_step)
    if requested_command is None:
        return ()
    return canonical_command_engine_actions(requested_command)


def canonical_command_engine_actions_for_demo_path_step(demo_path_step: str) -> tuple[str, ...]:
    return _readiness_engine_actions_for_demo_path_step(demo_path_step)
