"""Debug helpers for context storage."""

from __future__ import annotations

from pathlib import Path

__all__ = ["get_corrupt_file_count"]


def get_corrupt_file_count(state_root: Path | str) -> int:
    """Return the number of corrupt artifacts currently visible in *state_root*."""

    from .store import list_corrupt_files

    try:
        state_root_path = Path(state_root)
        return len(list_corrupt_files(state_root_path))
    except Exception:
        # Debug visibility should never become a new failure mode for storage
        # callers that are already handling missing or inaccessible state.
        return 0
