from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from exegesis_engine.context.basket import ContextBasket
    from exegesis_engine.drafting.service import DraftingService
    from exegesis_engine.metrics import MetricsDB, MetricsExporter, MetricsRecorder, UsageIntegrityService
    from exegesis_engine.retrieval.search_service import RetrievalConstraints, RetrievalQuery, RetrievalService
    from exegesis_engine.storage.project_store import ProjectStore
    from exegesis_engine.storage.vault import VaultService, VaultState

from exegesis_engine.patches.patch_model import PatchProposal
from exegesis_engine.patches.patch_service import PatchService
from exegesis_engine.state.models import (
    AppState,
    BasketItem,
    BasketState,
    DocumentSelection,
    DocumentState,
    InspectorState,
    ProjectItem,
    ProjectState,
    WorkflowActionRecord,
    WorkflowCard,
)
from exegesis_engine.workflow.plan_service import PlanService
from exegesis_engine.workflow.revise_service import ReviseService
from exegesis_shared.models.selection import Selection
from exegesis_engine.audit.event_log import AuditEvent, AuditLog

PatchDecision = Literal["accepted", "rejected"]

_DOCUMENT_CATEGORY_DIRS = {
    "Drafts": "drafts",
    "Memos": "memos",
    "Summaries": "summaries",
    "Transcripts": "transcripts",
    "Literature": "literature",
}


@dataclass
class EngineRuntime:
    vault: VaultState
    basket: ContextBasket
    drafting: DraftingService
    metrics: MetricsRecorder
    usage_integrity: UsageIntegrityService
    metrics_exporter: MetricsExporter


@dataclass(frozen=True)
class PatchResolution:
    patch_id: str
    decision: PatchDecision
    target_document_id: str
    document_content: str
    dirty: bool
    persisted: bool
    metadata: dict[str, object]
    continuation_document_id: str | None = None
    continuation_document_content: str = ""

    @property
    def current_document_content(self) -> str:
        if self.continuation_document_id is not None:
            return self.continuation_document_content
        return self.document_content


@dataclass(frozen=True)
class PatchResolutionSnapshot:
    resolution: PatchResolution
    session: ProjectItem


@dataclass(frozen=True)
class PatchPreviewResolutionSnapshot:
    preview: PatchPreview
    resolution: PatchResolution
    session: ProjectItem


@dataclass(frozen=True)
class PatchPreview:
    patch_id: str
    target_document_id: str
    target_range: tuple[int, int]
    original_text: str
    proposed_text: str
    preview_text: str
    metadata: dict[str, object]
    result_document_content: str | None = None
    can_apply: bool = False
    status: str = "stale"


class EngineService:
    """Existing bootstrap/runtime service preserved under the canonical package path."""

    def __init__(self) -> None:
        pass

    def bootstrap(self, *, app_data_dir: Path, project_name: str) -> EngineRuntime:
        from exegesis_engine.context.store import ContextBasketStore
        from exegesis_engine.drafting.service import DraftingService
        from exegesis_engine.metrics import MetricsDB, MetricsExporter, MetricsRecorder, UsageIntegrityService
        from exegesis_engine.storage.vault import VaultService
        vault = VaultService().create_or_open(app_data_dir, project_name)
        basket_store = ContextBasketStore(vault.root_dir)
        basket = basket_store.load()
        original_item_ids = list(basket.item_ids)
        sanitized = self._sanitize_item_ids(original_item_ids)
        basket.item_ids = sanitized
        if sanitized != original_item_ids:
            basket_store.save(basket)
        metrics_db = MetricsDB(vault.root_dir)
        return EngineRuntime(
            vault=vault,
            basket=basket,
            drafting=DraftingService(),
            metrics=MetricsRecorder(metrics_db),
            usage_integrity=UsageIntegrityService(metrics_db),
            metrics_exporter=MetricsExporter(metrics_db),
        )

    @staticmethod
    def _sanitize_item_ids(values: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for raw in values:
            normalized = raw.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            cleaned.append(normalized)
        return cleaned


class ExegesisAppService:
    """Engine-facing MVP contract for the future Textual client and current CLI shims."""

    def __init__(self, *, project_store: ProjectStore | None = None) -> None:
        self.state = AppState()
        self._project_store = project_store
        self._plan_service = PlanService()
        self._revise_service = ReviseService()
        self._patch_service = PatchService()
        self._retrieval_service: RetrievalService | None = None
        self._audit_log: AuditLog | None = None
        self._pending_patches: dict[str, PatchProposal] = {}
        self._resolved_patches: dict[str, PatchResolution] = {}

    def _ensure_project_open(self) -> None:
        if self.state.project.current_project_id_or_path is None:
            raise RuntimeError("Project must be opened before performing workflow actions")

    @staticmethod
    def _validate_metadata(metadata: dict[str, object] | None) -> None:
        if metadata is None:
            return
        if not isinstance(metadata, dict):
            raise TypeError("metadata must be a dictionary or None")
        for key in metadata:
            if not isinstance(key, str):
                raise TypeError("metadata keys must be string types")

    def open_project(self, project_path: str | Path) -> ProjectState:
        if not isinstance(project_path, (str, Path)):
            raise TypeError("project_path must be a string or Path")
        if isinstance(project_path, str):
            if not project_path.strip():
                raise ValueError("project_path cannot be empty or whitespace only")
            if "\x00" in project_path:
                raise ValueError("project_path cannot contain null bytes")
        root = Path(project_path)
        self._audit_log = AuditLog(root)
        from exegesis_engine.storage.project_store import ProjectStore
        self._project_store = ProjectStore(root)
        project_items = [self._with_project_metadata(item, project_id=str(root)) for item in self._project_store.list_project_items()]
        from exegesis_engine.retrieval.search_service import RetrievalService
        self._retrieval_service = RetrievalService(root, audit_log=self._audit_log)
        for item in project_items:
            path = Path(item.path)
            if not path.exists() or not path.is_file():
                continue
            self._retrieval_service.add_or_update_document(
                doc_id=item.id,
                doc_type=self._doc_type_for_item(item),
                title_hint=item.label,
                text=path.read_text(encoding="utf-8"),
            )
        self.state.project = ProjectState(
            current_project_id_or_path=str(root),
            project_items=[item for item in project_items if item.item_type == "document"],
            open_document_id=self.state.project.open_document_id,
            sessions=[item for item in project_items if item.item_type == "session"],
        )
        self._record_audit_event(
            "project.opened",
            {"project_path": str(root), "document_count": len(self.state.project.project_items)},
        )
        return self.state.project

    def list_project_items(self) -> list[ProjectItem]:
        if self._project_store is None:
            return []
        existing_session_metadata = {
            item.id: dict(item.metadata)
            for item in self.state.project.sessions
            if item.metadata
        }
        items = [self._with_project_metadata(item) for item in self._project_store.list_project_items()]
        self.state.project.project_items = [item for item in items if item.item_type == "document"]
        self.state.project.sessions = [
            ProjectItem(
                id=item.id,
                label=item.label,
                item_type=item.item_type,
                path=item.path,
                metadata=existing_session_metadata.get(item.id, item.metadata),
            )
            for item in items
            if item.item_type == "session"
        ]
        return items

    def _with_project_metadata(self, item: ProjectItem, project_id: str | None = None) -> ProjectItem:
        project_id = project_id or self.state.project.current_project_id_or_path
        metadata = dict(item.metadata)
        if project_id is not None:
            metadata.setdefault("project_id_or_path", project_id)
        return ProjectItem(
            id=item.id,
            label=item.label,
            item_type=item.item_type,
            path=item.path,
            metadata=metadata,
        )

    def open_document(self, document_id: str) -> DocumentState:
        if not isinstance(document_id, str):
            raise TypeError("document_id must be a string")
        if not document_id.strip():
            raise ValueError("document_id cannot be empty or whitespace only")
        if "\x00" in document_id:
            raise ValueError("document_id cannot contain null bytes")
        if self._project_store is None:
            project_path = self.state.project.current_project_id_or_path
            if project_path is None:
                raise RuntimeError("Project must be opened before documents can be loaded")
            doc_path = (
                Path(document_id)
                if Path(document_id).is_absolute()
                else (Path(project_path) / document_id).resolve()
            )
            content = doc_path.read_text(encoding="utf-8")
        else:
            _, content = self._project_store.read_document(document_id)
        self.state.project.open_document_id = document_id
        self.state.document = DocumentState(
            current_document_id=document_id,
            current_document_content=content,
            dirty=False,
            current_selection=None,
        )
        self._record_audit_event(
            "document.opened",
            {"doc_id": document_id, "content_length": len(content)},
        )
        return self.state.document

    def save_document(self, content: str | None = None) -> DocumentState:
        if content is not None:
            if not isinstance(content, str):
                raise TypeError("content must be a string or None")
            if "\x00" in content:
                raise ValueError("content cannot contain null bytes")
        if self.state.document.current_document_id is None:
            raise RuntimeError("Document must be opened before saving")
        if content is not None:
            self.state.document.current_document_content = content
        doc_id = self.state.document.current_document_id
        doc_content = self.state.document.current_document_content
        if self._project_store is not None:
            self._project_store.write_document(doc_id, doc_content)
        else:
            doc_path = (
                Path(doc_id)
                if Path(doc_id).is_absolute()
                else Path(doc_id).resolve()
            )
            doc_path.write_text(doc_content, encoding="utf-8")
        self.state.document.dirty = False
        if self._retrieval_service is not None:
            self._retrieval_service.add_or_update_document(
                doc_id=doc_id,
                doc_type=self._doc_type_for_path(doc_id),
                text=doc_content,
            )
        self._record_audit_event(
            "document.saved",
            {"doc_id": doc_id, "content_length": len(doc_content)},
        )
        return self.state.document

    def create_document(
        self,
        *,
        category: str,
        title: str,
        content: str,
        document_type: str,
        relative_path: str | None = None,
    ) -> ProjectItem:
        self._ensure_project_open()
        if self._project_store is None:
            raise RuntimeError("Project store is required before creating documents")
        self._validate_document_lifecycle_inputs(category=category, title=title, content=content, document_type=document_type)
        target_path = relative_path or self._deduped_category_document_path(category, title)
        item = self._project_store.create_document(target_path, content)
        project_item = ProjectItem(
            id=item.id,
            label=item.label,
            item_type=item.item_type,
            path=item.path,
            metadata={"category": category, "document_type": document_type},
        )
        self.list_project_items()
        self._index_document_item(project_item, content)
        self._record_audit_event(
            "document.created",
            {"doc_id": project_item.id, "category": category, "document_type": document_type, "content_length": len(content)},
        )
        return project_item

    def import_markdown_document(
        self,
        *,
        source_path: str | Path,
        category: str,
        relative_path: str | None = None,
    ) -> ProjectItem:
        self._ensure_project_open()
        if self._project_store is None:
            raise RuntimeError("Project store is required before importing documents")
        source = Path(source_path).expanduser()
        if source.suffix.lower() not in {".md", ".markdown", ".mdown"}:
            raise ValueError("only markdown files can be imported")
        title = source.name
        target_path = relative_path or self._deduped_category_document_path(category, title)
        item = self._project_store.import_document(source, target_path)
        content = Path(item.path).read_text(encoding="utf-8")
        project_item = ProjectItem(
            id=item.id,
            label=item.label,
            item_type=item.item_type,
            path=item.path,
            metadata={"category": category, "document_type": self._category_document_type(category), "source_path": str(source)},
        )
        self.list_project_items()
        self._index_document_item(project_item, content)
        self._record_audit_event(
            "document.imported",
            {"doc_id": project_item.id, "category": category, "source_path": str(source), "content_length": len(content)},
        )
        return project_item

    def move_document(self, document_id: str, new_relative_path: str) -> ProjectItem:
        self._ensure_project_open()
        if self._project_store is None:
            raise RuntimeError("Project store is required before moving documents")
        item = self._project_store.rename_document(document_id, new_relative_path)
        content = Path(item.path).read_text(encoding="utf-8")
        project_item = ProjectItem(id=item.id, label=item.label, item_type=item.item_type, path=item.path)
        if self.state.document.current_document_id == document_id:
            self.state.document.current_document_id = project_item.id
            self.state.document.current_document_content = content
        self.list_project_items()
        self._index_document_item(project_item, content)
        self._record_audit_event("document.moved", {"old_doc_id": document_id, "new_doc_id": project_item.id})
        return project_item

    def rename_document(self, document_id: str, new_title: str) -> ProjectItem:
        self._ensure_project_open()
        if self._project_store is None:
            raise RuntimeError("Project store is required before renaming documents")
        if not isinstance(new_title, str) or not new_title.strip():
            raise ValueError("new_title is required")
        current = Path(document_id)
        new_filename = self._safe_document_filename(
            new_title,
            default_stem=current.stem or "document",
            allow_extensionless=True,
        )
        new_relative_path = str(Path(*current.parts[:-1]) / new_filename) if len(current.parts) > 1 else new_filename
        item = self._project_store.rename_document(document_id, new_relative_path)
        content = Path(item.path).read_text(encoding="utf-8")
        project_item = ProjectItem(id=item.id, label=item.label, item_type=item.item_type, path=item.path)
        if self.state.document.current_document_id == document_id:
            self.state.document.current_document_id = project_item.id
            self.state.document.current_document_content = content
        self.list_project_items()
        self._index_document_item(project_item, content)
        self._record_audit_event("document.renamed", {"old_doc_id": document_id, "new_doc_id": project_item.id})
        return project_item

    def delete_document(self, document_id: str) -> ProjectItem:
        self._ensure_project_open()
        if self._project_store is None:
            raise RuntimeError("Project store is required before deleting documents")
        item = self._project_store.trash_document(document_id)
        trashed_item = ProjectItem(
            id=item.id,
            label=item.label,
            item_type=item.item_type,
            path=item.path,
            metadata=dict(item.metadata),
        )
        if self.state.project.open_document_id == document_id:
            self.state.project.open_document_id = None
        if self.state.document.current_document_id == document_id:
            self.state.document = DocumentState()
        self.list_project_items()
        self._record_audit_event("document.deleted", {"doc_id": document_id, "trash_path": trashed_item.path})
        return trashed_item

    def list_trash_items(self) -> list[ProjectItem]:
        self._ensure_project_open()
        if self._project_store is None:
            raise RuntimeError("Project store is required before listing trash")
        return [
            ProjectItem(
                id=item.id,
                label=item.label,
                item_type=item.item_type,
                path=item.path,
                metadata=dict(item.metadata),
            )
            for item in self._project_store.list_trash_items()
        ]

    def open_trash_document(self, trash_id: str) -> DocumentState:
        self._ensure_project_open()
        if self._project_store is None:
            raise RuntimeError("Project store is required before opening trash")
        _path, content, _metadata = self._project_store.read_trash_document(trash_id)
        self.state.document = DocumentState(
            current_document_id=trash_id,
            current_document_content=content,
            dirty=False,
        )
        return self.state.document

    def restore_trash_document(self, trash_id: str) -> ProjectItem:
        self._ensure_project_open()
        if self._project_store is None:
            raise RuntimeError("Project store is required before restoring trash")
        item = self._project_store.restore_trash_document(trash_id)
        content = Path(item.path).read_text(encoding="utf-8")
        project_item = ProjectItem(id=item.id, label=item.label, item_type=item.item_type, path=item.path)
        self.list_project_items()
        self._index_document_item(project_item, content)
        self._record_audit_event("document.restored", {"trash_id": trash_id, "doc_id": project_item.id})
        return project_item

    def restore_trash_document_as(self, trash_id: str, new_title: str) -> ProjectItem:
        self._ensure_project_open()
        if self._project_store is None:
            raise RuntimeError("Project store is required before restoring trash")
        trash_item = next((item for item in self._project_store.list_trash_items() if item.id == trash_id), None)
        if trash_item is None:
            raise FileNotFoundError(f"trashed document does not exist: {trash_id!r}")
        original_id = str(trash_item.metadata.get("original_id") or "")
        if not original_id:
            raise ValueError(f"trashed document has no restore target: {trash_id!r}")
        original_path = Path(original_id)
        filename = self._safe_document_filename(new_title, default_stem=original_path.stem or "document")
        if not Path(filename).suffix and original_path.suffix:
            filename = f"{filename}{original_path.suffix}"
        new_relative_path = str(Path(*original_path.parts[:-1]) / filename) if len(original_path.parts) > 1 else filename
        item = self._project_store.restore_trash_document_as(trash_id, new_relative_path)
        content = Path(item.path).read_text(encoding="utf-8")
        project_item = ProjectItem(id=item.id, label=item.label, item_type=item.item_type, path=item.path)
        self.list_project_items()
        self._index_document_item(project_item, content)
        self._record_audit_event(
            "document.restored",
            {"trash_id": trash_id, "doc_id": project_item.id, "restore_mode": "rename"},
        )
        return project_item

    def permanently_delete_trash_document(self, trash_id: str) -> ProjectItem:
        self._ensure_project_open()
        if self._project_store is None:
            raise RuntimeError("Project store is required before permanently deleting trash")
        item = self._project_store.permanently_delete_trash_document(trash_id)
        deleted_item = ProjectItem(
            id=item.id,
            label=item.label,
            item_type=item.item_type,
            path=item.path,
            metadata=dict(item.metadata),
        )
        self._record_audit_event(
            "document.permanently_deleted",
            {
                "trash_id": trash_id,
                "original_id": deleted_item.metadata.get("original_id", ""),
                "label": deleted_item.label,
            },
        )
        return deleted_item

    def add_basket_item(self, item_id: str, *, item_type: str = "excerpt", label: str | None = None, payload: dict[str, object] | None = None) -> BasketState:
        if not isinstance(item_id, str):
            raise TypeError("item_id must be a string")
        if not item_id.strip():
            raise ValueError("item_id cannot be empty or whitespace only")
        if "\x00" in item_id:
            raise ValueError("item_id cannot contain null bytes")
        if not isinstance(item_type, str):
            raise TypeError("item_type must be a string")
        if not item_type.strip():
            raise ValueError("item_type cannot be empty or whitespace only")
        if "\x00" in item_type:
            raise ValueError("item_type cannot contain null bytes")
        if label is not None:
            if not isinstance(label, str):
                raise TypeError("label must be a string or None")
            if not label.strip():
                raise ValueError("label cannot be empty or whitespace only")
            if "\x00" in label:
                raise ValueError("label cannot contain null bytes")
        if payload is not None and not isinstance(payload, dict):
            raise TypeError("payload must be a dictionary or None")
        item = BasketItem(id=item_id, item_type=item_type, label=label or item_id, payload=dict(payload or {}))
        if all(existing.id != item.id for existing in self.state.basket.items):
            self.state.basket.items.append(item)
        self.state.basket.selected_basket_item_id = item.id
        self._record_audit_event(
            "basket.item_added",
            {"item_id": item.id, "item_type": item.item_type, "basket_size": len(self.state.basket.items)},
        )
        return self.state.basket

    def remove_basket_item(self, item_id: str) -> BasketState:
        if not isinstance(item_id, str):
            raise TypeError("item_id must be a string")
        if not item_id.strip():
            raise ValueError("item_id cannot be empty or whitespace only")
        if "\x00" in item_id:
            raise ValueError("item_id cannot contain null bytes")
        self.state.basket.items = [item for item in self.state.basket.items if item.id != item_id]
        if self.state.basket.selected_basket_item_id == item_id:
            self.state.basket.selected_basket_item_id = self.state.basket.items[0].id if self.state.basket.items else None
        self._record_audit_event(
            "basket.item_removed",
            {"item_id": item_id, "basket_size": len(self.state.basket.items)},
        )
        return self.state.basket

    def clear_basket(self) -> BasketState:
        prev_size = len(self.state.basket.items)
        self.state.basket = BasketState()
        self._record_audit_event(
            "basket.cleared",
            {"cleared_item_count": prev_size},
        )
        return self.state.basket

    def set_current_selection(self, *, selection_type: str, selection_id: str, source_pane: str, payload: dict[str, object] | None = None) -> Selection:
        if not isinstance(selection_type, str):
            raise TypeError("selection_type must be a string")
        if not selection_type.strip():
            raise ValueError("selection_type cannot be empty or whitespace only")
        if "\x00" in selection_type:
            raise ValueError("selection_type cannot contain null bytes")
        if not isinstance(selection_id, str):
            raise TypeError("selection_id must be a string")
        if not selection_id.strip():
            raise ValueError("selection_id cannot be empty or whitespace only")
        if "\x00" in selection_id:
            raise ValueError("selection_id cannot contain null bytes")
        if not isinstance(source_pane, str):
            raise TypeError("source_pane must be a string")
        if not source_pane.strip():
            raise ValueError("source_pane cannot be empty or whitespace only")
        if "\x00" in source_pane:
            raise ValueError("source_pane cannot contain null bytes")
        if payload is not None and not isinstance(payload, dict):
            raise TypeError("payload must be a dictionary or None")
        selection = Selection(type=selection_type, id=selection_id, source_pane=source_pane, payload=dict(payload or {}))
        self.state.current_selection = selection
        self.state.inspector = InspectorState(
            current_inspected_object_type=selection.type,
            current_inspected_object_id=selection.id,
            current_payload=dict(selection.payload),
        )
        return selection

    def search_project(self, query_text: str, *, max_results: int = 10):
        if not isinstance(query_text, str):
            raise TypeError("query_text must be a string")
        if not query_text.strip():
            raise ValueError("query_text cannot be empty or whitespace only")
        if "\x00" in query_text:
            raise ValueError("query_text cannot contain null bytes")
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise TypeError("max_results must be an integer")
        return self._search(query_text=query_text, scope="vault", max_results=max_results)

    def search_memos(self, query_text: str, *, max_results: int = 10):
        if not isinstance(query_text, str):
            raise TypeError("query_text must be a string")
        if not query_text.strip():
            raise ValueError("query_text cannot be empty or whitespace only")
        if "\x00" in query_text:
            raise ValueError("query_text cannot contain null bytes")
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise TypeError("max_results must be an integer")
        return self._search(query_text=query_text, scope="vault", max_results=max_results, doc_types=("memo",))

    def search_literature(self, query_text: str, *, max_results: int = 10):
        if not isinstance(query_text, str):
            raise TypeError("query_text must be a string")
        if not query_text.strip():
            raise ValueError("query_text cannot be empty or whitespace only")
        if "\x00" in query_text:
            raise ValueError("query_text cannot contain null bytes")
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise TypeError("max_results must be an integer")
        return self._search(query_text=query_text, scope="vault", max_results=max_results, doc_types=("pdf", "paper", "literature"))

    def plan_from_basket(self, *, metadata: dict[str, object] | None = None) -> WorkflowCard:
        self._validate_metadata(metadata)
        self._ensure_project_open()
        context_snippets = self._gather_basket_snippets()
        card = self._plan_service.plan_from_basket(
            self.state.basket.items,
            context_snippets=context_snippets,
            prior_context_summary=self.state.workflow.compacted_context_summary,
            metadata=metadata,
        )
        self._remember_workflow_card(card)
        self.state.workflow.last_plan_card_id = card.id
        snippet_count = sum(len(v) for v in context_snippets.values())
        request_data = {
            "basket_item_ids": [item.id for item in self.state.basket.items],
            "basket_item_count": len(self.state.basket.items),
        }
        if self.state.project.current_project_id_or_path is not None:
            request_data["project_id_or_path"] = str(self.state.project.current_project_id_or_path)
        request_data.update(self._last_patch_continuation_metadata())
        if self.state.document.current_document_id is not None:
            request_data["document_id"] = self.state.document.current_document_id
        if metadata is not None:
            request_data.update(metadata)
        self._record_workflow_action(
            action="plan_from_basket",
            request=request_data,
            result={
                "card_id": card.id,
                "card_type": card.card_type,
                "title": card.title,
                "snippet_count": snippet_count,
            },
        )
        audit_payload = {
            "basket_item_ids": [item.id for item in self.state.basket.items],
            "basket_item_count": len(self.state.basket.items),
            "card_id": card.id,
            "snippet_count": snippet_count,
        }
        if self.state.project.current_project_id_or_path is not None:
            audit_payload["project_id_or_path"] = str(self.state.project.current_project_id_or_path)
        audit_payload.update(self._last_patch_continuation_metadata())
        if self.state.document.current_document_id is not None:
            audit_payload["document_id"] = self.state.document.current_document_id
        if metadata is not None:
            audit_payload.update(metadata)
        self._record_audit_event(
            "workflow.plan_from_basket",
            audit_payload,
        )
        return card

    def draft_from_basket(self, *, metadata: dict[str, object] | None = None) -> WorkflowCard:
        self._validate_metadata(metadata)
        self._ensure_project_open()
        context_snippets = self._gather_basket_snippets()
        card = self._revise_service.draft_from_basket(
            self.state.basket.items,
            context_snippets=context_snippets,
            prior_context_summary=self.state.workflow.compacted_context_summary,
            metadata=metadata,
        )
        self._remember_workflow_card(card)
        self.state.workflow.last_plan_card_id = card.id
        snippet_count = sum(len(v) for v in context_snippets.values())
        request_data = {
            "basket_item_ids": [item.id for item in self.state.basket.items],
            "basket_item_count": len(self.state.basket.items),
        }
        if self.state.project.current_project_id_or_path is not None:
            request_data["project_id_or_path"] = str(self.state.project.current_project_id_or_path)
        request_data.update(self._last_patch_continuation_metadata())
        if self.state.document.current_document_id is not None:
            request_data["document_id"] = self.state.document.current_document_id
        if metadata is not None:
            request_data.update(metadata)
        self._record_workflow_action(
            action="draft_from_basket",
            request=request_data,
            result={
                "card_id": card.id,
                "card_type": card.card_type,
                "title": card.title,
                "snippet_count": snippet_count,
            },
        )
        audit_payload = {
            "basket_item_ids": [item.id for item in self.state.basket.items],
            "basket_item_count": len(self.state.basket.items),
            "card_id": card.id,
            "snippet_count": snippet_count,
        }
        if self.state.project.current_project_id_or_path is not None:
            audit_payload["project_id_or_path"] = str(self.state.project.current_project_id_or_path)
        audit_payload.update(self._last_patch_continuation_metadata())
        if self.state.document.current_document_id is not None:
            audit_payload["document_id"] = self.state.document.current_document_id
        if metadata is not None:
            audit_payload.update(metadata)
        self._record_audit_event(
            "workflow.draft_from_basket",
            audit_payload,
        )
        return card

    def revise_selection(self, *, proposed_text: str, metadata: dict[str, object] | None = None) -> PatchProposal:
        if isinstance(proposed_text, str) and "\x00" in proposed_text:
            raise ValueError("proposed_text cannot contain null bytes")
        self._validate_metadata(metadata)
        self._ensure_project_open()
        document = self.state.document
        if document.current_document_id is None or document.current_selection is None:
            raise RuntimeError("Document selection is required before revising")
        selection = document.current_selection
        plan_card_id = self.state.workflow.last_plan_card_id
        revise_meta: dict[str, object] = {"source": "revise_selection"}
        if plan_card_id is not None:
            revise_meta["plan_card_id"] = plan_card_id
        revise_meta.update(self._last_patch_continuation_metadata())
        if metadata is not None:
            revise_meta.update(metadata)
        patch, preview = self._revise_service.revise_selection(
            document_id=document.current_document_id,
            original_text=selection.selected_text,
            proposed_text=proposed_text,
            target_range=(selection.start, selection.end),
            metadata=revise_meta,
        )
        self._pending_patches[patch.patch_id] = patch
        self._remember_workflow_card(
            WorkflowCard(
                id=patch.patch_id,
                card_type="patch",
                title="Revision Proposal",
                body=preview or proposed_text,
                metadata={"document_id": document.current_document_id},
                actions=[
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": patch.patch_id}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": patch.patch_id}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": patch.patch_id}},
                ],
            )
        )
        request_data = {
            "document_id": document.current_document_id,
            "target_range": [selection.start, selection.end],
            "original_text": selection.selected_text,
            "proposed_text": proposed_text,
        }
        if self.state.project.current_project_id_or_path is not None:
            request_data["project_id_or_path"] = str(self.state.project.current_project_id_or_path)
        request_data.update(self._last_patch_continuation_metadata())
        if metadata is not None:
            request_data.update(metadata)
        self._record_workflow_action(
            action="revise_selection",
            request=request_data,
            result={
                "patch_id": patch.patch_id,
                "preview_text": preview or proposed_text,
            },
        )
        revise_audit: dict[str, object] = {
            "patch_id": patch.patch_id,
            "document_id": document.current_document_id,
            "original_text": selection.selected_text,
            "proposed_text": proposed_text,
            "target_range": [selection.start, selection.end],
        }
        if plan_card_id is not None:
            revise_audit["plan_card_id"] = plan_card_id
        if self.state.project.current_project_id_or_path is not None:
            revise_audit["project_id_or_path"] = str(self.state.project.current_project_id_or_path)
        revise_audit.update(self._last_patch_continuation_metadata())
        if metadata is not None:
            revise_audit.update(metadata)
        self._record_audit_event("workflow.revise_selection", revise_audit)
        return patch

    def revise_from_basket(self, *, proposed_text: str, metadata: dict[str, object] | None = None) -> PatchProposal:
        if isinstance(proposed_text, str) and "\x00" in proposed_text:
            raise ValueError("proposed_text cannot contain null bytes")
        self._validate_metadata(metadata)
        self._ensure_project_open()
        document = self.state.document
        if document.current_document_id is None or document.current_selection is None:
            raise RuntimeError("Document selection is required before revising")
        selection = document.current_selection
        context_snippets = self._gather_basket_snippets()
        snippet_count = sum(len(v) for v in context_snippets.values())
        basket_item_ids = [item.id for item in self.state.basket.items]
        plan_card_id = self.state.workflow.last_plan_card_id
        from_basket_meta: dict[str, object] = {
            "source": "revise_from_basket",
            "basket_item_ids": basket_item_ids,
            "basket_item_count": len(basket_item_ids),
            "snippet_count": snippet_count,
        }
        if plan_card_id is not None:
            from_basket_meta["plan_card_id"] = plan_card_id
        from_basket_meta.update(self._last_patch_continuation_metadata())
        if metadata is not None:
            from_basket_meta.update(metadata)
        patch, preview = self._revise_service.revise_selection(
            document_id=document.current_document_id,
            original_text=selection.selected_text,
            proposed_text=proposed_text,
            target_range=(selection.start, selection.end),
            metadata=from_basket_meta,
        )
        self._pending_patches[patch.patch_id] = patch
        self._remember_workflow_card(
            WorkflowCard(
                id=patch.patch_id,
                card_type="patch",
                title="Revision From Basket",
                body=preview or proposed_text,
                metadata={"document_id": document.current_document_id},
                actions=[
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": patch.patch_id}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": patch.patch_id}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": patch.patch_id}},
                ],
            )
        )
        request_data = {
            "document_id": document.current_document_id,
            "target_range": [selection.start, selection.end],
            "original_text": selection.selected_text,
            "proposed_text": proposed_text,
            "basket_item_ids": basket_item_ids,
            "basket_item_count": len(basket_item_ids),
        }
        if self.state.project.current_project_id_or_path is not None:
            request_data["project_id_or_path"] = str(self.state.project.current_project_id_or_path)
        request_data.update(self._last_patch_continuation_metadata())
        if metadata is not None:
            request_data.update(metadata)
        self._record_workflow_action(
            action="revise_from_basket",
            request=request_data,
            result={
                "patch_id": patch.patch_id,
                "preview_text": preview or proposed_text,
                "snippet_count": snippet_count,
            },
        )
        from_basket_audit: dict[str, object] = {
            "patch_id": patch.patch_id,
            "document_id": document.current_document_id,
            "original_text": selection.selected_text,
            "proposed_text": proposed_text,
            "target_range": [selection.start, selection.end],
            "basket_item_ids": basket_item_ids,
            "basket_item_count": len(basket_item_ids),
            "snippet_count": snippet_count,
        }
        if plan_card_id is not None:
            from_basket_audit["plan_card_id"] = plan_card_id
        if self.state.project.current_project_id_or_path is not None:
            from_basket_audit["project_id_or_path"] = str(self.state.project.current_project_id_or_path)
        from_basket_audit.update(self._last_patch_continuation_metadata())
        if metadata is not None:
            from_basket_audit.update(metadata)
        self._record_audit_event("workflow.revise_from_basket", from_basket_audit)
        return patch

    def get_pending_patches(self) -> list[PatchProposal]:
        self._ensure_project_open()
        """Return all current pending patch proposals in creation order."""
        return list(self._pending_patches.values())

    def check_pending_patches_validity(self, *, lenient: bool = False) -> dict[str, bool]:
        """Check validity (can_apply) of all pending patches without side effects (no action/audit logs)."""
        if not isinstance(lenient, bool):
            raise TypeError("lenient must be a boolean")
        self._ensure_project_open()
        return {
            patch_id: self._patch_result_document_content(patch, lenient=lenient) is not None
            for patch_id, patch in self._pending_patches.items()
        }

    def get_resolved_patches(self) -> list[PatchResolution]:
        self._ensure_project_open()
        """Return all patch resolutions processed during the current session."""
        return list(self._resolved_patches.values())

    def preview_patch(self, patch_id: str) -> PatchPreview:
        if not isinstance(patch_id, str):
            raise TypeError("patch_id must be a string")
        if not patch_id.strip():
            raise ValueError("patch_id cannot be empty or whitespace only")
        self._ensure_project_open()
        if patch_id in self._resolved_patches:
            raise PermissionError(f"patch has already been resolved: {patch_id!r}")
        if patch_id not in self._pending_patches:
            raise ValueError(f"patch_id not found in pending patches: {patch_id!r}")
        patch = self._pending_patches[patch_id]
        preview_text = self._patch_preview_text(patch)
        result_document_content = self._patch_result_document_content(patch)
        can_apply = result_document_content is not None
        status = "ready_to_apply" if can_apply else "stale_target"

        pre_content = self.state.document.current_document_content or ""
        pre_char_count = len(pre_content)
        pre_word_count = len(pre_content.split())
        pre_line_count = len(pre_content.splitlines())

        if result_document_content is not None:
            post_content = result_document_content
        else:
            post_content = pre_content
        post_char_count = len(post_content)
        post_word_count = len(post_content.split())
        post_line_count = len(post_content.splitlines())

        patch_char_delta = len(patch.proposed_text) - len(patch.original_text)
        patch_word_delta = len(patch.proposed_text.split()) - len(patch.original_text.split())
        patch_line_delta = len(patch.proposed_text.splitlines()) - len(patch.original_text.splitlines())

        stats_metadata = {
            "pre_char_count": pre_char_count,
            "pre_word_count": pre_word_count,
            "pre_line_count": pre_line_count,
            "post_char_count": post_char_count,
            "post_word_count": post_word_count,
            "post_line_count": post_line_count,
            "patch_char_delta": patch_char_delta,
            "patch_word_delta": patch_word_delta,
            "patch_line_delta": patch_line_delta,
        }

        preview_metadata = dict(patch.metadata)
        preview_metadata.update(stats_metadata)

        preview = PatchPreview(
            patch_id=patch.patch_id,
            target_document_id=patch.target_document_id,
            target_range=patch.target_range,
            original_text=patch.original_text,
            proposed_text=patch.proposed_text,
            preview_text=preview_text,
            metadata=preview_metadata,
            result_document_content=result_document_content,
            can_apply=can_apply,
            status=status,
        )
        self.state.workflow.last_previewed_patch_id = patch.patch_id
        preview_manifest = self._patch_preview_manifest(preview)
        self.state.workflow.last_patch_preview = preview_manifest
        self._record_workflow_action(
            action="preview_patch",
            request={"patch_id": patch.patch_id},
            result=preview_manifest,
        )

        audit_preview_manifest = dict(preview_manifest)
        audit_preview_manifest.update(stats_metadata)

        self._record_audit_event(
            "workflow.preview_patch",
            audit_preview_manifest,
        )
        return preview

    def apply_patch(self, patch_id: str, *, persist: bool = False, reason: str | None = None, metadata: dict[str, object] | None = None) -> PatchResolution:
        return self.resolve_patch(patch_id, decision="accepted", persist=persist, reason=reason, metadata=metadata)

    def reject_patch(self, patch_id: str, *, reason: str | None = None, metadata: dict[str, object] | None = None) -> PatchResolution:
        return self.resolve_patch(patch_id, decision="rejected", reason=reason, metadata=metadata)

    def resolve_patch_and_save_session(
        self,
        patch_id: str,
        *,
        decision: PatchDecision,
        persist: bool = False,
        reason: str | None = None,
        session_id: str = "sessions/current-session.md",
        metadata: dict[str, object] | None = None,
    ) -> PatchResolutionSnapshot:
        if not isinstance(patch_id, str):
            raise TypeError("patch_id must be a string")
        if not isinstance(decision, str):
            raise TypeError("patch decision must be a string")
        if not isinstance(persist, bool):
            raise TypeError("persist must be a boolean")
        if reason is not None and not isinstance(reason, str):
            raise TypeError("reason must be a string or None")
        if not isinstance(session_id, str):
            raise TypeError("session_id must be a string")
        self._validate_metadata(metadata)
        resolution = self.resolve_patch(patch_id, decision=decision, persist=persist, reason=reason, metadata=metadata)
        request_data = {
            "patch_id": resolution.patch_id,
            "decision": resolution.decision,
            "persist": persist,
            "session_id": session_id,
        }
        if reason is not None:
            request_data["reason"] = reason
        if metadata is not None:
            request_data["metadata"] = metadata
        self._record_workflow_action(
            action="resolve_patch_and_save_session",
            request=request_data,
            result={
                "patch_resolution": self._patch_resolution_manifest(resolution),
                "session_id": session_id,
            },
        )
        session = self.save_session_snapshot(session_id)
        audit_payload = {
            "patch_id": resolution.patch_id,
            "decision": resolution.decision,
            "persisted": resolution.persisted,
            "session_id": session.id,
            "session_path": session.path,
        }
        for key in (
            "pre_char_count",
            "pre_word_count",
            "pre_line_count",
            "post_char_count",
            "post_word_count",
            "post_line_count",
            "patch_char_delta",
            "patch_word_delta",
            "patch_line_delta",
        ):
            if key in resolution.metadata:
                audit_payload[key] = resolution.metadata[key]
        self._record_audit_event(
            "workflow.resolve_patch_and_save_session",
            audit_payload,
        )
        return PatchResolutionSnapshot(resolution=resolution, session=session)

    def preview_resolve_patch_and_save_session(
        self,
        patch_id: str,
        *,
        decision: PatchDecision,
        persist: bool = False,
        reason: str | None = None,
        session_id: str = "sessions/current-session.md",
        metadata: dict[str, object] | None = None,
    ) -> PatchPreviewResolutionSnapshot:
        preview = self.preview_patch(patch_id)
        snapshot = self.resolve_patch_and_save_session(
            patch_id,
            decision=decision,
            persist=persist,
            reason=reason,
            session_id=session_id,
            metadata=metadata,
        )
        return PatchPreviewResolutionSnapshot(
            preview=preview,
            resolution=snapshot.resolution,
            session=snapshot.session,
        )

    def resolve_patch(self, patch_id: str, *, decision: PatchDecision, persist: bool = False, reason: str | None = None, metadata: dict[str, object] | None = None) -> PatchResolution:
        if not isinstance(patch_id, str):
            raise TypeError("patch_id must be a string")
        if not patch_id.strip():
            raise ValueError("patch_id cannot be empty or whitespace only")
        if not isinstance(decision, str):
            raise TypeError("patch decision must be a string")
        if not isinstance(persist, bool):
            raise TypeError("persist must be a boolean")
        if reason is not None and not isinstance(reason, str):
            raise TypeError("reason must be a string or None")
        self._validate_metadata(metadata)
        if reason is not None:
            reason = reason.strip()
            if not reason:
                reason = None
        self._ensure_project_open()
        if decision not in {"accepted", "rejected"}:
            raise ValueError("patch decision must be accepted or rejected")
        if patch_id in self._resolved_patches:
            raise PermissionError(f"patch has already been resolved: {patch_id!r}")
        if patch_id not in self._pending_patches:
            raise ValueError(f"patch_id not found in pending patches: {patch_id!r}")
        patch = self._pending_patches[patch_id]
        persisted = False

        # Collect pre-application document stats
        pre_content = self.state.document.current_document_content or ""
        pre_char_count = len(pre_content)
        pre_word_count = len(pre_content.split())
        pre_line_count = len(pre_content.splitlines())

        patch_char_delta = len(patch.proposed_text) - len(patch.original_text)
        patch_word_delta = len(patch.proposed_text.split()) - len(patch.original_text.split())
        patch_line_delta = len(patch.proposed_text.splitlines()) - len(patch.original_text.splitlines())

        if decision == "accepted":
            self._ensure_patch_targets_current_document(patch)
            if self._patch_service.is_noop(patch):
                raise ValueError("accepted patch decision requires a non-empty patch proposal")
            self._apply_patch_to_document(patch)
            if persist:
                self.save_document()
                persisted = True
        else:
            self._patch_service.reject(patch)

        # Collect post-application document stats
        post_content = self.state.document.current_document_content or ""
        post_char_count = len(post_content)
        post_word_count = len(post_content.split())
        post_line_count = len(post_content.splitlines())

        stats_metadata = {
            "pre_char_count": pre_char_count,
            "pre_word_count": pre_word_count,
            "pre_line_count": pre_line_count,
            "post_char_count": post_char_count,
            "post_word_count": post_word_count,
            "post_line_count": post_line_count,
            "patch_char_delta": patch_char_delta,
            "patch_word_delta": patch_word_delta,
            "patch_line_delta": patch_line_delta,
        }

        self._pending_patches.pop(patch_id)
        combined_extra = dict(metadata or {})
        combined_extra.update(stats_metadata)
        resolution_metadata = self._patch_resolution_metadata(
            patch=patch,
            decision=decision,
            persisted=persisted,
            reason=reason,
            extra_metadata=combined_extra,
        )
        self._remember_workflow_card(
            WorkflowCard(
                id=f"{patch.patch_id}:resolution",
                card_type="patch_resolution",
                title="Patch Accepted" if decision == "accepted" else "Patch Rejected",
                body=patch.proposed_text if decision == "accepted" else patch.original_text,
                metadata=resolution_metadata,
            )
        )
        self.state.document.current_selection = None
        self.state.workflow.last_resolved_patch_id = patch.patch_id

        resolution_document_content, resolution_dirty = self._patch_resolution_document_state(patch, decision)
        resolution = PatchResolution(
            patch_id=patch.patch_id,
            decision=decision,
            target_document_id=patch.target_document_id,
            document_content=resolution_document_content,
            dirty=resolution_dirty,
            persisted=persisted,
            metadata=resolution_metadata,
            continuation_document_id=self.state.document.current_document_id,
            continuation_document_content=self.state.document.current_document_content,
        )
        self._resolved_patches[patch.patch_id] = resolution
        resolution_manifest = self._patch_resolution_manifest(resolution)
        self.state.workflow.last_patch_resolution = resolution_manifest
        request_data = {
            "patch_id": patch.patch_id,
            "decision": decision,
            "persist": persist,
        }
        if self.state.project.current_project_id_or_path is not None:
            request_data["project_id_or_path"] = str(self.state.project.current_project_id_or_path)
        if reason is not None:
            request_data["reason"] = reason
        if metadata is not None:
            request_data["metadata"] = metadata
        self._record_workflow_action(
            action="resolve_patch",
            request=request_data,
            result=resolution_manifest,
        )
        resolve_audit: dict[str, object] = dict(resolution_manifest)
        resolve_audit.update(resolution.metadata)
        resolve_audit.update(stats_metadata)
        self._record_audit_event("workflow.resolve_patch", resolve_audit)
        return resolution

    def describe_state(self) -> dict[str, object]:
        return {
            "project": {
                "current_project_id_or_path": self.state.project.current_project_id_or_path,
                "open_document_id": self.state.project.open_document_id,
                "project_items": [self._project_item_manifest(item) for item in self.state.project.project_items],
                "sessions": [self._project_item_manifest(item) for item in self.state.project.sessions],
            },
            "document": {
                "current_document_id": self.state.document.current_document_id,
                "current_document_content": self.state.document.current_document_content,
                "dirty": self.state.document.dirty,
                "current_selection": self._document_selection_manifest(self.state.document.current_selection),
            },
            "basket": {
                "selected_basket_item_id": self.state.basket.selected_basket_item_id,
                "items": [self._basket_item_manifest(item) for item in self.state.basket.items],
            },
            "workflow": {
                "focused_card_id": self.state.workflow.focused_card_id,
                "last_plan_card_id": self.state.workflow.last_plan_card_id,
                "last_previewed_patch_id": self.state.workflow.last_previewed_patch_id,
                "last_resolved_patch_id": self.state.workflow.last_resolved_patch_id,
                "last_patch_preview": self.state.workflow.last_patch_preview,
                "last_patch_resolution": self.state.workflow.last_patch_resolution,
                "last_action_status": self.state.workflow.last_action_status,
                "compacted_action_count": self.state.workflow.compacted_action_count,
                "compacted_context_summary": self.state.workflow.compacted_context_summary,
                "command_history": list(self.state.workflow.command_history),
                "action_records": [
                    self._workflow_action_record_manifest(record) for record in self._workflow_action_records()
                ],
                "compacted_action_records": [
                    self._workflow_action_record_manifest(record)
                    for record in self.state.workflow.compacted_action_records
                ],
                "cards": [self._workflow_card_manifest(card) for card in self.state.workflow.cards],
                "patch_resolutions": [
                    self._workflow_card_manifest(card)
                    for card in self.state.workflow.cards
                    if card.card_type == "patch_resolution"
                ],
            },
            "pending_patch_proposals": [
                self._patch_proposal_manifest(patch)
                for patch in sorted(self._pending_patches.values(), key=lambda item: item.patch_id)
            ],
            "resolved_patch_resolutions": [
                self._patch_resolution_manifest(resolution)
                for resolution in sorted(self._resolved_patches.values(), key=lambda item: item.patch_id)
            ],
        }

    def save_session_snapshot(self, session_id: str = "sessions/current-session.md") -> ProjectItem:
        if not isinstance(session_id, str):
            raise TypeError("session_id must be a string")
        if self._project_store is None and not Path(session_id).is_absolute():
            raise RuntimeError(
                "Project must be opened before saving a session snapshot, "
                "or supply an absolute path for the snapshot file"
            )
        action_record = self._record_workflow_action(
            action="save_session_snapshot",
            request={"session_id": session_id},
            result={"snapshot_kind": "app_state"},
        )
        path = Path(session_id)
        if self._project_store is not None and not path.is_absolute():
            path = self._project_store.project_root / path
        path = path.resolve()
        if self._project_store is not None:
            try:
                item_id = str(path.relative_to(self._project_store.project_root.resolve()))
            except ValueError:
                item_id = str(path)
        else:
            item_id = str(path)
        item = ProjectItem(
            id=item_id,
            label=path.name,
            item_type="session",
            path=str(path),
            metadata={"snapshot_kind": "app_state"},
        )
        self.list_project_items()
        for index, existing in enumerate(self.state.project.sessions):
            if existing.id == item.id:
                self.state.project.sessions[index] = item
                break
        else:
            self.state.project.sessions.append(item)
        action_record.result.update(
            {
                "item_id": item.id,
                "path": item.path,
                "metadata": dict(item.metadata),
            }
        )
        manifest = self.describe_state()
        content = "# Exegesis Session Snapshot\n\n```json\n"
        content += json.dumps(manifest, indent=2, sort_keys=True)
        content += "\n```\n"
        if self._project_store is not None:
            self._project_store.write_document(session_id, content)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        self._record_audit_event(
            "session.snapshot_saved",
            {"session_id": session_id, "item_id": item.id},
        )
        return item

    def compact_workflow_history(self, *, max_recent: int = 10) -> dict[str, object]:
        """Compact old action records into a summary so long sessions stay navigable.

        Preserves the raw history in the session snapshot; only the live
        action_records list is trimmed. The compacted summary is threaded into
        subsequent plan/draft calls so the model context stays coherent.
        """
        self._ensure_project_open()
        records = self.state.workflow.action_records
        if len(records) <= max_recent:
            return {
                "compacted_count": 0,
                "retained_count": len(records),
                "compacted_context_summary": self.state.workflow.compacted_context_summary,
            }
        to_compact = records[:-max_recent]
        to_retain = records[-max_recent:]
        lines = []
        for rec in to_compact:
            result_keys = ", ".join(
                f"{k}={v!r}" for k, v in list(rec.result.items())[:3]
            )
            lines.append(f"[{rec.sequence}] {rec.action}: {result_keys}")
        new_summary = "; ".join(lines)
        prior = self.state.workflow.compacted_context_summary
        if prior:
            new_summary = f"{prior} | {new_summary}"
        self.state.workflow.compacted_action_records.extend(to_compact)
        self.state.workflow.compacted_context_summary = new_summary
        self.state.workflow.compacted_action_count += len(to_compact)
        self.state.workflow.action_records = to_retain
        self._record_audit_event(
            "session.history_compacted",
            {
                "compacted_count": len(to_compact),
                "retained_count": len(to_retain),
                "total_compacted_count": self.state.workflow.compacted_action_count,
            },
        )
        return {
            "compacted_count": len(to_compact),
            "retained_count": len(to_retain),
            "compacted_context_summary": self.state.workflow.compacted_context_summary,
        }

    def set_document_selection(self, *, start: int, end: int) -> DocumentSelection:
        if isinstance(start, bool) or not isinstance(start, int):
            raise TypeError("start must be an integer")
        if isinstance(end, bool) or not isinstance(end, int):
            raise TypeError("end must be an integer")
        self._ensure_project_open()
        if self.state.document.current_document_id is None:
            raise RuntimeError("No document is open")
        content = self.state.document.current_document_content
        if content is None:
            raise RuntimeError("No document is open")
        if start < 0 or end < start or end > len(content):
            raise ValueError("Invalid document selection range")
        selected_text = content[start:end]
        selection = DocumentSelection(start=start, end=end, selected_text=selected_text)
        self.state.document.current_selection = selection
        return selection

    def search_document_text(self, text: str, *, start_from: int = 0) -> DocumentSelection:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        if not text.strip():
            raise ValueError("text cannot be empty or whitespace only")
        if "\x00" in text:
            raise ValueError("text cannot contain null bytes")
        if isinstance(start_from, bool) or not isinstance(start_from, int):
            raise TypeError("start_from must be an integer")
        """Find text in the current document and set it as the active selection.

        Raises RuntimeError if no document is open, ValueError if text is not found.
        start_from offsets the search so callers can find later occurrences without
        computing byte positions manually.
        """
        if self.state.document.current_document_id is None:
            raise RuntimeError("No document is open")
        content = self.state.document.current_document_content
        pos = content.find(text, start_from)
        if pos == -1:
            raise ValueError(
                f"Text not found in current document (start_from={start_from}): {text!r}"
            )
        return self.set_document_selection(start=pos, end=pos + len(text))

    def _apply_patch_to_document(self, patch: PatchProposal) -> None:
        self.state.document.current_document_content = self._patch_service.apply(
            self.state.document.current_document_content,
            patch,
        )
        self.state.document.dirty = True

    def _ensure_patch_targets_current_document(self, patch: PatchProposal) -> None:
        if self.state.document.current_document_id != patch.target_document_id:
            raise ValueError("patch target document is not the current document")

    def _patch_preview_text(self, patch: PatchProposal) -> str:
        for card in reversed(self.state.workflow.cards):
            if card.id == patch.patch_id and card.card_type == "patch":
                return card.body
        return patch.proposed_text

    def _patch_result_document_content(self, patch: PatchProposal, *, lenient: bool = False) -> str | None:
        if self.state.document.current_document_id != patch.target_document_id:
            return None
        if lenient:
            start, end = patch.target_range
            current_content = self.state.document.current_document_content
            if start < 0 or end < start or end > len(current_content):
                return None
            current_target = current_content[start:end]
            if current_target.casefold() != patch.original_text.casefold():
                return None
            return f"{current_content[:start]}{patch.proposed_text}{current_content[end:]}"
        try:
            return self._patch_service.apply(
                self.state.document.current_document_content,
                patch,
            )
        except ValueError:
            return None

    def _patch_resolution_document_state(self, patch: PatchProposal, decision: PatchDecision) -> tuple[str, bool]:
        if self.state.document.current_document_id == patch.target_document_id:
            return self.state.document.current_document_content, self.state.document.dirty
        if decision == "rejected":
            _, document_content = self._project_store.read_document(patch.target_document_id)
            return document_content, False
        return self.state.document.current_document_content, self.state.document.dirty

    def _last_patch_continuation_metadata(self) -> dict[str, object]:
        resolution = self.state.workflow.last_patch_resolution
        if resolution is None:
            return {}
        patch_id = resolution.get("patch_id")
        decision = resolution.get("decision")
        if not isinstance(patch_id, str) or not isinstance(decision, str):
            return {}
        metadata: dict[str, object] = {
            "continued_from_patch_id": patch_id,
            "continued_from_patch_decision": decision,
        }
        continuation_document_id = resolution.get("continuation_document_id")
        if isinstance(continuation_document_id, str):
            metadata["continuation_document_id"] = continuation_document_id
        continuation_document_content = resolution.get("continuation_document_content")
        if isinstance(continuation_document_content, str):
            metadata["continuation_document_sha256"] = hashlib.sha256(
                continuation_document_content.encode("utf-8")
            ).hexdigest()
            metadata["continuation_document_char_count"] = len(continuation_document_content)
        dirty = resolution.get("dirty")
        if isinstance(dirty, bool):
            metadata["continuation_document_dirty"] = dirty
        return metadata

    def _gather_basket_snippets(self) -> dict[str, list[str]]:
        if not self.state.basket.items:
            return {}
        if self._retrieval_service is None:
            self._record_audit_event(
                "retrieval.basket_context_failed",
                {"reason": "retrieval_service_unavailable", "basket_item_count": len(self.state.basket.items)},
            )
            raise RuntimeError("retrieval service unavailable for basket context")
        from exegesis_engine.retrieval.search_service import RetrievalConstraints, RetrievalQuery
        snippets: dict[str, list[str]] = {}
        for item in self.state.basket.items:
            try:
                result = self._retrieval_service.retrieve_auto(
                    RetrievalQuery(
                        query_text=item.label,
                        scope="vault",
                        intent="lookup",
                        constraints=RetrievalConstraints(max_results=2),
                        confidentiality_profile="confidential",
                    )
                )
                excerpts = [h.excerpt_text for h in result.hits if h.excerpt_text]
                if excerpts:
                    snippets[item.id] = excerpts
            except Exception as exc:
                self._record_audit_event(
                    "retrieval.basket_context_failed",
                    {"item_id": item.id, "item_label": item.label, "error": str(exc)},
                )
                raise RuntimeError(f"retrieval failed while gathering basket context for {item.id}") from exc
        return snippets

    def _search(self, *, query_text: str, scope: str, max_results: int, doc_types: tuple[str, ...] = ()):
        if self._retrieval_service is None:
            raise RuntimeError("Project must be opened before retrieval can run")
        from exegesis_engine.retrieval.search_service import RetrievalConstraints, RetrievalQuery
        result = self._retrieval_service.retrieve_auto(
            RetrievalQuery(
                query_text=query_text,
                scope=scope,
                intent="lookup",
                constraints=RetrievalConstraints(max_results=max_results, doc_types=doc_types),
                confidentiality_profile="confidential",
            )
        )
        self.state.workflow.last_action_status = f"retrieval:{len(result.hits)} hits"
        return result

    def _remember_workflow_card(self, card: WorkflowCard) -> None:
        self.state.workflow.cards.append(card)
        self.state.workflow.focused_card_id = card.id
        self.state.workflow.last_action_status = card.title

    def _record_workflow_action(
        self,
        *,
        action: str,
        request: dict[str, object] | None = None,
        result: dict[str, object] | None = None,
    ) -> WorkflowActionRecord:
        self.state.workflow.command_history.append(action)
        action_records = self._workflow_action_records()
        record = WorkflowActionRecord(
            sequence=self.state.workflow.compacted_action_count + len(action_records) + 1,
            action=action,
            request=dict(request or {}),
            result=dict(result or {}),
        )
        action_records.append(record)
        return record

    def _workflow_action_records(self) -> list[WorkflowActionRecord]:
        return self.state.workflow.action_records

    def get_audit_events(self, *, name_filter: str | None = None) -> list[AuditEvent]:
        """Return persisted audit events, optionally filtered by event name."""
        if self._audit_log is None:
            return []
        return self._audit_log.read_events(name_filter=name_filter)

    def _record_audit_event(self, name: str, metadata: dict[str, object] | None = None) -> None:
        if self._audit_log is not None:
            self._audit_log.record(name=name, metadata=metadata)

    def _patch_proposal_manifest(self, patch: PatchProposal) -> dict[str, object]:
        result_document_content = self._patch_result_document_content(patch)
        return {
            "patch_id": patch.patch_id,
            "target_document_id": patch.target_document_id,
            "target_range": list(patch.target_range),
            "original_text": patch.original_text,
            "proposed_text": patch.proposed_text,
            "preview_text": self._patch_preview_text(patch),
            "result_document_content": result_document_content,
            "can_apply": result_document_content is not None,
            "status": "ready_to_apply" if result_document_content is not None else "stale_target",
            "metadata": dict(patch.metadata),
        }

    def _patch_resolution_metadata(
        self,
        *,
        patch: PatchProposal,
        decision: PatchDecision,
        persisted: bool,
        reason: str | None = None,
        extra_metadata: dict[str, object] | None = None,
    ) -> dict[str, object]:
        metadata = {
            "patch_id": patch.patch_id,
            "decision": decision,
            "document_id": patch.target_document_id,
            "target_range": list(patch.target_range),
            "original_text": patch.original_text,
            "proposed_text": patch.proposed_text,
            "preview_text": self._patch_preview_text(patch),
            "persisted": persisted,
            "continuation_document_id": self.state.document.current_document_id,
            "continuation_document_content": self.state.document.current_document_content,
            "decision_timestamp": datetime.now(timezone.utc).isoformat(),
            **dict(patch.metadata),
        }
        if self.state.project.current_project_id_or_path is not None:
            metadata["project_id_or_path"] = str(self.state.project.current_project_id_or_path)
        metadata.update(self._patch_resolution_preview_metadata(patch))
        if reason is not None:
            metadata["reason"] = reason
        if extra_metadata is not None:
            metadata.update(extra_metadata)
        return metadata

    def _patch_resolution_preview_metadata(self, patch: PatchProposal) -> dict[str, object]:
        preview = self.state.workflow.last_patch_preview
        if preview is None or preview.get("patch_id") != patch.patch_id:
            return {"previewed_before_resolution": False}
        metadata: dict[str, object] = {
            "previewed_before_resolution": True,
        }
        status = preview.get("status")
        can_apply = preview.get("can_apply")
        if isinstance(status, str):
            metadata["preview_status"] = status
        if isinstance(can_apply, bool):
            metadata["preview_can_apply"] = can_apply
        return metadata

    @staticmethod
    def _patch_preview_manifest(preview: PatchPreview) -> dict[str, object]:
        return {
            "patch_id": preview.patch_id,
            "target_document_id": preview.target_document_id,
            "target_range": list(preview.target_range),
            "original_text": preview.original_text,
            "proposed_text": preview.proposed_text,
            "preview_text": preview.preview_text,
            "metadata": dict(preview.metadata),
            "result_document_content": preview.result_document_content,
            "can_apply": preview.can_apply,
            "status": preview.status,
        }

    @staticmethod
    def _patch_resolution_manifest(resolution: PatchResolution) -> dict[str, object]:
        return {
            "patch_id": resolution.patch_id,
            "decision": resolution.decision,
            "target_document_id": resolution.target_document_id,
            "document_content": resolution.document_content,
            "dirty": resolution.dirty,
            "persisted": resolution.persisted,
            "metadata": dict(resolution.metadata),
            "continuation_document_id": resolution.continuation_document_id,
            "continuation_document_content": resolution.continuation_document_content,
        }

    @staticmethod
    def _project_item_manifest(item: ProjectItem) -> dict[str, object]:
        return {
            "id": item.id,
            "label": item.label,
            "item_type": item.item_type,
            "path": item.path,
            "metadata": dict(item.metadata),
        }

    @staticmethod
    def _basket_item_manifest(item: BasketItem) -> dict[str, object]:
        return {
            "id": item.id,
            "item_type": item.item_type,
            "label": item.label,
            "payload": dict(item.payload),
        }

    @staticmethod
    def _workflow_card_manifest(card: WorkflowCard) -> dict[str, object]:
        return {
            "id": card.id,
            "card_type": card.card_type,
            "title": card.title,
            "body": card.body,
            "metadata": dict(card.metadata),
            "actions": [dict(action) for action in card.actions],
        }

    @staticmethod
    def _workflow_action_record_manifest(record: WorkflowActionRecord) -> dict[str, object]:
        return {
            "sequence": record.sequence,
            "action": record.action,
            "request": dict(record.request),
            "result": dict(record.result),
        }

    @staticmethod
    def _document_selection_manifest(selection: DocumentSelection | None) -> dict[str, object] | None:
        if selection is None:
            return None
        return {
            "start": selection.start,
            "end": selection.end,
            "selected_text": selection.selected_text,
        }

    def _doc_type_for_item(self, item: ProjectItem) -> str:
        if item.item_type == "session":
            return "memo"
        return self._doc_type_for_path(item.path)

    @staticmethod
    def _doc_type_for_path(path: str) -> str:
        suffix = Path(path).suffix.lower()
        if suffix in {".md", ".markdown", ".rst"}:
            return "memo"
        return "document"

    def _validate_document_lifecycle_inputs(
        self,
        *,
        category: str,
        title: str,
        content: str,
        document_type: str,
    ) -> None:
        if category not in _DOCUMENT_CATEGORY_DIRS:
            raise ValueError(f"unknown document category: {category!r}")
        for name, value in {"title": title, "content": content, "document_type": document_type}.items():
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string")
            if "\x00" in value:
                raise ValueError(f"{name} cannot contain null bytes")
        if not title.strip():
            raise ValueError("title is required")
        if not document_type.strip():
            raise ValueError("document_type is required")

    def _deduped_category_document_path(self, category: str, title: str) -> str:
        if category not in _DOCUMENT_CATEGORY_DIRS:
            raise ValueError(f"unknown document category: {category!r}")
        if self._project_store is None:
            raise RuntimeError("Project store is required")
        folder = _DOCUMENT_CATEGORY_DIRS[category]
        filename = self._safe_document_filename(title, default_stem=self._category_document_type(category))
        candidate = Path(folder) / filename
        index = 2
        while (self._project_store.project_root / candidate).exists():
            stem = Path(filename).stem
            suffix = Path(filename).suffix
            candidate = Path(folder) / f"{stem}-{index}{suffix}"
            index += 1
        return str(candidate)

    @staticmethod
    def _safe_document_filename(title: str, *, default_stem: str = "document", allow_extensionless: bool = False) -> str:
        raw = Path(title.strip()).name
        suffix = Path(raw).suffix or ("" if allow_extensionless else ".md")
        stem = Path(raw).stem if Path(raw).suffix else raw
        safe_stem = re.sub(r"[^A-Za-z0-9._ -]+", "-", stem).strip(" .-_")
        if not safe_stem:
            safe_stem = default_stem
        return f"{safe_stem}{suffix}"

    @staticmethod
    def _category_document_type(category: str) -> str:
        return {
            "Drafts": "draft",
            "Memos": "memo",
            "Summaries": "summary",
            "Transcripts": "transcript",
            "Literature": "literature",
        }[category]

    def _index_document_item(self, item: ProjectItem, content: str) -> None:
        if self._retrieval_service is None:
            return
        self._retrieval_service.add_or_update_document(
            doc_id=item.id,
            doc_type=str(item.metadata.get("document_type") or self._doc_type_for_item(item)),
            title_hint=item.label,
            text=content,
        )
