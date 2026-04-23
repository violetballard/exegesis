from __future__ import annotations

import hashlib
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
ORIGINAL_LABEL_ENV = "QUAL_DIFF_ORIGINAL_LABEL"
PROPOSED_LABEL_ENV = "QUAL_DIFF_PROPOSED_LABEL"
OUTPUT_FORMAT_ENV = "QUAL_DIFF_OUTPUT_FORMAT"
INCLUDE_FINGERPRINT_ENV = "QUAL_DIFF_INCLUDE_FINGERPRINT"
MAX_FILE_LABEL_CHARS = 120
MAX_TRUNCATION_MARKER_CHARS = 120
ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
COMMAND_NAME = "diff-preview"


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


def _resolve_file_label(env_name: str, default: str) -> str:
    raw = os.getenv(env_name)
    if raw is None:
        return default
    label = _strip_ansi(raw)
    label = re.sub(r"[\x00-\x1f\x7f]+", " ", label)
    label = " ".join(label.split())
    label = re.sub(r"^(?:\+\+\+|---)\s*", "", label)
    label = label[:MAX_FILE_LABEL_CHARS].rstrip()
    if not label:
        return default
    return label


def _sanitize_inline_env_text(value: str, *, max_chars: int) -> str:
    sanitized = _strip_ansi(value)
    sanitized = re.sub(r"[\x00-\x1f\x7f]+", " ", sanitized)
    sanitized = " ".join(sanitized.split())
    return sanitized[:max_chars].rstrip()


def _apply_file_labels(diff: str) -> tuple[str, bool]:
    lines = diff.splitlines(keepends=True)
    if len(lines) < 2 or not lines[0].startswith("--- ") or not lines[1].startswith("+++ "):
        return diff, False
    original_label = _resolve_file_label(ORIGINAL_LABEL_ENV, "original")
    proposed_label = _resolve_file_label(PROPOSED_LABEL_ENV, "proposed")
    lines[0] = f"--- {original_label}\n"
    lines[1] = f"+++ {proposed_label}\n"
    return "".join(lines), True


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


def _diff_stats(diff: str) -> dict[str, int]:
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
    return {
        "added": added,
        "removed": removed,
        "hunks": hunks,
        "changed": added + removed,
        "net": added - removed,
    }


def _summarize_diff(diff: str) -> str:
    stats = _diff_stats(diff)
    summary = f"Diff summary: +{stats['added']} -{stats['removed']} (hunks: {stats['hunks']})"
    if _env_enabled(INCLUDE_SUMMARY_DETAILS_ENV):
        summary = f"{summary} [changed: {stats['changed']}, net: {stats['net']:+d}]"
    return summary


def _resolve_output_format() -> str:
    raw = os.getenv(OUTPUT_FORMAT_ENV)
    if raw is None:
        return "text"
    value = raw.strip().lower()
    if value == "json":
        return "json"
    return "text"


def _json_result(payload: dict[str, object]) -> str:
    return json.dumps(payload, sort_keys=True)


def _diff_fingerprint(diff: str) -> dict[str, object]:
    digest = hashlib.sha256(diff.encode("utf-8")).hexdigest()
    return {
        "algorithm": "sha256",
        "char_count": len(diff),
        "line_count": len(diff.splitlines()),
        "sha256": digest,
    }


def _labels_payload(*, applied: bool, original_label: str, proposed_label: str) -> dict[str, object]:
    return {
        "applied": applied,
        "original": original_label,
        "proposed": proposed_label,
    }


def _options_payload(
    *,
    ignore_trailing_whitespace: bool,
    suppress_file_headers: bool,
    include_summary: bool,
    include_options_banner: bool,
    max_chars: int,
) -> dict[str, object]:
    return {
        "canonicalize_inline_whitespace": _env_enabled(CANONICALIZE_INLINE_WHITESPACE_ENV),
        "ignore_all_blank_lines": _env_enabled(IGNORE_ALL_BLANK_LINES_ENV),
        "ignore_case": _env_enabled(IGNORE_CASE_ENV),
        "ignore_edge_blank_lines": _env_enabled(IGNORE_EDGE_BLANK_LINES_ENV),
        "ignore_trailing_whitespace": ignore_trailing_whitespace,
        "include_options_banner": include_options_banner,
        "include_summary": include_summary,
        "max_output_chars": max_chars,
        "strip_ansi": _env_enabled(STRIP_ANSI_ENV),
        "suppress_file_headers": suppress_file_headers,
        "truncation_strategy": _truncation_strategy(),
    }


def _no_diff_payload(
    message: str,
    *,
    summary_only: bool,
    original_label: str,
    proposed_label: str,
    ignore_trailing_whitespace: bool,
    suppress_file_headers: bool,
    include_summary: bool,
    include_options_banner: bool,
    max_chars: int,
) -> dict[str, object]:
    return {
        "command": COMMAND_NAME,
        "diff": "",
        "fingerprint": None,
        "labels": _labels_payload(
            applied=False,
            original_label=original_label,
            proposed_label=proposed_label,
        ),
        "message": message,
        "options": _options_payload(
            ignore_trailing_whitespace=ignore_trailing_whitespace,
            suppress_file_headers=suppress_file_headers,
            include_summary=include_summary,
            include_options_banner=include_options_banner,
            max_chars=max_chars,
        ),
        "status": "no_diff",
        "summary": None,
        "summary_only": summary_only,
        "truncated": False,
    }


def _no_diff_result(
    message: str,
    *,
    summary_only: bool,
    original_label: str,
    proposed_label: str,
    ignore_trailing_whitespace: bool,
    suppress_file_headers: bool,
    include_summary: bool,
    include_options_banner: bool,
    max_chars: int,
) -> str:
    if _resolve_output_format() == "json":
        return _json_result(
            _no_diff_payload(
                message,
                summary_only=summary_only,
                original_label=original_label,
                proposed_label=proposed_label,
                ignore_trailing_whitespace=ignore_trailing_whitespace,
                suppress_file_headers=suppress_file_headers,
                include_summary=include_summary,
                include_options_banner=include_options_banner,
                max_chars=max_chars,
            )
        )
    return message


def _emitted_diff_payload(*, output: str, summary_only: bool) -> str:
    if summary_only:
        return ""
    return output


def _fingerprint_source_payload(*, diff: str, output: str, summary_only: bool) -> str:
    # Fingerprints must identify the reviewed diff, even when the rendered view
    # is collapsed to summary-only text for a thin CLI surface.
    if summary_only:
        return diff
    return output


def _emitted_fingerprint_payload(fingerprint: dict[str, object]) -> dict[str, object] | None:
    if not _env_enabled(INCLUDE_FINGERPRINT_ENV):
        return None
    return fingerprint


def _text_or_json_result(
    *,
    summary_source: str,
    emitted_diff: str,
    max_chars: int,
    suppress_file_headers: bool,
    ignore_trailing_whitespace: bool,
    summary_only: bool,
    include_summary: bool,
    include_options_banner: bool,
    truncated: bool,
    labels_applied: bool,
    original_label: str,
    proposed_label: str,
    fingerprint: dict[str, object],
) -> str:
    banner = ""
    summary = _summarize_diff(summary_source)
    emitted_fingerprint = _emitted_fingerprint_payload(fingerprint)
    fingerprint_line = ""
    if emitted_fingerprint is not None:
        fingerprint_line = f"Diff fingerprint: sha256:{emitted_fingerprint['sha256']}"
    if include_options_banner:
        banner = (
            _options_banner(
                ignore_trailing_whitespace=ignore_trailing_whitespace,
                suppress_file_headers=suppress_file_headers,
                max_chars=max_chars,
            )
            + "\n\n"
        )
    if _resolve_output_format() == "json":
        return _json_result(
            {
                "command": COMMAND_NAME,
                "diff": emitted_diff,
                "fingerprint": emitted_fingerprint,
                "labels": _labels_payload(
                    applied=labels_applied,
                    original_label=original_label,
                    proposed_label=proposed_label,
                ),
                "options": _options_payload(
                    ignore_trailing_whitespace=ignore_trailing_whitespace,
                    suppress_file_headers=suppress_file_headers,
                    include_summary=include_summary,
                    include_options_banner=include_options_banner,
                    max_chars=max_chars,
                ),
                "status": "ok",
                "summary": {
                    "details_enabled": _env_enabled(INCLUDE_SUMMARY_DETAILS_ENV),
                    "stats": _diff_stats(summary_source),
                    "text": summary,
                },
                "summary_only": summary_only,
                "truncated": truncated,
            }
        )
    if summary_only:
        if fingerprint_line:
            return f"{banner}{summary}\n{fingerprint_line}"
        return f"{banner}{summary}"
    if include_summary:
        result = f"{banner}{emitted_diff}\n\n{summary}"
        if fingerprint_line:
            return f"{result}\n{fingerprint_line}"
        return result
    if fingerprint_line:
        return f"{banner}{emitted_diff}\n\n{fingerprint_line}"
    return f"{banner}{emitted_diff}"


def _options_banner(*, ignore_trailing_whitespace: bool, suppress_file_headers: bool, max_chars: int) -> str:
    return (
        "Diff options: "
        f"ignore_trailing_whitespace={str(ignore_trailing_whitespace).lower()}, "
        f"suppress_file_headers={str(suppress_file_headers).lower()}, "
        f"strip_ansi={str(_env_enabled(STRIP_ANSI_ENV)).lower()}, "
        f"canonicalize_inline_whitespace={str(_env_enabled(CANONICALIZE_INLINE_WHITESPACE_ENV)).lower()}, "
        f"ignore_case={str(_env_enabled(IGNORE_CASE_ENV)).lower()}, "
        f"ignore_edge_blank_lines={str(_env_enabled(IGNORE_EDGE_BLANK_LINES_ENV)).lower()}, "
        f"ignore_all_blank_lines={str(_env_enabled(IGNORE_ALL_BLANK_LINES_ENV)).lower()}, "
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


def _truncation_marker(omitted: int) -> str:
    custom = os.getenv(TRUNCATION_MARKER_ENV)
    if custom is not None:
        marker = _sanitize_inline_env_text(custom, max_chars=MAX_TRUNCATION_MARKER_CHARS)
        if marker:
            return marker
    return f"... diff truncated ({omitted} characters omitted) ..."


def _truncate_diff(diff: str, max_chars: int) -> str:
    strategy = _truncation_strategy()
    separator = "\n" if strategy == "tail" else ""
    omitted = max(len(diff) - max_chars, 0)
    marker = _truncation_marker(omitted)

    while True:
        visible_budget = max_chars - len(separator) - len(marker)
        if visible_budget <= 0:
            return marker[:max_chars]
        new_omitted = max(len(diff) - visible_budget, 0)
        new_marker = _truncation_marker(new_omitted)
        if new_omitted == omitted and new_marker == marker:
            break
        omitted = new_omitted
        marker = new_marker

    if strategy == "tail":
        return f"{diff[:visible_budget]}{separator}{marker}"

    lines = diff.splitlines(keepends=True)
    header_prefix = ""
    if len(lines) >= 2 and lines[0].startswith("--- ") and lines[1].startswith("+++ "):
        header_prefix = "".join(lines[:2])
    if header_prefix:
        if len(header_prefix) >= visible_budget:
            return f"{header_prefix[:visible_budget]}{marker}"
        remaining = diff[len(header_prefix):]
        remaining_budget = visible_budget - len(header_prefix)
        head_chars = remaining_budget // 2
        tail_chars = remaining_budget - head_chars
        return f"{header_prefix}{remaining[:head_chars]}{marker}{remaining[-tail_chars:]}"

    head_chars = visible_budget // 2
    tail_chars = visible_budget - head_chars
    return f"{diff[:head_chars]}{marker}{diff[-tail_chars:]}"


def run_diff_preview(payload: DiffPreviewInput) -> str:
    original = _normalize_text(payload.original)
    proposed = _normalize_text(payload.proposed)
    ignore_trailing_whitespace = _env_enabled(IGNORE_TRAILING_WHITESPACE_ENV)
    suppress_file_headers = _env_enabled(SUPPRESS_FILE_HEADERS_ENV)
    include_options_banner = _env_enabled(INCLUDE_OPTIONS_BANNER_ENV)
    summary_only = _env_enabled(SUMMARY_ONLY_ENV)
    include_summary = _env_enabled(INCLUDE_SUMMARY_ENV)
    max_chars = _max_diff_output_chars()
    original_label = _resolve_file_label(ORIGINAL_LABEL_ENV, "original")
    proposed_label = _resolve_file_label(PROPOSED_LABEL_ENV, "proposed")

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
        return _no_diff_result(
            "No diff: both inputs are empty.",
            summary_only=summary_only,
            original_label=original_label,
            proposed_label=proposed_label,
            ignore_trailing_whitespace=ignore_trailing_whitespace,
            suppress_file_headers=suppress_file_headers,
            include_summary=include_summary,
            include_options_banner=include_options_banner,
            max_chars=max_chars,
        )

    if original == proposed:
        return _no_diff_result(
            "No diff: inputs are identical after normalization.",
            summary_only=summary_only,
            original_label=original_label,
            proposed_label=proposed_label,
            ignore_trailing_whitespace=ignore_trailing_whitespace,
            suppress_file_headers=suppress_file_headers,
            include_summary=include_summary,
            include_options_banner=include_options_banner,
            max_chars=max_chars,
        )

    drafting = DraftingService()
    diff = drafting.propose_diff(original, proposed)
    summary_source = diff
    diff, labels_applied = _apply_file_labels(diff)
    if suppress_file_headers:
        diff = _suppress_file_headers(diff)
    if not diff:
        return _no_diff_result(
            "No diff: inputs are identical.",
            summary_only=summary_only,
            original_label=original_label,
            proposed_label=proposed_label,
            ignore_trailing_whitespace=ignore_trailing_whitespace,
            suppress_file_headers=suppress_file_headers,
            include_summary=include_summary,
            include_options_banner=include_options_banner,
            max_chars=max_chars,
        )
    output = diff
    truncated = False
    if len(diff) > max_chars:
        output = _truncate_diff(diff, max_chars)
        truncated = True
    emitted_diff = _emitted_diff_payload(output=output, summary_only=summary_only)
    fingerprint = _diff_fingerprint(
        _fingerprint_source_payload(diff=diff, output=output, summary_only=summary_only)
    )

    return _text_or_json_result(
        summary_source=summary_source,
        emitted_diff=emitted_diff,
        max_chars=max_chars,
        suppress_file_headers=suppress_file_headers,
        ignore_trailing_whitespace=ignore_trailing_whitespace,
        summary_only=summary_only,
        include_summary=include_summary,
        include_options_banner=include_options_banner,
        truncated=truncated,
        labels_applied=labels_applied,
        original_label=original_label,
        proposed_label=proposed_label,
        fingerprint=fingerprint,
    )
