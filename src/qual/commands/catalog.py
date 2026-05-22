from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class CommandSpec:
    name: str
    aliases: tuple[str, ...] = ()
    description: str = ""
    flow_step: str = "general"
    smoke_args: tuple[str, ...] = ()


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
    demo_path_steps: tuple[CommandDemoPathStep, ...] = ()


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
    demo_step: str = ""


@dataclass(frozen=True)
class CommandFlowRouteContract:
    entries: tuple[CommandFlowRouteEntry, ...]


@dataclass(frozen=True)
class CommandCliSmokeStep:
    flow_step: str
    name: str
    cli_token: str
    argv: tuple[str, ...]
    lookup_tokens: tuple[str, ...]
    description: str
    demo_step: str = ""


@dataclass(frozen=True)
class CommandCliSmokePlan:
    flow_steps: tuple[str, ...]
    route_summary: tuple[tuple[str, str, tuple[str, ...]], ...]
    steps: tuple[CommandCliSmokeStep, ...]
    argv: tuple[tuple[str, ...], ...]
    demo_path_steps: tuple[CommandDemoPathStep, ...] = ()


@dataclass(frozen=True)
class CommandCliSmokeCommand:
    flow_step: str
    name: str
    cli_token: str
    argv: tuple[str, ...]
    command: tuple[str, ...]
    lookup_tokens: tuple[str, ...]
    description: str
    demo_step: str = ""


@dataclass(frozen=True)
class CommandDemoPathStep:
    demo_step: str
    flow_step: str
    name: str
    cli_token: str
    argv: tuple[str, ...]
    description: str
    lookup_tokens: tuple[str, ...] = ()


@dataclass(frozen=True)
class CommandDemoPathCommand:
    demo_step: str
    flow_step: str
    name: str
    cli_token: str
    argv: tuple[str, ...]
    command: tuple[str, ...]
    description: str
    lookup_tokens: tuple[str, ...] = ()


@dataclass(frozen=True)
class CommandDemoPathContract:
    demo_steps: tuple[str, ...]
    flow_steps: tuple[str, ...]
    route_summary: tuple[tuple[str, str, tuple[str, ...]], ...]
    argv: tuple[tuple[str, ...], ...]
    commands: tuple[tuple[str, ...], ...]
    command_lookup_table: tuple[tuple[tuple[str, ...], str], ...]
    entries: tuple[CommandDemoPathCommand, ...]


@dataclass(frozen=True)
class CommandDemoPathReadinessStep:
    demo_step: str
    flow_step: str
    name: str
    cli_token: str
    argv: tuple[str, ...]
    command: tuple[str, ...]
    route_tokens: tuple[str, ...]
    description: str
    lookup_tokens: tuple[str, ...]
    ready: bool


@dataclass(frozen=True)
class CommandDemoPathReadiness:
    program: str
    ready: bool
    command_count: int
    demo_steps: tuple[str, ...]
    flow_steps: tuple[str, ...]
    argv: tuple[tuple[str, ...], ...]
    commands: tuple[tuple[str, ...], ...]
    command_lookup_table: tuple[tuple[tuple[str, ...], str], ...]
    route_summary: tuple[tuple[str, str, tuple[str, ...]], ...]
    steps: tuple[CommandDemoPathReadinessStep, ...] = ()
    missing_demo_steps: tuple[str, ...] = ()


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


def _validate_route_cli_tokens(
    route_catalog: tuple[CommandFlowRouteEntry, ...],
    cli_tokens: tuple[str, ...],
) -> None:
    parseable_tokens = set(cli_tokens)
    for entry in route_catalog:
        missing_tokens = tuple(
            token for token in entry.cli_tokens if token not in parseable_tokens
        )
        if missing_tokens:
            joined_tokens = ", ".join(missing_tokens)
            raise ValueError(f"Command CLI route has unparseable tokens for {entry.name}: {joined_tokens}")


def _validate_demo_path_steps_by_flow_step() -> None:
    seen_flow_steps: set[str] = set()
    seen_demo_steps: set[str] = set()
    for flow_step, demo_step in DEMO_PATH_STEPS_BY_FLOW_STEP:
        normalized_flow_step = _normalize_token(flow_step)
        normalized_demo_step = _normalize_token(demo_step)
        if not normalized_flow_step:
            raise ValueError("Command demo path flow steps must not be empty")
        if not normalized_demo_step:
            raise ValueError("Command demo path labels must not be empty")
        if normalized_flow_step in seen_flow_steps:
            raise ValueError(f"Duplicate command demo path flow step: {flow_step}")
        if normalized_demo_step in seen_demo_steps:
            raise ValueError(f"Duplicate command demo path label: {demo_step}")
        seen_flow_steps.add(normalized_flow_step)
        seen_demo_steps.add(normalized_demo_step)

    required_flow_steps = set(_normalize_flow_steps(DEMO_COMMAND_FLOW_STEPS))
    missing_flow_steps = tuple(
        flow_step
        for flow_step in DEMO_COMMAND_FLOW_STEPS
        if _normalize_token(flow_step) not in seen_flow_steps
    )
    if missing_flow_steps:
        joined_steps = ", ".join(missing_flow_steps)
        raise ValueError(f"Command demo path labels are missing for flow steps: {joined_steps}")

    extra_flow_steps = tuple(
        flow_step
        for flow_step in seen_flow_steps
        if flow_step not in required_flow_steps
    )
    if extra_flow_steps:
        joined_steps = ", ".join(extra_flow_steps)
        raise ValueError(f"Command demo path labels include unknown flow steps: {joined_steps}")


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
        smoke_args=("list",),
    ),
    CommandSpec(
        name="terminal",
        description="Run terminal export handoff routing.",
        flow_step="export-handoff",
    ),
)

# Keep the parser surface explicit: only these tokens are accepted by the current CLI.
# Each token must resolve through the command catalog so the surface cannot drift.
_CLI_ENTRYPOINTS: tuple[str, ...] = (
    "bootstrap",
    "diff-preview",
    "diff",
    "context-basket",
    "terminal",
)
DEMO_COMMAND_FLOW_STEPS: tuple[str, ...] = (
    "project-open",
    "retrieval",
    "patch-review",
    "export-handoff",
)
MVP_COMMAND_FLOW_STEPS: tuple[str, ...] = DEMO_COMMAND_FLOW_STEPS
DEMO_PATH_STEPS_BY_FLOW_STEP: tuple[tuple[str, str], ...] = (
    ("project-open", "open-project-document"),
    ("retrieval", "retrieve-relevant-material"),
    ("patch-review", "preview-apply-or-reject-patch"),
    ("export-handoff", "persist-and-continue"),
)


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


def normalize_command_argv(
    argv: tuple[str, ...] | list[str] | None,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    raw = tuple(argv or ())
    if not raw:
        return ("bootstrap",)

    first, *rest = raw
    if first.startswith("-"):
        return ("bootstrap", *raw)

    canonical_name = canonical_command_for(specs, first)
    if not canonical_name:
        return raw
    return (canonical_name, *rest)


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


@lru_cache(maxsize=None)
def command_cli_contract() -> CommandCliContract:
    lookup_table = command_cli_lookup_table()
    canonical_names = command_names()
    seen_canonical_names: set[str] = set()
    lookup_canonical_names: list[str] = []
    for _, canonical_name in lookup_table:
        if canonical_name in seen_canonical_names:
            continue
        seen_canonical_names.add(canonical_name)
        lookup_canonical_names.append(canonical_name)
    if tuple(lookup_canonical_names) != canonical_names:
        raise ValueError("Command CLI canonical names are inconsistent")
    return CommandCliContract(
        tokens=command_cli_tokens(),
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
    if contract.lookup_table != cli_contract.lookup_table:
        raise ValueError("Command CLI route lookup table is inconsistent")
    if contract.lookup_surface != command_flow_lookup_surface(specs, flow_steps):
        raise ValueError("Command CLI route lookup surface is inconsistent")
    if contract.flow_surface_tokens != command_flow_surface_tokens(specs, flow_steps):
        raise ValueError("Command CLI route surface tokens are inconsistent")
    _validate_route_cli_tokens(contract.route_catalog, cli_contract.tokens)


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
def command_flow_route_catalog(
    flow_steps: tuple[str, ...] | None = None,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandFlowRouteEntry, ...]:
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    # Keep the route view in smoke-flow order while preserving the parser tokens
    # that dispatch to each command.
    route_catalog = command_flow_surface_catalog(specs, ordered_flow_steps)
    cli_tokens_by_name = _route_cli_tokens_by_name(specs)
    demo_labels_by_flow_step = _demo_path_labels_by_flow_step()
    return tuple(
        CommandFlowRouteEntry(
            flow_step=entry.flow_step,
            name=entry.name,
            cli_tokens=cli_tokens_by_name.get(entry.name, (entry.name,)),
            lookup_tokens=entry.lookup_tokens,
            surface_tokens=entry.surface_tokens,
            description=entry.description,
            demo_step=demo_labels_by_flow_step.get(entry.flow_step, ""),
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
def command_cli_smoke_steps(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandCliSmokeStep, ...]:
    route_catalog = command_flow_route_catalog(flow_steps=flow_steps, specs=specs)
    if specs == COMMAND_SPECS:
        _validate_route_cli_tokens(route_catalog, command_cli_tokens())
    return tuple(
        CommandCliSmokeStep(
            flow_step=entry.flow_step,
            name=entry.name,
            cli_token=entry.cli_tokens[0],
            argv=(entry.cli_tokens[0], *_smoke_args_for_command(specs, entry.name)),
            lookup_tokens=entry.lookup_tokens,
            description=entry.description,
            demo_step=entry.demo_step,
        )
        for entry in route_catalog
    )


def _smoke_args_for_command(
    specs: tuple[CommandSpec, ...],
    name: str,
) -> tuple[str, ...]:
    spec = command_spec_for(specs, name)
    if spec is None:
        raise ValueError(f"Unknown command smoke target: {name}")
    return spec.smoke_args


def command_cli_smoke_argv(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, ...], ...]:
    return tuple(step.argv for step in command_cli_smoke_steps(specs, flow_steps))


def command_cli_smoke_commands(
    program: str = "qual-bootstrap",
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, ...], ...]:
    return tuple(entry.command for entry in command_cli_smoke_command_entries(program, specs, flow_steps))


def command_cli_smoke_command_entries(
    program: str = "qual-bootstrap",
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandCliSmokeCommand, ...]:
    normalized_program = _normalize_smoke_program(program)
    smoke_plan = command_cli_smoke_plan(specs, flow_steps)
    entries = tuple(
        CommandCliSmokeCommand(
            flow_step=step.flow_step,
            name=step.name,
            cli_token=step.cli_token,
            argv=step.argv,
            command=(normalized_program, *step.argv),
            lookup_tokens=step.lookup_tokens,
            description=step.description,
            demo_step=step.demo_step,
        )
        for step in smoke_plan.steps
    )
    _validate_command_cli_smoke_command_entries(entries, smoke_plan)
    return entries


def _validate_command_cli_smoke_command_entries(
    entries: tuple[CommandCliSmokeCommand, ...],
    smoke_plan: CommandCliSmokePlan,
) -> None:
    if tuple(entry.argv for entry in entries) != smoke_plan.argv:
        raise ValueError("Command CLI smoke command argv is inconsistent")
    if tuple(entry.flow_step for entry in entries) != smoke_plan.flow_steps:
        raise ValueError("Command CLI smoke command flow steps are inconsistent")
    if tuple(entry.name for entry in entries) != tuple(step.name for step in smoke_plan.steps):
        raise ValueError("Command CLI smoke command names are inconsistent")
    if tuple(entry.cli_token for entry in entries) != tuple(step.cli_token for step in smoke_plan.steps):
        raise ValueError("Command CLI smoke command tokens are inconsistent")
    if tuple(entry.demo_step for entry in entries) != tuple(step.demo_step for step in smoke_plan.steps):
        raise ValueError("Command CLI smoke command demo steps are inconsistent")
    for entry in entries:
        if entry.command != (entry.command[0], *entry.argv):
            raise ValueError("Command CLI smoke command tuple is inconsistent")


def _normalize_smoke_program(program: str) -> str:
    normalized_program = program.strip()
    if not normalized_program:
        raise ValueError("Command CLI smoke program must not be empty")
    return normalized_program


def _validate_command_cli_smoke_plan(plan: CommandCliSmokePlan) -> None:
    route_flow_steps = tuple(flow_step for flow_step, _, _ in plan.route_summary)
    if plan.flow_steps != route_flow_steps:
        raise ValueError("Command CLI smoke plan flow steps are inconsistent")
    if plan.flow_steps != tuple(step.flow_step for step in plan.steps):
        raise ValueError("Command CLI smoke plan steps are inconsistent")
    route_names = tuple(name for _, name, _ in plan.route_summary)
    if route_names != tuple(step.name for step in plan.steps):
        raise ValueError("Command CLI smoke plan names are inconsistent")
    primary_tokens = tuple(cli_tokens[0] for _, _, cli_tokens in plan.route_summary)
    if primary_tokens != tuple(step.cli_token for step in plan.steps):
        raise ValueError("Command CLI smoke plan primary tokens are inconsistent")
    if plan.argv != tuple(step.argv for step in plan.steps):
        raise ValueError("Command CLI smoke plan argv is inconsistent")
    if plan.demo_path_steps:
        if plan.flow_steps != tuple(step.flow_step for step in plan.demo_path_steps):
            raise ValueError("Command CLI smoke plan demo path steps are inconsistent")
        if tuple(step.name for step in plan.demo_path_steps) != tuple(step.name for step in plan.steps):
            raise ValueError("Command CLI smoke plan demo path names are inconsistent")
        if tuple(step.argv for step in plan.demo_path_steps) != plan.argv:
            raise ValueError("Command CLI smoke plan demo path argv is inconsistent")
        demo_path_labels = tuple(step.demo_step for step in plan.demo_path_steps)
        smoke_step_labels = tuple(step.demo_step for step in plan.steps)
        if demo_path_labels != smoke_step_labels:
            raise ValueError("Command CLI smoke plan demo path labels are inconsistent")


def _command_demo_path_steps_for_smoke_steps(
    smoke_steps: tuple[CommandCliSmokeStep, ...],
) -> tuple[CommandDemoPathStep, ...]:
    if _missing_demo_path_flow_steps(smoke_steps):
        return ()
    return tuple(
        CommandDemoPathStep(
            demo_step=step.demo_step,
            flow_step=step.flow_step,
            name=step.name,
            cli_token=step.cli_token,
            argv=step.argv,
            description=step.description,
            lookup_tokens=step.lookup_tokens,
        )
        for step in smoke_steps
    )


def _missing_demo_path_flow_steps(
    smoke_steps: tuple[CommandCliSmokeStep, ...],
) -> tuple[str, ...]:
    labels_by_flow_step = _demo_path_labels_by_flow_step()
    return tuple(step.flow_step for step in smoke_steps if step.flow_step not in labels_by_flow_step)


@lru_cache(maxsize=None)
def command_cli_smoke_plan(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandCliSmokePlan:
    route_summary = command_flow_route_summary(specs, flow_steps)
    steps = command_cli_smoke_steps(specs, flow_steps)
    plan = CommandCliSmokePlan(
        flow_steps=tuple(flow_step for flow_step, _, _ in route_summary),
        route_summary=route_summary,
        steps=steps,
        argv=tuple(step.argv for step in steps),
        demo_path_steps=_command_demo_path_steps_for_smoke_steps(steps),
    )
    _validate_command_cli_smoke_plan(plan)
    return plan


def _demo_path_labels_by_flow_step() -> dict[str, str]:
    _validate_demo_path_steps_by_flow_step()
    return {
        _normalize_token(flow_step): _normalize_token(demo_step)
        for flow_step, demo_step in DEMO_PATH_STEPS_BY_FLOW_STEP
    }


def command_demo_path_steps(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandDemoPathStep, ...]:
    smoke_plan = command_cli_smoke_plan(specs, flow_steps)
    if not smoke_plan.demo_path_steps:
        joined_steps = ", ".join(_missing_demo_path_flow_steps(smoke_plan.steps))
        raise ValueError(f"Command demo path labels are missing for flow steps: {joined_steps}")
    return smoke_plan.demo_path_steps


def command_demo_path_argv(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, ...], ...]:
    return tuple(step.argv for step in command_demo_path_steps(specs, flow_steps))


def command_demo_path_commands(
    program: str = "qual-bootstrap",
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, ...], ...]:
    return tuple(entry.command for entry in command_demo_path_command_entries(program, specs, flow_steps))


def command_demo_path_command_entries(
    program: str = "qual-bootstrap",
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandDemoPathCommand, ...]:
    normalized_program = _normalize_smoke_program(program)
    demo_steps = command_demo_path_steps(specs, flow_steps)
    entries = tuple(
        CommandDemoPathCommand(
            demo_step=step.demo_step,
            flow_step=step.flow_step,
            name=step.name,
            cli_token=step.cli_token,
            argv=step.argv,
            command=(normalized_program, *step.argv),
            description=step.description,
            lookup_tokens=step.lookup_tokens,
        )
        for step in demo_steps
    )
    _validate_command_demo_path_command_entries(entries, demo_steps)
    return entries


def command_demo_path_contract(
    program: str = "qual-bootstrap",
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandDemoPathContract:
    smoke_plan = command_cli_smoke_plan(specs, flow_steps)
    entries = command_demo_path_command_entries(program, specs, flow_steps)
    contract = CommandDemoPathContract(
        demo_steps=tuple(entry.demo_step for entry in entries),
        flow_steps=tuple(entry.flow_step for entry in entries),
        route_summary=smoke_plan.route_summary,
        argv=tuple(entry.argv for entry in entries),
        commands=tuple(entry.command for entry in entries),
        command_lookup_table=tuple((entry.command, entry.demo_step) for entry in entries),
        entries=entries,
    )
    _validate_command_demo_path_contract(contract, smoke_plan)
    return contract


def command_demo_path_readiness(
    program: str = "qual-bootstrap",
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandDemoPathReadiness:
    normalized_program = _normalize_smoke_program(program)
    contract = command_demo_path_contract(normalized_program, specs, flow_steps)
    steps = _command_demo_path_readiness_steps(contract, normalized_program)
    missing_demo_steps = _missing_demo_path_steps(contract.demo_steps)
    readiness = CommandDemoPathReadiness(
        program=normalized_program,
        ready=bool(steps) and not missing_demo_steps and all(step.ready for step in steps),
        command_count=len(contract.entries),
        demo_steps=contract.demo_steps,
        flow_steps=contract.flow_steps,
        missing_demo_steps=missing_demo_steps,
        argv=contract.argv,
        commands=contract.commands,
        command_lookup_table=contract.command_lookup_table,
        route_summary=contract.route_summary,
        steps=steps,
    )
    _validate_command_demo_path_readiness(readiness, contract)
    return readiness


def _command_demo_path_readiness_steps(
    contract: CommandDemoPathContract,
    program: str,
) -> tuple[CommandDemoPathReadinessStep, ...]:
    route_tokens_by_flow_step = {
        flow_step: cli_tokens for flow_step, _, cli_tokens in contract.route_summary
    }
    return tuple(
        CommandDemoPathReadinessStep(
            demo_step=entry.demo_step,
            flow_step=entry.flow_step,
            name=entry.name,
            cli_token=entry.cli_token,
            argv=entry.argv,
            command=entry.command,
            route_tokens=route_tokens_by_flow_step.get(entry.flow_step, ()),
            description=entry.description,
            lookup_tokens=entry.lookup_tokens,
            ready=(
                entry.command == (program, *entry.argv)
                and bool(route_tokens_by_flow_step.get(entry.flow_step, ()))
                and entry.cli_token in route_tokens_by_flow_step.get(entry.flow_step, ())
            ),
        )
        for entry in contract.entries
    )


def _missing_demo_path_steps(demo_steps: tuple[str, ...]) -> tuple[str, ...]:
    present_demo_steps = set(demo_steps)
    return tuple(
        demo_step
        for _, demo_step in DEMO_PATH_STEPS_BY_FLOW_STEP
        if demo_step not in present_demo_steps
    )


def _validate_command_demo_path_readiness(
    readiness: CommandDemoPathReadiness,
    contract: CommandDemoPathContract,
) -> None:
    if readiness.command_count != len(contract.entries):
        raise ValueError("Command demo path readiness count is inconsistent")
    if readiness.demo_steps != contract.demo_steps:
        raise ValueError("Command demo path readiness labels are inconsistent")
    if readiness.flow_steps != contract.flow_steps:
        raise ValueError("Command demo path readiness flow steps are inconsistent")
    if readiness.missing_demo_steps != _missing_demo_path_steps(contract.demo_steps):
        raise ValueError("Command demo path readiness missing labels are inconsistent")
    if readiness.argv != contract.argv:
        raise ValueError("Command demo path readiness argv is inconsistent")
    if readiness.commands != contract.commands:
        raise ValueError("Command demo path readiness commands are inconsistent")
    if readiness.command_lookup_table != contract.command_lookup_table:
        raise ValueError("Command demo path readiness command lookup table is inconsistent")
    if readiness.route_summary != contract.route_summary:
        raise ValueError("Command demo path readiness route summary is inconsistent")
    if tuple(step.demo_step for step in readiness.steps) != readiness.demo_steps:
        raise ValueError("Command demo path readiness step labels are inconsistent")
    if tuple(step.flow_step for step in readiness.steps) != readiness.flow_steps:
        raise ValueError("Command demo path readiness step flow steps are inconsistent")
    if tuple(step.argv for step in readiness.steps) != readiness.argv:
        raise ValueError("Command demo path readiness step argv is inconsistent")
    if tuple(step.command for step in readiness.steps) != readiness.commands:
        raise ValueError("Command demo path readiness step commands are inconsistent")
    if tuple(step.name for step in readiness.steps) != tuple(entry.name for entry in contract.entries):
        raise ValueError("Command demo path readiness step names are inconsistent")
    if tuple(step.cli_token for step in readiness.steps) != tuple(
        entry.cli_token for entry in contract.entries
    ):
        raise ValueError("Command demo path readiness step CLI tokens are inconsistent")
    if tuple(step.description for step in readiness.steps) != tuple(
        entry.description for entry in contract.entries
    ):
        raise ValueError("Command demo path readiness step descriptions are inconsistent")
    if tuple(step.lookup_tokens for step in readiness.steps) != tuple(
        entry.lookup_tokens for entry in contract.entries
    ):
        raise ValueError("Command demo path readiness step lookup tokens are inconsistent")
    if readiness.ready != (
        bool(readiness.steps)
        and not readiness.missing_demo_steps
        and all(step.ready for step in readiness.steps)
    ):
        raise ValueError("Command demo path readiness status is inconsistent")
    for step in readiness.steps:
        if not step.command or step.command[0] != readiness.program:
            raise ValueError("Command demo path readiness program is inconsistent")
        if not step.route_tokens:
            raise ValueError("Command demo path readiness route tokens are missing")


def _validate_command_demo_path_contract(
    contract: CommandDemoPathContract,
    smoke_plan: CommandCliSmokePlan,
) -> None:
    if contract.flow_steps != smoke_plan.flow_steps:
        raise ValueError("Command demo path contract flow steps are inconsistent")
    if contract.route_summary != smoke_plan.route_summary:
        raise ValueError("Command demo path contract route summary is inconsistent")
    if contract.argv != smoke_plan.argv:
        raise ValueError("Command demo path contract argv is inconsistent")
    if tuple(entry.demo_step for entry in contract.entries) != contract.demo_steps:
        raise ValueError("Command demo path contract labels are inconsistent")
    if tuple(entry.flow_step for entry in contract.entries) != contract.flow_steps:
        raise ValueError("Command demo path contract entries are inconsistent")
    if tuple(entry.argv for entry in contract.entries) != contract.argv:
        raise ValueError("Command demo path contract entry argv is inconsistent")
    if tuple(entry.command for entry in contract.entries) != contract.commands:
        raise ValueError("Command demo path contract commands are inconsistent")
    if tuple((entry.command, entry.demo_step) for entry in contract.entries) != contract.command_lookup_table:
        raise ValueError("Command demo path contract command lookup table is inconsistent")


def command_demo_path_command_lookup_table(
    program: str = "qual-bootstrap",
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[tuple[str, ...], str], ...]:
    return command_demo_path_contract(program, specs, flow_steps).command_lookup_table


def _validate_command_demo_path_command_entries(
    entries: tuple[CommandDemoPathCommand, ...],
    demo_steps: tuple[CommandDemoPathStep, ...],
) -> None:
    if tuple(entry.demo_step for entry in entries) != tuple(step.demo_step for step in demo_steps):
        raise ValueError("Command demo path command labels are inconsistent")
    if tuple(entry.flow_step for entry in entries) != tuple(step.flow_step for step in demo_steps):
        raise ValueError("Command demo path command flow steps are inconsistent")
    if tuple(entry.name for entry in entries) != tuple(step.name for step in demo_steps):
        raise ValueError("Command demo path command names are inconsistent")
    if tuple(entry.cli_token for entry in entries) != tuple(step.cli_token for step in demo_steps):
        raise ValueError("Command demo path command tokens are inconsistent")
    if tuple(entry.argv for entry in entries) != tuple(step.argv for step in demo_steps):
        raise ValueError("Command demo path command argv is inconsistent")
    if tuple(entry.description for entry in entries) != tuple(step.description for step in demo_steps):
        raise ValueError("Command demo path command descriptions are inconsistent")
    if tuple(entry.lookup_tokens for entry in entries) != tuple(
        step.lookup_tokens for step in demo_steps
    ):
        raise ValueError("Command demo path command lookup tokens are inconsistent")
    for entry in entries:
        if entry.command != (entry.command[0], *entry.argv):
            raise ValueError("Command demo path command tuple is inconsistent")


def command_demo_cli_smoke_steps() -> tuple[CommandCliSmokeStep, ...]:
    return command_cli_smoke_steps(flow_steps=command_demo_flow_steps())


def command_mvp_cli_smoke_steps() -> tuple[CommandCliSmokeStep, ...]:
    return command_demo_cli_smoke_steps()


def command_demo_cli_smoke_argv() -> tuple[tuple[str, ...], ...]:
    return command_cli_smoke_argv(flow_steps=command_demo_flow_steps())


def command_mvp_cli_smoke_argv() -> tuple[tuple[str, ...], ...]:
    return command_demo_cli_smoke_argv()


def command_demo_cli_smoke_commands(program: str = "qual-bootstrap") -> tuple[tuple[str, ...], ...]:
    return command_cli_smoke_commands(program=program, flow_steps=command_demo_flow_steps())


def command_mvp_cli_smoke_commands(program: str = "qual-bootstrap") -> tuple[tuple[str, ...], ...]:
    return command_demo_cli_smoke_commands(program=program)


def command_demo_cli_smoke_command_entries(
    program: str = "qual-bootstrap",
) -> tuple[CommandCliSmokeCommand, ...]:
    return command_cli_smoke_command_entries(program=program, flow_steps=command_demo_flow_steps())


def command_mvp_cli_smoke_command_entries(
    program: str = "qual-bootstrap",
) -> tuple[CommandCliSmokeCommand, ...]:
    return command_demo_cli_smoke_command_entries(program=program)


def command_demo_cli_smoke_plan() -> CommandCliSmokePlan:
    return command_cli_smoke_plan(flow_steps=command_demo_flow_steps())


def command_mvp_cli_smoke_plan() -> CommandCliSmokePlan:
    return command_demo_cli_smoke_plan()


def command_mvp_demo_path_steps() -> tuple[CommandDemoPathStep, ...]:
    return command_demo_path_steps(flow_steps=command_mvp_flow_steps())


def command_mvp_demo_path_argv() -> tuple[tuple[str, ...], ...]:
    return command_demo_path_argv(flow_steps=command_mvp_flow_steps())


def command_mvp_demo_path_commands(program: str = "qual-bootstrap") -> tuple[tuple[str, ...], ...]:
    return command_demo_path_commands(program=program, flow_steps=command_mvp_flow_steps())


def command_mvp_demo_path_command_entries(program: str = "qual-bootstrap") -> tuple[CommandDemoPathCommand, ...]:
    return command_demo_path_command_entries(program=program, flow_steps=command_mvp_flow_steps())


def command_mvp_demo_path_contract(program: str = "qual-bootstrap") -> CommandDemoPathContract:
    return command_demo_path_contract(program=program, flow_steps=command_mvp_flow_steps())


def command_mvp_demo_path_command_lookup_table(
    program: str = "qual-bootstrap",
) -> tuple[tuple[tuple[str, ...], str], ...]:
    return command_demo_path_command_lookup_table(program=program, flow_steps=command_mvp_flow_steps())


def command_mvp_demo_path_readiness(program: str = "qual-bootstrap") -> CommandDemoPathReadiness:
    return command_demo_path_readiness(program=program, flow_steps=command_mvp_flow_steps())


def command_mvp_demo_path_readiness_steps(
    program: str = "qual-bootstrap",
) -> tuple[CommandDemoPathReadinessStep, ...]:
    return command_mvp_demo_path_readiness(program=program).steps


@lru_cache(maxsize=None)
def command_flow_route_contract(
    flow_steps: tuple[str, ...] | None = None,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandFlowRouteContract:
    return CommandFlowRouteContract(entries=command_flow_route_catalog(flow_steps, specs))


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
    if tuple((entry.flow_step, entry.name) for entry in contract.route_catalog) != contract.lookup_table:
        raise ValueError("Command surface route table is inconsistent")
    if tuple(entry.lookup_tokens for entry in contract.route_catalog) != contract.lookup_tokens:
        raise ValueError("Command surface route lookup tokens are inconsistent")
    if tuple(entry.surface_tokens for entry in contract.route_catalog) != contract.flow_surface_tokens:
        raise ValueError("Command surface route surface tokens are inconsistent")
    if contract.lookup_surface != contract.lookup_index:
        raise ValueError("Command surface lookup surfaces must match")
    route_demo_steps = tuple(entry.demo_step for entry in contract.route_catalog)
    if any(route_demo_steps):
        if not contract.demo_path_steps:
            raise ValueError("Command surface demo path steps are missing")
        if tuple(step.demo_step for step in contract.demo_path_steps) != route_demo_steps:
            raise ValueError("Command surface demo path labels are inconsistent")
    if contract.demo_path_steps:
        if tuple(step.flow_step for step in contract.demo_path_steps) != contract.flow_steps:
            raise ValueError("Command surface demo path steps are inconsistent")
        if tuple(step.name for step in contract.demo_path_steps) != contract.names:
            raise ValueError("Command surface demo path names are inconsistent")
        route_cli_tokens = tuple(entry.cli_tokens[0] for entry in contract.route_catalog)
        if tuple(step.cli_token for step in contract.demo_path_steps) != route_cli_tokens:
            raise ValueError("Command surface demo path CLI tokens are inconsistent")
        demo_argv_tokens = tuple(step.argv[0] if step.argv else "" for step in contract.demo_path_steps)
        if demo_argv_tokens != route_cli_tokens:
            raise ValueError("Command surface demo path argv tokens are inconsistent")
        if tuple(step.description for step in contract.demo_path_steps) != tuple(
            entry.description for entry in contract.route_catalog
        ):
            raise ValueError("Command surface demo path descriptions are inconsistent")


@lru_cache(maxsize=None)
def command_flow_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandSurfaceContract:
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    sequence = command_flow_sequence(specs, ordered_flow_steps)
    route_catalog = command_flow_route_catalog(flow_steps=ordered_flow_steps, specs=specs)
    route_summary = command_flow_route_summary(specs, ordered_flow_steps)
    smoke_steps = command_cli_smoke_steps(specs, ordered_flow_steps)
    contract = CommandSurfaceContract(
        flow_steps=sequence.flow_steps,
        names=sequence.names,
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
        demo_path_steps=_command_demo_path_steps_for_smoke_steps(smoke_steps),
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
