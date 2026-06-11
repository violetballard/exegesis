from __future__ import annotations

from dataclasses import dataclass

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, Static


PATCH_CARD_APPLY_ID = "patch-card-apply"
PATCH_CARD_REJECT_ID = "patch-card-reject"
PATCH_CARD_TITLE_ID = "patch-card-title"
PATCH_CARD_META_ID = "patch-card-meta"
PATCH_CARD_BODY_ID = "patch-card-body"


@dataclass(frozen=True)
class PatchReviewCardData:
    patch_id: str
    document_title: str
    instruction_text: str
    source_chat_slug: str
    original_text: str = ""
    proposed_text: str = ""
    document_slug: str = ""
    target_range: tuple[int, int] | None = None
    block_insert: bool = False


class PatchReviewCard(Vertical):
    class ApplyRequested(Message):
        def __init__(self, patch_card: "PatchReviewCard", patch_id: str) -> None:
            super().__init__()
            self.patch_card = patch_card
            self.patch_id = patch_id

    class RejectRequested(Message):
        def __init__(self, patch_card: "PatchReviewCard", patch_id: str) -> None:
            super().__init__()
            self.patch_card = patch_card
            self.patch_id = patch_id

    def __init__(self) -> None:
        super().__init__(id="workflow-patch-card")
        self.border_title = "Patch Review"
        self.display = False
        self._data: PatchReviewCardData | None = None

    def compose(self) -> ComposeResult:
        yield Static("", id=PATCH_CARD_TITLE_ID)
        yield Static("", id=PATCH_CARD_META_ID)
        yield Static("", id=PATCH_CARD_BODY_ID)
        with Horizontal(id="workflow-patch-actions"):
            yield Button("Apply", id=PATCH_CARD_APPLY_ID, variant="success")
            yield Button("Reject", id=PATCH_CARD_REJECT_ID, variant="error")

    def show_patch(self, data: PatchReviewCardData) -> None:
        self._data = data
        self.query_one(f"#{PATCH_CARD_TITLE_ID}", Static).update("Revision Proposal")
        self.query_one(f"#{PATCH_CARD_META_ID}", Static).update(
            f"{data.document_title} • from {data.source_chat_slug}"
        )
        self.query_one(f"#{PATCH_CARD_BODY_ID}", Static).update(
            f"Instruction: {data.instruction_text}"
        )
        self.display = True

    def clear_patch(self) -> None:
        self._data = None
        self.display = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if self._data is None:
            return
        if event.button.id == PATCH_CARD_APPLY_ID:
            self.post_message(self.ApplyRequested(self, self._data.patch_id))
        elif event.button.id == PATCH_CARD_REJECT_ID:
            self.post_message(self.RejectRequested(self, self._data.patch_id))


__all__ = [
    "PATCH_CARD_APPLY_ID",
    "PATCH_CARD_BODY_ID",
    "PATCH_CARD_META_ID",
    "PATCH_CARD_REJECT_ID",
    "PATCH_CARD_TITLE_ID",
    "PatchReviewCard",
    "PatchReviewCardData",
]
