from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CommandSpec:
    name: str
    aliases: tuple[str, ...] = ()
    description: str = ""


def _normalize_token(value: str) -> str:
    return value.strip().casefold().replace("_", "-")


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
_COMMAND_NAME_BY_ALIAS = {
    _normalize_token(alias): spec.name
    for spec in COMMAND_SPECS
    for alias in (spec.name, *spec.aliases)
}


def command_names() -> tuple[str, ...]:
    return tuple(spec.name for spec in COMMAND_SPECS)


def command_specs() -> tuple[CommandSpec, ...]:
    return COMMAND_SPECS


def canonical_command(name: str) -> str:
    normalized = _normalize_token(name)
    if not normalized:
        return name.strip()
    return _COMMAND_NAME_BY_ALIAS.get(normalized, name.strip())
