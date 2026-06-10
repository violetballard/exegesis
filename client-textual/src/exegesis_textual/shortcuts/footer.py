from __future__ import annotations

from collections.abc import Iterable

from exegesis_textual.commands.palette import PaletteCommand


def footer_hint(commands: Iterable[PaletteCommand]) -> str:
    parts = [f"{command.key}: {command.label}" for command in commands]
    return " | ".join(parts)


__all__ = ["footer_hint"]
