from __future__ import annotations

from dataclasses import dataclass

from src.qual.drafting.service import DraftingService


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
    return diff
