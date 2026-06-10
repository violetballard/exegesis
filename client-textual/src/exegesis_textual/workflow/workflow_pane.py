from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from math import ceil
from pathlib import Path

from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Input, LoadingIndicator, Markdown, Static, TabPane, TabbedContent
from textual.worker import Worker

from exegesis_textual.cards.patch_card import PatchReviewCardData
from exegesis_textual.panes import PaneCopy
from exegesis_textual.workflow.mistral_chat import (
    ChatEvent,
    ChatMessage,
    DEFAULT_SYSTEM_PROMPT_PATH,
    MistralChatBackend,
    ShellChatContext,
    TerminalChatBackend,
)

WORKFLOW_PANE_COPY = PaneCopy(
    pane_id="workflow-pane",
    title="Notebook",
    summary="Tabbed model-facing notebook for prompts, context status, and future A2UI cards.",
    bullets=(
        "This is the Qual notebook, not an OS shell.",
        "Chats should feel like task threads around the active draft and available context.",
        "A2UI cards can eventually appear here without changing the notebook mental model.",
    ),
)

WORKFLOW_TABBED_CONTENT_ID = "workflow-tabs"
WORKFLOW_STATUS_ID = "workflow-status"
WORKFLOW_COMPOSER_ROW_ID = "workflow-composer-row"
WORKFLOW_COMPOSER_INPUT_ID = "workflow-composer-input"
WORKFLOW_SEND_ID = "workflow-send"
WORKFLOW_SEARCH_ID = "workflow-search"
WORKFLOW_DRAFT_ID = "workflow-draft"
WORKFLOW_REWRITE_SELECTION_ID = "workflow-rewrite-selection"
WORKFLOW_NEW_CHAT_ID = "workflow-new-chat"
WORKFLOW_SAVE_CHAT_ID = "workflow-save-chat"
WORKFLOW_COMPACT_CHAT_ID = "workflow-compact-chat"
WORKFLOW_CLOSE_CHAT_ID = "workflow-close-chat"
WORKFLOW_ARTIFACTS_DIR = Path(__file__).resolve().parents[3] / ".artifacts" / "transcripts"
PRIMARY_CHAT_SLUG = "chat-main"
TERMINAL_CONTEXT_WINDOW_TOKENS = 256 * 1024
CONTEXT_EARLY_COMPACT_PROMPT_RATIO = 0.75
CONTEXT_STRONG_COMPACT_PROMPT_RATIO = 0.90
CONTEXT_HARD_LIMIT_RATIO = 1.0
REWRITE_CARD_TEXT_LIMIT = 1_200
EMPTY_CONTEXT_USAGE_TEXT = f"0% context used (~0 / {TERMINAL_CONTEXT_WINDOW_TOKENS:,} tokens)"
NON_CONFIDENTIAL_TRANSCRIPT_WARNING = (
    "Non-confidential warning: full transcripts are not loaded into model context. "
    "Use excerpts, selected passages, search snippets, or text you provide here."
)


@dataclass(frozen=True)
class SearchResultMatch:
    snippet: str
    match_range: tuple[int, int]


@dataclass(frozen=True)
class SearchResultItem:
    document_slug: str
    title: str
    document_type: str
    snippet: str
    token_count: int
    location: str
    match_range: tuple[int, int] | None = None
    matches: tuple[SearchResultMatch, ...] = ()

    def match_count(self) -> int:
        return len(self.matches) or (1 if self.match_range is not None else 0)

    def match_at(self, index: int) -> SearchResultMatch | None:
        if self.matches:
            return self.matches[index % len(self.matches)]
        if self.match_range is None:
            return None
        return SearchResultMatch(snippet=self.snippet, match_range=self.match_range)


@dataclass
class HistoryTextEntry:
    role: str
    content: str
    streaming: bool = False


@dataclass(frozen=True)
class HistoryStatusEntry:
    content: str


@dataclass
class HistoryReasoningEntry:
    content: str
    streaming: bool = False


def _display_document_type(document_type: str) -> str:
    normalized = " ".join(document_type.replace("_", " ").replace("-", " ").split())
    return normalized.title() if normalized else "Document"


@dataclass
class HistorySearchEntry:
    query: str
    results: list[SearchResultItem]
    selected_match_indices: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class HistoryRewriteEntry:
    patch_id: str
    document_title: str
    instruction_text: str
    source_chat_slug: str
    original_text: str
    proposed_text: str
    document_slug: str = ""
    target_range: tuple[int, int] | None = None


@dataclass(frozen=True)
class HistoryCompactionEntry:
    transcript_title: str
    transcript_location: str
    source_chat_slug: str
    source_entry_count: int
    original_tokens: int
    compacted_tokens: int
    compression_ratio: float
    automatic: bool


@dataclass(frozen=True)
class HistoryCompactionPromptEntry:
    used_tokens: int
    token_capacity: int
    reason: str


@dataclass(frozen=True)
class RewriteRequestTarget:
    document_slug: str
    document_title: str
    target_range: tuple[int, int]
    original_text: str


@dataclass
class WorkflowChat:
    slug: str
    title: str
    summary: str
    context_available: str
    status_note: str
    messages: list[ChatMessage] = field(default_factory=list)
    history_entries: list[object] = field(default_factory=list)
    closable: bool = True
    generating: bool = False
    active_request_id: int | None = None
    active_request_mode: str | None = None
    active_instruction_text: str = ""
    active_history_index: int | None = None
    active_reasoning_index: int | None = None
    active_rewrite_target: RewriteRequestTarget | None = None
    pending_patch_id: str | None = None

    @property
    def transcript_name(self) -> str:
        return f"{self.slug}.md"

    @property
    def transcript_location(self) -> str:
        return f"transcripts/{self.transcript_name}"

    @property
    def bullets(self) -> tuple[str, ...]:
        return (
            f"Context available: {self.context_available}.",
            f"Status: {self.status_note}.",
            "Notebook chat is connected to the active project, current document, basket context, and model provider.",
        )


WORKFLOW_CHATS: dict[str, WorkflowChat] = {
    PRIMARY_CHAT_SLUG: WorkflowChat(
        slug=PRIMARY_CHAT_SLUG,
        title="Main chat",
        summary="Primary LLM conversation for the current draft and the default active chat.",
        context_available=EMPTY_CONTEXT_USAGE_TEXT,
        status_note="Live notebook chat with retrieval, basket, provider, and harness wiring.",
        closable=False,
        messages=[],
        history_entries=[],
    ),
    "chat-outline-pass": WorkflowChat(
        slug="chat-outline-pass",
        title="Outline pass",
        summary="Secondary chat for structural editing and outline experiments.",
        context_available=EMPTY_CONTEXT_USAGE_TEXT,
        status_note="Fresh context window; no transcript saved yet.",
        messages=[],
        history_entries=[],
    ),
}


def clipped_rewrite_card_text(label: str, text: str, limit: int = REWRITE_CARD_TEXT_LIMIT) -> str:
    clean_text = text.strip()
    if len(clean_text) <= limit:
        return f"{label}\n{clean_text}"
    clipped = clean_text[:limit].rstrip()
    omitted = len(clean_text) - len(clipped)
    return f"{label}\n{clipped}\n\n[{omitted:,} more character(s) shown inline in the document preview.]"


def register_workflow_document(
    *,
    slug: str,
    title: str,
    summary: str,
    location: str,
    content: str,
) -> None:
    from exegesis_textual.panes.document_pane import register_document_fixture

    register_document_fixture(
        slug=slug,
        title=title,
        location=location,
        summary=summary,
        content=content,
        document_type="transcript",
        is_transcript=True,
    )


class HistoryMarkdownEntry(Vertical):
    def __init__(self, entry: HistoryTextEntry | HistoryStatusEntry) -> None:
        self.source_entry = entry
        if isinstance(entry, HistoryStatusEntry):
            self._status_text = entry.content
            self._role_label = ""
            self._content_markdown = ""
            classes = "workflow-history-block workflow-history-status"
        else:
            content = entry.content or ("…" if entry.streaming else "")
            self._status_text = ""
            self._role_label = f"{entry.role.capitalize()}:"
            self._content_markdown = content
            classes = f"workflow-history-block workflow-history-text workflow-history-{entry.role}"
        super().__init__(classes=classes)

    def compose(self) -> ComposeResult:
        if isinstance(self.source_entry, HistoryStatusEntry):
            if self._status_text == "Generating draft proposal...":
                with Horizontal(classes="workflow-history-status-content workflow-history-loading-row"):
                    yield LoadingIndicator(classes="workflow-history-loading")
                    yield Static(self._status_text, classes="workflow-history-loading-text")
            else:
                yield Static(self._status_text, classes="workflow-history-status-content")
            return
        yield Static(self._role_label, classes="workflow-history-label")
        yield Markdown(self._content_markdown, classes="workflow-history-message")


class ReasoningTraceHistoryCard(Vertical):
    def __init__(self, entry: HistoryReasoningEntry) -> None:
        self.source_entry = entry
        super().__init__(classes="workflow-history-block workflow-reasoning-card")

    def compose(self) -> ComposeResult:
        yield Static("Reasoning Trace", classes="workflow-history-label workflow-reasoning-label")
        yield Markdown(self.source_entry.content or ("…" if self.source_entry.streaming else ""), classes="workflow-history-message")


class SearchResultsCard(Vertical):
    class ResultControl(Static):
        can_focus = False

        def __init__(self, card: "SearchResultsCard", result_index: int, action: str, label: str, *, id: str, classes: str) -> None:
            super().__init__(label, id=id, classes=classes)
            self.card = card
            self.result_index = result_index
            self.action = action

        def on_click(self, event: events.Click) -> None:
            event.stop()
            self.card.select_result(self.result_index, self.action)

    class ResultSelected(Message):
        def __init__(self, card: "SearchResultsCard", result: SearchResultItem, match_index: int) -> None:
            super().__init__()
            self.card = card
            self.result = result
            self.match_index = match_index

    def __init__(self, entry: HistorySearchEntry) -> None:
        super().__init__(classes="workflow-card workflow-search-card")
        self._entry = entry
        self._result_map: dict[str, tuple[int, str]] = {}
        self._selected_match_index: dict[int, int] = {}
        self.border_title = "Search Results"

    def compose(self) -> ComposeResult:
        yield Static(f'Search: "{self._entry.query}"', classes="workflow-card-title")
        if not self._entry.results:
            yield Static("No matching documents found.", classes="workflow-card-meta")
            return
        yield Static(f"{len(self._entry.results)} matching document(s)", classes="workflow-card-meta")
        for index, result in enumerate(self._entry.results, start=1):
            button_id = f"search-result-{index}"
            prev_id = f"search-result-prev-{index}"
            next_id = f"search-result-next-{index}"
            initial_match_index = self._entry.selected_match_indices.get(result.document_slug, 0)
            self._selected_match_index.setdefault(index - 1, initial_match_index)
            with Vertical(classes="workflow-search-result"):
                with Horizontal(classes="workflow-search-result-row"):
                    yield self.ResultControl(self, index - 1, "open", result.title, id=button_id, classes="workflow-search-result-title")
                    yield Static(self._match_label(result, initial_match_index), id=f"search-result-count-{index}", classes="workflow-card-meta workflow-search-result-count")
                    if result.match_count() > 1:
                        yield self.ResultControl(self, index - 1, "prev", "‹", id=prev_id, classes="workflow-search-result-arrow")
                        yield self.ResultControl(self, index - 1, "next", "›", id=next_id, classes="workflow-search-result-arrow")
                yield Static(
                    f"{_display_document_type(result.document_type)} • ~{result.token_count:,} tokens",
                    classes="workflow-card-meta",
                )
                yield Static(self._match_snippet(result, initial_match_index), id=f"search-result-snippet-{index}", classes="workflow-card-body workflow-search-result-snippet")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        mapped = self._result_map.get(event.button.id or "")
        if mapped is None:
            return
        result_index, action = mapped
        self.select_result(result_index, action)

    def select_result(self, result_index: int, action: str) -> None:
        result = self._entry.results[result_index]
        match_count = max(1, result.match_count())
        current_index = self._selected_match_index.get(result_index, 0)
        if action == "prev":
            current_index = (current_index - 1) % match_count
        elif action == "next":
            current_index = (current_index + 1) % match_count
        self._selected_match_index[result_index] = current_index
        self._entry.selected_match_indices[result.document_slug] = current_index
        self._refresh_match_display(result_index, result, current_index)
        self.post_message(self.ResultSelected(self, result, current_index))

    def _refresh_match_display(self, result_index: int, result: SearchResultItem, match_index: int) -> None:
        display_index = result_index + 1
        self.query_one(f"#search-result-count-{display_index}", Static).update(self._match_label(result, match_index))
        self.query_one(f"#search-result-snippet-{display_index}", Static).update(self._match_snippet(result, match_index))

    def _match_label(self, result: SearchResultItem, match_index: int) -> str:
        match_count = result.match_count()
        if match_count <= 1:
            return "1/1" if match_count == 1 else ""
        return f"{(match_index % match_count) + 1}/{match_count}"

    def _match_snippet(self, result: SearchResultItem, match_index: int) -> str:
        match = result.match_at(match_index)
        if match is not None and match.snippet.strip():
            return match.snippet
        return result.snippet or "Matching text found in this document."


class RewriteReviewHistoryCard(Vertical):
    class ApplyRequested(Message):
        def __init__(self, card: "RewriteReviewHistoryCard", patch_id: str) -> None:
            super().__init__()
            self.card = card
            self.patch_id = patch_id

    class RejectRequested(Message):
        def __init__(self, card: "RewriteReviewHistoryCard", patch_id: str) -> None:
            super().__init__()
            self.card = card
            self.patch_id = patch_id

    def __init__(self, entry: HistoryRewriteEntry) -> None:
        super().__init__(classes="workflow-card workflow-rewrite-card")
        self._entry = entry
        self._is_draft = entry.patch_id.startswith("draft-")
        self.border_title = "Draft Review" if self._is_draft else "Rewrite Review"

    def compose(self) -> ComposeResult:
        yield Static("Draft Proposal" if self._is_draft else self._entry.document_title, classes="workflow-card-title")
        yield Static(
            f"from {self._entry.source_chat_slug} • Instruction: {self._entry.instruction_text}",
            classes="workflow-card-meta",
        )
        if self._is_draft:
            yield Static(clipped_rewrite_card_text("Draft proposal", self._entry.proposed_text), classes="workflow-card-body")
        else:
            yield Static(clipped_rewrite_card_text("Original", self._entry.original_text), classes="workflow-card-body")
            yield Static(clipped_rewrite_card_text("Proposed", self._entry.proposed_text), classes="workflow-card-body")
        with Horizontal(classes="workflow-history-card-actions"):
            yield Button("Apply", id="rewrite-apply", classes="compact-action-primary")
            yield Button("Reject", id="rewrite-reject", classes="compact-action-warning")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "rewrite-apply":
            self.post_message(self.ApplyRequested(self, self._entry.patch_id))
        elif event.button.id == "rewrite-reject":
            self.post_message(self.RejectRequested(self, self._entry.patch_id))


class CompactionHistoryCard(Vertical):
    def __init__(self, entry: HistoryCompactionEntry) -> None:
        super().__init__(classes="workflow-card workflow-compaction-card")
        self._entry = entry
        self.border_title = "Compacted Context"

    def compose(self) -> ComposeResult:
        trigger = "automatic" if self._entry.automatic else "manual"
        yield Static(f"{self._entry.transcript_title}", classes="workflow-card-title")
        yield Static(
            (
                f"{trigger} compaction from {self._entry.source_chat_slug} • "
                f"{self._entry.source_entry_count} source entries"
            ),
            classes="workflow-card-meta",
        )
        yield Static(
            (
                f"Original: ~{self._entry.original_tokens:,} tokens\n"
                f"Compacted active context: ~{self._entry.compacted_tokens:,} tokens\n"
                f"Compression ratio: {self._entry.compression_ratio:.0%}\n"
                f"Full transcript: {self._entry.transcript_location}\n\n"
                "Raw history was saved before compaction. Double-select that transcript or use Restore "
                "while it is selected to start a new chat from the full transcript."
            ),
            classes="workflow-card-body",
        )


class CompactionPromptCard(Vertical):
    class CompactRequested(Message):
        def __init__(self, card: "CompactionPromptCard") -> None:
            super().__init__()
            self.card = card

    class NewChatRequested(Message):
        def __init__(self, card: "CompactionPromptCard") -> None:
            super().__init__()
            self.card = card

    def __init__(self, entry: HistoryCompactionPromptEntry) -> None:
        super().__init__(classes="workflow-card workflow-compaction-card")
        self._entry = entry
        self.border_title = "Context Limit"

    def compose(self) -> ComposeResult:
        percentage = (self._entry.used_tokens / self._entry.token_capacity) * 100 if self._entry.token_capacity else 0
        yield Static("Compaction needed to continue", classes="workflow-card-title")
        yield Static(
            f"{percentage:.0f}% context used (~{self._entry.used_tokens:,} / {self._entry.token_capacity:,} tokens)",
            classes="workflow-card-meta",
        )
        yield Static(
            (
                f"{self._entry.reason}\n\n"
                "Exegesis will save the full raw transcript before compacting. "
                "You can compact this chat or start a fresh chat instead."
            ),
            classes="workflow-card-body",
        )
        with Horizontal(classes="workflow-history-card-actions"):
            yield Button("Compact to Continue", id="compaction-compact", classes="compact-action-primary")
            yield Button("Start New Chat", id="compaction-new-chat", classes="compact-action-warning")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "compaction-compact":
            self.post_message(self.CompactRequested(self))
        elif event.button.id == "compaction-new-chat":
            self.post_message(self.NewChatRequested(self))


class WorkflowPane(Vertical):
    class ChatActivated(Message):
        def __init__(self, workflow_pane: "WorkflowPane", chat: WorkflowChat) -> None:
            super().__init__()
            self.workflow_pane = workflow_pane
            self.chat = chat

    class TranscriptSaved(Message):
        def __init__(self, workflow_pane: "WorkflowPane", chat: WorkflowChat, path: Path) -> None:
            super().__init__()
            self.workflow_pane = workflow_pane
            self.chat = chat
            self.path = path
            self.compacted = False

    class ChatCompacted(Message):
        def __init__(
            self,
            workflow_pane: "WorkflowPane",
            chat: WorkflowChat,
            path: Path,
            entry: HistoryCompactionEntry,
        ) -> None:
            super().__init__()
            self.workflow_pane = workflow_pane
            self.chat = chat
            self.path = path
            self.entry = entry

    class ChatCreated(Message):
        def __init__(self, workflow_pane: "WorkflowPane", chat: WorkflowChat) -> None:
            super().__init__()
            self.workflow_pane = workflow_pane
            self.chat = chat

    class DraftRequested(Message):
        def __init__(
            self,
            workflow_pane: "WorkflowPane",
            chat_slug: str,
            instruction_text: str,
            generated_text: str,
        ) -> None:
            super().__init__()
            self.workflow_pane = workflow_pane
            self.chat_slug = chat_slug
            self.instruction_text = instruction_text
            self.generated_text = generated_text

    class SearchResultSelected(Message):
        def __init__(
            self,
            workflow_pane: "WorkflowPane",
            document_slug: str,
            document_title: str,
            match_range: tuple[int, int] | None,
        ) -> None:
            super().__init__()
            self.workflow_pane = workflow_pane
            self.document_slug = document_slug
            self.document_title = document_title
            self.match_range = match_range

    class RewriteProposalReady(Message):
        def __init__(
            self,
            workflow_pane: "WorkflowPane",
            chat_slug: str,
            document_slug: str,
            document_title: str,
            target_range: tuple[int, int],
            original_text: str,
            instruction_text: str,
            proposed_text: str,
        ) -> None:
            super().__init__()
            self.workflow_pane = workflow_pane
            self.chat_slug = chat_slug
            self.document_slug = document_slug
            self.document_title = document_title
            self.target_range = target_range
            self.original_text = original_text
            self.instruction_text = instruction_text
            self.proposed_text = proposed_text

    class PatchDecisionRequested(Message):
        def __init__(self, workflow_pane: "WorkflowPane", patch_id: str, decision: str) -> None:
            super().__init__()
            self.workflow_pane = workflow_pane
            self.patch_id = patch_id
            self.decision = decision

    def __init__(self, backend: TerminalChatBackend | None = None) -> None:
        super().__init__(id=WORKFLOW_PANE_COPY.pane_id, classes="shell-pane")
        self.border_title = WORKFLOW_PANE_COPY.title
        self._backend = backend or MistralChatBackend()
        self._open_tabs: list[str] = [PRIMARY_CHAT_SLUG]
        self._active_slug = PRIMARY_CHAT_SLUG
        self._chat_counter = 2
        self._request_counter = 0
        self._status_message = ""
        self._workers: dict[str, Worker[None]] = {}
        self._history_render_versions: dict[str, int] = {}
        self._history_render_locks: dict[str, asyncio.Lock] = {}

    def compose(self) -> ComposeResult:
        with Horizontal(id="workflow-header"):
            yield Static("", classes="toolbar-spacer")
            yield Button("New Chat", id=WORKFLOW_NEW_CHAT_ID, classes="compact-action-primary")
            yield Button("Close chat", id=WORKFLOW_CLOSE_CHAT_ID, classes="compact-action-warning")
        with TabbedContent(initial=PRIMARY_CHAT_SLUG, id=WORKFLOW_TABBED_CONTENT_ID):
            yield self._make_pane(PRIMARY_CHAT_SLUG)
        with Horizontal(id=WORKFLOW_COMPOSER_ROW_ID):
            yield Input(placeholder="Search, draft, rewrite, or ask about the current document...", id=WORKFLOW_COMPOSER_INPUT_ID)
            yield Button("Chat", id=WORKFLOW_SEND_ID, variant="primary")
        with Horizontal(id="workflow-toolbar"):
            yield Button("Search", id=WORKFLOW_SEARCH_ID, classes="compact-action-primary")
            yield Button("Draft", id=WORKFLOW_DRAFT_ID, classes="compact-action-primary")
            yield Button("Rewrite", id=WORKFLOW_REWRITE_SELECTION_ID, classes="compact-action-primary")
            yield Button("Save", id=WORKFLOW_SAVE_CHAT_ID, classes="compact-action-primary")
            yield Button("Compact", id=WORKFLOW_COMPACT_CHAT_ID, classes="compact-action-primary")
            yield Static("", id=WORKFLOW_STATUS_ID)
            yield Static("", classes="workflow-status-spacer")

    def on_mount(self) -> None:
        self._sync_status()
        self._render_chat(self._active_slug)

    @property
    def active_chat(self) -> WorkflowChat:
        return WORKFLOW_CHATS[self._active_slug]

    def focus_editor(self) -> None:
        composer = self.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
        if not composer.disabled:
            composer.focus()
        else:
            self._history_for_slug(self._active_slug).focus()

    def set_status(self, message: str) -> None:
        self._status_message = message
        self._sync_status()

    def refresh_context_meter(self) -> None:
        if self.is_mounted:
            self._sync_status()

    async def new_chat(self) -> WorkflowChat:
        slug = f"chat-{self._chat_counter:02d}"
        self._chat_counter += 1
        chat = WorkflowChat(
            slug=slug,
            title=f"Chat {self._chat_counter - 1}",
            summary="Fresh live chat for trying a new prompt or workflow turn.",
            context_available=EMPTY_CONTEXT_USAGE_TEXT,
            status_note="fresh context window; no transcript saved yet",
            messages=[],
            history_entries=[],
        )
        WORKFLOW_CHATS[slug] = chat
        self._open_tabs.append(slug)
        tabbed = self.query_one(f"#{WORKFLOW_TABBED_CONTENT_ID}", TabbedContent)
        await tabbed.add_pane(self._make_pane(slug))
        tabbed.active = slug
        self._active_slug = slug
        self._sync_status()
        self._render_chat(slug)
        self.focus_editor()
        self.post_message(self.ChatCreated(self, chat))
        self.post_message(self.ChatActivated(self, chat))
        return chat

    async def close_active_chat(self) -> bool:
        if self.active_chat.generating:
            self.stop_active_generation()
            return False
        if not self.active_chat.closable:
            return False
        closing_slug = self._active_slug
        current_index = self._open_tabs.index(closing_slug)
        self._open_tabs.remove(closing_slug)
        fallback_slug = self._open_tabs[max(0, current_index - 1)]
        tabbed = self.query_one(f"#{WORKFLOW_TABBED_CONTENT_ID}", TabbedContent)
        await tabbed.remove_pane(closing_slug)
        self._active_slug = fallback_slug
        tabbed.active = fallback_slug
        self._sync_status()
        self._render_chat(fallback_slug)
        self.focus_editor()
        self.post_message(self.ChatActivated(self, self.active_chat))
        return True

    def save_active_transcript(self) -> Path:
        WORKFLOW_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        chat = self.active_chat
        path = WORKFLOW_ARTIFACTS_DIR / chat.transcript_name
        path.write_text(self._transcript_markdown(chat), encoding="utf-8")
        register_workflow_document(
            slug=f"transcript-{chat.slug}",
            title=chat.transcript_name,
            summary=f"Saved transcript from {chat.title.lower()} in the notebook pane.",
            location=chat.transcript_location,
            content=path.read_text(encoding="utf-8"),
        )
        self.post_message(self.TranscriptSaved(self, chat, path))
        return path

    def compact_active_chat(self, *, automatic: bool = False) -> Path | None:
        chat = self.active_chat
        if chat.generating:
            self.set_status("Wait for the current response to finish before compacting.")
            return None
        compactable_entries = [
            entry
            for entry in chat.history_entries
            if isinstance(entry, (HistoryTextEntry, HistoryStatusEntry, HistorySearchEntry))
        ]
        if len(compactable_entries) < 2:
            self.set_status("Not enough notebook history to compact yet.")
            return None
        path = self._save_compacted_transcript(chat)
        original_tokens = self._estimated_used_tokens(chat)
        source_count = len(chat.history_entries)
        summary = self._compaction_summary_text(chat, source_count)
        chat.messages = [ChatMessage("system", f"Compacted notebook context:\n{summary}")]
        chat.history_entries = [HistoryStatusEntry(summary)]
        compacted_tokens = self._estimated_used_tokens(chat)
        ratio = compacted_tokens / original_tokens if original_tokens else 1.0
        entry = HistoryCompactionEntry(
            transcript_title=path.name,
            transcript_location=f"transcripts/Compacted Conversations/{path.name}",
            source_chat_slug=chat.slug,
            source_entry_count=source_count,
            original_tokens=original_tokens,
            compacted_tokens=compacted_tokens,
            compression_ratio=ratio,
            automatic=automatic,
        )
        chat.history_entries.append(entry)
        chat.status_note = "using compacted notebook context; full raw transcript is saved"
        self._render_chat(chat.slug)
        self.set_status("Notebook context compacted. Raw history is still saved.")
        self._sync_status()
        self.post_message(self.ChatCompacted(self, chat, path, entry))
        return path

    async def new_chat_from_transcript(self, *, title: str, transcript_content: str, location: str) -> WorkflowChat:
        chat = await self.new_chat()
        chat.title = f"Restored: {title}"
        chat.summary = f"New chat started from compacted transcript {title}."
        chat.status_note = "restored from compacted conversation transcript"
        chat.messages = [
            ChatMessage(
                "system",
                (
                    "This chat was started from a saved compacted-conversation transcript. "
                    "Use it as raw prior notebook history, not as a project source document."
                ),
            )
        ]
        chat.history_entries = [
            HistoryStatusEntry(f"Restored from compacted conversation transcript: {location}"),
            HistoryTextEntry("assistant", transcript_content),
        ]
        tabbed = self.query_one(f"#{WORKFLOW_TABBED_CONTENT_ID}", TabbedContent)
        pane = tabbed.get_pane(chat.slug)
        pane.title = chat.title
        self._sync_status()
        self._render_chat(chat.slug)
        self.focus_editor()
        self.post_message(self.ChatActivated(self, chat))
        return chat

    def send_active_message(self) -> None:
        pending_proposal = self._pending_proposal_review_entry(self.active_chat)
        if pending_proposal is not None:
            if pending_proposal.patch_id.startswith("draft-"):
                self._start_request("draft", proposal_feedback_entry=pending_proposal)
                return
            rewrite_target = self._rewrite_target_from_review_entry(pending_proposal)
            if rewrite_target is not None:
                self._start_request("rewrite", rewrite_target=rewrite_target, proposal_feedback_entry=pending_proposal)
                return
        self._start_request("chat")

    def draft_into_document(self) -> None:
        self._start_request("draft")

    def rewrite_selection(self) -> None:
        if self.has_patch_review():
            self.set_status("Apply or reject the current revision proposal first.")
            return
        rewrite_target = self._rewrite_context()
        if rewrite_target is None:
            self.set_status("Select text in the document before requesting a rewrite.")
            return
        self._start_request("rewrite", rewrite_target=rewrite_target)

    def search_documents(self) -> None:
        chat = self.active_chat
        composer = self.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
        if chat.generating:
            self.set_status("Wait for the current response to finish.")
            return
        query = composer.value.strip()
        if not query:
            self.set_status("Enter a search query first.")
            return
        composer.value = ""
        chat.history_entries.append(HistoryTextEntry("user", f"Search: {query}"))
        results = self._search_documents(query)
        chat.history_entries.append(HistorySearchEntry(query=query, results=results))
        self._render_chat(chat.slug)
        self.set_status(f"Search found {len(results)} matching document(s).")

    def _start_request(
        self,
        request_mode: str,
        *,
        rewrite_target: RewriteRequestTarget | None = None,
        proposal_feedback_entry: HistoryRewriteEntry | None = None,
    ) -> None:
        chat = self.active_chat
        composer = self.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
        if chat.generating:
            self.set_status("Wait for the current response to finish.")
            return
        if not self._backend.is_configured():
            self.set_status("Open Model Settings and save a Mistral API key before using model actions.")
            request_settings = getattr(self.app, "shell_request_model_settings", None)
            if callable(request_settings):
                request_settings()
            return
        prompt = composer.value.strip()
        if not prompt:
            mode_text = "rewrite instruction" if request_mode == "rewrite" else "drafting instruction" if request_mode == "draft" else "message"
            self.set_status(f"Enter a {mode_text} first.")
            return
        shell_context = self._shell_context(rewrite_target)
        fixed_tokens = self._estimated_fixed_context_tokens_for_context(shell_context, request_mode)
        if self._fixed_context_is_too_large(fixed_tokens):
            message = self._fixed_context_too_large_message(fixed_tokens)
            chat.history_entries.append(HistoryStatusEntry(message))
            self.set_status(message)
            self._render_chat(chat.slug)
            self._sync_status()
            return
        used_tokens = self._estimated_used_tokens(chat)
        if used_tokens >= int(TERMINAL_CONTEXT_WINDOW_TOKENS * CONTEXT_HARD_LIMIT_RATIO):
            self._show_compaction_prompt(
                chat,
                used_tokens,
                "Estimated context is full. You may compact or start a new chat, but Exegesis will keep trying until the model refuses the request.",
            )
        elif used_tokens >= int(TERMINAL_CONTEXT_WINDOW_TOKENS * CONTEXT_STRONG_COMPACT_PROMPT_RATIO):
            self._show_compaction_prompt(
                chat,
                used_tokens,
                "This chat is close to the context limit. You can compact now, start a new chat, or keep going.",
            )
        elif used_tokens >= int(TERMINAL_CONTEXT_WINDOW_TOKENS * CONTEXT_EARLY_COMPACT_PROMPT_RATIO):
            self._show_compaction_prompt(
                chat,
                used_tokens,
                "This chat is getting long. You can compact soon, start a new chat, or keep going.",
            )
        request_prompt = self._proposal_feedback_prompt(prompt, proposal_feedback_entry) if proposal_feedback_entry is not None else prompt
        composer.value = ""
        chat.messages.append(ChatMessage("user", request_prompt))
        chat.messages.append(ChatMessage("assistant", "", streaming=True))
        chat.history_entries.append(HistoryTextEntry("user", prompt))
        if self._should_warn_about_withheld_transcript(shell_context):
            chat.history_entries.append(HistoryStatusEntry(NON_CONFIDENTIAL_TRANSCRIPT_WARNING))
            self.set_status("Full transcript withheld from non-confidential model context.")
        if request_mode in {"draft", "rewrite"}:
            chat.history_entries.append(HistoryStatusEntry(self._proposal_generation_status(request_mode)))
            chat.active_history_index = None
        else:
            chat.history_entries.append(HistoryTextEntry("assistant", "", streaming=True))
            chat.active_history_index = len(chat.history_entries) - 1
        self._request_counter += 1
        request_id = self._request_counter
        chat.generating = True
        chat.active_request_id = request_id
        chat.active_request_mode = request_mode
        chat.active_instruction_text = prompt
        chat.active_reasoning_index = None
        chat.active_rewrite_target = rewrite_target
        self._render_chat(chat.slug)
        self._sync_status()
        self._workers[chat.slug] = self.run_worker(
            self._stream_reply(chat.slug, request_id, request_mode),
            name=f"workflow-chat-{chat.slug}",
            group=f"chat:{chat.slug}",
            thread=False,
            exit_on_error=False,
            exclusive=True,
        )

    def _should_warn_about_withheld_transcript(self, shell_context: ShellChatContext) -> bool:
        return shell_context.document_type == "transcript" and shell_context.confidentiality_mode != "local-confidential"

    def stop_active_generation(self) -> None:
        chat = self.active_chat
        if not chat.generating:
            return
        self._backend.cancel(chat.slug)
        worker = self._workers.pop(chat.slug, None)
        if worker is not None:
            worker.cancel()
        chat.generating = False
        chat.active_request_id = None
        chat.active_request_mode = None
        chat.active_instruction_text = ""
        chat.active_rewrite_target = None
        if chat.messages and chat.messages[-1].role == "assistant":
            chat.messages[-1].streaming = False
        self._finalize_active_history_entry(chat)
        self.set_status("Stopped response.")
        self._render_chat(chat.slug)
        self._sync_status()

    def note_draft_inserted(self, chat_slug: str, document_title: str, document_type: str) -> None:
        chat = WORKFLOW_CHATS.get(chat_slug)
        if chat is None:
            return
        chat.history_entries.append(HistoryStatusEntry(f"Draft inserted into {document_title} ({document_type})."))
        self._render_chat(chat_slug)
        self.set_status(f"Draft inserted into {document_title}.")

    def note_patch_resolution(self, chat_slug: str, message: str) -> None:
        chat = WORKFLOW_CHATS.get(chat_slug)
        if chat is None:
            return
        chat.history_entries.append(HistoryStatusEntry(message))
        self._render_chat(chat_slug)
        self.set_status(message)

    def show_patch_review(self, data: PatchReviewCardData) -> None:
        slug = data.source_chat_slug if data.source_chat_slug in WORKFLOW_CHATS else self._active_slug
        chat = WORKFLOW_CHATS[slug]
        self._clear_patch_review_entries(chat)
        chat.history_entries.append(
            HistoryRewriteEntry(
                patch_id=data.patch_id,
                document_title=data.document_title,
                instruction_text=data.instruction_text,
                source_chat_slug=data.source_chat_slug,
                original_text=data.original_text,
                proposed_text=data.proposed_text,
                document_slug=data.document_slug,
                target_range=data.target_range,
            )
        )
        chat.pending_patch_id = data.patch_id
        self._render_chat(slug)
        self.set_status(f"Revision proposal ready for {data.document_title}.")

    def clear_patch_review(self, patch_id: str | None = None) -> None:
        for slug, chat in WORKFLOW_CHATS.items():
            if patch_id is None or chat.pending_patch_id == patch_id:
                self._clear_patch_review_entries(chat)
                self._render_chat(slug)

    def has_patch_review(self) -> bool:
        return any(chat.pending_patch_id for chat in WORKFLOW_CHATS.values())

    def _pending_proposal_review_entry(self, chat: WorkflowChat) -> HistoryRewriteEntry | None:
        if chat.pending_patch_id is None:
            return None
        for entry in reversed(chat.history_entries):
            if isinstance(entry, HistoryRewriteEntry) and entry.patch_id == chat.pending_patch_id:
                return entry
        return None

    def _rewrite_target_from_review_entry(self, entry: HistoryRewriteEntry) -> RewriteRequestTarget | None:
        if not entry.document_slug or entry.target_range is None:
            return None
        return RewriteRequestTarget(
            document_slug=entry.document_slug,
            document_title=entry.document_title,
            target_range=entry.target_range,
            original_text=entry.original_text,
        )

    @staticmethod
    def _proposal_generation_status(request_mode: str) -> str:
        return "Generating draft proposal..." if request_mode == "draft" else "Generating rewrite proposal..."

    def _proposal_feedback_prompt(self, feedback: str, entry: HistoryRewriteEntry | None) -> str:
        if entry is None:
            return feedback
        proposal_kind = "draft" if entry.patch_id.startswith("draft-") else "rewrite"
        original_label = "Original draft instruction" if proposal_kind == "draft" else "Original rewrite instruction"
        current_label = "Current pending draft proposal" if proposal_kind == "draft" else "Current pending rewrite proposal"
        return_instruction = (
            "Return only the revised draft proposal text."
            if proposal_kind == "draft"
            else "Return only the revised rewrite proposal text."
        )
        return (
            f"Revise the pending {proposal_kind} proposal using the user's feedback.\n\n"
            f"{original_label}:\n{entry.instruction_text}\n\n"
            f"{current_label}:\n{entry.proposed_text}\n\n"
            f"User feedback:\n{feedback}\n\n"
            f"{return_instruction}"
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == WORKFLOW_SEARCH_ID:
            self.search_documents()
        elif button_id == WORKFLOW_DRAFT_ID:
            self.draft_into_document()
        elif button_id == WORKFLOW_REWRITE_SELECTION_ID:
            self.rewrite_selection()
        elif button_id == WORKFLOW_NEW_CHAT_ID:
            await self.new_chat()
        elif button_id == WORKFLOW_SAVE_CHAT_ID:
            self.save_active_transcript()
        elif button_id == WORKFLOW_COMPACT_CHAT_ID:
            self.compact_active_chat()
        elif button_id == WORKFLOW_CLOSE_CHAT_ID:
            await self.close_active_chat()
        elif button_id == WORKFLOW_SEND_ID:
            self.send_active_message()

    async def on_compaction_prompt_card_compact_requested(self, message: CompactionPromptCard.CompactRequested) -> None:
        self._clear_compaction_prompt(self.active_chat)
        self.compact_active_chat()

    async def on_compaction_prompt_card_new_chat_requested(self, message: CompactionPromptCard.NewChatRequested) -> None:
        self._clear_compaction_prompt(self.active_chat)
        await self.new_chat()
        self.set_status("Started a new chat instead of compacting.")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == WORKFLOW_COMPOSER_INPUT_ID:
            self.send_active_message()

    def on_search_results_card_result_selected(self, message: SearchResultsCard.ResultSelected) -> None:
        match = message.result.match_at(message.match_index)
        self.post_message(
            self.SearchResultSelected(
                self,
                message.result.document_slug,
                message.result.title,
                match.match_range if match is not None else message.result.match_range,
            )
        )

    def on_rewrite_review_history_card_apply_requested(self, message: RewriteReviewHistoryCard.ApplyRequested) -> None:
        self.post_message(self.PatchDecisionRequested(self, message.patch_id, "apply"))

    def on_rewrite_review_history_card_reject_requested(self, message: RewriteReviewHistoryCard.RejectRequested) -> None:
        self.post_message(self.PatchDecisionRequested(self, message.patch_id, "reject"))

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        if event.tabbed_content.id != WORKFLOW_TABBED_CONTENT_ID:
            return
        pane = getattr(event, "pane", None)
        if pane is None or pane.id is None:
            return
        self._active_slug = pane.id
        self._sync_status()
        self._render_chat(self._active_slug)
        self.post_message(self.ChatActivated(self, self.active_chat))

    def _apply_chat_delta(self, slug: str, request_id: int, text: str) -> None:
        chat = WORKFLOW_CHATS.get(slug)
        if chat is None or chat.active_request_id != request_id:
            return
        assistant = self._active_assistant_message(chat)
        assistant.content += text
        if chat.active_request_mode not in {"draft", "rewrite"}:
            self._update_active_history_text(chat, text)
            self._render_chat(slug)

    def _apply_reasoning_delta(self, slug: str, request_id: int, text: str) -> None:
        chat = WORKFLOW_CHATS.get(slug)
        if chat is None or chat.active_request_id != request_id:
            return
        if chat.active_reasoning_index is None:
            insert_at = chat.active_history_index if chat.active_history_index is not None else len(chat.history_entries)
            chat.history_entries.insert(insert_at, HistoryReasoningEntry(text, streaming=True))
            chat.active_reasoning_index = insert_at
            if chat.active_history_index is not None and chat.active_history_index >= insert_at:
                chat.active_history_index += 1
        else:
            entry = chat.history_entries[chat.active_reasoning_index]
            if isinstance(entry, HistoryReasoningEntry):
                entry.content += text
        self._render_chat(slug)

    def _complete_chat_stream(self, slug: str, request_id: int, replay_content: object | None = None) -> None:
        chat = WORKFLOW_CHATS.get(slug)
        if chat is None or chat.active_request_id != request_id:
            return
        request_mode = chat.active_request_mode or "chat"
        instruction_text = chat.active_instruction_text
        rewrite_target = chat.active_rewrite_target
        assistant = self._active_assistant_message(chat)
        assistant.streaming = False
        if replay_content is not None:
            assistant.provider_content = replay_content
        elif assistant.provider_content is None:
            assistant.provider_content = assistant.content
        self._finalize_active_reasoning_entry(chat)
        if request_mode == "draft":
            generated_text = assistant.content.strip()
            if not generated_text:
                self._fail_chat_stream(slug, request_id, "Draft request returned no text to insert.")
                return
        elif request_mode == "rewrite":
            generated_text = assistant.content.strip()
            if not generated_text:
                self._fail_chat_stream(slug, request_id, "Rewrite request returned no proposal text.")
                return
            if rewrite_target is None:
                self._fail_chat_stream(slug, request_id, "Rewrite request lost its document selection context.")
                return
        chat.generating = False
        chat.active_request_id = None
        chat.active_request_mode = None
        chat.active_instruction_text = ""
        chat.active_reasoning_index = None
        chat.active_rewrite_target = None
        self._workers.pop(slug, None)
        if request_mode == "rewrite":
            self._remove_last_status_entry(chat, self._proposal_generation_status("rewrite"))
            self.post_message(
                self.RewriteProposalReady(
                    self,
                    slug,
                    rewrite_target.document_slug,
                    rewrite_target.document_title,
                    rewrite_target.target_range,
                    rewrite_target.original_text,
                    instruction_text,
                    generated_text,
                )
            )
        else:
            if request_mode == "draft":
                self._remove_last_status_entry(chat, self._proposal_generation_status("draft"))
                self.post_message(self.DraftRequested(self, slug, instruction_text, generated_text))
            else:
                self._finalize_active_history_entry(chat)
                if slug == self._active_slug:
                    self.set_status("")
                else:
                    self._sync_status()
        self._render_chat(slug)
        self._sync_status()

    def _fail_chat_stream(self, slug: str, request_id: int, error: str) -> None:
        chat = WORKFLOW_CHATS.get(slug)
        if chat is None or chat.active_request_id != request_id:
            return
        fixed_tokens = self._estimated_fixed_context_tokens(
            chat,
            request_mode=chat.active_request_mode or "chat",
            rewrite_target=chat.active_rewrite_target,
        )
        chat.generating = False
        chat.active_request_id = None
        chat.active_request_mode = None
        chat.active_instruction_text = ""
        chat.active_rewrite_target = None
        if chat.messages and chat.messages[-1].role == "assistant" and not chat.messages[-1].content:
            chat.messages.pop()
        else:
            self._active_assistant_message(chat).streaming = False
        self._remove_active_history_entry(chat)
        self._remove_active_reasoning_entry(chat)
        self._remove_last_status_entry(chat, self._proposal_generation_status("draft"))
        self._remove_last_status_entry(chat, self._proposal_generation_status("rewrite"))
        chat.history_entries.append(HistoryStatusEntry(error))
        self._workers.pop(slug, None)
        if self._is_context_limit_error(error) and self._fixed_context_is_too_large(fixed_tokens):
            message = self._fixed_context_too_large_message(fixed_tokens)
            chat.history_entries.append(HistoryStatusEntry(message))
            self.set_status(message)
        elif self._is_context_limit_error(error):
            self._show_compaction_prompt(
                chat,
                self._estimated_used_tokens(chat),
                "The model reported that this chat is out of context. Compact to continue or start a new chat.",
            )
            self.set_status("Model reported context limit. Compact to continue or start a new chat.")
        else:
            self.set_status(error)
        self._render_chat(slug)
        self._sync_status()

    @staticmethod
    def _is_context_limit_error(error: str) -> bool:
        lowered = error.casefold()
        return any(
            phrase in lowered
            for phrase in (
                "context length",
                "context limit",
                "context window",
                "maximum context",
                "too many tokens",
                "token limit",
                "input too long",
                "request too large",
            )
        )

    def _sync_status(self) -> None:
        chat = self.active_chat
        chat.context_available = self._context_available_text(chat)
        self.border_subtitle = chat.context_available
        status = self._status_message
        if not status and not self._backend.is_configured():
            status = "Search works locally. Open Model Settings to enable Draft, Rewrite, and Chat."
        self.query_one(f"#{WORKFLOW_STATUS_ID}", Static).update(status)

        search_button = self.query_one(f"#{WORKFLOW_SEARCH_ID}", Button)
        draft_button = self.query_one(f"#{WORKFLOW_DRAFT_ID}", Button)
        rewrite_button = self.query_one(f"#{WORKFLOW_REWRITE_SELECTION_ID}", Button)
        new_chat_button = self.query_one(f"#{WORKFLOW_NEW_CHAT_ID}", Button)
        save_button = self.query_one(f"#{WORKFLOW_SAVE_CHAT_ID}", Button)
        compact_button = self.query_one(f"#{WORKFLOW_COMPACT_CHAT_ID}", Button)
        close_button = self.query_one(f"#{WORKFLOW_CLOSE_CHAT_ID}", Button)
        composer_input = self.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
        send_button = self.query_one(f"#{WORKFLOW_SEND_ID}", Button)

        composer_input.disabled = False
        search_button.disabled = chat.generating
        send_button.disabled = chat.generating
        draft_button.disabled = chat.generating
        rewrite_button.disabled = chat.generating or self.has_patch_review()
        new_chat_button.disabled = chat.generating
        save_button.disabled = chat.generating
        compact_button.disabled = chat.generating
        close_button.label = "Stop" if chat.generating else "Close chat"
        close_button.disabled = not chat.generating and not chat.closable

    def _history_for_slug(self, slug: str) -> VerticalScroll:
        return self.query_one(f"#workflow-history-{slug}", VerticalScroll)

    def _render_chat(self, slug: str) -> None:
        if not self.is_mounted:
            return
        version = self._history_render_versions.get(slug, 0) + 1
        self._history_render_versions[slug] = version
        asyncio.create_task(self._refresh_history_view(slug, version))

    async def _refresh_history_view(self, slug: str, version: int) -> None:
        try:
            history = self._history_for_slug(slug)
        except Exception:
            return
        lock = self._history_render_locks.setdefault(slug, asyncio.Lock())
        async with lock:
            if version != self._history_render_versions.get(slug):
                return
            await history.remove_children()
            if version != self._history_render_versions.get(slug):
                return
            chat = WORKFLOW_CHATS[slug]
            widgets = [self._widget_for_history_entry(entry) for entry in chat.history_entries]
            if not widgets:
                widgets = [Static("Live notebook history will appear here...", classes="workflow-history-placeholder")]
            await history.mount_all(widgets)
            history.scroll_end(animate=False)

    def _widget_for_history_entry(self, entry: object):
        if isinstance(entry, HistoryReasoningEntry):
            return ReasoningTraceHistoryCard(entry)
        if isinstance(entry, (HistoryTextEntry, HistoryStatusEntry)):
            return HistoryMarkdownEntry(entry)
        if isinstance(entry, HistorySearchEntry):
            return SearchResultsCard(entry)
        if isinstance(entry, HistoryRewriteEntry):
            return RewriteReviewHistoryCard(entry)
        if isinstance(entry, HistoryCompactionEntry):
            return CompactionHistoryCard(entry)
        if isinstance(entry, HistoryCompactionPromptEntry):
            return CompactionPromptCard(entry)
        return Static(str(entry), classes="workflow-history-block")

    def _rendered_history_text(self, chat: WorkflowChat) -> str:
        blocks: list[str] = []
        for entry in chat.history_entries:
            if isinstance(entry, HistoryTextEntry):
                blocks.append(f"**{entry.role.capitalize()}:**\n\n{entry.content}")
            elif isinstance(entry, HistoryReasoningEntry):
                blocks.append(f"### Reasoning Trace\n\n{entry.content}")
            elif isinstance(entry, HistoryStatusEntry):
                blocks.append(f"> {entry.content}")
            elif isinstance(entry, HistorySearchEntry):
                header = [f'### Search: "{entry.query}"']
                if entry.results:
                    header.extend(
                        f"- {result.title} ({result.document_type}, ~{result.token_count:,} tokens): {result.snippet}"
                        for result in entry.results
                    )
                else:
                    header.append("- No matching documents found.")
                blocks.append("\n".join(header))
            elif isinstance(entry, HistoryRewriteEntry):
                blocks.append(
                    "\n".join(
                        [
                            f"### Rewrite Proposal for {entry.document_title}",
                            f"- Source: {entry.source_chat_slug}",
                            f"- Instruction: {entry.instruction_text}",
                            "#### Original",
                            entry.original_text,
                            "#### Proposed",
                            entry.proposed_text,
                        ]
                    )
                )
            elif isinstance(entry, HistoryCompactionEntry):
                blocks.append(
                    "\n".join(
                        [
                            "### Compacted Context",
                            f"- Transcript: {entry.transcript_location}",
                            f"- Source chat: {entry.source_chat_slug}",
                            f"- Source entries: {entry.source_entry_count}",
                            f"- Original tokens: ~{entry.original_tokens:,}",
                            f"- Compacted tokens: ~{entry.compacted_tokens:,}",
                            f"- Compression ratio: {entry.compression_ratio:.0%}",
                        ]
                    )
                )
            elif isinstance(entry, HistoryCompactionPromptEntry):
                blocks.append(
                    "\n".join(
                        [
                            "### Context Limit",
                            f"- Used tokens: ~{entry.used_tokens:,}",
                            f"- Capacity: {entry.token_capacity:,}",
                            f"- Reason: {entry.reason}",
                            "- Options: Compact to Continue; Start New Chat",
                        ]
                    )
                )
        return "\n\n".join(blocks).strip()

    def _show_compaction_prompt(self, chat: WorkflowChat, used_tokens: int, reason: str) -> None:
        self._clear_compaction_prompt(chat)
        chat.history_entries.append(
            HistoryCompactionPromptEntry(
                used_tokens=used_tokens,
                token_capacity=TERMINAL_CONTEXT_WINDOW_TOKENS,
                reason=reason,
            )
        )
        self._render_chat(chat.slug)
        self.set_status("Choose Compact to Continue or Start New Chat.")

    def _clear_compaction_prompt(self, chat: WorkflowChat) -> None:
        chat.history_entries = [entry for entry in chat.history_entries if not isinstance(entry, HistoryCompactionPromptEntry)]

    def _transcript_markdown(self, chat: WorkflowChat) -> str:
        transcript = self._rendered_history_text(chat)
        header = "\n".join(
            [
                f"# {chat.title}",
                "",
                f"- Source: {chat.slug}",
                f"- Context available: {chat.context_available}",
                f"- Status: {chat.status_note}",
            ]
        )
        return f"{header}\n\n{transcript}\n"

    def _save_compacted_transcript(self, chat: WorkflowChat) -> Path:
        folder = WORKFLOW_ARTIFACTS_DIR / "Compacted Conversations"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / chat.transcript_name
        if path.exists():
            stem = path.stem
            suffix = path.suffix
            index = 2
            while path.exists():
                path = folder / f"{stem}-{index}{suffix}"
                index += 1
        path.write_text(self._transcript_markdown(chat), encoding="utf-8")
        return path

    def _compaction_summary_text(self, chat: WorkflowChat, source_count: int) -> str:
        excerpt = self._rendered_history_text(chat)
        if len(excerpt) > 2_400:
            excerpt = excerpt[:2_400].rstrip() + "\n\n[Earlier raw notebook history saved in the compacted transcript.]"
        return (
            "Notebook context compacted. Raw history is still saved in "
            f"`Transcripts/Compacted Conversations/{chat.transcript_name}`.\n\n"
            f"Compacted {source_count} notebook entries from {chat.title}.\n\n"
            "Recent useful context snapshot:\n\n"
            f"{excerpt or '(No raw notebook text.)'}"
        )

    def _context_available_text(self, chat: WorkflowChat) -> str:
        used_tokens = self._estimated_used_tokens(chat)
        return self._format_context_usage(used_tokens, TERMINAL_CONTEXT_WINDOW_TOKENS)

    def _estimated_used_tokens(self, chat: WorkflowChat) -> int:
        shell_context = self._shell_context(chat.active_rewrite_target)
        total_chars = self._fixed_context_chars(shell_context, chat.active_request_mode or "chat")
        total_chars += sum(len(message.content) for message in chat.messages)
        structural_overhead = len(chat.messages) * 12
        # Approximate fixed message framing for the system prompt and shell context.
        return max(0, ceil((total_chars / 4) + structural_overhead + 24))

    def _estimated_fixed_context_tokens(
        self,
        chat: WorkflowChat,
        *,
        request_mode: str = "chat",
        rewrite_target: RewriteRequestTarget | None = None,
    ) -> int:
        shell_context = self._shell_context(rewrite_target)
        return self._estimated_fixed_context_tokens_for_context(shell_context, request_mode)

    def _estimated_fixed_context_tokens_for_context(self, shell_context: ShellChatContext, request_mode: str) -> int:
        total_chars = self._fixed_context_chars(shell_context, request_mode)
        # Fixed context includes the system prompt and shell context framing before chat history is added.
        return max(0, ceil((total_chars / 4) + 24))

    def _fixed_context_chars(self, shell_context: ShellChatContext, request_mode: str) -> int:
        context_parts = [
            self._system_prompt_text(),
            self._shell_context_prompt_text(shell_context, request_mode),
        ]
        return sum(len(part) for part in context_parts)

    @staticmethod
    def _fixed_context_is_too_large(fixed_tokens: int) -> bool:
        return fixed_tokens >= int(TERMINAL_CONTEXT_WINDOW_TOKENS * CONTEXT_HARD_LIMIT_RATIO)

    def _fixed_context_too_large_message(self, fixed_tokens: int) -> str:
        return (
            "Request not sent: current document and basket context already exceed the model window.\n\n"
            f"Fixed context: ~{fixed_tokens:,} / {TERMINAL_CONTEXT_WINDOW_TOKENS:,} tokens before chat history.\n\n"
            "Compaction only reduces notebook chat history.\n"
            "Please remove basket items, use excerpts instead of whole files, or switch to a smaller current document."
        )

    def _system_prompt_text(self) -> str:
        try:
            return DEFAULT_SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()
        except OSError:
            return "Exegesis writer system prompt."

    def _shell_context_prompt_text(self, shell_context: ShellChatContext, request_mode: str) -> str:
        mode = request_mode if request_mode in {"chat", "draft", "rewrite", "summary"} else "chat"
        transcript_policy = ""
        if shell_context.document_type == "transcript":
            document_content = (
                "[Transcript metadata only. The full transcript text is intentionally withheld because this is a "
                "non-confidential project. Do not claim to know, summarize, quote, analyze, or answer questions about "
                "the transcript content unless the user provides excerpts, selected text, snippets, or search results "
                "in this chat.]"
            )
            transcript_policy = (
                "- Transcript context policy: full transcript text is not available in this non-confidential model "
                "context. If the user asks about the active transcript, start the response by saying the full "
                "transcript is withheld in non-confidential mode. Do not ask how you can assist with the transcript. "
                "Ask how you can assist with the project, or invite the user to provide excerpts, selected passages, "
                "snippets, or search results for transcript-specific help.\n"
            )
        else:
            document_content = shell_context.document_content.strip() or "(empty document)"
        basket_context = shell_context.basket_context.strip() or "(empty basket)"
        selection_context = shell_context.selected_text.strip()
        mode_instruction = {
            "draft": (
                "Mode: draft. Use the open document and basket context to generate text for insertion. "
                "If drafting a body section, paragraph, or passage, return only that body text and do not repeat "
                "the document title or existing section heading unless explicitly asked."
            ),
            "rewrite": "Mode: rewrite. Use the open document, basket context, and selected text to rewrite only the selection.",
            "summary": "Mode: summary. Summarize the current open document according to the requested target length.",
        }.get(mode, "Mode: chat. Answer using the current document and basket context.")
        return (
            "Current shell context:\n"
            f"- Project: {shell_context.project_name}\n"
            f"- Active document: {shell_context.document_title}\n"
            f"- Active document type: {shell_context.document_type}\n"
            f"- Confidentiality mode: {shell_context.confidentiality_mode}\n\n"
            f"{transcript_policy}"
            "Current open document content:\n"
            "<current_document>\n"
            f"{document_content}\n"
            "</current_document>\n\n"
            "Active rewrite selection:\n"
            "<selected_text>\n"
            f"{selection_context}\n"
            "</selected_text>\n\n"
            "Current basket context:\n"
            "<basket>\n"
            f"{basket_context}\n"
            "</basket>\n\n"
            f"{mode_instruction}\n"
        )

    def _format_context_usage(self, used_tokens: int, token_capacity: int) -> str:
        percentage = (used_tokens / token_capacity) * 100 if token_capacity else 0
        if used_tokens == 0:
            percentage_text = "0%"
        elif percentage < 1:
            percentage_text = f"{percentage:.2f}%"
        elif percentage < 10:
            percentage_text = f"{percentage:.1f}%"
        else:
            percentage_text = f"{percentage:.0f}%"
        return f"{percentage_text} context used (~{used_tokens:,} / {token_capacity:,} tokens)"

    def _active_assistant_message(self, chat: WorkflowChat) -> ChatMessage:
        if chat.messages and chat.messages[-1].role == "assistant":
            return chat.messages[-1]
        assistant = ChatMessage("assistant", "", streaming=True)
        chat.messages.append(assistant)
        return assistant

    def _update_active_history_text(self, chat: WorkflowChat, text: str) -> None:
        index = chat.active_history_index
        if index is None or index >= len(chat.history_entries):
            return
        entry = chat.history_entries[index]
        if isinstance(entry, HistoryTextEntry):
            entry.content += text

    def _finalize_active_history_entry(self, chat: WorkflowChat) -> None:
        index = chat.active_history_index
        if index is None or index >= len(chat.history_entries):
            chat.active_history_index = None
            return
        entry = chat.history_entries[index]
        if isinstance(entry, HistoryTextEntry):
            entry.streaming = False
        chat.active_history_index = None

    def _finalize_active_reasoning_entry(self, chat: WorkflowChat) -> None:
        index = chat.active_reasoning_index
        if index is None or index >= len(chat.history_entries):
            chat.active_reasoning_index = None
            return
        entry = chat.history_entries[index]
        if isinstance(entry, HistoryReasoningEntry):
            entry.streaming = False

    def _remove_active_history_entry(self, chat: WorkflowChat) -> None:
        index = chat.active_history_index
        if index is None or index >= len(chat.history_entries):
            chat.active_history_index = None
            return
        chat.history_entries.pop(index)
        chat.active_history_index = None

    def _remove_active_reasoning_entry(self, chat: WorkflowChat) -> None:
        index = chat.active_reasoning_index
        if index is None or index >= len(chat.history_entries):
            chat.active_reasoning_index = None
            return
        chat.history_entries.pop(index)
        chat.active_reasoning_index = None

    def _remove_last_status_entry(self, chat: WorkflowChat, content: str) -> None:
        for index in range(len(chat.history_entries) - 1, -1, -1):
            entry = chat.history_entries[index]
            if isinstance(entry, HistoryStatusEntry) and entry.content == content:
                chat.history_entries.pop(index)
                return

    def _clear_patch_review_entries(self, chat: WorkflowChat) -> None:
        chat.history_entries = [entry for entry in chat.history_entries if not isinstance(entry, HistoryRewriteEntry)]
        chat.pending_patch_id = None

    async def _stream_reply(self, slug: str, request_id: int, request_mode: str) -> None:
        chat = WORKFLOW_CHATS[slug]
        shell_context = self._shell_context(chat.active_rewrite_target if request_mode == "rewrite" else None)
        try:
            async for event in self._backend.stream_reply(slug, chat.messages, shell_context, request_mode=request_mode):
                if event.kind == "assistant_delta":
                    self.call_later(self._apply_chat_delta, slug, request_id, event.text)
                elif event.kind == "reasoning_delta":
                    self.call_later(self._apply_reasoning_delta, slug, request_id, event.text)
                elif event.kind == "assistant_done":
                    self.call_later(self._complete_chat_stream, slug, request_id, event.replay_content)
                elif event.kind == "error":
                    self.call_later(self._fail_chat_stream, slug, request_id, event.error)
                    return
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self.call_later(self._fail_chat_stream, slug, request_id, f"Mistral request failed: {exc}")

    def _search_documents(self, query: str) -> list[SearchResultItem]:
        if hasattr(self.app, "shell_search_documents"):
            raw_results = self.app.shell_search_documents(query)
        else:
            raw_results = []
        results: list[SearchResultItem] = []
        for item in raw_results:
            snippet = str(item.get("snippet", "")).strip()
            if not snippet:
                snippet = "Matching text found in this document."
            raw_matches = item.get("matches") or []
            matches: list[SearchResultMatch] = []
            for raw_match in raw_matches:
                match_range = raw_match.get("match_range") if isinstance(raw_match, dict) else None
                if match_range is None:
                    continue
                match_snippet = str(raw_match.get("snippet", "")).strip() if isinstance(raw_match, dict) else ""
                matches.append(
                    SearchResultMatch(
                        snippet=match_snippet or snippet,
                        match_range=tuple(match_range),
                    )
                )
            fallback_range = tuple(item["match_range"]) if item.get("match_range") is not None else None
            if not matches and fallback_range is not None:
                matches.append(SearchResultMatch(snippet=snippet, match_range=fallback_range))
            results.append(
                SearchResultItem(
                    document_slug=str(item["document_slug"]),
                    title=str(item["title"]),
                    document_type=str(item["document_type"]),
                    snippet=snippet,
                    token_count=int(item["token_count"]),
                    location=str(item.get("location", "")),
                    match_range=fallback_range,
                    matches=tuple(matches),
                )
            )
        return results

    def _rewrite_context(self) -> RewriteRequestTarget | None:
        if not hasattr(self.app, "shell_rewrite_context"):
            return None
        raw = self.app.shell_rewrite_context()
        if not raw:
            return None
        return RewriteRequestTarget(
            document_slug=str(raw["document_slug"]),
            document_title=str(raw["document_title"]),
            target_range=tuple(raw["target_range"]),
            original_text=str(raw["original_text"]),
        )

    def _shell_context(self, rewrite_target: RewriteRequestTarget | None = None) -> ShellChatContext:
        if hasattr(self.app, "shell_chat_context"):
            raw = self.app.shell_chat_context()
            return ShellChatContext(
                project_name=str(raw.get("project_name", "Current Project")),
                document_title=str(raw.get("document_title", "current_draft.md")),
                document_type=str(raw.get("document_type", "draft")),
                document_content=str(raw.get("document_content", "")),
                confidentiality_mode=str(raw.get("confidentiality_mode", "online")),
                basket_context=str(raw.get("basket_context", "")),
                selected_text=rewrite_target.original_text if rewrite_target is not None else "",
                selection_start=rewrite_target.target_range[0] if rewrite_target is not None else None,
                selection_end=rewrite_target.target_range[1] if rewrite_target is not None else None,
            )
        return ShellChatContext(
            project_name="Current Project",
            document_title="current_draft.md",
            document_type="draft",
            document_content="",
            confidentiality_mode="online",
            basket_context="",
            selected_text=rewrite_target.original_text if rewrite_target is not None else "",
            selection_start=rewrite_target.target_range[0] if rewrite_target is not None else None,
            selection_end=rewrite_target.target_range[1] if rewrite_target is not None else None,
        )

    def _make_pane(self, slug: str) -> TabPane:
        chat = WORKFLOW_CHATS[slug]
        return TabPane(
            chat.title,
            VerticalScroll(id=f"workflow-history-{slug}", classes="workflow-history"),
            id=slug,
        )


WORKFLOW_CARD_MAP: dict[str, object] = {}


__all__ = [
    "PRIMARY_CHAT_SLUG",
    "WORKFLOW_ARTIFACTS_DIR",
    "WORKFLOW_CARD_MAP",
    "WORKFLOW_CLOSE_CHAT_ID",
    "WORKFLOW_CHATS",
    "WORKFLOW_COMPOSER_INPUT_ID",
    "WORKFLOW_COMPOSER_ROW_ID",
    "WORKFLOW_DRAFT_ID",
    "WORKFLOW_NEW_CHAT_ID",
    "WORKFLOW_COMPACT_CHAT_ID",
    "WORKFLOW_PANE_COPY",
    "WORKFLOW_REWRITE_SELECTION_ID",
    "WORKFLOW_SAVE_CHAT_ID",
    "WORKFLOW_SEARCH_ID",
    "WORKFLOW_SEND_ID",
    "WORKFLOW_STATUS_ID",
    "WORKFLOW_TABBED_CONTENT_ID",
    "HistoryCompactionEntry",
    "HistoryCompactionPromptEntry",
    "HistoryReasoningEntry",
    "WorkflowChat",
    "WorkflowPane",
    "clipped_rewrite_card_text",
]
