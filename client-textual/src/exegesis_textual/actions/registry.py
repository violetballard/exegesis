from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

AppActionSafety = Literal["read_only_auto", "proposal_auto", "confirm_required", "system_only"]
AppActionStatus = Literal["completed", "pending_confirmation", "refused", "failed"]
AppActionSource = Literal["button", "shortcut", "palette", "notebook", "model_tool", "system"]

_JSON_OBJECT_SCHEMA: dict[str, Any] = {"type": "object", "properties": {}, "additionalProperties": False}
_CATEGORY_ENUM = ["Drafts", "Memos", "Summaries", "Transcripts", "Literature"]


@dataclass(frozen=True)
class AppActionSpec:
    id: str
    label: str
    description: str
    category: str
    shortcut: str | None
    palette_visible: bool
    tool_visible: bool
    safety: AppActionSafety
    input_schema: dict[str, Any] = field(default_factory=lambda: dict(_JSON_OBJECT_SCHEMA))
    result_kind: str = "status"
    textual_action: str | None = None

    @property
    def action_name(self) -> str:
        return self.textual_action or self.id

    @property
    def requires_confirmation(self) -> bool:
        return self.safety == "confirm_required"

    def as_tool_spec(self) -> "ProviderToolSpec":
        return ProviderToolSpec(
            name=self.id,
            description=self.description,
            parameters=self.input_schema,
            safety=self.safety,
            action_id=self.id,
        )


@dataclass(frozen=True)
class AppActionRequest:
    action_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    source: AppActionSource = "system"
    conversation_turn_id: str | None = None
    requires_confirmation: bool = False


@dataclass(frozen=True)
class AppActionResult:
    status: AppActionStatus
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    card: dict[str, Any] | None = None
    audit_metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def provider_safe_text(self) -> str:
        if self.status == "completed":
            prefix = "Completed"
        elif self.status == "pending_confirmation":
            prefix = "Pending user confirmation"
        elif self.status == "refused":
            prefix = "Refused"
        else:
            prefix = "Failed"
        detail = self.message.strip() or self.status
        return f"{prefix}: {detail}"


@dataclass(frozen=True)
class ProviderToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]
    safety: AppActionSafety
    action_id: str


@dataclass(frozen=True)
class ToolCallRequest:
    provider: str
    tool_name: str
    arguments: dict[str, Any]
    raw_call_id: str | None = None
    raw_provider_content: object | None = None

    @property
    def action_id(self) -> str:
        return self.tool_name


@dataclass(frozen=True)
class ToolCallResult:
    request: ToolCallRequest
    action_result: AppActionResult

    @property
    def provider_safe_text(self) -> str:
        return self.action_result.provider_safe_text


def _schema(properties: dict[str, dict[str, Any]], required: tuple[str, ...] = ()) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": list(required),
        "additionalProperties": False,
    }


def _no_input() -> dict[str, Any]:
    return dict(_JSON_OBJECT_SCHEMA)


_ACTION_SPECS: tuple[AppActionSpec, ...] = (
    AppActionSpec(
        "search_documents",
        "Search",
        "Search project documents for a query and show matching snippets.",
        "notebook",
        "ctrl+enter",
        True,
        True,
        "read_only_auto",
        _schema({"query": {"type": "string", "description": "Search query."}}, ("query",)),
        "search_results",
        "terminal_search",
    ),
    AppActionSpec(
        "open_document",
        "Open document",
        "Open a project document by document slug or title.",
        "project",
        None,
        False,
        True,
        "read_only_auto",
        _schema({"document": {"type": "string", "description": "Document slug, title, or location."}}, ("document",)),
        "document",
    ),
    AppActionSpec(
        "open_search_result",
        "Open search result",
        "Open a search result and select the matched text.",
        "notebook",
        None,
        False,
        True,
        "read_only_auto",
        _schema(
            {
                "document_slug": {"type": "string"},
                "start": {"type": "integer"},
                "end": {"type": "integer"},
            },
            ("document_slug", "start", "end"),
        ),
        "document_selection",
    ),
    AppActionSpec(
        "show_context_status",
        "Show context status",
        "Show current document, basket, and notebook context usage.",
        "notebook",
        None,
        False,
        True,
        "read_only_auto",
        _no_input(),
        "context_status",
    ),
    AppActionSpec("focus_project", "Focus project", "Move focus to the project rail.", "navigation", "f1", True, False, "read_only_auto", _no_input(), "status"),
    AppActionSpec("focus_document", "Focus document", "Move focus to the writing viewport.", "navigation", "f2", True, False, "read_only_auto", _no_input(), "status"),
    AppActionSpec("focus_basket", "Focus basket", "Move focus to the context basket.", "navigation", "f3", True, False, "read_only_auto", _no_input(), "status"),
    AppActionSpec("focus_notebook", "Focus notebook", "Move focus to the notebook.", "navigation", "f4", True, False, "read_only_auto", _no_input(), "status", "focus_workflow"),
    AppActionSpec("focus_inspector", "Focus inspector", "Move focus to the inspector.", "navigation", "f5", True, False, "read_only_auto", _no_input(), "status"),
    AppActionSpec(
        "draft_into_document",
        "Draft",
        "Create a new draft proposal for insertion into the active document. If the user asks to write, draft, compose, generate, or add new prose without naming a target, infer the active document as the target. When the user names a document section such as abstract, introduction, findings, or conclusion, set insert_after_heading to that section title so Exegesis inserts the proposal into that existing section instead of appending it. Use this for adding new text such as an abstract, body section, paragraph, or passage.",
        "notebook",
        "ctrl+shift+g",
        True,
        True,
        "proposal_auto",
        _schema(
            {
                "instruction": {"type": "string", "description": "Draft instruction."},
                "insert_after_heading": {
                    "type": "string",
                    "description": "Optional Markdown heading title to insert the draft under in the active document.",
                },
            },
            ("instruction",),
        ),
        "draft_proposal",
        "terminal_draft",
    ),
    AppActionSpec(
        "rewrite_selection",
        "Rewrite",
        "Create a rewrite proposal for selected text or for a named contiguous Markdown section in the active document. If selected text is active and the user says make it shorter/clearer/stronger, revise it, rewrite it, tighten it, or otherwise gives an edit instruction without naming a target, infer the active selection as the target. Use target_heading/section_heading when the user asks to rewrite a section but no text is selected. Return replacement text for only that passage.",
        "notebook",
        "ctrl+shift+w",
        True,
        True,
        "proposal_auto",
        _schema(
            {
                "instruction": {"type": "string", "description": "Rewrite instruction."},
                "target_heading": {
                    "type": "string",
                    "description": "Optional Markdown heading whose body should be rewritten when no text is selected.",
                },
                "section_heading": {
                    "type": "string",
                    "description": "Alias for target_heading.",
                },
            },
            ("instruction",),
        ),
        "rewrite_proposal",
        "terminal_rewrite",
    ),
    AppActionSpec(
        "accept_proposal",
        "Accept proposal",
        "Apply the active notebook draft or rewrite proposal.",
        "notebook",
        "shift+enter",
        True,
        False,
        "system_only",
        _no_input(),
        "document",
        "terminal_accept_proposal",
    ),
    AppActionSpec(
        "reject_proposal",
        "Reject proposal",
        "Reject the active notebook draft or rewrite proposal.",
        "notebook",
        "escape",
        True,
        False,
        "system_only",
        _no_input(),
        "status",
        "terminal_reject_proposal",
    ),
    AppActionSpec(
        "add_excerpt_to_basket",
        "Add excerpt",
        "Add an excerpt to the basket with source-document provenance. Use this only when the user asks to add selected/provided text to the basket or context; do not use it to close, open, rename, or delete documents. If no excerpt is supplied, use the active document selection.",
        "basket",
        "ctrl+shift+e",
        True,
        True,
        "confirm_required",
        _schema(
            {
                "document": {"type": "string", "description": "Source document slug, title, or location."},
                "source_document": {"type": "string", "description": "Alias for document."},
                "document_title": {"type": "string", "description": "Alias for document."},
                "excerpt": {"type": "string", "description": "Excerpt text to preserve in the basket."},
                "quote": {"type": "string", "description": "Alias for excerpt."},
                "passage": {"type": "string", "description": "Alias for excerpt."},
                "selected_text": {"type": "string", "description": "Alias for excerpt."},
                "start": {"type": "integer", "description": "Optional source start character offset."},
                "end": {"type": "integer", "description": "Optional source end character offset."},
            },
            (),
        ),
        "basket",
        "add_excerpt_to_basket",
    ),
    AppActionSpec(
        "add_document_to_basket",
        "Add document",
        "Add a whole project document to the basket/context. Use add_excerpt_to_basket instead when the user provides quoted text, selected text, a passage, a snippet, or transcript excerpt. Do not use it to close, open, rename, or delete documents. If no document is supplied, use the active document.",
        "basket",
        "ctrl+shift+b",
        True,
        True,
        "confirm_required",
        _schema({"document": {"type": "string", "description": "Document slug, title, or location. Defaults to active document."}}, ()),
        "basket",
        "add_file_to_basket",
    ),
    AppActionSpec(
        "save_summary",
        "Save summary",
        "Generate and save a summary of the active document.",
        "inspector",
        None,
        False,
        True,
        "confirm_required",
        _schema({"length": {"type": "string", "enum": ["short", "medium", "long"]}}, ("length",)),
        "document",
    ),
    AppActionSpec("save_transcript", "Save transcript", "Save the active notebook transcript.", "notebook", "ctrl+shift+x", True, True, "confirm_required", _no_input(), "transcript", "terminal_save"),
    AppActionSpec("compact_chat", "Compact chat", "Compact the active notebook chat and save its raw transcript.", "notebook", "ctrl+shift+v", True, True, "confirm_required", _no_input(), "compaction", "terminal_compact"),
    AppActionSpec("start_new_chat_from_compaction", "Start New Chat", "Start a fresh notebook chat from a compaction prompt.", "notebook", None, False, True, "confirm_required", _no_input(), "chat"),
    AppActionSpec("close_chat", "Close chat", "Close the active notebook chat unless it is the main anchor chat.", "notebook", None, True, True, "confirm_required", _no_input(), "chat"),
    AppActionSpec("move_document_to_trash", "Move document to trash", "Move the selected project document to trash.", "project", "delete", True, True, "confirm_required", _no_input(), "trash", "move_selected_project_document_to_trash"),
    AppActionSpec(
        "restore_trash_item",
        "Restore trash item",
        "Restore a document from the project trash. Use this when the user asks to restore or recover a trashed item, including trashed files in subfolders.",
        "project",
        "ctrl+shift+r",
        True,
        True,
        "confirm_required",
        _schema(
            {
                "trash_item": {
                    "type": "string",
                    "description": "Trash item slug, title, filename, or original project path. Defaults to selected trash item.",
                },
                "document": {"type": "string", "description": "Alias for trash_item."},
                "title": {"type": "string", "description": "Alias for trash_item."},
                "filename": {"type": "string", "description": "Alias for trash_item."},
                "duplicate_action": {"type": "string", "enum": ["replace", "rename", "cancel"]},
                "duplicate_title": {"type": "string"},
            },
            (),
        ),
        "document",
        "restore_selected_trash_item",
    ),
    AppActionSpec("show_palette", "Open command palette", "Show Exegesis commands.", "system", "ctrl+p", True, False, "system_only", _no_input(), "status"),
    AppActionSpec(
        "close_document_tab",
        "Close tab",
        "Close the active document tab. Use this for requests like close this/current document. This does not add anything to the basket or context.",
        "document",
        "ctrl+w",
        True,
        True,
        "confirm_required",
        _no_input(),
        "status",
    ),
    AppActionSpec("save_current_document", "Save document", "Save the active document.", "document", "ctrl+s", True, True, "confirm_required", _no_input(), "document"),
    AppActionSpec(
        "rename_project",
        "Rename project",
        "Rename the current project without opening, creating, or deleting other projects.",
        "project",
        None,
        True,
        True,
        "confirm_required",
        _schema(
            {
                "name": {"type": "string", "description": "New current-project display name."},
                "duplicate_action": {"type": "string", "enum": ["replace", "rename", "cancel"]},
                "duplicate_name": {"type": "string", "description": "Alternate name to use when duplicate_action is rename."},
            },
            ("name",),
        ),
        "project",
    ),
    AppActionSpec("new_project", "New Project", "Create a new project folder.", "project", None, True, False, "system_only", _no_input(), "project"),
    AppActionSpec("open_project_browser", "Project Browser", "Open, switch, or delete projects.", "project", None, True, False, "system_only", _no_input(), "project"),
    AppActionSpec("change_projects_directory", "Change projects directory", "Choose where project folders are stored.", "project", None, True, False, "system_only", _no_input(), "settings"),
    AppActionSpec("model_settings", "Model Settings", "Configure provider settings and secure API-key storage.", "system", None, True, False, "system_only", _no_input(), "settings"),
    AppActionSpec("create_draft", "New draft", "Create a new draft document.", "project", "ctrl+shift+d", True, True, "confirm_required", _schema({"title": {"type": "string"}, "folder": {"type": "string", "description": "Optional category-relative destination folder. Omit this when the selected folder is the intended destination."}, "duplicate_action": {"type": "string", "enum": ["replace", "rename", "cancel"]}, "duplicate_title": {"type": "string"}}, ()), "document"),
    AppActionSpec("create_memo", "New memo", "Create a new memo document.", "project", "ctrl+shift+m", True, True, "confirm_required", _schema({"title": {"type": "string"}, "folder": {"type": "string", "description": "Optional category-relative destination folder. Omit this when the selected folder is the intended destination."}, "duplicate_action": {"type": "string", "enum": ["replace", "rename", "cancel"]}, "duplicate_title": {"type": "string"}}, ()), "document"),
    AppActionSpec("create_summary", "New summary", "Create a new summary document.", "project", "ctrl+shift+s", True, True, "confirm_required", _schema({"title": {"type": "string"}, "folder": {"type": "string", "description": "Optional category-relative destination folder. Omit this when the selected folder is the intended destination."}, "duplicate_action": {"type": "string", "enum": ["replace", "rename", "cancel"]}, "duplicate_title": {"type": "string"}}, ()), "document"),
    AppActionSpec("create_transcript", "New transcript", "Create a new transcript document.", "project", "ctrl+shift+t", True, True, "confirm_required", _schema({"title": {"type": "string"}, "folder": {"type": "string", "description": "Optional category-relative destination folder. Omit this when the selected folder is the intended destination."}, "duplicate_action": {"type": "string", "enum": ["replace", "rename", "cancel"]}, "duplicate_title": {"type": "string"}}, ()), "document"),
    AppActionSpec("create_literature", "New literature", "Create a new literature document.", "project", "ctrl+shift+l", True, True, "confirm_required", _schema({"title": {"type": "string"}, "folder": {"type": "string", "description": "Optional category-relative destination folder. Omit this when the selected folder is the intended destination."}, "duplicate_action": {"type": "string", "enum": ["replace", "rename", "cancel"]}, "duplicate_title": {"type": "string"}}, ()), "document"),
    AppActionSpec(
        "create_folder",
        "New folder",
        "Create a folder in a document category.",
        "project",
        "ctrl+shift+f",
        True,
        True,
        "confirm_required",
        _schema(
            {
                "category": {"type": "string", "enum": _CATEGORY_ENUM},
                "name": {"type": "string", "description": "Folder name or category-relative folder path. Do not repeat the selected folder name when the selected folder is the target."},
                "parent_folder": {"type": "string", "description": "Optional category-relative parent folder. Omit this when creating or reusing the selected folder."},
            },
            ("name",),
        ),
        "folder",
    ),
    AppActionSpec(
        "update_selected_project_item",
        "Update item",
        "Rename or move a project document inside its current document category.",
        "project",
        "ctrl+shift+u",
        True,
        True,
        "confirm_required",
        _schema(
            {
                "document": {"type": "string", "description": "Document slug, title, or location. Defaults to the selected document."},
                "title": {"type": "string", "description": "New file name or title."},
                "folder": {"type": "string", "description": "Destination folder inside the same category."},
                "duplicate_action": {"type": "string", "enum": ["replace", "rename", "cancel"]},
                "duplicate_title": {"type": "string"},
            },
            (),
        ),
        "document",
    ),
    AppActionSpec("import_document", "Import", "Import markdown documents.", "project", "ctrl+shift+i", True, False, "system_only", _no_input(), "document"),
    AppActionSpec("import_folder", "Import folder", "Import a folder of markdown documents.", "project", None, False, False, "system_only", _no_input(), "document"),
    AppActionSpec(
        "permanently_delete_trash_item",
        "Permanently delete trash item",
        "Permanently delete or delete forever a trash item while retaining the audit trail. Do not use this to restore or recover trashed items.",
        "project",
        "ctrl+shift+delete",
        True,
        True,
        "confirm_required",
        _schema({"trash_item": {"type": "string", "description": "Trash item slug, title, or original location. Defaults to selected trash item."}}, ()),
        "trash",
        "permanently_delete_selected_trash_item",
    ),
    AppActionSpec("save_short_summary", "Save Short Summary", "Generate and save a roughly 100 word summary.", "inspector", "ctrl+shift+1", True, False, "confirm_required", _no_input(), "document"),
    AppActionSpec("save_medium_summary", "Save Medium Summary", "Generate and save a roughly 500 word summary.", "inspector", "ctrl+shift+2", True, False, "confirm_required", _no_input(), "document"),
    AppActionSpec("save_long_summary", "Save Long Summary", "Generate and save a roughly 1000 word summary.", "inspector", "ctrl+shift+3", True, False, "confirm_required", _no_input(), "document"),
    AppActionSpec("new_chat", "New Chat", "Create a new notebook chat.", "notebook", "ctrl+shift+n", True, False, "confirm_required", _no_input(), "chat", "terminal_new_chat"),
    AppActionSpec("restart_exegesis", "Restart Exegesis", "Save documents and restart the shell.", "system", "ctrl+r", True, False, "system_only", _no_input(), "status"),
    AppActionSpec("quit", "Quit", "Save documents and quit Exegesis.", "system", "ctrl+q", True, False, "system_only", _no_input(), "status"),
)


def app_action_specs(*, include_local_developer: bool = False) -> tuple[AppActionSpec, ...]:
    if include_local_developer:
        return _ACTION_SPECS
    return tuple(spec for spec in _ACTION_SPECS if spec.id != "restart_exegesis")


def app_action_registry(*, include_local_developer: bool = False) -> dict[str, AppActionSpec]:
    return {spec.id: spec for spec in app_action_specs(include_local_developer=include_local_developer)}


def get_app_action_spec(action_id: str, *, include_local_developer: bool = False) -> AppActionSpec:
    try:
        return app_action_registry(include_local_developer=include_local_developer)[action_id]
    except KeyError as exc:
        raise KeyError(f"Unknown app action: {action_id}") from exc


def palette_action_specs(*, include_local_developer: bool = False) -> tuple[AppActionSpec, ...]:
    return tuple(spec for spec in app_action_specs(include_local_developer=include_local_developer) if spec.palette_visible)


def tool_action_specs() -> tuple[AppActionSpec, ...]:
    return tuple(spec for spec in _ACTION_SPECS if spec.tool_visible)


def provider_tool_specs() -> tuple[ProviderToolSpec, ...]:
    return tuple(spec.as_tool_spec() for spec in tool_action_specs())


def validate_app_action_registry(specs: tuple[AppActionSpec, ...] | None = None) -> None:
    specs = specs or _ACTION_SPECS
    ids: set[str] = set()
    shortcuts: set[str] = set()
    for spec in specs:
        if not spec.id or spec.id.strip() != spec.id:
            raise ValueError(f"Invalid action id: {spec.id!r}")
        if spec.id in ids:
            raise ValueError(f"Duplicate app action id: {spec.id}")
        ids.add(spec.id)
        if not spec.label.strip():
            raise ValueError(f"Action {spec.id} must have a label")
        if not spec.description.strip():
            raise ValueError(f"Action {spec.id} must have a description")
        if spec.shortcut:
            shortcut = spec.shortcut.casefold()
            if shortcut in shortcuts:
                raise ValueError(f"Duplicate app action shortcut: {spec.shortcut}")
            shortcuts.add(shortcut)
        schema = spec.input_schema
        if schema.get("type") != "object" or not isinstance(schema.get("properties"), dict):
            raise ValueError(f"Action {spec.id} input_schema must be a JSON object schema")
        if spec.tool_visible and spec.safety == "system_only":
            raise ValueError(f"System-only action cannot be tool-visible: {spec.id}")


validate_app_action_registry()


__all__ = [
    "AppActionRequest",
    "AppActionResult",
    "AppActionSafety",
    "AppActionSource",
    "AppActionSpec",
    "ProviderToolSpec",
    "ToolCallRequest",
    "ToolCallResult",
    "app_action_registry",
    "app_action_specs",
    "get_app_action_spec",
    "palette_action_specs",
    "provider_tool_specs",
    "tool_action_specs",
    "validate_app_action_registry",
]
