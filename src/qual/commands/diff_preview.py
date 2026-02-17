from __future__ import annotations

import os
from dataclasses import dataclass

from src.qual.drafting.service import DraftingService

MAX_DIFF_OUTPUT_CHARS = 20_000
MAX_DIFF_OUTPUT_CHARS_ENV = "QUAL_DIFF_MAX_OUTPUT_CHARS"
IGNORE_TRAILING_WHITESPACE_ENV = "QUAL_DIFF_IGNORE_TRAILING_WHITESPACE"
SUPPRESS_FILE_HEADERS_ENV = "QUAL_DIFF_SUPPRESS_FILE_HEADERS"
INCLUDE_SUMMARY_ENV = "QUAL_DIFF_INCLUDE_SUMMARY"
SUMMARY_ONLY_ENV = "QUAL_DIFF_SUMMARY_ONLY"


@dataclass(frozen=True)
class DiffPreviewInput:
    original: str
    proposed: str


def _normalize_text(value: str) -> str:
    # Normalize newlines so diff output is stable across platforms.
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _env_enabled(name: str) -> bool:
    value = os.getenv(name)
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _normalize_trailing_whitespace(value: str) -> str:
    lines = value.splitlines(keepends=True)
    return "".join(line.rstrip(" \t") + ("\n" if line.endswith("\n") else "") for line in lines)


def _suppress_file_headers(diff: str) -> str:
    lines = diff.splitlines(keepends=True)
    if len(lines) >= 2 and lines[0].startswith("--- ") and lines[1].startswith("+++ "):
        return "".join(lines[2:])
    return diff


def _max_diff_output_chars() -> int:
    raw = os.getenv(MAX_DIFF_OUTPUT_CHARS_ENV)
    if raw is None:
        return MAX_DIFF_OUTPUT_CHARS
    try:
        parsed = int(raw.strip())
    except ValueError:
        return MAX_DIFF_OUTPUT_CHARS
    if parsed <= 0:
        return MAX_DIFF_OUTPUT_CHARS
    return parsed


def _summarize_diff(diff: str) -> str:
    added = 0
    removed = 0
    hunks = 0
    for line in diff.splitlines():
        if line.startswith("@@ "):
            hunks += 1
            continue
        if line.startswith("+++ ") or line.startswith("--- "):
            continue
        if line.startswith("+"):
            added += 1
            continue
        if line.startswith("-"):
            removed += 1
    return f"Diff summary: +{added} -{removed} (hunks: {hunks})"


def run_diff_preview(payload: DiffPreviewInput) -> str:
    original = _normalize_text(payload.original)
    proposed = _normalize_text(payload.proposed)
    if _env_enabled(IGNORE_TRAILING_WHITESPACE_ENV):
        original = _normalize_trailing_whitespace(original)
        proposed = _normalize_trailing_whitespace(proposed)

    if not original and not proposed:
        return "No diff: both inputs are empty."

    if original == proposed:
        return "No diff: inputs are identical after normalization."

    drafting = DraftingService()
    diff = drafting.propose_diff(original, proposed)
    if _env_enabled(SUPPRESS_FILE_HEADERS_ENV):
        diff = _suppress_file_headers(diff)
    if not diff:
        return "No diff: inputs are identical."
    if _env_enabled(SUMMARY_ONLY_ENV):
        return _summarize_diff(diff)

    max_chars = _max_diff_output_chars()
    output = diff
    if len(diff) > max_chars:
        head_chars = max_chars // 2
        tail_chars = max_chars - head_chars
        omitted = len(diff) - (head_chars + tail_chars)
        output = (
            f"{diff[:head_chars]}"
            f"... diff truncated ({omitted} characters omitted) ..."
            f"{diff[-tail_chars:]}"
        )

    if _env_enabled(INCLUDE_SUMMARY_ENV):
        return f"{output}\n\n{_summarize_diff(diff)}"
    return output
