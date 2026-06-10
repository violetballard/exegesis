from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol
from uuid import uuid4


@dataclass(frozen=True)
class DocumentSelectionLike:
    document_id: str
    start: int
    end: int
    selected_text: str


@dataclass(frozen=True)
class PatchProposalLike:
    patch_id: str
    document_id: str
    target_range: tuple[int, int]
    original_text: str
    proposed_text: str
    instruction_text: str
    source_chat_slug: str
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class UpdatedDocumentLike:
    document_id: str
    patch_id: str
    target_range: tuple[int, int]
    proposed_text: str


class RewriteSessionAdapter(Protocol):
    def set_selection(
        self,
        *,
        document_id: str,
        start: int,
        end: int,
        selected_text: str,
    ) -> DocumentSelectionLike: ...

    def revise_selection(
        self,
        *,
        document_id: str,
        instruction_text: str,
        source_chat_slug: str,
        proposed_text: str | None = None,
    ) -> PatchProposalLike: ...

    def apply_patch(self, patch_id: str) -> UpdatedDocumentLike: ...

    def reject_patch(self, patch_id: str) -> PatchProposalLike: ...


class MockRewriteSessionAdapter:
    def __init__(self) -> None:
        self._selections: dict[str, DocumentSelectionLike] = {}
        self._patches: dict[str, PatchProposalLike] = {}

    def set_selection(
        self,
        *,
        document_id: str,
        start: int,
        end: int,
        selected_text: str,
    ) -> DocumentSelectionLike:
        selection = DocumentSelectionLike(
            document_id=document_id,
            start=start,
            end=end,
            selected_text=selected_text,
        )
        self._selections[document_id] = selection
        return selection

    def revise_selection(
        self,
        *,
        document_id: str,
        instruction_text: str,
        source_chat_slug: str,
        proposed_text: str | None = None,
    ) -> PatchProposalLike:
        selection = self._selections.get(document_id)
        if selection is None:
            raise RuntimeError("Document selection is required before revising")
        normalized_instruction = instruction_text.strip()
        if not normalized_instruction:
            raise RuntimeError("Rewrite instruction is required")
        resolved_proposed = proposed_text.strip() if proposed_text is not None else _mock_rewrite(selection.selected_text, normalized_instruction)
        if not resolved_proposed:
            raise RuntimeError("Rewrite proposal text is required")
        proposal = PatchProposalLike(
            patch_id=f"patch-{uuid4()}",
            document_id=document_id,
            target_range=(selection.start, selection.end),
            original_text=selection.selected_text,
            proposed_text=resolved_proposed,
            instruction_text=normalized_instruction,
            source_chat_slug=source_chat_slug,
            metadata={"source": "mock_rewrite_adapter"},
        )
        self._patches[proposal.patch_id] = proposal
        return proposal

    def apply_patch(self, patch_id: str) -> UpdatedDocumentLike:
        proposal = self._patches.pop(patch_id)
        return UpdatedDocumentLike(
            document_id=proposal.document_id,
            patch_id=proposal.patch_id,
            target_range=proposal.target_range,
            proposed_text=proposal.proposed_text,
        )

    def reject_patch(self, patch_id: str) -> PatchProposalLike:
        return self._patches.pop(patch_id)


def _mock_rewrite(original_text: str, instruction_text: str) -> str:
    normalized = " ".join(original_text.split())
    lowered = instruction_text.casefold()
    if "tighten" in lowered or "shorten" in lowered or "trim" in lowered:
        words = normalized.split()
        kept = max(1, min(len(words) - 1, int(len(words) * 0.7))) if len(words) > 1 else 1
        tightened = " ".join(words[:kept]).strip()
        return tightened if tightened != normalized else f"{normalized}."
    if "expand" in lowered or "develop" in lowered:
        return f"{normalized} This revision expands the idea to follow the requested direction."
    if "clarify" in lowered:
        return f"{normalized} This version clarifies the point more directly."
    return f"{normalized} Revised toward: {instruction_text.strip()}."


__all__ = [
    "DocumentSelectionLike",
    "MockRewriteSessionAdapter",
    "PatchProposalLike",
    "RewriteSessionAdapter",
    "UpdatedDocumentLike",
]
