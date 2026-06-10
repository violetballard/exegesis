from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from exegesis_engine.api.app_service import ExegesisAppService
from exegesis_engine.state.models import AppState, BasketItem, DocumentState, ProjectItem, ProjectState


@dataclass(frozen=True)
class ShellDocumentSnapshot:
    document_id: str
    title: str
    content: str
    dirty: bool


class ShellEngineAdapter:
    """Thin Textual-facing seam over the canonical engine app service.

    The shell should translate widget actions through this adapter rather than
    reaching into engine internals or the old mock fixture registry.
    """

    def __init__(self, service: ExegesisAppService | None = None) -> None:
        self.service = service or ExegesisAppService()

    @property
    def state(self) -> AppState:
        return self.service.state

    def open_project(self, project_path: str | Path) -> ProjectState:
        return self.service.open_project(project_path)

    def list_project_items(self) -> list[ProjectItem]:
        return self.service.list_project_items()

    def open_document(self, document_id: str) -> ShellDocumentSnapshot:
        document = self.service.open_document(document_id)
        return self._document_snapshot(document)

    def create_document(
        self,
        *,
        category: str,
        title: str,
        content: str,
        document_type: str,
        relative_path: str | None = None,
    ) -> ProjectItem:
        return self.service.create_document(
            category=category,
            title=title,
            content=content,
            document_type=document_type,
            relative_path=relative_path,
        )

    def import_markdown_document(
        self,
        *,
        source_path: str | Path,
        category: str,
        relative_path: str | None = None,
    ) -> ProjectItem:
        return self.service.import_markdown_document(source_path=source_path, category=category, relative_path=relative_path)

    def rename_document(self, document_id: str, new_title: str) -> ProjectItem:
        return self.service.rename_document(document_id, new_title)

    def move_document(self, document_id: str, new_relative_path: str) -> ProjectItem:
        return self.service.move_document(document_id, new_relative_path)

    def delete_document(self, document_id: str) -> ProjectItem:
        return self.service.delete_document(document_id)

    def list_trash_items(self) -> list[ProjectItem]:
        return self.service.list_trash_items()

    def open_trash_document(self, trash_id: str) -> ShellDocumentSnapshot:
        document = self.service.open_trash_document(trash_id)
        return self._document_snapshot(document)

    def restore_trash_document(self, trash_id: str) -> ProjectItem:
        return self.service.restore_trash_document(trash_id)

    def restore_trash_document_as(self, trash_id: str, new_title: str) -> ProjectItem:
        return self.service.restore_trash_document_as(trash_id, new_title)

    def permanently_delete_trash_document(self, trash_id: str) -> ProjectItem:
        return self.service.permanently_delete_trash_document(trash_id)

    def save_document(self, content: str | None = None) -> ShellDocumentSnapshot:
        document = self.service.save_document(content)
        return self._document_snapshot(document)

    def set_document_selection(self, start: int, end: int) -> None:
        self.service.set_document_selection(start=start, end=end)

    def add_excerpt_to_basket(
        self,
        *,
        item_id: str,
        label: str,
        source_document_id: str,
        source_document_type: str,
        selected_text: str,
        start: int,
        end: int,
        metadata: dict[str, Any] | None = None,
    ) -> list[BasketItem]:
        basket = self.service.add_basket_item(
            item_id,
            item_type="excerpt",
            label=label,
            payload={
                "source_document_id": source_document_id,
                "source_document_type": source_document_type,
                "selected_text": selected_text,
                "start": start,
                "end": end,
                **dict(metadata or {}),
            },
        )
        return list(basket.items)

    def add_document_to_basket(
        self,
        *,
        document_id: str,
        label: str,
        document_type: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> list[BasketItem]:
        basket = self.service.add_basket_item(
            f"document:{document_id}",
            item_type="document",
            label=label,
            payload={
                "document_id": document_id,
                "document_type": document_type,
                "content": content,
                **dict(metadata or {}),
            },
        )
        return list(basket.items)

    def remove_basket_item(self, item_id: str) -> list[BasketItem]:
        return list(self.service.remove_basket_item(item_id).items)

    def clear_basket(self) -> None:
        self.service.clear_basket()

    def describe_state(self) -> dict[str, Any]:
        return self.service.describe_state()

    @staticmethod
    def _document_snapshot(document: DocumentState) -> ShellDocumentSnapshot:
        document_id = document.current_document_id or ""
        return ShellDocumentSnapshot(
            document_id=document_id,
            title=Path(document_id).name or document_id,
            content=document.current_document_content,
            dirty=document.dirty,
        )
