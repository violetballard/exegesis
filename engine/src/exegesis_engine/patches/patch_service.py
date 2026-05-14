from __future__ import annotations

import uuid

from exegesis_engine.patches.patch_model import PatchProposal


class PatchService:
    def create_patch(
        self,
        *,
        target_document_id: str,
        original_text: str,
        proposed_text: str,
        target_range: tuple[int, int] | None = None,
        metadata: dict[str, object] | None = None,
    ) -> PatchProposal:
        start, end = target_range if target_range is not None else (0, len(original_text))
        return PatchProposal(
            patch_id=f"patch-{uuid.uuid4()}",
            target_document_id=target_document_id,
            target_range=(start, end),
            original_text=original_text,
            proposed_text=proposed_text,
            metadata=dict(metadata or {}),
        )

    def apply(self, current_content: str, patch: PatchProposal) -> str:
        start, end = patch.target_range
        if start < 0 or end < start or end > len(current_content):
            raise ValueError("patch target range is invalid for current content")
        if current_content[start:end] != patch.original_text:
            raise ValueError("patch original text does not match current document content")
        return f"{current_content[:start]}{patch.proposed_text}{current_content[end:]}"

    def reject(self, patch: PatchProposal) -> PatchProposal:
        return patch
