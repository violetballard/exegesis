from __future__ import annotations

from dataclasses import dataclass

from src.qual.drafting.service import DraftingService


@dataclass(frozen=True)
class DiffPreviewInput:
    original: str
    proposed: str


def run_diff_preview(payload: DiffPreviewInput) -> str:
    drafting = DraftingService()
    diff = drafting.propose_diff(payload.original, payload.proposed)
    if not diff:
        return "No diff: inputs are identical."
    return diff
