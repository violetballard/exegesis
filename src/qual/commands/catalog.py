from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CommandSpec:
    name: str
    aliases: tuple[str, ...] = ()
    description: str = ""
    mvp_role: str = ""


def _normalize_token(value: str) -> str:
    return value.strip().casefold().replace("_", "-")


def _build_command_spec_index(specs: tuple[CommandSpec, ...]) -> dict[str, CommandSpec]:
    index: dict[str, CommandSpec] = {}
    for spec in specs:
        if spec.name in index:
            raise ValueError(f"Duplicate command name: {spec.name}")
        index[spec.name] = spec
    return index


def _build_command_name_index(specs: tuple[CommandSpec, ...]) -> dict[str, str]:
    index: dict[str, str] = {}
    for spec in specs:
        for alias in (spec.name, *spec.aliases):
            normalized = _normalize_token(alias)
            existing = index.get(normalized)
            if existing is not None and existing != spec.name:
                raise ValueError(f"Duplicate command alias: {alias}")
            index[normalized] = spec.name
    return index


COMMAND_SPECS: tuple[CommandSpec, ...] = (
    CommandSpec(
        name="bootstrap",
        aliases=("open", "project-open", "project"),
        description="Run the project bootstrap flow.",
        mvp_role="project-open",
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
)
_COMMAND_SPEC_BY_NAME = _build_command_spec_index(COMMAND_SPECS)
_COMMAND_NAME_BY_ALIAS = _build_command_name_index(COMMAND_SPECS)


def command_names() -> tuple[str, ...]:
    return tuple(spec.name for spec in COMMAND_SPECS)


def command_specs() -> tuple[CommandSpec, ...]:
    return COMMAND_SPECS


def command_spec(name: str) -> CommandSpec | None:
    canonical = canonical_command(name)
    return _COMMAND_SPEC_BY_NAME.get(canonical)


def command_aliases(name: str) -> tuple[str, ...]:
    spec = command_spec(name)
    if spec is None:
        return ()
    return spec.aliases


def canonical_command(name: str) -> str:
    normalized = _normalize_token(name)
    if not normalized:
        return name.strip()
    return _COMMAND_NAME_BY_ALIAS.get(normalized, name.strip())
