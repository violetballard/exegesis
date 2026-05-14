from __future__ import annotations

from pathlib import Path
from typing import Iterable

from exegesis_engine.state.models import ProjectItem

_DOCUMENT_SUFFIXES = {".md", ".txt", ".markdown", ".rst"}


class ProjectStore:
    """Filesystem project adapter for the staged Textual MVP contract."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root)
        self.project_root.mkdir(parents=True, exist_ok=True)
        (self.project_root / "sessions").mkdir(parents=True, exist_ok=True)

    def list_project_items(self) -> list[ProjectItem]:
        documents = [
            ProjectItem(
                id=self._item_id(path),
                label=path.name,
                item_type="document",
                path=str(path),
            )
            for path in self._document_paths(self.project_root.iterdir())
        ]
        sessions_root = self.project_root / "sessions"
        sessions = [
            ProjectItem(
                id=self._item_id(path),
                label=path.name,
                item_type="session",
                path=str(path),
            )
            for path in self._document_paths(sessions_root.iterdir())
        ]
        return [*documents, *sessions]

    def read_document(self, document_id: str) -> tuple[Path, str]:
        path = self._resolve(document_id)
        return path, path.read_text(encoding="utf-8")

    def write_document(self, document_id: str, content: str) -> Path:
        path = self._resolve(document_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def ensure_document(self, relative_path: str, content: str = "") -> Path:
        path = self.project_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8")
        return path

    def _resolve(self, document_id: str) -> Path:
        path = Path(document_id)
        if not path.is_absolute():
            path = self.project_root / path
        return path.resolve()

    def _item_id(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.project_root))
        except ValueError:
            return str(path)

    def _document_paths(self, values: Iterable[Path]) -> list[Path]:
        return sorted(
            [path for path in values if path.is_file() and path.suffix.lower() in _DOCUMENT_SUFFIXES],
            key=lambda path: path.name,
        )
