from __future__ import annotations

import re
import shlex
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class CommandSpec:
    name: str
    aliases: tuple[str, ...] = ()
    description: str = ""
    flow_step: str = "general"
    cli_tokens: tuple[str, ...] = ()


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


@dataclass(frozen=True)
class CommandFlowRouteContract:
    entries: tuple[CommandFlowRouteEntry, ...]


@dataclass(frozen=True)
class CommandSmokeStep:
    flow_step: str
    name: str
    cli_token: str
    argv: tuple[str, ...]
    description: str

    @property
    def command_line(self) -> str:
        return shlex.join(self.argv)


@dataclass(frozen=True)
class CommandSmokeContract:
    steps: tuple[CommandSmokeStep, ...]
    command_tokens: tuple[str, ...]
    argv: tuple[tuple[str, ...], ...]
    lookup_table: tuple[tuple[str, str], ...]
    command_lines: tuple[str, ...] = ()
    route_summary: tuple[tuple[str, str, tuple[str, ...]], ...] = ()
    lookup_surface: tuple[tuple[str, str], ...] = ()
    flow_surface_tokens: tuple[tuple[str, ...], ...] = ()


@dataclass(frozen=True)
class CommandDemoPathStep:
    flow_step: str
    name: str
    cli_token: str
    argv: tuple[str, ...]
    command_line: str
    operator_checkpoint: str
    engine_handoff: str
    description: str
    engine_actions: tuple[str, ...] = ()


@dataclass(frozen=True)
class CommandDemoPathContract:
    steps: tuple[CommandDemoPathStep, ...]
    flow_steps: tuple[str, ...]
    names: tuple[str, ...]
    command_tokens: tuple[str, ...]
    command_lines: tuple[str, ...]
    engine_handoffs: tuple[str, ...]
    engine_actions: tuple[tuple[str, ...], ...] = ()


DEMO_PATH_ENGINE_HANDOFFS: dict[str, str] = {
    "project-open": "engine project bootstrap/open",
    "retrieval": "engine retrieval context selection",
    "patch-review": "engine patch preview and apply/reject decision",
    "export-handoff": "engine export handoff routing",
}

DEMO_PATH_ENGINE_ACTIONS: dict[str, tuple[str, ...]] = {
    "project-open": ("open_project",),
    "retrieval": ("retrieve_context",),
    "patch-review": ("preview_patch", "apply_patch", "reject_patch"),
    "export-handoff": ("persist_session", "export_handoff"),
}

DEMO_PATH_OPERATOR_CHECKPOINTS: dict[str, str] = {
    "project-open": "open project/document",
    "retrieval": "retrieve relevant material",
    "patch-review": "preview and accept or reject patch",
    "export-handoff": "persist and continue through export handoff",
}


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


def _cli_tokens(spec: CommandSpec) -> tuple[str, ...]:
    tokens = spec.cli_tokens or (spec.name,)
    return tuple(_normalize_token(token) for token in tokens)


def _validate_cli_entrypoints(specs: tuple[CommandSpec, ...] | None = None) -> None:
    specs = COMMAND_SPECS if specs is None else specs
    validate_command_catalog(specs)
    seen_entrypoints: set[str] = set()
    for spec in specs:
        for entrypoint in _cli_tokens(spec):
            if not entrypoint:
                raise ValueError("Command CLI entrypoints must not be empty")
            if entrypoint in seen_entrypoints:
                raise ValueError(f"Duplicate command CLI entrypoint: {entrypoint}")
            seen_entrypoints.add(entrypoint)
            if canonical_command_for(specs, entrypoint) != spec.name:
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
        cli_tokens=("bootstrap",),
    ),
    CommandSpec(
        name="diff-preview",
        aliases=("diff", "diff_preview"),
        description="Preview unified diff output.",
        flow_step="patch-review",
        cli_tokens=("diff-preview", "diff"),
    ),
    CommandSpec(
        name="context-basket",
        aliases=("context", "basket"),
        description="Manage retrieval context basket items.",
        flow_step="retrieval",
        cli_tokens=("context-basket",),
    ),
    CommandSpec(
        name="terminal",
        description="Run terminal export handoff routing.",
        flow_step="export-handoff",
        cli_tokens=("terminal",),
    ),
)

DEMO_COMMAND_FLOW_STEPS: tuple[str, ...] = (
    "project-open",
    "retrieval",
    "patch-review",
    "export-handoff",
)
MVP_COMMAND_FLOW_STEPS: tuple[str, ...] = DEMO_COMMAND_FLOW_STEPS


def _actual_cli_parser_surface() -> tuple[tuple[str, str], ...]:
    from src.qual.cli import command_parser_lookup_table

    return command_parser_lookup_table()


def _actual_cli_parser_tokens() -> tuple[str, ...]:
    from src.qual.cli import command_parser_tokens

    return command_parser_tokens()


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
def command_cli_tokens(specs: tuple[CommandSpec, ...] = COMMAND_SPECS) -> tuple[str, ...]:
    _validate_cli_entrypoints(specs)
    return tuple(token for spec in specs for token in _cli_tokens(spec))


@lru_cache(maxsize=None)
def command_cli_lookup_table(
    specs: tuple[CommandSpec, ...] = COMMAND_SPECS,
) -> tuple[tuple[str, str], ...]:
    _validate_cli_entrypoints(specs)
    lookup_table: list[tuple[str, str]] = []
    for spec in specs:
        for entrypoint in _cli_tokens(spec):
            lookup_table.append((entrypoint, spec.name))
    return tuple(lookup_table)


def _parser_cli_lookup_table() -> tuple[tuple[str, str], ...]:
    try:
        return _actual_cli_parser_surface()
    except ValueError as exc:
        raise ValueError("Command CLI parser surface is inconsistent") from exc


def _validate_cli_contract_lookup_table(
    lookup_table: tuple[tuple[str, str], ...],
    parser_lookup_table: tuple[tuple[str, str], ...],
) -> None:
    if parser_lookup_table != lookup_table:
        raise ValueError("Command CLI parser surface is inconsistent")
    for entrypoint, canonical_name in parser_lookup_table:
        spec = command_spec_for(COMMAND_SPECS, entrypoint)
        if spec is None:
            raise ValueError(f"Unknown CLI command entrypoint: {entrypoint}")
        if spec.name != canonical_name:
            raise ValueError("Command CLI parser surface is inconsistent")


@lru_cache(maxsize=None)
def command_cli_contract() -> CommandCliContract:
    try:
        tokens = command_cli_tokens()
        lookup_table = command_cli_lookup_table()
    except ValueError as exc:
        raise ValueError("Command CLI parser surface is inconsistent") from exc
    parser_lookup_table = _parser_cli_lookup_table()
    if tuple(token for token, _ in parser_lookup_table) != tokens:
        raise ValueError("Command CLI parser surface is inconsistent")
    _validate_cli_contract_lookup_table(lookup_table, parser_lookup_table)
    canonical_names = command_names()
    if canonical_names != tuple(dict.fromkeys(canonical_name for _, canonical_name in lookup_table)):
        raise ValueError("Command CLI canonical names are inconsistent")
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


def _validate_command_smoke_contract(
    contract: CommandSmokeContract,
    *,
    route_catalog: tuple[CommandFlowRouteEntry, ...],
) -> None:
    cli_lookup = dict(command_cli_lookup_table())
    expected_tokens: list[str] = []
    expected_argv: list[tuple[str, ...]] = []
    expected_lookup: list[tuple[str, str]] = []
    for step in contract.steps:
        if not step.cli_token:
            raise ValueError("Command smoke token must not be empty")
        if not step.argv or step.argv[0] != step.cli_token:
            raise ValueError("Command smoke argv must begin with the CLI token")
        if cli_lookup.get(step.cli_token) != step.name:
            raise ValueError("Command smoke token is not accepted by the CLI parser")
        expected_tokens.append(step.cli_token)
        expected_argv.append(step.argv)
        expected_lookup.append((step.cli_token, step.flow_step))
    if contract.command_tokens != tuple(expected_tokens):
        raise ValueError("Command smoke tokens are inconsistent")
    if contract.argv != tuple(expected_argv):
        raise ValueError("Command smoke argv is inconsistent")
    if contract.command_lines != tuple(shlex.join(argv) for argv in expected_argv):
        raise ValueError("Command smoke command lines are inconsistent")
    if contract.lookup_table != tuple(expected_lookup):
        raise ValueError("Command smoke lookup table is inconsistent")
    expected_route_summary = tuple(
        (entry.flow_step, entry.name, entry.cli_tokens)
        for entry in route_catalog
    )
    if contract.route_summary != expected_route_summary:
        raise ValueError("Command smoke route summary is inconsistent")
    if contract.lookup_surface != command_mvp_flow_lookup_surface():
        raise ValueError("Command smoke lookup surface is inconsistent")
    if contract.flow_surface_tokens != command_mvp_flow_surface_tokens():
        raise ValueError("Command smoke surface tokens are inconsistent")
    _validate_command_smoke_argv(contract.steps)


def _validate_command_smoke_argv(steps: tuple[CommandSmokeStep, ...]) -> None:
    from src.qual.cli import parse_args

    for step in steps:
        parsed = parse_args(list(step.argv))
        if parsed.command != step.name:
            raise ValueError("Command smoke argv does not parse to the expected command")
        if step.name == "context-basket" and parsed.basket_action != "list":
            raise ValueError("Command smoke argv does not parse to the expected basket action")


def _validate_command_demo_path_contract(contract: CommandDemoPathContract) -> None:
    smoke_contract = command_mvp_smoke_contract()
    if contract.flow_steps != tuple(step.flow_step for step in smoke_contract.steps):
        raise ValueError("Command demo path flow steps are inconsistent")
    if contract.names != tuple(step.name for step in smoke_contract.steps):
        raise ValueError("Command demo path names are inconsistent")
    if contract.command_tokens != smoke_contract.command_tokens:
        raise ValueError("Command demo path tokens are inconsistent")
    if contract.command_lines != smoke_contract.command_lines:
        raise ValueError("Command demo path command lines are inconsistent")
    expected_handoffs = tuple(
        DEMO_PATH_ENGINE_HANDOFFS[step.flow_step]
        for step in smoke_contract.steps
    )
    if contract.engine_handoffs != expected_handoffs:
        raise ValueError("Command demo path engine handoffs are inconsistent")
    expected_actions = tuple(
        DEMO_PATH_ENGINE_ACTIONS[step.flow_step]
        for step in smoke_contract.steps
    )
    if contract.engine_actions != expected_actions:
        raise ValueError("Command demo path engine actions are inconsistent")
    for step in contract.steps:
        if not step.engine_actions:
            raise ValueError("Command demo path engine actions must not be empty")
    patch_step = next((step for step in contract.steps if step.flow_step == "patch-review"), None)
    if patch_step is None:
        raise ValueError("Command demo path must include patch review")
    if not {"apply_patch", "reject_patch"}.issubset(patch_step.engine_actions):
        raise ValueError("Command demo path patch review must expose apply/reject actions")


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
def command_mvp_smoke_contract() -> CommandSmokeContract:
    route_catalog = command_mvp_flow_route_catalog()
    steps = tuple(
        CommandSmokeStep(
            flow_step=entry.flow_step,
            name=entry.name,
            cli_token=entry.cli_tokens[0],
            argv=_smoke_argv_for(entry.name, entry.cli_tokens[0]),
            description=entry.description,
        )
        for entry in route_catalog
    )
    contract = CommandSmokeContract(
        steps=steps,
        command_tokens=tuple(step.cli_token for step in steps),
        argv=tuple(step.argv for step in steps),
        command_lines=tuple(step.command_line for step in steps),
        lookup_table=tuple((step.cli_token, step.flow_step) for step in steps),
        route_summary=tuple(
            (entry.flow_step, entry.name, entry.cli_tokens)
            for entry in route_catalog
        ),
        lookup_surface=command_mvp_flow_lookup_surface(),
        flow_surface_tokens=command_mvp_flow_surface_tokens(),
    )
    _validate_command_smoke_contract(contract, route_catalog=route_catalog)
    return contract


def _smoke_argv_for(command_name: str, cli_token: str) -> tuple[str, ...]:
    if command_name == "context-basket":
        return (cli_token, "list")
    return (cli_token,)


def command_mvp_smoke_commands() -> tuple[str, ...]:
    return command_mvp_smoke_contract().command_tokens


def command_mvp_smoke_argv() -> tuple[tuple[str, ...], ...]:
    return command_mvp_smoke_contract().argv


def command_mvp_smoke_command_lines() -> tuple[str, ...]:
    return command_mvp_smoke_contract().command_lines


def command_mvp_smoke_lookup_table() -> tuple[tuple[str, str], ...]:
    return command_mvp_smoke_contract().lookup_table


def command_mvp_smoke_route_summary() -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    return command_mvp_smoke_contract().route_summary


@lru_cache(maxsize=None)
def command_mvp_demo_path_contract() -> CommandDemoPathContract:
    smoke_contract = command_mvp_smoke_contract()
    steps = tuple(
        CommandDemoPathStep(
            flow_step=step.flow_step,
            name=step.name,
            cli_token=step.cli_token,
            argv=step.argv,
            command_line=step.command_line,
            operator_checkpoint=DEMO_PATH_OPERATOR_CHECKPOINTS[step.flow_step],
            engine_handoff=DEMO_PATH_ENGINE_HANDOFFS[step.flow_step],
            description=step.description,
            engine_actions=DEMO_PATH_ENGINE_ACTIONS[step.flow_step],
        )
        for step in smoke_contract.steps
    )
    contract = CommandDemoPathContract(
        steps=steps,
        flow_steps=tuple(step.flow_step for step in steps),
        names=tuple(step.name for step in steps),
        command_tokens=tuple(step.cli_token for step in steps),
        command_lines=tuple(step.command_line for step in steps),
        engine_handoffs=tuple(step.engine_handoff for step in steps),
        engine_actions=tuple(step.engine_actions for step in steps),
    )
    _validate_command_demo_path_contract(contract)
    return contract


def command_mvp_demo_path_steps() -> tuple[CommandDemoPathStep, ...]:
    return command_mvp_demo_path_contract().steps


def command_mvp_demo_path_command_lines() -> tuple[str, ...]:
    return command_mvp_demo_path_contract().command_lines


def command_mvp_demo_path_operator_checkpoints() -> tuple[str, ...]:
    return tuple(step.operator_checkpoint for step in command_mvp_demo_path_contract().steps)


def command_mvp_demo_path_engine_handoffs() -> tuple[str, ...]:
    return command_mvp_demo_path_contract().engine_handoffs


def command_mvp_demo_path_engine_actions() -> tuple[tuple[str, ...], ...]:
    return command_mvp_demo_path_contract().engine_actions


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
