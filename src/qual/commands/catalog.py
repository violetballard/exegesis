from __future__ import annotations

import re
from dataclasses import dataclass, replace
from functools import lru_cache


@dataclass(frozen=True)
class CommandSpec:
    name: str
    aliases: tuple[str, ...] = ()
    cli_tokens: tuple[str, ...] = ()
    cli_exposed: bool = True
    smoke_argv: tuple[str, ...] = ()
    surface_argv: tuple[str, ...] = ()
    shim_argv: tuple[tuple[str, tuple[str, ...]], ...] = ()
    shim_pinned_options: tuple[tuple[str, tuple[str, ...]], ...] = ()
    preferred_surface_tokens: tuple[str, ...] = ()
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
    smoke_argv: tuple[str, ...] = ()


@dataclass(frozen=True)
class CommandSmokeContract:
    flow_steps: tuple[str, ...]
    names: tuple[str, ...]
    entries: tuple[CommandSmokeEntry, ...]
    primary_cli_tokens: tuple[str, ...]
    invocation_plan: tuple[CommandInvocationPlanEntry, ...]
    route_summary: tuple[tuple[str, str, tuple[str, ...]], ...]
    lookup_surface: tuple[tuple[str, str], ...]
    smoke_invocation_plan: tuple[CommandInvocationPlanEntry, ...] = ()


@dataclass(frozen=True)
class CommandDemoPathEntry:
    flow_step: str
    name: str
    primary_cli_token: str
    smoke_argv: tuple[str, ...]
    description: str
    parser_argv: tuple[str, ...] = ()
    argv: tuple[str, ...] = ()
    lookup_tokens: tuple[str, ...] = ()
    surface_tokens: tuple[str, ...] = ()
    preferred_surface_tokens: tuple[str, ...] = ()
    next_tokens: tuple[str, ...] = ()
    surface_invocations: tuple[tuple[str, tuple[str, ...]], ...] = ()
    preferred_surface_invocations: tuple[tuple[str, tuple[str, ...]], ...] = ()
    parser_surface_invocations: tuple[tuple[str, tuple[str, ...]], ...] = ()


@dataclass(frozen=True)
class CommandDemoPathContract:
    flow_steps: tuple[str, ...]
    names: tuple[str, ...]
    entries: tuple[CommandDemoPathEntry, ...]
    invocation_plan: tuple[CommandInvocationPlanEntry, ...] = ()
    lookup_table: tuple[tuple[str, str], ...] = ()
    lookup_surface: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class CommandDemoLoopEntry:
    token: str
    canonical_name: str
    flow_step: str
    argv: tuple[str, ...]
    description: str
    kind: str


@dataclass(frozen=True)
class CommandDemoLoopContract:
    tokens: tuple[str, ...]
    entries: tuple[CommandDemoLoopEntry, ...]
    invocation_plan: tuple[CommandInvocationPlanEntry, ...] = ()
    lookup_table: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class CommandDemoTransitionEntry:
    source_token: str
    target_token: str
    canonical_name: str
    flow_step: str
    argv: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class CommandDemoTransitionContract:
    entries: tuple[CommandDemoTransitionEntry, ...]
    lookup_table: tuple[tuple[tuple[str, str], str], ...] = ()
    invocation_table: tuple[tuple[tuple[str, str], tuple[str, ...]], ...] = ()
    targets_by_source: tuple[tuple[str, tuple[str, ...]], ...] = ()


@dataclass(frozen=True)
class CommandDemoCompatibilityEntry:
    token: str
    canonical_token: str
    canonical_name: str
    flow_step: str
    argv: tuple[str, ...]
    description: str
    kind: str


@dataclass(frozen=True)
class CommandDemoCompatibilityContract:
    tokens: tuple[str, ...]
    entries: tuple[CommandDemoCompatibilityEntry, ...]
    lookup_table: tuple[tuple[str, str], ...] = ()
    invocation_table: tuple[tuple[str, tuple[str, ...]], ...] = ()


@dataclass(frozen=True)
class CommandDemoWorkflowEntry:
    token: str
    canonical_name: str
    flow_step: str
    argv: tuple[str, ...]
    description: str
    next_tokens: tuple[str, ...]
    compatibility_tokens: tuple[str, ...]
    preferred_surface_tokens: tuple[str, ...] = ()


@dataclass(frozen=True)
class CommandDemoWorkflowContract:
    tokens: tuple[str, ...]
    entries: tuple[CommandDemoWorkflowEntry, ...]
    flow_steps: tuple[str, ...]
    lookup_table: tuple[tuple[str, str], ...] = ()
    invocation_table: tuple[tuple[str, tuple[str, ...]], ...] = ()
    transition_targets: tuple[tuple[str, tuple[str, ...]], ...] = ()
    compatibility_lookup_table: tuple[tuple[str, str], ...] = ()
    compatibility_invocation_table: tuple[tuple[str, tuple[str, ...]], ...] = ()


@dataclass(frozen=True)
class CommandTrustedSurfaceEntry:
    token: str
    canonical_token: str
    canonical_name: str
    flow_step: str
    argv: tuple[str, ...]
    description: str
    source: str
    next_tokens: tuple[str, ...] = ()
    compatibility_tokens: tuple[str, ...] = ()
    preferred_surface_tokens: tuple[str, ...] = ()


@dataclass(frozen=True)
class CommandTrustedSurfaceContract:
    tokens: tuple[str, ...]
    entries: tuple[CommandTrustedSurfaceEntry, ...]
    lookup_table: tuple[tuple[str, str], ...] = ()
    invocation_table: tuple[tuple[str, tuple[str, ...]], ...] = ()


@dataclass(frozen=True)
class CommandDemoNextActionEntry:
    source_token: str
    target_token: str
    canonical_name: str
    flow_step: str
    argv: tuple[str, ...]
    description: str
    compatibility_tokens: tuple[str, ...] = ()
    preferred_surface_tokens: tuple[str, ...] = ()
    preferred_surface_invocations: tuple[tuple[str, tuple[str, ...]], ...] = ()


@dataclass(frozen=True)
class CommandDemoNextActionContract:
    source_token: str
    entries: tuple[CommandDemoNextActionEntry, ...]
    lookup_table: tuple[tuple[str, str], ...] = ()
    invocation_table: tuple[tuple[str, tuple[str, ...]], ...] = ()
    preferred_invocation_table: tuple[tuple[str, tuple[str, ...]], ...] = ()
    compatibility_lookup_table: tuple[tuple[str, str], ...] = ()
    compatibility_invocation_table: tuple[tuple[str, tuple[str, ...]], ...] = ()


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
class CommandDemoWorkflowInvocationEntry:
    token: str
    canonical_name: str
    flow_step: str
    argv: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class CommandDemoWorkflowInvocationContract:
    decision_token: str
    entries: tuple[CommandDemoWorkflowInvocationEntry, ...]


@dataclass(frozen=True)
class ResolvedCommand:
    token: str
    normalized_token: str
    canonical_name: str
    flow_step: str
    primary_cli_token: str
    argv: tuple[str, ...]
    smoke_argv: tuple[str, ...]
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


def _parser_ready_argv(spec: CommandSpec) -> tuple[str, ...]:
    entrypoints = _declared_cli_entrypoints_for(spec)
    if not entrypoints:
        raise ValueError(f"Command {spec.name} must define at least one CLI entrypoint")
    return (entrypoints[0],)


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

    # The CLI contract must track the full declared catalog projection of CLI
    # entrypoints, not just the canonical-name projection. Dropping a canonical
    # token and keeping only an alias must still fail fast for both the default
    # catalog and custom spec sets.
    if validated_entrypoints is not None:
        expected_parser_surface = tuple(
            (spec.name, _declared_cli_entrypoints_for(spec))
            for spec in specs
            if spec.cli_exposed
        )
        if validated_entrypoints != expected_parser_surface:
            raise ValueError("Command CLI catalog entrypoint projection is inconsistent")

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
    return _parser_ready_argv(spec)


def _smoke_argv_for_spec(spec: CommandSpec) -> tuple[str, ...]:
    if not spec.smoke_argv:
        return _default_smoke_argv(spec)

    raw_argv = tuple(spec.smoke_argv)
    if any(not token.strip() for token in raw_argv):
        raise ValueError(f"Command {spec.name} has an empty smoke argv token")

    primary_cli_token = _default_smoke_argv(spec)[0]
    normalized_primary = _normalize_token(raw_argv[0])
    if normalized_primary != primary_cli_token:
        raise ValueError(
            "Command smoke argv must start with the primary CLI entrypoint: "
            f"{spec.name} -> {spec.smoke_argv[0]}"
        )
    return (primary_cli_token, *raw_argv[1:])


def _surface_argv_for_spec(spec: CommandSpec) -> tuple[str, ...]:
    if not spec.surface_argv:
        return _default_smoke_argv(spec)

    raw_argv = tuple(spec.surface_argv)
    if any(not token.strip() for token in raw_argv):
        raise ValueError(f"Command {spec.name} has an empty surface argv token")

    primary_cli_token = _default_smoke_argv(spec)[0]
    normalized_primary = _normalize_token(raw_argv[0])
    if normalized_primary != primary_cli_token:
        raise ValueError(
            "Command surface argv must start with the primary CLI entrypoint: "
            f"{spec.name} -> {spec.surface_argv[0]}"
        )
    return (primary_cli_token, *raw_argv[1:])


def _preferred_surface_tokens_for_spec(spec: CommandSpec) -> tuple[str, ...]:
    if not spec.preferred_surface_tokens:
        return (_normalize_token(spec.flow_step),)

    known_surface_tokens = _flow_surface_tokens(*_lookup_resolution_tokens(spec), spec.flow_step)
    known_surface_index = {token: token for token in known_surface_tokens}
    seen_tokens: set[str] = set()
    preferred_tokens: list[str] = []
    for raw_token in spec.preferred_surface_tokens:
        normalized_token = _normalize_token(raw_token)
        if not normalized_token:
            raise ValueError(f"Command {spec.name} has an empty preferred surface token")
        if normalized_token not in known_surface_index:
            raise ValueError(
                f"Command {spec.name} preferred surface token is not part of the command surface: {raw_token}"
            )
        if normalized_token in seen_tokens:
            raise ValueError(
                f"Command {spec.name} has a duplicate preferred surface token: {raw_token}"
            )
        seen_tokens.add(normalized_token)
        preferred_tokens.append(normalized_token)
    return tuple(preferred_tokens)


def _preferred_surface_tokens_for_name(
    specs: tuple[CommandSpec, ...],
    name: str,
) -> tuple[str, ...]:
    spec = command_spec_for(specs, name)
    if spec is None:
        raise ValueError(f"Unknown command preferred surface target: {name}")
    return _preferred_surface_tokens_for_spec(spec)


def _preferred_surface_tokens_for_workflow_token(
    specs: tuple[CommandSpec, ...],
    name: str,
    token: str,
) -> tuple[str, ...]:
    preferred_tokens = _preferred_surface_tokens_for_name(specs, name)
    normalized_token = _normalize_token(token)
    if not normalized_token:
        return ()

    transition_token_lookup = _command_demo_transition_token_lookup(specs)
    matching_tokens = tuple(
        preferred_token
        for preferred_token in preferred_tokens
        if transition_token_lookup.get(preferred_token, preferred_token) == normalized_token
    )
    if matching_tokens:
        return matching_tokens
    return (normalized_token,)


def _shim_argv_overrides_for_spec(spec: CommandSpec) -> tuple[tuple[str, tuple[str, ...]], ...]:
    if not spec.shim_argv:
        return ()

    known_surface_tokens = _flow_surface_tokens(*_lookup_resolution_tokens(spec), spec.flow_step)
    known_surface_index = {token: token for token in known_surface_tokens}
    primary_cli_token = _parser_ready_argv(spec)[0]
    seen_tokens: set[str] = set()
    overrides: list[tuple[str, tuple[str, ...]]] = []
    for raw_token, raw_argv in spec.shim_argv:
        normalized_token = _normalize_token(raw_token)
        if not normalized_token:
            raise ValueError(f"Command {spec.name} has an empty shim token")
        if normalized_token not in known_surface_index:
            raise ValueError(
                f"Command {spec.name} shim token is not part of the command surface: {raw_token}"
            )
        if normalized_token in seen_tokens:
            raise ValueError(f"Command {spec.name} has a duplicate shim token: {raw_token}")
        seen_tokens.add(normalized_token)

        if not raw_argv:
            raise ValueError(f"Command {spec.name} shim argv must not be empty: {raw_token}")
        if any(not token.strip() for token in raw_argv):
            raise ValueError(f"Command {spec.name} shim argv has an empty token: {raw_token}")
        normalized_primary = _normalize_token(raw_argv[0])
        if normalized_primary != primary_cli_token:
            raise ValueError(
                "Command shim argv must start with the primary CLI entrypoint: "
                f"{spec.name} -> {raw_argv[0]}"
            )
        overrides.append((normalized_token, (primary_cli_token, *raw_argv[1:])))
    return tuple(overrides)


def _shim_pinned_options_for_spec(spec: CommandSpec) -> tuple[tuple[str, tuple[str, ...]], ...]:
    if not spec.shim_pinned_options:
        return ()

    known_surface_tokens = _flow_surface_tokens(*_lookup_resolution_tokens(spec), spec.flow_step)
    known_surface_index = {token: token for token in known_surface_tokens}
    seen_tokens: set[str] = set()
    pinned_options: list[tuple[str, tuple[str, ...]]] = []
    for raw_token, raw_option_names in spec.shim_pinned_options:
        normalized_token = _normalize_token(raw_token)
        if not normalized_token:
            raise ValueError(f"Command {spec.name} has an empty pinned shim token")
        if normalized_token not in known_surface_index:
            raise ValueError(
                f"Command {spec.name} pinned shim token is not part of the command surface: {raw_token}"
            )
        if normalized_token in seen_tokens:
            raise ValueError(f"Command {spec.name} has a duplicate pinned shim token: {raw_token}")
        seen_tokens.add(normalized_token)

        normalized_option_names: list[str] = []
        seen_option_names: set[str] = set()
        for raw_option_name in raw_option_names:
            option_name = raw_option_name.strip()
            if not option_name.startswith("-"):
                raise ValueError(
                    f"Command {spec.name} pinned shim option must be an option token: {raw_option_name}"
                )
            if option_name in seen_option_names:
                raise ValueError(
                    f"Command {spec.name} has a duplicate pinned shim option: {raw_option_name}"
                )
            seen_option_names.add(option_name)
            normalized_option_names.append(option_name)
        pinned_options.append((normalized_token, tuple(normalized_option_names)))
    return tuple(pinned_options)


def _shim_option_names(argv: tuple[str, ...]) -> set[str]:
    option_names: set[str] = set()
    index = 0
    while index < len(argv):
        token = argv[index]
        if not token.startswith("-"):
            index += 1
            continue
        option_name, _, _ = token.partition("=")
        option_names.add(option_name or token)
        if index + 1 < len(argv) and not argv[index + 1].startswith("-"):
            index += 2
            continue
        index += 1
    return option_names


def _looks_like_known_option_token(token: str, known_option_names: frozenset[str]) -> bool:
    if token == "--":
        return True
    if not token.startswith("-"):
        return False
    option_name, _, _ = token.partition("=")
    return (option_name or token) in known_option_names


def _normalize_explicit_shim_args(
    explicit_args: tuple[str, ...],
    *,
    option_names_with_values: frozenset[str] = frozenset(),
    known_option_names: frozenset[str] = frozenset(),
) -> tuple[str, ...]:
    if not explicit_args:
        return ()

    segments = _argv_segments(
        explicit_args,
        option_names_with_values=option_names_with_values,
        known_option_names=known_option_names,
    )
    last_option_segment_index: dict[str, int] = {
        segment[0].partition("=")[0] or segment[0]: segment_index
        for segment_index, segment in enumerate(segments)
        if segment[0].startswith("-")
    }

    normalized: list[str] = []
    for segment_index, segment in enumerate(segments):
        head = segment[0]
        if head.startswith("-"):
            option_name, _, _ = head.partition("=")
            if last_option_segment_index.get(option_name or head) != segment_index:
                continue
        normalized.extend(segment)
    return tuple(normalized)


def _argv_segments(
    argv: tuple[str, ...],
    *,
    option_names_with_values: frozenset[str] = frozenset(),
    known_option_names: frozenset[str] = frozenset(),
) -> tuple[tuple[str, ...], ...]:
    segments: list[tuple[str, ...]] = []
    index = 0
    while index < len(argv):
        token = argv[index]
        if token.startswith("-"):
            option_name, _, _ = token.partition("=")
            if index + 1 < len(argv) and "=" not in token:
                next_token = argv[index + 1]
                if not next_token.startswith("-") or (
                    (option_name or token) in option_names_with_values
                    and not _looks_like_known_option_token(next_token, known_option_names)
                ):
                    segments.append((token, next_token))
                    index += 2
                    continue
            segments.append((token,))
            index += 1
            continue
        segments.append((token,))
        index += 1
    return tuple(segments)


def _shim_option_names_with_values(argv: tuple[str, ...]) -> frozenset[str]:
    option_names: set[str] = set()
    for segment in _argv_segments(argv):
        head = segment[0]
        if not head.startswith("-") or len(segment) != 2:
            continue
        option_name, _, _ = head.partition("=")
        option_names.add(option_name or head)
    return frozenset(option_names)


def _shim_known_option_names(argv: tuple[str, ...]) -> frozenset[str]:
    option_names = _shim_option_names(argv)
    return frozenset(option_names | _shim_option_names_with_values(argv))


def _merge_shim_argv(
    shim_argv: tuple[str, ...],
    explicit_args: tuple[str, ...],
    *,
    pinned_options: frozenset[str] = frozenset(),
) -> tuple[str, ...]:
    shim_option_names_with_values = _shim_option_names_with_values(shim_argv[1:])
    shim_known_option_names = _shim_known_option_names(shim_argv[1:])
    normalized_explicit_args = _normalize_explicit_shim_args(
        explicit_args,
        option_names_with_values=shim_option_names_with_values,
        known_option_names=shim_known_option_names,
    )
    if len(shim_argv) <= 1 or not normalized_explicit_args:
        return (*shim_argv, *normalized_explicit_args)

    explicit_segments = _argv_segments(
        normalized_explicit_args,
        option_names_with_values=shim_option_names_with_values,
        known_option_names=shim_known_option_names,
    )
    explicit_option_segments: dict[str, tuple[str, ...]] = {}
    explicit_tail_segments: list[tuple[str, ...]] = []
    for segment in explicit_segments:
        head = segment[0]
        if not head.startswith("-"):
            explicit_tail_segments.append(segment)
            continue
        option_name = head.partition("=")[0] or head
        if option_name in pinned_options:
            continue
        explicit_option_segments[option_name] = segment

    replace_default_tail = bool(explicit_tail_segments) and any(
        not segment[0].startswith("-")
        for segment in _argv_segments(
            shim_argv[1:],
            option_names_with_values=shim_option_names_with_values,
            known_option_names=shim_known_option_names,
        )
    )
    merged_segments: list[tuple[str, ...]] = [(shim_argv[0],)]
    for segment in _argv_segments(
        shim_argv[1:],
        option_names_with_values=shim_option_names_with_values,
        known_option_names=shim_known_option_names,
    ):
        head = segment[0]
        if not head.startswith("-"):
            if replace_default_tail:
                continue
            merged_segments.append(segment)
            continue
        option_name = head.partition("=")[0] or head
        override = explicit_option_segments.pop(option_name, None)
        if override is not None:
            merged_segments.append(override)
            continue
        merged_segments.append(segment)

    merged_segments.extend(explicit_option_segments.values())
    merged_segments.extend(explicit_tail_segments)
    return tuple(token for segment in merged_segments for token in segment)


def _shim_pinned_options_lookup(
    specs: tuple[CommandSpec, ...],
) -> dict[str, frozenset[str]]:
    return {
        shim_token: frozenset(option_names)
        for spec in specs
        for shim_token, option_names in _shim_pinned_options_for_spec(spec)
    }


def _default_route_pinned_options(
    specs: tuple[CommandSpec, ...],
    flow_steps: tuple[str, ...] | None = None,
) -> frozenset[str]:
    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    if not ordered_flow_steps:
        return frozenset()
    return _shim_pinned_options_lookup(specs).get(_normalize_token(ordered_flow_steps[0]), frozenset())


def _resolve_parser_surface_flow_steps(
    specs: tuple[CommandSpec, ...],
    flow_steps: tuple[str, ...] | None,
) -> tuple[str, ...]:
    if flow_steps is not None:
        return flow_steps
    return command_flow_steps(specs)


COMMAND_SPECS: tuple[CommandSpec, ...] = (
    CommandSpec(
        name="bootstrap",
        aliases=("open", "project-open", "project", "bootstrap-run", "document-open", "open-document"),
        cli_tokens=("bootstrap",),
        smoke_argv=("bootstrap", "--project", "demo"),
        surface_argv=("bootstrap",),
        preferred_surface_tokens=("project-open",),
        description="Run the project bootstrap flow.",
        flow_step="project-open",
    ),
    CommandSpec(
        name="diff-preview",
        aliases=("diff", "diff_preview", "review-patch"),
        cli_tokens=("diff-preview", "diff"),
        smoke_argv=("diff-preview", "--original", "before", "--proposed", "after"),
        surface_argv=("diff-preview",),
        preferred_surface_tokens=("patch-review",),
        description="Preview unified diff output.",
        flow_step="patch-review",
    ),
    CommandSpec(
        name="context-basket",
        aliases=("context", "basket", "retrieval", "retrieve"),
        cli_tokens=("context-basket",),
        smoke_argv=("context-basket", "list"),
        surface_argv=("context-basket", "list"),
        preferred_surface_tokens=("retrieval",),
        description="Manage retrieval context basket items.",
        flow_step="retrieval",
    ),
    CommandSpec(
        name="terminal",
        aliases=(
            "export",
            "save-export",
            "persist",
            "persist-continue",
            "apply-patch",
            "patch-apply",
            "reject-patch",
            "patch-reject",
        ),
        cli_tokens=("terminal",),
        smoke_argv=(
            "terminal",
            "--operation-kind",
            "terminal_synthesis_request",
            "--message",
            "Export handoff",
        ),
        surface_argv=(
            "terminal",
            "--operation-kind",
            "terminal_synthesis_request",
            "--message",
            "Export handoff",
        ),
        shim_argv=(
            (
                "export",
                (
                    "terminal",
                    "--operation-kind",
                    "terminal_synthesis_request",
                    "--message",
                    "Export handoff",
                ),
            ),
            (
                "save-export",
                (
                    "terminal",
                    "--operation-kind",
                    "terminal_synthesis_request",
                    "--message",
                    "Export handoff",
                ),
            ),
            (
                "export-handoff",
                (
                    "terminal",
                    "--operation-kind",
                    "terminal_synthesis_request",
                    "--message",
                    "Export handoff",
                ),
            ),
            (
                "persist",
                (
                    "terminal",
                    "--operation-kind",
                    "terminal_synthesis_request",
                    "--message",
                    "Persist and continue",
                ),
            ),
            (
                "persist-continue",
                (
                    "terminal",
                    "--operation-kind",
                    "terminal_synthesis_request",
                    "--message",
                    "Persist and continue",
                ),
            ),
            (
                "apply-patch",
                (
                    "terminal",
                    "--operation-kind",
                    "terminal_tool_orchestration",
                    "--message",
                    "Apply patch",
                ),
            ),
            (
                "patch-apply",
                (
                    "terminal",
                    "--operation-kind",
                    "terminal_tool_orchestration",
                    "--message",
                    "Apply patch",
                ),
            ),
            (
                "reject-patch",
                (
                    "terminal",
                    "--operation-kind",
                    "terminal_tool_orchestration",
                    "--message",
                    "Reject patch",
                ),
            ),
            (
                "patch-reject",
                (
                    "terminal",
                    "--operation-kind",
                    "terminal_tool_orchestration",
                    "--message",
                    "Reject patch",
                ),
            ),
        ),
        shim_pinned_options=(
            ("export", ("--operation-kind",)),
            ("save-export", ("--operation-kind",)),
            ("export-handoff", ("--operation-kind",)),
            ("persist", ("--operation-kind",)),
            ("persist-continue", ("--operation-kind",)),
            ("apply-patch", ("--operation-kind",)),
            ("patch-apply", ("--operation-kind",)),
            ("reject-patch", ("--operation-kind",)),
            ("patch-reject", ("--operation-kind",)),
        ),
        preferred_surface_tokens=("apply-patch", "reject-patch", "persist", "export-handoff", "export"),
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
            if spec.surface_argv:
                raise ValueError(f"Command {spec.name} must not declare surface argv when cli_exposed is false")
            if spec.shim_argv:
                raise ValueError(f"Command {spec.name} must not declare shim argv when cli_exposed is false")
            if spec.shim_pinned_options:
                raise ValueError(
                    f"Command {spec.name} must not declare pinned shim options when cli_exposed is false"
                )
            continue

        _smoke_argv_for_spec(spec)
        _surface_argv_for_spec(spec)
        _shim_argv_overrides_for_spec(spec)
        _shim_pinned_options_for_spec(spec)
        _preferred_surface_tokens_for_spec(spec)


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
    surface_tokens = command_surface_tokens_for(specs, spec.name)
    if not surface_tokens:
        return _lookup_aliases(spec)
    return tuple(token for token in surface_tokens if token != spec.name)


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
    contract = CommandCliFlowContract(entries=tuple(entries))
    _validate_command_cli_flow_contract(contract, specs)
    return contract


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
    contract = CommandCliSurfaceContract(entries=command_cli_surface_catalog(specs))
    _validate_command_cli_surface_contract(contract, specs)
    return contract


def _validate_command_cli_flow_contract(
    contract: CommandCliFlowContract,
    specs: tuple[CommandSpec, ...],
) -> None:
    cli_contract = _command_cli_contract_for(specs)
    expected_entries = tuple(
        CommandCliFlowEntry(
            token=token,
            canonical_name=canonical_name,
            flow_step=_normalize_token(spec.flow_step),
        )
        for token, canonical_name in cli_contract.lookup_table
        for spec in (command_spec_for(specs, canonical_name),)
        if spec is not None
    )
    if contract.entries != expected_entries:
        raise ValueError("Command CLI flow entries are inconsistent")


def _validate_command_cli_surface_contract(
    contract: CommandCliSurfaceContract,
    specs: tuple[CommandSpec, ...],
) -> None:
    expected_entries = command_cli_surface_catalog(specs)
    if contract.entries != expected_entries:
        raise ValueError("Command CLI surface entries are inconsistent")


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
    ordered_flow_steps = _resolve_parser_surface_flow_steps(specs, flow_steps)
    route_catalog = command_flow_route_catalog(flow_steps=ordered_flow_steps, specs=specs)
    entries: list[CommandCliShimEntry] = []
    for route_entry in route_catalog:
        spec = command_spec_for(specs, route_entry.name)
        if spec is None:
            raise ValueError(f"Unknown command shim target: {route_entry.name}")
        shim_argv_overrides = dict(_shim_argv_overrides_for_spec(spec))
        default_surface_argv = _surface_argv_for_spec(spec)
        for token in route_entry.surface_tokens:
            argv = shim_argv_overrides.get(token, default_surface_argv)
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
    invocation_lookup = dict(command_cli_shim_invocation_table(specs, flow_steps))
    pinned_options_lookup = _shim_pinned_options_lookup(specs)
    normalized_token = _normalize_token(raw_argv[0])
    shim_argv = invocation_lookup.get(normalized_token)
    if len(raw_argv) == 1:
        if shim_argv is not None:
            return shim_argv
    elif shim_argv is not None and len(shim_argv) > 1:
        # Preserve alias-specific default routing while still allowing callers to
        # append explicit parser flags for deterministic CLI smoke paths.
        return _merge_shim_argv(
            shim_argv,
            raw_argv[1:],
            pinned_options=pinned_options_lookup.get(normalized_token, frozenset()),
        )
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
    ordered_flow_steps = _resolve_parser_surface_flow_steps(specs, flow_steps)
    route_tokens = command_flow_route_tokens(specs, ordered_flow_steps)
    default_token = route_tokens[0] if route_tokens else ""
    smoke_plan = command_smoke_invocation_plan(specs, ordered_flow_steps)
    default_argv = smoke_plan[0].argv if smoke_plan else ()
    if not raw_argv:
        return (default_token,) if default_token else ()
    if raw_argv[0].lstrip().startswith("-"):
        if default_argv:
            return _merge_shim_argv(
                default_argv,
                raw_argv,
                pinned_options=_default_route_pinned_options(specs, ordered_flow_steps),
            )
        return (default_token, *raw_argv) if default_token else raw_argv
    compatibility_argv = (
        _normalize_demo_compatibility_argv(raw_argv)
        if _uses_demo_compatibility_flow(ordered_flow_steps)
        else raw_argv
    )
    normalized_argv = command_cli_shim_argv_for(specs, compatibility_argv, ordered_flow_steps)
    resolved = command_resolve_for(specs, compatibility_argv[0], ordered_flow_steps)
    if len(compatibility_argv) != 1:
        if not resolved.matched:
            fallback_argv = _resolve_demo_fallback_argv(specs, compatibility_argv, ordered_flow_steps)
            if fallback_argv:
                return fallback_argv
            return normalized_argv
        return _resolved_parser_ready_argv(specs, resolved, compatibility_argv[1:])

    if not resolved.matched:
        fallback_argv = _resolve_demo_fallback_argv(specs, compatibility_argv, ordered_flow_steps)
        if fallback_argv:
            return fallback_argv
        return normalized_argv

    spec = command_spec_for(specs, resolved.canonical_name)
    if spec is not None and spec.surface_argv:
        return normalized_argv

    smoke_argv = command_smoke_entry_argv_for(specs, resolved.canonical_name)
    if len(smoke_argv) > 1:
        return smoke_argv
    return normalized_argv


@lru_cache(maxsize=None)
def command_cli_shim_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    flow_steps: tuple[str, ...] | None = None,
) -> CommandCliShimContract:
    contract = CommandCliShimContract(
        entries=command_cli_shim_catalog(specs, flow_steps),
        lookup_table=command_cli_shim_lookup_table(specs, flow_steps),
        invocation_table=command_cli_shim_invocation_table(specs, flow_steps),
    )
    _validate_command_cli_shim_contract(contract, specs, flow_steps)
    return contract


def _validate_command_cli_shim_contract(
    contract: CommandCliShimContract,
    specs: tuple[CommandSpec, ...],
    flow_steps: tuple[str, ...] | None,
) -> None:
    expected_entries = command_cli_shim_catalog(specs, flow_steps)
    if contract.entries != expected_entries:
        raise ValueError("Command CLI shim entries are inconsistent")
    if contract.lookup_table != tuple((entry.token, entry.primary_cli_token) for entry in contract.entries):
        raise ValueError("Command CLI shim lookup table is inconsistent")
    if contract.invocation_table != tuple((entry.token, entry.argv) for entry in contract.entries):
        raise ValueError("Command CLI shim invocation table is inconsistent")


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
    return command_demo_cli_flow_contract(specs)


def command_demo_cli_flow_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandCliFlowContract:
    allowed_flow_steps = frozenset(command_demo_flow_steps())
    return CommandCliFlowContract(
        entries=tuple(
            entry
            for entry in command_cli_flow_contract(specs).entries
            if entry.flow_step in allowed_flow_steps
        )
    )


def command_demo_cli_surface_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandCliSurfaceEntry, ...]:
    allowed_flow_steps = frozenset(command_demo_flow_steps())
    return tuple(
        entry
        for entry in command_cli_surface_catalog(specs)
        if entry.flow_step in allowed_flow_steps
    )


def command_demo_cli_surface_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandCliSurfaceContract:
    return CommandCliSurfaceContract(entries=command_demo_cli_surface_catalog(specs))


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
    if tuple(entry.smoke_argv for entry in contract.entries) != tuple(
        entry.argv for entry in contract.smoke_invocation_plan
    ):
        raise ValueError("Command smoke argv is inconsistent")
    if tuple((entry.flow_step, entry.name, entry.cli_tokens) for entry in contract.entries) != contract.route_summary:
        raise ValueError("Command smoke route summary is inconsistent")
    if tuple((entry.flow_step, entry.name, entry.argv) for entry in contract.invocation_plan) != tuple(
        (entry.flow_step, entry.name, (entry.primary_cli_token,))
        for entry in contract.entries
    ):
        raise ValueError("Command smoke invocation plan is inconsistent")
    if tuple((entry.flow_step, entry.name) for entry in contract.smoke_invocation_plan) != tuple(
        (entry.flow_step, entry.name)
        for entry in contract.entries
    ):
        raise ValueError("Command smoke parser invocation order is inconsistent")

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


def _validate_command_demo_path_contract(
    contract: CommandDemoPathContract,
    smoke_contract: CommandSmokeContract,
    *,
    specs: tuple[CommandSpec, ...],
) -> None:
    transition_targets_by_source = dict(command_demo_transition_targets_by_source(specs))
    if contract.flow_steps != smoke_contract.flow_steps:
        raise ValueError("Command demo path flow steps are inconsistent")
    if contract.names != smoke_contract.names:
        raise ValueError("Command demo path names are inconsistent")
    if tuple((entry.flow_step, entry.name) for entry in contract.entries) != contract.lookup_table:
        raise ValueError("Command demo path lookup table is inconsistent")
    if tuple(entry.argv for entry in contract.entries) != tuple(
        entry.argv for entry in smoke_contract.invocation_plan
    ):
        raise ValueError("Command demo path invocation argv is inconsistent")
    if tuple(entry.parser_argv for entry in contract.entries) != tuple(
        entry.argv for entry in smoke_contract.smoke_invocation_plan
    ):
        raise ValueError("Command demo path parser argv is inconsistent")
    if tuple(entry.smoke_argv for entry in contract.entries) != tuple(
        entry.smoke_argv for entry in smoke_contract.entries
    ):
        raise ValueError("Command demo path smoke argv is inconsistent")
    if contract.invocation_plan != smoke_contract.smoke_invocation_plan:
        raise ValueError("Command demo path invocation plan is inconsistent")
    if tuple(entry.lookup_tokens for entry in contract.entries) != tuple(
        entry.lookup_tokens for entry in smoke_contract.entries
    ):
        raise ValueError("Command demo path lookup tokens are inconsistent")
    if tuple(entry.surface_tokens for entry in contract.entries) != tuple(
        entry.surface_tokens for entry in smoke_contract.entries
    ):
        raise ValueError("Command demo path surface tokens are inconsistent")
    if tuple(entry.preferred_surface_tokens for entry in contract.entries) != tuple(
        _preferred_surface_tokens_for_name(specs, entry.name) for entry in smoke_contract.entries
    ):
        raise ValueError("Command demo path preferred surface tokens are inconsistent")
    if tuple(entry.next_tokens for entry in contract.entries) != tuple(
        transition_targets_by_source.get(entry.flow_step, ()) for entry in contract.entries
    ):
        raise ValueError("Command demo path next tokens are inconsistent")
    if tuple(tuple(token for token, _ in entry.surface_invocations) for entry in contract.entries) != tuple(
        entry.surface_tokens for entry in smoke_contract.entries
    ):
        raise ValueError("Command demo path surface invocations are inconsistent")
    if tuple(tuple(token for token, _ in entry.preferred_surface_invocations) for entry in contract.entries) != tuple(
        entry.preferred_surface_tokens for entry in contract.entries
    ):
        raise ValueError("Command demo path preferred surface invocations are inconsistent")
    if tuple(tuple(token for token, _ in entry.parser_surface_invocations) for entry in contract.entries) != tuple(
        entry.cli_tokens for entry in smoke_contract.entries
    ):
        raise ValueError("Command demo path parser surface invocations are inconsistent")
    expected_surface_invocations = tuple(
        tuple(
            (
                token,
                command_smoke_argv_for(specs, (token,), contract.flow_steps),
            )
            for token in entry.surface_tokens
        )
        for entry in smoke_contract.entries
    )
    if tuple(entry.surface_invocations for entry in contract.entries) != expected_surface_invocations:
        raise ValueError("Command demo path surface invocation argv is inconsistent")
    expected_preferred_surface_invocations = tuple(
        tuple(
            (
                token,
                command_smoke_argv_for(specs, (token,), contract.flow_steps),
            )
            for token in entry.preferred_surface_tokens
        )
        for entry in contract.entries
    )
    if (
        tuple(entry.preferred_surface_invocations for entry in contract.entries)
        != expected_preferred_surface_invocations
    ):
        raise ValueError("Command demo path preferred surface invocation argv is inconsistent")
    expected_parser_surface_invocations = tuple(
        tuple(
            (
                token,
                command_smoke_argv_for(specs, (token,), contract.flow_steps),
            )
            for token in entry.cli_tokens
        )
        for entry in smoke_contract.entries
    )
    if tuple(entry.parser_surface_invocations for entry in contract.entries) != expected_parser_surface_invocations:
        raise ValueError("Command demo path parser surface invocation argv is inconsistent")
    if contract.lookup_surface != smoke_contract.lookup_surface:
        raise ValueError("Command demo path lookup surface is inconsistent")


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
    smoke_invocation_plan = command_smoke_invocation_plan(specs, ordered_flow_steps)
    smoke_argv_by_name = {entry.name: entry.argv for entry in smoke_invocation_plan}
    entries = tuple(
        CommandSmokeEntry(
            flow_step=entry.flow_step,
            name=entry.name,
            primary_cli_token=entry.primary_cli_token,
            cli_tokens=entry.cli_tokens,
            lookup_tokens=entry.lookup_tokens,
            surface_tokens=entry.surface_tokens,
            description=entry.description,
            smoke_argv=smoke_argv_by_name.get(entry.name, (entry.primary_cli_token,)),
        )
        for entry in route_catalog
    )
    contract = CommandSmokeContract(
        flow_steps=tuple(entry.flow_step for entry in entries),
        names=tuple(entry.name for entry in entries),
        entries=entries,
        primary_cli_tokens=tuple(entry.primary_cli_token for entry in entries),
        invocation_plan=command_flow_invocation_plan(specs, ordered_flow_steps),
        smoke_invocation_plan=smoke_invocation_plan,
        route_summary=tuple((entry.flow_step, entry.name, entry.cli_tokens) for entry in entries),
        lookup_surface=command_flow_lookup_surface(specs, ordered_flow_steps),
    )
    _validate_command_smoke_contract(contract)
    return contract


def command_demo_smoke_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandSmokeContract:
    return command_smoke_contract(specs, command_demo_flow_steps())


@lru_cache(maxsize=None)
def command_demo_path_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoPathContract:
    smoke_contract = command_demo_smoke_contract(specs)
    transition_targets_by_source = dict(command_demo_transition_targets_by_source(specs))
    route_invocation_plan = smoke_contract.invocation_plan
    parser_invocation_plan = smoke_contract.smoke_invocation_plan
    route_catalog = command_flow_route_catalog(flow_steps=command_demo_flow_steps(), specs=specs)
    route_entries_by_step = {entry.flow_step: entry for entry in route_catalog}
    shim_entries = command_cli_shim_catalog(specs, command_demo_flow_steps())
    parser_ready_invocations_by_step: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {}
    parser_surface_invocations_by_step: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {}
    for flow_step in smoke_contract.flow_steps:
        parser_ready_invocations_by_step[flow_step] = tuple(
            (
                entry.token,
                command_smoke_argv_for(specs, (entry.token,), command_demo_flow_steps()),
            )
            for entry in shim_entries
            if entry.flow_step == flow_step
        )
        route_entry = route_entries_by_step[flow_step]
        parser_surface_invocations_by_step[flow_step] = tuple(
            (
                cli_token,
                command_smoke_argv_for(specs, (cli_token,), command_demo_flow_steps()),
            )
            for cli_token in route_entry.cli_tokens
        )
    entries = tuple(
        CommandDemoPathEntry(
            flow_step=entry.flow_step,
            name=entry.name,
            primary_cli_token=entry.primary_cli_token,
            argv=route_invocation_plan[index].argv,
            parser_argv=parser_invocation_plan[index].argv,
            smoke_argv=entry.smoke_argv,
            description=entry.description,
            lookup_tokens=entry.lookup_tokens,
            surface_tokens=entry.surface_tokens,
            preferred_surface_tokens=_preferred_surface_tokens_for_name(specs, entry.name),
            next_tokens=transition_targets_by_source.get(entry.flow_step, ()),
            surface_invocations=parser_ready_invocations_by_step.get(entry.flow_step, ()),
            preferred_surface_invocations=tuple(
                (
                    token,
                    command_smoke_argv_for(specs, (token,), command_demo_flow_steps()),
                )
                for token in _preferred_surface_tokens_for_name(specs, entry.name)
            ),
            parser_surface_invocations=parser_surface_invocations_by_step.get(entry.flow_step, ()),
        )
        for index, entry in enumerate(smoke_contract.entries)
    )
    contract = CommandDemoPathContract(
        flow_steps=smoke_contract.flow_steps,
        names=smoke_contract.names,
        entries=entries,
        invocation_plan=parser_invocation_plan,
        lookup_table=tuple((entry.flow_step, entry.name) for entry in entries),
        lookup_surface=smoke_contract.lookup_surface,
    )
    _validate_command_demo_path_contract(contract, smoke_contract, specs=specs)
    return contract


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


@lru_cache(maxsize=None)
def command_mvp_path_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoPathContract:
    return command_demo_path_contract(specs)


def command_demo_path_invocation_plan(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandInvocationPlanEntry, ...]:
    """Return parser-ready argv for the canonical demo-path command sequence."""
    return command_demo_path_contract(specs).invocation_plan


def command_mvp_path_invocation_plan(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandInvocationPlanEntry, ...]:
    """Return parser-ready argv for the current MVP command sequence."""
    return command_demo_path_invocation_plan(specs)


_COMMAND_DEMO_LOOP_TOKENS = (
    "project-open",
    "retrieval",
    "patch-review",
    "apply-patch",
    "reject-patch",
    "persist",
    "export-handoff",
)

_COMMAND_DEMO_LOOP_DESCRIPTIONS = {
    "apply-patch": "Apply the reviewed patch through the terminal orchestration bridge.",
    "reject-patch": "Reject the reviewed patch through the terminal orchestration bridge.",
    "persist": "Persist current work and continue the CLI-first MVP loop.",
    "export-handoff": "Prepare the reviewed result for export handoff.",
}

_COMMAND_DEMO_LOOP_FALLBACK_TOKENS: dict[str, tuple[str, ...]] = {
    "project-open": ("open", "document-open", "open-document", "project", "bootstrap-run"),
    "retrieval": ("retrieve", "context", "basket", "context-basket"),
    "patch-review": ("review-patch", "diff-preview", "diff", "diff_preview"),
    "apply-patch": ("patch-apply",),
    "reject-patch": ("patch-reject",),
    "persist": ("persist-continue",),
    "export-handoff": ("export", "save-export", "terminal"),
}

_COMMAND_DEMO_TRANSITIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("project-open", ("retrieval",)),
    ("retrieval", ("patch-review",)),
    ("patch-review", ("apply-patch", "reject-patch")),
    ("apply-patch", ("persist",)),
    ("reject-patch", ("persist",)),
    ("persist", ("export-handoff",)),
)

_COMMAND_DEMO_COMPATIBILITY_TOKENS: dict[str, str] = {
    "open-project": "project-open",
    "retrieve-context": "retrieval",
    "review": "patch-review",
    "preview-patch": "patch-review",
    "save": "persist",
    "continue": "persist",
    "resume": "persist",
    "apply": "apply-patch",
    "approve": "apply-patch",
    "accept": "apply-patch",
    "reject": "reject-patch",
    "decline": "reject-patch",
    "discard": "reject-patch",
    "handoff": "export-handoff",
    "queue-export": "export-handoff",
}

_COMMAND_DEMO_COMPATIBILITY_VARIANTS: dict[str, str] = {
    "project-bootstrap": "project-open",
    "bootstrap-project": "project-open",
    "open-workspace": "project-open",
    "gather-context": "retrieval",
    "load-context": "retrieval",
    "review-diff": "patch-review",
    "preview-diff": "patch-review",
    "approve-patch": "apply-patch",
    "accept-patch": "apply-patch",
    "decline-patch": "reject-patch",
    "discard-patch": "reject-patch",
    "save-work": "persist",
    "continue-work": "persist",
    "resume-work": "persist",
    "handoff-export": "export-handoff",
    "queue-handoff": "export-handoff",
}


def _demo_compatibility_entries() -> tuple[tuple[str, str], ...]:
    base_tokens_by_canonical: dict[str, list[str]] = {}
    for token, canonical_token in _COMMAND_DEMO_COMPATIBILITY_TOKENS.items():
        base_tokens_by_canonical.setdefault(canonical_token, []).append(token)

    variant_tokens_by_canonical: dict[str, list[str]] = {}
    for variant_token, canonical_token in _COMMAND_DEMO_COMPATIBILITY_VARIANTS.items():
        variant_tokens_by_canonical.setdefault(canonical_token, []).append(variant_token)

    entries: list[tuple[str, str]] = []
    seen_canonical_tokens: set[str] = set()
    for canonical_token in _COMMAND_DEMO_COMPATIBILITY_TOKENS.values():
        if canonical_token in seen_canonical_tokens:
            continue
        seen_canonical_tokens.add(canonical_token)
        entries.extend((token, canonical_token) for token in base_tokens_by_canonical.get(canonical_token, ()))
        entries.extend((token, canonical_token) for token in variant_tokens_by_canonical.get(canonical_token, ()))
    return tuple(entries)


def _demo_loop_description_for(token: str, resolved: ResolvedCommand) -> str:
    return _COMMAND_DEMO_LOOP_DESCRIPTIONS.get(token, resolved.description)


def _normalize_demo_compatibility_token(token: str) -> str:
    normalized_token = _normalize_token(token)
    if not normalized_token:
        return token
    variant_token = _COMMAND_DEMO_COMPATIBILITY_VARIANTS.get(normalized_token)
    if variant_token is not None:
        return variant_token
    return _COMMAND_DEMO_COMPATIBILITY_TOKENS.get(normalized_token, normalized_token)


def _normalize_demo_compatibility_argv(argv: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    raw_argv = tuple(argv)
    if not raw_argv:
        return ()
    if raw_argv[0].lstrip().startswith("-"):
        return raw_argv
    return (_normalize_demo_compatibility_token(raw_argv[0]), *raw_argv[1:])


_COMMAND_DEMO_TERMINAL_MESSAGE_TOKENS: dict[tuple[str, str], str] = {
    ("terminal-tool-orchestration", "apply-patch"): "apply-patch",
    ("terminal-tool-orchestration", "approve-patch"): "apply-patch",
    ("terminal-tool-orchestration", "accept-patch"): "apply-patch",
    ("terminal-tool-orchestration", "reject-patch"): "reject-patch",
    ("terminal-tool-orchestration", "decline-patch"): "reject-patch",
    ("terminal-tool-orchestration", "discard-patch"): "reject-patch",
    ("terminal-synthesis-request", "persist"): "persist",
    ("terminal-synthesis-request", "persist-and-continue"): "persist",
    ("terminal-synthesis-request", "save-work"): "persist",
    ("terminal-synthesis-request", "continue-work"): "persist",
    ("terminal-synthesis-request", "resume-work"): "persist",
    ("terminal-synthesis-request", "export"): "export-handoff",
    ("terminal-synthesis-request", "export-handoff"): "export-handoff",
    ("terminal-synthesis-request", "handoff-export"): "export-handoff",
    ("terminal-synthesis-request", "queue-handoff"): "export-handoff",
}


def _argv_option_value(argv: tuple[str, ...], option_name: str) -> str:
    for index, token in enumerate(argv):
        if token == option_name and index + 1 < len(argv):
            return argv[index + 1]
        if token.startswith(f"{option_name}="):
            return token.partition("=")[2]
    return ""


def _canonical_demo_terminal_argv_token(resolved: ResolvedCommand) -> str:
    if resolved.canonical_name != "terminal" or not resolved.argv:
        return ""
    operation_kind = _normalize_token(_argv_option_value(resolved.argv, "--operation-kind"))
    message = _normalize_token(_argv_option_value(resolved.argv, "--message"))
    if not operation_kind or not message:
        return ""
    canonical_token = _COMMAND_DEMO_TERMINAL_MESSAGE_TOKENS.get((operation_kind, message), "")
    if canonical_token in _COMMAND_DEMO_LOOP_TOKENS:
        return canonical_token
    return ""


def _uses_demo_compatibility_surface(token: str) -> bool:
    normalized_token = _normalize_token(token)
    if not normalized_token:
        return False
    return (
        normalized_token in _COMMAND_DEMO_COMPATIBILITY_TOKENS
        or normalized_token in _COMMAND_DEMO_COMPATIBILITY_VARIANTS
    )


def _uses_demo_compatibility_flow(flow_steps: tuple[str, ...]) -> bool:
    return _normalize_flow_steps(flow_steps) == command_demo_flow_steps()


def _align_demo_flow_step(
    resolved: ResolvedCommand,
    demo_token: str,
) -> ResolvedCommand:
    normalized_demo_token = _normalize_token(demo_token)
    if (
        not resolved.matched
        or not normalized_demo_token
        or normalized_demo_token not in _COMMAND_DEMO_LOOP_TOKENS
        or resolved.flow_step == normalized_demo_token
    ):
        return resolved
    return replace(resolved, flow_step=normalized_demo_token)


def _demo_alignment_token_for_argv(
    resolved: ResolvedCommand,
    raw_argv: tuple[str, ...],
) -> str:
    if not raw_argv:
        return ""
    terminal_token = _canonical_demo_terminal_argv_token(resolved)
    if terminal_token:
        return terminal_token
    normalized_flow_step = _normalize_token(resolved.flow_step)
    if normalized_flow_step in _COMMAND_DEMO_LOOP_TOKENS:
        return normalized_flow_step
    return raw_argv[0]


def _resolve_demo_loop_token(
    specs: tuple[CommandSpec, ...],
    token: str,
    *,
    ordered_flow_steps: tuple[str, ...],
) -> ResolvedCommand:
    candidates = (token, *_COMMAND_DEMO_LOOP_FALLBACK_TOKENS.get(token, ()))
    for candidate in candidates:
        resolved = _prefer_demo_flow_smoke_resolution(
            command_resolve_for(specs, candidate, ordered_flow_steps),
            specs=specs,
            raw_argv=(candidate,),
        )
        if resolved.matched:
            return _align_demo_flow_step(resolved, token)
    raise ValueError(f"Command demo loop token is unresolved: {token}")


def _validate_command_demo_loop_contract(contract: CommandDemoLoopContract) -> None:
    if contract.tokens != tuple(entry.token for entry in contract.entries):
        raise ValueError("Command demo loop tokens are inconsistent")
    if contract.invocation_plan != tuple(
        CommandInvocationPlanEntry(
            flow_step=entry.flow_step,
            name=entry.canonical_name,
            argv=entry.argv,
            description=entry.description,
        )
        for entry in contract.entries
    ):
        raise ValueError("Command demo loop invocation plan is inconsistent")
    if contract.lookup_table != tuple((entry.token, entry.canonical_name) for entry in contract.entries):
        raise ValueError("Command demo loop lookup table is inconsistent")


def _validate_command_demo_transition_contract(contract: CommandDemoTransitionContract) -> None:
    if contract.lookup_table != tuple(
        ((entry.source_token, entry.target_token), entry.canonical_name) for entry in contract.entries
    ):
        raise ValueError("Command demo transition lookup table is inconsistent")
    if contract.invocation_table != tuple(
        ((entry.source_token, entry.target_token), entry.argv) for entry in contract.entries
    ):
        raise ValueError("Command demo transition invocation table is inconsistent")
    expected_targets_by_source: list[tuple[str, tuple[str, ...]]] = []
    for source_token, _ in _COMMAND_DEMO_TRANSITIONS:
        targets = tuple(entry.target_token for entry in contract.entries if entry.source_token == source_token)
        expected_targets_by_source.append((source_token, targets))
    if contract.targets_by_source != tuple(expected_targets_by_source):
        raise ValueError("Command demo transition targets are inconsistent")


def _validate_command_demo_compatibility_contract(contract: CommandDemoCompatibilityContract) -> None:
    if contract.tokens != tuple(entry.token for entry in contract.entries):
        raise ValueError("Command demo compatibility tokens are inconsistent")
    if contract.lookup_table != tuple((entry.token, entry.canonical_name) for entry in contract.entries):
        raise ValueError("Command demo compatibility lookup table is inconsistent")
    if contract.invocation_table != tuple((entry.token, entry.argv) for entry in contract.entries):
        raise ValueError("Command demo compatibility invocation table is inconsistent")
    if any(entry.kind != "compatibility" for entry in contract.entries):
        raise ValueError("Command demo compatibility kinds are inconsistent")
    if any(entry.token == entry.canonical_token for entry in contract.entries):
        raise ValueError("Command demo compatibility canonical tokens must differ from compatibility tokens")


def _validate_command_demo_workflow_contract(contract: CommandDemoWorkflowContract) -> None:
    if contract.tokens != tuple(entry.token for entry in contract.entries):
        raise ValueError("Command demo workflow tokens are inconsistent")
    if contract.lookup_table != tuple((entry.token, entry.canonical_name) for entry in contract.entries):
        raise ValueError("Command demo workflow lookup table is inconsistent")
    if contract.invocation_table != tuple((entry.token, entry.argv) for entry in contract.entries):
        raise ValueError("Command demo workflow invocation table is inconsistent")
    if contract.transition_targets != tuple((entry.token, entry.next_tokens) for entry in contract.entries):
        raise ValueError("Command demo workflow transition targets are inconsistent")
    expected_compatibility_lookup = tuple(
        (compatibility_token, entry.canonical_name)
        for entry in contract.entries
        for compatibility_token in entry.compatibility_tokens
    )
    if contract.compatibility_lookup_table != expected_compatibility_lookup:
        raise ValueError("Command demo workflow compatibility lookup table is inconsistent")
    expected_compatibility_invocations = tuple(
        (compatibility_token, entry.argv)
        for entry in contract.entries
        for compatibility_token in entry.compatibility_tokens
    )
    if contract.compatibility_invocation_table != expected_compatibility_invocations:
        raise ValueError("Command demo workflow compatibility invocation table is inconsistent")
    for entry in contract.entries:
        if not entry.argv:
            raise ValueError(f"Command demo workflow entry is missing argv: {entry.token}")
        if entry.flow_step != _normalize_token(entry.flow_step):
            raise ValueError(f"Command demo workflow flow step is inconsistent: {entry.token}")
        if entry.token != _normalize_token(entry.token):
            raise ValueError(f"Command demo workflow token is inconsistent: {entry.token}")


def _validate_command_demo_next_action_contract(contract: CommandDemoNextActionContract) -> None:
    if contract.lookup_table != tuple((entry.target_token, entry.canonical_name) for entry in contract.entries):
        raise ValueError("Command demo next action lookup table is inconsistent")
    if contract.invocation_table != tuple((entry.target_token, entry.argv) for entry in contract.entries):
        raise ValueError("Command demo next action invocation table is inconsistent")
    if contract.preferred_invocation_table != tuple(
        invocation
        for entry in contract.entries
        for invocation in entry.preferred_surface_invocations
    ):
        raise ValueError("Command demo next action preferred invocation table is inconsistent")
    expected_compatibility_lookup = tuple(
        (compatibility_token, entry.canonical_name)
        for entry in contract.entries
        for compatibility_token in entry.compatibility_tokens
    )
    if contract.compatibility_lookup_table != expected_compatibility_lookup:
        raise ValueError("Command demo next action compatibility lookup table is inconsistent")
    expected_compatibility_invocations = tuple(
        (compatibility_token, entry.argv)
        for entry in contract.entries
        for compatibility_token in entry.compatibility_tokens
    )
    if contract.compatibility_invocation_table != expected_compatibility_invocations:
        raise ValueError("Command demo next action compatibility invocation table is inconsistent")
    for entry in contract.entries:
        if entry.source_token != contract.source_token:
            raise ValueError("Command demo next action source token is inconsistent")
        if not entry.argv:
            raise ValueError(f"Command demo next action entry is missing argv: {entry.target_token}")
        if tuple(token for token, _ in entry.preferred_surface_invocations) != entry.preferred_surface_tokens:
            raise ValueError(
                "Command demo next action preferred surface invocations are inconsistent"
            )
        if any(not argv for _, argv in entry.preferred_surface_invocations):
            raise ValueError(
                f"Command demo next action preferred invocation is missing argv: {entry.target_token}"
            )


@lru_cache(maxsize=None)
def command_demo_loop_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoLoopContract:
    ordered_flow_steps = command_demo_flow_steps() if specs is COMMAND_SPECS else command_flow_steps(specs)
    entries: list[CommandDemoLoopEntry] = []
    for token in _COMMAND_DEMO_LOOP_TOKENS:
        resolved = _resolve_demo_loop_token(specs, token, ordered_flow_steps=ordered_flow_steps)
        entries.append(
            CommandDemoLoopEntry(
                token=token,
                canonical_name=resolved.canonical_name,
                flow_step=resolved.flow_step,
                argv=resolved.argv,
                description=_demo_loop_description_for(token, resolved),
                kind=resolved.kind,
            )
        )
    contract = CommandDemoLoopContract(
        tokens=tuple(entry.token for entry in entries),
        entries=tuple(entries),
        invocation_plan=tuple(
            CommandInvocationPlanEntry(
                flow_step=entry.flow_step,
                name=entry.canonical_name,
                argv=entry.argv,
                description=entry.description,
            )
            for entry in entries
        ),
        lookup_table=tuple((entry.token, entry.canonical_name) for entry in entries),
    )
    _validate_command_demo_loop_contract(contract)
    return contract


@lru_cache(maxsize=None)
def command_mvp_loop_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoLoopContract:
    return command_demo_loop_contract(specs)


@lru_cache(maxsize=None)
def command_demo_transition_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoTransitionContract:
    loop_entries = {entry.token: entry for entry in command_demo_loop_contract(specs).entries}
    entries: list[CommandDemoTransitionEntry] = []
    for source_token, target_tokens in _COMMAND_DEMO_TRANSITIONS:
        for target_token in target_tokens:
            entry = loop_entries[target_token]
            entries.append(
                CommandDemoTransitionEntry(
                    source_token=source_token,
                    target_token=target_token,
                    canonical_name=entry.canonical_name,
                    flow_step=entry.flow_step,
                    argv=entry.argv,
                    description=entry.description,
                )
            )
    contract = CommandDemoTransitionContract(
        entries=tuple(entries),
        lookup_table=tuple(
            ((entry.source_token, entry.target_token), entry.canonical_name) for entry in entries
        ),
        invocation_table=tuple(
            ((entry.source_token, entry.target_token), entry.argv) for entry in entries
        ),
        targets_by_source=tuple(
            (
                source_token,
                tuple(entry.target_token for entry in entries if entry.source_token == source_token),
            )
            for source_token, _ in _COMMAND_DEMO_TRANSITIONS
        ),
    )
    _validate_command_demo_transition_contract(contract)
    return contract


@lru_cache(maxsize=None)
def command_mvp_transition_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoTransitionContract:
    return command_demo_transition_contract(specs)


@lru_cache(maxsize=None)
def command_demo_compatibility_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoCompatibilityContract:
    ordered_flow_steps = command_demo_flow_steps() if specs is COMMAND_SPECS else command_flow_steps(specs)
    entries: list[CommandDemoCompatibilityEntry] = []
    for token, canonical_token in _demo_compatibility_entries():
        resolved = _resolve_demo_loop_token(specs, canonical_token, ordered_flow_steps=ordered_flow_steps)
        entries.append(
            CommandDemoCompatibilityEntry(
                token=token,
                canonical_token=canonical_token,
                canonical_name=resolved.canonical_name,
                flow_step=resolved.flow_step,
                argv=resolved.argv,
                description=_demo_loop_description_for(canonical_token, resolved),
                kind="compatibility",
            )
        )
    contract = CommandDemoCompatibilityContract(
        tokens=tuple(entry.token for entry in entries),
        entries=tuple(entries),
        lookup_table=tuple((entry.token, entry.canonical_name) for entry in entries),
        invocation_table=tuple((entry.token, entry.argv) for entry in entries),
    )
    _validate_command_demo_compatibility_contract(contract)
    return contract


@lru_cache(maxsize=None)
def command_mvp_compatibility_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoCompatibilityContract:
    return command_demo_compatibility_contract(specs)


@lru_cache(maxsize=None)
def command_demo_workflow_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoWorkflowContract:
    loop_contract = command_demo_loop_contract(specs)
    transition_contract = command_demo_transition_contract(specs)
    compatibility_contract = command_demo_compatibility_contract(specs)
    transition_targets_by_token = dict(transition_contract.targets_by_source)
    compatibility_tokens_by_canonical_token: dict[str, list[str]] = {}
    for entry in compatibility_contract.entries:
        compatibility_tokens_by_canonical_token.setdefault(entry.canonical_token, []).append(entry.token)

    entries = tuple(
        CommandDemoWorkflowEntry(
            token=entry.token,
            canonical_name=entry.canonical_name,
            flow_step=entry.flow_step,
            argv=entry.argv,
            description=entry.description,
            next_tokens=transition_targets_by_token.get(entry.token, ()),
            compatibility_tokens=tuple(compatibility_tokens_by_canonical_token.get(entry.token, ())),
            preferred_surface_tokens=_preferred_surface_tokens_for_workflow_token(
                specs,
                entry.canonical_name,
                entry.token,
            ),
        )
        for entry in loop_contract.entries
    )
    contract = CommandDemoWorkflowContract(
        tokens=tuple(entry.token for entry in entries),
        entries=entries,
        flow_steps=command_demo_path_contract(specs).flow_steps,
        lookup_table=tuple((entry.token, entry.canonical_name) for entry in entries),
        invocation_table=tuple((entry.token, entry.argv) for entry in entries),
        transition_targets=tuple((entry.token, entry.next_tokens) for entry in entries),
        compatibility_lookup_table=tuple(
            (compatibility_token, entry.canonical_name)
            for entry in entries
            for compatibility_token in entry.compatibility_tokens
        ),
        compatibility_invocation_table=tuple(
            (compatibility_token, entry.argv)
            for entry in entries
            for compatibility_token in entry.compatibility_tokens
        ),
    )
    _validate_command_demo_workflow_contract(contract)
    return contract


@lru_cache(maxsize=None)
def command_mvp_workflow_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoWorkflowContract:
    return command_demo_workflow_contract(specs)


def command_demo_workflow_entry_for(
    specs: tuple[CommandSpec, ...],
    token: str,
) -> CommandDemoWorkflowEntry | None:
    normalized_token = _normalize_token(token)
    if not normalized_token:
        return None
    workflow_entries = {entry.token: entry for entry in command_demo_workflow_contract(specs).entries}
    if normalized_token in workflow_entries:
        return workflow_entries[normalized_token]
    canonical_token = _command_demo_transition_token_lookup(specs).get(normalized_token)
    if canonical_token is None:
        return None
    return workflow_entries.get(canonical_token)


def command_mvp_workflow_entry_for(
    specs: tuple[CommandSpec, ...],
    token: str,
) -> CommandDemoWorkflowEntry | None:
    return command_demo_workflow_entry_for(specs, token)


def _demo_workflow_branch_token(
    specs: tuple[CommandSpec, ...],
    decision_token: str,
) -> str:
    workflow_entry = command_demo_workflow_entry_for(specs, decision_token)
    if workflow_entry is None or workflow_entry.token not in {"apply-patch", "reject-patch"}:
        raise ValueError(
            "Command demo workflow invocation plan requires an apply/reject branch token"
        )
    return workflow_entry.token


def _demo_workflow_branch_tokens(
    specs: tuple[CommandSpec, ...],
    decision_token: str,
) -> tuple[str, ...]:
    branch_token = _demo_workflow_branch_token(specs, decision_token)
    return ("project-open", "retrieval", "patch-review", branch_token, "persist", "export-handoff")


def _trusted_surface_entry_for_workflow_token(
    specs: tuple[CommandSpec, ...],
    workflow_token: str,
) -> CommandTrustedSurfaceEntry:
    trusted_entries = {entry.token: entry for entry in command_demo_trusted_surface_catalog(specs)}
    workflow_entry = command_demo_workflow_entry_for(specs, workflow_token)
    if workflow_entry is None:
        raise ValueError(f"Command trusted workflow token is unresolved: {workflow_token}")

    for preferred_token in workflow_entry.preferred_surface_tokens:
        trusted_entry = trusted_entries.get(_normalize_token(preferred_token))
        if trusted_entry is not None:
            return trusted_entry

    trusted_entry = trusted_entries.get(workflow_entry.token)
    if trusted_entry is not None:
        return trusted_entry

    for entry in trusted_entries.values():
        if entry.canonical_token == workflow_entry.token:
            return entry

    raise ValueError(f"Command trusted workflow surface is unresolved: {workflow_token}")


def command_demo_workflow_invocation_plan(
    decision_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandDemoWorkflowInvocationEntry, ...]:
    """Return a full parser-ready demo loop for either the apply or reject branch."""
    workflow_entries = {entry.token: entry for entry in command_demo_workflow_contract(specs).entries}
    return tuple(
        CommandDemoWorkflowInvocationEntry(
            token=token,
            canonical_name=workflow_entries[token].canonical_name,
            flow_step=workflow_entries[token].flow_step,
            argv=workflow_entries[token].argv,
            description=workflow_entries[token].description,
        )
        for token in _demo_workflow_branch_tokens(specs, decision_token)
    )


def command_mvp_workflow_invocation_plan(
    decision_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandDemoWorkflowInvocationEntry, ...]:
    """Return the current MVP parser-ready loop for either the apply or reject branch."""
    return command_demo_workflow_invocation_plan(decision_token, specs)


def command_demo_workflow_trusted_invocation_plan(
    decision_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandTrustedSurfaceEntry, ...]:
    """Return the trusted demo verbs for the full apply/reject branch in workflow order."""
    return tuple(
        _trusted_surface_entry_for_workflow_token(specs, token)
        for token in _demo_workflow_branch_tokens(specs, decision_token)
    )


def command_mvp_workflow_trusted_invocation_plan(
    decision_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandTrustedSurfaceEntry, ...]:
    """Return the current MVP trusted command surface for the full apply/reject branch."""
    return command_demo_workflow_trusted_invocation_plan(decision_token, specs)


def command_demo_workflow_invocation_contract(
    decision_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoWorkflowInvocationContract:
    canonical_decision_token = _demo_workflow_branch_token(specs, decision_token)
    return CommandDemoWorkflowInvocationContract(
        decision_token=canonical_decision_token,
        entries=command_demo_workflow_invocation_plan(canonical_decision_token, specs),
    )


def command_mvp_workflow_invocation_contract(
    decision_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoWorkflowInvocationContract:
    return command_demo_workflow_invocation_contract(decision_token, specs)


def command_demo_path_entry_for(
    specs: tuple[CommandSpec, ...],
    flow_step: str,
) -> CommandDemoPathEntry | None:
    normalized_flow_step = _normalize_token(flow_step)
    if not normalized_flow_step:
        return None
    path_entries = {entry.flow_step: entry for entry in command_demo_path_contract(specs).entries}
    return path_entries.get(normalized_flow_step)


def command_mvp_path_entry_for(
    specs: tuple[CommandSpec, ...],
    flow_step: str,
) -> CommandDemoPathEntry | None:
    return command_demo_path_entry_for(specs, flow_step)


@lru_cache(maxsize=None)
def command_demo_next_action_contract(
    source_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoNextActionContract:
    normalized_source_token = _normalize_token(source_token)
    canonical_source_token = _command_demo_transition_token_lookup(specs).get(
        normalized_source_token,
        normalized_source_token,
    )
    workflow_entries = {entry.token: entry for entry in command_demo_workflow_contract(specs).entries}
    ordered_flow_steps = command_demo_flow_steps() if specs is COMMAND_SPECS else command_flow_steps(specs)
    entries = tuple(
        CommandDemoNextActionEntry(
            source_token=canonical_source_token,
            target_token=target_token,
            canonical_name=workflow_entries[target_token].canonical_name,
            flow_step=workflow_entries[target_token].flow_step,
            argv=workflow_entries[target_token].argv,
            description=workflow_entries[target_token].description,
            compatibility_tokens=workflow_entries[target_token].compatibility_tokens,
            preferred_surface_tokens=workflow_entries[target_token].preferred_surface_tokens,
            preferred_surface_invocations=tuple(
                (
                    preferred_token,
                    command_smoke_argv_for(specs, (preferred_token,), ordered_flow_steps),
                )
                for preferred_token in workflow_entries[target_token].preferred_surface_tokens
            ),
        )
        for target_token in command_demo_transition_targets_for(specs, source_token)
    )
    contract = CommandDemoNextActionContract(
        source_token=canonical_source_token,
        entries=entries,
        lookup_table=tuple((entry.target_token, entry.canonical_name) for entry in entries),
        invocation_table=tuple((entry.target_token, entry.argv) for entry in entries),
        preferred_invocation_table=tuple(
            invocation
            for entry in entries
            for invocation in entry.preferred_surface_invocations
        ),
        compatibility_lookup_table=tuple(
            (compatibility_token, entry.canonical_name)
            for entry in entries
            for compatibility_token in entry.compatibility_tokens
        ),
        compatibility_invocation_table=tuple(
            (compatibility_token, entry.argv)
            for entry in entries
            for compatibility_token in entry.compatibility_tokens
        ),
    )
    _validate_command_demo_next_action_contract(contract)
    return contract


@lru_cache(maxsize=None)
def command_mvp_next_action_contract(
    source_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandDemoNextActionContract:
    return command_demo_next_action_contract(source_token, specs)


def command_demo_next_action_preferred_invocation_table(
    source_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_next_action_contract(source_token, specs).preferred_invocation_table


def command_mvp_next_action_preferred_invocation_table(
    source_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_next_action_preferred_invocation_table(source_token, specs)


def command_demo_loop_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandDemoLoopEntry, ...]:
    return command_demo_loop_contract(specs).entries


def command_demo_transition_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandDemoTransitionEntry, ...]:
    return command_demo_transition_contract(specs).entries


def command_demo_compatibility_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandDemoCompatibilityEntry, ...]:
    return command_demo_compatibility_contract(specs).entries


def command_mvp_compatibility_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandDemoCompatibilityEntry, ...]:
    return command_demo_compatibility_catalog(specs)


def command_mvp_loop_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandDemoLoopEntry, ...]:
    return command_demo_loop_catalog(specs)


def command_mvp_transition_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandDemoTransitionEntry, ...]:
    return command_demo_transition_catalog(specs)


def command_demo_workflow_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandDemoWorkflowEntry, ...]:
    return command_demo_workflow_contract(specs).entries


def command_mvp_workflow_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandDemoWorkflowEntry, ...]:
    return command_demo_workflow_catalog(specs)


def command_demo_workflow_entry(token: str) -> CommandDemoWorkflowEntry | None:
    return command_demo_workflow_entry_for(COMMAND_SPECS, token)


def command_mvp_workflow_entry(token: str) -> CommandDemoWorkflowEntry | None:
    return command_demo_workflow_entry(token)


def command_demo_next_action_catalog(
    source_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandDemoNextActionEntry, ...]:
    return command_demo_next_action_contract(source_token, specs).entries


def command_mvp_next_action_catalog(
    source_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandDemoNextActionEntry, ...]:
    return command_demo_next_action_catalog(source_token, specs)


def command_demo_loop_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return command_demo_loop_contract(specs).tokens


def command_demo_compatibility_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return command_demo_compatibility_contract(specs).tokens


def command_mvp_compatibility_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return command_demo_compatibility_tokens(specs)


def command_mvp_loop_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return command_demo_loop_tokens(specs)


def command_demo_workflow_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return command_demo_workflow_contract(specs).tokens


def command_mvp_workflow_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    return command_demo_workflow_tokens(specs)


def command_demo_loop_invocation_plan(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandInvocationPlanEntry, ...]:
    return command_demo_loop_contract(specs).invocation_plan


def command_mvp_loop_invocation_plan(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandInvocationPlanEntry, ...]:
    return command_demo_loop_invocation_plan(specs)


def command_demo_transition_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[tuple[str, str], str], ...]:
    return command_demo_transition_contract(specs).lookup_table


def command_mvp_transition_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[tuple[str, str], str], ...]:
    return command_demo_transition_lookup_table(specs)


def command_demo_transition_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[tuple[str, str], tuple[str, ...]], ...]:
    return command_demo_transition_contract(specs).invocation_table


def command_mvp_transition_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[tuple[str, str], tuple[str, ...]], ...]:
    return command_demo_transition_invocation_table(specs)


def command_demo_transition_targets_by_source(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_transition_contract(specs).targets_by_source


def command_mvp_transition_targets_by_source(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_transition_targets_by_source(specs)


@lru_cache(maxsize=None)
def _command_demo_transition_token_lookup(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> dict[str, str]:
    lookup: dict[str, str] = {}
    loop_entries = command_demo_loop_contract(specs).entries
    loop_token_by_argv = {entry.argv: entry.token for entry in loop_entries if entry.argv}

    for entry in loop_entries:
        normalized_entry_token = _normalize_token(entry.token)
        if normalized_entry_token:
            lookup[normalized_entry_token] = entry.token
        normalized_primary_cli_token = _normalize_token(entry.argv[0]) if entry.argv else ""
        if normalized_primary_cli_token and entry.kind != "lookup":
            lookup.setdefault(normalized_primary_cli_token, entry.token)

    for entry in command_demo_path_contract(specs).entries:
        for token, argv in (
            *entry.surface_invocations,
            *entry.preferred_surface_invocations,
            *entry.parser_surface_invocations,
        ):
            normalized_surface_token = _normalize_token(token)
            canonical_token = loop_token_by_argv.get(argv)
            if normalized_surface_token and canonical_token:
                lookup.setdefault(normalized_surface_token, canonical_token)

    for canonical_token, fallback_tokens in _COMMAND_DEMO_LOOP_FALLBACK_TOKENS.items():
        for fallback_token in fallback_tokens:
            normalized_fallback_token = _normalize_token(fallback_token)
            if normalized_fallback_token:
                lookup.setdefault(normalized_fallback_token, canonical_token)

    for entry in command_demo_compatibility_contract(specs).entries:
        normalized_compatibility_token = _normalize_token(entry.token)
        if normalized_compatibility_token:
            lookup[normalized_compatibility_token] = entry.canonical_token
    for variant_token, canonical_token in _COMMAND_DEMO_COMPATIBILITY_VARIANTS.items():
        normalized_variant_token = _normalize_token(variant_token)
        if normalized_variant_token:
            lookup.setdefault(normalized_variant_token, canonical_token)

    return lookup


def command_demo_transition_targets_for(
    specs: tuple[CommandSpec, ...],
    source_token: str,
) -> tuple[str, ...]:
    normalized_source_token = _normalize_token(source_token)
    if not normalized_source_token:
        return ()
    canonical_source_token = _command_demo_transition_token_lookup(specs).get(normalized_source_token)
    if canonical_source_token is None:
        return ()
    return dict(command_demo_transition_targets_by_source(specs)).get(canonical_source_token, ())


def command_mvp_transition_targets_for(
    specs: tuple[CommandSpec, ...],
    source_token: str,
) -> tuple[str, ...]:
    return command_demo_transition_targets_for(specs, source_token)


def command_demo_transition_argv_for(
    specs: tuple[CommandSpec, ...],
    source_token: str,
    target_token: str,
) -> tuple[str, ...]:
    token_lookup = _command_demo_transition_token_lookup(specs)
    canonical_source_token = token_lookup.get(_normalize_token(source_token))
    canonical_target_token = token_lookup.get(_normalize_token(target_token))
    if canonical_source_token is None or canonical_target_token is None:
        return ()
    return dict(command_demo_transition_invocation_table(specs)).get(
        (canonical_source_token, canonical_target_token),
        (),
    )


def command_mvp_transition_argv_for(
    specs: tuple[CommandSpec, ...],
    source_token: str,
    target_token: str,
) -> tuple[str, ...]:
    return command_demo_transition_argv_for(specs, source_token, target_token)


def command_demo_transition_targets(source_token: str) -> tuple[str, ...]:
    return command_demo_transition_targets_for(COMMAND_SPECS, source_token)


def command_mvp_transition_targets(source_token: str) -> tuple[str, ...]:
    return command_demo_transition_targets(source_token)


def command_demo_transition_argv(source_token: str, target_token: str) -> tuple[str, ...]:
    return command_demo_transition_argv_for(COMMAND_SPECS, source_token, target_token)


def command_mvp_transition_argv(source_token: str, target_token: str) -> tuple[str, ...]:
    return command_demo_transition_argv(source_token, target_token)


def command_demo_trusted_surface_entry(token: str) -> CommandTrustedSurfaceEntry | None:
    return command_demo_trusted_surface_entry_for(COMMAND_SPECS, token)


def command_mvp_trusted_surface_entry(token: str) -> CommandTrustedSurfaceEntry | None:
    return command_mvp_trusted_surface_entry_for(COMMAND_SPECS, token)


def command_demo_workflow_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_workflow_contract(specs).lookup_table


def command_mvp_workflow_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_workflow_lookup_table(specs)


def command_demo_workflow_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_workflow_contract(specs).invocation_table


def command_mvp_workflow_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_workflow_invocation_table(specs)


def command_demo_workflow_transition_targets(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_workflow_contract(specs).transition_targets


def command_mvp_workflow_transition_targets(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_workflow_transition_targets(specs)


def command_demo_next_action_lookup_table(
    source_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_next_action_contract(source_token, specs).lookup_table


def command_mvp_next_action_lookup_table(
    source_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_next_action_lookup_table(source_token, specs)


def command_demo_next_action_invocation_table(
    source_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_next_action_contract(source_token, specs).invocation_table


def command_mvp_next_action_invocation_table(
    source_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_next_action_invocation_table(source_token, specs)


def command_demo_next_action_compatibility_lookup_table(
    source_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_next_action_contract(source_token, specs).compatibility_lookup_table


def command_mvp_next_action_compatibility_lookup_table(
    source_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_next_action_compatibility_lookup_table(source_token, specs)


def command_demo_next_action_compatibility_invocation_table(
    source_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_next_action_contract(source_token, specs).compatibility_invocation_table


def command_mvp_next_action_compatibility_invocation_table(
    source_token: str,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return command_demo_next_action_compatibility_invocation_table(source_token, specs)


def command_demo_workflow_compatibility_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_workflow_contract(specs).compatibility_lookup_table


def command_mvp_workflow_compatibility_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_workflow_compatibility_lookup_table(specs)


def command_demo_workflow_compatibility_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Flatten demo-workflow compatibility verbs into parser-ready argv."""
    return command_demo_workflow_contract(specs).compatibility_invocation_table


def command_mvp_workflow_compatibility_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Flatten current MVP compatibility verbs into parser-ready argv."""
    return command_demo_workflow_compatibility_invocation_table(specs)


def command_demo_loop_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_loop_contract(specs).lookup_table


def command_demo_compatibility_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_compatibility_contract(specs).lookup_table


def command_mvp_compatibility_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_compatibility_lookup_table(specs)


def command_mvp_loop_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    return command_demo_loop_lookup_table(specs)


def command_demo_loop_surface_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Flatten the canonical review/apply-or-reject/persist/export loop to parser-ready argv."""
    return tuple((entry.token, entry.argv) for entry in command_demo_loop_contract(specs).entries)


def command_demo_compatibility_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Flatten legacy demo-loop verbs into parser-ready argv for smoke checks."""
    return command_demo_compatibility_contract(specs).invocation_table


def command_mvp_compatibility_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Flatten current MVP legacy demo-loop verbs into parser-ready argv for smoke checks."""
    return command_demo_compatibility_invocation_table(specs)


def _ordered_token_invocation_union(
    *tables: tuple[tuple[str, tuple[str, ...]], ...],
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    ordered_entries: list[tuple[str, tuple[str, ...]]] = []
    seen_tokens: set[str] = set()
    for table in tables:
        for token, argv in table:
            normalized_token = _normalize_token(token)
            if not normalized_token or normalized_token in seen_tokens:
                continue
            seen_tokens.add(normalized_token)
            ordered_entries.append((normalized_token, argv))
    return tuple(ordered_entries)


def _trusted_surface_source_by_token(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> dict[str, str]:
    source_by_token: dict[str, str] = {}
    for source, table in (
        ("preferred", command_demo_preferred_surface_invocation_table(specs)),
        ("surface", command_demo_surface_invocation_table(specs)),
        ("compatibility", command_demo_compatibility_invocation_table(specs)),
    ):
        for token, _ in table:
            normalized_token = _normalize_token(token)
            if normalized_token:
                source_by_token.setdefault(normalized_token, source)
    for token in _COMMAND_DEMO_COMPATIBILITY_VARIANTS:
        normalized_token = _normalize_token(token)
        if normalized_token:
            source_by_token.setdefault(normalized_token, "compatibility-variant")
    return source_by_token


def _validate_command_trusted_surface_contract(
    contract: CommandTrustedSurfaceContract,
    *,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> None:
    if contract.tokens != tuple(entry.token for entry in contract.entries):
        raise ValueError("Command trusted surface tokens are inconsistent")
    if contract.lookup_table != tuple((entry.token, entry.canonical_name) for entry in contract.entries):
        raise ValueError("Command trusted surface lookup table is inconsistent")
    if contract.invocation_table != tuple((entry.token, entry.argv) for entry in contract.entries):
        raise ValueError("Command trusted surface invocation table is inconsistent")
    allowed_sources = {"preferred", "surface", "compatibility", "compatibility-variant"}
    workflow_by_token = {entry.token: entry for entry in command_demo_workflow_contract(specs).entries}
    for entry in contract.entries:
        if not entry.argv:
            raise ValueError(f"Command trusted surface entry is missing argv: {entry.token}")
        if entry.source not in allowed_sources:
            raise ValueError(f"Command trusted surface source is inconsistent: {entry.token}")
        if entry.token != _normalize_token(entry.token):
            raise ValueError(f"Command trusted surface token is inconsistent: {entry.token}")
        if entry.canonical_token != _normalize_token(entry.canonical_token):
            raise ValueError(
                f"Command trusted surface canonical token is inconsistent: {entry.token}"
            )
        if entry.flow_step != _normalize_token(entry.flow_step):
            raise ValueError(f"Command trusted surface flow step is inconsistent: {entry.token}")
        canonical_workflow_entry = workflow_by_token.get(entry.canonical_token)
        if canonical_workflow_entry is None:
            raise ValueError(f"Command trusted surface canonical token is unresolved: {entry.token}")
        if entry.canonical_name != canonical_workflow_entry.canonical_name:
            raise ValueError(f"Command trusted surface canonical name is inconsistent: {entry.token}")
        if entry.flow_step != canonical_workflow_entry.flow_step:
            raise ValueError(f"Command trusted surface canonical flow step is inconsistent: {entry.token}")
        if entry.description != canonical_workflow_entry.description:
            raise ValueError(f"Command trusted surface description is inconsistent: {entry.token}")
        if entry.next_tokens != canonical_workflow_entry.next_tokens:
            raise ValueError(f"Command trusted surface next tokens are inconsistent: {entry.token}")
        if entry.compatibility_tokens != canonical_workflow_entry.compatibility_tokens:
            raise ValueError(f"Command trusted surface compatibility tokens are inconsistent: {entry.token}")
        if entry.preferred_surface_tokens != canonical_workflow_entry.preferred_surface_tokens:
            raise ValueError(
                f"Command trusted surface preferred surface tokens are inconsistent: {entry.token}"
            )


def command_demo_trusted_surface_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return the preferred, parser, and legacy demo verbs as one deterministic smoke surface."""
    compatibility_invocations = command_demo_compatibility_invocation_table(specs)
    known_compatibility_tokens = {_normalize_token(token) for token, _ in compatibility_invocations}
    compatibility_variants = tuple(
        (
            variant_token,
            resolved.argv,
        )
        for variant_token, canonical_token in _COMMAND_DEMO_COMPATIBILITY_VARIANTS.items()
        for resolved in (
            command_demo_workflow_entry_for(specs, canonical_token),
        )
        if resolved is not None and _normalize_token(variant_token) not in known_compatibility_tokens
    )
    return _ordered_token_invocation_union(
        command_demo_preferred_surface_invocation_table(specs),
        command_demo_surface_invocation_table(specs),
        compatibility_invocations,
        compatibility_variants,
    )


def command_mvp_trusted_surface_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return the current MVP trusted smoke surface, including compatibility verbs."""
    return command_demo_trusted_surface_invocation_table(specs)


def command_demo_trusted_surface_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    """List the deterministic token order for the trusted demo command surface."""
    return tuple(token for token, _ in command_demo_trusted_surface_invocation_table(specs))


def command_mvp_trusted_surface_tokens(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[str, ...]:
    """List the deterministic token order for the current MVP trusted command surface."""
    return command_demo_trusted_surface_tokens(specs)


def command_demo_trusted_surface_flow_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    """Map each trusted demo token to its canonical flow step."""
    return tuple((entry.token, entry.flow_step) for entry in command_demo_trusted_surface_contract(specs).entries)


def command_mvp_trusted_surface_flow_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    """Map each trusted MVP token to its canonical flow step."""
    return command_demo_trusted_surface_flow_lookup_table(specs)


@lru_cache(maxsize=None)
def command_demo_trusted_surface_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandTrustedSurfaceContract:
    invocation_table = command_demo_trusted_surface_invocation_table(specs)
    source_by_token = _trusted_surface_source_by_token(specs)
    workflow_by_token = {entry.token: entry for entry in command_demo_workflow_catalog(specs)}
    entries: list[CommandTrustedSurfaceEntry] = []
    for token, argv in invocation_table:
        workflow_entry = command_demo_workflow_entry_for(specs, token)
        if workflow_entry is None:
            raise ValueError(f"Command trusted surface token is unresolved: {token}")
        canonical_workflow_entry = workflow_by_token.get(workflow_entry.token)
        if canonical_workflow_entry is None:
            raise ValueError(f"Command trusted surface canonical token is unresolved: {token}")
        entries.append(
            CommandTrustedSurfaceEntry(
                token=token,
                canonical_token=workflow_entry.token,
                canonical_name=workflow_entry.canonical_name,
                flow_step=workflow_entry.flow_step,
                argv=argv,
                description=workflow_entry.description,
                next_tokens=canonical_workflow_entry.next_tokens,
                compatibility_tokens=canonical_workflow_entry.compatibility_tokens,
                preferred_surface_tokens=canonical_workflow_entry.preferred_surface_tokens,
                source=source_by_token.get(token, "surface"),
            )
        )
    contract = CommandTrustedSurfaceContract(
        tokens=tuple(entry.token for entry in entries),
        entries=tuple(entries),
        lookup_table=tuple((entry.token, entry.canonical_name) for entry in entries),
        invocation_table=tuple((entry.token, entry.argv) for entry in entries),
    )
    _validate_command_trusted_surface_contract(contract, specs=specs)
    return contract


@lru_cache(maxsize=None)
def command_mvp_trusted_surface_contract(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> CommandTrustedSurfaceContract:
    return command_demo_trusted_surface_contract(specs)


def command_demo_trusted_surface_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandTrustedSurfaceEntry, ...]:
    return command_demo_trusted_surface_contract(specs).entries


def command_mvp_trusted_surface_catalog(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[CommandTrustedSurfaceEntry, ...]:
    return command_demo_trusted_surface_catalog(specs)


def command_demo_trusted_surface_entry_for(
    specs: tuple[CommandSpec, ...],
    token: str,
) -> CommandTrustedSurfaceEntry | None:
    normalized_token = _normalize_token(token)
    if not normalized_token:
        return None
    trusted_entries = {entry.token: entry for entry in command_demo_trusted_surface_catalog(specs)}
    return trusted_entries.get(normalized_token)


def command_mvp_trusted_surface_entry_for(
    specs: tuple[CommandSpec, ...],
    token: str,
) -> CommandTrustedSurfaceEntry | None:
    return command_demo_trusted_surface_entry_for(specs, token)


def command_mvp_loop_surface_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Flatten the current MVP review/apply-or-reject/persist/export loop to parser-ready argv."""
    return command_demo_loop_surface_invocation_table(specs)


def command_demo_surface_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Flatten the demo-path surface into parser-ready invocations for smoke checks."""
    return tuple(
        invocation
        for entry in command_demo_path_contract(specs).entries
        for invocation in entry.surface_invocations
    )


def command_demo_preferred_surface_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Flatten the preferred demo-path verbs into parser-ready invocations."""
    return tuple(
        invocation
        for entry in command_demo_path_contract(specs).entries
        for invocation in entry.preferred_surface_invocations
    )


def command_mvp_surface_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Flatten the current MVP command surface into parser-ready invocations."""
    return command_demo_surface_invocation_table(specs)


def command_mvp_preferred_surface_invocation_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Flatten the current MVP preferred verbs into parser-ready invocations."""
    return command_demo_preferred_surface_invocation_table(specs)


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


@lru_cache(maxsize=None)
def command_surface_tokens_for(
    specs: tuple[CommandSpec, ...],
    name: str,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    validate_command_catalog(specs)
    spec = command_spec_for(specs, name)
    if spec is None:
        return ()

    ordered_flow_steps = _resolve_contract_flow_steps(specs, flow_steps)
    route_entry = next(
        (
            entry
            for entry in command_flow_route_catalog(specs=specs, flow_steps=ordered_flow_steps)
            if entry.name == spec.name
        ),
        None,
    )
    if route_entry is not None:
        return route_entry.surface_tokens
    if flow_steps is not None:
        return ()
    return _flow_surface_tokens(*_lookup_resolution_tokens(spec), spec.flow_step)


def command_surface_tokens(
    name: str,
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    return command_surface_tokens_for(COMMAND_SPECS, name, flow_steps)


def command_spec(name: str) -> CommandSpec | None:
    return command_spec_for(COMMAND_SPECS, name)


def command_demo_path_entry(flow_step: str) -> CommandDemoPathEntry | None:
    return command_demo_path_entry_for(COMMAND_SPECS, flow_step)


def command_mvp_path_entry(flow_step: str) -> CommandDemoPathEntry | None:
    return command_mvp_path_entry_for(COMMAND_SPECS, flow_step)


def command_aliases(name: str) -> tuple[str, ...]:
    return command_aliases_for(COMMAND_SPECS, name)


def canonical_command(name: str) -> str:
    if _uses_demo_compatibility_surface(name):
        return canonical_command_for(COMMAND_SPECS, _normalize_demo_compatibility_token(name))
    return canonical_command_for(COMMAND_SPECS, name)


def canonical_demo_command(name: str) -> str:
    normalized_name = _normalize_token(name)
    if not normalized_name:
        return normalized_name
    if _uses_demo_compatibility_surface(normalized_name):
        normalized_name = _normalize_demo_compatibility_token(normalized_name)
    workflow_entry = command_demo_workflow_entry(normalized_name)
    if workflow_entry is not None:
        return workflow_entry.token
    transition_token = _command_demo_transition_token_lookup(COMMAND_SPECS).get(normalized_name)
    if transition_token is not None:
        return transition_token
    return canonical_command(normalized_name)


def canonical_mvp_command(name: str) -> str:
    return canonical_demo_command(name)


def canonical_demo_command_argv(argv: tuple[str, ...] | list[str]) -> str:
    """Map a full demo-path invocation back to its stable workflow token."""
    raw_argv = tuple(argv)
    if not raw_argv:
        return ""

    resolved = command_demo_resolve_argv(raw_argv)
    workflow_token_by_argv = {
        entry.argv: entry.token
        for entry in command_demo_workflow_contract(COMMAND_SPECS).entries
        if entry.argv
    }
    workflow_token = workflow_token_by_argv.get(resolved.argv)
    if workflow_token is not None:
        return workflow_token

    terminal_token = _canonical_demo_terminal_argv_token(resolved)
    if terminal_token:
        return terminal_token

    if resolved.matched and resolved.flow_step:
        normalized_flow_step = _normalize_token(resolved.flow_step)
        if normalized_flow_step in _COMMAND_DEMO_LOOP_TOKENS:
            return normalized_flow_step

    return canonical_demo_command(raw_argv[0])


def canonical_mvp_command_argv(argv: tuple[str, ...] | list[str]) -> str:
    """Map a full MVP invocation back to its stable workflow token."""
    return canonical_demo_command_argv(argv)


def command_cli_shim_primary_token(
    token: str,
    flow_steps: tuple[str, ...] | None = None,
) -> str:
    if flow_steps is None and _uses_demo_compatibility_surface(token):
        return command_demo_cli_shim_primary_token(token)
    return command_cli_shim_primary_token_for(COMMAND_SPECS, token, flow_steps)


def command_cli_shim_argv(
    argv: tuple[str, ...] | list[str],
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    raw_argv = tuple(argv)
    if (
        flow_steps is None
        and raw_argv
        and not raw_argv[0].lstrip().startswith("-")
        and _uses_demo_compatibility_surface(raw_argv[0])
    ):
        return command_demo_cli_shim_argv(raw_argv)
    return command_cli_shim_argv_for(COMMAND_SPECS, argv, flow_steps)


def command_cli_entry_argv(
    argv: tuple[str, ...] | list[str],
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    raw_argv = tuple(argv)
    if (
        flow_steps is None
        and raw_argv
        and not raw_argv[0].lstrip().startswith("-")
        and _uses_demo_compatibility_surface(raw_argv[0])
    ):
        return command_demo_cli_entry_argv(raw_argv)
    return command_cli_entry_argv_for(COMMAND_SPECS, argv, flow_steps)


def command_demo_cli_entry_argv(
    argv: tuple[str, ...] | list[str],
) -> tuple[str, ...]:
    """Normalize argv against the canonical demo-path command surface."""
    resolved = command_demo_resolve_argv(argv)
    return resolved.argv


def command_mvp_cli_entry_argv(
    argv: tuple[str, ...] | list[str],
) -> tuple[str, ...]:
    """Normalize argv against the current MVP command surface."""
    return command_demo_cli_entry_argv(argv)


def command_demo_cli_shim_primary_token(token: str) -> str:
    """Resolve a demo-path surface token to its primary CLI entrypoint."""
    return command_cli_shim_primary_token_for(
        COMMAND_SPECS,
        _normalize_demo_compatibility_token(token),
        command_demo_flow_steps(),
    )


def command_mvp_cli_shim_primary_token(token: str) -> str:
    """Resolve an MVP surface token to its primary CLI entrypoint."""
    return command_demo_cli_shim_primary_token(token)


def command_demo_cli_shim_argv(
    argv: tuple[str, ...] | list[str],
) -> tuple[str, ...]:
    """Rewrite demo-path surface argv to the parser-facing command surface."""
    return command_cli_shim_argv_for(
        COMMAND_SPECS,
        _normalize_demo_compatibility_argv(argv),
        command_demo_flow_steps(),
    )


def command_mvp_cli_shim_argv(
    argv: tuple[str, ...] | list[str],
) -> tuple[str, ...]:
    """Rewrite MVP surface argv to the parser-facing command surface."""
    return command_demo_cli_shim_argv(argv)


def command_smoke_argv_for(
    specs: tuple[CommandSpec, ...],
    argv: tuple[str, ...] | list[str],
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    raw_argv = tuple(argv)
    ordered_flow_steps = _resolve_parser_surface_flow_steps(specs, flow_steps)
    smoke_plan = command_smoke_invocation_plan(specs, ordered_flow_steps)
    default_argv = smoke_plan[0].argv if smoke_plan else ()
    if not raw_argv:
        return default_argv
    if raw_argv[0].lstrip().startswith("-"):
        return (
            _merge_shim_argv(
                default_argv,
                raw_argv,
                pinned_options=_default_route_pinned_options(specs, ordered_flow_steps),
            )
            if default_argv
            else raw_argv
        )

    resolved = command_resolve_for(specs, raw_argv[0], ordered_flow_steps)
    if not resolved.matched:
        return raw_argv
    return _resolved_parser_ready_argv(specs, resolved, raw_argv[1:])


def command_smoke_argv(
    argv: tuple[str, ...] | list[str],
    flow_steps: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    return command_smoke_argv_for(COMMAND_SPECS, argv, flow_steps)


def command_demo_smoke_argv(
    argv: tuple[str, ...] | list[str],
) -> tuple[str, ...]:
    """Return a parser-smoke invocation for the canonical demo-path surface."""
    return command_smoke_argv_for(
        COMMAND_SPECS,
        _normalize_demo_compatibility_argv(argv),
        command_demo_flow_steps(),
    )


def command_mvp_smoke_argv(
    argv: tuple[str, ...] | list[str],
) -> tuple[str, ...]:
    """Return a parser-smoke invocation for the current MVP surface."""
    return command_demo_smoke_argv(argv)


def _resolved_smoke_argv_for(
    specs: tuple[CommandSpec, ...],
    canonical_name: str,
) -> tuple[str, ...]:
    if not canonical_name:
        return ()
    return command_smoke_entry_argv_for(specs, canonical_name)


def _resolved_single_token_argv(
    specs: tuple[CommandSpec, ...],
    canonical_name: str,
    fallback_argv: tuple[str, ...],
) -> tuple[str, ...]:
    if len(fallback_argv) > 1:
        return fallback_argv
    smoke_argv = _resolved_smoke_argv_for(specs, canonical_name)
    if len(smoke_argv) > 1:
        return smoke_argv
    return fallback_argv


def _resolved_parser_ready_argv(
    specs: tuple[CommandSpec, ...],
    resolved: ResolvedCommand,
    explicit_args: tuple[str, ...],
) -> tuple[str, ...]:
    if not resolved.matched:
        return explicit_args
    if not explicit_args:
        return resolved.smoke_argv or resolved.argv
    if len(resolved.smoke_argv) <= 1:
        return command_cli_shim_argv_for(specs, (resolved.token, *explicit_args), (resolved.flow_step,))
    return _merge_shim_argv(
        resolved.smoke_argv,
        explicit_args,
        pinned_options=_shim_pinned_options_lookup(specs).get(resolved.normalized_token, frozenset()),
    )


def _resolve_demo_fallback_argv(
    specs: tuple[CommandSpec, ...],
    argv: tuple[str, ...],
    ordered_flow_steps: tuple[str, ...],
) -> tuple[str, ...]:
    if not argv or not _uses_demo_compatibility_flow(ordered_flow_steps):
        return ()

    demo_token = _normalize_demo_compatibility_token(argv[0])
    if demo_token not in _COMMAND_DEMO_LOOP_TOKENS:
        return ()

    try:
        resolved = _resolve_demo_loop_token(
            specs,
            demo_token,
            ordered_flow_steps=ordered_flow_steps,
        )
    except ValueError:
        return ()
    return _resolved_parser_ready_argv(specs, resolved, argv[1:])


def _prefer_primary_smoke_argv(
    spec: CommandSpec | None,
    *,
    normalized_token: str,
    resolved_argv: tuple[str, ...],
    smoke_argv: tuple[str, ...],
) -> tuple[str, ...]:
    if spec is None or not spec.shim_argv:
        return resolved_argv
    if normalized_token != _parser_ready_argv(spec)[0]:
        return resolved_argv
    if len(resolved_argv) != 1 or len(smoke_argv) <= 1:
        return resolved_argv
    # Keep shim-backed canonical commands deterministic when the primary token
    # would otherwise resolve to a generic parser entrypoint with missing defaults.
    return smoke_argv


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
            smoke_argv=(),
            cli_tokens=(),
            lookup_tokens=(),
            surface_tokens=(),
            description="",
            kind="empty",
            matched=False,
        )

    ordered_flow_steps = _resolve_parser_surface_flow_steps(specs, flow_steps)
    route_catalog = command_flow_route_catalog(flow_steps=ordered_flow_steps, specs=specs)
    shim_invocations = dict(command_cli_shim_invocation_table(specs, ordered_flow_steps))
    for route_entry in route_catalog:
        if normalized_token not in route_entry.surface_tokens:
            continue
        resolved_argv = shim_invocations.get(
            normalized_token,
            (route_entry.primary_cli_token,),
        )
        spec = command_spec_for(specs, route_entry.name)
        smoke_argv = _resolved_single_token_argv(
            specs,
            route_entry.name,
            resolved_argv,
        )
        resolved_argv = _prefer_primary_smoke_argv(
            spec,
            normalized_token=normalized_token,
            resolved_argv=resolved_argv,
            smoke_argv=smoke_argv,
        )
        return ResolvedCommand(
            token=token,
            normalized_token=normalized_token,
            canonical_name=route_entry.name,
            flow_step=route_entry.flow_step,
            primary_cli_token=route_entry.primary_cli_token,
            argv=resolved_argv,
            smoke_argv=smoke_argv,
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
        smoke_argv=(),
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
    if flow_steps is None and _uses_demo_compatibility_surface(token):
        return command_demo_resolve(token)
    return command_resolve_for(COMMAND_SPECS, token, flow_steps)


def _prefer_demo_flow_smoke_resolution(
    resolved: ResolvedCommand,
    *,
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
    raw_argv: tuple[str, ...] = (),
) -> ResolvedCommand:
    if not resolved.matched or not raw_argv:
        return resolved
    if len(resolved.smoke_argv) <= 1:
        return resolved
    explicit_args = raw_argv[1:]
    if explicit_args:
        parser_ready_argv = _merge_shim_argv(
            resolved.smoke_argv,
            explicit_args,
            pinned_options=_shim_pinned_options_lookup(specs).get(resolved.normalized_token, frozenset()),
        )
    else:
        parser_ready_argv = resolved.smoke_argv
    return ResolvedCommand(
        token=resolved.token,
        normalized_token=resolved.normalized_token,
        canonical_name=resolved.canonical_name,
        flow_step=resolved.flow_step,
        primary_cli_token=resolved.primary_cli_token,
        argv=parser_ready_argv,
        smoke_argv=resolved.smoke_argv,
        cli_tokens=resolved.cli_tokens,
        lookup_tokens=resolved.lookup_tokens,
        surface_tokens=resolved.surface_tokens,
        description=resolved.description,
        kind=resolved.kind,
        matched=resolved.matched,
    )


def _preserve_requested_token(
    resolved: ResolvedCommand,
    token: str,
) -> ResolvedCommand:
    normalized_token = _normalize_token(token)
    if not token or (
        resolved.token == token
        and resolved.normalized_token == normalized_token
    ):
        return resolved
    return replace(
        resolved,
        token=token,
        normalized_token=normalized_token,
    )


def command_demo_resolve(token: str) -> ResolvedCommand:
    """Resolve a token against the canonical demo-path command surface."""
    normalized_token = _normalize_demo_compatibility_token(token)
    return _preserve_requested_token(
        _align_demo_flow_step(
            _prefer_demo_flow_smoke_resolution(
                command_resolve_for(COMMAND_SPECS, normalized_token, command_demo_flow_steps()),
                specs=COMMAND_SPECS,
                raw_argv=(normalized_token,),
            ),
            normalized_token,
        ),
        token,
    )


def command_mvp_resolve(token: str) -> ResolvedCommand:
    """Resolve a token against the current MVP command surface."""
    return command_demo_resolve(token)


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
            smoke_argv=(),
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
            smoke_argv=(),
            cli_tokens=(),
            lookup_tokens=(),
            surface_tokens=(),
            description="",
            kind="flag",
            matched=False,
        )

    ordered_flow_steps = _resolve_parser_surface_flow_steps(specs, flow_steps)
    resolved = command_resolve_for(specs, raw_argv[0], ordered_flow_steps)
    if not resolved.matched:
        fallback_argv = _resolve_demo_fallback_argv(specs, raw_argv, ordered_flow_steps)
        if fallback_argv:
            normalized_token = _normalize_demo_compatibility_token(raw_argv[0])
            try:
                fallback_resolved = _preserve_requested_token(
                    _resolve_demo_loop_token(
                        specs,
                        normalized_token,
                        ordered_flow_steps=ordered_flow_steps,
                    ),
                    raw_argv[0],
                )
            except ValueError:
                fallback_resolved = resolved
            return ResolvedCommand(
                token=fallback_resolved.token,
                normalized_token=fallback_resolved.normalized_token,
                canonical_name=fallback_resolved.canonical_name,
                flow_step=fallback_resolved.flow_step,
                primary_cli_token=fallback_resolved.primary_cli_token,
                argv=fallback_argv,
                smoke_argv=fallback_resolved.smoke_argv,
                cli_tokens=fallback_resolved.cli_tokens,
                lookup_tokens=fallback_resolved.lookup_tokens,
                surface_tokens=fallback_resolved.surface_tokens,
                description=fallback_resolved.description,
                kind=fallback_resolved.kind,
                matched=True,
            )
        return ResolvedCommand(
            token=resolved.token,
            normalized_token=resolved.normalized_token,
            canonical_name=resolved.canonical_name,
            flow_step=resolved.flow_step,
            primary_cli_token=resolved.primary_cli_token,
            argv=raw_argv,
            smoke_argv=resolved.smoke_argv,
            cli_tokens=resolved.cli_tokens,
            lookup_tokens=resolved.lookup_tokens,
            surface_tokens=resolved.surface_tokens,
            description=resolved.description,
            kind=resolved.kind,
            matched=False,
        )

    resolved_argv = command_cli_shim_argv_for(specs, raw_argv, ordered_flow_steps)
    spec = command_spec_for(specs, resolved.canonical_name)
    if len(raw_argv) == 1:
        resolved_argv = _prefer_primary_smoke_argv(
            spec,
            normalized_token=resolved.normalized_token,
            resolved_argv=resolved_argv,
            smoke_argv=resolved.smoke_argv,
        )
    if (
        len(raw_argv) > 1
        and resolved.kind == "primary"
        and spec is not None
        and spec.shim_argv
        and len(resolved.smoke_argv) > 1
    ):
        # Keep direct canonical invocations aligned with alias-backed parser defaults
        # when the command surface uses shimmed demo-path routes.
        resolved_argv = _merge_shim_argv(
            resolved.smoke_argv,
            raw_argv[1:],
            pinned_options=_shim_pinned_options_lookup(specs).get(resolved.normalized_token, frozenset()),
        )

    return ResolvedCommand(
        token=resolved.token,
        normalized_token=resolved.normalized_token,
        canonical_name=resolved.canonical_name,
        flow_step=resolved.flow_step,
        primary_cli_token=resolved.primary_cli_token,
        argv=resolved_argv,
        smoke_argv=resolved.smoke_argv,
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
    raw_argv = tuple(argv)
    if (
        flow_steps is None
        and raw_argv
        and not raw_argv[0].lstrip().startswith("-")
        and _uses_demo_compatibility_surface(raw_argv[0])
    ):
        return command_demo_resolve_argv(raw_argv)
    return command_resolve_argv_for(COMMAND_SPECS, argv, flow_steps)


def command_demo_resolve_argv(
    argv: tuple[str, ...] | list[str],
) -> ResolvedCommand:
    """Resolve argv against the canonical demo-path command surface."""
    requested_argv = tuple(argv)
    raw_argv = _normalize_demo_compatibility_argv(requested_argv)
    resolved = _prefer_demo_flow_smoke_resolution(
        command_resolve_argv_for(COMMAND_SPECS, raw_argv, command_demo_flow_steps()),
        specs=COMMAND_SPECS,
        raw_argv=raw_argv,
    )
    resolved = _align_demo_flow_step(
        resolved,
        _demo_alignment_token_for_argv(resolved, raw_argv),
    )
    if not requested_argv:
        return resolved
    return _preserve_requested_token(resolved, requested_argv[0])


def command_mvp_resolve_argv(
    argv: tuple[str, ...] | list[str],
) -> ResolvedCommand:
    """Resolve argv against the current MVP command surface."""
    return command_demo_resolve_argv(argv)
