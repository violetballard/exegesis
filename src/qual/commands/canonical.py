"""Public wrappers for command canonicalization helpers."""

from __future__ import annotations

from src.qual.commands.catalog import (
    canonical_command,
    canonical_demo_command,
    canonical_demo_command_argv,
    canonical_mvp_command,
    canonical_mvp_command_argv,
)

__all__ = [
    "canonical_command",
    "canonical_demo_command",
    "canonical_demo_command_argv",
    "canonical_mvp_command",
    "canonical_mvp_command_argv",
]
