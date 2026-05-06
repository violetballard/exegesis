from __future__ import annotations

import hashlib
import json
import re
import shlex
from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import PurePath


SHELL_ENV_ASSIGNMENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=.*")
SHELL_REDIRECT_OPERATOR_RE = re.compile(r"(?:[0-9]+)?(?:>>?|<<?|<>|>&|<&)|&>>?")
SHELL_REDIRECT_WITH_TARGET_RE = re.compile(
    r"(?:(?:[0-9]+)?(?:>>?|<<?|<>|>&|<&)|&>>?).+"
)


@dataclass(frozen=True)
class CommandSpec:
    name: str
    aliases: tuple[str, ...] = ()
    description: str = ""
    flow_step: str = "general"


@dataclass(frozen=True)
class CommandManifestEntry:
    name: str
    aliases: tuple[str, ...]
    description: str
    flow_step: str
    lookup_tokens: tuple[str, ...]


@dataclass(frozen=True)
class CommandFlowEntry:
    flow_step: str
    name: str
    aliases: tuple[str, ...]
    description: str
    lookup_tokens: tuple[str, ...]


@dataclass(frozen=True)
class CommandFlowSurfaceEntry:
    flow_step: str
    name: str
    aliases: tuple[str, ...]
    description: str
    lookup_tokens: tuple[str, ...]
    surface_tokens: tuple[str, ...]


@dataclass(frozen=True)
class CommandFlowSequence:
    flow_steps: tuple[str, ...]
    names: tuple[str, ...]
    lookup_table: tuple[tuple[str, str], ...]
    lookup_tokens: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class CommandSurfaceContract:
    flow_steps: tuple[str, ...]
    names: tuple[str, ...]
    smoke_tokens: tuple[str, ...]
    manifest: tuple[CommandManifestEntry, ...]
    lookup_table: tuple[tuple[str, str], ...]
    lookup_index: tuple[tuple[str, str], ...]
    lookup_tokens: tuple[tuple[str, ...], ...]
    flow_catalog: tuple[CommandFlowEntry, ...]
    lookup_surface: tuple[tuple[str, str], ...] = ()
    flow_tokens: tuple[str, ...] = ()
    flow_surface_tokens: tuple[tuple[str, ...], ...] = ()
    route_catalog: tuple[CommandFlowRouteEntry, ...] = ()
    route_summary: tuple[tuple[str, str, tuple[str, ...]], ...] = ()


@dataclass(frozen=True)
class CommandCliContract:
    tokens: tuple[str, ...]
    canonical_names: tuple[str, ...]
    lookup_table: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CommandCliRouteContract:
    """Bundle the parser surface, deterministic MVP route order, route catalog, and smoke surface."""

    tokens: tuple[str, ...]
    canonical_names: tuple[str, ...]
    smoke_tokens: tuple[str, ...]
    lookup_table: tuple[tuple[str, str], ...]
    flow_steps: tuple[str, ...]
    flow_names: tuple[str, ...]
    route_summary: tuple[tuple[str, str, tuple[str, ...]], ...]
    lookup_surface: tuple[tuple[str, str], ...] = ()
    flow_surface_tokens: tuple[tuple[str, ...], ...] = ()
    route_catalog: tuple[CommandFlowRouteEntry, ...] = ()


@dataclass(frozen=True)
class CommandCliFlowEntry:
    token: str
    canonical_name: str
    flow_step: str


@dataclass(frozen=True)
class CommandCliFlowContract:
    entries: tuple[CommandCliFlowEntry, ...]


@dataclass(frozen=True)
class CommandFlowRouteEntry:
    flow_step: str
    name: str
    cli_tokens: tuple[str, ...]
    lookup_tokens: tuple[str, ...]
    surface_tokens: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class CommandFlowRouteContract:
    entries: tuple[CommandFlowRouteEntry, ...]


@dataclass(frozen=True)
class CommandDemoPathEntry:
    flow_step: str
    name: str
    cli_tokens: tuple[str, ...]
    engine_actions: tuple[str, ...]
    demo_path_step: str


@dataclass(frozen=True)
class CommandDemoPathContract:
    entries: tuple[CommandDemoPathEntry, ...]


@dataclass(frozen=True)
class CommandDemoSmokeEntry:
    smoke_token: str
    name: str
    flow_step: str
    demo_path_step: str
    engine_actions: tuple[str, ...]


@dataclass(frozen=True)
class CommandDemoSmokeContract:
    entries: tuple[CommandDemoSmokeEntry, ...]


@dataclass(frozen=True)
class CommandDemoSmokeCommandEntry:
    flow_step: str
    name: str
    argv: tuple[str, ...]
    demo_path_step: str
    engine_actions: tuple[str, ...]


@dataclass(frozen=True)
class CommandDemoSmokeCommandContract:
    entries: tuple[CommandDemoSmokeCommandEntry, ...]


@dataclass(frozen=True)
class CommandDemoSmokeMatrixEntry:
    flow_step: str
    name: str
    argv: tuple[str, ...]
    cli_tokens: tuple[str, ...]
    demo_path_step: str
    engine_actions: tuple[str, ...]


@dataclass(frozen=True)
class CommandDemoSmokeMatrixContract:
    entries: tuple[CommandDemoSmokeMatrixEntry, ...]


@dataclass(frozen=True)
class CommandDemoSmokeScriptStep:
    ordinal: int
    flow_step: str
    name: str
    argv: tuple[str, ...]
    demo_path_step: str
    engine_actions: tuple[str, ...]


@dataclass(frozen=True)
class CommandDemoSmokeScriptContract:
    steps: tuple[CommandDemoSmokeScriptStep, ...]


@dataclass(frozen=True)
class CommandDemoSmokeCliScriptStep:
    ordinal: int
    flow_step: str
    name: str
    command_argv: tuple[str, ...]
    demo_path_step: str
    engine_actions: tuple[str, ...]


@dataclass(frozen=True)
class CommandDemoSmokeCliScriptContract:
    steps: tuple[CommandDemoSmokeCliScriptStep, ...]


@dataclass(frozen=True)
class CommandDemoSmokeArgvEntry:
    flow_step: str
    argv: tuple[str, ...]


@dataclass(frozen=True)
class CommandDemoSmokeArgvContract:
    entries: tuple[CommandDemoSmokeArgvEntry, ...]


@dataclass(frozen=True)
class CommandDemoActionEntry:
    engine_action: str
    flow_step: str
    name: str
    smoke_token: str
    demo_path_step: str


@dataclass(frozen=True)
class CommandDemoActionContract:
    entries: tuple[CommandDemoActionEntry, ...]


@dataclass(frozen=True)
class CommandDemoActionRouteEntry:
    engine_action: str
    flow_step: str
    name: str
    cli_tokens: tuple[str, ...]
    smoke_token: str
    demo_path_step: str


@dataclass(frozen=True)
class CommandDemoActionRouteContract:
    entries: tuple[CommandDemoActionRouteEntry, ...]


@dataclass(frozen=True)
class CommandDemoActionSmokeArgvEntry:
    engine_action: str
    flow_step: str
    name: str
    argv: tuple[str, ...]
    smoke_token: str
    demo_path_step: str


@dataclass(frozen=True)
class CommandDemoActionSmokeArgvContract:
    entries: tuple[CommandDemoActionSmokeArgvEntry, ...]


@dataclass(frozen=True)
class CommandDemoActionSmokeCliArgvEntry:
    engine_action: str
    flow_step: str
    name: str
    command_argv: tuple[str, ...]
    smoke_token: str
    demo_path_step: str


@dataclass(frozen=True)
class CommandDemoActionSmokeCliArgvContract:
    entries: tuple[CommandDemoActionSmokeCliArgvEntry, ...]


@dataclass(frozen=True)
class CommandDemoActionSmokeScriptStep:
    ordinal: int
    engine_action: str
    flow_step: str
    name: str
    command_argv: tuple[str, ...]
    smoke_token: str
    demo_path_step: str


@dataclass(frozen=True)
class CommandDemoActionSmokeScriptContract:
    steps: tuple[CommandDemoActionSmokeScriptStep, ...]


@dataclass(frozen=True)
class CommandDemoReadinessEntry:
    ordinal: int
    flow_step: str
    name: str
    command_argv: tuple[str, ...]
    demo_path_step: str
    engine_actions: tuple[str, ...]
    action_command_argv: tuple[tuple[str, tuple[str, ...]], ...]


@dataclass(frozen=True)
class CommandDemoReadinessContract:
    entries: tuple[CommandDemoReadinessEntry, ...]


@dataclass(frozen=True)
class CommandDemoReadinessCliEntry:
    cli_token: str
    flow_step: str
    name: str
    command_argv: tuple[str, ...]
    demo_path_step: str
    engine_actions: tuple[str, ...]


@dataclass(frozen=True)
class CommandDemoReadinessCliContract:
    entries: tuple[CommandDemoReadinessCliEntry, ...]


@dataclass(frozen=True)
class CommandDemoReadinessActionEntry:
    engine_action: str
    flow_step: str
    name: str
    command_argv: tuple[str, ...]
    action_command_argv: tuple[str, ...]
    demo_path_step: str


@dataclass(frozen=True)
class CommandDemoReadinessActionContract:
    entries: tuple[CommandDemoReadinessActionEntry, ...]


@dataclass(frozen=True)
class CommandDemoReadinessExactActionEntry:
    engine_action: str
    flow_step: str
    name: str
    command_argv: tuple[str, ...]
    command_line: str
    demo_path_step: str


@dataclass(frozen=True)
class CommandDemoReadinessExactCliAuditEntry:
    engine_action: str
    flow_step: str
    name: str
    parser_token: str
    command_line: str
    canonical_command_line: str
    demo_path_step: str
    is_cli_entrypoint: bool


@dataclass(frozen=True)
class CommandDemoReadinessExactCliAuditContract:
    is_complete: bool
    entries: tuple[CommandDemoReadinessExactCliAuditEntry, ...]
    invalid_engine_actions: tuple[str, ...]


@dataclass(frozen=True)
class CommandDemoReadinessExactActionContract:
    entries: tuple[CommandDemoReadinessExactActionEntry, ...]


@dataclass(frozen=True)
class CommandDemoReadinessExactActionScriptStep:
    ordinal: int
    engine_action: str
    flow_step: str
    name: str
    command_argv: tuple[str, ...]
    command_line: str
    demo_path_step: str


@dataclass(frozen=True)
class CommandDemoReadinessExactActionScriptContract:
    steps: tuple[CommandDemoReadinessExactActionScriptStep, ...]


@dataclass(frozen=True)
class CommandDemoReadinessSmokePlanStep:
    ordinal: int
    flow_step: str
    name: str
    command_line: str
    demo_path_step: str
    action_lines: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CommandDemoReadinessSmokePlan:
    steps: tuple[CommandDemoReadinessSmokePlanStep, ...]


@dataclass(frozen=True)
class CommandDemoPathReadinessStep:
    ordinal: int
    demo_path_step: str
    flow_step: str
    name: str
    command_line: str
    engine_actions: tuple[str, ...]
    action_lines: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CommandDemoPathReadinessContract:
    steps: tuple[CommandDemoPathReadinessStep, ...]


@dataclass(frozen=True)
class CommandDemoReadinessHandoffEntry:
    ordinal: int
    demo_path_step: str
    flow_step: str
    name: str
    command_line: str
    action_lines: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CommandDemoReadinessHandoffContract:
    entries: tuple[CommandDemoReadinessHandoffEntry, ...]


@dataclass(frozen=True)
class CommandDemoReadinessHandoffLine:
    ordinal: int
    demo_path_step: str
    flow_step: str
    name: str
    line: str


@dataclass(frozen=True)
class CommandDemoReadinessHandoffLineContract:
    lines: tuple[CommandDemoReadinessHandoffLine, ...]


@dataclass(frozen=True)
class CommandDemoReadinessHandoffChecklistLine:
    ordinal: int
    demo_path_step: str
    flow_step: str
    name: str
    line: str


@dataclass(frozen=True)
class CommandDemoReadinessHandoffChecklistContract:
    lines: tuple[CommandDemoReadinessHandoffChecklistLine, ...]


@dataclass(frozen=True)
class CommandDemoReadinessRouteEntry:
    ordinal: int
    demo_path_step: str
    flow_step: str
    name: str
    cli_tokens: tuple[str, ...]
    command_line: str
    engine_actions: tuple[str, ...]
    action_lines: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CommandDemoReadinessRouteContract:
    entries: tuple[CommandDemoReadinessRouteEntry, ...]


@dataclass(frozen=True)
class CommandDemoReadinessHandoffActionStep:
    ordinal: int
    demo_path_step: str
    flow_step: str
    name: str
    command_line: str
    exact_action_lines: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CommandDemoReadinessHandoffActionContract:
    steps: tuple[CommandDemoReadinessHandoffActionStep, ...]


@dataclass(frozen=True)
class CommandDemoReadinessActionSequenceStep:
    ordinal: int
    engine_action: str
    demo_path_step: str
    flow_step: str
    name: str
    command_line: str


@dataclass(frozen=True)
class CommandDemoReadinessActionSequenceContract:
    steps: tuple[CommandDemoReadinessActionSequenceStep, ...]


@dataclass(frozen=True)
class CommandDemoReadinessGate:
    is_complete: bool
    missing_engine_actions: tuple[str, ...]
    command_lines: tuple[str, ...]
    action_lines: tuple[tuple[str, str], ...]
    covered_flow_steps: tuple[str, ...] = ()
    missing_flow_steps: tuple[str, ...] = ()
    cli_command_lines: tuple[str, ...] = ()
    cli_exact_action_lines: tuple[str, ...] = ()
    invalid_cli_argv: tuple[tuple[str, ...], ...] = ()
    invalid_cli_exact_action_argv: tuple[tuple[str, ...], ...] = ()


@dataclass(frozen=True)
class CommandDemoReadinessReport:
    is_complete: bool
    missing_engine_actions: tuple[str, ...]
    command_lines: tuple[str, ...]
    action_lines: tuple[tuple[str, str], ...]
    checklist_lines: tuple[str, ...]
    markdown: str


@dataclass(frozen=True)
class CommandDemoReadinessHandoffPacket:
    scope_completed: str
    roadmap_items: tuple[str, ...]
    vision_capabilities: tuple[str, ...]
    routing_provider_impact: str
    fingerprint_algorithm: str
    fingerprint_digest: str
    canonical_demo_path_steps: tuple[str, ...]
    command_lines: tuple[str, ...]
    exact_action_lines: tuple[str, ...]
    checklist_lines: tuple[str, ...]
    is_complete: bool
    missing_flow_steps: tuple[str, ...]
    missing_engine_actions: tuple[str, ...]
    invalid_argv: tuple[tuple[str, ...], ...]
    action_steps: tuple[CommandDemoReadinessHandoffActionStep, ...] = ()
    cli_exact_action_lines: tuple[str, ...] = ()
    step_seals: tuple[CommandDemoReadinessStepSeal, ...] = ()
    cli_step_validations: tuple[CommandDemoReadinessCliStepValidation, ...] = ()


@dataclass(frozen=True)
class CommandDemoReadinessHandoffStepStatus:
    ordinal: int
    demo_path_step: str
    flow_step: str
    name: str
    command_line: str
    parser_token: str
    engine_actions: tuple[str, ...]
    exact_action_lines: tuple[tuple[str, str], ...]
    is_cli_entrypoint: bool
    is_complete: bool


@dataclass(frozen=True)
class CommandDemoReadinessHandoffStepStatusContract:
    fingerprint_algorithm: str
    fingerprint_digest: str
    is_complete: bool
    steps: tuple[CommandDemoReadinessHandoffStepStatus, ...]


@dataclass(frozen=True)
class CommandDemoReadinessHandoffAudit:
    is_complete: bool
    fingerprint_digest: str
    packet_fingerprint_digest: str
    command_lines_match: bool
    exact_action_lines_match: bool
    cli_exact_action_lines_match: bool
    invalid_argv: tuple[tuple[str, ...], ...]
    missing_flow_steps: tuple[str, ...]
    missing_engine_actions: tuple[str, ...]


@dataclass(frozen=True)
class CommandDemoReadinessSeal:
    is_complete: bool
    flow_steps: tuple[str, ...]
    command_lines: tuple[str, ...]
    exact_action_lines: tuple[str, ...]
    cli_exact_action_lines: tuple[str, ...]
    engine_actions: tuple[str, ...]
    missing_flow_steps: tuple[str, ...]
    missing_engine_actions: tuple[str, ...]
    invalid_argv: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class CommandDemoReadinessFingerprint:
    algorithm: str
    digest: str
    flow_steps: tuple[str, ...]
    engine_actions: tuple[str, ...]
    command_lines: tuple[str, ...]
    exact_action_lines: tuple[str, ...]
    cli_exact_action_lines: tuple[str, ...]


@dataclass(frozen=True)
class CommandDemoReadinessStepSeal:
    ordinal: int
    demo_path_step: str
    flow_step: str
    name: str
    command_argv: tuple[str, ...]
    command_line: str
    engine_actions: tuple[str, ...]
    exact_action_lines: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CommandDemoReadinessStepSealContract:
    steps: tuple[CommandDemoReadinessStepSeal, ...]


@dataclass(frozen=True)
class CommandDemoReadinessCliStepValidation:
    ordinal: int
    demo_path_step: str
    flow_step: str
    name: str
    command_line: str
    parser_token: str
    canonical_command_line: str
    is_cli_entrypoint: bool


@dataclass(frozen=True)
class CommandDemoReadinessCliStepValidationContract:
    steps: tuple[CommandDemoReadinessCliStepValidation, ...]


@dataclass(frozen=True)
class CommandDemoReadinessIndexEntry:
    ordinal: int
    demo_path_step: str
    flow_step: str
    name: str
    command_line: str
    engine_actions: tuple[str, ...]
    exact_action_lines: tuple[tuple[str, str], ...]
    readiness_fingerprint_digest: str
    step_fingerprint_digest: str


@dataclass(frozen=True)
class CommandDemoReadinessIndexContract:
    fingerprint_algorithm: str
    readiness_fingerprint_digest: str
    entries: tuple[CommandDemoReadinessIndexEntry, ...]


@dataclass(frozen=True)
class CommandDemoReadinessShellScript:
    lines: tuple[str, ...]
    command_lines: tuple[str, ...]
    action_lines: tuple[tuple[str, str], ...]
    text: str


@dataclass(frozen=True)
class CommandDemoReadinessTraceEntry:
    ordinal: int
    engine_action: str
    demo_path_step: str
    flow_step: str
    name: str
    command_line: str
    action_line: str


@dataclass(frozen=True)
class CommandDemoReadinessTraceContract:
    entries: tuple[CommandDemoReadinessTraceEntry, ...]


@dataclass(frozen=True)
class CommandDemoReadinessCommandTraceEntry:
    ordinal: int
    demo_path_step: str
    flow_step: str
    name: str
    command_line: str
    action_lines: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CommandDemoReadinessCommandTraceContract:
    entries: tuple[CommandDemoReadinessCommandTraceEntry, ...]


@dataclass(frozen=True)
class CommandDemoReadinessExactActionRouteEntry:
    engine_action: str
    demo_path_step: str
    flow_step: str
    name: str
    cli_tokens: tuple[str, ...]
    command_argv: tuple[str, ...]
    command_line: str


@dataclass(frozen=True)
class CommandDemoReadinessExactActionRouteContract:
    entries: tuple[CommandDemoReadinessExactActionRouteEntry, ...]


@dataclass(frozen=True)
class CommandDemoCommandReadinessEntry:
    ordinal: int
    demo_path_step: str
    flow_step: str
    name: str
    command_line: str
    engine_actions: tuple[str, ...]
    exact_action_lines: tuple[tuple[str, str], ...]
    cli_exact_action_lines: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CommandDemoCommandReadinessContract:
    entries: tuple[CommandDemoCommandReadinessEntry, ...]


@dataclass(frozen=True)
class CommandDemoCommandSurfaceEntry:
    ordinal: int
    demo_path_step: str
    flow_step: str
    name: str
    command_argv: tuple[str, ...]
    command_line: str
    engine_actions: tuple[str, ...]
    exact_action_argv: tuple[tuple[str, tuple[str, ...]], ...]
    exact_action_lines: tuple[tuple[str, str], ...]
    cli_exact_action_lines: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CommandDemoCommandSurfaceContract:
    launcher_argv: tuple[str, ...]
    entries: tuple[CommandDemoCommandSurfaceEntry, ...]


@dataclass(frozen=True)
class CommandDemoSurfaceReadinessEntry:
    ordinal: int
    demo_path_step: str
    flow_step: str
    name: str
    cli_tokens: tuple[str, ...]
    command_argv: tuple[str, ...]
    command_line: str
    engine_actions: tuple[str, ...]
    exact_action_lines: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CommandDemoSurfaceReadinessContract:
    launcher_argv: tuple[str, ...]
    fingerprint_algorithm: str
    fingerprint_digest: str
    is_complete: bool
    entries: tuple[CommandDemoSurfaceReadinessEntry, ...]


@dataclass(frozen=True)
class CommandDemoCommandCoverageEntry:
    ordinal: int
    demo_path_step: str
    flow_step: str
    name: str
    command_line: str
    required_engine_actions: tuple[str, ...]
    covered_engine_actions: tuple[str, ...]
    missing_engine_actions: tuple[str, ...]
    is_complete: bool


@dataclass(frozen=True)
class CommandDemoCommandCoverageContract:
    entries: tuple[CommandDemoCommandCoverageEntry, ...]


@dataclass(frozen=True)
class CommandDemoSupportedLauncherReadinessEntry:
    launcher_argv: tuple[str, ...]
    is_complete: bool
    missing_engine_actions: tuple[str, ...]
    command_lines: tuple[str, ...]
    action_lines: tuple[tuple[str, str], ...]
    exact_action_lines: tuple[tuple[str, str], ...] = ()
    cli_smoke_lines: tuple[str, ...] = ()


@dataclass(frozen=True)
class CommandDemoSupportedLauncherReadinessContract:
    entries: tuple[CommandDemoSupportedLauncherReadinessEntry, ...]


@dataclass(frozen=True)
class CommandDemoReadinessArgvValidation:
    requested_argv: tuple[str, ...]
    canonical_argv: tuple[str, ...]
    command_line: str
    flow_step: str | None
    name: str | None
    demo_path_step: str | None
    engine_actions: tuple[str, ...]
    exact_engine_action: str | None = None


@dataclass(frozen=True)
class CommandDemoReadinessCliArgvValidation:
    requested_argv: tuple[str, ...]
    canonical_argv: tuple[str, ...]
    command_line: str
    parser_token: str | None
    is_cli_entrypoint: bool
    flow_step: str | None
    name: str | None
    demo_path_step: str | None
    engine_actions: tuple[str, ...]
    exact_engine_action: str | None = None


@dataclass(frozen=True)
class CommandDemoReadinessScriptValidation:
    requested_argv: tuple[tuple[str, ...], ...]
    canonical_argv: tuple[tuple[str, ...], ...]
    command_lines: tuple[str, ...]
    covered_flow_steps: tuple[str, ...]
    missing_flow_steps: tuple[str, ...]
    covered_engine_actions: tuple[str, ...]
    missing_engine_actions: tuple[str, ...]
    invalid_argv: tuple[tuple[str, ...], ...]
    is_complete: bool


@dataclass(frozen=True)
class CommandDemoExecutionPlanStep:
    ordinal: int
    demo_path_step: str
    flow_step: str
    name: str
    launcher_argv: tuple[str, ...]
    command_argv: tuple[str, ...]
    command_line: str
    engine_actions: tuple[str, ...]
    action_lines: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CommandDemoExecutionPlanContract:
    launcher_argv: tuple[str, ...]
    steps: tuple[CommandDemoExecutionPlanStep, ...]


@dataclass(frozen=True)
class CommandDemoActionCoverageEntry:
    engine_action: str
    demo_path_step: str
    flow_step: str
    name: str
    command_argv: tuple[str, ...]
    command_line: str
    action_line: str


@dataclass(frozen=True)
class CommandDemoActionCoverageContract:
    entries: tuple[CommandDemoActionCoverageEntry, ...]


@dataclass(frozen=True)
class CommandDemoCommandActionEntry:
    flow_step: str
    name: str
    cli_tokens: tuple[str, ...]
    smoke_token: str
    demo_path_step: str
    engine_actions: tuple[str, ...]


@dataclass(frozen=True)
class CommandDemoCommandActionContract:
    entries: tuple[CommandDemoCommandActionEntry, ...]


@dataclass(frozen=True)
class CommandDemoReadinessCommandAuditEntry:
    ordinal: int
    flow_step: str
    name: str
    demo_path_step: str
    command_line: str
    engine_actions: tuple[str, ...]
    exact_action_lines: tuple[tuple[str, str], ...]
    is_cli_entrypoint: bool
    is_complete: bool


@dataclass(frozen=True)
class CommandDemoReadinessCommandAuditContract:
    fingerprint_algorithm: str
    fingerprint_digest: str
    is_complete: bool
    entries: tuple[CommandDemoReadinessCommandAuditEntry, ...]


def _normalize_token(value: str) -> str:
    normalized = re.sub(r"[-_\s]+", "-", value.strip().casefold())
    return normalized.strip("-")


def _lookup_aliases(spec: CommandSpec) -> tuple[str, ...]:
    # Keep the surface stable if a spec repeats the command name verbatim.
    return tuple(alias for alias in spec.aliases if alias != spec.name)


def _lookup_tokens(spec: CommandSpec) -> tuple[str, ...]:
    return (spec.name, *_lookup_aliases(spec))


def _flow_surface_tokens(*tokens: str) -> tuple[str, ...]:
    seen_tokens: set[str] = set()
    surface_tokens: list[str] = []
    for token in tokens:
        normalized_token = _normalize_token(token)
        if not normalized_token or normalized_token in seen_tokens:
            continue
        seen_tokens.add(normalized_token)
        surface_tokens.append(normalized_token)
    return tuple(surface_tokens)


def _validate_flow_steps(flow_steps: tuple[str, ...]) -> None:
    seen_flow_steps: set[str] = set()
    for flow_step in flow_steps:
        normalized_flow_step = _normalize_token(flow_step)
        if not normalized_flow_step:
            raise ValueError("Command flow steps must not be empty")
        if normalized_flow_step in seen_flow_steps:
            raise ValueError(f"Duplicate command flow step order: {flow_step}")
        seen_flow_steps.add(normalized_flow_step)


def _normalize_flow_steps(flow_steps: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(_normalize_token(flow_step) for flow_step in flow_steps)


def _validate_cli_entrypoints() -> None:
    # Keep the parser surface explicit so the command contract stays deterministic.
    command_lookup = _COMMAND_SPEC_BY_ALIAS
    seen_entrypoints: set[str] = set()
    for entrypoint in _CLI_ENTRYPOINTS:
        normalized_entrypoint = _normalize_token(entrypoint)
        if not normalized_entrypoint:
            raise ValueError("Command CLI entrypoints must not be empty")
        if normalized_entrypoint in seen_entrypoints:
            raise ValueError(f"Duplicate command CLI entrypoint: {entrypoint}")
        seen_entrypoints.add(normalized_entrypoint)
        if normalized_entrypoint not in command_lookup:
            raise ValueError(f"Unknown CLI command entrypoint: {entrypoint}")


def _command_cli_tokens_by_name() -> dict[str, tuple[str, ...]]:
    tokens_by_name: dict[str, list[str]] = {}
    for token, canonical_name in command_cli_lookup_table():
        tokens_by_name.setdefault(canonical_name, []).append(token)
    return {name: tuple(tokens) for name, tokens in tokens_by_name.items()}


def _route_cli_tokens_by_name(specs: tuple[CommandSpec, ...]) -> dict[str, tuple[str, ...]]:
    # Keep the real parser surface for the default catalog, but fall back to the
    # supplied spec lookup tokens when callers build custom smoke surfaces.
    if specs == COMMAND_SPECS:
        return _command_cli_tokens_by_name()
    return {spec.name: _lookup_tokens(spec) for spec in specs}


COMMAND_SPECS: tuple[CommandSpec, ...] = (
    CommandSpec(
        name="bootstrap",
        aliases=("open", "project-open", "project"),
        description="Run the project bootstrap flow.",
        flow_step="project-open",
    ),
    CommandSpec(
        name="diff-preview",
        aliases=("diff", "diff_preview"),
        description="Preview unified diff output.",
        flow_step="patch-review",
    ),
    CommandSpec(
        name="context-basket",
        aliases=("context", "basket"),
        description="Manage retrieval context basket items.",
        flow_step="retrieval",
    ),
    CommandSpec(
        name="terminal",
        description="Run terminal export handoff routing.",
        flow_step="export-handoff",
    ),
)

# Keep the parser surface explicit: only these tokens are accepted by the current CLI.
# Each token must resolve through the command catalog so the surface cannot drift.
_CANONICAL_CLI_ENTRYPOINTS: tuple[str, ...] = (
    "bootstrap",
    "diff-preview",
    "diff",
    "context-basket",
    "terminal",
)
_CLI_ENTRYPOINTS: tuple[str, ...] = _CANONICAL_CLI_ENTRYPOINTS
COMMAND_SMOKE_CLI_LAUNCHER_ARGV: tuple[str, ...] = ("python", "-m", "src.main")
COMMAND_SMOKE_SCRIPT_LAUNCHER_ARGV: tuple[str, ...] = ("python", "src/main.py")
COMMAND_SMOKE_CLI_PYTHON3_LAUNCHER_ARGV: tuple[str, ...] = ("python3", "-m", "src.main")
COMMAND_SMOKE_SCRIPT_PYTHON3_LAUNCHER_ARGV: tuple[str, ...] = ("python3", "src/main.py")
COMMAND_SMOKE_UV_CLI_LAUNCHER_ARGV: tuple[str, ...] = ("uv", "run", "python", "-m", "src.main")
COMMAND_SMOKE_UV_SCRIPT_LAUNCHER_ARGV: tuple[str, ...] = ("uv", "run", "python", "src/main.py")
COMMAND_SMOKE_UV_CLI_PYTHON3_LAUNCHER_ARGV: tuple[str, ...] = ("uv", "run", "python3", "-m", "src.main")
COMMAND_SMOKE_UV_SCRIPT_PYTHON3_LAUNCHER_ARGV: tuple[str, ...] = ("uv", "run", "python3", "src/main.py")
COMMAND_SMOKE_ENV_CLI_LAUNCHER_ARGV: tuple[str, ...] = ("env", "python", "-m", "src.main")
COMMAND_SMOKE_ENV_SCRIPT_LAUNCHER_ARGV: tuple[str, ...] = ("env", "python", "src/main.py")
COMMAND_SMOKE_ENV_CLI_PYTHON3_LAUNCHER_ARGV: tuple[str, ...] = ("env", "python3", "-m", "src.main")
COMMAND_SMOKE_ENV_SCRIPT_PYTHON3_LAUNCHER_ARGV: tuple[str, ...] = ("env", "python3", "src/main.py")
COMMAND_SMOKE_SUPPORTED_LAUNCHER_ARGV: tuple[tuple[str, ...], ...] = (
    COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
    COMMAND_SMOKE_SCRIPT_LAUNCHER_ARGV,
    COMMAND_SMOKE_CLI_PYTHON3_LAUNCHER_ARGV,
    COMMAND_SMOKE_SCRIPT_PYTHON3_LAUNCHER_ARGV,
    COMMAND_SMOKE_UV_CLI_LAUNCHER_ARGV,
    COMMAND_SMOKE_UV_SCRIPT_LAUNCHER_ARGV,
    COMMAND_SMOKE_UV_CLI_PYTHON3_LAUNCHER_ARGV,
    COMMAND_SMOKE_UV_SCRIPT_PYTHON3_LAUNCHER_ARGV,
    COMMAND_SMOKE_ENV_CLI_LAUNCHER_ARGV,
    COMMAND_SMOKE_ENV_SCRIPT_LAUNCHER_ARGV,
    COMMAND_SMOKE_ENV_CLI_PYTHON3_LAUNCHER_ARGV,
    COMMAND_SMOKE_ENV_SCRIPT_PYTHON3_LAUNCHER_ARGV,
)
COMMAND_SMOKE_SUPPORTED_LAUNCHER_TAILS: tuple[tuple[str, ...], ...] = (
    ("-m", "src.main"),
    ("src/main.py",),
)
COMMAND_SMOKE_SUPPORTED_LAUNCHER_PREFIXES: tuple[tuple[str, ...], ...] = (
    ("uv", "run", "--"),
    ("uv", "run"),
)
COMMAND_SMOKE_UV_RUN_VALUE_OPTIONS: tuple[str, ...] = (
    "--config-file",
    "--directory",
    "--env-file",
    "--extra",
    "--group",
    "--index",
    "--index-url",
    "--keyring-provider",
    "--link-mode",
    "--no-group",
    "--only-group",
    "--project",
    "--python",
    "--refresh-package",
    "--resolution",
    "--upgrade-package",
    "--with",
    "--with-editable",
    "--with-requirements",
)
COMMAND_SMOKE_UV_RUN_FLAG_OPTIONS: tuple[str, ...] = (
    "--active",
    "--all-extras",
    "--all-groups",
    "--frozen",
    "--isolated",
    "--locked",
    "--managed-python",
    "--no-build",
    "--no-build-isolation",
    "--no-dev",
    "--no-default-groups",
    "--no-editable",
    "--no-index",
    "--no-managed-python",
    "--no-project",
    "--no-sources",
    "--no-sync",
    "--only-dev",
    "--refresh",
    "--upgrade",
)
COMMAND_SMOKE_SUPPORTED_PYTHON_LAUNCHERS: tuple[str, ...] = (
    "python",
    "python3",
)
COMMAND_SMOKE_PYTHON_FLAG_OPTIONS: tuple[str, ...] = (
    "-B",
    "-E",
    "-I",
    "-O",
    "-OO",
    "-P",
    "-S",
    "-s",
    "-u",
)
COMMAND_SMOKE_PYTHON_VALUE_OPTIONS: tuple[str, ...] = (
    "-W",
    "-X",
)
COMMAND_SMOKE_ENV_LAUNCHERS: tuple[str, ...] = (
    "env",
)
COMMAND_SMOKE_ENV_FLAGS: tuple[str, ...] = (
    "-i",
    "--ignore-environment",
)
COMMAND_SMOKE_ENV_VALUE_OPTIONS: tuple[str, ...] = (
    "-u",
    "--unset",
)
COMMAND_SMOKE_ENV_SPLIT_STRING_OPTIONS: tuple[str, ...] = (
    "-S",
    "--split-string",
)
COMMAND_SMOKE_SHELL_SETUP_COMMANDS: tuple[str, ...] = (
    "cd",
    "pwd",
)
COMMAND_SMOKE_SHELL_STATUS_COMMANDS: tuple[str, ...] = (
    "exit",
    "return",
)
COMMAND_SMOKE_SHELL_PROBE_COMMANDS: tuple[str, ...] = (
    "command",
)
COMMAND_SMOKE_SHELL_PROBE_FLAGS: tuple[str, ...] = (
    "-v",
    "-V",
)
COMMAND_SMOKE_SHELL_WRAPPER_COMMANDS: tuple[str, ...] = (
    "command",
    "exec",
    "time",
)
COMMAND_SMOKE_SHELL_WRAPPER_FLAGS: tuple[str, ...] = (
    "-p",
)
COMMAND_SMOKE_SHELL_OUTPUT_SINK_COMMANDS: tuple[str, ...] = (
    "tee",
)
COMMAND_SMOKE_SHELL_OUTPUT_SINK_FLAGS: tuple[str, ...] = (
    "-a",
    "--append",
)
COMMAND_SMOKE_SHELL_CONTROL_KEYWORDS: tuple[str, ...] = (
    "if",
    "then",
    "else",
    "elif",
    "fi",
    "for",
    "while",
    "until",
    "do",
    "done",
)
DEMO_COMMAND_FLOW_STEPS: tuple[str, ...] = (
    "project-open",
    "retrieval",
    "patch-review",
    "export-handoff",
)
MVP_COMMAND_FLOW_STEPS: tuple[str, ...] = DEMO_COMMAND_FLOW_STEPS
_DEMO_PATH_STEP_BY_FLOW_STEP: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "project-open",
        "open project/document",
        ("ExegesisAppService.open_project", "ExegesisAppService.open_document"),
    ),
    (
        "retrieval",
        "retrieve relevant material and gather context",
        ("ExegesisAppService.search_project", "ExegesisAppService.add_basket_item"),
    ),
    (
        "patch-review",
        "preview and apply or reject a patch",
        (
            "ExegesisAppService.revise_selection",
            "ExegesisAppService.apply_patch",
            "ExegesisAppService.reject_patch",
        ),
    ),
    (
        "export-handoff",
        "persist and continue",
        ("ExegesisAppService.save_document",),
    ),
)
_DEMO_SMOKE_ARGV_BY_FLOW_STEP: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("project-open", ("bootstrap",)),
    ("retrieval", ("context-basket", "list")),
    (
        "patch-review",
        (
            "diff-preview",
            "--original",
            "draft text",
            "--proposed",
            "revised draft text",
        ),
    ),
    (
        "export-handoff",
        (
            "terminal",
            "--operation-kind",
            "terminal_synthesis_request",
            "--message",
            "persist and continue",
        ),
    ),
)
_DEMO_ACTION_SMOKE_ARGV_BY_ENGINE_ACTION: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("ExegesisAppService.open_project", ("bootstrap",)),
    ("ExegesisAppService.open_document", ("bootstrap",)),
    ("ExegesisAppService.search_project", ("context-basket", "list")),
    ("ExegesisAppService.add_basket_item", ("context-basket", "add", "demo-retrieval-result")),
    (
        "ExegesisAppService.revise_selection",
        (
            "diff-preview",
            "--original",
            "draft text",
            "--proposed",
            "revised draft text",
        ),
    ),
    (
        "ExegesisAppService.apply_patch",
        (
            "diff-preview",
            "--original",
            "draft text",
            "--proposed",
            "revised draft text",
        ),
    ),
    (
        "ExegesisAppService.reject_patch",
        (
            "diff-preview",
            "--original",
            "draft text",
            "--proposed",
            "revised draft text",
        ),
    ),
    (
        "ExegesisAppService.save_document",
        (
            "terminal",
            "--operation-kind",
            "terminal_synthesis_request",
            "--message",
            "persist and continue",
        ),
    ),
)
_DEMO_EXACT_ACTION_SMOKE_ARGV_BY_ENGINE_ACTION: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("ExegesisAppService.open_project", ("bootstrap", "--project", "demo-project")),
    ("ExegesisAppService.open_document", ("bootstrap", "--project", "demo-document")),
    ("ExegesisAppService.search_project", ("context-basket", "list")),
    ("ExegesisAppService.add_basket_item", ("context-basket", "add", "demo-retrieval-result")),
    (
        "ExegesisAppService.revise_selection",
        (
            "diff-preview",
            "--original",
            "draft text before revision",
            "--proposed",
            "revised draft text",
        ),
    ),
    (
        "ExegesisAppService.apply_patch",
        (
            "diff-preview",
            "--original",
            "draft text before apply",
            "--proposed",
            "applied draft text",
        ),
    ),
    (
        "ExegesisAppService.reject_patch",
        (
            "diff-preview",
            "--original",
            "draft text before reject",
            "--proposed",
            "rejected draft text",
        ),
    ),
    (
        "ExegesisAppService.save_document",
        (
            "terminal",
            "--operation-kind",
            "terminal_synthesis_request",
            "--message",
            "persist and continue",
        ),
    ),
)
_SMOKE_VALUE_AGNOSTIC_OPTIONS_BY_COMMAND: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("bootstrap", ("--project",)),
    ("diff-preview", ("--original", "--proposed")),
    ("terminal", ("--operation-kind", "--message")),
)
_SMOKE_VALUE_AGNOSTIC_POSITIONALS_BY_COMMAND: tuple[tuple[str, tuple[int, ...]], ...] = (
    ("context-basket", (1,)),
)


def _demo_smoke_argv_by_flow_step() -> dict[str, tuple[str, ...]]:
    argv_by_flow_step: dict[str, tuple[str, ...]] = {}
    for flow_step, argv in _DEMO_SMOKE_ARGV_BY_FLOW_STEP:
        normalized_flow_step = _normalize_token(flow_step)
        if not normalized_flow_step:
            raise ValueError("Command demo smoke argv flow step must not be empty")
        if normalized_flow_step in argv_by_flow_step:
            raise ValueError(f"Duplicate command demo smoke argv flow step: {flow_step}")
        if not argv or any(not token.strip() for token in argv):
            raise ValueError(f"Command demo smoke argv must not be empty: {flow_step}")
        argv_by_flow_step[normalized_flow_step] = argv
    return argv_by_flow_step


def _demo_action_smoke_argv_by_engine_action() -> dict[str, tuple[str, ...]]:
    argv_by_action: dict[str, tuple[str, ...]] = {}
    for engine_action, argv in _DEMO_ACTION_SMOKE_ARGV_BY_ENGINE_ACTION:
        if not engine_action.strip():
            raise ValueError("Command demo action smoke argv action must not be empty")
        if engine_action in argv_by_action:
            raise ValueError(f"Duplicate command demo action smoke argv action: {engine_action}")
        if not argv or any(not token.strip() for token in argv):
            raise ValueError(f"Command demo action smoke argv must not be empty: {engine_action}")
        argv_by_action[engine_action] = argv
    return argv_by_action


def _demo_action_smoke_argv_for(route_entry: CommandDemoActionRouteEntry) -> tuple[str, ...]:
    action_argv = _demo_action_smoke_argv_by_engine_action().get(route_entry.engine_action)
    if action_argv is None:
        raise ValueError(f"Missing command demo action smoke argv: {route_entry.engine_action}")
    return action_argv


def _demo_exact_action_smoke_argv_by_engine_action(
    specs: tuple[CommandSpec, ...],
) -> dict[str, tuple[str, ...]]:
    expected_actions = set(command_demo_engine_actions(specs))
    expected_command_by_action = dict(command_demo_action_lookup_table(specs))
    cli_lookup = dict(command_cli_lookup_table()) if specs == COMMAND_SPECS else dict(command_lookup_index(specs))
    argv_by_action: dict[str, tuple[str, ...]] = {}
    seen_argv: set[tuple[str, ...]] = set()
    for engine_action, argv in _DEMO_EXACT_ACTION_SMOKE_ARGV_BY_ENGINE_ACTION:
        if engine_action not in expected_actions:
            raise ValueError(f"Unknown command demo exact action smoke argv: {engine_action}")
        if engine_action in argv_by_action:
            raise ValueError(f"Duplicate command demo exact action smoke argv action: {engine_action}")
        if not argv or any(not token.strip() for token in argv):
            raise ValueError(f"Command demo exact action smoke argv must not be empty: {engine_action}")
        if argv in seen_argv:
            raise ValueError(f"Duplicate command demo exact action smoke argv: {engine_action}")
        requested_command = _normalize_token(_strip_command_palette_prefix(argv[0]))
        expected_command = expected_command_by_action.get(engine_action)
        if cli_lookup.get(requested_command) != expected_command:
            raise ValueError(
                "Command demo exact action smoke argv must use the approved parser surface: "
                f"{engine_action}"
            )
        seen_argv.add(argv)
        argv_by_action[engine_action] = argv
    missing_actions = tuple(
        engine_action
        for engine_action in command_demo_engine_actions(specs)
        if engine_action not in argv_by_action
    )
    if missing_actions:
        raise ValueError(f"Missing command demo exact action smoke argv: {', '.join(missing_actions)}")
    return argv_by_action


def _validate_demo_action_smoke_argv_coverage(
    route_contract: CommandDemoActionRouteContract,
) -> None:
    expected_actions = tuple(entry.engine_action for entry in route_contract.entries)
    configured_actions = tuple(engine_action for engine_action, _ in _DEMO_ACTION_SMOKE_ARGV_BY_ENGINE_ACTION)
    missing_actions = tuple(engine_action for engine_action in expected_actions if engine_action not in configured_actions)
    if missing_actions:
        raise ValueError(f"Missing command demo action smoke argv: {', '.join(missing_actions)}")
    extra_actions = tuple(engine_action for engine_action in configured_actions if engine_action not in expected_actions)
    if extra_actions:
        raise ValueError(f"Unknown command demo action smoke argv: {', '.join(extra_actions)}")


def _validate_demo_smoke_argv_coverage(
    specs: tuple[CommandSpec, ...],
    flow_steps: tuple[str, ...],
) -> None:
    argv_by_flow_step = _demo_smoke_argv_by_flow_step()
    expected_flow_steps = set(_normalize_flow_steps(flow_steps))
    configured_flow_steps = set(argv_by_flow_step)
    missing_flow_steps = tuple(
        flow_step for flow_step in flow_steps if _normalize_token(flow_step) not in configured_flow_steps
    )
    if missing_flow_steps:
        raise ValueError(f"Missing command demo smoke argv flow steps: {', '.join(missing_flow_steps)}")
    extra_flow_steps = tuple(
        flow_step for flow_step, _ in _DEMO_SMOKE_ARGV_BY_FLOW_STEP if _normalize_token(flow_step) not in expected_flow_steps
    )
    if extra_flow_steps:
        raise ValueError(f"Unknown command demo smoke argv flow steps: {', '.join(extra_flow_steps)}")
    _validate_demo_smoke_argv_parser_surface(specs, flow_steps, argv_by_flow_step)


def _validate_demo_smoke_argv_parser_surface(
    specs: tuple[CommandSpec, ...],
    flow_steps: tuple[str, ...],
    argv_by_flow_step: dict[str, tuple[str, ...]],
) -> None:
    manifest_by_flow_step = {
        _normalize_token(entry.flow_step): entry
        for entry in command_flow_manifest(specs, flow_steps)
    }
    parser_lookup = (
        dict(command_cli_lookup_table())
        if specs == COMMAND_SPECS
        else dict(command_lookup_index(specs))
    )
    for flow_step in _normalize_flow_steps(flow_steps):
        argv = argv_by_flow_step[flow_step]
        command_token = _normalize_token(_strip_command_palette_prefix(argv[0]))
        expected_name = manifest_by_flow_step[flow_step].name
        if parser_lookup.get(command_token) != expected_name:
            raise ValueError(
                "Command demo smoke argv must use the approved parser surface: "
                f"{flow_step}"
            )


def _validate_smoke_matching_policy(specs: tuple[CommandSpec, ...]) -> None:
    command_names = {_normalize_token(spec.name) for spec in specs}
    option_commands = set(
        _validate_smoke_value_agnostic_options(command_names)
    )
    positional_commands = set(
        _validate_smoke_value_agnostic_positionals(command_names)
    )
    unknown_policy_commands = tuple(
        command_name
        for command_name in (*option_commands, *positional_commands)
        if command_name not in command_names
    )
    if unknown_policy_commands:
        raise ValueError(
            "Command smoke matching policy references unknown commands: "
            + ", ".join(unknown_policy_commands)
        )


def _validate_smoke_value_agnostic_options(
    command_names: set[str],
) -> tuple[str, ...]:
    seen_commands: set[str] = set()
    normalized_commands: list[str] = []
    for command_name, options in _SMOKE_VALUE_AGNOSTIC_OPTIONS_BY_COMMAND:
        normalized_command = _normalize_token(command_name)
        if not normalized_command:
            raise ValueError("Command smoke value-agnostic option command must not be empty")
        if normalized_command in seen_commands:
            raise ValueError(f"Duplicate command smoke value-agnostic option command: {command_name}")
        seen_commands.add(normalized_command)
        normalized_commands.append(normalized_command)
        if normalized_command not in command_names:
            continue
        if not options:
            raise ValueError(f"Command smoke value-agnostic options must not be empty: {command_name}")
        if len(set(options)) != len(options):
            raise ValueError(f"Duplicate command smoke value-agnostic option: {command_name}")
        if any(not option.startswith("--") or option == "--" for option in options):
            raise ValueError(f"Invalid command smoke value-agnostic option: {command_name}")
    return tuple(normalized_commands)


def _validate_smoke_value_agnostic_positionals(
    command_names: set[str],
) -> tuple[str, ...]:
    seen_commands: set[str] = set()
    normalized_commands: list[str] = []
    for command_name, positional_indexes in _SMOKE_VALUE_AGNOSTIC_POSITIONALS_BY_COMMAND:
        normalized_command = _normalize_token(command_name)
        if not normalized_command:
            raise ValueError("Command smoke value-agnostic positional command must not be empty")
        if normalized_command in seen_commands:
            raise ValueError(f"Duplicate command smoke value-agnostic positional command: {command_name}")
        seen_commands.add(normalized_command)
        normalized_commands.append(normalized_command)
        if normalized_command not in command_names:
            continue
        if not positional_indexes:
            raise ValueError(f"Command smoke value-agnostic positionals must not be empty: {command_name}")
        if len(set(positional_indexes)) != len(positional_indexes):
            raise ValueError(f"Duplicate command smoke value-agnostic positional: {command_name}")
        if any(index < 0 for index in positional_indexes):
            raise ValueError(f"Invalid command smoke value-agnostic positional: {command_name}")
    return tuple(normalized_commands)


def validate_command_catalog(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> None:
    seen_names: set[str] = set()
    seen_flow_steps: set[str] = set()
    seen_aliases: dict[str, str] = {}
    seen_lookup_tokens: dict[str, str] = {}
    for spec in specs:
        normalized_name = _normalize_token(spec.name)
        if not normalized_name:
            raise ValueError("Command names must not be empty")
        if normalized_name in seen_names:
            raise ValueError(f"Duplicate command name: {spec.name}")
        seen_names.add(normalized_name)

        normalized_flow_step = _normalize_token(spec.flow_step)
        if not normalized_flow_step:
            raise ValueError(f"Command {spec.name} must define a flow step")
        if normalized_flow_step in seen_flow_steps:
            raise ValueError(f"Duplicate command flow step: {spec.flow_step}")
        seen_flow_steps.add(normalized_flow_step)

        if normalized_name in seen_lookup_tokens and seen_lookup_tokens[normalized_name] != spec.name:
            raise ValueError(f"Duplicate command lookup token: {spec.name}")
        seen_lookup_tokens[normalized_name] = spec.name

        if normalized_flow_step in seen_lookup_tokens and seen_lookup_tokens[normalized_flow_step] != spec.name:
            raise ValueError(f"Duplicate command lookup token: {spec.flow_step}")
        seen_lookup_tokens[normalized_flow_step] = spec.name

        seen_local_aliases: set[str] = set()
        for alias in spec.aliases:
            normalized_alias = _normalize_token(alias)
            if not normalized_alias:
                raise ValueError(f"Command {spec.name} has an empty lookup alias")
            if normalized_alias in seen_local_aliases:
                raise ValueError(f"Duplicate command lookup alias: {alias}")
            seen_local_aliases.add(normalized_alias)
            existing_name = seen_aliases.get(normalized_alias)
            if existing_name is not None and existing_name != spec.name:
                raise ValueError(f"Duplicate command lookup alias: {alias}")
            seen_aliases[normalized_alias] = spec.name
            if normalized_alias in seen_lookup_tokens and seen_lookup_tokens[normalized_alias] != spec.name:
                raise ValueError(f"Duplicate command lookup token: {alias}")
            seen_lookup_tokens[normalized_alias] = spec.name

    if specs == COMMAND_SPECS:
        _validate_smoke_matching_policy(specs)


@lru_cache(maxsize=None)
def _command_spec_for(specs: tuple[CommandSpec, ...], name: str) -> CommandSpec | None:
    normalized = _normalize_token(name)
    if not normalized:
        return None
    if specs is COMMAND_SPECS:
        return _COMMAND_SPEC_BY_ALIAS.get(normalized) or _COMMAND_SPEC_BY_FLOW_STEP.get(normalized)
    alias_index = _build_command_spec_by_alias(specs)
    return alias_index.get(normalized) or _build_command_spec_by_flow_step(specs).get(normalized)


@lru_cache(maxsize=None)
def command_spec_for(specs: tuple[CommandSpec, ...], name: str) -> CommandSpec | None:
    validate_command_catalog(specs)
    return _command_spec_for(specs, name)


@lru_cache(maxsize=None)
def command_aliases_for(specs: tuple[CommandSpec, ...], name: str) -> tuple[str, ...]:
    spec = command_spec_for(specs, name)
    if spec is None:
        return ()
    return _lookup_aliases(spec)


@lru_cache(maxsize=None)
def command_lookup_tokens_for(specs: tuple[CommandSpec, ...], name: str) -> tuple[str, ...]:
    spec = command_spec_for(specs, name)
    if spec is None:
        return ()
    return _lookup_tokens(spec)


@lru_cache(maxsize=None)
def canonical_command_for(specs: tuple[CommandSpec, ...], name: str) -> str:
    normalized = _normalize_token(name)
    if not normalized:
        return name.strip()
    spec = command_spec_for(specs, normalized)
    if spec is None:
        return normalized
    return spec.name


@lru_cache(maxsize=None)
def _build_command_spec_by_alias(specs: tuple[CommandSpec, ...]) -> dict[str, CommandSpec]:
    validate_command_catalog(specs)
    index: dict[str, CommandSpec] = {}
    for spec in specs:
        for alias in _lookup_tokens(spec):
            index[_normalize_token(alias)] = spec
    return index


@lru_cache(maxsize=None)
def _build_command_spec_by_flow_step(specs: tuple[CommandSpec, ...]) -> dict[str, CommandSpec]:
    validate_command_catalog(specs)
    index: dict[str, CommandSpec] = {}
    for spec in specs:
        index[_normalize_token(spec.flow_step)] = spec
    return index


_COMMAND_SPEC_BY_ALIAS = _build_command_spec_by_alias(COMMAND_SPECS)
_COMMAND_SPEC_BY_FLOW_STEP = _build_command_spec_by_flow_step(COMMAND_SPECS)


@lru_cache(maxsize=None)
def command_flow_manifest(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandManifestEntry, ...]:
    validate_command_catalog(specs)
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    normalized_flow_steps = _normalize_flow_steps(ordered_flow_steps)
    _validate_flow_steps(ordered_flow_steps)
    manifest_by_flow_step = {_normalize_token(entry.flow_step): entry for entry in command_manifest(specs)}
    missing_steps = tuple(flow_step for flow_step in normalized_flow_steps if flow_step not in manifest_by_flow_step)
    if missing_steps:
        raise ValueError(f"Missing command flow steps: {', '.join(missing_steps)}")
    return tuple(
        CommandManifestEntry(
            name=entry.name,
            aliases=entry.aliases,
            description=entry.description,
            flow_step=flow_step,
            lookup_tokens=entry.lookup_tokens,
        )
        for flow_step in normalized_flow_steps
        for entry in (manifest_by_flow_step[flow_step],)
    )


@lru_cache(maxsize=None)
def command_flow_sequence(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandFlowSequence:
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    normalized_flow_steps = _normalize_flow_steps(ordered_flow_steps)
    manifest = command_flow_manifest(specs, ordered_flow_steps)
    return CommandFlowSequence(
        flow_steps=normalized_flow_steps,
        names=tuple(entry.name for entry in manifest),
        lookup_table=command_flow_lookup_table(specs, ordered_flow_steps),
        lookup_tokens=tuple(entry.lookup_tokens for entry in manifest),
    )


@lru_cache(maxsize=None)
def command_flow_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandFlowEntry, ...]:
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    normalized_flow_steps = _normalize_flow_steps(ordered_flow_steps)
    manifest = command_flow_manifest(specs, ordered_flow_steps)
    manifest_by_flow_step = {_normalize_token(entry.flow_step): entry for entry in manifest}
    return tuple(
        CommandFlowEntry(
            flow_step=flow_step,
            name=entry.name,
            aliases=entry.aliases,
            description=entry.description,
            lookup_tokens=entry.lookup_tokens,
        )
        for flow_step in normalized_flow_steps
        for entry in (manifest_by_flow_step[flow_step],)
    )


@lru_cache(maxsize=None)
def command_flow_surface_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandFlowSurfaceEntry, ...]:
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    normalized_flow_steps = _normalize_flow_steps(ordered_flow_steps)
    manifest = command_flow_manifest(specs, ordered_flow_steps)
    manifest_by_flow_step = {_normalize_token(entry.flow_step): entry for entry in manifest}
    return tuple(
        CommandFlowSurfaceEntry(
            flow_step=flow_step,
            name=entry.name,
            aliases=entry.aliases,
            description=entry.description,
            lookup_tokens=entry.lookup_tokens,
            surface_tokens=_flow_surface_tokens(*entry.lookup_tokens, flow_step),
        )
        for flow_step in normalized_flow_steps
        for entry in (manifest_by_flow_step[flow_step],)
    )


@lru_cache(maxsize=None)
def command_flow_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, str], ...]:
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    manifest = command_flow_manifest(specs, ordered_flow_steps)
    return tuple((entry.flow_step, entry.name) for entry in manifest)


@lru_cache(maxsize=None)
def command_names(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[str, ...]:
    validate_command_catalog(specs)
    return tuple(spec.name for spec in specs)


def command_specs(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[CommandSpec, ...]:
    return specs


@lru_cache(maxsize=None)
def command_manifest(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[CommandManifestEntry, ...]:
    validate_command_catalog(specs)
    return tuple(
        CommandManifestEntry(
            name=spec.name,
            aliases=spec.aliases,
            description=spec.description,
            flow_step=_normalize_token(spec.flow_step),
            lookup_tokens=_lookup_tokens(spec),
        )
        for spec in specs
    )


def command_lookup_table(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[tuple[str, str], ...]:
    return command_lookup_index(specs)


@lru_cache(maxsize=None)
def command_cli_tokens() -> tuple[str, ...]:
    _validate_cli_entrypoints()
    return tuple(_CLI_ENTRYPOINTS)


@lru_cache(maxsize=None)
def command_cli_lookup_table() -> tuple[tuple[str, str], ...]:
    _validate_cli_entrypoints()
    lookup_table: list[tuple[str, str]] = []
    for entrypoint in _CLI_ENTRYPOINTS:
        spec = command_spec_for(COMMAND_SPECS, entrypoint)
        if spec is None:
            raise ValueError(f"Unknown CLI command entrypoint: {entrypoint}")
        lookup_table.append((entrypoint, spec.name))
    return tuple(lookup_table)


def _approved_cli_tokens() -> tuple[str, ...]:
    return _CANONICAL_CLI_ENTRYPOINTS


def _approved_cli_lookup_table() -> tuple[tuple[str, str], ...]:
    lookup_table: list[tuple[str, str]] = []
    for entrypoint in _approved_cli_tokens():
        spec = command_spec_for(COMMAND_SPECS, entrypoint)
        if spec is None:
            raise ValueError(f"Unknown approved CLI command entrypoint: {entrypoint}")
        lookup_table.append((entrypoint, spec.name))
    return tuple(lookup_table)


def _approved_cli_canonical_names() -> tuple[str, ...]:
    return tuple(
        canonical_name
        for token, canonical_name in _approved_cli_lookup_table()
        if token == canonical_name
    )


@lru_cache(maxsize=None)
def command_cli_contract() -> CommandCliContract:
    tokens = command_cli_tokens()
    lookup_table = command_cli_lookup_table()
    canonical_names = command_names()
    if tokens != _approved_cli_tokens():
        raise ValueError("Command CLI parser surface is inconsistent")
    if lookup_table != _approved_cli_lookup_table():
        raise ValueError("Command CLI parser surface is inconsistent")
    if canonical_names != _approved_cli_canonical_names():
        raise ValueError("Command CLI canonical tokens are inconsistent")
    return CommandCliContract(
        tokens=tokens,
        canonical_names=canonical_names,
        lookup_table=lookup_table,
    )


@lru_cache(maxsize=None)
def command_cli_route_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandFlowRouteEntry, ...]:
    return command_flow_route_catalog(flow_steps=flow_steps, specs=specs)


def _validate_command_cli_route_contract(
    contract: CommandCliRouteContract,
    route_summary: tuple[tuple[str, str, tuple[str, ...]], ...],
    *,
    specs: tuple[CommandSpec, ...],
    flow_steps: tuple[str, ...],
) -> None:
    if contract.route_summary != route_summary:
        raise ValueError("Command CLI route summary is inconsistent")
    if contract.flow_steps != tuple(flow_step for flow_step, _, _ in route_summary):
        raise ValueError("Command CLI route steps are inconsistent")
    if contract.flow_names != tuple(name for _, name, _ in route_summary):
        raise ValueError("Command CLI route names are inconsistent")
    expected_route_catalog = command_cli_route_catalog(specs, flow_steps)
    if contract.route_catalog != expected_route_catalog:
        raise ValueError("Command CLI route catalog is inconsistent")
    cli_contract = command_cli_contract()
    if contract.tokens != cli_contract.tokens:
        raise ValueError("Command CLI route tokens are inconsistent")
    if contract.canonical_names != cli_contract.canonical_names:
        raise ValueError("Command CLI route canonical names are inconsistent")
    if contract.smoke_tokens != command_flow_smoke_tokens(specs, flow_steps):
        raise ValueError("Command CLI route smoke tokens are inconsistent")
    if contract.lookup_table != cli_contract.lookup_table:
        raise ValueError("Command CLI route lookup table is inconsistent")
    if contract.lookup_surface != command_flow_lookup_surface(specs, flow_steps):
        raise ValueError("Command CLI route lookup surface is inconsistent")
    if contract.flow_surface_tokens != command_flow_surface_tokens(specs, flow_steps):
        raise ValueError("Command CLI route surface tokens are inconsistent")


@lru_cache(maxsize=None)
def command_cli_route_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandCliRouteContract:
    cli_contract = command_cli_contract()
    route_summary = command_flow_route_summary(specs, flow_steps)
    ordered_flow_steps = tuple(flow_step for flow_step, _, _ in route_summary)
    route_catalog = command_cli_route_catalog(specs, ordered_flow_steps)
    contract = CommandCliRouteContract(
        tokens=cli_contract.tokens,
        canonical_names=cli_contract.canonical_names,
        smoke_tokens=command_flow_smoke_tokens(specs, ordered_flow_steps),
        lookup_table=cli_contract.lookup_table,
        flow_steps=ordered_flow_steps,
        flow_names=tuple(name for _, name, _ in route_summary),
        route_summary=route_summary,
        lookup_surface=command_flow_lookup_surface(specs, ordered_flow_steps),
        flow_surface_tokens=command_flow_surface_tokens(specs, ordered_flow_steps),
        route_catalog=route_catalog,
    )
    _validate_command_cli_route_contract(
        contract,
        route_summary,
        specs=specs,
        flow_steps=ordered_flow_steps,
    )
    return contract


@lru_cache(maxsize=None)
def command_cli_flow_contract() -> CommandCliFlowContract:
    lookup_table = command_cli_lookup_table()
    entries: list[CommandCliFlowEntry] = []
    for token, canonical_name in lookup_table:
        spec = command_spec_for(COMMAND_SPECS, canonical_name)
        if spec is None:
            raise ValueError(f"Unknown CLI command target: {canonical_name}")
        entries.append(
            CommandCliFlowEntry(
                token=token,
                canonical_name=spec.name,
                flow_step=_normalize_token(spec.flow_step),
            )
        )
    return CommandCliFlowContract(entries=tuple(entries))


@lru_cache(maxsize=None)
def command_cli_flow_lookup_table() -> tuple[tuple[str, str], ...]:
    return tuple((entry.token, entry.flow_step) for entry in command_cli_flow_contract().entries)


@lru_cache(maxsize=None)
def command_cli_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    return command_flow_route_summary(specs, flow_steps)


@lru_cache(maxsize=None)
def command_flow_smoke_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    return tuple(cli_tokens[0] for _, _, cli_tokens in command_flow_route_summary(specs, flow_steps))


@lru_cache(maxsize=None)
def command_flow_route_catalog(
    flow_steps: tuple[str, ...] | None = None,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandFlowRouteEntry, ...]:
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    # Keep the route view in smoke-flow order while preserving the parser tokens
    # that dispatch to each command.
    route_catalog = command_flow_surface_catalog(specs, ordered_flow_steps)
    cli_tokens_by_name = _route_cli_tokens_by_name(specs)
    return tuple(
        CommandFlowRouteEntry(
            flow_step=entry.flow_step,
            name=entry.name,
            cli_tokens=cli_tokens_by_name.get(entry.name, (entry.name,)),
            lookup_tokens=entry.lookup_tokens,
            surface_tokens=entry.surface_tokens,
            description=entry.description,
        )
        for entry in route_catalog
    )


@lru_cache(maxsize=None)
def command_flow_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    route_catalog = command_flow_route_catalog(flow_steps=flow_steps, specs=specs)
    return tuple((entry.flow_step, entry.name, entry.cli_tokens) for entry in route_catalog)


@lru_cache(maxsize=None)
def command_flow_route_contract(
    flow_steps: tuple[str, ...] | None = None,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandFlowRouteContract:
    return CommandFlowRouteContract(entries=command_flow_route_catalog(flow_steps, specs))


@lru_cache(maxsize=None)
def command_demo_path_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoPathContract:
    route_catalog = command_flow_route_catalog(flow_steps=command_demo_flow_steps(), specs=specs)
    path_steps = {
        _normalize_token(flow_step): (demo_path_step, engine_actions)
        for flow_step, demo_path_step, engine_actions in _DEMO_PATH_STEP_BY_FLOW_STEP
    }
    entries: list[CommandDemoPathEntry] = []
    for route in route_catalog:
        demo_path_step, engine_actions = _demo_path_metadata_for_route(route.flow_step, path_steps)
        entries.append(
            CommandDemoPathEntry(
                flow_step=route.flow_step,
                name=route.name,
                cli_tokens=route.cli_tokens,
                engine_actions=engine_actions,
                demo_path_step=demo_path_step,
            )
        )
    contract = CommandDemoPathContract(entries=tuple(entries))
    _validate_command_demo_path_contract(contract, route_catalog)
    return contract


def _demo_path_metadata_for_route(
    flow_step: str,
    path_steps: dict[str, tuple[str, tuple[str, ...]]],
) -> tuple[str, tuple[str, ...]]:
    try:
        demo_path_step, engine_actions = path_steps[flow_step]
    except KeyError as exc:
        raise ValueError(f"Missing command demo path metadata: {flow_step}") from exc
    if not demo_path_step.strip():
        raise ValueError(f"Command demo path step must not be empty: {flow_step}")
    if not engine_actions or any(not action.strip() for action in engine_actions):
        raise ValueError(f"Command demo path engine actions must not be empty: {flow_step}")
    return demo_path_step, engine_actions


def _validate_command_demo_path_contract(
    contract: CommandDemoPathContract,
    route_catalog: tuple[CommandFlowRouteEntry, ...],
) -> None:
    if tuple(entry.flow_step for entry in contract.entries) != tuple(route.flow_step for route in route_catalog):
        raise ValueError("Command demo path route steps are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(route.name for route in route_catalog):
        raise ValueError("Command demo path route names are inconsistent")
    if tuple(entry.cli_tokens for entry in contract.entries) != tuple(route.cli_tokens for route in route_catalog):
        raise ValueError("Command demo path route tokens are inconsistent")
    if tuple(entry.flow_step for entry in contract.entries) != command_demo_flow_steps():
        raise ValueError("Command demo path steps are inconsistent")


@lru_cache(maxsize=None)
def command_demo_path_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, tuple[str, ...], str, tuple[str, ...]], ...]:
    contract = command_demo_path_contract(specs)
    return tuple(
        (
            entry.flow_step,
            entry.name,
            entry.cli_tokens,
            entry.demo_path_step,
            entry.engine_actions,
        )
        for entry in contract.entries
    )


def command_mvp_demo_path_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoPathContract:
    return command_demo_path_contract(specs)


def command_mvp_demo_path_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, tuple[str, ...], str, tuple[str, ...]], ...]:
    return command_demo_path_summary(specs)


@lru_cache(maxsize=None)
def command_demo_smoke_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoSmokeContract:
    demo_path_contract = command_demo_path_contract(specs)
    entries = tuple(
        CommandDemoSmokeEntry(
            smoke_token=path_entry.cli_tokens[0],
            name=path_entry.name,
            flow_step=path_entry.flow_step,
            demo_path_step=path_entry.demo_path_step,
            engine_actions=path_entry.engine_actions,
        )
        for path_entry in demo_path_contract.entries
    )
    contract = CommandDemoSmokeContract(entries=entries)
    _validate_command_demo_smoke_contract(contract, demo_path_contract, specs=specs)
    return contract


def _validate_command_demo_smoke_contract(
    contract: CommandDemoSmokeContract,
    demo_path_contract: CommandDemoPathContract,
    *,
    specs: tuple[CommandSpec, ...],
) -> None:
    if tuple(entry.smoke_token for entry in contract.entries) != command_demo_flow_smoke_tokens(specs):
        raise ValueError("Command demo smoke tokens are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(
        entry.name for entry in demo_path_contract.entries
    ):
        raise ValueError("Command demo smoke names are inconsistent")
    if tuple(entry.flow_step for entry in contract.entries) != command_demo_flow_steps():
        raise ValueError("Command demo smoke flow steps are inconsistent")
    if tuple(entry.demo_path_step for entry in contract.entries) != tuple(
        entry.demo_path_step for entry in demo_path_contract.entries
    ):
        raise ValueError("Command demo smoke path steps are inconsistent")
    if tuple(entry.engine_actions for entry in contract.entries) != tuple(
        entry.engine_actions for entry in demo_path_contract.entries
    ):
        raise ValueError("Command demo smoke engine actions are inconsistent")


def command_demo_smoke_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, str, str, tuple[str, ...]], ...]:
    contract = command_demo_smoke_contract(specs)
    return tuple(
        (
            entry.smoke_token,
            entry.name,
            entry.flow_step,
            entry.demo_path_step,
            entry.engine_actions,
        )
        for entry in contract.entries
    )


def command_mvp_demo_smoke_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoSmokeContract:
    return command_demo_smoke_contract(specs)


def command_mvp_demo_smoke_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, str, str, tuple[str, ...]], ...]:
    return command_demo_smoke_summary(specs)


@lru_cache(maxsize=None)
def command_demo_smoke_command_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoSmokeCommandContract:
    smoke_contract = command_demo_smoke_contract(specs)
    _validate_demo_smoke_argv_coverage(
        specs,
        tuple(entry.flow_step for entry in smoke_contract.entries),
    )
    argv_by_flow_step = _demo_smoke_argv_by_flow_step()
    entries = tuple(
        CommandDemoSmokeCommandEntry(
            flow_step=smoke_entry.flow_step,
            name=smoke_entry.name,
            argv=argv_by_flow_step[smoke_entry.flow_step],
            demo_path_step=smoke_entry.demo_path_step,
            engine_actions=smoke_entry.engine_actions,
        )
        for smoke_entry in smoke_contract.entries
    )
    contract = CommandDemoSmokeCommandContract(entries=entries)
    _validate_command_demo_smoke_command_contract(contract, smoke_contract, specs=specs)
    return contract


def _validate_command_demo_smoke_command_contract(
    contract: CommandDemoSmokeCommandContract,
    smoke_contract: CommandDemoSmokeContract,
    *,
    specs: tuple[CommandSpec, ...],
) -> None:
    if tuple(entry.flow_step for entry in contract.entries) != tuple(
        smoke_entry.flow_step for smoke_entry in smoke_contract.entries
    ):
        raise ValueError("Command demo smoke argv flow steps are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(
        smoke_entry.name for smoke_entry in smoke_contract.entries
    ):
        raise ValueError("Command demo smoke argv names are inconsistent")
    if tuple(entry.demo_path_step for entry in contract.entries) != tuple(
        smoke_entry.demo_path_step for smoke_entry in smoke_contract.entries
    ):
        raise ValueError("Command demo smoke argv path steps are inconsistent")
    if tuple(entry.engine_actions for entry in contract.entries) != tuple(
        smoke_entry.engine_actions for smoke_entry in smoke_contract.entries
    ):
        raise ValueError("Command demo smoke argv engine actions are inconsistent")

    cli_lookup = dict(command_cli_lookup_table()) if specs == COMMAND_SPECS else dict(command_lookup_index(specs))
    seen_flow_steps = set()
    for entry in contract.entries:
        if entry.flow_step in seen_flow_steps:
            raise ValueError(f"Duplicate command demo smoke argv flow step: {entry.flow_step}")
        seen_flow_steps.add(entry.flow_step)
        if not entry.argv or any(not token.strip() for token in entry.argv):
            raise ValueError(f"Command demo smoke argv must not be empty: {entry.flow_step}")
        canonical_name = cli_lookup.get(_normalize_token(entry.argv[0]))
        if canonical_name != entry.name:
            raise ValueError(f"Command demo smoke argv does not route to {entry.name}: {entry.flow_step}")


def command_demo_smoke_command_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, tuple[str, ...], str, tuple[str, ...]], ...]:
    contract = command_demo_smoke_command_contract(specs)
    return tuple(
        (
            entry.flow_step,
            entry.name,
            entry.argv,
            entry.demo_path_step,
            entry.engine_actions,
        )
        for entry in contract.entries
    )


def command_mvp_demo_smoke_command_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoSmokeCommandContract:
    return command_demo_smoke_command_contract(specs)


def command_mvp_demo_smoke_command_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, tuple[str, ...], str, tuple[str, ...]], ...]:
    return command_demo_smoke_command_summary(specs)


@lru_cache(maxsize=None)
def command_demo_smoke_argv_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoSmokeArgvContract:
    command_contract = command_demo_smoke_command_contract(specs)
    contract = CommandDemoSmokeArgvContract(
        entries=tuple(
            CommandDemoSmokeArgvEntry(
                flow_step=entry.flow_step,
                argv=entry.argv,
            )
            for entry in command_contract.entries
        )
    )
    _validate_command_demo_smoke_argv_contract(contract, command_contract)
    return contract


def _validate_command_demo_smoke_argv_contract(
    contract: CommandDemoSmokeArgvContract,
    command_contract: CommandDemoSmokeCommandContract,
) -> None:
    if tuple(entry.flow_step for entry in contract.entries) != tuple(
        command_entry.flow_step for command_entry in command_contract.entries
    ):
        raise ValueError("Command demo smoke argv contract flow steps are inconsistent")
    if tuple(entry.argv for entry in contract.entries) != tuple(
        command_entry.argv for command_entry in command_contract.entries
    ):
        raise ValueError("Command demo smoke argv contract commands are inconsistent")


def command_demo_smoke_argv_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return tuple((entry.flow_step, entry.argv) for entry in command_demo_smoke_argv_contract(specs).entries)


@lru_cache(maxsize=None)
def _command_demo_smoke_argv_for_flow_step(
    specs: tuple[CommandSpec, ...],
    flow_step: str,
) -> tuple[str, ...]:
    requested_flow_step = _normalize_token(flow_step)
    if not requested_flow_step:
        return ()
    return dict(command_demo_smoke_argv_lookup_table(specs)).get(requested_flow_step, ())


def command_demo_smoke_argv_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return _command_demo_smoke_argv_for_flow_step(specs, flow_step)


def command_mvp_demo_smoke_argv_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoSmokeArgvContract:
    return command_demo_smoke_argv_contract(specs)


def command_mvp_demo_smoke_argv_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_smoke_argv_lookup_table(specs)


def command_mvp_demo_smoke_argv_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return command_demo_smoke_argv_for_flow_step(flow_step, specs)


@lru_cache(maxsize=None)
def command_demo_smoke_matrix_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoSmokeMatrixContract:
    path_contract = command_demo_path_contract(specs)
    command_contract = command_demo_smoke_command_contract(specs)
    routes_by_flow_step = {entry.flow_step: entry for entry in path_contract.entries}
    entries = tuple(
        CommandDemoSmokeMatrixEntry(
            flow_step=command_entry.flow_step,
            name=command_entry.name,
            argv=command_entry.argv,
            cli_tokens=routes_by_flow_step[command_entry.flow_step].cli_tokens,
            demo_path_step=command_entry.demo_path_step,
            engine_actions=command_entry.engine_actions,
        )
        for command_entry in command_contract.entries
    )
    contract = CommandDemoSmokeMatrixContract(entries=entries)
    _validate_command_demo_smoke_matrix_contract(
        contract,
        path_contract,
        command_contract,
        specs=specs,
    )
    return contract


def _validate_command_demo_smoke_matrix_contract(
    contract: CommandDemoSmokeMatrixContract,
    path_contract: CommandDemoPathContract,
    command_contract: CommandDemoSmokeCommandContract,
    *,
    specs: tuple[CommandSpec, ...],
) -> None:
    if tuple(entry.flow_step for entry in contract.entries) != tuple(
        entry.flow_step for entry in command_contract.entries
    ):
        raise ValueError("Command demo smoke matrix flow steps are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(entry.name for entry in command_contract.entries):
        raise ValueError("Command demo smoke matrix names are inconsistent")
    if tuple(entry.argv for entry in contract.entries) != tuple(entry.argv for entry in command_contract.entries):
        raise ValueError("Command demo smoke matrix argv values are inconsistent")
    if tuple(entry.demo_path_step for entry in contract.entries) != tuple(
        entry.demo_path_step for entry in command_contract.entries
    ):
        raise ValueError("Command demo smoke matrix path steps are inconsistent")
    if tuple(entry.engine_actions for entry in contract.entries) != tuple(
        entry.engine_actions for entry in command_contract.entries
    ):
        raise ValueError("Command demo smoke matrix engine actions are inconsistent")

    routes_by_flow_step = {entry.flow_step: entry for entry in path_contract.entries}
    cli_lookup = dict(command_cli_flow_lookup_table()) if specs == COMMAND_SPECS else dict(
        command_flow_lookup_table(specs)
    )
    for entry in contract.entries:
        route = routes_by_flow_step.get(entry.flow_step)
        if route is None:
            raise ValueError(f"Command demo smoke matrix missing route: {entry.flow_step}")
        if entry.cli_tokens != route.cli_tokens:
            raise ValueError("Command demo smoke matrix CLI tokens are inconsistent")
        normalized_argv_command = _normalize_token(entry.argv[0])
        if normalized_argv_command not in entry.cli_tokens:
            raise ValueError(f"Command demo smoke matrix argv is outside route tokens: {entry.flow_step}")
        routed_flow_step = cli_lookup.get(normalized_argv_command)
        if routed_flow_step is not None and routed_flow_step != entry.flow_step:
            raise ValueError(f"Command demo smoke matrix argv routes to the wrong flow step: {entry.flow_step}")


def command_demo_smoke_matrix_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, tuple[str, ...], tuple[str, ...], str, tuple[str, ...]], ...]:
    contract = command_demo_smoke_matrix_contract(specs)
    return tuple(
        (
            entry.flow_step,
            entry.name,
            entry.argv,
            entry.cli_tokens,
            entry.demo_path_step,
            entry.engine_actions,
        )
        for entry in contract.entries
    )


@lru_cache(maxsize=None)
def command_demo_smoke_script_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoSmokeScriptContract:
    matrix_contract = command_demo_smoke_matrix_contract(specs)
    contract = CommandDemoSmokeScriptContract(
        steps=tuple(
            CommandDemoSmokeScriptStep(
                ordinal=ordinal,
                flow_step=entry.flow_step,
                name=entry.name,
                argv=entry.argv,
                demo_path_step=entry.demo_path_step,
                engine_actions=entry.engine_actions,
            )
            for ordinal, entry in enumerate(matrix_contract.entries, start=1)
        )
    )
    _validate_command_demo_smoke_script_contract(contract, matrix_contract)
    return contract


def _validate_command_demo_smoke_script_contract(
    contract: CommandDemoSmokeScriptContract,
    matrix_contract: CommandDemoSmokeMatrixContract,
) -> None:
    expected_ordinals = tuple(range(1, len(matrix_contract.entries) + 1))
    if tuple(step.ordinal for step in contract.steps) != expected_ordinals:
        raise ValueError("Command demo smoke script ordinals are inconsistent")
    if tuple(step.flow_step for step in contract.steps) != tuple(
        entry.flow_step for entry in matrix_contract.entries
    ):
        raise ValueError("Command demo smoke script flow steps are inconsistent")
    if tuple(step.name for step in contract.steps) != tuple(entry.name for entry in matrix_contract.entries):
        raise ValueError("Command demo smoke script names are inconsistent")
    if tuple(step.argv for step in contract.steps) != tuple(entry.argv for entry in matrix_contract.entries):
        raise ValueError("Command demo smoke script argv values are inconsistent")
    if tuple(step.demo_path_step for step in contract.steps) != tuple(
        entry.demo_path_step for entry in matrix_contract.entries
    ):
        raise ValueError("Command demo smoke script path steps are inconsistent")
    if tuple(step.engine_actions for step in contract.steps) != tuple(
        entry.engine_actions for entry in matrix_contract.entries
    ):
        raise ValueError("Command demo smoke script engine actions are inconsistent")


def command_demo_smoke_script_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[int, str, str, tuple[str, ...], str, tuple[str, ...]], ...]:
    contract = command_demo_smoke_script_contract(specs)
    return tuple(
        (
            step.ordinal,
            step.flow_step,
            step.name,
            step.argv,
            step.demo_path_step,
            step.engine_actions,
        )
        for step in contract.steps
    )


def command_demo_smoke_script_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[int, tuple[str, ...]], ...]:
    return tuple((step.ordinal, step.argv) for step in command_demo_smoke_script_contract(specs).steps)


def _validate_command_smoke_cli_launcher_tokens(launcher_argv: tuple[str, ...]) -> None:
    if not launcher_argv or any(not token.strip() for token in launcher_argv):
        raise ValueError("Command smoke CLI launcher argv must not be empty")


def _validate_command_smoke_launcher_roundtrip(launcher_argv: tuple[str, ...]) -> None:
    probe_argv = (*launcher_argv, "bootstrap")
    if _detected_launcher_argv(probe_argv) != launcher_argv:
        raise ValueError("Command smoke CLI launcher argv is unsupported")
    if _argv_without_launcher(probe_argv, launcher_argv) != ("bootstrap",):
        raise ValueError("Command smoke CLI launcher argv does not resolve to CLI commands")


def _validate_command_smoke_cli_launcher(launcher_argv: tuple[str, ...]) -> None:
    _validate_command_smoke_cli_launcher_tokens(launcher_argv)
    _validate_command_smoke_launcher_roundtrip(launcher_argv)


def _validate_command_smoke_supported_launchers() -> None:
    seen_launchers: set[tuple[str, ...]] = set()
    for launcher_argv in COMMAND_SMOKE_SUPPORTED_LAUNCHER_ARGV:
        _validate_command_smoke_cli_launcher(launcher_argv)
        if launcher_argv in seen_launchers:
            raise ValueError("Duplicate command smoke supported launcher argv")
        seen_launchers.add(launcher_argv)


def command_demo_supported_launcher_argv() -> tuple[tuple[str, ...], ...]:
    _validate_command_smoke_supported_launchers()
    return COMMAND_SMOKE_SUPPORTED_LAUNCHER_ARGV


def command_mvp_demo_supported_launcher_argv() -> tuple[tuple[str, ...], ...]:
    return command_demo_supported_launcher_argv()


@lru_cache(maxsize=None)
def command_demo_smoke_cli_script_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoSmokeCliScriptContract:
    _validate_command_smoke_cli_launcher(launcher_argv)
    script_contract = command_demo_smoke_script_contract(specs)
    contract = CommandDemoSmokeCliScriptContract(
        steps=tuple(
            CommandDemoSmokeCliScriptStep(
                ordinal=step.ordinal,
                flow_step=step.flow_step,
                name=step.name,
                command_argv=(*launcher_argv, *step.argv),
                demo_path_step=step.demo_path_step,
                engine_actions=step.engine_actions,
            )
            for step in script_contract.steps
        )
    )
    _validate_command_demo_smoke_cli_script_contract(contract, script_contract, launcher_argv)
    return contract


def _validate_command_demo_smoke_cli_script_contract(
    contract: CommandDemoSmokeCliScriptContract,
    script_contract: CommandDemoSmokeScriptContract,
    launcher_argv: tuple[str, ...],
) -> None:
    if tuple(step.ordinal for step in contract.steps) != tuple(step.ordinal for step in script_contract.steps):
        raise ValueError("Command demo smoke CLI script ordinals are inconsistent")
    if tuple(step.flow_step for step in contract.steps) != tuple(step.flow_step for step in script_contract.steps):
        raise ValueError("Command demo smoke CLI script flow steps are inconsistent")
    if tuple(step.name for step in contract.steps) != tuple(step.name for step in script_contract.steps):
        raise ValueError("Command demo smoke CLI script names are inconsistent")
    if tuple(step.demo_path_step for step in contract.steps) != tuple(
        step.demo_path_step for step in script_contract.steps
    ):
        raise ValueError("Command demo smoke CLI script path steps are inconsistent")
    if tuple(step.engine_actions for step in contract.steps) != tuple(
        step.engine_actions for step in script_contract.steps
    ):
        raise ValueError("Command demo smoke CLI script engine actions are inconsistent")
    if tuple(step.command_argv[: len(launcher_argv)] for step in contract.steps) != tuple(
        launcher_argv for _ in script_contract.steps
    ):
        raise ValueError("Command demo smoke CLI script launcher argv is inconsistent")
    if tuple(step.command_argv[len(launcher_argv) :] for step in contract.steps) != tuple(
        step.argv for step in script_contract.steps
    ):
        raise ValueError("Command demo smoke CLI script command argv is inconsistent")


def command_demo_smoke_cli_script_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, tuple[str, ...], str, tuple[str, ...]], ...]:
    contract = command_demo_smoke_cli_script_contract(specs, launcher_argv)
    return tuple(
        (
            step.ordinal,
            step.flow_step,
            step.name,
            step.command_argv,
            step.demo_path_step,
            step.engine_actions,
        )
        for step in contract.steps
    )


def command_demo_smoke_cli_script_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, tuple[str, ...]], ...]:
    return tuple(
        (step.ordinal, step.command_argv)
        for step in command_demo_smoke_cli_script_contract(specs, launcher_argv).steps
    )


def _shell_join(argv: tuple[str, ...]) -> str:
    return shlex.join(argv)


def command_demo_smoke_cli_script_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str], ...]:
    return tuple(
        (step.ordinal, step.flow_step, step.demo_path_step, _shell_join(step.command_argv))
        for step in command_demo_smoke_cli_script_contract(specs, launcher_argv).steps
    )


@lru_cache(maxsize=None)
def _command_demo_smoke_script_step_for_ordinal(
    specs: tuple[CommandSpec, ...],
    ordinal: int,
) -> CommandDemoSmokeScriptStep | None:
    if ordinal <= 0:
        return None
    return {step.ordinal: step for step in command_demo_smoke_script_contract(specs).steps}.get(ordinal)


def command_demo_smoke_script_step(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoSmokeScriptStep | None:
    return _command_demo_smoke_script_step_for_ordinal(specs, ordinal)


def command_demo_smoke_script_argv(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    step = command_demo_smoke_script_step(ordinal, specs)
    if step is None:
        return ()
    return step.argv


@lru_cache(maxsize=None)
def _command_demo_smoke_cli_script_step_for_ordinal(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    ordinal: int,
) -> CommandDemoSmokeCliScriptStep | None:
    if ordinal <= 0:
        return None
    return {
        step.ordinal: step
        for step in command_demo_smoke_cli_script_contract(specs, launcher_argv).steps
    }.get(ordinal)


def command_demo_smoke_cli_script_step(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoSmokeCliScriptStep | None:
    return _command_demo_smoke_cli_script_step_for_ordinal(specs, launcher_argv, ordinal)


def command_demo_smoke_cli_script_argv(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    step = command_demo_smoke_cli_script_step(ordinal, specs, launcher_argv)
    if step is None:
        return ()
    return step.command_argv


def command_mvp_demo_smoke_matrix_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoSmokeMatrixContract:
    return command_demo_smoke_matrix_contract(specs)


def command_mvp_demo_smoke_matrix_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, tuple[str, ...], tuple[str, ...], str, tuple[str, ...]], ...]:
    return command_demo_smoke_matrix_summary(specs)


def command_mvp_demo_smoke_script_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoSmokeScriptContract:
    return command_demo_smoke_script_contract(specs)


def command_mvp_demo_smoke_script_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[int, str, str, tuple[str, ...], str, tuple[str, ...]], ...]:
    return command_demo_smoke_script_summary(specs)


def command_mvp_demo_smoke_script_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[int, tuple[str, ...]], ...]:
    return command_demo_smoke_script_lookup_table(specs)


def command_mvp_demo_smoke_cli_script_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoSmokeCliScriptContract:
    return command_demo_smoke_cli_script_contract(specs, launcher_argv)


def command_mvp_demo_smoke_cli_script_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, tuple[str, ...], str, tuple[str, ...]], ...]:
    return command_demo_smoke_cli_script_summary(specs, launcher_argv)


def command_mvp_demo_smoke_cli_script_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, tuple[str, ...]], ...]:
    return command_demo_smoke_cli_script_lookup_table(specs, launcher_argv)


def command_mvp_demo_smoke_cli_script_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str], ...]:
    return command_demo_smoke_cli_script_lines(specs, launcher_argv)


def command_mvp_demo_smoke_script_step(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoSmokeScriptStep | None:
    return command_demo_smoke_script_step(ordinal, specs)


def command_mvp_demo_smoke_script_argv(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return command_demo_smoke_script_argv(ordinal, specs)


def command_mvp_demo_smoke_cli_script_step(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoSmokeCliScriptStep | None:
    return command_demo_smoke_cli_script_step(ordinal, specs, launcher_argv)


def command_mvp_demo_smoke_cli_script_argv(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_smoke_cli_script_argv(ordinal, specs, launcher_argv)


@lru_cache(maxsize=None)
def command_demo_action_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoActionContract:
    smoke_contract = command_demo_smoke_contract(specs)
    entries = tuple(
        CommandDemoActionEntry(
            engine_action=engine_action,
            flow_step=smoke_entry.flow_step,
            name=smoke_entry.name,
            smoke_token=smoke_entry.smoke_token,
            demo_path_step=smoke_entry.demo_path_step,
        )
        for smoke_entry in smoke_contract.entries
        for engine_action in smoke_entry.engine_actions
    )
    contract = CommandDemoActionContract(entries=entries)
    _validate_command_demo_action_contract(contract, smoke_contract)
    return contract


def _validate_command_demo_action_contract(
    contract: CommandDemoActionContract,
    smoke_contract: CommandDemoSmokeContract,
) -> None:
    expected_actions = tuple(
        engine_action
        for smoke_entry in smoke_contract.entries
        for engine_action in smoke_entry.engine_actions
    )
    if tuple(entry.engine_action for entry in contract.entries) != expected_actions:
        raise ValueError("Command demo action engine actions are inconsistent")
    if len(set(expected_actions)) != len(expected_actions):
        raise ValueError("Command demo action engine actions must be unique")
    smoke_by_action = {
        engine_action: smoke_entry
        for smoke_entry in smoke_contract.entries
        for engine_action in smoke_entry.engine_actions
    }
    if any(entry.flow_step != smoke_by_action[entry.engine_action].flow_step for entry in contract.entries):
        raise ValueError("Command demo action flow steps are inconsistent")
    if any(entry.name != smoke_by_action[entry.engine_action].name for entry in contract.entries):
        raise ValueError("Command demo action command names are inconsistent")
    if any(entry.smoke_token != smoke_by_action[entry.engine_action].smoke_token for entry in contract.entries):
        raise ValueError("Command demo action smoke tokens are inconsistent")
    if any(entry.demo_path_step != smoke_by_action[entry.engine_action].demo_path_step for entry in contract.entries):
        raise ValueError("Command demo action path steps are inconsistent")


def command_demo_action_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, str, str, str], ...]:
    contract = command_demo_action_contract(specs)
    return tuple(
        (
            entry.engine_action,
            entry.flow_step,
            entry.name,
            entry.smoke_token,
            entry.demo_path_step,
        )
        for entry in contract.entries
    )


def command_demo_action_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return tuple((entry.engine_action, entry.name) for entry in command_demo_action_contract(specs).entries)


def command_demo_engine_actions(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return tuple(entry.engine_action for entry in command_demo_action_contract(specs).entries)


def command_demo_action_flow_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return tuple((entry.engine_action, entry.flow_step) for entry in command_demo_action_contract(specs).entries)


def command_demo_action_demo_path_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (entry.engine_action, entry.demo_path_step)
        for entry in command_demo_action_contract(specs).entries
    )


def command_demo_action_flow_step(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> str | None:
    entry = command_demo_action_entry(engine_action, specs)
    if entry is None:
        return None
    return entry.flow_step


def command_demo_action_demo_path_step(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> str | None:
    entry = command_demo_action_entry(engine_action, specs)
    if entry is None:
        return None
    return entry.demo_path_step


def command_demo_action_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, str, str], ...]:
    return tuple(
        (
            entry.engine_action,
            entry.flow_step,
            entry.name,
            entry.smoke_token,
        )
        for entry in command_demo_action_contract(specs).entries
    )


@lru_cache(maxsize=None)
def command_demo_action_route_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoActionRouteContract:
    demo_path_contract = command_demo_path_contract(specs)
    entries = tuple(
        CommandDemoActionRouteEntry(
            engine_action=engine_action,
            flow_step=path_entry.flow_step,
            name=path_entry.name,
            cli_tokens=path_entry.cli_tokens,
            smoke_token=path_entry.cli_tokens[0],
            demo_path_step=path_entry.demo_path_step,
        )
        for path_entry in demo_path_contract.entries
        for engine_action in path_entry.engine_actions
    )
    contract = CommandDemoActionRouteContract(entries=entries)
    _validate_command_demo_action_route_contract(contract, demo_path_contract, specs=specs)
    return contract


def _validate_command_demo_action_route_contract(
    contract: CommandDemoActionRouteContract,
    demo_path_contract: CommandDemoPathContract,
    *,
    specs: tuple[CommandSpec, ...],
) -> None:
    action_contract = command_demo_action_contract(specs)
    if tuple(entry.engine_action for entry in contract.entries) != tuple(
        entry.engine_action for entry in action_contract.entries
    ):
        raise ValueError("Command demo action route actions are inconsistent")
    if tuple(entry.flow_step for entry in contract.entries) != tuple(
        entry.flow_step for entry in action_contract.entries
    ):
        raise ValueError("Command demo action route flow steps are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(
        entry.name for entry in action_contract.entries
    ):
        raise ValueError("Command demo action route command names are inconsistent")
    if tuple(entry.smoke_token for entry in contract.entries) != tuple(
        entry.smoke_token for entry in action_contract.entries
    ):
        raise ValueError("Command demo action route smoke tokens are inconsistent")
    if tuple(entry.demo_path_step for entry in contract.entries) != tuple(
        entry.demo_path_step for entry in action_contract.entries
    ):
        raise ValueError("Command demo action route path steps are inconsistent")
    cli_tokens_by_action = {
        engine_action: path_entry.cli_tokens
        for path_entry in demo_path_contract.entries
        for engine_action in path_entry.engine_actions
    }
    if any(entry.cli_tokens != cli_tokens_by_action[entry.engine_action] for entry in contract.entries):
        raise ValueError("Command demo action route CLI tokens are inconsistent")


def command_demo_action_cli_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return tuple(
        (entry.engine_action, entry.cli_tokens)
        for entry in command_demo_action_route_contract(specs).entries
    )


def command_demo_action_cli_smoke_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (entry.engine_action, entry.smoke_token)
        for entry in command_demo_action_route_contract(specs).entries
    )


@lru_cache(maxsize=None)
def command_demo_action_smoke_argv_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoActionSmokeArgvContract:
    route_contract = command_demo_action_route_contract(specs)
    _validate_demo_action_smoke_argv_coverage(route_contract)
    entries = tuple(
        CommandDemoActionSmokeArgvEntry(
            engine_action=route_entry.engine_action,
            flow_step=route_entry.flow_step,
            name=route_entry.name,
            argv=_demo_action_smoke_argv_for(route_entry),
            smoke_token=route_entry.smoke_token,
            demo_path_step=route_entry.demo_path_step,
        )
        for route_entry in route_contract.entries
    )
    contract = CommandDemoActionSmokeArgvContract(entries=entries)
    _validate_command_demo_action_smoke_argv_contract(contract, route_contract, specs=specs)
    return contract


def _validate_command_demo_action_smoke_argv_contract(
    contract: CommandDemoActionSmokeArgvContract,
    route_contract: CommandDemoActionRouteContract,
    *,
    specs: tuple[CommandSpec, ...],
) -> None:
    if tuple(entry.engine_action for entry in contract.entries) != tuple(
        route_entry.engine_action for route_entry in route_contract.entries
    ):
        raise ValueError("Command demo action smoke argv actions are inconsistent")
    if tuple(entry.flow_step for entry in contract.entries) != tuple(
        route_entry.flow_step for route_entry in route_contract.entries
    ):
        raise ValueError("Command demo action smoke argv flow steps are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(
        route_entry.name for route_entry in route_contract.entries
    ):
        raise ValueError("Command demo action smoke argv command names are inconsistent")
    if tuple(entry.smoke_token for entry in contract.entries) != tuple(
        route_entry.smoke_token for route_entry in route_contract.entries
    ):
        raise ValueError("Command demo action smoke argv tokens are inconsistent")
    if tuple(entry.demo_path_step for entry in contract.entries) != tuple(
        route_entry.demo_path_step for route_entry in route_contract.entries
    ):
        raise ValueError("Command demo action smoke argv path steps are inconsistent")

    route_tokens_by_action = {
        route_entry.engine_action: route_entry.cli_tokens
        for route_entry in route_contract.entries
    }
    cli_lookup = dict(command_cli_lookup_table()) if specs == COMMAND_SPECS else dict(command_lookup_index(specs))
    for entry in contract.entries:
        if not entry.argv:
            raise ValueError(f"Command demo action smoke argv must not be empty: {entry.engine_action}")
        argv_command = _normalize_token(entry.argv[0])
        if argv_command != entry.smoke_token:
            raise ValueError(f"Command demo action smoke argv token mismatch: {entry.engine_action}")
        if argv_command not in route_tokens_by_action[entry.engine_action]:
            raise ValueError(f"Command demo action smoke argv is outside route tokens: {entry.engine_action}")
        if cli_lookup.get(argv_command) != entry.name:
            raise ValueError(f"Command demo action smoke argv routes to the wrong command: {entry.engine_action}")


def command_demo_action_smoke_argv_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return tuple(
        (entry.engine_action, entry.argv)
        for entry in command_demo_action_smoke_argv_contract(specs).entries
    )


@lru_cache(maxsize=None)
def command_demo_action_smoke_argv_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, CommandDemoActionSmokeArgvEntry], ...]:
    return tuple(
        (entry.engine_action, entry)
        for entry in command_demo_action_smoke_argv_contract(specs).entries
    )


@lru_cache(maxsize=None)
def _command_demo_action_smoke_argv_entry_for(
    specs: tuple[CommandSpec, ...],
    engine_action: str,
) -> CommandDemoActionSmokeArgvEntry | None:
    requested_action = engine_action.strip()
    if not requested_action:
        return None
    return dict(command_demo_action_smoke_argv_index(specs)).get(requested_action)


def command_demo_action_smoke_argv_entry(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoActionSmokeArgvEntry | None:
    return _command_demo_action_smoke_argv_entry_for(specs, engine_action)


def command_demo_action_smoke_argv(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    entry = command_demo_action_smoke_argv_entry(engine_action, specs)
    if entry is None:
        return ()
    return entry.argv


@lru_cache(maxsize=None)
def command_demo_action_smoke_cli_argv_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoActionSmokeCliArgvContract:
    _validate_command_smoke_cli_launcher(launcher_argv)
    argv_contract = command_demo_action_smoke_argv_contract(specs)
    contract = CommandDemoActionSmokeCliArgvContract(
        entries=tuple(
            CommandDemoActionSmokeCliArgvEntry(
                engine_action=entry.engine_action,
                flow_step=entry.flow_step,
                name=entry.name,
                command_argv=(*launcher_argv, *entry.argv),
                smoke_token=entry.smoke_token,
                demo_path_step=entry.demo_path_step,
            )
            for entry in argv_contract.entries
        )
    )
    _validate_command_demo_action_smoke_cli_argv_contract(
        contract,
        argv_contract,
        launcher_argv,
    )
    return contract


def _validate_command_demo_action_smoke_cli_argv_contract(
    contract: CommandDemoActionSmokeCliArgvContract,
    argv_contract: CommandDemoActionSmokeArgvContract,
    launcher_argv: tuple[str, ...],
) -> None:
    if tuple(entry.engine_action for entry in contract.entries) != tuple(
        entry.engine_action for entry in argv_contract.entries
    ):
        raise ValueError("Command demo action smoke CLI argv actions are inconsistent")
    if tuple(entry.flow_step for entry in contract.entries) != tuple(
        entry.flow_step for entry in argv_contract.entries
    ):
        raise ValueError("Command demo action smoke CLI argv flow steps are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(
        entry.name for entry in argv_contract.entries
    ):
        raise ValueError("Command demo action smoke CLI argv command names are inconsistent")
    if tuple(entry.smoke_token for entry in contract.entries) != tuple(
        entry.smoke_token for entry in argv_contract.entries
    ):
        raise ValueError("Command demo action smoke CLI argv tokens are inconsistent")
    if tuple(entry.demo_path_step for entry in contract.entries) != tuple(
        entry.demo_path_step for entry in argv_contract.entries
    ):
        raise ValueError("Command demo action smoke CLI argv path steps are inconsistent")
    if tuple(entry.command_argv[: len(launcher_argv)] for entry in contract.entries) != tuple(
        launcher_argv for _ in argv_contract.entries
    ):
        raise ValueError("Command demo action smoke CLI argv launcher is inconsistent")
    if tuple(entry.command_argv[len(launcher_argv) :] for entry in contract.entries) != tuple(
        entry.argv for entry in argv_contract.entries
    ):
        raise ValueError("Command demo action smoke CLI argv command is inconsistent")


def command_demo_action_smoke_cli_argv_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return tuple(
        (entry.engine_action, entry.command_argv)
        for entry in command_demo_action_smoke_cli_argv_contract(specs, launcher_argv).entries
    )


@lru_cache(maxsize=None)
def command_demo_action_smoke_cli_argv_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, CommandDemoActionSmokeCliArgvEntry], ...]:
    return tuple(
        (entry.engine_action, entry)
        for entry in command_demo_action_smoke_cli_argv_contract(specs, launcher_argv).entries
    )


@lru_cache(maxsize=None)
def _command_demo_action_smoke_cli_argv_entry_for(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    engine_action: str,
) -> CommandDemoActionSmokeCliArgvEntry | None:
    requested_action = engine_action.strip()
    if not requested_action:
        return None
    return dict(command_demo_action_smoke_cli_argv_index(specs, launcher_argv)).get(requested_action)


def command_demo_action_smoke_cli_argv_entry(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoActionSmokeCliArgvEntry | None:
    return _command_demo_action_smoke_cli_argv_entry_for(specs, launcher_argv, engine_action)


def command_demo_action_smoke_cli_argv(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    entry = command_demo_action_smoke_cli_argv_entry(engine_action, specs, launcher_argv)
    if entry is None:
        return ()
    return entry.command_argv


@lru_cache(maxsize=None)
def command_demo_action_smoke_script_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoActionSmokeScriptContract:
    argv_contract = command_demo_action_smoke_cli_argv_contract(specs, launcher_argv)
    contract = CommandDemoActionSmokeScriptContract(
        steps=tuple(
            CommandDemoActionSmokeScriptStep(
                ordinal=ordinal,
                engine_action=entry.engine_action,
                flow_step=entry.flow_step,
                name=entry.name,
                command_argv=entry.command_argv,
                smoke_token=entry.smoke_token,
                demo_path_step=entry.demo_path_step,
            )
            for ordinal, entry in enumerate(argv_contract.entries, start=1)
        )
    )
    _validate_command_demo_action_smoke_script_contract(contract, argv_contract)
    return contract


def _validate_command_demo_action_smoke_script_contract(
    contract: CommandDemoActionSmokeScriptContract,
    argv_contract: CommandDemoActionSmokeCliArgvContract,
) -> None:
    expected_ordinals = tuple(range(1, len(argv_contract.entries) + 1))
    if tuple(step.ordinal for step in contract.steps) != expected_ordinals:
        raise ValueError("Command demo action smoke script ordinals are inconsistent")
    if tuple(step.engine_action for step in contract.steps) != tuple(
        entry.engine_action for entry in argv_contract.entries
    ):
        raise ValueError("Command demo action smoke script actions are inconsistent")
    if tuple(step.flow_step for step in contract.steps) != tuple(
        entry.flow_step for entry in argv_contract.entries
    ):
        raise ValueError("Command demo action smoke script flow steps are inconsistent")
    if tuple(step.name for step in contract.steps) != tuple(entry.name for entry in argv_contract.entries):
        raise ValueError("Command demo action smoke script command names are inconsistent")
    if tuple(step.command_argv for step in contract.steps) != tuple(
        entry.command_argv for entry in argv_contract.entries
    ):
        raise ValueError("Command demo action smoke script argv values are inconsistent")
    if tuple(step.smoke_token for step in contract.steps) != tuple(
        entry.smoke_token for entry in argv_contract.entries
    ):
        raise ValueError("Command demo action smoke script tokens are inconsistent")
    if tuple(step.demo_path_step for step in contract.steps) != tuple(
        entry.demo_path_step for entry in argv_contract.entries
    ):
        raise ValueError("Command demo action smoke script path steps are inconsistent")


def command_demo_action_smoke_script_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, tuple[str, ...], str], ...]:
    contract = command_demo_action_smoke_script_contract(specs, launcher_argv)
    return tuple(
        (
            step.ordinal,
            step.engine_action,
            step.flow_step,
            step.name,
            step.command_argv,
            step.demo_path_step,
        )
        for step in contract.steps
    )


def command_demo_action_smoke_script_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, tuple[str, ...]], ...]:
    return tuple(
        (step.ordinal, step.engine_action, step.command_argv)
        for step in command_demo_action_smoke_script_contract(specs, launcher_argv).steps
    )


def command_demo_action_smoke_script_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str], ...]:
    return tuple(
        (
            step.ordinal,
            step.engine_action,
            step.flow_step,
            step.demo_path_step,
            _shell_join(step.command_argv),
        )
        for step in command_demo_action_smoke_script_contract(specs, launcher_argv).steps
    )


@lru_cache(maxsize=None)
def _command_demo_action_smoke_script_step_for_ordinal(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    ordinal: int,
) -> CommandDemoActionSmokeScriptStep | None:
    if ordinal <= 0:
        return None
    return {
        step.ordinal: step
        for step in command_demo_action_smoke_script_contract(specs, launcher_argv).steps
    }.get(ordinal)


def command_demo_action_smoke_script_step(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoActionSmokeScriptStep | None:
    return _command_demo_action_smoke_script_step_for_ordinal(specs, launcher_argv, ordinal)


def command_demo_action_smoke_script_argv(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    step = command_demo_action_smoke_script_step(ordinal, specs, launcher_argv)
    if step is None:
        return ()
    return step.command_argv


@lru_cache(maxsize=None)
def command_demo_readiness_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessContract:
    script_contract = command_demo_smoke_cli_script_contract(specs, launcher_argv)
    action_argv_by_action = dict(command_demo_action_smoke_cli_argv_lookup_table(specs, launcher_argv))
    contract = CommandDemoReadinessContract(
        entries=tuple(
            CommandDemoReadinessEntry(
                ordinal=step.ordinal,
                flow_step=step.flow_step,
                name=step.name,
                command_argv=step.command_argv,
                demo_path_step=step.demo_path_step,
                engine_actions=step.engine_actions,
                action_command_argv=tuple(
                    (engine_action, action_argv_by_action[engine_action])
                    for engine_action in step.engine_actions
                    if engine_action in action_argv_by_action
                ),
            )
            for step in script_contract.steps
        )
    )
    _validate_command_demo_readiness_contract(contract, script_contract, action_argv_by_action)
    return contract


def _validate_command_demo_readiness_contract(
    contract: CommandDemoReadinessContract,
    script_contract: CommandDemoSmokeCliScriptContract,
    action_argv_by_action: dict[str, tuple[str, ...]],
) -> None:
    if tuple(entry.ordinal for entry in contract.entries) != tuple(step.ordinal for step in script_contract.steps):
        raise ValueError("Command demo readiness ordinals are inconsistent")
    if tuple(entry.flow_step for entry in contract.entries) != tuple(
        step.flow_step for step in script_contract.steps
    ):
        raise ValueError("Command demo readiness flow steps are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(step.name for step in script_contract.steps):
        raise ValueError("Command demo readiness command names are inconsistent")
    if tuple(entry.command_argv for entry in contract.entries) != tuple(
        step.command_argv for step in script_contract.steps
    ):
        raise ValueError("Command demo readiness argv values are inconsistent")
    if tuple(entry.demo_path_step for entry in contract.entries) != tuple(
        step.demo_path_step for step in script_contract.steps
    ):
        raise ValueError("Command demo readiness path steps are inconsistent")
    if tuple(entry.engine_actions for entry in contract.entries) != tuple(
        step.engine_actions for step in script_contract.steps
    ):
        raise ValueError("Command demo readiness engine actions are inconsistent")

    for entry in contract.entries:
        expected_action_argv = tuple(
            (engine_action, action_argv_by_action[engine_action])
            for engine_action in entry.engine_actions
            if engine_action in action_argv_by_action
        )
        if expected_action_argv != entry.action_command_argv:
            raise ValueError(f"Command demo readiness action argv is incomplete: {entry.flow_step}")
        if len(expected_action_argv) != len(entry.engine_actions):
            raise ValueError(f"Command demo readiness action coverage is incomplete: {entry.flow_step}")
        if any(not argv for _, argv in entry.action_command_argv):
            raise ValueError(f"Command demo readiness action argv must not be empty: {entry.flow_step}")


def command_demo_readiness_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, tuple[str, ...], str, tuple[str, ...], tuple[tuple[str, tuple[str, ...]], ...]], ...]:
    contract = command_demo_readiness_contract(specs, launcher_argv)
    return tuple(
        (
            entry.ordinal,
            entry.flow_step,
            entry.name,
            entry.command_argv,
            entry.demo_path_step,
            entry.engine_actions,
            entry.action_command_argv,
        )
        for entry in contract.entries
    )


def command_demo_readiness_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return tuple(
        (entry.flow_step, entry.command_argv)
        for entry in command_demo_readiness_contract(specs, launcher_argv).entries
    )


def command_demo_readiness_command_line_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (entry.flow_step, _shell_join(entry.command_argv))
        for entry in command_demo_readiness_contract(specs, launcher_argv).entries
    )


@lru_cache(maxsize=None)
def command_demo_readiness_cli_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessCliContract:
    readiness_by_name = {
        entry.name: entry
        for entry in command_demo_readiness_contract(specs, launcher_argv).entries
    }
    cli_lookup = command_cli_lookup_table() if specs == COMMAND_SPECS else command_lookup_index(specs)
    contract = CommandDemoReadinessCliContract(
        entries=tuple(
            CommandDemoReadinessCliEntry(
                cli_token=cli_token,
                flow_step=readiness_entry.flow_step,
                name=readiness_entry.name,
                command_argv=readiness_entry.command_argv,
                demo_path_step=readiness_entry.demo_path_step,
                engine_actions=readiness_entry.engine_actions,
            )
            for cli_token, canonical_name in cli_lookup
            for readiness_entry in (readiness_by_name.get(canonical_name),)
            if readiness_entry is not None
        )
    )
    _validate_command_demo_readiness_cli_contract(
        contract,
        readiness_by_name,
        cli_lookup,
    )
    return contract


def _validate_command_demo_readiness_cli_contract(
    contract: CommandDemoReadinessCliContract,
    readiness_by_name: dict[str, CommandDemoReadinessEntry],
    cli_lookup: tuple[tuple[str, str], ...],
) -> None:
    if tuple(entry.cli_token for entry in contract.entries) != tuple(token for token, _ in cli_lookup):
        raise ValueError("Command demo readiness CLI tokens are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(name for _, name in cli_lookup):
        raise ValueError("Command demo readiness CLI names are inconsistent")
    if len({entry.cli_token for entry in contract.entries}) != len(contract.entries):
        raise ValueError("Command demo readiness CLI tokens must be unique")
    for entry in contract.entries:
        readiness_entry = readiness_by_name.get(entry.name)
        if readiness_entry is None:
            raise ValueError(f"Command demo readiness CLI route is missing: {entry.cli_token}")
        if not entry.cli_token.strip():
            raise ValueError("Command demo readiness CLI token must not be empty")
        if entry.flow_step != readiness_entry.flow_step:
            raise ValueError(f"Command demo readiness CLI flow step is inconsistent: {entry.cli_token}")
        if entry.command_argv != readiness_entry.command_argv:
            raise ValueError(f"Command demo readiness CLI argv is inconsistent: {entry.cli_token}")
        if entry.demo_path_step != readiness_entry.demo_path_step:
            raise ValueError(f"Command demo readiness CLI path step is inconsistent: {entry.cli_token}")
        if entry.engine_actions != readiness_entry.engine_actions:
            raise ValueError(f"Command demo readiness CLI actions are inconsistent: {entry.cli_token}")


def command_demo_readiness_cli_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, tuple[str, ...], str, tuple[str, ...]], ...]:
    return tuple(
        (
            entry.cli_token,
            entry.flow_step,
            entry.name,
            entry.command_argv,
            entry.demo_path_step,
            entry.engine_actions,
        )
        for entry in command_demo_readiness_cli_contract(specs, launcher_argv).entries
    )


def command_demo_readiness_cli_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str], ...]:
    return tuple(
        (entry.cli_token, entry.flow_step, entry.name)
        for entry in command_demo_readiness_cli_contract(specs, launcher_argv).entries
    )


def command_demo_readiness_action_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    return tuple(
        (entry.flow_step, entry.engine_action, entry.action_command_argv)
        for entry in command_demo_readiness_action_contract(specs, launcher_argv).entries
    )


def command_demo_readiness_action_argv_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return tuple(
        (entry.engine_action, entry.action_command_argv)
        for entry in command_demo_readiness_action_contract(specs, launcher_argv).entries
    )


def command_demo_readiness_missing_engine_actions(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    covered_actions = {
        engine_action
        for engine_action, _ in command_demo_readiness_action_argv_lookup_table(specs, launcher_argv)
    }
    return tuple(
        engine_action
        for engine_action in command_demo_engine_actions(specs)
        if engine_action not in covered_actions
    )


def command_demo_readiness_is_complete(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> bool:
    return not command_demo_readiness_missing_engine_actions(specs, launcher_argv)


def command_demo_readiness_action_line_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (engine_action, _shell_join(action_argv))
        for engine_action, action_argv in command_demo_readiness_action_argv_lookup_table(specs, launcher_argv)
    )


@lru_cache(maxsize=None)
def command_demo_readiness_action_argv_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_readiness_action_argv_lookup_table(specs, launcher_argv)


def command_demo_readiness_argv_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    requested_action = engine_action.strip()
    if not requested_action:
        return ()
    return dict(command_demo_readiness_action_argv_index(specs, launcher_argv)).get(requested_action, ())


def command_demo_readiness_line_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    argv = command_demo_readiness_argv_for_engine_action(engine_action, specs, launcher_argv)
    if not argv:
        return ""
    return _shell_join(argv)


def command_demo_readiness_command_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    entry = command_demo_readiness_action_entry(engine_action, specs, launcher_argv)
    if entry is None:
        return None
    return entry.name


@lru_cache(maxsize=None)
def command_demo_readiness_action_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessActionContract:
    readiness_contract = command_demo_readiness_contract(specs, launcher_argv)
    entries = tuple(
        CommandDemoReadinessActionEntry(
            engine_action=engine_action,
            flow_step=readiness_entry.flow_step,
            name=readiness_entry.name,
            command_argv=readiness_entry.command_argv,
            action_command_argv=action_command_argv,
            demo_path_step=readiness_entry.demo_path_step,
        )
        for readiness_entry in readiness_contract.entries
        for engine_action, action_command_argv in readiness_entry.action_command_argv
    )
    contract = CommandDemoReadinessActionContract(entries=entries)
    _validate_command_demo_readiness_action_contract(contract, readiness_contract, launcher_argv)
    return contract


def _validate_command_demo_readiness_action_contract(
    contract: CommandDemoReadinessActionContract,
    readiness_contract: CommandDemoReadinessContract,
    launcher_argv: tuple[str, ...],
) -> None:
    expected_entries = tuple(
        (
            engine_action,
            readiness_entry.flow_step,
            readiness_entry.name,
            readiness_entry.command_argv,
            action_command_argv,
            readiness_entry.demo_path_step,
        )
        for readiness_entry in readiness_contract.entries
        for engine_action, action_command_argv in readiness_entry.action_command_argv
    )
    actual_entries = tuple(
        (
            entry.engine_action,
            entry.flow_step,
            entry.name,
            entry.command_argv,
            entry.action_command_argv,
            entry.demo_path_step,
        )
        for entry in contract.entries
    )
    if actual_entries != expected_entries:
        raise ValueError("Command demo readiness action entries are inconsistent")
    if len({entry.engine_action for entry in contract.entries}) != len(contract.entries):
        raise ValueError("Command demo readiness action entries must be unique")
    for entry in contract.entries:
        if not entry.action_command_argv:
            raise ValueError(f"Command demo readiness action argv must not be empty: {entry.engine_action}")
        if entry.action_command_argv[: len(launcher_argv)] != launcher_argv:
            raise ValueError(f"Command demo readiness action launcher is inconsistent: {entry.engine_action}")

def command_demo_readiness_action_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, tuple[str, ...], tuple[str, ...], str], ...]:
    return tuple(
        (
            entry.engine_action,
            entry.flow_step,
            entry.name,
            entry.command_argv,
            entry.action_command_argv,
            entry.demo_path_step,
        )
        for entry in command_demo_readiness_action_contract(specs, launcher_argv).entries
    )


def command_demo_readiness_action_smoke_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, str, str], ...]:
    return tuple(
        (
            entry.engine_action,
            entry.flow_step,
            entry.name,
            _shell_join(entry.action_command_argv),
            entry.demo_path_step,
        )
        for entry in command_demo_readiness_action_contract(specs, launcher_argv).entries
    )


@lru_cache(maxsize=None)
def command_demo_readiness_smoke_plan(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessSmokePlan:
    readiness_contract = command_demo_readiness_contract(specs, launcher_argv)
    plan = CommandDemoReadinessSmokePlan(
        steps=tuple(
            CommandDemoReadinessSmokePlanStep(
                ordinal=entry.ordinal,
                flow_step=entry.flow_step,
                name=entry.name,
                command_line=_shell_join(entry.command_argv),
                demo_path_step=entry.demo_path_step,
                action_lines=tuple(
                    (engine_action, _shell_join(action_command_argv))
                    for engine_action, action_command_argv in entry.action_command_argv
                ),
            )
            for entry in readiness_contract.entries
        )
    )
    _validate_command_demo_readiness_smoke_plan(plan, readiness_contract)
    return plan


def _validate_command_demo_readiness_smoke_plan(
    plan: CommandDemoReadinessSmokePlan,
    readiness_contract: CommandDemoReadinessContract,
) -> None:
    if tuple(step.ordinal for step in plan.steps) != tuple(
        entry.ordinal for entry in readiness_contract.entries
    ):
        raise ValueError("Command demo readiness smoke plan ordinals are inconsistent")
    if tuple(step.flow_step for step in plan.steps) != tuple(
        entry.flow_step for entry in readiness_contract.entries
    ):
        raise ValueError("Command demo readiness smoke plan flow steps are inconsistent")
    if tuple(step.name for step in plan.steps) != tuple(entry.name for entry in readiness_contract.entries):
        raise ValueError("Command demo readiness smoke plan command names are inconsistent")
    if tuple(step.demo_path_step for step in plan.steps) != tuple(
        entry.demo_path_step for entry in readiness_contract.entries
    ):
        raise ValueError("Command demo readiness smoke plan path steps are inconsistent")
    for step, entry in zip(plan.steps, readiness_contract.entries, strict=True):
        if step.command_line != _shell_join(entry.command_argv):
            raise ValueError(f"Command demo readiness smoke plan command is inconsistent: {entry.flow_step}")
        expected_action_lines = tuple(
            (engine_action, _shell_join(action_command_argv))
            for engine_action, action_command_argv in entry.action_command_argv
        )
        if step.action_lines != expected_action_lines:
            raise ValueError(f"Command demo readiness smoke plan actions are inconsistent: {entry.flow_step}")
        if not step.command_line:
            raise ValueError(f"Command demo readiness smoke plan command must not be empty: {entry.flow_step}")
        if any(not action_line for _, action_line in step.action_lines):
            raise ValueError(f"Command demo readiness smoke plan action must not be empty: {entry.flow_step}")


def command_demo_readiness_smoke_plan_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, tuple[tuple[str, str], ...]], ...]:
    return tuple(
        (
            step.ordinal,
            step.flow_step,
            step.name,
            step.command_line,
            step.demo_path_step,
            step.action_lines,
        )
        for step in command_demo_readiness_smoke_plan(specs, launcher_argv).steps
    )


@lru_cache(maxsize=None)
def _command_demo_readiness_smoke_plan_step_for_ordinal(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    ordinal: int,
) -> CommandDemoReadinessSmokePlanStep | None:
    for step in command_demo_readiness_smoke_plan(specs, launcher_argv).steps:
        if step.ordinal == ordinal:
            return step
    return None


def command_demo_readiness_smoke_plan_step(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessSmokePlanStep | None:
    return _command_demo_readiness_smoke_plan_step_for_ordinal(specs, launcher_argv, ordinal)


@lru_cache(maxsize=None)
def _command_demo_readiness_smoke_plan_step_for_demo_path_step(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    demo_path_step: str,
) -> CommandDemoReadinessSmokePlanStep | None:
    requested_step = _normalize_token(demo_path_step)
    if not requested_step:
        return None
    for step in command_demo_readiness_smoke_plan(specs, launcher_argv).steps:
        if _normalize_token(step.demo_path_step) == requested_step:
            return step
    return None


def command_demo_readiness_smoke_plan_step_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessSmokePlanStep | None:
    return _command_demo_readiness_smoke_plan_step_for_demo_path_step(
        specs,
        launcher_argv,
        demo_path_step,
    )


@lru_cache(maxsize=None)
def _command_demo_readiness_smoke_plan_step_for_flow_step(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    flow_step: str,
) -> CommandDemoReadinessSmokePlanStep | None:
    requested_flow_step = _normalize_token(flow_step)
    if not requested_flow_step:
        return None
    for step in command_demo_readiness_smoke_plan(specs, launcher_argv).steps:
        if step.flow_step == requested_flow_step:
            return step
    return None


def command_demo_readiness_smoke_plan_step_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessSmokePlanStep | None:
    return _command_demo_readiness_smoke_plan_step_for_flow_step(
        specs,
        launcher_argv,
        flow_step,
    )


def command_demo_readiness_smoke_plan_argv(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    step = command_demo_readiness_smoke_plan_step(ordinal, specs, launcher_argv)
    if step is None:
        return ()
    return tuple(shlex.split(step.command_line))


def command_demo_readiness_smoke_plan_argv_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    step = command_demo_readiness_smoke_plan_step_for_flow_step(flow_step, specs, launcher_argv)
    if step is None:
        return ()
    return tuple(shlex.split(step.command_line))


def command_demo_readiness_required_argv(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, ...], ...]:
    return tuple(entry.command_argv for entry in command_demo_readiness_contract(specs, launcher_argv).entries)


def command_demo_readiness_required_argv_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return tuple(
        (entry.flow_step, entry.command_argv)
        for entry in command_demo_readiness_contract(specs, launcher_argv).entries
    )


@lru_cache(maxsize=None)
def command_demo_path_readiness_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoPathReadinessContract:
    readiness_entries = {
        entry.ordinal: entry
        for entry in command_demo_readiness_contract(specs, launcher_argv).entries
    }
    smoke_plan = command_demo_readiness_smoke_plan(specs, launcher_argv)
    contract = CommandDemoPathReadinessContract(
        steps=tuple(
            CommandDemoPathReadinessStep(
                ordinal=step.ordinal,
                demo_path_step=step.demo_path_step,
                flow_step=step.flow_step,
                name=step.name,
                command_line=step.command_line,
                engine_actions=readiness_entries[step.ordinal].engine_actions,
                action_lines=step.action_lines,
            )
            for step in smoke_plan.steps
        )
    )
    _validate_command_demo_path_readiness_contract(contract, smoke_plan, readiness_entries)
    return contract


def _validate_command_demo_path_readiness_contract(
    contract: CommandDemoPathReadinessContract,
    smoke_plan: CommandDemoReadinessSmokePlan,
    readiness_entries: dict[int, CommandDemoReadinessEntry],
) -> None:
    if tuple(step.ordinal for step in contract.steps) != tuple(step.ordinal for step in smoke_plan.steps):
        raise ValueError("Command demo path readiness ordinals are inconsistent")
    if tuple(step.demo_path_step for step in contract.steps) != tuple(
        step.demo_path_step for step in smoke_plan.steps
    ):
        raise ValueError("Command demo path readiness path steps are inconsistent")
    if tuple(step.flow_step for step in contract.steps) != tuple(step.flow_step for step in smoke_plan.steps):
        raise ValueError("Command demo path readiness flow steps are inconsistent")
    if tuple(step.name for step in contract.steps) != tuple(step.name for step in smoke_plan.steps):
        raise ValueError("Command demo path readiness command names are inconsistent")
    if tuple(step.command_line for step in contract.steps) != tuple(
        step.command_line for step in smoke_plan.steps
    ):
        raise ValueError("Command demo path readiness command lines are inconsistent")
    for step in contract.steps:
        readiness_entry = readiness_entries.get(step.ordinal)
        if readiness_entry is None:
            raise ValueError(f"Command demo path readiness missing step: {step.ordinal}")
        if step.engine_actions != readiness_entry.engine_actions:
            raise ValueError(f"Command demo path readiness actions are inconsistent: {step.flow_step}")
        if step.action_lines != tuple(
            (engine_action, _shell_join(action_argv))
            for engine_action, action_argv in readiness_entry.action_command_argv
        ):
            raise ValueError(f"Command demo path readiness action lines are inconsistent: {step.flow_step}")
        _validate_command_demo_path_readiness_cli_lines(step, readiness_entry)


def _validate_command_demo_path_readiness_cli_lines(
    step: CommandDemoPathReadinessStep,
    readiness_entry: CommandDemoReadinessEntry,
) -> None:
    try:
        command_argv = tuple(shlex.split(step.command_line))
    except ValueError as exc:
        raise ValueError(
            f"Command demo path readiness command line is not parseable: {step.flow_step}"
        ) from exc
    if command_argv != readiness_entry.command_argv:
        raise ValueError(
            f"Command demo path readiness command line argv is inconsistent: {step.flow_step}"
        )

    action_argv_by_action = dict(readiness_entry.action_command_argv)
    for engine_action, action_line in step.action_lines:
        try:
            action_argv = tuple(shlex.split(action_line))
        except ValueError as exc:
            raise ValueError(
                f"Command demo path readiness action line is not parseable: {engine_action}"
            ) from exc
        if action_argv != action_argv_by_action.get(engine_action):
            raise ValueError(
                f"Command demo path readiness action line argv is inconsistent: {engine_action}"
            )


def command_demo_path_readiness_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, tuple[str, ...], tuple[tuple[str, str], ...]], ...]:
    return tuple(
        (
            step.ordinal,
            step.demo_path_step,
            step.flow_step,
            step.name,
            step.command_line,
            step.engine_actions,
            step.action_lines,
        )
        for step in command_demo_path_readiness_contract(specs, launcher_argv).steps
    )


@lru_cache(maxsize=None)
def command_demo_readiness_handoff_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessHandoffContract:
    readiness_contract = command_demo_path_readiness_contract(specs, launcher_argv)
    contract = CommandDemoReadinessHandoffContract(
        entries=tuple(
            CommandDemoReadinessHandoffEntry(
                ordinal=step.ordinal,
                demo_path_step=step.demo_path_step,
                flow_step=step.flow_step,
                name=step.name,
                command_line=step.command_line,
                action_lines=step.action_lines,
            )
            for step in readiness_contract.steps
        )
    )
    _validate_command_demo_readiness_handoff_contract(contract, readiness_contract)
    return contract


def _validate_command_demo_readiness_handoff_contract(
    contract: CommandDemoReadinessHandoffContract,
    readiness_contract: CommandDemoPathReadinessContract,
) -> None:
    if tuple(entry.ordinal for entry in contract.entries) != tuple(
        step.ordinal for step in readiness_contract.steps
    ):
        raise ValueError("Command demo readiness handoff ordinals are inconsistent")
    if tuple(entry.demo_path_step for entry in contract.entries) != tuple(
        step.demo_path_step for step in readiness_contract.steps
    ):
        raise ValueError("Command demo readiness handoff path steps are inconsistent")
    if tuple(entry.flow_step for entry in contract.entries) != tuple(
        step.flow_step for step in readiness_contract.steps
    ):
        raise ValueError("Command demo readiness handoff flow steps are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(step.name for step in readiness_contract.steps):
        raise ValueError("Command demo readiness handoff command names are inconsistent")
    if tuple(entry.command_line for entry in contract.entries) != tuple(
        step.command_line for step in readiness_contract.steps
    ):
        raise ValueError("Command demo readiness handoff command lines are inconsistent")
    if tuple(entry.action_lines for entry in contract.entries) != tuple(
        step.action_lines for step in readiness_contract.steps
    ):
        raise ValueError("Command demo readiness handoff action lines are inconsistent")
    if any(not entry.command_line for entry in contract.entries):
        raise ValueError("Command demo readiness handoff command lines must not be empty")
    if any(not entry.action_lines for entry in contract.entries):
        raise ValueError("Command demo readiness handoff action lines must not be empty")


def command_demo_readiness_handoff_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, tuple[tuple[str, str], ...]], ...]:
    return tuple(
        (
            entry.ordinal,
            entry.demo_path_step,
            entry.flow_step,
            entry.name,
            entry.command_line,
            entry.action_lines,
        )
        for entry in command_demo_readiness_handoff_contract(specs, launcher_argv).entries
    )


def _format_command_demo_readiness_handoff_line(
    entry: CommandDemoReadinessHandoffEntry,
) -> str:
    action_lines = "; ".join(
        f"{engine_action}: {command_line}"
        for engine_action, command_line in entry.action_lines
    )
    return (
        f"{entry.ordinal}. {entry.demo_path_step} "
        f"[{entry.flow_step}/{entry.name}] command={entry.command_line}; "
        f"actions={action_lines}"
    )


@lru_cache(maxsize=None)
def command_demo_readiness_handoff_line_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessHandoffLineContract:
    handoff_contract = command_demo_readiness_handoff_contract(specs, launcher_argv)
    contract = CommandDemoReadinessHandoffLineContract(
        lines=tuple(
            CommandDemoReadinessHandoffLine(
                ordinal=entry.ordinal,
                demo_path_step=entry.demo_path_step,
                flow_step=entry.flow_step,
                name=entry.name,
                line=_format_command_demo_readiness_handoff_line(entry),
            )
            for entry in handoff_contract.entries
        )
    )
    _validate_command_demo_readiness_handoff_line_contract(contract, handoff_contract)
    return contract


def _validate_command_demo_readiness_handoff_line_contract(
    contract: CommandDemoReadinessHandoffLineContract,
    handoff_contract: CommandDemoReadinessHandoffContract,
) -> None:
    if tuple(line.ordinal for line in contract.lines) != tuple(
        entry.ordinal for entry in handoff_contract.entries
    ):
        raise ValueError("Command demo readiness handoff line ordinals are inconsistent")
    if tuple(line.demo_path_step for line in contract.lines) != tuple(
        entry.demo_path_step for entry in handoff_contract.entries
    ):
        raise ValueError("Command demo readiness handoff line path steps are inconsistent")
    if tuple(line.flow_step for line in contract.lines) != tuple(
        entry.flow_step for entry in handoff_contract.entries
    ):
        raise ValueError("Command demo readiness handoff line flow steps are inconsistent")
    if tuple(line.name for line in contract.lines) != tuple(
        entry.name for entry in handoff_contract.entries
    ):
        raise ValueError("Command demo readiness handoff line names are inconsistent")
    expected_lines = tuple(
        _format_command_demo_readiness_handoff_line(entry)
        for entry in handoff_contract.entries
    )
    if tuple(line.line for line in contract.lines) != expected_lines:
        raise ValueError("Command demo readiness handoff lines are inconsistent")
    if any(not line.line for line in contract.lines):
        raise ValueError("Command demo readiness handoff lines must not be empty")


def command_demo_readiness_handoff_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return tuple(
        line.line
        for line in command_demo_readiness_handoff_line_contract(specs, launcher_argv).lines
    )


def _format_command_demo_readiness_handoff_checklist_line(
    entry: CommandDemoReadinessHandoffActionStep,
) -> str:
    action_lines = ", ".join(
        f"{engine_action} -> `{command_line}`"
        for engine_action, command_line in entry.exact_action_lines
    )
    return (
        f"- [ ] {entry.ordinal}. {entry.demo_path_step} "
        f"({entry.flow_step}/{entry.name}): `{entry.command_line}`; "
        f"actions: {action_lines}"
    )


@lru_cache(maxsize=None)
def command_demo_readiness_handoff_checklist_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessHandoffChecklistContract:
    handoff_contract = command_demo_readiness_handoff_action_contract(specs, launcher_argv)
    contract = CommandDemoReadinessHandoffChecklistContract(
        lines=tuple(
            CommandDemoReadinessHandoffChecklistLine(
                ordinal=entry.ordinal,
                demo_path_step=entry.demo_path_step,
                flow_step=entry.flow_step,
                name=entry.name,
                line=_format_command_demo_readiness_handoff_checklist_line(entry),
            )
            for entry in handoff_contract.steps
        )
    )
    _validate_command_demo_readiness_handoff_checklist_contract(contract, handoff_contract)
    return contract


def _validate_command_demo_readiness_handoff_checklist_contract(
    contract: CommandDemoReadinessHandoffChecklistContract,
    handoff_contract: CommandDemoReadinessHandoffActionContract,
) -> None:
    if tuple(line.ordinal for line in contract.lines) != tuple(
        entry.ordinal for entry in handoff_contract.steps
    ):
        raise ValueError("Command demo readiness handoff checklist ordinals are inconsistent")
    if tuple(line.demo_path_step for line in contract.lines) != tuple(
        entry.demo_path_step for entry in handoff_contract.steps
    ):
        raise ValueError("Command demo readiness handoff checklist path steps are inconsistent")
    if tuple(line.flow_step for line in contract.lines) != tuple(
        entry.flow_step for entry in handoff_contract.steps
    ):
        raise ValueError("Command demo readiness handoff checklist flow steps are inconsistent")
    if tuple(line.name for line in contract.lines) != tuple(
        entry.name for entry in handoff_contract.steps
    ):
        raise ValueError("Command demo readiness handoff checklist names are inconsistent")
    expected_lines = tuple(
        _format_command_demo_readiness_handoff_checklist_line(entry)
        for entry in handoff_contract.steps
    )
    if tuple(line.line for line in contract.lines) != expected_lines:
        raise ValueError("Command demo readiness handoff checklist lines are inconsistent")
    if any(not line.line for line in contract.lines):
        raise ValueError("Command demo readiness handoff checklist lines must not be empty")
    if any(not line.line.startswith("- [ ] ") for line in contract.lines):
        raise ValueError("Command demo readiness handoff checklist lines must be checklist items")


def command_demo_readiness_handoff_checklist_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return tuple(
        line.line
        for line in command_demo_readiness_handoff_checklist_contract(specs, launcher_argv).lines
    )


@lru_cache(maxsize=None)
def command_demo_readiness_handoff_action_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessHandoffActionContract:
    readiness_steps = command_demo_path_readiness_contract(specs, launcher_argv)
    exact_action_lines = command_demo_readiness_exact_action_line_lookup_table(specs, launcher_argv)
    exact_action_lines_by_flow_step: dict[str, list[tuple[str, str]]] = {}
    for engine_action, command_line in exact_action_lines:
        flow_step = command_demo_readiness_flow_step_for_argv(command_line, specs, launcher_argv)
        if flow_step is None:
            raise ValueError(f"Command demo readiness handoff action is not routeable: {engine_action}")
        exact_action_lines_by_flow_step.setdefault(flow_step, []).append((engine_action, command_line))

    contract = CommandDemoReadinessHandoffActionContract(
        steps=tuple(
            CommandDemoReadinessHandoffActionStep(
                ordinal=step.ordinal,
                demo_path_step=step.demo_path_step,
                flow_step=step.flow_step,
                name=step.name,
                command_line=step.command_line,
                exact_action_lines=tuple(exact_action_lines_by_flow_step.get(step.flow_step, ())),
            )
            for step in readiness_steps.steps
        )
    )
    _validate_command_demo_readiness_handoff_action_contract(
        contract,
        readiness_steps,
        exact_action_lines,
        specs,
        launcher_argv,
    )
    return contract


def _validate_command_demo_readiness_handoff_action_contract(
    contract: CommandDemoReadinessHandoffActionContract,
    readiness_steps: CommandDemoPathReadinessContract,
    exact_action_lines: tuple[tuple[str, str], ...],
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    if tuple(step.ordinal for step in contract.steps) != tuple(step.ordinal for step in readiness_steps.steps):
        raise ValueError("Command demo readiness handoff action ordinals are inconsistent")
    if tuple(step.demo_path_step for step in contract.steps) != tuple(
        step.demo_path_step for step in readiness_steps.steps
    ):
        raise ValueError("Command demo readiness handoff action path steps are inconsistent")
    if tuple(step.flow_step for step in contract.steps) != tuple(step.flow_step for step in readiness_steps.steps):
        raise ValueError("Command demo readiness handoff action flow steps are inconsistent")
    if tuple(step.name for step in contract.steps) != tuple(step.name for step in readiness_steps.steps):
        raise ValueError("Command demo readiness handoff action names are inconsistent")
    if tuple(step.command_line for step in contract.steps) != tuple(
        step.command_line for step in readiness_steps.steps
    ):
        raise ValueError("Command demo readiness handoff action command lines are inconsistent")

    flattened_action_lines = tuple(
        action_line
        for step in contract.steps
        for action_line in step.exact_action_lines
    )
    if flattened_action_lines != exact_action_lines:
        raise ValueError("Command demo readiness handoff action exact lines are inconsistent")
    if any(not step.exact_action_lines for step in contract.steps):
        raise ValueError("Command demo readiness handoff action steps must include exact action lines")
    for step in contract.steps:
        for engine_action, command_line in step.exact_action_lines:
            action_flow_step = command_demo_readiness_flow_step_for_argv(command_line, specs, launcher_argv)
            if action_flow_step != step.flow_step:
                raise ValueError(
                    f"Command demo readiness handoff action line is attached to the wrong flow step: {engine_action}"
                )


def command_demo_readiness_handoff_action_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, tuple[tuple[str, str], ...]], ...]:
    return tuple(
        (
            step.ordinal,
            step.demo_path_step,
            step.flow_step,
            step.name,
            step.command_line,
            step.exact_action_lines,
        )
        for step in command_demo_readiness_handoff_action_contract(
            specs,
            launcher_argv,
        ).steps
    )


@lru_cache(maxsize=None)
def command_demo_readiness_route_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessRouteContract:
    readiness_contract = command_demo_path_readiness_contract(specs, launcher_argv)
    routes_by_flow_step = {
        entry.flow_step: entry
        for entry in command_demo_path_contract(specs).entries
    }
    contract = CommandDemoReadinessRouteContract(
        entries=tuple(
            CommandDemoReadinessRouteEntry(
                ordinal=step.ordinal,
                demo_path_step=step.demo_path_step,
                flow_step=step.flow_step,
                name=step.name,
                cli_tokens=routes_by_flow_step[step.flow_step].cli_tokens,
                command_line=step.command_line,
                engine_actions=step.engine_actions,
                action_lines=step.action_lines,
            )
            for step in readiness_contract.steps
        )
    )
    _validate_command_demo_readiness_route_contract(
        contract,
        readiness_contract,
        routes_by_flow_step,
        specs=specs,
        launcher_argv=launcher_argv,
    )
    return contract


def _validate_command_demo_readiness_route_contract(
    contract: CommandDemoReadinessRouteContract,
    readiness_contract: CommandDemoPathReadinessContract,
    routes_by_flow_step: dict[str, CommandDemoPathEntry],
    *,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    if tuple(entry.ordinal for entry in contract.entries) != tuple(
        step.ordinal for step in readiness_contract.steps
    ):
        raise ValueError("Command demo readiness route ordinals are inconsistent")
    if tuple(entry.demo_path_step for entry in contract.entries) != tuple(
        step.demo_path_step for step in readiness_contract.steps
    ):
        raise ValueError("Command demo readiness route path steps are inconsistent")
    if tuple(entry.flow_step for entry in contract.entries) != tuple(
        step.flow_step for step in readiness_contract.steps
    ):
        raise ValueError("Command demo readiness route flow steps are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(
        step.name for step in readiness_contract.steps
    ):
        raise ValueError("Command demo readiness route names are inconsistent")
    if tuple(entry.command_line for entry in contract.entries) != tuple(
        step.command_line for step in readiness_contract.steps
    ):
        raise ValueError("Command demo readiness route command lines are inconsistent")
    if tuple(entry.engine_actions for entry in contract.entries) != tuple(
        step.engine_actions for step in readiness_contract.steps
    ):
        raise ValueError("Command demo readiness route actions are inconsistent")
    if tuple(entry.action_lines for entry in contract.entries) != tuple(
        step.action_lines for step in readiness_contract.steps
    ):
        raise ValueError("Command demo readiness route action lines are inconsistent")

    for entry in contract.entries:
        route = routes_by_flow_step.get(entry.flow_step)
        if route is None:
            raise ValueError(f"Command demo readiness route is missing: {entry.flow_step}")
        if entry.cli_tokens != route.cli_tokens:
            raise ValueError(f"Command demo readiness route CLI tokens are inconsistent: {entry.flow_step}")
        if not entry.cli_tokens or any(not token.strip() for token in entry.cli_tokens):
            raise ValueError(f"Command demo readiness route CLI tokens must not be empty: {entry.flow_step}")
        if not entry.command_line:
            raise ValueError(f"Command demo readiness route command must not be empty: {entry.flow_step}")
        if not entry.action_lines:
            raise ValueError(f"Command demo readiness route action lines must not be empty: {entry.flow_step}")
        _validate_command_demo_readiness_route_lines(entry, specs, launcher_argv)


def _validate_command_demo_readiness_route_lines(
    entry: CommandDemoReadinessRouteEntry,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    command_entry = command_demo_readiness_entry_for_argv(entry.command_line, specs, launcher_argv)
    if command_entry is None:
        raise ValueError(f"Command demo readiness route command is not routeable: {entry.flow_step}")
    if command_entry.flow_step != entry.flow_step or command_entry.name != entry.name:
        raise ValueError(f"Command demo readiness route command target is inconsistent: {entry.flow_step}")

    seen_actions: list[str] = []
    for engine_action, action_line in entry.action_lines:
        action_entries = command_demo_readiness_action_entries_for_argv(action_line, specs, launcher_argv)
        if not any(action_entry.engine_action == engine_action for action_entry in action_entries):
            raise ValueError(f"Command demo readiness route action is not routeable: {engine_action}")
        if any(
            action_entry.flow_step != entry.flow_step or action_entry.name != entry.name
            for action_entry in action_entries
            if action_entry.engine_action == engine_action
        ):
            raise ValueError(f"Command demo readiness route action target is inconsistent: {engine_action}")
        seen_actions.append(engine_action)

    if tuple(seen_actions) != entry.engine_actions:
        raise ValueError(f"Command demo readiness route action coverage is inconsistent: {entry.flow_step}")


def command_demo_readiness_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, tuple[str, ...], str, tuple[str, ...], tuple[tuple[str, str], ...]], ...]:
    return tuple(
        (
            entry.ordinal,
            entry.demo_path_step,
            entry.flow_step,
            entry.name,
            entry.cli_tokens,
            entry.command_line,
            entry.engine_actions,
            entry.action_lines,
        )
        for entry in command_demo_readiness_route_contract(specs, launcher_argv).entries
    )


def command_demo_readiness_route_payload(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> dict[str, object]:
    contract = command_demo_readiness_route_contract(specs, launcher_argv)
    return {
        "launcher_argv": launcher_argv,
        "routes": [
            {
                "ordinal": entry.ordinal,
                "demo_path_step": entry.demo_path_step,
                "flow_step": entry.flow_step,
                "command": entry.name,
                "cli_tokens": entry.cli_tokens,
                "command_line": entry.command_line,
                "engine_actions": entry.engine_actions,
                "action_lines": [
                    {
                        "engine_action": engine_action,
                        "command_line": command_line,
                    }
                    for engine_action, command_line in entry.action_lines
                ],
            }
            for entry in contract.entries
        ],
    }


def command_demo_readiness_route_json(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return json.dumps(
        command_demo_readiness_route_payload(specs, launcher_argv),
        sort_keys=True,
        separators=(",", ":"),
    )


@lru_cache(maxsize=None)
def command_demo_execution_plan_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoExecutionPlanContract:
    readiness_contract = command_demo_readiness_contract(specs, launcher_argv)
    contract = CommandDemoExecutionPlanContract(
        launcher_argv=launcher_argv,
        steps=tuple(
            CommandDemoExecutionPlanStep(
                ordinal=entry.ordinal,
                demo_path_step=entry.demo_path_step,
                flow_step=entry.flow_step,
                name=entry.name,
                launcher_argv=launcher_argv,
                command_argv=entry.command_argv,
                command_line=_shell_join(entry.command_argv),
                engine_actions=entry.engine_actions,
                action_lines=tuple(
                    (engine_action, _shell_join(action_argv))
                    for engine_action, action_argv in entry.action_command_argv
                ),
            )
            for entry in readiness_contract.entries
        ),
    )
    _validate_command_demo_execution_plan_contract(contract, readiness_contract, launcher_argv)
    return contract


def _validate_command_demo_execution_plan_contract(
    contract: CommandDemoExecutionPlanContract,
    readiness_contract: CommandDemoReadinessContract,
    launcher_argv: tuple[str, ...],
) -> None:
    _validate_command_smoke_cli_launcher(launcher_argv)
    if contract.launcher_argv != launcher_argv:
        raise ValueError("Command demo execution plan launcher is inconsistent")
    if tuple(step.ordinal for step in contract.steps) != tuple(
        entry.ordinal for entry in readiness_contract.entries
    ):
        raise ValueError("Command demo execution plan ordinals are inconsistent")
    if tuple(step.demo_path_step for step in contract.steps) != tuple(
        entry.demo_path_step for entry in readiness_contract.entries
    ):
        raise ValueError("Command demo execution plan path steps are inconsistent")
    if tuple(step.flow_step for step in contract.steps) != tuple(
        entry.flow_step for entry in readiness_contract.entries
    ):
        raise ValueError("Command demo execution plan flow steps are inconsistent")
    if tuple(step.name for step in contract.steps) != tuple(
        entry.name for entry in readiness_contract.entries
    ):
        raise ValueError("Command demo execution plan command names are inconsistent")

    for step, entry in zip(contract.steps, readiness_contract.entries, strict=True):
        if step.launcher_argv != launcher_argv:
            raise ValueError(f"Command demo execution plan step launcher is inconsistent: {step.flow_step}")
        if step.command_argv != entry.command_argv:
            raise ValueError(f"Command demo execution plan argv is inconsistent: {step.flow_step}")
        if step.command_argv[: len(launcher_argv)] != launcher_argv:
            raise ValueError(f"Command demo execution plan argv launcher is inconsistent: {step.flow_step}")
        if step.command_line != _shell_join(entry.command_argv):
            raise ValueError(f"Command demo execution plan command line is inconsistent: {step.flow_step}")
        if step.engine_actions != entry.engine_actions:
            raise ValueError(f"Command demo execution plan actions are inconsistent: {step.flow_step}")
        expected_action_lines = tuple(
            (engine_action, _shell_join(action_argv))
            for engine_action, action_argv in entry.action_command_argv
        )
        if step.action_lines != expected_action_lines:
            raise ValueError(f"Command demo execution plan action lines are inconsistent: {step.flow_step}")
        if not step.command_line or not step.action_lines:
            raise ValueError(f"Command demo execution plan step must be smoke-testable: {step.flow_step}")


def command_demo_execution_plan_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    tuple[int, str, str, str, tuple[str, ...], tuple[str, ...], str, tuple[str, ...], tuple[tuple[str, str], ...]],
    ...,
]:
    return tuple(
        (
            step.ordinal,
            step.demo_path_step,
            step.flow_step,
            step.name,
            step.launcher_argv,
            step.command_argv,
            step.command_line,
            step.engine_actions,
            step.action_lines,
        )
        for step in command_demo_execution_plan_contract(specs, launcher_argv).steps
    )


def command_demo_execution_plan_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return tuple(
        (step.flow_step, step.command_argv)
        for step in command_demo_execution_plan_contract(specs, launcher_argv).steps
    )


@lru_cache(maxsize=None)
def command_demo_action_coverage_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoActionCoverageContract:
    execution_plan = command_demo_execution_plan_contract(specs, launcher_argv)
    contract = CommandDemoActionCoverageContract(
        entries=tuple(
            CommandDemoActionCoverageEntry(
                engine_action=engine_action,
                demo_path_step=step.demo_path_step,
                flow_step=step.flow_step,
                name=step.name,
                command_argv=step.command_argv,
                command_line=step.command_line,
                action_line=action_line,
            )
            for step in execution_plan.steps
            for engine_action, fallback_action_line in step.action_lines
            for action_line in (
                _command_demo_action_coverage_line(
                    engine_action,
                    fallback_action_line,
                    specs,
                    launcher_argv,
                ),
            )
        )
    )
    _validate_command_demo_action_coverage_contract(contract, execution_plan, specs)
    return contract


def _command_demo_action_coverage_line(
    engine_action: str,
    fallback_action_line: str,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> str:
    try:
        exact_line = command_demo_readiness_exact_line_for_engine_action(
            engine_action,
            specs,
            launcher_argv,
        )
    except ValueError:
        exact_line = ""
    return exact_line or fallback_action_line


def _validate_command_demo_action_coverage_contract(
    contract: CommandDemoActionCoverageContract,
    execution_plan: CommandDemoExecutionPlanContract,
    specs: tuple[CommandSpec, ...],
) -> None:
    expected_actions = command_demo_engine_actions(specs)
    if tuple(entry.engine_action for entry in contract.entries) != expected_actions:
        raise ValueError("Command demo action coverage actions are inconsistent")

    entries_by_action = {entry.engine_action: entry for entry in contract.entries}
    for step in execution_plan.steps:
        for engine_action, fallback_action_line in step.action_lines:
            entry = entries_by_action.get(engine_action)
            if entry is None:
                raise ValueError(f"Command demo action coverage is missing: {engine_action}")
            action_line = _command_demo_action_coverage_line(
                engine_action,
                fallback_action_line,
                specs,
                execution_plan.launcher_argv,
            )
            if entry.demo_path_step != step.demo_path_step:
                raise ValueError(f"Command demo action coverage path step is inconsistent: {engine_action}")
            if entry.flow_step != step.flow_step:
                raise ValueError(f"Command demo action coverage flow step is inconsistent: {engine_action}")
            if entry.name != step.name:
                raise ValueError(f"Command demo action coverage command name is inconsistent: {engine_action}")
            if entry.command_argv != step.command_argv:
                raise ValueError(f"Command demo action coverage argv is inconsistent: {engine_action}")
            if entry.command_line != step.command_line:
                raise ValueError(f"Command demo action coverage command line is inconsistent: {engine_action}")
            if entry.action_line != action_line:
                raise ValueError(f"Command demo action coverage action line is inconsistent: {engine_action}")
            if not entry.command_line or not entry.action_line:
                raise ValueError(f"Command demo action coverage line must not be empty: {engine_action}")
            resolved_action = command_demo_readiness_exact_action_for_argv(
                entry.action_line,
                specs,
                execution_plan.launcher_argv,
            )
            if resolved_action != engine_action:
                raise ValueError(f"Command demo action coverage exact route is inconsistent: {engine_action}")

    action_lines = tuple(entry.action_line for entry in contract.entries)
    if len(set(action_lines)) != len(action_lines):
        raise ValueError("Command demo action coverage lines must be exact and unique")


def command_demo_action_coverage_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, str, str, str], ...]:
    return tuple(
        (
            entry.engine_action,
            entry.demo_path_step,
            entry.flow_step,
            entry.name,
            entry.command_line,
            entry.action_line,
        )
        for entry in command_demo_action_coverage_contract(specs, launcher_argv).entries
    )


def command_demo_action_coverage_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (entry.engine_action, entry.action_line)
        for entry in command_demo_action_coverage_contract(specs, launcher_argv).entries
    )


@lru_cache(maxsize=None)
def _command_demo_action_coverage_entry(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    engine_action: str,
) -> CommandDemoActionCoverageEntry | None:
    requested_action = engine_action.strip()
    if not requested_action:
        return None
    return next(
        (
            entry
            for entry in command_demo_action_coverage_contract(specs, launcher_argv).entries
            if entry.engine_action == requested_action
        ),
        None,
    )


def command_demo_action_coverage_entry(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoActionCoverageEntry | None:
    return _command_demo_action_coverage_entry(specs, launcher_argv, engine_action)


@lru_cache(maxsize=None)
def _command_demo_execution_plan_step_for_flow_step(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    flow_step: str,
) -> CommandDemoExecutionPlanStep | None:
    requested_flow_step = _normalize_token(flow_step)
    if not requested_flow_step:
        return None
    return next(
        (
            step
            for step in command_demo_execution_plan_contract(specs, launcher_argv).steps
            if step.flow_step == requested_flow_step
        ),
        None,
    )


def command_demo_execution_plan_step_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoExecutionPlanStep | None:
    return _command_demo_execution_plan_step_for_flow_step(specs, launcher_argv, flow_step)


@lru_cache(maxsize=None)
def _command_demo_execution_plan_step_for_demo_path_step(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    demo_path_step: str,
) -> CommandDemoExecutionPlanStep | None:
    requested_demo_path_step = _normalize_token(demo_path_step)
    if not requested_demo_path_step:
        return None
    return next(
        (
            step
            for step in command_demo_execution_plan_contract(specs, launcher_argv).steps
            if _normalize_token(step.demo_path_step) == requested_demo_path_step
        ),
        None,
    )


def command_demo_execution_plan_step_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoExecutionPlanStep | None:
    return _command_demo_execution_plan_step_for_demo_path_step(
        specs,
        launcher_argv,
        demo_path_step,
    )


@lru_cache(maxsize=None)
def _command_demo_execution_plan_step_for_command(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    command_name: str,
) -> CommandDemoExecutionPlanStep | None:
    requested_command = canonical_command_for(specs, command_name)
    if not requested_command:
        return None
    return next(
        (
            step
            for step in command_demo_execution_plan_contract(specs, launcher_argv).steps
            if step.name == requested_command
        ),
        None,
    )


def command_demo_execution_plan_step_for_command(
    command_name: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoExecutionPlanStep | None:
    return _command_demo_execution_plan_step_for_command(specs, launcher_argv, command_name)


@lru_cache(maxsize=None)
def _command_demo_execution_plan_step_for_engine_action(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    engine_action: str,
) -> CommandDemoExecutionPlanStep | None:
    requested_engine_action = engine_action.strip()
    if not requested_engine_action:
        return None
    return next(
        (
            step
            for step in command_demo_execution_plan_contract(specs, launcher_argv).steps
            if requested_engine_action in step.engine_actions
        ),
        None,
    )


def command_demo_execution_plan_step_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoExecutionPlanStep | None:
    return _command_demo_execution_plan_step_for_engine_action(specs, launcher_argv, engine_action)


def command_demo_execution_plan_step_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoExecutionPlanStep | None:
    readiness_entry = command_demo_readiness_entry_for_argv(argv, specs, launcher_argv)
    if readiness_entry is None:
        return None
    return command_demo_execution_plan_step_for_flow_step(
        readiness_entry.flow_step,
        specs,
        launcher_argv,
    )


def command_mvp_demo_execution_plan_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoExecutionPlanContract:
    return command_demo_execution_plan_contract(specs, launcher_argv)


def command_mvp_demo_execution_plan_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    tuple[int, str, str, str, tuple[str, ...], tuple[str, ...], str, tuple[str, ...], tuple[tuple[str, str], ...]],
    ...,
]:
    return command_demo_execution_plan_summary(specs, launcher_argv)


def command_mvp_demo_execution_plan_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_execution_plan_lookup_table(specs, launcher_argv)


def command_mvp_demo_action_coverage_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoActionCoverageContract:
    return command_demo_action_coverage_contract(specs, launcher_argv)


def command_mvp_demo_action_coverage_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, str, str, str], ...]:
    return command_demo_action_coverage_summary(specs, launcher_argv)


def command_mvp_demo_action_coverage_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return command_demo_action_coverage_lookup_table(specs, launcher_argv)


def command_mvp_demo_action_coverage_entry(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoActionCoverageEntry | None:
    return command_demo_action_coverage_entry(engine_action, specs, launcher_argv)


def command_mvp_demo_execution_plan_step_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoExecutionPlanStep | None:
    return command_demo_execution_plan_step_for_flow_step(flow_step, specs, launcher_argv)


def command_mvp_demo_execution_plan_step_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoExecutionPlanStep | None:
    return command_demo_execution_plan_step_for_demo_path_step(demo_path_step, specs, launcher_argv)


def command_mvp_demo_execution_plan_step_for_command(
    command_name: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoExecutionPlanStep | None:
    return command_demo_execution_plan_step_for_command(command_name, specs, launcher_argv)


def command_mvp_demo_execution_plan_step_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoExecutionPlanStep | None:
    return command_demo_execution_plan_step_for_engine_action(engine_action, specs, launcher_argv)


def command_mvp_demo_execution_plan_step_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoExecutionPlanStep | None:
    return command_demo_execution_plan_step_for_argv(argv, specs, launcher_argv)


def command_demo_readiness_handoff_markdown(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return "\n".join(command_demo_readiness_handoff_checklist_lines(specs, launcher_argv))


@lru_cache(maxsize=None)
def command_demo_readiness_gate(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessGate:
    missing_engine_actions = command_demo_readiness_missing_engine_actions(specs, launcher_argv)
    smoke_plan = command_demo_readiness_smoke_plan(specs, launcher_argv)
    exact_action_lines = command_demo_readiness_exact_action_line_lookup_table(specs, launcher_argv)
    covered_flow_steps = tuple(step.flow_step for step in smoke_plan.steps)
    expected_flow_steps = _expected_command_demo_flow_steps(specs)
    cli_validation = command_demo_readiness_validate_cli_script(
        tuple(step.command_line for step in smoke_plan.steps),
        specs,
        launcher_argv,
    )
    cli_exact_action_validation = command_demo_readiness_validate_cli_exact_action_script(
        tuple(line for _, line in exact_action_lines),
        specs,
        launcher_argv,
    )
    missing_flow_steps = tuple(
        flow_step
        for flow_step in expected_flow_steps
        if flow_step not in covered_flow_steps
    )
    invalid_cli_argv = cli_validation.invalid_argv
    invalid_cli_exact_action_argv = cli_exact_action_validation.invalid_argv
    gate = CommandDemoReadinessGate(
        is_complete=(
            not missing_engine_actions
            and not missing_flow_steps
            and not invalid_cli_argv
            and not invalid_cli_exact_action_argv
        ),
        missing_engine_actions=missing_engine_actions,
        command_lines=tuple(step.command_line for step in smoke_plan.steps),
        action_lines=exact_action_lines,
        covered_flow_steps=covered_flow_steps,
        missing_flow_steps=missing_flow_steps,
        cli_command_lines=cli_validation.command_lines,
        cli_exact_action_lines=cli_exact_action_validation.command_lines,
        invalid_cli_argv=invalid_cli_argv,
        invalid_cli_exact_action_argv=invalid_cli_exact_action_argv,
    )
    _validate_command_demo_readiness_gate(
        gate,
        smoke_plan,
        specs=specs,
        launcher_argv=launcher_argv,
    )
    return gate


def _validate_command_demo_readiness_gate(
    gate: CommandDemoReadinessGate,
    smoke_plan: CommandDemoReadinessSmokePlan,
    *,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    expected_command_lines = tuple(step.command_line for step in smoke_plan.steps)
    expected_action_lines = command_demo_readiness_exact_action_line_lookup_table(specs, launcher_argv)
    cli_validation = command_demo_readiness_validate_cli_script(
        expected_command_lines,
        specs,
        launcher_argv,
    )
    cli_exact_action_validation = command_demo_readiness_validate_cli_exact_action_script(
        tuple(line for _, line in expected_action_lines),
        specs,
        launcher_argv,
    )
    if gate.command_lines != expected_command_lines:
        raise ValueError("Command demo readiness gate command lines are inconsistent")
    if gate.action_lines != expected_action_lines:
        raise ValueError("Command demo readiness gate action lines are inconsistent")
    if gate.cli_command_lines != cli_validation.command_lines:
        raise ValueError("Command demo readiness gate CLI command lines are inconsistent")
    if gate.cli_exact_action_lines != cli_exact_action_validation.command_lines:
        raise ValueError("Command demo readiness gate CLI exact action lines are inconsistent")
    if gate.invalid_cli_argv != cli_validation.invalid_argv:
        raise ValueError("Command demo readiness gate invalid CLI argv are inconsistent")
    if gate.invalid_cli_exact_action_argv != cli_exact_action_validation.invalid_argv:
        raise ValueError("Command demo readiness gate invalid CLI exact action argv are inconsistent")
    if gate.invalid_cli_argv:
        raise ValueError("Command demo readiness gate includes unsupported CLI argv")
    if gate.invalid_cli_exact_action_argv:
        raise ValueError("Command demo readiness gate includes unsupported CLI exact action argv")
    if gate.covered_flow_steps != tuple(step.flow_step for step in smoke_plan.steps):
        raise ValueError("Command demo readiness gate flow coverage is inconsistent")
    expected_flow_steps = _expected_command_demo_flow_steps(specs)
    if gate.missing_flow_steps != tuple(
        flow_step
        for flow_step in expected_flow_steps
        if flow_step not in gate.covered_flow_steps
    ):
        raise ValueError("Command demo readiness gate missing flow steps are inconsistent")
    if tuple(engine_action for engine_action, _ in gate.action_lines) != command_demo_engine_actions(specs):
        raise ValueError("Command demo readiness gate action coverage is inconsistent")
    for engine_action, action_line in gate.action_lines:
        exact_action = command_demo_readiness_exact_action_for_argv(action_line, specs, launcher_argv)
        if exact_action != engine_action:
            raise ValueError(f"Command demo readiness gate exact action is inconsistent: {engine_action}")
    if gate.is_complete != (
        not gate.missing_engine_actions
        and not gate.missing_flow_steps
        and not gate.invalid_cli_argv
        and not gate.invalid_cli_exact_action_argv
    ):
        raise ValueError("Command demo readiness gate completeness is inconsistent")


def command_demo_readiness_gate_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[bool, tuple[str, ...], tuple[str, ...], tuple[tuple[str, str], ...]]:
    gate = command_demo_readiness_gate(specs, launcher_argv)
    return (
        gate.is_complete,
        gate.missing_engine_actions,
        gate.command_lines,
        gate.action_lines,
    )


def command_demo_readiness_flow_gate_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[bool, tuple[str, ...], tuple[str, ...]]:
    gate = command_demo_readiness_gate(specs, launcher_argv)
    return (
        gate.is_complete,
        gate.covered_flow_steps,
        gate.missing_flow_steps,
    )


def command_demo_readiness_gate_issues(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return _command_demo_readiness_gate_issues(command_demo_readiness_gate(specs, launcher_argv))


def _command_demo_readiness_gate_issues(gate: CommandDemoReadinessGate) -> tuple[str, ...]:
    issues: list[str] = []
    if gate.missing_engine_actions:
        issues.append(f"engine actions: {', '.join(gate.missing_engine_actions)}")
    if gate.missing_flow_steps:
        issues.append(f"flow steps: {', '.join(gate.missing_flow_steps)}")
    if gate.invalid_cli_argv:
        invalid_lines = ", ".join(_shell_join(argv) for argv in gate.invalid_cli_argv)
        issues.append(f"invalid CLI argv: {invalid_lines}")
    if gate.invalid_cli_exact_action_argv:
        invalid_lines = ", ".join(_shell_join(argv) for argv in gate.invalid_cli_exact_action_argv)
        issues.append(f"invalid CLI exact action argv: {invalid_lines}")
    return tuple(issues)


def require_command_demo_readiness_complete(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessGate:
    gate = command_demo_readiness_gate(specs, launcher_argv)
    if not gate.is_complete:
        missing = "; ".join(_command_demo_readiness_gate_issues(gate))
        raise ValueError(f"Command demo readiness is incomplete: {missing}")
    return gate


@lru_cache(maxsize=None)
def command_demo_readiness_report(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessReport:
    gate = command_demo_readiness_gate(specs, launcher_argv)
    checklist_lines = command_demo_readiness_handoff_checklist_lines(specs, launcher_argv)
    report = CommandDemoReadinessReport(
        is_complete=gate.is_complete,
        missing_engine_actions=gate.missing_engine_actions,
        command_lines=gate.command_lines,
        action_lines=gate.action_lines,
        checklist_lines=checklist_lines,
        markdown="\n".join(checklist_lines),
    )
    _validate_command_demo_readiness_report(report, gate, checklist_lines)
    return report


def _validate_command_demo_readiness_report(
    report: CommandDemoReadinessReport,
    gate: CommandDemoReadinessGate,
    checklist_lines: tuple[str, ...],
) -> None:
    if report.is_complete != gate.is_complete:
        raise ValueError("Command demo readiness report completeness is inconsistent")
    if report.missing_engine_actions != gate.missing_engine_actions:
        raise ValueError("Command demo readiness report missing actions are inconsistent")
    if report.command_lines != gate.command_lines:
        raise ValueError("Command demo readiness report command lines are inconsistent")
    if report.action_lines != gate.action_lines:
        raise ValueError("Command demo readiness report action lines are inconsistent")
    if report.checklist_lines != checklist_lines:
        raise ValueError("Command demo readiness report checklist lines are inconsistent")
    if report.markdown != "\n".join(checklist_lines):
        raise ValueError("Command demo readiness report markdown is inconsistent")


def command_demo_readiness_report_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[bool, tuple[str, ...], tuple[str, ...], tuple[tuple[str, str], ...], tuple[str, ...], str]:
    report = command_demo_readiness_report(specs, launcher_argv)
    return (
        report.is_complete,
        report.missing_engine_actions,
        report.command_lines,
        report.action_lines,
        report.checklist_lines,
        report.markdown,
    )


@lru_cache(maxsize=None)
def command_demo_readiness_handoff_packet(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessHandoffPacket:
    seal = command_demo_readiness_seal(specs, launcher_argv)
    fingerprint = command_demo_readiness_fingerprint(specs, launcher_argv)
    checklist_lines = command_demo_readiness_handoff_checklist_lines(specs, launcher_argv)
    action_steps = command_demo_readiness_handoff_action_contract(specs, launcher_argv).steps
    step_seals = command_demo_readiness_step_seal_contract(specs, launcher_argv).steps
    cli_step_validations = command_demo_readiness_cli_step_validation_contract(specs, launcher_argv).steps
    packet = CommandDemoReadinessHandoffPacket(
        scope_completed=(
            "CLI compatibility and migration-safe entrypoints for the engine-first "
            "open, retrieval, patch-review, and persist demo loop."
        ),
        roadmap_items=(
            "Milestone 3: Real workflow loop",
            "feat-commands: CLI compatibility and migration-safe entrypoints",
        ),
        vision_capabilities=(
            "Required capability 1: Writing-centered workflow",
            "Required capability 2: Retrieval-first context handling",
            "Required capability 3: Canonical engine contract",
            "Required capability 6: Auditable state and workflow",
        ),
        routing_provider_impact="None: command readiness metadata does not touch model routing or providers.",
        fingerprint_algorithm=fingerprint.algorithm,
        fingerprint_digest=fingerprint.digest,
        canonical_demo_path_steps=tuple(
            step.demo_path_step
            for step in command_demo_path_readiness_contract(specs, launcher_argv).steps
        ),
        command_lines=seal.command_lines,
        exact_action_lines=seal.exact_action_lines,
        checklist_lines=checklist_lines,
        is_complete=seal.is_complete,
        missing_flow_steps=seal.missing_flow_steps,
        missing_engine_actions=seal.missing_engine_actions,
        invalid_argv=seal.invalid_argv,
        action_steps=action_steps,
        cli_exact_action_lines=seal.cli_exact_action_lines,
        step_seals=step_seals,
        cli_step_validations=cli_step_validations,
    )
    _validate_command_demo_readiness_handoff_packet(
        packet,
        seal,
        fingerprint,
        checklist_lines,
        action_steps,
        step_seals,
        cli_step_validations,
        specs,
        launcher_argv,
    )
    return packet


def _validate_command_demo_readiness_handoff_packet(
    packet: CommandDemoReadinessHandoffPacket,
    seal: CommandDemoReadinessSeal,
    fingerprint: CommandDemoReadinessFingerprint,
    checklist_lines: tuple[str, ...],
    action_steps: tuple[CommandDemoReadinessHandoffActionStep, ...],
    step_seals: tuple[CommandDemoReadinessStepSeal, ...],
    cli_step_validations: tuple[CommandDemoReadinessCliStepValidation, ...],
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    if not packet.scope_completed.strip():
        raise ValueError("Command demo readiness handoff packet scope must not be empty")
    if not packet.roadmap_items:
        raise ValueError("Command demo readiness handoff packet roadmap items must not be empty")
    if not packet.vision_capabilities:
        raise ValueError("Command demo readiness handoff packet vision capabilities must not be empty")
    if not packet.routing_provider_impact.strip():
        raise ValueError("Command demo readiness handoff packet provider impact must not be empty")
    if packet.fingerprint_algorithm != fingerprint.algorithm:
        raise ValueError("Command demo readiness handoff packet fingerprint algorithm is inconsistent")
    if packet.fingerprint_digest != fingerprint.digest:
        raise ValueError("Command demo readiness handoff packet fingerprint digest is inconsistent")
    expected_demo_steps = tuple(
        step.demo_path_step
        for step in command_demo_path_readiness_contract(specs, launcher_argv).steps
    )
    if packet.canonical_demo_path_steps != expected_demo_steps:
        raise ValueError("Command demo readiness handoff packet demo path steps are inconsistent")
    if packet.command_lines != seal.command_lines:
        raise ValueError("Command demo readiness handoff packet command lines are inconsistent")
    if packet.exact_action_lines != seal.exact_action_lines:
        raise ValueError("Command demo readiness handoff packet exact action lines are inconsistent")
    if packet.cli_exact_action_lines != seal.cli_exact_action_lines:
        raise ValueError("Command demo readiness handoff packet CLI exact action lines are inconsistent")
    if packet.checklist_lines != checklist_lines:
        raise ValueError("Command demo readiness handoff packet checklist lines are inconsistent")
    if packet.is_complete != seal.is_complete:
        raise ValueError("Command demo readiness handoff packet completeness is inconsistent")
    if packet.missing_flow_steps != seal.missing_flow_steps:
        raise ValueError("Command demo readiness handoff packet missing flow steps are inconsistent")
    if packet.missing_engine_actions != seal.missing_engine_actions:
        raise ValueError("Command demo readiness handoff packet missing actions are inconsistent")
    if packet.invalid_argv != seal.invalid_argv:
        raise ValueError("Command demo readiness handoff packet invalid argv are inconsistent")
    if packet.action_steps != action_steps:
        raise ValueError("Command demo readiness handoff packet action steps are inconsistent")
    if packet.step_seals != step_seals:
        raise ValueError("Command demo readiness handoff packet step seals are inconsistent")
    if packet.cli_step_validations != cli_step_validations:
        raise ValueError("Command demo readiness handoff packet CLI step validations are inconsistent")
    if tuple(step.command_line for step in packet.action_steps) != packet.command_lines:
        raise ValueError("Command demo readiness handoff packet action step commands are inconsistent")
    if tuple(step.command_line for step in packet.step_seals) != packet.command_lines:
        raise ValueError("Command demo readiness handoff packet step seal commands are inconsistent")
    if tuple(step.command_line for step in packet.cli_step_validations) != packet.command_lines:
        raise ValueError("Command demo readiness handoff packet CLI step validation commands are inconsistent")
    if any(not step.is_cli_entrypoint for step in packet.cli_step_validations):
        raise ValueError("Command demo readiness handoff packet includes unsupported CLI step")
    if tuple(
        line
        for step in packet.action_steps
        for _, line in step.exact_action_lines
    ) != packet.exact_action_lines:
        raise ValueError("Command demo readiness handoff packet action step exact lines are inconsistent")
    if tuple(
        line
        for step in packet.step_seals
        for _, line in step.exact_action_lines
    ) != packet.exact_action_lines:
        raise ValueError("Command demo readiness handoff packet step seal exact lines are inconsistent")


def _command_demo_readiness_handoff_packet_payload(
    packet: CommandDemoReadinessHandoffPacket,
) -> dict[str, object]:
    return {
        "scope_completed": packet.scope_completed,
        "roadmap_items": list(packet.roadmap_items),
        "vision_capabilities": list(packet.vision_capabilities),
        "routing_provider_impact": packet.routing_provider_impact,
        "fingerprint": {
            "algorithm": packet.fingerprint_algorithm,
            "digest": packet.fingerprint_digest,
        },
        "canonical_demo_path_steps": list(packet.canonical_demo_path_steps),
        "command_lines": list(packet.command_lines),
        "exact_action_lines": list(packet.exact_action_lines),
        "cli_exact_action_lines": list(packet.cli_exact_action_lines),
        "checklist_lines": list(packet.checklist_lines),
        "is_complete": packet.is_complete,
        "missing_flow_steps": list(packet.missing_flow_steps),
        "missing_engine_actions": list(packet.missing_engine_actions),
        "invalid_argv": [list(argv) for argv in packet.invalid_argv],
        "action_steps": [
            {
                "ordinal": step.ordinal,
                "demo_path_step": step.demo_path_step,
                "flow_step": step.flow_step,
                "name": step.name,
                "command_line": step.command_line,
                "exact_action_lines": [
                    {
                        "engine_action": engine_action,
                        "command_line": command_line,
                    }
                    for engine_action, command_line in step.exact_action_lines
                ],
            }
            for step in packet.action_steps
        ],
        "step_seals": [
            {
                "ordinal": step.ordinal,
                "demo_path_step": step.demo_path_step,
                "flow_step": step.flow_step,
                "name": step.name,
                "command_argv": list(step.command_argv),
                "command_line": step.command_line,
                "engine_actions": list(step.engine_actions),
                "exact_action_lines": [
                    {
                        "engine_action": engine_action,
                        "command_line": command_line,
                    }
                    for engine_action, command_line in step.exact_action_lines
                ],
            }
            for step in packet.step_seals
        ],
        "cli_step_validations": [
            {
                "ordinal": step.ordinal,
                "demo_path_step": step.demo_path_step,
                "flow_step": step.flow_step,
                "name": step.name,
                "command_line": step.command_line,
                "parser_token": step.parser_token,
                "canonical_command_line": step.canonical_command_line,
                "is_cli_entrypoint": step.is_cli_entrypoint,
            }
            for step in packet.cli_step_validations
        ],
    }


def _validate_command_demo_readiness_handoff_packet_payload(
    payload: dict[str, object],
    packet: CommandDemoReadinessHandoffPacket,
) -> None:
    if payload != _command_demo_readiness_handoff_packet_payload(packet):
        raise ValueError("Command demo readiness handoff packet payload is inconsistent")
    json.dumps(payload, sort_keys=True, separators=(",", ":"))


def command_demo_readiness_handoff_packet_payload(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> dict[str, object]:
    packet = command_demo_readiness_handoff_packet(specs, launcher_argv)
    payload = _command_demo_readiness_handoff_packet_payload(packet)
    _validate_command_demo_readiness_handoff_packet_payload(payload, packet)
    return payload


def command_demo_readiness_handoff_packet_json(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return json.dumps(
        command_demo_readiness_handoff_packet_payload(specs, launcher_argv),
        sort_keys=True,
        separators=(",", ":"),
    )


@lru_cache(maxsize=None)
def command_demo_surface_readiness_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoSurfaceReadinessContract:
    packet = command_demo_readiness_handoff_packet(specs, launcher_argv)
    routes_by_flow_step = {
        entry.flow_step: entry
        for entry in command_demo_readiness_route_contract(specs, launcher_argv).entries
    }
    contract = CommandDemoSurfaceReadinessContract(
        launcher_argv=launcher_argv,
        fingerprint_algorithm=packet.fingerprint_algorithm,
        fingerprint_digest=packet.fingerprint_digest,
        is_complete=packet.is_complete,
        entries=tuple(
            CommandDemoSurfaceReadinessEntry(
                ordinal=step.ordinal,
                demo_path_step=step.demo_path_step,
                flow_step=step.flow_step,
                name=step.name,
                cli_tokens=routes_by_flow_step[step.flow_step].cli_tokens,
                command_argv=step.command_argv,
                command_line=step.command_line,
                engine_actions=step.engine_actions,
                exact_action_lines=step.exact_action_lines,
            )
            for step in packet.step_seals
        ),
    )
    _validate_command_demo_surface_readiness_contract(
        contract,
        packet,
        routes_by_flow_step,
        launcher_argv,
    )
    return contract


def _validate_command_demo_surface_readiness_contract(
    contract: CommandDemoSurfaceReadinessContract,
    packet: CommandDemoReadinessHandoffPacket,
    routes_by_flow_step: dict[str, CommandDemoReadinessRouteEntry],
    launcher_argv: tuple[str, ...],
) -> None:
    if contract.launcher_argv != launcher_argv:
        raise ValueError("Command demo surface readiness launcher is inconsistent")
    if contract.fingerprint_algorithm != packet.fingerprint_algorithm:
        raise ValueError("Command demo surface readiness fingerprint algorithm is inconsistent")
    if contract.fingerprint_digest != packet.fingerprint_digest:
        raise ValueError("Command demo surface readiness fingerprint digest is inconsistent")
    if contract.is_complete != packet.is_complete:
        raise ValueError("Command demo surface readiness completeness is inconsistent")
    if tuple(entry.command_line for entry in contract.entries) != packet.command_lines:
        raise ValueError("Command demo surface readiness command lines are inconsistent")
    if tuple(entry.demo_path_step for entry in contract.entries) != packet.canonical_demo_path_steps:
        raise ValueError("Command demo surface readiness path steps are inconsistent")
    if tuple(
        line
        for entry in contract.entries
        for _, line in entry.exact_action_lines
    ) != packet.exact_action_lines:
        raise ValueError("Command demo surface readiness exact action lines are inconsistent")

    seen_flow_steps: set[str] = set()
    for entry in contract.entries:
        if entry.flow_step in seen_flow_steps:
            raise ValueError(f"Duplicate command demo surface readiness flow step: {entry.flow_step}")
        seen_flow_steps.add(entry.flow_step)
        route = routes_by_flow_step.get(entry.flow_step)
        if route is None:
            raise ValueError(f"Command demo surface readiness route is missing: {entry.flow_step}")
        if entry.name != route.name:
            raise ValueError(f"Command demo surface readiness command is inconsistent: {entry.flow_step}")
        if entry.cli_tokens != route.cli_tokens:
            raise ValueError(f"Command demo surface readiness CLI tokens are inconsistent: {entry.flow_step}")
        if not entry.cli_tokens or not entry.command_line or not entry.exact_action_lines:
            raise ValueError(f"Command demo surface readiness entry is not smoke-testable: {entry.flow_step}")
        for engine_action, command_line in entry.exact_action_lines:
            if not engine_action or not command_line:
                raise ValueError(f"Command demo surface readiness exact action is empty: {entry.flow_step}")
            resolved_action = command_demo_readiness_exact_action_for_argv(
                command_line,
                specs,
                launcher_argv=launcher_argv,
            )
            if resolved_action != engine_action:
                raise ValueError(
                    f"Command demo surface readiness exact action does not round-trip: {entry.flow_step}"
                )


def command_demo_surface_readiness_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    tuple[int, str, str, str, tuple[str, ...], str, tuple[str, ...], tuple[tuple[str, str], ...]],
    ...,
]:
    return tuple(
        (
            entry.ordinal,
            entry.demo_path_step,
            entry.flow_step,
            entry.name,
            entry.cli_tokens,
            entry.command_line,
            entry.engine_actions,
            entry.exact_action_lines,
        )
        for entry in command_demo_surface_readiness_contract(specs, launcher_argv).entries
    )


def command_demo_surface_readiness_payload(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> dict[str, object]:
    contract = command_demo_surface_readiness_contract(specs, launcher_argv)
    payload: dict[str, object] = {
        "launcher_argv": list(contract.launcher_argv),
        "fingerprint": {
            "algorithm": contract.fingerprint_algorithm,
            "digest": contract.fingerprint_digest,
        },
        "is_complete": contract.is_complete,
        "entries": [
            {
                "ordinal": entry.ordinal,
                "demo_path_step": entry.demo_path_step,
                "flow_step": entry.flow_step,
                "name": entry.name,
                "cli_tokens": list(entry.cli_tokens),
                "command_argv": list(entry.command_argv),
                "command_line": entry.command_line,
                "engine_actions": list(entry.engine_actions),
                "exact_action_lines": [
                    {
                        "engine_action": engine_action,
                        "command_line": command_line,
                    }
                    for engine_action, command_line in entry.exact_action_lines
                ],
            }
            for entry in contract.entries
        ],
    }
    json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return payload


def command_demo_surface_readiness_json(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return json.dumps(
        command_demo_surface_readiness_payload(specs, launcher_argv),
        sort_keys=True,
        separators=(",", ":"),
    )


def command_demo_readiness_handoff_packet_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    str,
    tuple[str, ...],
    tuple[str, ...],
    str,
    str,
    str,
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    bool,
    tuple[str, ...],
    tuple[str, ...],
    tuple[tuple[str, ...], ...],
]:
    packet = command_demo_readiness_handoff_packet(specs, launcher_argv)
    return (
        packet.scope_completed,
        packet.roadmap_items,
        packet.vision_capabilities,
        packet.routing_provider_impact,
        packet.fingerprint_algorithm,
        packet.fingerprint_digest,
        packet.canonical_demo_path_steps,
        packet.command_lines,
        packet.exact_action_lines,
        packet.checklist_lines,
        packet.is_complete,
        packet.missing_flow_steps,
        packet.missing_engine_actions,
        packet.invalid_argv,
    )


def command_demo_readiness_handoff_packet_markdown(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    packet = command_demo_readiness_handoff_packet(specs, launcher_argv)
    risks = _command_demo_readiness_handoff_packet_risks(packet)
    lines = (
        "## Command Demo Readiness Handoff",
        "",
        f"- Scope completed: {packet.scope_completed}",
        f"- Roadmap item(s) affected: {'; '.join(packet.roadmap_items)}",
        f"- Vision capability affected: {'; '.join(packet.vision_capabilities)}",
        f"- Routing/provider impact: {packet.routing_provider_impact}",
        f"- Readiness complete: {str(packet.is_complete).lower()}",
        f"- Fingerprint: {packet.fingerprint_algorithm}:{packet.fingerprint_digest}",
        f"- Canonical demo-path steps: {'; '.join(packet.canonical_demo_path_steps)}",
        f"- Commands: {'; '.join(packet.command_lines)}",
        f"- Exact engine actions: {'; '.join(packet.exact_action_lines)}",
        f"- Risks/blockers: {'; '.join(risks)}",
        "",
        "### Demo Path Checklist",
        *packet.checklist_lines,
    )
    markdown = "\n".join(lines)
    _validate_command_demo_readiness_handoff_packet_markdown(markdown, packet, risks)
    return markdown


def _command_demo_readiness_handoff_packet_risks(
    packet: CommandDemoReadinessHandoffPacket,
) -> tuple[str, ...]:
    risks: list[str] = []
    if packet.missing_flow_steps:
        risks.append(f"missing flow steps: {', '.join(packet.missing_flow_steps)}")
    if packet.missing_engine_actions:
        risks.append(f"missing engine actions: {', '.join(packet.missing_engine_actions)}")
    if packet.invalid_argv:
        invalid = ", ".join(_shell_join(argv) for argv in packet.invalid_argv)
        risks.append(f"invalid argv: {invalid}")
    if not risks:
        risks.append("None from command readiness metadata.")
    return tuple(risks)


def _validate_command_demo_readiness_handoff_packet_markdown(
    markdown: str,
    packet: CommandDemoReadinessHandoffPacket,
    risks: tuple[str, ...],
) -> None:
    if not markdown.strip():
        raise ValueError("Command demo readiness handoff packet markdown must not be empty")
    required_fragments = (
        packet.scope_completed,
        *packet.roadmap_items,
        *packet.vision_capabilities,
        packet.routing_provider_impact,
        f"{packet.fingerprint_algorithm}:{packet.fingerprint_digest}",
        *packet.canonical_demo_path_steps,
        *packet.command_lines,
        *packet.exact_action_lines,
        *packet.checklist_lines,
        *risks,
    )
    missing_fragments = tuple(fragment for fragment in required_fragments if fragment not in markdown)
    if missing_fragments:
        raise ValueError("Command demo readiness handoff packet markdown is incomplete")
    if "Roadmap item(s) affected" not in markdown or "Vision capability affected" not in markdown:
        raise ValueError("Command demo readiness handoff packet markdown lacks integration fields")


def command_demo_readiness_handoff_status_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    packet = command_demo_readiness_handoff_packet(specs, launcher_argv)
    gate = command_demo_readiness_gate(specs, launcher_argv)
    lines = (
        f"readiness={str(packet.is_complete).lower()}",
        f"fingerprint={packet.fingerprint_algorithm}:{packet.fingerprint_digest}",
        f"demo_path_steps={'; '.join(packet.canonical_demo_path_steps)}",
        f"command_lines={'; '.join(packet.command_lines)}",
        f"cli_command_lines={'; '.join(gate.cli_command_lines)}",
        f"exact_action_lines={'; '.join(packet.exact_action_lines)}",
        f"cli_exact_action_lines={'; '.join(packet.cli_exact_action_lines)}",
        f"missing_flow_steps={'; '.join(packet.missing_flow_steps)}",
        f"missing_engine_actions={'; '.join(packet.missing_engine_actions)}",
        f"invalid_cli_argv={'; '.join(_shell_join(argv) for argv in gate.invalid_cli_argv)}",
        "invalid_cli_exact_action_argv="
        f"{'; '.join(_shell_join(argv) for argv in gate.invalid_cli_exact_action_argv)}",
    )
    _validate_command_demo_readiness_handoff_status_lines(lines, packet, gate)
    return lines


def _validate_command_demo_readiness_handoff_status_lines(
    lines: tuple[str, ...],
    packet: CommandDemoReadinessHandoffPacket,
    gate: CommandDemoReadinessGate,
) -> None:
    if len(lines) != 11 or any(not line.strip() for line in lines):
        raise ValueError("Command demo readiness handoff status lines are incomplete")
    expected_lines = (
        f"readiness={str(packet.is_complete).lower()}",
        f"fingerprint={packet.fingerprint_algorithm}:{packet.fingerprint_digest}",
        f"demo_path_steps={'; '.join(packet.canonical_demo_path_steps)}",
        f"command_lines={'; '.join(packet.command_lines)}",
        f"cli_command_lines={'; '.join(gate.cli_command_lines)}",
        f"exact_action_lines={'; '.join(packet.exact_action_lines)}",
        f"cli_exact_action_lines={'; '.join(packet.cli_exact_action_lines)}",
        f"missing_flow_steps={'; '.join(packet.missing_flow_steps)}",
        f"missing_engine_actions={'; '.join(packet.missing_engine_actions)}",
        f"invalid_cli_argv={'; '.join(_shell_join(argv) for argv in gate.invalid_cli_argv)}",
        "invalid_cli_exact_action_argv="
        f"{'; '.join(_shell_join(argv) for argv in gate.invalid_cli_exact_action_argv)}",
    )
    if lines != expected_lines:
        raise ValueError("Command demo readiness handoff status lines are inconsistent")


@lru_cache(maxsize=None)
def command_demo_readiness_handoff_step_status_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessHandoffStepStatusContract:
    packet = command_demo_readiness_handoff_packet(specs, launcher_argv)
    validations_by_ordinal = {
        validation.ordinal: validation
        for validation in packet.cli_step_validations
    }
    steps = tuple(
        CommandDemoReadinessHandoffStepStatus(
            ordinal=step.ordinal,
            demo_path_step=step.demo_path_step,
            flow_step=step.flow_step,
            name=step.name,
            command_line=step.command_line,
            parser_token=validations_by_ordinal[step.ordinal].parser_token,
            engine_actions=step.engine_actions,
            exact_action_lines=step.exact_action_lines,
            is_cli_entrypoint=validations_by_ordinal[step.ordinal].is_cli_entrypoint,
            is_complete=(
                validations_by_ordinal[step.ordinal].is_cli_entrypoint
                and bool(step.command_line)
                and bool(step.engine_actions)
                and tuple(engine_action for engine_action, _ in step.exact_action_lines)
                == step.engine_actions
            ),
        )
        for step in packet.step_seals
    )
    contract = CommandDemoReadinessHandoffStepStatusContract(
        fingerprint_algorithm=packet.fingerprint_algorithm,
        fingerprint_digest=packet.fingerprint_digest,
        is_complete=packet.is_complete and all(step.is_complete for step in steps),
        steps=steps,
    )
    _validate_command_demo_readiness_handoff_step_status_contract(contract, packet)
    return contract


def _validate_command_demo_readiness_handoff_step_status_contract(
    contract: CommandDemoReadinessHandoffStepStatusContract,
    packet: CommandDemoReadinessHandoffPacket,
) -> None:
    if contract.fingerprint_algorithm != packet.fingerprint_algorithm:
        raise ValueError("Command demo readiness handoff step status fingerprint algorithm is inconsistent")
    if contract.fingerprint_digest != packet.fingerprint_digest:
        raise ValueError("Command demo readiness handoff step status fingerprint digest is inconsistent")
    if tuple(step.ordinal for step in contract.steps) != tuple(step.ordinal for step in packet.step_seals):
        raise ValueError("Command demo readiness handoff step status ordinals are inconsistent")
    if tuple(step.demo_path_step for step in contract.steps) != packet.canonical_demo_path_steps:
        raise ValueError("Command demo readiness handoff step status demo path steps are inconsistent")
    if tuple(step.flow_step for step in contract.steps) != tuple(step.flow_step for step in packet.step_seals):
        raise ValueError("Command demo readiness handoff step status flow steps are inconsistent")
    if tuple(step.name for step in contract.steps) != tuple(step.name for step in packet.step_seals):
        raise ValueError("Command demo readiness handoff step status command names are inconsistent")
    if tuple(step.command_line for step in contract.steps) != packet.command_lines:
        raise ValueError("Command demo readiness handoff step status command lines are inconsistent")
    if tuple(
        line
        for step in contract.steps
        for _, line in step.exact_action_lines
    ) != packet.exact_action_lines:
        raise ValueError("Command demo readiness handoff step status exact action lines are inconsistent")
    validations_by_ordinal = {
        validation.ordinal: validation
        for validation in packet.cli_step_validations
    }
    for step, seal in zip(contract.steps, packet.step_seals, strict=True):
        validation = validations_by_ordinal.get(step.ordinal)
        if validation is None:
            raise ValueError(f"Command demo readiness handoff step status validation is missing: {step.flow_step}")
        if step.parser_token != validation.parser_token:
            raise ValueError(f"Command demo readiness handoff step status parser token is inconsistent: {step.flow_step}")
        if step.engine_actions != seal.engine_actions:
            raise ValueError(f"Command demo readiness handoff step status actions are inconsistent: {step.flow_step}")
        if step.exact_action_lines != seal.exact_action_lines:
            raise ValueError(
                f"Command demo readiness handoff step status exact actions are inconsistent: {step.flow_step}"
            )
        if step.is_cli_entrypoint != validation.is_cli_entrypoint:
            raise ValueError(f"Command demo readiness handoff step status CLI flag is inconsistent: {step.flow_step}")
        expected_complete = (
            step.is_cli_entrypoint
            and bool(step.command_line)
            and bool(step.engine_actions)
            and tuple(engine_action for engine_action, _ in step.exact_action_lines) == step.engine_actions
        )
        if step.is_complete != expected_complete:
            raise ValueError(f"Command demo readiness handoff step status completeness drifted: {step.flow_step}")
    if contract.is_complete != (packet.is_complete and all(step.is_complete for step in contract.steps)):
        raise ValueError("Command demo readiness handoff step status completeness is inconsistent")


def command_demo_readiness_handoff_step_status_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    str,
    str,
    bool,
    tuple[tuple[int, str, str, str, str, str, tuple[str, ...], tuple[tuple[str, str], ...], bool, bool], ...],
]:
    contract = command_demo_readiness_handoff_step_status_contract(specs, launcher_argv)
    return (
        contract.fingerprint_algorithm,
        contract.fingerprint_digest,
        contract.is_complete,
        tuple(
            (
                step.ordinal,
                step.demo_path_step,
                step.flow_step,
                step.name,
                step.command_line,
                step.parser_token,
                step.engine_actions,
                step.exact_action_lines,
                step.is_cli_entrypoint,
                step.is_complete,
            )
            for step in contract.steps
        ),
    )


@lru_cache(maxsize=None)
def command_demo_readiness_command_audit_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessCommandAuditContract:
    step_status = command_demo_readiness_handoff_step_status_contract(specs, launcher_argv)
    entries = tuple(
        CommandDemoReadinessCommandAuditEntry(
            ordinal=step.ordinal,
            flow_step=step.flow_step,
            name=step.name,
            demo_path_step=step.demo_path_step,
            command_line=step.command_line,
            engine_actions=step.engine_actions,
            exact_action_lines=step.exact_action_lines,
            is_cli_entrypoint=step.is_cli_entrypoint,
            is_complete=step.is_complete,
        )
        for step in step_status.steps
    )
    contract = CommandDemoReadinessCommandAuditContract(
        fingerprint_algorithm=step_status.fingerprint_algorithm,
        fingerprint_digest=step_status.fingerprint_digest,
        is_complete=step_status.is_complete and all(entry.is_complete for entry in entries),
        entries=entries,
    )
    _validate_command_demo_readiness_command_audit_contract(contract, step_status)
    return contract


def _validate_command_demo_readiness_command_audit_contract(
    contract: CommandDemoReadinessCommandAuditContract,
    step_status: CommandDemoReadinessHandoffStepStatusContract,
) -> None:
    if contract.fingerprint_algorithm != step_status.fingerprint_algorithm:
        raise ValueError("Command demo readiness command audit fingerprint algorithm is inconsistent")
    if contract.fingerprint_digest != step_status.fingerprint_digest:
        raise ValueError("Command demo readiness command audit fingerprint digest is inconsistent")
    if tuple(entry.ordinal for entry in contract.entries) != tuple(step.ordinal for step in step_status.steps):
        raise ValueError("Command demo readiness command audit ordinals are inconsistent")
    if tuple(entry.flow_step for entry in contract.entries) != tuple(step.flow_step for step in step_status.steps):
        raise ValueError("Command demo readiness command audit flow steps are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(step.name for step in step_status.steps):
        raise ValueError("Command demo readiness command audit names are inconsistent")
    if tuple(entry.demo_path_step for entry in contract.entries) != tuple(
        step.demo_path_step for step in step_status.steps
    ):
        raise ValueError("Command demo readiness command audit demo path steps are inconsistent")
    if tuple(entry.command_line for entry in contract.entries) != tuple(
        step.command_line for step in step_status.steps
    ):
        raise ValueError("Command demo readiness command audit command lines are inconsistent")
    for entry, step in zip(contract.entries, step_status.steps, strict=True):
        if entry.engine_actions != step.engine_actions:
            raise ValueError(f"Command demo readiness command audit actions are inconsistent: {entry.flow_step}")
        if entry.exact_action_lines != step.exact_action_lines:
            raise ValueError(
                f"Command demo readiness command audit exact action lines are inconsistent: {entry.flow_step}"
            )
        if entry.is_cli_entrypoint != step.is_cli_entrypoint:
            raise ValueError(f"Command demo readiness command audit CLI flag is inconsistent: {entry.flow_step}")
        if entry.is_complete != step.is_complete:
            raise ValueError(f"Command demo readiness command audit completeness is inconsistent: {entry.flow_step}")
    if contract.is_complete != (step_status.is_complete and all(entry.is_complete for entry in contract.entries)):
        raise ValueError("Command demo readiness command audit completeness is inconsistent")


def command_demo_readiness_command_audit_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, bool, tuple[str, ...]], ...]:
    contract = command_demo_readiness_command_audit_contract(specs, launcher_argv)
    return tuple(
        (
            entry.flow_step,
            entry.name,
            entry.demo_path_step,
            entry.is_complete,
            entry.engine_actions,
        )
        for entry in contract.entries
    )


def command_mvp_demo_readiness_command_audit_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessCommandAuditContract:
    return command_demo_readiness_command_audit_contract(specs, launcher_argv)


def command_mvp_demo_readiness_command_audit_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, bool, tuple[str, ...]], ...]:
    return command_demo_readiness_command_audit_summary(specs, launcher_argv)


def command_demo_readiness_handoff_step_status_payload(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> dict[str, object]:
    contract = command_demo_readiness_handoff_step_status_contract(specs, launcher_argv)
    payload: dict[str, object] = {
        "fingerprint": {
            "algorithm": contract.fingerprint_algorithm,
            "digest": contract.fingerprint_digest,
        },
        "is_complete": contract.is_complete,
        "steps": [
            {
                "ordinal": step.ordinal,
                "demo_path_step": step.demo_path_step,
                "flow_step": step.flow_step,
                "command": step.name,
                "command_line": step.command_line,
                "parser_token": step.parser_token,
                "engine_actions": list(step.engine_actions),
                "exact_action_lines": [
                    {
                        "engine_action": engine_action,
                        "command_line": command_line,
                    }
                    for engine_action, command_line in step.exact_action_lines
                ],
                "is_cli_entrypoint": step.is_cli_entrypoint,
                "is_complete": step.is_complete,
            }
            for step in contract.steps
        ],
    }
    json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return payload


def command_demo_readiness_handoff_step_status_json(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return json.dumps(
        command_demo_readiness_handoff_step_status_payload(specs, launcher_argv),
        sort_keys=True,
        separators=(",", ":"),
    )


@lru_cache(maxsize=None)
def command_demo_readiness_handoff_audit(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessHandoffAudit:
    packet = command_demo_readiness_handoff_packet(specs, launcher_argv)
    seal = command_demo_readiness_seal(specs, launcher_argv)
    fingerprint = command_demo_readiness_fingerprint(specs, launcher_argv)
    cli_validation = command_demo_readiness_validate_cli_exact_action_shell_script_lines(
        packet.cli_exact_action_lines,
        specs,
        launcher_argv,
    )
    exact_validation = command_demo_readiness_validate_exact_action_shell_script_lines(
        packet.exact_action_lines,
        specs,
        launcher_argv,
    )
    invalid_argv = _ordered_unique_argv(
        *packet.invalid_argv,
        *cli_validation.invalid_argv,
        *exact_validation.invalid_argv,
    )
    missing_flow_steps = _ordered_unique_tokens(
        *packet.missing_flow_steps,
        *cli_validation.missing_flow_steps,
        *exact_validation.missing_flow_steps,
    )
    missing_engine_actions = _ordered_unique_tokens(
        *packet.missing_engine_actions,
        *cli_validation.missing_engine_actions,
        *exact_validation.missing_engine_actions,
    )
    audit = CommandDemoReadinessHandoffAudit(
        is_complete=(
            packet.is_complete
            and seal.is_complete
            and cli_validation.is_complete
            and exact_validation.is_complete
            and packet.fingerprint_digest == fingerprint.digest
            and packet.command_lines == seal.command_lines
            and packet.exact_action_lines == seal.exact_action_lines
            and packet.cli_exact_action_lines == seal.cli_exact_action_lines
            and not invalid_argv
            and not missing_flow_steps
            and not missing_engine_actions
        ),
        fingerprint_digest=fingerprint.digest,
        packet_fingerprint_digest=packet.fingerprint_digest,
        command_lines_match=packet.command_lines == seal.command_lines,
        exact_action_lines_match=packet.exact_action_lines == seal.exact_action_lines,
        cli_exact_action_lines_match=packet.cli_exact_action_lines == seal.cli_exact_action_lines,
        invalid_argv=invalid_argv,
        missing_flow_steps=missing_flow_steps,
        missing_engine_actions=missing_engine_actions,
    )
    _validate_command_demo_readiness_handoff_audit(audit, packet, seal, fingerprint)
    return audit


def _validate_command_demo_readiness_handoff_audit(
    audit: CommandDemoReadinessHandoffAudit,
    packet: CommandDemoReadinessHandoffPacket,
    seal: CommandDemoReadinessSeal,
    fingerprint: CommandDemoReadinessFingerprint,
) -> None:
    if audit.fingerprint_digest != fingerprint.digest:
        raise ValueError("Command demo readiness handoff audit fingerprint is inconsistent")
    if audit.packet_fingerprint_digest != packet.fingerprint_digest:
        raise ValueError("Command demo readiness handoff audit packet fingerprint is inconsistent")
    if audit.command_lines_match != (packet.command_lines == seal.command_lines):
        raise ValueError("Command demo readiness handoff audit command match is inconsistent")
    if audit.exact_action_lines_match != (packet.exact_action_lines == seal.exact_action_lines):
        raise ValueError("Command demo readiness handoff audit exact action match is inconsistent")
    if audit.cli_exact_action_lines_match != (
        packet.cli_exact_action_lines == seal.cli_exact_action_lines
    ):
        raise ValueError("Command demo readiness handoff audit CLI exact action match is inconsistent")
    if audit.is_complete != (
        packet.is_complete
        and seal.is_complete
        and audit.fingerprint_digest == audit.packet_fingerprint_digest
        and audit.command_lines_match
        and audit.exact_action_lines_match
        and audit.cli_exact_action_lines_match
        and not audit.invalid_argv
        and not audit.missing_flow_steps
        and not audit.missing_engine_actions
    ):
        raise ValueError("Command demo readiness handoff audit completeness is inconsistent")


def command_demo_readiness_handoff_audit_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    bool,
    str,
    str,
    bool,
    bool,
    bool,
    tuple[tuple[str, ...], ...],
    tuple[str, ...],
    tuple[str, ...],
]:
    audit = command_demo_readiness_handoff_audit(specs, launcher_argv)
    return (
        audit.is_complete,
        audit.fingerprint_digest,
        audit.packet_fingerprint_digest,
        audit.command_lines_match,
        audit.exact_action_lines_match,
        audit.cli_exact_action_lines_match,
        audit.invalid_argv,
        audit.missing_flow_steps,
        audit.missing_engine_actions,
    )


@lru_cache(maxsize=None)
def command_demo_readiness_exact_action_route_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessExactActionRouteContract:
    routes_by_flow_step = {
        route.flow_step: route
        for route in command_demo_readiness_route_contract(specs, launcher_argv).entries
    }
    entries: list[CommandDemoReadinessExactActionRouteEntry] = []
    for engine_action in command_demo_engine_actions(specs):
        action_entry = command_demo_readiness_action_entry(engine_action, specs, launcher_argv)
        if action_entry is None:
            raise ValueError(f"Command demo readiness exact action is not routeable: {engine_action}")
        route = routes_by_flow_step.get(action_entry.flow_step)
        if route is None:
            raise ValueError(f"Command demo readiness exact action route is missing: {engine_action}")
        command_argv = command_demo_readiness_exact_argv_for_engine_action(
            engine_action,
            specs,
            launcher_argv,
        )
        command_line = command_demo_readiness_exact_line_for_engine_action(
            engine_action,
            specs,
            launcher_argv,
        )
        entries.append(
            CommandDemoReadinessExactActionRouteEntry(
                engine_action=engine_action,
                demo_path_step=action_entry.demo_path_step,
                flow_step=action_entry.flow_step,
                name=action_entry.name,
                cli_tokens=route.cli_tokens,
                command_argv=command_argv,
                command_line=command_line,
            )
        )
    contract = CommandDemoReadinessExactActionRouteContract(entries=tuple(entries))
    _validate_command_demo_readiness_exact_action_route_contract(
        contract,
        specs,
        launcher_argv,
    )
    return contract


def _validate_command_demo_readiness_exact_action_route_contract(
    contract: CommandDemoReadinessExactActionRouteContract,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    if tuple(entry.engine_action for entry in contract.entries) != command_demo_engine_actions(specs):
        raise ValueError("Command demo readiness exact action route actions are inconsistent")
    seen_actions: set[str] = set()
    for entry in contract.entries:
        if entry.engine_action in seen_actions:
            raise ValueError(f"Duplicate command demo readiness exact action: {entry.engine_action}")
        seen_actions.add(entry.engine_action)
        action_entry = command_demo_readiness_action_entry(entry.engine_action, specs, launcher_argv)
        if action_entry is None:
            raise ValueError(f"Command demo readiness exact action is not configured: {entry.engine_action}")
        if entry.demo_path_step != action_entry.demo_path_step:
            raise ValueError(f"Command demo readiness exact action path is inconsistent: {entry.engine_action}")
        if entry.flow_step != action_entry.flow_step:
            raise ValueError(f"Command demo readiness exact action flow is inconsistent: {entry.engine_action}")
        if entry.name != action_entry.name:
            raise ValueError(f"Command demo readiness exact action command is inconsistent: {entry.engine_action}")
        if not entry.command_argv or not entry.command_line:
            raise ValueError(f"Command demo readiness exact action line is missing: {entry.engine_action}")
        if _shell_join(entry.command_argv) != entry.command_line:
            raise ValueError(f"Command demo readiness exact action line is inconsistent: {entry.engine_action}")
        validation = command_demo_readiness_validate_cli_argv(entry.command_argv, specs, launcher_argv)
        if not validation.is_cli_entrypoint or validation.exact_engine_action != entry.engine_action:
            raise ValueError(f"Command demo readiness exact action is not CLI-routeable: {entry.engine_action}")
        if entry.flow_step != validation.flow_step or entry.name != validation.name:
            raise ValueError(f"Command demo readiness exact action validation drifted: {entry.engine_action}")


def command_demo_readiness_exact_action_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, str, tuple[str, ...], str], ...]:
    return tuple(
        (
            entry.engine_action,
            entry.demo_path_step,
            entry.flow_step,
            entry.name,
            entry.cli_tokens,
            entry.command_line,
        )
        for entry in command_demo_readiness_exact_action_route_contract(
            specs,
            launcher_argv,
        ).entries
    )


def command_demo_readiness_exact_action_route_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (entry.engine_action, entry.command_line)
        for entry in command_demo_readiness_exact_action_route_contract(
            specs,
            launcher_argv,
        ).entries
    )


@lru_cache(maxsize=None)
def command_demo_readiness_action_sequence_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessActionSequenceContract:
    exact_actions = command_demo_readiness_exact_action_line_lookup_table(specs, launcher_argv)
    steps: list[CommandDemoReadinessActionSequenceStep] = []
    for ordinal, (engine_action, command_line) in enumerate(exact_actions, start=1):
        action_entry = command_demo_readiness_action_entry(engine_action, specs, launcher_argv)
        if action_entry is None:
            raise ValueError(f"Command demo readiness action sequence is not routeable: {engine_action}")
        steps.append(
            CommandDemoReadinessActionSequenceStep(
                ordinal=ordinal,
                engine_action=engine_action,
                demo_path_step=action_entry.demo_path_step,
                flow_step=action_entry.flow_step,
                name=action_entry.name,
                command_line=command_line,
            )
        )
    contract = CommandDemoReadinessActionSequenceContract(steps=tuple(steps))
    _validate_command_demo_readiness_action_sequence_contract(
        contract,
        specs,
        launcher_argv,
    )
    return contract


def _validate_command_demo_readiness_action_sequence_contract(
    contract: CommandDemoReadinessActionSequenceContract,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    expected_actions = command_demo_engine_actions(specs)
    if tuple(step.ordinal for step in contract.steps) != tuple(range(1, len(contract.steps) + 1)):
        raise ValueError("Command demo readiness action sequence ordinals are inconsistent")
    if tuple(step.engine_action for step in contract.steps) != expected_actions:
        raise ValueError("Command demo readiness action sequence actions are inconsistent")
    if tuple(step.command_line for step in contract.steps) != command_demo_readiness_exact_action_shell_script_lines(
        specs,
        launcher_argv,
    ):
        raise ValueError("Command demo readiness action sequence lines are inconsistent")
    handoff_action_lines = tuple(
        (engine_action, command_line)
        for handoff_step in command_demo_readiness_handoff_action_contract(specs, launcher_argv).steps
        for engine_action, command_line in handoff_step.exact_action_lines
    )
    sequence_action_lines = tuple((step.engine_action, step.command_line) for step in contract.steps)
    if sequence_action_lines != handoff_action_lines:
        raise ValueError("Command demo readiness action sequence handoff lines are inconsistent")
    for step in contract.steps:
        exact_action = command_demo_readiness_exact_action_for_argv(
            step.command_line,
            specs,
            launcher_argv,
        )
        if exact_action != step.engine_action:
            raise ValueError(f"Command demo readiness action sequence exact action is inconsistent: {step.engine_action}")


def command_demo_readiness_action_sequence_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, str], ...]:
    return tuple(
        (
            step.ordinal,
            step.engine_action,
            step.demo_path_step,
            step.flow_step,
            step.name,
            step.command_line,
        )
        for step in command_demo_readiness_action_sequence_contract(specs, launcher_argv).steps
    )


@lru_cache(maxsize=None)
def command_demo_readiness_seal(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessSeal:
    gate = require_command_demo_readiness_complete(specs, launcher_argv)
    exact_action_lines = command_demo_readiness_exact_action_shell_script_lines(specs, launcher_argv)
    exact_validation = command_demo_readiness_validate_exact_action_shell_script_lines(
        exact_action_lines,
        specs,
        launcher_argv,
    )
    cli_exact_action_lines = command_demo_readiness_cli_exact_action_shell_script_lines(specs, launcher_argv)
    cli_validation = command_demo_readiness_validate_cli_exact_action_shell_script_lines(
        cli_exact_action_lines,
        specs,
        launcher_argv,
    )
    exact_cli_audit = command_demo_readiness_exact_cli_audit_contract(specs, launcher_argv)
    missing_flow_steps = _ordered_unique_tokens(
        *exact_validation.missing_flow_steps,
        *cli_validation.missing_flow_steps,
    )
    missing_engine_actions = _ordered_unique_tokens(
        *gate.missing_engine_actions,
        *exact_validation.missing_engine_actions,
        *cli_validation.missing_engine_actions,
        *exact_cli_audit.invalid_engine_actions,
    )
    invalid_argv = _ordered_unique_argv(
        *exact_validation.invalid_argv,
        *cli_validation.invalid_argv,
    )
    seal = CommandDemoReadinessSeal(
        is_complete=(
            gate.is_complete
            and exact_validation.is_complete
            and cli_validation.is_complete
            and exact_cli_audit.is_complete
            and not missing_flow_steps
            and not missing_engine_actions
            and not invalid_argv
        ),
        flow_steps=command_demo_flow_steps(),
        command_lines=gate.command_lines,
        exact_action_lines=exact_action_lines,
        cli_exact_action_lines=cli_exact_action_lines,
        engine_actions=command_demo_engine_actions(specs),
        missing_flow_steps=missing_flow_steps,
        missing_engine_actions=missing_engine_actions,
        invalid_argv=invalid_argv,
    )
    _validate_command_demo_readiness_seal(seal, specs, launcher_argv)
    return seal


def _ordered_unique_tokens(*values: str) -> tuple[str, ...]:
    seen_values: set[str] = set()
    ordered_values: list[str] = []
    for value in values:
        if value in seen_values:
            continue
        seen_values.add(value)
        ordered_values.append(value)
    return tuple(ordered_values)


def _ordered_unique_argv(*values: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    seen_values: set[tuple[str, ...]] = set()
    ordered_values: list[tuple[str, ...]] = []
    for value in values:
        if value in seen_values:
            continue
        seen_values.add(value)
        ordered_values.append(value)
    return tuple(ordered_values)


def _validate_command_demo_readiness_seal(
    seal: CommandDemoReadinessSeal,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    if seal.flow_steps != command_demo_flow_steps():
        raise ValueError("Command demo readiness seal flow steps are inconsistent")
    if seal.command_lines != require_command_demo_readiness_complete(specs, launcher_argv).command_lines:
        raise ValueError("Command demo readiness seal commands are inconsistent")
    if seal.engine_actions != command_demo_engine_actions(specs):
        raise ValueError("Command demo readiness seal actions are inconsistent")
    expected_exact_action_lines = command_demo_readiness_exact_action_shell_script_lines(
        specs,
        launcher_argv,
    )
    if seal.exact_action_lines != expected_exact_action_lines:
        raise ValueError("Command demo readiness seal exact action lines are inconsistent")
    expected_cli_exact_action_lines = command_demo_readiness_cli_exact_action_shell_script_lines(
        specs,
        launcher_argv,
    )
    if seal.cli_exact_action_lines != expected_cli_exact_action_lines:
        raise ValueError("Command demo readiness seal CLI exact action lines are inconsistent")
    expected_executable_lines = _dedupe_command_lines(
        ("set -euo pipefail", *seal.command_lines, *seal.exact_action_lines)
    )
    shell_executable_lines = command_demo_readiness_shell_executable_lines(specs, launcher_argv)
    if tuple(line for line in expected_executable_lines if line not in shell_executable_lines):
        raise ValueError("Command demo readiness seal shell script lines are incomplete")
    if tuple(line for line in shell_executable_lines if line not in expected_executable_lines):
        raise ValueError("Command demo readiness seal shell script lines are inconsistent")
    exact_validation = command_demo_readiness_validate_exact_action_shell_script_lines(
        seal.exact_action_lines,
        specs,
        launcher_argv,
    )
    cli_validation = command_demo_readiness_validate_cli_exact_action_shell_script_lines(
        seal.cli_exact_action_lines,
        specs,
        launcher_argv,
    )
    if not exact_validation.is_complete:
        raise ValueError("Command demo readiness seal exact action script is incomplete")
    if not cli_validation.is_complete:
        raise ValueError("Command demo readiness seal CLI exact action script is incomplete")
    if seal.missing_flow_steps or seal.missing_engine_actions or seal.invalid_argv:
        raise ValueError("Command demo readiness seal must not report missing coverage")
    if not seal.is_complete:
        raise ValueError("Command demo readiness seal must be complete")


def command_demo_readiness_seal_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    bool,
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[tuple[str, ...], ...],
]:
    seal = command_demo_readiness_seal(specs, launcher_argv)
    return (
        seal.is_complete,
        seal.flow_steps,
        seal.command_lines,
        seal.exact_action_lines,
        seal.cli_exact_action_lines,
        seal.engine_actions,
        seal.missing_flow_steps,
        seal.missing_engine_actions,
        seal.invalid_argv,
    )


def _command_demo_readiness_fingerprint_payload(seal: CommandDemoReadinessSeal) -> dict[str, object]:
    return {
        "flow_steps": seal.flow_steps,
        "engine_actions": seal.engine_actions,
        "command_lines": seal.command_lines,
        "exact_action_lines": seal.exact_action_lines,
        "cli_exact_action_lines": seal.cli_exact_action_lines,
    }


@lru_cache(maxsize=None)
def command_demo_readiness_fingerprint(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessFingerprint:
    seal = command_demo_readiness_seal(specs, launcher_argv)
    payload = _command_demo_readiness_fingerprint_payload(seal)
    digest_input = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    fingerprint = CommandDemoReadinessFingerprint(
        algorithm="sha256",
        digest=hashlib.sha256(digest_input).hexdigest(),
        flow_steps=seal.flow_steps,
        engine_actions=seal.engine_actions,
        command_lines=seal.command_lines,
        exact_action_lines=seal.exact_action_lines,
        cli_exact_action_lines=seal.cli_exact_action_lines,
    )
    _validate_command_demo_readiness_fingerprint(fingerprint, seal)
    return fingerprint


def _validate_command_demo_readiness_fingerprint(
    fingerprint: CommandDemoReadinessFingerprint,
    seal: CommandDemoReadinessSeal,
) -> None:
    if fingerprint.algorithm != "sha256":
        raise ValueError("Command demo readiness fingerprint algorithm is inconsistent")
    if fingerprint.flow_steps != seal.flow_steps:
        raise ValueError("Command demo readiness fingerprint flow steps are inconsistent")
    if fingerprint.engine_actions != seal.engine_actions:
        raise ValueError("Command demo readiness fingerprint actions are inconsistent")
    if fingerprint.command_lines != seal.command_lines:
        raise ValueError("Command demo readiness fingerprint commands are inconsistent")
    if fingerprint.exact_action_lines != seal.exact_action_lines:
        raise ValueError("Command demo readiness fingerprint exact actions are inconsistent")
    if fingerprint.cli_exact_action_lines != seal.cli_exact_action_lines:
        raise ValueError("Command demo readiness fingerprint CLI exact actions are inconsistent")
    expected_digest = hashlib.sha256(
        json.dumps(
            _command_demo_readiness_fingerprint_payload(seal),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    if fingerprint.digest != expected_digest:
        raise ValueError("Command demo readiness fingerprint digest is inconsistent")


def command_demo_readiness_fingerprint_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, str, tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    fingerprint = command_demo_readiness_fingerprint(specs, launcher_argv)
    return (
        fingerprint.algorithm,
        fingerprint.digest,
        fingerprint.flow_steps,
        fingerprint.engine_actions,
        fingerprint.command_lines,
        fingerprint.exact_action_lines,
        fingerprint.cli_exact_action_lines,
    )


@lru_cache(maxsize=None)
def command_demo_readiness_step_seal_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessStepSealContract:
    readiness_entries = command_demo_readiness_contract(specs, launcher_argv).entries
    exact_lines_by_flow_step: dict[str, list[tuple[str, str]]] = {}
    for engine_action, command_line in command_demo_readiness_exact_action_line_lookup_table(
        specs,
        launcher_argv,
    ):
        flow_step = command_demo_readiness_flow_step_for_argv(command_line, specs, launcher_argv)
        if flow_step is None:
            raise ValueError(f"Command demo readiness step seal action is not routeable: {engine_action}")
        exact_lines_by_flow_step.setdefault(flow_step, []).append((engine_action, command_line))

    contract = CommandDemoReadinessStepSealContract(
        steps=tuple(
            CommandDemoReadinessStepSeal(
                ordinal=entry.ordinal,
                demo_path_step=entry.demo_path_step,
                flow_step=entry.flow_step,
                name=entry.name,
                command_argv=_argv_without_launcher(entry.command_argv, launcher_argv),
                command_line=_shell_join(entry.command_argv),
                engine_actions=entry.engine_actions,
                exact_action_lines=tuple(exact_lines_by_flow_step.get(entry.flow_step, ())),
            )
            for entry in readiness_entries
        )
    )
    _validate_command_demo_readiness_step_seal_contract(contract, specs, launcher_argv)
    return contract


def _validate_command_demo_readiness_step_seal_contract(
    contract: CommandDemoReadinessStepSealContract,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    readiness_entries = command_demo_readiness_contract(specs, launcher_argv).entries
    if tuple(step.ordinal for step in contract.steps) != tuple(entry.ordinal for entry in readiness_entries):
        raise ValueError("Command demo readiness step seal ordinals are inconsistent")
    if tuple(step.flow_step for step in contract.steps) != tuple(entry.flow_step for entry in readiness_entries):
        raise ValueError("Command demo readiness step seal flow steps are inconsistent")
    if tuple(step.name for step in contract.steps) != tuple(entry.name for entry in readiness_entries):
        raise ValueError("Command demo readiness step seal command names are inconsistent")
    if tuple(step.command_line for step in contract.steps) != tuple(
        _shell_join(entry.command_argv) for entry in readiness_entries
    ):
        raise ValueError("Command demo readiness step seal command lines are inconsistent")
    if tuple(step.demo_path_step for step in contract.steps) != tuple(
        entry.demo_path_step for entry in readiness_entries
    ):
        raise ValueError("Command demo readiness step seal demo path steps are inconsistent")
    if tuple(step.engine_actions for step in contract.steps) != tuple(
        entry.engine_actions for entry in readiness_entries
    ):
        raise ValueError("Command demo readiness step seal actions are inconsistent")
    for step in contract.steps:
        expected_actions = tuple(engine_action for engine_action, _ in step.exact_action_lines)
        if expected_actions != step.engine_actions:
            raise ValueError(f"Command demo readiness step seal exact actions are incomplete: {step.flow_step}")
        if any(not command_line.strip() for _, command_line in step.exact_action_lines):
            raise ValueError(f"Command demo readiness step seal exact action line is empty: {step.flow_step}")


def command_demo_readiness_step_seal_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    tuple[int, str, str, str, tuple[str, ...], str, tuple[str, ...], tuple[tuple[str, str], ...]],
    ...,
]:
    return tuple(
        (
            step.ordinal,
            step.demo_path_step,
            step.flow_step,
            step.name,
            step.command_argv,
            step.command_line,
            step.engine_actions,
            step.exact_action_lines,
        )
        for step in command_demo_readiness_step_seal_contract(specs, launcher_argv).steps
    )


def command_demo_readiness_step_seal_payload(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "ordinal": step.ordinal,
            "demo_path_step": step.demo_path_step,
            "flow_step": step.flow_step,
            "command": step.name,
            "command_argv": step.command_argv,
            "command_line": step.command_line,
            "engine_actions": step.engine_actions,
            "exact_action_lines": step.exact_action_lines,
        }
        for step in command_demo_readiness_step_seal_contract(specs, launcher_argv).steps
    )


def command_demo_readiness_step_seal_json(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return json.dumps(
        command_demo_readiness_step_seal_payload(specs, launcher_argv),
        sort_keys=True,
        separators=(",", ":"),
    )


@lru_cache(maxsize=None)
def command_demo_readiness_cli_step_validation_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessCliStepValidationContract:
    steps: list[CommandDemoReadinessCliStepValidation] = []
    for step in command_demo_readiness_step_seal_contract(specs, launcher_argv).steps:
        validation = command_demo_readiness_validate_cli_argv(
            step.command_line,
            specs,
            launcher_argv,
        )
        steps.append(
            CommandDemoReadinessCliStepValidation(
                ordinal=step.ordinal,
                demo_path_step=step.demo_path_step,
                flow_step=step.flow_step,
                name=step.name,
                command_line=step.command_line,
                parser_token=validation.parser_token or "",
                canonical_command_line=validation.command_line,
                is_cli_entrypoint=validation.is_cli_entrypoint,
            )
        )
    contract = CommandDemoReadinessCliStepValidationContract(steps=tuple(steps))
    _validate_command_demo_readiness_cli_step_validation_contract(contract, specs, launcher_argv)
    return contract


def _validate_command_demo_readiness_cli_step_validation_contract(
    contract: CommandDemoReadinessCliStepValidationContract,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    step_seals = command_demo_readiness_step_seal_contract(specs, launcher_argv).steps
    if tuple(step.ordinal for step in contract.steps) != tuple(step.ordinal for step in step_seals):
        raise ValueError("Command demo readiness CLI step validation ordinals are inconsistent")
    if tuple(step.demo_path_step for step in contract.steps) != tuple(step.demo_path_step for step in step_seals):
        raise ValueError("Command demo readiness CLI step validation demo path steps are inconsistent")
    if tuple(step.flow_step for step in contract.steps) != tuple(step.flow_step for step in step_seals):
        raise ValueError("Command demo readiness CLI step validation flow steps are inconsistent")
    if tuple(step.name for step in contract.steps) != tuple(step.name for step in step_seals):
        raise ValueError("Command demo readiness CLI step validation command names are inconsistent")
    if tuple(step.command_line for step in contract.steps) != tuple(step.command_line for step in step_seals):
        raise ValueError("Command demo readiness CLI step validation command lines are inconsistent")
    cli_lookup = dict(command_cli_lookup_table()) if specs == COMMAND_SPECS else {}
    for step in contract.steps:
        if not step.parser_token:
            raise ValueError(f"Command demo readiness CLI step validation parser token is empty: {step.flow_step}")
        if specs == COMMAND_SPECS and cli_lookup.get(step.parser_token) != step.name:
            raise ValueError(f"Command demo readiness CLI step validation parser token is inconsistent: {step.flow_step}")
        validation = command_demo_readiness_validate_cli_argv(
            step.command_line,
            specs,
            launcher_argv,
        )
        if step.canonical_command_line != validation.command_line:
            raise ValueError(f"Command demo readiness CLI step validation canonical line is inconsistent: {step.flow_step}")
        if not step.is_cli_entrypoint or not validation.is_cli_entrypoint:
            raise ValueError(f"Command demo readiness CLI step validation is not routeable: {step.flow_step}")


def command_demo_readiness_cli_step_validation_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, str, str, bool], ...]:
    return tuple(
        (
            step.ordinal,
            step.demo_path_step,
            step.flow_step,
            step.name,
            step.command_line,
            step.parser_token,
            step.canonical_command_line,
            step.is_cli_entrypoint,
        )
        for step in command_demo_readiness_cli_step_validation_contract(specs, launcher_argv).steps
    )


def command_demo_readiness_cli_step_validation_payload(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "ordinal": step.ordinal,
            "demo_path_step": step.demo_path_step,
            "flow_step": step.flow_step,
            "command": step.name,
            "command_line": step.command_line,
            "parser_token": step.parser_token,
            "canonical_command_line": step.canonical_command_line,
            "is_cli_entrypoint": step.is_cli_entrypoint,
        }
        for step in command_demo_readiness_cli_step_validation_contract(specs, launcher_argv).steps
    )


def command_demo_readiness_cli_step_validation_json(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return json.dumps(
        command_demo_readiness_cli_step_validation_payload(specs, launcher_argv),
        sort_keys=True,
        separators=(",", ":"),
    )


def _command_demo_readiness_index_step_payload(
    step: CommandDemoReadinessStepSeal,
) -> dict[str, object]:
    return {
        "ordinal": step.ordinal,
        "demo_path_step": step.demo_path_step,
        "flow_step": step.flow_step,
        "name": step.name,
        "command_line": step.command_line,
        "engine_actions": step.engine_actions,
        "exact_action_lines": step.exact_action_lines,
    }


def _command_demo_readiness_index_step_digest(
    step: CommandDemoReadinessStepSeal,
) -> str:
    digest_input = json.dumps(
        _command_demo_readiness_index_step_payload(step),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(digest_input).hexdigest()


@lru_cache(maxsize=None)
def command_demo_readiness_index_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessIndexContract:
    fingerprint = command_demo_readiness_fingerprint(specs, launcher_argv)
    contract = CommandDemoReadinessIndexContract(
        fingerprint_algorithm=fingerprint.algorithm,
        readiness_fingerprint_digest=fingerprint.digest,
        entries=tuple(
            CommandDemoReadinessIndexEntry(
                ordinal=step.ordinal,
                demo_path_step=step.demo_path_step,
                flow_step=step.flow_step,
                name=step.name,
                command_line=step.command_line,
                engine_actions=step.engine_actions,
                exact_action_lines=step.exact_action_lines,
                readiness_fingerprint_digest=fingerprint.digest,
                step_fingerprint_digest=_command_demo_readiness_index_step_digest(step),
            )
            for step in command_demo_readiness_step_seal_contract(specs, launcher_argv).steps
        ),
    )
    _validate_command_demo_readiness_index_contract(contract, specs, launcher_argv)
    return contract


def _validate_command_demo_readiness_index_contract(
    contract: CommandDemoReadinessIndexContract,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    fingerprint = command_demo_readiness_fingerprint(specs, launcher_argv)
    step_seals = command_demo_readiness_step_seal_contract(specs, launcher_argv).steps
    if contract.fingerprint_algorithm != fingerprint.algorithm:
        raise ValueError("Command demo readiness index fingerprint algorithm is inconsistent")
    if contract.readiness_fingerprint_digest != fingerprint.digest:
        raise ValueError("Command demo readiness index fingerprint digest is inconsistent")
    if tuple(entry.ordinal for entry in contract.entries) != tuple(step.ordinal for step in step_seals):
        raise ValueError("Command demo readiness index ordinals are inconsistent")
    if tuple(entry.demo_path_step for entry in contract.entries) != tuple(
        step.demo_path_step for step in step_seals
    ):
        raise ValueError("Command demo readiness index demo path steps are inconsistent")
    if tuple(entry.flow_step for entry in contract.entries) != tuple(step.flow_step for step in step_seals):
        raise ValueError("Command demo readiness index flow steps are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(step.name for step in step_seals):
        raise ValueError("Command demo readiness index command names are inconsistent")
    if tuple(entry.command_line for entry in contract.entries) != tuple(
        step.command_line for step in step_seals
    ):
        raise ValueError("Command demo readiness index command lines are inconsistent")
    for entry, step in zip(contract.entries, step_seals, strict=True):
        if entry.engine_actions != step.engine_actions:
            raise ValueError(f"Command demo readiness index actions are inconsistent: {entry.flow_step}")
        if entry.exact_action_lines != step.exact_action_lines:
            raise ValueError(
                f"Command demo readiness index exact action lines are inconsistent: {entry.flow_step}"
            )
        if entry.readiness_fingerprint_digest != fingerprint.digest:
            raise ValueError(f"Command demo readiness index entry fingerprint is inconsistent: {entry.flow_step}")
        if entry.step_fingerprint_digest != _command_demo_readiness_index_step_digest(step):
            raise ValueError(
                f"Command demo readiness index step fingerprint is inconsistent: {entry.flow_step}"
            )


def command_demo_readiness_index_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    str,
    str,
    tuple[tuple[int, str, str, str, str, tuple[str, ...], tuple[tuple[str, str], ...], str, str], ...],
]:
    contract = command_demo_readiness_index_contract(specs, launcher_argv)
    return (
        contract.fingerprint_algorithm,
        contract.readiness_fingerprint_digest,
        tuple(
            (
                entry.ordinal,
                entry.demo_path_step,
                entry.flow_step,
                entry.name,
                entry.command_line,
                entry.engine_actions,
                entry.exact_action_lines,
                entry.readiness_fingerprint_digest,
                entry.step_fingerprint_digest,
            )
            for entry in contract.entries
        ),
    )


def command_demo_readiness_index_payload(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> dict[str, object]:
    contract = command_demo_readiness_index_contract(specs, launcher_argv)
    return {
        "fingerprint_algorithm": contract.fingerprint_algorithm,
        "readiness_fingerprint_digest": contract.readiness_fingerprint_digest,
        "entries": [
            {
                "ordinal": entry.ordinal,
                "demo_path_step": entry.demo_path_step,
                "flow_step": entry.flow_step,
                "command": entry.name,
                "command_line": entry.command_line,
                "engine_actions": entry.engine_actions,
                "exact_action_lines": entry.exact_action_lines,
                "readiness_fingerprint_digest": entry.readiness_fingerprint_digest,
                "step_fingerprint_digest": entry.step_fingerprint_digest,
            }
            for entry in contract.entries
        ],
    }


def command_demo_readiness_index_json(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return json.dumps(
        command_demo_readiness_index_payload(specs, launcher_argv),
        sort_keys=True,
        separators=(",", ":"),
    )


@lru_cache(maxsize=None)
def command_demo_readiness_shell_script(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessShellScript:
    smoke_plan = command_demo_readiness_smoke_plan(specs, launcher_argv)
    command_lines = tuple(step.command_line for step in smoke_plan.steps)
    cli_exact_action_lines = command_demo_readiness_cli_exact_action_line_lookup_table(
        specs,
        launcher_argv,
    )
    cli_exact_action_lines_by_flow_step: dict[str, list[tuple[str, str]]] = {}
    for engine_action, command_line in cli_exact_action_lines:
        flow_step = command_demo_readiness_flow_step_for_argv(command_line, specs, launcher_argv)
        if flow_step is None:
            raise ValueError(f"Command demo readiness shell CLI exact action is not routeable: {engine_action}")
        cli_exact_action_lines_by_flow_step.setdefault(flow_step, []).append((engine_action, command_line))
    action_lines = cli_exact_action_lines
    lines: list[str] = ["set -euo pipefail"]
    emitted_command_lines = {"set -euo pipefail"}
    for step in smoke_plan.steps:
        lines.append(f"# {step.ordinal}. {step.demo_path_step} [{step.flow_step}/{step.name}]")
        if step.command_line not in emitted_command_lines:
            emitted_command_lines.add(step.command_line)
            lines.append(step.command_line)
        for engine_action, command_line in cli_exact_action_lines_by_flow_step.get(step.flow_step, ()):
            lines.append(f"# action: {engine_action}")
            if command_line not in emitted_command_lines:
                emitted_command_lines.add(command_line)
                lines.append(command_line)
    script = CommandDemoReadinessShellScript(
        lines=tuple(lines),
        command_lines=command_lines,
        action_lines=action_lines,
        text="\n".join(lines),
    )
    _validate_command_demo_readiness_shell_script(script, smoke_plan, specs, launcher_argv)
    return script


def _validate_command_demo_readiness_shell_script(
    script: CommandDemoReadinessShellScript,
    smoke_plan: CommandDemoReadinessSmokePlan,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    expected_command_lines = tuple(step.command_line for step in smoke_plan.steps)
    expected_action_lines = command_demo_readiness_cli_exact_action_line_lookup_table(
        specs,
        launcher_argv,
    )
    if script.command_lines != expected_command_lines:
        raise ValueError("Command demo readiness shell script command lines are inconsistent")
    if script.action_lines != expected_action_lines:
        raise ValueError("Command demo readiness shell script CLI action lines are inconsistent")
    if not script.lines or script.lines[0] != "set -euo pipefail":
        raise ValueError("Command demo readiness shell script must start with strict shell mode")
    if script.text != "\n".join(script.lines):
        raise ValueError("Command demo readiness shell script text is inconsistent")
    if any(not line.strip() for line in script.lines):
        raise ValueError("Command demo readiness shell script lines must not be empty")
    executable_lines = tuple(line for line in script.lines if not line.startswith("#"))
    expected_executable_lines = _dedupe_command_lines(
        tuple(
            line
            for grouped_lines in (
                ("set -euo pipefail",),
                *(
                    (
                        step.command_line,
                        *(
                            command_line
                            for _, command_line in expected_action_lines
                            if command_demo_readiness_flow_step_for_argv(
                                command_line,
                                specs,
                                launcher_argv,
                            )
                            == step.flow_step
                        ),
                    )
                    for step in smoke_plan.steps
                ),
            )
            for line in grouped_lines
        )
    )
    if executable_lines != expected_executable_lines:
        raise ValueError("Command demo readiness shell script executable lines are inconsistent")
    _validate_command_demo_readiness_shell_routes(script, smoke_plan, specs, launcher_argv)
    validation = command_demo_readiness_validate_shell_script_lines(
        script.lines,
        specs,
        launcher_argv,
    )
    if not validation.is_complete:
        raise ValueError("Command demo readiness shell script does not cover the MVP route")
    cli_exact_validation = command_demo_readiness_validate_cli_exact_action_shell_script_lines(
        tuple(command_line for _, command_line in expected_action_lines),
        specs,
        launcher_argv,
    )
    if not cli_exact_validation.is_complete:
        raise ValueError("Command demo readiness shell script does not cover CLI exact MVP actions")


def _dedupe_command_lines(lines: tuple[str, ...]) -> tuple[str, ...]:
    seen_lines: set[str] = set()
    deduped_lines: list[str] = []
    for line in lines:
        if line in seen_lines:
            continue
        seen_lines.add(line)
        deduped_lines.append(line)
    return tuple(deduped_lines)


def _validate_command_demo_readiness_shell_routes(
    script: CommandDemoReadinessShellScript,
    smoke_plan: CommandDemoReadinessSmokePlan,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    for step in smoke_plan.steps:
        if command_demo_readiness_entry_for_argv(step.command_line, specs, launcher_argv) is None:
            raise ValueError(
                f"Command demo readiness shell command is not routeable: {step.flow_step}"
            )
        for engine_action, action_line in step.action_lines:
            entry = command_demo_readiness_entry_for_argv(action_line, specs, launcher_argv)
            if entry is None:
                raise ValueError(
                    f"Command demo readiness shell action is not routeable: {engine_action}"
                )
            if engine_action not in entry.engine_actions:
                raise ValueError(
                    f"Command demo readiness shell action routes to the wrong step: {engine_action}"
                )


def command_demo_readiness_shell_script_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_shell_script(specs, launcher_argv).lines


def command_demo_readiness_shell_executable_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return tuple(
        line
        for line in command_demo_readiness_shell_script_lines(specs, launcher_argv)
        if not line.startswith("#")
    )


def command_demo_readiness_shell_executable_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, str | None], ...]:
    entries: list[tuple[str, str, str, str | None]] = []
    for line in command_demo_readiness_shell_executable_lines(specs, launcher_argv):
        if line == "set -euo pipefail":
            continue
        validation = command_demo_readiness_validate_cli_argv(line, specs, launcher_argv)
        if validation.flow_step is None or validation.name is None:
            raise ValueError(f"Command demo readiness shell executable is not routeable: {line}")
        entries.append((line, validation.flow_step, validation.name, validation.exact_engine_action))
    return tuple(entries)


def command_demo_readiness_cli_smoke_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    seal = command_demo_readiness_seal(specs, launcher_argv)
    lines = _dedupe_command_lines((*seal.command_lines, *seal.cli_exact_action_lines))
    validation = command_demo_readiness_validate_cli_shell_script_lines(
        lines,
        specs,
        launcher_argv,
    )
    if not validation.is_complete:
        raise ValueError("Command demo readiness CLI smoke lines do not cover the MVP route")
    return lines


def command_demo_readiness_shell_script_text(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_shell_script(specs, launcher_argv).text


@lru_cache(maxsize=None)
def command_demo_readiness_trace_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessTraceContract:
    handoff_contract = command_demo_readiness_handoff_contract(specs, launcher_argv)
    exact_lines_by_action = dict(command_demo_readiness_exact_action_line_lookup_table(specs, launcher_argv))
    contract = CommandDemoReadinessTraceContract(
        entries=tuple(
            CommandDemoReadinessTraceEntry(
                ordinal=entry.ordinal,
                engine_action=engine_action,
                demo_path_step=entry.demo_path_step,
                flow_step=entry.flow_step,
                name=entry.name,
                command_line=entry.command_line,
                action_line=exact_lines_by_action[engine_action],
            )
            for entry in handoff_contract.entries
            for engine_action, _ in entry.action_lines
        )
    )
    _validate_command_demo_readiness_trace_contract(
        contract,
        handoff_contract,
        specs=specs,
        launcher_argv=launcher_argv,
    )
    return contract


def _validate_command_demo_readiness_trace_contract(
    contract: CommandDemoReadinessTraceContract,
    handoff_contract: CommandDemoReadinessHandoffContract,
    *,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    exact_lines_by_action = dict(command_demo_readiness_exact_action_line_lookup_table(specs, launcher_argv))
    expected_entries = tuple(
        (
            entry.ordinal,
            engine_action,
            entry.demo_path_step,
            entry.flow_step,
            entry.name,
            entry.command_line,
            exact_lines_by_action[engine_action],
        )
        for entry in handoff_contract.entries
        for engine_action, _ in entry.action_lines
    )
    actual_entries = tuple(
        (
            entry.ordinal,
            entry.engine_action,
            entry.demo_path_step,
            entry.flow_step,
            entry.name,
            entry.command_line,
            entry.action_line,
        )
        for entry in contract.entries
    )
    if actual_entries != expected_entries:
        raise ValueError("Command demo readiness trace entries are inconsistent")
    if tuple(entry.engine_action for entry in contract.entries) != command_demo_engine_actions(specs):
        raise ValueError("Command demo readiness trace action coverage is inconsistent")
    if len({entry.engine_action for entry in contract.entries}) != len(contract.entries):
        raise ValueError("Command demo readiness trace actions must be unique")
    if any(not entry.command_line or not entry.action_line for entry in contract.entries):
        raise ValueError("Command demo readiness trace lines must not be empty")
    for entry in contract.entries:
        if command_demo_readiness_exact_action_for_argv(
            entry.action_line,
            specs,
            launcher_argv,
        ) != entry.engine_action:
            raise ValueError(f"Command demo readiness trace exact route is inconsistent: {entry.engine_action}")


def command_demo_readiness_trace_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, str, str], ...]:
    return tuple(
        (
            entry.ordinal,
            entry.engine_action,
            entry.demo_path_step,
            entry.flow_step,
            entry.name,
            entry.command_line,
            entry.action_line,
        )
        for entry in command_demo_readiness_trace_contract(specs, launcher_argv).entries
    )


def command_demo_readiness_trace_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (entry.engine_action, entry.action_line)
        for entry in command_demo_readiness_trace_contract(specs, launcher_argv).entries
    )


def command_demo_readiness_trace_entry_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessTraceEntry | None:
    requested_action = engine_action.strip()
    if not requested_action:
        return None
    return next(
        (
            entry
            for entry in command_demo_readiness_trace_contract(specs, launcher_argv).entries
            if entry.engine_action == requested_action
        ),
        None,
    )


def command_demo_readiness_trace_entry_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessTraceEntry | None:
    exact_action = command_demo_readiness_exact_action_for_argv(argv, specs, launcher_argv)
    if exact_action is None:
        return None
    return command_demo_readiness_trace_entry_for_engine_action(
        exact_action,
        specs,
        launcher_argv,
    )


@lru_cache(maxsize=None)
def command_demo_readiness_command_trace_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessCommandTraceContract:
    handoff_contract = command_demo_readiness_handoff_contract(specs, launcher_argv)
    contract = CommandDemoReadinessCommandTraceContract(
        entries=tuple(
            CommandDemoReadinessCommandTraceEntry(
                ordinal=entry.ordinal,
                demo_path_step=entry.demo_path_step,
                flow_step=entry.flow_step,
                name=entry.name,
                command_line=entry.command_line,
                action_lines=entry.action_lines,
            )
            for entry in handoff_contract.entries
        )
    )
    _validate_command_demo_readiness_command_trace_contract(
        contract,
        handoff_contract,
        specs=specs,
    )
    return contract


def _validate_command_demo_readiness_command_trace_contract(
    contract: CommandDemoReadinessCommandTraceContract,
    handoff_contract: CommandDemoReadinessHandoffContract,
    *,
    specs: tuple[CommandSpec, ...],
) -> None:
    if tuple(entry.ordinal for entry in contract.entries) != tuple(
        entry.ordinal for entry in handoff_contract.entries
    ):
        raise ValueError("Command demo readiness command trace ordinals are inconsistent")
    if tuple(entry.demo_path_step for entry in contract.entries) != tuple(
        entry.demo_path_step for entry in handoff_contract.entries
    ):
        raise ValueError("Command demo readiness command trace path steps are inconsistent")
    if tuple(entry.flow_step for entry in contract.entries) != tuple(
        entry.flow_step for entry in handoff_contract.entries
    ):
        raise ValueError("Command demo readiness command trace flow steps are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(
        entry.name for entry in handoff_contract.entries
    ):
        raise ValueError("Command demo readiness command trace names are inconsistent")
    if tuple(entry.command_line for entry in contract.entries) != tuple(
        entry.command_line for entry in handoff_contract.entries
    ):
        raise ValueError("Command demo readiness command trace command lines are inconsistent")
    if tuple(entry.action_lines for entry in contract.entries) != tuple(
        entry.action_lines for entry in handoff_contract.entries
    ):
        raise ValueError("Command demo readiness command trace action lines are inconsistent")
    if tuple(entry.name for entry in contract.entries) != command_mvp_flow_names(specs):
        raise ValueError("Command demo readiness command trace command order is inconsistent")
    if any(not entry.command_line or not entry.action_lines for entry in contract.entries):
        raise ValueError("Command demo readiness command trace lines must not be empty")


def command_demo_readiness_command_trace_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, tuple[tuple[str, str], ...]], ...]:
    return tuple(
        (
            entry.ordinal,
            entry.demo_path_step,
            entry.flow_step,
            entry.name,
            entry.command_line,
            entry.action_lines,
        )
        for entry in command_demo_readiness_command_trace_contract(specs, launcher_argv).entries
    )


def command_demo_readiness_command_trace_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, tuple[tuple[str, str], ...]], ...]:
    return tuple(
        (entry.name, entry.action_lines)
        for entry in command_demo_readiness_command_trace_contract(specs, launcher_argv).entries
    )


@lru_cache(maxsize=None)
def command_demo_command_readiness_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoCommandReadinessContract:
    exact_lines_by_action = dict(command_demo_readiness_exact_action_line_lookup_table(specs, launcher_argv))
    cli_exact_lines_by_action = dict(command_demo_readiness_cli_exact_action_line_lookup_table(specs, launcher_argv))
    entries = tuple(
        CommandDemoCommandReadinessEntry(
            ordinal=entry.ordinal,
            demo_path_step=entry.demo_path_step,
            flow_step=entry.flow_step,
            name=entry.name,
            command_line=entry.command_line,
            engine_actions=tuple(action for action, _ in entry.action_lines),
            exact_action_lines=tuple(
                (action, exact_lines_by_action[action])
                for action, _ in entry.action_lines
                if action in exact_lines_by_action
            ),
            cli_exact_action_lines=tuple(
                (action, cli_exact_lines_by_action[action])
                for action, _ in entry.action_lines
                if action in cli_exact_lines_by_action
            ),
        )
        for entry in command_demo_readiness_command_trace_contract(specs, launcher_argv).entries
    )
    contract = CommandDemoCommandReadinessContract(entries=entries)
    _validate_command_demo_command_readiness_contract(contract)
    return contract


def _validate_command_demo_command_readiness_contract(
    contract: CommandDemoCommandReadinessContract,
) -> None:
    for entry in contract.entries:
        if not entry.command_line:
            raise ValueError(f"Command demo readiness command line is missing: {entry.name}")
        if not entry.engine_actions:
            raise ValueError(f"Command demo readiness engine actions are missing: {entry.name}")
        if tuple(action for action, _ in entry.exact_action_lines) != entry.engine_actions:
            raise ValueError(f"Command demo readiness exact action lines are incomplete: {entry.name}")
        if tuple(action for action, _ in entry.cli_exact_action_lines) != entry.engine_actions:
            raise ValueError(f"Command demo readiness CLI exact action lines are incomplete: {entry.name}")


def command_demo_command_readiness_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    tuple[
        int,
        str,
        str,
        str,
        str,
        tuple[str, ...],
        tuple[tuple[str, str], ...],
        tuple[tuple[str, str], ...],
    ],
    ...,
]:
    return tuple(
        (
            entry.ordinal,
            entry.demo_path_step,
            entry.flow_step,
            entry.name,
            entry.command_line,
            entry.engine_actions,
            entry.exact_action_lines,
            entry.cli_exact_action_lines,
        )
        for entry in command_demo_command_readiness_contract(specs, launcher_argv).entries
    )


def command_demo_command_readiness_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    return tuple(
        (entry.name, entry.command_line, entry.engine_actions)
        for entry in command_demo_command_readiness_contract(specs, launcher_argv).entries
    )


@lru_cache(maxsize=None)
def command_demo_command_surface_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoCommandSurfaceContract:
    readiness_by_name = dict(command_demo_readiness_index_by_command(specs, launcher_argv))
    exact_argv_by_action = {
        action: argv
        for argv, action in command_demo_readiness_exact_action_argv_lookup_table(
            specs,
            launcher_argv,
        )
    }
    entries: list[CommandDemoCommandSurfaceEntry] = []
    for readiness_entry in command_demo_command_readiness_contract(specs, launcher_argv).entries:
        command_entry = readiness_by_name.get(readiness_entry.name)
        if command_entry is None:
            raise ValueError(f"Missing command demo surface readiness entry: {readiness_entry.name}")
        entries.append(
            CommandDemoCommandSurfaceEntry(
                ordinal=readiness_entry.ordinal,
                demo_path_step=readiness_entry.demo_path_step,
                flow_step=readiness_entry.flow_step,
                name=readiness_entry.name,
                command_argv=command_entry.command_argv,
                command_line=readiness_entry.command_line,
                engine_actions=readiness_entry.engine_actions,
                exact_action_argv=tuple(
                    (action, exact_argv_by_action[action])
                    for action in readiness_entry.engine_actions
                    if action in exact_argv_by_action
                ),
                exact_action_lines=readiness_entry.exact_action_lines,
                cli_exact_action_lines=readiness_entry.cli_exact_action_lines,
            )
        )
    contract = CommandDemoCommandSurfaceContract(
        launcher_argv=launcher_argv,
        entries=tuple(entries),
    )
    _validate_command_demo_command_surface_contract(contract, specs, launcher_argv)
    return contract


def _validate_command_demo_command_surface_contract(
    contract: CommandDemoCommandSurfaceContract,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    if contract.launcher_argv != launcher_argv:
        raise ValueError("Command demo surface launcher is inconsistent")
    readiness_entries = command_demo_readiness_contract(specs, launcher_argv).entries
    command_entries = command_demo_command_readiness_contract(specs, launcher_argv).entries
    if tuple(entry.ordinal for entry in contract.entries) != tuple(entry.ordinal for entry in readiness_entries):
        raise ValueError("Command demo surface ordinals are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(entry.name for entry in command_entries):
        raise ValueError("Command demo surface command names are inconsistent")
    if tuple(entry.command_argv for entry in contract.entries) != tuple(
        entry.command_argv for entry in readiness_entries
    ):
        raise ValueError("Command demo surface command argv are inconsistent")
    if tuple(entry.command_line for entry in contract.entries) != tuple(
        entry.command_line for entry in command_entries
    ):
        raise ValueError("Command demo surface command lines are inconsistent")
    if tuple(entry.engine_actions for entry in contract.entries) != tuple(
        entry.engine_actions for entry in command_entries
    ):
        raise ValueError("Command demo surface engine actions are inconsistent")
    for entry, command_entry in zip(contract.entries, command_entries, strict=True):
        if tuple(action for action, _ in entry.exact_action_argv) != entry.engine_actions:
            raise ValueError(f"Command demo surface exact argv are incomplete: {entry.name}")
        if tuple(action for action, _ in entry.exact_action_lines) != entry.engine_actions:
            raise ValueError(f"Command demo surface exact lines are incomplete: {entry.name}")
        if entry.exact_action_lines != command_entry.exact_action_lines:
            raise ValueError(f"Command demo surface exact lines are inconsistent: {entry.name}")
        if entry.cli_exact_action_lines != command_entry.cli_exact_action_lines:
            raise ValueError(f"Command demo surface CLI exact lines are inconsistent: {entry.name}")
        for engine_action, argv in entry.exact_action_argv:
            if command_demo_readiness_exact_action_for_argv(argv, specs, launcher_argv) != engine_action:
                raise ValueError(f"Command demo surface exact argv is not routeable: {engine_action}")


def command_demo_command_surface_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    tuple[
        int,
        str,
        str,
        str,
        tuple[str, ...],
        str,
        tuple[str, ...],
        tuple[tuple[str, tuple[str, ...]], ...],
        tuple[tuple[str, str], ...],
        tuple[tuple[str, str], ...],
    ],
    ...,
]:
    return tuple(
        (
            entry.ordinal,
            entry.demo_path_step,
            entry.flow_step,
            entry.name,
            entry.command_argv,
            entry.command_line,
            entry.engine_actions,
            entry.exact_action_argv,
            entry.exact_action_lines,
            entry.cli_exact_action_lines,
        )
        for entry in command_demo_command_surface_contract(specs, launcher_argv).entries
    )


def command_demo_command_surface_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...]:
    return tuple(
        (entry.name, entry.command_argv, entry.engine_actions)
        for entry in command_demo_command_surface_contract(specs, launcher_argv).entries
    )


@lru_cache(maxsize=None)
def command_demo_command_coverage_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoCommandCoverageContract:
    entries = tuple(
        CommandDemoCommandCoverageEntry(
            ordinal=entry.ordinal,
            demo_path_step=entry.demo_path_step,
            flow_step=entry.flow_step,
            name=entry.name,
            command_line=entry.command_line,
            required_engine_actions=entry.engine_actions,
            covered_engine_actions=tuple(action for action, _ in entry.exact_action_lines),
            missing_engine_actions=tuple(
                action
                for action in entry.engine_actions
                if action not in {covered_action for covered_action, _ in entry.exact_action_lines}
            ),
            is_complete=tuple(action for action, _ in entry.exact_action_lines) == entry.engine_actions,
        )
        for entry in command_demo_command_surface_contract(specs, launcher_argv).entries
    )
    contract = CommandDemoCommandCoverageContract(entries=entries)
    _validate_command_demo_command_coverage_contract(contract, specs, launcher_argv)
    return contract


def _validate_command_demo_command_coverage_contract(
    contract: CommandDemoCommandCoverageContract,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    surface_entries = command_demo_command_surface_contract(specs, launcher_argv).entries
    if tuple(entry.ordinal for entry in contract.entries) != tuple(entry.ordinal for entry in surface_entries):
        raise ValueError("Command demo coverage ordinals are inconsistent")
    if tuple(entry.demo_path_step for entry in contract.entries) != tuple(
        entry.demo_path_step for entry in surface_entries
    ):
        raise ValueError("Command demo coverage path steps are inconsistent")
    if tuple(entry.flow_step for entry in contract.entries) != tuple(entry.flow_step for entry in surface_entries):
        raise ValueError("Command demo coverage flow steps are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(entry.name for entry in surface_entries):
        raise ValueError("Command demo coverage names are inconsistent")
    if tuple(entry.command_line for entry in contract.entries) != tuple(
        entry.command_line for entry in surface_entries
    ):
        raise ValueError("Command demo coverage command lines are inconsistent")
    for entry, surface_entry in zip(contract.entries, surface_entries, strict=True):
        if entry.required_engine_actions != surface_entry.engine_actions:
            raise ValueError(f"Command demo coverage required actions are inconsistent: {entry.name}")
        if entry.covered_engine_actions != tuple(action for action, _ in surface_entry.exact_action_lines):
            raise ValueError(f"Command demo coverage covered actions are inconsistent: {entry.name}")
        expected_missing = tuple(
            action
            for action in entry.required_engine_actions
            if action not in set(entry.covered_engine_actions)
        )
        if entry.missing_engine_actions != expected_missing:
            raise ValueError(f"Command demo coverage missing actions are inconsistent: {entry.name}")
        if entry.is_complete != (not entry.missing_engine_actions):
            raise ValueError(f"Command demo coverage completion state is inconsistent: {entry.name}")


def command_demo_command_coverage_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, tuple[str, ...], tuple[str, ...], tuple[str, ...], bool], ...]:
    return tuple(
        (
            entry.ordinal,
            entry.demo_path_step,
            entry.flow_step,
            entry.name,
            entry.command_line,
            entry.required_engine_actions,
            entry.covered_engine_actions,
            entry.missing_engine_actions,
            entry.is_complete,
        )
        for entry in command_demo_command_coverage_contract(specs, launcher_argv).entries
    )


def command_demo_command_coverage_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, bool, tuple[str, ...]], ...]:
    return tuple(
        (entry.name, entry.is_complete, entry.covered_engine_actions)
        for entry in command_demo_command_coverage_contract(specs, launcher_argv).entries
    )


@lru_cache(maxsize=None)
def _command_demo_command_coverage_entry_for_flow_step(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    flow_step: str,
) -> CommandDemoCommandCoverageEntry | None:
    requested_flow_step = _normalize_token(flow_step)
    if not requested_flow_step:
        return None
    return next(
        (
            entry
            for entry in command_demo_command_coverage_contract(specs, launcher_argv).entries
            if entry.flow_step == requested_flow_step
        ),
        None,
    )


def command_demo_command_coverage_entry_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoCommandCoverageEntry | None:
    return _command_demo_command_coverage_entry_for_flow_step(
        specs,
        launcher_argv,
        flow_step,
    )


@lru_cache(maxsize=None)
def _command_demo_command_coverage_entry_for_demo_path_step(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    demo_path_step: str,
) -> CommandDemoCommandCoverageEntry | None:
    requested_demo_path_step = _normalize_token(demo_path_step)
    if not requested_demo_path_step:
        return None
    return next(
        (
            entry
            for entry in command_demo_command_coverage_contract(specs, launcher_argv).entries
            if _normalize_token(entry.demo_path_step) == requested_demo_path_step
        ),
        None,
    )


def command_demo_command_coverage_entry_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoCommandCoverageEntry | None:
    return _command_demo_command_coverage_entry_for_demo_path_step(
        specs,
        launcher_argv,
        demo_path_step,
    )


def command_demo_command_coverage_is_complete_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> bool:
    entry = command_demo_command_coverage_entry_for_demo_path_step(
        demo_path_step,
        specs,
        launcher_argv,
    )
    return entry is not None and entry.is_complete


def command_demo_command_coverage_missing_actions_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    entry = command_demo_command_coverage_entry_for_demo_path_step(
        demo_path_step,
        specs,
        launcher_argv,
    )
    if entry is None:
        return ()
    return entry.missing_engine_actions


def command_mvp_demo_command_readiness_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoCommandReadinessContract:
    return command_demo_command_readiness_contract(specs, launcher_argv)


def command_mvp_demo_command_readiness_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    tuple[
        int,
        str,
        str,
        str,
        str,
        tuple[str, ...],
        tuple[tuple[str, str], ...],
        tuple[tuple[str, str], ...],
    ],
    ...,
]:
    return command_demo_command_readiness_summary(specs, launcher_argv)


def command_mvp_demo_command_readiness_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    return command_demo_command_readiness_lookup_table(specs, launcher_argv)


def command_mvp_demo_command_surface_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoCommandSurfaceContract:
    return command_demo_command_surface_contract(specs, launcher_argv)


def command_mvp_demo_command_surface_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    tuple[
        int,
        str,
        str,
        str,
        tuple[str, ...],
        str,
        tuple[str, ...],
        tuple[tuple[str, tuple[str, ...]], ...],
        tuple[tuple[str, str], ...],
        tuple[tuple[str, str], ...],
    ],
    ...,
]:
    return command_demo_command_surface_summary(specs, launcher_argv)


def command_mvp_demo_command_surface_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...]:
    return command_demo_command_surface_lookup_table(specs, launcher_argv)


def command_mvp_demo_command_coverage_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoCommandCoverageContract:
    return command_demo_command_coverage_contract(specs, launcher_argv)


def command_mvp_demo_command_coverage_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, tuple[str, ...], tuple[str, ...], tuple[str, ...], bool], ...]:
    return command_demo_command_coverage_summary(specs, launcher_argv)


def command_mvp_demo_command_coverage_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, bool, tuple[str, ...]], ...]:
    return command_demo_command_coverage_lookup_table(specs, launcher_argv)


def command_mvp_demo_command_coverage_entry_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoCommandCoverageEntry | None:
    return command_demo_command_coverage_entry_for_flow_step(
        flow_step,
        specs,
        launcher_argv,
    )


def command_mvp_demo_command_coverage_entry_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoCommandCoverageEntry | None:
    return command_demo_command_coverage_entry_for_demo_path_step(
        demo_path_step,
        specs,
        launcher_argv,
    )


def command_mvp_demo_command_coverage_is_complete_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> bool:
    return command_demo_command_coverage_is_complete_for_demo_path_step(
        demo_path_step,
        specs,
        launcher_argv,
    )


def command_mvp_demo_command_coverage_missing_actions_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_command_coverage_missing_actions_for_demo_path_step(
        demo_path_step,
        specs,
        launcher_argv,
    )


@lru_cache(maxsize=None)
def command_demo_supported_launcher_readiness_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoSupportedLauncherReadinessContract:
    entries: list[CommandDemoSupportedLauncherReadinessEntry] = []
    for launcher_argv in command_demo_supported_launcher_argv():
        gate = command_demo_readiness_gate(specs, launcher_argv)
        exact_action_lines = command_demo_readiness_exact_action_line_lookup_table(
            specs,
            launcher_argv,
        )
        cli_smoke_lines = command_demo_readiness_cli_smoke_lines(
            specs,
            launcher_argv,
        )
        entries.append(
            CommandDemoSupportedLauncherReadinessEntry(
                launcher_argv=launcher_argv,
                is_complete=gate.is_complete,
                missing_engine_actions=gate.missing_engine_actions,
                command_lines=gate.command_lines,
                action_lines=gate.action_lines,
                exact_action_lines=exact_action_lines,
                cli_smoke_lines=cli_smoke_lines,
            )
        )
    contract = CommandDemoSupportedLauncherReadinessContract(
        entries=tuple(entries)
    )
    _validate_command_demo_supported_launcher_readiness_contract(contract, specs)
    return contract


def _validate_command_demo_supported_launcher_readiness_contract(
    contract: CommandDemoSupportedLauncherReadinessContract,
    specs: tuple[CommandSpec, ...],
) -> None:
    if tuple(entry.launcher_argv for entry in contract.entries) != command_demo_supported_launcher_argv():
        raise ValueError("Command demo supported launcher order is inconsistent")
    for entry in contract.entries:
        _validate_command_smoke_cli_launcher(entry.launcher_argv)
        gate = require_command_demo_readiness_complete(specs, entry.launcher_argv)
        if not entry.is_complete:
            raise ValueError("Command demo supported launcher readiness must be complete")
        if entry.missing_engine_actions:
            raise ValueError("Command demo supported launcher actions must not be missing")
        if entry.is_complete != gate.is_complete:
            raise ValueError("Command demo supported launcher readiness is inconsistent")
        if entry.missing_engine_actions != gate.missing_engine_actions:
            raise ValueError("Command demo supported launcher missing actions are inconsistent")
        if entry.command_lines != gate.command_lines:
            raise ValueError("Command demo supported launcher commands are inconsistent")
        if entry.action_lines != gate.action_lines:
            raise ValueError("Command demo supported launcher actions are inconsistent")
        expected_exact_action_lines = command_demo_readiness_exact_action_line_lookup_table(
            specs,
            entry.launcher_argv,
        )
        if entry.exact_action_lines != expected_exact_action_lines:
            raise ValueError("Command demo supported launcher exact actions are inconsistent")
        if not entry.command_lines:
            raise ValueError("Command demo supported launcher commands must not be empty")
        if not entry.action_lines:
            raise ValueError("Command demo supported launcher actions must not be empty")
        expected_cli_smoke_lines = command_demo_readiness_cli_smoke_lines(
            specs,
            entry.launcher_argv,
        )
        if entry.cli_smoke_lines != expected_cli_smoke_lines:
            raise ValueError("Command demo supported launcher CLI smoke lines are inconsistent")
        if not entry.cli_smoke_lines:
            raise ValueError("Command demo supported launcher CLI smoke lines must not be empty")
        cli_smoke_validation = command_demo_readiness_validate_cli_shell_script_lines(
            entry.cli_smoke_lines,
            specs,
            entry.launcher_argv,
        )
        if not cli_smoke_validation.is_complete:
            raise ValueError("Command demo supported launcher CLI smoke lines must cover the MVP route")
        exact_validation = command_demo_readiness_validate_cli_exact_action_shell_script_lines(
            tuple(line for _, line in entry.exact_action_lines),
            specs,
            entry.launcher_argv,
        )
        if not exact_validation.is_complete:
            raise ValueError("Command demo supported launcher exact actions must cover the MVP loop")


def command_demo_supported_launcher_readiness_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[tuple[str, ...], bool, tuple[str, ...], tuple[str, ...], tuple[tuple[str, str], ...]], ...]:
    return tuple(
        (
            entry.launcher_argv,
            entry.is_complete,
            entry.missing_engine_actions,
            entry.command_lines,
            entry.action_lines,
        )
        for entry in command_demo_supported_launcher_readiness_contract(specs).entries
    )


def command_demo_supported_launcher_readiness_audit_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[
    tuple[
        tuple[str, ...],
        bool,
        tuple[str, ...],
        tuple[str, ...],
        tuple[tuple[str, str], ...],
        tuple[str, ...],
    ],
    ...,
]:
    return tuple(
        (
            entry.launcher_argv,
            entry.is_complete,
            entry.missing_engine_actions,
            entry.command_lines,
            entry.exact_action_lines,
            entry.cli_smoke_lines,
        )
        for entry in command_demo_supported_launcher_readiness_contract(specs).entries
    )


def command_demo_supported_launcher_readiness_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]:
    return tuple(
        (entry.launcher_argv, entry.command_lines)
        for entry in command_demo_supported_launcher_readiness_contract(specs).entries
    )


def command_demo_supported_launcher_exact_action_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[tuple[str, ...], tuple[tuple[str, str], ...]], ...]:
    return tuple(
        (entry.launcher_argv, entry.exact_action_lines)
        for entry in command_demo_supported_launcher_readiness_contract(specs).entries
    )


def command_demo_supported_launcher_cli_smoke_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]:
    return tuple(
        (entry.launcher_argv, entry.cli_smoke_lines)
        for entry in command_demo_supported_launcher_readiness_contract(specs).entries
    )


def command_mvp_demo_supported_launcher_readiness_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoSupportedLauncherReadinessContract:
    return command_demo_supported_launcher_readiness_contract(specs)


def command_mvp_demo_supported_launcher_readiness_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[tuple[str, ...], bool, tuple[str, ...], tuple[str, ...], tuple[tuple[str, str], ...]], ...]:
    return command_demo_supported_launcher_readiness_summary(specs)


def command_mvp_demo_supported_launcher_readiness_audit_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[
    tuple[
        tuple[str, ...],
        bool,
        tuple[str, ...],
        tuple[str, ...],
        tuple[tuple[str, str], ...],
        tuple[str, ...],
    ],
    ...,
]:
    return command_demo_supported_launcher_readiness_audit_summary(specs)


def command_mvp_demo_supported_launcher_readiness_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]:
    return command_demo_supported_launcher_readiness_lookup_table(specs)


def command_mvp_demo_supported_launcher_exact_action_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[tuple[str, ...], tuple[tuple[str, str], ...]], ...]:
    return command_demo_supported_launcher_exact_action_lookup_table(specs)


def command_mvp_demo_supported_launcher_cli_smoke_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]:
    return command_demo_supported_launcher_cli_smoke_lookup_table(specs)


def command_demo_readiness_command_trace_entry_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessCommandTraceEntry | None:
    requested_action = engine_action.strip()
    if not requested_action:
        return None
    return next(
        (
            entry
            for entry in command_demo_readiness_command_trace_contract(specs, launcher_argv).entries
            if any(action == requested_action for action, _ in entry.action_lines)
        ),
        None,
    )


def command_demo_readiness_command_trace_entry_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessCommandTraceEntry | None:
    readiness_entry = command_demo_readiness_entry_for_argv(argv, specs, launcher_argv)
    if readiness_entry is None:
        return None
    return next(
        (
            entry
            for entry in command_demo_readiness_command_trace_contract(specs, launcher_argv).entries
            if entry.flow_step == readiness_entry.flow_step
        ),
        None,
    )


@lru_cache(maxsize=None)
def command_demo_readiness_action_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, CommandDemoReadinessActionEntry], ...]:
    return tuple(
        (entry.engine_action, entry)
        for entry in command_demo_readiness_action_contract(specs, launcher_argv).entries
    )


def command_demo_readiness_action_entry(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessActionEntry | None:
    requested_action = engine_action.strip()
    if not requested_action:
        return None
    return dict(command_demo_readiness_action_index(specs, launcher_argv)).get(requested_action)


@lru_cache(maxsize=None)
def _command_demo_readiness_action_entries_for_argv(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    argv: tuple[str, ...],
) -> tuple[CommandDemoReadinessActionEntry, ...]:
    requested_argv = _normalize_smoke_argv(argv)
    if not requested_argv:
        return ()
    requested_command_argv = _argv_without_launcher(requested_argv, launcher_argv)
    requested_command_argv = _normalize_implicit_bootstrap_argv(specs, requested_command_argv)
    requested_canonical_command_argv = _canonicalize_smoke_command_argv(specs, requested_command_argv)
    matches: list[CommandDemoReadinessActionEntry] = []
    for entry in command_demo_readiness_action_contract(specs, launcher_argv).entries:
        action_argv = _argv_without_launcher(entry.action_command_argv, launcher_argv)
        if (
            _smoke_argv_matches(requested_argv, entry.action_command_argv)
            or _smoke_argv_matches(requested_command_argv, action_argv)
            or _smoke_argv_matches(requested_canonical_command_argv, action_argv)
        ):
            matches.append(entry)
    return tuple(matches)


def command_demo_readiness_action_entries_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[CommandDemoReadinessActionEntry, ...]:
    return _command_demo_readiness_action_entries_for_argv(
        specs,
        launcher_argv,
        _coerce_smoke_argv(argv),
    )


@lru_cache(maxsize=None)
def command_demo_readiness_exact_action_argv_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[tuple[str, ...], str], ...]:
    _validate_command_smoke_cli_launcher(launcher_argv)
    exact_argv_by_action = _demo_exact_action_smoke_argv_by_engine_action(specs)
    return tuple(
        ((*launcher_argv, *exact_argv_by_action[engine_action]), engine_action)
        for engine_action in command_demo_engine_actions(specs)
    )


def command_demo_readiness_cli_exact_action_argv_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[tuple[str, ...], str], ...]:
    lookup = command_demo_readiness_exact_action_argv_lookup_table(specs, launcher_argv)
    invalid_entries: list[str] = []
    for argv, engine_action in lookup:
        validation = command_demo_readiness_validate_cli_argv(argv, specs, launcher_argv)
        if not validation.is_cli_entrypoint or validation.exact_engine_action != engine_action:
            invalid_entries.append(_shell_join(argv))
    if invalid_entries:
        raise ValueError(
            "Command demo CLI exact action argv are inconsistent: "
            + "; ".join(invalid_entries)
        )
    return lookup


def command_demo_readiness_exact_action_line_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (engine_action, _shell_join(argv))
        for argv, engine_action in command_demo_readiness_exact_action_argv_lookup_table(
            specs,
            launcher_argv,
        )
    )


def command_demo_readiness_cli_exact_action_line_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (engine_action, _shell_join(argv))
        for argv, engine_action in command_demo_readiness_cli_exact_action_argv_lookup_table(
            specs,
            launcher_argv,
        )
    )


def command_demo_readiness_cli_exact_argv_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    requested_action = engine_action.strip()
    if not requested_action:
        return ()
    return {
        action: argv
        for argv, action in command_demo_readiness_cli_exact_action_argv_lookup_table(
            specs,
            launcher_argv,
        )
    }.get(requested_action, ())


def command_demo_readiness_cli_exact_line_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    argv = command_demo_readiness_cli_exact_argv_for_engine_action(
        engine_action,
        specs,
        launcher_argv,
    )
    if not argv:
        return ""
    return _shell_join(argv)


def command_demo_readiness_exact_action_shell_script_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    lines = tuple(
        line
        for _, line in command_demo_readiness_exact_action_line_lookup_table(
            specs,
            launcher_argv,
        )
    )
    validation = command_demo_readiness_validate_exact_action_shell_script_lines(
        lines,
        specs,
        launcher_argv,
    )
    if not validation.is_complete:
        raise ValueError("Command demo exact action script does not cover the MVP loop")
    return lines


def command_demo_readiness_exact_action_shell_script_text(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return "\n".join(
        command_demo_readiness_exact_action_shell_script_lines(
            specs,
            launcher_argv,
        )
    )


def command_demo_readiness_cli_exact_action_shell_script_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    lines = tuple(
        line
        for _, line in command_demo_readiness_cli_exact_action_line_lookup_table(
            specs,
            launcher_argv,
        )
    )
    validation = command_demo_readiness_validate_cli_exact_action_shell_script_lines(
        lines,
        specs,
        launcher_argv,
    )
    if not validation.is_complete:
        raise ValueError("Command demo CLI exact action script does not cover the MVP loop")
    return lines


def command_demo_readiness_cli_exact_action_shell_script_text(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return "\n".join(
        command_demo_readiness_cli_exact_action_shell_script_lines(
            specs,
            launcher_argv,
        )
    )


def command_demo_readiness_exact_action_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    requested_argv = _normalize_smoke_argv(_coerce_smoke_argv(argv))
    if not requested_argv:
        return None
    requested_launcher_argv = _detected_launcher_argv(requested_argv)
    requested_command_argv = _argv_without_launcher(requested_argv, launcher_argv)
    requested_command_argv = _normalize_implicit_bootstrap_argv(specs, requested_command_argv)
    requested_canonical_command_argv = _canonicalize_exact_action_command_argv(
        specs,
        requested_command_argv,
    )
    lookup = dict(command_demo_readiness_exact_action_argv_lookup_table(specs, launcher_argv))
    for action_argv, engine_action in lookup.items():
        action_command_argv = _argv_without_launcher(action_argv, launcher_argv)
        canonical_action_argv = _canonical_argv_with_requested_launcher(action_argv, requested_launcher_argv)
        if (
            _exact_action_argv_matches(requested_argv, action_argv)
            or _exact_action_argv_matches(requested_argv, action_command_argv)
            or _exact_action_argv_matches(requested_argv, canonical_action_argv)
        ):
            return engine_action
        if _exact_action_argv_matches(requested_canonical_command_argv, action_command_argv):
            return engine_action
    return None


def command_demo_readiness_cli_exact_action_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    validation = command_demo_readiness_validate_cli_argv(argv, specs, launcher_argv)
    if not validation.is_cli_entrypoint:
        return None
    return validation.exact_engine_action


def command_demo_readiness_exact_action_entry_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessExactActionEntry | None:
    engine_action = command_demo_readiness_exact_action_for_argv(argv, specs, launcher_argv)
    if engine_action is None:
        return None
    command_argv = command_demo_readiness_exact_argv_for_engine_action(
        engine_action,
        specs,
        launcher_argv,
    )
    action_entry = command_demo_readiness_action_entry(engine_action, specs, launcher_argv)
    if action_entry is None or not command_argv:
        return None
    return CommandDemoReadinessExactActionEntry(
        engine_action=engine_action,
        flow_step=action_entry.flow_step,
        name=action_entry.name,
        command_argv=command_argv,
        command_line=_shell_join(command_argv),
        demo_path_step=action_entry.demo_path_step,
    )


def _canonicalize_exact_action_command_argv(
    specs: tuple[CommandSpec, ...],
    argv: tuple[str, ...],
) -> tuple[str, ...]:
    if specs != COMMAND_SPECS:
        return _canonicalize_smoke_command_argv(specs, argv)
    if not argv:
        return ()
    parser_token = _normalize_token(_strip_command_palette_prefix(argv[0]))
    if parser_token not in dict(command_cli_lookup_table()):
        return ()
    return _canonicalize_smoke_command_argv(specs, argv)


def command_demo_readiness_exact_argv_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    requested_action = engine_action.strip()
    if not requested_action:
        return ()
    return {
        action: argv
        for argv, action in command_demo_readiness_exact_action_argv_lookup_table(
            specs,
            launcher_argv,
        )
    }.get(requested_action, ())


def command_demo_readiness_exact_line_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    argv = command_demo_readiness_exact_argv_for_engine_action(
        engine_action,
        specs,
        launcher_argv,
    )
    if not argv:
        return ""
    return _shell_join(argv)


@lru_cache(maxsize=None)
def command_demo_readiness_exact_action_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessExactActionContract:
    action_entries = dict(command_demo_readiness_action_index(specs, launcher_argv))
    entries: list[CommandDemoReadinessExactActionEntry] = []
    for argv, engine_action in command_demo_readiness_exact_action_argv_lookup_table(
        specs,
        launcher_argv,
    ):
        action_entry = action_entries.get(engine_action)
        if action_entry is None:
            raise ValueError(f"Missing command demo readiness action: {engine_action}")
        entries.append(
            CommandDemoReadinessExactActionEntry(
                engine_action=engine_action,
                flow_step=action_entry.flow_step,
                name=action_entry.name,
                command_argv=argv,
                command_line=_shell_join(argv),
                demo_path_step=action_entry.demo_path_step,
            )
        )
    contract = CommandDemoReadinessExactActionContract(entries=tuple(entries))
    _validate_command_demo_readiness_exact_action_contract(contract, specs, launcher_argv)
    return contract


def _validate_command_demo_readiness_exact_action_contract(
    contract: CommandDemoReadinessExactActionContract,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    expected_actions = command_demo_engine_actions(specs)
    if tuple(entry.engine_action for entry in contract.entries) != expected_actions:
        raise ValueError("Command demo exact action entries are inconsistent")
    if tuple(entry.command_argv for entry in contract.entries) != tuple(
        argv
        for argv, _ in command_demo_readiness_exact_action_argv_lookup_table(
            specs,
            launcher_argv,
        )
    ):
        raise ValueError("Command demo exact action argv entries are inconsistent")
    if tuple((entry.engine_action, entry.command_line) for entry in contract.entries) != (
        command_demo_readiness_exact_action_line_lookup_table(specs, launcher_argv)
    ):
        raise ValueError("Command demo exact action lines are inconsistent")

    readiness_entries = {
        entry.engine_action: entry
        for entry in command_demo_readiness_action_contract(specs, launcher_argv).entries
    }
    for entry in contract.entries:
        readiness_entry = readiness_entries.get(entry.engine_action)
        if readiness_entry is None:
            raise ValueError(f"Missing command demo readiness action: {entry.engine_action}")
        if entry.flow_step != readiness_entry.flow_step:
            raise ValueError(f"Command demo exact action flow step is inconsistent: {entry.engine_action}")
        if entry.name != readiness_entry.name:
            raise ValueError(f"Command demo exact action command is inconsistent: {entry.engine_action}")
        if entry.demo_path_step != readiness_entry.demo_path_step:
            raise ValueError(f"Command demo exact action path step is inconsistent: {entry.engine_action}")
        if command_demo_readiness_exact_action_for_argv(
            entry.command_argv,
            specs,
            launcher_argv,
        ) != entry.engine_action:
            raise ValueError(f"Command demo exact action argv does not round trip: {entry.engine_action}")


def command_demo_readiness_exact_action_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, str, str], ...]:
    return tuple(
        (
            entry.engine_action,
            entry.flow_step,
            entry.name,
            entry.command_line,
            entry.demo_path_step,
        )
        for entry in command_demo_readiness_exact_action_contract(specs, launcher_argv).entries
    )


@lru_cache(maxsize=None)
def command_demo_readiness_exact_cli_audit_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessExactCliAuditContract:
    entries = tuple(
        _command_demo_readiness_exact_cli_audit_entry(entry, specs, launcher_argv)
        for entry in command_demo_readiness_exact_action_contract(specs, launcher_argv).entries
    )
    invalid_engine_actions = tuple(
        entry.engine_action
        for entry in entries
        if not entry.is_cli_entrypoint or entry.command_line != entry.canonical_command_line
    )
    contract = CommandDemoReadinessExactCliAuditContract(
        is_complete=not invalid_engine_actions,
        entries=entries,
        invalid_engine_actions=invalid_engine_actions,
    )
    _validate_command_demo_readiness_exact_cli_audit_contract(contract, specs, launcher_argv)
    return contract


def _command_demo_readiness_exact_cli_audit_entry(
    entry: CommandDemoReadinessExactActionEntry,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> CommandDemoReadinessExactCliAuditEntry:
    validation = command_demo_readiness_validate_cli_argv(
        entry.command_argv,
        specs,
        launcher_argv,
    )
    return CommandDemoReadinessExactCliAuditEntry(
        engine_action=entry.engine_action,
        flow_step=entry.flow_step,
        name=entry.name,
        parser_token=validation.parser_token or "",
        command_line=entry.command_line,
        canonical_command_line=validation.command_line,
        demo_path_step=entry.demo_path_step,
        is_cli_entrypoint=(
            validation.is_cli_entrypoint
            and validation.name == entry.name
            and validation.flow_step == entry.flow_step
            and validation.demo_path_step == entry.demo_path_step
            and validation.exact_engine_action == entry.engine_action
        ),
    )


def _validate_command_demo_readiness_exact_cli_audit_contract(
    contract: CommandDemoReadinessExactCliAuditContract,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    exact_contract = command_demo_readiness_exact_action_contract(specs, launcher_argv)
    if tuple(entry.engine_action for entry in contract.entries) != tuple(
        entry.engine_action for entry in exact_contract.entries
    ):
        raise ValueError("Command demo exact CLI audit actions are inconsistent")
    if tuple(entry.flow_step for entry in contract.entries) != tuple(
        entry.flow_step for entry in exact_contract.entries
    ):
        raise ValueError("Command demo exact CLI audit flow steps are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(
        entry.name for entry in exact_contract.entries
    ):
        raise ValueError("Command demo exact CLI audit command names are inconsistent")
    if tuple(entry.demo_path_step for entry in contract.entries) != tuple(
        entry.demo_path_step for entry in exact_contract.entries
    ):
        raise ValueError("Command demo exact CLI audit path steps are inconsistent")
    if tuple(entry.command_line for entry in contract.entries) != tuple(
        entry.command_line for entry in exact_contract.entries
    ):
        raise ValueError("Command demo exact CLI audit command lines are inconsistent")
    if len({entry.engine_action for entry in contract.entries}) != len(contract.entries):
        raise ValueError("Command demo exact CLI audit actions must be unique")
    for entry in contract.entries:
        if not entry.parser_token:
            raise ValueError(f"Command demo exact CLI audit parser token is missing: {entry.engine_action}")
        if not entry.is_cli_entrypoint:
            raise ValueError(f"Command demo exact CLI audit entry is not parser-backed: {entry.engine_action}")
        if entry.command_line != entry.canonical_command_line:
            raise ValueError(f"Command demo exact CLI audit line drift: {entry.engine_action}")
    if contract.invalid_engine_actions:
        raise ValueError("Command demo exact CLI audit must not report invalid actions")
    if not contract.is_complete:
        raise ValueError("Command demo exact CLI audit must be complete")


def command_demo_readiness_exact_cli_audit_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, str, str, str, bool], ...]:
    return tuple(
        (
            entry.engine_action,
            entry.flow_step,
            entry.name,
            entry.parser_token,
            entry.command_line,
            entry.demo_path_step,
            entry.is_cli_entrypoint,
        )
        for entry in command_demo_readiness_exact_cli_audit_contract(
            specs,
            launcher_argv,
        ).entries
    )


@lru_cache(maxsize=None)
def command_demo_readiness_exact_action_script_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessExactActionScriptContract:
    contract = CommandDemoReadinessExactActionScriptContract(
        steps=tuple(
            CommandDemoReadinessExactActionScriptStep(
                ordinal=index,
                engine_action=entry.engine_action,
                flow_step=entry.flow_step,
                name=entry.name,
                command_argv=entry.command_argv,
                command_line=entry.command_line,
                demo_path_step=entry.demo_path_step,
            )
            for index, entry in enumerate(
                command_demo_readiness_exact_action_contract(
                    specs,
                    launcher_argv,
                ).entries,
                start=1,
            )
        )
    )
    _validate_command_demo_readiness_exact_action_script_contract(contract, specs, launcher_argv)
    return contract


def _validate_command_demo_readiness_exact_action_script_contract(
    contract: CommandDemoReadinessExactActionScriptContract,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> None:
    exact_contract = command_demo_readiness_exact_action_contract(specs, launcher_argv)
    if tuple(step.ordinal for step in contract.steps) != tuple(range(1, len(contract.steps) + 1)):
        raise ValueError("Command demo exact action script ordinals are inconsistent")
    if tuple(step.engine_action for step in contract.steps) != tuple(
        entry.engine_action for entry in exact_contract.entries
    ):
        raise ValueError("Command demo exact action script actions are inconsistent")
    if tuple(step.command_argv for step in contract.steps) != tuple(
        entry.command_argv for entry in exact_contract.entries
    ):
        raise ValueError("Command demo exact action script argv entries are inconsistent")
    if tuple(step.command_line for step in contract.steps) != tuple(
        entry.command_line for entry in exact_contract.entries
    ):
        raise ValueError("Command demo exact action script lines are inconsistent")

    validation = command_demo_readiness_validate_exact_action_script(
        tuple(step.command_argv for step in contract.steps),
        specs,
        launcher_argv,
    )
    if not validation.is_complete:
        raise ValueError("Command demo exact action script contract does not cover the MVP loop")


def command_demo_readiness_exact_action_script_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, str], ...]:
    return tuple(
        (
            step.ordinal,
            step.engine_action,
            step.flow_step,
            step.name,
            step.command_line,
            step.demo_path_step,
        )
        for step in command_demo_readiness_exact_action_script_contract(
            specs,
            launcher_argv,
        ).steps
    )


def command_demo_readiness_engine_action_matches_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return tuple(
        entry.engine_action
        for entry in command_demo_readiness_action_entries_for_argv(argv, specs, launcher_argv)
    )


def command_demo_readiness_action_lines_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (entry.engine_action, _shell_join(entry.action_command_argv))
        for entry in command_demo_readiness_action_entries_for_argv(argv, specs, launcher_argv)
    )


def command_demo_readiness_entry_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessEntry | None:
    action_entry = command_demo_readiness_action_entry(engine_action, specs, launcher_argv)
    if action_entry is None:
        return None
    return command_demo_readiness_entry_for_flow_step(action_entry.flow_step, specs, launcher_argv)


@lru_cache(maxsize=None)
def command_demo_readiness_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, CommandDemoReadinessEntry], ...]:
    return tuple(
        (entry.flow_step, entry)
        for entry in command_demo_readiness_contract(specs, launcher_argv).entries
    )


@lru_cache(maxsize=None)
def _command_demo_readiness_entry_for_flow_step(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    flow_step: str,
) -> CommandDemoReadinessEntry | None:
    requested_flow_step = _normalize_token(flow_step)
    if not requested_flow_step:
        return None
    return dict(command_demo_readiness_index(specs, launcher_argv)).get(requested_flow_step)


def command_demo_readiness_entry_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessEntry | None:
    return _command_demo_readiness_entry_for_flow_step(specs, launcher_argv, flow_step)


def command_demo_readiness_argv_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    entry = command_demo_readiness_entry_for_flow_step(flow_step, specs, launcher_argv)
    if entry is None:
        return ()
    return entry.command_argv


def command_demo_readiness_line_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    argv = command_demo_readiness_argv_for_flow_step(flow_step, specs, launcher_argv)
    if not argv:
        return ""
    return _shell_join(argv)


def command_demo_readiness_command_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    entry = command_demo_readiness_entry_for_flow_step(flow_step, specs, launcher_argv)
    if entry is None:
        return None
    return entry.name


@lru_cache(maxsize=None)
def command_demo_readiness_index_by_command(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, CommandDemoReadinessEntry], ...]:
    return tuple(
        (entry.name, entry)
        for entry in command_demo_readiness_contract(specs, launcher_argv).entries
    )


@lru_cache(maxsize=None)
def _command_demo_readiness_entry_for_command(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    command_name: str,
) -> CommandDemoReadinessEntry | None:
    requested_command = canonical_command_for(specs, command_name)
    if not requested_command:
        return None
    return dict(command_demo_readiness_index_by_command(specs, launcher_argv)).get(requested_command)


def command_demo_readiness_entry_for_command(
    command_name: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessEntry | None:
    return _command_demo_readiness_entry_for_command(specs, launcher_argv, command_name)


def command_demo_readiness_argv_for_command(
    command_name: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    entry = command_demo_readiness_entry_for_command(command_name, specs, launcher_argv)
    if entry is None:
        return ()
    return entry.command_argv


def command_demo_readiness_line_for_command(
    command_name: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    argv = command_demo_readiness_argv_for_command(command_name, specs, launcher_argv)
    if not argv:
        return ""
    return _shell_join(argv)


def command_demo_readiness_flow_step_for_command(
    command_name: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    entry = command_demo_readiness_entry_for_command(command_name, specs, launcher_argv)
    if entry is None:
        return None
    return entry.flow_step


def command_demo_readiness_demo_path_step_for_command(
    command_name: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    entry = command_demo_readiness_entry_for_command(command_name, specs, launcher_argv)
    if entry is None:
        return None
    return entry.demo_path_step


@lru_cache(maxsize=None)
def command_demo_readiness_index_by_demo_path_step(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, CommandDemoReadinessEntry], ...]:
    return tuple(
        (_normalize_token(entry.demo_path_step), entry)
        for entry in command_demo_readiness_contract(specs, launcher_argv).entries
    )


@lru_cache(maxsize=None)
def _command_demo_readiness_entry_for_demo_path_step(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    demo_path_step: str,
) -> CommandDemoReadinessEntry | None:
    requested_step = _normalize_token(demo_path_step)
    if not requested_step:
        return None
    return dict(command_demo_readiness_index_by_demo_path_step(specs, launcher_argv)).get(requested_step)


def command_demo_readiness_entry_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessEntry | None:
    return _command_demo_readiness_entry_for_demo_path_step(specs, launcher_argv, demo_path_step)


def command_demo_readiness_argv_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    entry = command_demo_readiness_entry_for_demo_path_step(demo_path_step, specs, launcher_argv)
    if entry is None:
        return ()
    return entry.command_argv


def command_demo_readiness_line_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    argv = command_demo_readiness_argv_for_demo_path_step(demo_path_step, specs, launcher_argv)
    if not argv:
        return ""
    return _shell_join(argv)


def command_demo_readiness_command_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    entry = command_demo_readiness_entry_for_demo_path_step(demo_path_step, specs, launcher_argv)
    if entry is None:
        return None
    return entry.name


def command_demo_readiness_flow_step_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    entry = command_demo_readiness_entry_for_demo_path_step(demo_path_step, specs, launcher_argv)
    if entry is None:
        return None
    return entry.flow_step


def command_demo_readiness_engine_actions_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    entry = command_demo_readiness_entry_for_demo_path_step(demo_path_step, specs, launcher_argv)
    if entry is None:
        return ()
    return entry.engine_actions


def command_demo_readiness_exact_action_lines_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    requested_step = _normalize_token(demo_path_step)
    if not requested_step:
        return ()
    for step in command_demo_readiness_handoff_action_contract(specs, launcher_argv).steps:
        if _normalize_token(step.demo_path_step) == requested_step:
            return step.exact_action_lines
    return ()


def command_demo_readiness_cli_exact_action_lines_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    requested_step = _normalize_token(demo_path_step)
    if not requested_step:
        return ()
    cli_exact_action_lines = dict(
        command_demo_readiness_cli_exact_action_line_lookup_table(specs, launcher_argv)
    )
    return tuple(
        (engine_action, cli_exact_action_lines[engine_action])
        for engine_action, _command_line in command_demo_readiness_exact_action_lines_for_demo_path_step(
            requested_step,
            specs,
            launcher_argv,
        )
        if engine_action in cli_exact_action_lines
    )


def _normalize_smoke_argv(argv: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(stripped for token in argv for stripped in (token.strip(),) if stripped)


def _coerce_smoke_argv(argv: Sequence[str] | str) -> tuple[str, ...]:
    if isinstance(argv, str):
        try:
            return tuple(shlex.split(argv))
        except ValueError:
            return ()
    return tuple(argv)


def _strip_shell_env_assignments(argv: tuple[str, ...]) -> tuple[str, ...]:
    index = 0
    while index < len(argv) and SHELL_ENV_ASSIGNMENT_RE.fullmatch(argv[index]):
        index += 1
    return argv[index:]


def _argv_without_launcher(argv: tuple[str, ...], launcher_argv: tuple[str, ...]) -> tuple[str, ...]:
    argv = _strip_shell_env_assignments(argv)
    argv = _strip_shell_command_wrappers(argv)
    if launcher_argv and argv[: len(launcher_argv)] == launcher_argv:
        return _strip_launcher_separator(argv[len(launcher_argv) :])
    for supported_launcher_argv in COMMAND_SMOKE_SUPPORTED_LAUNCHER_ARGV:
        if argv[: len(supported_launcher_argv)] == supported_launcher_argv:
            return _strip_launcher_separator(argv[len(supported_launcher_argv) :])
    launcher_prefix, unwrapped_argv = _split_supported_launcher_prefix(argv)
    if launcher_prefix:
        if _env_split_string_prefix(launcher_prefix):
            return _strip_launcher_separator(unwrapped_argv)
        unwrapped_without_launcher = _argv_without_launcher(unwrapped_argv, ())
        if unwrapped_without_launcher != unwrapped_argv:
            return unwrapped_without_launcher
        unwrapped_without_implicit_python = _argv_without_implicit_python_launcher_tail(unwrapped_argv)
        if unwrapped_without_implicit_python != unwrapped_argv:
            return unwrapped_without_implicit_python
    python_launcher_argv, command_argv = _split_python_launcher_argv(argv)
    if python_launcher_argv:
        return _strip_launcher_separator(command_argv)
    return argv


def _detected_launcher_argv(argv: tuple[str, ...]) -> tuple[str, ...]:
    argv = _strip_shell_env_assignments(argv)
    argv = _strip_shell_command_wrappers(argv)
    for supported_launcher_argv in COMMAND_SMOKE_SUPPORTED_LAUNCHER_ARGV:
        if argv[: len(supported_launcher_argv)] == supported_launcher_argv:
            return supported_launcher_argv
    launcher_prefix, unwrapped_argv = _split_supported_launcher_prefix(argv)
    if launcher_prefix:
        if _env_split_string_prefix(launcher_prefix):
            return launcher_prefix
        detected_argv = _detected_launcher_argv(unwrapped_argv)
        if detected_argv:
            return (*launcher_prefix, *detected_argv)
        implicit_python_tail = _detected_implicit_python_launcher_tail(unwrapped_argv)
        if implicit_python_tail:
            return (*launcher_prefix, *implicit_python_tail)
    python_launcher_argv, _command_argv = _split_python_launcher_argv(argv)
    if python_launcher_argv:
        return python_launcher_argv
    return ()


def _argv_without_implicit_python_launcher_tail(argv: tuple[str, ...]) -> tuple[str, ...]:
    for launcher_tail in COMMAND_SMOKE_SUPPORTED_LAUNCHER_TAILS:
        if _launcher_tail_matches(argv[: len(launcher_tail)], launcher_tail):
            return _strip_launcher_separator(argv[len(launcher_tail) :])
    return argv


def _detected_implicit_python_launcher_tail(argv: tuple[str, ...]) -> tuple[str, ...]:
    for launcher_tail in COMMAND_SMOKE_SUPPORTED_LAUNCHER_TAILS:
        if _launcher_tail_matches(argv[: len(launcher_tail)], launcher_tail):
            return launcher_tail
    return ()


def _split_supported_launcher_prefix(argv: tuple[str, ...]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    env_prefix, env_unwrapped_argv = _split_env_launcher_prefix(argv)
    if env_prefix:
        return env_prefix, env_unwrapped_argv
    uv_python_prefix, uv_python_unwrapped_argv = _split_uv_python_launcher_prefix(argv)
    if uv_python_prefix:
        return uv_python_prefix, uv_python_unwrapped_argv
    uv_run_prefix, uv_run_unwrapped_argv = _split_uv_run_option_prefix(argv)
    if uv_run_prefix:
        return uv_run_prefix, uv_run_unwrapped_argv
    for launcher_prefix in COMMAND_SMOKE_SUPPORTED_LAUNCHER_PREFIXES:
        requested_prefix = argv[: len(launcher_prefix)]
        if _launcher_prefix_matches(requested_prefix, launcher_prefix):
            return requested_prefix, argv[len(launcher_prefix) :]
    return (), argv


def _split_env_launcher_prefix(argv: tuple[str, ...]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if not argv or PurePath(argv[0]).name not in COMMAND_SMOKE_ENV_LAUNCHERS:
        return (), argv
    index = 1
    while index < len(argv):
        token = argv[index]
        if token == "--":
            return argv[: index + 1], argv[index + 1 :]
        if _env_option_has_inline_value(token):
            index += 1
            continue
        if token in COMMAND_SMOKE_ENV_VALUE_OPTIONS:
            if index + 1 >= len(argv):
                return (), argv
            index += 2
            continue
        if token in COMMAND_SMOKE_ENV_SPLIT_STRING_OPTIONS:
            if index + 1 >= len(argv):
                return (), argv
            split_prefix, split_unwrapped_argv = _split_env_split_string_launcher_prefix(
                argv[: index + 1],
                argv[index + 1],
                argv[index + 2 :],
            )
            if not split_prefix:
                return (), argv
            return split_prefix, split_unwrapped_argv
        if token.startswith("--split-string=") and token != "--split-string=":
            split_prefix, split_unwrapped_argv = _split_env_split_string_launcher_prefix(
                argv[:index],
                token.split("=", 1)[1],
                argv[index + 1 :],
                inline_option="--split-string",
            )
            if not split_prefix:
                return (), argv
            return split_prefix, split_unwrapped_argv
        if token in COMMAND_SMOKE_ENV_FLAGS or SHELL_ENV_ASSIGNMENT_RE.fullmatch(token):
            index += 1
            continue
        break
    if index >= len(argv):
        return (), argv
    return argv[:index], argv[index:]


def _env_option_has_inline_value(token: str) -> bool:
    return token.startswith("--unset=") and token != "--unset="


def _env_split_string_prefix(prefix: tuple[str, ...]) -> bool:
    return any(
        token in COMMAND_SMOKE_ENV_SPLIT_STRING_OPTIONS
        or (token.startswith("--split-string=") and token != "--split-string=")
        for token in prefix
    )


def _split_env_split_string_launcher_prefix(
    prefix_argv: tuple[str, ...],
    split_value: str,
    trailing_argv: tuple[str, ...],
    *,
    inline_option: str | None = None,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    split_argv = _split_env_split_string_argv(split_value)
    detected_launcher = _detected_launcher_argv(split_argv)
    if not detected_launcher:
        return (), trailing_argv
    split_command_argv = _argv_without_launcher(split_argv, detected_launcher)
    launcher_value = _shell_join(detected_launcher)
    if inline_option is not None:
        normalized_prefix = (*prefix_argv, f"{inline_option}={launcher_value}")
    else:
        normalized_prefix = (*prefix_argv, launcher_value)
    return normalized_prefix, (*split_command_argv, *trailing_argv)


def _split_env_split_string_argv(value: str) -> tuple[str, ...]:
    try:
        return tuple(shlex.split(value))
    except ValueError:
        return ()


def _strip_shell_command_wrappers(argv: tuple[str, ...]) -> tuple[str, ...]:
    tokens = _strip_shell_control_keywords(argv)
    while tokens and PurePath(tokens[0]).name in COMMAND_SMOKE_SHELL_WRAPPER_COMMANDS:
        index = 1
        while index < len(tokens) and tokens[index] in COMMAND_SMOKE_SHELL_WRAPPER_FLAGS:
            index += 1
        tokens = tokens[index:]
        tokens = _strip_shell_env_assignments(tokens)
        tokens = _strip_shell_control_keywords(tokens)
    return tokens


def _split_uv_python_launcher_prefix(argv: tuple[str, ...]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if len(argv) < 3 or not _is_supported_uv_launcher(argv[0]) or argv[1] != "run":
        return (), argv
    python_option = argv[2]
    if python_option == "--python":
        if len(argv) < 4:
            return (), argv
        python_launcher = argv[3]
        prefix = argv[:4]
        unwrapped_argv = argv[4:]
    elif python_option.startswith("--python="):
        python_launcher = python_option.split("=", 1)[1]
        prefix = argv[:3]
        unwrapped_argv = argv[3:]
    else:
        return (), argv
    if not python_launcher.strip() or not _is_supported_python_launcher(python_launcher):
        return (), argv
    if unwrapped_argv[:1] == ("--",):
        prefix = (*prefix, "--")
        unwrapped_argv = unwrapped_argv[1:]
    return prefix, unwrapped_argv


def _split_uv_run_option_prefix(argv: tuple[str, ...]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if len(argv) < 4 or not _is_supported_uv_launcher(argv[0]) or argv[1] != "run":
        return (), argv
    index = 2
    while index < len(argv):
        token = argv[index]
        if token == "--":
            return argv[: index + 1], argv[index + 1 :]
        if not token.startswith("-") or token == "-":
            break
        option, has_inline_value = _split_uv_run_option(token)
        if option in COMMAND_SMOKE_UV_RUN_FLAG_OPTIONS:
            if has_inline_value:
                return (), argv
            index += 1
            continue
        if option not in COMMAND_SMOKE_UV_RUN_VALUE_OPTIONS:
            return (), argv
        index += 1
        if not has_inline_value:
            if index >= len(argv):
                return (), argv
            index += 1
    if index <= 2 or index >= len(argv):
        return (), argv
    return argv[:index], argv[index:]


def _split_uv_run_option(token: str) -> tuple[str, bool]:
    if "=" not in token:
        return token, False
    option, _value = token.split("=", 1)
    return option, True


def _launcher_prefix_matches(
    requested_prefix: tuple[str, ...],
    expected_prefix: tuple[str, ...],
) -> bool:
    if requested_prefix == expected_prefix:
        return True
    if not requested_prefix or not expected_prefix:
        return False
    if expected_prefix[0] != "uv":
        return False
    return _is_supported_uv_launcher(requested_prefix[0]) and requested_prefix[1:] == expected_prefix[1:]


def _is_supported_uv_launcher(token: str) -> bool:
    return PurePath(token).name == "uv"


def _canonical_argv_with_requested_launcher(
    canonical_argv: tuple[str, ...],
    requested_launcher_argv: tuple[str, ...],
) -> tuple[str, ...]:
    if not requested_launcher_argv:
        return canonical_argv
    command_argv = _argv_without_launcher(canonical_argv, requested_launcher_argv)
    return (*requested_launcher_argv, *command_argv)


def _strip_launcher_separator(argv: tuple[str, ...]) -> tuple[str, ...]:
    if argv[:1] == ("--",):
        return argv[1:]
    return argv


def _is_supported_python_launcher(token: str) -> bool:
    launcher_name = PurePath(token).name
    if launcher_name in COMMAND_SMOKE_SUPPORTED_PYTHON_LAUNCHERS:
        return True
    return re.fullmatch(r"python\d+(?:\.\d+)*", launcher_name) is not None


def _split_python_launcher_argv(argv: tuple[str, ...]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if not argv or not _is_supported_python_launcher(argv[0]):
        return (), argv
    index = 1
    while index < len(argv):
        token = argv[index]
        if token in COMMAND_SMOKE_PYTHON_FLAG_OPTIONS:
            index += 1
            continue
        if any(
            token.startswith(option) and token != option
            for option in COMMAND_SMOKE_PYTHON_VALUE_OPTIONS
        ):
            index += 1
            continue
        if token in COMMAND_SMOKE_PYTHON_VALUE_OPTIONS:
            if index + 1 >= len(argv):
                return (), argv
            index += 2
            continue
        break
    for launcher_tail in COMMAND_SMOKE_SUPPORTED_LAUNCHER_TAILS:
        tail_end = index + len(launcher_tail)
        if len(argv) >= tail_end and _launcher_tail_matches(argv[index:tail_end], launcher_tail):
            return argv[:tail_end], argv[tail_end:]
    return (), argv


def _launcher_tail_matches(argv_tail: tuple[str, ...], expected_tail: tuple[str, ...]) -> bool:
    if argv_tail == expected_tail:
        return True
    if expected_tail == ("src/main.py",) and len(argv_tail) == 1:
        path_parts = PurePath(argv_tail[0]).parts
        return len(path_parts) >= 2 and path_parts[-2:] == ("src", "main.py")
    return False


def _canonicalize_smoke_command_argv(
    specs: tuple[CommandSpec, ...],
    argv: tuple[str, ...],
) -> tuple[str, ...]:
    argv = _normalize_implicit_bootstrap_argv(specs, argv)
    if not argv:
        return ()
    return (canonical_command_for(specs, _strip_command_palette_prefix(argv[0])), *argv[1:])


def _normalize_implicit_bootstrap_argv(
    specs: tuple[CommandSpec, ...],
    argv: tuple[str, ...],
) -> tuple[str, ...]:
    if command_spec_for(specs, "bootstrap") is None:
        return argv
    if not argv:
        return ("bootstrap",)
    if argv[0].startswith("-"):
        return ("bootstrap", *argv)
    return argv


def _strip_command_palette_prefix(command_token: str) -> str:
    if command_token.startswith("/") and not command_token.startswith("//"):
        return command_token[1:]
    return command_token


def _split_smoke_option_argv(
    argv: tuple[str, ...],
) -> tuple[str, tuple[str, ...], tuple[tuple[str, str | None], ...]] | None:
    if not argv:
        return None
    command = argv[0]
    positionals: list[str] = []
    options: list[tuple[str, str | None]] = []
    index = 1
    while index < len(argv):
        token = argv[index]
        if token.startswith("--"):
            option, value = _split_smoke_long_option(token)
            if value is None and index + 1 < len(argv) and not argv[index + 1].startswith("--"):
                value = argv[index + 1]
                index += 1
            options.append((option, value))
        else:
            positionals.append(token)
        index += 1
    return command, tuple(positionals), tuple(options)


def _split_smoke_long_option(token: str) -> tuple[str, str | None]:
    if "=" not in token:
        return token, None
    option, value = token.split("=", 1)
    return option, value


def _smoke_option_argv_matches(
    requested_argv: tuple[str, ...],
    expected_argv: tuple[str, ...],
) -> bool:
    requested = _split_smoke_option_argv(requested_argv)
    expected = _split_smoke_option_argv(expected_argv)
    if requested is None or expected is None:
        return False
    requested_command, requested_positionals, requested_options = requested
    expected_command, expected_positionals, expected_options = expected
    if requested_command != expected_command:
        return False
    if not _smoke_positionals_match(
        requested_command,
        requested_positionals,
        expected_positionals,
    ):
        return False
    if len({option for option, _ in requested_options}) != len(requested_options):
        return False
    if len({option for option, _ in expected_options}) != len(expected_options):
        return False
    value_agnostic_options = _smoke_value_agnostic_options_for_command(expected_command)
    if not expected_options:
        return all(option in value_agnostic_options and value is not None for option, value in requested_options)
    requested_by_option = dict(requested_options)
    expected_by_option = dict(expected_options)
    if requested_by_option.keys() != expected_by_option.keys():
        return False
    return all(
        (option in value_agnostic_options and requested_by_option[option] is not None)
        or requested_by_option[option] == expected_by_option[option]
        for option in expected_by_option
    )


def _exact_option_argv_matches(
    requested_argv: tuple[str, ...],
    expected_argv: tuple[str, ...],
) -> bool:
    requested = _split_smoke_option_argv(requested_argv)
    expected = _split_smoke_option_argv(expected_argv)
    if requested is None or expected is None:
        return False
    requested_command, requested_positionals, requested_options = requested
    expected_command, expected_positionals, expected_options = expected
    if requested_command != expected_command or requested_positionals != expected_positionals:
        return False
    if len({option for option, _ in requested_options}) != len(requested_options):
        return False
    if len({option for option, _ in expected_options}) != len(expected_options):
        return False
    return dict(requested_options) == dict(expected_options)


@lru_cache(maxsize=None)
def _smoke_value_agnostic_options_for_command(command: str) -> tuple[str, ...]:
    command_name = _normalize_token(command)
    option_rows = dict(_SMOKE_VALUE_AGNOSTIC_OPTIONS_BY_COMMAND)
    return option_rows.get(command_name, ())


@lru_cache(maxsize=None)
def _smoke_value_agnostic_positionals_for_command(command: str) -> tuple[int, ...]:
    command_name = _normalize_token(command)
    positional_rows = dict(_SMOKE_VALUE_AGNOSTIC_POSITIONALS_BY_COMMAND)
    return positional_rows.get(command_name, ())


def _smoke_positionals_match(
    command: str,
    requested_positionals: tuple[str, ...],
    expected_positionals: tuple[str, ...],
) -> bool:
    if len(requested_positionals) != len(expected_positionals):
        return False
    value_agnostic_indexes = set(_smoke_value_agnostic_positionals_for_command(command))
    return all(
        index in value_agnostic_indexes or requested_value == expected_value
        for index, (requested_value, expected_value) in enumerate(
            zip(requested_positionals, expected_positionals, strict=True)
        )
    )


def _smoke_argv_matches(
    requested_argv: tuple[str, ...],
    expected_argv: tuple[str, ...],
) -> bool:
    return requested_argv == expected_argv or _smoke_option_argv_matches(requested_argv, expected_argv)


def _exact_action_argv_matches(
    requested_argv: tuple[str, ...],
    expected_argv: tuple[str, ...],
) -> bool:
    return requested_argv == expected_argv or _exact_option_argv_matches(requested_argv, expected_argv)


@lru_cache(maxsize=None)
def _command_demo_readiness_entry_for_argv(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    argv: tuple[str, ...],
) -> CommandDemoReadinessEntry | None:
    requested_argv = _normalize_smoke_argv(argv)
    if not requested_argv:
        return None
    requested_command_argv = _argv_without_launcher(requested_argv, launcher_argv)
    requested_command_argv = _normalize_implicit_bootstrap_argv(specs, requested_command_argv)
    requested_canonical_command_argv = _canonicalize_smoke_command_argv(specs, requested_command_argv)
    for entry in command_demo_readiness_contract(specs, launcher_argv).entries:
        entry_command_argv = _argv_without_launcher(entry.command_argv, launcher_argv)
        if (
            _smoke_argv_matches(requested_argv, entry.command_argv)
            or _smoke_argv_matches(requested_command_argv, entry_command_argv)
            or _smoke_argv_matches(requested_canonical_command_argv, entry_command_argv)
        ):
            return entry
        for _, action_command_argv in entry.action_command_argv:
            action_argv = _argv_without_launcher(action_command_argv, launcher_argv)
            if (
                _smoke_argv_matches(requested_argv, action_command_argv)
                or _smoke_argv_matches(requested_command_argv, action_argv)
                or _smoke_argv_matches(requested_canonical_command_argv, action_argv)
            ):
                return entry
    return None


@lru_cache(maxsize=None)
def _command_demo_readiness_canonical_argv_for_argv(
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
    argv: tuple[str, ...],
) -> tuple[str, ...]:
    requested_argv = _normalize_smoke_argv(argv)
    if not requested_argv:
        return ()
    requested_launcher_argv = _detected_launcher_argv(requested_argv)
    requested_command_argv = _argv_without_launcher(requested_argv, launcher_argv)
    requested_command_argv = _normalize_implicit_bootstrap_argv(specs, requested_command_argv)
    requested_canonical_command_argv = _canonicalize_smoke_command_argv(specs, requested_command_argv)
    for entry in command_demo_readiness_contract(specs, launcher_argv).entries:
        entry_command_argv = _argv_without_launcher(entry.command_argv, launcher_argv)
        if (
            _smoke_argv_matches(requested_argv, entry.command_argv)
            or _smoke_argv_matches(requested_command_argv, entry_command_argv)
            or _smoke_argv_matches(requested_canonical_command_argv, entry_command_argv)
        ):
            return _canonical_argv_with_requested_launcher(entry.command_argv, requested_launcher_argv)
        for _, action_command_argv in entry.action_command_argv:
            action_argv = _argv_without_launcher(action_command_argv, launcher_argv)
            if (
                _smoke_argv_matches(requested_argv, action_command_argv)
                or _smoke_argv_matches(requested_command_argv, action_argv)
                or _smoke_argv_matches(requested_canonical_command_argv, action_argv)
            ):
                return _canonical_argv_with_requested_launcher(action_command_argv, requested_launcher_argv)
    return ()


def command_demo_readiness_entry_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessEntry | None:
    return _command_demo_readiness_entry_for_argv(specs, launcher_argv, _coerce_smoke_argv(argv))


def command_demo_readiness_flow_step_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    entry = command_demo_readiness_entry_for_argv(argv, specs, launcher_argv)
    if entry is None:
        return None
    return entry.flow_step


def command_demo_readiness_command_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    entry = command_demo_readiness_entry_for_argv(argv, specs, launcher_argv)
    if entry is None:
        return None
    return entry.name


def command_demo_readiness_demo_path_step_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    entry = command_demo_readiness_entry_for_argv(argv, specs, launcher_argv)
    if entry is None:
        return None
    return entry.demo_path_step


def command_demo_readiness_engine_actions_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    entry = command_demo_readiness_entry_for_argv(argv, specs, launcher_argv)
    if entry is None:
        return ()
    return entry.engine_actions


def command_demo_readiness_line_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    command_argv = _command_demo_readiness_canonical_argv_for_argv(
        specs,
        launcher_argv,
        _coerce_smoke_argv(argv),
    )
    if not command_argv:
        return ""
    return _shell_join(command_argv)


def command_demo_readiness_argv_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return _command_demo_readiness_canonical_argv_for_argv(
        specs,
        launcher_argv,
        _coerce_smoke_argv(argv),
    )


def command_mvp_demo_readiness_entry_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessEntry | None:
    return command_demo_readiness_entry_for_argv(argv, specs, launcher_argv)


def command_mvp_demo_readiness_flow_step_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    return command_demo_readiness_flow_step_for_argv(argv, specs, launcher_argv)


def command_mvp_demo_readiness_command_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    return command_demo_readiness_command_for_argv(argv, specs, launcher_argv)


def command_mvp_demo_readiness_demo_path_step_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    return command_demo_readiness_demo_path_step_for_argv(argv, specs, launcher_argv)


def command_mvp_demo_readiness_engine_actions_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_engine_actions_for_argv(argv, specs, launcher_argv)


def command_mvp_demo_readiness_line_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_line_for_argv(argv, specs, launcher_argv)


def command_mvp_demo_readiness_argv_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_argv_for_argv(argv, specs, launcher_argv)


def command_demo_readiness_validate_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessArgvValidation:
    requested_argv = _normalize_smoke_argv(_coerce_smoke_argv(argv))
    entry = command_demo_readiness_entry_for_argv(requested_argv, specs, launcher_argv)
    exact_engine_action = command_demo_readiness_exact_action_for_argv(
        requested_argv,
        specs,
        launcher_argv,
    )
    canonical_argv = _validation_canonical_argv(
        requested_argv,
        exact_engine_action,
        specs,
        launcher_argv,
    )
    if entry is None:
        return CommandDemoReadinessArgvValidation(
            requested_argv=requested_argv,
            canonical_argv=(),
            command_line="",
            flow_step=None,
            name=None,
            demo_path_step=None,
            engine_actions=(),
        )
    return CommandDemoReadinessArgvValidation(
        requested_argv=requested_argv,
        canonical_argv=canonical_argv,
        command_line=_shell_join(canonical_argv),
        flow_step=entry.flow_step,
        name=entry.name,
        demo_path_step=entry.demo_path_step,
        engine_actions=entry.engine_actions,
        exact_engine_action=exact_engine_action,
    )


def _validation_canonical_argv(
    requested_argv: tuple[str, ...],
    exact_engine_action: str | None,
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> tuple[str, ...]:
    if exact_engine_action is None:
        return command_demo_readiness_argv_for_argv(requested_argv, specs, launcher_argv)
    exact_argv = command_demo_readiness_exact_argv_for_engine_action(
        exact_engine_action,
        specs,
        launcher_argv,
    )
    if not exact_argv:
        return command_demo_readiness_argv_for_argv(requested_argv, specs, launcher_argv)
    requested_launcher_argv = _detected_launcher_argv(requested_argv)
    return _canonical_argv_with_requested_launcher(exact_argv, requested_launcher_argv)


def _cli_parser_token_for_requested_argv(
    specs: tuple[CommandSpec, ...],
    argv: tuple[str, ...],
    launcher_argv: tuple[str, ...],
) -> str | None:
    requested_command_argv = _argv_without_launcher(argv, launcher_argv)
    requested_command_argv = _normalize_implicit_bootstrap_argv(specs, requested_command_argv)
    if not requested_command_argv:
        return None
    token = _normalize_token(_strip_command_palette_prefix(requested_command_argv[0]))
    if not token:
        return None
    return token


def command_demo_readiness_validate_cli_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessCliArgvValidation:
    requested_argv = _normalize_smoke_argv(_coerce_smoke_argv(argv))
    parser_token = _cli_parser_token_for_requested_argv(specs, requested_argv, launcher_argv)
    compatibility_validation = command_demo_readiness_validate_argv(
        requested_argv,
        specs,
        launcher_argv,
    )
    is_cli_entrypoint = (
        specs == COMMAND_SPECS
        and parser_token is not None
        and parser_token in dict(command_cli_lookup_table())
        and compatibility_validation.name is not None
    )
    if not is_cli_entrypoint:
        return CommandDemoReadinessCliArgvValidation(
            requested_argv=requested_argv,
            canonical_argv=(),
            command_line="",
            parser_token=parser_token,
            is_cli_entrypoint=False,
            flow_step=None,
            name=None,
            demo_path_step=None,
            engine_actions=(),
        )
    return CommandDemoReadinessCliArgvValidation(
        requested_argv=compatibility_validation.requested_argv,
        canonical_argv=compatibility_validation.canonical_argv,
        command_line=compatibility_validation.command_line,
        parser_token=parser_token,
        is_cli_entrypoint=True,
        flow_step=compatibility_validation.flow_step,
        name=compatibility_validation.name,
        demo_path_step=compatibility_validation.demo_path_step,
        engine_actions=compatibility_validation.engine_actions,
        exact_engine_action=compatibility_validation.exact_engine_action,
    )


def command_demo_readiness_validate_cli_script(
    argvs: Sequence[Sequence[str] | str],
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    validations = tuple(command_demo_readiness_validate_cli_argv(argv, specs, launcher_argv) for argv in argvs)
    requested_argv = tuple(validation.requested_argv for validation in validations)
    canonical_argv = tuple(validation.canonical_argv for validation in validations if validation.canonical_argv)
    covered_flow_step_set = {validation.flow_step for validation in validations if validation.flow_step is not None}
    expected_flow_steps = _expected_command_demo_flow_steps(specs)
    covered_flow_steps = tuple(flow_step for flow_step in expected_flow_steps if flow_step in covered_flow_step_set)
    missing_flow_steps = tuple(flow_step for flow_step in expected_flow_steps if flow_step not in covered_flow_step_set)

    valid_requested_argv = tuple(
        validation.requested_argv for validation in validations if validation.is_cli_entrypoint
    )
    covered_action_set = _covered_demo_readiness_engine_actions(
        valid_requested_argv,
        specs,
        launcher_argv,
    )
    expected_actions = command_demo_engine_actions(specs)
    covered_engine_actions = tuple(action for action in expected_actions if action in covered_action_set)
    missing_engine_actions = tuple(action for action in expected_actions if action not in covered_action_set)
    invalid_argv = tuple(validation.requested_argv for validation in validations if not validation.is_cli_entrypoint)

    return CommandDemoReadinessScriptValidation(
        requested_argv=requested_argv,
        canonical_argv=canonical_argv,
        command_lines=tuple(_shell_join(argv) for argv in canonical_argv),
        covered_flow_steps=covered_flow_steps,
        missing_flow_steps=missing_flow_steps,
        covered_engine_actions=covered_engine_actions,
        missing_engine_actions=missing_engine_actions,
        invalid_argv=invalid_argv,
        is_complete=not missing_flow_steps and not missing_engine_actions and not invalid_argv,
    )


def command_demo_readiness_validate_cli_shell_script_lines(
    lines: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    return command_demo_readiness_validate_cli_script(
        _shell_script_executable_argv(lines),
        specs,
        launcher_argv,
    )


def command_demo_readiness_validate_exact_action_script(
    argvs: Sequence[Sequence[str] | str],
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    validations = tuple(command_demo_readiness_validate_argv(argv, specs, launcher_argv) for argv in argvs)
    requested_argv = tuple(validation.requested_argv for validation in validations)
    exact_action_by_argv = tuple(
        (validation.requested_argv, validation.exact_engine_action)
        for validation in validations
    )
    exact_action_set = {
        exact_engine_action
        for _, exact_engine_action in exact_action_by_argv
        if exact_engine_action is not None
    }
    expected_actions = command_demo_engine_actions(specs)
    covered_engine_actions = tuple(action for action in expected_actions if action in exact_action_set)
    missing_engine_actions = tuple(action for action in expected_actions if action not in exact_action_set)
    invalid_argv = tuple(
        requested
        for requested, exact_engine_action in exact_action_by_argv
        if exact_engine_action is None
    )
    canonical_argv = tuple(
        command_demo_readiness_exact_argv_for_engine_action(action, specs, launcher_argv)
        for action in covered_engine_actions
    )
    covered_flow_step_set = {
        command_demo_readiness_flow_step_for_argv(argv, specs, launcher_argv)
        for argv in canonical_argv
    }
    expected_flow_steps = _expected_command_demo_flow_steps(specs)
    covered_flow_steps = tuple(flow_step for flow_step in expected_flow_steps if flow_step in covered_flow_step_set)
    missing_flow_steps = tuple(flow_step for flow_step in expected_flow_steps if flow_step not in covered_flow_step_set)

    return CommandDemoReadinessScriptValidation(
        requested_argv=requested_argv,
        canonical_argv=canonical_argv,
        command_lines=tuple(_shell_join(argv) for argv in canonical_argv),
        covered_flow_steps=covered_flow_steps,
        missing_flow_steps=missing_flow_steps,
        covered_engine_actions=covered_engine_actions,
        missing_engine_actions=missing_engine_actions,
        invalid_argv=invalid_argv,
        is_complete=not missing_flow_steps and not missing_engine_actions and not invalid_argv,
    )


def command_demo_readiness_validate_exact_action_shell_script_lines(
    lines: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    return command_demo_readiness_validate_exact_action_script(
        _shell_script_executable_argv(lines),
        specs,
        launcher_argv,
    )


def command_demo_readiness_validate_cli_exact_action_script(
    argvs: Sequence[Sequence[str] | str],
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    validations = tuple(command_demo_readiness_validate_cli_argv(argv, specs, launcher_argv) for argv in argvs)
    requested_argv = tuple(validation.requested_argv for validation in validations)
    exact_action_by_argv = tuple(
        (validation.requested_argv, validation.exact_engine_action)
        for validation in validations
        if validation.is_cli_entrypoint
    )
    exact_action_set = {
        exact_engine_action
        for _, exact_engine_action in exact_action_by_argv
        if exact_engine_action is not None
    }
    expected_actions = command_demo_engine_actions(specs)
    covered_engine_actions = tuple(action for action in expected_actions if action in exact_action_set)
    missing_engine_actions = tuple(action for action in expected_actions if action not in exact_action_set)
    invalid_argv = tuple(
        validation.requested_argv
        for validation in validations
        if not validation.is_cli_entrypoint or validation.exact_engine_action is None
    )
    canonical_argv = tuple(
        command_demo_readiness_exact_argv_for_engine_action(action, specs, launcher_argv)
        for action in covered_engine_actions
    )
    covered_flow_step_set = {
        command_demo_readiness_flow_step_for_argv(argv, specs, launcher_argv)
        for argv in canonical_argv
    }
    expected_flow_steps = _expected_command_demo_flow_steps(specs)
    covered_flow_steps = tuple(flow_step for flow_step in expected_flow_steps if flow_step in covered_flow_step_set)
    missing_flow_steps = tuple(flow_step for flow_step in expected_flow_steps if flow_step not in covered_flow_step_set)

    return CommandDemoReadinessScriptValidation(
        requested_argv=requested_argv,
        canonical_argv=canonical_argv,
        command_lines=tuple(_shell_join(argv) for argv in canonical_argv),
        covered_flow_steps=covered_flow_steps,
        missing_flow_steps=missing_flow_steps,
        covered_engine_actions=covered_engine_actions,
        missing_engine_actions=missing_engine_actions,
        invalid_argv=invalid_argv,
        is_complete=not missing_flow_steps and not missing_engine_actions and not invalid_argv,
    )


def command_demo_readiness_validate_cli_exact_action_shell_script_lines(
    lines: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    return command_demo_readiness_validate_cli_exact_action_script(
        _shell_script_executable_argv(lines),
        specs,
        launcher_argv,
    )


def command_demo_readiness_validate_handoff_script(
    argvs: Sequence[Sequence[str] | str],
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    return command_demo_readiness_validate_cli_exact_action_script(
        argvs,
        specs,
        launcher_argv,
    )


def command_demo_readiness_validate_handoff_shell_script_lines(
    lines: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    return command_demo_readiness_validate_cli_exact_action_shell_script_lines(
        lines,
        specs,
        launcher_argv,
    )


def command_mvp_demo_readiness_validate_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessArgvValidation:
    return command_demo_readiness_validate_argv(argv, specs, launcher_argv)


def command_mvp_demo_readiness_validate_cli_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessCliArgvValidation:
    return command_demo_readiness_validate_cli_argv(argv, specs, launcher_argv)


def command_mvp_demo_readiness_validate_cli_script(
    argvs: Sequence[Sequence[str] | str],
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    return command_demo_readiness_validate_cli_script(argvs, specs, launcher_argv)


def command_mvp_demo_readiness_validate_cli_shell_script_lines(
    lines: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    return command_demo_readiness_validate_cli_shell_script_lines(lines, specs, launcher_argv)


def command_mvp_demo_readiness_validate_exact_action_script(
    argvs: Sequence[Sequence[str] | str],
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    return command_demo_readiness_validate_exact_action_script(argvs, specs, launcher_argv)


def command_mvp_demo_readiness_validate_exact_action_shell_script_lines(
    lines: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    return command_demo_readiness_validate_exact_action_shell_script_lines(lines, specs, launcher_argv)


def command_mvp_demo_readiness_validate_cli_exact_action_script(
    argvs: Sequence[Sequence[str] | str],
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    return command_demo_readiness_validate_cli_exact_action_script(argvs, specs, launcher_argv)


def command_mvp_demo_readiness_validate_cli_exact_action_shell_script_lines(
    lines: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    return command_demo_readiness_validate_cli_exact_action_shell_script_lines(lines, specs, launcher_argv)


def command_mvp_demo_readiness_validate_handoff_script(
    argvs: Sequence[Sequence[str] | str],
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    return command_demo_readiness_validate_handoff_script(argvs, specs, launcher_argv)


def command_mvp_demo_readiness_validate_handoff_shell_script_lines(
    lines: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    return command_demo_readiness_validate_handoff_shell_script_lines(lines, specs, launcher_argv)


def command_demo_readiness_validate_script(
    argvs: Sequence[Sequence[str] | str],
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    validations = tuple(command_demo_readiness_validate_argv(argv, specs, launcher_argv) for argv in argvs)
    requested_argv = tuple(validation.requested_argv for validation in validations)
    canonical_argv = tuple(validation.canonical_argv for validation in validations if validation.canonical_argv)
    covered_flow_step_set = {validation.flow_step for validation in validations if validation.flow_step is not None}
    expected_flow_steps = _expected_command_demo_flow_steps(specs)
    covered_flow_steps = tuple(flow_step for flow_step in expected_flow_steps if flow_step in covered_flow_step_set)
    missing_flow_steps = tuple(flow_step for flow_step in expected_flow_steps if flow_step not in covered_flow_step_set)

    covered_action_set = _covered_demo_readiness_engine_actions(
        tuple(validation.requested_argv for validation in validations),
        specs,
        launcher_argv,
    )
    expected_actions = command_demo_engine_actions(specs)
    covered_engine_actions = tuple(action for action in expected_actions if action in covered_action_set)
    missing_engine_actions = tuple(action for action in expected_actions if action not in covered_action_set)
    invalid_argv = tuple(validation.requested_argv for validation in validations if validation.name is None)

    return CommandDemoReadinessScriptValidation(
        requested_argv=requested_argv,
        canonical_argv=canonical_argv,
        command_lines=tuple(_shell_join(argv) for argv in canonical_argv),
        covered_flow_steps=covered_flow_steps,
        missing_flow_steps=missing_flow_steps,
        covered_engine_actions=covered_engine_actions,
        missing_engine_actions=missing_engine_actions,
        invalid_argv=invalid_argv,
        is_complete=not missing_flow_steps and not missing_engine_actions and not invalid_argv,
    )


def _expected_command_demo_flow_steps(specs: tuple[CommandSpec, ...]) -> tuple[str, ...]:
    if specs is COMMAND_SPECS:
        return command_demo_flow_steps()
    return command_flow_steps(specs)


def _covered_demo_readiness_engine_actions(
    requested_argv: tuple[tuple[str, ...], ...],
    specs: tuple[CommandSpec, ...],
    launcher_argv: tuple[str, ...],
) -> set[str]:
    covered_actions: set[str] = set()
    for argv in requested_argv:
        covered_actions.update(
            action_entry.engine_action
            for action_entry in command_demo_readiness_action_entries_for_argv(
                argv,
                specs,
                launcher_argv,
            )
        )
    return covered_actions


def _coerce_shell_script_lines(lines: Sequence[str] | str) -> tuple[str, ...]:
    if isinstance(lines, str):
        return tuple(lines.splitlines())
    return tuple(str(line) for line in lines)


def _logical_shell_script_lines(lines: Sequence[str] | str) -> tuple[str, ...]:
    logical_lines: list[str] = []
    pending_parts: list[str] = []
    for raw_line in _coerce_shell_script_lines(lines):
        line = raw_line.rstrip()
        if line.endswith("\\"):
            pending_parts.append(line[:-1].rstrip())
            continue
        if pending_parts:
            pending_parts.append(line.lstrip())
            logical_lines.append(" ".join(part for part in pending_parts if part))
            pending_parts = []
            continue
        logical_lines.append(line)
    if pending_parts:
        logical_lines.append(" ".join(part for part in pending_parts if part))
    return tuple(logical_lines)


def _shell_script_executable_argv(lines: Sequence[str] | str) -> tuple[tuple[str, ...], ...]:
    executable_argv: list[tuple[str, ...]] = []
    for raw_line in _logical_shell_script_lines(lines):
        line = raw_line.strip()
        if not line or line.startswith("#") or _is_shell_strict_mode_setup_line(line):
            continue
        argv = _split_shell_script_line(line)
        for segment_argv in _split_shell_script_command_segments(argv):
            if _is_shell_script_setup_argv(segment_argv):
                continue
            if segment_argv:
                executable_argv.append(segment_argv)
    return tuple(executable_argv)


def _split_shell_script_line(line: str) -> tuple[str, ...]:
    lexer = shlex.shlex(line, posix=True, punctuation_chars=";&|")
    lexer.whitespace_split = True
    lexer.commenters = "#"
    try:
        return tuple(lexer)
    except ValueError:
        return (line,)


def _split_shell_script_command_segments(argv: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    segments: list[tuple[str, ...]] = []
    current_segment: list[str] = []
    opened_groups = 0
    for token in argv:
        if token in {"&&", "||", ";", "|"}:
            if current_segment:
                segment, opened_groups = _normalize_shell_script_segment_argv(
                    tuple(current_segment),
                    opened_groups,
                )
                if segment:
                    segments.append(segment)
                current_segment = []
            continue
        current_segment.append(token)
    if current_segment:
        segment, opened_groups = _normalize_shell_script_segment_argv(
            tuple(current_segment),
            opened_groups,
        )
        if segment:
            segments.append(segment)
    return tuple(segments)


def _normalize_shell_script_segment_argv(
    argv: tuple[str, ...],
    opened_groups: int,
) -> tuple[tuple[str, ...], int]:
    tokens = list(argv)

    while tokens and tokens[0] in {"(", "{"}:
        opened_groups += 1
        tokens.pop(0)
    while tokens and tokens[-1] in {")", "}"} and opened_groups:
        opened_groups -= 1
        tokens.pop()

    if tokens and tokens[0].startswith(("(", "{")):
        stripped = tokens[0].lstrip("({")
        opened_groups += len(tokens[0]) - len(stripped)
        tokens[0] = stripped
    if opened_groups and tokens and tokens[-1].endswith((")", "}")):
        stripped = tokens[-1].rstrip(")}")
        opened_groups = max(0, opened_groups - (len(tokens[-1]) - len(stripped)))
        tokens[-1] = stripped

    return (
        _strip_shell_control_keywords(
            _strip_shell_redirections(tuple(token for token in tokens if token))
        ),
        opened_groups,
    )


def _strip_shell_control_keywords(argv: tuple[str, ...]) -> tuple[str, ...]:
    index = 0
    while index < len(argv) and argv[index] in COMMAND_SMOKE_SHELL_CONTROL_KEYWORDS:
        index += 1
    return argv[index:]


def _strip_shell_redirections(argv: tuple[str, ...]) -> tuple[str, ...]:
    stripped_argv: list[str] = []
    index = 0
    while index < len(argv):
        token = argv[index]
        if _is_shell_redirection_operator(token):
            if index + 2 < len(argv) and argv[index + 1] == "&" and argv[index + 2].isdigit():
                index += 3
                continue
            index += 2
            continue
        if _is_shell_redirection_with_target(token):
            index += 1
            continue
        stripped_argv.append(token)
        index += 1
    return tuple(stripped_argv)


def _is_shell_redirection_operator(token: str) -> bool:
    return SHELL_REDIRECT_OPERATOR_RE.fullmatch(token) is not None


def _is_shell_redirection_with_target(token: str) -> bool:
    return (
        not _is_shell_redirection_operator(token)
        and SHELL_REDIRECT_WITH_TARGET_RE.fullmatch(token) is not None
    )


def _is_shell_strict_mode_setup_line(line: str) -> bool:
    return _is_shell_strict_mode_setup_argv(_split_shell_script_line(line))


def _is_shell_strict_mode_setup_argv(argv: tuple[str, ...]) -> bool:
    if len(argv) < 2 or argv[0] != "set":
        return False
    index = 1
    while index < len(argv):
        token = argv[index]
        if token == "-o":
            if index + 1 >= len(argv) or argv[index + 1] != "pipefail":
                return False
            index += 2
            continue
        if token.startswith("-") and token[1:] and set(token[1:]).issubset({"E", "e", "u", "o", "x"}):
            if "o" in token:
                if index + 1 >= len(argv) or argv[index + 1] != "pipefail":
                    return False
                index += 2
                continue
            index += 1
            continue
        return False
    return True


def _is_shell_script_setup_argv(argv: tuple[str, ...]) -> bool:
    if not argv:
        return False
    argv = _strip_shell_env_assignments(argv)
    if not argv:
        return True
    command = PurePath(argv[0]).name
    if command == "export":
        return all(SHELL_ENV_ASSIGNMENT_RE.fullmatch(token) for token in argv[1:])
    if command == "set":
        return _is_shell_strict_mode_setup_argv(argv)
    if command in COMMAND_SMOKE_SHELL_STATUS_COMMANDS:
        return _is_shell_status_argv(argv[1:])
    if command in COMMAND_SMOKE_SHELL_PROBE_COMMANDS:
        return _is_shell_script_probe_setup_argv(argv[1:])
    if command in COMMAND_SMOKE_SHELL_OUTPUT_SINK_COMMANDS:
        return _is_shell_script_output_sink_argv(argv[1:])
    return command in COMMAND_SMOKE_SHELL_SETUP_COMMANDS


def _is_shell_status_argv(argv: tuple[str, ...]) -> bool:
    return len(argv) <= 1 and all(token.isdigit() for token in argv)


def _is_shell_script_probe_setup_argv(argv: tuple[str, ...]) -> bool:
    if not argv:
        return False
    index = 0
    while index < len(argv) and argv[index] in COMMAND_SMOKE_SHELL_PROBE_FLAGS:
        index += 1
    return index > 0 and index < len(argv) and all(not token.startswith("-") for token in argv[index:])


def _is_shell_script_output_sink_argv(argv: tuple[str, ...]) -> bool:
    if not argv:
        return False
    index = 0
    while index < len(argv) and argv[index] in COMMAND_SMOKE_SHELL_OUTPUT_SINK_FLAGS:
        index += 1
    return index < len(argv)


def command_demo_readiness_validate_shell_script_lines(
    lines: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    return command_demo_readiness_validate_script(
        _shell_script_executable_argv(lines),
        specs,
        launcher_argv,
    )


def command_mvp_demo_readiness_validate_script(
    argvs: Sequence[Sequence[str] | str],
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    return command_demo_readiness_validate_script(argvs, specs, launcher_argv)


def command_mvp_demo_readiness_validate_shell_script_lines(
    lines: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessScriptValidation:
    return command_demo_readiness_validate_shell_script_lines(lines, specs, launcher_argv)


@lru_cache(maxsize=None)
def command_demo_command_action_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoCommandActionContract:
    demo_path_contract = command_demo_path_contract(specs)
    contract = CommandDemoCommandActionContract(
        entries=tuple(
            CommandDemoCommandActionEntry(
                flow_step=entry.flow_step,
                name=entry.name,
                cli_tokens=entry.cli_tokens,
                smoke_token=entry.cli_tokens[0],
                demo_path_step=entry.demo_path_step,
                engine_actions=entry.engine_actions,
            )
            for entry in demo_path_contract.entries
        )
    )
    _validate_command_demo_command_action_contract(contract, demo_path_contract, specs=specs)
    return contract


def _validate_command_demo_command_action_contract(
    contract: CommandDemoCommandActionContract,
    demo_path_contract: CommandDemoPathContract,
    *,
    specs: tuple[CommandSpec, ...],
) -> None:
    if tuple(entry.flow_step for entry in contract.entries) != tuple(
        path_entry.flow_step for path_entry in demo_path_contract.entries
    ):
        raise ValueError("Command demo command action flow steps are inconsistent")
    if tuple(entry.name for entry in contract.entries) != tuple(
        path_entry.name for path_entry in demo_path_contract.entries
    ):
        raise ValueError("Command demo command action names are inconsistent")
    if tuple(entry.cli_tokens for entry in contract.entries) != tuple(
        path_entry.cli_tokens for path_entry in demo_path_contract.entries
    ):
        raise ValueError("Command demo command action CLI tokens are inconsistent")
    if tuple(entry.smoke_token for entry in contract.entries) != tuple(
        path_entry.cli_tokens[0] for path_entry in demo_path_contract.entries
    ):
        raise ValueError("Command demo command action smoke tokens are inconsistent")
    if tuple(entry.demo_path_step for entry in contract.entries) != tuple(
        path_entry.demo_path_step for path_entry in demo_path_contract.entries
    ):
        raise ValueError("Command demo command action path steps are inconsistent")
    if tuple(entry.engine_actions for entry in contract.entries) != tuple(
        path_entry.engine_actions for path_entry in demo_path_contract.entries
    ):
        raise ValueError("Command demo command action engine actions are inconsistent")

    action_routes_by_name: dict[str, list[CommandDemoActionRouteEntry]] = {}
    for route_entry in command_demo_action_route_contract(specs).entries:
        action_routes_by_name.setdefault(route_entry.name, []).append(route_entry)

    for entry in contract.entries:
        route_entries = tuple(action_routes_by_name.get(entry.name, ()))
        if tuple(route_entry.engine_action for route_entry in route_entries) != entry.engine_actions:
            raise ValueError(f"Command demo command action route actions are inconsistent: {entry.name}")
        if any(route_entry.flow_step != entry.flow_step for route_entry in route_entries):
            raise ValueError(f"Command demo command action route flow step is inconsistent: {entry.name}")
        if any(route_entry.cli_tokens != entry.cli_tokens for route_entry in route_entries):
            raise ValueError(f"Command demo command action route CLI tokens are inconsistent: {entry.name}")
        if any(route_entry.smoke_token != entry.smoke_token for route_entry in route_entries):
            raise ValueError(f"Command demo command action route smoke token is inconsistent: {entry.name}")


def command_demo_command_action_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, tuple[str, ...], str, tuple[str, ...]], ...]:
    contract = command_demo_command_action_contract(specs)
    return tuple(
        (
            entry.flow_step,
            entry.name,
            entry.cli_tokens,
            entry.demo_path_step,
            entry.engine_actions,
        )
        for entry in contract.entries
    )


def command_demo_command_action_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return tuple(
        (entry.name, entry.engine_actions)
        for entry in command_demo_command_action_contract(specs).entries
    )


@lru_cache(maxsize=None)
def command_demo_action_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, CommandDemoActionEntry], ...]:
    return tuple((entry.engine_action, entry) for entry in command_demo_action_contract(specs).entries)


@lru_cache(maxsize=None)
def _command_demo_action_entry_for(
    specs: tuple[CommandSpec, ...],
    engine_action: str,
) -> CommandDemoActionEntry | None:
    requested_action = engine_action.strip()
    if not requested_action:
        return None
    return dict(command_demo_action_index(specs)).get(requested_action)


def command_demo_action_entry(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoActionEntry | None:
    return _command_demo_action_entry_for(specs, engine_action)


def command_demo_action_cli_token(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> str | None:
    entry = command_demo_action_entry(engine_action, specs)
    if entry is None:
        return None
    return entry.smoke_token


def command_mvp_demo_action_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoActionContract:
    return command_demo_action_contract(specs)


def command_mvp_demo_action_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, str, str, str], ...]:
    return command_demo_action_summary(specs)


def command_mvp_demo_action_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_action_lookup_table(specs)


def command_mvp_demo_engine_actions(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return command_demo_engine_actions(specs)


def command_mvp_demo_action_flow_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_action_flow_lookup_table(specs)


def command_mvp_demo_action_demo_path_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_action_demo_path_lookup_table(specs)


def command_mvp_demo_action_flow_step(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> str | None:
    return command_demo_action_flow_step(engine_action, specs)


def command_mvp_demo_action_demo_path_step(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> str | None:
    return command_demo_action_demo_path_step(engine_action, specs)


def command_mvp_demo_action_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, str, str], ...]:
    return command_demo_action_route_summary(specs)


def command_mvp_demo_action_route_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoActionRouteContract:
    return command_demo_action_route_contract(specs)


def command_mvp_demo_action_cli_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_action_cli_lookup_table(specs)


def command_mvp_demo_action_cli_smoke_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_action_cli_smoke_lookup_table(specs)


def command_mvp_demo_action_smoke_argv_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoActionSmokeArgvContract:
    return command_demo_action_smoke_argv_contract(specs)


def command_mvp_demo_action_smoke_argv_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_action_smoke_argv_lookup_table(specs)


def command_mvp_demo_action_smoke_argv_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, CommandDemoActionSmokeArgvEntry], ...]:
    return command_demo_action_smoke_argv_index(specs)


def command_mvp_demo_action_smoke_argv_entry(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoActionSmokeArgvEntry | None:
    return command_demo_action_smoke_argv_entry(engine_action, specs)


def command_mvp_demo_action_smoke_argv(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return command_demo_action_smoke_argv(engine_action, specs)


def command_mvp_demo_action_smoke_cli_argv_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoActionSmokeCliArgvContract:
    return command_demo_action_smoke_cli_argv_contract(specs, launcher_argv)


def command_mvp_demo_action_smoke_cli_argv_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_action_smoke_cli_argv_lookup_table(specs, launcher_argv)


def command_mvp_demo_action_smoke_cli_argv_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, CommandDemoActionSmokeCliArgvEntry], ...]:
    return command_demo_action_smoke_cli_argv_index(specs, launcher_argv)


def command_mvp_demo_action_smoke_cli_argv_entry(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoActionSmokeCliArgvEntry | None:
    return command_demo_action_smoke_cli_argv_entry(engine_action, specs, launcher_argv)


def command_mvp_demo_action_smoke_cli_argv(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_action_smoke_cli_argv(engine_action, specs, launcher_argv)


def command_mvp_demo_action_smoke_script_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoActionSmokeScriptContract:
    return command_demo_action_smoke_script_contract(specs, launcher_argv)


def command_mvp_demo_action_smoke_script_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, tuple[str, ...], str], ...]:
    return command_demo_action_smoke_script_summary(specs, launcher_argv)


def command_mvp_demo_action_smoke_script_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, tuple[str, ...]], ...]:
    return command_demo_action_smoke_script_lookup_table(specs, launcher_argv)


def command_mvp_demo_action_smoke_script_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str], ...]:
    return command_demo_action_smoke_script_lines(specs, launcher_argv)


def command_mvp_demo_action_smoke_script_step(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoActionSmokeScriptStep | None:
    return command_demo_action_smoke_script_step(ordinal, specs, launcher_argv)


def command_mvp_demo_action_smoke_script_argv(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_action_smoke_script_argv(ordinal, specs, launcher_argv)


def command_mvp_demo_readiness_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessContract:
    return command_demo_readiness_contract(specs, launcher_argv)


def command_mvp_demo_readiness_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, tuple[str, ...], str, tuple[str, ...], tuple[tuple[str, tuple[str, ...]], ...]], ...]:
    return command_demo_readiness_summary(specs, launcher_argv)


def command_mvp_demo_readiness_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_readiness_lookup_table(specs, launcher_argv)


def command_mvp_demo_readiness_command_line_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return command_demo_readiness_command_line_lookup_table(specs, launcher_argv)


def command_mvp_demo_readiness_cli_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessCliContract:
    return command_demo_readiness_cli_contract(specs, launcher_argv)


def command_mvp_demo_readiness_cli_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, tuple[str, ...], str, tuple[str, ...]], ...]:
    return command_demo_readiness_cli_summary(specs, launcher_argv)


def command_mvp_demo_readiness_cli_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str], ...]:
    return command_demo_readiness_cli_lookup_table(specs, launcher_argv)


def command_mvp_demo_readiness_action_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    return command_demo_readiness_action_lookup_table(specs, launcher_argv)


def command_mvp_demo_readiness_action_argv_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_readiness_action_argv_lookup_table(specs, launcher_argv)


def command_mvp_demo_readiness_missing_engine_actions(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_missing_engine_actions(specs, launcher_argv)


def command_mvp_demo_readiness_is_complete(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> bool:
    return command_demo_readiness_is_complete(specs, launcher_argv)


def command_mvp_demo_readiness_action_line_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return command_demo_readiness_action_line_lookup_table(specs, launcher_argv)


def command_mvp_demo_readiness_action_argv_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_readiness_action_argv_index(specs, launcher_argv)


def command_mvp_demo_readiness_argv_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_argv_for_engine_action(engine_action, specs, launcher_argv)


def command_mvp_demo_readiness_line_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_line_for_engine_action(engine_action, specs, launcher_argv)


def command_mvp_demo_readiness_command_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    return command_demo_readiness_command_for_engine_action(engine_action, specs, launcher_argv)


def command_mvp_demo_readiness_action_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessActionContract:
    return command_demo_readiness_action_contract(specs, launcher_argv)


def command_mvp_demo_readiness_action_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, tuple[str, ...], tuple[str, ...], str], ...]:
    return command_demo_readiness_action_summary(specs, launcher_argv)


def command_mvp_demo_readiness_action_smoke_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, str, str], ...]:
    return command_demo_readiness_action_smoke_summary(specs, launcher_argv)


def command_mvp_demo_readiness_smoke_plan(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessSmokePlan:
    return command_demo_readiness_smoke_plan(specs, launcher_argv)


def command_mvp_demo_readiness_smoke_plan_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, tuple[tuple[str, str], ...]], ...]:
    return command_demo_readiness_smoke_plan_summary(specs, launcher_argv)


def command_mvp_demo_readiness_smoke_plan_step(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessSmokePlanStep | None:
    return command_demo_readiness_smoke_plan_step(ordinal, specs, launcher_argv)


def command_mvp_demo_readiness_smoke_plan_step_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessSmokePlanStep | None:
    return command_demo_readiness_smoke_plan_step_for_demo_path_step(
        demo_path_step,
        specs,
        launcher_argv,
    )


def command_mvp_demo_readiness_smoke_plan_step_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessSmokePlanStep | None:
    return command_demo_readiness_smoke_plan_step_for_flow_step(
        flow_step,
        specs,
        launcher_argv,
    )


def command_mvp_demo_readiness_smoke_plan_argv(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_smoke_plan_argv(ordinal, specs, launcher_argv)


def command_mvp_demo_readiness_smoke_plan_argv_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_smoke_plan_argv_for_flow_step(flow_step, specs, launcher_argv)


def command_mvp_demo_readiness_required_argv(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, ...], ...]:
    return command_demo_readiness_required_argv(specs, launcher_argv)


def command_mvp_demo_readiness_required_argv_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_readiness_required_argv_lookup_table(specs, launcher_argv)


def command_mvp_demo_path_readiness_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoPathReadinessContract:
    return command_demo_path_readiness_contract(specs, launcher_argv)


def command_mvp_demo_path_readiness_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, tuple[str, ...], tuple[tuple[str, str], ...]], ...]:
    return command_demo_path_readiness_summary(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessHandoffContract:
    return command_demo_readiness_handoff_contract(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, tuple[tuple[str, str], ...]], ...]:
    return command_demo_readiness_handoff_summary(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_line_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessHandoffLineContract:
    return command_demo_readiness_handoff_line_contract(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_handoff_lines(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_checklist_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessHandoffChecklistContract:
    return command_demo_readiness_handoff_checklist_contract(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_checklist_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_handoff_checklist_lines(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_action_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessHandoffActionContract:
    return command_demo_readiness_handoff_action_contract(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_action_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, tuple[tuple[str, str], ...]], ...]:
    return command_demo_readiness_handoff_action_summary(specs, launcher_argv)


def command_mvp_demo_readiness_action_sequence_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessActionSequenceContract:
    return command_demo_readiness_action_sequence_contract(specs, launcher_argv)


def command_mvp_demo_readiness_action_sequence_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, str], ...]:
    return command_demo_readiness_action_sequence_summary(specs, launcher_argv)


def command_mvp_demo_readiness_route_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessRouteContract:
    return command_demo_readiness_route_contract(specs, launcher_argv)


def command_mvp_demo_readiness_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, tuple[str, ...], str, tuple[str, ...], tuple[tuple[str, str], ...]], ...]:
    return command_demo_readiness_route_summary(specs, launcher_argv)


def command_mvp_demo_readiness_route_payload(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> dict[str, object]:
    return command_demo_readiness_route_payload(specs, launcher_argv)


def command_mvp_demo_readiness_route_json(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_route_json(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_markdown(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_handoff_markdown(specs, launcher_argv)


def command_mvp_demo_readiness_gate(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessGate:
    return command_demo_readiness_gate(specs, launcher_argv)


def command_mvp_demo_readiness_gate_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[bool, tuple[str, ...], tuple[str, ...], tuple[tuple[str, str], ...]]:
    return command_demo_readiness_gate_summary(specs, launcher_argv)


def command_mvp_demo_readiness_flow_gate_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[bool, tuple[str, ...], tuple[str, ...]]:
    return command_demo_readiness_flow_gate_summary(specs, launcher_argv)


def command_mvp_demo_readiness_gate_issues(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_gate_issues(specs, launcher_argv)


def command_mvp_demo_readiness_report(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessReport:
    return command_demo_readiness_report(specs, launcher_argv)


def command_mvp_demo_readiness_report_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[bool, tuple[str, ...], tuple[str, ...], tuple[tuple[str, str], ...], tuple[str, ...], str]:
    return command_demo_readiness_report_summary(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_packet(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessHandoffPacket:
    return command_demo_readiness_handoff_packet(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_packet_payload(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> dict[str, object]:
    return command_demo_readiness_handoff_packet_payload(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_packet_json(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_handoff_packet_json(specs, launcher_argv)


def command_mvp_demo_surface_readiness_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoSurfaceReadinessContract:
    return command_demo_surface_readiness_contract(specs, launcher_argv)


def command_mvp_demo_surface_readiness_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    tuple[int, str, str, str, tuple[str, ...], str, tuple[str, ...], tuple[tuple[str, str], ...]],
    ...,
]:
    return command_demo_surface_readiness_summary(specs, launcher_argv)


def command_mvp_demo_surface_readiness_payload(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> dict[str, object]:
    return command_demo_surface_readiness_payload(specs, launcher_argv)


def command_mvp_demo_surface_readiness_json(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_surface_readiness_json(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_packet_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    str,
    tuple[str, ...],
    tuple[str, ...],
    str,
    str,
    str,
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    bool,
    tuple[str, ...],
    tuple[str, ...],
    tuple[tuple[str, ...], ...],
]:
    return command_demo_readiness_handoff_packet_summary(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_packet_markdown(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_handoff_packet_markdown(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_status_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_handoff_status_lines(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_step_status_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessHandoffStepStatusContract:
    return command_demo_readiness_handoff_step_status_contract(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_step_status_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    str,
    str,
    bool,
    tuple[tuple[int, str, str, str, str, str, tuple[str, ...], tuple[tuple[str, str], ...], bool, bool], ...],
]:
    return command_demo_readiness_handoff_step_status_summary(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_step_status_payload(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> dict[str, object]:
    return command_demo_readiness_handoff_step_status_payload(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_step_status_json(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_handoff_step_status_json(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_audit(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessHandoffAudit:
    return command_demo_readiness_handoff_audit(specs, launcher_argv)


def command_mvp_demo_readiness_handoff_audit_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    bool,
    str,
    str,
    bool,
    bool,
    bool,
    tuple[tuple[str, ...], ...],
    tuple[str, ...],
    tuple[str, ...],
]:
    return command_demo_readiness_handoff_audit_summary(specs, launcher_argv)


def command_mvp_demo_readiness_exact_action_route_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessExactActionRouteContract:
    return command_demo_readiness_exact_action_route_contract(specs, launcher_argv)


def command_mvp_demo_readiness_exact_action_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, str, tuple[str, ...], str], ...]:
    return command_demo_readiness_exact_action_route_summary(specs, launcher_argv)


def command_mvp_demo_readiness_exact_action_route_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return command_demo_readiness_exact_action_route_lookup_table(specs, launcher_argv)


def command_mvp_demo_readiness_seal(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessSeal:
    return command_demo_readiness_seal(specs, launcher_argv)


def command_mvp_demo_readiness_seal_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    bool,
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[tuple[str, ...], ...],
]:
    return command_demo_readiness_seal_summary(specs, launcher_argv)


def command_mvp_demo_readiness_fingerprint(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessFingerprint:
    return command_demo_readiness_fingerprint(specs, launcher_argv)


def command_mvp_demo_readiness_fingerprint_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, str, tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    return command_demo_readiness_fingerprint_summary(specs, launcher_argv)


def command_mvp_demo_readiness_step_seal_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessStepSealContract:
    return command_demo_readiness_step_seal_contract(specs, launcher_argv)


def command_mvp_demo_readiness_step_seal_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    tuple[int, str, str, str, tuple[str, ...], str, tuple[str, ...], tuple[tuple[str, str], ...]],
    ...,
]:
    return command_demo_readiness_step_seal_summary(specs, launcher_argv)


def command_mvp_demo_readiness_step_seal_payload(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[dict[str, object], ...]:
    return command_demo_readiness_step_seal_payload(specs, launcher_argv)


def command_mvp_demo_readiness_step_seal_json(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_step_seal_json(specs, launcher_argv)


def command_mvp_demo_readiness_cli_step_validation_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessCliStepValidationContract:
    return command_demo_readiness_cli_step_validation_contract(specs, launcher_argv)


def command_mvp_demo_readiness_cli_step_validation_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, str, str, bool], ...]:
    return command_demo_readiness_cli_step_validation_summary(specs, launcher_argv)


def command_mvp_demo_readiness_cli_step_validation_payload(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[dict[str, object], ...]:
    return command_demo_readiness_cli_step_validation_payload(specs, launcher_argv)


def command_mvp_demo_readiness_cli_step_validation_json(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_cli_step_validation_json(specs, launcher_argv)


def command_mvp_demo_readiness_index_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessIndexContract:
    return command_demo_readiness_index_contract(specs, launcher_argv)


def command_mvp_demo_readiness_index_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[
    str,
    str,
    tuple[tuple[int, str, str, str, str, tuple[str, ...], tuple[tuple[str, str], ...], str, str], ...],
]:
    return command_demo_readiness_index_summary(specs, launcher_argv)


def command_mvp_demo_readiness_index_payload(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> dict[str, object]:
    return command_demo_readiness_index_payload(specs, launcher_argv)


def command_mvp_demo_readiness_index_json(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_index_json(specs, launcher_argv)


def command_mvp_demo_readiness_shell_script(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessShellScript:
    return command_demo_readiness_shell_script(specs, launcher_argv)


def command_mvp_demo_readiness_shell_script_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_shell_script_lines(specs, launcher_argv)


def command_mvp_demo_readiness_shell_executable_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_shell_executable_lines(specs, launcher_argv)


def command_mvp_demo_readiness_shell_executable_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, str | None], ...]:
    return command_demo_readiness_shell_executable_route_summary(specs, launcher_argv)


def command_mvp_demo_readiness_cli_smoke_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_cli_smoke_lines(specs, launcher_argv)


def command_mvp_demo_readiness_shell_script_text(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_shell_script_text(specs, launcher_argv)


def command_mvp_demo_readiness_trace_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessTraceContract:
    return command_demo_readiness_trace_contract(specs, launcher_argv)


def command_mvp_demo_readiness_trace_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, str, str], ...]:
    return command_demo_readiness_trace_summary(specs, launcher_argv)


def command_mvp_demo_readiness_trace_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return command_demo_readiness_trace_lookup_table(specs, launcher_argv)


def command_mvp_demo_readiness_trace_entry_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessTraceEntry | None:
    return command_demo_readiness_trace_entry_for_engine_action(
        engine_action,
        specs,
        launcher_argv,
    )


def command_mvp_demo_readiness_trace_entry_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessTraceEntry | None:
    return command_demo_readiness_trace_entry_for_argv(
        argv,
        specs,
        launcher_argv,
    )


def command_mvp_demo_readiness_command_trace_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessCommandTraceContract:
    return command_demo_readiness_command_trace_contract(specs, launcher_argv)


def command_mvp_demo_readiness_command_trace_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, tuple[tuple[str, str], ...]], ...]:
    return command_demo_readiness_command_trace_summary(specs, launcher_argv)


def command_mvp_demo_readiness_command_trace_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, tuple[tuple[str, str], ...]], ...]:
    return command_demo_readiness_command_trace_lookup_table(specs, launcher_argv)


def command_mvp_demo_readiness_command_trace_entry_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessCommandTraceEntry | None:
    return command_demo_readiness_command_trace_entry_for_engine_action(
        engine_action,
        specs,
        launcher_argv,
    )


def command_mvp_demo_readiness_command_trace_entry_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessCommandTraceEntry | None:
    return command_demo_readiness_command_trace_entry_for_argv(
        argv,
        specs,
        launcher_argv,
    )


def require_command_mvp_demo_readiness_complete(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessGate:
    return require_command_demo_readiness_complete(specs, launcher_argv)


def command_mvp_demo_readiness_action_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, CommandDemoReadinessActionEntry], ...]:
    return command_demo_readiness_action_index(specs, launcher_argv)


def command_mvp_demo_readiness_action_entry(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessActionEntry | None:
    return command_demo_readiness_action_entry(engine_action, specs, launcher_argv)


def command_mvp_demo_readiness_exact_action_argv_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[tuple[str, ...], str], ...]:
    return command_demo_readiness_exact_action_argv_lookup_table(specs, launcher_argv)


def command_mvp_demo_readiness_cli_exact_action_argv_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[tuple[str, ...], str], ...]:
    return command_demo_readiness_cli_exact_action_argv_lookup_table(specs, launcher_argv)


def command_mvp_demo_readiness_exact_action_line_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return command_demo_readiness_exact_action_line_lookup_table(specs, launcher_argv)


def command_mvp_demo_readiness_cli_exact_action_line_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return command_demo_readiness_cli_exact_action_line_lookup_table(specs, launcher_argv)


def command_mvp_demo_readiness_cli_exact_argv_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_cli_exact_argv_for_engine_action(
        engine_action,
        specs,
        launcher_argv,
    )


def command_mvp_demo_readiness_cli_exact_line_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_cli_exact_line_for_engine_action(
        engine_action,
        specs,
        launcher_argv,
    )


def command_mvp_demo_readiness_exact_action_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessExactActionContract:
    return command_demo_readiness_exact_action_contract(specs, launcher_argv)


def command_mvp_demo_readiness_exact_action_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, str, str], ...]:
    return command_demo_readiness_exact_action_summary(specs, launcher_argv)


def command_mvp_demo_readiness_exact_cli_audit_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessExactCliAuditContract:
    return command_demo_readiness_exact_cli_audit_contract(specs, launcher_argv)


def command_mvp_demo_readiness_exact_cli_audit_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str, str, str, str, str, bool], ...]:
    return command_demo_readiness_exact_cli_audit_summary(specs, launcher_argv)


def command_mvp_demo_readiness_exact_action_script_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessExactActionScriptContract:
    return command_demo_readiness_exact_action_script_contract(specs, launcher_argv)


def command_mvp_demo_readiness_exact_action_script_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[int, str, str, str, str, str], ...]:
    return command_demo_readiness_exact_action_script_summary(specs, launcher_argv)


def command_mvp_demo_readiness_exact_action_shell_script_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_exact_action_shell_script_lines(specs, launcher_argv)


def command_mvp_demo_readiness_exact_action_shell_script_text(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_exact_action_shell_script_text(specs, launcher_argv)


def command_mvp_demo_readiness_cli_exact_action_shell_script_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_cli_exact_action_shell_script_lines(specs, launcher_argv)


def command_mvp_demo_readiness_cli_exact_action_shell_script_text(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_cli_exact_action_shell_script_text(specs, launcher_argv)


def command_mvp_demo_readiness_exact_action_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    return command_demo_readiness_exact_action_for_argv(argv, specs, launcher_argv)


def command_mvp_demo_readiness_cli_exact_action_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    return command_demo_readiness_cli_exact_action_for_argv(argv, specs, launcher_argv)


def command_mvp_demo_readiness_exact_action_entry_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessExactActionEntry | None:
    return command_demo_readiness_exact_action_entry_for_argv(argv, specs, launcher_argv)


def command_mvp_demo_readiness_exact_argv_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_exact_argv_for_engine_action(
        engine_action,
        specs,
        launcher_argv,
    )


def command_mvp_demo_readiness_exact_line_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_exact_line_for_engine_action(
        engine_action,
        specs,
        launcher_argv,
    )


def command_mvp_demo_readiness_action_entries_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[CommandDemoReadinessActionEntry, ...]:
    return command_demo_readiness_action_entries_for_argv(argv, specs, launcher_argv)


def command_mvp_demo_readiness_engine_action_matches_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_engine_action_matches_for_argv(argv, specs, launcher_argv)


def command_mvp_demo_readiness_action_lines_for_argv(
    argv: Sequence[str] | str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return command_demo_readiness_action_lines_for_argv(argv, specs, launcher_argv)


def command_mvp_demo_readiness_entry_for_engine_action(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessEntry | None:
    return command_demo_readiness_entry_for_engine_action(engine_action, specs, launcher_argv)


def command_mvp_demo_readiness_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, CommandDemoReadinessEntry], ...]:
    return command_demo_readiness_index(specs, launcher_argv)


def command_mvp_demo_readiness_entry_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessEntry | None:
    return command_demo_readiness_entry_for_flow_step(flow_step, specs, launcher_argv)


def command_mvp_demo_readiness_argv_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_argv_for_flow_step(flow_step, specs, launcher_argv)


def command_mvp_demo_readiness_line_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_line_for_flow_step(flow_step, specs, launcher_argv)


def command_mvp_demo_readiness_command_for_flow_step(
    flow_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    return command_demo_readiness_command_for_flow_step(flow_step, specs, launcher_argv)


def command_mvp_demo_readiness_index_by_command(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, CommandDemoReadinessEntry], ...]:
    return command_demo_readiness_index_by_command(specs, launcher_argv)


def command_mvp_demo_readiness_entry_for_command(
    command_name: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessEntry | None:
    return command_demo_readiness_entry_for_command(command_name, specs, launcher_argv)


def command_mvp_demo_readiness_argv_for_command(
    command_name: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_argv_for_command(command_name, specs, launcher_argv)


def command_mvp_demo_readiness_line_for_command(
    command_name: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_line_for_command(command_name, specs, launcher_argv)


def command_mvp_demo_readiness_flow_step_for_command(
    command_name: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    return command_demo_readiness_flow_step_for_command(command_name, specs, launcher_argv)


def command_mvp_demo_readiness_demo_path_step_for_command(
    command_name: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    return command_demo_readiness_demo_path_step_for_command(command_name, specs, launcher_argv)


def command_mvp_demo_readiness_index_by_demo_path_step(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, CommandDemoReadinessEntry], ...]:
    return command_demo_readiness_index_by_demo_path_step(specs, launcher_argv)


def command_mvp_demo_readiness_entry_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessEntry | None:
    return command_demo_readiness_entry_for_demo_path_step(demo_path_step, specs, launcher_argv)


def command_mvp_demo_readiness_argv_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_argv_for_demo_path_step(demo_path_step, specs, launcher_argv)


def command_mvp_demo_readiness_line_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str:
    return command_demo_readiness_line_for_demo_path_step(demo_path_step, specs, launcher_argv)


def command_mvp_demo_readiness_command_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    return command_demo_readiness_command_for_demo_path_step(demo_path_step, specs, launcher_argv)


def command_mvp_demo_readiness_flow_step_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> str | None:
    return command_demo_readiness_flow_step_for_demo_path_step(demo_path_step, specs, launcher_argv)


def command_mvp_demo_readiness_engine_actions_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_engine_actions_for_demo_path_step(demo_path_step, specs, launcher_argv)


def command_mvp_demo_readiness_exact_action_lines_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return command_demo_readiness_exact_action_lines_for_demo_path_step(
        demo_path_step,
        specs,
        launcher_argv,
    )


def command_mvp_demo_readiness_cli_exact_action_lines_for_demo_path_step(
    demo_path_step: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[tuple[str, str], ...]:
    return command_demo_readiness_cli_exact_action_lines_for_demo_path_step(
        demo_path_step,
        specs,
        launcher_argv,
    )


def command_mvp_demo_command_action_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoCommandActionContract:
    return command_demo_command_action_contract(specs)


def command_mvp_demo_command_action_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, tuple[str, ...], str, tuple[str, ...]], ...]:
    return command_demo_command_action_summary(specs)


def command_mvp_demo_command_action_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_command_action_lookup_table(specs)


def command_mvp_demo_action_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, CommandDemoActionEntry], ...]:
    return command_demo_action_index(specs)


def command_mvp_demo_action_entry(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoActionEntry | None:
    return command_demo_action_entry(engine_action, specs)


def command_mvp_demo_action_cli_token(
    engine_action: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> str | None:
    return command_demo_action_cli_token(engine_action, specs)


def command_demo_flow_route_catalog() -> tuple[CommandFlowRouteEntry, ...]:
    return command_flow_route_catalog(flow_steps=command_demo_flow_steps())


def command_demo_flow_route_contract() -> CommandFlowRouteContract:
    return command_flow_route_contract(flow_steps=command_demo_flow_steps())


def command_demo_flow_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    return command_flow_route_summary(specs, command_demo_flow_steps())


def command_mvp_flow_route_catalog() -> tuple[CommandFlowRouteEntry, ...]:
    return command_demo_flow_route_catalog()


def command_mvp_flow_route_contract() -> CommandFlowRouteContract:
    return command_demo_flow_route_contract()


def command_mvp_flow_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    return command_demo_flow_route_summary(specs)


def command_demo_flow_smoke_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return command_flow_smoke_tokens(specs, command_demo_flow_steps())


def command_mvp_flow_smoke_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return command_demo_flow_smoke_tokens(specs)


@lru_cache(maxsize=None)
def command_lookup_index(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[tuple[str, str], ...]:
    validate_command_catalog(specs)
    seen_tokens: set[str] = set()
    index: list[tuple[str, str]] = []
    for spec in specs:
        for alias in _lookup_tokens(spec):
            normalized_alias = _normalize_token(alias)
            if normalized_alias in seen_tokens:
                continue
            seen_tokens.add(normalized_alias)
            index.append((normalized_alias, spec.name))
    return tuple(index)


@lru_cache(maxsize=None)
def _command_flow_lookup_index(
    specs: tuple[CommandSpec, ...],
    flow_steps: tuple[str, ...],
    *,
    include_flow_step: bool,
) -> tuple[tuple[str, str], ...]:
    manifest = command_flow_manifest(specs, flow_steps)
    seen_tokens: set[str] = set()
    index: list[tuple[str, str]] = []
    for entry in manifest:
        tokens = (*entry.lookup_tokens, entry.flow_step) if include_flow_step else entry.lookup_tokens
        for token in tokens:
            normalized_token = _normalize_token(token)
            if normalized_token in seen_tokens:
                continue
            seen_tokens.add(normalized_token)
            index.append((normalized_token, entry.name))
    return tuple(index)


@lru_cache(maxsize=None)
def command_flow_surface_lookup_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, str], ...]:
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    return command_flow_lookup_surface(specs, ordered_flow_steps)


@lru_cache(maxsize=None)
def command_flow_lookup_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, str], ...]:
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    return _command_flow_lookup_index(specs, ordered_flow_steps, include_flow_step=False)


@lru_cache(maxsize=None)
def command_flow_lookup_surface(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, str], ...]:
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    surface_catalog = command_flow_surface_catalog(specs, ordered_flow_steps)
    seen_tokens: set[str] = set()
    index: list[tuple[str, str]] = []
    for entry in surface_catalog:
        for token in entry.surface_tokens:
            normalized_token = _normalize_token(token)
            if normalized_token in seen_tokens:
                continue
            seen_tokens.add(normalized_token)
            index.append((normalized_token, entry.name))
    return tuple(index)


@lru_cache(maxsize=None)
def command_flow_surface_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, ...], ...]:
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    surface_catalog = command_flow_surface_catalog(specs, ordered_flow_steps)
    return tuple(entry.surface_tokens for entry in surface_catalog)


@lru_cache(maxsize=None)
def command_flow_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    seen_tokens: set[str] = set()
    tokens: list[str] = []
    for surface_tokens in command_flow_surface_tokens(specs, ordered_flow_steps):
        for token in surface_tokens:
            normalized_token = _normalize_token(token)
            if normalized_token in seen_tokens:
                continue
            seen_tokens.add(normalized_token)
            tokens.append(normalized_token)
    return tuple(tokens)


@lru_cache(maxsize=None)
def command_flow_steps(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[str, ...]:
    validate_command_catalog(specs)
    return tuple(_normalize_token(spec.flow_step) for spec in specs)


def command_mvp_flow_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandFlowEntry, ...]:
    return command_demo_flow_catalog(specs)


def command_mvp_flow_manifest(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandManifestEntry, ...]:
    return command_demo_flow_manifest(specs)


def command_mvp_flow_sequence(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandFlowSequence:
    return command_demo_flow_sequence(specs)


def command_mvp_flow(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[CommandManifestEntry, ...]:
    return command_demo_flow_manifest(specs)


def command_mvp_flow_steps() -> tuple[str, ...]:
    return command_demo_flow_steps()


def command_mvp_flow_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_flow_lookup_table(specs)


def command_mvp_lookup_index(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[tuple[str, str], ...]:
    return command_demo_lookup_index(specs)


def command_mvp_flow_names(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[str, ...]:
    return command_demo_flow_names(specs)


def command_mvp_flow_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandSurfaceContract:
    return command_mvp_surface_contract(specs)


def command_mvp_cli_flow_contract() -> CommandCliFlowContract:
    return command_cli_flow_contract()


def command_demo_cli_flow_contract() -> CommandCliFlowContract:
    return command_cli_flow_contract()


def command_demo_cli_route_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandFlowRouteEntry, ...]:
    return command_cli_route_catalog(specs, flow_steps)


def command_demo_cli_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    return command_cli_route_summary(specs, flow_steps)


def command_demo_cli_route_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandCliRouteContract:
    return command_cli_route_contract(specs, flow_steps)


def command_mvp_cli_route_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandCliRouteContract:
    return command_cli_route_contract(specs, flow_steps)


def command_mvp_cli_route_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandFlowRouteEntry, ...]:
    return command_cli_route_catalog(specs, flow_steps)


def command_mvp_cli_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    return command_cli_route_summary(specs, flow_steps)


def command_surface_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandSurfaceContract:
    return command_mvp_surface_contract(specs)


def _resolve_contract_flow_steps(
    specs: tuple[CommandSpec, ...],
    flow_steps: tuple[str, ...] | None,
) -> tuple[str, ...]:
    if flow_steps is not None:
        return flow_steps
    # Keep the default flow surface aligned with the current MVP smoke path.
    if specs is COMMAND_SPECS:
        return command_demo_flow_steps()
    return command_flow_steps(specs)


def _validate_command_surface_contract(contract: CommandSurfaceContract) -> None:
    route_summary = tuple(
        (entry.flow_step, entry.name, entry.cli_tokens)
        for entry in contract.route_catalog
    )
    if contract.route_summary != route_summary:
        raise ValueError("Command surface route summary is inconsistent")
    if tuple(entry.flow_step for entry in contract.route_catalog) != contract.flow_steps:
        raise ValueError("Command surface route steps are inconsistent")
    if tuple(entry.name for entry in contract.route_catalog) != contract.names:
        raise ValueError("Command surface route names are inconsistent")
    if tuple(entry.cli_tokens[0] for entry in contract.route_catalog) != contract.smoke_tokens:
        raise ValueError("Command surface smoke tokens are inconsistent")
    if tuple((entry.flow_step, entry.name) for entry in contract.route_catalog) != contract.lookup_table:
        raise ValueError("Command surface route table is inconsistent")
    if tuple(entry.lookup_tokens for entry in contract.route_catalog) != contract.lookup_tokens:
        raise ValueError("Command surface route lookup tokens are inconsistent")
    if tuple(entry.surface_tokens for entry in contract.route_catalog) != contract.flow_surface_tokens:
        raise ValueError("Command surface route surface tokens are inconsistent")
    if contract.lookup_surface != contract.lookup_index:
        raise ValueError("Command surface lookup surfaces must match")


@lru_cache(maxsize=None)
def command_flow_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandSurfaceContract:
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    sequence = command_flow_sequence(specs, ordered_flow_steps)
    route_catalog = command_flow_route_catalog(flow_steps=ordered_flow_steps, specs=specs)
    route_summary = command_flow_route_summary(specs, ordered_flow_steps)
    contract = CommandSurfaceContract(
        flow_steps=sequence.flow_steps,
        names=sequence.names,
        smoke_tokens=command_flow_smoke_tokens(specs, ordered_flow_steps),
        manifest=command_flow_manifest(specs, ordered_flow_steps),
        lookup_table=sequence.lookup_table,
        lookup_index=command_flow_surface_lookup_index(specs, ordered_flow_steps),
        lookup_tokens=sequence.lookup_tokens,
        flow_tokens=command_flow_tokens(specs, ordered_flow_steps),
        flow_catalog=command_flow_catalog(specs, ordered_flow_steps),
        lookup_surface=command_flow_lookup_surface(specs, ordered_flow_steps),
        flow_surface_tokens=command_flow_surface_tokens(specs, ordered_flow_steps),
        route_catalog=route_catalog,
        route_summary=route_summary,
    )
    _validate_command_surface_contract(contract)
    return contract


def command_demo_flow_steps() -> tuple[str, ...]:
    return DEMO_COMMAND_FLOW_STEPS


def command_demo_flow_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandFlowEntry, ...]:
    return command_flow_catalog(specs, command_demo_flow_steps())


def command_demo_flow_manifest(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandManifestEntry, ...]:
    return command_flow_manifest(specs, command_demo_flow_steps())


def command_demo_flow_sequence(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandFlowSequence:
    return command_flow_sequence(specs, command_demo_flow_steps())


def command_demo_flow_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_flow_lookup_table(specs, command_demo_flow_steps())


def command_demo_lookup_index(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[tuple[str, str], ...]:
    return command_flow_lookup_index(specs, command_demo_flow_steps())


def command_demo_flow_lookup_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_flow_lookup_index(specs, command_demo_flow_steps())


def command_demo_flow_surface_lookup_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_flow_surface_lookup_index(specs, command_demo_flow_steps())


def command_demo_flow_lookup_surface(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_flow_lookup_surface(specs, command_demo_flow_steps())


def command_demo_flow_surface_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandFlowSurfaceEntry, ...]:
    return command_flow_surface_catalog(specs, command_demo_flow_steps())


def command_demo_flow_tokens(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[str, ...]:
    return command_flow_tokens(specs, command_demo_flow_steps())


def command_demo_flow_surface_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, ...], ...]:
    return command_flow_surface_tokens(specs, command_demo_flow_steps())


def command_demo_flow_names(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[str, ...]:
    return tuple(entry.name for entry in command_demo_flow_manifest(specs))


def command_demo_flow_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandSurfaceContract:
    return command_flow_contract(specs, command_demo_flow_steps())


def command_demo_surface_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandSurfaceContract:
    return command_demo_flow_contract(specs)


@lru_cache(maxsize=None)
def command_mvp_surface_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandSurfaceContract:
    return command_demo_surface_contract(specs)


def command_demo_flow(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[CommandManifestEntry, ...]:
    return command_demo_flow_manifest(specs)


def command_mvp_flow_lookup_surface(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_flow_lookup_surface(specs)


def command_mvp_flow_surface_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandFlowSurfaceEntry, ...]:
    return command_demo_flow_surface_catalog(specs)


def command_mvp_flow_tokens(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[str, ...]:
    return command_demo_flow_tokens(specs)


def command_mvp_flow_surface_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, ...], ...]:
    return command_demo_flow_surface_tokens(specs)


def command_mvp_flow_lookup_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_lookup_index(specs)


def command_mvp_flow_surface_lookup_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_flow_surface_lookup_index(specs)


@lru_cache(maxsize=None)
def command_tokens(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[str, ...]:
    validate_command_catalog(specs)
    return tuple(alias for spec in specs for alias in _lookup_tokens(spec))


def command_lookup_tokens(name: str) -> tuple[str, ...]:
    return command_lookup_tokens_for(COMMAND_SPECS, name)


def command_spec(name: str) -> CommandSpec | None:
    return command_spec_for(COMMAND_SPECS, name)


def command_aliases(name: str) -> tuple[str, ...]:
    return command_aliases_for(COMMAND_SPECS, name)


def canonical_command(name: str) -> str:
    return canonical_command_for(COMMAND_SPECS, name)
