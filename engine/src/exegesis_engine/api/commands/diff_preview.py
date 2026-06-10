from __future__ import annotations

import os
import re
from dataclasses import dataclass

from exegesis_engine.drafting.service import DraftingService

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
IGNORE_WHITESPACE_ENV = "QUAL_DIFF_IGNORE_WHITESPACE"
LARGE_PATCH_THRESHOLD_ENV = "QUAL_DIFF_LARGE_PATCH_THRESHOLD"
MAX_INPUT_CHARS_ENV = "QUAL_DIFF_MAX_INPUT_CHARS"
TRUNCATION_MARKER_ENV = "QUAL_DIFF_TRUNCATION_MARKER"
ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


@dataclass(frozen=True)
class DiffPreviewInput:
    original: str
    proposed: str

    def __post_init__(self) -> None:
        if not isinstance(self.original, str):
            raise TypeError("original must be a string")
        if not isinstance(self.proposed, str):
            raise TypeError("proposed must be a string")


@dataclass(frozen=True)
class PatchApplyInput:
    original: str
    proposed: str

    def __post_init__(self) -> None:
        if not isinstance(self.original, str):
            raise TypeError("original must be a string")
        if not isinstance(self.proposed, str):
            raise TypeError("proposed must be a string")


@dataclass(frozen=True)
class PatchRejectInput:
    original: str
    proposed: str

    def __post_init__(self) -> None:
        if not isinstance(self.original, str):
            raise TypeError("original must be a string")
        if not isinstance(self.proposed, str):
            raise TypeError("proposed must be a string")


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
            normalized.append(line[:-1].rstrip(" \t") + "\n")
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


def _strip_all_whitespace(value: str) -> str:
    lines = value.splitlines(keepends=True)
    normalized: list[str] = []
    for line in lines:
        newline = "\n" if line.endswith("\n") else ""
        body = line[:-1] if newline else line
        body = re.sub(r"[ \t\r]+", "", body)
        normalized.append(body + newline)
    return "".join(normalized)


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
    summary = f"Diff summary: +{added} -{removed} (hunks: {hunks})"
    if _env_enabled(INCLUDE_SUMMARY_DETAILS_ENV):
        changed = added + removed
        net = added - removed
        summary = f"{summary} [changed: {changed}, net: {net:+d}]"
    return summary


def _large_patch_threshold() -> int:
    raw = os.getenv(LARGE_PATCH_THRESHOLD_ENV)
    if raw is None:
        return 0
    try:
        parsed = int(raw.strip())
    except ValueError:
        return 0
    if parsed <= 0:
        return 0
    return parsed


def _max_input_chars() -> int:
    raw = os.getenv(MAX_INPUT_CHARS_ENV)
    if raw is None:
        return 0
    try:
        parsed = int(raw.strip())
    except ValueError:
        return 0
    if parsed <= 0:
        return 0
    return parsed


def _options_banner(*, ignore_trailing_whitespace: bool, suppress_file_headers: bool, max_chars: int) -> str:
    return (
        "Diff options: "
        f"ignore_trailing_whitespace={str(ignore_trailing_whitespace).lower()}, "
        f"ignore_whitespace={str(_env_enabled(IGNORE_WHITESPACE_ENV)).lower()}, "
        f"suppress_file_headers={str(suppress_file_headers).lower()}, "
        f"strip_ansi={str(_env_enabled(STRIP_ANSI_ENV)).lower()}, "
        f"canonicalize_inline_whitespace={str(_env_enabled(CANONICALIZE_INLINE_WHITESPACE_ENV)).lower()}, "
        f"ignore_case={str(_env_enabled(IGNORE_CASE_ENV)).lower()}, "
        f"ignore_edge_blank_lines={str(_env_enabled(IGNORE_EDGE_BLANK_LINES_ENV)).lower()}, "
        f"ignore_all_blank_lines={str(_env_enabled(IGNORE_ALL_BLANK_LINES_ENV)).lower()}, "
        f"max_output_chars={max_chars}, "
        f"truncation_strategy={_truncation_strategy()}, "
        f"truncation_marker={os.getenv(TRUNCATION_MARKER_ENV) or 'default'}, "
        f"large_patch_threshold={_large_patch_threshold()}, "
        f"max_input_chars={_max_input_chars()}"
    )


def _truncation_strategy() -> str:
    raw = os.getenv(TRUNCATION_STRATEGY_ENV)
    if raw is None:
        return "middle"
    value = raw.strip().lower()
    if value in {"middle", "tail", "head", "none"}:
        return value
    return "middle"


def _truncation_marker(omitted: int) -> str:
    custom = os.getenv(TRUNCATION_MARKER_ENV)
    if custom is not None and custom.strip():
        marker = custom.strip()
        if "{omitted}" in marker:
            try:
                return marker.format(omitted=omitted)
            except (ValueError, KeyError, IndexError):
                pass
        return marker
    return f"... diff truncated ({omitted} characters omitted) ..."


def _truncate_diff(diff: str, max_chars: int) -> str:
    strategy = _truncation_strategy()
    if strategy == "none":
        return diff
    if strategy == "tail":
        omitted = len(diff) - max_chars
        return f"{diff[:max_chars]}\n{_truncation_marker(omitted)}"
    elif strategy == "head":
        omitted = len(diff) - max_chars
        return f"{_truncation_marker(omitted)}\n{diff[-max_chars:]}"

    head_chars = max_chars // 2
    tail_chars = max_chars - head_chars
    omitted = len(diff) - (head_chars + tail_chars)
    return (
        f"{diff[:head_chars]}"
        f"{_truncation_marker(omitted)}"
        f"{diff[-tail_chars:]}"
    )


def run_patch_apply(payload: PatchApplyInput) -> str:
    """Accept the proposed changes; delegate actual write to the caller."""
    return _normalize_text(payload.proposed)


def run_patch_reject(payload: PatchRejectInput) -> str:
    """Decline the proposed changes; retain original text."""
    return _normalize_text(payload.original)


def run_diff_preview(payload: DiffPreviewInput) -> str:
    original = _normalize_text(payload.original)
    proposed = _normalize_text(payload.proposed)

    max_in_chars = _max_input_chars()
    if max_in_chars > 0:
        if len(original) > max_in_chars or len(proposed) > max_in_chars:
            return f"Error: input length ({len(original)} or {len(proposed)}) exceeds maximum allowed limit ({max_in_chars} characters)."

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
    if _env_enabled(IGNORE_WHITESPACE_ENV):
        original = _strip_all_whitespace(original)
        proposed = _strip_all_whitespace(proposed)
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
    if not diff:
        return "No diff: inputs are identical."
    max_chars = _max_diff_output_chars()
    banner = ""
    if include_options_banner:
        banner = (
            _options_banner(
                ignore_trailing_whitespace=ignore_trailing_whitespace,
                suppress_file_headers=suppress_file_headers,
                max_chars=max_chars,
            )
            + "\n\n"
        )
    added = 0
    removed = 0
    for line in summary_source.splitlines():
        if line.startswith("+++ ") or line.startswith("--- ") or line.startswith("@@ "):
            continue
        if line.startswith("+"):
            added += 1
        elif line.startswith("-"):
            removed += 1
    total_changes = added + removed
    threshold = _large_patch_threshold()
    warning = ""
    if threshold > 0 and total_changes > threshold:
        warning = f"\nWarning: large patch detected ({total_changes} changes exceed threshold of {threshold})"

    if _env_enabled(SUMMARY_ONLY_ENV):
        return f"{banner}{_summarize_diff(summary_source)}{warning}"

    output = diff
    if len(diff) > max_chars:
        output = _truncate_diff(diff, max_chars)

    if _env_enabled(INCLUDE_SUMMARY_ENV):
        res = f"{banner}{output}\n\n{_summarize_diff(summary_source)}"
    else:
        res = f"{banner}{output}"

    if warning:
        res = f"{res}{warning}"
    return res
