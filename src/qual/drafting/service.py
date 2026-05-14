from __future__ import annotations

import difflib


class DraftingService:
    """Draft revision scaffold service."""

    def propose_diff(self, original: str, proposed: str) -> str:
        before_text = self._normalize_for_diff(original)
        after_text = self._normalize_for_diff(proposed)
        if before_text == after_text:
            return ""
        before = before_text.splitlines(keepends=True)
        after = after_text.splitlines(keepends=True)
        return "".join(
            difflib.unified_diff(before, after, fromfile="original", tofile="proposed")
        )

    @staticmethod
    def _normalize_newlines(value: str) -> str:
        normalized = value.replace("\r\n", "\n").replace("\r", "\n")
        normalized = normalized.replace("\u2028", "\n").replace("\u2029", "\n")
        return normalized.replace("\u0085", "\n")

    @classmethod
    def _normalize_for_diff(cls, value: str) -> str:
        normalized = cls._normalize_newlines(value)
        had_trailing_newline = normalized.endswith("\n")
        parts = normalized.split("\n")
        if had_trailing_newline:
            parts = parts[:-1]
        cleaned = [line[1:] if line.startswith("\ufeff") else line for line in parts]
        cleaned = [line.rstrip(" \t") for line in cleaned]
        result = "\n".join(cleaned)
        if result and not result.endswith("\n"):
            result += "\n"
        elif had_trailing_newline:
            result += "\n"
        return result
