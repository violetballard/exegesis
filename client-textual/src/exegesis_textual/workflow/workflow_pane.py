from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field, replace
from math import ceil
from pathlib import Path
from uuid import uuid4

from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Button, LoadingIndicator, Markdown, Static, TabPane, TabbedContent
from textual.worker import Worker

from exegesis_textual.actions.registry import (
    AppActionResult,
    ToolCallRequest,
    get_app_action_spec,
    provider_tool_specs,
)
from exegesis_textual.cards.patch_card import PatchReviewCardData
from exegesis_textual.panes import PaneCopy
from exegesis_textual.widgets import SystemClipboardInput as Input
from exegesis_textual.workflow.mistral_chat import (
    ChatEvent,
    ChatMessage,
    DEFAULT_SYSTEM_PROMPT_PATH,
    MistralChatBackend,
    ShellChatContext,
    TerminalChatBackend,
)
from exegesis_textual.services.model_settings import DEFAULT_CONTEXT_WINDOW_TOKENS

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
TERMINAL_CONTEXT_WINDOW_TOKENS = DEFAULT_CONTEXT_WINDOW_TOKENS
COMMAND_HISTORY_LIMIT = 100
CONTEXT_EARLY_COMPACT_PROMPT_RATIO = 0.75
CONTEXT_STRONG_COMPACT_PROMPT_RATIO = 0.90
CONTEXT_HARD_LIMIT_RATIO = 1.0
REWRITE_CARD_TEXT_LIMIT = 1_200
EMPTY_CONTEXT_USAGE_TEXT = f"0% context used (~0 / {TERMINAL_CONTEXT_WINDOW_TOKENS:,} tokens)"
NON_CONFIDENTIAL_TRANSCRIPT_WARNING = (
    "Non-confidential warning: full transcripts are not loaded into model context. "
    "Use excerpts, selected passages, search snippets, or text you provide here."
)
EXCERPT_INTENT_TERMS = (
    "excerpt",
    "quote",
    "quoted",
    "passage",
    "snippet",
    "selection",
    "selected text",
    "highlight",
    "highlighted",
)
SAFE_TRANSCRIPT_FILE_ACTION_TERMS = (
    "close",
    "close tab",
    "delete",
    "delete forever",
    "move to trash",
    "permanently delete",
    "remove",
    "rename",
    "restore",
    "trash",
    "update item",
)
RESTORE_TRASH_INTENT_TERMS = ("restore", "recover", "put back", "bring back")
PERMANENT_DELETE_INTENT_TERMS = ("delete forever", "permanently delete", "permanent delete", "purge")
DELETE_TO_TRASH_INTENT_TERMS = ("delete", "move to trash", "remove", "trash")
_DRAFT_INTENT_RE = re.compile(
    r"^\s*(?:please\s+)?(?:(?:can|could|would)\s+you\s+)?(?:write|draft|compose|generate)\b",
    re.IGNORECASE,
)
_DRAFT_TEXT_OBJECT_RE = re.compile(
    r"\b(?:abstract|body|conclusion|draft|finding|findings|introduction|paragraph|passage|section|sentence)\b",
    re.IGNORECASE,
)
_DRAFT_ADD_CREATE_RE = re.compile(r"^\s*(?:please\s+)?(?:add|create)\b", re.IGNORECASE)
_REWRITE_VERB_RE = re.compile(
    r"\b(?:shorten|tighten|condense|revise|rewrite|edit|polish|clarify|simplify|expand)\b",
    re.IGNORECASE,
)
_REWRITE_MAKE_RE = re.compile(
    r"\bmake\s+(?:it|this|that|the\s+(?:current\s+)?(?:selection|excerpt|passage|text))\b.*"
    r"\b(?:shorter|longer|clearer|stronger|tighter|more|less|concise|specific|polished|academic|readable)\b",
    re.IGNORECASE,
)
_GENERAL_QUESTION_RE = re.compile(
    r"^\s*(?:how\s+(?:do|should|can)\s+i|what\s+(?:is|are)|why\b|where\b|when\b|who\b|explain\b|tell\s+me\s+about\b)",
    re.IGNORECASE,
)
_HEADING_LINE_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*$")
_DRAFT_HEADING_ALIASES = {
    "abstract": ("abstract",),
    "introduction": ("introduction", "intro"),
    "background": ("background",),
    "methods": ("methods", "methodology", "method"),
    "methodology": ("methodology", "methods", "method"),
    "findings": ("findings", "finding", "results", "result"),
    "results": ("results", "result", "findings", "finding"),
    "discussion": ("discussion",),
    "conclusion": ("conclusion", "concluding"),
    "references": ("references", "reference", "bibliography"),
}


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
    visible: bool = True


@dataclass(frozen=True)
class HistoryStatusEntry:
    content: str


@dataclass
class HistoryReasoningEntry:
    content: str
    streaming: bool = False
    revealed: bool = False
    visible: bool = True


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
    block_insert: bool = False


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
class HistoryActionRequestEntry:
    action_id: str
    label: str
    message: str
    payload: dict[str, object] = field(default_factory=dict)
    conversation_turn_id: str | None = None
    options: tuple[dict[str, object], ...] = field(default_factory=tuple)
    input_name: str | None = None
    input_placeholder: str = ""
    request_id: str = field(default_factory=lambda: f"action-request-{uuid4().hex}")


@dataclass(frozen=True)
class HistoryActionResultEntry:
    action_id: str
    label: str
    status: str
    message: str
    data: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class DirectAppCommand:
    action_id: str
    payload: dict[str, object]


@dataclass(frozen=True)
class RewriteRequestTarget:
    document_slug: str
    document_title: str
    target_range: tuple[int, int]
    original_text: str
    block_insert: bool = False


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
    active_history_visible: bool = True
    active_reasoning_index: int | None = None
    active_rewrite_target: RewriteRequestTarget | None = None
    active_draft_target_range: tuple[int, int] | None = None
    active_draft_block_insert: bool = False
    pending_patch_id: str | None = None
    command_history: list[str] = field(default_factory=list)
    command_history_index: int | None = None
    command_history_draft: str = ""

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
        if self.source_entry.streaming:
            with Horizontal(classes="workflow-history-loading-row"):
                yield LoadingIndicator(classes="workflow-history-loading")
                yield Static("Thinking...", classes="workflow-history-loading-text")
        else:
            yield Static("Thinking complete", classes="workflow-reasoning-summary")
        if self.source_entry.revealed and not self.source_entry.streaming:
            yield Markdown(self.source_entry.content or "(no reasoning text captured)", classes="workflow-history-message")
        elif not self.source_entry.streaming:
            yield Static("Click to reveal reasoning trace.", classes="workflow-reasoning-summary")

    def on_click(self, event: events.Click) -> None:
        event.stop()
        if self.source_entry.streaming:
            return
        self.source_entry.revealed = not self.source_entry.revealed
        self.refresh(recompose=True)


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

    class AddToBasketRequested(Message):
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
            add_id = f"search-result-add-{index}"
            button_id = f"search-result-{index}"
            prev_id = f"search-result-prev-{index}"
            next_id = f"search-result-next-{index}"
            initial_match_index = self._entry.selected_match_indices.get(result.document_slug, 0)
            self._selected_match_index.setdefault(index - 1, initial_match_index)
            with Vertical(classes="workflow-search-result"):
                with Horizontal(classes="workflow-search-result-row"):
                    yield self.ResultControl(self, index - 1, "basket", "Add", id=add_id, classes="workflow-search-result-add")
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
        if action == "basket":
            self.post_message(self.AddToBasketRequested(self, result, current_index))
            return
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


class ActionRequestCard(Vertical):
    class ConfirmRequested(Message):
        def __init__(self, card: "ActionRequestCard", entry: HistoryActionRequestEntry) -> None:
            super().__init__()
            self.card = card
            self.entry = entry

    class CancelRequested(Message):
        def __init__(self, card: "ActionRequestCard", entry: HistoryActionRequestEntry) -> None:
            super().__init__()
            self.card = card
            self.entry = entry

    def __init__(self, entry: HistoryActionRequestEntry) -> None:
        super().__init__(classes="workflow-card workflow-action-card")
        self._entry = entry
        self.border_title = "Action Request"

    def compose(self) -> ComposeResult:
        yield Static(self._entry.label, classes="workflow-card-title")
        yield Static(self._entry.message, classes="workflow-card-body")
        payload_text = self._payload_summary()
        if payload_text:
            yield Static(payload_text, classes="workflow-card-meta")
        if self._entry.input_name:
            yield Input(
                placeholder=self._entry.input_placeholder or self._entry.input_name.replace("_", " ").title(),
                id="action-request-input",
            )
        with Horizontal(classes="workflow-history-card-actions"):
            if self._entry.options:
                for index, option in enumerate(self._entry.options):
                    label = str(option.get("label") or f"Option {index + 1}")
                    classes = str(option.get("classes") or "compact-action-primary")
                    yield Button(label, id=f"action-request-option-{index}", classes=classes)
            else:
                yield Button("Confirm", id="action-request-confirm", classes="compact-action-primary")
                yield Button("Cancel", id="action-request-cancel", classes="compact-action-warning")

    def _payload_summary(self) -> str:
        lines: list[str] = []
        for key, value in sorted(self._entry.payload.items()):
            if str(key).startswith("_") or value in (None, ""):
                continue
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "action-request-confirm":
            self.post_message(self.ConfirmRequested(self, self._entry))
        elif event.button.id == "action-request-cancel":
            self.post_message(self.CancelRequested(self, self._entry))
        elif event.button.id and event.button.id.startswith("action-request-option-"):
            index_text = event.button.id.removeprefix("action-request-option-")
            try:
                option = self._entry.options[int(index_text)]
            except (IndexError, ValueError):
                return
            payload = dict(self._entry.payload)
            payload.update(dict(option.get("payload") or {}))
            if self._entry.input_name:
                try:
                    input_value = self.query_one("#action-request-input", Input).value.strip()
                except Exception:
                    input_value = ""
                if input_value:
                    payload[self._entry.input_name] = input_value
            if option.get("cancel"):
                self.post_message(self.CancelRequested(self, self._entry))
                return
            self.post_message(self.ConfirmRequested(self, replace(self._entry, payload=payload)))


class ActionResultCard(Vertical):
    def __init__(self, entry: HistoryActionResultEntry) -> None:
        super().__init__(classes="workflow-card workflow-action-card")
        self._entry = entry
        self.border_title = "Action Result"

    def compose(self) -> ComposeResult:
        yield Static(self._entry.label, classes="workflow-card-title")
        yield Static(f"{self._status_label()}: {self._entry.message}", classes="workflow-card-body workflow-action-result-body")
        summary = self._data_summary()
        if summary:
            yield Static(summary, classes="workflow-card-meta")

    def _status_label(self) -> str:
        return self._entry.status.replace("_", " ").capitalize()

    def _data_summary(self) -> str:
        if not self._entry.data:
            return ""
        if self._entry.action_id == "search_documents":
            results = self._entry.data.get("results")
            if isinstance(results, list):
                return f"{len(results)} result(s) available."
        return "\n".join(f"- {key}: {value}" for key, value in sorted(self._entry.data.items()) if isinstance(value, (str, int, float, bool)))


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
            target_range: tuple[int, int] | None = None,
            block_insert: bool = False,
        ) -> None:
            super().__init__()
            self.workflow_pane = workflow_pane
            self.chat_slug = chat_slug
            self.instruction_text = instruction_text
            self.generated_text = generated_text
            self.target_range = target_range
            self.block_insert = block_insert

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

    class SearchResultAddToBasketRequested(Message):
        def __init__(
            self,
            workflow_pane: "WorkflowPane",
            document_slug: str,
            document_title: str,
            document_type: str,
            excerpt: str,
            match_range: tuple[int, int] | None,
        ) -> None:
            super().__init__()
            self.workflow_pane = workflow_pane
            self.document_slug = document_slug
            self.document_title = document_title
            self.document_type = document_type
            self.excerpt = excerpt
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
            block_insert: bool = False,
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
            self.block_insert = block_insert

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

    def _context_window_tokens(self) -> int:
        context_window = getattr(self._backend, "context_window_tokens", None)
        if callable(context_window):
            try:
                tokens = int(context_window())
            except (TypeError, ValueError):
                return TERMINAL_CONTEXT_WINDOW_TOKENS
            return tokens if tokens >= 0 else TERMINAL_CONTEXT_WINDOW_TOKENS
        return TERMINAL_CONTEXT_WINDOW_TOKENS

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
                self._start_request(
                    "draft",
                    proposal_feedback_entry=pending_proposal,
                    draft_target_range=pending_proposal.target_range,
                    draft_block_insert=pending_proposal.block_insert,
                )
                return
            rewrite_target = self._rewrite_target_from_review_entry(pending_proposal)
            if rewrite_target is not None:
                self._start_request("rewrite", rewrite_target=rewrite_target, proposal_feedback_entry=pending_proposal)
                return
        self._start_request("chat")

    def draft_into_document(
        self,
        *,
        target_range: tuple[int, int] | None = None,
        block_insert: bool = False,
        show_user_prompt: bool = True,
    ) -> None:
        self._start_request(
            "draft",
            draft_target_range=target_range,
            draft_block_insert=block_insert,
            show_user_prompt=show_user_prompt,
        )

    def rewrite_selection(self, target: RewriteRequestTarget | None = None, *, show_user_prompt: bool = True) -> None:
        if self.has_patch_review():
            self.set_status("Apply or reject the current revision proposal first.")
            return
        rewrite_target = target or self._rewrite_context()
        if rewrite_target is None:
            self.set_status("Select text in the document before requesting a rewrite.")
            return
        self._start_request("rewrite", rewrite_target=rewrite_target, show_user_prompt=show_user_prompt)

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
        self._record_command_history(chat, query)
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
        draft_target_range: tuple[int, int] | None = None,
        draft_block_insert: bool = False,
        show_user_prompt: bool = True,
    ) -> None:
        chat = self.active_chat
        composer = self.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
        if chat.generating:
            self.set_status("Wait for the current response to finish.")
            return
        prompt = composer.value.strip()
        if request_mode == "chat" and self._handle_direct_app_command(prompt):
            return
        if not self._backend.is_configured():
            self.set_status("Open Model Settings and save an API key before using model actions.")
            request_settings = getattr(self.app, "shell_request_model_settings", None)
            if callable(request_settings):
                request_settings()
            return
        if not prompt:
            mode_text = "rewrite instruction" if request_mode == "rewrite" else "drafting instruction" if request_mode == "draft" else "message"
            self.set_status(f"Enter a {mode_text} first.")
            return
        if request_mode == "chat":
            request_mode, rewrite_target = self._infer_chat_model_action(prompt)
        if request_mode == "draft" and draft_target_range is None:
            inferred_draft_range = self._draft_target_range_from_prompt(prompt)
            if inferred_draft_range is not None:
                draft_target_range = inferred_draft_range
                draft_block_insert = True
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
        token_capacity = self._context_window_tokens()
        if token_capacity > 0 and used_tokens >= int(token_capacity * CONTEXT_HARD_LIMIT_RATIO):
            self._show_compaction_prompt(
                chat,
                used_tokens,
                "Estimated context is full. You may compact or start a new chat, but Exegesis will keep trying until the model refuses the request.",
            )
        elif token_capacity > 0 and used_tokens >= int(token_capacity * CONTEXT_STRONG_COMPACT_PROMPT_RATIO):
            self._show_compaction_prompt(
                chat,
                used_tokens,
                "This chat is close to the context limit. You can compact now, start a new chat, or keep going.",
            )
        elif token_capacity > 0 and used_tokens >= int(token_capacity * CONTEXT_EARLY_COMPACT_PROMPT_RATIO):
            self._show_compaction_prompt(
                chat,
                used_tokens,
                "This chat is getting long. You can compact soon, start a new chat, or keep going.",
            )
        request_prompt = self._proposal_feedback_prompt(prompt, proposal_feedback_entry) if proposal_feedback_entry is not None else prompt
        if show_user_prompt:
            self._record_command_history(chat, prompt)
        composer.value = ""
        chat.history_entries.append(HistoryTextEntry("user", prompt, visible=show_user_prompt))
        if self._should_warn_about_withheld_transcript(shell_context, prompt):
            chat.history_entries.append(HistoryStatusEntry(NON_CONFIDENTIAL_TRANSCRIPT_WARNING))
            self.set_status("Full transcript withheld from non-confidential model context.")
            self._render_chat(chat.slug)
            self._sync_status()
            return
        chat.messages.append(ChatMessage("user", request_prompt))
        chat.messages.append(ChatMessage("assistant", "", streaming=True))
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
        chat.active_history_visible = True
        chat.active_rewrite_target = rewrite_target
        chat.active_draft_target_range = draft_target_range
        chat.active_draft_block_insert = draft_block_insert
        self._begin_reasoning_entry(chat)
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

    def _handle_direct_app_command(self, prompt: str) -> bool:
        command = self._direct_app_command_from_prompt(prompt)
        if command is None:
            return False
        chat = self.active_chat
        composer = self.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
        self._record_command_history(chat, prompt)
        composer.value = ""
        chat.messages.append(ChatMessage("user", prompt))
        chat.history_entries.append(HistoryTextEntry("user", prompt))
        try:
            spec = get_app_action_spec(command.action_id)
        except KeyError:
            result = AppActionResult("failed", f"Unknown app action: {command.action_id}")
            chat.history_entries.append(HistoryActionResultEntry(command.action_id, command.action_id, result.status, result.message, {}))
            self.set_status(result.message)
            self._render_chat(chat.slug)
            self._sync_status()
            return True
        result = AppActionResult(
            "pending_confirmation",
            f"{spec.label} requires confirmation before Exegesis changes project state.",
            card={
                "type": "action_request",
                "action_id": command.action_id,
                "label": spec.label,
                "payload": dict(command.payload),
                "conversation_turn_id": f"{chat.slug}:direct:{uuid4()}",
            },
        )
        chat.history_entries.append(
            self._action_request_entry_from_result(
                result,
                fallback_action_id=command.action_id,
                fallback_label=spec.label,
                fallback_payload=dict(command.payload),
                conversation_turn_id=None,
            )
        )
        self.set_status(result.message)
        self._render_chat(chat.slug)
        self._sync_status()
        return True

    def _direct_app_command_from_prompt(self, prompt: str) -> DirectAppCommand | None:
        text = prompt.strip()
        if not text or self._looks_like_file_operation_question(text):
            return None
        if self._user_prompt_requests_permanent_delete(text):
            target = self._direct_file_operation_target(text, "permanent_delete")
            return DirectAppCommand("permanently_delete_trash_item", {"trash_item": target} if target else {})
        if self._user_prompt_requests_restore(text):
            target = self._direct_file_operation_target(text, "restore")
            return DirectAppCommand("restore_trash_item", {"trash_item": target} if target else {})
        if self._user_prompt_requests_delete_to_trash(text):
            target = self._direct_file_operation_target(text, "delete")
            return DirectAppCommand("move_document_to_trash", {"document": target} if target else {})
        return None

    @staticmethod
    def _looks_like_file_operation_question(prompt: str) -> bool:
        normalized = prompt.strip().casefold()
        return normalized.startswith(("how do i ", "how can i ", "what happens", "why "))

    def _infer_chat_model_action(self, prompt: str) -> tuple[str, RewriteRequestTarget | None]:
        if self._looks_like_general_instruction_question(prompt):
            return "chat", None
        rewrite_target = self._rewrite_context()
        if rewrite_target is not None and self._prompt_requests_selection_rewrite(prompt):
            return "rewrite", rewrite_target
        if self._prompt_requests_active_document_draft(prompt):
            return "draft", None
        return "chat", None

    @staticmethod
    def _looks_like_general_instruction_question(prompt: str) -> bool:
        return bool(_GENERAL_QUESTION_RE.search(prompt.strip()))

    @staticmethod
    def _prompt_requests_selection_rewrite(prompt: str) -> bool:
        normalized = prompt.strip()
        return bool(_REWRITE_VERB_RE.search(normalized) or _REWRITE_MAKE_RE.search(normalized))

    @staticmethod
    def _prompt_requests_active_document_draft(prompt: str) -> bool:
        normalized = prompt.strip()
        if _DRAFT_INTENT_RE.search(normalized):
            return True
        return bool(_DRAFT_ADD_CREATE_RE.search(normalized) and _DRAFT_TEXT_OBJECT_RE.search(normalized))

    def _draft_target_range_from_prompt(self, prompt: str) -> tuple[int, int] | None:
        heading = self._draft_heading_from_prompt(prompt)
        if not heading:
            return None
        shell_context = self._shell_context(None)
        return self._document_section_body_range(shell_context.document_content, heading)

    def _draft_heading_from_prompt(self, prompt: str) -> str | None:
        shell_context = self._shell_context(None)
        document_headings = self._document_headings(shell_context.document_content)
        if not document_headings:
            return None
        prompt_text = self._normalized_prompt_match_text(prompt)
        for heading in sorted(document_headings, key=lambda value: len(value), reverse=True):
            heading_key = self._normalized_prompt_match_text(heading)
            if not heading_key:
                continue
            variants = _DRAFT_HEADING_ALIASES.get(heading_key, (heading_key,))
            if any(self._prompt_contains_phrase(prompt_text, variant) for variant in variants):
                return heading
        return None

    @staticmethod
    def _document_headings(document_text: str) -> tuple[str, ...]:
        headings: list[str] = []
        for line in document_text.splitlines():
            match = _HEADING_LINE_RE.match(line.strip())
            if not match:
                continue
            title = match.group("title").strip().strip("*_`").rstrip(":").strip()
            if title:
                headings.append(title)
        return tuple(headings)

    @staticmethod
    def _document_section_body_range(document_text: str, heading: str) -> tuple[int, int] | None:
        target = WorkflowPane._normalized_prompt_match_text(heading)
        if not target:
            return None
        lines = document_text.splitlines(keepends=True)
        offset = 0
        for index, line in enumerate(lines):
            match = _HEADING_LINE_RE.match(line.strip())
            if match is None or WorkflowPane._normalized_prompt_match_text(match.group("title")) != target:
                offset += len(line)
                continue
            section_start = offset + len(line)
            section_end = len(document_text)
            next_offset = section_start
            for next_line in lines[index + 1 :]:
                if _HEADING_LINE_RE.match(next_line.strip()):
                    section_end = next_offset
                    break
                next_offset += len(next_line)
            return (section_start, section_end)
        return None

    @staticmethod
    def _normalized_prompt_match_text(value: str) -> str:
        return " ".join(re.sub(r"[^a-z0-9]+", " ", value.casefold()).split())

    @staticmethod
    def _prompt_contains_phrase(prompt_text: str, phrase: str) -> bool:
        normalized_phrase = WorkflowPane._normalized_prompt_match_text(phrase)
        if not normalized_phrase:
            return False
        return bool(re.search(rf"(?:^|\s){re.escape(normalized_phrase)}(?:\s|$)", prompt_text))

    @staticmethod
    def _direct_file_operation_target(prompt: str, operation: str) -> str:
        target = prompt.strip().strip(" \t\r\n.!?")
        target = re.sub(r"^\s*(please\s+)?((can|could|would)\s+you\s+)?", "", target, flags=re.IGNORECASE)
        if operation == "restore":
            target = re.sub(r"^\s*(restore|recover|put\s+back|bring\s+back)\s+", "", target, flags=re.IGNORECASE)
            target = re.sub(r"\s+(from|out\s+of)\s+(the\s+)?trash\s*$", "", target, flags=re.IGNORECASE)
        elif operation == "permanent_delete":
            target = re.sub(r"^\s*(permanently\s+delete|permanent\s+delete|delete\s+forever|purge)\s+", "", target, flags=re.IGNORECASE)
            target = re.sub(r"\s+(from|out\s+of)\s+(the\s+)?trash\s*$", "", target, flags=re.IGNORECASE)
        else:
            target = re.sub(r"^\s*(delete|remove|trash)\s+", "", target, flags=re.IGNORECASE)
            target = re.sub(r"^\s*move\s+", "", target, flags=re.IGNORECASE)
            target = re.sub(r"\s+(to|into)\s+(the\s+)?trash\s*$", "", target, flags=re.IGNORECASE)
            target = re.sub(r"\s+from\s+(the\s+)?project\s*$", "", target, flags=re.IGNORECASE)
        target = re.sub(r"^\s*(the\s+)?(document|file|item)\s+(named|called)?\s*", "", target, flags=re.IGNORECASE)
        target = target.strip(" \t\r\n\"'`")
        if target.casefold() in {"", "it", "this", "that", "current", "selected"}:
            return ""
        return target

    def _should_warn_about_withheld_transcript(self, shell_context: ShellChatContext, prompt: str) -> bool:
        if shell_context.document_type != "transcript" or shell_context.confidentiality_mode == "local-confidential":
            return False
        if shell_context.selected_text.strip() and self._user_prompt_requests_excerpt(prompt):
            return False
        if self._user_prompt_requests_safe_transcript_file_action(prompt):
            return False
        return True

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
        chat.active_draft_target_range = None
        chat.active_draft_block_insert = False
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
                block_insert=data.block_insert,
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
            block_insert=entry.block_insert,
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

    async def on_action_request_card_confirm_requested(self, message: ActionRequestCard.ConfirmRequested) -> None:
        target_chat = self.active_chat
        if self._pending_action_request_index(message.entry, chat=target_chat) is None:
            self.set_status(f"{message.entry.label} is no longer active.")
            self._sync_status()
            return
        result = await self._dispatch_confirmed_action_request(message.entry)
        self._replace_action_request_with_result(message.entry, result, chat=target_chat)
        self.set_status(result.message)
        self._render_chat(self.active_chat.slug)
        self._sync_status()

    async def on_action_request_card_cancel_requested(self, message: ActionRequestCard.CancelRequested) -> None:
        target_chat = self.active_chat
        if self._pending_action_request_index(message.entry, chat=target_chat) is None:
            self.set_status(f"{message.entry.label} is no longer active.")
            self._sync_status()
            return
        result = AppActionResult("refused", f"Cancelled {message.entry.label}.")
        self._replace_action_request_with_result(message.entry, result, chat=target_chat)
        self.set_status(result.message)
        self._render_chat(self.active_chat.slug)
        self._sync_status()

    async def _dispatch_confirmed_action_request(self, entry: HistoryActionRequestEntry) -> AppActionResult:
        dispatcher = getattr(self.app, "dispatch_app_action", None)
        if not callable(dispatcher):
            return AppActionResult("failed", "The shell action dispatcher is unavailable.")
        return await dispatcher(
            entry.action_id,
            dict(entry.payload),
            source="model_tool",
            conversation_turn_id=entry.conversation_turn_id,
            confirmed=True,
        )

    def _replace_action_request_with_result(
        self,
        request_entry: HistoryActionRequestEntry,
        result: AppActionResult,
        *,
        chat: WorkflowChat | None = None,
    ) -> None:
        target_chat = chat or self.active_chat
        replacement: HistoryActionRequestEntry | HistoryActionResultEntry
        if result.status == "pending_confirmation":
            replacement = self._action_request_entry_from_result(
                result,
                fallback_action_id=request_entry.action_id,
                fallback_label=request_entry.label,
                fallback_payload=dict(request_entry.payload),
                conversation_turn_id=request_entry.conversation_turn_id,
            )
        else:
            replacement = HistoryActionResultEntry(
                action_id=request_entry.action_id,
                label=request_entry.label,
                status=result.status,
                message=result.message,
                data=dict(result.data),
            )
        index = self._pending_action_request_index(request_entry, chat=target_chat)
        if index is None:
            target_chat.history_entries.append(replacement)
        else:
            target_chat.history_entries[index] = replacement

    def _pending_action_request_index(
        self,
        request_entry: HistoryActionRequestEntry,
        *,
        chat: WorkflowChat | None = None,
    ) -> int | None:
        target_chat = chat or self.active_chat
        for index, entry in enumerate(target_chat.history_entries):
            if isinstance(entry, HistoryActionRequestEntry) and entry.request_id == request_entry.request_id:
                return index
        return None

    def _active_action_request_entry(self, chat: WorkflowChat | None = None) -> HistoryActionRequestEntry | None:
        target_chat = chat or self.active_chat
        for entry in reversed(target_chat.history_entries):
            if isinstance(entry, HistoryActionRequestEntry):
                return entry
        return None

    def decide_active_notebook_card(self, decision: str) -> AppActionResult:
        """Accept/reject the active proposal or action-confirmation card."""
        normalized = "apply" if decision in {"apply", "accept", "confirm"} else "reject"
        chat = self.active_chat
        if chat.pending_patch_id is not None:
            self.post_message(self.PatchDecisionRequested(self, chat.pending_patch_id, normalized))
            verb = "Accepted" if normalized == "apply" else "Rejected"
            return AppActionResult("completed", f"{verb} notebook proposal.")
        request_entry = self._active_action_request_entry(chat)
        if request_entry is None:
            verb = "accept" if normalized == "apply" else "reject"
            return AppActionResult("refused", f"No active notebook card to {verb}.")
        if normalized == "apply":
            self.run_worker(
                self._confirm_action_request_from_shortcut(chat.slug, request_entry),
                name=f"workflow-action-confirm-{chat.slug}",
                group=f"chat:{chat.slug}",
                thread=False,
                exit_on_error=False,
            )
            return AppActionResult("completed", f"Confirming {request_entry.label}.")
        result = AppActionResult("refused", f"Cancelled {request_entry.label}.")
        self._replace_action_request_with_result(request_entry, result, chat=chat)
        self.set_status(result.message)
        self._render_chat(chat.slug)
        self._sync_status()
        return AppActionResult("completed", result.message)

    async def _confirm_action_request_from_shortcut(self, chat_slug: str, request_entry: HistoryActionRequestEntry) -> None:
        target_chat = WORKFLOW_CHATS.get(chat_slug)
        if target_chat is None:
            return
        if self._pending_action_request_index(request_entry, chat=target_chat) is None:
            self.set_status(f"{request_entry.label} is no longer active.")
            self._sync_status()
            return
        result = await self._dispatch_confirmed_action_request(request_entry)
        self._replace_action_request_with_result(request_entry, result, chat=target_chat)
        self.set_status(result.message)
        self._render_chat(chat_slug)
        self._sync_status()

    @staticmethod
    def _action_request_entry_from_result(
        result: AppActionResult,
        *,
        fallback_action_id: str,
        fallback_label: str,
        fallback_payload: dict[str, object],
        conversation_turn_id: str | None,
    ) -> HistoryActionRequestEntry:
        card = result.card if isinstance(result.card, dict) else {}
        action_id = str(card.get("action_id") or fallback_action_id)
        payload = dict(fallback_payload)
        if isinstance(card.get("payload"), dict):
            payload.update(dict(card["payload"]))
        raw_options = card.get("options")
        options: tuple[dict[str, object], ...] = ()
        if isinstance(raw_options, list):
            options = tuple(option for option in raw_options if isinstance(option, dict))
        raw_input = card.get("input")
        input_name = None
        input_placeholder = ""
        if isinstance(raw_input, dict):
            raw_name = raw_input.get("name")
            input_name = str(raw_name) if raw_name else None
            input_placeholder = str(raw_input.get("placeholder") or "")
        raw_turn_id = card.get("conversation_turn_id") or conversation_turn_id
        return HistoryActionRequestEntry(
            action_id=action_id,
            label=str(card.get("label") or fallback_label),
            message=result.message,
            payload=payload,
            conversation_turn_id=str(raw_turn_id) if raw_turn_id else None,
            options=options,
            input_name=input_name,
            input_placeholder=input_placeholder,
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == WORKFLOW_COMPOSER_INPUT_ID:
            self.send_active_message()

    def on_key(self, event: events.Key) -> None:
        key_aliases = {event.key, *(getattr(event, "aliases", ()) or ())}
        modifiers = {str(modifier).casefold() for modifier in (getattr(event, "modifiers", ()) or ())}
        if "shift+enter" in key_aliases or (event.key == "enter" and "shift" in modifiers):
            result = self.decide_active_notebook_card("apply")
            self.set_status(result.message)
            event.stop()
            event.prevent_default()
            return
        if "escape" in key_aliases:
            result = self.decide_active_notebook_card("reject")
            self.set_status(result.message)
            event.stop()
            event.prevent_default()
            return
        if event.key not in {"up", "down"}:
            return
        composer = self.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
        if self.app.focused is not composer or composer.disabled:
            return
        direction = -1 if event.key == "up" else 1
        if self._recall_command_history(direction):
            event.stop()
            event.prevent_default()

    def _record_command_history(self, chat: WorkflowChat, prompt: str) -> None:
        command = prompt.strip()
        if not command:
            return
        if not chat.command_history or chat.command_history[-1] != command:
            chat.command_history.append(command)
            if len(chat.command_history) > COMMAND_HISTORY_LIMIT:
                del chat.command_history[: len(chat.command_history) - COMMAND_HISTORY_LIMIT]
        chat.command_history_index = None
        chat.command_history_draft = ""

    def _recall_command_history(self, direction: int) -> bool:
        chat = self.active_chat
        if not chat.command_history:
            return False
        composer = self.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
        if chat.command_history_index is None:
            if direction > 0:
                return False
            chat.command_history_draft = composer.value
            chat.command_history_index = len(chat.command_history) - 1
        else:
            next_index = chat.command_history_index + direction
            if next_index < 0:
                next_index = 0
            if next_index >= len(chat.command_history):
                chat.command_history_index = None
                self._set_composer_history_value(chat.command_history_draft)
                chat.command_history_draft = ""
                return True
            chat.command_history_index = next_index
        self._set_composer_history_value(chat.command_history[chat.command_history_index])
        return True

    def _set_composer_history_value(self, value: str) -> None:
        composer = self.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
        composer.value = value
        composer.cursor_position = len(value)

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

    def on_search_results_card_add_to_basket_requested(self, message: SearchResultsCard.AddToBasketRequested) -> None:
        match = message.result.match_at(message.match_index)
        self.post_message(
            self.SearchResultAddToBasketRequested(
                self,
                message.result.document_slug,
                message.result.title,
                message.result.document_type,
                match.snippet if match is not None else message.result.snippet,
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
            self._begin_reasoning_entry(chat)
        else:
            entry = chat.history_entries[chat.active_reasoning_index]
            if isinstance(entry, HistoryReasoningEntry):
                entry.content += text
                return
        if chat.active_reasoning_index is not None:
            entry = chat.history_entries[chat.active_reasoning_index]
            if isinstance(entry, HistoryReasoningEntry):
                entry.content += text

    def _complete_chat_stream(self, slug: str, request_id: int, replay_content: object | None = None) -> None:
        chat = WORKFLOW_CHATS.get(slug)
        if chat is None or chat.active_request_id != request_id:
            return
        request_mode = chat.active_request_mode or "chat"
        instruction_text = chat.active_instruction_text
        rewrite_target = chat.active_rewrite_target
        rewrite_block_insert = rewrite_target.block_insert if rewrite_target is not None else False
        draft_target_range = chat.active_draft_target_range
        draft_block_insert = chat.active_draft_block_insert
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
        chat.active_history_visible = True
        chat.active_rewrite_target = None
        chat.active_draft_target_range = None
        chat.active_draft_block_insert = False
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
                    rewrite_block_insert,
                )
            )
        else:
            if request_mode == "draft":
                self._remove_last_status_entry(chat, self._proposal_generation_status("draft"))
                self.post_message(
                    self.DraftRequested(
                        self,
                        slug,
                        instruction_text,
                        generated_text,
                        draft_target_range,
                        draft_block_insert,
                    )
                )
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
        chat.active_history_visible = True
        chat.active_rewrite_target = None
        chat.active_draft_target_range = None
        chat.active_draft_block_insert = False
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
            widgets = [self._widget_for_history_entry(entry) for entry in chat.history_entries if self._history_entry_is_visible(entry)]
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
        if isinstance(entry, HistoryActionRequestEntry):
            return ActionRequestCard(entry)
        if isinstance(entry, HistoryActionResultEntry):
            return ActionResultCard(entry)
        return Static(str(entry), classes="workflow-history-block")

    @staticmethod
    def _history_entry_is_visible(entry: object) -> bool:
        return bool(getattr(entry, "visible", True))

    def _rendered_history_text(self, chat: WorkflowChat) -> str:
        blocks: list[str] = []
        for entry in chat.history_entries:
            if isinstance(entry, HistoryTextEntry):
                blocks.append(f"**{entry.role.capitalize()}:**\n\n{entry.content}")
            elif isinstance(entry, HistoryReasoningEntry):
                content = entry.content.strip() or "(No provider-exposed thinking text was captured.)"
                blocks.append(f"### Reasoning Trace\n\n{content}")
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
            elif isinstance(entry, HistoryActionRequestEntry):
                blocks.append(
                    "\n".join(
                        [
                            "### App Action Request",
                            f"- Action: {entry.action_id}",
                            f"- Label: {entry.label}",
                            f"- Status: pending confirmation",
                            entry.message,
                        ]
                    )
                )
            elif isinstance(entry, HistoryActionResultEntry):
                blocks.append(
                    "\n".join(
                        [
                            "### App Action Result",
                            f"- Action: {entry.action_id}",
                            f"- Label: {entry.label}",
                            f"- Status: {entry.status}",
                            entry.message,
                        ]
                    )
                )
        return "\n\n".join(blocks).strip()

    def _show_compaction_prompt(self, chat: WorkflowChat, used_tokens: int, reason: str) -> None:
        self._clear_compaction_prompt(chat)
        chat.history_entries.append(
            HistoryCompactionPromptEntry(
                used_tokens=used_tokens,
                token_capacity=self._context_window_tokens(),
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
        return self._format_context_usage(used_tokens, self._context_window_tokens())

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

    def _fixed_context_is_too_large(self, fixed_tokens: int) -> bool:
        token_capacity = self._context_window_tokens()
        if token_capacity <= 0:
            return False
        return fixed_tokens >= int(token_capacity * CONTEXT_HARD_LIMIT_RATIO)

    def _fixed_context_too_large_message(self, fixed_tokens: int) -> str:
        token_capacity = self._context_window_tokens()
        return (
            "Request not sent: current document and basket context already exceed the model window.\n\n"
            f"Fixed context: ~{fixed_tokens:,} / {token_capacity:,} tokens before chat history.\n\n"
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
        if shell_context.document_type == "transcript" and shell_context.confidentiality_mode != "local-confidential":
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
        section_context = self._document_sections_context(document_content)
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
            "Notebook action inference:\n"
            "- If the user asks to write, draft, compose, generate, or add prose without naming a target, infer the active document as the target and use draft_into_document.\n"
            "- If the user names an existing section such as abstract, introduction, findings, or conclusion, infer that section as the draft insertion target and draft only the body text for that section.\n"
            "- If selected text is active and the user asks to make it shorter/clearer/stronger, revise it, rewrite it, tighten it, or otherwise edit it without naming a target, infer the active selection as the target and use rewrite_selection.\n\n"
            "Available document sections:\n"
            f"{section_context}\n\n"
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

    @classmethod
    def _document_sections_context(cls, document_content: str) -> str:
        headings = cls._document_headings(document_content)
        if not headings:
            return "(none detected)"
        return "\n".join(f"- {heading}" for heading in headings)

    def _format_context_usage(self, used_tokens: int, token_capacity: int) -> str:
        if token_capacity <= 0:
            return f"context used (~{used_tokens:,} tokens / unknown limit)"
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

    def _begin_reasoning_entry(self, chat: WorkflowChat) -> None:
        if chat.active_reasoning_index is not None:
            return
        insert_at = chat.active_history_index if chat.active_history_index is not None else len(chat.history_entries)
        chat.history_entries.insert(insert_at, HistoryReasoningEntry("", streaming=True, visible=chat.active_history_visible))
        chat.active_reasoning_index = insert_at
        if chat.active_history_index is not None and chat.active_history_index >= insert_at:
            chat.active_history_index += 1

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

    def _hide_active_turn_display(self, chat: WorkflowChat) -> None:
        """Keep provider scaffolding transcript-only once a tool call starts."""
        if chat.active_history_index is not None and chat.active_history_index < len(chat.history_entries):
            entry = chat.history_entries[chat.active_history_index]
            if isinstance(entry, HistoryTextEntry):
                entry.visible = False
        if chat.active_reasoning_index is not None and chat.active_reasoning_index < len(chat.history_entries):
            entry = chat.history_entries[chat.active_reasoning_index]
            if isinstance(entry, HistoryReasoningEntry):
                entry.visible = False
        chat.active_history_visible = False

    def _remove_last_status_entry(self, chat: WorkflowChat, content: str) -> None:
        for index in range(len(chat.history_entries) - 1, -1, -1):
            entry = chat.history_entries[index]
            if isinstance(entry, HistoryStatusEntry) and entry.content == content:
                chat.history_entries.pop(index)
                return

    def _clear_patch_review_entries(self, chat: WorkflowChat) -> None:
        chat.history_entries = [entry for entry in chat.history_entries if not isinstance(entry, HistoryRewriteEntry)]
        chat.pending_patch_id = None

    async def _stream_reply(self, slug: str, request_id: int, request_mode: str, *, allow_tools: bool = True) -> None:
        chat = WORKFLOW_CHATS[slug]
        shell_context = self._shell_context(chat.active_rewrite_target if request_mode == "rewrite" else None)
        tools = provider_tool_specs() if allow_tools and request_mode == "chat" else None
        completed = False
        try:
            async for event in self._stream_backend_reply(
                slug,
                chat.messages,
                shell_context,
                request_mode=request_mode,
                tools=tools,
            ):
                if event.kind == "assistant_delta":
                    self.call_later(self._apply_chat_delta, slug, request_id, event.text)
                elif event.kind == "reasoning_delta":
                    self.call_later(self._apply_reasoning_delta, slug, request_id, event.text)
                elif event.kind == "assistant_done":
                    completed = True
                    self.call_later(self._complete_chat_stream, slug, request_id, event.replay_content)
                    return
                elif event.kind == "tool_call" and event.tool_call is not None:
                    if allow_tools:
                        self.call_later(self._start_tool_call_worker, slug, request_id, event.tool_call)
                    else:
                        self.call_later(self._suppress_recursive_tool_call, slug, request_id)
                    return
                elif event.kind == "error":
                    self.call_later(self._fail_chat_stream, slug, request_id, event.error)
                    return
            if not completed:
                self.call_later(self._complete_chat_stream, slug, request_id)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self.call_later(self._fail_chat_stream, slug, request_id, f"Mistral request failed: {exc}")

    async def _stream_backend_reply(
        self,
        slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        *,
        request_mode: str,
        tools: tuple[object, ...] | None,
    ):
        try:
            stream = self._backend.stream_reply(slug, messages, shell_context, request_mode=request_mode, tools=tools)
        except TypeError:
            stream = self._backend.stream_reply(slug, messages, shell_context, request_mode=request_mode)
        async for event in stream:
            yield event

    def _start_tool_call_worker(self, slug: str, request_id: int, tool_call: ToolCallRequest) -> None:
        chat = WORKFLOW_CHATS.get(slug)
        if chat is None or chat.active_request_id != request_id:
            return
        self._hide_active_turn_display(chat)
        self._render_chat(slug)
        self.run_worker(
            self._handle_tool_call(slug, request_id, tool_call),
            name=f"workflow-tool-{slug}",
            group=f"chat:{slug}",
            thread=False,
            exit_on_error=False,
            exclusive=True,
        )

    def _suppress_recursive_tool_call(self, slug: str, request_id: int) -> None:
        chat = WORKFLOW_CHATS.get(slug)
        if chat is None or chat.active_request_id != request_id:
            return
        chat.generating = False
        chat.active_request_id = None
        chat.active_request_mode = None
        chat.active_instruction_text = ""
        chat.active_rewrite_target = None
        chat.active_draft_target_range = None
        chat.active_draft_block_insert = False
        if chat.messages and chat.messages[-1].role == "assistant" and not chat.messages[-1].content:
            chat.messages.pop()
        self._remove_active_history_entry(chat)
        self._remove_active_reasoning_entry(chat)
        chat.active_history_visible = True
        self._workers.pop(slug, None)
        self._render_chat(slug)
        self._sync_status()

    async def _handle_tool_call(self, slug: str, request_id: int, tool_call: ToolCallRequest) -> None:
        chat = WORKFLOW_CHATS.get(slug)
        if chat is None or chat.active_request_id != request_id:
            return
        self._finish_tool_call_turn(chat)
        tool_call = self._coerce_tool_call_from_prompt(chat, tool_call)
        try:
            spec = get_app_action_spec(tool_call.action_id)
        except KeyError:
            result = AppActionResult("refused", f"Unknown app action requested by model: {tool_call.action_id}")
            self._append_action_result(chat, tool_call.action_id, tool_call.action_id, result)
            self._render_chat(slug)
            self._sync_status()
            return
        if spec.safety == "system_only":
            result = AppActionResult("refused", f"{spec.label} must be invoked manually from Exegesis.")
            self._append_action_result(chat, spec.id, spec.label, result)
            self.set_status(result.message)
            self._render_chat(slug)
            self._sync_status()
            return

        if spec.safety == "confirm_required":
            result = await self._dispatch_tool_action(tool_call, conversation_turn_id=f"{slug}:{request_id}")
            if result.status == "pending_confirmation":
                chat.history_entries.append(
                    self._action_request_entry_from_result(
                        result,
                        fallback_action_id=spec.id,
                        fallback_label=spec.label,
                        fallback_payload=dict(tool_call.arguments),
                        conversation_turn_id=f"{slug}:{request_id}",
                    )
                )
            else:
                self._append_action_result(chat, spec.id, spec.label, result)
            self.set_status(result.message)
            self._render_chat(slug)
            self._sync_status()
            return
        if spec.safety == "proposal_auto":
            result = await self._dispatch_tool_action(tool_call, conversation_turn_id=f"{slug}:{request_id}")
            self.set_status(result.message)
            if result.status != "completed":
                self._append_action_result(chat, spec.id, spec.label, result)
                self._render_chat(slug)
                self._sync_status()
                return
            self._render_chat(slug)
            self._sync_status()
            return
        result = await self._dispatch_tool_action(tool_call, conversation_turn_id=f"{slug}:{request_id}")
        self._append_action_result(chat, spec.id, spec.label, result)
        if spec.id == "search_documents" and result.status == "completed":
            query = str(tool_call.arguments.get("query") or "")
            chat.history_entries.append(HistorySearchEntry(query=query, results=self._search_documents(query)))
        self._append_tool_result_messages(chat, tool_call, result)
        if result.status == "completed":
            self._start_follow_up_after_tool(slug)
        else:
            self.set_status(result.message)
            self._render_chat(slug)
            self._sync_status()

    def _coerce_tool_call_from_prompt(self, chat: WorkflowChat, tool_call: ToolCallRequest) -> ToolCallRequest:
        tool_call = self._coerce_trash_tool_call_from_prompt(chat, tool_call)
        return self._coerce_basket_tool_call_from_prompt(chat, tool_call)

    def _coerce_trash_tool_call_from_prompt(self, chat: WorkflowChat, tool_call: ToolCallRequest) -> ToolCallRequest:
        latest_user = self._latest_user_message_content(chat)
        if tool_call.action_id == "permanently_delete_trash_item" and self._user_prompt_requests_restore(latest_user):
            return replace(tool_call, tool_name="restore_trash_item")
        if tool_call.action_id == "restore_trash_item" and self._user_prompt_requests_permanent_delete(latest_user):
            return replace(tool_call, tool_name="permanently_delete_trash_item")
        if tool_call.action_id in {"restore_trash_item", "permanently_delete_trash_item"} and self._user_prompt_requests_delete_to_trash(latest_user):
            return replace(tool_call, tool_name="move_document_to_trash")
        return tool_call

    def _coerce_basket_tool_call_from_prompt(self, chat: WorkflowChat, tool_call: ToolCallRequest) -> ToolCallRequest:
        if tool_call.action_id != "add_document_to_basket":
            return tool_call
        if self._tool_payload_requests_excerpt(tool_call.arguments):
            return replace(tool_call, tool_name="add_excerpt_to_basket")
        latest_user = self._latest_user_message_content(chat)
        if self._user_prompt_requests_excerpt(latest_user):
            return replace(tool_call, tool_name="add_excerpt_to_basket")
        return tool_call

    @staticmethod
    def _latest_user_message_content(chat: WorkflowChat) -> str:
        return next((message.content for message in reversed(chat.messages) if message.role == "user"), "")

    @staticmethod
    def _tool_payload_requests_excerpt(arguments: dict[str, object]) -> bool:
        if any(
            arguments.get(key) not in (None, "")
            for key in (
                "excerpt",
                "selected_text",
                "selection",
                "text",
                "snippet",
                "quote",
                "passage",
                "source_excerpt",
                "start",
                "end",
            )
        ):
            return True
        raw_range = arguments.get("match_range") or arguments.get("range")
        return isinstance(raw_range, (list, tuple)) and len(raw_range) >= 2

    @staticmethod
    def _user_prompt_requests_excerpt(prompt: str) -> bool:
        normalized = prompt.casefold()
        return any(term in normalized for term in EXCERPT_INTENT_TERMS)

    @staticmethod
    def _user_prompt_requests_safe_transcript_file_action(prompt: str) -> bool:
        normalized = prompt.casefold()
        return any(term in normalized for term in SAFE_TRANSCRIPT_FILE_ACTION_TERMS)

    @staticmethod
    def _user_prompt_requests_restore(prompt: str) -> bool:
        normalized = prompt.casefold()
        return any(term in normalized for term in RESTORE_TRASH_INTENT_TERMS) and not any(
            term in normalized for term in PERMANENT_DELETE_INTENT_TERMS
        )

    @staticmethod
    def _user_prompt_requests_permanent_delete(prompt: str) -> bool:
        normalized = prompt.casefold()
        return any(term in normalized for term in PERMANENT_DELETE_INTENT_TERMS)

    @staticmethod
    def _user_prompt_requests_delete_to_trash(prompt: str) -> bool:
        normalized = prompt.casefold()
        return (
            any(term in normalized for term in DELETE_TO_TRASH_INTENT_TERMS)
            and not any(term in normalized for term in RESTORE_TRASH_INTENT_TERMS)
            and not any(term in normalized for term in PERMANENT_DELETE_INTENT_TERMS)
        )

    def _finish_tool_call_turn(self, chat: WorkflowChat) -> None:
        chat.generating = False
        chat.active_request_id = None
        chat.active_request_mode = None
        chat.active_instruction_text = ""
        chat.active_rewrite_target = None
        chat.active_draft_target_range = None
        chat.active_draft_block_insert = False
        if chat.messages and chat.messages[-1].role == "assistant":
            chat.messages.pop()
        self._remove_active_history_entry(chat)
        if chat.active_reasoning_index is not None and chat.active_reasoning_index < len(chat.history_entries):
            entry = chat.history_entries[chat.active_reasoning_index]
            if isinstance(entry, HistoryReasoningEntry):
                entry.visible = False
        self._finalize_active_reasoning_entry(chat)
        chat.active_reasoning_index = None
        chat.active_history_visible = True
        self._workers.pop(chat.slug, None)
        self._render_chat(chat.slug)

    async def _dispatch_tool_action(
        self,
        tool_call: ToolCallRequest,
        *,
        conversation_turn_id: str,
        confirmed: bool = False,
    ) -> AppActionResult:
        dispatcher = getattr(self.app, "dispatch_app_action", None)
        if not callable(dispatcher):
            return AppActionResult("failed", "The shell action dispatcher is unavailable.")
        return await dispatcher(
            tool_call.action_id,
            dict(tool_call.arguments),
            source="model_tool",
            conversation_turn_id=conversation_turn_id,
            confirmed=confirmed,
        )

    def _append_action_result(
        self,
        chat: WorkflowChat,
        action_id: str,
        label: str,
        result: AppActionResult,
    ) -> None:
        chat.history_entries.append(
            HistoryActionResultEntry(
                action_id=action_id,
                label=label,
                status=result.status,
                message=result.message,
                data=dict(result.data),
            )
        )

    def _append_tool_result_messages(
        self,
        chat: WorkflowChat,
        tool_call: ToolCallRequest,
        result: AppActionResult,
    ) -> None:
        call_id = tool_call.raw_call_id or f"exegesis-{chat.slug}-{len(chat.messages) + 1}"
        arguments = {key: value for key, value in tool_call.arguments.items() if not str(key).casefold().endswith("key")}
        chat.messages.append(
            ChatMessage(
                "assistant",
                "",
                provider_content={
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": call_id,
                            "type": "function",
                            "function": {
                                "name": tool_call.tool_name,
                                "arguments": json.dumps(arguments, sort_keys=True),
                            },
                        }
                    ],
                },
            )
        )
        chat.messages.append(
            ChatMessage(
                "tool",
                result.provider_safe_text,
                provider_content={
                    "role": "tool",
                    "name": tool_call.tool_name,
                    "content": result.provider_safe_text,
                    "tool_call_id": call_id,
                },
            )
        )

    def _start_follow_up_after_tool(self, slug: str) -> None:
        chat = WORKFLOW_CHATS[slug]
        if chat.generating:
            return
        chat.messages.append(ChatMessage("assistant", "", streaming=True))
        chat.history_entries.append(HistoryTextEntry("assistant", "", streaming=True, visible=False))
        chat.active_history_index = len(chat.history_entries) - 1
        self._request_counter += 1
        request_id = self._request_counter
        chat.generating = True
        chat.active_request_id = request_id
        chat.active_request_mode = "chat"
        chat.active_instruction_text = ""
        chat.active_reasoning_index = None
        chat.active_history_visible = False
        chat.active_rewrite_target = None
        chat.active_draft_target_range = None
        chat.active_draft_block_insert = False
        self._render_chat(slug)
        self._sync_status()
        self._workers[slug] = self.run_worker(
            self._stream_reply(slug, request_id, "chat", allow_tools=False),
            name=f"workflow-chat-{slug}",
            group=f"chat:{slug}",
            thread=False,
            exit_on_error=False,
            exclusive=True,
        )

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
            selected_text = str(raw.get("selected_text", ""))
            selection_start = self._coerce_optional_int(raw.get("selection_start"))
            selection_end = self._coerce_optional_int(raw.get("selection_end"))
            return ShellChatContext(
                project_name=str(raw.get("project_name", "Current Project")),
                document_title=str(raw.get("document_title", "current_draft.md")),
                document_type=str(raw.get("document_type", "draft")),
                document_content=str(raw.get("document_content", "")),
                confidentiality_mode=str(raw.get("confidentiality_mode", "non-confidential")),
                basket_context=str(raw.get("basket_context", "")),
                selected_text=rewrite_target.original_text if rewrite_target is not None else selected_text,
                selection_start=rewrite_target.target_range[0] if rewrite_target is not None else selection_start,
                selection_end=rewrite_target.target_range[1] if rewrite_target is not None else selection_end,
            )
        return ShellChatContext(
            project_name="Current Project",
            document_title="current_draft.md",
            document_type="draft",
            document_content="",
            confidentiality_mode="non-confidential",
            basket_context="",
            selected_text=rewrite_target.original_text if rewrite_target is not None else "",
            selection_start=rewrite_target.target_range[0] if rewrite_target is not None else None,
            selection_end=rewrite_target.target_range[1] if rewrite_target is not None else None,
        )

    @staticmethod
    def _coerce_optional_int(value: object) -> int | None:
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

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
    "ActionRequestCard",
    "ActionResultCard",
    "HistoryActionRequestEntry",
    "HistoryActionResultEntry",
    "HistoryCompactionEntry",
    "HistoryCompactionPromptEntry",
    "HistoryReasoningEntry",
    "HistorySearchEntry",
    "WorkflowChat",
    "WorkflowPane",
    "clipped_rewrite_card_text",
]
