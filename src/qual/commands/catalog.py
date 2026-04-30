from __future__ import annotations

import re
import shlex
from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache


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
class CommandDemoReadinessGate:
    is_complete: bool
    missing_engine_actions: tuple[str, ...]
    command_lines: tuple[str, ...]
    action_lines: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CommandDemoReadinessReport:
    is_complete: bool
    missing_engine_actions: tuple[str, ...]
    command_lines: tuple[str, ...]
    action_lines: tuple[tuple[str, str], ...]
    checklist_lines: tuple[str, ...]
    markdown: str


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
    seen_entrypoints: set[str] = set()
    for entrypoint in _CLI_ENTRYPOINTS:
        normalized_entrypoint = _normalize_token(entrypoint)
        if not normalized_entrypoint:
            raise ValueError("Command CLI entrypoints must not be empty")
        if normalized_entrypoint in seen_entrypoints:
            raise ValueError(f"Duplicate command CLI entrypoint: {entrypoint}")
        seen_entrypoints.add(normalized_entrypoint)
        if command_spec_for(COMMAND_SPECS, entrypoint) is None:
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


def _validate_demo_smoke_argv_coverage(flow_steps: tuple[str, ...]) -> None:
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
        tuple(entry.flow_step for entry in smoke_contract.entries)
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


def _validate_command_smoke_cli_launcher(launcher_argv: tuple[str, ...]) -> None:
    if not launcher_argv or any(not token.strip() for token in launcher_argv):
        raise ValueError("Command smoke CLI launcher argv must not be empty")


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


def command_demo_readiness_smoke_plan_argv(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    step = command_demo_readiness_smoke_plan_step(ordinal, specs, launcher_argv)
    if step is None:
        return ()
    return tuple(shlex.split(step.command_line))


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
    entry: CommandDemoReadinessHandoffEntry,
) -> str:
    action_lines = ", ".join(
        f"{engine_action} -> `{command_line}`"
        for engine_action, command_line in entry.action_lines
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
    handoff_contract = command_demo_readiness_handoff_contract(specs, launcher_argv)
    contract = CommandDemoReadinessHandoffChecklistContract(
        lines=tuple(
            CommandDemoReadinessHandoffChecklistLine(
                ordinal=entry.ordinal,
                demo_path_step=entry.demo_path_step,
                flow_step=entry.flow_step,
                name=entry.name,
                line=_format_command_demo_readiness_handoff_checklist_line(entry),
            )
            for entry in handoff_contract.entries
        )
    )
    _validate_command_demo_readiness_handoff_checklist_contract(contract, handoff_contract)
    return contract


def _validate_command_demo_readiness_handoff_checklist_contract(
    contract: CommandDemoReadinessHandoffChecklistContract,
    handoff_contract: CommandDemoReadinessHandoffContract,
) -> None:
    if tuple(line.ordinal for line in contract.lines) != tuple(
        entry.ordinal for entry in handoff_contract.entries
    ):
        raise ValueError("Command demo readiness handoff checklist ordinals are inconsistent")
    if tuple(line.demo_path_step for line in contract.lines) != tuple(
        entry.demo_path_step for entry in handoff_contract.entries
    ):
        raise ValueError("Command demo readiness handoff checklist path steps are inconsistent")
    if tuple(line.flow_step for line in contract.lines) != tuple(
        entry.flow_step for entry in handoff_contract.entries
    ):
        raise ValueError("Command demo readiness handoff checklist flow steps are inconsistent")
    if tuple(line.name for line in contract.lines) != tuple(
        entry.name for entry in handoff_contract.entries
    ):
        raise ValueError("Command demo readiness handoff checklist names are inconsistent")
    expected_lines = tuple(
        _format_command_demo_readiness_handoff_checklist_line(entry)
        for entry in handoff_contract.entries
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
    )
    return contract


def _validate_command_demo_readiness_route_contract(
    contract: CommandDemoReadinessRouteContract,
    readiness_contract: CommandDemoPathReadinessContract,
    routes_by_flow_step: dict[str, CommandDemoPathEntry],
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
    gate = CommandDemoReadinessGate(
        is_complete=not missing_engine_actions,
        missing_engine_actions=missing_engine_actions,
        command_lines=tuple(step.command_line for step in smoke_plan.steps),
        action_lines=tuple(action_line for step in smoke_plan.steps for action_line in step.action_lines),
    )
    _validate_command_demo_readiness_gate(gate, smoke_plan, specs=specs)
    return gate


def _validate_command_demo_readiness_gate(
    gate: CommandDemoReadinessGate,
    smoke_plan: CommandDemoReadinessSmokePlan,
    *,
    specs: tuple[CommandSpec, ...],
) -> None:
    expected_command_lines = tuple(step.command_line for step in smoke_plan.steps)
    expected_action_lines = tuple(
        action_line for step in smoke_plan.steps for action_line in step.action_lines
    )
    if gate.command_lines != expected_command_lines:
        raise ValueError("Command demo readiness gate command lines are inconsistent")
    if gate.action_lines != expected_action_lines:
        raise ValueError("Command demo readiness gate action lines are inconsistent")
    if tuple(engine_action for engine_action, _ in gate.action_lines) != command_demo_engine_actions(specs):
        raise ValueError("Command demo readiness gate action coverage is inconsistent")
    if gate.is_complete != (not gate.missing_engine_actions):
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


def require_command_demo_readiness_complete(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessGate:
    gate = command_demo_readiness_gate(specs, launcher_argv)
    if not gate.is_complete:
        missing = ", ".join(gate.missing_engine_actions)
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
def command_demo_readiness_shell_script(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> CommandDemoReadinessShellScript:
    smoke_plan = command_demo_readiness_smoke_plan(specs, launcher_argv)
    command_lines = tuple(step.command_line for step in smoke_plan.steps)
    action_lines = tuple(action_line for step in smoke_plan.steps for action_line in step.action_lines)
    lines: list[str] = ["set -euo pipefail"]
    for step in smoke_plan.steps:
        lines.append(f"# {step.ordinal}. {step.demo_path_step} [{step.flow_step}/{step.name}]")
        lines.append(step.command_line)
        for engine_action, command_line in step.action_lines:
            lines.append(f"# action: {engine_action}")
            lines.append(command_line)
    script = CommandDemoReadinessShellScript(
        lines=tuple(lines),
        command_lines=command_lines,
        action_lines=action_lines,
        text="\n".join(lines),
    )
    _validate_command_demo_readiness_shell_script(script, smoke_plan)
    return script


def _validate_command_demo_readiness_shell_script(
    script: CommandDemoReadinessShellScript,
    smoke_plan: CommandDemoReadinessSmokePlan,
) -> None:
    expected_command_lines = tuple(step.command_line for step in smoke_plan.steps)
    expected_action_lines = tuple(
        action_line for step in smoke_plan.steps for action_line in step.action_lines
    )
    if script.command_lines != expected_command_lines:
        raise ValueError("Command demo readiness shell script command lines are inconsistent")
    if script.action_lines != expected_action_lines:
        raise ValueError("Command demo readiness shell script action lines are inconsistent")
    if not script.lines or script.lines[0] != "set -euo pipefail":
        raise ValueError("Command demo readiness shell script must start with strict shell mode")
    if script.text != "\n".join(script.lines):
        raise ValueError("Command demo readiness shell script text is inconsistent")
    if any(not line.strip() for line in script.lines):
        raise ValueError("Command demo readiness shell script lines must not be empty")
    executable_lines = tuple(line for line in script.lines if not line.startswith("#"))
    expected_executable_lines = tuple(
        line
        for grouped_lines in (
            ("set -euo pipefail",),
            *(
                (step.command_line, *(command_line for _, command_line in step.action_lines))
                for step in smoke_plan.steps
            ),
        )
        for line in grouped_lines
    )
    if executable_lines != expected_executable_lines:
        raise ValueError("Command demo readiness shell script executable lines are inconsistent")


def command_demo_readiness_shell_script_lines(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_shell_script(specs, launcher_argv).lines


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
    contract = CommandDemoReadinessTraceContract(
        entries=tuple(
            CommandDemoReadinessTraceEntry(
                ordinal=entry.ordinal,
                engine_action=engine_action,
                demo_path_step=entry.demo_path_step,
                flow_step=entry.flow_step,
                name=entry.name,
                command_line=entry.command_line,
                action_line=action_line,
            )
            for entry in handoff_contract.entries
            for engine_action, action_line in entry.action_lines
        )
    )
    _validate_command_demo_readiness_trace_contract(contract, handoff_contract, specs=specs)
    return contract


def _validate_command_demo_readiness_trace_contract(
    contract: CommandDemoReadinessTraceContract,
    handoff_contract: CommandDemoReadinessHandoffContract,
    *,
    specs: tuple[CommandSpec, ...],
) -> None:
    expected_entries = tuple(
        (
            entry.ordinal,
            engine_action,
            entry.demo_path_step,
            entry.flow_step,
            entry.name,
            entry.command_line,
            action_line,
        )
        for entry in handoff_contract.entries
        for engine_action, action_line in entry.action_lines
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
    requested_canonical_command_argv = _canonicalize_smoke_command_argv(specs, requested_command_argv)
    matches: list[CommandDemoReadinessActionEntry] = []
    for entry in command_demo_readiness_action_contract(specs, launcher_argv).entries:
        action_argv = _argv_without_launcher(entry.action_command_argv, launcher_argv)
        if (
            requested_argv == entry.action_command_argv
            or requested_command_argv == action_argv
            or requested_canonical_command_argv == action_argv
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


def _normalize_smoke_argv(argv: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(token.strip() for token in argv if token.strip())


def _coerce_smoke_argv(argv: Sequence[str] | str) -> tuple[str, ...]:
    if isinstance(argv, str):
        return tuple(shlex.split(argv))
    return tuple(argv)


def _argv_without_launcher(argv: tuple[str, ...], launcher_argv: tuple[str, ...]) -> tuple[str, ...]:
    if argv[: len(launcher_argv)] == launcher_argv:
        return argv[len(launcher_argv) :]
    return argv


def _canonicalize_smoke_command_argv(
    specs: tuple[CommandSpec, ...],
    argv: tuple[str, ...],
) -> tuple[str, ...]:
    if not argv:
        return ()
    return (canonical_command_for(specs, argv[0]), *argv[1:])


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
    requested_canonical_command_argv = _canonicalize_smoke_command_argv(specs, requested_command_argv)
    for entry in command_demo_readiness_contract(specs, launcher_argv).entries:
        entry_command_argv = _argv_without_launcher(entry.command_argv, launcher_argv)
        if (
            requested_argv == entry.command_argv
            or requested_command_argv == entry_command_argv
            or requested_canonical_command_argv == entry_command_argv
        ):
            return entry
        for _, action_command_argv in entry.action_command_argv:
            action_argv = _argv_without_launcher(action_command_argv, launcher_argv)
            if (
                requested_argv == action_command_argv
                or requested_command_argv == action_argv
                or requested_canonical_command_argv == action_argv
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
    requested_command_argv = _argv_without_launcher(requested_argv, launcher_argv)
    requested_canonical_command_argv = _canonicalize_smoke_command_argv(specs, requested_command_argv)
    for entry in command_demo_readiness_contract(specs, launcher_argv).entries:
        entry_command_argv = _argv_without_launcher(entry.command_argv, launcher_argv)
        if (
            requested_argv == entry.command_argv
            or requested_command_argv == entry_command_argv
            or requested_canonical_command_argv == entry_command_argv
        ):
            return entry.command_argv
        for _, action_command_argv in entry.action_command_argv:
            action_argv = _argv_without_launcher(action_command_argv, launcher_argv)
            if (
                requested_argv == action_command_argv
                or requested_command_argv == action_argv
                or requested_canonical_command_argv == action_argv
            ):
                return action_command_argv
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


def command_mvp_demo_readiness_smoke_plan_argv(
    ordinal: int,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    launcher_argv: tuple[str, ...] = COMMAND_SMOKE_CLI_LAUNCHER_ARGV,
) -> tuple[str, ...]:
    return command_demo_readiness_smoke_plan_argv(ordinal, specs, launcher_argv)


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
