from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandSpec:
    name: str
    aliases: tuple[str, ...] = ()
    description: str = ""
    mvp_role: str = ""


@dataclass(frozen=True)
class CommandCatalogEntry:
    name: str
    aliases: tuple[str, ...]
    description: str
    mvp_role: str
    lookup_names: tuple[str, ...]
    in_mvp_flow: bool = False


def _normalize_token(value: str) -> str:
    # Collapse common shell separators so aliases stay stable across caller styles.
    return re.sub(r"[-_\s]+", "-", value.strip().casefold())


def _validate_command_spec(spec: CommandSpec) -> None:
    if not spec.name.strip():
        raise ValueError("Command name cannot be blank.")

    seen_aliases: set[str] = set()
    for alias in spec.aliases:
        normalized = _normalize_token(alias)
        if not normalized:
            raise ValueError(f"Command alias cannot be blank: {spec.name}")
        if normalized in seen_aliases:
            raise ValueError(f"Duplicate command alias within spec: {alias}")
        seen_aliases.add(normalized)


def _build_command_spec_index(specs: tuple[CommandSpec, ...]) -> dict[str, CommandSpec]:
    index: dict[str, CommandSpec] = {}
    for spec in specs:
        _validate_command_spec(spec)
        if spec.name in index:
            raise ValueError(f"Duplicate command name: {spec.name}")
        index[spec.name] = spec
    return index


def _build_command_lookup_index(specs: tuple[CommandSpec, ...]) -> dict[str, CommandSpec]:
    index: dict[str, CommandSpec] = {}
    for spec in specs:
        for alias in (spec.name, *spec.aliases):
            normalized = _normalize_token(alias)
            existing = index.get(normalized)
            if existing is not None and existing.name != spec.name:
                raise ValueError(f"Duplicate command lookup alias: {alias}")
            index[normalized] = spec
    return index


COMMAND_SPECS: tuple[CommandSpec, ...] = (
    CommandSpec(
        name="bootstrap",
        aliases=("open", "project-open", "project"),
        description="Run the project bootstrap flow.",
        mvp_role="project-open",
    ),
    CommandSpec(
        name="retrieve",
        aliases=("retrieval", "lookup"),
        description="Run the project retrieval flow.",
        mvp_role="retrieval-invocation",
    ),
    CommandSpec(
        name="diff-preview",
        aliases=("diff", "diff_preview"),
        description="Preview unified diff output.",
        mvp_role="patch-review",
    ),
    CommandSpec(
        name="context-basket",
        aliases=("context", "basket"),
        description="Manage context basket items.",
        mvp_role="retrieval-staging",
    ),
    CommandSpec(
        name="terminal",
        description="Run terminal routing scaffolding.",
        mvp_role="a2ui-routing",
    ),
    CommandSpec(
        name="export-preview",
        aliases=("export", "handoff"),
        description="Prepare export handoff artifacts.",
        mvp_role="export-handoff",
    ),
)
_COMMAND_SPEC_BY_NAME = _build_command_spec_index(COMMAND_SPECS)
_COMMAND_LOOKUP_BY_ALIAS = _build_command_lookup_index(COMMAND_SPECS)

_MVP_FLOW_COMMAND_NAMES: tuple[str, ...] = (
    "bootstrap",
    "retrieve",
    "context-basket",
    "diff-preview",
    "terminal",
    "export-preview",
)


def command_names() -> tuple[str, ...]:
    return tuple(spec.name for spec in COMMAND_SPECS)


def command_specs() -> tuple[CommandSpec, ...]:
    return COMMAND_SPECS


def _build_command_catalog_entry(spec: CommandSpec, *, in_mvp_flow: bool) -> CommandCatalogEntry:
    return CommandCatalogEntry(
        name=spec.name,
        aliases=spec.aliases,
        description=spec.description,
        mvp_role=spec.mvp_role,
        lookup_names=_lookup_names_for_specs((spec,)),
        in_mvp_flow=in_mvp_flow,
    )


def command_catalog_entries() -> tuple[CommandCatalogEntry, ...]:
    return _command_catalog_entries_for_specs(COMMAND_SPECS)


def command_catalog_index() -> dict[str, CommandCatalogEntry]:
    return {entry.name: entry for entry in command_catalog_entries()}


def command_catalog_entries_for_role(mvp_role: str) -> tuple[CommandCatalogEntry, ...]:
    return _command_catalog_entries_for_specs(command_specs_for_role(mvp_role))


def command_catalog_entry(name: str) -> CommandCatalogEntry | None:
    spec = command_spec(name)
    if spec is None:
        return None
    return _build_command_catalog_entry(spec, in_mvp_flow=spec.name in _MVP_FLOW_COMMAND_NAME_SET)


def _command_catalog_entries_for_specs(specs: tuple[CommandSpec, ...]) -> tuple[CommandCatalogEntry, ...]:
    flow_names = _MVP_FLOW_COMMAND_NAME_SET
    return tuple(
        _build_command_catalog_entry(spec, in_mvp_flow=spec.name in flow_names)
        for spec in specs
    )


def _lookup_names_for_specs(specs: tuple[CommandSpec, ...]) -> tuple[str, ...]:
    names: list[str] = []
    seen: set[str] = set()
    for spec in specs:
        for alias in (spec.name, *spec.aliases):
            normalized = _normalize_token(alias)
            if normalized in seen:
                continue
            seen.add(normalized)
            names.append(normalized)
    return tuple(names)


def command_lookup_names() -> tuple[str, ...]:
    return _lookup_names_for_specs(COMMAND_SPECS)


def command_lookup_index() -> dict[str, CommandSpec]:
    return dict(_COMMAND_LOOKUP_BY_ALIAS)


def command_spec(name: str) -> CommandSpec | None:
    normalized = _normalize_token(name)
    if not normalized:
        return None
    return _COMMAND_LOOKUP_BY_ALIAS.get(normalized)


def command_aliases(name: str) -> tuple[str, ...]:
    spec = command_spec(name)
    if spec is None:
        return ()
    return spec.aliases


def command_mvp_role(name: str) -> str:
    spec = command_spec(name)
    if spec is None:
        return ""
    return spec.mvp_role


def command_mvp_flow_specs() -> tuple[CommandSpec, ...]:
    specs: list[CommandSpec] = []
    for name in _MVP_FLOW_COMMAND_NAMES:
        spec = _COMMAND_SPEC_BY_NAME.get(name)
        if spec is None:
            raise ValueError(f"Unknown MVP flow command: {name}")
        specs.append(spec)
    return tuple(specs)


_MVP_FLOW_SPECS: tuple[CommandSpec, ...] = command_mvp_flow_specs()
_MVP_FLOW_COMMAND_NAME_SET: frozenset[str] = frozenset(spec.name for spec in _MVP_FLOW_SPECS)


def command_specs_for_role(mvp_role: str) -> tuple[CommandSpec, ...]:
    normalized_role = mvp_role.strip().casefold()
    if not normalized_role:
        return ()
    return tuple(spec for spec in COMMAND_SPECS if spec.mvp_role.casefold() == normalized_role)


def command_names_for_role(mvp_role: str) -> tuple[str, ...]:
    return tuple(spec.name for spec in command_specs_for_role(mvp_role))


def command_lookup_names_for_role(mvp_role: str) -> tuple[str, ...]:
    return _lookup_names_for_specs(command_specs_for_role(mvp_role))


def command_mvp_roles() -> tuple[str, ...]:
    roles: list[str] = []
    seen: set[str] = set()
    for spec in COMMAND_SPECS:
        role = spec.mvp_role.strip()
        if not role:
            continue
        normalized = role.casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        roles.append(role)
    return tuple(roles)


def command_mvp_flow_names() -> tuple[str, ...]:
    return tuple(spec.name for spec in _MVP_FLOW_SPECS)


def command_mvp_flow_lookup_names() -> tuple[str, ...]:
    return _lookup_names_for_specs(_MVP_FLOW_SPECS)


def command_mvp_flow_entries() -> tuple[CommandCatalogEntry, ...]:
    return _command_catalog_entries_for_specs(_MVP_FLOW_SPECS)


def command_mvp_flow_index() -> dict[str, CommandCatalogEntry]:
    return {entry.name: entry for entry in command_mvp_flow_entries()}


def command_mvp_flow_lookup_index() -> dict[str, CommandSpec]:
    return _build_command_lookup_index(_MVP_FLOW_SPECS)


def canonical_command(name: str) -> str:
    normalized = _normalize_token(name)
    if not normalized:
        return name.strip()
    spec = _COMMAND_LOOKUP_BY_ALIAS.get(normalized)
    if spec is None:
        return name.strip()
    return spec.name


def _validate_command_catalog_contract() -> None:
    spec_names = command_names()
    if len(spec_names) != len(set(spec_names)):
        raise ValueError("Command catalog contains duplicate names.")
    flow_names = command_mvp_flow_names()
    if len(flow_names) != len(set(flow_names)):
        raise ValueError("MVP flow command list contains duplicate names.")
    missing_flow_names = tuple(name for name in flow_names if name not in _COMMAND_SPEC_BY_NAME)
    if missing_flow_names:
        raise ValueError(
            "MVP flow command list contains unknown names: " + ", ".join(missing_flow_names)
        )
    if tuple(entry.name for entry in command_catalog_entries()) != spec_names:
        raise ValueError("Command catalog entries are out of sync with command definitions.")
    if tuple(entry.name for entry in command_mvp_flow_entries()) != flow_names:
        raise ValueError("MVP flow catalog entries are out of sync with flow definitions.")


_validate_command_catalog_contract()
