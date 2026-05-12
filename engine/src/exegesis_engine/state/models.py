from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from exegesis_shared.models.selection import Selection


@dataclass(frozen=True)
class ProjectItem:
    id: str
    label: str
    item_type: str
    path: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BasketItem:
    id: str
    item_type: str
    label: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkflowCard:
    id: str
    card_type: str
    title: str
    body: str
    metadata: dict[str, Any] = field(default_factory=dict)
    actions: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class DocumentSelection:
    start: int
    end: int
    selected_text: str = ""


@dataclass
class ProjectState:
    current_project_id_or_path: str | None = None
    project_items: list[ProjectItem] = field(default_factory=list)
    open_document_id: str | None = None
    sessions: list[ProjectItem] = field(default_factory=list)


@dataclass
class DocumentState:
    current_document_id: str | None = None
    current_document_content: str = ""
    dirty: bool = False
    current_selection: DocumentSelection | None = None


@dataclass
class WorkflowState:
    cards: list[WorkflowCard] = field(default_factory=list)
    focused_card_id: str | None = None
    command_history: list[str] = field(default_factory=list)
    last_action_status: str | None = None


@dataclass
class BasketState:
    items: list[BasketItem] = field(default_factory=list)
    selected_basket_item_id: str | None = None


@dataclass
class InspectorState:
    current_inspected_object_type: str | None = None
    current_inspected_object_id: str | None = None
    current_payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class UIState:
    focused_pane: str = "project"
    command_palette_open: bool = False
    transient_modal: str | None = None


@dataclass
class AppState:
    project: ProjectState = field(default_factory=ProjectState)
    document: DocumentState = field(default_factory=DocumentState)
    workflow: WorkflowState = field(default_factory=WorkflowState)
    basket: BasketState = field(default_factory=BasketState)
    inspector: InspectorState = field(default_factory=InspectorState)
    ui: UIState = field(default_factory=UIState)
    current_selection: Selection | None = None
