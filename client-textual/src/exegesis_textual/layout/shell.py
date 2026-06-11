from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from math import ceil
import os
from pathlib import Path
import re
import shutil
from uuid import uuid4
from urllib.parse import parse_qs, quote, unquote, urlencode, urlparse

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button, Input, LoadingIndicator, Markdown, OptionList, Select, Static, TabbedContent, Tree
from textual.widgets.option_list import Option

from exegesis_textual.actions.registry import (
    AppActionResult,
    AppActionSource,
    AppActionSpec,
    app_action_specs,
    get_app_action_spec,
)
from exegesis_textual.cards.patch_card import PatchReviewCardData
from exegesis_textual.commands.palette import ExegesisCommandProvider
from exegesis_textual.engine_adapter import ShellEngineAdapter
from exegesis_textual.layout.basket_controller import BasketControllerMixin
from exegesis_textual.layout.inspector_controller import InspectorControllerMixin
from exegesis_textual.layout.blueprint import PaneBlueprint, SHELL_BLUEPRINT, ShellBlueprint
from exegesis_textual.layout.notebook_controller import NotebookControllerMixin
from exegesis_textual.layout.labels import shortcut_label
from exegesis_textual.layout.styles import SHELL_CSS
from exegesis_textual.layout.project_controller import ProjectControllerMixin
from exegesis_textual.layout.modals import (
    DEFAULT_IMPORT_CATEGORY,
    IMPORTABLE_PROJECT_CATEGORIES,
    DUPLICATE_CANCEL_ID,
    DUPLICATE_CANCEL_IMPORT_ID,
    DUPLICATE_SKIP_ALL_IMPORT_ID,
    DUPLICATE_RENAME_INPUT_ID,
    DUPLICATE_REPLACE_ALL_ID,
    IMPORT_BROWSER_OPTIONS_ID,
    PROJECT_PICKER_OPTIONS_ID,
    PROJECT_DUPLICATE_CANCEL_ID,
    PROJECT_DUPLICATE_RENAME_ID,
    PROJECT_DUPLICATE_RENAME_INPUT_ID,
    PROJECT_DUPLICATE_REPLACE_ID,
    PROJECT_RENAME_ACTIVE_INPUT_ID,
    PROJECT_RENAME_INPUT_ID,
    PROJECT_UPDATE_CANCEL_ID,
    PROJECT_UPDATE_CONFIRM_ID,
    PROJECT_UPDATE_SELECTED_FOLDER_ID,
    PROJECT_UPDATE_TITLE_INPUT_ID,
    PROJECTS_DIRECTORY_CREATE_FOLDER_ID,
    PROJECTS_DIRECTORY_NEW_FOLDER_INPUT_ID,
    PROJECTS_DIRECTORY_PATH_ID,
    SUMMARY_PROGRESS_CANCEL_ID,
    SUMMARY_PROGRESS_MODAL_ID,
    TRASH_CANCEL_ID,
    TRASH_PERMANENT_DELETE_ID,
    TRASH_RESTORE_ID,
    UpdateFolderPickerTree,
    DeleteFolderConfirmModal,
    DeleteProjectConfirmModal,
    DuplicateDocumentModal,
    DuplicateProjectModal,
    ImportMarkdownModal,
    ImportProgressModal,
    ModelSettingsAction,
    ModelSettingsModal,
    NewProjectFolderModal,
    NewProjectModal,
    OpenProjectModal,
    PermanentDeleteTrashConfirmModal,
    ProjectBrowserAction,
    RenameActiveProjectModal,
    RenameProjectEntryModal,
    SelectProjectsDirectoryModal,
    SummaryProgressModal,
    TranscriptWarningModal,
    TrashDocumentModal,
    UpdateProjectItemModal,
)
from exegesis_engine.state.models import BasketItem
from exegesis_textual.panes.basket_pane import (
    BASKET_DOCUMENTS_LIST_ID,
    BASKET_EXCERPTS_LIST_ID,
    BASKET_PANE_COPY,
    BasketEntry,
    BasketPane,
)
from exegesis_textual.panes.document_pane import (
    CURRENT_DRAFT_SLUG,
    DOCUMENT_FIXTURES,
    DOCUMENT_PANE_COPY,
    DOCUMENT_TABBED_CONTENT_ID,
    DocumentPane,
    PendingRewritePreview,
    clean_generated_rewrite_text,
    load_document_fixture_content,
    register_document_fixture,
)
from exegesis_textual.panes.inspector_pane import InspectorPane
from exegesis_textual.panes.project_pane import (
    CURRENT_DRAFT_BULLETS,
    CURRENT_DRAFT_LOCATION,
    CURRENT_DRAFT_NAME,
    CURRENT_DRAFT_SUMMARY,
    PROJECT_ENTRIES,
    PROJECT_IMPORT_ID,
    PROJECT_NEW_FOLDER_ID,
    PROJECT_NAME,
    PROJECT_NEW_DRAFT_ID,
    PROJECT_NEW_PROJECT_ID,
    PROJECT_NEW_LITERATURE_ID,
    PROJECT_NEW_MEMO_ID,
    PROJECT_NEW_SUMMARY_ID,
    PROJECT_OPEN_PROJECT_ID,
    PROJECT_NEW_TRANSCRIPT_ID,
    PROJECT_PANE_COPY,
    PROJECT_TRASH_DELETE_ID,
    PROJECT_TRASH_RESTORE_ID,
    ProjectEntry,
    ProjectNodeInfo,
    ProjectPane,
)
from exegesis_textual.services.project_fixtures import (
    DEFAULT_EMPTY_PROJECT_NAME,
    DEFAULT_PROJECT_DOCUMENT_IDS,
    DEFAULT_PROJECT_NAMES,
    NEW_PROJECT_CURRENT_DRAFT_CONTENT,
    NEW_PROJECT_CURRENT_DRAFT_ENTRY,
    PROJECT_MANIFEST_PATH,
    default_project_fixture_content,
    reset_default_demo_project,
)
from exegesis_textual.services.imports import (
    MARKDOWN_EXTENSIONS,
    browseable_import_entries,
    importable_markdown_files_in_folder,
    is_markdown_file,
    is_safe_external_link,
    path_has_hidden_part,
)
from exegesis_textual.services.credentials import CredentialStoreError
from exegesis_textual.services.projects import (
    LOCAL_DEVELOPER_ENV,
    ProjectRecord,
    is_local_developer_mode,
    safe_project_dir_name,
    save_textual_last_project_name,
    save_textual_projects_dir,
    textual_last_project_name,
    textual_projects_dir,
    textual_repo_root,
)
from exegesis_textual.services.model_settings import PROVIDER_OPTIONS
from exegesis_textual.workflow.mistral_chat import ChatMessage, MistralChatBackend, ShellChatContext, TerminalChatBackend
from exegesis_textual.workflow.rewrite_adapter import MockRewriteSessionAdapter
from exegesis_textual.workflow.workflow_pane import (
    WORKFLOW_CARD_MAP,
    WORKFLOW_PANE_COPY,
    WORKFLOW_TABBED_CONTENT_ID,
    RewriteRequestTarget,
    WorkflowPane,
)


def _normalized_heading_label(value: str) -> str:
    normalized = value.strip().lstrip("#").strip()
    normalized = normalized.strip("*_`").strip()
    normalized = normalized.rstrip(":").strip()
    return " ".join(normalized.split()).casefold()


FOOTER_CONFIDENTIALITY_ID = "shell-footer-confidentiality"
NON_CONFIDENTIAL_MODE_LABEL = "Non-confidential"
CONFIDENTIAL_MODE_LABEL = "Confidential"
FOOTER_HINTS_ID = "shell-footer-hints"
FOOTER_PALETTE_ID = "shell-footer-palette"
FOOTER_CLOSE_ID = "shell-footer-close"
FOOTER_RESTART_ID = "shell-footer-restart"
FOOTER_QUIT_ID = "shell-footer-quit"
FOOTER_PROJECT_ID = "shell-footer-project"
FOOTER_DOCUMENT_ID = "shell-footer-document"
FOOTER_BASKET_ID = "shell-footer-basket"
FOOTER_TERMINAL_ID = "shell-footer-terminal"
FOOTER_INSPECTOR_ID = "shell-footer-inspector"
COMMAND_BAR_ID = "shell-command-bar"
COMMAND_BAR_TOP_ID = "shell-command-bar-top"
COMMAND_BAR_BOTTOM_ID = "shell-command-bar-bottom"
COMMAND_BAR_FILE_ID = "shell-command-bar-file"
COMMAND_BAR_SUMMARY_ID = "shell-command-bar-summary"
COMMAND_BAR_TERMINAL_ID = "shell-command-bar-terminal"
COMMAND_BAR_NOTEBOOK_ID = "shell-command-bar-notebook"
TOP_EXCERPT_ID = "top-add-excerpt"
TOP_FILE_ID = "top-add-file"
TOP_NEW_DRAFT_ID = "top-new-draft"
TOP_NEW_MEMO_ID = "top-new-memo"
TOP_NEW_SUMMARY_ID = "top-new-summary"
TOP_NEW_TRANSCRIPT_ID = "top-new-transcript"
TOP_NEW_LITERATURE_ID = "top-new-literature"
TOP_NEW_FOLDER_ID = "top-new-folder"
TOP_IMPORT_ID = "top-import"
TOP_SAVE_DOCUMENT_ID = "top-save-document"
TOP_MOVE_TO_TRASH_ID = "top-move-to-trash"
TOP_RESTORE_TRASH_ID = "top-restore-trash"
TOP_UPDATE_ITEM_ID = "top-update-item"
TOP_PERMANENT_DELETE_TRASH_ID = "top-permanent-delete-trash"
TOP_DELETE_ID = "top-delete"
TOP_SAVE_SHORT_SUMMARY_ID = "top-save-short-summary"
TOP_SAVE_MEDIUM_SUMMARY_ID = "top-save-medium-summary"
TOP_SAVE_LONG_SUMMARY_ID = "top-save-long-summary"
TOP_TERMINAL_SEARCH_ID = "top-terminal-search"
TOP_TERMINAL_DRAFT_ID = "top-terminal-draft"
TOP_TERMINAL_REWRITE_ID = "top-terminal-rewrite"
TOP_TERMINAL_ACCEPT_ID = "top-terminal-accept"
TOP_TERMINAL_REJECT_ID = "top-terminal-reject"
TOP_TERMINAL_NEW_CHAT_ID = "top-terminal-new-chat"
TOP_TERMINAL_SAVE_ID = "top-terminal-save"
TOP_TERMINAL_COMPACT_ID = "top-terminal-compact"


def _binding_for_spec(spec: AppActionSpec) -> Binding | None:
    if not spec.shortcut:
        return None
    if spec.shortcut == "delete":
        # Delete is focus-sensitive in project and basket panes; a global shell binding steals it.
        return None
    return Binding(spec.shortcut, spec.action_name, spec.label, priority=True)


def _shell_bindings() -> list[Binding]:
    bindings = [
        binding
        for spec in app_action_specs(include_local_developer=True)
        if (binding := _binding_for_spec(spec)) is not None
    ]
    # Backspace should behave like Delete, but the visible shortcut stays Ctrl+Shift+Del.
    bindings.append(
        Binding(
            "ctrl+shift+backspace",
            "permanently_delete_selected_trash_item",
            "Permanently delete trash item",
            priority=True,
        )
    )
    return bindings


TOP_BUTTON_ACTIONS: dict[str, str] = {
    TOP_EXCERPT_ID: "add_excerpt_to_basket",
    TOP_FILE_ID: "add_document_to_basket",
    TOP_NEW_DRAFT_ID: "create_draft",
    TOP_NEW_MEMO_ID: "create_memo",
    TOP_NEW_SUMMARY_ID: "create_summary",
    TOP_NEW_TRANSCRIPT_ID: "create_transcript",
    TOP_NEW_LITERATURE_ID: "create_literature",
    TOP_NEW_FOLDER_ID: "create_folder",
    TOP_UPDATE_ITEM_ID: "update_selected_project_item",
    TOP_IMPORT_ID: "import_document",
    TOP_SAVE_DOCUMENT_ID: "save_current_document",
    TOP_MOVE_TO_TRASH_ID: "move_document_to_trash",
    TOP_RESTORE_TRASH_ID: "restore_trash_item",
    TOP_PERMANENT_DELETE_TRASH_ID: "permanently_delete_trash_item",
    TOP_SAVE_SHORT_SUMMARY_ID: "save_short_summary",
    TOP_SAVE_MEDIUM_SUMMARY_ID: "save_medium_summary",
    TOP_SAVE_LONG_SUMMARY_ID: "save_long_summary",
    TOP_TERMINAL_SEARCH_ID: "search_documents",
    TOP_TERMINAL_DRAFT_ID: "draft_into_document",
    TOP_TERMINAL_REWRITE_ID: "rewrite_selection",
    TOP_TERMINAL_ACCEPT_ID: "accept_proposal",
    TOP_TERMINAL_REJECT_ID: "reject_proposal",
    TOP_TERMINAL_NEW_CHAT_ID: "new_chat",
    TOP_TERMINAL_SAVE_ID: "save_transcript",
    TOP_TERMINAL_COMPACT_ID: "compact_chat",
}


FOOTER_BUTTON_ACTIONS: dict[str, str] = {
    FOOTER_PALETTE_ID: "show_palette",
    FOOTER_RESTART_ID: "restart_exegesis",
    FOOTER_QUIT_ID: "quit",
    FOOTER_CLOSE_ID: "close_document_tab",
    FOOTER_PROJECT_ID: "focus_project",
    FOOTER_DOCUMENT_ID: "focus_document",
    FOOTER_BASKET_ID: "focus_basket",
    FOOTER_TERMINAL_ID: "focus_notebook",
    FOOTER_INSPECTOR_ID: "focus_inspector",
}





class QualShellApp(ProjectControllerMixin, BasketControllerMixin, NotebookControllerMixin, InspectorControllerMixin, App[None]):
    """Basic shell scaffold for the future Qual Textual client."""

    TITLE = "Exegesis"
    SUB_TITLE = ""
    COMMANDS = App.COMMANDS | {ExegesisCommandProvider}
    CSS = SHELL_CSS
    BINDINGS = _shell_bindings()

    def __init__(self, workflow_backend: TerminalChatBackend | None = None) -> None:
        super().__init__()
        self.theme = "textual-dark"
        self._rewrite_adapter = MockRewriteSessionAdapter()
        self._workflow_backend = workflow_backend or MistralChatBackend()
        self._engine_adapter = ShellEngineAdapter()
        self._document_id_by_slug: dict[str, str] = {}
        self._trash_id_by_slug: dict[str, str] = {}
        self._trash_metadata_by_slug: dict[str, dict[str, object]] = {}
        self._dirty_document_slugs: set[str] = set()
        self._navigating_search_result = False
        self._project_names = list(DEFAULT_PROJECT_NAMES)
        self._project_records: list[ProjectRecord] = []
        self._projects_base_dir = textual_projects_dir(self._repo_root())
        self._current_project_slug: str | None = None
        self._prompt_for_initial_project = not is_local_developer_mode() and not self._has_project_directories()
        self._current_project_name = self._initial_project_name()
        self._current_project_slug = self._project_slug_for_name(self._current_project_name)
        self._project_root = self._project_root_for_name(self._current_project_name)
        self._current_project_confidentiality = self._project_confidentiality_from_root(self._project_root)
        self._initial_placeholder_project_root = self._project_root if self._prompt_for_initial_project else None
        if self._current_project_name == PROJECT_NAME:
            self._ensure_default_project_documents()
        elif not self._prompt_for_initial_project:
            self._ensure_minimal_project_documents()
        self._engine_adapter.open_project(self._project_root)
        if self._current_project_name == PROJECT_NAME:
            self._map_default_project_documents()
        else:
            self._map_minimal_project_documents()

    def get_system_commands(self, screen):
        for command in super().get_system_commands(screen):
            if command.title == "Theme":
                continue
            yield command

    def compose(self) -> ComposeResult:
        with Vertical(id="shell-status"):
            with Vertical(id=COMMAND_BAR_ID):
                with Horizontal(id=COMMAND_BAR_TOP_ID):
                    yield Button(shortcut_label("Ctrl+Shift+E", "Add excerpt to basket"), id=TOP_EXCERPT_ID, classes="command-link")
                    yield Button(shortcut_label("Ctrl+Shift+B", "Add document to basket"), id=TOP_FILE_ID, classes="command-link")
                    yield Button(shortcut_label("Delete", "Delete basket item"), id=TOP_DELETE_ID, classes="command-link")
                with Horizontal(id=COMMAND_BAR_BOTTOM_ID):
                    yield Button(shortcut_label("Ctrl+Shift+D", "New draft"), id=TOP_NEW_DRAFT_ID, classes="command-link")
                    yield Button(shortcut_label("Ctrl+Shift+M", "New memo"), id=TOP_NEW_MEMO_ID, classes="command-link")
                    yield Button(shortcut_label("Ctrl+Shift+S", "New summary"), id=TOP_NEW_SUMMARY_ID, classes="command-link")
                    yield Button(shortcut_label("Ctrl+Shift+T", "New transcript"), id=TOP_NEW_TRANSCRIPT_ID, classes="command-link")
                    yield Button(shortcut_label("Ctrl+Shift+L", "New literature"), id=TOP_NEW_LITERATURE_ID, classes="command-link")
                    yield Button(shortcut_label("Ctrl+Shift+I", "Import"), id=TOP_IMPORT_ID, classes="command-link")
                with Horizontal(id=COMMAND_BAR_FILE_ID):
                    yield Button(shortcut_label("Ctrl+S", "Save"), id=TOP_SAVE_DOCUMENT_ID, classes="command-link")
                    yield Button(shortcut_label("Ctrl+Shift+F", "New folder"), id=TOP_NEW_FOLDER_ID, classes="command-link")
                    yield Button(shortcut_label("Ctrl+Shift+U", "Update item"), id=TOP_UPDATE_ITEM_ID, classes="command-link")
                    yield Button(shortcut_label("Delete", "Move to trash"), id=TOP_MOVE_TO_TRASH_ID, classes="command-link")
                    yield Button(shortcut_label("Ctrl+Shift+R", "Restore"), id=TOP_RESTORE_TRASH_ID, classes="command-link")
                    yield Button(shortcut_label("Ctrl+Shift+Del", "Delete forever"), id=TOP_PERMANENT_DELETE_TRASH_ID, classes="command-link")
                with Horizontal(id=COMMAND_BAR_SUMMARY_ID):
                    yield Button(shortcut_label("Ctrl+Shift+1", "Short summary"), id=TOP_SAVE_SHORT_SUMMARY_ID, classes="command-link")
                    yield Button(shortcut_label("Ctrl+Shift+2", "Medium summary"), id=TOP_SAVE_MEDIUM_SUMMARY_ID, classes="command-link")
                    yield Button(shortcut_label("Ctrl+Shift+3", "Long summary"), id=TOP_SAVE_LONG_SUMMARY_ID, classes="command-link")
                with Horizontal(id=COMMAND_BAR_TERMINAL_ID):
                    yield Button(shortcut_label("Ctrl+Enter", "Search"), id=TOP_TERMINAL_SEARCH_ID, classes="command-link")
                    yield Button(shortcut_label("Ctrl+Shift+G", "Draft"), id=TOP_TERMINAL_DRAFT_ID, classes="command-link")
                    yield Button(shortcut_label("Ctrl+Shift+W", "Rewrite"), id=TOP_TERMINAL_REWRITE_ID, classes="command-link")
                    yield Button(shortcut_label("Shift+Enter", "Accept"), id=TOP_TERMINAL_ACCEPT_ID, classes="command-link")
                    yield Button(shortcut_label("Esc", "Reject"), id=TOP_TERMINAL_REJECT_ID, classes="command-link")
                with Horizontal(id=COMMAND_BAR_NOTEBOOK_ID):
                    yield Button(shortcut_label("Ctrl+Shift+N", "New Chat"), id=TOP_TERMINAL_NEW_CHAT_ID, classes="command-link")
                    yield Button(shortcut_label("Ctrl+Shift+X", "Save transcript"), id=TOP_TERMINAL_SAVE_ID, classes="command-link")
                    yield Button(shortcut_label("Ctrl+Shift+V", "Compact"), id=TOP_TERMINAL_COMPACT_ID, classes="command-link")
        with Horizontal(id="shell-body"):
            yield ProjectPane()
            with Vertical(id="document-column"):
                yield BasketPane()
                yield DocumentPane()
                yield WorkflowPane(backend=self._workflow_backend)
            with Vertical(id="right-column"):
                yield InspectorPane()
        with Horizontal(id="shell-footer-bar"):
            yield Static(NON_CONFIDENTIAL_MODE_LABEL, id=FOOTER_CONFIDENTIALITY_ID)
            with Horizontal(id=FOOTER_HINTS_ID):
                yield Button(shortcut_label("Ctrl+W", "Close tab"), id=FOOTER_CLOSE_ID, classes="footer-link")
                yield Button(shortcut_label("F1", "Project"), id=FOOTER_PROJECT_ID, classes="footer-link")
                yield Button(shortcut_label("F2", "Document"), id=FOOTER_DOCUMENT_ID, classes="footer-link")
                yield Button(shortcut_label("F3", "Basket"), id=FOOTER_BASKET_ID, classes="footer-link")
                yield Button(shortcut_label("F4", "Notebook"), id=FOOTER_TERMINAL_ID, classes="footer-link")
                yield Button(shortcut_label("F5", "Inspector"), id=FOOTER_INSPECTOR_ID, classes="footer-link")
            if is_local_developer_mode():
                yield Button(shortcut_label("Ctrl+R", "Restart"), id=FOOTER_RESTART_ID, classes="footer-link")
            yield Button(shortcut_label("Ctrl+Q", "Quit"), id=FOOTER_QUIT_ID, classes="footer-link")
            yield Button(shortcut_label("Ctrl+P", "Palette"), id=FOOTER_PALETTE_ID, classes="footer-link")

    def on_mount(self) -> None:
        self._load_engine_project_entries()
        self._sync_footer_bar()
        self._sync_save_controls()
        self.call_after_refresh(
            lambda: self.run_worker(
                self._run_startup_prompts(),
                name="startup-prompts",
                group="startup",
                exclusive=True,
                thread=False,
            )
        )

    async def dispatch_app_action(
        self,
        action_id: str,
        payload: dict[str, object] | None = None,
        source: AppActionSource | str = "system",
        conversation_turn_id: str | None = None,
        *,
        confirmed: bool = False,
    ) -> AppActionResult:
        payload = dict(payload or {})
        try:
            spec = get_app_action_spec(action_id, include_local_developer=is_local_developer_mode())
        except KeyError:
            return AppActionResult("failed", f"Unknown app action: {action_id}")
        if source == "model_tool" and spec.safety == "system_only":
            return AppActionResult(
                "refused",
                f"{spec.label} must be invoked manually from Exegesis.",
                audit_metadata={"action_id": action_id, "source": str(source)},
            )
        if source == "model_tool" and spec.safety == "confirm_required" and not confirmed:
            preflight = self._preflight_confirm_required_action(
                spec,
                payload,
                source=str(source),
                conversation_turn_id=conversation_turn_id,
            )
            if preflight is not None:
                return preflight
            return AppActionResult(
                "pending_confirmation",
                f"{spec.label} requires confirmation before Exegesis changes project state.",
                card={
                    "type": "action_request",
                    "action_id": action_id,
                    "payload": payload,
                    "conversation_turn_id": conversation_turn_id,
                },
                audit_metadata={"action_id": action_id, "source": str(source)},
            )
        try:
            return await self._execute_app_action(spec, payload, source=str(source), confirmed=confirmed)
        except Exception as exc:
            return AppActionResult(
                "failed",
                f"{spec.label} failed: {exc}",
                audit_metadata={"action_id": action_id, "source": str(source)},
            )

    def _preflight_confirm_required_action(
        self,
        spec: AppActionSpec,
        payload: dict[str, object],
        *,
        source: str,
        conversation_turn_id: str | None,
    ) -> AppActionResult | None:
        if spec.id != "add_document_to_basket":
            return None
        if self._payload_requests_basket_excerpt(payload):
            return AppActionResult(
                "pending_confirmation",
                "Add excerpt requires confirmation before Exegesis changes project state.",
                card={
                    "type": "action_request",
                    "action_id": "add_excerpt_to_basket",
                    "label": "Add excerpt",
                    "payload": payload,
                    "conversation_turn_id": conversation_turn_id,
                },
                audit_metadata={"action_id": "add_excerpt_to_basket", "source": source},
            )
        slug = self._find_project_document_slug(
            payload.get("document")
            or payload.get("document_slug")
            or payload.get("document_title")
            or payload.get("source_document")
            or payload.get("source_document_slug")
            or payload.get("source_title")
            or payload.get("title")
            or payload.get("location")
        )
        fixture = DOCUMENT_FIXTURES.get(slug or "")
        if fixture is not None and fixture.is_transcript and not self._current_project_is_confidential():
            return AppActionResult(
                "refused",
                "Full transcripts cannot be added to the basket in a non-confidential project. Add excerpts instead.",
                audit_metadata={"action_id": spec.id, "source": source},
            )
        return None

    async def _execute_app_action(
        self,
        spec: AppActionSpec,
        payload: dict[str, object],
        *,
        source: str,
        confirmed: bool,
    ) -> AppActionResult:
        action_id = spec.id
        del confirmed
        if action_id == "search_documents":
            query = str(payload.get("query") or "").strip()
            if query:
                results = self.shell_search_documents(query)
                titles = ", ".join(str(item.get("title", "")) for item in results[:3] if item.get("title"))
                suffix = f": {titles}" if titles else ""
                return AppActionResult(
                    "completed",
                    f"Search found {len(results)} matching document(s){suffix}.",
                    data={"query": query, "results": results},
                    audit_metadata={"action_id": action_id, "source": source},
                )
            self.action_terminal_search()
            return AppActionResult("completed", "Search command opened from the notebook composer.")
        if action_id == "open_document":
            document = str(payload.get("document") or "").strip()
            slug = self._find_document_slug(document)
            if slug is None:
                return AppActionResult("failed", f"Document not found: {document or '(blank)'}")
            document_pane = self.query_one(DocumentPane)
            await document_pane.open_document(slug, focus=False)
            self._sync_save_controls()
            self._show_document_subject(DOCUMENT_FIXTURES[slug])
            return AppActionResult("completed", f"Opened {DOCUMENT_FIXTURES[slug].title}.", data={"document_slug": slug})
        if action_id == "open_search_result":
            slug = str(payload.get("document_slug") or "").strip()
            if slug not in DOCUMENT_FIXTURES:
                return AppActionResult("failed", f"Search result document is unavailable: {slug or '(blank)'}")
            start = self._coerce_dispatch_int(payload.get("start"))
            end = self._coerce_dispatch_int(payload.get("end"))
            match_range = (start, end) if start is not None and end is not None else None
            document_pane = self.query_one(DocumentPane)
            await document_pane.open_document_with_selection(slug, match_range, focus=False)
            self._sync_save_controls()
            self._show_document_subject(DOCUMENT_FIXTURES[slug], refresh_notebook_context=False)
            return AppActionResult("completed", f"Opened search result in {DOCUMENT_FIXTURES[slug].title}.")
        if action_id == "show_context_status":
            context = self.shell_chat_context()
            chat = self.query_one(WorkflowPane).active_chat
            return AppActionResult(
                "completed",
                f"Context status: {chat.context_available}. Active document: {context.get('document_title', 'current document')}.",
                data={
                    "context_available": chat.context_available,
                    "document_title": context.get("document_title", ""),
                    "document_type": context.get("document_type", ""),
                },
            )
        if action_id == "draft_into_document":
            self._set_notebook_instruction(payload.get("instruction"))
            heading = str(payload.get("insert_after_heading") or payload.get("after_heading") or "").strip()
            target_range = self._draft_target_range_from_payload(payload)
            if heading and target_range is None:
                return AppActionResult("failed", f"Draft target heading not found: {heading}")
            workflow = self.query_one(WorkflowPane)
            show_user_prompt = source != "model_tool"
            if target_range is None:
                self._save_dirty_documents()
                workflow.draft_into_document(show_user_prompt=show_user_prompt)
            else:
                self._save_dirty_documents()
                workflow.draft_into_document(target_range=target_range, block_insert=True, show_user_prompt=show_user_prompt)
            if workflow.active_chat.generating:
                return AppActionResult("completed", "Draft proposal requested.")
            return AppActionResult("failed", workflow._status_message or "Draft proposal could not be started.")
        if action_id == "rewrite_selection":
            self._set_notebook_instruction(payload.get("instruction"))
            document_pane = self.query_one(DocumentPane)
            heading = self._rewrite_heading_from_payload(payload)
            rewrite_target = self._rewrite_target_from_payload(payload)
            if heading and rewrite_target is None:
                return AppActionResult("failed", f"Rewrite target heading not found or empty: {heading}")
            if rewrite_target is None and not document_pane.selected_text.strip():
                return AppActionResult("failed", "Select text in the document before requesting a rewrite.")
            workflow = self.query_one(WorkflowPane)
            show_user_prompt = source != "model_tool"
            if rewrite_target is None:
                self._save_dirty_documents()
                workflow.rewrite_selection(show_user_prompt=show_user_prompt)
            else:
                self._save_dirty_documents()
                workflow.rewrite_selection(target=rewrite_target, show_user_prompt=show_user_prompt)
            if workflow.active_chat.generating:
                return AppActionResult("completed", "Rewrite proposal requested.")
            return AppActionResult("failed", workflow._status_message or "Rewrite proposal could not be started.")
        if action_id == "accept_proposal":
            return self._decide_active_notebook_proposal_or_card("apply")
        if action_id == "reject_proposal":
            return self._decide_active_notebook_proposal_or_card("reject")
        if action_id == "add_excerpt_to_basket":
            if source == "model_tool" or payload:
                return self._dispatch_add_excerpt_to_basket_from_payload(payload)
            self.action_add_excerpt_to_basket()
            return AppActionResult("completed", "Excerpt add requested.")
        if action_id == "add_document_to_basket":
            if source == "model_tool" or payload.get("document"):
                return self._dispatch_add_document_to_basket_from_payload(payload)
            self.action_add_file_to_basket()
            return AppActionResult("completed", "Document add requested.")
        if action_id == "save_summary":
            length = str(payload.get("length") or "medium").casefold()
            {"short": self.action_save_short_summary, "medium": self.action_save_medium_summary, "long": self.action_save_long_summary}.get(
                length,
                self.action_save_medium_summary,
            )()
            return AppActionResult("completed", f"{length.capitalize()} summary requested.")
        if action_id == "save_transcript":
            self.action_terminal_save()
            return AppActionResult("completed", "Notebook transcript saved.")
        if action_id == "compact_chat":
            self.action_terminal_compact()
            return AppActionResult("completed", "Notebook compaction requested.")
        if action_id == "start_new_chat_from_compaction":
            await self.action_terminal_new_chat()
            return AppActionResult("completed", "Started a new notebook chat.")
        if action_id == "close_chat":
            workflow_pane = self.query_one(WorkflowPane)
            closing_title = workflow_pane.active_chat.title
            if not workflow_pane.active_chat.closable:
                return AppActionResult("refused", "The main chat stays open as the anchor notebook chat.")
            closed = await workflow_pane.close_active_chat()
            if closed:
                active = workflow_pane.active_chat
                self._set_status(f"Closed chat. Active notebook chat: {active.title}")
                self._show_chat_subject(active)
                return AppActionResult("completed", f"Closed {closing_title}.", data={"closed_chat": closing_title})
            return AppActionResult("failed", f"Could not close {closing_title}.")
        if action_id == "move_document_to_trash":
            if source == "model_tool" or payload.get("document"):
                return await self._dispatch_move_to_trash_from_payload(payload)
            await self.action_move_selected_project_document_to_trash()
            return AppActionResult("completed", "Move to trash requested.")
        if action_id == "restore_trash_item":
            if source == "model_tool" or payload.get("trash_item"):
                return self._dispatch_restore_trash_from_payload(payload)
            self.action_restore_selected_trash_item()
            return AppActionResult("completed", "Restore requested.")
        if action_id == "show_palette":
            self.action_show_palette()
            return AppActionResult("completed", "Opened command palette.")
        if action_id == "close_document_tab":
            document_pane = self.query_one(DocumentPane)
            closing_title = document_pane.active_document.title
            self._save_dirty_documents()
            closed = await document_pane.close_active_document()
            if closed:
                active = document_pane.active_document
                self._set_status(f"Closed tab. Active document: {active.title}")
                self._show_document_subject(active)
                return AppActionResult("completed", f"Closed {closing_title}.", data={"closed_document": closing_title})
            return AppActionResult("refused", "The main draft stays open as the anchor document.")
        if action_id == "save_current_document":
            self.action_save_current_document()
            return AppActionResult("completed", "Save document requested.")
        if action_id == "rename_project":
            if source == "model_tool" or payload.get("name"):
                return self._dispatch_rename_project_from_payload(payload)
            self.push_screen(RenameActiveProjectModal(self._current_project_name), callback=self._handle_active_project_rename_result)
            return AppActionResult("completed", "Project rename opened.")
        if action_id == "new_project":
            await self.action_new_project()
            return AppActionResult("completed", "New project requested.")
        if action_id == "open_project_browser":
            await self.action_open_project_browser()
            return AppActionResult("completed", "Project browser opened.")
        if action_id == "change_projects_directory":
            await self.action_change_projects_directory()
            return AppActionResult("completed", "Projects directory chooser opened.")
        if action_id == "model_settings":
            await self.action_model_settings()
            return AppActionResult("completed", "Model Settings opened.")
        if action_id == "create_draft":
            if source == "model_tool" or payload.get("title"):
                return await self._dispatch_create_document_from_payload("Drafts", payload)
            await self.action_create_draft()
            return AppActionResult("completed", "New draft requested.")
        if action_id == "create_memo":
            if source == "model_tool" or payload.get("title"):
                return await self._dispatch_create_document_from_payload("Memos", payload)
            await self.action_create_memo()
            return AppActionResult("completed", "New memo requested.")
        if action_id == "create_summary":
            if source == "model_tool" or payload.get("title"):
                return await self._dispatch_create_document_from_payload("Summaries", payload)
            await self.action_create_summary()
            return AppActionResult("completed", "New summary requested.")
        if action_id == "create_transcript":
            if source == "model_tool" or payload.get("title"):
                return await self._dispatch_create_document_from_payload("Transcripts", payload)
            await self.action_create_transcript()
            return AppActionResult("completed", "New transcript requested.")
        if action_id == "create_literature":
            if source == "model_tool" or payload.get("title"):
                return await self._dispatch_create_document_from_payload("Literature", payload)
            await self.action_create_literature()
            return AppActionResult("completed", "New literature document requested.")
        if action_id == "create_folder":
            if source == "model_tool" or payload.get("name"):
                return self._dispatch_create_folder_from_payload(payload)
            await self.action_create_folder()
            return AppActionResult("completed", "New folder requested.")
        if action_id == "update_selected_project_item":
            if source == "model_tool" or payload:
                return self._dispatch_update_project_item_from_payload(payload)
            await self.action_update_selected_project_item()
            return AppActionResult("completed", "Update item requested.")
        if action_id in {"import_document", "import_folder"}:
            await self.action_import_document()
            return AppActionResult("completed", "Import opened.")
        if action_id == "permanently_delete_trash_item":
            if source == "model_tool" or payload.get("trash_item"):
                return self._dispatch_permanent_delete_from_payload(payload)
            self.action_permanently_delete_selected_trash_item()
            return AppActionResult("completed", "Permanent delete requested.")
        if action_id == "save_short_summary":
            self.action_save_short_summary()
            return AppActionResult("completed", "Short summary requested.")
        if action_id == "save_medium_summary":
            self.action_save_medium_summary()
            return AppActionResult("completed", "Medium summary requested.")
        if action_id == "save_long_summary":
            self.action_save_long_summary()
            return AppActionResult("completed", "Long summary requested.")
        if action_id == "new_chat":
            await self.action_terminal_new_chat()
            return AppActionResult("completed", "New chat requested.")
        if action_id == "restart_exegesis":
            self.action_restart_exegesis()
            return AppActionResult("completed", "Restart requested.")
        if action_id == "quit":
            self.action_quit()
            return AppActionResult("completed", "Quit requested.")
        if action_id == "focus_project":
            self.action_focus_project()
            return AppActionResult("completed", "Focused Project.")
        if action_id == "focus_document":
            self.action_focus_document()
            return AppActionResult("completed", "Focused Document.")
        if action_id == "focus_basket":
            self.action_focus_basket()
            return AppActionResult("completed", "Focused Basket.")
        if action_id == "focus_notebook":
            self.action_focus_workflow()
            return AppActionResult("completed", "Focused Notebook.")
        if action_id == "focus_inspector":
            self.action_focus_inspector()
            return AppActionResult("completed", "Focused Inspector.")
        return AppActionResult("failed", f"No dispatcher implementation for {action_id}.")

    def _draft_target_range_from_payload(self, payload: dict[str, object]) -> tuple[int, int] | None:
        heading = str(payload.get("insert_after_heading") or payload.get("after_heading") or "").strip()
        if not heading:
            return None
        document = self.query_one(DocumentPane).active_document
        return self._document_section_body_range(document.content, heading)

    @staticmethod
    def _rewrite_heading_from_payload(payload: dict[str, object]) -> str:
        return str(
            payload.get("target_heading")
            or payload.get("section_heading")
            or payload.get("rewrite_heading")
            or payload.get("heading")
            or ""
        ).strip()

    def _rewrite_target_from_payload(self, payload: dict[str, object]) -> RewriteRequestTarget | None:
        heading = self._rewrite_heading_from_payload(payload)
        if not heading:
            return None
        document = self.query_one(DocumentPane).active_document
        target_range = self._document_section_body_range(document.content, heading)
        if target_range is None:
            return None
        original_text = document.content[target_range[0] : target_range[1]]
        if not original_text.strip():
            return None
        return RewriteRequestTarget(
            document_slug=document.slug,
            document_title=document.title,
            target_range=target_range,
            original_text=original_text,
            block_insert=True,
        )

    @staticmethod
    def _document_section_body_range(document_text: str, heading: str) -> tuple[int, int] | None:
        target = _normalized_heading_label(heading)
        if not target:
            return None
        lines = document_text.splitlines(keepends=True)
        offset = 0
        for index, line in enumerate(lines):
            stripped = line.strip()
            if not stripped.startswith("#") or _normalized_heading_label(stripped) != target:
                offset += len(line)
                continue
            section_start = offset + len(line)
            section_end = len(document_text)
            next_offset = section_start
            for next_line in lines[index + 1 :]:
                if next_line.strip().startswith("#"):
                    section_end = next_offset
                    break
                next_offset += len(next_line)
            return (section_start, section_end)
        return None

    def _find_document_slug(self, document: str) -> str | None:
        if not document:
            return None
        needle = document.casefold()
        for slug, fixture in DOCUMENT_FIXTURES.items():
            candidates = {slug.casefold(), fixture.title.casefold(), fixture.location.casefold()}
            if needle in candidates:
                return slug
        return next(
            (
                slug
                for slug, fixture in DOCUMENT_FIXTURES.items()
                if needle in slug.casefold() or needle in fixture.title.casefold() or needle in fixture.location.casefold()
            ),
            None,
        )

    @staticmethod
    def _lookup_variants(value: object) -> set[str]:
        text = str(value or "").strip()
        if not text:
            return set()
        normalized = " ".join(text.replace("\\", "/").split()).casefold()
        path = Path(normalized)
        variants = {normalized}
        if path.name:
            variants.add(path.name)
            variants.add(Path(path.name).stem)
        if path.stem:
            variants.add(path.stem)
        if normalized.endswith(".md"):
            variants.add(normalized[:-3])
        return {variant for variant in variants if variant}

    @staticmethod
    def _lookup_tokens(value: object) -> set[str]:
        text = str(value or "").casefold()
        if not text:
            return set()
        stop_words = {
            "a",
            "an",
            "and",
            "document",
            "file",
            "from",
            "in",
            "item",
            "of",
            "recover",
            "restore",
            "the",
            "this",
            "trash",
            "trashed",
        }
        return {
            token
            for token in re.findall(r"[a-z0-9]+", text)
            if token not in stop_words and (len(token) > 2 or token.isdigit())
        }

    @staticmethod
    def _coerce_dispatch_int(value: object) -> int | None:
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @classmethod
    def _payload_requests_basket_excerpt(cls, payload: dict[str, object]) -> bool:
        if any(
            payload.get(key) not in (None, "")
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
        raw_range = payload.get("match_range") or payload.get("range")
        return isinstance(raw_range, (list, tuple)) and len(raw_range) >= 2

    def _card_conflict_result(
        self,
        *,
        action_id: str,
        label: str,
        message: str,
        payload: dict[str, object],
        input_name: str | None = None,
        input_placeholder: str = "",
    ) -> AppActionResult:
        options: list[dict[str, object]] = [
            {"label": "Replace", "payload": {"duplicate_action": "replace"}, "classes": "compact-action-warning"},
        ]
        if input_name:
            options.append({"label": "Rename", "payload": {"duplicate_action": "rename"}, "classes": "compact-action-primary"})
        options.append({"label": "Cancel", "payload": {"duplicate_action": "cancel"}, "classes": "compact-action-warning", "cancel": True})
        card: dict[str, object] = {
            "type": "action_request",
            "action_id": action_id,
            "label": label,
            "payload": payload,
            "options": options,
        }
        if input_name:
            card["input"] = {"name": input_name, "placeholder": input_placeholder}
        return AppActionResult("pending_confirmation", message, card=card)

    def _find_project_document_slug(self, document: object) -> str | None:
        document_text = str(document or "").strip()
        active_slug = self.query_one(DocumentPane).active_document.slug
        active_project_slug = active_slug if active_slug in self._document_id_by_slug else None
        if document_text:
            if document_text.casefold() in {
                "active",
                "active document",
                "active file",
                "current",
                "current document",
                "current file",
                "open document",
                "opened document",
                "selected document",
                "this document",
                "this file",
                "active transcript",
                "current transcript",
                "open transcript",
                "opened transcript",
                "selected transcript",
                "this transcript",
            }:
                return active_project_slug
            slug = self._find_document_slug(document_text)
            if slug in self._document_id_by_slug:
                return slug
            return None
        if active_project_slug is not None:
            return active_project_slug
        selected = self.query_one(ProjectPane).selected_entry_info()
        if selected is not None and selected.kind == "entry" and selected.slug in self._document_id_by_slug:
            return selected.slug
        return None

    def _dispatch_add_document_to_basket_from_payload(self, payload: dict[str, object]) -> AppActionResult:
        if self._payload_requests_basket_excerpt(payload):
            return self._dispatch_add_excerpt_to_basket_from_payload(payload)
        slug = self._find_project_document_slug(
            payload.get("document")
            or payload.get("document_slug")
            or payload.get("document_title")
            or payload.get("source_document")
            or payload.get("source_document_slug")
            or payload.get("source_title")
            or payload.get("title")
            or payload.get("location")
        )
        if slug is None:
            return AppActionResult("failed", "Add document needs a project document.")
        fixture = DOCUMENT_FIXTURES.get(slug)
        if fixture is None:
            return AppActionResult("failed", "Add document source is no longer available.")
        if fixture.is_transcript and not self._current_project_is_confidential():
            return AppActionResult(
                "refused",
                "Full transcripts cannot be added to the basket in a non-confidential project. Add excerpts instead.",
            )
        if not self._add_document_slug_to_basket(slug):
            return AppActionResult("failed", f"Could not add {fixture.title} to the basket.")
        return AppActionResult(
            "completed",
            f"Added document {fixture.title} to the basket.",
            data={"document_slug": slug, "document_title": fixture.title},
        )

    def _dispatch_add_excerpt_to_basket_from_payload(self, payload: dict[str, object]) -> AppActionResult:
        document_ref = (
            payload.get("document")
            or payload.get("document_slug")
            or payload.get("document_title")
            or payload.get("source_document")
            or payload.get("source_document_slug")
            or payload.get("source_document_title")
            or payload.get("source_title")
            or payload.get("title")
            or payload.get("location")
        )
        slug = self._find_project_document_slug(document_ref)
        document_pane = self.query_one(DocumentPane)
        active_slug = document_pane.active_document.slug
        selection = document_pane.current_selection_snapshot() if slug is None or slug == active_slug else None
        if slug is None and selection is not None:
            slug = active_slug
        if slug is None:
            return AppActionResult("failed", "Add excerpt needs a source document for provenance.")
        fixture = DOCUMENT_FIXTURES.get(slug)
        if fixture is None:
            return AppActionResult("failed", "Add excerpt source is no longer available.")

        excerpt_text = str(
            payload.get("excerpt")
            or payload.get("selected_text")
            or payload.get("selection")
            or payload.get("text")
            or payload.get("snippet")
            or payload.get("quote")
            or payload.get("passage")
            or payload.get("source_excerpt")
            or ""
        ).strip()
        start = self._coerce_dispatch_int(payload.get("start"))
        end = self._coerce_dispatch_int(payload.get("end"))
        raw_range = payload.get("match_range") or payload.get("range")
        if (start is None or end is None) and isinstance(raw_range, (list, tuple)) and len(raw_range) >= 2:
            start = self._coerce_dispatch_int(raw_range[0])
            end = self._coerce_dispatch_int(raw_range[1])
        provenance_match = "provided"

        if not excerpt_text and selection is not None:
            excerpt_text = selection.selected_text.strip()
            start = selection.start
            end = selection.end
            provenance_match = "selection"
        elif start is not None and end is not None and end > start:
            excerpt_text = excerpt_text or fixture.content[start:end].strip()
            provenance_match = "range"
        elif excerpt_text:
            match_index = fixture.content.casefold().find(excerpt_text.casefold())
            if match_index >= 0:
                start = match_index
                end = match_index + len(excerpt_text)
                provenance_match = "matched_text"

        if not excerpt_text:
            return AppActionResult("failed", "Add excerpt needs excerpt text or an active text selection.")

        start = start if start is not None and start >= 0 else 0
        end = end if end is not None and end >= start else start
        document_id = self._document_id_by_slug.get(slug, fixture.location)
        if end > start:
            item_id = f"excerpt:{document_id}:{start}-{end}"
        else:
            digest = hashlib.sha256(f"{document_id}\0{excerpt_text}".encode("utf-8")).hexdigest()[:16]
            item_id = f"excerpt:{document_id}:provided-{digest}"
        items = self._engine_adapter.add_excerpt_to_basket(
            item_id=item_id,
            label=f"Excerpt from {fixture.title}",
            source_document_id=document_id,
            source_document_type=fixture.document_type,
            selected_text=excerpt_text,
            start=start,
            end=end,
            metadata={
                "source_document_slug": slug,
                "source_title": fixture.title,
                "source_match_status": provenance_match,
                **self._basket_source_metadata(),
            },
        )
        entry = self._sync_basket_from_engine_items(items, selected_item_id=item_id)
        self._set_status(f"Added excerpt from {fixture.title} to the basket.")
        self._show_basket_subject(entry)
        return AppActionResult(
            "completed",
            f"Added excerpt from {fixture.title} to the basket.",
            data={
                "document_slug": slug,
                "document_title": fixture.title,
                "start": start,
                "end": end,
                "source_match_status": provenance_match,
            },
        )

    def _find_trash_slug(self, item: object) -> str | None:
        needles = self._lookup_variants(item)
        needle_tokens = self._lookup_tokens(item)
        if needles:
            for slug, trash_id in self._trash_id_by_slug.items():
                fixture = DOCUMENT_FIXTURES.get(slug)
                metadata = self._trash_metadata_by_slug.get(slug, {})
                candidates = set()
                for value in self._trash_search_parts(slug, trash_id, fixture, metadata):
                    candidates.update(self._lookup_variants(value))
                if needles & candidates:
                    return slug
            for slug, trash_id in self._trash_id_by_slug.items():
                fixture = DOCUMENT_FIXTURES.get(slug)
                metadata = self._trash_metadata_by_slug.get(slug, {})
                relaxed_haystack = " ".join(self._trash_search_parts(slug, trash_id, fixture, metadata)).casefold()
                haystack = self._lookup_variants(relaxed_haystack)
                if needles & haystack:
                    return slug
                if any(needle in relaxed_haystack for needle in needles):
                    return slug
                haystack_tokens = self._lookup_tokens(relaxed_haystack)
                if needle_tokens and needle_tokens.issubset(haystack_tokens):
                    return slug
        selected = self.query_one(ProjectPane).selected_entry_info()
        return selected.slug if selected is not None and selected.slug in self._trash_id_by_slug else None

    @staticmethod
    def _trash_search_parts(slug: str, trash_id: str, fixture: object | None, metadata: dict[str, object]) -> tuple[str, ...]:
        original_id = str(metadata.get("original_id") or "")
        display_label = str(metadata.get("display_label") or "")
        original_path = Path(original_id) if original_id else Path()
        fixture_title = str(getattr(fixture, "title", "") or "")
        fixture_location = str(getattr(fixture, "location", "") or "")
        return tuple(
            part
            for part in (
                slug,
                trash_id,
                original_id,
                original_path.name if original_id else "",
                original_path.stem if original_id else "",
                " ".join(original_path.parts) if original_id else "",
                display_label,
                Path(display_label).stem if display_label else "",
                fixture_title,
                Path(fixture_title).stem if fixture_title else "",
                fixture_location,
            )
            if part
        )

    def _dispatch_rename_project_from_payload(self, payload: dict[str, object]) -> AppActionResult:
        duplicate_action = str(payload.get("duplicate_action") or "").strip().casefold()
        if duplicate_action == "rename" and not str(payload.get("duplicate_name") or "").strip():
            return AppActionResult("failed", "Rename needs an alternate project name.")
        requested_name = str(payload.get("duplicate_name") or payload.get("name") or "").strip()
        if not requested_name:
            return AppActionResult("failed", "Project rename needs a new project name.")
        if duplicate_action == "cancel":
            return AppActionResult("refused", "Project rename cancelled.")
        new_root = self._project_root_for_name(requested_name)
        try:
            same_root = self._project_root.resolve() == new_root.resolve()
        except OSError:
            same_root = self._project_root == new_root
        if new_root.exists() and not same_root and duplicate_action not in {"replace", "rename"}:
            return self._card_conflict_result(
                action_id="rename_project",
                label="Rename project",
                message=f"Project folder already exists for {requested_name}. Replace it or enter a different name.",
                payload={"name": requested_name},
                input_name="duplicate_name",
                input_placeholder="Alternate project name",
            )
        self._rename_active_project(requested_name, replace_existing=(duplicate_action == "replace"))
        return AppActionResult("completed", f"Renamed project to {requested_name}.", data={"project_name": requested_name})

    async def _dispatch_create_document_from_payload(self, category: str, payload: dict[str, object]) -> AppActionResult:
        duplicate_action = str(payload.get("duplicate_action") or "").strip().casefold()
        if duplicate_action == "rename" and not str(payload.get("duplicate_title") or "").strip():
            return AppActionResult("failed", "Rename needs an alternate file name.")
        title = str(payload.get("duplicate_title") or payload.get("title") or "").strip()
        if not title:
            await self._create_project_document(category)
            return AppActionResult("completed", f"Created a new {self._category_document_type(category)} document.")
        folder = self._resolve_model_document_folder_path(category, payload.get("folder"))
        if duplicate_action == "cancel":
            return AppActionResult("refused", "Document creation cancelled.")
        target_id = self._target_document_id(category, title, folder)
        existing_slug = next((slug for slug, document_id in self._document_id_by_slug.items() if document_id == target_id), None)
        if self._project_child_path(target_id).exists() and duplicate_action not in {"replace", "rename"}:
            return self._card_conflict_result(
                action_id=f"create_{self._category_document_type(category)}",
                label=f"New {self._category_document_type(category)}",
                message=f"{target_id} already exists. Replace it or enter a different name.",
                payload={"title": title, "folder": folder},
                input_name="duplicate_title",
                input_placeholder="Alternate file name",
            )
        if duplicate_action == "replace" and existing_slug is not None:
            existing_title = self._project_title_for_slug(existing_slug) or Path(target_id).name
            replaced = self._engine_adapter.delete_document(target_id, display_label=existing_title)
            self.query_one(ProjectPane).remove_entry(existing_slug)
            self._document_id_by_slug.pop(existing_slug, None)
            DOCUMENT_FIXTURES.pop(existing_slug, None)
            self._remove_document_tab(existing_slug)
            self._mark_basket_sources(source_document_id=target_id, source_document_slug=existing_slug, status="trashed")
            self._register_trash_entry(replaced.id, replaced.label, dict(replaced.metadata), old_source_slug=existing_slug)
        document_type = self._category_document_type(category)
        content_title = Path(title).stem or document_type.title()
        content = f"# {content_title}\n\n"
        item = self._engine_adapter.create_document(
            category=category,
            title=Path(target_id).name,
            content=content,
            document_type=document_type,
            relative_path=target_id,
        )
        slug = self._next_dynamic_slug(self._category_slug_prefix(category))
        self._document_id_by_slug[slug] = item.id
        register_document_fixture(
            slug=slug,
            title=item.label,
            location=item.id,
            summary=f"{item.label} in {category.lower()}.",
            content=content,
            document_type=document_type,
            is_transcript=(category == "Transcripts"),
        )
        self.query_one(ProjectPane).add_project_entry(
            category=category,
            slug=slug,
            title=item.label,
            location=item.id,
            summary=f"{item.label} in {category.lower()}.",
            bullets=(f"Category: {category}", f"Location: {item.id}", f"Document type: {document_type}"),
        )
        await self.query_one(DocumentPane).open_document(slug, focus=False)
        self._sync_save_controls()
        self._set_status(f"Created {item.label} in {category}.")
        return AppActionResult("completed", f"Created {item.label}.", data={"document_slug": slug, "location": item.id})

    def _dispatch_create_folder_from_payload(self, payload: dict[str, object]) -> AppActionResult:
        category = str(payload.get("category") or self._selected_project_category()).strip()
        if category not in IMPORTABLE_PROJECT_CATEGORIES:
            category = DEFAULT_IMPORT_CATEGORY
        name = str(payload.get("name") or "").strip()
        if not name:
            return AppActionResult("failed", "Folder creation needs a folder name.")
        folder_path = self._resolve_model_folder_creation_path(category, name, payload.get("parent_folder"))
        if not folder_path:
            return AppActionResult("failed", "Folder creation needs a valid folder name.")
        target = self._project_root / self._category_folder(category) / folder_path
        target.mkdir(parents=True, exist_ok=True)
        project_pane = self.query_one(ProjectPane)
        project_pane.add_folder(category=category, folder_path=folder_path.as_posix())
        project_pane.select_folder(category=category, folder_path=folder_path.as_posix())
        self._set_status(f"Created folder {folder_path.as_posix()} in {category}.")
        return AppActionResult("completed", f"Created folder {folder_path.as_posix()} in {category}.")

    def _dispatch_update_project_item_from_payload(self, payload: dict[str, object]) -> AppActionResult:
        slug = self._find_project_document_slug(payload.get("document"))
        if slug is None:
            return AppActionResult("failed", "Select or name a project document to update.")
        fixture = DOCUMENT_FIXTURES.get(slug)
        document_id = self._document_id_by_slug.get(slug, "")
        title = str(payload.get("duplicate_title") or payload.get("title") or (fixture.title if fixture else "")).strip()
        folder = str(payload.get("folder") if payload.get("folder") is not None else self._folder_path_for_document_id(document_id)).strip()
        duplicate_action = str(payload.get("duplicate_action") or "").strip().casefold()
        if duplicate_action == "rename" and not str(payload.get("duplicate_title") or "").strip():
            return AppActionResult("failed", "Rename needs an alternate file name.")
        if duplicate_action == "cancel":
            return AppActionResult("refused", "Update cancelled.")
        category = self._category_for_document_id(document_id)
        if category is None:
            return AppActionResult("failed", "Selected project item is outside a visible document category.")
        target_id = self._target_document_id(category, title, folder, allow_extensionless=True)
        if target_id != document_id and self._project_child_path(target_id).exists() and duplicate_action not in {"replace", "rename"}:
            return self._card_conflict_result(
                action_id="update_selected_project_item",
                label="Update item",
                message=f"{target_id} already exists. Replace it or enter a different name.",
                payload={"document": slug, "title": title, "folder": folder},
                input_name="duplicate_title",
                input_placeholder="Alternate file name",
            )
        updated = self._update_project_item(
            slug,
            title,
            folder,
            duplicate_action=duplicate_action or None,
            duplicate_title=str(payload.get("duplicate_title") or "") or None,
        )
        return AppActionResult("completed" if updated else "failed", f"Updated {title}." if updated else "Project item was not updated.")

    async def _dispatch_move_to_trash_from_payload(self, payload: dict[str, object]) -> AppActionResult:
        slug = self._find_project_document_slug(payload.get("document"))
        if slug is None:
            return AppActionResult("failed", "Select or name a project document to move to trash.")
        fixture = DOCUMENT_FIXTURES.get(slug)
        if slug == CURRENT_DRAFT_SLUG:
            return AppActionResult("refused", "The anchor draft cannot be moved to trash.")
        info = ProjectNodeInfo(
            kind="entry",
            title=fixture.title if fixture else slug,
            summary=fixture.summary if fixture else "",
            bullets=(),
            slug=slug,
            note=self._document_id_by_slug.get(slug, ""),
        )
        moved = await self._move_project_document_to_trash(info)
        return AppActionResult(
            "completed" if moved else "failed",
            f"Moved {info.title} to trash." if moved else f"Could not move {info.title} to trash.",
        )

    def _dispatch_restore_trash_from_payload(self, payload: dict[str, object]) -> AppActionResult:
        slug = self._find_trash_slug(
            payload.get("trash_item")
            or payload.get("document")
            or payload.get("document_title")
            or payload.get("title")
            or payload.get("filename")
            or payload.get("file")
            or payload.get("path")
            or payload.get("original_id")
        )
        if slug is None:
            return AppActionResult("failed", "Select or name a trash item to restore.")
        duplicate_action = str(payload.get("duplicate_action") or "").strip().casefold()
        if duplicate_action == "rename" and not str(payload.get("duplicate_title") or "").strip():
            return AppActionResult("failed", "Rename needs an alternate restored file name.")
        if duplicate_action == "cancel":
            return AppActionResult("refused", "Restore cancelled.")
        metadata = self._trash_metadata_by_slug.get(slug, {})
        original_id = str(metadata.get("original_id") or "")
        if original_id and (self._project_root / original_id).exists() and duplicate_action not in {"replace", "rename"}:
            return self._card_conflict_result(
                action_id="restore_trash_item",
                label="Restore trash item",
                message=f"{original_id} already exists. Replace it or enter a different restored name.",
                payload={"trash_item": slug},
                input_name="duplicate_title",
                input_placeholder="Alternate restored file name",
            )
        if duplicate_action in {"replace", "rename"}:
            self._handle_duplicate_restore_result(
                slug,
                (
                    duplicate_action,
                    str(payload.get("duplicate_title") or "").strip() or None,
                ),
            )
        else:
            self._handle_trash_document_result(slug, "restore")
        return AppActionResult("completed", "Restore requested.", data={"trash_slug": slug})

    def _dispatch_permanent_delete_from_payload(self, payload: dict[str, object]) -> AppActionResult:
        slug = self._find_trash_slug(
            payload.get("trash_item")
            or payload.get("document")
            or payload.get("document_title")
            or payload.get("title")
            or payload.get("filename")
            or payload.get("file")
            or payload.get("path")
            or payload.get("original_id")
        )
        if slug is None:
            return AppActionResult("failed", "Select or name a trash item to permanently delete.")
        deleted = self._permanently_delete_trash_item(slug)
        return AppActionResult(
            "completed" if deleted else "failed",
            "Permanently deleted trash item. Audit trail retained." if deleted else "Trash item was not permanently deleted.",
        )

    def _set_notebook_instruction(self, instruction: object) -> None:
        text = str(instruction or "").strip()
        if not text:
            return
        self.query_one("#workflow-composer-input", Input).value = text

    async def action_close_document_tab(self) -> None:
        if self._focus_is_inside(self.query_one(WorkflowPane)):
            await self.action_close_notebook_chat()
            return
        self._save_dirty_documents()
        document_pane = self.query_one(DocumentPane)
        closed = await document_pane.close_active_document()
        if closed:
            active = document_pane.active_document
            self._set_status(f"Closed tab. Active document: {active.title}")
            self._show_document_subject(active)
        else:
            self._set_status("The main draft stays open as the anchor document.")

    async def action_close_notebook_chat(self) -> None:
        workflow_pane = self.query_one(WorkflowPane)
        was_generating = workflow_pane.active_chat.generating
        closed = await workflow_pane.close_active_chat()
        if closed:
            active = workflow_pane.active_chat
            self._set_status(f"Closed chat. Active notebook chat: {active.title}")
            self._show_chat_subject(active)
        elif was_generating:
            self._set_status("Stopped notebook response.")
        else:
            self._set_status("The main chat stays open as the anchor notebook chat.")

    def _focus_is_inside(self, container: Widget) -> bool:
        focused = self.focused
        while focused is not None:
            if focused is container:
                return True
            focused = focused.parent
        return False

    def action_save_current_document(self) -> None:
        document = self.query_one(DocumentPane).active_document
        if self._save_dirty_documents({document.slug}):
            self._set_status(f"Saved {document.title}.")
        else:
            self._set_status(f"No unsaved changes in {document.title}.")
        self._sync_save_controls()

    def action_show_palette(self) -> None:
        self.action_command_palette()

    async def action_model_settings(self) -> None:
        await self._open_model_settings(first_launch=False)

    async def action_rename_project(self) -> None:
        await self.dispatch_app_action("rename_project", source="shortcut")

    async def action_close_chat(self) -> None:
        await self.dispatch_app_action("close_chat", source="shortcut")

    def shell_request_model_settings(self) -> None:
        self.call_after_refresh(lambda: self.run_worker(self._open_model_settings(first_launch=False), thread=False))

    def _model_backend(self) -> MistralChatBackend | None:
        return self._workflow_backend if isinstance(self._workflow_backend, MistralChatBackend) else None

    async def _open_model_settings(self, *, first_launch: bool) -> None:
        backend = self._model_backend()
        if backend is None:
            self._set_status("Model Settings are available for the Mistral backend.")
            return
        settings = backend.model_settings()
        status = backend.credential_status()
        result = await self.push_screen_wait(
            ModelSettingsModal(
                settings=settings,
                has_api_key=backend.has_api_key(),
                has_api_keys={provider: backend.has_api_key(provider) for provider in PROVIDER_OPTIONS},
                secure_storage_available=status.available,
                secure_storage_message=status.error_message,
                first_launch=first_launch,
                lock_to_local_openai=self._current_project_is_confidential(),
            )
        )
        self._handle_model_settings_result(result)

    async def _run_startup_prompts(self) -> None:
        if self._should_prompt_for_model_settings():
            await self._open_model_settings(first_launch=True)
        if self._prompt_for_initial_project:
            result = await self.push_screen_wait(NewProjectModal(local_endpoint_configured=self._local_endpoint_configured()))
            self._prompt_for_initial_project = False
            self._handle_new_project_result(result)
        self.action_focus_document()

    def _should_prompt_for_model_settings(self) -> bool:
        backend = self._model_backend()
        if backend is None or backend.has_api_key():
            return False
        settings = backend.model_settings()
        return not settings.settings_prompt_dismissed

    def _maybe_prompt_for_model_settings(self) -> None:
        if self._should_prompt_for_model_settings():
            self.run_worker(self._open_model_settings(first_launch=True), thread=False)

    def _handle_model_settings_result(self, result: ModelSettingsAction | None) -> None:
        if result is None:
            return
        backend = self._model_backend()
        if backend is None:
            return
        action, settings, api_key = result
        try:
            if action in {"save", "skip"}:
                backend.save_model_settings(settings)
                if action == "save" and api_key:
                    backend.set_api_key(api_key, settings.provider)
                self._set_status("Model settings saved." if action == "save" else "Model setup skipped for now.")
            elif action == "clear":
                backend.clear_api_key(settings.provider)
                backend.save_model_settings(settings)
                self._set_status(f"{settings.provider_label()} API key cleared from secure storage.")
        except CredentialStoreError as exc:
            self._set_status(str(exc))
        except OSError as exc:
            self._set_status(f"Could not save model settings: {exc}")
        finally:
            self.query_one(WorkflowPane)._sync_status()

    def on_model_settings_modal_test_connection_requested(
        self, message: ModelSettingsModal.TestConnectionRequested
    ) -> None:
        message.stop()

        async def run_test() -> None:
            backend = self._model_backend()
            if backend is None:
                message.modal.complete_connection_test("Model Settings are available for the Mistral backend.")
                return
            result = await backend.test_connection(message.settings, message.api_key)
            message.modal.complete_connection_test(result.message)
            self._set_status(result.message)

        self.run_worker(run_test(), name="model-settings-live-test", group="model-settings", exclusive=True, thread=False)

    def action_restart_exegesis(self) -> None:
        if not is_local_developer_mode():
            self._set_status("Restart is only available in local developer mode.")
            return
        self._save_dirty_documents()
        self.exit(result="restart")

    def action_quit(self) -> None:
        self._save_dirty_documents()
        self.exit()

    def action_add_excerpt_to_basket(self) -> None:
        self._save_dirty_documents()
        self.query_one(DocumentPane).request_excerpt()

    def action_add_file_to_basket(self) -> None:
        self._save_dirty_documents()
        if self._add_marked_project_documents_to_basket():
            return
        self.query_one(DocumentPane).request_document()

    async def action_create_draft(self) -> None:
        await self._create_project_document("Drafts")

    async def action_create_memo(self) -> None:
        await self._create_project_document("Memos")

    async def action_create_summary(self) -> None:
        await self._create_project_document("Summaries")

    async def action_create_transcript(self) -> None:
        await self._create_project_document("Transcripts")

    async def action_create_literature(self) -> None:
        await self._create_project_document("Literature")

    async def action_create_folder(self) -> None:
        project_pane = self.query_one(ProjectPane)
        category = project_pane.selected_category()
        if category not in IMPORTABLE_PROJECT_CATEGORIES:
            category = DEFAULT_IMPORT_CATEGORY
        await self.push_screen(
            NewProjectFolderModal(category, project_pane.selected_folder_path()),
            callback=lambda result, category=category: self._handle_new_folder_result(category, result),
        )

    async def action_update_selected_project_item(self) -> None:
        selected = self.query_one(ProjectPane).selected_entry_info()
        if selected is None or selected.kind != "entry" or selected.slug is None:
            self._set_status("Select a project document to update first.")
            return
        current_folder = ""
        document_id = self._document_id_by_slug.get(selected.slug) or selected.note or ""
        if document_id:
            current_folder = self._folder_path_for_document_id(document_id)
        category = self._category_for_document_id(document_id) or "Project"
        await self.push_screen(
            UpdateProjectItemModal(
                selected.title,
                category,
                current_folder,
                self._folder_choices_for_document_id(document_id),
            ),
            callback=lambda result, slug=selected.slug: self._handle_project_update_result(slug, result),
        )

    async def action_import_document(self) -> None:
        self._save_dirty_documents()
        await self.push_screen(ImportMarkdownModal(), callback=self._handle_import_result)

    def on_key(self, event: events.Key) -> None:
        """Make notebook proposal decisions work even when the card is not focused."""
        if isinstance(self.screen, ModalScreen):
            return
        decision = self._proposal_decision_from_key_event(event)
        if decision is None:
            return
        workflow_pane = self.query_one(WorkflowPane)
        result = self._decide_active_notebook_proposal_or_card(decision)
        if result.status == "refused":
            return
        workflow_pane.set_status(result.message)
        event.stop()
        event.prevent_default()

    @staticmethod
    def _proposal_decision_from_key_event(event: events.Key) -> str | None:
        key_aliases = {event.key, *(getattr(event, "aliases", ()) or ())}
        modifiers = {str(modifier).casefold() for modifier in (getattr(event, "modifiers", ()) or ())}
        if "shift+enter" in key_aliases or (event.key == "enter" and "shift" in modifiers):
            return "apply"
        if "escape" in key_aliases:
            return "reject"
        return None

    async def action_new_project(self) -> None:
        self._save_dirty_documents()
        await self.push_screen(NewProjectModal(local_endpoint_configured=self._local_endpoint_configured()), callback=self._handle_new_project_result)

    async def action_open_project_browser(self) -> None:
        self._save_dirty_documents()
        if is_local_developer_mode():
            self._ensure_demo_project_available()
        elif not self._has_project_directories():
            await self.push_screen(NewProjectModal(local_endpoint_configured=self._local_endpoint_configured()), callback=self._handle_new_project_result)
            return
        self._refresh_project_names(include_fallback=False)
        if not self._project_names:
            await self.push_screen(NewProjectModal(local_endpoint_configured=self._local_endpoint_configured()), callback=self._handle_new_project_result)
            return
        await self.push_screen(OpenProjectModal(self._project_records, local_endpoint_configured=self._local_endpoint_configured()), callback=self._handle_open_project_result)

    async def action_change_projects_directory(self) -> None:
        self._save_dirty_documents()
        await self.push_screen(
            SelectProjectsDirectoryModal(self._projects_base_dir),
            callback=self._handle_projects_directory_result,
        )

    async def action_move_selected_project_document_to_trash(self) -> None:
        await self._delete_selected_project_document()

    def action_restore_selected_trash_item(self) -> None:
        if self._restore_selected_compacted_conversation():
            return
        slugs = self._selected_trash_slugs()
        if not slugs:
            self._set_status("Select a trash item first.")
            return
        for slug in slugs:
            self._handle_trash_document_result(slug, "restore")
        if len(slugs) > 1:
            self._set_status(f"Restored {len(slugs)} trash items.")

    def action_permanently_delete_selected_trash_item(self) -> None:
        slugs = self._selected_trash_slugs()
        if not slugs:
            self._set_status("Select a trash item first.")
            return
        self._confirm_permanent_delete_trash_items(slugs)

    async def action_delete_selected_item(self) -> None:
        if self.query_one(BasketPane).has_list_focus():
            self._delete_selected_basket_item()
            return
        await self._delete_selected_project_document()

    def action_delete_selected_basket_item(self) -> None:
        self._delete_selected_basket_item()

    def action_save_short_summary(self) -> None:
        self._request_summary("short", 100)

    def action_save_medium_summary(self) -> None:
        self._request_summary("medium", 500)

    def action_save_long_summary(self) -> None:
        self._request_summary("long", 1000)

    def action_terminal_draft(self) -> None:
        self._save_dirty_documents()
        workflow_pane = self.query_one(WorkflowPane)
        workflow_pane.draft_into_document()

    def action_terminal_search(self) -> None:
        self._save_dirty_documents()
        workflow_pane = self.query_one(WorkflowPane)
        workflow_pane.search_documents()

    def action_terminal_rewrite(self) -> None:
        self._save_dirty_documents()
        workflow_pane = self.query_one(WorkflowPane)
        workflow_pane.rewrite_selection()

    def action_terminal_accept_proposal(self) -> None:
        result = self._decide_active_notebook_proposal_or_card("apply")
        self.query_one(WorkflowPane).set_status(result.message)

    def action_terminal_reject_proposal(self) -> None:
        result = self._decide_active_notebook_proposal_or_card("reject")
        self.query_one(WorkflowPane).set_status(result.message)

    def _decide_active_notebook_proposal_or_card(self, decision: str) -> AppActionResult:
        workflow_pane = self.query_one(WorkflowPane)
        return workflow_pane.decide_active_notebook_card(decision)

    def _decide_active_notebook_proposal(self, decision: str) -> AppActionResult:
        workflow_pane = self.query_one(WorkflowPane)
        patch_id = workflow_pane.active_chat.pending_patch_id
        if patch_id is None:
            verb = "accept" if decision == "apply" else "reject"
            return AppActionResult("refused", f"No active notebook proposal to {verb}.")
        self.on_workflow_pane_patch_decision_requested(
            WorkflowPane.PatchDecisionRequested(workflow_pane, patch_id, decision)
        )
        verb = "Accepted" if decision == "apply" else "Rejected"
        return AppActionResult("completed", f"{verb} notebook proposal.")

    async def action_terminal_new_chat(self) -> None:
        workflow_pane = self.query_one(WorkflowPane)
        await workflow_pane.new_chat()

    def action_terminal_save(self) -> None:
        self._save_dirty_documents()
        workflow_pane = self.query_one(WorkflowPane)
        workflow_pane.save_active_transcript()

    def action_terminal_compact(self) -> None:
        self._save_dirty_documents()
        workflow_pane = self.query_one(WorkflowPane)
        workflow_pane.compact_active_chat()

    def action_focus_project(self) -> None:
        self._save_dirty_documents()
        self.query_one("#project-pane").focus()
        self._set_status("Focus moved to Project. Use this rail for workspace and document selection.")
        self._show_subject("Current Draft", CURRENT_DRAFT_SUMMARY, CURRENT_DRAFT_BULLETS, None)

    def action_focus_document(self) -> None:
        document_pane = self.query_one(DocumentPane)
        document_pane.focus_editor()
        self._set_status("Focus moved to Document. This is the main writing surface scaffold.")
        active = document_pane.active_document
        self._show_document_subject(active)

    def action_focus_basket(self) -> None:
        self._save_dirty_documents()
        basket_pane = self.query_one(BasketPane)
        basket_pane.focus_primary()
        self._set_status("Focus moved to Basket. Promoted excerpts and files live here.")
        selected = basket_pane.selected_entry()
        if selected is not None:
            self._show_basket_subject(selected)

    def action_focus_workflow(self) -> None:
        self._save_dirty_documents()
        workflow_pane = self.query_one(WorkflowPane)
        workflow_pane.focus_editor()
        self._set_status("Focus moved to Notebook. This pane is for prompts, context status, and future cards.")
        self._show_chat_subject(workflow_pane.active_chat)

    def action_focus_inspector(self) -> None:
        self._save_dirty_documents()
        self.query_one("#inspector-pane").focus()
        self._set_status("Focus moved to Inspector. Protocol and workflow diagnostics live here for now.")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        action_id = FOOTER_BUTTON_ACTIONS.get(button_id or "") or TOP_BUTTON_ACTIONS.get(button_id or "")
        if action_id is not None:
            await self.dispatch_app_action(action_id, source="button")
        elif button_id == TOP_DELETE_ID:
            self.action_delete_selected_basket_item()

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        option_id = event.option_id
        basket_entry = self.query_one(BasketPane).get_entry(option_id)
        if basket_entry is not None:
            self._show_basket_subject(basket_entry)
            return
        if option_id in WORKFLOW_CARD_MAP:
            card = WORKFLOW_CARD_MAP[option_id]
            self._show_subject(card.title, card.summary, card.bullets, f"Notebook status: {card.status}")

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted[ProjectNodeInfo]) -> None:
        data = event.node.data
        if data is None or not isinstance(data, ProjectNodeInfo):
            return
        self._sync_project_context_actions(data)
        if data.kind == "entry" and data.slug is not None and data.slug in DOCUMENT_FIXTURES:
            self._show_document_subject(DOCUMENT_FIXTURES[data.slug])
            return
        if data.kind == "trash_entry":
            self._show_trash_subject(data)
            return
        self._show_subject(data.title, data.summary, data.bullets, None)

    async def on_tree_node_selected(self, event: Tree.NodeSelected[ProjectNodeInfo]) -> None:
        data = event.node.data
        if data is None or not isinstance(data, ProjectNodeInfo):
            return
        self._sync_project_context_actions(data)
        if data.kind == "entry" and data.slug is not None:
            self._save_dirty_documents()
            document_pane = self.query_one(DocumentPane)
            await document_pane.open_document(data.slug, focus=False)
            self._sync_save_controls()
            self._sync_terminal_patch_card()
        elif data.kind == "trash_entry" and data.slug is not None:
            self._save_dirty_documents()
            document_pane = self.query_one(DocumentPane)
            await document_pane.open_document(data.slug, focus=False)
            self._sync_save_controls()
            self._set_status("Double-select a trash item to restore or permanently delete it.")
        self._set_status(f"Selected project browser item: {data.title}")
        if data.kind == "entry" and data.slug is not None and data.slug in DOCUMENT_FIXTURES:
            self._show_document_subject(DOCUMENT_FIXTURES[data.slug])
        elif data.kind == "trash_entry":
            self._show_trash_subject(data)
        else:
            self._show_subject(data.title, data.summary, data.bullets, None)

    def _sync_project_context_actions(self, data: ProjectNodeInfo | None = None) -> None:
        selected = data or self.query_one(ProjectPane).selected_entry_info()
        is_trash = selected is not None and selected.kind in {"trash_entry", "trash_category", "trash_folder"}
        self.query_one(ProjectPane).set_trash_action_mode(is_trash)

    def on_project_browser_tree_double_selected(self, message: ProjectBrowserTree.DoubleSelected) -> None:
        data = message.info
        if data.slug is None:
            return
        if data.kind == "trash_entry":
            self.push_screen(
                TrashDocumentModal(data.title, data.note or ""),
                callback=lambda result, slug=data.slug: self._handle_trash_document_result(slug, result),
            )
        elif data.kind == "entry" and self._is_compacted_conversation_slug(data.slug):
            self._restore_compacted_conversation_chat(data.slug)
        elif data.kind == "entry":
            document_id = self._document_id_by_slug.get(data.slug) or data.note or ""
            category = self._category_for_document_id(document_id) or "Project"
            self.push_screen(
                UpdateProjectItemModal(
                    data.title,
                    category,
                    self._folder_path_for_document_id(document_id),
                    self._folder_choices_for_document_id(document_id),
                ),
                callback=lambda result, slug=data.slug: self._handle_project_update_result(slug, result),
            )

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        if event.tabbed_content.id == DOCUMENT_TABBED_CONTENT_ID:
            document_pane = self.query_one(DocumentPane)
            active = document_pane.active_document
            self._set_status(f"Active document tab: {active.title}")
            if active.slug in self._trash_id_by_slug:
                selected = self.query_one(ProjectPane).selected_entry_info()
                if selected is not None and selected.slug == active.slug:
                    self._show_trash_subject(selected)
                else:
                    self._show_document_subject(active, refresh_notebook_context=not self._navigating_search_result)
            else:
                self._show_document_subject(active, refresh_notebook_context=not self._navigating_search_result)
            self._sync_terminal_patch_card()
        elif event.tabbed_content.id == WORKFLOW_TABBED_CONTENT_ID:
            workflow_pane = self.query_one(WorkflowPane)
            active = workflow_pane.active_chat
            self._set_status(f"Active notebook chat: {active.title}")
            self._show_chat_subject(active)

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        widget_id = event.widget.id or ""
        if not widget_id.startswith("document-editor-"):
            return
        active = self.query_one(DocumentPane).active_document
        self._show_document_subject(active)

    async def on_document_pane_close_requested(self, message: DocumentPane.CloseRequested) -> None:
        await self.action_close_document_tab()

    def on_document_pane_save_requested(self, message: DocumentPane.SaveRequested) -> None:
        self.action_save_current_document()

    def on_document_pane_content_changed(self, message: DocumentPane.ContentChanged) -> None:
        self._dirty_document_slugs.add(message.slug)
        self._mark_basket_sources(
            source_document_id=self._document_id_by_slug.get(message.slug),
            source_document_slug=message.slug,
            status="changed",
        )
        self._sync_save_controls()
        self._refresh_notebook_context_meter()

    def on_project_pane_new_project_requested(self, message: ProjectPane.NewProjectRequested) -> None:
        self.push_screen(NewProjectModal(local_endpoint_configured=self._local_endpoint_configured()), callback=self._handle_new_project_result)

    def on_project_pane_open_project_requested(self, message: ProjectPane.OpenProjectRequested) -> None:
        if is_local_developer_mode():
            self._ensure_demo_project_available()
        elif not self._has_project_directories():
            self.push_screen(NewProjectModal(local_endpoint_configured=self._local_endpoint_configured()), callback=self._handle_new_project_result)
            return
        self._refresh_project_names(include_fallback=False)
        if not self._project_names:
            self.push_screen(NewProjectModal(local_endpoint_configured=self._local_endpoint_configured()), callback=self._handle_new_project_result)
            return
        self.push_screen(OpenProjectModal(self._project_records, local_endpoint_configured=self._local_endpoint_configured()), callback=self._handle_open_project_result)

    def on_project_pane_rename_project_requested(self, message: ProjectPane.RenameProjectRequested) -> None:
        self.push_screen(RenameActiveProjectModal(self._current_project_name), callback=self._handle_active_project_rename_result)

    async def on_project_pane_update_item_requested(self, message: ProjectPane.UpdateItemRequested) -> None:
        await self.action_update_selected_project_item()

    async def on_project_pane_create_requested(self, message: ProjectPane.CreateRequested) -> None:
        if message.category == "Folder":
            await self.action_create_folder()
            return
        await self._create_project_document(message.category)

    async def on_project_pane_import_requested(self, message: ProjectPane.ImportRequested) -> None:
        self.push_screen(ImportMarkdownModal(), callback=self._handle_import_result)

    async def on_project_pane_delete_requested(self, message: ProjectPane.DeleteRequested) -> None:
        selected = self.query_one(ProjectPane).selected_entry_info()
        if selected is not None and selected.kind in {"trash_entry", "trash_category", "trash_folder"}:
            self.action_permanently_delete_selected_trash_item()
            return
        await self._delete_selected_project_document()

    def on_project_pane_restore_requested(self, message: ProjectPane.RestoreRequested) -> None:
        self.action_restore_selected_trash_item()

    def on_basket_pane_delete_requested(self, message: BasketPane.DeleteRequested) -> None:
        self._delete_selected_basket_item()

    def _sync_footer_bar(self) -> None:
        badge = self.query_one(f"#{FOOTER_CONFIDENTIALITY_ID}", Static)
        if self._current_project_is_confidential():
            badge.update(CONFIDENTIAL_MODE_LABEL)
            badge.add_class("confidential")
            badge.remove_class("non-confidential")
        else:
            badge.update(NON_CONFIDENTIAL_MODE_LABEL)
            badge.add_class("non-confidential")
            badge.remove_class("confidential")

    def _sync_save_controls(self) -> None:
        document_pane = self.query_one(DocumentPane)
        active_slug = document_pane.active_document.slug
        is_dirty = active_slug in self._dirty_document_slugs and document_pane.document_view_status(active_slug) is None
        document_pane.set_save_enabled(is_dirty)

    def _sync_terminal_patch_card(self) -> None:
        document_pane = self.query_one(DocumentPane)
        workflow_pane = self.query_one(WorkflowPane)
        preview = document_pane.pending_preview_for()
        if preview is None:
            workflow_pane.clear_patch_review()
            return
        workflow_pane.show_patch_review(
            PatchReviewCardData(
                patch_id=preview.patch_id,
                document_title=document_pane.active_document.title,
                instruction_text=preview.instruction_text,
                source_chat_slug=preview.source_chat_slug,
                original_text=preview.original_text,
                proposed_text=preview.proposed_text,
                document_slug=preview.document_slug,
                target_range=preview.target_range,
                block_insert=preview.block_insert,
            )
        )

    def _set_status(self, message: str) -> None:
        return

    def _save_dirty_documents(self, slugs: set[str] | None = None) -> bool:
        target_slugs = set(self._dirty_document_slugs if slugs is None else slugs & self._dirty_document_slugs)
        saved_any = False
        for slug in sorted(target_slugs):
            document_id = self._document_id_by_slug.get(slug)
            fixture = DOCUMENT_FIXTURES.get(slug)
            if document_id is None or fixture is None:
                self._dirty_document_slugs.discard(slug)
                continue
            try:
                self._engine_adapter.open_document(document_id)
                self._engine_adapter.save_document(fixture.content)
            except (OSError, RuntimeError, ValueError) as exc:
                self._set_status(f"Save failed for {document_id}: {exc}")
                continue
            self._mark_basket_sources(
                source_document_id=document_id,
                source_document_slug=slug,
                status="changed",
            )
            self._dirty_document_slugs.discard(slug)
            saved_any = True
        self._sync_save_controls()
        return saved_any



__all__ = ["PaneBlueprint", "QualShellApp", "SHELL_BLUEPRINT", "ShellBlueprint"]
