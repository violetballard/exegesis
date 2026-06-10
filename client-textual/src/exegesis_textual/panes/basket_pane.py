from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from exegesis_textual.panes import PaneCopy

BASKET_PANE_COPY = PaneCopy(
    pane_id="basket-pane",
    title="Basket",
    summary="Promoted excerpts and supporting documents for the draft in focus.",
    bullets=(
        "The basket should contain only excerpts and whole documents.",
        "Excerpts should read like saved selections, with source file context attached.",
        "Documents in the basket should open or select the matching document tab.",
    ),
)

BASKET_EXCERPTS_LIST_ID = "basket-excerpts-list"
BASKET_DOCUMENTS_LIST_ID = "basket-documents-list"


def _fixture_content(filename: str) -> str:
    path = Path(__file__).parents[1] / "workflow" / "prompts" / filename
    try:
        return path.read_text(encoding="utf-8").strip() + "\n"
    except OSError:
        return ""


@dataclass
class BasketEntry:
    slug: str
    kind: str
    title: str
    source: str
    source_document_slug: str | None
    source_document_type: str
    summary: str
    bullets: tuple[str, ...]
    content: str
    document_slug: str | None = None
    source_document_id: str | None = None
    source_status: str = "current"
    captured_at: str | None = None
    selection_start: int | None = None
    selection_end: int | None = None


INITIAL_BASKET_ENTRIES = (
    BasketEntry(
        "basket-document-data-memo-1",
        "document",
        "Document",
        "Data Memo 1",
        "project-demo-essay",
        "memo",
        "A supporting memo promoted into the basket for the demo workflow.",
        (
            "Whole files can live in the basket alongside excerpts.",
            "Selecting this should open or focus the matching document tab.",
            "Memos carry writer intent and should strongly shape drafting.",
        ),
        _fixture_content("data_memo_1.md"),
        document_slug="project-demo-essay",
    ),
)


class BasketPane(Vertical):
    BINDINGS = [
        Binding("delete", "request_delete", "Delete", priority=True),
        Binding("backspace", "request_delete", "Delete", priority=True),
    ]

    class DeleteRequested(Message):
        def __init__(self, basket_pane: "BasketPane") -> None:
            super().__init__()
            self.basket_pane = basket_pane

    def __init__(self) -> None:
        super().__init__(id=BASKET_PANE_COPY.pane_id, classes="shell-pane")
        self.border_title = BASKET_PANE_COPY.title
        self._entries: dict[str, BasketEntry] = {}

    def compose(self) -> ComposeResult:
        with Horizontal(id="basket-columns"):
            with BasketColumn("Excerpts", id="basket-excerpts-column"):
                yield OptionList(id=BASKET_EXCERPTS_LIST_ID)
            with BasketColumn("Documents", id="basket-documents-column"):
                yield OptionList(id=BASKET_DOCUMENTS_LIST_ID)

    def on_mount(self) -> None:
        self._sync_subtitle()

    @property
    def entries(self) -> dict[str, BasketEntry]:
        return self._entries

    def focus_primary(self) -> None:
        self.query_one(f"#{BASKET_EXCERPTS_LIST_ID}", OptionList).focus()

    def add_entry(self, entry: BasketEntry) -> None:
        list_id = BASKET_EXCERPTS_LIST_ID if entry.kind == "excerpt" else BASKET_DOCUMENTS_LIST_ID
        target_list = self.query_one(f"#{list_id}", OptionList)
        if entry.slug in self._entries:
            old = self._entries[entry.slug]
            old_list_id = BASKET_EXCERPTS_LIST_ID if old.kind == "excerpt" else BASKET_DOCUMENTS_LIST_ID
            self.query_one(f"#{old_list_id}", OptionList).remove_option(entry.slug)
        self._entries[entry.slug] = entry
        prompt = basket_entry_prompt(entry)
        target_list.add_option(Option(prompt, id=entry.slug))
        self._sync_subtitle()

    def get_entry(self, slug: str | None) -> BasketEntry | None:
        if slug is None:
            return None
        return self._entries.get(slug)

    def selected_entry(self) -> BasketEntry | None:
        for list_id in (BASKET_EXCERPTS_LIST_ID, BASKET_DOCUMENTS_LIST_ID):
            option_list = self.query_one(f"#{list_id}", OptionList)
            option = option_list.highlighted_option
            if option is not None and option.id in self._entries:
                return self._entries[option.id]
        return None

    def remove_entry(self, slug: str | None) -> BasketEntry | None:
        entry = self.get_entry(slug)
        if entry is None:
            return None
        list_id = BASKET_EXCERPTS_LIST_ID if entry.kind == "excerpt" else BASKET_DOCUMENTS_LIST_ID
        self.query_one(f"#{list_id}", OptionList).remove_option(entry.slug)
        self._entries.pop(entry.slug, None)
        self._sync_subtitle()
        return entry

    def remove_selected_entry(self) -> BasketEntry | None:
        entry = self.selected_entry()
        return self.remove_entry(entry.slug if entry is not None else None)

    def has_list_focus(self) -> bool:
        return any(
            self.query_one(f"#{list_id}", OptionList).has_focus
            for list_id in (BASKET_EXCERPTS_LIST_ID, BASKET_DOCUMENTS_LIST_ID)
        )

    def action_request_delete(self) -> None:
        if self.has_list_focus():
            self.post_message(self.DeleteRequested(self))

    def _sync_subtitle(self) -> None:
        excerpt_count = sum(1 for entry in self._entries.values() if entry.kind == "excerpt")
        document_count = sum(1 for entry in self._entries.values() if entry.kind == "document")
        approx_tokens = sum(max(1, len(entry.content) // 4) for entry in self._entries.values())
        self.border_subtitle = f"{excerpt_count} excerpts • {document_count} documents • ~{approx_tokens:,} tokens"


def basket_source_status_label(source_status: str) -> str:
    return {
        "source_deleted": "deleted",
    }.get(source_status, source_status.replace("_", " "))


def basket_source_status_style(source_status: str) -> str:
    return {
        "current": "green",
        "restored": "green",
        "changed": "yellow",
        "trashed": "orange3",
        "source_deleted": "red",
    }.get(source_status, "white")


def basket_entry_prompt(entry: BasketEntry) -> Text:
    return Text.assemble(
        (entry.source, "bold"),
        " ",
        (f"[{basket_source_status_label(entry.source_status)}]", basket_source_status_style(entry.source_status)),
    )


BASKET_ENTRY_MAP = {entry.slug: entry for entry in INITIAL_BASKET_ENTRIES}


class BasketColumn(Vertical):
    def __init__(self, title: str, *, id: str) -> None:
        super().__init__(classes="basket-column", id=id)
        self.border_title = title


__all__ = [
    "BASKET_DOCUMENTS_LIST_ID",
    "BASKET_ENTRY_MAP",
    "BASKET_EXCERPTS_LIST_ID",
    "BASKET_PANE_COPY",
    "BasketEntry",
    "BasketPane",
    "basket_entry_prompt",
    "basket_source_status_label",
    "basket_source_status_style",
]
