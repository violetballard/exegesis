from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
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
from exegesis_textual.services.model_settings import MistralModelSettings
from exegesis_textual.workflow.mistral_chat import ChatMessage, MistralChatBackend, ShellChatContext, TerminalChatBackend
from exegesis_textual.workflow.rewrite_adapter import MockRewriteSessionAdapter
from exegesis_textual.workflow.workflow_pane import (
    TERMINAL_CONTEXT_WINDOW_TOKENS,
    WORKFLOW_CARD_MAP,
    WORKFLOW_PANE_COPY,
    WORKFLOW_TABBED_CONTENT_ID,
    WorkflowPane,
)

FOOTER_CONFIDENTIALITY_ID = "shell-footer-confidentiality"
NON_CONFIDENTIAL_MODE_LABEL = "Non-confidential"
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
TOP_TERMINAL_NEW_CHAT_ID = "top-terminal-new-chat"
TOP_TERMINAL_SAVE_ID = "top-terminal-save"
TOP_TERMINAL_COMPACT_ID = "top-terminal-compact"





class QualShellApp(ProjectControllerMixin, BasketControllerMixin, NotebookControllerMixin, InspectorControllerMixin, App[None]):
    """Basic shell scaffold for the future Qual Textual client."""

    TITLE = "Exegesis"
    SUB_TITLE = ""
    COMMANDS = App.COMMANDS | {ExegesisCommandProvider}
    CSS = SHELL_CSS
    BINDINGS = [
        Binding("ctrl+p", "show_palette", "Palette", priority=True),
        Binding("ctrl+w", "close_document_tab", "Close Tab", priority=True),
        Binding("ctrl+shift+e", "add_excerpt_to_basket", "Excerpt to Basket", priority=True),
        Binding("ctrl+shift+b", "add_file_to_basket", "File to Basket", priority=True),
        Binding("ctrl+shift+d", "create_draft", "New Draft", priority=True),
        Binding("ctrl+shift+m", "create_memo", "New Memo", priority=True),
        Binding("ctrl+shift+s", "create_summary", "New Summary", priority=True),
        Binding("ctrl+shift+t", "create_transcript", "New Transcript", priority=True),
        Binding("ctrl+shift+l", "create_literature", "New Literature", priority=True),
        Binding("ctrl+shift+f", "create_folder", "New Folder", priority=True),
        Binding("ctrl+shift+u", "update_selected_project_item", "Update Item", priority=True),
        Binding("ctrl+shift+i", "import_document", "Import", priority=True),
        Binding("ctrl+shift+r", "restore_selected_trash_item", "Restore Trash", priority=True),
        Binding("ctrl+shift+delete", "permanently_delete_selected_trash_item", "Delete Forever", priority=True),
        Binding("ctrl+shift+backspace", "permanently_delete_selected_trash_item", "Delete Forever", priority=True),
        Binding("ctrl+shift+1", "save_short_summary", "Save Short Summary", priority=True),
        Binding("ctrl+shift+2", "save_medium_summary", "Save Medium Summary", priority=True),
        Binding("ctrl+shift+3", "save_long_summary", "Save Long Summary", priority=True),
        Binding("ctrl+enter", "terminal_search", "Search", priority=True),
        Binding("ctrl+shift+g", "terminal_draft", "Draft", priority=True),
        Binding("ctrl+shift+w", "terminal_rewrite", "Rewrite", priority=True),
        Binding("ctrl+shift+n", "terminal_new_chat", "New Chat", priority=True),
        Binding("ctrl+shift+x", "terminal_save", "Save transcript", priority=True),
        Binding("ctrl+shift+v", "terminal_compact", "Compact chat", priority=True),
        Binding("ctrl+s", "save_current_document", "Save Document", priority=True),
        Binding("ctrl+r", "restart_exegesis", "Restart Exegesis", priority=True),
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("f1", "focus_project", "Project"),
        Binding("f2", "focus_document", "Document"),
        Binding("f3", "focus_basket", "Basket"),
        Binding("f4", "focus_workflow", "Notebook"),
        Binding("f5", "focus_inspector", "Inspector"),
    ]

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
                secure_storage_available=status.available,
                secure_storage_message=status.error_message,
                first_launch=first_launch,
            )
        )
        self._handle_model_settings_result(result)

    async def _run_startup_prompts(self) -> None:
        if self._should_prompt_for_model_settings():
            await self._open_model_settings(first_launch=True)
        if self._prompt_for_initial_project:
            result = await self.push_screen_wait(NewProjectModal())
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
                    backend.set_api_key(api_key)
                self._set_status("Model settings saved." if action == "save" else "Model setup skipped for now.")
            elif action == "clear":
                backend.clear_api_key()
                backend.save_model_settings(settings)
                self._set_status("Mistral API key cleared from secure storage.")
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

    async def action_new_project(self) -> None:
        self._save_dirty_documents()
        await self.push_screen(NewProjectModal(), callback=self._handle_new_project_result)

    async def action_open_project_browser(self) -> None:
        self._save_dirty_documents()
        if is_local_developer_mode():
            self._ensure_demo_project_available()
        elif not self._has_project_directories():
            await self.push_screen(NewProjectModal(), callback=self._handle_new_project_result)
            return
        self._refresh_project_names(include_fallback=False)
        if not self._project_names:
            await self.push_screen(NewProjectModal(), callback=self._handle_new_project_result)
            return
        await self.push_screen(OpenProjectModal(self._project_records), callback=self._handle_open_project_result)

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
        if button_id == FOOTER_PALETTE_ID:
            self._save_dirty_documents()
            self.action_show_palette()
        elif button_id == FOOTER_RESTART_ID:
            self.action_restart_exegesis()
        elif button_id == FOOTER_QUIT_ID:
            self.action_quit()
        elif button_id == FOOTER_CLOSE_ID:
            await self.action_close_document_tab()
        elif button_id == FOOTER_PROJECT_ID:
            self.action_focus_project()
        elif button_id == FOOTER_DOCUMENT_ID:
            self.action_focus_document()
        elif button_id == FOOTER_BASKET_ID:
            self.action_focus_basket()
        elif button_id == FOOTER_TERMINAL_ID:
            self.action_focus_workflow()
        elif button_id == FOOTER_INSPECTOR_ID:
            self.action_focus_inspector()
        elif button_id == TOP_EXCERPT_ID:
            self.action_add_excerpt_to_basket()
        elif button_id == TOP_FILE_ID:
            self.action_add_file_to_basket()
        elif button_id == TOP_NEW_DRAFT_ID:
            await self.action_create_draft()
        elif button_id == TOP_NEW_MEMO_ID:
            await self.action_create_memo()
        elif button_id == TOP_NEW_SUMMARY_ID:
            await self.action_create_summary()
        elif button_id == TOP_NEW_TRANSCRIPT_ID:
            await self.action_create_transcript()
        elif button_id == TOP_NEW_LITERATURE_ID:
            await self.action_create_literature()
        elif button_id == TOP_NEW_FOLDER_ID:
            await self.action_create_folder()
        elif button_id == TOP_UPDATE_ITEM_ID:
            await self.action_update_selected_project_item()
        elif button_id == TOP_IMPORT_ID:
            await self.action_import_document()
        elif button_id == TOP_SAVE_DOCUMENT_ID:
            self.action_save_current_document()
        elif button_id == TOP_MOVE_TO_TRASH_ID:
            await self.action_move_selected_project_document_to_trash()
        elif button_id == TOP_RESTORE_TRASH_ID:
            self.action_restore_selected_trash_item()
        elif button_id == TOP_PERMANENT_DELETE_TRASH_ID:
            self.action_permanently_delete_selected_trash_item()
        elif button_id == TOP_DELETE_ID:
            self.action_delete_selected_basket_item()
        elif button_id == TOP_SAVE_SHORT_SUMMARY_ID:
            self.action_save_short_summary()
        elif button_id == TOP_SAVE_MEDIUM_SUMMARY_ID:
            self.action_save_medium_summary()
        elif button_id == TOP_SAVE_LONG_SUMMARY_ID:
            self.action_save_long_summary()
        elif button_id == TOP_TERMINAL_SEARCH_ID:
            self.action_terminal_search()
        elif button_id == TOP_TERMINAL_DRAFT_ID:
            self.action_terminal_draft()
        elif button_id == TOP_TERMINAL_REWRITE_ID:
            self.action_terminal_rewrite()
        elif button_id == TOP_TERMINAL_NEW_CHAT_ID:
            await self.action_terminal_new_chat()
        elif button_id == TOP_TERMINAL_SAVE_ID:
            self.action_terminal_save()
        elif button_id == TOP_TERMINAL_COMPACT_ID:
            self.action_terminal_compact()

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
        self.push_screen(NewProjectModal(), callback=self._handle_new_project_result)

    def on_project_pane_open_project_requested(self, message: ProjectPane.OpenProjectRequested) -> None:
        if is_local_developer_mode():
            self._ensure_demo_project_available()
        elif not self._has_project_directories():
            self.push_screen(NewProjectModal(), callback=self._handle_new_project_result)
            return
        self._refresh_project_names(include_fallback=False)
        if not self._project_names:
            self.push_screen(NewProjectModal(), callback=self._handle_new_project_result)
            return
        self.push_screen(OpenProjectModal(self._project_records), callback=self._handle_open_project_result)

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
        badge.update(NON_CONFIDENTIAL_MODE_LABEL)
        badge.styles.background = "#ff1744"
        badge.styles.color = "#ffffff"
        badge.styles.border = ("none", "#ff1744")

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
