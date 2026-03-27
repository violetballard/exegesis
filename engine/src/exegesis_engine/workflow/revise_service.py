from __future__ import annotations

from exegesis_engine.drafting.service import DraftingService

from exegesis_engine.patches.patch_model import PatchProposal
from exegesis_engine.patches.patch_service import PatchService
from exegesis_engine.state.models import BasketItem, WorkflowCard


class ReviseService:
    def __init__(self) -> None:
        self._drafting = DraftingService()
        self._patches = PatchService()

    def draft_from_basket(self, basket_items: list[BasketItem]) -> WorkflowCard:
        if not basket_items:
            body = "Basket is empty. Add context before drafting."
        else:
            body = "\n".join(f"- Draft against {item.label}" for item in basket_items)
        return WorkflowCard(
            id="draft-from-basket",
            card_type="message",
            title="Draft From Basket",
            body=body,
            metadata={"item_count": len(basket_items)},
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
        patch = self._patches.create_patch(
            target_document_id=document_id,
            original_text=original_text,
            proposed_text=proposed_text,
            target_range=target_range,
            metadata=metadata,
        )
        preview = self._drafting.propose_diff(original_text, proposed_text)
        return patch, preview
