from __future__ import annotations

from src.qual.commands.catalog import (
    canonical_command as _canonical_command,
    command_mvp_demo_readiness_argv_for_engine_action as _readiness_argv_for_engine_action,
    command_mvp_demo_readiness_argv_for_flow_step as _readiness_argv_for_flow_step,
    command_mvp_demo_readiness_command_for_engine_action as _readiness_command_for_engine_action,
    command_mvp_demo_readiness_command_for_flow_step as _readiness_command_for_flow_step,
)

__all__ = [
    "canonical_command",
    "canonical_command_argv_for_engine_action",
    "canonical_command_argv_for_flow_step",
    "canonical_command_for_engine_action",
    "canonical_command_for_flow_step",
]


def canonical_command(name: str) -> str:
    return _canonical_command(name)


def canonical_command_for_engine_action(engine_action: str) -> str | None:
    return _readiness_command_for_engine_action(engine_action)


def canonical_command_argv_for_engine_action(engine_action: str) -> tuple[str, ...]:
    return _readiness_argv_for_engine_action(engine_action)


def canonical_command_for_flow_step(flow_step: str) -> str | None:
    return _readiness_command_for_flow_step(flow_step)


def canonical_command_argv_for_flow_step(flow_step: str) -> tuple[str, ...]:
    return _readiness_argv_for_flow_step(flow_step)
