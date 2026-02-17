from __future__ import annotations

import difflib


class DraftingService:
    """Draft revision scaffold service."""

    def propose_diff(self, original: str, proposed: str) -> str:
        before = original.splitlines(keepends=True)
        after = proposed.splitlines(keepends=True)
        return "".join(
            difflib.unified_diff(before, after, fromfile="original", tofile="proposed")
        )
