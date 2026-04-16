from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class CommandSpec:
    name: str
    aliases: tuple[str, ...] = ()
    cli_tokens: tuple[str, ...] = ()
    cli_exposed: bool = True
    smoke_argv: tuple[str, ...] = ()
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
class CommandSmokeEntry:
    flow_step: str
    name: str
    primary_cli_token: str
    cli_tokens: tuple[str, ...]
    lookup_tokens: tuple[str, ...]
    surface_tokens: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class CommandSmokeContract:
    flow_steps: tuple[str, ...]
    names: tuple[str, ...]
    entries: tuple[CommandSmokeEntry, ...]
    primary_cli_tokens: tuple[str, ...]
    invocation_plan: tuple[CommandInvocationPlanEntry, ...]
    route_summary: tuple[tuple[str, str, tuple[str, ...]], ...]
    lookup_surface: tuple[tuple[str, str], ...]


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
    route_tokens: tuple[str, ...] = ()
    invocation_plan: tuple[CommandInvocationPlanEntry, ...] = ()
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
    lookup_table: tuple[tuple[str, str], ...]
    route_lookup_table: tuple[tuple[str, str], ...]
    route_flow_lookup_table: tuple[tuple[str, str], ...]
    flow_steps: tuple[str, ...]
    flow_names: tuple[str, ...]
    route_summary: tuple[tuple[str, str, tuple[str, ...]], ...]
    lookup_surface: tuple[tuple[str, str], ...] = ()
    flow_surface_tokens: tuple[tuple[str, ...], ...] = ()
    route_tokens: tuple[str, ...] = ()
    invocation_plan: tuple[CommandInvocationPlanEntry, ...] = ()
    route_catalog: tuple[CommandFlowRouteEntry, ...] = ()


@dataclass(frozen=True)
class CommandCliFlowEntry:
    token: str
    canonical_name: str
    flow_step: str


@dataclass(frozen=True)
class CommandCliSurfaceEntry:
    token: str
    canonical_name: str
    flow_step: str
    aliases: tuple[str, ...]
    lookup_tokens: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class CommandCliFlowContract:
    entries: tuple[CommandCliFlowEntry, ...]


@dataclass(frozen=True)
class CommandCliSurfaceContract:
    entries: tuple[CommandCliSurfaceEntry, ...]


@dataclass(frozen=True)
class CommandCliShimEntry:
    token: str
    canonical_name: str
    flow_step: str
    primary_cli_token: str
    argv: tuple[str, ...]
    kind: str


@dataclass(frozen=True)
class CommandCliShimContract:
    entries: tuple[CommandCliShimEntry, ...]
    lookup_table: tuple[tuple[str, str], ...]
    invocation_table: tuple[tuple[str, tuple[str, ...]], ...]


@dataclass(frozen=True)
class CommandInvocationPlanEntry:
    flow_step: str
    name: str
    argv: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class CommandFlowRouteEntry:
    flow_step: str
    name: str
    cli_tokens: tuple[str, ...]
    primary_cli_token: str
    lookup_tokens: tuple[str, ...]
    surface_tokens: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class CommandFlowRouteContract:
    entries: tuple[CommandFlowRouteEntry, ...]


@dataclass(frozen=True)
class CommandInvocationPlanContract:
    entries: tuple[CommandInvocationPlanEntry, ...]


@dataclass(frozen=True)
class CommandSmokeInvocationContract:
    entries: tuple[CommandInvocationPlanEntry, ...]


@dataclass(frozen=True)
class ResolvedCommand:
    token: str
    normalized_token: str
    canonical_name: str
    flow_step: str
    primary_cli_token: str
    argv: tuple[str, ...]
    cli_tokens: tuple[str, ...]
    lookup_tokens: tuple[str, ...]
    surface_tokens: tuple[str, ...]
    description: str
    kind: str
    matched: bool


def _normalize_token(value: str) -> str:
    normalized = re.sub(r"[-_\s]+", "-", value.strip().casefold())
    return normalized.strip("-")


def _lookup_aliases(spec: CommandSpec) -> tuple[str, ...]:
    # Keep the surface stable if a spec repeats the command name verbatim.
    return tuple(alias for alias in spec.aliases if alias != spec.name)


def _lookup_tokens(spec: CommandSpec) -> tuple[str, ...]:
    return (spec.name, *_lookup_aliases(spec))


def _lookup_resolution_tokens(spec: CommandSpec) -> tuple[str, ...]:
    return (*_lookup_tokens(spec), *spec.cli_tokens)


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


def _validated_cli_entrypoints_for(
    specs: tuple[CommandSpec, ...],
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    validate_command_catalog(specs)
    require_lookup_resolution = specs is COMMAND_SPECS
    seen_entrypoints: set[str] = set()
    validated_entrypoints: list[tuple[str, tuple[str, ...]]] = []
    for spec in specs:
        if not spec.cli_exposed:
            continue
        entrypoints = spec.cli_tokens or _lookup_tokens(spec)
        if not entrypoints:
            raise ValueError(f"Command {spec.name} must define at least one CLI entrypoint")
        normalized_entrypoints: list[str] = []
        for entrypoint in entrypoints:
            normalized_entrypoint = _normalize_token(entrypoint)
            if not normalized_entrypoint:
                raise ValueError("Command CLI entrypoints must not be empty")
            if normalized_entrypoint in seen_entrypoints:
                raise ValueError(f"Duplicate command CLI entrypoint: {entrypoint}")
            seen_entrypoints.add(normalized_entrypoint)
            if require_lookup_resolution:
                resolved = command_spec_for(specs, entrypoint)
                if resolved is None:
                    raise ValueError(f"Unknown CLI command entrypoint: {entrypoint}")
                if resolved.name != spec.name:
                    raise ValueError(
                        "Command CLI entrypoint resolves to the wrong command: "
                        f"{entrypoint} -> {resolved.name}"
                    )
            normalized_entrypoints.append(normalized_entrypoint)
        validated_entrypoints.append((spec.name, tuple(normalized_entrypoints)))
    return tuple(validated_entrypoints)

def _cli_entrypoints_by_name(
    specs: tuple[CommandSpec, ...],
) -> dict[str, tuple[str, ...]]:
    return {name: entrypoints for name, entrypoints in _validated_cli_entrypoints_for(specs)}


def _command_cli_tokens_by_name() -> dict[str, tuple[str, ...]]:
    return _cli_entrypoints_by_name(COMMAND_SPECS)


def _declared_cli_entrypoints_for(spec: CommandSpec) -> tuple[str, ...]:
    if not spec.cli_exposed:
        return ()
    entrypoints = spec.cli_tokens or _lookup_tokens(spec)
    return tuple(_normalize_token(entrypoint) for entrypoint in entrypoints)


def _validate_command_cli_contract(
    contract: CommandCliContract,
    specs: tuple[CommandSpec, ...],
    *,
    validated_entrypoints: tuple[tuple[str, tuple[str, ...]], ...] | None = None,
) -> None:
    validate_command_catalog(specs)
    expected_canonical_names = tuple(name for name, _ in validated_entrypoints or ())
    if contract.canonical_names != expected_canonical_names:
        raise ValueError("Command CLI canonical names are inconsistent")

    expected_parser_surface = tuple(
        (spec.name, _declared_cli_entrypoints_for(spec))
        for spec in specs
        if spec.cli_exposed
    )
    if validated_entrypoints is not None and validated_entrypoints != expected_parser_surface:
        raise ValueError("Command CLI parser surface is inconsistent")

    expected_tokens = tuple(
        normalized_entrypoint
        for spec in specs
        for normalized_entrypoint in _declared_cli_entrypoints_for(spec)
    )
    if contract.tokens != expected_tokens:
        raise ValueError("Command CLI tokens are inconsistent")

    expected_lookup_table = tuple(
        (normalized_entrypoint, spec.name)
        for spec in specs
        for normalized_entrypoint in _declared_cli_entrypoints_for(spec)
    )
    if contract.lookup_table != expected_lookup_table:
        raise ValueError("Command CLI lookup table is inconsistent")


def _command_cli_contract_for(specs: tuple[CommandSpec, ...]) -> CommandCliContract:
    validated_entrypoints = _validated_cli_entrypoints_for(specs)
    tokens: list[str] = []
    lookup_table: list[tuple[str, str]] = []
    seen_canonical_names: set[str] = set()
    canonical_names: list[str] = []
    for spec_name, entrypoints in validated_entrypoints:
        for normalized_entrypoint in entrypoints:
            tokens.append(normalized_entrypoint)
            lookup_table.append((normalized_entrypoint, spec_name))
        if spec_name in seen_canonical_names:
            continue
        seen_canonical_names.add(spec_name)
        canonical_names.append(spec_name)

    contract = CommandCliContract(
        tokens=tuple(tokens),
        canonical_names=tuple(canonical_names),
        lookup_table=tuple(lookup_table),
    )
    _validate_command_cli_contract(
        contract,
        specs,
        validated_entrypoints=validated_entrypoints,
    )
    return contract


def _route_cli_tokens_by_name(specs: tuple[CommandSpec, ...]) -> dict[str, tuple[str, ...]]:
    # Keep the real parser surface for the default catalog, but fall back to the
    # supplied spec lookup tokens when callers build custom smoke surfaces.
    if specs == COMMAND_SPECS:
        return _command_cli_tokens_by_name()
    route_tokens_by_name: dict[str, tuple[str, ...]] = {}
    for spec in specs:
        if spec.cli_tokens:
            route_tokens_by_name[spec.name] = _flow_surface_tokens(*spec.cli_tokens)
            continue
        route_tokens_by_name[spec.name] = _flow_surface_tokens(*_lookup_tokens(spec))
    return route_tokens_by_name


def _primary_route_cli_token(cli_tokens: tuple[str, ...], *, name: str) -> str:
    if not cli_tokens:
        raise ValueError(f"Command {name} must define at least one CLI entrypoint")
    return cli_tokens[0]


def _default_smoke_argv(spec: CommandSpec) -> tuple[str, ...]:
    entrypoints = _declared_cli_entrypoints_for(spec)
    if not entrypoints:
        raise ValueError(f"Command {spec.name} must define at least one CLI entrypoint")
    return (entrypoints[0],)


def _smoke_argv_for_spec(spec: CommandSpec) -> tuple[str, ...]:
    if not spec.smoke_argv:
        return _default_smoke_argv(spec)

    normalized_argv = tuple(_normalize_token(token) for token in spec.smoke_argv)
    if any(not token for token in normalized_argv):
        raise ValueError(f"Command {spec.name} has an empty smoke argv token")

    primary_cli_token = _default_smoke_argv(spec)[0]
    if normalized_argv[0] != primary_cli_token:
        raise ValueError(
            "Command smoke argv must start with the primary CLI entrypoint: "
            f"{spec.name} -> {spec.smoke_argv[0]}"
        )
    return normalized_argv


COMMAND_SPECS: tuple[CommandSpec, ...] = (
    CommandSpec(
        name="bootstrap",
        aliases=("open", "project-open", "project", "bootstrap-run"),
        cli_tokens=("bootstrap",),
        description="Run the project bootstrap flow.",
        flow_step="project-open",
    ),
    CommandSpec(
        name="diff-preview",
        aliases=("diff", "diff_preview", "review-patch"),
        cli_tokens=("diff-preview", "diff"),
        description="Preview unified diff output.",
        flow_step="patch-review",
    ),
    CommandSpec(
        name="context-basket",
        aliases=("context", "basket", "retrieval", "retrieve"),
        cli_tokens=("context-basket",),
        smoke_argv=("context-basket", "list"),
        description="Manage retrieval context basket items.",
        flow_step="retrieval",
    ),
    CommandSpec(
        name="terminal",
        aliases=("export", "save-export"),
        cli_tokens=("terminal",),
        description="Run terminal export handoff routing.",
        flow_step="export-handoff",
    ),
)
DEMO_COMMAND_FLOW_STEPS: tuple[str, ...] = (
    "project-open",
    "retrieval",
    "patch-review",
    "export-handoff",
)
MVP_COMMAND_FLOW_STEPS: tuple[str, ...] = DEMO_COMMAND_FLOW_STEPS


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

        seen_local_cli_tokens: set[str] = set()
        for cli_token in spec.cli_tokens:
            normalized_cli_token = _normalize_token(cli_token)
            if not normalized_cli_token:
                raise ValueError(f"Command {spec.name} has an empty CLI entrypoint")
            if normalized_cli_token in seen_local_cli_tokens:
                raise ValueError(f"Duplicate command CLI entrypoint: {cli_token}")
            seen_local_cli_tokens.add(normalized_cli_token)
            if normalized_cli_token in seen_lookup_tokens and seen_lookup_tokens[normalized_cli_token] != spec.name:
                raise ValueError(f"Duplicate command lookup token: {cli_token}")
            seen_lookup_tokens[normalized_cli_token] = spec.name

        if not spec.cli_exposed:
            if spec.cli_tokens:
                raise ValueError(f"Command {spec.name} must not declare CLI entrypoints when cli_exposed is false")
            if spec.smoke_argv:
                raise ValueError(f"Command {spec.name} must not declare smoke argv when cli_exposed is false")
            continue

        _smoke_argv_for_spec(spec)


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
def command_resolution_tokens_for(specs: tuple[CommandSpec, ...], name: str) -> tuple[str, ...]:
    spec = command_spec_for(specs, name)
    if spec is None:
        return ()
    return _lookup_resolution_tokens(spec)


@lru_cache(maxsize=None)
def command_cli_tokens_for(specs: tuple[CommandSpec, ...], name: str) -> tuple[str, ...]:
    spec = command_spec_for(specs, name)
    if spec is None:
        return ()
    return _cli_entrypoints_by_name(specs).get(spec.name, ())


@lru_cache(maxsize=None)
def command_primary_cli_token_for(specs: tuple[CommandSpec, ...], name: str) -> str:
    cli_tokens = command_cli_tokens_for(specs, name)
    if not cli_tokens:
        return ""
    return cli_tokens[0]


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
        for alias in _lookup_resolution_tokens(spec):
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
    route_tokens_by_name = _route_cli_tokens_by_name(specs)
    return tuple(
        CommandFlowSurfaceEntry(
            flow_step=flow_step,
            name=entry.name,
            aliases=entry.aliases,
            description=entry.description,
            lookup_tokens=entry.lookup_tokens,
            surface_tokens=_flow_surface_tokens(
                *route_tokens_by_name.get(entry.name, (entry.name,)),
                *entry.lookup_tokens,
                flow_step,
            ),
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


def command_resolution_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_resolution_lookup_index(specs)


@lru_cache(maxsize=None)
def command_cli_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return _command_cli_contract_for(specs).tokens


@lru_cache(maxsize=None)
def command_cli_primary_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return tuple(
        command_primary_cli_token_for(specs, name)
        for name in command_cli_contract(specs).canonical_names
    )


@lru_cache(maxsize=None)
def command_cli_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return _command_cli_contract_for(specs).lookup_table


@lru_cache(maxsize=None)
def command_cli_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandCliContract:
    return _command_cli_contract_for(specs)


@lru_cache(maxsize=None)
def command_cli_route_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandFlowRouteEntry, ...]:
    return command_flow_route_catalog(flow_steps=flow_steps, specs=specs)


@lru_cache(maxsize=None)
def command_cli_route_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, str], ...]:
    route_catalog = command_cli_route_catalog(specs, flow_steps)
    return tuple(
        (cli_token, entry.name)
        for entry in route_catalog
        for cli_token in entry.cli_tokens
    )


@lru_cache(maxsize=None)
def command_cli_route_flow_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, str], ...]:
    route_catalog = command_cli_route_catalog(specs, flow_steps)
    return tuple(
        (cli_token, entry.flow_step)
        for entry in route_catalog
        for cli_token in entry.cli_tokens
    )


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
    cli_contract = _command_cli_contract_for(specs)
    if contract.tokens != cli_contract.tokens:
        raise ValueError("Command CLI route tokens are inconsistent")
    if contract.canonical_names != cli_contract.canonical_names:
        raise ValueError("Command CLI route canonical names are inconsistent")
    if contract.lookup_table != cli_contract.lookup_table:
        raise ValueError("Command CLI route lookup table is inconsistent")
    if contract.route_lookup_table != command_cli_route_lookup_table(specs, flow_steps):
        raise ValueError("Command CLI route canonical lookup surface is inconsistent")
    if contract.route_flow_lookup_table != command_cli_route_flow_lookup_table(specs, flow_steps):
        raise ValueError("Command CLI route flow lookup surface is inconsistent")
    if contract.lookup_surface != command_flow_lookup_surface(specs, flow_steps):
        raise ValueError("Command CLI route lookup surface is inconsistent")
    if contract.flow_surface_tokens != command_flow_surface_tokens(specs, flow_steps):
        raise ValueError("Command CLI route surface tokens are inconsistent")
    if tuple(entry.primary_cli_token for entry in contract.route_catalog) != contract.route_tokens:
        raise ValueError("Command CLI route catalog invocation tokens are inconsistent")
    if contract.route_tokens != command_flow_route_tokens(specs, flow_steps):
        raise ValueError("Command CLI route invocation tokens are inconsistent")
    if contract.invocation_plan != command_flow_invocation_plan(specs, flow_steps):
        raise ValueError("Command CLI route invocation plan is inconsistent")


@lru_cache(maxsize=None)
def command_cli_route_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandCliRouteContract:
    cli_contract = _command_cli_contract_for(specs)
    route_summary = command_flow_route_summary(specs, flow_steps)
    ordered_flow_steps = tuple(flow_step for flow_step, _, _ in route_summary)
    route_catalog = command_cli_route_catalog(specs, ordered_flow_steps)
    contract = CommandCliRouteContract(
        tokens=cli_contract.tokens,
        canonical_names=cli_contract.canonical_names,
        lookup_table=cli_contract.lookup_table,
        route_lookup_table=command_cli_route_lookup_table(specs, ordered_flow_steps),
        route_flow_lookup_table=command_cli_route_flow_lookup_table(specs, ordered_flow_steps),
        flow_steps=ordered_flow_steps,
        flow_names=tuple(name for _, name, _ in route_summary),
        route_summary=route_summary,
        lookup_surface=command_flow_lookup_surface(specs, ordered_flow_steps),
        flow_surface_tokens=command_flow_surface_tokens(specs, ordered_flow_steps),
        route_tokens=command_flow_route_tokens(specs, ordered_flow_steps),
        invocation_plan=command_flow_invocation_plan(specs, ordered_flow_steps),
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
def command_cli_flow_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandCliFlowContract:
    cli_contract = _command_cli_contract_for(specs)
    entries: list[CommandCliFlowEntry] = []
    for token, canonical_name in cli_contract.lookup_table:
        spec = command_spec_for(specs, canonical_name)
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
def command_cli_flow_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return tuple((entry.token, entry.flow_step) for entry in command_cli_flow_contract(specs).entries)


@lru_cache(maxsize=None)
def command_cli_surface_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandCliSurfaceEntry, ...]:
    cli_contract = _command_cli_contract_for(specs)
    entries: list[CommandCliSurfaceEntry] = []
    for token, canonical_name in cli_contract.lookup_table:
        spec = command_spec_for(specs, canonical_name)
        if spec is None:
            raise ValueError(f"Unknown CLI command target: {canonical_name}")
        entries.append(
            CommandCliSurfaceEntry(
                token=token,
                canonical_name=spec.name,
                flow_step=_normalize_token(spec.flow_step),
                aliases=_lookup_aliases(spec),
                lookup_tokens=_flow_surface_tokens(*_lookup_resolution_tokens(spec)),
                description=spec.description,
            )
        )
    return tuple(entries)


@lru_cache(maxsize=None)
def command_cli_surface_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandCliSurfaceContract:
    return CommandCliSurfaceContract(entries=command_cli_surface_catalog(specs))


def _surface_token_kind(token: str, route_entry: CommandFlowRouteEntry) -> str:
    raw_token = token.strip().casefold()
    if raw_token == route_entry.primary_cli_token.casefold():
        return "primary"
    if any(raw_token == cli_token.casefold() for cli_token in route_entry.cli_tokens):
        return "cli"
    if raw_token == route_entry.flow_step.casefold():
        return "flow-step"
    if any(raw_token == lookup_token.casefold() for lookup_token in route_entry.lookup_tokens):
        return "lookup"

    normalized_token = _normalize_token(token)
    if normalized_token == route_entry.primary_cli_token:
        return "primary"
    if normalized_token in route_entry.cli_tokens:
        return "cli"
    if normalized_token == route_entry.flow_step:
        return "flow-step"
    return "lookup"


@lru_cache(maxsize=None)
def command_cli_shim_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandCliShimEntry, ...]:
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    route_catalog = command_flow_route_catalog(flow_steps=ordered_flow_steps, specs=specs)
    entries: list[CommandCliShimEntry] = []
    for route_entry in route_catalog:
        argv = (route_entry.primary_cli_token,)
        for token in route_entry.surface_tokens:
            entries.append(
                CommandCliShimEntry(
                    token=token,
                    canonical_name=route_entry.name,
                    flow_step=route_entry.flow_step,
                    primary_cli_token=route_entry.primary_cli_token,
                    argv=argv,
                    kind=_surface_token_kind(token, route_entry),
                )
            )
    return tuple(entries)


@lru_cache(maxsize=None)
def command_cli_shim_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (entry.token, entry.primary_cli_token)
        for entry in command_cli_shim_catalog(specs, flow_steps)
    )


@lru_cache(maxsize=None)
def command_cli_shim_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return tuple(
        (entry.token, entry.argv)
        for entry in command_cli_shim_catalog(specs, flow_steps)
    )


@lru_cache(maxsize=None)
def command_cli_shim_primary_token_for(
    specs: tuple[CommandSpec, ...],
    token: str,
    flow_steps: tuple[str, ...] | None = None,
) -> str:
    normalized_token = _normalize_token(token)
    if not normalized_token:
        return ""
    shim_lookup = dict(command_cli_shim_lookup_table(specs, flow_steps))
    return shim_lookup.get(normalized_token, "")


def command_cli_shim_argv_for(
    specs: tuple[CommandSpec, ...],
    argv: tuple[str, ...] | list[str],
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    raw_argv = tuple(argv)
    if not raw_argv:
        return ()
    if raw_argv[0].lstrip().startswith("-"):
        return raw_argv
    primary_token = command_cli_shim_primary_token_for(specs, raw_argv[0], flow_steps)
    if not primary_token:
        return raw_argv
    return (primary_token, *raw_argv[1:])


def command_cli_entry_argv_for(
    specs: tuple[CommandSpec, ...],
    argv: tuple[str, ...] | list[str],
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    """Normalize argv to a parser-ready command entrypoint for CLI-first flows."""
    raw_argv = tuple(argv)
    route_tokens = command_flow_route_tokens(specs, flow_steps)
    default_token = route_tokens[0] if route_tokens else ""
    if not raw_argv:
        return (default_token,) if default_token else ()
    if raw_argv[0].lstrip().startswith("-"):
        return (default_token, *raw_argv) if default_token else raw_argv
    return command_cli_shim_argv_for(specs, raw_argv, flow_steps)


@lru_cache(maxsize=None)
def command_cli_shim_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandCliShimContract:
    return CommandCliShimContract(
        entries=command_cli_shim_catalog(specs, flow_steps),
        lookup_table=command_cli_shim_lookup_table(specs, flow_steps),
        invocation_table=command_cli_shim_invocation_table(specs, flow_steps),
    )


@lru_cache(maxsize=None)
def command_cli_surface_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    seen_tokens: set[str] = set()
    lookup_table: list[tuple[str, str]] = []
    for entry in command_cli_surface_catalog(specs):
        for token in entry.lookup_tokens:
            normalized_token = _normalize_token(token)
            if normalized_token in seen_tokens:
                continue
            seen_tokens.add(normalized_token)
            lookup_table.append((normalized_token, entry.canonical_name))
    return tuple(lookup_table)


@lru_cache(maxsize=None)
def command_cli_surface_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return tuple(token for token, _ in command_cli_surface_lookup_table(specs))


@lru_cache(maxsize=None)
def command_cli_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    return command_flow_route_summary(specs, flow_steps)


@lru_cache(maxsize=None)
def command_cli_route_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    return command_flow_route_tokens(specs, flow_steps)


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
            primary_cli_token=_primary_route_cli_token(
                cli_tokens_by_name.get(entry.name, (entry.name,)),
                name=entry.name,
            ),
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
def command_flow_route_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    route_catalog = command_flow_route_catalog(flow_steps=flow_steps, specs=specs)
    return tuple(entry.primary_cli_token for entry in route_catalog)


@lru_cache(maxsize=None)
def command_flow_route_contract(
    flow_steps: tuple[str, ...] | None = None,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandFlowRouteContract:
    return CommandFlowRouteContract(entries=command_flow_route_catalog(flow_steps, specs))


@lru_cache(maxsize=None)
def command_flow_invocation_plan(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandInvocationPlanEntry, ...]:
    route_catalog = command_flow_route_catalog(flow_steps=flow_steps, specs=specs)
    return tuple(
        CommandInvocationPlanEntry(
            flow_step=entry.flow_step,
            name=entry.name,
            argv=(entry.primary_cli_token,),
            description=entry.description,
        )
        for entry in route_catalog
    )


@lru_cache(maxsize=None)
def command_flow_invocation_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandInvocationPlanContract:
    return CommandInvocationPlanContract(entries=command_flow_invocation_plan(specs, flow_steps))


@lru_cache(maxsize=None)
def command_smoke_entry_argv_for(
    specs: tuple[CommandSpec, ...],
    name: str,
) -> tuple[str, ...]:
    spec = command_spec_for(specs, name)
    if spec is None:
        return ()
    return _smoke_argv_for_spec(spec)


def command_smoke_entry_argv(name: str) -> tuple[str, ...]:
    return command_smoke_entry_argv_for(COMMAND_SPECS, name)


@lru_cache(maxsize=None)
def command_smoke_invocation_plan(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandInvocationPlanEntry, ...]:
    route_catalog = command_flow_route_catalog(flow_steps=flow_steps, specs=specs)
    return tuple(
        CommandInvocationPlanEntry(
            flow_step=entry.flow_step,
            name=entry.name,
            argv=command_smoke_entry_argv_for(specs, entry.name),
            description=entry.description,
        )
        for entry in route_catalog
    )


@lru_cache(maxsize=None)
def command_smoke_invocation_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandSmokeInvocationContract:
    return CommandSmokeInvocationContract(entries=command_smoke_invocation_plan(specs, flow_steps))


def command_demo_smoke_invocation_plan(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandInvocationPlanEntry, ...]:
    return command_smoke_invocation_plan(specs, command_demo_flow_steps())


def command_demo_smoke_invocation_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandSmokeInvocationContract:
    return command_smoke_invocation_contract(specs, command_demo_flow_steps())


def command_mvp_smoke_invocation_plan(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandInvocationPlanEntry, ...]:
    return command_demo_smoke_invocation_plan(specs)


def command_mvp_smoke_invocation_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandSmokeInvocationContract:
    return command_demo_smoke_invocation_contract(specs)


def command_demo_flow_route_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandFlowRouteEntry, ...]:
    return command_flow_route_catalog(flow_steps=command_demo_flow_steps(), specs=specs)


def command_demo_flow_route_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandFlowRouteContract:
    return command_flow_route_contract(flow_steps=command_demo_flow_steps(), specs=specs)


def command_demo_flow_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    return command_flow_route_summary(specs, command_demo_flow_steps())


def command_demo_flow_route_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return command_flow_route_tokens(specs, command_demo_flow_steps())


def command_demo_flow_invocation_plan(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandInvocationPlanEntry, ...]:
    return command_flow_invocation_plan(specs, command_demo_flow_steps())


def command_demo_flow_invocation_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandInvocationPlanContract:
    return command_flow_invocation_contract(specs, command_demo_flow_steps())


def command_mvp_flow_route_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandFlowRouteEntry, ...]:
    return command_demo_flow_route_catalog(specs)


def command_mvp_flow_route_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandFlowRouteContract:
    return command_demo_flow_route_contract(specs)


def command_mvp_flow_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    return command_demo_flow_route_summary(specs)


def command_mvp_flow_route_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return command_demo_flow_route_tokens(specs)


def command_mvp_flow_invocation_plan(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandInvocationPlanEntry, ...]:
    return command_demo_flow_invocation_plan(specs)


def command_mvp_flow_invocation_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandInvocationPlanContract:
    return command_demo_flow_invocation_contract(specs)


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
def command_resolution_lookup_index(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    validate_command_catalog(specs)
    seen_tokens: set[str] = set()
    index: list[tuple[str, str]] = []
    for spec in specs:
        for token in _lookup_resolution_tokens(spec):
            normalized_token = _normalize_token(token)
            if normalized_token in seen_tokens:
                continue
            seen_tokens.add(normalized_token)
            index.append((normalized_token, spec.name))
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


def command_mvp_cli_flow_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandCliFlowContract:
    return command_cli_flow_contract(specs)


def command_demo_cli_flow_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandCliFlowContract:
    return command_cli_flow_contract(specs)


def command_demo_cli_surface_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandCliSurfaceEntry, ...]:
    return command_cli_surface_catalog(specs)


def command_demo_cli_surface_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandCliSurfaceContract:
    return command_cli_surface_contract(specs)


def command_demo_cli_shim_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandCliShimEntry, ...]:
    ordered_flow_steps = command_demo_flow_steps() if flow_steps is None else flow_steps
    return command_cli_shim_catalog(specs, ordered_flow_steps)


def command_demo_cli_shim_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, str], ...]:
    ordered_flow_steps = command_demo_flow_steps() if flow_steps is None else flow_steps
    return command_cli_shim_lookup_table(specs, ordered_flow_steps)


def command_demo_cli_shim_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    ordered_flow_steps = command_demo_flow_steps() if flow_steps is None else flow_steps
    return command_cli_shim_invocation_table(specs, ordered_flow_steps)


def command_demo_cli_shim_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandCliShimContract:
    ordered_flow_steps = command_demo_flow_steps() if flow_steps is None else flow_steps
    return command_cli_shim_contract(specs, ordered_flow_steps)


def command_demo_cli_route_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandFlowRouteEntry, ...]:
    ordered_flow_steps = command_demo_flow_steps() if flow_steps is None else flow_steps
    return command_cli_route_catalog(specs, ordered_flow_steps)


def command_demo_cli_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    ordered_flow_steps = command_demo_flow_steps() if flow_steps is None else flow_steps
    return command_cli_route_summary(specs, ordered_flow_steps)


def command_demo_cli_route_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    ordered_flow_steps = command_demo_flow_steps() if flow_steps is None else flow_steps
    return command_cli_route_tokens(specs, ordered_flow_steps)


def command_demo_cli_route_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandCliRouteContract:
    ordered_flow_steps = command_demo_flow_steps() if flow_steps is None else flow_steps
    return command_cli_route_contract(specs, ordered_flow_steps)


def command_mvp_cli_route_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandCliRouteContract:
    return command_demo_cli_route_contract(specs, flow_steps)


def command_mvp_cli_surface_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandCliSurfaceEntry, ...]:
    return command_demo_cli_surface_catalog(specs)


def command_mvp_cli_surface_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandCliSurfaceContract:
    return command_demo_cli_surface_contract(specs)


def command_mvp_cli_shim_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandCliShimEntry, ...]:
    return command_demo_cli_shim_catalog(specs, flow_steps)


def command_mvp_cli_shim_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, str], ...]:
    return command_demo_cli_shim_lookup_table(specs, flow_steps)


def command_mvp_cli_shim_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_cli_shim_invocation_table(specs, flow_steps)


def command_mvp_cli_shim_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandCliShimContract:
    return command_demo_cli_shim_contract(specs, flow_steps)


def command_mvp_cli_route_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[CommandFlowRouteEntry, ...]:
    return command_demo_cli_route_catalog(specs, flow_steps)


def command_mvp_cli_route_summary(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    return command_demo_cli_route_summary(specs, flow_steps)


def command_mvp_cli_route_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    return command_demo_cli_route_tokens(specs, flow_steps)


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
    if tuple(entry.primary_cli_token for entry in contract.route_catalog) != contract.route_tokens:
        raise ValueError("Command surface route invocation tokens are inconsistent")
    if tuple(entry.argv for entry in contract.invocation_plan) != tuple((token,) for token in contract.route_tokens):
        raise ValueError("Command surface invocation argv is inconsistent")
    if tuple((entry.flow_step, entry.name) for entry in contract.invocation_plan) != contract.lookup_table:
        raise ValueError("Command surface invocation order is inconsistent")
    if contract.lookup_surface != contract.lookup_index:
        raise ValueError("Command surface lookup surfaces must match")


def _validate_command_smoke_contract(contract: CommandSmokeContract) -> None:
    if tuple(entry.flow_step for entry in contract.entries) != contract.flow_steps:
        raise ValueError("Command smoke flow steps are inconsistent")
    if tuple(entry.name for entry in contract.entries) != contract.names:
        raise ValueError("Command smoke names are inconsistent")
    if tuple(entry.primary_cli_token for entry in contract.entries) != contract.primary_cli_tokens:
        raise ValueError("Command smoke primary CLI tokens are inconsistent")
    if tuple((entry.flow_step, entry.name, entry.cli_tokens) for entry in contract.entries) != contract.route_summary:
        raise ValueError("Command smoke route summary is inconsistent")
    if tuple((entry.flow_step, entry.name, entry.argv) for entry in contract.invocation_plan) != tuple(
        (entry.flow_step, entry.name, (entry.primary_cli_token,))
        for entry in contract.entries
    ):
        raise ValueError("Command smoke invocation plan is inconsistent")

    expected_lookup_surface: list[tuple[str, str]] = []
    seen_tokens: set[str] = set()
    for entry in contract.entries:
        for token in entry.surface_tokens:
            normalized_token = _normalize_token(token)
            if normalized_token in seen_tokens:
                continue
            seen_tokens.add(normalized_token)
            expected_lookup_surface.append((normalized_token, entry.name))
    if tuple(expected_lookup_surface) != contract.lookup_surface:
        raise ValueError("Command smoke lookup surface is inconsistent")


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
        manifest=command_flow_manifest(specs, ordered_flow_steps),
        lookup_table=sequence.lookup_table,
        lookup_index=command_flow_surface_lookup_index(specs, ordered_flow_steps),
        lookup_tokens=sequence.lookup_tokens,
        flow_tokens=command_flow_tokens(specs, ordered_flow_steps),
        flow_catalog=command_flow_catalog(specs, ordered_flow_steps),
        lookup_surface=command_flow_lookup_surface(specs, ordered_flow_steps),
        flow_surface_tokens=command_flow_surface_tokens(specs, ordered_flow_steps),
        route_tokens=command_flow_route_tokens(specs, ordered_flow_steps),
        invocation_plan=command_flow_invocation_plan(specs, ordered_flow_steps),
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


@lru_cache(maxsize=None)
def command_smoke_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandSmokeContract:
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    route_catalog = command_flow_route_catalog(flow_steps=ordered_flow_steps, specs=specs)
    entries = tuple(
        CommandSmokeEntry(
            flow_step=entry.flow_step,
            name=entry.name,
            primary_cli_token=entry.primary_cli_token,
            cli_tokens=entry.cli_tokens,
            lookup_tokens=entry.lookup_tokens,
            surface_tokens=entry.surface_tokens,
            description=entry.description,
        )
        for entry in route_catalog
    )
    contract = CommandSmokeContract(
        flow_steps=tuple(entry.flow_step for entry in entries),
        names=tuple(entry.name for entry in entries),
        entries=entries,
        primary_cli_tokens=tuple(entry.primary_cli_token for entry in entries),
        invocation_plan=command_flow_invocation_plan(specs, ordered_flow_steps),
        route_summary=tuple((entry.flow_step, entry.name, entry.cli_tokens) for entry in entries),
        lookup_surface=command_flow_lookup_surface(specs, ordered_flow_steps),
    )
    _validate_command_smoke_contract(contract)
    return contract


def command_demo_smoke_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandSmokeContract:
    return command_smoke_contract(specs, command_demo_flow_steps())


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


def command_mvp_smoke_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandSmokeContract:
    return command_demo_smoke_contract(specs)


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


@lru_cache(maxsize=None)
def command_resolution_tokens(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[str, ...]:
    validate_command_catalog(specs)
    return tuple(token for spec in specs for token in _lookup_resolution_tokens(spec))


def command_lookup_tokens(name: str) -> tuple[str, ...]:
    return command_lookup_tokens_for(COMMAND_SPECS, name)


def command_resolution_lookup_tokens(name: str) -> tuple[str, ...]:
    return command_resolution_tokens_for(COMMAND_SPECS, name)


def command_spec(name: str) -> CommandSpec | None:
    return command_spec_for(COMMAND_SPECS, name)


def command_aliases(name: str) -> tuple[str, ...]:
    return command_aliases_for(COMMAND_SPECS, name)


def canonical_command(name: str) -> str:
    return canonical_command_for(COMMAND_SPECS, name)


def command_cli_shim_primary_token(
    token: str,
    flow_steps: tuple[str, ...] | None = None,
) -> str:
    return command_cli_shim_primary_token_for(COMMAND_SPECS, token, flow_steps)


def command_cli_shim_argv(
    argv: tuple[str, ...] | list[str],
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    return command_cli_shim_argv_for(COMMAND_SPECS, argv, flow_steps)


def command_cli_entry_argv(
    argv: tuple[str, ...] | list[str],
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    return command_cli_entry_argv_for(COMMAND_SPECS, argv, flow_steps)


def command_smoke_argv_for(
    specs: tuple[CommandSpec, ...],
    argv: tuple[str, ...] | list[str],
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    raw_argv = tuple(argv)
    smoke_plan = command_smoke_invocation_plan(specs, flow_steps)
    default_argv = smoke_plan[0].argv if smoke_plan else ()
    if not raw_argv:
        return default_argv
    if raw_argv[0].lstrip().startswith("-"):
        return (*default_argv, *raw_argv) if default_argv else raw_argv

    resolved = command_resolve_for(specs, raw_argv[0], flow_steps)
    if not resolved.matched:
        return raw_argv
    if len(raw_argv) == 1:
        return command_smoke_entry_argv_for(specs, resolved.canonical_name)
    return (resolved.primary_cli_token, *raw_argv[1:])


def command_smoke_argv(
    argv: tuple[str, ...] | list[str],
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    return command_smoke_argv_for(COMMAND_SPECS, argv, flow_steps)


@lru_cache(maxsize=None)
def command_resolve_for(
    specs: tuple[CommandSpec, ...],
    token: str,
    flow_steps: tuple[str, ...] | None = None,
) -> ResolvedCommand:
    normalized_token = _normalize_token(token)
    if not normalized_token:
        return ResolvedCommand(
            token=token,
            normalized_token="",
            canonical_name="",
            flow_step="",
            primary_cli_token="",
            argv=(),
            cli_tokens=(),
            lookup_tokens=(),
            surface_tokens=(),
            description="",
            kind="empty",
            matched=False,
        )

    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    route_catalog = command_flow_route_catalog(flow_steps=ordered_flow_steps, specs=specs)
    for route_entry in route_catalog:
        if normalized_token not in route_entry.surface_tokens:
            continue
        return ResolvedCommand(
            token=token,
            normalized_token=normalized_token,
            canonical_name=route_entry.name,
            flow_step=route_entry.flow_step,
            primary_cli_token=route_entry.primary_cli_token,
            argv=(route_entry.primary_cli_token,),
            cli_tokens=route_entry.cli_tokens,
            lookup_tokens=route_entry.lookup_tokens,
            surface_tokens=route_entry.surface_tokens,
            description=route_entry.description,
            kind=_surface_token_kind(token, route_entry),
            matched=True,
        )

    return ResolvedCommand(
        token=token,
        normalized_token=normalized_token,
        canonical_name=canonical_command_for(specs, normalized_token),
        flow_step="",
        primary_cli_token="",
        argv=(normalized_token,),
        cli_tokens=(),
        lookup_tokens=(),
        surface_tokens=(),
        description="",
        kind="unknown",
        matched=False,
    )


def command_resolve(
    token: str,
    flow_steps: tuple[str, ...] | None = None,
) -> ResolvedCommand:
    return command_resolve_for(COMMAND_SPECS, token, flow_steps)


def command_resolve_argv_for(
    specs: tuple[CommandSpec, ...],
    argv: tuple[str, ...] | list[str],
    flow_steps: tuple[str, ...] | None = None,
) -> ResolvedCommand:
    raw_argv = tuple(argv)
    if not raw_argv:
        return ResolvedCommand(
            token="",
            normalized_token="",
            canonical_name="",
            flow_step="",
            primary_cli_token="",
            argv=(),
            cli_tokens=(),
            lookup_tokens=(),
            surface_tokens=(),
            description="",
            kind="empty",
            matched=False,
        )
    if raw_argv[0].lstrip().startswith("-"):
        token = raw_argv[0]
        return ResolvedCommand(
            token=token,
            normalized_token=_normalize_token(token),
            canonical_name="",
            flow_step="",
            primary_cli_token="",
            argv=raw_argv,
            cli_tokens=(),
            lookup_tokens=(),
            surface_tokens=(),
            description="",
            kind="flag",
            matched=False,
        )

    resolved = command_resolve_for(specs, raw_argv[0], flow_steps)
    if not resolved.matched:
        return ResolvedCommand(
            token=resolved.token,
            normalized_token=resolved.normalized_token,
            canonical_name=resolved.canonical_name,
            flow_step=resolved.flow_step,
            primary_cli_token=resolved.primary_cli_token,
            argv=raw_argv,
            cli_tokens=resolved.cli_tokens,
            lookup_tokens=resolved.lookup_tokens,
            surface_tokens=resolved.surface_tokens,
            description=resolved.description,
            kind=resolved.kind,
            matched=False,
        )

    return ResolvedCommand(
        token=resolved.token,
        normalized_token=resolved.normalized_token,
        canonical_name=resolved.canonical_name,
        flow_step=resolved.flow_step,
        primary_cli_token=resolved.primary_cli_token,
        argv=(resolved.primary_cli_token, *raw_argv[1:]),
        cli_tokens=resolved.cli_tokens,
        lookup_tokens=resolved.lookup_tokens,
        surface_tokens=resolved.surface_tokens,
        description=resolved.description,
        kind=resolved.kind,
        matched=True,
    )


def command_resolve_argv(
    argv: tuple[str, ...] | list[str],
    flow_steps: tuple[str, ...] | None = None,
) -> ResolvedCommand:
    return command_resolve_argv_for(COMMAND_SPECS, argv, flow_steps)
