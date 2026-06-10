from __future__ import annotations

from pathlib import Path

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Input, LoadingIndicator, OptionList, Select, Static, Tree
from textual.widgets.option_list import Option

from exegesis_textual.services.imports import (
    browseable_import_entries,
    importable_markdown_files_in_folder,
    is_markdown_file,
)
from exegesis_textual.services.project_fixtures import DEFAULT_EMPTY_PROJECT_NAME
from exegesis_textual.services.projects import ProjectRecord, safe_project_dir_name
from exegesis_textual.services.model_settings import (
    MISTRAL_MODEL_OPTIONS,
    MISTRAL_REASONING_EFFORTS,
    MistralModelSettings,
    model_supports_reasoning,
)

PROJECT_NAME_INPUT_ID = "project-name-input"
PROJECT_NAME_CREATE_ID = "project-name-create"
PROJECT_NAME_CANCEL_ID = "project-name-cancel"
PROJECT_RENAME_ACTIVE_INPUT_ID = "project-rename-active-input"
PROJECT_RENAME_ACTIVE_CONFIRM_ID = "project-rename-active-confirm"
PROJECT_RENAME_ACTIVE_CANCEL_ID = "project-rename-active-cancel"
PROJECT_PICKER_OPTIONS_ID = "project-picker-options"
PROJECT_PICKER_OPEN_ID = "project-picker-open"
PROJECT_PICKER_DELETE_ID = "project-picker-delete"
PROJECT_PICKER_CANCEL_ID = "project-picker-cancel"
PROJECT_DELETE_CONFIRM_ID = "project-delete-confirm"
PROJECT_DELETE_CANCEL_ID = "project-delete-cancel"
PROJECTS_DIRECTORY_PATH_ID = "projects-directory-path"
PROJECTS_DIRECTORY_NEW_FOLDER_INPUT_ID = "projects-directory-new-folder-input"
PROJECTS_DIRECTORY_CREATE_FOLDER_ID = "projects-directory-create-folder"
PROJECTS_DIRECTORY_OPTIONS_ID = "projects-directory-options"
PROJECTS_DIRECTORY_SELECT_ID = "projects-directory-select"
PROJECTS_DIRECTORY_CANCEL_ID = "projects-directory-cancel"
PROJECT_RENAME_INPUT_ID = "project-rename-input"
PROJECT_RENAME_CONFIRM_ID = "project-rename-confirm"
PROJECT_RENAME_CANCEL_ID = "project-rename-cancel"
PROJECT_FOLDER_INPUT_ID = "project-folder-input"
PROJECT_FOLDER_CREATE_ID = "project-folder-create"
PROJECT_FOLDER_CANCEL_ID = "project-folder-cancel"
PROJECT_UPDATE_TITLE_INPUT_ID = "project-update-title-input"
PROJECT_UPDATE_FOLDER_TREE_ID = "project-update-folder-tree"
PROJECT_UPDATE_SELECTED_FOLDER_ID = "project-update-selected-folder"
PROJECT_UPDATE_CONFIRM_ID = "project-update-confirm"
PROJECT_UPDATE_CANCEL_ID = "project-update-cancel"
TRASH_RESTORE_ID = "trash-restore"
TRASH_PERMANENT_DELETE_ID = "trash-permanent-delete"
TRASH_CANCEL_ID = "trash-cancel"
DUPLICATE_REPLACE_ID = "duplicate-replace"
DUPLICATE_REPLACE_ALL_ID = "duplicate-replace-all"
DUPLICATE_RENAME_ID = "duplicate-rename"
DUPLICATE_CANCEL_ID = "duplicate-cancel"
DUPLICATE_CANCEL_IMPORT_ID = "duplicate-cancel-import"
DUPLICATE_RENAME_INPUT_ID = "duplicate-rename-input"
PROJECT_DUPLICATE_REPLACE_ID = "project-duplicate-replace"
PROJECT_DUPLICATE_RENAME_ID = "project-duplicate-rename"
PROJECT_DUPLICATE_CANCEL_ID = "project-duplicate-cancel"
PROJECT_DUPLICATE_RENAME_INPUT_ID = "project-duplicate-rename-input"
IMPORT_CATEGORY_SELECT_ID = "import-category-select"
IMPORT_BROWSER_PATH_ID = "import-browser-path"
IMPORT_BROWSER_SEARCH_ID = "import-browser-search"
IMPORT_BROWSER_OPTIONS_ID = "import-browser-options"
IMPORT_BROWSER_HELP_ID = "import-browser-help"
IMPORT_BROWSER_IMPORT_SELECTED_ID = "import-browser-import-selected"
IMPORT_BROWSER_IMPORT_FILES_FROM_FOLDER_ID = "import-browser-import-files-from-folder"
IMPORT_BROWSER_IMPORT_FOLDER_ID = "import-browser-import-folder"
IMPORT_BROWSER_CANCEL_ID = "import-browser-cancel"
IMPORT_PROGRESS_CURRENT_ID = "import-progress-current"
IMPORT_PROGRESS_COUNTS_ID = "import-progress-counts"
IMPORT_PROGRESS_STATUS_ID = "import-progress-status"
IMPORT_PROGRESS_CANCEL_ID = "import-progress-cancel"
SUMMARY_PROGRESS_MODAL_ID = "summary-progress-modal"
SUMMARY_PROGRESS_CURRENT_ID = "summary-progress-current"
SUMMARY_PROGRESS_CANCEL_ID = "summary-progress-cancel"
MODEL_SETTINGS_API_KEY_ID = "model-settings-api-key"
MODEL_SETTINGS_MODEL_ID = "model-settings-model"
MODEL_SETTINGS_REASONING_ID = "model-settings-reasoning"
MODEL_SETTINGS_STATUS_ID = "model-settings-status"
MODEL_SETTINGS_SAVE_ID = "model-settings-save"
MODEL_SETTINGS_TEST_ID = "model-settings-test"
MODEL_SETTINGS_CLEAR_ID = "model-settings-clear"
MODEL_SETTINGS_SKIP_ID = "model-settings-skip"
MODEL_SETTINGS_CANCEL_ID = "model-settings-cancel"
IMPORTABLE_PROJECT_CATEGORIES = ("Drafts", "Memos", "Summaries", "Transcripts", "Literature")
DEFAULT_IMPORT_CATEGORY = "Memos"


class TranscriptWarningModal(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="transcript-warning-modal"):
                yield Static("[b]Transcript Warning[/b]", id="project-modal-title")
                yield Static(
                    "Adding a full transcript to the basket while in online mode could reveal your participants "
                    "by sending identifiable material to a cloud LLM.",
                    id="transcript-warning-text",
                )
                with Horizontal(classes="project-modal-actions"):
                    yield Button("Dismiss", id="transcript-warning-dismiss", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "transcript-warning-dismiss":
            self.dismiss(None)


class NewProjectModal(ModalScreen[str | None]):
    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="project-name-modal"):
                yield Static("[b]New Project[/b]", id="project-modal-title")
                yield Input(placeholder="Project name", id=PROJECT_NAME_INPUT_ID)
                with Horizontal(classes="project-modal-actions"):
                    yield Button("Create", id=PROJECT_NAME_CREATE_ID, variant="primary")
                    yield Button("Cancel", id=PROJECT_NAME_CANCEL_ID)

    def on_mount(self) -> None:
        self.query_one(f"#{PROJECT_NAME_INPUT_ID}", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == PROJECT_NAME_INPUT_ID:
            self._submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == PROJECT_NAME_CREATE_ID:
            self._submit()
        elif event.button.id == PROJECT_NAME_CANCEL_ID:
            self.dismiss(None)

    def _submit(self) -> None:
        raw = self.query_one(f"#{PROJECT_NAME_INPUT_ID}", Input).value.strip()
        self.dismiss(raw or DEFAULT_EMPTY_PROJECT_NAME)


class RenameActiveProjectModal(ModalScreen[str | None]):
    def __init__(self, current_name: str) -> None:
        super().__init__()
        self._current_name = current_name

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="project-name-modal"):
                yield Static("[b]Rename Project[/b]", id="project-modal-title")
                yield Input(value=self._current_name, id=PROJECT_RENAME_ACTIVE_INPUT_ID)
                with Horizontal(classes="project-modal-actions"):
                    yield Button("Rename", id=PROJECT_RENAME_ACTIVE_CONFIRM_ID, variant="primary")
                    yield Button("Cancel", id=PROJECT_RENAME_ACTIVE_CANCEL_ID)

    def on_mount(self) -> None:
        rename_input = self.query_one(f"#{PROJECT_RENAME_ACTIVE_INPUT_ID}", Input)
        rename_input.focus()
        rename_input.action_end()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == PROJECT_RENAME_ACTIVE_INPUT_ID:
            self._submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == PROJECT_RENAME_ACTIVE_CONFIRM_ID:
            self._submit()
        elif event.button.id == PROJECT_RENAME_ACTIVE_CANCEL_ID:
            self.dismiss(None)

    def _submit(self) -> None:
        raw = self.query_one(f"#{PROJECT_RENAME_ACTIVE_INPUT_ID}", Input).value.strip()
        self.dismiss(raw or None)


ProjectBrowserAction = tuple[str, str]


class OpenProjectModal(ModalScreen[ProjectBrowserAction | None]):
    def __init__(self, projects: list[ProjectRecord]) -> None:
        super().__init__()
        self._projects = projects
        self._project_labels = [project.display_label for project in projects]
        self._project_by_label = {
            project.display_label: project
            for project in projects
        }

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="project-picker-modal"):
                yield Static("[b]Project Browser[/b]", id="project-modal-title")
                yield OptionList(*self._project_labels, id=PROJECT_PICKER_OPTIONS_ID)
                with Horizontal(classes="project-modal-actions"):
                    yield Button("Open", id=PROJECT_PICKER_OPEN_ID, variant="primary")
                    yield Button("Delete", id=PROJECT_PICKER_DELETE_ID, variant="warning")
                    yield Button("Cancel", id=PROJECT_PICKER_CANCEL_ID)

    def on_mount(self) -> None:
        options = self.query_one(f"#{PROJECT_PICKER_OPTIONS_ID}", OptionList)
        if self._projects:
            options.highlighted = 0
        options.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option_list.id == PROJECT_PICKER_OPTIONS_ID:
            project = self._project_from_prompt(event.option.prompt)
            if project is not None:
                self.dismiss(("open", project.slug))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == PROJECT_PICKER_OPEN_ID:
            project = self._selected_project()
            if project is not None:
                self.dismiss(("open", project.slug))
        elif event.button.id == PROJECT_PICKER_DELETE_ID:
            project = self._selected_project()
            if project is not None:
                self.dismiss(("delete", project.slug))
        elif event.button.id == PROJECT_PICKER_CANCEL_ID:
            self.dismiss(None)

    def _selected_project(self) -> ProjectRecord | None:
        options = self.query_one(f"#{PROJECT_PICKER_OPTIONS_ID}", OptionList)
        highlighted = options.highlighted
        if highlighted is None or highlighted < 0 or highlighted >= len(self._projects):
            return None
        return self._projects[highlighted]

    def _project_from_prompt(self, prompt: object) -> ProjectRecord | None:
        label = prompt.plain if hasattr(prompt, "plain") else str(prompt)
        return self._project_by_label.get(label)


class DeleteProjectConfirmModal(ModalScreen[bool]):
    def __init__(self, project: ProjectRecord) -> None:
        super().__init__()
        self._project = project

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="project-delete-confirm-modal"):
                yield Static("[b]Delete Project?[/b]", id="project-modal-title")
                yield Static(
                    f"Are you sure you want to delete {self._project.display_label}?\n\n"
                    "This removes the project folder from disk.",
                    id="project-delete-confirm-text",
                )
                with Horizontal(classes="project-modal-actions"):
                    yield Button("Delete", id=PROJECT_DELETE_CONFIRM_ID, variant="error")
                    yield Button("Cancel", id=PROJECT_DELETE_CANCEL_ID, variant="warning")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == PROJECT_DELETE_CONFIRM_ID:
            self.dismiss(True)
        elif event.button.id == PROJECT_DELETE_CANCEL_ID:
            self.dismiss(False)


class DeleteFolderConfirmModal(ModalScreen[bool]):
    def __init__(self, folder_label: str, document_count: int) -> None:
        super().__init__()
        self._folder_label = folder_label
        self._document_count = document_count

    def compose(self) -> ComposeResult:
        noun = "document" if self._document_count == 1 else "documents"
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="folder-delete-confirm-modal"):
                yield Static("[b]Delete Folder?[/b]", id="project-modal-title")
                yield Static(
                    f"Are you sure you want to move {self._folder_label} to trash?\n\n"
                    f"This moves {self._document_count} {noun} inside it to the project trash.",
                    id="project-delete-confirm-text",
                )
                with Horizontal(classes="project-modal-actions"):
                    yield Button(
                        "Move to Trash",
                        id=PROJECT_DELETE_CONFIRM_ID,
                        variant="error",
                        classes="confirm-modal-button",
                    )
                    yield Button(
                        "Cancel",
                        id=PROJECT_DELETE_CANCEL_ID,
                        classes="confirm-modal-button",
                    )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == PROJECT_DELETE_CONFIRM_ID:
            self.dismiss(True)
        elif event.button.id == PROJECT_DELETE_CANCEL_ID:
            self.dismiss(False)


class PermanentDeleteTrashConfirmModal(ModalScreen[bool]):
    def __init__(self, title: str, count: int = 1) -> None:
        super().__init__()
        self._title = title
        self._count = count

    def compose(self) -> ComposeResult:
        subject = self._title if self._count == 1 else f"{self._count} trash items"
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="trash-delete-confirm-modal"):
                yield Static("[b]Delete Forever?[/b]", id="project-modal-title")
                yield Static(
                    f"Are you sure you want to permanently delete {subject}?\n\n"
                    "This removes the trashed content from disk. The audit trail is retained.",
                    id="project-delete-confirm-text",
                )
                with Horizontal(classes="project-modal-actions"):
                    yield Button(
                        "Delete Forever",
                        id=PROJECT_DELETE_CONFIRM_ID,
                        variant="error",
                        classes="confirm-modal-button",
                    )
                    yield Button(
                        "Cancel",
                        id=PROJECT_DELETE_CANCEL_ID,
                        classes="confirm-modal-button",
                    )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == PROJECT_DELETE_CONFIRM_ID:
            self.dismiss(True)
        elif event.button.id == PROJECT_DELETE_CANCEL_ID:
            self.dismiss(False)


class SelectProjectsDirectoryModal(ModalScreen[Path | None]):
    def __init__(self, start_dir: Path) -> None:
        super().__init__()
        self._current_dir = start_dir.expanduser().resolve()
        self._entry_map: dict[str, Path] = {}

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="projects-directory-modal"):
                yield Static("[b]Projects Directory[/b]", id="project-modal-title")
                yield Static(str(self._current_dir), id=PROJECTS_DIRECTORY_PATH_ID)
                with Horizontal(id="projects-directory-create-row"):
                    yield Input(placeholder="New folder name", id=PROJECTS_DIRECTORY_NEW_FOLDER_INPUT_ID)
                    yield Button("Create Folder", id=PROJECTS_DIRECTORY_CREATE_FOLDER_ID, variant="primary")
                yield OptionList(id=PROJECTS_DIRECTORY_OPTIONS_ID)
                with Horizontal(classes="project-modal-actions"):
                    yield Button("Use This Folder", id=PROJECTS_DIRECTORY_SELECT_ID, variant="primary")
                    yield Button("Cancel", id=PROJECTS_DIRECTORY_CANCEL_ID)

    def on_mount(self) -> None:
        self._refresh_entries()
        self.query_one(f"#{PROJECTS_DIRECTORY_OPTIONS_ID}", OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option_list.id != PROJECTS_DIRECTORY_OPTIONS_ID:
            return
        target = self._entry_map.get(event.option.id or "")
        if target is None:
            return
        self._current_dir = target.resolve()
        self._refresh_entries()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == PROJECTS_DIRECTORY_CREATE_FOLDER_ID:
            self._create_folder()
        elif event.button.id == PROJECTS_DIRECTORY_SELECT_ID:
            self.dismiss(self._current_dir)
        elif event.button.id == PROJECTS_DIRECTORY_CANCEL_ID:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == PROJECTS_DIRECTORY_NEW_FOLDER_INPUT_ID:
            self._create_folder()

    def _create_folder(self) -> None:
        folder_input = self.query_one(f"#{PROJECTS_DIRECTORY_NEW_FOLDER_INPUT_ID}", Input)
        raw = folder_input.value.strip()
        if not raw:
            return
        safe_name = raw.replace("/", "-").replace("\\", "-").strip()
        if not safe_name:
            return
        target = (self._current_dir / safe_name).resolve()
        try:
            target.mkdir(parents=True, exist_ok=True)
        except OSError:
            return
        self._current_dir = target
        folder_input.value = ""
        self._refresh_entries()

    def _refresh_entries(self) -> None:
        self._entry_map.clear()
        options: list[Option] = []
        if self._current_dir.parent != self._current_dir:
            self._entry_map["parent"] = self._current_dir.parent
            options.append(Option("../", id="parent"))
        try:
            directories = [
                entry
                for entry in self._current_dir.iterdir()
                if entry.is_dir() and not entry.name.startswith(".")
            ]
        except OSError:
            directories = []
        for index, entry in enumerate(sorted(directories, key=lambda path: path.name.lower()), start=1):
            option_id = f"entry-{index}"
            self._entry_map[option_id] = entry
            options.append(Option(f"{entry.name}/", id=option_id))
        self.query_one(f"#{PROJECTS_DIRECTORY_OPTIONS_ID}", OptionList).set_options(options)
        self.query_one(f"#{PROJECTS_DIRECTORY_PATH_ID}", Static).update(str(self._current_dir))


class RenameProjectEntryModal(ModalScreen[str | None]):
    def __init__(self, current_name: str) -> None:
        super().__init__()
        self._current_name = current_name

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="project-name-modal"):
                yield Static("[b]Rename File[/b]", id="project-modal-title")
                yield Input(value=self._current_name, id=PROJECT_RENAME_INPUT_ID)
                with Horizontal(classes="project-modal-actions"):
                    yield Button("Rename", id=PROJECT_RENAME_CONFIRM_ID, variant="primary")
                    yield Button("Cancel", id=PROJECT_RENAME_CANCEL_ID)

    def on_mount(self) -> None:
        rename_input = self.query_one(f"#{PROJECT_RENAME_INPUT_ID}", Input)
        rename_input.focus()
        rename_input.action_end()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == PROJECT_RENAME_INPUT_ID:
            self._submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == PROJECT_RENAME_CONFIRM_ID:
            self._submit()
        elif event.button.id == PROJECT_RENAME_CANCEL_ID:
            self.dismiss(None)

    def _submit(self) -> None:
        raw = self.query_one(f"#{PROJECT_RENAME_INPUT_ID}", Input).value.strip()
        self.dismiss(raw or None)


class NewProjectFolderModal(ModalScreen[str | None]):
    def __init__(self, category: str, parent_folder: str = "") -> None:
        super().__init__()
        self._category = category
        self._parent_folder = parent_folder

    def compose(self) -> ComposeResult:
        parent = self._parent_folder or "/"
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="project-name-modal"):
                yield Static("[b]New Folder[/b]", id="project-modal-title")
                yield Static(f"Create a folder in {self._category}: {parent}", id="project-modal-subtitle")
                yield Input(placeholder="Folder name", id=PROJECT_FOLDER_INPUT_ID)
                with Horizontal(classes="project-modal-actions"):
                    yield Button("Create Folder", id=PROJECT_FOLDER_CREATE_ID, variant="primary")
                    yield Button("Cancel", id=PROJECT_FOLDER_CANCEL_ID)

    def on_mount(self) -> None:
        self.query_one(f"#{PROJECT_FOLDER_INPUT_ID}", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == PROJECT_FOLDER_INPUT_ID:
            self._submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == PROJECT_FOLDER_CREATE_ID:
            self._submit()
        elif event.button.id == PROJECT_FOLDER_CANCEL_ID:
            self.dismiss(None)

    def _submit(self) -> None:
        raw = self.query_one(f"#{PROJECT_FOLDER_INPUT_ID}", Input).value.strip()
        self.dismiss(raw or None)


class UpdateFolderPickerTree(Tree[str]):
    def __init__(self, category: str, folder_paths: tuple[str, ...], current_folder: str = "") -> None:
        super().__init__(category, data="", id=PROJECT_UPDATE_FOLDER_TREE_ID)
        self.show_root = True
        self.auto_expand = True
        self._node_by_folder: dict[str, Tree.Node[str]] = {"": self.root}
        self._build_folder_tree(folder_paths)
        self.select_folder(current_folder)

    def _build_folder_tree(self, folder_paths: tuple[str, ...]) -> None:
        for folder_path in sorted({path for path in folder_paths if path}, key=lambda path: (Path(path).parts, path.casefold())):
            current = self.root
            accumulated: list[str] = []
            for part in Path(folder_path).parts:
                accumulated.append(part)
                folder = Path(*accumulated).as_posix()
                node = self._node_by_folder.get(folder)
                if node is None:
                    node = current.add(part, data=folder)
                    node.expand()
                    self._node_by_folder[folder] = node
                current = node
        self.root.expand()

    def on_mount(self) -> None:
        self.select_folder(self.selected_folder)

    @property
    def selected_folder(self) -> str:
        node = self.cursor_node
        return "" if node is None or node.data is None else node.data

    def select_folder(self, folder: str) -> None:
        normalized = "" if folder in {"", "."} else Path(folder).as_posix()
        node = self._node_by_folder.get(normalized, self.root)
        _ = self._tree_lines
        self.move_cursor(node, animate=False)


class UpdateProjectItemModal(ModalScreen[tuple[str, str] | None]):
    def __init__(self, current_title: str, category: str, current_folder: str = "", folder_paths: tuple[str, ...] = ()) -> None:
        super().__init__()
        self._current_title = current_title
        self._category = category
        self._current_folder = current_folder
        self._draft_title = current_title
        self._selected_folder = current_folder
        self._action_dispatched = False
        self._folder_paths = tuple(sorted({"", current_folder, *folder_paths}))

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="project-update-modal"):
                yield Static("[b]Update Item[/b]", id="project-modal-title")
                yield Static(
                    "Rename the item or move it to a folder in the same document category.",
                    id="project-update-modal-subtitle",
                )
                yield Static("File name", classes="project-modal-field-label")
                yield Input(value=self._current_title, id=PROJECT_UPDATE_TITLE_INPUT_ID)
                yield Static("Move to folder", classes="project-modal-field-label")
                yield UpdateFolderPickerTree(self._category, self._folder_paths, self._current_folder)
                yield Static(self._folder_label(self._current_folder), id=PROJECT_UPDATE_SELECTED_FOLDER_ID)
                with Horizontal(classes="project-modal-actions"):
                    yield Button("Update Item", id=PROJECT_UPDATE_CONFIRM_ID, variant="primary")
                    yield Button("Cancel", id=PROJECT_UPDATE_CANCEL_ID)

    def on_mount(self) -> None:
        title_input = self.query_one(f"#{PROJECT_UPDATE_TITLE_INPUT_ID}", Input)
        title_input.focus()
        title_input.action_end()
        self.query_one(UpdateFolderPickerTree).select_folder(self._current_folder)

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted[str]) -> None:
        if isinstance(event.control, UpdateFolderPickerTree):
            event.stop()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == PROJECT_UPDATE_TITLE_INPUT_ID:
            self._submit()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == PROJECT_UPDATE_TITLE_INPUT_ID:
            self._draft_title = event.value

    def on_tree_node_selected(self, event: Tree.NodeSelected[str]) -> None:
        if isinstance(event.control, UpdateFolderPickerTree):
            folder = event.node.data or ""
            self._selected_folder = folder
            self.query_one(f"#{PROJECT_UPDATE_SELECTED_FOLDER_ID}", Static).update(self._folder_label(folder))
            event.stop()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id not in {PROJECT_UPDATE_CONFIRM_ID, PROJECT_UPDATE_CANCEL_ID}:
            return
        event.stop()
        if self._action_dispatched:
            return
        self._action_dispatched = True
        if event.button.id == PROJECT_UPDATE_CONFIRM_ID:
            self._submit()
        else:
            self._cancel()

    def _submit(self) -> None:
        title_input = self.query_one(f"#{PROJECT_UPDATE_TITLE_INPUT_ID}", Input)
        title = (title_input.value or self._draft_title).strip()
        folder = self._selected_folder
        if not title:
            self.dismiss(None)
            return
        self.dismiss((title, folder))

    def _cancel(self) -> None:
        self.dismiss(None)

    def _folder_label(self, folder: str) -> str:
        return f"Selected folder: {folder}" if folder else f"Selected folder: {self._category}"


class TrashDocumentModal(ModalScreen[str | None]):
    def __init__(self, title: str, original_id: str) -> None:
        super().__init__()
        self._title = title
        self._original_id = original_id

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="trash-document-modal"):
                yield Static("[b]Trash[/b]", id="project-modal-title")
                yield Static(
                    f"{self._title}\n\nRestore target: {self._original_id or 'Unknown'}",
                    id="trash-document-details",
                )
                with Horizontal(classes="project-modal-actions trash-modal-actions"):
                    yield Button("Restore", id=TRASH_RESTORE_ID, variant="primary", classes="trash-modal-button trash-modal-side-button")
                    yield Button(
                        "Permanently Delete",
                        id=TRASH_PERMANENT_DELETE_ID,
                        variant="error",
                        classes="trash-modal-button trash-modal-danger-button",
                    )
                    yield Button("Cancel", id=TRASH_CANCEL_ID, variant="warning", classes="trash-modal-button trash-modal-side-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == TRASH_RESTORE_ID:
            self.dismiss("restore")
        elif event.button.id == TRASH_PERMANENT_DELETE_ID:
            self.dismiss("permanent_delete")
        elif event.button.id == TRASH_CANCEL_ID:
            self.dismiss(None)


class DuplicateDocumentModal(ModalScreen[tuple[str, str | None] | None]):
    def __init__(
        self,
        title: str,
        existing_id: str,
        *,
        cancel_label: str = "Cancel",
        cancel_result: tuple[str, str | None] | None = None,
        replace_all_label: str | None = None,
        replace_all_result: tuple[str, str | None] | None = None,
        cancel_import_label: str | None = None,
        cancel_import_result: tuple[str, str | None] | None = None,
    ) -> None:
        super().__init__()
        self._title = title
        self._existing_id = existing_id
        self._cancel_label = cancel_label
        self._cancel_result = cancel_result
        self._replace_all_label = replace_all_label
        self._replace_all_result = replace_all_result
        self._cancel_import_label = cancel_import_label
        self._cancel_import_result = cancel_import_result

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="duplicate-document-modal"):
                yield Static("[b]Duplicate Document[/b]", id="project-modal-title")
                yield Static(
                    f"A document already exists at:\n{self._existing_id}\n\nReplace it, import with a new name, or skip this file.",
                    id="duplicate-document-details",
                )
                yield Input(value=self._title, id=DUPLICATE_RENAME_INPUT_ID)
                with Horizontal(classes="project-modal-actions duplicate-modal-actions"):
                    yield Button("Replace", id=DUPLICATE_REPLACE_ID, variant="warning")
                    if self._replace_all_label is not None:
                        yield Button(self._replace_all_label, id=DUPLICATE_REPLACE_ALL_ID, variant="warning")
                    yield Button("Rename", id=DUPLICATE_RENAME_ID, variant="primary")
                    yield Button(self._cancel_label, id=DUPLICATE_CANCEL_ID, variant="primary")
                if self._cancel_import_label is not None:
                    with Horizontal(classes="project-modal-actions duplicate-modal-cancel-actions"):
                        yield Button(self._cancel_import_label, id=DUPLICATE_CANCEL_IMPORT_ID)

    def on_mount(self) -> None:
        rename_input = self.query_one(f"#{DUPLICATE_RENAME_INPUT_ID}", Input)
        rename_input.focus()
        rename_input.action_end()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == DUPLICATE_REPLACE_ID:
            self.dismiss(("replace", None))
        elif event.button.id == DUPLICATE_REPLACE_ALL_ID:
            self.dismiss(self._replace_all_result)
        elif event.button.id == DUPLICATE_RENAME_ID:
            value = self.query_one(f"#{DUPLICATE_RENAME_INPUT_ID}", Input).value.strip()
            self.dismiss(("rename", value or self._title))
        elif event.button.id == DUPLICATE_CANCEL_ID:
            self.dismiss(self._cancel_result)
        elif event.button.id == DUPLICATE_CANCEL_IMPORT_ID:
            self.dismiss(self._cancel_import_result)


class DuplicateProjectModal(ModalScreen[tuple[str, str | None] | None]):
    def __init__(self, project_name: str, existing_slug: str) -> None:
        super().__init__()
        self._project_name = project_name
        self._existing_slug = existing_slug

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="duplicate-project-modal"):
                yield Static("[b]Duplicate Project[/b]", id="project-modal-title")
                yield Static(
                    f"A project folder already exists at:\n{self._existing_slug}\n\n"
                    "Replace it with the current project, rename this project, or cancel.",
                    id="duplicate-document-details",
                )
                yield Input(value=self._project_name, id=PROJECT_DUPLICATE_RENAME_INPUT_ID)
                with Horizontal(classes="project-modal-actions duplicate-modal-actions"):
                    yield Button("Replace", id=PROJECT_DUPLICATE_REPLACE_ID, variant="warning")
                    yield Button("Rename", id=PROJECT_DUPLICATE_RENAME_ID, variant="primary")
                    yield Button("Cancel", id=PROJECT_DUPLICATE_CANCEL_ID)

    def on_mount(self) -> None:
        rename_input = self.query_one(f"#{PROJECT_DUPLICATE_RENAME_INPUT_ID}", Input)
        rename_input.focus()
        rename_input.action_end()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == PROJECT_DUPLICATE_RENAME_INPUT_ID:
            self._rename()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == PROJECT_DUPLICATE_REPLACE_ID:
            self.dismiss(("replace", None))
        elif event.button.id == PROJECT_DUPLICATE_RENAME_ID:
            self._rename()
        elif event.button.id == PROJECT_DUPLICATE_CANCEL_ID:
            self.dismiss(None)

    def _rename(self) -> None:
        value = self.query_one(f"#{PROJECT_DUPLICATE_RENAME_INPUT_ID}", Input).value.strip()
        self.dismiss(("rename", value or self._project_name))


class ImportBrowserOptionList(OptionList):
    def on_click(self, event: events.Click) -> None:
        clicked_option = event.style.meta.get("option")
        if clicked_option is None:
            clicked_option = self._mouse_hovering_over
        if clicked_option is None:
            clicked_option = self.highlighted
        modal = next((ancestor for ancestor in self.ancestors_with_self if isinstance(ancestor, ImportMarkdownModal)), None)
        if not isinstance(clicked_option, int) or modal is None:
            return
        try:
            option = self.get_option_at_index(clicked_option)
        except (IndexError, ValueError):
            return
        highlighted = self.highlighted_option
        modal.record_option_click(option.id or "", shift=event.shift, prior_option_id=highlighted.id if highlighted else None)


class ImportMarkdownModal(ModalScreen[tuple[object, ...] | None]):
    BINDINGS = [
        Binding("space", "toggle_selected_file", "Select file", priority=True),
    ]

    def __init__(self, start_dir: Path | None = None, default_category: str = DEFAULT_IMPORT_CATEGORY) -> None:
        super().__init__()
        self._current_dir = (start_dir or Path.home()).expanduser().resolve()
        self._selected_category = default_category if default_category in IMPORTABLE_PROJECT_CATEGORIES else DEFAULT_IMPORT_CATEGORY
        self._search_query = ""
        self._entry_map: dict[str, Path] = {}
        self._selected_paths: set[Path] = set()
        self._pending_option_click: tuple[str, bool, str | None] | None = None

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="import-browser-modal"):
                yield Static("[b]Import Markdown[/b]", id="project-modal-title")
                yield Static("Document type", id="import-category-label")
                yield Select(
                    [(category, category) for category in IMPORTABLE_PROJECT_CATEGORIES],
                    value=self._selected_category,
                    allow_blank=False,
                    id=IMPORT_CATEGORY_SELECT_ID,
                )
                yield Static(str(self._current_dir), id=IMPORT_BROWSER_PATH_ID)
                yield Input(placeholder="Search filenames in this folder", id=IMPORT_BROWSER_SEARCH_ID)
                yield Static("Shift-click or Space selects files. Enter or click imports one file.", id=IMPORT_BROWSER_HELP_ID)
                yield ImportBrowserOptionList(id=IMPORT_BROWSER_OPTIONS_ID)
                with Horizontal(classes="project-modal-actions import-browser-actions"):
                    yield Button("Import", id=IMPORT_BROWSER_IMPORT_SELECTED_ID, variant="primary")
                    yield Button("Import all", id=IMPORT_BROWSER_IMPORT_FILES_FROM_FOLDER_ID, variant="primary")
                    yield Button("Import folder", id=IMPORT_BROWSER_IMPORT_FOLDER_ID, variant="warning")
                    yield Button("Cancel", id=IMPORT_BROWSER_CANCEL_ID)

    def on_mount(self) -> None:
        self._refresh_entries()
        self.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}", OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option_list.id != IMPORT_BROWSER_OPTIONS_ID:
            return
        pending = self._pending_option_click
        self._pending_option_click = None
        if pending is not None and pending[0] == (event.option.id or ""):
            option_id, shift, _prior_option_id = pending
            if shift:
                self.toggle_option_id(option_id, include_highlighted=False)
                return
        self.select_option_id(event.option.id or "")

    def record_option_click(self, option_id: str, *, shift: bool, prior_option_id: str | None) -> None:
        self._pending_option_click = (option_id, shift, prior_option_id)

    def select_option_index(self, option_index: int) -> bool:
        option_list = self.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}", OptionList)
        try:
            option = option_list.get_option_at_index(option_index)
        except (IndexError, ValueError):
            return False
        option_list.highlighted = option_index
        return self.select_option_id(option.id or "")

    def select_option_id(self, option_id: str) -> bool:
        target = self._entry_map.get(option_id)
        if target is None:
            return False
        if target.is_dir():
            self._current_dir = target.resolve()
            self._search_query = ""
            self._refresh_entries()
            return True
        if is_markdown_file(target):
            self.dismiss((str(target.resolve()), self._selected_category))
            return True
        return False

    def action_toggle_selected_file(self) -> None:
        option = self.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}", OptionList).highlighted_option
        if option is None:
            return
        self.toggle_option_id(option.id or "", include_highlighted=False)

    def toggle_option_index(self, option_index: int, *, include_highlighted: bool) -> bool:
        option_list = self.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}", OptionList)
        try:
            option = option_list.get_option_at_index(option_index)
        except (IndexError, ValueError):
            return False
        if include_highlighted:
            highlighted = option_list.highlighted_option
            if highlighted is not None and highlighted.id != option.id and self._is_option_marked(highlighted.id or ""):
                self._mark_option_id(highlighted.id or "")
        option_list.highlighted = option_index
        selected = self.toggle_option_id(option.id or "", include_highlighted=False)
        return selected

    def toggle_option_id(self, option_id: str, *, include_highlighted: bool) -> bool:
        if include_highlighted:
            highlighted = self.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}", OptionList).highlighted_option
            if highlighted is not None and highlighted.id != option_id:
                self._mark_option_id(highlighted.id or "")
        target = self._entry_map.get(option_id)
        if target is None or not is_markdown_file(target):
            return False
        resolved = target.resolve()
        if resolved in self._selected_paths:
            self._selected_paths.remove(resolved)
        else:
            self._selected_paths.add(resolved)
        self._refresh_option_label(option_id)
        return True

    def _mark_option_id(self, option_id: str) -> None:
        target = self._entry_map.get(option_id)
        if target is not None and is_markdown_file(target):
            self._selected_paths.add(target.resolve())
            self._refresh_option_label(option_id)

    def _is_option_marked(self, option_id: str) -> bool:
        target = self._entry_map.get(option_id)
        return target is not None and is_markdown_file(target) and target.resolve() in self._selected_paths

    def _refresh_option_label(self, option_id: str) -> None:
        target = self._entry_map.get(option_id)
        if target is None:
            return
        selected_marker = "* " if target.resolve() in self._selected_paths else ""
        label = f"{target.name}/" if target.is_dir() else f"{selected_marker}{target.name}"
        self.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}", OptionList).replace_option_prompt(option_id, label)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id != IMPORT_CATEGORY_SELECT_ID:
            return
        value = event.value
        if isinstance(value, str) and value in IMPORTABLE_PROJECT_CATEGORIES:
            self._selected_category = value

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != IMPORT_BROWSER_SEARCH_ID:
            return
        self._search_query = event.value
        self._refresh_entries()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == IMPORT_BROWSER_CANCEL_ID:
            self.dismiss(None)
        elif event.button.id == IMPORT_BROWSER_IMPORT_SELECTED_ID:
            selected = tuple(str(path) for path in sorted(self._selected_paths, key=lambda item: item.name.casefold()))
            if selected:
                self.dismiss((selected, self._selected_category, "selected", None))
        elif event.button.id == IMPORT_BROWSER_IMPORT_FILES_FROM_FOLDER_ID:
            files = tuple(str(path) for path in importable_markdown_files_in_folder(self._current_dir))
            if files:
                self.dismiss((files, self._selected_category, "folder_flat", str(self._current_dir)))
        elif event.button.id == IMPORT_BROWSER_IMPORT_FOLDER_ID:
            files = tuple(str(path) for path in importable_markdown_files_in_folder(self._current_dir))
            if files:
                self.dismiss((files, self._selected_category, "folder_tree", str(self._current_dir)))

    def _refresh_entries(self, *, preserve_view: bool = False, preserve_highlight: bool = True) -> None:
        option_list = self.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}", OptionList)
        scroll_y = option_list.scroll_y
        highlighted = option_list.highlighted if preserve_highlight else None
        self._entry_map.clear()
        options: list[Option] = []
        if self._current_dir.parent != self._current_dir:
            self._entry_map["parent"] = self._current_dir.parent
            options.append(Option("../", id="parent"))
        for index, entry in enumerate(browseable_import_entries(self._current_dir, self._search_query), start=1):
            option_id = f"entry-{index}"
            self._entry_map[option_id] = entry
            selected_marker = "* " if entry.resolve() in self._selected_paths else ""
            label = f"{entry.name}/" if entry.is_dir() else f"{selected_marker}{entry.name}"
            options.append(Option(label, id=option_id))
        option_list.set_options(options)
        if preserve_view:
            self._restore_option_view(scroll_y=scroll_y, highlighted=highlighted)
            self.call_after_refresh(lambda: self._restore_option_view(scroll_y=scroll_y, highlighted=highlighted))
        else:
            self._clear_option_highlight()
            self.call_after_refresh(self._clear_option_highlight)
        self.query_one(f"#{IMPORT_BROWSER_PATH_ID}", Static).update(str(self._current_dir))
        search_input = self.query_one(f"#{IMPORT_BROWSER_SEARCH_ID}", Input)
        if search_input.value != self._search_query:
            search_input.value = self._search_query

    def _clear_option_highlight(self) -> None:
        option_list = self.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}", OptionList)
        option_list.highlighted = None
        option_list._mouse_hovering_over = None

    def _restore_option_view(self, *, scroll_y: float, highlighted: int | None) -> None:
        option_list = self.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}", OptionList)
        option_list.highlighted = highlighted
        option_list.scroll_y = scroll_y


class ImportProgressModal(ModalScreen[None]):
    def __init__(self, *, total: int, category: str) -> None:
        super().__init__()
        self._total = total
        self._category = category
        self.cancel_requested = False

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="import-progress-modal"):
                yield Static("[b]Importing Markdown[/b]", id="project-modal-title")
                yield Static(f"Preparing to import {self._total} files into {self._category}.", id=IMPORT_PROGRESS_CURRENT_ID)
                yield Static(f"0 of {self._total} processed. 0 added. 0 skipped.", id=IMPORT_PROGRESS_COUNTS_ID)
                yield Static("Duplicate files will ask whether to replace, rename, or skip.", id=IMPORT_PROGRESS_STATUS_ID)
                with Horizontal(classes="project-modal-actions import-progress-actions"):
                    yield Button("Cancel remaining", id=IMPORT_PROGRESS_CANCEL_ID, variant="warning")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == IMPORT_PROGRESS_CANCEL_ID:
            self.cancel_requested = True
            event.button.disabled = True
            self.query_one(f"#{IMPORT_PROGRESS_STATUS_ID}", Static).update(
                "Cancelling after the current file. Already imported files will remain."
            )

    def update_progress(
        self,
        *,
        current: str,
        processed: int,
        imported: int,
        skipped: int,
        status: str = "Importing...",
    ) -> None:
        self.query_one(f"#{IMPORT_PROGRESS_CURRENT_ID}", Static).update(current)
        self.query_one(f"#{IMPORT_PROGRESS_COUNTS_ID}", Static).update(
            f"{processed} of {self._total} processed. {imported} added. {skipped} skipped."
        )
        self.query_one(f"#{IMPORT_PROGRESS_STATUS_ID}", Static).update(status)

    def complete(self, message: str) -> None:
        self.query_one(f"#{IMPORT_PROGRESS_STATUS_ID}", Static).update(message)


class SummaryProgressModal(ModalScreen[None]):
    class CancelRequested(Message):
        def __init__(self, modal: "SummaryProgressModal", chat_slug: str) -> None:
            super().__init__()
            self.modal = modal
            self.chat_slug = chat_slug

    def __init__(self, *, size: str, title: str, chat_slug: str) -> None:
        super().__init__()
        self._summary_size = size
        self._document_title = title
        self._chat_slug = chat_slug
        self.cancel_requested = False

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-screen-center"):
            with Vertical(id=SUMMARY_PROGRESS_MODAL_ID):
                yield Static("[b]Generating Summary[/b]", id="project-modal-title")
                yield Static(
                    f"Writing a {self._summary_size} summary for {self._document_title}.\n\n"
                    "This can take a moment while the model reads the current document.",
                    id=SUMMARY_PROGRESS_CURRENT_ID,
                )
                yield LoadingIndicator()
                with Horizontal(classes="project-modal-actions summary-progress-actions"):
                    yield Button("Cancel", id=SUMMARY_PROGRESS_CANCEL_ID, classes="confirm-modal-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == SUMMARY_PROGRESS_CANCEL_ID:
            self.cancel_requested = True
            event.button.disabled = True
            self.query_one(f"#{SUMMARY_PROGRESS_CURRENT_ID}", Static).update(
                "Cancelling summary generation. Any partial response will be discarded."
            )
            self.post_message(self.CancelRequested(self, self._chat_slug))

    def complete(self, message: str) -> None:
        self.query_one(f"#{SUMMARY_PROGRESS_CURRENT_ID}", Static).update(message)


ModelSettingsAction = tuple[str, MistralModelSettings, str]


class ModelSettingsModal(ModalScreen[ModelSettingsAction | None]):
    class TestConnectionRequested(Message):
        def __init__(self, modal: "ModelSettingsModal", settings: MistralModelSettings, api_key: str) -> None:
            super().__init__()
            self.modal = modal
            self.settings = settings
            self.api_key = api_key

    def __init__(
        self,
        *,
        settings: MistralModelSettings,
        has_api_key: bool,
        secure_storage_available: bool = True,
        secure_storage_message: str = "",
        first_launch: bool = False,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._has_api_key = has_api_key
        self._secure_storage_available = secure_storage_available
        self._secure_storage_message = secure_storage_message
        self._first_launch = first_launch

    def compose(self) -> ComposeResult:
        key_placeholder = "Stored securely" if self._has_api_key else "Mistral API key"
        with Vertical(classes="modal-screen-center"):
            with Vertical(id="model-settings-modal"):
                yield Static("[b]Model Settings[/b]", id="project-modal-title")
                yield Static(
                    "Configure the Mistral model used by the notebook. API keys are stored with the system keyring, not in settings JSON.",
                    id=MODEL_SETTINGS_STATUS_ID,
                )
                yield Input(placeholder=key_placeholder, password=True, id=MODEL_SETTINGS_API_KEY_ID)
                yield Static("Model", classes="modal-field-label")
                yield Select(
                    [(model, model) for model in MISTRAL_MODEL_OPTIONS],
                    value=self._settings.model,
                    id=MODEL_SETTINGS_MODEL_ID,
                    allow_blank=False,
                )
                yield Static("Reasoning effort", classes="modal-field-label")
                yield Select(
                    [(effort.title(), effort) for effort in MISTRAL_REASONING_EFFORTS],
                    value=self._settings.reasoning_effort if self._settings.reasoning_effort in MISTRAL_REASONING_EFFORTS else "none",
                    id=MODEL_SETTINGS_REASONING_ID,
                    allow_blank=False,
                )
                with Horizontal(classes="project-modal-actions model-settings-actions"):
                    yield Button("Save", id=MODEL_SETTINGS_SAVE_ID, variant="primary")
                    yield Button("Test connection", id=MODEL_SETTINGS_TEST_ID, variant="primary")
                    yield Button("Clear key", id=MODEL_SETTINGS_CLEAR_ID, variant="warning")
                    yield Button("Skip for now" if self._first_launch else "Cancel", id=MODEL_SETTINGS_SKIP_ID if self._first_launch else MODEL_SETTINGS_CANCEL_ID)

    def on_mount(self) -> None:
        self._sync_reasoning_state()
        self.query_one(f"#{MODEL_SETTINGS_API_KEY_ID}", Input).focus()
        self._sync_secure_storage_actions()
        if not self._secure_storage_available:
            self._update_status(self._secure_storage_message or "Secure credential storage is unavailable or locked.")

    def on_paste(self, event: events.Paste) -> None:
        focused = self.app.focused
        if isinstance(focused, Input) and focused.id == MODEL_SETTINGS_API_KEY_ID:
            focused.insert_text_at_cursor(event.text)
            event.stop()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == MODEL_SETTINGS_MODEL_ID:
            self._sync_reasoning_state()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == MODEL_SETTINGS_SAVE_ID:
            if not self._secure_storage_available:
                self._update_status(self._secure_storage_message or "Secure credential storage is unavailable or locked.")
                return
            self.dismiss(("save", self._current_settings(dismissed=True), self._api_key_value()))
        elif event.button.id == MODEL_SETTINGS_TEST_ID:
            self._request_live_connection_test()
        elif event.button.id == MODEL_SETTINGS_CLEAR_ID:
            if not self._secure_storage_available:
                self._update_status(self._secure_storage_message or "Secure credential storage is unavailable or locked.")
                return
            self.dismiss(("clear", self._current_settings(dismissed=True), ""))
        elif event.button.id == MODEL_SETTINGS_SKIP_ID:
            self.dismiss(("skip", self._current_settings(dismissed=True), ""))
        elif event.button.id == MODEL_SETTINGS_CANCEL_ID:
            self.dismiss(None)

    def _api_key_value(self) -> str:
        return self.query_one(f"#{MODEL_SETTINGS_API_KEY_ID}", Input).value.strip()

    def _selected_model(self) -> str:
        value = self.query_one(f"#{MODEL_SETTINGS_MODEL_ID}", Select).value
        return str(value or self._settings.model)

    def _selected_reasoning_effort(self) -> str:
        model = self._selected_model()
        if not model_supports_reasoning(model):
            return "none"
        value = self.query_one(f"#{MODEL_SETTINGS_REASONING_ID}", Select).value
        return str(value or self._settings.reasoning_effort or "high")

    def _current_settings(self, *, dismissed: bool) -> MistralModelSettings:
        return MistralModelSettings(
            model=self._selected_model(),
            reasoning_effort=self._selected_reasoning_effort(),
            settings_prompt_dismissed=dismissed,
        )

    def _sync_reasoning_state(self) -> None:
        model = self._selected_model()
        reasoning = self.query_one(f"#{MODEL_SETTINGS_REASONING_ID}", Select)
        supported = model_supports_reasoning(model)
        reasoning.disabled = not supported
        if not supported:
            reasoning.value = "none"
            return
        if reasoning.value not in MISTRAL_REASONING_EFFORTS:
            reasoning.value = "high"

    def _sync_secure_storage_actions(self) -> None:
        self.query_one(f"#{MODEL_SETTINGS_SAVE_ID}", Button).disabled = not self._secure_storage_available
        self.query_one(f"#{MODEL_SETTINGS_CLEAR_ID}", Button).disabled = not self._secure_storage_available

    def _update_status(self, message: str) -> None:
        self.query_one(f"#{MODEL_SETTINGS_STATUS_ID}", Static).update(f"Status: {message}")

    def _request_live_connection_test(self) -> None:
        if not self._secure_storage_available:
            self._update_status(self._secure_storage_message or "Secure credential storage is unavailable or locked.")
            return
        if not self._has_api_key and not self._api_key_value():
            self._update_status("Mistral API key is missing. Paste a key or skip setup for now.")
            return
        settings = self._current_settings(dismissed=True)
        self.query_one(f"#{MODEL_SETTINGS_TEST_ID}", Button).disabled = True
        self._update_status(f"Testing live Mistral connection with {settings.model}...")
        self.post_message(self.TestConnectionRequested(self, settings, self._api_key_value()))

    def complete_connection_test(self, message: str) -> None:
        if not self.is_mounted:
            return
        self.query_one(f"#{MODEL_SETTINGS_TEST_ID}", Button).disabled = False
        self._update_status(message)
