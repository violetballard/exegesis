from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from textual.actions import SkipAction
from textual.app import ComposeResult
from rich.text import Text
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Static, TabPane, TabbedContent, TextArea
from textual.document._document import Selection

from exegesis_textual.panes import PaneCopy
from exegesis_textual.services.clipboard import read_system_clipboard, write_system_clipboard

DOCUMENT_PANE_COPY = PaneCopy(
    pane_id="document-pane",
    title="Document",
    summary="Primary writing viewport for the open document.",
    bullets=(
        "Open documents appear as tabs.",
        "Drafting inserts generated text into the active document.",
        "Rewrite proposals appear inline until applied or rejected.",
    ),
)

DOCUMENT_TABBED_CONTENT_ID = "document-tabs"
DOCUMENT_TOOLBAR_ID = "document-toolbar"
DOCUMENT_ADD_EXCERPT_ID = "document-add-excerpt"
DOCUMENT_ADD_FILE_ID = "document-add-file"
DOCUMENT_SAVE_BUTTON_ID = "document-save"
DOCUMENT_CLOSE_BUTTON_ID = "document-close-tab"
CURRENT_DRAFT_SLUG = "current-draft"
DEFAULT_DOCUMENT_FIXTURE_DIR = Path(__file__).parents[1] / "workflow" / "prompts"


@dataclass
class DocumentFixture:
    slug: str
    title: str
    location: str
    summary: str
    content: str
    document_type: str
    closable: bool = True
    is_transcript: bool = False


@dataclass(frozen=True)
class DocumentSelectionSnapshot:
    start: int
    end: int
    selected_text: str


@dataclass(frozen=True)
class PendingRewritePreview:
    patch_id: str
    document_slug: str
    target_range: tuple[int, int]
    original_text: str
    proposed_text: str
    instruction_text: str
    source_chat_slug: str


DocumentViewStatus = str


class SystemClipboardTextArea(TextArea):
    """TextArea with host OS clipboard support for packaged terminal shells."""

    def action_copy(self) -> None:
        selected_text = self.selected_text
        if not selected_text:
            raise SkipAction()
        super().action_copy()
        write_system_clipboard(selected_text)

    def action_cut(self) -> None:
        before_clipboard = self.app.clipboard
        super().action_cut()
        if self.app.clipboard != before_clipboard:
            write_system_clipboard(self.app.clipboard)

    def action_paste(self) -> None:
        if self.read_only:
            return
        clipboard = read_system_clipboard()
        if clipboard is None:
            clipboard = self.app.clipboard
        if not clipboard:
            raise SkipAction()
        if result := self._replace_via_keyboard(clipboard, *self.selection):
            self.move_cursor(result.end_location)


def document_fixture_dir() -> Path:
    configured = os.environ.get("EXEGESIS_DOCUMENT_FIXTURE_DIR")
    if configured:
        return Path(configured).expanduser()
    return DEFAULT_DOCUMENT_FIXTURE_DIR


def load_document_fixture_content(filename: str) -> str:
    path = document_fixture_dir() / filename
    try:
        content = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise RuntimeError(f"Document fixture is unavailable: {path} ({exc})") from exc
    if not content:
        raise RuntimeError(f"Document fixture is empty: {path}")
    return f"{content}\n"


DOCUMENT_FIXTURES = {
    CURRENT_DRAFT_SLUG: DocumentFixture(
        slug=CURRENT_DRAFT_SLUG,
        title="current_draft.md",
        location="current_draft.md",
        summary="The primary manuscript for the project and the default open writing tab.",
        content=load_document_fixture_content("current_draft.md"),
        document_type="draft",
        closable=True,
    ),
    "project-demo-essay": DocumentFixture(
        slug="project-demo-essay",
        title="Data Memo 1",
        location="data_memo_1.md",
        summary="Browser-first demo manuscript for the core writing flow.",
        content=load_document_fixture_content("data_memo_1.md"),
        document_type="memo",
    ),
    "project-longform-essay": DocumentFixture(
        slug="project-longform-essay",
        title="Summary 1",
        location="summary_1.md",
        summary="A heavier longform draft for testing multi-document editing.",
        content=load_document_fixture_content("summary_1.md"),
        document_type="summary",
    ),
    "project-notebook": DocumentFixture(
        slug="project-notebook",
        title="Transcript 1 - Participant 1 - 5.1.26",
        location="transcript_1_participant_1_5_1_26.md",
        summary="Notebook-style research notes that should feel editable and secondary to the main draft.",
        content=load_document_fixture_content("transcript_1_participant_1_5_1_26.md"),
        document_type="transcript",
        is_transcript=True,
    ),
    "project-lit-review": DocumentFixture(
        slug="project-lit-review",
        title="Article 1 - Last, First - Title",
        location="article_1_last_first_title.md",
        summary="Source-heavy support material for testing tabbed project browsing.",
        content=load_document_fixture_content("article_1_last_first_title.md"),
        document_type="literature",
    ),
}


def register_document_fixture(
    *,
    slug: str,
    title: str,
    location: str,
    summary: str,
    content: str,
    document_type: str,
    is_transcript: bool = False,
) -> None:
    DOCUMENT_FIXTURES[slug] = DocumentFixture(
        slug=slug,
        title=title,
        location=location,
        summary=summary,
        content=content,
        document_type=document_type,
        is_transcript=is_transcript,
    )


def render_review_document_text(document_text: str, preview: PendingRewritePreview) -> str:
    start, end = preview.target_range
    before = document_text[:start]
    after = document_text[end:]
    review_block = _render_review_block(preview)
    return f"{before}{review_block}{after}"


def render_review_document_rich(document_text: str, preview: PendingRewritePreview) -> Text:
    start, end = preview.target_range
    before = document_text[:start]
    after = document_text[end:]
    rich_text = Text()
    rich_text.append(before)
    rich_text.append(_render_review_block_rich(preview))
    rich_text.append(after)
    return rich_text


def apply_preview_to_content(document_text: str, preview: PendingRewritePreview) -> str:
    start, end = preview.target_range
    return f"{document_text[:start]}{preview.proposed_text}{document_text[end:]}"


def review_preview_start_location(document_text: str, preview: PendingRewritePreview) -> tuple[int, int]:
    """Return the TextArea location where the inline review block begins."""
    start = max(0, min(preview.target_range[0], len(document_text)))
    before = document_text[:start]
    return (before.count("\n") + 1, 0)


def generated_text_insert_location(
    document_text: str,
    generated_text: str,
    target_range: tuple[int, int] | None,
) -> tuple[int, int] | None:
    clean_text = generated_text.strip("\n")
    if not clean_text:
        return None
    if target_range is None:
        if not document_text:
            start = 0
        else:
            separator = "" if document_text.endswith("\n\n") else "\n" if document_text.endswith("\n") else "\n\n"
            start = len(document_text) + len(separator)
    else:
        start, end = target_range
        if end < start:
            start, end = end, start
        start = max(0, min(start, len(document_text)))
    before = insert_generated_text_at_range(document_text, generated_text, target_range)[:start]
    return (before.count("\n"), len(before.rsplit("\n", 1)[-1]))


def insert_generated_text_at_range(
    document_text: str,
    generated_text: str,
    target_range: tuple[int, int] | None,
) -> str:
    clean_text = generated_text.strip("\n")
    if not clean_text:
        return document_text
    if target_range is None:
        if not document_text:
            return clean_text
        separator = "" if document_text.endswith("\n\n") else "\n" if document_text.endswith("\n") else "\n\n"
        return f"{document_text}{separator}{clean_text}"
    start, end = target_range
    if end < start:
        start, end = end, start
    return f"{document_text[:start]}{clean_text}{document_text[end:]}"


def clean_generated_draft_text(document_text: str, generated_text: str) -> str:
    """Trim duplicate existing headings that models often prepend to body drafts."""
    heading_titles = {
        _normalized_heading_text(line)
        for line in document_text.splitlines()
        if line.lstrip().startswith("#") and _normalized_heading_text(line)
    }
    if not heading_titles:
        return generated_text.strip("\n")
    lines = generated_text.strip("\n").splitlines()
    while lines:
        normalized = _normalized_heading_text(lines[0])
        if normalized and normalized in heading_titles:
            lines.pop(0)
            while lines and not lines[0].strip():
                lines.pop(0)
            continue
        break
    return "\n".join(lines).strip("\n")


def _normalized_heading_text(line: str) -> str:
    normalized = line.strip()
    normalized = normalized.lstrip("#").strip()
    normalized = normalized.strip("*_`").strip()
    while (
        (normalized.startswith("**") and normalized.endswith("**"))
        or (normalized.startswith("__") and normalized.endswith("__"))
        or (normalized.startswith("*") and normalized.endswith("*"))
        or (normalized.startswith("_") and normalized.endswith("_"))
    ):
        normalized = normalized.strip("*_").strip()
    normalized = normalized.rstrip(":").strip()
    return " ".join(normalized.split()).casefold()


def clean_generated_rewrite_text(document_text: str, generated_text: str) -> str:
    """Trim proposal scaffolding and duplicate headings from model rewrite output."""
    lines = generated_text.strip("\n").splitlines()
    cleaned: list[str] = []
    take_after_label = False
    for raw_line in lines:
        stripped = raw_line.strip()
        lowered = stripped.rstrip(":").casefold()
        if not stripped:
            if cleaned:
                cleaned.append(raw_line)
            continue
        if lowered in {"revision proposal", "rewrite proposal", "proposed", "proposed revision", "proposed rewrite"}:
            take_after_label = True
            cleaned = []
            continue
        if lowered in {"original", "original text", "instruction", "insertion point"}:
            continue
        if stripped.casefold().startswith(("instruction:", "original:", "original text:", "insertion point:")):
            continue
        if stripped.casefold().startswith(("proposed:", "proposed revision:", "proposed rewrite:")):
            _, _, remainder = raw_line.partition(":")
            cleaned = [remainder.strip()] if remainder.strip() else []
            take_after_label = True
            continue
        cleaned.append(raw_line)
    result = "\n".join(cleaned if take_after_label else lines).strip("\n")
    return clean_generated_draft_text(document_text, result)


def _render_review_block(preview: PendingRewritePreview) -> str:
    original_lines = preview.original_text.splitlines() or [preview.original_text]
    proposed_lines = preview.proposed_text.splitlines() or [preview.proposed_text]
    is_draft = preview.patch_id.startswith("draft-")
    if is_draft:
        block_lines = [
            "",
            "┌─ Draft Proposal",
            *[f"│ + {line}" for line in proposed_lines],
            "└─ End Draft Proposal",
            "",
        ]
        return "\n".join(block_lines)
    block_lines = [
        "",
        "┌─ Revision Proposal",
        "│ Original",
        *[f"│ - {line}" for line in original_lines],
        "│",
        "│ Proposed",
        *[f"│ + {line}" for line in proposed_lines],
        "└─ End Revision Proposal",
        "",
    ]
    return "\n".join(block_lines)


def _render_review_block_rich(preview: PendingRewritePreview) -> Text:
    original_lines = preview.original_text.splitlines() or [preview.original_text]
    proposed_lines = preview.proposed_text.splitlines() or [preview.proposed_text]
    is_draft = preview.patch_id.startswith("draft-")
    text = Text()
    text.append("\n")
    if is_draft:
        text.append("┌─ Draft Proposal\n", style="bold")
        for line in proposed_lines:
            text.append(f"│   {line}\n", style="white on #7f1d1d")
        text.append("└─ End Draft Proposal\n\n", style="bold")
        return text
    text.append("┌─ Revision Proposal\n", style="bold")
    text.append("│ Original\n", style="bold green")
    for line in original_lines:
        text.append(f"│   {line}\n", style="white on #14532d")
    text.append("│\n")
    text.append("│ Proposed\n", style="bold red")
    for line in proposed_lines:
        text.append(f"│   {line}\n", style="white on #7f1d1d")
    text.append("└─ End Revision Proposal\n\n", style="bold")
    return text


def _offset_from_location(text: str, location: tuple[int, int]) -> int:
    line, column = location
    lines = text.split("\n")
    line = max(0, min(line, len(lines) - 1))
    offset = 0
    for index in range(line):
        offset += len(lines[index]) + 1
    return min(offset + column, len(text))


def _location_from_offset(text: str, offset: int) -> tuple[int, int]:
    offset = max(0, min(offset, len(text)))
    before = text[:offset]
    return (before.count("\n"), len(before.rsplit("\n", 1)[-1]))


class DocumentPane(Vertical):
    class ExcerptRequested(Message):
        def __init__(self, document_pane: "DocumentPane", slug: str, excerpt_text: str, start: int, end: int) -> None:
            super().__init__()
            self.document_pane = document_pane
            self.slug = slug
            self.excerpt_text = excerpt_text
            self.start = start
            self.end = end

    class DocumentRequested(Message):
        def __init__(self, document_pane: "DocumentPane", slug: str) -> None:
            super().__init__()
            self.document_pane = document_pane
            self.slug = slug

    class CloseRequested(Message):
        def __init__(self, document_pane: "DocumentPane") -> None:
            super().__init__()
            self.document_pane = document_pane

    class SaveRequested(Message):
        def __init__(self, document_pane: "DocumentPane") -> None:
            super().__init__()
            self.document_pane = document_pane

    class ContentChanged(Message):
        def __init__(self, document_pane: "DocumentPane", slug: str, content: str) -> None:
            super().__init__()
            self.document_pane = document_pane
            self.slug = slug
            self.content = content

    def __init__(self) -> None:
        super().__init__(id=DOCUMENT_PANE_COPY.pane_id, classes="shell-pane")
        self.border_title = DOCUMENT_PANE_COPY.title
        self._open_tabs: list[str] = [CURRENT_DRAFT_SLUG]
        self._active_slug = CURRENT_DRAFT_SLUG
        self._pending_previews: dict[str, PendingRewritePreview] = {}
        self._search_selection_ranges: dict[str, tuple[int, int]] = {}
        self._view_statuses: dict[str, DocumentViewStatus] = {}
        self._syncing_slugs: set[str] = set()
        self._save_enabled = False

    def compose(self) -> ComposeResult:
        with Horizontal(id=DOCUMENT_TOOLBAR_ID):
            yield Button("Excerpt to Basket", id=DOCUMENT_ADD_EXCERPT_ID, classes="compact-action-primary")
            yield Button("File to Basket", id=DOCUMENT_ADD_FILE_ID, classes="compact-action-primary")
            yield Static("", classes="toolbar-spacer")
            yield Button("Save", id=DOCUMENT_SAVE_BUTTON_ID, classes="compact-action-primary")
            yield Button("Close tab", id=DOCUMENT_CLOSE_BUTTON_ID, classes="compact-action-warning")
        with TabbedContent(initial=CURRENT_DRAFT_SLUG, id=DOCUMENT_TABBED_CONTENT_ID):
            yield self._make_pane(CURRENT_DRAFT_SLUG)

    def on_mount(self) -> None:
        self._sync_controls()
        self._apply_editor_state(self._active_slug)

    @property
    def active_document(self) -> DocumentFixture:
        return DOCUMENT_FIXTURES[self._active_slug]

    @property
    def active_document_is_transcript(self) -> bool:
        return self.active_document.is_transcript or self.active_document.slug.startswith("transcript-")

    def focus_editor(self) -> None:
        self._editor_for_slug(self._active_slug).focus()

    def set_save_enabled(self, enabled: bool) -> None:
        self._save_enabled = enabled
        self._sync_controls()

    def set_document_view_status(self, slug: str, status: DocumentViewStatus | None) -> None:
        if status is None:
            self._view_statuses.pop(slug, None)
        else:
            self._view_statuses[slug] = status
        if slug in self._open_tabs:
            self._apply_editor_state(slug)
            self._sync_tab_label(slug)
            self._sync_controls()

    def document_view_status(self, slug: str) -> DocumentViewStatus | None:
        return self._view_statuses.get(slug)

    def current_selection_snapshot(self) -> DocumentSelectionSnapshot | None:
        if self._active_slug in self._pending_previews:
            return None
        editor = self._editor_for_slug(self._active_slug)
        selection = editor.selection
        start = _offset_from_location(editor.text, selection.start)
        end = _offset_from_location(editor.text, selection.end)
        if end < start:
            start, end = end, start
        if start != end:
            self._search_selection_ranges.pop(self._active_slug, None)
            return DocumentSelectionSnapshot(start=start, end=end, selected_text=editor.text[start:end])
        search_range = self._search_selection_ranges.get(self._active_slug)
        if search_range is None:
            return None
        start, end = search_range
        if end < start:
            start, end = end, start
        text = editor.text
        start = max(0, min(start, len(text)))
        end = max(0, min(end, len(text)))
        if start == end:
            return None
        return DocumentSelectionSnapshot(start=start, end=end, selected_text=text[start:end])

    def has_pending_preview(self, slug: str | None = None) -> bool:
        target = slug or self._active_slug
        return target in self._pending_previews

    def pending_preview_for(self, slug: str | None = None) -> PendingRewritePreview | None:
        target = slug or self._active_slug
        return self._pending_previews.get(target)

    def show_pending_rewrite(self, preview: PendingRewritePreview) -> None:
        self._pending_previews[preview.document_slug] = preview
        self._apply_editor_state(preview.document_slug, reveal_pending_preview=True)
        self._sync_controls()

    def apply_pending_rewrite(self, patch_id: str) -> PendingRewritePreview | None:
        slug, preview = self._find_preview_by_patch_id(patch_id)
        if slug is None or preview is None:
            return None
        fixture = DOCUMENT_FIXTURES[slug]
        fixture.content = apply_preview_to_content(fixture.content, preview)
        self._pending_previews.pop(slug, None)
        self._apply_editor_state(slug)
        self._sync_controls()
        return preview

    def reject_pending_rewrite(self, patch_id: str) -> PendingRewritePreview | None:
        slug, preview = self._find_preview_by_patch_id(patch_id)
        if slug is None or preview is None:
            return None
        self._pending_previews.pop(slug, None)
        self._apply_editor_state(slug)
        self._sync_controls()
        return preview

    async def open_document(self, slug: str, *, focus: bool = True) -> None:
        if slug not in DOCUMENT_FIXTURES:
            return
        tabbed_content = self.query_one(f"#{DOCUMENT_TABBED_CONTENT_ID}", TabbedContent)
        if slug not in self._open_tabs:
            self._open_tabs.append(slug)
            await tabbed_content.add_pane(self._make_pane(slug))
            self._sync_tab_label(slug)
        tabbed_content.active = slug
        self._active_slug = slug
        self._apply_editor_state(slug)
        if focus:
            self.focus_editor()
        self._sync_controls()

    async def open_document_with_selection(
        self,
        slug: str,
        target_range: tuple[int, int] | None,
        *,
        focus: bool = True,
    ) -> None:
        await self.open_document(slug, focus=focus)
        if target_range is None or slug not in DOCUMENT_FIXTURES:
            return
        self._search_selection_ranges.pop(slug, None)
        self._apply_search_selection(slug, target_range, focus=focus)
        self.call_after_refresh(lambda: self._apply_search_selection(slug, target_range, focus=focus))

    def _apply_search_selection(
        self,
        slug: str,
        target_range: tuple[int, int],
        *,
        focus: bool,
    ) -> None:
        if slug not in DOCUMENT_FIXTURES:
            return
        fixture = DOCUMENT_FIXTURES[slug]
        start, end = target_range
        if end < start:
            start, end = end, start
        start = max(0, min(start, len(fixture.content)))
        end = max(0, min(end, len(fixture.content)))
        if start == end:
            return
        self._search_selection_ranges[slug] = (start, end)
        editor = self._editor_for_slug(slug)
        start_location = _location_from_offset(editor.text, start)
        end_location = _location_from_offset(editor.text, end)
        editor.selection = Selection(end_location, end_location)
        editor.move_cursor(end_location, center=True)
        editor.selection = Selection(start_location, end_location)
        editor.scroll_cursor_visible(center=True, animate=False)
        if focus:
            editor.focus()

    async def open_readonly_snapshot(
        self,
        *,
        slug: str,
        title: str,
        content: str,
        document_type: str,
        status: DocumentViewStatus,
        focus: bool = True,
    ) -> None:
        if slug not in DOCUMENT_FIXTURES:
            register_document_fixture(
                slug=slug,
                title=title,
                location=slug,
                summary="Read-only basket snapshot.",
                content=content,
                document_type=document_type,
            )
        else:
            fixture = DOCUMENT_FIXTURES[slug]
            fixture.title = title
            fixture.content = content
            fixture.document_type = document_type
        self.set_document_view_status(slug, status)
        await self.open_document(slug, focus=focus)

    async def close_active_document(self) -> bool:
        if len(self._open_tabs) <= 1:
            return False
        fixture = self.active_document
        if not fixture.closable or self._active_slug in self._pending_previews:
            return False
        closing_slug = self._active_slug
        current_index = self._open_tabs.index(closing_slug)
        self._open_tabs.remove(closing_slug)
        fallback_slug = self._open_tabs[max(0, current_index - 1)]
        tabbed_content = self.query_one(f"#{DOCUMENT_TABBED_CONTENT_ID}", TabbedContent)
        tabbed_content.active = fallback_slug
        await tabbed_content.remove_pane(closing_slug)
        tabbed_content.active = fallback_slug
        self._active_slug = fallback_slug
        self._apply_editor_state(fallback_slug)
        self._sync_controls()
        self.focus_editor()
        return True

    async def remove_document(self, slug: str) -> bool:
        if slug not in DOCUMENT_FIXTURES:
            return False
        fixture = DOCUMENT_FIXTURES[slug]
        if not fixture.closable or slug in self._pending_previews:
            return False
        if slug in self._open_tabs:
            tabbed_content = self.query_one(f"#{DOCUMENT_TABBED_CONTENT_ID}", TabbedContent)
            if len(self._open_tabs) == 1:
                if slug == CURRENT_DRAFT_SLUG or CURRENT_DRAFT_SLUG not in DOCUMENT_FIXTURES:
                    return False
                self._open_tabs.append(CURRENT_DRAFT_SLUG)
                await tabbed_content.add_pane(self._make_pane(CURRENT_DRAFT_SLUG))
            current_index = self._open_tabs.index(slug)
            self._open_tabs.remove(slug)
            fallback_index = max(0, min(current_index - 1, len(self._open_tabs) - 1))
            fallback_slug = self._open_tabs[fallback_index]
            if slug == self._active_slug:
                tabbed_content.active = fallback_slug
            await tabbed_content.remove_pane(slug)
            if slug == self._active_slug:
                tabbed_content.active = fallback_slug
                self._active_slug = fallback_slug
                self._apply_editor_state(fallback_slug)
                self.focus_editor()
        DOCUMENT_FIXTURES.pop(slug, None)
        self._view_statuses.pop(slug, None)
        self._pending_previews.pop(slug, None)
        self._search_selection_ranges.pop(slug, None)
        self._sync_controls()
        return True

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        pane = getattr(event, "pane", None)
        if pane is None or pane.id is None:
            return
        self._active_slug = pane.id
        self._apply_editor_state(self._active_slug)
        self._sync_controls()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        editor_id = event.text_area.id or ""
        if not editor_id.startswith("document-editor-"):
            return
        slug = editor_id.removeprefix("document-editor-")
        if slug in self._syncing_slugs or slug in self._pending_previews:
            return
        if slug in DOCUMENT_FIXTURES:
            if self._is_read_only_slug(slug):
                return
            if event.text_area.text == DOCUMENT_FIXTURES[slug].content:
                return
            DOCUMENT_FIXTURES[slug].content = event.text_area.text
            self.post_message(self.ContentChanged(self, slug, event.text_area.text))

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == DOCUMENT_ADD_EXCERPT_ID:
            self.request_excerpt()
        elif button_id == DOCUMENT_ADD_FILE_ID:
            self.request_document()
        elif button_id == DOCUMENT_SAVE_BUTTON_ID:
            self.post_message(self.SaveRequested(self))
        elif button_id == DOCUMENT_CLOSE_BUTTON_ID:
            self.post_message(self.CloseRequested(self))

    def _editor_for_slug(self, slug: str) -> TextArea:
        return self.query_one(f"#document-editor-{slug}", TextArea)

    @property
    def selected_text(self) -> str:
        snapshot = self.current_selection_snapshot()
        return snapshot.selected_text if snapshot is not None else ""

    def _first_nonempty_line(self) -> str:
        for line in self.active_document.content.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                return stripped
        return self.active_document.title

    def request_excerpt(self) -> None:
        snapshot = self.current_selection_snapshot()
        if snapshot is not None:
            excerpt_text = snapshot.selected_text.strip()
            start = snapshot.start
            end = snapshot.end
        else:
            excerpt_text = self._first_nonempty_line()
            start = self.active_document.content.find(excerpt_text)
            start = max(0, start)
            end = start + len(excerpt_text)
        self.post_message(self.ExcerptRequested(self, self._active_slug, excerpt_text, start, end))

    def request_document(self) -> None:
        self.post_message(self.DocumentRequested(self, self._active_slug))

    def rename_document(self, slug: str, title: str, location: str | None = None) -> None:
        fixture = DOCUMENT_FIXTURES.get(slug)
        if fixture is None:
            return
        fixture.title = title
        fixture.location = location or title
        if slug not in self._open_tabs:
            return
        self._sync_tab_label(slug)

    def insert_generated_text(self, slug: str, generated_text: str) -> str | None:
        fixture = DOCUMENT_FIXTURES.get(slug)
        if fixture is None:
            return None
        editor = self._editor_for_slug(slug)
        selection = editor.selection
        start = _offset_from_location(editor.text, selection.start)
        end = _offset_from_location(editor.text, selection.end)
        if end < start:
            start, end = end, start
        target_range: tuple[int, int] | None
        if end > start:
            target_range = (start, end)
        elif start > 0:
            target_range = (start, start)
        else:
            target_range = None
        insert_location = generated_text_insert_location(fixture.content, generated_text, target_range)
        fixture.content = insert_generated_text_at_range(fixture.content, generated_text, target_range)
        self._apply_editor_state(slug, reveal_location=insert_location)
        return fixture.content

    def show_pending_generated_text(
        self,
        *,
        slug: str,
        patch_id: str,
        generated_text: str,
        instruction_text: str,
        source_chat_slug: str,
    ) -> PendingRewritePreview | None:
        fixture = DOCUMENT_FIXTURES.get(slug)
        if fixture is None:
            return None
        existing_preview = self._pending_previews.get(slug)
        if existing_preview is not None and existing_preview.patch_id.startswith("draft-"):
            target_range = existing_preview.target_range
            original_text = existing_preview.original_text
        else:
            editor = self._editor_for_slug(slug)
            selection = editor.selection
            start = _offset_from_location(editor.text, selection.start)
            end = _offset_from_location(editor.text, selection.end)
            if end < start:
                start, end = end, start
            if end > start:
                target_range = (start, end)
                original_text = fixture.content[start:end]
            elif start > 0:
                target_range = (start, start)
                original_text = ""
            else:
                target_range = (len(fixture.content), len(fixture.content))
                original_text = ""
        preview = PendingRewritePreview(
            patch_id=patch_id,
            document_slug=slug,
            target_range=target_range,
            original_text=original_text,
            proposed_text=clean_generated_draft_text(fixture.content, generated_text),
            instruction_text=instruction_text,
            source_chat_slug=source_chat_slug,
        )
        self.show_pending_rewrite(preview)
        return preview

    def _sync_controls(self) -> None:
        has_pending = self._active_slug in self._pending_previews
        is_read_only = self._is_read_only_slug(self._active_slug)
        self.query_one(f"#{DOCUMENT_CLOSE_BUTTON_ID}", Button).disabled = (
            len(self._open_tabs) <= 1 or not self.active_document.closable or has_pending
        )
        self.query_one(f"#{DOCUMENT_ADD_EXCERPT_ID}", Button).disabled = has_pending
        self.query_one(f"#{DOCUMENT_ADD_FILE_ID}", Button).disabled = has_pending or is_read_only
        self.query_one(f"#{DOCUMENT_SAVE_BUTTON_ID}", Button).disabled = has_pending or is_read_only or not self._save_enabled

    def _is_read_only_slug(self, slug: str) -> bool:
        return slug in self._pending_previews or self._view_statuses.get(slug) in {"trashed", "source_deleted"}

    def _apply_editor_state(
        self,
        slug: str,
        *,
        reveal_pending_preview: bool = False,
        reveal_location: tuple[int, int] | None = None,
    ) -> None:
        if slug not in DOCUMENT_FIXTURES:
            return
        editor = self._editor_for_slug(slug)
        fixture = DOCUMENT_FIXTURES[slug]
        preview = self._pending_previews.get(slug)
        preview_container = self._preview_container_for_slug(slug)
        preview_widget = self._preview_for_slug(slug)
        self._syncing_slugs.add(slug)
        try:
            editor.load_text(fixture.content)
            editor.read_only = self._is_read_only_slug(slug)
            if preview is not None:
                editor.display = False
                preview_widget.update(render_review_document_rich(fixture.content, preview))
                preview_container.display = True
                preview_container.scroll_home(animate=False)
            else:
                preview_container.display = False
                editor.display = True
                preview_widget.update("")
            if preview is None and reveal_location is not None:
                editor.move_cursor(reveal_location, center=True)
                editor.scroll_cursor_visible(center=True, animate=False)
        finally:
            self._syncing_slugs.discard(slug)

    def _find_preview_by_patch_id(self, patch_id: str) -> tuple[str | None, PendingRewritePreview | None]:
        for slug, preview in self._pending_previews.items():
            if preview.patch_id == patch_id:
                return slug, preview
        return None, None

    def _make_pane(self, slug: str) -> TabPane:
        fixture = DOCUMENT_FIXTURES[slug]
        return TabPane(
            self._tab_label_for_slug(slug),
            SystemClipboardTextArea(
                fixture.content,
                language="markdown",
                theme="vscode_dark",
                soft_wrap=True,
                show_line_numbers=True,
                id=f"document-editor-{slug}",
                classes="document-editor",
            ),
            VerticalScroll(
                Static("", id=f"document-preview-{slug}", classes="document-preview"),
                id=f"document-preview-container-{slug}",
                classes="document-preview-container",
            ),
            id=slug,
        )

    def _preview_container_for_slug(self, slug: str) -> VerticalScroll:
        return self.query_one(f"#document-preview-container-{slug}", VerticalScroll)

    def _preview_for_slug(self, slug: str) -> Static:
        return self.query_one(f"#document-preview-{slug}", Static)

    def _sync_tab_label(self, slug: str) -> None:
        if slug not in self._open_tabs or slug not in DOCUMENT_FIXTURES:
            return
        tabbed_content = self.query_one(f"#{DOCUMENT_TABBED_CONTENT_ID}", TabbedContent)
        tab = tabbed_content.get_tab(slug)
        if tab is not None:
            tab.label = self._tab_label_for_slug(slug)
            tab.set_class(self._view_statuses.get(slug) == "trashed", "document-tab-trashed")
            tab.set_class(self._view_statuses.get(slug) == "source_deleted", "document-tab-deleted")

    def _tab_label_for_slug(self, slug: str):
        return DOCUMENT_FIXTURES[slug].title


__all__ = [
    "CURRENT_DRAFT_SLUG",
    "DOCUMENT_ADD_EXCERPT_ID",
    "DOCUMENT_ADD_FILE_ID",
    "DOCUMENT_CLOSE_BUTTON_ID",
    "DOCUMENT_FIXTURES",
    "DOCUMENT_PANE_COPY",
    "DOCUMENT_SAVE_BUTTON_ID",
    "DOCUMENT_TABBED_CONTENT_ID",
    "DocumentFixture",
    "DocumentPane",
    "DocumentSelectionSnapshot",
    "PendingRewritePreview",
    "SystemClipboardTextArea",
    "apply_preview_to_content",
    "clean_generated_rewrite_text",
    "generated_text_insert_location",
    "insert_generated_text_at_range",
    "register_document_fixture",
    "render_review_document_rich",
    "render_review_document_text",
    "review_preview_start_location",
]
