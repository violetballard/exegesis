from __future__ import annotations

import os
import json
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from typing import Iterable
from uuid import uuid4

_DOCUMENT_SUFFIXES = {"", ".md", ".txt", ".markdown", ".rst"}
_MAX_EXCLUDE_PATHS = 1024
_NONPORTABLE_DOCUMENT_NAME_CHARS = set('<>:"|?*')
_WINDOWS_RESERVED_DOCUMENT_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}

__all__ = ["ProjectItem", "ProjectStore"]


@dataclass(frozen=True)
class ProjectItem:
    id: str
    label: str
    item_type: str
    path: str
    metadata: dict[str, Any] = field(default_factory=dict)


class ProjectStore:
    """Filesystem project adapter for canonical engine document access."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root)
        if self._path_uses_symlink_alias(self.project_root):
            raise ValueError(f"project root uses a symlink alias: {project_root!r}")
        if self._quarantine_blocking_directory(self.project_root):
            self._fsync_directory(self.project_root.parent)
        self.project_root.mkdir(parents=True, exist_ok=True)
        sessions_root = self.project_root / "sessions"
        if self._path_uses_symlink_alias(sessions_root):
            raise ValueError("sessions root uses a symlink alias")
        if self._quarantine_blocking_directory(sessions_root):
            self._fsync_directory(sessions_root.parent)
        sessions_root.mkdir(parents=True, exist_ok=True)

    def list_project_items(self) -> list[ProjectItem]:
        documents = [
            ProjectItem(
                id=self._item_id(path),
                label=path.name,
                item_type="document",
                path=str(path),
            )
            for path in self._document_paths(
                self.project_root,
                exclude_paths=(self.project_root / "sessions", self.project_root / ".trash"),
            )
        ]
        sessions_root = self.project_root / "sessions"
        sessions = [
            ProjectItem(
                id=self._item_id(path),
                label=path.name,
                item_type="session",
                path=str(path),
            )
            for path in self._document_paths(sessions_root)
        ]
        return [*documents, *sessions]

    def read_document(self, document_id: str) -> tuple[Path, str]:
        path = self._resolve(document_id)
        try:
            return path, path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            self._quarantine_corrupt_artifact(path, self._next_corrupt_path(path.with_suffix(".corrupt")))
            self._fsync_directory(path.parent)
            raise ValueError(f"document content is not valid UTF-8: {document_id!r}") from exc

    def write_document(self, document_id: str, content: str) -> Path:
        path = self._resolve(document_id)
        self._atomic_write(path, content)
        return path

    def ensure_document(self, relative_path: str, content: str = "") -> Path:
        path = self._resolve(relative_path)
        if not path.exists():
            self._atomic_write(path, content)
        return path

    def create_document(self, relative_path: str, content: str = "") -> ProjectItem:
        path = self._resolve(relative_path)
        if path.exists():
            raise FileExistsError(f"document already exists: {relative_path!r}")
        self._atomic_write(path, content)
        return self._project_item(path)

    def import_document(self, source_path: str | Path, relative_path: str) -> ProjectItem:
        source = Path(source_path).expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(f"import source is not a file: {source_path!r}")
        try:
            content = source.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"import source is not valid UTF-8: {source_path!r}") from exc
        return self.create_document(relative_path, content)

    def rename_document(self, document_id: str, new_relative_path: str) -> ProjectItem:
        source = self._resolve(document_id)
        destination = self._resolve(new_relative_path)
        if not source.exists():
            raise FileNotFoundError(f"document does not exist: {document_id!r}")
        if destination.exists():
            raise FileExistsError(f"document already exists: {new_relative_path!r}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        os.replace(source, destination)
        self._fsync_directory(source.parent)
        self._fsync_directory(destination.parent)
        return self._project_item(destination)

    def trash_document(self, document_id: str) -> ProjectItem:
        source = self._resolve(document_id)
        if not source.exists():
            raise FileNotFoundError(f"document does not exist: {document_id!r}")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        trash_dir = self.project_root / ".trash" / "documents" / timestamp
        destination = trash_dir / source.name
        index = 2
        while destination.exists():
            destination = trash_dir / f"{source.stem}-{index}{source.suffix}"
            index += 1
        destination.parent.mkdir(parents=True, exist_ok=True)
        os.replace(source, destination)
        manifest_path = self._trash_manifest_path(destination)
        trashed_at = datetime.now(timezone.utc).isoformat()
        self._atomic_write_json(
            manifest_path,
            {
                "original_id": document_id,
                "trashed_at": trashed_at,
                "trash_id": self._item_id(destination),
            },
        )
        self._fsync_directory(source.parent)
        self._fsync_directory(destination.parent)
        return ProjectItem(
            id=self._item_id(destination),
            label=destination.name,
            item_type="document",
            path=str(destination),
            metadata={"trashed": True, "original_id": document_id, "trashed_at": trashed_at},
        )

    def list_trash_items(self) -> list[ProjectItem]:
        trash_root = self.project_root / ".trash" / "documents"
        items: list[ProjectItem] = []
        for path in self._document_paths(trash_root):
            metadata = self._read_trash_manifest(path)
            items.append(
                ProjectItem(
                    id=self._item_id(path),
                    label=path.name,
                    item_type="trash_document",
                    path=str(path),
                    metadata={
                        "trashed": True,
                        "original_id": metadata.get("original_id", ""),
                        "trashed_at": metadata.get("trashed_at", ""),
                    },
                )
            )
        return items

    def read_trash_document(self, trash_id: str) -> tuple[Path, str, dict[str, Any]]:
        path = self._resolve_trash_document_id(trash_id)
        if not path.exists():
            raise FileNotFoundError(f"trashed document does not exist: {trash_id!r}")
        return path, path.read_text(encoding="utf-8"), self._read_trash_manifest(path)

    def restore_trash_document(self, trash_id: str) -> ProjectItem:
        source = self._resolve_trash_document_id(trash_id)
        if not source.exists():
            raise FileNotFoundError(f"trashed document does not exist: {trash_id!r}")
        metadata = self._read_trash_manifest(source)
        original_id = metadata.get("original_id")
        if not isinstance(original_id, str) or not original_id.strip():
            raise ValueError(f"trashed document has no restore target: {trash_id!r}")
        destination = self._resolve(original_id)
        if destination.exists():
            raise FileExistsError(f"restore target already exists: {original_id!r}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        os.replace(source, destination)
        self._remove_trash_manifest(source)
        self._fsync_directory(source.parent)
        self._fsync_directory(destination.parent)
        return self._project_item(destination)

    def restore_trash_document_as(self, trash_id: str, new_relative_path: str) -> ProjectItem:
        source = self._resolve_trash_document_id(trash_id)
        if not source.exists():
            raise FileNotFoundError(f"trashed document does not exist: {trash_id!r}")
        destination = self._resolve(new_relative_path)
        if destination.exists():
            raise FileExistsError(f"restore target already exists: {new_relative_path!r}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        os.replace(source, destination)
        self._remove_trash_manifest(source)
        self._fsync_directory(source.parent)
        self._fsync_directory(destination.parent)
        return self._project_item(destination)

    def permanently_delete_trash_document(self, trash_id: str) -> ProjectItem:
        path = self._resolve_trash_document_id(trash_id)
        if not path.exists():
            raise FileNotFoundError(f"trashed document does not exist: {trash_id!r}")
        metadata = self._read_trash_manifest(path)
        item = ProjectItem(
            id=self._item_id(path),
            label=path.name,
            item_type="trash_document",
            path=str(path),
            metadata={
                "trashed": True,
                "original_id": metadata.get("original_id", ""),
                "trashed_at": metadata.get("trashed_at", ""),
            },
        )
        path.unlink()
        self._remove_trash_manifest(path)
        self._fsync_directory(path.parent)
        return item

    def _atomic_write(self, path: Path, content: str) -> None:
        if not isinstance(content, str):
            raise TypeError("document content must be a string")
        try:
            content.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ValueError("document content must be valid UTF-8 text") from exc
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
        try:
            with tmp.open("w", encoding="utf-8") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp, path)
            self._fsync_directory(path.parent)
        finally:
            try:
                if tmp.exists():
                    tmp.unlink()
            except OSError:
                pass

    def _atomic_write_json(self, path: Path, payload: dict[str, Any]) -> None:
        self._atomic_write(path, json.dumps(payload, sort_keys=True, indent=2))

    def _fsync_directory(self, path: Path) -> None:
        try:
            fd = os.open(path, os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(fd)
        except OSError:
            pass
        finally:
            os.close(fd)

    def _quarantine_corrupt_artifact(self, source: Path, destination: Path) -> None:
        try:
            os.replace(source, destination)
        except OSError as exc:
            raise ValueError(f"document state could not be quarantined: {source!r}") from exc

    def _quarantine_blocking_directory(self, path: Path) -> bool:
        try:
            if not path.exists() or path.is_dir():
                return False
        except OSError as exc:
            raise ValueError(f"project path cannot be probed safely: {path!r}") from exc
        self._quarantine_corrupt_artifact(path, self._next_corrupt_path(path.with_suffix(".corrupt")))
        return True

    def _next_corrupt_path(self, destination: Path) -> Path:
        if not destination.exists():
            return destination
        index = 1
        while True:
            candidate = destination.with_name(f"{destination.name}.{index}")
            if not candidate.exists():
                return candidate
            index += 1

    def _resolve(self, document_id: str) -> Path:
        path = Path(document_id)
        if path.is_absolute():
            try:
                rel_path = path.resolve().relative_to(self.project_root.resolve())
                document_id = str(rel_path)
            except ValueError:
                pass
        self._validate_document_id(document_id)
        path = Path(document_id)
        if not path.is_absolute():
            path = self.project_root / path
        try:
            if self._path_uses_symlink_alias(path.parent):
                raise ValueError(f"document path uses a symlink alias: {document_id!r}")
            if path.is_symlink():
                raise ValueError(f"document path is a symlink: {document_id!r}")
        except OSError as exc:
            raise ValueError(f"document path could not be probed: {document_id!r}") from exc
        resolved = path.resolve()
        try:
            resolved.relative_to(self.project_root.resolve())
        except ValueError as exc:
            raise ValueError(f"document path escapes project root: {document_id!r}") from exc
        return resolved

    def _resolve_trash_document_id(self, trash_id: str) -> Path:
        if not isinstance(trash_id, str):
            raise TypeError("trash id must be a string")
        if not trash_id.startswith(".trash/documents/"):
            raise ValueError(f"trash id must point inside project trash: {trash_id!r}")
        if "\\" in trash_id or "\x00" in trash_id or any(part in {"", ".", ".."} for part in trash_id.split("/")):
            raise ValueError(f"trash id contains an unsafe path: {trash_id!r}")
        path = self.project_root / trash_id
        resolved = path.resolve()
        trash_root = (self.project_root / ".trash" / "documents").resolve()
        try:
            resolved.relative_to(trash_root)
        except ValueError as exc:
            raise ValueError(f"trash path escapes project trash: {trash_id!r}") from exc
        if resolved.suffix.lower() not in _DOCUMENT_SUFFIXES:
            raise ValueError(f"trash id must identify a document: {trash_id!r}")
        if resolved.is_symlink():
            raise ValueError(f"trash path is a symlink: {trash_id!r}")
        return resolved

    def _validate_document_id(self, document_id: object) -> None:
        if not isinstance(document_id, str):
            raise TypeError("document id must be a string")
        try:
            document_id.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ValueError("document id must be valid UTF-8 text") from exc
        if not document_id.strip():
            raise ValueError("document id is required")
        if document_id != document_id.strip():
            raise ValueError("document id cannot contain leading/trailing spaces")
        if "\\" in document_id:
            raise ValueError(f"document path contains an unsupported separator: {document_id!r}")
        if any(unicodedata.category(char) in {"Cc", "Cf"} for char in document_id):
            raise ValueError(f"document path contains control characters: {document_id!r}")
        path = Path(document_id)
        if path.is_absolute():
            raise ValueError(f"document path must be relative: {document_id!r}")
        if any(part in {"", ".", ".."} for part in document_id.split("/")):
            raise ValueError(f"document path contains non-canonical segments: {document_id!r}")
        for part in path.parts:
            if part != part.strip():
                raise ValueError(f"document path contains a whitespace-padded segment: {document_id!r}")
            if part.startswith("."):
                raise ValueError(f"document path contains a reserved metadata segment: {document_id!r}")
            if part.endswith("."):
                raise ValueError(f"document path contains a dot-suffixed segment: {document_id!r}")
            if self._path_part_is_corrupt_artifact(part):
                raise ValueError(f"document path contains a reserved quarantine segment: {document_id!r}")
            if any(char in _NONPORTABLE_DOCUMENT_NAME_CHARS for char in part):
                raise ValueError(f"document path contains nonportable characters: {document_id!r}")
            if part.split(".", 1)[0].upper() in _WINDOWS_RESERVED_DOCUMENT_NAMES:
                raise ValueError(f"document path contains a reserved segment: {document_id!r}")

    def _path_part_is_corrupt_artifact(self, part: str) -> bool:
        suffixes = Path(part).suffixes
        return ".corrupt" in suffixes or part.endswith(".corrupt")

    def _path_uses_symlink_alias(self, path: Path) -> bool:
        candidates: list[Path] = []
        candidate = Path(path)
        while candidate != candidate.parent:
            candidates.append(candidate)
            candidate = candidate.parent
        candidates.append(candidate)
        for candidate in reversed(candidates):
            try:
                if self._is_platform_root_alias(candidate):
                    continue
                if candidate.is_symlink():
                    return True
            except OSError:
                return True
        return False

    def _is_platform_root_alias(self, path: Path) -> bool:
        try:
            if path.parent != path.parent.parent:
                return False
            resolved = path.resolve(strict=True)
        except OSError:
            return False
        return (str(path), str(resolved)) in {
            ("/var", "/private/var"),
            ("/tmp", "/private/tmp"),
        }

    def _item_id(self, path: Path) -> str:
        try:
            return str(Path(path).resolve().relative_to(self.project_root.resolve()))
        except ValueError:
            return str(path)

    def _project_item(self, path: Path) -> ProjectItem:
        return ProjectItem(
            id=self._item_id(path),
            label=path.name,
            item_type="document",
            path=str(path),
        )

    def _trash_manifest_path(self, path: Path) -> Path:
        return path.with_name(f"{path.name}.trash.json")

    def _read_trash_manifest(self, path: Path) -> dict[str, Any]:
        manifest_path = self._trash_manifest_path(path)
        if not manifest_path.exists():
            return {}
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def _remove_trash_manifest(self, path: Path) -> None:
        manifest_path = self._trash_manifest_path(path)
        try:
            manifest_path.unlink()
        except FileNotFoundError:
            return
        except OSError:
            return

    def _document_paths(self, root: Path, *, exclude_paths: Iterable[Path] = ()) -> list[Path]:
        root = Path(root)
        if not root.exists():
            return []
        project_root = self.project_root.resolve()
        try:
            resolved_root = root.resolve()
        except (OSError, RuntimeError):
            return []
        try:
            resolved_root.relative_to(project_root)
        except ValueError:
            return []
        excluded = self._resolvable_excluded_paths(exclude_paths)
        candidates: list[tuple[str, Path, Path]] = []
        iterator = iter(root.rglob("*"))
        while True:
            try:
                path = next(iterator)
            except StopIteration:
                break
            except (OSError, RuntimeError):
                continue
            try:
                is_file = path.is_file()
                is_symlink = path.is_symlink()
            except (OSError, RuntimeError):
                continue
            try:
                relative_parts = path.relative_to(root).parts
            except ValueError:
                continue
            if any(self._path_part_is_corrupt_artifact(part) for part in relative_parts):
                continue
            if not is_file or is_symlink or path.suffix.lower() not in _DOCUMENT_SUFFIXES:
                continue
            try:
                resolved_path = path.resolve()
            except (OSError, RuntimeError):
                # Skip files whose target cannot be resolved cleanly. A single
                # malformed or concurrently disappearing path should not abort
                # discovery for the rest of the project.
                continue
            if not resolved_path.is_relative_to(resolved_root):
                continue
            if any(resolved_path.is_relative_to(excluded_path) for excluded_path in excluded):
                continue
            candidates.append((str(Path(*relative_parts)), path, resolved_path))
        deduplicated: list[Path] = []
        seen_resolved_paths: set[Path] = set()
        for _, path, resolved_path in sorted(candidates, key=lambda item: item[0]):
            if resolved_path in seen_resolved_paths:
                continue
            seen_resolved_paths.add(resolved_path)
            deduplicated.append(path)
        return deduplicated

    def _resolvable_excluded_paths(self, exclude_paths: Iterable[Path]) -> tuple[Path, ...]:
        resolved_paths: list[Path] = []
        try:
            iterator = iter(exclude_paths)
        except (OSError, RuntimeError, TypeError, ValueError):
            return ()
        attempts = 0
        while attempts < _MAX_EXCLUDE_PATHS:
            attempts += 1
            try:
                candidate = next(iterator)
            except StopIteration:
                break
            except (OSError, RuntimeError, TypeError, ValueError):
                break
            try:
                resolved_paths.append(Path(candidate).resolve())
            except (OSError, RuntimeError, TypeError, ValueError):
                continue
        return tuple(resolved_paths)
