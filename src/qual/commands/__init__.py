"""Stable command compatibility surface for the CLI-first MVP loop."""

from src.qual.commands.catalog import *  # noqa: F401,F403
from src.qual.commands.canonical import *  # noqa: F401,F403
from src.qual.commands.diff_preview import DiffPreviewInput, run_diff_preview

__all__ = tuple(name for name in globals() if not name.startswith("_"))
