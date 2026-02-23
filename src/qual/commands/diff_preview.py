from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

from src.qual.drafting.service import DraftingService

MAX_DIFF_OUTPUT_CHARS = 20_000
MAX_DIFF_OUTPUT_CHARS_ENV = "QUAL_DIFF_MAX_OUTPUT_CHARS"
IGNORE_TRAILING_WHITESPACE_ENV = "QUAL_DIFF_IGNORE_TRAILING_WHITESPACE"
SUPPRESS_FILE_HEADERS_ENV = "QUAL_DIFF_SUPPRESS_FILE_HEADERS"
INCLUDE_SUMMARY_ENV = "QUAL_DIFF_INCLUDE_SUMMARY"
SUMMARY_ONLY_ENV = "QUAL_DIFF_SUMMARY_ONLY"
INCLUDE_SUMMARY_DETAILS_ENV = "QUAL_DIFF_INCLUDE_SUMMARY_DETAILS"
INCLUDE_OPTIONS_BANNER_ENV = "QUAL_DIFF_INCLUDE_OPTIONS_BANNER"
TRUNCATION_STRATEGY_ENV = "QUAL_DIFF_TRUNCATION_STRATEGY"
STRIP_ANSI_ENV = "QUAL_DIFF_STRIP_ANSI"
CANONICALIZE_INLINE_WHITESPACE_ENV = "QUAL_DIFF_CANONICALIZE_INLINE_WHITESPACE"
IGNORE_CASE_ENV = "QUAL_DIFF_IGNORE_CASE"
IGNORE_EDGE_BLANK_LINES_ENV = "QUAL_DIFF_IGNORE_EDGE_BLANK_LINES"
IGNORE_ALL_BLANK_LINES_ENV = "QUAL_DIFF_IGNORE_ALL_BLANK_LINES"
TRUNCATION_MARKER_ENV = "QUAL_DIFF_TRUNCATION_MARKER"
MAX_DIFF_OUTPUT_LINES_ENV = "QUAL_DIFF_MAX_OUTPUT_LINES"
SUPPRESS_HUNK_HEADERS_ENV = "QUAL_DIFF_SUPPRESS_HUNK_HEADERS"
SUMMARY_JSON_ENV = "QUAL_DIFF_SUMMARY_JSON"
SUMMARY_JSON_INDENT_ENV = "QUAL_DIFF_SUMMARY_JSON_INDENT"
SUMMARY_JSON_SORT_KEYS_ENV = "QUAL_DIFF_SUMMARY_JSON_SORT_KEYS"
SUMMARY_JSON_ENSURE_ASCII_ENV = "QUAL_DIFF_SUMMARY_JSON_ENSURE_ASCII"
ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


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
    normalized: list[str] = []
    for line in lines:
        if line.endswith("\n"):
            normalized.append(f"{line[:-1].rstrip(' \t')}\n")
        else:
            normalized.append(line.rstrip(" \t"))
    return "".join(normalized)


def _strip_ansi(value: str) -> str:
    return ANSI_ESCAPE_RE.sub("", value)


def _canonicalize_inline_whitespace(value: str) -> str:
    lines = value.splitlines(keepends=True)
    normalized: list[str] = []
    for line in lines:
        newline = "\n" if line.endswith("\n") else ""
        body = line[:-1] if newline else line
        body = re.sub(r"[ \t]+", " ", body)
        normalized.append(body + newline)
    return "".join(normalized)


def _normalize_case(value: str) -> str:
    return value.casefold()


def _strip_edge_blank_lines(value: str) -> str:
    lines = value.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


def _strip_all_blank_lines(value: str) -> str:
    lines = [line for line in value.splitlines() if line.strip()]
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


def _suppress_file_headers(diff: str) -> str:
    lines = diff.splitlines(keepends=True)
    if len(lines) >= 2 and lines[0].startswith("--- ") and lines[1].startswith("+++ "):
        return "".join(lines[2:])
    return diff


def _suppress_hunk_headers(diff: str) -> str:
    return "".join(line for line in diff.splitlines(keepends=True) if not line.startswith("@@ "))


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


def _max_diff_output_lines() -> int | None:
    raw = os.getenv(MAX_DIFF_OUTPUT_LINES_ENV)
    if raw is None:
        return None
    try:
        parsed = int(raw.strip())
    except ValueError:
        return None
    if parsed <= 0:
        return None
    return parsed


def _diff_stats(diff: str) -> tuple[int, int, int]:
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
    return added, removed, hunks


def _summarize_diff(diff: str) -> str:
    added, removed, hunks = _diff_stats(diff)
    if _env_enabled(SUMMARY_JSON_ENV):
        payload: dict[str, int] = {
            "added": added,
            "removed": removed,
            "hunks": hunks,
        }
        if _env_enabled(INCLUDE_SUMMARY_DETAILS_ENV):
            payload["changed"] = added + removed
            payload["net"] = added - removed
        sort_keys = _summary_json_sort_keys()
        ensure_ascii = _summary_json_ensure_ascii()
        indent = _summary_json_indent()
        if indent is None:
            return json.dumps(payload, separators=(",", ":"), sort_keys=sort_keys, ensure_ascii=ensure_ascii)
        return json.dumps(payload, indent=indent, sort_keys=sort_keys, ensure_ascii=ensure_ascii)

    summary = f"Diff summary: +{added} -{removed} (hunks: {hunks})"
    if _env_enabled(INCLUDE_SUMMARY_DETAILS_ENV):
        changed = added + removed
        net = added - removed
        summary = f"{summary} [changed: {changed}, net: {net:+d}]"
    return summary


def _summary_json_indent() -> int | None:
    raw = os.getenv(SUMMARY_JSON_INDENT_ENV)
    if raw is None:
        return None
    try:
        parsed = int(raw.strip())
    except ValueError:
        return None
    if parsed <= 0:
        return None
    return parsed


def _summary_json_sort_keys() -> bool:
    raw = os.getenv(SUMMARY_JSON_SORT_KEYS_ENV)
    if raw is None:
        return True
    value = raw.strip().lower()
    if value in {"0", "false", "no", "off"}:
        return False
    if value in {"1", "true", "yes", "on"}:
        return True
    return True


def _summary_json_ensure_ascii() -> bool:
    raw = os.getenv(SUMMARY_JSON_ENSURE_ASCII_ENV)
    if raw is None:
        return True
    value = raw.strip().lower()
    if value in {"0", "false", "no", "off"}:
        return False
    if value in {"1", "true", "yes", "on"}:
        return True
    return True


def _options_banner(
    *, ignore_trailing_whitespace: bool, suppress_file_headers: bool, max_chars: int, max_lines: int | None
) -> str:
    max_lines_value = "none" if max_lines is None else str(max_lines)
    return (
        "Diff options: "
        f"ignore_trailing_whitespace={str(ignore_trailing_whitespace).lower()}, "
        f"suppress_file_headers={str(suppress_file_headers).lower()}, "
        f"strip_ansi={str(_env_enabled(STRIP_ANSI_ENV)).lower()}, "
        f"canonicalize_inline_whitespace={str(_env_enabled(CANONICALIZE_INLINE_WHITESPACE_ENV)).lower()}, "
        f"ignore_case={str(_env_enabled(IGNORE_CASE_ENV)).lower()}, "
        f"ignore_edge_blank_lines={str(_env_enabled(IGNORE_EDGE_BLANK_LINES_ENV)).lower()}, "
        f"ignore_all_blank_lines={str(_env_enabled(IGNORE_ALL_BLANK_LINES_ENV)).lower()}, "
        f"summary_json={str(_env_enabled(SUMMARY_JSON_ENV)).lower()}, "
        f"summary_json_indent={str(_summary_json_indent() or 0)}, "
        f"summary_json_sort_keys={str(_summary_json_sort_keys()).lower()}, "
        f"summary_json_ensure_ascii={str(_summary_json_ensure_ascii()).lower()}, "
        f"suppress_hunk_headers={str(_env_enabled(SUPPRESS_HUNK_HEADERS_ENV)).lower()}, "
        f"max_output_lines={max_lines_value}, "
        f"max_output_chars={max_chars}, "
        f"truncation_strategy={_truncation_strategy()}"
    )


def _truncation_strategy() -> str:
    raw = os.getenv(TRUNCATION_STRATEGY_ENV)
    if raw is None:
        return "middle"
    value = raw.strip().lower()
    if value in {"middle", "tail"}:
        return value
    return "middle"


def _truncation_marker(omitted: int, *, unit: str = "characters") -> str:
    custom = os.getenv(TRUNCATION_MARKER_ENV)
    if custom is not None and custom.strip():
        return custom.strip()
    return f"... diff truncated ({omitted} {unit} omitted) ..."


def _truncate_diff(diff: str, max_chars: int) -> str:
    strategy = _truncation_strategy()
    if strategy == "tail":
        omitted = len(diff) - max_chars
        return f"{diff[:max_chars]}\n{_truncation_marker(omitted, unit='characters')}"

    head_chars = max_chars // 2
    tail_chars = max_chars - head_chars
    omitted = len(diff) - (head_chars + tail_chars)
    return (
        f"{diff[:head_chars]}"
        f"{_truncation_marker(omitted, unit='characters')}"
        f"{diff[-tail_chars:]}"
    )


def _truncate_diff_lines(diff: str, max_lines: int) -> str:
    lines = diff.splitlines(keepends=True)
    if len(lines) <= max_lines:
        return diff

    strategy = _truncation_strategy()
    omitted = len(lines) - max_lines
    marker = _truncation_marker(omitted, unit="lines")
    if strategy == "tail":
        head = "".join(lines[:max_lines])
        if head and not head.endswith("\n"):
            head += "\n"
        return f"{head}{marker}\n"

    head_lines = max_lines // 2
    tail_lines = max_lines - head_lines
    head = "".join(lines[:head_lines])
    tail = "".join(lines[-tail_lines:])
    if head and not head.endswith("\n"):
        head += "\n"
    return f"{head}{marker}\n{tail}"


def run_diff_preview(payload: DiffPreviewInput) -> str:
    original = _normalize_text(payload.original)
    proposed = _normalize_text(payload.proposed)
    ignore_trailing_whitespace = _env_enabled(IGNORE_TRAILING_WHITESPACE_ENV)
    suppress_file_headers = _env_enabled(SUPPRESS_FILE_HEADERS_ENV)
    include_options_banner = _env_enabled(INCLUDE_OPTIONS_BANNER_ENV)

    if _env_enabled(STRIP_ANSI_ENV):
        original = _strip_ansi(original)
        proposed = _strip_ansi(proposed)
    if _env_enabled(CANONICALIZE_INLINE_WHITESPACE_ENV):
        original = _canonicalize_inline_whitespace(original)
        proposed = _canonicalize_inline_whitespace(proposed)
    if _env_enabled(IGNORE_CASE_ENV):
        original = _normalize_case(original)
        proposed = _normalize_case(proposed)
    if _env_enabled(IGNORE_EDGE_BLANK_LINES_ENV):
        original = _strip_edge_blank_lines(original)
        proposed = _strip_edge_blank_lines(proposed)
    if _env_enabled(IGNORE_ALL_BLANK_LINES_ENV):
        original = _strip_all_blank_lines(original)
        proposed = _strip_all_blank_lines(proposed)
    if ignore_trailing_whitespace:
        original = _normalize_trailing_whitespace(original)
        proposed = _normalize_trailing_whitespace(proposed)

    if not original and not proposed:
        return "No diff: both inputs are empty."

    if original == proposed:
        return "No diff: inputs are identical after normalization."

    drafting = DraftingService()
    diff = drafting.propose_diff(original, proposed)
    summary_source = diff
    if suppress_file_headers:
        diff = _suppress_file_headers(diff)
    if _env_enabled(SUPPRESS_HUNK_HEADERS_ENV):
        diff = _suppress_hunk_headers(diff)
    if not diff:
        return "No diff: inputs are identical."
    max_chars = _max_diff_output_chars()
    max_lines = _max_diff_output_lines()
    banner = ""
    if include_options_banner:
        banner = (
            _options_banner(
                ignore_trailing_whitespace=ignore_trailing_whitespace,
                suppress_file_headers=suppress_file_headers,
                max_chars=max_chars,
                max_lines=max_lines,
            )
            + "\n\n"
        )
    if _env_enabled(SUMMARY_ONLY_ENV):
        return f"{banner}{_summarize_diff(summary_source)}"

    output = diff
    if max_lines is not None:
        output = _truncate_diff_lines(output, max_lines)
    if len(output) > max_chars:
        output = _truncate_diff(output, max_chars)

    if _env_enabled(INCLUDE_SUMMARY_ENV):
        return f"{banner}{output}\n\n{_summarize_diff(summary_source)}"
    return f"{banner}{output}"
