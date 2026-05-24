from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from exegesis_engine.context.basket import ContextBasket
from exegesis_engine.context.store import ContextBasketStore
from exegesis_engine.drafting.service import DraftingService
from exegesis_engine.metrics import MetricsDB, MetricsExporter, MetricsRecorder, UsageIntegrityService
from exegesis_engine.storage.vault import VaultService, VaultState

from exegesis_engine.patches.patch_model import PatchProposal
from exegesis_engine.patches.patch_service import PatchService
from exegesis_engine.retrieval.search_service import RetrievalConstraints, RetrievalQuery, RetrievalService
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
from exegesis_engine.storage.project_store import ProjectStore
from exegesis_engine.workflow.plan_service import PlanService
from exegesis_engine.workflow.revise_service import ReviseService
from exegesis_shared.models.selection import Selection
from exegesis_engine.audit.event_log import AuditLog

PatchDecision = Literal["accepted", "rejected"]


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
        self._vault_service = VaultService()
        self._drafting_service = DraftingService()

    def bootstrap(self, *, app_data_dir: Path, project_name: str) -> EngineRuntime:
        vault = self._vault_service.create_or_open(app_data_dir, project_name)
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
            drafting=self._drafting_service,
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

    def open_project(self, project_path: str | Path) -> ProjectState:
        root = Path(project_path)
        self._project_store = ProjectStore(root)
        project_items = self._project_store.list_project_items()
        self._audit_log = AuditLog(root)
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
        return self.state.project

    def list_project_items(self) -> list[ProjectItem]:
        if self._project_store is None:
            return []
        existing_session_metadata = {
            item.id: dict(item.metadata)
            for item in self.state.project.sessions
            if item.metadata
        }
        items = self._project_store.list_project_items()
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

    def open_document(self, document_id: str) -> DocumentState:
        if self._project_store is None:
            raise RuntimeError("Project must be opened before documents can be loaded")
        _, content = self._project_store.read_document(document_id)
        self.state.project.open_document_id = document_id
        self.state.document = DocumentState(
            current_document_id=document_id,
            current_document_content=content,
            dirty=False,
            current_selection=None,
        )
        return self.state.document

    def save_document(self, content: str | None = None) -> DocumentState:
        if self._project_store is None or self.state.document.current_document_id is None:
            raise RuntimeError("Document must be opened before saving")
        if content is not None:
            self.state.document.current_document_content = content
        self._project_store.write_document(
            self.state.document.current_document_id,
            self.state.document.current_document_content,
        )
        self.state.document.dirty = False
        return self.state.document

    def add_basket_item(self, item_id: str, *, item_type: str = "excerpt", label: str | None = None, payload: dict[str, object] | None = None) -> BasketState:
        item = BasketItem(id=item_id, item_type=item_type, label=label or item_id, payload=dict(payload or {}))
        if all(existing.id != item.id for existing in self.state.basket.items):
            self.state.basket.items.append(item)
        self.state.basket.selected_basket_item_id = item.id
        return self.state.basket

    def remove_basket_item(self, item_id: str) -> BasketState:
        self.state.basket.items = [item for item in self.state.basket.items if item.id != item_id]
        if self.state.basket.selected_basket_item_id == item_id:
            self.state.basket.selected_basket_item_id = self.state.basket.items[0].id if self.state.basket.items else None
        return self.state.basket

    def clear_basket(self) -> BasketState:
        self.state.basket = BasketState()
        return self.state.basket

    def set_current_selection(self, *, selection_type: str, selection_id: str, source_pane: str, payload: dict[str, object] | None = None) -> Selection:
        selection = Selection(type=selection_type, id=selection_id, source_pane=source_pane, payload=dict(payload or {}))
        self.state.current_selection = selection
        self.state.inspector = InspectorState(
            current_inspected_object_type=selection.type,
            current_inspected_object_id=selection.id,
            current_payload=dict(selection.payload),
        )
        return selection

    def search_project(self, query_text: str, *, max_results: int = 10):
        return self._search(query_text=query_text, scope="vault", max_results=max_results)

    def search_memos(self, query_text: str, *, max_results: int = 10):
        return self._search(query_text=query_text, scope="vault", max_results=max_results, doc_types=("memo",))

    def search_literature(self, query_text: str, *, max_results: int = 10):
        return self._search(query_text=query_text, scope="vault", max_results=max_results, doc_types=("pdf", "paper", "literature"))

    def plan_from_basket(self) -> WorkflowCard:
        card = self._plan_service.plan_from_basket(self.state.basket.items)
        self._remember_workflow_card(card)
        self._record_workflow_action(
            action="plan_from_basket",
            request={
                "basket_item_ids": [item.id for item in self.state.basket.items],
                "basket_item_count": len(self.state.basket.items),
            },
            result={
                "card_id": card.id,
                "card_type": card.card_type,
                "title": card.title,
            },
        )
        return card

    def draft_from_basket(self) -> WorkflowCard:
        card = self._revise_service.draft_from_basket(self.state.basket.items)
        self._remember_workflow_card(card)
        self._record_workflow_action(
            action="draft_from_basket",
            request={
                "basket_item_ids": [item.id for item in self.state.basket.items],
                "basket_item_count": len(self.state.basket.items),
            },
            result={
                "card_id": card.id,
                "card_type": card.card_type,
                "title": card.title,
            },
        )
        return card

    def revise_selection(self, *, proposed_text: str) -> PatchProposal:
        document = self.state.document
        if document.current_document_id is None or document.current_selection is None:
            raise RuntimeError("Document selection is required before revising")
        selection = document.current_selection
        patch, preview = self._revise_service.revise_selection(
            document_id=document.current_document_id,
            original_text=selection.selected_text,
            proposed_text=proposed_text,
            target_range=(selection.start, selection.end),
            metadata={"source": "revise_selection"},
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
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": patch.patch_id}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": patch.patch_id}},
                ],
            )
        )
        self._record_workflow_action(
            action="revise_selection",
            request={
                "document_id": document.current_document_id,
                "target_range": [selection.start, selection.end],
                "original_text": selection.selected_text,
                "proposed_text": proposed_text,
            },
            result={
                "patch_id": patch.patch_id,
                "preview_text": preview or proposed_text,
            },
        )
        return patch

    def preview_patch(self, patch_id: str) -> PatchPreview:
        patch = self._pending_patches[patch_id]
        preview_text = self._patch_preview_text(patch)
        result_document_content = self._patch_result_document_content(patch)
        can_apply = result_document_content is not None
        status = "ready_to_apply" if can_apply else "stale_target"
        preview = PatchPreview(
            patch_id=patch.patch_id,
            target_document_id=patch.target_document_id,
            target_range=patch.target_range,
            original_text=patch.original_text,
            proposed_text=patch.proposed_text,
            preview_text=preview_text,
            metadata=dict(patch.metadata),
            result_document_content=result_document_content,
            can_apply=can_apply,
            status=status,
        )
        self.state.workflow.last_previewed_patch_id = patch.patch_id
        self.state.workflow.last_patch_preview = {
            "patch_id": preview.patch_id,
            "target_document_id": preview.target_document_id,
            "target_range": list(preview.target_range),
            "original_text": preview.original_text,
            "proposed_text": preview.proposed_text,
            "preview_text": preview.preview_text,
            "result_document_content": preview.result_document_content,
            "can_apply": preview.can_apply,
            "status": preview.status,
        }
        self._record_workflow_action(
            action="preview_patch",
            request={"patch_id": patch.patch_id},
            result={
                "patch_id": preview.patch_id,
                "target_document_id": preview.target_document_id,
                "target_range": list(preview.target_range),
                "preview_text": preview.preview_text,
                "result_document_content": preview.result_document_content,
                "can_apply": preview.can_apply,
                "status": preview.status,
            },
        )
        return preview

    def apply_patch(self, patch_id: str, *, persist: bool = False) -> PatchResolution:
        return self.resolve_patch(patch_id, decision="accepted", persist=persist)

    def reject_patch(self, patch_id: str) -> PatchResolution:
        return self.resolve_patch(patch_id, decision="rejected")

    def resolve_patch(self, patch_id: str, *, decision: PatchDecision, persist: bool = False) -> PatchResolution:
        if decision not in {"accepted", "rejected"}:
            raise ValueError("patch decision must be accepted or rejected")

        patch = self._pending_patches[patch_id]
        persisted = False
        if decision == "accepted":
            self._ensure_patch_targets_current_document(patch)
            self._apply_patch_to_document(patch)
            if persist:
                self.save_document()
                persisted = True
        else:
            self._patch_service.reject(patch)

        self._pending_patches.pop(patch_id)
        resolution_metadata = self._patch_resolution_metadata(
            patch=patch,
            decision=decision,
            persisted=persisted,
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
        resolution_manifest: dict[str, object] = {
            "patch_id": resolution.patch_id,
            "decision": resolution.decision,
            "target_document_id": resolution.target_document_id,
            "document_content": resolution.document_content,
            "dirty": resolution.dirty,
            "persisted": resolution.persisted,
            "continuation_document_id": resolution.continuation_document_id,
            "continuation_document_content": resolution.continuation_document_content,
        }
        self.state.workflow.last_patch_resolution = resolution_manifest
        self._record_workflow_action(
            action="resolve_patch",
            request={
                "patch_id": patch.patch_id,
                "decision": decision,
                "persist": persist,
            },
            result=resolution_manifest,
        )
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
                "last_previewed_patch_id": self.state.workflow.last_previewed_patch_id,
                "last_resolved_patch_id": self.state.workflow.last_resolved_patch_id,
                "last_patch_preview": self.state.workflow.last_patch_preview,
                "last_patch_resolution": self.state.workflow.last_patch_resolution,
                "last_action_status": self.state.workflow.last_action_status,
                "command_history": list(self.state.workflow.command_history),
                "action_records": [
                    self._workflow_action_record_manifest(record) for record in self._workflow_action_records()
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
        }

    def save_session_snapshot(self, session_id: str = "sessions/current-session.md") -> ProjectItem:
        if self._project_store is None:
            raise RuntimeError("Project must be opened before saving a session snapshot")
        action_record = self._record_workflow_action(
            action="save_session_snapshot",
            request={"session_id": session_id},
            result={"snapshot_kind": "app_state"},
        )
        path = Path(session_id)
        if not path.is_absolute():
            path = self._project_store.project_root / path
        path = path.resolve()
        try:
            item_id = str(path.relative_to(self._project_store.project_root.resolve()))
        except ValueError:
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
        self._project_store.write_document(session_id, content)
        return item

    def set_document_selection(self, *, start: int, end: int) -> DocumentSelection:
        content = self.state.document.current_document_content
        selected_text = content[start:end]
        selection = DocumentSelection(start=start, end=end, selected_text=selected_text)
        self.state.document.current_selection = selection
        return selection

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

    def _patch_result_document_content(self, patch: PatchProposal) -> str | None:
        if self.state.document.current_document_id != patch.target_document_id:
            return None
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

    def _search(self, *, query_text: str, scope: str, max_results: int, doc_types: tuple[str, ...] = ()):
        if self._retrieval_service is None:
            raise RuntimeError("Project must be opened before retrieval can run")
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
            sequence=len(action_records) + 1,
            action=action,
            request=dict(request or {}),
            result=dict(result or {}),
        )
        action_records.append(record)
        return record

    def _workflow_action_records(self) -> list[WorkflowActionRecord]:
        return self.state.workflow.action_records

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
    ) -> dict[str, object]:
        return {
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
            **dict(patch.metadata),
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
        suffix = Path(item.path).suffix.lower()
        if suffix in {".md", ".markdown", ".rst"}:
            return "memo"
        return "document"
