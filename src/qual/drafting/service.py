from __future__ import annotations

import difflib


class DraftingService:
    """Draft revision scaffold service."""

    def propose_diff(self, original: str, proposed: str) -> str:
        before = self._normalize_for_diff(original).splitlines(keepends=True)
        after = self._normalize_for_diff(proposed).splitlines(keepends=True)
        return "".join(
            difflib.unified_diff(before, after, fromfile="original", tofile="proposed")
        )

    @staticmethod
    def _normalize_newlines(value: str) -> str:
        return value.replace("\r\n", "\n").replace("\r", "\n")

    @classmethod
    def _normalize_for_diff(cls, value: str) -> str:
        normalized = cls._normalize_newlines(value)
        if normalized.startswith("\ufeff"):
            normalized = normalized[1:]
        had_trailing_newline = normalized.endswith("\n")
        parts = normalized.split("\n")
        if had_trailing_newline:
            parts = parts[:-1]
        cleaned = [line.rstrip(" \t") for line in parts]
        result = "\n".join(cleaned)
        if had_trailing_newline:
            result += "\n"
        return result
