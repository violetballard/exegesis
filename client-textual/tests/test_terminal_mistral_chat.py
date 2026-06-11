from __future__ import annotations

import asyncio
from dataclasses import replace
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from rich.style import Style
from textual import events
from textual.app import App, ComposeResult
from textual.document._document import Selection
from textual.widgets import Button, Header, Input, Markdown, OptionList, RadioButton, Select, Static, TabbedContent, TextArea

from exegesis_textual.actions.registry import AppActionResult, ToolCallRequest, provider_tool_specs
from exegesis_textual.cards.patch_card import PatchReviewCardData
from exegesis_textual.commands.palette import ExegesisCommandProvider, default_palette_commands
from exegesis_textual.layout.modals import (
    MODEL_SETTINGS_API_KEY_ID,
    MODEL_SETTINGS_API_KEY_GROUP_ID,
    MODEL_SETTINGS_CLEAR_ID,
    MODEL_SETTINGS_CONTEXT_ID,
    MODEL_SETTINGS_LOCAL_FIELDS_ID,
    MODEL_SETTINGS_LOCAL_CONTEXT_INPUT_ID,
    MODEL_SETTINGS_LOCAL_CONTEXT_SLIDER_ID,
    MODEL_SETTINGS_LOCAL_ENDPOINT_ID,
    MODEL_SETTINGS_LOCAL_MODEL_ID,
    MODEL_SETTINGS_MODEL_ID,
    MODEL_SETTINGS_REASONING_ID,
    MODEL_SETTINGS_SAVE_ID,
    MODEL_SETTINGS_STANDARD_FIELDS_ID,
    MODEL_SETTINGS_STATUS_ID,
    MODEL_SETTINGS_TEST_ID,
)
from exegesis_textual.layout.shell import (
    DEFAULT_IMPORT_CATEGORY,
    DUPLICATE_REPLACE_ALL_ID,
    DUPLICATE_RENAME_INPUT_ID,
    DUPLICATE_CANCEL_IMPORT_ID,
    DUPLICATE_CANCEL_ID,
    DUPLICATE_SKIP_ALL_IMPORT_ID,
    DeleteFolderConfirmModal,
    DeleteProjectConfirmModal,
    DuplicateDocumentModal,
    DuplicateProjectModal,
    FOOTER_CONFIDENTIALITY_ID,
    FOOTER_PALETTE_ID,
    FOOTER_QUIT_ID,
    FOOTER_RESTART_ID,
    IMPORT_BROWSER_OPTIONS_ID,
    ImportMarkdownModal,
    ImportProgressModal,
    NON_CONFIDENTIAL_MODE_LABEL,
    NewProjectFolderModal,
    NewProjectModal,
    OpenProjectModal,
    PermanentDeleteTrashConfirmModal,
    PROJECT_RENAME_ACTIVE_INPUT_ID,
    PROJECT_RENAME_INPUT_ID,
    PROJECT_UPDATE_CANCEL_ID,
    PROJECT_UPDATE_CONFIRM_ID,
    PROJECT_UPDATE_SELECTED_FOLDER_ID,
    PROJECT_UPDATE_TITLE_INPUT_ID,
    PROJECTS_DIRECTORY_CREATE_FOLDER_ID,
    PROJECTS_DIRECTORY_NEW_FOLDER_INPUT_ID,
    PROJECTS_DIRECTORY_PATH_ID,
    PROJECT_PICKER_OPTIONS_ID,
    PROJECT_DUPLICATE_RENAME_INPUT_ID,
    ProjectRecord,
    RenameActiveProjectModal,
    RenameProjectEntryModal,
    SelectProjectsDirectoryModal,
    TRASH_CANCEL_ID,
    TRASH_PERMANENT_DELETE_ID,
    TRASH_RESTORE_ID,
    TrashDocumentModal,
    UpdateFolderPickerTree,
    UpdateProjectItemModal,
    ModelSettingsModal,
    COMMAND_BAR_FILE_ID,
    COMMAND_BAR_NOTEBOOK_ID,
    TOP_MOVE_TO_TRASH_ID,
    TOP_NEW_FOLDER_ID,
    TOP_PERMANENT_DELETE_TRASH_ID,
    TOP_RESTORE_TRASH_ID,
    TOP_SAVE_DOCUMENT_ID,
    TOP_SAVE_SHORT_SUMMARY_ID,
    TOP_TERMINAL_ACCEPT_ID,
    TOP_TERMINAL_DRAFT_ID,
    TOP_TERMINAL_NEW_CHAT_ID,
    TOP_TERMINAL_REJECT_ID,
    TOP_TERMINAL_SAVE_ID,
    TOP_TERMINAL_SEARCH_ID,
    TOP_UPDATE_ITEM_ID,
    QualShellApp,
    SUMMARY_PROGRESS_CANCEL_ID,
    SUMMARY_PROGRESS_MODAL_ID,
    reset_default_demo_project,
)
from exegesis_textual.panes.document_pane import (
    CURRENT_DRAFT_SLUG,
    DOCUMENT_FIXTURES,
    DOCUMENT_SAVE_BUTTON_ID,
    DOCUMENT_TABBED_CONTENT_ID,
    DocumentPane,
    PendingRewritePreview,
    clean_generated_draft_text,
    generated_text_insert_location,
    insert_generated_text_at_range,
    render_review_document_rich,
    render_review_document_text,
)
from exegesis_textual.panes.basket_pane import (
    BASKET_DOCUMENTS_LIST_ID,
    BasketEntry,
    BasketPane,
    basket_entry_prompt,
)
from exegesis_textual.panes.inspector_pane import (
    INSPECTOR_EXCERPT_TEXT_ID,
    INSPECTOR_MARKDOWN_ID,
    INSPECTOR_SAVE_SHORT_SUMMARY_ID,
    INSPECTOR_SUMMARY_ACTIONS_ID,
    InspectorPane,
    render_inspector_markdown,
)
from exegesis_textual.panes.project_pane import (
    PROJECT_BROWSER_LABEL_WRAP_WIDTH,
    PROJECT_DELETE_ID,
    PROJECT_TRASH_DELETE_ID,
    PROJECT_TRASH_RESTORE_ID,
    ProjectBrowserTree,
    ProjectPane,
    ProjectTitle,
)
from exegesis_textual.services.credentials import (
    CLAUDE_ACCOUNT,
    CredentialStoreError,
    GOOGLE_ACCOUNT,
    InMemoryCredentialStore,
    KEYRING_SERVICE,
    LOCAL_OPENAI_ACCOUNT,
    MISTRAL_ACCOUNT,
    OPENAI_ACCOUNT,
    UnavailableCredentialStore,
)
from exegesis_textual.services.model_settings import (
    CLAUDE_FABLE_MODEL,
    CLAUDE_HAIKU_MODEL,
    CLAUDE_OPUS_MODEL,
    CLAUDE_PROVIDER,
    CLAUDE_SONNET_MODEL,
    CONTEXT_1M_TOKENS,
    CONTEXT_200K_TOKENS,
    CONTEXT_256K_TOKENS,
    GOOGLE_GEMINI_FLASH_MODEL,
    GOOGLE_PROVIDER,
    LOCAL_OPENAI_PROVIDER,
    ModelSettings,
    MISTRAL_LARGE_MODEL,
    MISTRAL_MEDIUM_MODEL,
    MistralModelSettings,
    OPENAI_GPT_55_MODEL,
    OPENAI_PROVIDER,
    ProviderModelProfile,
    is_loopback_endpoint,
    load_model_settings,
    load_mistral_model_settings,
    normalize_local_openai_base_url,
    reasoning_options_for_model,
    save_model_settings,
    save_mistral_model_settings,
)
from exegesis_textual.services.projects import (
    CONFIDENTIALITY_CONFIDENTIAL,
    LOCAL_DEVELOPER_ENV,
    TEXTUAL_SETTINGS_PATH_ENV,
    textual_settings_path,
)
from exegesis_textual.workflow.mistral_chat import (
    DEFAULT_SYSTEM_PROMPT_PATH,
    DEFAULT_MISTRAL_MODEL,
    ChatEvent,
    ChatMessage,
    MistralChatBackend,
    ShellChatContext,
)
from exegesis_textual.workflow.rewrite_adapter import MockRewriteSessionAdapter
from exegesis_textual.workflow.workflow_pane import (
    EMPTY_CONTEXT_USAGE_TEXT,
    PRIMARY_CHAT_SLUG,
    WORKFLOW_COMPOSER_INPUT_ID,
    WORKFLOW_COMPACT_CHAT_ID,
    WORKFLOW_DRAFT_ID,
    WORKFLOW_REWRITE_SELECTION_ID,
    WORKFLOW_SEARCH_ID,
    WORKFLOW_SEND_ID,
    HistoryCompactionEntry,
    HistoryCompactionPromptEntry,
    HistoryReasoningEntry,
    HistoryRewriteEntry,
    HistorySearchEntry,
    HistoryStatusEntry,
    HistoryTextEntry,
    NON_CONFIDENTIAL_TRANSCRIPT_WARNING,
    SearchResultItem,
    SearchResultMatch,
    SearchResultsCard,
    WORKFLOW_CHATS,
    WorkflowChat,
    WorkflowPane,
    ActionRequestCard,
    ActionResultCard,
    HistoryActionRequestEntry,
    HistoryActionResultEntry,
    clipped_rewrite_card_text,
    _display_document_type,
)
from exegesis_textual.widgets import SystemClipboardInput

DEMO_MEMO_FOLDER = "fieldwork/round_1"
DEMO_MEMO_DOCUMENT_ID = f"memos/{DEMO_MEMO_FOLDER}/data_memo_1.md"


def reset_workflow_chats() -> None:
    WORKFLOW_CHATS.clear()
    WORKFLOW_CHATS.update(
        {
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
    )


class FakeBackend:
    def __init__(self, configured: bool = True) -> None:
        self._configured = configured
        self.last_mode: str | None = None
        self.last_context: ShellChatContext | None = None
        self.cancelled_chats: list[str] = []

    def is_configured(self) -> bool:
        return self._configured

    async def stream_reply(
        self,
        chat_slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str = "chat",
        tools: object | None = None,
    ):
        del chat_slug, messages
        self.last_mode = request_mode
        self.last_context = shell_context
        await asyncio.sleep(0)
        first = "hello " if request_mode == "chat" else "Drafted " if request_mode == "draft" else "Rewritten "
        second = "world" if request_mode == "chat" else "paragraph." if request_mode == "draft" else "section."
        yield ChatEvent(kind="assistant_delta", text=first)
        await asyncio.sleep(0)
        yield ChatEvent(kind="assistant_delta", text=second)
        yield ChatEvent(kind="assistant_done")

    def cancel(self, chat_slug: str) -> None:
        self.cancelled_chats.append(chat_slug)


class ReasoningBackend(FakeBackend):
    async def stream_reply(
        self,
        chat_slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str = "chat",
        tools: object | None = None,
    ):
        del chat_slug, messages, shell_context, request_mode
        await asyncio.sleep(0)
        yield ChatEvent(kind="reasoning_delta", text="reasoning ")
        yield ChatEvent(kind="assistant_delta", text="answer")
        yield ChatEvent(kind="assistant_done", replay_content=[{"type": "thinking", "thinking": "reasoning "}, {"type": "text", "text": "answer"}])


class NoDoneBackend(FakeBackend):
    async def stream_reply(
        self,
        chat_slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str = "chat",
        tools: object | None = None,
    ):
        del chat_slug, messages, shell_context, request_mode, tools
        await asyncio.sleep(0)
        yield ChatEvent(kind="assistant_delta", text="completed without explicit done")


class ToolCallWithPreambleBackend(FakeBackend):
    def __init__(self, tool_call: ToolCallRequest) -> None:
        super().__init__(configured=True)
        self.tool_call = tool_call

    async def stream_reply(
        self,
        chat_slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str = "chat",
        tools: object | None = None,
    ):
        del chat_slug, messages, shell_context, request_mode, tools
        await asyncio.sleep(0)
        yield ChatEvent(kind="assistant_delta", text="I will rewrite the user's request into a more detailed prompt.")
        yield ChatEvent(kind="tool_call", tool_call=self.tool_call)


class DelayedToolCallWithPreambleBackend(FakeBackend):
    def __init__(self, tool_call: ToolCallRequest) -> None:
        super().__init__(configured=True)
        self.tool_call = tool_call
        self.preamble_sent = asyncio.Event()
        self.release_tool_call = asyncio.Event()

    async def stream_reply(
        self,
        chat_slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str = "chat",
        tools: object | None = None,
    ):
        del chat_slug, messages, shell_context, request_mode, tools
        await asyncio.sleep(0)
        yield ChatEvent(kind="assistant_delta", text="I will rewrite the user's request into a more detailed prompt.")
        self.preamble_sent.set()
        await self.release_tool_call.wait()
        yield ChatEvent(kind="tool_call", tool_call=self.tool_call)


class SequencedDraftBackend(FakeBackend):
    def __init__(self, draft_outputs: list[str]) -> None:
        super().__init__(configured=True)
        self.draft_outputs = draft_outputs
        self.prompts: list[str] = []

    async def stream_reply(
        self,
        chat_slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str = "chat",
        tools: object | None = None,
    ):
        del chat_slug
        self.last_mode = request_mode
        self.last_context = shell_context
        latest_user_message = next((message.content for message in reversed(messages) if message.role == "user"), "")
        self.prompts.append(latest_user_message)
        await asyncio.sleep(0)
        if request_mode == "draft":
            text = self.draft_outputs.pop(0)
        else:
            text = "hello world"
        yield ChatEvent(kind="assistant_delta", text=text)
        yield ChatEvent(kind="assistant_done")


class SequencedRewriteBackend(FakeBackend):
    def __init__(self, rewrite_outputs: list[str]) -> None:
        super().__init__(configured=True)
        self.rewrite_outputs = rewrite_outputs
        self.prompts: list[str] = []

    async def stream_reply(
        self,
        chat_slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str = "chat",
        tools: object | None = None,
    ):
        del chat_slug
        self.last_mode = request_mode
        self.last_context = shell_context
        latest_user_message = next((message.content for message in reversed(messages) if message.role == "user"), "")
        self.prompts.append(latest_user_message)
        await asyncio.sleep(0)
        if request_mode == "rewrite":
            text = self.rewrite_outputs.pop(0)
        else:
            text = "hello world"
        yield ChatEvent(kind="assistant_delta", text=text)
        yield ChatEvent(kind="assistant_done")


class ContextLimitBackend(FakeBackend):
    async def stream_reply(
        self,
        chat_slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str = "chat",
        tools: object | None = None,
    ):
        del chat_slug, messages
        self.last_mode = request_mode
        self.last_context = shell_context
        await asyncio.sleep(0)
        yield ChatEvent(kind="error", error="context length exceeded for this model")


class RateLimitBackend(FakeBackend):
    async def stream_reply(
        self,
        chat_slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str = "chat",
        tools: object | None = None,
    ):
        del chat_slug, messages
        self.last_mode = request_mode
        self.last_context = shell_context
        await asyncio.sleep(0)
        yield ChatEvent(
            kind="error",
            error=(
                "Mistral rate limit reached.\n\n"
                "Try again in about 1 minute.\n\n"
                "This request was not completed. Reduce basket context, use excerpts instead of whole files, "
                "or wait before trying again."
            ),
        )


class SlowSummaryBackend(FakeBackend):
    def __init__(self) -> None:
        super().__init__(configured=True)
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def stream_reply(
        self,
        chat_slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str = "chat",
        tools: object | None = None,
    ):
        del chat_slug, messages
        self.last_mode = request_mode
        self.last_context = shell_context
        self.started.set()
        await self.release.wait()
        yield ChatEvent(kind="assistant_delta", text="Slow summary complete.")
        yield ChatEvent(kind="assistant_done")


class ToolCallBackend(FakeBackend):
    def __init__(self, tool_call: ToolCallRequest, follow_up: str = "Tool result acknowledged.") -> None:
        super().__init__(configured=True)
        self.tool_call = tool_call
        self.follow_up = follow_up
        self.calls = 0
        self.seen_tools: list[object] = []

    async def stream_reply(
        self,
        chat_slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str = "chat",
        tools: object | None = None,
    ):
        del chat_slug, shell_context
        self.last_mode = request_mode
        self.seen_tools.append(tools)
        self.calls += 1
        await asyncio.sleep(0)
        if self.calls == 1:
            yield ChatEvent(kind="tool_call", tool_call=self.tool_call)
            return
        latest_tool_text = next((message.content for message in reversed(messages) if message.role == "tool"), "")
        yield ChatEvent(kind="assistant_delta", text=f"{self.follow_up} {latest_tool_text}".strip())
        yield ChatEvent(kind="assistant_done")


class ToolCallWithReasoningFollowUpBackend(ToolCallBackend):
    async def stream_reply(
        self,
        chat_slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str = "chat",
        tools: object | None = None,
    ):
        del chat_slug, shell_context
        self.last_mode = request_mode
        self.seen_tools.append(tools)
        self.calls += 1
        await asyncio.sleep(0)
        if self.calls == 1:
            yield ChatEvent(kind="tool_call", tool_call=self.tool_call)
            return
        latest_tool_text = next((message.content for message in reversed(messages) if message.role == "tool"), "")
        yield ChatEvent(kind="reasoning_delta", text="tool follow-up thinking")
        yield ChatEvent(kind="assistant_delta", text=f"Tool follow-up answer. {latest_tool_text}".strip())
        yield ChatEvent(kind="assistant_done")


class ProjectBrowserTreeTests(unittest.TestCase):
    def test_long_project_entry_titles_render_as_continuation_rows(self) -> None:
        tree = ProjectBrowserTree()
        _ = tree._tree_lines
        node = tree._entry_nodes["project-notebook"]
        line = next(line for line in tree._tree_lines if line.node is node)
        wrapped = tree._wrapped_title_lines(
            "Transcript 1 - Participant 1 - 5.1.26",
            width=tree._available_label_width(line.path),
        )

        self.assertGreater(len(wrapped), 1)
        self.assertTrue(all(len(line) <= PROJECT_BROWSER_LABEL_WRAP_WIDTH for line in wrapped))
        self.assertIn(wrapped[1], [line.plain for line in tree._wrapped_continuations.values()])

    def test_markers_clear_when_multi_selection_collapses_to_one_item(self) -> None:
        tree = ProjectBrowserTree()

        tree.toggle_marked_entry("project-demo-essay")
        tree.toggle_marked_entry("project-lit-review")
        self.assertEqual(
            {info.slug for info in tree.marked_entry_infos(kinds={"entry"})},
            {"project-demo-essay", "project-lit-review"},
        )

        tree.toggle_marked_entry("project-demo-essay")

        self.assertEqual(tree.marked_entry_infos(kinds={"entry"}), ())
        self.assertFalse(str(tree._entry_nodes["project-lit-review"].label).startswith("[*] "))
        self.assertIsNone(tree._normal_click_anchor_slug)

    def test_shift_click_after_collapse_does_not_resurrect_deselected_anchor(self) -> None:
        tree = ProjectBrowserTree()
        _ = tree._tree_lines

        tree._normal_click_anchor_slug = "project-demo-essay"
        tree.toggle_marked_entry("project-demo-essay")
        tree.toggle_marked_entry("project-lit-review")

        demo_node = tree._entry_nodes["project-demo-essay"]
        asyncio.run(
            tree._on_click(
                events.Click(
                    tree,
                    x=0,
                    y=demo_node._line,
                    delta_x=0,
                    delta_y=0,
                    button=1,
                    shift=True,
                    meta=False,
                    ctrl=False,
                    style=Style(meta={"line": demo_node._line}),
                )
            )
        )
        self.assertEqual(tree.marked_entry_infos(kinds={"entry"}), ())
        self.assertIsNone(tree._normal_click_anchor_slug)

        notebook_node = tree._entry_nodes["project-notebook"]
        asyncio.run(
            tree._on_click(
                events.Click(
                    tree,
                    x=0,
                    y=notebook_node._line,
                    delta_x=0,
                    delta_y=0,
                    button=1,
                    shift=True,
                    meta=False,
                    ctrl=False,
                    style=Style(meta={"line": notebook_node._line}),
                )
            )
        )

        self.assertEqual(
            {info.slug for info in tree.marked_entry_infos(kinds={"entry"})},
            {"project-notebook"},
        )
        self.assertFalse(str(tree._entry_nodes["project-demo-essay"].label).startswith("[*] "))
        self.assertFalse(str(tree._entry_nodes["project-lit-review"].label).startswith("[*] "))

    def test_space_toggles_folders_but_marks_file_entries(self) -> None:
        tree = ProjectBrowserTree()
        _ = tree._tree_lines
        folder_node = tree._folder_nodes[("Memos", "fieldwork")]

        tree.cursor_line = folder_node._line
        self.assertTrue(folder_node.is_expanded)
        tree.action_toggle_marked_cursor()

        self.assertFalse(folder_node.is_expanded)
        self.assertEqual(tree.marked_entry_infos(kinds={"entry"}), ())

        _ = tree._tree_lines
        entry_node = tree._entry_nodes["project-root-memo"]
        tree.cursor_line = entry_node._line
        tree.action_toggle_marked_cursor()

        self.assertEqual(
            {info.slug for info in tree.marked_entry_infos(kinds={"entry"})},
            {"project-root-memo"},
        )

    def test_folder_click_toggles_expand_collapse(self) -> None:
        tree = ProjectBrowserTree()
        _ = tree._tree_lines
        folder_node = tree._folder_nodes[("Memos", "fieldwork")]
        self.assertTrue(folder_node.is_expanded)

        asyncio.run(
            tree._on_click(
                events.Click(
                    tree,
                    x=0,
                    y=folder_node._line,
                    delta_x=0,
                    delta_y=0,
                    button=1,
                    shift=False,
                    meta=False,
                    ctrl=False,
                    style=Style(meta={"line": folder_node._line}),
                )
            )
        )

        self.assertFalse(folder_node.is_expanded)
        self.assertEqual(tree.cursor_line, folder_node._line)

    def test_folder_label_click_with_node_metadata_toggles_expand_collapse(self) -> None:
        tree = ProjectBrowserTree()
        _ = tree._tree_lines
        folder_node = tree._folder_nodes[("Memos", "fieldwork")]
        self.assertTrue(folder_node.is_expanded)

        asyncio.run(
            tree._on_click(
                events.Click(
                    tree,
                    x=2,
                    y=0,
                    delta_x=0,
                    delta_y=0,
                    button=1,
                    shift=False,
                    meta=False,
                    ctrl=False,
                    style=Style(meta={"node": folder_node._id}),
                )
            )
        )

        self.assertFalse(folder_node.is_expanded)
        self.assertEqual(tree.cursor_line, folder_node._line)

    def test_nested_entries_wrap_with_available_indented_width(self) -> None:
        tree = ProjectBrowserTree()
        _ = tree._tree_lines

        nested_transcript = tree._entry_nodes["project-notebook"]
        line = next(line for line in tree._tree_lines if line.node is nested_transcript)
        wrapped_lines = tree._wrapped_title_lines(
            nested_transcript.data.title,
            width=tree._available_label_width(line.path),
        )

        self.assertGreater(len(wrapped_lines), 1)
        self.assertEqual(str(nested_transcript.label), wrapped_lines[0])
        self.assertTrue(
            any(text.plain in wrapped_lines[1:] for text in tree._wrapped_continuations.values())
        )

    def test_shift_click_on_wrapped_continuation_marks_entry_once(self) -> None:
        tree = ProjectBrowserTree()
        _ = tree._tree_lines
        selected_node = tree._entry_nodes["project-root-memo"]
        wrapped_node = tree._entry_nodes["project-notebook"]
        tree.cursor_line = selected_node._line
        tree._normal_click_anchor_slug = selected_node.data.slug
        continuation_line = next(
            index
            for index, line in enumerate(tree._tree_lines)
            if line.node is wrapped_node and index in tree._wrapped_continuations
        )

        asyncio.run(
            tree._on_click(
                events.Click(
                    tree,
                    x=4,
                    y=continuation_line,
                    delta_x=0,
                    delta_y=0,
                    button=1,
                    shift=True,
                    meta=False,
                    ctrl=False,
                    style=Style(meta={"line": continuation_line}),
                )
            )
        )

        self.assertEqual(
            {info.slug for info in tree.marked_entry_infos(kinds={"entry"})},
            {"project-root-memo", "project-notebook"},
        )

    def test_shift_click_keeps_normal_click_anchor_when_cursor_has_moved(self) -> None:
        tree = ProjectBrowserTree()
        tree.post_message = Mock()
        _ = tree._tree_lines
        first_node = tree._entry_nodes["project-root-memo"]
        second_node = tree._entry_nodes["project-lit-review"]

        asyncio.run(
            tree._on_click(
                events.Click(
                    tree,
                    x=0,
                    y=first_node._line,
                    delta_x=0,
                    delta_y=0,
                    button=1,
                    shift=False,
                    meta=False,
                    ctrl=False,
                    style=Style(),
                )
            )
        )
        self.assertEqual(tree.selected_entry_info().slug, "project-root-memo")

        asyncio.run(
            tree._on_click(
                events.Click(
                    tree,
                    x=0,
                    y=second_node._line,
                    delta_x=0,
                    delta_y=0,
                    button=1,
                    shift=True,
                    meta=False,
                    ctrl=False,
                    style=Style(),
                )
            )
        )

        self.assertEqual(
            {info.slug for info in tree.marked_entry_infos(kinds={"entry"})},
            {"project-root-memo", "project-lit-review"},
        )

    def test_shift_click_on_highlighted_entry_marks_that_entry(self) -> None:
        tree = ProjectBrowserTree()
        tree.post_message = Mock()
        _ = tree._tree_lines
        node = tree._entry_nodes["project-root-memo"]

        asyncio.run(
            tree._on_click(
                events.Click(
                    tree,
                    x=0,
                    y=node._line,
                    delta_x=0,
                    delta_y=0,
                    button=1,
                    shift=False,
                    meta=False,
                    ctrl=False,
                    style=Style(),
                )
            )
        )
        self.assertEqual(tree.selected_entry_info().slug, "project-root-memo")

        asyncio.run(
            tree._on_click(
                events.Click(
                    tree,
                    x=0,
                    y=node._line,
                    delta_x=0,
                    delta_y=0,
                    button=1,
                    shift=True,
                    meta=False,
                    ctrl=False,
                    style=Style(),
                )
            )
        )

        self.assertEqual(
            {info.slug for info in tree.marked_entry_infos(kinds={"entry"})},
            {"project-root-memo"},
        )

    def test_project_title_double_click_requests_project_rename(self) -> None:
        title = ProjectTitle("Demo Project")
        event = Mock()
        event.chain = 2
        title.focus = Mock()
        title.post_message = Mock()

        title.on_click(event)

        title.focus.assert_called_once_with()
        event.stop.assert_called_once_with()
        title.post_message.assert_called_once()
        message = title.post_message.call_args.args[0]
        self.assertIsInstance(message, ProjectTitle.RenameRequested)
        self.assertIs(message.title, title)


class WorkflowTestApp(App[None]):
    def __init__(self, backend: FakeBackend) -> None:
        reset_workflow_chats()
        super().__init__()
        self._backend = backend
        self.messages: list[object] = []

    def compose(self) -> ComposeResult:
        yield WorkflowPane(backend=self._backend)

    def shell_chat_context(self) -> dict[str, str]:
        return {
            "project_name": "Test Project",
            "document_title": "current_draft.md",
            "document_type": "draft",
            "document_content": "# Current Draft\n\nExisting body.",
            "confidentiality_mode": "online",
            "basket_context": "[1] kind=excerpt\nsource_title=current_draft.md\nsource_type=draft\ncontent:\nSeed context",
        }

    def on_workflow_pane_search_result_selected(self, message: WorkflowPane.SearchResultSelected) -> None:
        self.messages.append(message)

    def on_workflow_pane_search_result_add_to_basket_requested(self, message: WorkflowPane.SearchResultAddToBasketRequested) -> None:
        self.messages.append(message)


class WorkflowActionDispatchTestApp(WorkflowTestApp):
    def __init__(self, backend: FakeBackend) -> None:
        super().__init__(backend)
        self.dispatched_actions: list[tuple[str, dict[str, object], str, bool]] = []

    async def dispatch_app_action(
        self,
        action_id: str,
        payload: dict[str, object] | None = None,
        source: str = "system",
        conversation_turn_id: str | None = None,
        *,
        confirmed: bool = False,
    ):
        del conversation_turn_id
        clean_payload = dict(payload or {})
        self.dispatched_actions.append((action_id, clean_payload, source, confirmed))
        if action_id == "search_documents":
            return AppActionResult(
                "completed",
                "Search found 1 matching document: current_draft.md.",
                data={"query": clean_payload.get("query", ""), "results": self.shell_search_documents(str(clean_payload.get("query", "")))},
            )
        if action_id == "add_document_to_basket" and clean_payload.get("document") == "Transcript":
            return AppActionResult(
                "refused",
                "Full transcripts cannot be added to the basket in a non-confidential project. Add excerpts instead.",
            )
        if action_id == "add_document_to_basket" and not confirmed:
            return AppActionResult("pending_confirmation", "Add document requires confirmation.")
        if action_id == "update_selected_project_item" and not confirmed:
            return AppActionResult(
                "pending_confirmation",
                "memos/data_memo_1.md already exists. Replace it or enter a different name.",
                card={
                    "type": "action_request",
                    "action_id": action_id,
                    "label": "Update item",
                    "payload": clean_payload,
                    "options": [
                        {"label": "Replace", "payload": {"duplicate_action": "replace"}},
                        {"label": "Rename", "payload": {"duplicate_action": "rename"}},
                        {"label": "Cancel", "payload": {"duplicate_action": "cancel"}, "cancel": True},
                    ],
                    "input": {"name": "duplicate_title", "placeholder": "Alternate file name"},
                },
            )
        return AppActionResult("completed", f"{action_id} completed.")

    def shell_search_documents(self, query: str) -> list[dict[str, object]]:
        return [
            {
                "document_slug": CURRENT_DRAFT_SLUG,
                "title": "current_draft.md",
                "document_type": "draft",
                "snippet": f"Match for {query}",
                "token_count": 12,
                "location": "current_draft.md",
                "match_range": (0, len(query)),
                "matches": [{"snippet": f"Match for {query}", "match_range": (0, len(query))}],
            }
        ]


class WorkflowTranscriptActionDispatchTestApp(WorkflowActionDispatchTestApp):
    def shell_chat_context(self) -> dict[str, str]:
        return {
            "project_name": "Test Project",
            "document_title": "Transcript 1",
            "document_type": "transcript",
            "document_content": "Sensitive transcript text should stay withheld.",
            "confidentiality_mode": "online",
            "basket_context": "",
        }


class SlowWorkflowActionDispatchTestApp(WorkflowActionDispatchTestApp):
    def __init__(self, backend: FakeBackend) -> None:
        super().__init__(backend)
        self.dispatch_started = asyncio.Event()
        self.dispatch_release = asyncio.Event()

    async def dispatch_app_action(
        self,
        action_id: str,
        payload: dict[str, object] | None = None,
        source: str = "system",
        conversation_turn_id: str | None = None,
        *,
        confirmed: bool = False,
    ):
        self.dispatch_started.set()
        await self.dispatch_release.wait()
        return await super().dispatch_app_action(
            action_id,
            payload,
            source,
            conversation_turn_id,
            confirmed=confirmed,
        )


class WorkflowTranscriptTestApp(WorkflowTestApp):
    def shell_chat_context(self) -> dict[str, str]:
        return {
            "project_name": "Test Project",
            "document_title": "Transcript 1",
            "document_type": "transcript",
            "document_content": "Sensitive transcript text should stay withheld.",
            "confidentiality_mode": "online",
            "basket_context": "",
        }


class WorkflowHugeFixedContextApp(WorkflowTestApp):
    def shell_chat_context(self) -> dict[str, str]:
        context = super().shell_chat_context()
        context["basket_context"] = "Huge basket context. " * 70_000
        return context


class WorkflowDraftTestApp(App[None]):
    def __init__(self, backend: FakeBackend) -> None:
        reset_workflow_chats()
        super().__init__()
        self._backend = backend

    def compose(self) -> ComposeResult:
        yield DocumentPane()
        yield WorkflowPane(backend=self._backend)

    def shell_chat_context(self) -> dict[str, str]:
        document = self.query_one(DocumentPane).active_document
        return {
            "project_name": "Test Project",
            "document_title": document.title,
            "document_type": document.document_type,
            "document_content": document.content,
            "confidentiality_mode": "online",
            "basket_context": "[1] kind=excerpt\nsource_title=current_draft.md\nsource_type=draft\ncontent:\nSeed context",
        }

    def on_workflow_pane_draft_requested(self, message: WorkflowPane.DraftRequested) -> None:
        document_pane = self.query_one(DocumentPane)
        active = document_pane.active_document
        preview = document_pane.show_pending_generated_text(
            slug=active.slug,
            patch_id="draft-test-proposal",
            generated_text=message.generated_text,
            instruction_text=message.instruction_text,
            source_chat_slug=message.chat_slug,
            target_range=message.target_range,
            block_insert=message.block_insert,
        )
        if preview is not None:
            self.query_one(WorkflowPane).show_patch_review(
                PatchReviewCardData(
                    patch_id=preview.patch_id,
                    document_title=active.title,
                    instruction_text=preview.instruction_text,
                    source_chat_slug=preview.source_chat_slug,
                    original_text=preview.original_text,
                    proposed_text=preview.proposed_text,
                    document_slug=preview.document_slug,
                    target_range=preview.target_range,
                    block_insert=preview.block_insert,
                )
            )


class ShellWorkflowTestApp(QualShellApp):
    def __init__(self, backend: FakeBackend) -> None:
        reset_workflow_chats()
        super().__init__(workflow_backend=backend)
        self._backend = backend
        self._rewrite_adapter = MockRewriteSessionAdapter()

    def shell_search_documents(self, query: str) -> list[dict[str, object]]:
        return [
            {
                "document_slug": CURRENT_DRAFT_SLUG,
                "title": "current_draft.md",
                "document_type": "draft",
                "snippet": f"Match for {query}",
                "token_count": 12,
                "location": "current_draft.md",
            }
        ]

    def shell_rewrite_context(self) -> dict[str, object] | None:
        return {
            "document_slug": CURRENT_DRAFT_SLUG,
            "document_title": "current_draft.md",
            "target_range": (0, 5),
            "original_text": "# Cur",
        }


class ShellConfidentialityModeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self._previous_local_developer = os.environ.get("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER")
        os.environ["EXEGESIS_TEXTUAL_LOCAL_DEVELOPER"] = "1"

    def tearDown(self) -> None:
        if self._previous_local_developer is None:
            os.environ.pop("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER", None)
        else:
            os.environ["EXEGESIS_TEXTUAL_LOCAL_DEVELOPER"] = self._previous_local_developer

    async def test_shell_is_fixed_non_confidential_mode(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            footer = app.query_one(f"#{FOOTER_CONFIDENTIALITY_ID}", Static)
            self.assertEqual(footer.render(), NON_CONFIDENTIAL_MODE_LABEL)
            self.assertNotIsInstance(footer, Button)
            self.assertEqual(app.shell_chat_context()["confidentiality_mode"], "non-confidential")

    async def test_confidential_project_footer_uses_confidential_badge(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            app._current_project_confidentiality = CONFIDENTIALITY_CONFIDENTIAL
            app._sync_footer_bar()

            footer = app.query_one(f"#{FOOTER_CONFIDENTIALITY_ID}", Static)
            self.assertEqual(footer.render(), "Confidential")
            self.assertTrue(footer.has_class("confidential"))
            self.assertFalse(footer.has_class("non-confidential"))
            self.assertNotEqual(str(footer.styles.background), "#ff1744")

    async def test_empty_projects_root_creates_demo_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
            try:
                with patch("exegesis_textual.layout.shell.textual_projects_dir", return_value=Path(tmp)):
                    app = ShellWorkflowTestApp(FakeBackend(configured=True))
                    async with app.run_test() as pilot:
                        await pilot.pause()

                        project_root = Path(tmp) / "demo-project"
                        self.assertEqual(app._current_project_name, "Demo Project")
                        self.assertEqual(app._project_root, project_root)
                        self.assertIn("current-draft", app._document_id_by_slug)
                        self.assertTrue((project_root / "drafts" / "current_draft.md").exists())
                        self.assertTrue((project_root / DEMO_MEMO_DOCUMENT_ID).exists())
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_active_project_rename_moves_folder_and_updates_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    app._handle_new_project_result("Field Project")
                    await pilot.pause()
                    old_root = Path(tmp) / "field-project"
                    self.assertTrue(old_root.exists())

                    app._handle_active_project_rename_result("Renamed Field Project")
                    await pilot.pause()

                    new_root = Path(tmp) / "renamed-field-project"
                    self.assertFalse(old_root.exists())
                    self.assertTrue((new_root / "drafts" / "current_draft.md").exists())
                    self.assertEqual(app._current_project_name, "Renamed Field Project")
                    self.assertEqual(app._project_root, new_root)
                    self.assertIn(
                        '"name": "Renamed Field Project"',
                        (new_root / ".exegesis" / "project.json").read_text(encoding="utf-8"),
                    )
                    self.assertEqual(app.query_one(ProjectPane)._project_name, "Renamed Field Project")
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_full_transcript_cannot_be_added_to_basket(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            await app.query_one(DocumentPane).open_document("project-notebook")
            await pilot.pause()
            app.action_add_file_to_basket()
            await pilot.pause()
            self.assertNotIn("project-notebook", app._serialize_basket_context())

    async def test_notebook_can_restore_trashed_transcript_in_non_confidential_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                tool_call = ToolCallRequest(
                    provider="mistral",
                    tool_name="restore_trash_item",
                    arguments={},
                    raw_call_id="call-restore-transcript",
                )
                app = ShellWorkflowTestApp(ToolCallBackend(tool_call))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    await app._create_project_document("Transcripts")
                    await pilot.pause()
                    transcript_slug = app.query_one(DocumentPane).active_document.slug
                    transcript_id = app._document_id_by_slug[transcript_slug]
                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._entry_nodes[transcript_slug], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()
                    [(trash_slug, _trash_id)] = list(app._trash_id_by_slug.items())
                    tree.move_cursor(tree._entry_nodes[trash_slug], animate=False)
                    await app.query_one(DocumentPane).open_document(trash_slug, focus=False)
                    await pilot.pause()

                    workflow = app.query_one(WorkflowPane)
                    app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input).value = "Restore this transcript from the trash."
                    workflow.send_active_message()
                    for _ in range(6):
                        await pilot.pause()

                    self.assertFalse(any(isinstance(entry, HistoryStatusEntry) and "full transcripts" in entry.content.casefold() for entry in workflow.active_chat.history_entries))
                    request_entries = [entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryActionRequestEntry)]
                    self.assertEqual(len(request_entries), 1)
                    self.assertEqual(request_entries[0].action_id, "restore_trash_item")

                    await workflow.on_action_request_card_confirm_requested(
                        ActionRequestCard.ConfirmRequested(ActionRequestCard(request_entries[0]), request_entries[0])
                    )
                    await pilot.pause()
                    await pilot.pause()

                    self.assertNotIn(trash_slug, app._trash_id_by_slug)
                    self.assertIn(transcript_id, app._document_id_by_slug.values())
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_notebook_can_restore_named_nested_trashed_transcript(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                tool_call = ToolCallRequest(
                    provider="openai",
                    tool_name="restore_trash_item",
                    arguments={"document": "Transcript 1 - Participant 1 - 5.1.26"},
                    raw_call_id="call-restore-named-transcript",
                )
                app = ShellWorkflowTestApp(ToolCallBackend(tool_call))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    transcript_slug = "project-notebook"
                    transcript_id = app._document_id_by_slug[transcript_slug]
                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._entry_nodes[transcript_slug], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()
                    [(trash_slug, _trash_id)] = list(app._trash_id_by_slug.items())
                    self.assertNotIn(transcript_slug, app._document_id_by_slug)

                    tree.move_cursor(tree._entry_nodes[CURRENT_DRAFT_SLUG], animate=False)
                    await app.query_one(DocumentPane).open_document(CURRENT_DRAFT_SLUG, focus=False)
                    await pilot.pause()

                    workflow = app.query_one(WorkflowPane)
                    composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                    composer.value = "Restore Transcript 1 from the trash."
                    workflow.send_active_message()
                    for _ in range(6):
                        await pilot.pause()

                    request_entries = [
                        entry
                        for entry in workflow.active_chat.history_entries
                        if isinstance(entry, HistoryActionRequestEntry)
                    ]
                    self.assertEqual(len(request_entries), 1)
                    self.assertEqual(request_entries[0].action_id, "restore_trash_item")

                    await workflow.on_action_request_card_confirm_requested(
                        ActionRequestCard.ConfirmRequested(ActionRequestCard(request_entries[0]), request_entries[0])
                    )
                    await pilot.pause()
                    await pilot.pause()

                    self.assertNotIn(trash_slug, app._trash_id_by_slug)
                    self.assertIn(transcript_id, app._document_id_by_slug.values())
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_model_can_restore_trash_item_by_same_partial_title_used_to_delete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    created = await app.dispatch_app_action(
                        "create_transcript",
                        {"title": "Alpha Restore Transcript"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()
                    self.assertEqual(created.status, "completed")
                    created_slug = next(
                        slug
                        for slug, fixture in DOCUMENT_FIXTURES.items()
                        if fixture.title == "Alpha Restore Transcript.md"
                    )
                    transcript_id = app._document_id_by_slug[created_slug]
                    moved = await app.dispatch_app_action(
                        "move_document_to_trash",
                        {"document": "Alpha Restore"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()
                    self.assertEqual(moved.status, "completed")
                    [(trash_slug, _trash_id)] = list(app._trash_id_by_slug.items())

                    restored = await app.dispatch_app_action(
                        "restore_trash_item",
                        {"trash_item": "Alpha Restore"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()

                    self.assertEqual(restored.status, "completed")
                    self.assertNotIn(trash_slug, app._trash_id_by_slug)
                    self.assertIn(transcript_id, app._document_id_by_slug.values())
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_model_can_permanently_delete_trash_item_by_same_partial_title_used_to_delete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    created = await app.dispatch_app_action(
                        "create_memo",
                        {"title": "Alpha Delete Memo"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()
                    self.assertEqual(created.status, "completed")
                    moved = await app.dispatch_app_action(
                        "move_document_to_trash",
                        {"document": "Alpha Delete"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()
                    self.assertEqual(moved.status, "completed")
                    [(trash_slug, _trash_id)] = list(app._trash_id_by_slug.items())

                    deleted = await app.dispatch_app_action(
                        "permanently_delete_trash_item",
                        {"trash_item": "Alpha Delete"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()

                    self.assertEqual(deleted.status, "completed")
                    self.assertNotIn(trash_slug, app._trash_id_by_slug)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_notebook_restore_intent_corrects_misrouted_permanent_delete_tool(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                tool_call = ToolCallRequest(
                    provider="google",
                    tool_name="permanently_delete_trash_item",
                    arguments={"document": "Transcript 1 - Participant 1 - 5.1.26"},
                    raw_call_id="call-misrouted-restore",
                )
                app = ShellWorkflowTestApp(ToolCallBackend(tool_call))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    transcript_slug = "project-notebook"
                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._entry_nodes[transcript_slug], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()
                    [(trash_slug, _trash_id)] = list(app._trash_id_by_slug.items())

                    tree.move_cursor(tree._entry_nodes[CURRENT_DRAFT_SLUG], animate=False)
                    workflow = app.query_one(WorkflowPane)
                    composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                    composer.value = "Restore the transcript from the trash."
                    workflow.send_active_message()
                    for _ in range(6):
                        await pilot.pause()

                    request_entries = [
                        entry
                        for entry in workflow.active_chat.history_entries
                        if isinstance(entry, HistoryActionRequestEntry)
                    ]
                    self.assertEqual(len(request_entries), 1)
                    self.assertEqual(request_entries[0].action_id, "restore_trash_item")
                    self.assertIn(trash_slug, app._trash_id_by_slug)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_notebook_delete_intent_corrects_misrouted_restore_tool(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                tool_call = ToolCallRequest(
                    provider="mistral",
                    tool_name="restore_trash_item",
                    arguments={"document": "Alpha Delete"},
                    raw_call_id="call-misrouted-delete",
                )
                app = ShellWorkflowTestApp(ToolCallBackend(tool_call))
                async with app.run_test() as pilot:
                    await pilot.pause()
                    created = await app.dispatch_app_action(
                        "create_memo",
                        {"title": "Alpha Delete Memo"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()
                    self.assertEqual(created.status, "completed")

                    workflow = app.query_one(WorkflowPane)
                    composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                    composer.value = "Delete Alpha Delete Memo."
                    workflow.send_active_message()
                    for _ in range(6):
                        await pilot.pause()

                    request_entries = [
                        entry
                        for entry in workflow.active_chat.history_entries
                        if isinstance(entry, HistoryActionRequestEntry)
                    ]
                    self.assertEqual(len(request_entries), 1)
                    self.assertEqual(request_entries[0].action_id, "move_document_to_trash")

                    await workflow.on_action_request_card_confirm_requested(
                        ActionRequestCard.ConfirmRequested(ActionRequestCard(request_entries[0]), request_entries[0])
                    )
                    await pilot.pause()
                    self.assertEqual(len(app._trash_id_by_slug), 1)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_notebook_normal_delete_intent_corrects_misrouted_permanent_delete_tool(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                tool_call = ToolCallRequest(
                    provider="mistral",
                    tool_name="permanently_delete_trash_item",
                    arguments={"document": "Alpha Delete"},
                    raw_call_id="call-misrouted-normal-delete",
                )
                app = ShellWorkflowTestApp(ToolCallBackend(tool_call))
                async with app.run_test() as pilot:
                    await pilot.pause()
                    created = await app.dispatch_app_action(
                        "create_memo",
                        {"title": "Alpha Delete Memo"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()
                    self.assertEqual(created.status, "completed")

                    workflow = app.query_one(WorkflowPane)
                    composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                    composer.value = "Remove Alpha Delete Memo."
                    workflow.send_active_message()
                    for _ in range(6):
                        await pilot.pause()

                    request_entries = [
                        entry
                        for entry in workflow.active_chat.history_entries
                        if isinstance(entry, HistoryActionRequestEntry)
                    ]
                    self.assertEqual(len(request_entries), 1)
                    self.assertEqual(request_entries[0].action_id, "move_document_to_trash")
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_notebook_direct_delete_command_bypasses_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                backend = FakeBackend(configured=False)
                app = ShellWorkflowTestApp(backend)
                async with app.run_test() as pilot:
                    await pilot.pause()
                    created = await app.dispatch_app_action(
                        "create_memo",
                        {"title": "Alpha Direct Delete Memo"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()
                    self.assertEqual(created.status, "completed")

                    workflow = app.query_one(WorkflowPane)
                    composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                    composer.value = "Delete Alpha Direct Delete Memo."
                    workflow.send_active_message()
                    await pilot.pause()

                    request_entries = [
                        entry
                        for entry in workflow.active_chat.history_entries
                        if isinstance(entry, HistoryActionRequestEntry)
                    ]
                    self.assertEqual(len(request_entries), 1)
                    self.assertEqual(request_entries[0].action_id, "move_document_to_trash")
                    self.assertEqual(request_entries[0].payload["document"], "Alpha Direct Delete Memo")
                    self.assertIsNone(backend.last_mode)

                    await workflow.on_action_request_card_confirm_requested(
                        ActionRequestCard.ConfirmRequested(ActionRequestCard(request_entries[0]), request_entries[0])
                    )
                    await pilot.pause()
                    self.assertEqual(len(app._trash_id_by_slug), 1)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_notebook_direct_restore_command_bypasses_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                backend = FakeBackend(configured=False)
                app = ShellWorkflowTestApp(backend)
                async with app.run_test() as pilot:
                    await pilot.pause()
                    created = await app.dispatch_app_action(
                        "create_memo",
                        {"title": "Alpha Direct Restore Memo"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()
                    self.assertEqual(created.status, "completed")
                    moved = await app.dispatch_app_action(
                        "move_document_to_trash",
                        {"document": "Alpha Direct Restore"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()
                    self.assertEqual(moved.status, "completed")
                    self.assertEqual(len(app._trash_id_by_slug), 1)

                    workflow = app.query_one(WorkflowPane)
                    composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                    composer.value = "Restore Alpha Direct Restore from trash."
                    workflow.send_active_message()
                    await pilot.pause()

                    request_entries = [
                        entry
                        for entry in workflow.active_chat.history_entries
                        if isinstance(entry, HistoryActionRequestEntry)
                    ]
                    self.assertEqual(len(request_entries), 1)
                    self.assertEqual(request_entries[0].action_id, "restore_trash_item")
                    self.assertEqual(request_entries[0].payload["trash_item"], "Alpha Direct Restore")
                    self.assertIsNone(backend.last_mode)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_notebook_can_permanently_delete_trashed_transcript_in_non_confidential_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                tool_call = ToolCallRequest(
                    provider="mistral",
                    tool_name="permanently_delete_trash_item",
                    arguments={},
                    raw_call_id="call-delete-transcript",
                )
                app = ShellWorkflowTestApp(ToolCallBackend(tool_call))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    await app._create_project_document("Transcripts")
                    await pilot.pause()
                    transcript_slug = app.query_one(DocumentPane).active_document.slug
                    transcript_id = app._document_id_by_slug[transcript_slug]
                    backing_path = Path(tmp) / "demo-project" / transcript_id
                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._entry_nodes[transcript_slug], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()
                    [(trash_slug, _trash_id)] = list(app._trash_id_by_slug.items())
                    tree.move_cursor(tree._entry_nodes[trash_slug], animate=False)
                    await app.query_one(DocumentPane).open_document(trash_slug, focus=False)
                    await pilot.pause()

                    workflow = app.query_one(WorkflowPane)
                    app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input).value = "Permanently delete this transcript from trash."
                    workflow.send_active_message()
                    for _ in range(6):
                        await pilot.pause()

                    self.assertFalse(any(isinstance(entry, HistoryStatusEntry) and "full transcripts" in entry.content.casefold() for entry in workflow.active_chat.history_entries))
                    request_entries = [entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryActionRequestEntry)]
                    self.assertEqual(len(request_entries), 1)
                    self.assertEqual(request_entries[0].action_id, "permanently_delete_trash_item")

                    await workflow.on_action_request_card_confirm_requested(
                        ActionRequestCard.ConfirmRequested(ActionRequestCard(request_entries[0]), request_entries[0])
                    )
                    await pilot.pause()
                    await pilot.pause()

                    self.assertFalse(backing_path.exists())
                    self.assertNotIn(trash_slug, app._trash_id_by_slug)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_model_add_document_prefers_active_document_over_stale_project_selection(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            await app.query_one(DocumentPane).open_document("project-longform-essay", focus=False)
            tree = app.query_one(ProjectBrowserTree)
            tree.move_cursor(tree._entry_nodes["project-notebook"], animate=False)
            await pilot.pause()

            result = await app.dispatch_app_action("add_document_to_basket", {}, source="model_tool", confirmed=True)
            await pilot.pause()

            self.assertEqual(result.status, "completed")
            [item] = app._engine_adapter.state.basket.items
            self.assertEqual(item.payload["source_document_slug"], "project-longform-essay")
            self.assertEqual(item.payload["document_type"], "summary")
            self.assertNotEqual(item.payload["source_document_slug"], "project-notebook")

    async def test_model_add_excerpt_prefers_active_selection_over_stale_project_selection(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            content = DOCUMENT_FIXTURES["project-longform-essay"].content
            selected = "exploratory prose"
            start = content.casefold().index(selected)
            await app.query_one(DocumentPane).open_document_with_selection(
                "project-longform-essay",
                (start, start + len(selected)),
                focus=False,
            )
            tree = app.query_one(ProjectBrowserTree)
            tree.move_cursor(tree._entry_nodes["project-notebook"], animate=False)
            await pilot.pause()

            result = await app.dispatch_app_action("add_excerpt_to_basket", {}, source="model_tool", confirmed=True)
            await pilot.pause()

            self.assertEqual(result.status, "completed")
            [item] = app._engine_adapter.state.basket.items
            self.assertEqual(item.payload["source_document_slug"], "project-longform-essay")
            self.assertEqual(item.payload["source_document_type"], "summary")
            self.assertEqual(item.payload["selected_text"].casefold(), selected)

    async def test_model_full_transcript_add_refuses_before_confirmation(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            await app.query_one(DocumentPane).open_document("project-notebook", focus=False)
            await pilot.pause()

            result = await app.dispatch_app_action("add_document_to_basket", {}, source="model_tool")
            await pilot.pause()

            self.assertEqual(result.status, "refused")
            self.assertNotEqual(result.card.get("type") if isinstance(result.card, dict) else None, "action_request")
            self.assertNotIn("project-notebook", app._serialize_basket_context())

    async def test_model_add_excerpt_payload_from_transcript_is_allowed(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            content = DOCUMENT_FIXTURES["project-notebook"].content
            excerpt = "Interview fragments"
            self.assertIn(excerpt, content)

            result = await app.dispatch_app_action(
                "add_excerpt_to_basket",
                {"source_document": "project-notebook", "quote": excerpt},
                source="model_tool",
                confirmed=True,
            )
            await pilot.pause()

            self.assertEqual(result.status, "completed")
            [item] = app._engine_adapter.state.basket.items
            self.assertEqual(item.item_type, "excerpt")
            self.assertEqual(item.payload["source_document_slug"], "project-notebook")
            self.assertEqual(item.payload["source_document_type"], "transcript")
            self.assertEqual(item.payload["selected_text"], excerpt)

    async def test_model_document_action_with_excerpt_payload_reroutes_to_excerpt(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            excerpt = "Interview fragments"

            pending = await app.dispatch_app_action(
                "add_document_to_basket",
                {"document": "project-notebook", "passage": excerpt},
                source="model_tool",
            )
            self.assertEqual(pending.status, "pending_confirmation")
            self.assertEqual(pending.card.get("action_id") if isinstance(pending.card, dict) else None, "add_excerpt_to_basket")

            result = await app.dispatch_app_action(
                "add_document_to_basket",
                {"document": "project-notebook", "passage": excerpt},
                source="model_tool",
                confirmed=True,
            )
            await pilot.pause()

            self.assertEqual(result.status, "completed")
            [item] = app._engine_adapter.state.basket.items
            self.assertEqual(item.item_type, "excerpt")
            self.assertEqual(item.payload["source_document_slug"], "project-notebook")
            self.assertEqual(item.payload["selected_text"], excerpt)

    async def test_notebook_tool_can_confirm_transcript_excerpt_add(self) -> None:
        excerpt = "Interview fragments"
        tool_call = ToolCallRequest(
            provider="mistral",
            tool_name="add_excerpt_to_basket",
            arguments={"source_document": "project-notebook", "quote": excerpt},
            raw_call_id="call-transcript-excerpt",
        )
        app = ShellWorkflowTestApp(ToolCallBackend(tool_call))

        async with app.run_test() as pilot:
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            workflow = app.query_one(WorkflowPane)
            composer.value = "Add this transcript excerpt to the basket"

            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()
            await pilot.pause()

            request_entries = [
                entry
                for entry in workflow.active_chat.history_entries
                if isinstance(entry, HistoryActionRequestEntry)
            ]
            self.assertEqual(len(request_entries), 1)
            self.assertEqual(request_entries[0].action_id, "add_excerpt_to_basket")

            await workflow.on_action_request_card_confirm_requested(
                ActionRequestCard.ConfirmRequested(ActionRequestCard(request_entries[0]), request_entries[0])
            )
            await pilot.pause()

            [item] = app._engine_adapter.state.basket.items
            self.assertEqual(item.item_type, "excerpt")
            self.assertEqual(item.payload["source_document_slug"], "project-notebook")
            self.assertEqual(item.payload["source_document_type"], "transcript")
            self.assertEqual(item.payload["selected_text"], excerpt)

    async def test_notebook_document_tool_call_with_excerpt_intent_adds_selected_transcript_excerpt(self) -> None:
        excerpt = "Interview fragments"
        tool_call = ToolCallRequest(
            provider="mistral",
            tool_name="add_document_to_basket",
            arguments={},
            raw_call_id="call-misclassified-excerpt",
        )
        app = ShellWorkflowTestApp(ToolCallBackend(tool_call))

        async with app.run_test() as pilot:
            await pilot.pause()
            content = DOCUMENT_FIXTURES["project-notebook"].content
            start = content.index(excerpt)
            await app.query_one(DocumentPane).open_document_with_selection(
                "project-notebook",
                (start, start + len(excerpt)),
                focus=False,
            )
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            workflow = app.query_one(WorkflowPane)
            composer.value = "Add the selected excerpt to the basket"

            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()
            await pilot.pause()

            request_entries = [
                entry
                for entry in workflow.active_chat.history_entries
                if isinstance(entry, HistoryActionRequestEntry)
            ]
            self.assertEqual(len(request_entries), 1)
            self.assertEqual(request_entries[0].action_id, "add_excerpt_to_basket")
            self.assertFalse(
                any(
                    isinstance(entry, HistoryStatusEntry)
                    and entry.content == NON_CONFIDENTIAL_TRANSCRIPT_WARNING
                    for entry in workflow.active_chat.history_entries
                )
            )

            await workflow.on_action_request_card_confirm_requested(
                ActionRequestCard.ConfirmRequested(ActionRequestCard(request_entries[0]), request_entries[0])
            )
            await pilot.pause()

            [item] = app._engine_adapter.state.basket.items
            self.assertEqual(item.item_type, "excerpt")
            self.assertEqual(item.payload["source_document_slug"], "project-notebook")
            self.assertEqual(item.payload["source_document_type"], "transcript")
            self.assertEqual(item.payload["selected_text"], excerpt)

    async def test_model_folder_creation_does_not_recreate_selected_folder_inside_itself(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._folder_nodes[("Memos", "fieldwork")], animate=False)
                    result = await app.dispatch_app_action(
                        "create_folder",
                        {"category": "Memos", "name": "new_round"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()

                    self.assertEqual(result.status, "completed")
                    self.assertIn(("Memos", "fieldwork/new_round"), tree._folder_nodes)
                    self.assertEqual(tree.selected_folder_path(), "fieldwork/new_round")

                    repeated = await app.dispatch_app_action(
                        "create_folder",
                        {"category": "Memos", "name": "new_round"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()

                    self.assertEqual(repeated.status, "completed")
                    self.assertIn(("Memos", "fieldwork/new_round"), tree._folder_nodes)
                    self.assertNotIn(("Memos", "fieldwork/new_round/new_round"), tree._folder_nodes)
                    self.assertFalse((app._project_root / "memos" / "fieldwork" / "new_round" / "new_round").exists())
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_model_document_creation_uses_selected_folder_when_folder_is_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._folder_nodes[("Memos", "fieldwork")], animate=False)
                    await app.dispatch_app_action(
                        "create_folder",
                        {"category": "Memos", "name": "new_round"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()

                    result = await app.dispatch_app_action(
                        "create_memo",
                        {"title": "observation.md"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()

                    self.assertEqual(result.status, "completed")
                    self.assertTrue((app._project_root / "memos" / "fieldwork" / "new_round" / "observation.md").exists())
                    self.assertFalse((app._project_root / "memos" / "observation.md").exists())
                    document_slug = str(result.data["document_slug"])
                    self.assertEqual(app._document_id_by_slug[document_slug], "memos/fieldwork/new_round/observation.md")
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_transcript_document_is_not_auto_loaded_into_chat_context(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            await app.query_one(DocumentPane).open_document("project-notebook")
            await pilot.pause()
            context = app.shell_chat_context()
            self.assertEqual(context["document_type"], "transcript")
            self.assertEqual(context["document_content"], "")

    async def test_search_result_opens_document_with_snippet_selected_for_excerpt(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            transcript_text = DOCUMENT_FIXTURES["project-notebook"].content
            query = next(
                phrase
                for phrase in ("source context", "generated text", "Interview fragments", "Transcript")
                if phrase.casefold() in transcript_text.casefold()
            )
            results = QualShellApp.shell_search_documents(app, query)
            transcript_result = next(result for result in results if result["document_slug"] == "project-notebook")

            await app.on_workflow_pane_search_result_selected(
                WorkflowPane.SearchResultSelected(
                    app.query_one(WorkflowPane),
                    str(transcript_result["document_slug"]),
                    str(transcript_result["title"]),
                    tuple(transcript_result["match_range"]),
                )
            )
            await pilot.pause()

            document_pane = app.query_one(DocumentPane)
            self.assertEqual(document_pane.active_document.slug, "project-notebook")
            self.assertEqual(document_pane.selected_text.casefold(), query.casefold())

            app.action_add_excerpt_to_basket()
            await pilot.pause()
            basket_context = app._serialize_basket_context()
            self.assertIn("source_type=transcript", basket_context)
            self.assertIn(query.casefold(), basket_context.casefold())

    async def test_document_editor_copy_writes_host_clipboard(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            content = DOCUMENT_FIXTURES["project-demo-essay"].content
            selected = "theoretical frameworks"
            start = content.index(selected)
            await app.query_one(DocumentPane).open_document_with_selection(
                "project-demo-essay",
                (start, start + len(selected)),
                focus=True,
            )
            await pilot.pause()
            editor = app.query_one("#document-editor-project-demo-essay", TextArea)
            editor.focus()

            with patch("exegesis_textual.panes.document_pane.write_system_clipboard") as write_clipboard:
                await pilot.press("ctrl+c")
                await pilot.pause()

            write_clipboard.assert_called_once_with(selected)
            self.assertEqual(app.clipboard, selected)

    async def test_document_editors_show_text_area_line_numbers(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()

            await app.query_one(DocumentPane).open_document("project-demo-essay")
            await pilot.pause()

            self.assertTrue(app.query_one("#document-editor-current-draft", TextArea).show_line_numbers)
            self.assertTrue(app.query_one("#document-editor-project-demo-essay", TextArea).show_line_numbers)

    async def test_document_editor_paste_reads_host_clipboard(self) -> None:
        original = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content
        try:
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await pilot.pause()
                document_pane = app.query_one(DocumentPane)
                await document_pane.open_document(CURRENT_DRAFT_SLUG)
                await pilot.pause()
                editor = app.query_one("#document-editor-current-draft", TextArea)
                editor.selection = Selection((0, 0), (0, 0))
                editor.focus()

                with patch("exegesis_textual.panes.document_pane.read_system_clipboard", return_value="Pasted line\n"):
                    await pilot.press("ctrl+v")
                    await pilot.pause()

                self.assertTrue(editor.text.startswith("Pasted line\n"))
                self.assertTrue(DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content.startswith("Pasted line\n"))
        finally:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = original

    async def test_add_excerpt_to_basket_writes_engine_basket_payload(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()

            await app.query_one(DocumentPane).open_document("project-demo-essay")
            await pilot.pause()
            content = DOCUMENT_FIXTURES["project-demo-essay"].content
            selected = "theoretical frameworks"
            start = content.index(selected)
            await app.query_one(DocumentPane).open_document_with_selection(
                "project-demo-essay",
                (start, start + len(selected)),
                focus=False,
            )
            await pilot.pause()

            app.action_add_excerpt_to_basket()
            await pilot.pause()

            [item] = app._engine_adapter.state.basket.items
            self.assertEqual(item.item_type, "excerpt")
            self.assertEqual(item.payload["selected_text"], selected)
            self.assertEqual(item.payload["start"], start)
            self.assertEqual(item.payload["end"], start + len(selected))
            self.assertEqual(item.payload["source_document_slug"], "project-demo-essay")
            self.assertEqual(item.payload["source_status"], "current")
            self.assertIn("captured_at", item.payload)
            self.assertIsNotNone(app.query_one(BasketPane).get_entry(item.id))

    async def test_notebook_payload_adds_provenanced_excerpt_to_basket(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            content = DOCUMENT_FIXTURES["project-demo-essay"].content
            selected = "theoretical frameworks"
            start = content.index(selected)

            result = await app.dispatch_app_action(
                "add_excerpt_to_basket",
                {"document": "project-demo-essay", "excerpt": selected},
                source="model_tool",
                confirmed=True,
            )
            await pilot.pause()

            self.assertEqual(result.status, "completed")
            [item] = app._engine_adapter.state.basket.items
            self.assertEqual(item.item_type, "excerpt")
            self.assertEqual(item.payload["selected_text"], selected)
            self.assertEqual(item.payload["start"], start)
            self.assertEqual(item.payload["end"], start + len(selected))
            self.assertEqual(item.payload["source_document_slug"], "project-demo-essay")
            self.assertEqual(item.payload["source_match_status"], "matched_text")
            self.assertIsNotNone(app.query_one(BasketPane).get_entry(item.id))

    async def test_model_close_document_tab_closes_active_document_without_basket_mutation(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            document_pane = app.query_one(DocumentPane)
            await document_pane.open_document("project-longform-essay", focus=False)
            await pilot.pause()

            result = await app.dispatch_app_action("close_document_tab", {}, source="model_tool", confirmed=True)
            await pilot.pause()

            self.assertEqual(result.status, "completed")
            self.assertEqual(document_pane.active_document.slug, CURRENT_DRAFT_SLUG)
            self.assertEqual(app._engine_adapter.state.basket.items, [])

    async def test_search_result_add_to_basket_handler_adds_whole_document(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()

            await app.on_workflow_pane_search_result_add_to_basket_requested(
                WorkflowPane.SearchResultAddToBasketRequested(
                    app.query_one(WorkflowPane),
                    "project-demo-essay",
                    "Data Memo 1",
                    "memo",
                )
            )
            await pilot.pause()

            [item] = app._engine_adapter.state.basket.items
            self.assertEqual(item.item_type, "document")
            self.assertEqual(item.payload["source_document_slug"], "project-demo-essay")
            self.assertEqual(item.payload["document_type"], "memo")
            self.assertNotIn("selected_text", item.payload)

    async def test_search_result_add_to_basket_handler_refuses_full_transcript_in_non_confidential_project(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()

            await app.on_workflow_pane_search_result_add_to_basket_requested(
                WorkflowPane.SearchResultAddToBasketRequested(
                    app.query_one(WorkflowPane),
                    "project-notebook",
                    "Transcript 1 - Participant 1 - 5.1.26",
                    "transcript",
                )
            )
            await pilot.pause()

            self.assertEqual(app._engine_adapter.state.basket.items, [])
            self.assertIn("Full transcripts cannot be added", app.query_one(WorkflowPane)._status_message)

    async def test_basket_excerpt_inspector_shows_excerpt_type_without_instructional_copy(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()

            await app.query_one(DocumentPane).open_document("project-demo-essay")
            await pilot.pause()
            content = DOCUMENT_FIXTURES["project-demo-essay"].content
            selected = "theoretical frameworks"
            start = content.index(selected)
            await app.query_one(DocumentPane).open_document_with_selection(
                "project-demo-essay",
                (start, start + len(selected)),
                focus=False,
            )
            await pilot.pause()

            app.action_add_excerpt_to_basket()
            await pilot.pause()

            [item] = app._engine_adapter.state.basket.items
            entry = app.query_one(BasketPane).get_entry(item.id)
            self.assertIsNotNone(entry)
            self.assertEqual(entry.kind, "excerpt")
            self.assertTrue(entry.source_document_id)
            self.assertTrue(entry.captured_at)
            await app.query_one(DocumentPane).open_document(CURRENT_DRAFT_SLUG)
            await pilot.pause()
            await app._handle_basket_selection(entry)
            await pilot.pause()

            self.assertEqual(app.query_one(DocumentPane).active_document.slug, CURRENT_DRAFT_SLUG)
            markdown = app.query_one(f"#{INSPECTOR_MARKDOWN_ID}").source
            self.assertIn("Document type: **Excerpt**", markdown)
            self.assertNotIn("Selected excerpt from", markdown)
            self.assertNotIn("Saved from the current document selection.", markdown)
            self.assertNotIn("Selecting it should show the excerpt text in the inspector.", markdown)
            self.assertNotIn("Source type:", markdown)
            self.assertEqual(str(app.query_one(f"#{INSPECTOR_EXCERPT_TEXT_ID}", Static).render()), selected)
            markdown_widget = app.query_one(f"#{INSPECTOR_MARKDOWN_ID}", Markdown)
            link_event = Markdown.LinkClicked(markdown_widget, app._basket_entry_link_href(entry))
            await app.on_markdown_link_clicked(link_event)
            await pilot.pause()
            self.assertTrue(link_event._no_default_action)
            document_pane = app.query_one(DocumentPane)
            self.assertEqual(document_pane.active_document.slug, "project-demo-essay")
            self.assertEqual(document_pane.selected_text, selected)

    def test_basket_prompt_shows_color_coded_source_status(self) -> None:
        cases = {
            "current": ("Data Memo 1 [current]", "green"),
            "changed": ("Data Memo 1 [changed]", "yellow"),
            "trashed": ("Data Memo 1 [trashed]", "orange3"),
            "restored": ("Data Memo 1 [restored]", "green"),
            "source_deleted": ("Data Memo 1 [deleted]", "red"),
        }
        for source_status, (plain, style) in cases.items():
            with self.subTest(source_status=source_status):
                prompt = basket_entry_prompt(
                    BasketEntry(
                        slug=f"basket-{source_status}",
                        kind="document",
                        title="Document",
                        source="Data Memo 1",
                        source_document_slug="project-demo-essay",
                        source_document_type="memo",
                        summary="",
                        bullets=(),
                        content="Snapshot.",
                        source_status=source_status,
                    )
                )
                self.assertEqual(prompt.plain, plain)
                self.assertEqual(str(prompt.spans[-1].style), style)

    async def test_non_document_inspector_link_opens_externally(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            markdown_widget = app.query_one(f"#{INSPECTOR_MARKDOWN_ID}", Markdown)
            link_event = Markdown.LinkClicked(markdown_widget, "file:///tmp/source.pdf")
            with patch.object(app, "open_url") as open_url:
                await app.on_markdown_link_clicked(link_event)

            open_url.assert_called_once_with("file:///tmp/source.pdf")
            self.assertFalse(link_event._no_default_action)

    async def test_unsafe_inspector_link_is_blocked(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            markdown_widget = app.query_one(f"#{INSPECTOR_MARKDOWN_ID}", Markdown)
            link_event = Markdown.LinkClicked(markdown_widget, "javascript:alert(1)")
            with patch.object(app, "open_url") as open_url:
                await app.on_markdown_link_clicked(link_event)

            open_url.assert_not_called()
            self.assertTrue(link_event._no_default_action)

    async def test_basket_document_inspector_uses_normal_document_excerpt_without_instructional_copy(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()

            self.assertTrue(app._add_document_slug_to_basket("project-demo-essay"))
            await pilot.pause()

            [item] = app._engine_adapter.state.basket.items
            entry = app.query_one(BasketPane).get_entry(item.id)
            self.assertIsNotNone(entry)
            self.assertEqual(app.query_one(DocumentPane).active_document.slug, CURRENT_DRAFT_SLUG)
            await app._handle_basket_selection(entry)
            await pilot.pause()

            self.assertEqual(app.query_one(DocumentPane).active_document.slug, CURRENT_DRAFT_SLUG)
            markdown = app.query_one(f"#{INSPECTOR_MARKDOWN_ID}").source
            excerpt = str(app.query_one(f"#{INSPECTOR_EXCERPT_TEXT_ID}", Static).render())
            expected_excerpt = app._document_excerpt(DOCUMENT_FIXTURES["project-demo-essay"].content)
            self.assertIn("Document type: **Memo**", markdown)
            self.assertIn("- Source file: memos/", markdown)
            self.assertIn("- Source status: current", markdown)
            self.assertIn("- Captured at:", markdown)
            self.assertNotIn("- Source status: current.", markdown)
            self.assertEqual(excerpt, expected_excerpt)
            self.assertNotIn("Whole file added from", markdown)
            self.assertNotIn("Saved from the active document tab.", markdown)
            self.assertNotIn("Selecting it should open or focus the document tab.", markdown)
            self.assertNotIn("Source type:", markdown)
            markdown_widget = app.query_one(f"#{INSPECTOR_MARKDOWN_ID}", Markdown)
            link_event = Markdown.LinkClicked(markdown_widget, app._basket_entry_link_href(entry))
            await app.on_markdown_link_clicked(link_event)
            await pilot.pause()
            self.assertTrue(link_event._no_default_action)
            self.assertEqual(app.query_one(DocumentPane).active_document.slug, "project-demo-essay")

    async def test_saved_source_marks_basket_snapshot_changed_without_replacing_content(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()

            await app.query_one(DocumentPane).open_document("project-demo-essay")
            await pilot.pause()
            original_content = DOCUMENT_FIXTURES["project-demo-essay"].content
            try:
                self.assertTrue(app._add_document_slug_to_basket("project-demo-essay"))
                await pilot.pause()

                [item] = app._engine_adapter.state.basket.items
                self.assertEqual(item.payload["content"], original_content)

                DOCUMENT_FIXTURES["project-demo-essay"].content = f"{original_content}\nManual update after capture.\n"
                app._dirty_document_slugs.add("project-demo-essay")
                app._save_dirty_documents({"project-demo-essay"})
                await pilot.pause()

                [updated_item] = app._engine_adapter.state.basket.items
                self.assertEqual(updated_item.payload["source_status"], "changed")
                self.assertEqual(updated_item.payload["content"], original_content)
                entry = app.query_one(BasketPane).get_entry(updated_item.id)
                self.assertIsNotNone(entry)
                self.assertEqual(entry.source_status, "changed")
                context = app._serialize_basket_context()
                self.assertIn("source_status=changed", context)
            finally:
                DOCUMENT_FIXTURES["project-demo-essay"].content = original_content

    async def test_saved_source_marks_basket_excerpt_changed_without_replacing_content(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()

            await app.query_one(DocumentPane).open_document("project-demo-essay")
            await pilot.pause()
            original_content = DOCUMENT_FIXTURES["project-demo-essay"].content
            selected = "theoretical frameworks"
            start = original_content.index(selected)
            try:
                await app.query_one(DocumentPane).open_document_with_selection(
                    "project-demo-essay",
                    (start, start + len(selected)),
                    focus=False,
                )
                await pilot.pause()

                app.action_add_excerpt_to_basket()
                await pilot.pause()

                [item] = app._engine_adapter.state.basket.items
                self.assertEqual(item.item_type, "excerpt")
                self.assertEqual(item.payload["source_status"], "current")

                DOCUMENT_FIXTURES["project-demo-essay"].content = f"{original_content}\nManual update after excerpt capture.\n"
                app._dirty_document_slugs.add("project-demo-essay")
                app._save_dirty_documents({"project-demo-essay"})
                await pilot.pause()

                [updated_item] = app._engine_adapter.state.basket.items
                self.assertEqual(updated_item.payload["source_status"], "changed")
                self.assertEqual(updated_item.payload["selected_text"], selected)
                entry = app.query_one(BasketPane).get_entry(updated_item.id)
                self.assertIsNotNone(entry)
                self.assertEqual(entry.source_status, "changed")
                self.assertEqual(entry.content, selected)
                self.assertIn("source_status=changed", app._serialize_basket_context())
            finally:
                DOCUMENT_FIXTURES["project-demo-essay"].content = original_content

    async def test_dirty_source_marks_basket_excerpt_changed_before_save(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()

            await app.query_one(DocumentPane).open_document("project-demo-essay")
            await pilot.pause()
            original_content = DOCUMENT_FIXTURES["project-demo-essay"].content
            selected = "theoretical frameworks"
            start = original_content.index(selected)
            try:
                await app.query_one(DocumentPane).open_document_with_selection(
                    "project-demo-essay",
                    (start, start + len(selected)),
                    focus=False,
                )
                await pilot.pause()

                app.action_add_excerpt_to_basket()
                await pilot.pause()

                [item] = app._engine_adapter.state.basket.items
                self.assertEqual(item.payload["source_status"], "current")

                changed_content = f"{original_content}\nManual unsaved update after excerpt capture.\n"
                DOCUMENT_FIXTURES["project-demo-essay"].content = changed_content
                app.on_document_pane_content_changed(
                    DocumentPane.ContentChanged(app.query_one(DocumentPane), "project-demo-essay", changed_content)
                )
                await pilot.pause()

                [updated_item] = app._engine_adapter.state.basket.items
                self.assertEqual(updated_item.payload["source_status"], "changed")
                self.assertEqual(updated_item.payload["selected_text"], selected)
                entry = app.query_one(BasketPane).get_entry(updated_item.id)
                self.assertIsNotNone(entry)
                self.assertEqual(entry.source_status, "changed")
            finally:
                DOCUMENT_FIXTURES["project-demo-essay"].content = original_content

    async def test_trashed_and_permanently_deleted_sources_preserve_basket_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Memos")
                    await pilot.pause()
                    [(slug, document_id)] = [
                        (slug, document_id)
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    ]
                    original_content = DOCUMENT_FIXTURES[slug].content

                    self.assertTrue(app._add_document_slug_to_basket(slug))
                    await pilot.pause()
                    [item] = app._engine_adapter.state.basket.items
                    self.assertEqual(item.payload["source_status"], "current")

                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._entry_nodes[slug], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()

                    [trashed_item] = app._engine_adapter.state.basket.items
                    self.assertEqual(trashed_item.payload["source_status"], "trashed")
                    self.assertEqual(trashed_item.payload["content"], original_content)
                    self.assertNotIn(slug, app._document_id_by_slug)
                    context = app._serialize_basket_context()
                    self.assertIn("source_status=trashed", context)

                    [(trash_slug, trash_id)] = list(app._trash_id_by_slug.items())
                    app._handle_trash_document_result(trash_slug, "permanent_delete")
                    await pilot.pause()

                    self.assertIsInstance(app.screen, PermanentDeleteTrashConfirmModal)
                    app._handle_permanent_delete_confirmed((trash_slug,), True)
                    await pilot.pause()

                    [deleted_item] = app._engine_adapter.state.basket.items
                    self.assertEqual(deleted_item.payload["source_status"], "source_deleted")
                    self.assertEqual(deleted_item.payload["content"], original_content)
                    self.assertIn("source_status=source_deleted", app._serialize_basket_context())

                    await app.query_one(DocumentPane).open_document(CURRENT_DRAFT_SLUG)
                    await pilot.pause()
                    entry = app.query_one(BasketPane).get_entry(deleted_item.id)
                    self.assertIsNotNone(entry)
                    await app._handle_basket_selection(entry)
                    await pilot.pause()
                    self.assertEqual(app.query_one(DocumentPane).active_document.slug, CURRENT_DRAFT_SLUG)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_trash_document_opens_read_only_with_trashed_view_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Memos")
                    await pilot.pause()
                    [(slug, _document_id)] = [
                        (slug, document_id)
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    ]

                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._entry_nodes[slug], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()
                    [(trash_slug, _trash_id)] = list(app._trash_id_by_slug.items())

                    await app.query_one(DocumentPane).open_document(trash_slug, focus=False)
                    await pilot.pause()

                    document_pane = app.query_one(DocumentPane)
                    editor = document_pane.query_one(f"#document-editor-{trash_slug}", TextArea)
                    self.assertEqual(document_pane.document_view_status(trash_slug), "trashed")
                    tab = app.query_one(f"#{DOCUMENT_TABBED_CONTENT_ID}", TabbedContent).get_tab(trash_slug)
                    self.assertIsNotNone(tab)
                    self.assertTrue(tab.has_class("document-tab-trashed"))
                    self.assertTrue(editor.read_only)
                    self.assertTrue(app.query_one(f"#{DOCUMENT_SAVE_BUTTON_ID}", Button).disabled)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_deleted_basket_excerpt_title_opens_read_only_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Memos")
                    await pilot.pause()
                    [(slug, _document_id)] = [
                        (slug, document_id)
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    ]
                    fixture = DOCUMENT_FIXTURES[slug]
                    fixture.content = "# Temporary memo\n\nA captured basket excerpt survives deletion.\n"
                    selected = "captured basket excerpt"
                    start = fixture.content.index(selected)
                    await app.query_one(DocumentPane).open_document_with_selection(slug, (start, start + len(selected)), focus=False)
                    await pilot.pause()

                    app.action_add_excerpt_to_basket()
                    await pilot.pause()

                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._entry_nodes[slug], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()
                    [(trash_slug, _trash_id)] = list(app._trash_id_by_slug.items())
                    app._handle_trash_document_result(trash_slug, "permanent_delete")
                    await pilot.pause()
                    app._handle_permanent_delete_confirmed((trash_slug,), True)
                    await pilot.pause()

                    [item] = app._engine_adapter.state.basket.items
                    entry = app.query_one(BasketPane).get_entry(item.id)
                    self.assertIsNotNone(entry)
                    self.assertEqual(entry.source_status, "source_deleted")
                    href = app._basket_entry_link_href(entry)
                    self.assertTrue(href.startswith("exegesis://basket/"))

                    markdown_widget = app.query_one(f"#{INSPECTOR_MARKDOWN_ID}", Markdown)
                    link_event = Markdown.LinkClicked(markdown_widget, href)
                    await app.on_markdown_link_clicked(link_event)
                    await pilot.pause()

                    document_pane = app.query_one(DocumentPane)
                    snapshot_slug = app._basket_snapshot_slug(entry)
                    editor = document_pane.query_one(f"#document-editor-{snapshot_slug}", TextArea)
                    self.assertEqual(document_pane.active_document.slug, snapshot_slug)
                    self.assertEqual(document_pane.document_view_status(snapshot_slug), "source_deleted")
                    tab = app.query_one(f"#{DOCUMENT_TABBED_CONTENT_ID}", TabbedContent).get_tab(snapshot_slug)
                    self.assertIsNotNone(tab)
                    self.assertTrue(tab.has_class("document-tab-deleted"))
                    self.assertTrue(editor.read_only)
                    self.assertFalse(editor.has_class("document-editor-deleted"))
                    self.assertIn(selected, editor.text)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_restored_source_rebinds_basket_snapshot_to_restored_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Memos")
                    await pilot.pause()
                    [(slug, document_id)] = [
                        (slug, document_id)
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    ]
                    original_content = DOCUMENT_FIXTURES[slug].content

                    self.assertTrue(app._add_document_slug_to_basket(slug))
                    await pilot.pause()

                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._entry_nodes[slug], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()
                    [(trash_slug, _trash_id)] = list(app._trash_id_by_slug.items())

                    app._handle_trash_document_result(trash_slug, "restore")
                    await pilot.pause()

                    [restored_item] = app._engine_adapter.state.basket.items
                    restored_slug = restored_item.payload["source_document_slug"]
                    self.assertEqual(restored_item.payload["source_status"], "restored")
                    self.assertEqual(restored_item.payload["document_id"], document_id)
                    self.assertIn(restored_slug, app._document_id_by_slug)
                    self.assertEqual(restored_item.payload["content"], original_content)
                    self.assertIn("source_status=restored", app._serialize_basket_context())

                    await app.query_one(DocumentPane).open_document(CURRENT_DRAFT_SLUG)
                    await pilot.pause()
                    entry = app.query_one(BasketPane).get_entry(restored_item.id)
                    self.assertIsNotNone(entry)
                    self.assertEqual(entry.source_status, "restored")
                    await app._handle_basket_selection(entry)
                    await pilot.pause()
                    self.assertEqual(app.query_one(DocumentPane).active_document.slug, CURRENT_DRAFT_SLUG)
                    markdown_widget = app.query_one(f"#{INSPECTOR_MARKDOWN_ID}", Markdown)
                    link_event = Markdown.LinkClicked(markdown_widget, app._basket_entry_link_href(entry))
                    await app.on_markdown_link_clicked(link_event)
                    await pilot.pause()
                    self.assertTrue(link_event._no_default_action)
                    self.assertEqual(app.query_one(DocumentPane).active_document.slug, restored_slug)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_closing_leftmost_active_document_tab_keeps_tab_selection_in_sync(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            document_pane = app.query_one(DocumentPane)
            tabbed_content = document_pane.query_one(f"#{DOCUMENT_TABBED_CONTENT_ID}", TabbedContent)

            await document_pane.open_document("project-demo-essay")
            await document_pane.open_document(CURRENT_DRAFT_SLUG)
            await pilot.pause()
            self.assertEqual(document_pane._open_tabs[:2], [CURRENT_DRAFT_SLUG, "project-demo-essay"])
            self.assertEqual(tabbed_content.active, CURRENT_DRAFT_SLUG)

            closed = await document_pane.close_active_document()
            await pilot.pause()

            self.assertTrue(closed)
            self.assertNotIn(CURRENT_DRAFT_SLUG, document_pane._open_tabs)
            self.assertEqual(document_pane.active_document.slug, "project-demo-essay")
            self.assertEqual(tabbed_content.active, "project-demo-essay")

    async def test_trash_actions_are_exposed_in_top_shortcuts_and_palette(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()

            self.assertIsNotNone(app.query_one(f"#{TOP_RESTORE_TRASH_ID}", Button))
            self.assertIsNotNone(app.query_one(f"#{TOP_MOVE_TO_TRASH_ID}", Button))
            self.assertIsNotNone(app.query_one(f"#{TOP_PERMANENT_DELETE_TRASH_ID}", Button))
            self.assertIsNotNone(app.query_one(f"#{TOP_SAVE_DOCUMENT_ID}", Button))
            self.assertIsNotNone(app.query_one(f"#{TOP_UPDATE_ITEM_ID}", Button))
            self.assertIsNotNone(app.query_one(f"#{DOCUMENT_SAVE_BUTTON_ID}", Button))
            file_row_button_ids = [button.id for button in app.query_one(f"#{COMMAND_BAR_FILE_ID}").query(Button)]
            self.assertEqual(
                file_row_button_ids[:3],
                [TOP_SAVE_DOCUMENT_ID, TOP_NEW_FOLDER_ID, TOP_UPDATE_ITEM_ID],
            )

            labels = {command.label for command in default_palette_commands()}
            self.assertIn("Move document to trash", labels)
            self.assertIn("Restore trash item", labels)
            self.assertIn("Permanently delete trash item", labels)
            self.assertIn("Save document", labels)
            self.assertIn("Update item", labels)

    async def test_trash_modal_buttons_match_shell_action_styles(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await app.push_screen(TrashDocumentModal("Working Memo", "memos/memo_01.md"))
            await pilot.pause()

            modal = app.screen_stack[-1]
            self.assertIsNotNone(modal.query_one("#trash-document-modal"))
            for button_id in (TRASH_RESTORE_ID, TRASH_PERMANENT_DELETE_ID, TRASH_CANCEL_ID):
                self.assertTrue(modal.query_one(f"#{button_id}", Button).has_class("trash-modal-button"))
            self.assertTrue(modal.query_one(f"#{TRASH_RESTORE_ID}", Button).has_class("trash-modal-side-button"))
            self.assertTrue(modal.query_one(f"#{TRASH_CANCEL_ID}", Button).has_class("trash-modal-side-button"))
            self.assertTrue(modal.query_one(f"#{TRASH_PERMANENT_DELETE_ID}", Button).has_class("trash-modal-danger-button"))
            self.assertEqual(modal.query_one(f"#{TRASH_RESTORE_ID}", Button).variant, "primary")
            self.assertEqual(modal.query_one(f"#{TRASH_PERMANENT_DELETE_ID}", Button).variant, "error")
            self.assertEqual(modal.query_one(f"#{TRASH_CANCEL_ID}", Button).variant, "warning")

    async def test_delete_folder_confirm_modal_buttons_match_shell_action_styles(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await app.push_screen(DeleteFolderConfirmModal("fieldwork/round_1", 1))
            await pilot.pause()

            modal = app.screen_stack[-1]
            self.assertIsNotNone(modal.query_one("#folder-delete-confirm-modal"))
            confirm = modal.query_one("#project-delete-confirm", Button)
            cancel = modal.query_one("#project-delete-cancel", Button)
            self.assertTrue(confirm.has_class("confirm-modal-button"))
            self.assertTrue(cancel.has_class("confirm-modal-button"))
            self.assertEqual(confirm.variant, "error")
            self.assertEqual(cancel.variant, "default")

    async def test_permanent_delete_confirm_modal_buttons_match_shell_action_styles(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await app.push_screen(PermanentDeleteTrashConfirmModal("memo_01.md"))
            await pilot.pause()

            modal = app.screen_stack[-1]
            self.assertIsNotNone(modal.query_one("#trash-delete-confirm-modal"))
            confirm = modal.query_one("#project-delete-confirm", Button)
            cancel = modal.query_one("#project-delete-cancel", Button)
            self.assertTrue(confirm.has_class("confirm-modal-button"))
            self.assertTrue(cancel.has_class("confirm-modal-button"))
            self.assertEqual(confirm.variant, "error")
            self.assertEqual(cancel.variant, "default")

    async def test_shell_creates_restores_and_permanently_deletes_real_project_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Drafts")
                    await pilot.pause()

                    [(slug, document_id)] = [
                        (slug, document_id)
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    ]
                    backing_path = Path(tmp) / "demo-project" / document_id
                    self.assertTrue(backing_path.exists())

                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._entry_nodes[slug], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()

                    self.assertFalse(backing_path.exists())
                    trash_root = Path(tmp) / "demo-project" / ".trash" / "documents"
                    self.assertTrue(any(path.name == backing_path.name for path in trash_root.rglob("*.md")))
                    self.assertNotIn(slug, app._document_id_by_slug)
                    self.assertNotIn(slug, app.query_one(DocumentPane)._open_tabs)
                    [(trash_slug, trash_id)] = list(app._trash_id_by_slug.items())

                    await app.query_one(DocumentPane).open_document(trash_slug)
                    await pilot.pause()
                    self.assertIn(trash_slug, app.query_one(DocumentPane)._open_tabs)

                    app._handle_trash_document_result(trash_slug, "restore")
                    await pilot.pause()

                    self.assertTrue(backing_path.exists())
                    self.assertNotIn(trash_slug, app._trash_id_by_slug)
                    self.assertNotIn(trash_slug, app.query_one(DocumentPane)._open_tabs)
                    restored_slug = next(
                        restored_slug
                        for restored_slug, restored_document_id in app._document_id_by_slug.items()
                        if restored_document_id == document_id
                    )

                    tree.move_cursor(tree._entry_nodes[restored_slug], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()

                    [(trash_slug, trash_id)] = list(app._trash_id_by_slug.items())
                    await app.query_one(DocumentPane).open_document(trash_slug)
                    await pilot.pause()
                    self.assertIn(trash_slug, app.query_one(DocumentPane)._open_tabs)

                    app._handle_trash_document_result(trash_slug, "permanent_delete")
                    await pilot.pause()

                    self.assertIsInstance(app.screen, PermanentDeleteTrashConfirmModal)
                    app._handle_permanent_delete_confirmed((trash_slug,), True)
                    await pilot.pause()

                    self.assertFalse(backing_path.exists())
                    self.assertNotIn(trash_slug, app._trash_id_by_slug)
                    self.assertNotIn(trash_slug, app.query_one(DocumentPane)._open_tabs)
                    audit_text = (Path(tmp) / "demo-project" / "audit_events.jsonl").read_text(encoding="utf-8")
                    self.assertIn("document.permanently_deleted", audit_text)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_project_browser_delete_key_moves_selected_document_to_trash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Memos")
                    await pilot.pause()
                    [(slug, document_id)] = [
                        (slug, document_id)
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    ]
                    backing_path = Path(tmp) / "demo-project" / document_id

                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._entry_nodes[slug], animate=False)
                    tree.focus()
                    await pilot.press("delete")
                    await pilot.pause()

                    self.assertFalse(backing_path.exists())
                    self.assertNotIn(slug, app._document_id_by_slug)
                    self.assertNotIn(slug, app.query_one(DocumentPane)._open_tabs)
                    self.assertEqual(len(app._trash_id_by_slug), 1)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_project_browser_preserves_extensionless_display_title_in_trash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    slug = "project-demo-essay"
                    document_id = app._document_id_by_slug[slug]
                    tree = app.query_one(ProjectBrowserTree)
                    source_info = tree._entry_nodes[slug].data
                    self.assertIsNotNone(source_info)
                    self.assertEqual(source_info.title, "Data Memo 1")

                    tree.move_cursor(tree._entry_nodes[slug], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()

                    [(trash_slug, _trash_id)] = list(app._trash_id_by_slug.items())
                    trash_info = tree._entry_nodes[trash_slug].data
                    self.assertIsNotNone(trash_info)
                    self.assertEqual(trash_info.title, "Data Memo 1")
                    self.assertNotIn(".md", str(tree._entry_nodes[trash_slug].label))
                    self.assertEqual(app._engine_adapter.list_trash_items()[0].label, "Data Memo 1")

                    app._handle_trash_document_result(trash_slug, "restore")
                    await pilot.pause()

                    restored_slug = next(
                        candidate_slug
                        for candidate_slug, candidate_document_id in app._document_id_by_slug.items()
                        if candidate_document_id == document_id
                    )
                    restored_info = tree._entry_nodes[restored_slug].data
                    self.assertIsNotNone(restored_info)
                    self.assertEqual(restored_info.title, "Data Memo 1")
                    self.assertNotIn(".md", str(tree._entry_nodes[restored_slug].label))
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_project_browser_backspace_key_moves_selected_document_to_trash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Memos")
                    await pilot.pause()
                    [(slug, document_id)] = [
                        (slug, document_id)
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    ]
                    backing_path = Path(tmp) / "demo-project" / document_id

                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._entry_nodes[slug], animate=False)
                    tree.focus()
                    await pilot.press("backspace")
                    await pilot.pause()

                    self.assertFalse(backing_path.exists())
                    self.assertNotIn(slug, app._document_id_by_slug)
                    self.assertEqual(len(app._trash_id_by_slug), 1)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_project_browser_enter_opens_update_item_modal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Memos")
                    await pilot.pause()
                    [(slug, document_id)] = [
                        (slug, document_id)
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    ]
                    backing_path = Path(tmp) / "demo-project" / document_id

                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._entry_nodes[slug], animate=False)
                    tree.focus()
                    await pilot.press("enter")
                    await pilot.pause()

                    self.assertIsInstance(app.screen, UpdateProjectItemModal)
                    self.assertEqual(app.screen.query_one(f"#{PROJECT_UPDATE_TITLE_INPUT_ID}", Input).value, "memo_01.md")
                    self.assertIn(
                        "Memos",
                        str(app.screen.query_one(f"#{PROJECT_UPDATE_SELECTED_FOLDER_ID}", Static).render()),
                    )
                    self.assertTrue(backing_path.exists())
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_project_browser_mouse_click_toggles_folder_expand_collapse(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test(size=(254, 91)) as pilot:
            await pilot.pause()

            tree = app.query_one(ProjectBrowserTree)
            _ = tree._tree_lines
            folder_node = tree._folder_nodes[("Memos", "fieldwork")]
            self.assertTrue(folder_node.is_expanded)

            await pilot.click(tree, offset=(2, folder_node._line - int(tree.scroll_y)))
            await pilot.pause()

            self.assertFalse(folder_node.is_expanded)

            _ = tree._tree_lines
            await pilot.click(tree, offset=(2, folder_node._line - int(tree.scroll_y)))
            await pilot.pause()

            self.assertTrue(folder_node.is_expanded)

    async def test_new_folder_creation_selects_new_folder_and_expands_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    tree = app.query_one(ProjectBrowserTree)
                    parent_node = tree._folder_nodes[("Memos", "fieldwork")]
                    parent_node.collapse()
                    tree.move_cursor(parent_node, animate=False)

                    app._handle_new_folder_result("Memos", "new_round")
                    await pilot.pause()

                    new_node = tree._folder_nodes[("Memos", "fieldwork/new_round")]
                    self.assertTrue(parent_node.is_expanded)
                    self.assertIs(tree.cursor_node, new_node)
                    self.assertEqual(tree.selected_folder_path(), "fieldwork/new_round")
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_repeated_single_click_does_not_open_rename_modal(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()

            tree = app.query_one(ProjectBrowserTree)
            tree.move_cursor(tree._entry_nodes["project-demo-essay"], animate=False)
            await tree.run_action("select_cursor")
            await pilot.pause()
            await tree.run_action("select_cursor")
            await pilot.pause()

            self.assertEqual(app.screen.id, "_default")
            self.assertEqual(app.query_one(DocumentPane).active_document.slug, "project-demo-essay")

    async def test_project_browser_shift_click_marks_individual_documents_for_bulk_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Memos")
                    await app._create_project_document("Literature")
                    await pilot.pause()
                    slugs = [
                        slug
                        for slug in app._document_id_by_slug
                        if slug not in before_create and slug in DOCUMENT_FIXTURES
                    ]
                    self.assertEqual(len(slugs), 2)

                    tree = app.query_one(ProjectBrowserTree)
                    first_node = tree._entry_nodes[slugs[0]]
                    await tree._on_click(
                        events.Click(
                            tree,
                            x=0,
                            y=first_node._line - int(tree.scroll_y),
                            delta_x=0,
                            delta_y=0,
                            button=1,
                            shift=False,
                            meta=False,
                            ctrl=False,
                            style=Style(),
                        )
                    )
                    node = tree._entry_nodes[slugs[1]]
                    await tree._on_click(
                        events.Click(
                            tree,
                            x=0,
                            y=node._line - int(tree.scroll_y),
                            delta_x=0,
                            delta_y=0,
                            button=1,
                            shift=True,
                            meta=False,
                            ctrl=False,
                            style=Style(),
                        )
                    )

                    marked = tree.marked_entry_infos(kinds={"entry"})
                    self.assertEqual({info.slug for info in marked}, set(slugs))
                    self.assertTrue(all(str(tree._entry_nodes[slug].label).startswith("[*] ") for slug in slugs))

                    app.action_add_file_to_basket()
                    await pilot.pause()

                    basket = app.query_one(BasketPane)
                    for slug in slugs:
                        self.assertIsNotNone(basket.get_entry(f"document:{app._document_id_by_slug[slug]}"))
                    self.assertEqual(
                        {item.id for item in app._engine_adapter.state.basket.items},
                        {f"document:{app._document_id_by_slug[slug]}" for slug in slugs},
                    )
                    self.assertEqual(tree.marked_entry_infos(kinds={"entry"}), ())
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_project_browser_pilot_shift_click_marks_visible_documents_once(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test(size=(254, 91)) as pilot:
            await pilot.pause()

            tree = app.query_one(ProjectBrowserTree)
            first_node = tree._entry_nodes["project-demo-essay"]
            second_node = tree._entry_nodes["project-root-memo"]

            self.assertTrue(await pilot.click(tree, offset=(6, first_node._line - int(tree.scroll_y))))
            await pilot.pause()
            self.assertEqual(tree.selected_entry_info().slug, "project-demo-essay")

            self.assertTrue(
                await pilot.click(
                    tree,
                    offset=(6, second_node._line - int(tree.scroll_y)),
                    shift=True,
                )
            )
            await pilot.pause()

            self.assertEqual(
                {info.slug for info in tree.marked_entry_infos(kinds={"entry"})},
                {"project-demo-essay", "project-root-memo"},
            )

    async def test_project_browser_space_marks_individual_documents_for_keyboard_bulk_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Memos")
                    await app._create_project_document("Literature")
                    await pilot.pause()
                    slugs = [
                        slug
                        for slug in app._document_id_by_slug
                        if slug not in before_create and slug in DOCUMENT_FIXTURES
                    ]
                    self.assertEqual(len(slugs), 2)

                    tree = app.query_one(ProjectBrowserTree)
                    tree.focus()
                    for slug in slugs:
                        tree.move_cursor(tree._entry_nodes[slug], animate=False)
                        await pilot.press("space")
                        await pilot.pause()

                    self.assertEqual({info.slug for info in tree.marked_entry_infos(kinds={"entry"})}, set(slugs))

                    app.action_add_file_to_basket()
                    await pilot.pause()

                    basket = app.query_one(BasketPane)
                    for slug in slugs:
                        self.assertIsNotNone(basket.get_entry(f"document:{app._document_id_by_slug[slug]}"))
                    self.assertEqual(
                        {item.id for item in app._engine_adapter.state.basket.items},
                        {f"document:{app._document_id_by_slug[slug]}" for slug in slugs},
                    )
                    self.assertEqual(tree.marked_entry_infos(kinds={"entry"}), ())
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_project_browser_bulk_delete_restore_and_permanent_delete_from_marked_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Memos")
                    await app._create_project_document("Literature")
                    await pilot.pause()
                    created = {
                        slug: document_id
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    }
                    self.assertEqual(len(created), 2)

                    tree = app.query_one(ProjectBrowserTree)
                    for slug in created:
                        tree.toggle_marked_entry(slug)

                    await app._delete_selected_project_document()
                    await pilot.pause()

                    self.assertTrue(all(slug not in app._document_id_by_slug for slug in created))
                    self.assertEqual(len(app._trash_id_by_slug), 2)
                    trash_slugs = tuple(app._trash_id_by_slug)

                    for trash_slug in trash_slugs:
                        tree.toggle_marked_entry(trash_slug)
                    app.action_restore_selected_trash_item()
                    await pilot.pause()

                    self.assertEqual(app._trash_id_by_slug, {})
                    restored = {
                        slug: document_id
                        for slug, document_id in app._document_id_by_slug.items()
                        if document_id in set(created.values())
                    }
                    self.assertEqual(set(restored.values()), set(created.values()))

                    for slug in restored:
                        tree.toggle_marked_entry(slug)
                    await app._delete_selected_project_document()
                    await pilot.pause()
                    self.assertEqual(len(app._trash_id_by_slug), 2)
                    trash_slugs = tuple(app._trash_id_by_slug)

                    for trash_slug in trash_slugs:
                        tree.toggle_marked_entry(trash_slug)
                    app.action_permanently_delete_selected_trash_item()
                    await pilot.pause()

                    self.assertIsInstance(app.screen, PermanentDeleteTrashConfirmModal)
                    app._handle_permanent_delete_confirmed(trash_slugs, True)
                    await pilot.pause()

                    self.assertEqual(app._trash_id_by_slug, {})
                    audit_text = (Path(tmp) / "demo-project" / "audit_events.jsonl").read_text(encoding="utf-8")
                    self.assertGreaterEqual(audit_text.count("document.permanently_deleted"), 2)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_project_browser_folder_delete_moves_descendants_to_mirrored_trash_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Memos")
                    await app._create_project_document("Memos")
                    await pilot.pause()
                    created = {
                        slug: document_id
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    }
                    self.assertEqual(len(created), 2)
                    for slug, document_id in tuple(created.items()):
                        app._update_project_item(slug, Path(document_id).name, "scratch/round_1")
                    await pilot.pause()

                    tree = app.query_one(ProjectBrowserTree)
                    folder_node = tree._folder_nodes[("Memos", "scratch")]
                    tree.move_cursor(folder_node, animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()

                    self.assertIsInstance(app.screen, DeleteFolderConfirmModal)
                    app.screen.dismiss(True)
                    await pilot.pause()

                    self.assertTrue(all(slug not in app._document_id_by_slug for slug in created))
                    self.assertEqual(len(app._trash_id_by_slug), 2)
                    self.assertNotIn(("Memos", "scratch"), tree._folder_nodes)
                    self.assertIn(("Trash", "Memos"), tree._folder_nodes)
                    self.assertIn(("Trash", "Memos/scratch"), tree._folder_nodes)
                    self.assertIn(("Trash", "Memos/scratch/round_1"), tree._folder_nodes)
                    for metadata in app._trash_metadata_by_slug.values():
                        self.assertIn("memos/scratch/round_1/", str(metadata.get("original_id") or ""))
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_project_browser_empty_folder_delete_removes_folder_after_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    app._handle_new_folder_result("Memos", "empty_scratch")
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    empty_folder = project_root / "memos" / "empty_scratch"
                    self.assertTrue(empty_folder.is_dir())
                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._folder_nodes[("Memos", "empty_scratch")], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()

                    self.assertIsInstance(app.screen, DeleteFolderConfirmModal)
                    app.screen.dismiss(True)
                    await pilot.pause()

                    self.assertFalse(empty_folder.exists())
                    self.assertNotIn(("Memos", "empty_scratch"), tree._folder_nodes)
                    self.assertEqual(app._trash_id_by_slug, {})
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_trash_folder_selection_restores_all_descendants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Memos")
                    await app._create_project_document("Memos")
                    await pilot.pause()
                    created = {
                        slug: document_id
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    }
                    for slug, document_id in tuple(created.items()):
                        app._update_project_item(slug, Path(document_id).name, "scratch/round_1")
                    await pilot.pause()
                    moved_ids = {
                        slug: document_id
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug in created
                    }

                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._folder_nodes[("Memos", "scratch")], animate=False)
                    app._handle_folder_delete_confirmation(
                        "scratch",
                        "Memos",
                        "scratch",
                        tuple(tree.descendant_entry_infos(tree._folder_nodes[("Memos", "scratch")], kinds={"entry"})),
                        True,
                    )
                    await pilot.pause()
                    self.assertEqual(len(app._trash_id_by_slug), 2)

                    tree.move_cursor(tree._folder_nodes[("Trash", "Memos/scratch")], animate=False)
                    app.action_restore_selected_trash_item()
                    await pilot.pause()

                    self.assertEqual(app._trash_id_by_slug, {})
                    restored_ids = set(app._document_id_by_slug.values())
                    self.assertTrue(set(moved_ids.values()).issubset(restored_ids))
                    self.assertNotIn(("Trash", "Memos"), tree._folder_nodes)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_trash_selection_shows_full_file_details_in_inspector(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Memos")
                    await pilot.pause()
                    [(slug, _document_id)] = [
                        (slug, document_id)
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    ]

                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._entry_nodes[slug], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()
                    [(trash_slug, _trash_id)] = list(app._trash_id_by_slug.items())

                    tree.move_cursor(tree._entry_nodes[trash_slug], animate=False)
                    tree.focus()
                    await pilot.press("enter")
                    await pilot.pause()

                    self.assertEqual(app.query_one(DocumentPane).active_document.slug, trash_slug)
                    markdown = app.query_one(f"#{INSPECTOR_MARKDOWN_ID}").source
                    self.assertIn("Document type: **Memo**", markdown)
                    self.assertNotIn("Document Type:", markdown)
                    self.assertIn("Words:", markdown)
                    self.assertIn("Tokens:", markdown)
                    self.assertIn("is in the project trash. Double-select to restore or permanently delete it.", markdown)
                    self.assertIn("- Original location: memos/", markdown)
                    self.assertIn("- Deleted at:", markdown)
                    self.assertNotIn("- Deleted at: Unknown", markdown)
                    self.assertNotIn("- Double-select to restore", markdown)
                    excerpt = str(app.query_one(f"#{INSPECTOR_EXCERPT_TEXT_ID}", Static).render())
                    self.assertNotIn("Original location:", excerpt)
                    self.assertNotIn("Deleted at:", excerpt)
                    self.assertIn("This is a new memo document.", excerpt)
                    self.assertTrue(app.query_one(f"#{INSPECTOR_SUMMARY_ACTIONS_ID}").display)
                    self.assertFalse(app.query_one(f"#{INSPECTOR_SAVE_SHORT_SUMMARY_ID}").disabled)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_normal_document_inspector_hides_explanatory_summary_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    app._show_document_subject(DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG])
                    await pilot.pause()
                    markdown = app.query_one(f"#{INSPECTOR_MARKDOWN_ID}").source
                    self.assertIn("## [current\\_draft\\.md](exegesis://document/current-draft)", markdown)
                    self.assertIn("Document type: **Draft**", markdown)
                    self.assertNotIn("Document Type:", markdown)
                    self.assertIn("Words:", markdown)
                    self.assertIn("Tokens:", markdown)
                    self.assertNotIn("The primary manuscript for the project and the default writing tab.", markdown)
                    self.assertNotIn("Location:", markdown)

                    await app._create_project_document("Memos")
                    await pilot.pause()
                    active = app.query_one(DocumentPane).active_document
                    app._show_document_subject(active)
                    await pilot.pause()
                    markdown = app.query_one(f"#{INSPECTOR_MARKDOWN_ID}").source
                    self.assertIn("](", markdown.splitlines()[0])
                    self.assertIn("Document type: **Memo**", markdown)
                    self.assertNotIn("Document Type:", markdown)
                    self.assertNotIn("in memos.", markdown)
                    self.assertNotIn("Category:", markdown)
                    self.assertNotIn("Location:", markdown)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    def test_inspector_markdown_escapes_filename_titles(self) -> None:
        markdown = render_inspector_markdown(
            "Data Memo 1.md",
            "",
            (),
            selection_type="memo",
            word_count=38,
            token_count=60,
        )

        self.assertTrue(markdown.startswith("## Data Memo 1\\.md"))
        self.assertNotIn("[Data Memo 1]", markdown)
        self.assertNotIn("](1.md)", markdown)

    async def test_trash_shortcut_actions_restore_and_permanently_delete_selected_item(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Drafts")
                    await pilot.pause()
                    [(slug, document_id)] = [
                        (slug, document_id)
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    ]
                    backing_path = Path(tmp) / "demo-project" / document_id

                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._entry_nodes[slug], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()
                    [(trash_slug, _trash_id)] = list(app._trash_id_by_slug.items())

                    tree.move_cursor(tree._entry_nodes[trash_slug], animate=False)
                    app.action_restore_selected_trash_item()
                    await pilot.pause()

                    self.assertTrue(backing_path.exists())
                    self.assertNotIn(trash_slug, app._trash_id_by_slug)
                    restored_slug = next(
                        restored_slug
                        for restored_slug, restored_document_id in app._document_id_by_slug.items()
                        if restored_document_id == document_id
                    )

                    tree.move_cursor(tree._entry_nodes[restored_slug], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()
                    [(trash_slug, _trash_id)] = list(app._trash_id_by_slug.items())

                    tree.move_cursor(tree._entry_nodes[trash_slug], animate=False)
                    app.action_permanently_delete_selected_trash_item()
                    await pilot.pause()

                    self.assertIsInstance(app.screen, PermanentDeleteTrashConfirmModal)
                    app._handle_permanent_delete_confirmed((trash_slug,), True)
                    await pilot.pause()

                    self.assertFalse(backing_path.exists())
                    self.assertNotIn(trash_slug, app._trash_id_by_slug)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_project_browser_trash_selection_splits_delete_action_into_delete_and_restore(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Drafts")
                    await pilot.pause()
                    [(slug, document_id)] = [
                        (slug, document_id)
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    ]

                    tree = app.query_one(ProjectBrowserTree)
                    project_pane = app.query_one(ProjectPane)
                    self.assertTrue(project_pane.query_one(f"#{PROJECT_DELETE_ID}", Button).display)
                    self.assertFalse(project_pane.query_one(f"#{PROJECT_TRASH_DELETE_ID}", Button).display)
                    self.assertFalse(project_pane.query_one(f"#{PROJECT_TRASH_RESTORE_ID}", Button).display)

                    tree.move_cursor(tree._entry_nodes[slug], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()
                    [(trash_slug, _trash_id)] = list(app._trash_id_by_slug.items())

                    trash_info = tree._entry_nodes[trash_slug].data
                    app._sync_project_context_actions(trash_info)
                    await pilot.pause()
                    self.assertFalse(project_pane.query_one(f"#{PROJECT_DELETE_ID}", Button).display)
                    self.assertTrue(project_pane.query_one(f"#{PROJECT_TRASH_DELETE_ID}", Button).display)
                    self.assertTrue(project_pane.query_one(f"#{PROJECT_TRASH_RESTORE_ID}", Button).display)

                    tree.move_cursor(tree._entry_nodes[trash_slug], animate=False)
                    project_pane.query_one(f"#{PROJECT_TRASH_RESTORE_ID}", Button).press()
                    await pilot.pause()
                    self.assertNotIn(trash_slug, app._trash_id_by_slug)
                    restored_slug = next(
                        restored_slug
                        for restored_slug, restored_document_id in app._document_id_by_slug.items()
                        if restored_document_id == document_id
                    )

                    tree.move_cursor(tree._entry_nodes[restored_slug], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()
                    [(trash_slug, _trash_id)] = list(app._trash_id_by_slug.items())
                    trash_info = tree._entry_nodes[trash_slug].data
                    app._sync_project_context_actions(trash_info)
                    tree.move_cursor(tree._entry_nodes[trash_slug], animate=False)
                    project_pane.query_one(f"#{PROJECT_TRASH_DELETE_ID}", Button).press()
                    await pilot.pause()

                    self.assertIsInstance(app.screen, PermanentDeleteTrashConfirmModal)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_shell_saves_real_project_document_edits_on_explicit_save(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    await app._create_project_document("Drafts")
                    await pilot.pause()

                    [(slug, document_id)] = [
                        (slug, document_id)
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    ]
                    backing_path = Path(tmp) / "demo-project" / document_id
                    editor = app.query_one(f"#document-editor-{slug}")
                    original = backing_path.read_text(encoding="utf-8")
                    self.assertFalse(app.query_one(f"#{TOP_SAVE_DOCUMENT_ID}", Button).disabled)
                    self.assertTrue(app.query_one(f"#{DOCUMENT_SAVE_BUTTON_ID}", Button).disabled)

                    editor.text = "# Saved\n\nThis should hit disk only after save.\n"
                    await pilot.pause()

                    self.assertEqual(backing_path.read_text(encoding="utf-8"), original)
                    self.assertFalse(app.query_one(f"#{TOP_SAVE_DOCUMENT_ID}", Button).disabled)
                    self.assertFalse(app.query_one(f"#{DOCUMENT_SAVE_BUTTON_ID}", Button).disabled)

                    app.action_save_current_document()
                    await pilot.pause()

                    self.assertEqual(backing_path.read_text(encoding="utf-8"), "# Saved\n\nThis should hit disk only after save.\n")
                    self.assertFalse(app.query_one(f"#{TOP_SAVE_DOCUMENT_ID}", Button).disabled)
                    self.assertTrue(app.query_one(f"#{DOCUMENT_SAVE_BUTTON_ID}", Button).disabled)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_shell_saves_document_edits_when_focus_leaves_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    backing_path = Path(tmp) / "demo-project" / "drafts/current_draft.md"
                    editor = app.query_one("#document-editor-current-draft")
                    editor.text = "# Focus Save\n\nThis should save when leaving the document pane.\n"
                    await pilot.pause()

                    self.assertNotEqual(backing_path.read_text(encoding="utf-8"), editor.text)
                    app.action_focus_project()
                    await pilot.pause()

                    self.assertEqual(backing_path.read_text(encoding="utf-8"), editor.text)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_shell_can_create_each_project_document_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    expected_categories = ("Drafts", "Memos", "Summaries", "Transcripts", "Literature")
                    before_create = set(app._document_id_by_slug)
                    for category in expected_categories:
                        await app._create_project_document(category)
                        await pilot.pause()

                    created_ids = [
                        document_id
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    ]
                    self.assertEqual(len(created_ids), len(expected_categories))
                    project_root = Path(tmp) / "demo-project"
                    for document_id in created_ids:
                        self.assertTrue((project_root / document_id).exists(), document_id)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_create_document_keyboard_shortcuts_create_real_documents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    before_create = set(app._document_id_by_slug)
                    for key in ("ctrl+shift+d", "ctrl+shift+m", "ctrl+shift+s", "ctrl+shift+t", "ctrl+shift+l"):
                        await pilot.press(key)
                        await pilot.pause()

                    created_ids = {
                        document_id
                        for slug, document_id in app._document_id_by_slug.items()
                        if slug not in before_create
                    }
                    self.assertEqual(len(created_ids), 5)
                    self.assertTrue(any(document_id.startswith("drafts/") for document_id in created_ids))
                    self.assertTrue(any(document_id.startswith("memos/") for document_id in created_ids))
                    self.assertTrue(any(document_id.startswith("summaries/") for document_id in created_ids))
                    self.assertTrue(any(document_id.startswith("transcripts/") for document_id in created_ids))
                    self.assertTrue(any(document_id.startswith("literature/") for document_id in created_ids))
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_default_fixture_documents_are_seeded_as_real_project_documents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    expected = {
                        "current-draft": "drafts/current_draft.md",
                        "project-demo-essay": "memos/fieldwork/round_1/data_memo_1.md",
                        "project-root-memo": "memos/root_memo_example.md",
                        "project-longform-essay": "summaries/summary_1.md",
                        "project-notebook": (
                            "transcripts/interviews/2026/participant_1/"
                            "transcript_1_participant_1_5_1_26.md"
                        ),
                        "project-root-transcript": "transcripts/transcript_root_example.md",
                        "project-lit-review": "literature/literature_reviews/leadership/article_1_last_first_title.md",
                        "project-root-literature": "literature/article_root_example.md",
                    }
                    self.assertEqual({slug: app._document_id_by_slug[slug] for slug in expected}, expected)
                    self.assertTrue(all((project_root / document_id).exists() for document_id in expected.values()))
                    project_tree = app.query_one("#project-browser")
                    folder_keys = set(project_tree._folder_nodes)
                    self.assertIn(("Memos", "fieldwork"), folder_keys)
                    self.assertIn(("Memos", "fieldwork/round_1"), folder_keys)
                    self.assertIn(("Transcripts", "interviews/2026/participant_1"), folder_keys)
                    self.assertIn(("Literature", "literature_reviews/leadership"), folder_keys)

                    editor = app.query_one("#document-editor-current-draft")
                    editor.text = "# Seeded Draft\n\nAutosaved from the original fixture.\n"
                    await pilot.pause()
                    app.action_save_current_document()
                    await pilot.pause()

                    self.assertEqual(
                        (project_root / "drafts/current_draft.md").read_text(encoding="utf-8"),
                        "# Seeded Draft\n\nAutosaved from the original fixture.\n",
                    )
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_default_project_reset_helper_reseeds_server_start_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                project_root = Path(tmp) / "demo-project"
                generated_summary = project_root / "summaries/current_draft_short_summary_99.md"
                generated_draft = project_root / "drafts/working_draft_99.md"
                stale_retrieval_blob = project_root / ".retrieval/doc_blobs/summaries/current_draft_short_summary_99.md.enc"
                generated_summary.parent.mkdir(parents=True, exist_ok=True)
                generated_draft.parent.mkdir(parents=True, exist_ok=True)
                stale_retrieval_blob.parent.mkdir(parents=True, exist_ok=True)
                generated_summary.write_text("# Generated summary clutter\n", encoding="utf-8")
                generated_draft.write_text("# Generated draft clutter\n", encoding="utf-8")
                stale_retrieval_blob.write_text("stale encrypted blob", encoding="utf-8")

                reset_default_demo_project()
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    self.assertFalse(generated_summary.exists())
                    self.assertFalse(generated_draft.exists())
                    self.assertFalse(stale_retrieval_blob.exists())
                    self.assertNotIn("summaries/current_draft_short_summary_99.md", set(app._document_id_by_slug.values()))
                    self.assertNotIn("drafts/working_draft_99.md", set(app._document_id_by_slug.values()))
                    self.assertEqual(app._document_id_by_slug["project-longform-essay"], "summaries/summary_1.md")
                    self.assertTrue((project_root / "summaries/summary_1.md").exists())
                    self.assertTrue((project_root / ".retrieval/retrieval_v1.key").exists())
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_new_project_creates_minimal_current_draft_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    app._handle_new_project_result("Methodology Notes")
                    await pilot.pause()

                    project_root = Path(tmp) / "methodology-notes"
                    self.assertEqual(app._current_project_name, "Methodology Notes")
                    self.assertEqual(app._document_id_by_slug, {"current-draft": "drafts/current_draft.md"})
                    self.assertTrue((project_root / "drafts" / "current_draft.md").exists())
                    self.assertFalse((project_root / DEMO_MEMO_DOCUMENT_ID).exists())
                    self.assertIn("Welcome to your Exegesis project", (project_root / "drafts" / "current_draft.md").read_text(encoding="utf-8"))
                    manifest = project_root / ".exegesis" / "project.json"
                    self.assertIn('"name": "Methodology Notes"', manifest.read_text(encoding="utf-8"))
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_new_project_clears_prior_document_tabs_and_basket(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()
                    document_pane = app.query_one(DocumentPane)
                    basket_pane = app.query_one(BasketPane)

                    await document_pane.open_document("project-demo-essay", focus=False)
                    app._add_document_slug_to_basket("project-demo-essay")
                    await pilot.pause()

                    self.assertIn("project-demo-essay", document_pane._open_tabs)
                    self.assertTrue(basket_pane.entries)
                    self.assertTrue(app._engine_adapter.state.basket.items)

                    app._handle_new_project_result("Fresh Project")
                    for _ in range(4):
                        await pilot.pause()

                    self.assertEqual(document_pane._open_tabs, [CURRENT_DRAFT_SLUG])
                    self.assertEqual(document_pane.active_document.slug, CURRENT_DRAFT_SLUG)
                    self.assertEqual(basket_pane.entries, {})
                    self.assertEqual(app._engine_adapter.state.basket.items, [])
                    self.assertIn(
                        "Welcome to your Exegesis project",
                        DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content,
                    )
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_empty_default_projects_directory_creates_demo_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
            try:
                with patch("exegesis_textual.layout.shell.textual_projects_dir", return_value=Path(tmp)):
                    app = ShellWorkflowTestApp(FakeBackend(configured=True))
                    async with app.run_test() as pilot:
                        await pilot.pause()

                        project_root = Path(tmp) / "demo-project"
                        self.assertEqual(app._current_project_name, "Demo Project")
                        self.assertEqual(app._project_root, project_root)
                        self.assertIn("current-draft", app._document_id_by_slug)
                        self.assertTrue((project_root / "drafts" / "current_draft.md").exists())
                        self.assertTrue((project_root / DEMO_MEMO_DOCUMENT_ID).exists())
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_active_project_rename_moves_folder_and_updates_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    app._handle_new_project_result("Field Project")
                    await pilot.pause()
                    old_root = Path(tmp) / "field-project"
                    self.assertTrue(old_root.exists())

                    app._handle_active_project_rename_result("Renamed Field Project")
                    await pilot.pause()

                    new_root = Path(tmp) / "renamed-field-project"
                    self.assertFalse(old_root.exists())
                    self.assertTrue(new_root.exists())
                    self.assertEqual(app._current_project_name, "Renamed Field Project")
                    self.assertEqual(app._project_root, new_root)
                    self.assertIn('"name": "Renamed Field Project"', (new_root / ".exegesis" / "project.json").read_text(encoding="utf-8"))
                    self.assertEqual(app.query_one(ProjectPane)._project_name, "Renamed Field Project")
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_startup_loads_last_opened_project_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
            previous_dev = os.environ.get("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER")
            os.environ.pop("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER", None)
            projects_root = Path(tmp) / "projects"
            settings_path = Path(tmp) / "settings.json"
            try:
                for name, slug in (("Field Project", "field-project"), ("Archive Project", "archive-project")):
                    manifest = projects_root / slug / ".exegesis" / "project.json"
                    manifest.parent.mkdir(parents=True, exist_ok=True)
                    manifest.write_text(json.dumps({"name": name, "slug": slug}), encoding="utf-8")
                settings_path.write_text(json.dumps({"last_project_name": "Archive Project"}), encoding="utf-8")

                with (
                    patch("exegesis_textual.layout.shell.textual_projects_dir", return_value=projects_root),
                    patch("exegesis_textual.services.projects.textual_settings_path", return_value=settings_path),
                ):
                    app = ShellWorkflowTestApp(FakeBackend(configured=True))
                    async with app.run_test() as pilot:
                        await pilot.pause()

                        self.assertEqual(app._current_project_name, "Archive Project")
                        self.assertEqual(app._project_root, projects_root / "archive-project")
                        self.assertTrue((projects_root / "archive-project" / "drafts" / "current_draft.md").exists())
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous
                if previous_dev is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_LOCAL_DEVELOPER"] = previous_dev

    async def test_local_developer_startup_ignores_last_project_and_opens_demo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            previous_dev = os.environ.get("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER")
            os.environ["EXEGESIS_TEXTUAL_LOCAL_DEVELOPER"] = "1"
            os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
            projects_root = Path(tmp) / "projects"
            settings_path = Path(tmp) / "settings.json"
            try:
                manifest = projects_root / "field-project" / ".exegesis" / "project.json"
                manifest.parent.mkdir(parents=True, exist_ok=True)
                manifest.write_text(json.dumps({"name": "Field Project", "slug": "field-project"}), encoding="utf-8")
                settings_path.write_text(json.dumps({"last_project_name": "Field Project"}), encoding="utf-8")

                with (
                    patch("exegesis_textual.layout.shell.textual_projects_dir", return_value=projects_root),
                    patch("exegesis_textual.services.projects.textual_settings_path", return_value=settings_path),
                ):
                    app = ShellWorkflowTestApp(FakeBackend(configured=True))
                    async with app.run_test() as pilot:
                        await pilot.pause()

                        self.assertEqual(app._current_project_name, "Demo Project")
                        self.assertEqual(app._project_root, projects_root / "demo-project")
                        self.assertIn("Demo Project", app._project_names)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous
                if previous_dev is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_LOCAL_DEVELOPER"] = previous_dev

    async def test_non_developer_blank_start_prompts_for_named_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous_projects = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            previous_dev = os.environ.get("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER")
            os.environ.pop("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER", None)
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()
                    await pilot.pause()

                    self.assertEqual(app.screen.query_one("#project-name-input", Input).placeholder, "Project name")
                    self.assertFalse((Path(tmp) / "demo-project").exists())
            finally:
                if previous_projects is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous_projects
                if previous_dev is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_LOCAL_DEVELOPER"] = previous_dev

    async def test_non_developer_blank_start_prompts_model_settings_before_first_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous_projects = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            previous_dev = os.environ.get("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER")
            previous_settings = os.environ.get(TEXTUAL_SETTINGS_PATH_ENV)
            os.environ.pop("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER", None)
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = str(Path(tmp) / "projects")
            os.environ[TEXTUAL_SETTINGS_PATH_ENV] = str(Path(tmp) / "settings.json")
            try:
                backend = MistralChatBackend(credential_store=InMemoryCredentialStore())
                app = ShellWorkflowTestApp(backend)
                async with app.run_test() as pilot:
                    await pilot.pause()
                    await pilot.pause()

                    self.assertIsInstance(app.screen, ModelSettingsModal)
                    app.screen.dismiss(("skip", MistralModelSettings(settings_prompt_dismissed=True), ""))
                    await pilot.pause()
                    await pilot.pause()

                    self.assertIsInstance(app.screen, NewProjectModal)
                    app.screen.dismiss("First Field Project")
                    await pilot.pause()

                    self.assertEqual(app._current_project_name, "First Field Project")
                    self.assertTrue((Path(tmp) / "projects" / "first-field-project").exists())
                    self.assertFalse((Path(tmp) / "projects" / "untitled-project").exists())
            finally:
                if previous_projects is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous_projects
                if previous_dev is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_LOCAL_DEVELOPER"] = previous_dev
                if previous_settings is None:
                    os.environ.pop(TEXTUAL_SETTINGS_PATH_ENV, None)
                else:
                    os.environ[TEXTUAL_SETTINGS_PATH_ENV] = previous_settings

    async def test_open_project_uses_known_projects_from_project_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    app._handle_new_project_result("Field Project")
                    await pilot.pause()
                    app._handle_new_project_result("Archive Project")
                    await pilot.pause()
                    app._handle_open_project_result("Field Project")
                    await pilot.pause()

                    self.assertEqual(app._current_project_name, "Field Project")
                    self.assertEqual(app._project_root, Path(tmp) / "field-project")
                    self.assertIn("Field Project", app._project_names)
                    self.assertIn("Archive Project", app._project_names)

                    app._handle_open_project_result("/tmp/not-an-exegesis-project")
                    await pilot.pause()

                    self.assertEqual(app._current_project_name, "Field Project")
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_project_browser_lists_seeded_demo_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    app._ensure_demo_project_available()
                    app._refresh_project_names()

                    self.assertEqual(app._project_names, ["Demo Project"])
                    self.assertTrue((Path(tmp) / "demo-project" / "drafts" / "current_draft.md").exists())
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_project_browser_delete_removes_selected_project_and_keeps_others(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    app._handle_new_project_result("Field Project")
                    await pilot.pause()
                    app._handle_new_project_result("Archive Project")
                    await pilot.pause()
                    app._handle_open_project_result(("open", "Field Project"))
                    await pilot.pause()

                    app._handle_open_project_result(("delete", "Archive Project"))
                    await pilot.pause()

                    self.assertTrue((Path(tmp) / "archive-project").exists())
                    self.assertIsInstance(app.screen, DeleteProjectConfirmModal)

                    app.screen.dismiss(True)
                    await pilot.pause()

                    self.assertEqual(app._current_project_name, "Field Project")
                    self.assertTrue((Path(tmp) / "field-project").exists())
                    self.assertFalse((Path(tmp) / "archive-project").exists())
                    self.assertIn("Field Project", app._project_names)
                    self.assertNotIn("Archive Project", app._project_names)
                    self.assertIsInstance(app.screen, OpenProjectModal)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_project_browser_delete_current_project_opens_next_available_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    app._handle_new_project_result("Field Project")
                    await pilot.pause()
                    app._handle_new_project_result("Archive Project")
                    await pilot.pause()

                    app._handle_open_project_result(("delete", "Archive Project"))
                    await pilot.pause()

                    self.assertTrue((Path(tmp) / "archive-project").exists())
                    self.assertIsInstance(app.screen, DeleteProjectConfirmModal)

                    app.screen.dismiss(True)
                    await pilot.pause()

                    self.assertFalse((Path(tmp) / "archive-project").exists())
                    self.assertEqual(app._current_project_name, "Demo Project")
                    self.assertEqual(app._project_root, Path(tmp) / "demo-project")
                    self.assertIsInstance(app.screen, OpenProjectModal)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_project_browser_delete_cancel_keeps_project_and_reopens_browser(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    app._handle_new_project_result("Field Project")
                    await pilot.pause()
                    app._handle_new_project_result("Archive Project")
                    await pilot.pause()

                    app._handle_open_project_result(("delete", "archive-project"))
                    await pilot.pause()

                    self.assertIsInstance(app.screen, DeleteProjectConfirmModal)
                    app.screen.dismiss(False)
                    await pilot.pause()

                    self.assertTrue((Path(tmp) / "archive-project").exists())
                    self.assertIn("Archive Project", app._project_names)
                    self.assertEqual(app._current_project_name, "Archive Project")
                    self.assertIsInstance(app.screen, OpenProjectModal)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_project_browser_delete_only_project_opens_new_project_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous_projects = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            previous_dev = os.environ.get("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            os.environ.pop("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER", None)
            try:
                manifest = Path(tmp) / "solo-project" / ".exegesis" / "project.json"
                manifest.parent.mkdir(parents=True, exist_ok=True)
                manifest.write_text(json.dumps({"name": "Solo Project", "slug": "solo-project"}), encoding="utf-8")

                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    self.assertEqual(app._current_project_name, "Solo Project")
                    app._handle_open_project_result(("delete", "solo-project"))
                    await pilot.pause()

                    self.assertIsInstance(app.screen, DeleteProjectConfirmModal)
                    app.screen.dismiss(True)
                    await pilot.pause()

                    self.assertFalse((Path(tmp) / "solo-project").exists())
                    self.assertEqual(app._project_records, [])
                    self.assertEqual(app._current_project_name, "Untitled Project")
                    self.assertIsInstance(app.screen, NewProjectModal)
            finally:
                if previous_projects is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous_projects
                if previous_dev is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_LOCAL_DEVELOPER"] = previous_dev

    async def test_duplicate_project_names_keep_display_name_with_numbered_folders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    app._handle_new_project_result("Field Project")
                    await pilot.pause()
                    self.assertEqual(app._current_project_name, "Field Project")
                    self.assertEqual(app._project_root, Path(tmp) / "field-project")

                    app._handle_new_project_result("Field Project")
                    await pilot.pause()
                    self.assertEqual(app._current_project_name, "Field Project")
                    self.assertEqual(app._project_root, Path(tmp) / "field-project-2")
                    self.assertIn('"name": "Field Project"', (Path(tmp) / "field-project-2" / ".exegesis" / "project.json").read_text(encoding="utf-8"))

                    app._handle_open_project_result(("open", "field-project"))
                    await pilot.pause()
                    self.assertEqual(app._project_root, Path(tmp) / "field-project")

                    app._handle_open_project_result(("open", "field-project-2"))
                    await pilot.pause()
                    self.assertEqual(app._current_project_name, "Field Project")
                    self.assertEqual(app._project_root, Path(tmp) / "field-project-2")
                    self.assertIn("Field Project", app._project_names)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_project_title_enter_opens_rename_modal(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()

            project_header = app.query_one("#project-header", Static)
            project_header.focus()
            await pilot.press("enter")
            await pilot.pause()

            self.assertIsInstance(app.screen, RenameActiveProjectModal)

    async def test_active_project_rename_duplicate_can_replace_existing_project_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    app._handle_new_project_result("Field Project")
                    await pilot.pause()
                    app._handle_new_project_result("Archive Project")
                    await pilot.pause()
                    app._handle_open_project_result(("open", "field-project"))
                    await pilot.pause()

                    app._handle_active_project_rename_result("Archive Project")
                    await pilot.pause()

                    self.assertIsInstance(app.screen, DuplicateProjectModal)
                    self.assertEqual(
                        app.screen.query_one(f"#{PROJECT_DUPLICATE_RENAME_INPUT_ID}", Input).value,
                        "Archive Project",
                    )
                    app.screen.dismiss(("replace", None))
                    await pilot.pause()

                    self.assertFalse((Path(tmp) / "field-project").exists())
                    self.assertTrue((Path(tmp) / "archive-project" / "drafts" / "current_draft.md").exists())
                    self.assertEqual(app._current_project_name, "Archive Project")
                    self.assertEqual(app._project_root, Path(tmp) / "archive-project")
                    self.assertIn(
                        '"name": "Archive Project"',
                        (Path(tmp) / "archive-project" / ".exegesis" / "project.json").read_text(encoding="utf-8"),
                    )
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_active_project_rename_duplicate_can_choose_new_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    app._handle_new_project_result("Field Project")
                    await pilot.pause()
                    app._handle_new_project_result("Archive Project")
                    await pilot.pause()
                    app._handle_open_project_result(("open", "field-project"))
                    await pilot.pause()

                    app._handle_active_project_rename_result("Archive Project")
                    await pilot.pause()

                    self.assertIsInstance(app.screen, DuplicateProjectModal)
                    app.screen.dismiss(("rename", "Field Notes"))
                    await pilot.pause()

                    self.assertFalse((Path(tmp) / "field-project").exists())
                    self.assertTrue((Path(tmp) / "field-notes").exists())
                    self.assertTrue((Path(tmp) / "archive-project").exists())
                    self.assertEqual(app._current_project_name, "Field Notes")
                    self.assertEqual(app._project_root, Path(tmp) / "field-notes")
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_browser_refresh_preserves_project_edits_without_demo_reset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                first_app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with first_app.run_test() as pilot:
                    await pilot.pause()
                    editor = first_app.query_one("#document-editor-current-draft")
                    editor.text = "# Browser Refresh Check\n\nManual testing note: autosave is working.\n"
                    await pilot.pause()
                    first_app.action_save_current_document()
                    await pilot.pause()

                second_app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with second_app.run_test() as pilot:
                    await pilot.pause()
                    document = second_app.query_one(DocumentPane).active_document
                    self.assertIn("Manual testing note: autosave is working.", document.content)
                    self.assertIn("Manual testing note: autosave is working.", second_app.shell_chat_context()["document_content"])
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_default_fixture_seed_source_survives_project_permanent_delete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            preserved_fixture = DOCUMENT_FIXTURES.get("project-demo-essay")
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    backing_path = project_root / DEMO_MEMO_DOCUMENT_ID
                    backing_path.unlink()
                    DOCUMENT_FIXTURES.pop("project-demo-essay", None)
                    app._document_id_by_slug.pop("project-demo-essay", None)

                    app._ensure_default_project_documents()
                    app._map_default_project_documents()

                    self.assertTrue(backing_path.exists())
                    self.assertIn("project-demo-essay", DOCUMENT_FIXTURES)
                    self.assertEqual(app._document_id_by_slug["project-demo-essay"], DEMO_MEMO_DOCUMENT_ID)
            finally:
                if preserved_fixture is not None:
                    DOCUMENT_FIXTURES["project-demo-essay"] = preserved_fixture
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_plain_import_creates_real_project_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    source = Path(tmp) / "new_import.md"
                    source.write_text("# New Import\n\nUnique import content.\n", encoding="utf-8")

                    await app._import_project_document(source, category="Literature")
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    imported_path = project_root / "literature/new_import.md"
                    self.assertEqual(imported_path.read_text(encoding="utf-8"), "# New Import\n\nUnique import content.\n")
                    self.assertIn(
                        "literature/new_import.md",
                        set(app._document_id_by_slug.values()),
                    )
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_import_without_category_defaults_to_memos_even_when_trash_selected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._section_nodes["Trash"], animate=False)
                    self.assertEqual(app._selected_project_category(), DEFAULT_IMPORT_CATEGORY)

                    source = Path(tmp) / "trash_selected_import.md"
                    source.write_text("# Trash Selected Import\n", encoding="utf-8")
                    await app._import_project_document(source)
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    self.assertEqual(
                        (project_root / "memos/trash_selected_import.md").read_text(encoding="utf-8"),
                        "# Trash Selected Import\n",
                    )
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_import_handler_uses_dropdown_category_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._section_nodes["Trash"], animate=False)

                    source = Path(tmp) / "dropdown_literature_import.md"
                    source.write_text("# Dropdown Literature Import\n", encoding="utf-8")
                    app._handle_import_result((str(source), "Literature"))
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    self.assertEqual(
                        (project_root / "literature/dropdown_literature_import.md").read_text(encoding="utf-8"),
                        "# Dropdown Literature Import\n",
                    )
                    self.assertFalse((project_root / "memos/dropdown_literature_import.md").exists())
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_duplicate_import_can_replace_or_rename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    source = Path(tmp) / "data_memo_1.md"
                    source.write_text("# Replacement\n", encoding="utf-8")
                    original_content = (project_root / DEMO_MEMO_DOCUMENT_ID).read_text(encoding="utf-8")

                    await app._import_project_document(source, category="Memos", destination_folder=DEMO_MEMO_FOLDER)
                    await pilot.pause()
                    self.assertEqual((project_root / DEMO_MEMO_DOCUMENT_ID).read_text(encoding="utf-8"), original_content)

                    await app._import_project_document(source, category="Memos", destination_folder=DEMO_MEMO_FOLDER, duplicate_action="replace")
                    await pilot.pause()
                    self.assertEqual((project_root / DEMO_MEMO_DOCUMENT_ID).read_text(encoding="utf-8"), "# Replacement\n")

                    await app._import_project_document(
                        source,
                        category="Memos",
                        destination_folder=DEMO_MEMO_FOLDER,
                        duplicate_action="rename",
                        duplicate_title="renamed_data_memo.md",
                    )
                    await pilot.pause()
                    self.assertEqual((project_root / "memos" / DEMO_MEMO_FOLDER / "renamed_data_memo.md").read_text(encoding="utf-8"), "# Replacement\n")
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_batch_import_can_import_multiple_markdown_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    first = Path(tmp) / "batch_one.md"
                    second = Path(tmp) / "batch_two.md"
                    first.write_text("# Batch One\n", encoding="utf-8")
                    second.write_text("# Batch Two\n", encoding="utf-8")

                    await app._import_project_documents([first, second], category="Literature")
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    self.assertEqual((project_root / "literature/batch_one.md").read_text(encoding="utf-8"), "# Batch One\n")
                    self.assertEqual((project_root / "literature/batch_two.md").read_text(encoding="utf-8"), "# Batch Two\n")
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_imports_allow_same_filename_in_different_project_folders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    first = Path(tmp) / "same.md"
                    second = Path(tmp) / "other" / "same.md"
                    second.parent.mkdir()
                    first.write_text("# First\n", encoding="utf-8")
                    second.write_text("# Second\n", encoding="utf-8")

                    await app._import_project_document(first, category="Memos", destination_folder="folder-a")
                    await app._import_project_document(second, category="Memos", destination_folder="folder-b")
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    self.assertEqual((project_root / "memos/folder-a/same.md").read_text(encoding="utf-8"), "# First\n")
                    self.assertEqual((project_root / "memos/folder-b/same.md").read_text(encoding="utf-8"), "# Second\n")
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_imports_allow_same_filename_in_different_categories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    memo_source = Path(tmp) / "same.md"
                    literature_source = Path(tmp) / "sources" / "same.md"
                    literature_source.parent.mkdir()
                    memo_source.write_text("# Memo Same\n", encoding="utf-8")
                    literature_source.write_text("# Literature Same\n", encoding="utf-8")

                    await app._import_project_document(memo_source, category="Memos")
                    await app._import_project_document(literature_source, category="Literature")
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    self.assertEqual((project_root / "memos/same.md").read_text(encoding="utf-8"), "# Memo Same\n")
                    self.assertEqual((project_root / "literature/same.md").read_text(encoding="utf-8"), "# Literature Same\n")
                    self.assertNotIsInstance(app.screen, DuplicateDocumentModal)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_folder_import_modes_flatten_or_preserve_source_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    source_root = Path(tmp) / "Source Pack"
                    nested = source_root / "Nested"
                    nested.mkdir(parents=True)
                    root_file = source_root / "root.md"
                    nested_file = nested / "child.md"
                    root_file.write_text("# Root\n", encoding="utf-8")
                    nested_file.write_text("# Child\n", encoding="utf-8")

                    await app._import_project_documents(
                        [root_file, nested_file],
                        category="Literature",
                        destination_folder="flat-dest",
                        mode="folder_flat",
                        source_root=source_root,
                    )
                    await app._import_project_documents(
                        [root_file, nested_file],
                        category="Literature",
                        destination_folder="tree-dest",
                        mode="folder_tree",
                        source_root=source_root,
                    )
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    self.assertTrue((project_root / "literature/flat-dest/root.md").exists())
                    self.assertTrue((project_root / "literature/flat-dest/child.md").exists())
                    self.assertTrue((project_root / "literature/tree-dest/Source Pack/root.md").exists())
                    self.assertTrue((project_root / "literature/tree-dest/Source Pack/Nested/child.md").exists())
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_update_item_move_to_duplicate_folder_opens_duplicate_dialog(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    first = Path(tmp) / "same.md"
                    second = Path(tmp) / "same-second.md"
                    first.write_text("# First\n", encoding="utf-8")
                    second.write_text("# Second\n", encoding="utf-8")
                    await app._import_project_document(first, category="Memos", destination_folder="folder-a")
                    await app._import_project_document(second, category="Memos", destination_folder="folder-b", duplicate_action="rename", duplicate_title="same.md")
                    await pilot.pause()

                    slug = app._slug_for_document_id("memos/folder-a/same.md")
                    self.assertIsNotNone(slug)
                    app._update_project_item(slug or "", "same.md", "folder-b")
                    await pilot.pause()

                    self.assertIsInstance(app.screen, DuplicateDocumentModal)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_update_item_respects_extensionless_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    source = Path(tmp) / "extension-test.md"
                    source.write_text("# Extension Test\n", encoding="utf-8")
                    await app._import_project_document(source, category="Memos")
                    await pilot.pause()

                    slug = app._slug_for_document_id("memos/extension-test.md")
                    self.assertIsNotNone(slug)
                    self.assertTrue(app._update_project_item(slug or "", "extension-test", ""))
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    self.assertTrue((project_root / "memos/extension-test").exists())
                    self.assertFalse((project_root / "memos/extension-test.md").exists())
                    self.assertEqual(app._document_id_by_slug[slug or ""], "memos/extension-test")
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_update_item_extensionless_duplicate_opens_duplicate_dialog(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    first = Path(tmp) / "same.md"
                    second = Path(tmp) / "other.md"
                    first.write_text("# First\n", encoding="utf-8")
                    second.write_text("# Second\n", encoding="utf-8")
                    await app._import_project_document(first, category="Memos", destination_folder="folder-a")
                    await app._import_project_document(second, category="Memos", destination_folder="folder-b")
                    await pilot.pause()

                    other_slug = app._slug_for_document_id("memos/folder-b/other.md")
                    self.assertIsNotNone(other_slug)
                    self.assertTrue(app._update_project_item(other_slug or "", "same", "folder-b"))
                    await pilot.pause()
                    self.assertEqual(app._document_id_by_slug[other_slug or ""], "memos/folder-b/same")

                    slug = app._slug_for_document_id("memos/folder-a/same.md")
                    self.assertIsNotNone(slug)
                    app._update_project_item(slug or "", "same", "folder-b")
                    await pilot.pause()

                    self.assertIsInstance(app.screen, DuplicateDocumentModal)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_import_modal_shift_click_selects_files_without_checkbox_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "alpha.md").write_text("# Alpha\n", encoding="utf-8")
            (root / "beta.md").write_text("# Beta\n", encoding="utf-8")
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await app.push_screen(ImportMarkdownModal(start_dir=root))
                await pilot.pause()

                option_list = app.screen.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}", OptionList)
                await pilot.click(f"#{IMPORT_BROWSER_OPTIONS_ID}", offset=(2, 2), shift=True)
                await pilot.pause()
                await pilot.click(f"#{IMPORT_BROWSER_OPTIONS_ID}", offset=(2, 3), shift=True)
                await pilot.pause()

                prompts = [str(option_list.get_option_at_index(index).prompt) for index in (1, 2)]
                self.assertEqual(prompts, ["* alpha.md", "* beta.md"])
                self.assertFalse(any("[ ]" in prompt or "[x]" in prompt for prompt in prompts))
                self.assertIsInstance(app.screen, ImportMarkdownModal)

    async def test_import_modal_shift_click_does_not_restore_deselected_ghosts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "alpha.md").write_text("# Alpha\n", encoding="utf-8")
            (root / "beta.md").write_text("# Beta\n", encoding="utf-8")
            (root / "gamma.md").write_text("# Gamma\n", encoding="utf-8")
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await app.push_screen(ImportMarkdownModal(start_dir=root))
                await pilot.pause()

                option_list = app.screen.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}", OptionList)
                await pilot.click(f"#{IMPORT_BROWSER_OPTIONS_ID}", offset=(2, 2), shift=True)
                await pilot.pause()
                await pilot.click(f"#{IMPORT_BROWSER_OPTIONS_ID}", offset=(2, 3), shift=True)
                await pilot.pause()
                await pilot.click(f"#{IMPORT_BROWSER_OPTIONS_ID}", offset=(2, 3), shift=True)
                await pilot.pause()
                await pilot.click(f"#{IMPORT_BROWSER_OPTIONS_ID}", offset=(2, 2), shift=True)
                await pilot.pause()
                await pilot.click(f"#{IMPORT_BROWSER_OPTIONS_ID}", offset=(2, 4), shift=True)
                await pilot.pause()

                prompts = [str(option_list.get_option_at_index(index).prompt) for index in (1, 2, 3)]
                self.assertEqual(prompts, ["alpha.md", "beta.md", "* gamma.md"])

    async def test_import_modal_mouse_click_imports_single_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "alpha.md").write_text("# Alpha\n", encoding="utf-8")
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await app.push_screen(ImportMarkdownModal(start_dir=root))
                await pilot.pause()

                await pilot.click(f"#{IMPORT_BROWSER_OPTIONS_ID}", offset=(2, 2))
                await pilot.pause()

                self.assertNotIsInstance(app.screen, ImportMarkdownModal)

    async def test_import_modal_mouse_click_without_option_metadata_imports_highlighted_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "alpha.md").write_text("# Alpha\n", encoding="utf-8")
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await app.push_screen(ImportMarkdownModal(start_dir=root))
                await pilot.pause()

                option_list = app.screen.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}", OptionList)
                self.assertIsNone(option_list.highlighted)
                option_list.highlighted = 1
                option = option_list.get_option_at_index(1)
                app.screen.record_option_click(option.id or "", shift=False, prior_option_id=None)
                app.screen.on_option_list_option_selected(OptionList.OptionSelected(option_list, option, 1))
                await pilot.pause()

                self.assertNotIsInstance(app.screen, ImportMarkdownModal)

    async def test_import_modal_clicking_folder_navigates_without_importing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            child = root / "child"
            child.mkdir()
            (child / "inside.md").write_text("# Inside\n", encoding="utf-8")
            (root / "alpha.md").write_text("# Alpha\n", encoding="utf-8")
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await app.push_screen(ImportMarkdownModal(start_dir=root))
                await pilot.pause()

                option_list = app.screen.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}", OptionList)
                await pilot.click(f"#{IMPORT_BROWSER_OPTIONS_ID}", offset=(2, 3))
                await pilot.pause()

                self.assertIsInstance(app.screen, ImportMarkdownModal)
                self.assertEqual(app.screen._current_dir, child)
                await pilot.pause()
                self.assertIsNone(app.screen.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}", OptionList).highlighted)

    async def test_import_modal_shift_click_after_folder_open_ignores_auto_highlight(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            child = root / "child"
            child.mkdir()
            (child / "alpha.md").write_text("# Alpha\n", encoding="utf-8")
            (child / "beta.md").write_text("# Beta\n", encoding="utf-8")
            (child / "gamma.md").write_text("# Gamma\n", encoding="utf-8")
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await app.push_screen(ImportMarkdownModal(start_dir=root))
                await pilot.pause()

                await pilot.click(f"#{IMPORT_BROWSER_OPTIONS_ID}", offset=(2, 2))
                await pilot.pause()

                option_list = app.screen.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}", OptionList)
                await pilot.click(f"#{IMPORT_BROWSER_OPTIONS_ID}", offset=(2, 4), shift=True)
                await pilot.pause()

                prompts = [str(option_list.get_option_at_index(index).prompt) for index in (1, 2, 3)]
                self.assertEqual(prompts, ["alpha.md", "beta.md", "* gamma.md"])

    async def test_import_modal_marking_file_preserves_scroll_position(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            for index in range(30):
                (root / f"file_{index:02}.md").write_text(f"# File {index}\n", encoding="utf-8")
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await app.push_screen(ImportMarkdownModal(start_dir=root))
                await pilot.pause()

                option_list = app.screen.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}", OptionList)
                option_list.highlighted = 20
                option_list.scroll_y = 12
                option = option_list.get_option_at_index(20)
                app.screen.record_option_click(option.id or "", shift=True, prior_option_id=None)
                app.screen.on_option_list_option_selected(OptionList.OptionSelected(option_list, option, 20))
                await pilot.pause()

                self.assertEqual(option_list.scroll_y, 12)
                self.assertEqual(str(option_list.get_option_at_index(20).prompt), "* file_19.md")

    async def test_batch_import_duplicate_skip_continues_remaining_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    duplicate = Path(tmp) / "data_memo_1.md"
                    unique = Path(tmp) / "batch_after_skip.md"
                    duplicate.write_text("# Duplicate Replacement\n", encoding="utf-8")
                    unique.write_text("# Batch After Skip\n", encoding="utf-8")
                    original_content = (project_root / DEMO_MEMO_DOCUMENT_ID).read_text(encoding="utf-8")

                    await app._import_project_documents(
                        [duplicate, unique],
                        category="Memos",
                        destination_folder=DEMO_MEMO_FOLDER,
                        duplicate_result=("skip", None),
                    )
                    await pilot.pause()

                    self.assertEqual((project_root / DEMO_MEMO_DOCUMENT_ID).read_text(encoding="utf-8"), original_content)
                    self.assertEqual((project_root / "memos" / DEMO_MEMO_FOLDER / "batch_after_skip.md").read_text(encoding="utf-8"), "# Batch After Skip\n")
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_batch_import_duplicate_keeps_progress_modal_open(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    duplicate = Path(tmp) / "data_memo_1.md"
                    unique = Path(tmp) / "batch_after_duplicate.md"
                    duplicate.write_text("# Duplicate Replacement\n", encoding="utf-8")
                    unique.write_text("# Batch After Duplicate\n", encoding="utf-8")
                    progress_modal = ImportProgressModal(total=2, category="Memos")
                    await app.push_screen(progress_modal)
                    await pilot.pause()

                    await app._import_project_documents([duplicate, unique], category="Memos", destination_folder=DEMO_MEMO_FOLDER, progress_modal=progress_modal)
                    await pilot.pause()

                    self.assertIsInstance(app.screen, DuplicateDocumentModal)
                    self.assertIn(progress_modal, app.screen_stack)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_bulk_import_handler_shows_progress_before_duplicate_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    duplicate = Path(tmp) / "data_memo_1.md"
                    unique = Path(tmp) / "bulk_handler_after_duplicate.md"
                    duplicate.write_text("# Duplicate Replacement\n", encoding="utf-8")
                    unique.write_text("# Bulk Handler After Duplicate\n", encoding="utf-8")
                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._folder_nodes[("Memos", DEMO_MEMO_FOLDER)], animate=False)

                    app._handle_import_result(((str(duplicate), str(unique)), "Memos"))
                    await pilot.pause()
                    await pilot.pause()

                    self.assertIsInstance(app.screen, DuplicateDocumentModal)
                    self.assertTrue(any(isinstance(screen, ImportProgressModal) for screen in app.screen_stack))
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_tuple_import_handler_uses_bulk_progress_even_for_one_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    duplicate = Path(tmp) / "data_memo_1.md"
                    duplicate.write_text("# Duplicate Replacement\n", encoding="utf-8")
                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._folder_nodes[("Memos", DEMO_MEMO_FOLDER)], animate=False)

                    app._handle_import_result(((str(duplicate),), "Memos"))
                    await pilot.pause()
                    await pilot.pause()

                    self.assertIsInstance(app.screen, DuplicateDocumentModal)
                    self.assertTrue(any(isinstance(screen, ImportProgressModal) for screen in app.screen_stack))
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_batch_import_skips_files_already_in_project_without_duplicate_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    already_imported = project_root / DEMO_MEMO_DOCUMENT_ID
                    progress_modal = ImportProgressModal(total=1, category="Memos")
                    await app.push_screen(progress_modal)
                    await pilot.pause()

                    await app._import_project_documents([already_imported], category="Memos", destination_folder=DEMO_MEMO_FOLDER, progress_modal=progress_modal)
                    await pilot.pause()

                    self.assertNotIsInstance(app.screen, DuplicateDocumentModal)
                    memo_paths = sorted(path.name for path in (project_root / "memos" / DEMO_MEMO_FOLDER).glob("data_memo_1*.md"))
                    self.assertEqual(memo_paths, ["data_memo_1.md"])
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_batch_duplicate_modal_has_skip_file_and_cancel_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    duplicate = Path(tmp) / "data_memo_1.md"
                    unique = Path(tmp) / "cancel_after_duplicate.md"
                    duplicate.write_text("# Duplicate Replacement\n", encoding="utf-8")
                    unique.write_text("# Cancel After Duplicate\n", encoding="utf-8")
                    progress_modal = ImportProgressModal(total=2, category="Memos")
                    await app.push_screen(progress_modal)
                    await pilot.pause()

                    await app._import_project_documents([duplicate, unique], category="Memos", destination_folder=DEMO_MEMO_FOLDER, progress_modal=progress_modal)
                    await pilot.pause()

                    self.assertIsInstance(app.screen, DuplicateDocumentModal)
                    self.assertEqual(str(app.screen.query_one(f"#{DUPLICATE_CANCEL_ID}", Button).label), "Skip")
                    self.assertEqual(str(app.screen.query_one(f"#{DUPLICATE_REPLACE_ALL_ID}", Button).label), "Replace all")
                    self.assertEqual(str(app.screen.query_one(f"#{DUPLICATE_SKIP_ALL_IMPORT_ID}", Button).label), "Skip all")
                    self.assertEqual(str(app.screen.query_one(f"#{DUPLICATE_CANCEL_IMPORT_ID}", Button).label), "Cancel")
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_batch_import_cancel_stops_remaining_without_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    first = Path(tmp) / "already_added.md"
                    second = Path(tmp) / "should_not_import.md"
                    first.write_text("# Already Added\n", encoding="utf-8")
                    second.write_text("# Should Not Import\n", encoding="utf-8")
                    project_root = Path(tmp) / "demo-project"
                    progress_modal = ImportProgressModal(total=2, category="Memos")
                    await app.push_screen(progress_modal)
                    await pilot.pause()

                    await app._import_project_documents([first], category="Memos", progress_modal=progress_modal)
                    progress_modal.cancel_requested = True
                    await app._import_project_documents(
                        [first, second],
                        category="Memos",
                        start_index=1,
                        progress_modal=progress_modal,
                        imported_count=1,
                    )
                    await pilot.pause()

                    self.assertEqual((project_root / "memos/already_added.md").read_text(encoding="utf-8"), "# Already Added\n")
                    self.assertFalse((project_root / "memos/should_not_import.md").exists())
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_batch_duplicate_cancel_import_stops_remaining_without_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    duplicate = Path(tmp) / "data_memo_1.md"
                    unique = Path(tmp) / "cancelled_remaining.md"
                    duplicate.write_text("# Duplicate Replacement\n", encoding="utf-8")
                    unique.write_text("# Cancelled Remaining\n", encoding="utf-8")
                    project_root = Path(tmp) / "demo-project"
                    progress_modal = ImportProgressModal(total=2, category="Memos")
                    await app.push_screen(progress_modal)
                    await pilot.pause()

                    app._handle_duplicate_batch_import_result(
                        [duplicate, unique],
                        "Memos",
                        0,
                        ("cancel_import", None),
                        progress_modal,
                        imported_count=0,
                        skipped_count=0,
                    )
                    await pilot.pause()

                    self.assertFalse((project_root / "memos/cancelled_remaining.md").exists())
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_batch_import_duplicate_replace_and_rename_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    duplicate = Path(tmp) / "data_memo_1.md"
                    duplicate.write_text("# Batch Replacement\n", encoding="utf-8")

                    await app._import_project_documents(
                        [duplicate],
                        category="Memos",
                        destination_folder=DEMO_MEMO_FOLDER,
                        duplicate_result=("replace", None),
                    )
                    await pilot.pause()
                    self.assertEqual((project_root / DEMO_MEMO_DOCUMENT_ID).read_text(encoding="utf-8"), "# Batch Replacement\n")

                    await app._import_project_documents(
                        [duplicate],
                        category="Memos",
                        destination_folder=DEMO_MEMO_FOLDER,
                        duplicate_result=("rename", "batch_renamed_memo.md"),
                    )
                    await pilot.pause()
                    self.assertEqual((project_root / "memos" / DEMO_MEMO_FOLDER / "batch_renamed_memo.md").read_text(encoding="utf-8"), "# Batch Replacement\n")
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_batch_import_duplicate_replace_all_replaces_later_duplicates_without_reprompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    memo_duplicate = Path(tmp) / "data_memo_1.md"
                    second_duplicate = Path(tmp) / "second_duplicate.md"
                    memo_duplicate.write_text("# Batch Replace All Memo\n", encoding="utf-8")
                    second_duplicate.write_text("# Batch Replace All Second\n", encoding="utf-8")
                    second_target = project_root / "memos" / DEMO_MEMO_FOLDER / "second_duplicate.md"
                    second_target.write_text("# Existing Second Duplicate\n", encoding="utf-8")
                    progress_modal = ImportProgressModal(total=2, category="Memos")
                    await app.push_screen(progress_modal)
                    await pilot.pause()

                    await app._import_project_documents(
                        [memo_duplicate, second_duplicate],
                        category="Memos",
                        destination_folder=DEMO_MEMO_FOLDER,
                        progress_modal=progress_modal,
                    )
                    await pilot.pause()

                    self.assertIsInstance(app.screen, DuplicateDocumentModal)
                    app.screen.query_one(f"#{DUPLICATE_REPLACE_ALL_ID}", Button).press()
                    await pilot.pause()
                    await pilot.pause()

                    self.assertEqual((project_root / DEMO_MEMO_DOCUMENT_ID).read_text(encoding="utf-8"), "# Batch Replace All Memo\n")
                    self.assertEqual(second_target.read_text(encoding="utf-8"), "# Batch Replace All Second\n")
                    self.assertNotIsInstance(app.screen, DuplicateDocumentModal)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_batch_import_duplicate_skip_all_skips_later_duplicates_without_reprompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    memo_duplicate = Path(tmp) / "data_memo_1.md"
                    unique = Path(tmp) / "skip_all_unique.md"
                    second_duplicate = Path(tmp) / "second_duplicate.md"
                    memo_duplicate.write_text("# Skip All Memo\n", encoding="utf-8")
                    unique.write_text("# Skip All Unique\n", encoding="utf-8")
                    second_duplicate.write_text("# Skip All Second\n", encoding="utf-8")
                    second_target = project_root / "memos" / DEMO_MEMO_FOLDER / "second_duplicate.md"
                    second_target.write_text("# Existing Second Duplicate\n", encoding="utf-8")
                    original_memo = (project_root / DEMO_MEMO_DOCUMENT_ID).read_text(encoding="utf-8")
                    progress_modal = ImportProgressModal(total=3, category="Memos")
                    await app.push_screen(progress_modal)
                    await pilot.pause()

                    await app._import_project_documents(
                        [memo_duplicate, unique, second_duplicate],
                        category="Memos",
                        destination_folder=DEMO_MEMO_FOLDER,
                        progress_modal=progress_modal,
                    )
                    await pilot.pause()

                    self.assertIsInstance(app.screen, DuplicateDocumentModal)
                    app.screen.query_one(f"#{DUPLICATE_SKIP_ALL_IMPORT_ID}", Button).press()
                    await pilot.pause()
                    await pilot.pause()

                    self.assertEqual((project_root / DEMO_MEMO_DOCUMENT_ID).read_text(encoding="utf-8"), original_memo)
                    self.assertEqual(
                        (project_root / "memos" / DEMO_MEMO_FOLDER / "skip_all_unique.md").read_text(encoding="utf-8"),
                        "# Skip All Unique\n",
                    )
                    self.assertEqual(second_target.read_text(encoding="utf-8"), "# Existing Second Duplicate\n")
                    self.assertNotIsInstance(app.screen, DuplicateDocumentModal)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_restore_duplicate_can_rename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    project_root = Path(tmp) / "demo-project"
                    tree = app.query_one(ProjectBrowserTree)
                    tree.move_cursor(tree._entry_nodes["project-demo-essay"], animate=False)
                    await app._delete_selected_project_document()
                    await pilot.pause()

                    app._ensure_default_project_documents()
                    self.assertTrue((project_root / DEMO_MEMO_DOCUMENT_ID).exists())
                    [(trash_slug, _trash_id)] = list(app._trash_id_by_slug.items())

                    app._handle_duplicate_restore_result(trash_slug, ("rename", "restored_data_memo.md"))
                    await pilot.pause()

                    self.assertTrue((project_root / DEMO_MEMO_DOCUMENT_ID).exists())
                    self.assertTrue((project_root / "memos" / DEMO_MEMO_FOLDER / "restored_data_memo.md").exists())
                    self.assertNotIn(trash_slug, app._trash_id_by_slug)
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous



class ModelSettingsModalTests(unittest.IsolatedAsyncioTestCase):
    class TestHost(App[None]):
        def __init__(self) -> None:
            super().__init__()
            self.requests: list[ModelSettingsModal.TestConnectionRequested] = []

        def on_model_settings_modal_test_connection_requested(
            self, message: ModelSettingsModal.TestConnectionRequested
        ) -> None:
            self.requests.append(message)
            message.stop()

    async def test_model_settings_modal_disables_secure_writes_when_keyring_is_unavailable(self) -> None:
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                ModelSettingsModal(
                    settings=MistralModelSettings(),
                    has_api_key=False,
                    secure_storage_available=False,
                    secure_storage_message="Secure storage locked.",
                )
            )
            await pilot.pause()

            self.assertTrue(app.screen.query_one(f"#{MODEL_SETTINGS_SAVE_ID}", Button).disabled)
            self.assertTrue(app.screen.query_one(f"#{MODEL_SETTINGS_CLEAR_ID}", Button).disabled)
            status = str(app.screen.query_one(f"#{MODEL_SETTINGS_STATUS_ID}", Static).render())
            self.assertIn("Secure storage locked.", status)

    async def test_model_settings_modal_paste_inserts_api_key_text(self) -> None:
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                ModelSettingsModal(
                    settings=MistralModelSettings(),
                    has_api_key=False,
                    secure_storage_available=True,
                )
            )
            await pilot.pause()

            api_key_input = app.screen.query_one(f"#{MODEL_SETTINGS_API_KEY_ID}", Input)
            self.assertTrue(api_key_input.has_focus)

            app.screen.on_paste(events.Paste("paste-key"))
            await pilot.pause()

            self.assertEqual(api_key_input.value, "paste-key")

    async def test_model_settings_modal_paste_inserts_local_model_id_text(self) -> None:
        settings = ModelSettings(provider=LOCAL_OPENAI_PROVIDER, endpoint_url="http://127.0.0.1:1234")
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                ModelSettingsModal(
                    settings=settings,
                    has_api_key=False,
                    secure_storage_available=True,
                )
            )
            await pilot.pause()

            model_input = app.screen.query_one(f"#{MODEL_SETTINGS_LOCAL_MODEL_ID}", Input)
            model_input.focus()
            await pilot.pause()
            app.screen.on_paste(events.Paste("gemma-4-31b-it\n"))
            await pilot.pause()

            self.assertEqual(model_input.value, "gemma-4-31b-it")

    async def test_model_settings_modal_test_connection_posts_live_request(self) -> None:
        app = self.TestHost()
        async with app.run_test() as pilot:
            await app.push_screen(
                ModelSettingsModal(
                    settings=MistralModelSettings(model=MISTRAL_MEDIUM_MODEL, reasoning_effort="high"),
                    has_api_key=False,
                    secure_storage_available=True,
                )
            )
            await pilot.pause()

            app.screen.query_one(f"#{MODEL_SETTINGS_API_KEY_ID}", Input).value = "test-key"
            app.screen.query_one(f"#{MODEL_SETTINGS_TEST_ID}", Button).press()
            await pilot.pause()

            self.assertEqual(len(app.requests), 1)
            self.assertEqual(app.requests[0].api_key, "test-key")
            self.assertEqual(app.requests[0].settings.model, MISTRAL_MEDIUM_MODEL)
            self.assertTrue(app.screen.query_one(f"#{MODEL_SETTINGS_TEST_ID}", Button).disabled)
            status = str(app.screen.query_one(f"#{MODEL_SETTINGS_STATUS_ID}", Static).render())
            self.assertIn("Testing live Mistral connection", status)

            app.requests[0].modal.complete_connection_test("Live Mistral connection succeeded.")
            await pilot.pause()
            self.assertFalse(app.screen.query_one(f"#{MODEL_SETTINGS_TEST_ID}", Button).disabled)

    async def test_model_settings_modal_provider_selection_resets_defaults(self) -> None:
        app = self.TestHost()
        async with app.run_test() as pilot:
            await app.push_screen(
                ModelSettingsModal(
                    settings=MistralModelSettings(),
                    has_api_key=False,
                    has_api_keys={GOOGLE_PROVIDER: True},
                    secure_storage_available=True,
                )
            )
            await pilot.pause()

            provider_radio = app.screen.query_one("#model-settings-provider-google", RadioButton)
            provider_radio.toggle()
            await pilot.pause()

            model_select = app.screen.query_one(f"#{MODEL_SETTINGS_MODEL_ID}", Select)
            reasoning_select = app.screen.query_one(f"#{MODEL_SETTINGS_REASONING_ID}", Select)
            context_select = app.screen.query_one(f"#{MODEL_SETTINGS_CONTEXT_ID}", Select)
            api_key_input = app.screen.query_one(f"#{MODEL_SETTINGS_API_KEY_ID}", Input)
            api_key_group = app.screen.query_one(f"#{MODEL_SETTINGS_API_KEY_GROUP_ID}")

            self.assertEqual(str(api_key_group.query_one(Static).render()), "API Key")
            self.assertTrue(app.screen.query_one(f"#{MODEL_SETTINGS_STANDARD_FIELDS_ID}").display)
            self.assertFalse(app.screen.query_one(f"#{MODEL_SETTINGS_LOCAL_FIELDS_ID}").display)
            self.assertEqual(model_select.value, GOOGLE_GEMINI_FLASH_MODEL)
            self.assertEqual(reasoning_select.value, "medium")
            self.assertEqual(context_select.value, CONTEXT_200K_TOKENS)
            self.assertFalse(reasoning_select.disabled)
            self.assertFalse(context_select.disabled)
            self.assertEqual(api_key_input.placeholder, "Stored securely")

            app.screen.query_one(f"#{MODEL_SETTINGS_TEST_ID}", Button).press()
            await pilot.pause()

            self.assertEqual(len(app.requests), 1)
            self.assertEqual(app.requests[0].settings.provider, GOOGLE_PROVIDER)
            self.assertEqual(app.requests[0].settings.model, GOOGLE_GEMINI_FLASH_MODEL)
            self.assertEqual(app.requests[0].settings.reasoning_effort, "medium")
            self.assertEqual(app.requests[0].settings.context_window_tokens, CONTEXT_200K_TOKENS)

    async def test_model_settings_modal_local_provider_uses_open_fields(self) -> None:
        settings = ModelSettings(
            provider=LOCAL_OPENAI_PROVIDER,
            model="gemma-4-31b-it",
            reasoning_effort="medium",
            context_window_tokens=0,
            endpoint_url="http://127.0.0.1:1234",
        )
        app = self.TestHost()
        async with app.run_test() as pilot:
            await app.push_screen(
                ModelSettingsModal(
                    settings=settings,
                    has_api_key=False,
                    secure_storage_available=False,
                    secure_storage_message="Secure storage locked.",
                )
            )
            await pilot.pause()

            self.assertEqual(app.screen.query_one(f"#{MODEL_SETTINGS_API_KEY_ID}", Input).placeholder, "local")
            self.assertFalse(app.screen.query_one(f"#{MODEL_SETTINGS_STANDARD_FIELDS_ID}").display)
            self.assertTrue(app.screen.query_one(f"#{MODEL_SETTINGS_LOCAL_FIELDS_ID}").display)
            self.assertEqual(app.screen.query_one(f"#{MODEL_SETTINGS_LOCAL_ENDPOINT_ID}", Input).value, "http://127.0.0.1:1234")
            self.assertEqual(app.screen.query_one(f"#{MODEL_SETTINGS_LOCAL_MODEL_ID}", Input).value, "gemma-4-31b-it")
            self.assertEqual(app.screen.query_one(f"#{MODEL_SETTINGS_LOCAL_CONTEXT_INPUT_ID}", Input).value, "0")
            context_slider = app.screen.query_one(f"#{MODEL_SETTINGS_LOCAL_CONTEXT_SLIDER_ID}")
            self.assertEqual(context_slider.value, 0)
            slider_render = context_slider.render().plain
            self.assertIn("2K", slider_render)
            self.assertIn("4K", slider_render)
            self.assertIn("8K", slider_render)
            self.assertIn("16K", slider_render)
            self.assertIn("32K", slider_render)
            self.assertIn("64K", slider_render)
            self.assertIn("128K", slider_render)
            self.assertIn("256K", slider_render)
            self.assertIn("512K", slider_render)
            self.assertIn("1M", slider_render)
            self.assertTrue(app.screen.query_one(f"#{MODEL_SETTINGS_MODEL_ID}", Select).display is False)
            self.assertFalse(app.screen.query_one(f"#{MODEL_SETTINGS_SAVE_ID}", Button).disabled)
            self.assertFalse(app.screen.query_one(f"#{MODEL_SETTINGS_TEST_ID}", Button).disabled)

            app.screen.query_one(f"#{MODEL_SETTINGS_TEST_ID}", Button).press()
            await pilot.pause()

            self.assertEqual(len(app.requests), 1)
            self.assertEqual(app.requests[0].settings.provider, LOCAL_OPENAI_PROVIDER)
            self.assertEqual(app.requests[0].settings.model, "gemma-4-31b-it")
            self.assertEqual(app.requests[0].settings.endpoint_url, "http://127.0.0.1:1234")
            self.assertEqual(app.requests[0].settings.context_window_tokens, 0)


class SystemClipboardInputTests(unittest.IsolatedAsyncioTestCase):
    class ClipboardInputApp(App[None]):
        def compose(self) -> ComposeResult:
            yield SystemClipboardInput(value="replace me", id="clipboard-input")

    async def test_paste_reads_host_clipboard_and_replaces_selection(self) -> None:
        app = self.ClipboardInputApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            text_input = app.query_one("#clipboard-input", SystemClipboardInput)
            text_input.select_all()

            with patch("exegesis_textual.widgets.clipboard_input.read_system_clipboard", return_value="local-model\n"):
                text_input.action_paste()

            self.assertEqual(text_input.value, "local-model")

    async def test_copy_writes_host_clipboard(self) -> None:
        app = self.ClipboardInputApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            text_input = app.query_one("#clipboard-input", SystemClipboardInput)
            text_input.select_all()

            with patch("exegesis_textual.widgets.clipboard_input.write_system_clipboard") as write_clipboard:
                text_input.action_copy()

            write_clipboard.assert_called_once_with("replace me")


class MistralChatBackendTests(unittest.TestCase):
    def setUp(self) -> None:
        self._previous_settings_path = os.environ.get(TEXTUAL_SETTINGS_PATH_ENV)
        self._previous_local_developer = os.environ.get(LOCAL_DEVELOPER_ENV)
        self._settings_tmp = tempfile.TemporaryDirectory()
        self._settings_path = Path(self._settings_tmp.name) / "settings.json"
        os.environ[TEXTUAL_SETTINGS_PATH_ENV] = str(self._settings_path)
        os.environ.pop(LOCAL_DEVELOPER_ENV, None)

    def tearDown(self) -> None:
        if self._previous_settings_path is None:
            os.environ.pop(TEXTUAL_SETTINGS_PATH_ENV, None)
        else:
            os.environ[TEXTUAL_SETTINGS_PATH_ENV] = self._previous_settings_path
        if self._previous_local_developer is None:
            os.environ.pop(LOCAL_DEVELOPER_ENV, None)
        else:
            os.environ[LOCAL_DEVELOPER_ENV] = self._previous_local_developer
        self._settings_tmp.cleanup()

    def test_default_model_constant(self) -> None:
        self.assertEqual(DEFAULT_MISTRAL_MODEL, "mistral-small-latest")

    def test_claude_effort_options_match_api_supported_models(self) -> None:
        deep_efforts = ("low", "medium", "high", "xhigh", "max")
        self.assertEqual(reasoning_options_for_model(CLAUDE_FABLE_MODEL), deep_efforts)
        self.assertEqual(reasoning_options_for_model(CLAUDE_OPUS_MODEL), deep_efforts)
        self.assertEqual(reasoning_options_for_model(CLAUDE_SONNET_MODEL), ("low", "medium", "high", "max"))
        self.assertEqual(reasoning_options_for_model(CLAUDE_HAIKU_MODEL), ("none",))

    def test_settings_path_uses_test_override(self) -> None:
        self.assertEqual(textual_settings_path(), self._settings_path)

    def test_local_developer_settings_path_uses_codex_folder(self) -> None:
        os.environ.pop(TEXTUAL_SETTINGS_PATH_ENV, None)
        os.environ[LOCAL_DEVELOPER_ENV] = "1"

        settings_path = textual_settings_path(Path("/tmp/repo"))

        self.assertEqual(settings_path, Path("/tmp/repo/.codex/shell/settings.json"))

    def test_model_settings_persist_without_secrets(self) -> None:
        settings = MistralModelSettings(model=MISTRAL_MEDIUM_MODEL, reasoning_effort="none", settings_prompt_dismissed=True)

        save_mistral_model_settings(settings)

        raw = json.loads(self._settings_path.read_text(encoding="utf-8"))
        self.assertEqual(raw["model"]["provider"], "mistral")
        self.assertEqual(raw["model"]["model"], MISTRAL_MEDIUM_MODEL)
        self.assertEqual(raw["model"]["reasoning_effort"], "none")
        self.assertEqual(raw["model"]["context_window_tokens"], CONTEXT_256K_TOKENS)
        self.assertTrue(raw["model"]["settings_prompt_dismissed"])
        self.assertNotIn("api", json.dumps(raw).casefold())
        self.assertEqual(load_mistral_model_settings(), settings)

    def test_multi_provider_model_settings_persist_without_secrets(self) -> None:
        settings = ModelSettings(
            provider=GOOGLE_PROVIDER,
            model=GOOGLE_GEMINI_FLASH_MODEL,
            reasoning_effort="high",
            context_window_tokens=CONTEXT_1M_TOKENS,
            settings_prompt_dismissed=True,
        )

        save_model_settings(settings)

        raw = json.loads(self._settings_path.read_text(encoding="utf-8"))
        self.assertEqual(raw["model"]["provider"], GOOGLE_PROVIDER)
        self.assertEqual(raw["model"]["model"], GOOGLE_GEMINI_FLASH_MODEL)
        self.assertEqual(raw["model"]["reasoning_effort"], "high")
        self.assertEqual(raw["model"]["context_window_tokens"], CONTEXT_1M_TOKENS)
        self.assertNotIn("api", json.dumps(raw).casefold())
        self.assertEqual(load_model_settings(), settings)

    def test_local_openai_profile_persists_without_secrets(self) -> None:
        settings = ModelSettings(
            provider=LOCAL_OPENAI_PROVIDER,
            model="gemma-4-31b-it",
            reasoning_effort="medium",
            context_window_tokens=0,
            endpoint_url="localhost:1234",
            profiles={
                LOCAL_OPENAI_PROVIDER: ProviderModelProfile(
                    provider=LOCAL_OPENAI_PROVIDER,
                    model="gemma-4-31b-it",
                    reasoning_effort="medium",
                    context_window_tokens=0,
                    endpoint_url="localhost:1234",
                )
            },
        )

        save_model_settings(settings)

        raw = json.loads(self._settings_path.read_text(encoding="utf-8"))
        local_profile = raw["model"]["profiles"][LOCAL_OPENAI_PROVIDER]
        self.assertEqual(raw["model"]["provider"], LOCAL_OPENAI_PROVIDER)
        self.assertEqual(local_profile["model"], "gemma-4-31b-it")
        self.assertEqual(local_profile["endpoint_url"], "localhost:1234")
        self.assertEqual(local_profile["context_window_tokens"], 0)
        self.assertTrue(load_model_settings().local_endpoint_configured())
        self.assertEqual(normalize_local_openai_base_url("localhost:1234"), "http://localhost:1234/v1")
        self.assertEqual(normalize_local_openai_base_url("http://127.0.0.1:1234/v1"), "http://127.0.0.1:1234/v1")
        self.assertTrue(is_loopback_endpoint("http://127.0.0.1:1234"))
        self.assertFalse(is_loopback_endpoint("http://192.168.1.20:1234"))
        self.assertNotIn("api", json.dumps(raw).casefold())

    def test_large_model_omits_reasoning_effort(self) -> None:
        settings = MistralModelSettings(model=MISTRAL_LARGE_MODEL, reasoning_effort="high")

        self.assertIsNone(settings.provider_payload_reasoning_effort())

    def test_in_memory_credential_store_supports_ci(self) -> None:
        store = InMemoryCredentialStore()
        backend = MistralChatBackend(credential_store=store)

        self.assertFalse(backend.is_configured())
        backend.set_api_key(" test-key ")
        self.assertTrue(backend.is_configured())
        self.assertEqual(store.get_secret(MISTRAL_ACCOUNT), "test-key")
        backend.clear_api_key()
        self.assertFalse(backend.is_configured())

    def test_provider_keys_are_stored_per_provider_account(self) -> None:
        store = InMemoryCredentialStore()
        backend = MistralChatBackend(credential_store=store)
        settings = ModelSettings(provider=GOOGLE_PROVIDER, model=GOOGLE_GEMINI_FLASH_MODEL, reasoning_effort="medium")
        backend.save_model_settings(settings)

        self.assertFalse(backend.has_api_key(GOOGLE_PROVIDER))
        backend.set_api_key(" google-key ", GOOGLE_PROVIDER)

        self.assertTrue(backend.has_api_key(GOOGLE_PROVIDER))
        self.assertEqual(store.get_secret(GOOGLE_ACCOUNT), "google-key")
        self.assertFalse(backend.has_api_key("mistral"))
        self.assertTrue(backend.is_configured())

    def test_local_openai_default_key_does_not_look_stored(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore())

        self.assertFalse(backend.has_api_key(LOCAL_OPENAI_PROVIDER))
        self.assertEqual(backend._api_key(LOCAL_OPENAI_PROVIDER), "local")

        backend.set_api_key(" real-local-key ", LOCAL_OPENAI_PROVIDER)

        self.assertTrue(backend.has_api_key(LOCAL_OPENAI_PROVIDER))
        self.assertEqual(backend._api_key(LOCAL_OPENAI_PROVIDER), "real-local-key")

    def test_local_openai_requires_loopback_endpoint_and_model_to_be_configured(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore())
        backend.save_model_settings(ModelSettings(provider=LOCAL_OPENAI_PROVIDER, endpoint_url="http://127.0.0.1:1234"))

        self.assertFalse(backend.is_configured())

        backend.save_model_settings(
            ModelSettings(provider=LOCAL_OPENAI_PROVIDER, model="local-model", endpoint_url="http://192.168.1.20:1234")
        )

        self.assertFalse(backend.is_configured())

        backend.save_model_settings(
            ModelSettings(provider=LOCAL_OPENAI_PROVIDER, model="local-model", endpoint_url="http://127.0.0.1:1234")
        )

        self.assertTrue(backend.is_configured())

    def test_unavailable_credential_store_has_no_plaintext_fallback(self) -> None:
        backend = MistralChatBackend(credential_store=UnavailableCredentialStore("locked"))

        self.assertFalse(backend.is_configured())
        with self.assertRaises(CredentialStoreError):
            backend.set_api_key("secret")

    def test_keyring_store_uses_expected_service_and_account(self) -> None:
        class FakeKeyring:
            def __init__(self) -> None:
                self.calls: list[tuple[str, str, str | None]] = []
                self.secret = "stored"

            def get_password(self, service: str, account: str) -> str:
                self.calls.append(("get", service, account))
                return self.secret

            def set_password(self, service: str, account: str, secret: str) -> None:
                self.calls.append(("set", service, account))
                self.secret = secret

            def delete_password(self, service: str, account: str) -> None:
                self.calls.append(("delete", service, account))
                self.secret = ""

            def get_keyring(self):
                return self

        from exegesis_textual.services.credentials import KeyringCredentialStore

        fake = FakeKeyring()
        with patch.object(KeyringCredentialStore, "_keyring", return_value=fake):
            store = KeyringCredentialStore()
            self.assertEqual(store.get_secret(MISTRAL_ACCOUNT), "stored")
            store.set_secret(MISTRAL_ACCOUNT, "new-secret")
            store.delete_secret(MISTRAL_ACCOUNT)

        self.assertEqual(fake.calls[0], ("get", KEYRING_SERVICE, MISTRAL_ACCOUNT))
        self.assertEqual(fake.calls[1], ("set", KEYRING_SERVICE, MISTRAL_ACCOUNT))
        self.assertEqual(fake.calls[2], ("delete", KEYRING_SERVICE, MISTRAL_ACCOUNT))

    def test_keyring_store_reports_fail_backend_as_unavailable(self) -> None:
        class FailBackend:
            pass

        FailBackend.__module__ = "keyring.backends.fail"

        class FakeKeyring:
            def get_keyring(self):
                return FailBackend()

        from exegesis_textual.services.credentials import KeyringCredentialStore

        with patch.object(KeyringCredentialStore, "_keyring", return_value=FakeKeyring()):
            status = KeyringCredentialStore().status()

        self.assertFalse(status.available)
        self.assertEqual(status.backend_name, "keyring.backends.fail.FailBackend")
        self.assertIn("no secure backend", status.error_message)

    def test_live_connection_test_uses_completion_and_selected_reasoning(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({MISTRAL_ACCOUNT: "stored-key"}))
        settings = MistralModelSettings(model=MISTRAL_MEDIUM_MODEL, reasoning_effort="high")
        client = _RecordingMistralClient([])

        async def test_connection():
            with patch.object(backend, "_get_client", return_value=client):
                return await backend.test_connection(settings)

        result = asyncio.run(test_connection())

        self.assertTrue(result.ok)
        self.assertIn("Live Mistral connection succeeded", result.message)
        self.assertEqual(client.complete_calls[0]["model"], MISTRAL_MEDIUM_MODEL)
        self.assertEqual(client.complete_calls[0]["reasoning_effort"], "high")
        self.assertEqual(client.complete_calls[0]["max_tokens"], 32)
        self.assertEqual(client.complete_calls[0]["temperature"], 0)
        self.assertEqual(client.complete_calls[0]["top_p"], 1)
        self.assertEqual(client.complete_calls[0]["messages"][0]["role"], "user")

    def test_live_connection_test_uses_unsaved_api_key_without_storing_it(self) -> None:
        store = InMemoryCredentialStore()
        backend = MistralChatBackend(credential_store=store)
        client = _RecordingMistralClient([])

        async def test_connection():
            with patch.object(backend, "_get_client", return_value=client) as get_client:
                result = await backend.test_connection(MistralModelSettings(), api_key=" typed-key ")
                return result, get_client

        result, get_client = asyncio.run(test_connection())

        self.assertTrue(result.ok)
        get_client.assert_called_once_with("typed-key")
        self.assertEqual(store.get_secret(MISTRAL_ACCOUNT), "")

    def test_google_connection_test_posts_live_generate_content_request(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({GOOGLE_ACCOUNT: "key"}))
        settings = ModelSettings(provider=GOOGLE_PROVIDER, model=GOOGLE_GEMINI_FLASH_MODEL, reasoning_effort="medium")
        calls: list[dict[str, object]] = []

        class FakeGoogleModels:
            async def generate_content(self, **kwargs):
                calls.append(kwargs)
                return {"candidates": [{"content": {"parts": [{"text": "OK"}]}}]}

        class FakeGoogleAio:
            models = FakeGoogleModels()

        class FakeGoogleClient:
            def __init__(self, *, api_key: str):
                calls.append({"api_key": api_key})
                self.aio = FakeGoogleAio()

        async def test_connection():
            from google import genai as google_genai

            with patch.object(google_genai, "Client", FakeGoogleClient):
                return await backend.test_connection(settings)

        result = asyncio.run(test_connection())

        self.assertTrue(result.ok)
        self.assertIn("Live Google connection succeeded", result.message)
        self.assertEqual(calls[0]["api_key"], "key")
        self.assertEqual(calls[1]["model"], GOOGLE_GEMINI_FLASH_MODEL)
        self.assertEqual(calls[1]["config"]["max_output_tokens"], 32)
        self.assertNotIn("thinking_config", calls[1]["config"])

    def test_google_connection_test_distinguishes_generation_quota_from_bad_configuration(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({GOOGLE_ACCOUNT: "key"}))
        settings = ModelSettings(provider=GOOGLE_PROVIDER, model=GOOGLE_GEMINI_FLASH_MODEL, reasoning_effort="medium")
        calls: list[dict[str, object]] = []

        class FakeGoogleModels:
            async def generate_content(self, **kwargs):
                calls.append({"generate": kwargs})
                raise RuntimeError('status_code: 429 body: {"error":{"status":"RESOURCE_EXHAUSTED"}}')

            async def get(self, **kwargs):
                calls.append({"get": kwargs})
                return {"name": f"models/{GOOGLE_GEMINI_FLASH_MODEL}"}

        class FakeGoogleAio:
            models = FakeGoogleModels()

        class FakeGoogleClient:
            def __init__(self, *, api_key: str):
                calls.append({"api_key": api_key})
                self.aio = FakeGoogleAio()

        async def test_connection():
            from google import genai as google_genai

            with patch.object(google_genai, "Client", FakeGoogleClient):
                return await backend.test_connection(settings)

        result = asyncio.run(test_connection())

        self.assertFalse(result.ok)
        self.assertIn("API key and model are configured", result.message)
        self.assertIn("generation quota is currently exhausted", result.message)
        self.assertEqual(calls[0]["api_key"], "key")
        self.assertEqual(calls[1]["generate"]["model"], GOOGLE_GEMINI_FLASH_MODEL)
        self.assertEqual(calls[3]["get"]["model"], GOOGLE_GEMINI_FLASH_MODEL)

    def test_claude_connection_test_uses_sdk_messages_create(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({CLAUDE_ACCOUNT: "key"}))
        settings = ModelSettings(provider=CLAUDE_PROVIDER, model=CLAUDE_SONNET_MODEL, reasoning_effort="high")
        calls: list[dict[str, object]] = []

        class FakeClaudeMessages:
            async def create(self, **kwargs):
                calls.append(kwargs)
                return {"content": [{"type": "text", "text": "OK"}]}

        class FakeClaudeClient:
            def __init__(self, *, api_key: str):
                calls.append({"api_key": api_key})
                self.messages = FakeClaudeMessages()

        async def test_connection():
            with patch.object(__import__("anthropic"), "AsyncAnthropic", FakeClaudeClient):
                return await backend.test_connection(settings)

        result = asyncio.run(test_connection())

        self.assertTrue(result.ok)
        self.assertIn("Live Claude connection succeeded", result.message)
        self.assertEqual(calls[0]["api_key"], "key")
        self.assertEqual(calls[1]["model"], CLAUDE_SONNET_MODEL)
        self.assertEqual(calls[1]["max_tokens"], 32)
        self.assertNotIn("temperature", calls[1])
        self.assertNotIn("extra_body", calls[1])
        self.assertEqual(calls[1]["thinking"], {"type": "adaptive"})
        self.assertEqual(calls[1]["output_config"], {"effort": "high"})

    def test_openai_connection_rate_limit_uses_settings_error_copy(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({OPENAI_ACCOUNT: "key"}))
        settings = ModelSettings(provider=OPENAI_PROVIDER, model=OPENAI_GPT_55_MODEL, reasoning_effort="medium")

        class FakeOpenAIResponses:
            async def create(self, **_kwargs):
                raise RuntimeError('status_code: 429 body: {"message":"rate limit exceeded","type":"rate_limit"}')

        class FakeOpenAIClient:
            def __init__(self, *, api_key: str):
                self.responses = FakeOpenAIResponses()

        async def test_connection():
            with patch.object(__import__("openai"), "AsyncOpenAI", FakeOpenAIClient):
                return await backend.test_connection(settings)

        result = asyncio.run(test_connection())

        self.assertFalse(result.ok)
        self.assertIn("OpenAI rate limit reached", result.message)
        self.assertIn("connection test", result.message)
        self.assertNotIn("Reduce basket context", result.message)

    def test_google_stream_reply_uses_sdk_streaming(self) -> None:
        settings = ModelSettings(provider=GOOGLE_PROVIDER, model=GOOGLE_GEMINI_FLASH_MODEL, reasoning_effort="medium")
        save_model_settings(settings)
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({GOOGLE_ACCOUNT: "google-key"}))
        calls: list[dict[str, object]] = []
        clients: list[dict[str, object]] = []

        class FakeGoogleStream:
            def __aiter__(self):
                self._chunks = iter(
                    [
                        {
                            "candidates": [
                                {"content": {"parts": [{"text": "thinking", "thought": True}, {"text": " answer"}]}}
                            ]
                        },
                        {
                            "candidates": [
                                {
                                    "content": {
                                        "parts": [
                                            {
                                                "functionCall": {
                                                    "name": "search_documents",
                                                    "args": {"query": "leadership"},
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        },
                    ]
                )
                return self

            async def __anext__(self):
                try:
                    return next(self._chunks)
                except StopIteration:
                    raise StopAsyncIteration

        class FakeModels:
            async def generate_content_stream(self, **kwargs):
                calls.append(kwargs)
                return FakeGoogleStream()

        class FakeAio:
            def __init__(self) -> None:
                self.models = FakeModels()

        class FakeGoogleClient:
            def __init__(self, **kwargs) -> None:
                clients.append(kwargs)
                self.aio = FakeAio()

        from google import genai as google_genai

        async def collect() -> list[ChatEvent]:
            with patch.object(backend, "_load_system_prompt", return_value="system"), patch.object(
                google_genai, "Client", FakeGoogleClient
            ):
                return [
                    event
                    async for event in backend.stream_reply(
                        "chat-main",
                        [ChatMessage("user", "Find leadership")],
                        self._context(),
                        tools=provider_tool_specs(),
                    )
                ]

        events = asyncio.run(collect())

        self.assertEqual([event.kind for event in events], ["reasoning_delta", "assistant_delta", "tool_call"])
        self.assertEqual(events[0].text, "thinking")
        self.assertEqual(events[1].text, " answer")
        self.assertEqual(events[2].tool_call.tool_name, "search_documents")
        self.assertEqual(events[2].tool_call.arguments, {"query": "leadership"})
        self.assertEqual(clients[0]["api_key"], "google-key")
        self.assertEqual(calls[0]["model"], GOOGLE_GEMINI_FLASH_MODEL)
        self.assertEqual(calls[0]["config"]["thinking_config"], {"thinking_level": "medium"})
        self.assertIn("tools", calls[0]["config"])
        tool_payload = json.dumps(calls[0]["config"]["tools"])
        self.assertNotIn("additionalProperties", tool_payload)
        self.assertNotIn("additional_properties", tool_payload)

    def test_openai_stream_reply_uses_selected_provider_and_responses_api(self) -> None:
        settings = ModelSettings(provider=OPENAI_PROVIDER, model=OPENAI_GPT_55_MODEL, reasoning_effort="medium")
        save_model_settings(settings)
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({OPENAI_ACCOUNT: "openai-key"}))
        calls: list[dict[str, object]] = []
        clients: list[dict[str, object]] = []

        class FakeResponseStream:
            def __aiter__(self):
                self._events = iter([{"type": "response.output_text.delta", "delta": "OpenAI answer"}])
                return self

            async def __anext__(self):
                try:
                    return next(self._events)
                except StopIteration:
                    raise StopAsyncIteration

        class FakeResponses:
            async def create(self, **kwargs):
                calls.append(kwargs)
                return FakeResponseStream()

        class FakeAsyncOpenAI:
            def __init__(self, **kwargs):
                clients.append(kwargs)
                self.responses = FakeResponses()

        async def collect() -> list[ChatEvent]:
            with patch.object(backend, "_load_system_prompt", return_value="system"), patch.object(
                __import__("openai"), "AsyncOpenAI", FakeAsyncOpenAI
            ):
                return [
                    event
                    async for event in backend.stream_reply(
                        "chat-main",
                        [ChatMessage("user", "Hello")],
                        self._context(),
                    )
                ]

        events = asyncio.run(collect())

        self.assertEqual([event.kind for event in events], ["assistant_delta", "assistant_done"])
        self.assertEqual(events[0].text, "OpenAI answer")
        self.assertEqual(clients[0]["api_key"], "openai-key")
        self.assertEqual(calls[0]["model"], OPENAI_GPT_55_MODEL)
        self.assertEqual(calls[0]["reasoning"], {"effort": "medium"})
        self.assertTrue(calls[0]["stream"])

    def test_openai_stream_waits_for_completed_tool_call_arguments(self) -> None:
        settings = ModelSettings(provider=OPENAI_PROVIDER, model=OPENAI_GPT_55_MODEL, reasoning_effort="medium")
        save_model_settings(settings)
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({OPENAI_ACCOUNT: "openai-key"}))
        calls: list[dict[str, object]] = []

        class FakeResponseStream:
            def __aiter__(self):
                self._events = iter(
                    [
                        {
                            "type": "response.output_item.added",
                            "item": {
                                "id": "fc_1",
                                "type": "function_call",
                                "status": "in_progress",
                                "arguments": "",
                                "call_id": "call_1",
                                "name": "draft_into_document",
                            },
                        },
                        {
                            "type": "response.function_call_arguments.delta",
                            "item_id": "fc_1",
                            "delta": '{"instruction":"Draft an abstract"',
                        },
                        {
                            "type": "response.output_item.done",
                            "item": {
                                "id": "fc_1",
                                "type": "function_call",
                                "status": "completed",
                                "arguments": '{"instruction":"Draft an abstract","insert_after_heading":"Abstract"}',
                                "call_id": "call_1",
                                "name": "draft_into_document",
                            },
                        },
                    ]
                )
                return self

            async def __anext__(self):
                try:
                    return next(self._events)
                except StopIteration:
                    raise StopAsyncIteration

        class FakeResponses:
            async def create(self, **kwargs):
                calls.append(kwargs)
                return FakeResponseStream()

        class FakeAsyncOpenAI:
            def __init__(self, **_kwargs):
                self.responses = FakeResponses()

        async def collect() -> list[ChatEvent]:
            with patch.object(backend, "_load_system_prompt", return_value="system"), patch.object(
                __import__("openai"), "AsyncOpenAI", FakeAsyncOpenAI
            ):
                return [
                    event
                    async for event in backend.stream_reply(
                        "chat-main",
                        [ChatMessage("user", "Draft an abstract")],
                        self._context(),
                        tools=provider_tool_specs(),
                    )
                ]

        events = asyncio.run(collect())

        self.assertEqual([event.kind for event in events], ["tool_call"])
        self.assertEqual(events[0].tool_call.tool_name, "draft_into_document")
        self.assertEqual(
            events[0].tool_call.arguments,
            {"instruction": "Draft an abstract", "insert_after_heading": "Abstract"},
        )
        self.assertIn("tools", calls[0])

    def test_local_openai_stream_splits_reasoning_tags_from_answer_text(self) -> None:
        settings = ModelSettings(
            provider=LOCAL_OPENAI_PROVIDER,
            model="gemma-4-31b-it",
            reasoning_effort="medium",
            context_window_tokens=262_144,
            endpoint_url="http://127.0.0.1:1234",
            profiles={
                LOCAL_OPENAI_PROVIDER: ProviderModelProfile(
                    provider=LOCAL_OPENAI_PROVIDER,
                    model="gemma-4-31b-it",
                    reasoning_effort="medium",
                    context_window_tokens=262_144,
                    endpoint_url="http://127.0.0.1:1234",
                )
            },
        )
        save_model_settings(settings)
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore())
        calls: list[dict[str, object]] = []
        clients: list[dict[str, object]] = []

        class FakeDelta:
            def __init__(self, content: str) -> None:
                self.content = content
                self.tool_calls = None

        class FakeChoice:
            def __init__(self, content: str) -> None:
                self.delta = FakeDelta(content)

        class FakeChunk:
            def __init__(self, content: str) -> None:
                self.choices = [FakeChoice(content)]

        class FakeChatStream:
            def __aiter__(self):
                self._chunks = iter(
                    [
                        FakeChunk("Answer before <thi"),
                        FakeChunk("nk>hidden thought</thi"),
                        FakeChunk("nk> final answer"),
                    ]
                )
                return self

            async def __anext__(self):
                try:
                    return next(self._chunks)
                except StopIteration:
                    raise StopAsyncIteration

        class FakeCompletions:
            async def create(self, **kwargs):
                calls.append(kwargs)
                return FakeChatStream()

        class FakeChat:
            def __init__(self) -> None:
                self.completions = FakeCompletions()

        class FakeAsyncOpenAI:
            def __init__(self, **kwargs):
                clients.append(kwargs)
                self.chat = FakeChat()

        async def collect() -> list[ChatEvent]:
            with patch.object(backend, "_load_system_prompt", return_value="system"), patch.object(
                __import__("openai"), "AsyncOpenAI", FakeAsyncOpenAI
            ):
                return [
                    event
                    async for event in backend.stream_reply(
                        "chat-main",
                        [ChatMessage("user", "Hello")],
                        self._context(),
                    )
                ]

        events = asyncio.run(collect())

        self.assertEqual([event.kind for event in events], ["assistant_delta", "reasoning_delta", "assistant_delta", "assistant_done"])
        self.assertEqual(events[0].text, "Answer before ")
        self.assertEqual(events[1].text, "hidden thought")
        self.assertEqual(events[2].text, " final answer")
        self.assertEqual(clients[0]["api_key"], "local")
        self.assertEqual(clients[0]["base_url"], "http://127.0.0.1:1234/v1")
        self.assertEqual(calls[0]["model"], "gemma-4-31b-it")
        self.assertEqual(calls[0]["extra_body"], {"reasoning_effort": "medium"})

    def test_claude_stream_reply_emits_tool_call_event(self) -> None:
        settings = ModelSettings(provider=CLAUDE_PROVIDER, model=CLAUDE_SONNET_MODEL, reasoning_effort="high")
        save_model_settings(settings)
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({CLAUDE_ACCOUNT: "claude-key"}))
        calls: list[dict[str, object]] = []
        clients: list[dict[str, object]] = []

        class FakeClaudeStream:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb) -> None:
                return None

            def __aiter__(self):
                self._events = iter(
                    [
                        {
                            "type": "content_block_start",
                            "content_block": {
                                "type": "tool_use",
                                "id": "toolu_search",
                                "name": "search_documents",
                                "input": {},
                            },
                        },
                        {
                            "type": "content_block_delta",
                            "delta": {"type": "input_json_delta", "partial_json": '{"query": "leadership"}'},
                        },
                        {"type": "content_block_stop"},
                    ]
                )
                return self

            async def __anext__(self):
                try:
                    return next(self._events)
                except StopIteration:
                    raise StopAsyncIteration

        class FakeMessages:
            def stream(self, **kwargs):
                calls.append(kwargs)
                return FakeClaudeStream()

        class FakeAsyncAnthropic:
            def __init__(self, **kwargs):
                clients.append(kwargs)
                self.messages = FakeMessages()

        async def collect() -> list[ChatEvent]:
            with patch.object(backend, "_load_system_prompt", return_value="system"), patch.object(
                __import__("anthropic"), "AsyncAnthropic", FakeAsyncAnthropic
            ):
                return [
                    event
                    async for event in backend.stream_reply(
                        "chat-main",
                        [ChatMessage("user", "Find leadership")],
                        self._context(),
                        tools=provider_tool_specs(),
                    )
                ]

        events = asyncio.run(collect())

        self.assertEqual([event.kind for event in events], ["tool_call"])
        self.assertEqual(events[0].tool_call.tool_name, "search_documents")
        self.assertEqual(events[0].tool_call.arguments, {"query": "leadership"})
        self.assertEqual(clients[0]["api_key"], "claude-key")
        self.assertEqual(calls[0]["model"], CLAUDE_SONNET_MODEL)
        self.assertNotIn("temperature", calls[0])
        self.assertNotIn("extra_body", calls[0])
        self.assertEqual(calls[0]["thinking"], {"type": "adaptive"})
        self.assertEqual(calls[0]["output_config"], {"effort": "high"})
        self.assertIn("tools", calls[0])

    def test_live_connection_test_large_model_omits_reasoning_effort(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({MISTRAL_ACCOUNT: "key"}))
        settings = MistralModelSettings(model=MISTRAL_LARGE_MODEL, reasoning_effort="high")
        client = _RecordingMistralClient([])

        async def test_connection():
            with patch.object(backend, "_get_client", return_value=client):
                return await backend.test_connection(settings)

        result = asyncio.run(test_connection())

        self.assertTrue(result.ok)
        self.assertEqual(client.complete_calls[0]["model"], MISTRAL_LARGE_MODEL)
        self.assertNotIn("reasoning_effort", client.complete_calls[0])

    def test_live_connection_test_formats_provider_errors(self) -> None:
        class RateLimitedChat:
            async def complete_async(self, **_kwargs):
                raise RuntimeError(
                    'status_code: 429 body: {"message":"rate limit exceeded","type":"rate_limit","retry_after":60}'
                )

        class RateLimitedClient:
            chat = RateLimitedChat()

        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({MISTRAL_ACCOUNT: "key"}))

        async def test_connection():
            with patch.object(backend, "_get_client", return_value=RateLimitedClient()):
                return await backend.test_connection(MistralModelSettings())

        result = asyncio.run(test_connection())

        self.assertFalse(result.ok)
        self.assertIn("Mistral rate limit reached", result.message)
        self.assertIn("connection test", result.message)
        self.assertNotIn("Reduce basket context", result.message)
        self.assertNotIn("status_code", result.message)
        self.assertNotIn('{"message"', result.message)

    def test_live_connection_test_formats_auth_errors(self) -> None:
        class UnauthorizedChat:
            async def complete_async(self, **_kwargs):
                raise RuntimeError('Status 401 Body: {"detail":"Unauthorized"}')

        class UnauthorizedClient:
            chat = UnauthorizedChat()

        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({MISTRAL_ACCOUNT: "key"}))

        async def test_connection():
            with patch.object(backend, "_get_client", return_value=UnauthorizedClient()):
                return await backend.test_connection(MistralModelSettings())

        result = asyncio.run(test_connection())

        self.assertFalse(result.ok)
        self.assertIn("Mistral rejected this API key", result.message)
        self.assertNotIn("Status 401", result.message)
        self.assertNotIn('{"detail"', result.message)

    def test_small_and_medium_send_reasoning_effort(self) -> None:
        context = self._context()
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({MISTRAL_ACCOUNT: "key"}))
        save_mistral_model_settings(MistralModelSettings(model=MISTRAL_MEDIUM_MODEL, reasoning_effort="high"))
        client = _RecordingMistralClient([_fake_stream_event([{"type": "text", "text": "hello"}], finish_reason="stop")])

        async def collect() -> list[ChatEvent]:
            with patch.object(backend, "_load_system_prompt", return_value="system"), patch.object(
                backend, "_get_client", return_value=client
            ):
                return [
                    event
                    async for event in backend.stream_reply(
                        "chat-main",
                        [ChatMessage("user", "Hello")],
                        context,
                    )
                ]

        events = asyncio.run(collect())

        self.assertEqual(client.calls[0]["model"], MISTRAL_MEDIUM_MODEL)
        self.assertEqual(client.calls[0]["reasoning_effort"], "high")
        self.assertEqual([event.kind for event in events], ["assistant_delta", "assistant_done"])

    def test_large_model_sends_no_reasoning_effort(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({MISTRAL_ACCOUNT: "key"}))
        save_mistral_model_settings(MistralModelSettings(model=MISTRAL_LARGE_MODEL, reasoning_effort="high"))
        client = _RecordingMistralClient([_fake_stream_event([{"type": "text", "text": "hello"}], finish_reason="stop")])

        async def collect() -> None:
            with patch.object(backend, "_load_system_prompt", return_value="system"), patch.object(
                backend, "_get_client", return_value=client
            ):
                async for _event in backend.stream_reply("chat-main", [ChatMessage("user", "Hello")], self._context()):
                    pass

        asyncio.run(collect())

        self.assertEqual(client.calls[0]["model"], MISTRAL_LARGE_MODEL)
        self.assertNotIn("reasoning_effort", client.calls[0])

    def test_chat_mode_sends_registry_tools_to_mistral(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({MISTRAL_ACCOUNT: "key"}))
        client = _RecordingMistralClient([_fake_stream_event([{"type": "text", "text": "hello"}], finish_reason="stop")])
        tools = provider_tool_specs()

        async def collect() -> None:
            with patch.object(backend, "_load_system_prompt", return_value="system"), patch.object(
                backend, "_get_client", return_value=client
            ):
                async for _event in backend.stream_reply(
                    "chat-main",
                    [ChatMessage("user", "Search the project")],
                    self._context(),
                    tools=tools,
                ):
                    pass

        asyncio.run(collect())

        self.assertEqual(client.calls[0]["tool_choice"], "auto")
        self.assertFalse(client.calls[0]["parallel_tool_calls"])
        tool_names = [tool["function"]["name"] for tool in client.calls[0]["tools"]]
        self.assertIn("search_documents", tool_names)
        self.assertIn("add_document_to_basket", tool_names)

    def test_mistral_tool_call_is_emitted_as_tool_event(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({MISTRAL_ACCOUNT: "key"}))
        tool_call = {
            "id": "call-search",
            "type": "function",
            "function": {"name": "search_documents", "arguments": '{"query": "leadership"}'},
        }
        client = _RecordingMistralClient([_fake_stream_event(None, finish_reason="tool_calls", tool_calls=[tool_call])])

        async def collect() -> list[ChatEvent]:
            with patch.object(backend, "_load_system_prompt", return_value="system"), patch.object(
                backend, "_get_client", return_value=client
            ):
                return [
                    event
                    async for event in backend.stream_reply(
                        "chat-main",
                        [ChatMessage("user", "Find leadership")],
                        self._context(),
                        tools=provider_tool_specs(),
                    )
                ]

        events = asyncio.run(collect())

        self.assertEqual([event.kind for event in events], ["tool_call"])
        self.assertEqual(events[0].tool_call.tool_name, "search_documents")
        self.assertEqual(events[0].tool_call.arguments, {"query": "leadership"})

    def test_reasoning_chunks_are_emitted_separately_from_answer_text(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({MISTRAL_ACCOUNT: "key"}))
        save_mistral_model_settings(MistralModelSettings(model=DEFAULT_MISTRAL_MODEL, reasoning_effort="high"))
        chunks = [
            {"type": "thinking", "thinking": [{"type": "text", "text": "thinking "}]},
            {"type": "text", "text": "answer"},
        ]
        client = _RecordingMistralClient([_fake_stream_event(chunks, finish_reason="stop")])

        async def collect() -> list[ChatEvent]:
            with patch.object(backend, "_load_system_prompt", return_value="system"), patch.object(
                backend, "_get_client", return_value=client
            ):
                return [
                    event
                    async for event in backend.stream_reply("chat-main", [ChatMessage("user", "Hello")], self._context())
                ]

        events = asyncio.run(collect())

        self.assertEqual(events[0], ChatEvent(kind="reasoning_delta", text="thinking "))
        self.assertEqual(events[1], ChatEvent(kind="assistant_delta", text="answer"))
        self.assertEqual(events[2].kind, "assistant_done")
        self.assertEqual(events[2].replay_content, chunks)

    def test_build_messages_replays_full_mistral_reasoning_for_assistant_turns(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({MISTRAL_ACCOUNT: "key"}))
        replay = [{"type": "thinking", "thinking": "hidden"}, {"type": "text", "text": "visible"}]

        payload = backend._build_messages(
            "system",
            [ChatMessage("user", "Hello"), ChatMessage("assistant", "visible", provider_content=replay)],
            self._context(),
            "chat",
        )

        self.assertEqual(payload[-1]["role"], "assistant")
        self.assertEqual(payload[-1]["content"], replay)

    def test_provider_tool_replay_uses_flattened_tool_call_metadata(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({MISTRAL_ACCOUNT: "key"}))
        messages = [
            ChatMessage("user", "Find leadership"),
            ChatMessage(
                "assistant",
                "",
                provider_content={
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "call-search",
                            "type": "function",
                            "function": {"name": "search_documents", "arguments": '{"query": "leadership"}'},
                        }
                    ],
                },
            ),
            ChatMessage(
                "tool",
                "Completed: Search found.",
                provider_content={
                    "role": "tool",
                    "name": "search_documents",
                    "content": "Completed: Search found.",
                    "tool_call_id": "call-search",
                },
            ),
        ]
        payload = backend._build_messages("system", messages, self._context(), "chat")
        _system, conversation = backend._provider_system_and_messages("system", payload)

        local_messages = backend._local_openai_messages(payload)
        self.assertEqual(local_messages[-2]["tool_calls"][0]["id"], "call-search")
        self.assertEqual(local_messages[-2]["tool_calls"][0]["function"]["name"], "search_documents")
        self.assertEqual(local_messages[-1]["tool_call_id"], "call-search")

        claude_messages = backend._claude_messages(conversation)
        self.assertEqual(claude_messages[-2]["content"][0]["id"], "call-search")
        self.assertEqual(claude_messages[-2]["content"][0]["name"], "search_documents")
        self.assertEqual(claude_messages[-1]["content"][0]["tool_use_id"], "call-search")

        google_contents = backend._google_contents(conversation)
        self.assertEqual(google_contents[-2]["parts"][0]["functionCall"]["name"], "search_documents")
        self.assertEqual(google_contents[-1]["parts"][0]["functionResponse"]["name"], "search_documents")

        openai_input = backend._openai_responses_input(conversation)
        self.assertEqual(openai_input[-2]["call_id"], "call-search")
        self.assertEqual(openai_input[-2]["name"], "search_documents")
        self.assertEqual(openai_input[-1]["call_id"], "call-search")

    def test_mistral_reasoning_replay_is_normalized_for_next_turn(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({MISTRAL_ACCOUNT: "key"}))

        parsed = backend._parse_content(
            [
                {"type": "thinking", "thinking": "hidden reasoning"},
                {"type": "text", "text": "visible answer"},
            ]
        )

        self.assertEqual(parsed.reasoning, "hidden reasoning")
        self.assertEqual(parsed.text, "visible answer")
        self.assertEqual(
            parsed.replay_parts,
            (
                {"type": "thinking", "thinking": [{"type": "text", "text": "hidden reasoning"}]},
                {"type": "text", "text": "visible answer"},
            ),
        )

    def test_mistral_streamed_answer_text_replays_as_text_chunk(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore({MISTRAL_ACCOUNT: "key"}))

        parsed = backend._parse_content("visible answer")

        self.assertEqual(parsed.reasoning, "")
        self.assertEqual(parsed.text, "visible answer")
        self.assertEqual(parsed.replay_parts, ({"type": "text", "text": "visible answer"},))

    def test_rate_limit_error_is_formatted_without_raw_provider_json(self) -> None:
        class RateLimitedChat:
            async def stream_async(self, **_kwargs):
                raise RuntimeError(
                    'status_code: 429 body: {"message":"rate limit exceeded","type":"rate_limit","retry_after":60}'
                )

        class RateLimitedClient:
            chat = RateLimitedChat()

        async def collect_errors() -> list[ChatEvent]:
            backend = MistralChatBackend(credential_store=InMemoryCredentialStore({MISTRAL_ACCOUNT: "key"}))
            with patch.object(backend, "_load_system_prompt", return_value="system"), patch.object(
                backend, "_get_client", return_value=RateLimitedClient()
            ):
                return [
                    event
                    async for event in backend.stream_reply(
                        "chat-main",
                        [ChatMessage("user", "Hello")],
                        self._context(),
                    )
                ]

        events = asyncio.run(collect_errors())
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].kind, "error")
        self.assertIn("Mistral rate limit reached", events[0].error)
        self.assertIn("about 1 minute", events[0].error)
        self.assertNotIn("status_code", events[0].error)
        self.assertNotIn('{"message"', events[0].error)

    def test_non_rate_limit_provider_error_is_redacted(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore())
        error = backend._format_provider_error(
            RuntimeError('status_code: 500 body: {"api_key":"secret-key","prompt":"raw prompt text"}')
        )

        self.assertIn("Mistral request failed", error)
        self.assertNotIn("status_code", error)
        self.assertNotIn("secret-key", error)
        self.assertNotIn("raw prompt text", error)
        self.assertNotIn('{"api_key"', error)

    def test_auth_provider_error_tells_user_to_replace_key_without_raw_json(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore())
        error = backend._format_provider_error(RuntimeError('status_code: 401 body: {"detail":"Unauthorized"}'))

        self.assertIn("Mistral rejected this API key", error)
        self.assertNotIn("status_code", error)
        self.assertNotIn("Unauthorized", error)
        self.assertNotIn('{"detail"', error)

    def test_system_prompt_override_is_ignored_outside_local_developer_mode(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore())
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.md"
            prompt_path.write_text("Unsafe override prompt", encoding="utf-8")
            previous_prompt = os.environ.get("EXEGESIS_SYSTEM_PROMPT_PATH")
            os.environ["EXEGESIS_SYSTEM_PROMPT_PATH"] = str(prompt_path)
            os.environ.pop(LOCAL_DEVELOPER_ENV, None)
            try:
                self.assertEqual(backend._system_prompt_path(), DEFAULT_SYSTEM_PROMPT_PATH)
            finally:
                if previous_prompt is None:
                    os.environ.pop("EXEGESIS_SYSTEM_PROMPT_PATH", None)
                else:
                    os.environ["EXEGESIS_SYSTEM_PROMPT_PATH"] = previous_prompt

    def test_loads_system_prompt_from_file(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore())
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.md"
            prompt_path.write_text("System prompt", encoding="utf-8")
            previous_prompt = os.environ.get("EXEGESIS_SYSTEM_PROMPT_PATH")
            os.environ["EXEGESIS_SYSTEM_PROMPT_PATH"] = str(prompt_path)
            os.environ[LOCAL_DEVELOPER_ENV] = "1"
            try:
                self.assertEqual(backend._load_system_prompt(), "System prompt")
            finally:
                if previous_prompt is None:
                    os.environ.pop("EXEGESIS_SYSTEM_PROMPT_PATH", None)
                else:
                    os.environ["EXEGESIS_SYSTEM_PROMPT_PATH"] = previous_prompt

    def test_missing_prompt_file_raises_clear_error(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore())
        previous_prompt = os.environ.get("EXEGESIS_SYSTEM_PROMPT_PATH")
        os.environ["EXEGESIS_SYSTEM_PROMPT_PATH"] = str(DEFAULT_SYSTEM_PROMPT_PATH.parent / "missing.md")
        os.environ[LOCAL_DEVELOPER_ENV] = "1"
        try:
            with self.assertRaisesRegex(RuntimeError, "System prompt is unavailable"):
                backend._load_system_prompt()
        finally:
            if previous_prompt is None:
                os.environ.pop("EXEGESIS_SYSTEM_PROMPT_PATH", None)
            else:
                os.environ["EXEGESIS_SYSTEM_PROMPT_PATH"] = previous_prompt

    def test_rewrite_messages_include_selected_text_and_scope_guard(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore())
        context = ShellChatContext(
            project_name="Test Project",
            document_title="current_draft.md",
            document_type="draft",
            document_content="# Draft\n\nKeep this context.",
            confidentiality_mode="online",
            basket_context="",
            selected_text="Only this sentence should change.",
            selection_start=9,
            selection_end=42,
        )
        payload = backend._build_messages(
            "Base system prompt",
            [ChatMessage("user", "Make it sharper.")],
            context,
            "rewrite",
        )
        joined = "\n\n".join(str(message["content"]) for message in payload)
        self.assertIn("<selected_text>\nOnly this sentence should change.\n</selected_text>", joined)
        self.assertIn("Character range: 9-42", joined)
        self.assertIn("Do not rewrite or summarize the whole document", joined)

    def test_transcript_content_is_not_sent_as_current_document_context(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore())
        context = ShellChatContext(
            project_name="Test Project",
            document_title="Transcript 1",
            document_type="transcript",
            document_content="Sensitive full transcript text should stay out.",
            confidentiality_mode="online",
            basket_context="",
        )
        payload = backend._build_messages("Base system prompt", [ChatMessage("user", "Summarize it.")], context, "chat")
        joined = "\n\n".join(str(message["content"]) for message in payload)
        self.assertNotIn("Sensitive full transcript text should stay out.", joined)
        self.assertIn(
            "<current_document>\n"
            "[Transcript metadata only. The full transcript text is intentionally withheld because this is a "
            "non-confidential project. Do not claim to know, summarize, quote, analyze, or answer questions about "
            "the transcript content unless the user provides excerpts, selected text, snippets, or search results "
            "in this chat.]\n"
            "</current_document>",
            joined,
        )
        self.assertIn("Transcript context policy: full transcript text is not available", joined)
        self.assertIn("start the response by saying the full transcript is withheld in non-confidential mode", joined)
        self.assertIn("Do not ask how you can assist with the transcript", joined)
        self.assertIn("Ask how you can assist with the project", joined)
        self.assertNotIn("<current_document>\n(empty document)\n</current_document>", joined)

    def test_confidential_project_sends_transcript_content_as_current_document_context(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore())
        context = ShellChatContext(
            project_name="Test Project",
            document_title="Transcript 1",
            document_type="transcript",
            document_content="Sensitive full transcript text can be used locally.",
            confidentiality_mode="local-confidential",
            basket_context="",
        )

        payload = backend._build_messages("Base system prompt", [ChatMessage("user", "Summarize it.")], context, "chat")
        joined = "\n\n".join(str(message["content"]) for message in payload)

        self.assertIn("Sensitive full transcript text can be used locally.", joined)
        self.assertNotIn("Transcript metadata only", joined)
        self.assertNotIn("full transcript text is intentionally withheld", joined)

    def test_notebook_prompt_labels_withheld_transcript_context(self) -> None:
        workflow = WorkflowPane(FakeBackend(configured=True))
        context = ShellChatContext(
            project_name="Test Project",
            document_title="Transcript 1",
            document_type="transcript",
            document_content="Sensitive full transcript text should stay out.",
            confidentiality_mode="online",
            basket_context="",
        )

        prompt = workflow._shell_context_prompt_text(context, "chat")

        self.assertNotIn("Sensitive full transcript text should stay out.", prompt)
        self.assertIn("Transcript metadata only", prompt)
        self.assertIn("Mode: chat", prompt)
        self.assertNotIn("Mistral", prompt)

    def test_build_messages_lists_available_document_sections_for_tool_targeting(self) -> None:
        backend = MistralChatBackend(credential_store=InMemoryCredentialStore())
        context = ShellChatContext(
            project_name="Test Project",
            document_title="current_draft.md",
            document_type="draft",
            document_content="# Paper\n\n## Abstract\n\nExisting abstract.\n\n## Introduction\n\nIntro body.",
            confidentiality_mode="online",
            basket_context="",
        )

        payload = backend._build_messages("Base system prompt", [ChatMessage("user", "Write an abstract.")], context, "chat")
        joined = "\n\n".join(str(message["content"]) for message in payload)

        self.assertIn("Available document sections:", joined)
        self.assertIn("- Paper", joined)
        self.assertIn("- Abstract", joined)
        self.assertIn("- Introduction", joined)
        self.assertIn("set insert_after_heading", joined)

    def _context(self) -> ShellChatContext:
        return ShellChatContext(
            project_name="Demo",
            document_title="current_draft.md",
            document_type="draft",
            document_content="Draft text.",
            confidentiality_mode="online",
            basket_context="",
        )


class _RecordingMistralStream:
    def __init__(self, events: list[object]) -> None:
        self._events = events
        self.response = Mock()
        self.response.aclose = Mock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    def __aiter__(self):
        self._iter = iter(self._events)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration


class _RecordingMistralChat:
    def __init__(self, events: list[object]) -> None:
        self._events = events
        self.calls: list[dict[str, object]] = []
        self.complete_calls: list[dict[str, object]] = []

    async def stream_async(self, **kwargs):
        self.calls.append(kwargs)
        return _RecordingMistralStream(self._events)

    async def complete_async(self, **kwargs):
        self.complete_calls.append(kwargs)
        return Mock()


class _RecordingMistralClient:
    def __init__(self, events: list[object]) -> None:
        self.chat = _RecordingMistralChat(events)

    @property
    def calls(self) -> list[dict[str, object]]:
        return self.chat.calls

    @property
    def complete_calls(self) -> list[dict[str, object]]:
        return self.chat.complete_calls


def _fake_stream_event(content: object, *, finish_reason: str | None = None, tool_calls: object | None = None):
    delta = Mock()
    delta.content = content
    delta.tool_calls = tool_calls
    choice = Mock()
    choice.delta = delta
    choice.finish_reason = finish_reason
    choice.message = None
    data = Mock()
    data.choices = [choice]
    event = Mock()
    event.data = data
    return event


class WorkflowPaneChatTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_key_keeps_model_actions_clickable(self) -> None:
        app = WorkflowTestApp(FakeBackend(configured=False))
        async with app.run_test() as pilot:
            await pilot.pause()
            send = app.query_one(f"#{WORKFLOW_SEND_ID}", Button)
            draft = app.query_one(f"#{WORKFLOW_DRAFT_ID}", Button)
            rewrite = app.query_one(f"#{WORKFLOW_REWRITE_SELECTION_ID}", Button)
            search = app.query_one(f"#{WORKFLOW_SEARCH_ID}", Button)
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            self.assertFalse(send.disabled)
            self.assertFalse(draft.disabled)
            self.assertFalse(rewrite.disabled)
            self.assertFalse(composer.disabled)
            self.assertFalse(search.disabled)

    async def test_send_streams_into_active_chat(self) -> None:
        app = WorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "Say hello"
            workflow = app.query_one(WorkflowPane)
            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()
            transcript = workflow.active_chat.messages[-1].content
            self.assertEqual(transcript, "hello world")
            self.assertFalse(workflow.active_chat.generating)
            self.assertEqual(app._backend.last_mode, "chat")
            self.assertEqual(app._backend.last_context.document_type, "draft")
            rendered_text_entries = [
                (entry.role, entry.content) for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryTextEntry)
            ]
            self.assertEqual(rendered_text_entries[-2:], [("user", "Say hello"), ("assistant", "hello world")])

    async def test_composer_up_down_recalls_sent_message_history(self) -> None:
        app = WorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            workflow = app.query_one(WorkflowPane)

            composer.value = "First message"
            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()
            composer.value = "Second message"
            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()

            composer.value = "unsent draft"
            composer.focus()
            await pilot.press("up")
            self.assertEqual(composer.value, "Second message")
            await pilot.press("up")
            self.assertEqual(composer.value, "First message")
            await pilot.press("down")
            self.assertEqual(composer.value, "Second message")
            await pilot.press("down")
            self.assertEqual(composer.value, "unsent draft")

    async def test_composer_history_is_per_chat(self) -> None:
        app = WorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            workflow = app.query_one(WorkflowPane)

            composer.value = "Main chat message"
            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()
            await workflow.new_chat()
            await pilot.pause()

            composer.value = "secondary draft"
            composer.focus()
            await pilot.press("up")

            self.assertEqual(composer.value, "secondary draft")

    async def test_send_shows_thinking_card_without_provider_reasoning_deltas(self) -> None:
        app = WorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "Say hello"
            workflow = app.query_one(WorkflowPane)

            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()

            reasoning_entries = [entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryReasoningEntry)]
            self.assertEqual(len(reasoning_entries), 1)
            self.assertEqual(reasoning_entries[0].content, "")
            self.assertFalse(reasoning_entries[0].streaming)
            card_text = "\n".join(str(widget.render()) for widget in workflow.query_one(".workflow-reasoning-card").query(Static))
            self.assertIn("Thinking complete", card_text)
            self.assertIn("Click to reveal reasoning trace.", card_text)
            self.assertIn("No provider-exposed thinking text", workflow._rendered_history_text(workflow.active_chat))

    async def test_send_finalizes_when_backend_stream_omits_done_event(self) -> None:
        app = WorkflowTestApp(NoDoneBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "Say hello"
            workflow = app.query_one(WorkflowPane)

            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()
            await pilot.pause()

            self.assertEqual(workflow.active_chat.messages[-1].content, "completed without explicit done")
            self.assertFalse(workflow.active_chat.generating)
            self.assertFalse(app.query_one(f"#{WORKFLOW_SEND_ID}", Button).disabled)
            self.assertFalse(app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input).disabled)

    async def test_normal_chat_can_auto_run_read_only_search_tool(self) -> None:
        tool_call = ToolCallRequest(
            provider="mistral",
            tool_name="search_documents",
            arguments={"query": "leadership"},
            raw_call_id="call-search",
        )
        backend = ToolCallBackend(tool_call, follow_up="I found matching context.")
        app = WorkflowActionDispatchTestApp(backend)

        async with app.run_test() as pilot:
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "Find leadership examples"
            workflow = app.query_one(WorkflowPane)

            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()
            await pilot.pause()
            await pilot.pause()

            self.assertEqual(app.dispatched_actions[0][0], "search_documents")
            self.assertEqual(app.dispatched_actions[0][2], "model_tool")
            self.assertIsNotNone(backend.seen_tools[0])
            self.assertIsNone(backend.seen_tools[1])
            entries = workflow.active_chat.history_entries
            self.assertFalse(any(isinstance(entry, HistoryActionResultEntry) for entry in entries))
            self.assertTrue(any(isinstance(entry, HistorySearchEntry) for entry in entries))
            self.assertIn("I found matching context.", workflow.active_chat.messages[-1].content)
            transcript = workflow._rendered_history_text(workflow.active_chat)
            self.assertIn('### Search: "leadership"', transcript)
            self.assertNotIn("raw_provider", transcript)

    async def test_tool_follow_up_reasoning_and_text_are_transcript_only(self) -> None:
        tool_call = ToolCallRequest(
            provider="mistral",
            tool_name="search_documents",
            arguments={"query": "leadership"},
            raw_call_id="call-search",
        )
        app = WorkflowActionDispatchTestApp(ToolCallWithReasoningFollowUpBackend(tool_call))

        async with app.run_test() as pilot:
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "Find leadership examples"
            workflow = app.query_one(WorkflowPane)

            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()
            await pilot.pause()
            await pilot.pause()

            history = workflow._history_for_slug(workflow.active_chat.slug)
            rendered_sources = [widget.source_entry for widget in history.children if hasattr(widget, "source_entry")]
            self.assertFalse(any(isinstance(entry, HistoryReasoningEntry) for entry in rendered_sources))
            self.assertFalse(
                any(
                    isinstance(entry, HistoryTextEntry)
                    and entry.role == "assistant"
                    and "Tool follow-up answer" in entry.content
                    for entry in rendered_sources
                )
            )
            transcript = workflow._rendered_history_text(workflow.active_chat)
            self.assertIn("### Reasoning Trace", transcript)
            self.assertIn("tool follow-up thinking", transcript)
            self.assertIn("**Assistant:**\n\nTool follow-up answer.", transcript)

    async def test_proposal_auto_tool_call_defers_to_proposal_flow_without_success_card(self) -> None:
        tool_call = ToolCallRequest(
            provider="mistral",
            tool_name="draft_into_document",
            arguments={"instruction": "Draft an abstract.", "insert_after_heading": "Abstract"},
            raw_call_id="call-draft",
        )
        app = WorkflowActionDispatchTestApp(ToolCallBackend(tool_call))

        async with app.run_test() as pilot:
            await pilot.pause()
            app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input).value = "Draft an abstract"
            workflow = app.query_one(WorkflowPane)

            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()
            await pilot.pause()

            self.assertEqual(app.dispatched_actions[-1][0], "draft_into_document")
            self.assertFalse(any(isinstance(entry, HistoryActionResultEntry) for entry in workflow.active_chat.history_entries))
            visible_user_entries = [
                entry
                for entry in workflow.active_chat.history_entries
                if isinstance(entry, HistoryTextEntry) and entry.role == "user" and entry.visible
            ]
            self.assertEqual([entry.content for entry in visible_user_entries], ["Draft an abstract"])
            self.assertEqual(workflow.active_chat.command_history, ["Draft an abstract"])

    async def test_tool_call_discards_streamed_preamble_text_before_action(self) -> None:
        tool_call = ToolCallRequest(
            provider="mistral",
            tool_name="draft_into_document",
            arguments={"instruction": "Draft an abstract.", "insert_after_heading": "Abstract"},
            raw_call_id="call-draft",
        )
        app = WorkflowActionDispatchTestApp(ToolCallWithPreambleBackend(tool_call))

        async with app.run_test() as pilot:
            await pilot.pause()
            app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input).value = "Draft an abstract"
            workflow = app.query_one(WorkflowPane)

            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()
            await pilot.pause()

            self.assertEqual(app.dispatched_actions[-1][0], "draft_into_document")
            self.assertFalse(
                any(
                    "more detailed prompt" in message.content
                    for message in workflow.active_chat.messages
                    if message.role == "assistant"
                )
            )
            self.assertFalse(
                any(
                    isinstance(entry, HistoryTextEntry)
                    and entry.role == "assistant"
                    and "more detailed prompt" in entry.content
                    for entry in workflow.active_chat.history_entries
                )
            )
            visible_user_entries = [
                entry
                for entry in workflow.active_chat.history_entries
                if isinstance(entry, HistoryTextEntry) and entry.role == "user" and entry.visible
            ]
            self.assertEqual([entry.content for entry in visible_user_entries], ["Draft an abstract"])

    async def test_tool_call_hides_streamed_preamble_while_dispatching(self) -> None:
        tool_call = ToolCallRequest(
            provider="mistral",
            tool_name="search_documents",
            arguments={"query": "leadership"},
            raw_call_id="call-search",
        )
        app = SlowWorkflowActionDispatchTestApp(ToolCallWithPreambleBackend(tool_call))

        async with app.run_test() as pilot:
            await pilot.pause()
            app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input).value = "Find leadership examples"
            workflow = app.query_one(WorkflowPane)

            workflow.send_active_message()
            await asyncio.wait_for(app.dispatch_started.wait(), timeout=2)
            await pilot.pause()
            history = workflow._history_for_slug(workflow.active_chat.slug)
            rendered_sources = [widget.source_entry for widget in history.children if hasattr(widget, "source_entry")]

            self.assertFalse(
                any(
                    isinstance(entry, HistoryTextEntry)
                    and "more detailed prompt" in entry.content
                    for entry in rendered_sources
                )
            )
            self.assertFalse(any(isinstance(entry, HistoryReasoningEntry) for entry in rendered_sources))

            app.dispatch_release.set()
            await pilot.pause()
            await pilot.pause()
            self.assertEqual(app.dispatched_actions[0][0], "search_documents")

    async def test_tool_call_preamble_stays_hidden_before_tool_arrives(self) -> None:
        tool_call = ToolCallRequest(
            provider="mistral",
            tool_name="search_documents",
            arguments={"query": "leadership"},
            raw_call_id="call-search",
        )
        backend = DelayedToolCallWithPreambleBackend(tool_call)
        app = WorkflowActionDispatchTestApp(backend)

        async with app.run_test() as pilot:
            await pilot.pause()
            app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input).value = "Find leadership examples"
            workflow = app.query_one(WorkflowPane)

            workflow.send_active_message()
            await asyncio.wait_for(backend.preamble_sent.wait(), timeout=2)
            await pilot.pause()
            history = workflow._history_for_slug(workflow.active_chat.slug)
            rendered_sources = [widget.source_entry for widget in history.children if hasattr(widget, "source_entry")]

            self.assertFalse(
                any(
                    isinstance(entry, HistoryTextEntry)
                    and "more detailed prompt" in entry.content
                    for entry in rendered_sources
                )
            )

            backend.release_tool_call.set()
            for _ in range(12):
                await pilot.pause()
                if not workflow.active_chat.generating:
                    break
            self.assertEqual(app.dispatched_actions[0][0], "search_documents")

    async def test_follow_up_ignores_recursive_tool_call_from_provider(self) -> None:
        tool_call = ToolCallRequest(
            provider="mistral",
            tool_name="search_documents",
            arguments={"query": "leadership"},
            raw_call_id="call-search",
        )
        app = WorkflowActionDispatchTestApp(ToolCallWithPreambleBackend(tool_call))

        async with app.run_test() as pilot:
            await pilot.pause()
            app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input).value = "Find leadership examples"
            workflow = app.query_one(WorkflowPane)

            workflow.send_active_message()
            for _ in range(12):
                await pilot.pause()
                if not workflow.active_chat.generating:
                    break

            self.assertFalse(workflow.active_chat.generating)
            self.assertEqual([action[0] for action in app.dispatched_actions], ["search_documents"])
            self.assertEqual(
                sum(isinstance(entry, HistoryActionResultEntry) for entry in workflow.active_chat.history_entries),
                0,
            )
            self.assertEqual(
                sum(isinstance(entry, HistorySearchEntry) for entry in workflow.active_chat.history_entries),
                1,
            )
            history = workflow._history_for_slug(workflow.active_chat.slug)
            rendered_sources = [widget.source_entry for widget in history.children if hasattr(widget, "source_entry")]
            self.assertFalse(
                any(
                    isinstance(entry, HistoryTextEntry)
                    and "more detailed prompt" in entry.content
                    for entry in rendered_sources
                )
            )

    def test_action_result_card_uses_capitalized_compact_status_body(self) -> None:
        card = ActionResultCard(HistoryActionResultEntry("rename_project", "Rename project", "completed", "Renamed project."))
        widgets = list(card.compose())
        body = widgets[1]

        self.assertEqual(str(body.render()), "Completed: Renamed project.")
        self.assertTrue(body.has_class("workflow-action-result-body"))

    def test_action_request_card_hides_empty_private_payload_details(self) -> None:
        card = ActionRequestCard(
            HistoryActionRequestEntry(
                "compact_chat",
                "Compact chat",
                "Compact chat requires confirmation before Exegesis changes project state.",
                payload={"_raw": "", "note": None},
            )
        )

        rendered = card._payload_summary()

        self.assertNotIn("_raw", rendered)
        self.assertNotIn("- note", rendered)
        self.assertEqual(rendered, "")

    async def test_confirm_required_tool_call_renders_action_request(self) -> None:
        tool_call = ToolCallRequest(
            provider="mistral",
            tool_name="add_document_to_basket",
            arguments={},
            raw_call_id="call-basket",
        )
        app = WorkflowActionDispatchTestApp(ToolCallBackend(tool_call))

        async with app.run_test() as pilot:
            await pilot.pause()
            app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input).value = "Add this document to the basket"
            workflow = app.query_one(WorkflowPane)

            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()
            await pilot.pause()

            request_entries = [entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryActionRequestEntry)]
            self.assertEqual(len(request_entries), 1)
            self.assertEqual(request_entries[0].action_id, "add_document_to_basket")
            self.assertIsNotNone(workflow.query_one("#action-request-confirm", Button))

            await workflow.on_action_request_card_confirm_requested(ActionRequestCard.ConfirmRequested(ActionRequestCard(request_entries[0]), request_entries[0]))
            self.assertEqual(app.dispatched_actions[-1], ("add_document_to_basket", {}, "model_tool", True))
            self.assertTrue(any(isinstance(entry, HistoryActionResultEntry) for entry in workflow.active_chat.history_entries))

    async def test_refused_confirm_required_tool_call_renders_action_result(self) -> None:
        tool_call = ToolCallRequest(
            provider="mistral",
            tool_name="add_document_to_basket",
            arguments={"document": "Transcript"},
            raw_call_id="call-transcript",
        )
        app = WorkflowActionDispatchTestApp(ToolCallBackend(tool_call))

        async with app.run_test() as pilot:
            await pilot.pause()
            app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input).value = "Add the transcript to the basket"
            workflow = app.query_one(WorkflowPane)

            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()
            await pilot.pause()

            self.assertFalse(
                any(isinstance(entry, HistoryActionRequestEntry) for entry in workflow.active_chat.history_entries)
            )
            result_entries = [
                entry
                for entry in workflow.active_chat.history_entries
                if isinstance(entry, HistoryActionResultEntry)
            ]
            self.assertEqual(len(result_entries), 1)
            self.assertEqual(result_entries[0].action_id, "add_document_to_basket")
            self.assertEqual(result_entries[0].status, "refused")
            self.assertIn("Full transcripts cannot be added", result_entries[0].message)

    async def test_confirm_required_file_conflict_tool_call_renders_card_options(self) -> None:
        tool_call = ToolCallRequest(
            provider="mistral",
            tool_name="update_selected_project_item",
            arguments={"document": "Data Memo 1", "title": "data_memo_1.md", "folder": "memos"},
            raw_call_id="call-update",
        )
        app = WorkflowActionDispatchTestApp(ToolCallBackend(tool_call))

        async with app.run_test() as pilot:
            await pilot.pause()
            app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input).value = "Rename Data Memo 1"
            workflow = app.query_one(WorkflowPane)

            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()
            await pilot.pause()

            request_entries = [entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryActionRequestEntry)]
            self.assertEqual(len(request_entries), 1)
            self.assertEqual(request_entries[0].action_id, "update_selected_project_item")
            self.assertEqual([option["label"] for option in request_entries[0].options], ["Replace", "Rename", "Cancel"])
            self.assertEqual(request_entries[0].input_name, "duplicate_title")

            renamed_entry = replace(
                request_entries[0],
                payload={**request_entries[0].payload, "duplicate_action": "rename", "duplicate_title": "renamed_memo.md"},
            )
            await workflow.on_action_request_card_confirm_requested(ActionRequestCard.ConfirmRequested(ActionRequestCard(renamed_entry), renamed_entry))
            self.assertEqual(
                app.dispatched_actions[-1],
                (
                    "update_selected_project_item",
                    {
                        "document": "Data Memo 1",
                        "title": "data_memo_1.md",
                        "folder": "memos",
                        "duplicate_action": "rename",
                        "duplicate_title": "renamed_memo.md",
                    },
                    "model_tool",
                    True,
                ),
            )
            self.assertFalse(any(isinstance(entry, HistoryActionRequestEntry) for entry in workflow.active_chat.history_entries))
            self.assertTrue(any(isinstance(entry, HistoryActionResultEntry) for entry in workflow.active_chat.history_entries))

            dispatch_count = len(app.dispatched_actions)
            await workflow.on_action_request_card_confirm_requested(ActionRequestCard.ConfirmRequested(ActionRequestCard(renamed_entry), renamed_entry))
            self.assertEqual(len(app.dispatched_actions), dispatch_count)
            self.assertFalse(any(isinstance(entry, HistoryActionRequestEntry) for entry in workflow.active_chat.history_entries))

    async def test_system_only_tool_call_is_refused_without_dispatch(self) -> None:
        tool_call = ToolCallRequest(provider="mistral", tool_name="model_settings", arguments={}, raw_call_id="call-settings")
        app = WorkflowActionDispatchTestApp(ToolCallBackend(tool_call))

        async with app.run_test() as pilot:
            await pilot.pause()
            app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input).value = "Open model settings"
            workflow = app.query_one(WorkflowPane)

            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()
            await pilot.pause()

            self.assertEqual(app.dispatched_actions, [])
            results = [entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryActionResultEntry)]
            self.assertEqual(results[-1].status, "refused")
            self.assertIn("must be invoked manually", results[-1].message)

    async def test_reasoning_trace_renders_separately_from_assistant_answer(self) -> None:
        app = WorkflowTestApp(ReasoningBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "Explain your answer"
            workflow = app.query_one(WorkflowPane)

            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()

            entries = workflow.active_chat.history_entries
            self.assertTrue(any(isinstance(entry, HistoryReasoningEntry) for entry in entries))
            self.assertEqual(workflow.active_chat.messages[-1].content, "answer")
            self.assertEqual(
                workflow.active_chat.messages[-1].provider_content,
                [{"type": "thinking", "thinking": "reasoning "}, {"type": "text", "text": "answer"}],
            )
            card_text = "\n".join(str(widget.render()) for widget in workflow.query_one(".workflow-reasoning-card").query(Static))
            self.assertIn("Thinking complete", card_text)
            self.assertIn("Click to reveal reasoning trace.", card_text)
            transcript = workflow._rendered_history_text(workflow.active_chat)
            self.assertIn("### Reasoning Trace", transcript)
            self.assertIn("reasoning", transcript)
            self.assertIn("**Assistant:**\n\nanswer", transcript)

    async def test_send_warns_immediately_when_active_transcript_is_withheld(self) -> None:
        app = WorkflowTranscriptTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "What can you do with this transcript?"
            workflow = app.query_one(WorkflowPane)

            workflow.send_active_message()
            await pilot.pause()
            await pilot.pause()

            rendered_entries = [
                entry
                for entry in workflow.active_chat.history_entries
                if isinstance(entry, (HistoryTextEntry, HistoryStatusEntry))
            ][-2:]
            self.assertEqual([type(entry) for entry in rendered_entries], [HistoryTextEntry, HistoryStatusEntry])
            self.assertEqual(rendered_entries[1].content, NON_CONFIDENTIAL_TRANSCRIPT_WARNING)
            self.assertIsNone(app._backend.last_context)

    async def test_search_prompt_while_transcript_open_does_not_trigger_withheld_warning(self) -> None:
        tool_call = ToolCallRequest(
            provider="mistral",
            tool_name="search_documents",
            arguments={"query": "leadership"},
            raw_call_id="call-search",
        )
        app = WorkflowTranscriptActionDispatchTestApp(ToolCallBackend(tool_call))
        async with app.run_test() as pilot:
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "Find references to leadership"
            workflow = app.query_one(WorkflowPane)

            workflow.send_active_message()
            for _ in range(12):
                await pilot.pause()
                if not workflow.active_chat.generating:
                    break

            self.assertEqual(app.dispatched_actions[0][0], "search_documents")
            self.assertFalse(
                any(
                    isinstance(entry, HistoryStatusEntry)
                    and entry.content == NON_CONFIDENTIAL_TRANSCRIPT_WARNING
                    for entry in workflow.active_chat.history_entries
                )
            )
            self.assertTrue(any(isinstance(entry, HistorySearchEntry) for entry in workflow.active_chat.history_entries))

    async def test_notebook_display_order_is_chronological_with_latest_at_bottom(self) -> None:
        app = WorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            workflow = app.query_one(WorkflowPane)
            original_entries = list(workflow.active_chat.history_entries)
            try:
                workflow.active_chat.history_entries = [
                    HistoryTextEntry("user", "Older question"),
                    HistoryTextEntry("assistant", "Older answer"),
                    HistoryStatusEntry("Middle status"),
                    HistoryTextEntry("user", "Newest question"),
                    HistoryTextEntry("assistant", "Newest answer"),
                ]
                workflow._render_chat(workflow.active_chat.slug)
                await pilot.pause()

                history = workflow._history_for_slug(workflow.active_chat.slug)
                rendered = [widget for widget in history.children if hasattr(widget, "source_entry")]

                self.assertEqual(
                    [
                        (entry.role, entry.content) if isinstance(entry, HistoryTextEntry) else ("status", entry.content)
                        for entry in (widget.source_entry for widget in rendered)
                    ],
                    [
                        ("user", "Older question"),
                        ("assistant", "Older answer"),
                        ("status", "Middle status"),
                        ("user", "Newest question"),
                        ("assistant", "Newest answer"),
                    ],
                )
            finally:
                workflow.active_chat.history_entries = original_entries

    async def test_notebook_context_counter_uses_selected_model_window(self) -> None:
        app = WorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            workflow = app.query_one(WorkflowPane)
            self.assertIn("context used", workflow.border_subtitle or "")
            self.assertIn("/ 256,000 tokens", workflow.border_subtitle or "")
            self.assertNotIn("/ 128,000 tokens", workflow.border_subtitle or "")
            self.assertNotEqual(workflow.border_subtitle, "0% context used (~0 / 256,000 tokens)")

    async def test_notebook_context_counter_includes_current_document_and_basket(self) -> None:
        app = WorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            workflow = app.query_one(WorkflowPane)
            used_with_context = workflow._estimated_used_tokens(workflow.active_chat)

        class EmptyContextApp(WorkflowTestApp):
            def shell_chat_context(self) -> dict[str, str]:
                context = super().shell_chat_context()
                context["document_content"] = ""
                context["basket_context"] = ""
                return context

        empty_app = EmptyContextApp(FakeBackend(configured=True))
        async with empty_app.run_test() as pilot:
            await pilot.pause()
            empty_workflow = empty_app.query_one(WorkflowPane)
            used_without_context = empty_workflow._estimated_used_tokens(empty_workflow.active_chat)

        self.assertGreater(used_with_context, used_without_context)

    async def test_notebook_context_counter_refreshes_when_file_added_to_basket(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            workflow = app.query_one(WorkflowPane)
            before_text = workflow.active_chat.context_available
            before_tokens = workflow._estimated_used_tokens(workflow.active_chat)

            self.assertTrue(app._add_document_slug_to_basket("project-demo-essay"))
            await pilot.pause()

            after_tokens = workflow._estimated_used_tokens(workflow.active_chat)
            self.assertGreater(after_tokens, before_tokens)
            self.assertNotEqual(workflow.active_chat.context_available, before_text)
            self.assertEqual(workflow.border_subtitle, workflow.active_chat.context_available)

    async def test_uncompactable_fixed_context_blocks_send_without_compaction_loop(self) -> None:
        app = WorkflowHugeFixedContextApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            workflow = app.query_one(WorkflowPane)
            composer = workflow.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "Try to use too many basket files."

            workflow.send_active_message()
            await pilot.pause()

            self.assertIsNone(app._backend.last_mode)
            self.assertEqual(composer.value, "Try to use too many basket files.")
            rendered = workflow._rendered_history_text(workflow.active_chat)
            self.assertIn("Request not sent", rendered)
            self.assertIn("Fixed context:", rendered)
            self.assertIn("Compaction only reduces notebook chat history", rendered)
            self.assertNotIn("Compact to Continue", rendered)
            status_entries = [entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryStatusEntry)]
            self.assertTrue(any("\n\nFixed context:" in entry.content for entry in status_entries))
            self.assertIn("remove basket items", workflow._status_message)

    async def test_provider_rate_limit_renders_as_notebook_status_alert(self) -> None:
        app = WorkflowTestApp(RateLimitBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            workflow = app.query_one(WorkflowPane)
            composer = workflow.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "Try a rate-limited request"

            workflow.send_active_message()
            await pilot.pause()

            rendered = workflow._rendered_history_text(workflow.active_chat)
            self.assertIn("Mistral rate limit reached", rendered)
            self.assertIn("Try again in about 1 minute", rendered)
            self.assertNotIn("status_code", rendered)
            self.assertNotIn('{"message"', rendered)
            status_entries = [entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryStatusEntry)]
            self.assertTrue(any("Mistral rate limit reached" in entry.content for entry in status_entries))
            self.assertEqual(workflow._status_message.splitlines()[0], "Mistral rate limit reached.")

    async def test_draft_button_streams_draft_mode(self) -> None:
        app = WorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "Draft a stronger opening"
            app.query_one(WorkflowPane).draft_into_document()
            await pilot.pause()
            self.assertEqual(app._backend.last_mode, "draft")
            self.assertIn("Seed context", app._backend.last_context.basket_context)

    async def test_chat_write_intent_routes_to_draft_mode(self) -> None:
        original = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content
        target_document = "# Paper\n\n## Abstract\n\n## Introduction\n\nIntro body."
        try:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = target_document
            app = WorkflowDraftTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await pilot.pause()
                composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                composer.value = "Write an abstract"

                app.query_one(WorkflowPane).send_active_message()
                await pilot.pause()
                await pilot.pause()
                await pilot.pause()

                self.assertEqual(app._backend.last_mode, "draft")
                self.assertTrue(app.query_one(DocumentPane).has_pending_preview(CURRENT_DRAFT_SLUG))
                draft_cards = [
                    entry for entry in app.query_one(WorkflowPane).active_chat.history_entries if isinstance(entry, HistoryRewriteEntry)
                ]
                self.assertEqual(len(draft_cards), 1)
                self.assertTrue(draft_cards[0].patch_id.startswith("draft-"))
                start = target_document.index("## Abstract") + len("## Abstract\n")
                end = target_document.index("## Introduction")
                self.assertEqual(draft_cards[0].target_range, (start, end))
                self.assertTrue(draft_cards[0].block_insert)

                applied = app.query_one(DocumentPane).apply_pending_rewrite(draft_cards[0].patch_id)
                self.assertIsNotNone(applied)
                self.assertIn("## Abstract\n\nDrafted paragraph.\n\n## Introduction", DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content)
        finally:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = original

    async def test_chat_selection_edit_intent_routes_to_rewrite_mode(self) -> None:
        original = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content
        try:
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await pilot.pause()
                composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                composer.value = "Make it shorter"

                app.query_one(WorkflowPane).send_active_message()
                await pilot.pause()
                await pilot.pause()
                await pilot.pause()

                self.assertEqual(app._backend.last_mode, "rewrite")
                self.assertIsNotNone(app._backend.last_context)
                self.assertEqual(app._backend.last_context.selected_text, "# Cur")
                self.assertEqual(app._backend.last_context.selection_start, 0)
                self.assertEqual(app._backend.last_context.selection_end, 5)
        finally:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = original

    async def test_general_writing_question_stays_chat_mode(self) -> None:
        app = WorkflowDraftTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "How should I write an abstract?"

            app.query_one(WorkflowPane).send_active_message()
            await pilot.pause()
            await pilot.pause()

            self.assertEqual(app._backend.last_mode, "chat")

    async def test_search_result_click_reselects_each_matching_document_range(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            current_text = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content
            notebook_text = DOCUMENT_FIXTURES["project-notebook"].content
            current_query = next(
                phrase
                for phrase in ("current", "draft", "paper", "abstract")
                if phrase.casefold() in current_text.casefold()
            )
            notebook_query = next(
                phrase
                for phrase in ("search results", "source context", "generated text", "interview")
                if phrase.casefold() in notebook_text.casefold()
            )
            current_start = current_text.casefold().find(current_query)
            notebook_start = notebook_text.casefold().find(notebook_query)
            self.assertGreaterEqual(current_start, 0)
            self.assertGreaterEqual(notebook_start, 0)

            for slug, title, query, start in (
                (CURRENT_DRAFT_SLUG, "current_draft.md", current_query, current_start),
                ("project-notebook", "Data Memo 1", notebook_query, notebook_start),
                (CURRENT_DRAFT_SLUG, "current_draft.md", current_query, current_start),
            ):
                await app.on_workflow_pane_search_result_selected(
                    WorkflowPane.SearchResultSelected(
                        app.query_one(WorkflowPane),
                        slug,
                        title,
                        (start, start + len(query)),
                    )
                )
                await pilot.pause()
                await pilot.pause()
                document_pane = app.query_one(DocumentPane)
                self.assertEqual(document_pane.active_document.slug, slug)
                self.assertEqual(document_pane.selected_text.casefold(), query)

    async def test_search_button_adds_search_history_entry(self) -> None:
        app = WorkflowTestApp(FakeBackend(configured=False))
        app.shell_search_documents = lambda query: [
            {
                "document_slug": CURRENT_DRAFT_SLUG,
                "title": "current_draft.md",
                "document_type": "draft",
                "snippet": f"Result for {query}",
                "token_count": 12,
                "location": "current_draft.md",
                "match_range": (0, len(query)),
            }
        ]
        async with app.run_test() as pilot:
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "anchor"
            app.query_one(WorkflowPane).search_documents()
            await pilot.pause()
            self.assertIsInstance(app.query_one(WorkflowPane).active_chat.history_entries[-1], HistorySearchEntry)

    async def test_shell_search_documents_returns_all_document_matches_with_snippets(self) -> None:
        original = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content
        try:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = "alpha one\nbeta\nalpha two\nalpha three\n"
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await pilot.pause()
                DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = "alpha one\nbeta\nalpha two\nalpha three\n"
                app._dirty_document_slugs.add(CURRENT_DRAFT_SLUG)
                result = next(
                    item
                    for item in QualShellApp.shell_search_documents(app, "alpha")
                    if item["document_slug"] == CURRENT_DRAFT_SLUG
                )

                self.assertEqual(result["match_range"], (0, 5))
                self.assertEqual([match["match_range"] for match in result["matches"]], [(0, 5), (15, 20), (25, 30)])
                self.assertTrue(result["snippet"])
                self.assertTrue(all(match["snippet"] for match in result["matches"]))
        finally:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = original

    async def test_search_result_arrows_select_previous_and_next_match_instances(self) -> None:
        app = WorkflowTestApp(FakeBackend(configured=False))
        search_entry = HistorySearchEntry(
            query="alpha",
            results=[
                SearchResultItem(
                    document_slug=CURRENT_DRAFT_SLUG,
                    title="current_draft.md",
                    document_type="draft",
                    snippet="alpha one",
                    token_count=12,
                    location="current_draft.md",
                    match_range=(0, 5),
                    matches=(
                        SearchResultMatch("alpha one", (0, 5)),
                        SearchResultMatch("alpha two", (15, 20)),
                        SearchResultMatch("alpha three", (25, 30)),
                    ),
                ),
                SearchResultItem(
                    document_slug="project-notebook",
                    title="Data Memo 1",
                    document_type="memo",
                    snippet="memo alpha",
                    token_count=8,
                    location="memos/data_memo_1.md",
                    match_range=(2, 7),
                    matches=(SearchResultMatch("memo alpha", (2, 7)),),
                )
            ],
        )
        WORKFLOW_CHATS[PRIMARY_CHAT_SLUG].history_entries.append(search_entry)
        async with app.run_test() as pilot:
            await pilot.pause()
            workflow = app.query_one(WorkflowPane)
            workflow._render_chat(PRIMARY_CHAT_SLUG)
            await pilot.pause()

            app.query_one("#search-result-next-1", Static).card.select_result(0, "next")
            await pilot.pause()
            message = app.messages[-1]
            self.assertIsInstance(message, WorkflowPane.SearchResultSelected)
            self.assertEqual(message.match_range, (15, 20))
            self.assertEqual(str(app.query_one("#search-result-snippet-1", Static).render()), "alpha two")
            self.assertEqual(str(app.query_one("#search-result-count-1", Static).render()), "2/3")

            app.query_one("#search-result-prev-1", Static).card.select_result(0, "prev")
            await pilot.pause()
            message = app.messages[-1]
            self.assertIsInstance(message, WorkflowPane.SearchResultSelected)
            self.assertEqual(message.match_range, (0, 5))
            self.assertEqual(str(app.query_one("#search-result-snippet-1", Static).render()), "alpha one")

            app.query_one("#search-result-next-1", Static).card.select_result(0, "next")
            await pilot.pause()
            self.assertEqual(app.messages[-1].match_range, (15, 20))

            app.query_one("#search-result-2", Static).card.select_result(1, "open")
            await pilot.pause()
            self.assertEqual(app.messages[-1].match_range, (2, 7))

            workflow._render_chat(PRIMARY_CHAT_SLUG)
            await pilot.pause()

            app.query_one("#search-result-1", Static).card.select_result(0, "open")
            await pilot.pause()
            self.assertEqual(app.messages[-1].match_range, (15, 20))
            self.assertEqual(str(app.query_one("#search-result-count-1", Static).render()), "2/3")

    async def test_search_result_add_button_requests_basket_document_for_result(self) -> None:
        app = WorkflowTestApp(FakeBackend(configured=False))
        search_entry = HistorySearchEntry(
            query="alpha",
            results=[
                SearchResultItem(
                    document_slug=CURRENT_DRAFT_SLUG,
                    title="current_draft.md",
                    document_type="draft",
                    snippet="alpha one",
                    token_count=12,
                    location="current_draft.md",
                    match_range=(0, 5),
                    matches=(
                        SearchResultMatch("alpha one", (0, 5)),
                        SearchResultMatch("alpha two", (15, 20)),
                    ),
                )
            ],
        )
        WORKFLOW_CHATS[PRIMARY_CHAT_SLUG].history_entries.append(search_entry)
        async with app.run_test() as pilot:
            await pilot.pause()
            workflow = app.query_one(WorkflowPane)
            workflow._render_chat(PRIMARY_CHAT_SLUG)
            await pilot.pause()

            add_control = app.query_one("#search-result-add-1", Static)
            self.assertEqual(str(add_control.render()), "Add")
            app.query_one("#search-result-next-1", Static).card.select_result(0, "next")
            await pilot.pause()
            add_control.card.select_result(0, "basket")
            await pilot.pause()

            message = app.messages[-1]
            self.assertIsInstance(message, WorkflowPane.SearchResultAddToBasketRequested)
            self.assertEqual(message.document_slug, CURRENT_DRAFT_SLUG)
            self.assertEqual(message.document_title, "current_draft.md")
            self.assertEqual(message.document_type, "draft")
            self.assertEqual(search_entry.selected_match_indices[CURRENT_DRAFT_SLUG], 1)

    async def test_single_match_search_result_hides_navigation_arrows(self) -> None:
        app = WorkflowTestApp(FakeBackend(configured=False))
        WORKFLOW_CHATS[PRIMARY_CHAT_SLUG].history_entries.append(
            HistorySearchEntry(
                query="alpha",
                results=[
                    SearchResultItem(
                        document_slug=CURRENT_DRAFT_SLUG,
                        title="current_draft.md",
                        document_type="draft",
                        snippet="alpha one",
                        token_count=12,
                        location="current_draft.md",
                        match_range=(0, 5),
                        matches=(SearchResultMatch("alpha one", (0, 5)),),
                    )
                ],
            )
        )
        async with app.run_test() as pilot:
            await pilot.pause()
            workflow = app.query_one(WorkflowPane)
            workflow._render_chat(PRIMARY_CHAT_SLUG)
            await pilot.pause()

            self.assertIsNotNone(app.query_one("#search-result-1", Static))
            with self.assertRaises(Exception):
                app.query_one("#search-result-next-1", Button)

    async def test_search_result_without_backend_snippet_gets_visible_fallback_excerpt(self) -> None:
        app = WorkflowTestApp(FakeBackend(configured=False))
        app.shell_search_documents = lambda query: [
            {
                "document_slug": CURRENT_DRAFT_SLUG,
                "title": "current_draft.md",
                "document_type": "draft",
                "token_count": 12,
                "location": "current_draft.md",
                "match_range": (0, len(query)),
            }
        ]
        async with app.run_test() as pilot:
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "anchor"
            app.query_one(WorkflowPane).search_documents()
            await pilot.pause()
            entry = app.query_one(WorkflowPane).active_chat.history_entries[-1]
            self.assertIsInstance(entry, HistorySearchEntry)
            self.assertEqual(entry.results[0].snippet, "Matching text found in this document.")

    def test_search_result_document_type_display_is_title_cased(self) -> None:
        self.assertEqual(_display_document_type("draft"), "Draft")
        self.assertEqual(_display_document_type("field_note"), "Field Note")
        self.assertEqual(_display_document_type("source-transcript"), "Source Transcript")

    async def test_inspector_summary_button_saves_summary_document(self) -> None:
        before = set(DOCUMENT_FIXTURES)
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause(0.1)
            inspector = app.query_one(InspectorPane)
            inspector.post_message(InspectorPane.SummaryRequested(inspector, "short", 100))
            await pilot.pause()
            await pilot.pause()
            created = [slug for slug in DOCUMENT_FIXTURES if slug not in before and slug.startswith("summary-short")]
            self.assertEqual(len(created), 1)
            fixture = DOCUMENT_FIXTURES[created[0]]
            self.assertEqual(fixture.document_type, "summary")
            self.assertIn("Rewritten section.", fixture.content)
            self.assertEqual(app._backend.last_mode, "summary")
        for slug in set(DOCUMENT_FIXTURES) - before:
            DOCUMENT_FIXTURES.pop(slug, None)


class DocumentInsertionTests(unittest.TestCase):
    def test_generated_draft_text_removes_duplicate_existing_heading_prefixes(self) -> None:
        document_text = "# Existing Title\n\n## Abstract\n\nOriginal body."
        generated_text = "Existing Title\n\nAbstract\n\nThis is the body section."

        cleaned = clean_generated_draft_text(document_text, generated_text)

        self.assertEqual(cleaned, "This is the body section.")

    def test_generated_draft_text_removes_bold_duplicate_heading_prefixes(self) -> None:
        document_text = "# Existing Title\n\n## Abstract\n\nOriginal body."
        generated_text = "**Abstract**\n\nThis is the body section."

        cleaned = clean_generated_draft_text(document_text, generated_text)

        self.assertEqual(cleaned, "This is the body section.")

    def test_generated_draft_text_removes_duplicate_heading_with_colon(self) -> None:
        document_text = "# Existing Title\n\n## Findings\n\nOriginal body."
        generated_text = "Findings:\n\nThis is the body section."

        cleaned = clean_generated_draft_text(document_text, generated_text)

        self.assertEqual(cleaned, "This is the body section.")

    def test_generated_draft_text_removes_tool_proposal_scaffolding(self) -> None:
        document_text = "# Existing Title\n\n## Abstract\n\nOriginal body."
        generated_text = "\n".join(
            [
                "Draft Proposal",
                "Instruction: Draft an abstract for the current document.",
                "Insertion point: after Abstract",
                "",
                "Proposed draft",
                "Existing Title",
                "",
                "Abstract",
                "",
                "This is the body section.",
            ]
        )

        cleaned = clean_generated_draft_text(document_text, generated_text)

        self.assertEqual(cleaned, "This is the body section.")

    def test_draft_preview_block_shows_only_the_proposed_draft(self) -> None:
        preview = PendingRewritePreview(
            patch_id="draft-test",
            document_slug=CURRENT_DRAFT_SLUG,
            target_range=(11, 11),
            original_text="",
            proposed_text="This is the proposed paragraph.",
            instruction_text="Write an abstract.",
            source_chat_slug="chat-main",
        )

        rendered = render_review_document_text("Hello world", preview)

        self.assertIn("┌─ Draft Proposal", rendered)
        self.assertIn("│ + This is the proposed paragraph.", rendered)
        self.assertIn("└─ End Draft Proposal", rendered)
        self.assertNotIn("Instruction:", rendered)
        self.assertNotIn("Insertion point", rendered)
        self.assertNotIn("Proposed draft", rendered)

    def test_revision_preview_block_marks_original_and_proposed_lines(self) -> None:
        preview = PendingRewritePreview(
            patch_id="patch-test",
            document_slug=CURRENT_DRAFT_SLUG,
            target_range=(0, 8),
            original_text="Old line",
            proposed_text="New line",
            instruction_text="Revise it.",
            source_chat_slug="chat-main",
        )

        rendered = render_review_document_text("Old line\n\nRest", preview)

        self.assertIn("┌─ Revision Proposal", rendered)
        self.assertIn("│ Original", rendered)
        self.assertIn("│ - Old line", rendered)
        self.assertIn("│ Proposed", rendered)
        self.assertIn("│ + New line", rendered)
        self.assertNotIn("Instruction:", rendered)
        self.assertIn("└─ End Revision Proposal", rendered)

    def test_rich_preview_block_does_not_add_phantom_blank_lines_around_proposal(self) -> None:
        document_text = "# Paper\n\n## Abstract\n\n## Introduction\n\nIntro body."
        start = document_text.index("## Abstract") + len("## Abstract\n")
        end = document_text.index("## Introduction")
        preview = PendingRewritePreview(
            patch_id="draft-test",
            document_slug=CURRENT_DRAFT_SLUG,
            target_range=(start, end),
            original_text=document_text[start:end],
            proposed_text="This is the proposed abstract.",
            instruction_text="Write an abstract.",
            source_chat_slug="chat-main",
        )

        rendered = render_review_document_rich(document_text, preview).plain

        self.assertIn("## Abstract\n┌─ Draft Proposal", rendered)
        self.assertIn("└─ End Draft Proposal\n## Introduction", rendered)
        self.assertNotIn("## Abstract\n\n┌─ Draft Proposal", rendered)
        self.assertNotIn("└─ End Draft Proposal\n\n## Introduction", rendered)

    def test_replace_selection(self) -> None:
        self.assertEqual(
            insert_generated_text_at_range("Hello world", "New text", (6, 11)),
            "Hello New text",
        )

    def test_insert_at_cursor(self) -> None:
        self.assertEqual(
            insert_generated_text_at_range("Hello world", "bright ", (6, 6)),
            "Hello bright world",
        )

    def test_append_when_no_target_range(self) -> None:
        self.assertEqual(
            insert_generated_text_at_range("Hello world", "New paragraph", None),
            "Hello world\n\nNew paragraph",
        )

    def test_block_insert_preserves_markdown_section_spacing(self) -> None:
        content = "# Paper\n\n## Abstract\n\n## Introduction\n\nIntro body."
        start = content.index("## Abstract") + len("## Abstract\n")
        end = content.index("## Introduction")

        self.assertEqual(
            insert_generated_text_at_range(content, "Abstract body.", (start, end), block_insert=True),
            "# Paper\n\n## Abstract\n\nAbstract body.\n\n## Introduction\n\nIntro body.",
        )

    def test_insert_location_targets_replaced_selection(self) -> None:
        self.assertEqual(
            generated_text_insert_location("Hello world", "New text", (6, 11)),
            (0, 6),
        )

    def test_insert_location_targets_cursor_insert(self) -> None:
        self.assertEqual(
            generated_text_insert_location("Hello world", "bright ", (6, 6)),
            (0, 6),
        )

    def test_insert_location_targets_append_fallback(self) -> None:
        self.assertEqual(
            generated_text_insert_location("Hello world", "New paragraph", None),
            (2, 0),
        )


class WorkflowPaneDraftInsertionTests(unittest.IsolatedAsyncioTestCase):
    async def test_draft_creates_review_card_before_apply(self) -> None:
        original = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content
        try:
            app = WorkflowDraftTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await pilot.pause()
                composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                composer.value = "Add a new paragraph"
                app.query_one(WorkflowPane).draft_into_document()
                await pilot.pause()
                workflow = app.query_one(WorkflowPane)
                await pilot.pause()
                document_pane = app.query_one(DocumentPane)
                self.assertEqual(DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content, original)
                self.assertTrue(document_pane.has_pending_preview(CURRENT_DRAFT_SLUG))
                self.assertFalse(
                    any(
                        isinstance(entry, HistoryTextEntry) and entry.role == "assistant" and "Drafted paragraph." in entry.content
                        for entry in workflow.active_chat.history_entries
                    )
                )
                draft_cards = [
                    entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryRewriteEntry)
                ]
                self.assertEqual(len(draft_cards), 1)
                self.assertTrue(draft_cards[0].patch_id.startswith("draft-"))
                self.assertEqual(draft_cards[0].proposed_text, "Drafted paragraph.")
                self.assertIsNotNone(workflow.query_one("#rewrite-apply", Button))
                self.assertIsNotNone(workflow.query_one("#rewrite-reject", Button))

                rejected = document_pane.reject_pending_rewrite(draft_cards[0].patch_id)
                self.assertIsNotNone(rejected)
                self.assertEqual(DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content, original)
                self.assertEqual(document_pane.query_one("#document-editor-current-draft", TextArea).text, original)

                composer.value = "Add a new paragraph again"
                workflow.draft_into_document()
                await pilot.pause()
                await pilot.pause()
                second_card = [
                    entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryRewriteEntry)
                ][-1]
                applied = document_pane.apply_pending_rewrite(second_card.patch_id)
                self.assertIsNotNone(applied)
                self.assertIn("Drafted paragraph.", DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content)
                selection = document_pane.current_selection_snapshot()
                self.assertIsNotNone(selection)
                self.assertEqual(selection.selected_text, "Drafted paragraph.")
        finally:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = original

    async def test_pending_draft_feedback_updates_review_card(self) -> None:
        original = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content
        try:
            backend = SequencedDraftBackend(["First draft proposal.", "Revised draft proposal."])
            app = WorkflowDraftTestApp(backend)
            async with app.run_test() as pilot:
                await pilot.pause()
                composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                workflow = app.query_one(WorkflowPane)
                document_pane = app.query_one(DocumentPane)

                composer.value = "Draft a body section"
                workflow.draft_into_document()
                await pilot.pause()
                await pilot.pause()

                first_cards = [
                    entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryRewriteEntry)
                ]
                self.assertEqual(len(first_cards), 1)
                self.assertEqual(first_cards[0].proposed_text, "First draft proposal.")
                self.assertTrue(document_pane.has_pending_preview(CURRENT_DRAFT_SLUG))

                composer.value = "Make it more concrete and keep it shorter"
                workflow.send_active_message()
                await pilot.pause()
                await pilot.pause()

                revised_cards = [
                    entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryRewriteEntry)
                ]
                self.assertEqual(len(revised_cards), 1)
                self.assertEqual(revised_cards[0].proposed_text, "Revised draft proposal.")
                self.assertEqual(revised_cards[0].instruction_text, "Make it more concrete and keep it shorter")
                self.assertTrue(document_pane.has_pending_preview(CURRENT_DRAFT_SLUG))
                self.assertEqual(DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content, original)
                self.assertFalse(
                    any(
                        isinstance(entry, HistoryTextEntry)
                        and entry.role == "assistant"
                        and "Revised draft proposal." in entry.content
                        for entry in workflow.active_chat.history_entries
                    )
                )
                self.assertIn("Current pending draft proposal:\nFirst draft proposal.", backend.prompts[-1])
                self.assertIn("User feedback:\nMake it more concrete and keep it shorter", backend.prompts[-1])
        finally:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = original

    async def test_draft_can_target_existing_heading_instead_of_cursor(self) -> None:
        original = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content
        target_document = "# Paper\n\n## Abstract\n\n## Introduction\n\nIntro body."
        try:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = target_document
            backend = SequencedDraftBackend(["Abstract\n\nTargeted abstract body."])
            app = WorkflowDraftTestApp(backend)
            async with app.run_test() as pilot:
                await pilot.pause()
                composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                workflow = app.query_one(WorkflowPane)
                document_pane = app.query_one(DocumentPane)
                start = target_document.index("## Abstract") + len("## Abstract\n")
                end = target_document.index("## Introduction")

                composer.value = "Draft me an abstract in the current document"
                workflow.draft_into_document(target_range=(start, end), block_insert=True)
                await pilot.pause()
                await pilot.pause()

                cards = [entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryRewriteEntry)]
                self.assertEqual(len(cards), 1)
                self.assertEqual(cards[0].proposed_text, "Targeted abstract body.")
                self.assertEqual(DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content, target_document)

                applied = document_pane.apply_pending_rewrite(cards[0].patch_id)
                self.assertIsNotNone(applied)
                self.assertIn("## Abstract\n\nTargeted abstract body.\n\n## Introduction", DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content)
                selection = document_pane.current_selection_snapshot()
                self.assertIsNotNone(selection)
                self.assertEqual(selection.selected_text, "Targeted abstract body.")
        finally:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = original

    async def test_rewrite_creates_review_card_and_pending_preview(self) -> None:
        original = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content
        try:
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await pilot.pause()
                composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                composer.value = "Tighten this opening"
                app.query_one(WorkflowPane).rewrite_selection()
                await pilot.pause()
                self.assertEqual(app._backend.last_mode, "rewrite")
                self.assertEqual(app._backend.last_context.selected_text, "# Cur")
                self.assertEqual(app._backend.last_context.selection_start, 0)
                self.assertEqual(app._backend.last_context.selection_end, 5)
                self.assertTrue(app.query_one(DocumentPane).has_pending_preview(CURRENT_DRAFT_SLUG))
                rewrite_cards = [
                    entry for entry in app.query_one(WorkflowPane).active_chat.history_entries if isinstance(entry, HistoryRewriteEntry)
                ]
                self.assertEqual(len(rewrite_cards), 1)
                app.on_workflow_pane_patch_decision_requested(
                    WorkflowPane.PatchDecisionRequested(app.query_one(WorkflowPane), rewrite_cards[0].patch_id, "apply")
                )
                await pilot.pause()
                self.assertIn(CURRENT_DRAFT_SLUG, app._dirty_document_slugs)
        finally:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = original

    async def test_model_rewrite_can_target_heading_without_manual_selection(self) -> None:
        original = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content
        target_document = "# Paper\n\n## Abstract\n\nOld abstract.\n\n## Introduction\n\nIntro body."
        try:
            backend = SequencedRewriteBackend(["Updated abstract."])
            app = ShellWorkflowTestApp(backend)
            async with app.run_test() as pilot:
                await pilot.pause()
                DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = target_document
                result = await app.dispatch_app_action(
                    "rewrite_selection",
                    {"instruction": "Rewrite the abstract", "target_heading": "Abstract"},
                    source="model_tool",
                )
                await pilot.pause()
                await pilot.pause()

                self.assertEqual(result.status, "completed")
                self.assertEqual(backend.last_mode, "rewrite")
                self.assertEqual(backend.last_context.selected_text.strip(), "Old abstract.")
                start = target_document.index("## Abstract") + len("## Abstract\n")
                end = target_document.index("## Introduction")
                self.assertEqual(backend.last_context.selection_start, start)
                self.assertEqual(backend.last_context.selection_end, end)

                workflow = app.query_one(WorkflowPane)
                cards = [entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryRewriteEntry)]
                self.assertEqual(len(cards), 1)
                self.assertEqual(cards[0].target_range, (start, end))
                self.assertTrue(cards[0].block_insert)
                self.assertEqual(cards[0].proposed_text, "Updated abstract.")

                applied = app.query_one(DocumentPane).apply_pending_rewrite(cards[0].patch_id)
                self.assertIsNotNone(applied)
                self.assertIn("## Abstract\n\nUpdated abstract.\n\n## Introduction", DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content)
        finally:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = original

    async def test_pending_rewrite_feedback_updates_review_card(self) -> None:
        original_before_app = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content
        try:
            backend = SequencedRewriteBackend(["First rewrite proposal.", "Revised rewrite proposal."])
            app = ShellWorkflowTestApp(backend)
            async with app.run_test() as pilot:
                await pilot.pause()
                composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                workflow = app.query_one(WorkflowPane)
                document_pane = app.query_one(DocumentPane)
                loaded_original = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content

                composer.value = "Tighten this opening"
                workflow.rewrite_selection()
                await pilot.pause()
                await pilot.pause()

                first_cards = [
                    entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryRewriteEntry)
                ]
                self.assertEqual(len(first_cards), 1)
                self.assertEqual(first_cards[0].proposed_text, "First rewrite proposal.")
                self.assertEqual(first_cards[0].document_slug, CURRENT_DRAFT_SLUG)
                self.assertEqual(first_cards[0].target_range, (0, 5))
                self.assertTrue(document_pane.has_pending_preview(CURRENT_DRAFT_SLUG))
                self.assertFalse(
                    any(
                        isinstance(entry, HistoryTextEntry)
                        and entry.role == "assistant"
                        and "First rewrite proposal." in entry.content
                        for entry in workflow.active_chat.history_entries
                    )
                )

                composer.value = "Make it sharper"
                workflow.send_active_message()
                await pilot.pause()
                await pilot.pause()

                revised_cards = [
                    entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryRewriteEntry)
                ]
                self.assertEqual(len(revised_cards), 1)
                self.assertEqual(revised_cards[0].proposed_text, "Revised rewrite proposal.")
                self.assertEqual(revised_cards[0].instruction_text, "Make it sharper")
                self.assertEqual(revised_cards[0].document_slug, CURRENT_DRAFT_SLUG)
                self.assertEqual(revised_cards[0].target_range, (0, 5))
                self.assertTrue(document_pane.has_pending_preview(CURRENT_DRAFT_SLUG))
                self.assertEqual(DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content, loaded_original)
                self.assertFalse(
                    any(
                        isinstance(entry, HistoryTextEntry)
                        and entry.role == "assistant"
                        and "Revised rewrite proposal." in entry.content
                        for entry in workflow.active_chat.history_entries
                    )
                )
                self.assertIn("Current pending rewrite proposal:\nFirst rewrite proposal.", backend.prompts[-1])
                self.assertIn("User feedback:\nMake it sharper", backend.prompts[-1])
        finally:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = original_before_app


class ShellWorkflowShortcutTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self._previous_projects_dir = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
        self._previous_local_developer = os.environ.get("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER")
        self._projects_tmp = tempfile.TemporaryDirectory()
        os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = self._projects_tmp.name
        os.environ["EXEGESIS_TEXTUAL_LOCAL_DEVELOPER"] = "1"

    def tearDown(self) -> None:
        if self._previous_projects_dir is None:
            os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
        else:
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = self._previous_projects_dir
        if self._previous_local_developer is None:
            os.environ.pop("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER", None)
        else:
            os.environ["EXEGESIS_TEXTUAL_LOCAL_DEVELOPER"] = self._previous_local_developer
        self._projects_tmp.cleanup()

    def test_palette_includes_summary_shortcuts(self) -> None:
        commands = {(command.key, command.label) for command in default_palette_commands()}
        self.assertIn(("palette", "New Project"), commands)
        self.assertIn(("palette", "Project Browser"), commands)
        self.assertIn(("palette", "Change projects directory"), commands)
        self.assertIn(("palette", "Model Settings"), commands)
        self.assertIn(("ctrl+shift+1", "Save Short Summary"), commands)
        self.assertIn(("ctrl+shift+2", "Save Medium Summary"), commands)
        self.assertIn(("ctrl+shift+3", "Save Long Summary"), commands)
        self.assertIn(("ctrl+shift+e", "Add excerpt"), commands)
        self.assertIn(("ctrl+shift+t", "New transcript"), commands)
        self.assertIn(("ctrl+shift+g", "Draft"), commands)
        self.assertIn(("ctrl+shift+w", "Rewrite"), commands)
        self.assertIn(("shift+enter", "Accept proposal"), commands)
        self.assertIn(("escape", "Reject proposal"), commands)
        self.assertIn(("ctrl+shift+x", "Save transcript"), commands)
        self.assertIn(("ctrl+shift+v", "Compact chat"), commands)
        self.assertIn(("ctrl+shift+u", "Update item"), commands)
        self.assertIn(("ctrl+r", "Restart Exegesis"), commands)

    async def test_system_palette_keeps_quit_and_screenshot_but_omits_theme(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()

            names = {command.title for command in app.get_system_commands(app.screen)}
            self.assertIn("Quit", names)
            self.assertIn("Screenshot", names)
            self.assertNotIn("Theme", names)

    async def test_basket_is_taller_without_changing_document_pane_height(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()

            self.assertEqual(app.query_one("#basket-pane").styles.height.value, 15)
            self.assertEqual(app.query_one("#basket-pane").styles.min_height.value, 12)
            self.assertEqual(app.query_one("#document-pane").styles.height.value, 2)
            self.assertEqual(app.query_one("#workflow-pane").styles.height.value, 1.4)
            self.assertEqual(app.query_one("#workflow-pane").styles.min_height.value, 12)

    def test_palette_omits_restart_outside_local_developer_mode(self) -> None:
        os.environ.pop("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER", None)
        commands = {(command.key, command.label) for command in default_palette_commands()}

        self.assertIn(("palette", "New Project"), commands)
        self.assertIn(("palette", "Project Browser"), commands)
        self.assertNotIn(("ctrl+r", "Restart Exegesis"), commands)

    def test_palette_commands_are_wired_to_shell_actions(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        self.assertIn(ExegesisCommandProvider, app.COMMANDS)
        for command in default_palette_commands():
            with self.subTest(command=command.label):
                self.assertTrue(hasattr(app, f"action_{command.action}"))

    def test_shell_command_shortcuts_are_priority_bindings(self) -> None:
        bindings = {(binding.key, binding.action): binding.priority for binding in ShellWorkflowTestApp.BINDINGS}
        expected_priority = {
            ("ctrl+p", "show_palette"),
            ("ctrl+r", "restart_exegesis"),
            ("ctrl+s", "save_current_document"),
            ("ctrl+shift+e", "add_excerpt_to_basket"),
            ("ctrl+shift+b", "add_file_to_basket"),
            ("ctrl+shift+d", "create_draft"),
            ("ctrl+shift+m", "create_memo"),
            ("ctrl+shift+s", "create_summary"),
            ("ctrl+shift+t", "create_transcript"),
            ("ctrl+shift+l", "create_literature"),
            ("ctrl+shift+f", "create_folder"),
            ("ctrl+shift+u", "update_selected_project_item"),
            ("ctrl+shift+i", "import_document"),
            ("ctrl+shift+r", "restore_selected_trash_item"),
            ("ctrl+shift+delete", "permanently_delete_selected_trash_item"),
            ("ctrl+shift+backspace", "permanently_delete_selected_trash_item"),
            ("ctrl+shift+1", "save_short_summary"),
            ("ctrl+shift+2", "save_medium_summary"),
            ("ctrl+shift+3", "save_long_summary"),
            ("ctrl+enter", "terminal_search"),
            ("ctrl+shift+g", "terminal_draft"),
            ("ctrl+shift+w", "terminal_rewrite"),
            ("shift+enter", "terminal_accept_proposal"),
            ("escape", "terminal_reject_proposal"),
            ("ctrl+shift+n", "terminal_new_chat"),
            ("ctrl+shift+x", "terminal_save"),
            ("ctrl+shift+v", "terminal_compact"),
        }
        for key_action in expected_priority:
            with self.subTest(binding=key_action):
                self.assertTrue(bindings.get(key_action))
        self.assertNotIn(("palette", "new_project"), bindings)
        self.assertNotIn(("palette", "open_project_browser"), bindings)
        self.assertNotIn(("palette", "change_projects_directory"), bindings)

    async def test_shell_omits_internal_header_but_keeps_footer_palette_and_restart(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            self.assertEqual(len(app.query(Header)), 0)
            footer_button_ids = [
                button.id
                for button in app.query("#shell-footer-bar Button")
                if button.id in {FOOTER_RESTART_ID, FOOTER_QUIT_ID, FOOTER_PALETTE_ID}
            ]
            self.assertEqual(footer_button_ids, [FOOTER_RESTART_ID, FOOTER_QUIT_ID, FOOTER_PALETTE_ID])
            self.assertEqual(app.query_one(f"#{FOOTER_PALETTE_ID}", Button).label.plain, "Ctrl+P Palette")
            self.assertEqual(app.query_one(f"#{FOOTER_QUIT_ID}", Button).label.plain, "Ctrl+Q Quit")
            self.assertEqual(app.query_one(f"#{FOOTER_RESTART_ID}", Button).label.plain, "Ctrl+R Restart")

    async def test_shell_omits_restart_footer_outside_local_developer_mode(self) -> None:
        os.environ.pop("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER", None)
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()

            self.assertEqual(len(app.query(f"#{FOOTER_RESTART_ID}")), 0)
            footer_button_ids = [
                button.id
                for button in app.query("#shell-footer-bar Button")
                if button.id in {FOOTER_QUIT_ID, FOOTER_PALETTE_ID}
            ]
            self.assertEqual(footer_button_ids, [FOOTER_QUIT_ID, FOOTER_PALETTE_ID])
            self.assertEqual(app.query_one(f"#{FOOTER_QUIT_ID}", Button).label.plain, "Ctrl+Q Quit")
            self.assertEqual(app.query_one(f"#{FOOTER_PALETTE_ID}", Button).label.plain, "Ctrl+P Palette")

    async def test_project_top_actions_use_stacked_full_width_button_chrome(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            new_project = app.query_one("#project-new-project", Button)
            project_browser = app.query_one("#project-open-project", Button)
            project_header = app.query_one("#project-header", Static)

            self.assertEqual(new_project.styles.width.value, 100)
            self.assertEqual(project_browser.styles.width.value, 100)
            self.assertEqual(new_project.styles.height.value, 3)
            self.assertEqual(project_browser.styles.height.value, 3)
            self.assertEqual(new_project.styles.min_height.value, 3)
            self.assertEqual(project_browser.styles.min_height.value, 3)
            self.assertEqual(project_browser.label.plain, "Project Browser")
            self.assertEqual(project_header.styles.height.value, 3)
            self.assertEqual(project_header.styles.min_height.value, 3)
            self.assertEqual(project_header.styles.width.value, 1)
            self.assertEqual(project_header.styles.content_align_horizontal, "center")
            self.assertEqual(project_header.styles.content_align_vertical, "middle")
            self.assertEqual(project_header.styles.border.left[0], "")
            self.assertEqual(project_header.styles.border.right[0], "")
            project_header.focus()
            await pilot.pause()
            self.assertEqual(str(project_header.styles.background), "Color(0, 255, 0)")
            self.assertEqual(str(project_header.styles.color), "Color(18, 18, 18)")

    async def test_new_project_modal_fits_confidential_action_buttons(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test(size=(140, 50)) as pilot:
            await app.push_screen(NewProjectModal(local_endpoint_configured=True))
            await pilot.pause()

            modal = app.screen.query_one("#project-name-modal")
            create = app.screen.query_one("#project-name-create", Button)
            confidential = app.screen.query_one("#project-name-create-confidential", Button)
            cancel = app.screen.query_one("#project-name-cancel", Button)

            self.assertEqual(modal.styles.width.value, 86)
            self.assertEqual(create.styles.width.value, 20)
            self.assertEqual(confidential.styles.width.value, 34)
            self.assertEqual(cancel.styles.width.value, 16)
            self.assertEqual(confidential.label.plain, "Create Confidential Project")
            self.assertEqual(cancel.label.plain, "Cancel")

    async def test_project_browser_modal_uses_tall_project_list(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        projects = [ProjectRecord(f"Project {index}", f"project-{index}") for index in range(1, 12)]
        async with app.run_test() as pilot:
            await app.push_screen(OpenProjectModal(projects))
            await pilot.pause()

            modal = app.screen.query_one("#project-picker-modal")
            options = app.screen.query_one(f"#{PROJECT_PICKER_OPTIONS_ID}", OptionList)
            self.assertEqual(modal.styles.height.value, 28)
            self.assertEqual(options.styles.height.value, 1)

    async def test_duplicate_modal_rename_input_allows_backspace(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await app.push_screen(DuplicateDocumentModal("memo_01.md", "memos/memo_01.md"))
            await pilot.pause()

            rename_input = app.screen.query_one(f"#{DUPLICATE_RENAME_INPUT_ID}", Input)
            self.assertTrue(rename_input.has_focus)
            await pilot.press("backspace")
            await pilot.pause()

            self.assertEqual(rename_input.value, "memo_01.m")

    async def test_rename_modals_space_buttons_below_input(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await app.push_screen(RenameProjectEntryModal("memo_01.md"))
            await pilot.pause()
            rename_input = app.screen.query_one(f"#{PROJECT_RENAME_INPUT_ID}", Input)
            self.assertEqual(rename_input.styles.margin.bottom, 1)
            app.pop_screen()
            await pilot.pause()

            await app.push_screen(RenameActiveProjectModal("Field Project"))
            await pilot.pause()
            active_input = app.screen.query_one(f"#{PROJECT_RENAME_ACTIVE_INPUT_ID}", Input)
            self.assertEqual(active_input.styles.margin.bottom, 1)

    async def test_projects_directory_modal_can_create_and_select_new_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await app.push_screen(SelectProjectsDirectoryModal(Path(tmp)))
                await pilot.pause()

                folder_input = app.screen.query_one(f"#{PROJECTS_DIRECTORY_NEW_FOLDER_INPUT_ID}", Input)
                folder_input.value = "new project home"
                app.screen.query_one(f"#{PROJECTS_DIRECTORY_CREATE_FOLDER_ID}", Button).press()
                await pilot.pause()

                expected = Path(tmp) / "new project home"
                self.assertTrue(expected.exists())
                self.assertEqual(app.screen._current_dir, expected.resolve())
                self.assertEqual(str(app.screen.query_one(f"#{PROJECTS_DIRECTORY_PATH_ID}", Static).render()), str(expected.resolve()))

    async def test_change_projects_directory_updates_project_root_from_palette_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = str(Path(tmp) / "initial-projects")
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=True))
                async with app.run_test() as pilot:
                    await pilot.pause()

                    selected = Path(tmp) / "selected-projects"
                    with patch("exegesis_textual.layout.project_controller.save_textual_projects_dir") as save_projects_dir:
                        app._handle_projects_directory_result(selected)
                        await pilot.pause()

                    self.assertEqual(app._projects_base_dir, selected.resolve())
                    self.assertEqual(app._project_root, selected.resolve() / "demo-project")
                    self.assertTrue((selected / "demo-project" / "drafts" / "current_draft.md").exists())
                    save_projects_dir.assert_called_once()
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_basket_delete_key_removes_selected_item(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            app.action_add_file_to_basket()
            await pilot.pause()

            basket = app.query_one(BasketPane)
            document_list = basket.query_one(f"#{BASKET_DOCUMENTS_LIST_ID}", OptionList)
            document_list.focus()
            document_list.highlighted = 0
            await pilot.press("delete")
            await pilot.pause()

            self.assertEqual(basket.entries, {})
            self.assertEqual(app._engine_adapter.state.basket.items, [])

    def test_restart_action_saves_dirty_documents_and_exits_for_launcher(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        app._save_dirty_documents = Mock(return_value=True)  # type: ignore[method-assign]
        app.exit = Mock()  # type: ignore[method-assign]

        app.action_restart_exegesis()

        app._save_dirty_documents.assert_called_once()
        app.exit.assert_called_once_with(result="restart")

    async def test_native_palette_provider_finds_actions_by_search_text(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            provider = ExegesisCommandProvider(app.screen)
            hits = [hit async for hit in provider.search("save document")]
            labels = {hit.text for hit in hits}
            self.assertIn("Save document", labels)
            self.assertTrue(hasattr(app, "action_save_current_document"))

    async def test_new_folder_modal_names_category_instead_of_category_root(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test(size=(140, 50)) as pilot:
            await app.push_screen(NewProjectFolderModal("Memos", ""))
            await pilot.pause()

            subtitle = str(app.screen.query_one("#project-modal-subtitle", Static).render())
            self.assertEqual(subtitle, "Create a folder in Memos: /")
            self.assertNotIn("category root", subtitle)
            self.assertNotIn("Memos: Memos", subtitle)

    async def test_update_item_modal_uses_folder_picker_and_single_click_cancel(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        results: list[tuple[str, str] | None] = []
        async with app.run_test(size=(140, 50)) as pilot:
            await app.push_screen(
                UpdateProjectItemModal("memo.md", "Memos", "folder-a", ("folder-a", "folder-b/nested")),
                callback=results.append,
            )
            await pilot.pause()

            picker = app.screen.query_one(UpdateFolderPickerTree)
            self.assertEqual(picker.selected_folder, "folder-a")
            picker.select_folder("folder-b/nested")
            await picker.run_action("select_cursor")
            await pilot.pause()

            self.assertIn(
                "folder-b/nested",
                str(app.screen.query_one(f"#{PROJECT_UPDATE_SELECTED_FOLDER_ID}", Static).render()),
            )
            self.assertEqual(str(app.screen.query_one(f"#{PROJECT_UPDATE_CONFIRM_ID}", Button).label), "Update Item")
            self.assertEqual(str(app.screen.query_one(f"#{PROJECT_UPDATE_CANCEL_ID}", Button).label), "Cancel")
            await pilot.click(f"#{PROJECT_UPDATE_CANCEL_ID}")
            await pilot.pause()

            self.assertEqual(results, [None])
            self.assertEqual(app.screen.id, "_default")

    async def test_update_item_modal_confirm_returns_selected_folder(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        results: list[tuple[str, str] | None] = []
        async with app.run_test(size=(140, 50)) as pilot:
            await app.push_screen(
                UpdateProjectItemModal("memo.md", "Memos", "", ("folder-a", "folder-b/nested")),
                callback=results.append,
            )
            await pilot.pause()

            picker = app.screen.query_one(UpdateFolderPickerTree)
            picker.select_folder("folder-b/nested")
            await picker.run_action("select_cursor")
            await pilot.pause()
            app.screen.query_one(f"#{PROJECT_UPDATE_TITLE_INPUT_ID}", Input).value = "updated.md"
            await pilot.click(f"#{PROJECT_UPDATE_CONFIRM_ID}")
            await pilot.pause()

            self.assertEqual(results, [("updated.md", "folder-b/nested")])

    async def test_top_short_summary_button_saves_summary_document(self) -> None:
        before = set(DOCUMENT_FIXTURES)
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        try:
            async with app.run_test() as pilot:
                await pilot.pause()
                await pilot.click(f"#{TOP_SAVE_SHORT_SUMMARY_ID}")
                await pilot.pause()
                await pilot.pause()
                created = [slug for slug in DOCUMENT_FIXTURES if slug not in before and slug.startswith("summary-short")]
                self.assertEqual(len(created), 1)
                self.assertEqual(DOCUMENT_FIXTURES[created[0]].document_type, "summary")
                self.assertEqual(app._backend.last_mode, "summary")
                summary_id = app._document_id_by_slug[created[0]]
                self.assertTrue((Path(self._projects_tmp.name) / "demo-project" / summary_id).exists())
        finally:
            for slug in set(DOCUMENT_FIXTURES) - before:
                DOCUMENT_FIXTURES.pop(slug, None)

    async def test_summary_generation_shows_progress_modal_until_complete(self) -> None:
        before = set(DOCUMENT_FIXTURES)
        backend = SlowSummaryBackend()
        app = ShellWorkflowTestApp(backend)
        try:
            async with app.run_test() as pilot:
                await pilot.pause()
                await pilot.click(f"#{TOP_SAVE_SHORT_SUMMARY_ID}")
                await asyncio.wait_for(backend.started.wait(), timeout=1)
                await pilot.pause()

                self.assertIsNotNone(app.screen.query_one(f"#{SUMMARY_PROGRESS_MODAL_ID}"))

                backend.release.set()
                await pilot.pause()
                await pilot.pause()

                created = [slug for slug in DOCUMENT_FIXTURES if slug not in before and slug.startswith("summary-short")]
                self.assertEqual(len(created), 1)
                self.assertEqual(DOCUMENT_FIXTURES[created[0]].document_type, "summary")
                with self.assertRaises(Exception):
                    app.screen.query_one(f"#{SUMMARY_PROGRESS_MODAL_ID}")
        finally:
            for slug in set(DOCUMENT_FIXTURES) - before:
                DOCUMENT_FIXTURES.pop(slug, None)

    async def test_summary_generation_cancel_discards_partial_summary(self) -> None:
        before = set(DOCUMENT_FIXTURES)
        backend = SlowSummaryBackend()
        app = ShellWorkflowTestApp(backend)
        try:
            async with app.run_test() as pilot:
                await pilot.pause()
                await pilot.click(f"#{TOP_SAVE_SHORT_SUMMARY_ID}")
                await asyncio.wait_for(backend.started.wait(), timeout=1)
                await pilot.pause()

                await pilot.click(f"#{SUMMARY_PROGRESS_CANCEL_ID}")
                await pilot.pause()

                self.assertEqual(backend.cancelled_chats, ["inspector-summary-short"])
                backend.release.set()
                await pilot.pause()
                await pilot.pause()

                created = [slug for slug in DOCUMENT_FIXTURES if slug not in before and slug.startswith("summary-short")]
                self.assertEqual(created, [])
                with self.assertRaises(Exception):
                    app.screen.query_one(f"#{SUMMARY_PROGRESS_MODAL_ID}")
        finally:
            for slug in set(DOCUMENT_FIXTURES) - before:
                DOCUMENT_FIXTURES.pop(slug, None)

    async def test_top_terminal_search_button_routes_to_search(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=False))
        async with app.run_test() as pilot:
            await pilot.pause()
            composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "anchor"
            await pilot.click(f"#{TOP_TERMINAL_SEARCH_ID}")
            await pilot.pause()
            self.assertIsInstance(app.query_one(WorkflowPane).active_chat.history_entries[-1], HistorySearchEntry)

    async def test_top_terminal_draft_button_routes_to_workflow(self) -> None:
        original = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content
        try:
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await pilot.pause()
                composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                composer.value = "Draft a sharper paragraph"
                await pilot.click(f"#{TOP_TERMINAL_DRAFT_ID}")
                await pilot.pause()
                self.assertEqual(app._backend.last_mode, "draft")
                self.assertEqual(DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content, original)
                draft_cards = [
                    entry for entry in app.query_one(WorkflowPane).active_chat.history_entries if isinstance(entry, HistoryRewriteEntry)
                ]
                self.assertEqual(len(draft_cards), 1)
                self.assertTrue(draft_cards[0].patch_id.startswith("draft-"))
                self.assertTrue(app.query_one(DocumentPane).has_pending_preview(CURRENT_DRAFT_SLUG))
                app.on_workflow_pane_patch_decision_requested(
                    WorkflowPane.PatchDecisionRequested(app.query_one(WorkflowPane), draft_cards[0].patch_id, "apply")
                )
                await pilot.pause()
                self.assertIn("Drafted paragraph.", DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content)
                self.assertIn(CURRENT_DRAFT_SLUG, app._dirty_document_slugs)
        finally:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = original

    async def test_top_notebook_proposal_buttons_are_visible(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()

            notebook_row = app.query_one(f"#{COMMAND_BAR_NOTEBOOK_ID}")
            self.assertEqual(notebook_row.styles.height.value, 1)
            self.assertEqual(notebook_row.styles.min_height.value, 1)
            self.assertEqual(notebook_row.styles.align_horizontal, "center")
            self.assertEqual(app.query_one(f"#{TOP_TERMINAL_ACCEPT_ID}", Button).label.plain, "Shift+Enter Accept")
            self.assertEqual(app.query_one(f"#{TOP_TERMINAL_REJECT_ID}", Button).label.plain, "Esc Reject")
            self.assertEqual(app.query_one(f"#{TOP_TERMINAL_NEW_CHAT_ID}", Button).label.plain, "Ctrl+Shift+N New Chat")

    async def test_shift_enter_accepts_active_notebook_proposal(self) -> None:
        original = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content
        try:
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await pilot.pause()
                composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                composer.value = "Draft a sharper paragraph"
                app.query_one(WorkflowPane).draft_into_document()
                await pilot.pause()
                await pilot.pause()

                self.assertTrue(app.query_one(DocumentPane).has_pending_preview(CURRENT_DRAFT_SLUG))

                await pilot.press("shift+enter")
                await pilot.pause()
                await pilot.pause()

                self.assertIn("Drafted paragraph.", DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content)
                self.assertFalse(app.query_one(DocumentPane).has_pending_preview(CURRENT_DRAFT_SLUG))
                self.assertIn(CURRENT_DRAFT_SLUG, app._dirty_document_slugs)
                selection = app.query_one(DocumentPane).current_selection_snapshot()
                self.assertIsNotNone(selection)
                self.assertEqual(selection.selected_text, "Drafted paragraph.")
                self.assertEqual(getattr(app.focused, "id", None), WORKFLOW_COMPOSER_INPUT_ID)
        finally:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = original

    async def test_shift_enter_accepts_active_notebook_proposal_from_document_focus(self) -> None:
        original = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content
        try:
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await pilot.pause()
                composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                composer.value = "Draft a sharper paragraph"
                app.query_one(WorkflowPane).draft_into_document()
                await pilot.pause()
                await pilot.pause()

                self.assertTrue(app.query_one(DocumentPane).has_pending_preview(CURRENT_DRAFT_SLUG))
                app.query_one(DocumentPane).focus_editor()
                await pilot.pause()

                await pilot.press("shift+enter")
                await pilot.pause()

                self.assertIn("Drafted paragraph.", DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content)
                self.assertFalse(app.query_one(DocumentPane).has_pending_preview(CURRENT_DRAFT_SLUG))
        finally:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = original

    async def test_escape_rejects_active_notebook_proposal(self) -> None:
        original = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content
        try:
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await pilot.pause()
                composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                composer.value = "Draft a sharper paragraph"
                app.query_one(WorkflowPane).draft_into_document()
                await pilot.pause()
                await pilot.pause()

                self.assertTrue(app.query_one(DocumentPane).has_pending_preview(CURRENT_DRAFT_SLUG))

                await pilot.press("escape")
                await pilot.pause()

                self.assertEqual(DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content, original)
                self.assertFalse(app.query_one(DocumentPane).has_pending_preview(CURRENT_DRAFT_SLUG))
                self.assertNotIn(CURRENT_DRAFT_SLUG, app._dirty_document_slugs)
        finally:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = original

    async def test_escape_rejects_active_notebook_proposal_from_card_focus(self) -> None:
        original = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content
        try:
            app = ShellWorkflowTestApp(FakeBackend(configured=True))
            async with app.run_test() as pilot:
                await pilot.pause()
                composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                composer.value = "Draft a sharper paragraph"
                app.query_one(WorkflowPane).draft_into_document()
                await pilot.pause()
                await pilot.pause()

                self.assertTrue(app.query_one(DocumentPane).has_pending_preview(CURRENT_DRAFT_SLUG))
                app.query_one("#rewrite-apply", Button).focus()
                await pilot.pause()

                await pilot.press("escape")
                await pilot.pause()

                self.assertEqual(DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content, original)
                self.assertFalse(app.query_one(DocumentPane).has_pending_preview(CURRENT_DRAFT_SLUG))
        finally:
            DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG].content = original

    async def test_shift_enter_confirms_active_action_request_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=False))
                async with app.run_test() as pilot:
                    await pilot.pause()
                    created = await app.dispatch_app_action(
                        "create_memo",
                        {"title": "Shortcut Delete Memo"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()
                    self.assertEqual(created.status, "completed")

                    workflow = app.query_one(WorkflowPane)
                    composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                    composer.value = "Delete Shortcut Delete Memo."
                    workflow.send_active_message()
                    await pilot.pause()
                    self.assertTrue(any(isinstance(entry, HistoryActionRequestEntry) for entry in workflow.active_chat.history_entries))

                    await pilot.press("shift+enter")
                    for _ in range(6):
                        await pilot.pause()
                        if app._trash_id_by_slug:
                            break

                    self.assertEqual(len(app._trash_id_by_slug), 1)
                    self.assertFalse(any(isinstance(entry, HistoryActionRequestEntry) for entry in workflow.active_chat.history_entries))
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_escape_cancels_active_action_request_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
            os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = tmp
            try:
                app = ShellWorkflowTestApp(FakeBackend(configured=False))
                async with app.run_test() as pilot:
                    await pilot.pause()
                    created = await app.dispatch_app_action(
                        "create_memo",
                        {"title": "Shortcut Cancel Memo"},
                        source="model_tool",
                        confirmed=True,
                    )
                    await pilot.pause()
                    self.assertEqual(created.status, "completed")

                    workflow = app.query_one(WorkflowPane)
                    composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                    composer.value = "Delete Shortcut Cancel Memo."
                    workflow.send_active_message()
                    await pilot.pause()
                    self.assertTrue(any(isinstance(entry, HistoryActionRequestEntry) for entry in workflow.active_chat.history_entries))

                    await pilot.press("escape")
                    await pilot.pause()

                    self.assertFalse(app._trash_id_by_slug)
                    self.assertFalse(any(isinstance(entry, HistoryActionRequestEntry) for entry in workflow.active_chat.history_entries))
                    self.assertTrue(
                        any(
                            isinstance(entry, HistoryActionResultEntry)
                            and entry.action_id == "move_document_to_trash"
                            and entry.status == "refused"
                            for entry in workflow.active_chat.history_entries
                        )
                    )
            finally:
                if previous is None:
                    os.environ.pop("EXEGESIS_TEXTUAL_PROJECTS_DIR", None)
                else:
                    os.environ["EXEGESIS_TEXTUAL_PROJECTS_DIR"] = previous

    async def test_top_terminal_new_chat_button_creates_chat(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            self.assertEqual(len(app.query_one(WorkflowPane)._open_tabs), 1)
            await pilot.click(f"#{TOP_TERMINAL_NEW_CHAT_ID}")
            await pilot.pause()
            self.assertEqual(len(app.query_one(WorkflowPane)._open_tabs), 2)

    async def test_terminal_new_chat_shortcut_creates_chat(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            workflow = app.query_one(WorkflowPane)
            self.assertEqual(len(workflow._open_tabs), 1)

            await pilot.press("ctrl+shift+n")
            await pilot.pause()

            self.assertEqual(len(workflow._open_tabs), 2)

    async def test_ctrl_w_closes_chat_when_notebook_has_focus(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            workflow = app.query_one(WorkflowPane)
            await workflow.new_chat()
            await pilot.pause()
            self.assertEqual(len(workflow._open_tabs), 2)

            workflow.focus_editor()
            await pilot.pause()
            await pilot.press("ctrl+w")
            await pilot.pause()

            self.assertEqual(len(workflow._open_tabs), 1)
            self.assertEqual(workflow.active_chat.slug, "chat-main")

    async def test_model_close_chat_action_closes_secondary_chat_only(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            workflow = app.query_one(WorkflowPane)
            await workflow.new_chat()
            await pilot.pause()

            result = await app.dispatch_app_action("close_chat", {}, source="model_tool", confirmed=True)
            await pilot.pause()

            self.assertEqual(result.status, "completed")
            self.assertEqual(len(workflow._open_tabs), 1)
            self.assertEqual(workflow.active_chat.slug, "chat-main")

            main_result = await app.dispatch_app_action("close_chat", {}, source="model_tool", confirmed=True)

            self.assertEqual(main_result.status, "refused")
            self.assertEqual(len(workflow._open_tabs), 1)
            self.assertEqual(workflow.active_chat.slug, "chat-main")

    async def test_close_chat_action_card_does_not_append_result_to_main_chat(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            workflow = app.query_one(WorkflowPane)
            secondary = await workflow.new_chat()
            request = HistoryActionRequestEntry(
                "close_chat",
                "Close chat",
                "Close chat requires confirmation before Exegesis changes project state.",
            )
            secondary.history_entries.append(request)
            await pilot.pause()

            await workflow.on_action_request_card_confirm_requested(ActionRequestCard.ConfirmRequested(ActionRequestCard(request), request))
            await pilot.pause()

            self.assertEqual(workflow.active_chat.slug, "chat-main")
            self.assertFalse(any(isinstance(entry, HistoryActionResultEntry) for entry in workflow.active_chat.history_entries))
            self.assertTrue(any(isinstance(entry, HistoryActionResultEntry) for entry in secondary.history_entries))

    async def test_top_terminal_save_button_saves_transcript(self) -> None:
        before = set(DOCUMENT_FIXTURES)
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        try:
            async with app.run_test() as pilot:
                await pilot.pause()
                composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                composer.value = "Say hello"
                app.query_one(WorkflowPane).send_active_message()
                await pilot.pause()
                app.action_terminal_save()
                await pilot.pause()

                self.assertIn("transcript-chat-main", DOCUMENT_FIXTURES)
                project_transcripts = [
                    slug
                    for slug in DOCUMENT_FIXTURES
                    if slug not in before and slug.startswith("transcript-") and slug != "transcript-chat-main"
                ]
                self.assertEqual(len(project_transcripts), 1)
                transcript_slug = project_transcripts[0]
                transcript_id = app._document_id_by_slug[transcript_slug]
                transcript_path = Path(self._projects_tmp.name) / "demo-project" / transcript_id
                self.assertTrue(transcript_path.exists())
                transcript_text = transcript_path.read_text(encoding="utf-8")
                self.assertTrue(transcript_text.startswith("# Main chat\n\n- Source: chat-main\n"))
                self.assertIn("- Status: Live notebook chat with retrieval, basket, provider, and harness wiring.", transcript_text)
                self.assertIn("**User:**\n\nSay hello", transcript_text)
                self.assertIn("**Assistant:**\n\nhello world", transcript_text)
                self.assertNotIn("**assistant**", transcript_text)
                self.assertNotIn("shell-only", transcript_text)
                self.assertNotIn("no retrieval", transcript_text)
        finally:
            for slug in set(DOCUMENT_FIXTURES) - before:
                DOCUMENT_FIXTURES.pop(slug, None)

    async def test_notebook_compact_button_saves_full_transcript_in_compacted_conversations(self) -> None:
        before = set(DOCUMENT_FIXTURES)
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        try:
            async with app.run_test() as pilot:
                await pilot.pause()
                composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                composer.value = "Say hello before compacting"
                app.query_one(WorkflowPane).send_active_message()
                await pilot.pause()

                app.query_one(WorkflowPane).query_one(f"#{WORKFLOW_COMPACT_CHAT_ID}", Button).press()
                await pilot.pause()

                compacted_slugs = [
                    slug
                    for slug in DOCUMENT_FIXTURES
                    if slug not in before
                    and slug.startswith("transcript-")
                    and "Compacted Conversations" in app._document_id_by_slug.get(slug, "")
                ]
                self.assertEqual(len(compacted_slugs), 1)
                compacted_slug = compacted_slugs[0]
                compacted_id = app._document_id_by_slug[compacted_slug]
                self.assertTrue(compacted_id.startswith("transcripts/Compacted Conversations/"))
                transcript_path = Path(self._projects_tmp.name) / "demo-project" / compacted_id
                self.assertTrue(transcript_path.exists())
                self.assertIn("Say hello before compacting", transcript_path.read_text(encoding="utf-8"))

                history = app.query_one(WorkflowPane).active_chat.history_entries
                self.assertTrue(any(isinstance(entry, HistoryCompactionEntry) for entry in history))
                self.assertIn("using compacted notebook context", app.query_one(WorkflowPane).active_chat.status_note)
        finally:
            for slug in set(DOCUMENT_FIXTURES) - before:
                DOCUMENT_FIXTURES.pop(slug, None)

    async def test_restore_on_compacted_conversation_transcript_starts_new_chat(self) -> None:
        before = set(DOCUMENT_FIXTURES)
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        try:
            async with app.run_test() as pilot:
                await pilot.pause()
                composer = app.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                composer.value = "Preserve this raw conversation"
                app.query_one(WorkflowPane).send_active_message()
                await pilot.pause()
                app.action_terminal_compact()
                await pilot.pause()

                compacted_slug = next(
                    slug
                    for slug in DOCUMENT_FIXTURES
                    if slug not in before and "Compacted Conversations" in app._document_id_by_slug.get(slug, "")
                )
                workflow = app.query_one(WorkflowPane)
                before_tabs = len(workflow._open_tabs)
                tree = app.query_one(ProjectBrowserTree)
                tree.move_cursor(tree._entry_nodes[compacted_slug], animate=False)
                await pilot.pause()

                app.action_restore_selected_trash_item()
                await pilot.pause()

                self.assertEqual(len(workflow._open_tabs), before_tabs + 1)
                self.assertTrue(workflow.active_chat.title.startswith("Restored:"))
                rendered = workflow._rendered_history_text(workflow.active_chat)
                self.assertIn("Preserve this raw conversation", rendered)
        finally:
            for slug in set(DOCUMENT_FIXTURES) - before:
                DOCUMENT_FIXTURES.pop(slug, None)

    async def test_context_early_threshold_shows_compaction_choice_card_but_still_sends(self) -> None:
        before = set(DOCUMENT_FIXTURES)
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        try:
            async with app.run_test() as pilot:
                await pilot.pause()
                workflow = app.query_one(WorkflowPane)
                workflow.active_chat.history_entries.extend(
                    [
                        HistoryStatusEntry("Older planning turn."),
                        HistoryStatusEntry("Older revision turn."),
                    ]
                )
                workflow._estimated_used_tokens = lambda _chat: 197_000  # type: ignore[method-assign]
                composer = workflow.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                composer.value = "Continue after early compaction warning"

                workflow.send_active_message()
                await pilot.pause()

                self.assertEqual(app._backend.last_mode, "chat")
                self.assertTrue(any(isinstance(entry, HistoryCompactionPromptEntry) for entry in workflow.active_chat.history_entries))
                self.assertFalse(any("Compacted Conversations" in app._document_id_by_slug.get(slug, "") for slug in set(DOCUMENT_FIXTURES) - before))
                rendered = workflow._rendered_history_text(workflow.active_chat)
                self.assertIn("getting long", rendered)
                self.assertIn("Compact to Continue", rendered)
                self.assertIn("Start New Chat", rendered)
                self.assertTrue(workflow.query_one("#compaction-compact", Button).has_class("compact-action-primary"))
                self.assertTrue(workflow.query_one("#compaction-new-chat", Button).has_class("compact-action-warning"))
        finally:
            for slug in set(DOCUMENT_FIXTURES) - before:
                DOCUMENT_FIXTURES.pop(slug, None)

    async def test_context_strong_threshold_shows_compaction_choice_card_but_still_sends(self) -> None:
        before = set(DOCUMENT_FIXTURES)
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        try:
            async with app.run_test() as pilot:
                await pilot.pause()
                workflow = app.query_one(WorkflowPane)
                workflow.active_chat.history_entries.extend(
                    [
                        HistoryStatusEntry("Older planning turn."),
                        HistoryStatusEntry("Older revision turn."),
                    ]
                )
                workflow._estimated_used_tokens = lambda _chat: 236_000  # type: ignore[method-assign]
                composer = workflow.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                composer.value = "Continue after compaction"

                workflow.send_active_message()
                await pilot.pause()

                self.assertEqual(app._backend.last_mode, "chat")
                self.assertTrue(any(isinstance(entry, HistoryCompactionPromptEntry) for entry in workflow.active_chat.history_entries))
                self.assertFalse(any("Compacted Conversations" in app._document_id_by_slug.get(slug, "") for slug in set(DOCUMENT_FIXTURES) - before))
                rendered = workflow._rendered_history_text(workflow.active_chat)
                self.assertIn("Compact to Continue", rendered)
                self.assertIn("Start New Chat", rendered)
        finally:
            for slug in set(DOCUMENT_FIXTURES) - before:
                DOCUMENT_FIXTURES.pop(slug, None)

    async def test_compaction_prompt_compact_button_saves_transcript(self) -> None:
        before = set(DOCUMENT_FIXTURES)
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        try:
            async with app.run_test() as pilot:
                await pilot.pause()
                workflow = app.query_one(WorkflowPane)
                workflow.active_chat.history_entries.extend(
                    [HistoryStatusEntry("Older planning turn."), HistoryStatusEntry("Older revision turn.")]
                )
                workflow._estimated_used_tokens = lambda _chat: 236_000  # type: ignore[method-assign]
                composer = workflow.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                composer.value = "Continue after compaction"
                workflow.send_active_message()
                await pilot.pause()

                prompt = next(entry for entry in workflow.active_chat.history_entries if isinstance(entry, HistoryCompactionPromptEntry))
                await workflow.on_compaction_prompt_card_compact_requested(type("Msg", (), {"card": object()})())  # type: ignore[arg-type]
                await pilot.pause()

                self.assertNotIn(prompt, workflow.active_chat.history_entries)
                self.assertTrue(any(isinstance(entry, HistoryCompactionEntry) for entry in workflow.active_chat.history_entries))
                compacted_slugs = [
                    slug
                    for slug in DOCUMENT_FIXTURES
                    if slug not in before and "Compacted Conversations" in app._document_id_by_slug.get(slug, "")
                ]
                self.assertEqual(len(compacted_slugs), 1)
        finally:
            for slug in set(DOCUMENT_FIXTURES) - before:
                DOCUMENT_FIXTURES.pop(slug, None)

    async def test_compaction_prompt_new_chat_button_starts_new_chat_without_compacting(self) -> None:
        before = set(DOCUMENT_FIXTURES)
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        try:
            async with app.run_test() as pilot:
                await pilot.pause()
                workflow = app.query_one(WorkflowPane)
                workflow.active_chat.history_entries.extend(
                    [HistoryStatusEntry("Older planning turn."), HistoryStatusEntry("Older revision turn.")]
                )
                workflow._estimated_used_tokens = lambda _chat: 236_000  # type: ignore[method-assign]
                composer = workflow.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
                composer.value = "Start a fresh chat instead"
                workflow.send_active_message()
                await pilot.pause()
                before_tabs = len(workflow._open_tabs)

                await workflow.on_compaction_prompt_card_new_chat_requested(type("Msg", (), {"card": object()})())  # type: ignore[arg-type]
                await pilot.pause()

                self.assertEqual(len(workflow._open_tabs), before_tabs + 1)
                self.assertFalse(any("Compacted Conversations" in app._document_id_by_slug.get(slug, "") for slug in set(DOCUMENT_FIXTURES) - before))
        finally:
            for slug in set(DOCUMENT_FIXTURES) - before:
                DOCUMENT_FIXTURES.pop(slug, None)

    async def test_full_estimated_context_warns_but_still_sends(self) -> None:
        app = ShellWorkflowTestApp(FakeBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            workflow = app.query_one(WorkflowPane)
            workflow._estimated_used_tokens = lambda _chat: 262_144  # type: ignore[method-assign]
            composer = workflow.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "This should not send"

            workflow.send_active_message()
            await pilot.pause()

            self.assertEqual(app._backend.last_mode, "chat")
            rendered = workflow._rendered_history_text(workflow.active_chat)
            self.assertIn("Compact to Continue", rendered)
            self.assertIn("Start New Chat", rendered)
            self.assertIn("hello world", rendered)

    async def test_model_context_error_forces_compaction_choice(self) -> None:
        app = ShellWorkflowTestApp(ContextLimitBackend(configured=True))
        async with app.run_test() as pilot:
            await pilot.pause()
            workflow = app.query_one(WorkflowPane)
            composer = workflow.query_one(f"#{WORKFLOW_COMPOSER_INPUT_ID}", Input)
            composer.value = "This should hit provider context limits"

            workflow.send_active_message()
            await pilot.pause()

            self.assertEqual(app._backend.last_mode, "chat")
            rendered = workflow._rendered_history_text(workflow.active_chat)
            self.assertIn("context length exceeded", rendered)
            self.assertIn("Compact to Continue", rendered)
            self.assertIn("Start New Chat", rendered)
            self.assertIn("Model reported context limit", workflow._status_message)


if __name__ == "__main__":
    unittest.main()
