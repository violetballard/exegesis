from __future__ import annotations

import uuid
from datetime import datetime, timezone

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
        if not isinstance(target_document_id, str):
            raise TypeError("target_document_id must be a string")
        if not isinstance(original_text, str):
            raise TypeError("original_text must be a string")
        if not isinstance(proposed_text, str):
            raise TypeError("proposed_text must be a string")

        if target_range is not None:
            if not isinstance(target_range, tuple) or len(target_range) != 2:
                raise TypeError("target_range must be a tuple of two integers")
            start, end = target_range
            if not isinstance(start, int) or not isinstance(end, int):
                raise TypeError("target_range elements must be integers")
            if start < 0:
                raise ValueError("target_range start index cannot be negative")
            if end < start:
                raise ValueError("target_range end index cannot be less than start index")
        else:
            start, end = 0, len(original_text)

        if metadata is not None:
            if not isinstance(metadata, dict):
                raise TypeError("metadata must be a dictionary")
            for key in metadata:
                if not isinstance(key, str):
                    raise TypeError("metadata keys must be string types")
        patch_metadata = dict(metadata or {})
        if "created_at" not in patch_metadata:
            patch_metadata["created_at"] = datetime.now(timezone.utc).isoformat()

        return PatchProposal(
            patch_id=f"patch-{uuid.uuid4()}",
            target_document_id=target_document_id,
            target_range=(start, end),
            original_text=original_text,
            proposed_text=proposed_text,
            metadata=patch_metadata,
        )

    def apply(self, current_content: str, patch: PatchProposal) -> str:
        if not isinstance(current_content, str):
            raise TypeError("current_content must be a string")
        if not isinstance(patch, PatchProposal):
            raise TypeError("patch must be a PatchProposal instance")
        start, end = patch.target_range
        if start < 0 or end < start or end > len(current_content):
            raise ValueError("patch target range is invalid for current content")
        if current_content[start:end] != patch.original_text:
            raise ValueError("patch original text does not match current document content")
        return f"{current_content[:start]}{patch.proposed_text}{current_content[end:]}"

    def reject(self, patch: PatchProposal) -> PatchProposal:
        if not isinstance(patch, PatchProposal):
            raise TypeError("patch must be a PatchProposal instance")
        return patch

    def is_noop(self, patch: PatchProposal) -> bool:
        """Return whether applying the patch would leave the replacement unchanged."""
        if not isinstance(patch, PatchProposal):
            raise TypeError("patch must be a PatchProposal instance")
        return patch.original_text == patch.proposed_text

    def can_apply(self, current_content: str, patch: PatchProposal) -> bool:
        """Return whether the patch can be successfully applied to the current content."""
        if not isinstance(current_content, str):
            raise TypeError("current_content must be a string")
        if not isinstance(patch, PatchProposal):
            raise TypeError("patch must be a PatchProposal instance")
        start, end = patch.target_range
        if start < 0 or end < start or end > len(current_content):
            return False
        return current_content[start:end] == patch.original_text

    def analyze_patch(self, patch: PatchProposal) -> dict[str, object]:
        """Perform a detailed analysis of the proposed patch changes for provenance and dogfooding."""
        if not isinstance(patch, PatchProposal):
            raise TypeError("patch must be a PatchProposal instance")

        original = patch.original_text
        proposed = patch.proposed_text

        char_removed = len(original)
        char_added = len(proposed)
        char_delta = char_added - char_removed

        orig_words = original.split()
        prop_words = proposed.split()
        word_removed = len(orig_words)
        word_added = len(prop_words)
        word_delta = word_added - word_removed

        orig_lines = original.splitlines()
        prop_lines = proposed.splitlines()
        line_removed = len(orig_lines)
        line_added = len(prop_lines)
        line_delta = line_added - line_removed

        import difflib
        matcher = difflib.SequenceMatcher(None, original, proposed)
        similarity = matcher.ratio()

        is_noop = original == proposed
        is_pure_addition = len(original) == 0 and len(proposed) > 0
        is_pure_deletion = len(proposed) == 0 and len(original) > 0

        return {
            "char_removed": char_removed,
            "char_added": char_added,
            "char_delta": char_delta,
            "word_removed": word_removed,
            "word_added": word_added,
            "word_delta": word_delta,
            "line_removed": line_removed,
            "line_added": line_added,
            "line_delta": line_delta,
            "similarity_ratio": similarity,
            "is_noop": is_noop,
            "is_pure_addition": is_pure_addition,
            "is_pure_deletion": is_pure_deletion,
        }
