from __future__ import annotations

import difflib


class DraftingService:
    """Draft revision scaffold service."""

    def propose_diff(self, original: str, proposed: str) -> str:
        before = self._normalize_newlines(original).splitlines(keepends=True)
        after = self._normalize_newlines(proposed).splitlines(keepends=True)
        return "".join(
            difflib.unified_diff(before, after, fromfile="original", tofile="proposed")
        )

    @staticmethod
    def _normalize_newlines(value: str) -> str:
        return value.replace("\r\n", "\n").replace("\r", "\n")
