"""Utility helpers for the :mod:`exegesis_engine.context` package.

The original repository exposed corrupt-state helpers in ``store.py``. Some
consumers import those helpers from a module named ``utils`` instead. This
shim keeps those legacy import paths working while still forwarding all
behavior to the canonical implementations in ``store``.

The wrappers are intentionally thin so the cleanup and preflight recovery
logic has one source of truth and stays consistent with the policy used by
the engine storage layer.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union


def clear_corrupt_files(state_root: Union[Path, str]) -> int:
    """Forward to :func:`qual.context.store.clear_corrupt_files`."""

    from .store import clear_corrupt_files

    return clear_corrupt_files(state_root)


def purge_corrupt_state(state_root: Union[Path, str]) -> int:
    """Forward to :func:`qual.context.store.purge_corrupt_state`."""

    from .store import purge_corrupt_state

    return purge_corrupt_state(state_root)


def list_corrupt_files(state_root: Union[Path, str]) -> list[Path]:
    """Forward to :func:`qual.context.store.list_corrupt_files`."""

    from .store import list_corrupt_files

    return list_corrupt_files(state_root)


def is_clean_state(state_root: Union[Path, str]) -> bool:
    """Forward to :func:`qual.context.store.is_clean_state`."""

    from .store import is_clean_state

    return is_clean_state(state_root)


def validate_and_quarantine(path: Union[Path, str]) -> bool:
    """Forward to :func:`qual.context.store.validate_and_quarantine`."""

    from .store import validate_and_quarantine

    return validate_and_quarantine(path)


def get_corrupt_file_count(state_root: Union[Path, str]) -> int:
    """Forward to :func:`qual.context.debug.get_corrupt_file_count`."""

    from .debug import get_corrupt_file_count

    return get_corrupt_file_count(state_root)


def remove_all_corrupt_files(state_root: Union[Path, str]) -> int:
    """Backward-compatible alias for :func:`clear_corrupt_files`."""

    return clear_corrupt_files(state_root)


__all__ = [
    "clear_corrupt_files",
    "purge_corrupt_state",
    "list_corrupt_files",
    "is_clean_state",
    "validate_and_quarantine",
    "get_corrupt_file_count",
    "remove_all_corrupt_files",
]
