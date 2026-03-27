from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandSpec:
    name: str
    aliases: tuple[str, ...] = ()
    description: str = ""


@dataclass(frozen=True)
class CommandManifestEntry:
    name: str
    aliases: tuple[str, ...]
    description: str


def _normalize_token(value: str) -> str:
    return re.sub(r"[-_\s]+", "-", value.strip().casefold())


COMMAND_SPECS: tuple[CommandSpec, ...] = (
    CommandSpec(
        name="bootstrap",
        aliases=("open", "project-open", "project"),
        description="Run the project bootstrap flow.",
    ),
    CommandSpec(
        name="diff-preview",
        aliases=("diff", "diff_preview"),
        description="Preview unified diff output.",
    ),
    CommandSpec(
        name="context-basket",
        aliases=("context", "basket"),
        description="Manage context basket items.",
    ),
    CommandSpec(
        name="terminal",
        description="Run terminal routing scaffolding.",
    ),
)
_COMMAND_SPEC_BY_ALIAS: dict[str, CommandSpec] = {}
for spec in COMMAND_SPECS:
    for alias in (spec.name, *spec.aliases):
        normalized = _normalize_token(alias)
        existing = _COMMAND_SPEC_BY_ALIAS.get(normalized)
        if existing is not None and existing.name != spec.name:
            raise ValueError(f"Duplicate command lookup alias: {alias}")
        _COMMAND_SPEC_BY_ALIAS[normalized] = spec


def command_names() -> tuple[str, ...]:
    return tuple(spec.name for spec in COMMAND_SPECS)


def command_specs() -> tuple[CommandSpec, ...]:
    return COMMAND_SPECS


def command_manifest() -> tuple[CommandManifestEntry, ...]:
    return tuple(
        CommandManifestEntry(name=spec.name, aliases=spec.aliases, description=spec.description)
        for spec in COMMAND_SPECS
    )


def command_tokens() -> tuple[str, ...]:
    return tuple(alias for spec in COMMAND_SPECS for alias in (spec.name, *spec.aliases))


def command_lookup_tokens(name: str) -> tuple[str, ...]:
    spec = command_spec(name)
    if spec is None:
        return ()
    return (spec.name, *spec.aliases)


def command_spec(name: str) -> CommandSpec | None:
    normalized = _normalize_token(name)
    if not normalized:
        return None
    return _COMMAND_SPEC_BY_ALIAS.get(normalized)


def command_aliases(name: str) -> tuple[str, ...]:
    spec = command_spec(name)
    if spec is None:
        return ()
    return spec.aliases


def canonical_command(name: str) -> str:
    normalized = _normalize_token(name)
    if not normalized:
        return name.strip()
    spec = command_spec(normalized)
    if spec is None:
        return normalized
    return spec.name
