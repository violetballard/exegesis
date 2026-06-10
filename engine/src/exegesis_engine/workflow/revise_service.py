from __future__ import annotations

import uuid

from exegesis_engine.drafting.service import DraftingService

from exegesis_engine.patches.patch_model import PatchProposal
from exegesis_engine.patches.patch_service import PatchService
from exegesis_engine.state.models import BasketItem, WorkflowCard


class ReviseService:
    def __init__(self) -> None:
        self._drafting = DraftingService()
        self._patches = PatchService()

    def draft_from_basket(
        self,
        basket_items: list[BasketItem],
        *,
        context_snippets: dict[str, list[str]] | None = None,
        prior_context_summary: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> WorkflowCard:
        if not isinstance(basket_items, list):
            raise TypeError("basket_items must be a list")
        for item in basket_items:
            if not isinstance(item, BasketItem):
                raise TypeError("basket_items must contain only BasketItem instances")

        if context_snippets is not None:
            if not isinstance(context_snippets, dict):
                raise TypeError("context_snippets must be a dictionary")
            for k, v in context_snippets.items():
                if not isinstance(k, str):
                    raise TypeError("context_snippets keys must be strings")
                if "\x00" in k:
                    raise ValueError("context_snippets keys cannot contain null bytes")
                if not isinstance(v, list):
                    raise TypeError("context_snippets values must be lists")
                for snippet in v:
                    if not isinstance(snippet, str):
                        raise TypeError("context_snippets list elements must be strings")
                    if "\x00" in snippet:
                        raise ValueError("context_snippets list elements cannot contain null bytes")
        if prior_context_summary is not None and not isinstance(prior_context_summary, str):
            raise TypeError("prior_context_summary must be a string")
        if metadata is not None:
            if not isinstance(metadata, dict):
                raise TypeError("metadata must be a dictionary")
            for key in metadata:
                if not isinstance(key, str):
                    raise TypeError("metadata keys must be string types")

        if not basket_items:
            body = "Basket is empty. Add context before drafting."
        else:
            lines = []
            if prior_context_summary:
                lines.append(f"Prior session context:\n{prior_context_summary}\n")
            for item in basket_items:
                snippets = (context_snippets or {}).get(item.id, [])
                if snippets:
                    for idx, snippet in enumerate(snippets):
                        excerpt = snippet[:200].strip()
                        if len(snippets) > 1:
                            lines.append(f"- {item.label} ({item.item_type}) [{idx+1}]: {excerpt}")
                        else:
                            lines.append(f"- {item.label} ({item.item_type}): {excerpt}")
                else:
                    lines.append(f"- Draft against {item.label}")
            body = "\n".join(lines)

        card_metadata = {
            "item_count": len(basket_items),
            "snippet_count": sum(len(v) for v in (context_snippets or {}).values()),
        }
        if metadata is not None:
            card_metadata.update(metadata)

        return WorkflowCard(
            id=f"draft-{uuid.uuid4()}",
            card_type="draft",
            title="Draft From Basket",
            body=body,
            metadata=card_metadata,
        )

    def revise_selection(
        self,
        *,
        document_id: str,
        original_text: str,
        proposed_text: str,
        target_range: tuple[int, int],
        metadata: dict[str, object] | None = None,
    ) -> tuple[PatchProposal, str]:
        if not isinstance(document_id, str):
            raise TypeError("document_id must be a string")
        if not document_id.strip():
            raise ValueError("document_id cannot be empty or whitespace only")
        if "\x00" in document_id:
            raise ValueError("document_id cannot contain null bytes")
        if not isinstance(original_text, str):
            raise TypeError("original_text must be a string")
        if "\x00" in original_text:
            raise ValueError("original_text cannot contain null bytes")
        if not isinstance(proposed_text, str):
            raise TypeError("proposed_text must be a string")
        if "\x00" in proposed_text:
            raise ValueError("proposed_text cannot contain null bytes")
        if not isinstance(target_range, tuple) or len(target_range) != 2:
            raise TypeError("target_range must be a tuple of two integers")
        start, end = target_range
        if not isinstance(start, int) or not isinstance(end, int) or isinstance(start, bool) or isinstance(end, bool):
            raise TypeError("target_range elements must be integers")
        if start < 0:
            raise ValueError("target_range start index cannot be negative")
        if end < start:
            raise ValueError("target_range end index cannot be less than start index")
        if metadata is not None:
            if not isinstance(metadata, dict):
                raise TypeError("metadata must be a dictionary")
            for key in metadata:
                if not isinstance(key, str):
                    raise TypeError("metadata keys must be string types")

        patch = self._patches.create_patch(
            target_document_id=document_id,
            original_text=original_text,
            proposed_text=proposed_text,
            target_range=target_range,
            metadata=metadata,
        )
        preview = self._drafting.propose_diff(original_text, proposed_text)
        return patch, preview
