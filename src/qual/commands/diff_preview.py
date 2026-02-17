from __future__ import annotations

from dataclasses import dataclass

from src.qual.drafting.service import DraftingService

MAX_DIFF_OUTPUT_CHARS = 20_000


@dataclass(frozen=True)
class DiffPreviewInput:
    original: str
    proposed: str


def _normalize_text(value: str) -> str:
    # Normalize newlines so diff output is stable across platforms.
    return value.replace("\r\n", "\n").replace("\r", "\n")


def run_diff_preview(payload: DiffPreviewInput) -> str:
    original = _normalize_text(payload.original)
    proposed = _normalize_text(payload.proposed)

    if not original and not proposed:
        return "No diff: both inputs are empty."

    if original == proposed:
        return "No diff: inputs are identical after normalization."

    drafting = DraftingService()
    diff = drafting.propose_diff(original, proposed)
    if not diff:
        return "No diff: inputs are identical."
    if len(diff) > MAX_DIFF_OUTPUT_CHARS:
        head_chars = MAX_DIFF_OUTPUT_CHARS // 2
        tail_chars = MAX_DIFF_OUTPUT_CHARS - head_chars
        omitted = len(diff) - (head_chars + tail_chars)
        return (
            f"{diff[:head_chars]}"
            f"... diff truncated ({omitted} characters omitted) ..."
            f"{diff[-tail_chars:]}"
        )
    return diff
