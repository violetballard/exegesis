from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Button, Markdown, Static

from exegesis_textual.panes import PaneCopy

INSPECTOR_PANE_COPY = PaneCopy(
    pane_id="inspector-pane",
    title="Inspector",
    summary="Details for the selected project item, document, basket entry, or notebook card.",
    bullets=(),
)

INSPECTOR_MARKDOWN_ID = "inspector-markdown"
INSPECTOR_EXCERPT_TITLE_ID = "inspector-excerpt-title"
INSPECTOR_EXCERPT_TEXT_ID = "inspector-excerpt-text"
INSPECTOR_SUMMARY_ACTIONS_ID = "inspector-summary-actions"
INSPECTOR_SAVE_SHORT_SUMMARY_ID = "inspector-save-short-summary"
INSPECTOR_SAVE_MEDIUM_SUMMARY_ID = "inspector-save-medium-summary"
INSPECTOR_SAVE_LONG_SUMMARY_ID = "inspector-save-long-summary"


def escape_markdown_heading(text: str) -> str:
    """Escape heading text so filenames are displayed, not parsed."""
    return "".join(f"\\{char}" if char in r"\`*_{}[]<>()#+-.!|" else char for char in text)


def default_inspector_markdown() -> str:
    return "## Inspector\n\nNo selection."


def format_token_capacity(token_capacity: int) -> str:
    if token_capacity >= 1024 and token_capacity % 1024 == 0:
        return f"{token_capacity // 1024}k"
    return f"{token_capacity:,}"


def render_inspector_markdown(
    title: str,
    summary: str,
    bullets: tuple[str, ...],
    note: str | None = None,
    *,
    title_href: str | None = None,
    selection_type: str | None = None,
    word_count: int | None = None,
    token_count: int | None = None,
    token_capacity: int | None = None,
) -> str:
    escaped_title = escape_markdown_heading(title)
    if title_href:
        sections = [f"## [{escaped_title}]({title_href})"]
    else:
        sections = [f"## {escaped_title}"]
    metadata_lines: list[str] = []
    if selection_type:
        metadata_lines.append(f"- Document type: **{selection_type.title()}**")
    if word_count is not None:
        metadata_lines.append(f"- Words: **{word_count:,}**")
    if token_count is not None:
        if token_capacity is not None:
            metadata_lines.append(f"- Tokens: **~{token_count:,} / {format_token_capacity(token_capacity)}**")
        else:
            metadata_lines.append(f"- Tokens: **~{token_count:,}**")
    if metadata_lines:
        sections.append("\n".join(metadata_lines))
    if summary:
        sections.append(summary)
    if bullets:
        sections.append("\n".join(f"- {bullet}" for bullet in bullets))
    return "\n\n".join(sections)


class InspectorPane(Vertical):
    class SummaryRequested(Message):
        def __init__(self, inspector_pane: "InspectorPane", size: str, word_count: int) -> None:
            super().__init__()
            self.inspector_pane = inspector_pane
            self.size = size
            self.word_count = word_count

    def __init__(self) -> None:
        super().__init__(id=INSPECTOR_PANE_COPY.pane_id, classes="shell-pane")
        self.border_title = INSPECTOR_PANE_COPY.title
        self._has_excerpt = False

    def compose(self) -> ComposeResult:
        yield Markdown(default_inspector_markdown(), id=INSPECTOR_MARKDOWN_ID, open_links=False)
        yield Static("Excerpt", id=INSPECTOR_EXCERPT_TITLE_ID)
        yield Static("", id=INSPECTOR_EXCERPT_TEXT_ID)
        with Vertical(id=INSPECTOR_SUMMARY_ACTIONS_ID, classes="inspector-summary-actions"):
            yield Button(
                "Save a Short Summary\n~100 Words",
                id=INSPECTOR_SAVE_SHORT_SUMMARY_ID,
                variant="primary",
                classes="inspector-summary-button",
            )
            yield Button(
                "Save a Medium Summary\n~500 Words",
                id=INSPECTOR_SAVE_MEDIUM_SUMMARY_ID,
                variant="primary",
                classes="inspector-summary-button",
            )
            yield Button(
                "Save a Long Summary\n~1000 Words",
                id=INSPECTOR_SAVE_LONG_SUMMARY_ID,
                variant="primary",
                classes="inspector-summary-button",
            )

    def on_mount(self) -> None:
        self._sync_summary_actions()

    def show_subject(
        self,
        title: str,
        summary: str,
        bullets: tuple[str, ...],
        note: str | None = None,
        *,
        title_href: str | None = None,
        selection_type: str | None = None,
        word_count: int | None = None,
        token_count: int | None = None,
        token_capacity: int | None = None,
        allow_summary_actions: bool = False,
    ) -> None:
        self.query_one(f"#{INSPECTOR_MARKDOWN_ID}", Markdown).update(
            render_inspector_markdown(
                title,
                summary,
                bullets,
                title_href=title_href,
                selection_type=selection_type,
                word_count=word_count,
                token_count=token_count,
                token_capacity=token_capacity,
            )
        )
        excerpt_title = self.query_one(f"#{INSPECTOR_EXCERPT_TITLE_ID}", Static)
        excerpt_text = self.query_one(f"#{INSPECTOR_EXCERPT_TEXT_ID}", Static)
        excerpt_title.display = bool(note)
        excerpt_text.display = bool(note)
        excerpt_text.update(note or "")
        self._has_excerpt = bool(note and selection_type and allow_summary_actions)
        self._sync_summary_actions()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == INSPECTOR_SAVE_SHORT_SUMMARY_ID:
            self.post_message(self.SummaryRequested(self, "short", 100))
        elif event.button.id == INSPECTOR_SAVE_MEDIUM_SUMMARY_ID:
            self.post_message(self.SummaryRequested(self, "medium", 500))
        elif event.button.id == INSPECTOR_SAVE_LONG_SUMMARY_ID:
            self.post_message(self.SummaryRequested(self, "long", 1000))

    def _sync_summary_actions(self) -> None:
        if not self.is_mounted:
            return
        for button_id in (
            INSPECTOR_SAVE_SHORT_SUMMARY_ID,
            INSPECTOR_SAVE_MEDIUM_SUMMARY_ID,
            INSPECTOR_SAVE_LONG_SUMMARY_ID,
        ):
            self.query_one(f"#{button_id}", Button).disabled = not self._has_excerpt
        self.query_one(f"#{INSPECTOR_SUMMARY_ACTIONS_ID}", Vertical).display = self._has_excerpt


__all__ = [
    "INSPECTOR_EXCERPT_TEXT_ID",
    "INSPECTOR_EXCERPT_TITLE_ID",
    "INSPECTOR_MARKDOWN_ID",
    "INSPECTOR_PANE_COPY",
    "INSPECTOR_SAVE_LONG_SUMMARY_ID",
    "INSPECTOR_SAVE_MEDIUM_SUMMARY_ID",
    "INSPECTOR_SAVE_SHORT_SUMMARY_ID",
    "InspectorPane",
    "default_inspector_markdown",
    "render_inspector_markdown",
]
