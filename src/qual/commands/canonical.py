from __future__ import annotations

from src.qual.commands.catalog import canonical_command as _canonical_command


def canonical_command(name: str) -> str:
    return _canonical_command(name)
