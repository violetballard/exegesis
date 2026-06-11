from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
from uuid import uuid4

from exegesis_textual.layout.modals import (
    DEFAULT_IMPORT_CATEGORY,
    IMPORTABLE_PROJECT_CATEGORIES,
    DeleteFolderConfirmModal,
    DeleteProjectConfirmModal,
    DuplicateDocumentModal,
    DuplicateProjectModal,
    ImportProgressModal,
    NewProjectModal,
    NewProjectFolderModal,
    OpenProjectModal,
    PermanentDeleteTrashConfirmModal,
    ProjectBrowserAction,
    RenameProjectEntryModal,
    TrashDocumentModal,
    UpdateProjectItemModal,
)
from exegesis_textual.panes.document_pane import (
    CURRENT_DRAFT_SLUG,
    DOCUMENT_FIXTURES,
    DocumentPane,
    register_document_fixture,
)
from exegesis_textual.panes.basket_pane import BasketPane
from exegesis_textual.panes.project_pane import (
    CURRENT_DRAFT_BULLETS,
    CURRENT_DRAFT_LOCATION,
    CURRENT_DRAFT_NAME,
    CURRENT_DRAFT_SUMMARY,
    PROJECT_ENTRIES,
    PROJECT_NAME,
    ProjectEntry,
    ProjectBrowserTree,
    ProjectNodeInfo,
    ProjectPane,
)
from exegesis_textual.services.imports import (
    MARKDOWN_EXTENSIONS,
    importable_markdown_files_in_folder,
    is_markdown_file,
    path_has_hidden_part,
)
from exegesis_textual.services.model_settings import (
    LOCAL_OPENAI_PROVIDER,
    ModelSettings,
    load_model_settings,
    provider_profile_from_settings,
)
from exegesis_textual.services.project_fixtures import (
    DEFAULT_EMPTY_PROJECT_NAME,
    DEFAULT_PROJECT_DOCUMENT_IDS,
    DEFAULT_PROJECT_NAMES,
    NEW_PROJECT_CURRENT_DRAFT_CONTENT,
    NEW_PROJECT_CURRENT_DRAFT_ENTRY,
    PROJECT_MANIFEST_PATH,
    default_project_fixture_content,
)
from exegesis_textual.services.projects import (
    CONFIDENTIALITY_CONFIDENTIAL,
    CONFIDENTIALITY_NON_CONFIDENTIAL,
    ProjectRecord,
    is_local_developer_mode,
    normalize_project_confidentiality,
    safe_project_dir_name,
    save_textual_last_project_name,
    save_textual_projects_dir,
    textual_last_project_name,
    textual_projects_dir,
)


class ProjectControllerMixin:
    def _selected_project_category(self) -> str:
        category = self.query_one(ProjectPane).selected_category()
        return category if category in IMPORTABLE_PROJECT_CATEGORIES else DEFAULT_IMPORT_CATEGORY

    def _repo_root(self) -> Path:
        return Path(__file__).resolve().parents[4]

    def _project_root_for_name(self, project_name: str) -> Path:
        if project_name == getattr(self, "_current_project_name", None) and getattr(self, "_current_project_slug", None):
            return self._projects_base_dir / str(self._current_project_slug)
        return self._projects_base_dir / self._safe_project_dir_name(project_name)

    def _project_root_for_slug(self, slug: str) -> Path:
        return self._projects_base_dir / slug

    def _project_record_for_slug(self, slug: str) -> ProjectRecord | None:
        return next((record for record in self._project_records if record.slug == slug), None)

    def _project_record_for_name(self, project_name: str) -> ProjectRecord | None:
        return next((record for record in self._project_records if record.name == project_name), None)

    def _project_slug_for_name(self, project_name: str) -> str | None:
        record = self._project_record_for_name(project_name)
        return record.slug if record is not None else None

    def _safe_project_dir_name(self, project_name: str) -> str:
        return safe_project_dir_name(project_name)

    def _empty_project_fallback_name(self) -> str:
        return PROJECT_NAME if is_local_developer_mode() else DEFAULT_EMPTY_PROJECT_NAME

    def _has_project_directories(self) -> bool:
        try:
            return any(path.is_dir() and not path.name.startswith(".") for path in self._projects_base_dir.iterdir())
        except OSError:
            return False

    def _initial_project_name(self) -> str:
        if is_local_developer_mode():
            self._ensure_demo_project_available()
            self._refresh_project_names()
            return PROJECT_NAME
        self._refresh_project_names()
        last_project_name = textual_last_project_name(self._repo_root())
        if last_project_name in self._project_names:
            return last_project_name
        return self._project_names[0] if self._project_names else self._empty_project_fallback_name()

    def _project_manifest_path(self, project_root: Path) -> Path:
        return project_root / PROJECT_MANIFEST_PATH

    def _write_project_manifest(self, project_root: Path, project_name: str, confidentiality: str | None = None) -> None:
        manifest_path = self._project_manifest_path(project_root)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        if confidentiality is None:
            confidentiality = self._project_confidentiality_from_root(project_root)
        manifest_path.write_text(
            json.dumps(
                {
                    "name": project_name,
                    "slug": project_root.name,
                    "confidentiality": normalize_project_confidentiality(confidentiality),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    def _project_name_from_root(self, project_root: Path) -> str:
        manifest_path = self._project_manifest_path(project_root)
        try:
            raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            if project_root.name == self._safe_project_dir_name(PROJECT_NAME):
                return PROJECT_NAME
            return project_root.name.replace("-", " ").strip().title() or project_root.name
        name = raw.get("name")
        return name if isinstance(name, str) and name.strip() else project_root.name

    def _project_confidentiality_from_root(self, project_root: Path) -> str:
        manifest_path = self._project_manifest_path(project_root)
        try:
            raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return CONFIDENTIALITY_NON_CONFIDENTIAL
        return normalize_project_confidentiality(raw.get("confidentiality"))

    def _refresh_project_names(self, *, include_fallback: bool = True) -> None:
        projects_root = self._projects_base_dir
        projects_root.mkdir(parents=True, exist_ok=True)
        records = [
            ProjectRecord(self._project_name_from_root(path), path.name, self._project_confidentiality_from_root(path))
            for path in sorted(projects_root.iterdir(), key=lambda item: item.name.lower())
            if path.is_dir() and not path.name.startswith(".")
        ]
        self._project_records = records
        self._project_names = [record.name for record in records]
        if not records and include_fallback:
            self._project_names = [self._empty_project_fallback_name()]

    def _ensure_demo_project_available(self) -> None:
        previous_project_name = getattr(self, "_current_project_name", None)
        previous_project_slug = getattr(self, "_current_project_slug", None)
        previous_project_root = getattr(self, "_project_root", None)
        try:
            self._current_project_name = PROJECT_NAME
            self._current_project_slug = self._safe_project_dir_name(PROJECT_NAME)
            self._project_root = self._project_root_for_name(PROJECT_NAME)
            self._ensure_default_project_documents()
        finally:
            if previous_project_name is not None:
                self._current_project_name = previous_project_name
            self._current_project_slug = previous_project_slug
            if previous_project_root is not None:
                self._project_root = previous_project_root

    def _ensure_default_project_documents(self) -> None:
        if self._current_project_name != PROJECT_NAME:
            return
        self._write_project_manifest(self._project_root, PROJECT_NAME, CONFIDENTIALITY_NON_CONFIDENTIAL)
        for entry in PROJECT_ENTRIES:
            document_id = DEFAULT_PROJECT_DOCUMENT_IDS.get(entry.slug)
            if document_id is None:
                continue
            path = self._project_root / document_id
            if path.exists():
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(default_project_fixture_content(entry.slug), encoding="utf-8")

    def _map_default_project_documents(self) -> None:
        if self._current_project_name != PROJECT_NAME:
            return
        for entry in PROJECT_ENTRIES:
            document_id = DEFAULT_PROJECT_DOCUMENT_IDS.get(entry.slug)
            if document_id is None:
                continue
            path = self._project_root / document_id
            content = default_project_fixture_content(entry.slug)
            if path.exists():
                try:
                    content = path.read_text(encoding="utf-8")
                except OSError:
                    pass
            category = self._category_for_document_id(document_id) or entry.category
            register_document_fixture(
                slug=entry.slug,
                title=entry.title,
                location=document_id,
                summary=entry.summary,
                content=content,
                document_type=self._category_document_type(category),
                is_transcript=(category == "Transcripts"),
            )
            self._document_id_by_slug[entry.slug] = document_id

    def _ensure_minimal_project_documents(self) -> None:
        self._write_project_manifest(
            self._project_root,
            self._current_project_name,
            getattr(self, "_current_project_confidentiality", CONFIDENTIALITY_NON_CONFIDENTIAL),
        )
        draft_path = self._project_root / "drafts" / "current_draft.md"
        if not draft_path.exists():
            draft_path.parent.mkdir(parents=True, exist_ok=True)
            draft_path.write_text(NEW_PROJECT_CURRENT_DRAFT_CONTENT, encoding="utf-8")

    def _map_minimal_project_documents(self) -> None:
        document_id = "drafts/current_draft.md"
        path = self._project_root / document_id
        content = NEW_PROJECT_CURRENT_DRAFT_CONTENT
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8")
            except OSError:
                pass
        register_document_fixture(
            slug=NEW_PROJECT_CURRENT_DRAFT_ENTRY.slug,
            title=NEW_PROJECT_CURRENT_DRAFT_ENTRY.title,
            location=document_id,
            summary=NEW_PROJECT_CURRENT_DRAFT_ENTRY.summary,
            content=content,
            document_type="draft",
            is_transcript=False,
        )
        self._document_id_by_slug[NEW_PROJECT_CURRENT_DRAFT_ENTRY.slug] = document_id

    def _load_engine_project_entries(self) -> None:
        if not self.is_mounted:
            return
        project_pane = self.query_one(ProjectPane)
        self._load_project_folders(project_pane)
        for item in self._engine_adapter.list_project_items():
            if item.item_type != "document":
                continue
            if item.id in self._document_id_by_slug.values():
                continue
            category = self._category_for_document_id(item.id)
            if category is None:
                continue
            slug = self._next_dynamic_slug(self._category_slug_prefix(category))
            try:
                content = Path(item.path).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            summary = f"{item.label} in {category.lower()}."
            self._document_id_by_slug[slug] = item.id
            register_document_fixture(
                slug=slug,
                title=item.label,
                location=item.id,
                summary=summary,
                content=content,
                document_type=self._category_document_type(category),
                is_transcript=(category == "Transcripts"),
            )
            project_pane.add_project_entry(
                category=category,
                slug=slug,
                title=item.label,
                location=item.id,
                summary=summary,
                bullets=(
                    f"Category: {category}",
                    f"Location: {item.id}",
                    "Loaded from the real project folder.",
                ),
            )
        for item in self._engine_adapter.list_trash_items():
            if item.id in self._trash_id_by_slug.values():
                continue
            self._register_trash_entry(item.id, item.label, dict(item.metadata))

    def _load_project_folders(self, project_pane: ProjectPane) -> None:
        for category in IMPORTABLE_PROJECT_CATEGORIES:
            category_root = self._project_root / self._category_folder(category)
            if not category_root.exists():
                continue
            for folder in sorted((path for path in category_root.rglob("*") if path.is_dir()), key=lambda path: str(path).casefold()):
                try:
                    relative = folder.relative_to(category_root)
                except ValueError:
                    continue
                if any(part.startswith(".") for part in relative.parts):
                    continue
                project_pane.add_folder(category=category, folder_path=relative.as_posix())

    def _register_trash_entry(
        self,
        trash_id: str,
        title: str,
        metadata: dict[str, object],
        *,
        old_source_slug: str | None = None,
    ) -> str:
        slug = self._next_dynamic_slug("trash")
        display_title = str(metadata.get("display_label") or title)
        original_id = str(metadata.get("original_id") or "")
        trashed_at = str(metadata.get("trashed_at") or "")
        content = self._read_trash_document_content_by_id(trash_id)
        document_type = self._document_type_for_document_id(original_id)
        category = self._category_for_document_id(original_id)
        folder_path = self._folder_path_for_document_id(original_id) if category is not None else ""
        self._trash_id_by_slug[slug] = trash_id
        self._trash_metadata_by_slug[slug] = dict(metadata)
        register_document_fixture(
            slug=slug,
            title=display_title,
            location=trash_id,
            summary=f"{display_title} is in the project trash. Double-select to restore or permanently delete it.",
            content=content,
            document_type=document_type,
            is_transcript=(document_type == "transcript"),
        )
        self.query_one(DocumentPane).set_document_view_status(slug, "trashed")
        self.query_one(ProjectPane).add_trash_entry(
            slug=slug,
            title=display_title,
            location=original_id,
            summary=f"{display_title} is in the project trash. Double-select to restore or permanently delete it.",
            bullets=(
                f"Trash location: {trash_id}",
            ),
            category=category,
            folder_path=folder_path,
        )
        self._rebind_basket_sources_to_trash(
            old_source_document_id=original_id or None,
            old_source_document_slug=old_source_slug,
            trash_source_document_slug=slug,
            source_title=display_title,
        )
        return slug

    def _project_title_for_slug(self, slug: str | None) -> str | None:
        if not slug:
            return None
        try:
            node = self.query_one(ProjectBrowserTree)._entry_nodes.get(slug)
        except Exception:
            node = None
        if node is not None and node.data is not None and node.data.title:
            return node.data.title
        fixture = DOCUMENT_FIXTURES.get(slug)
        if fixture is not None and fixture.title:
            return fixture.title
        return None

    def _rebind_basket_sources_to_trash(
        self,
        *,
        old_source_document_id: str | None,
        old_source_document_slug: str | None,
        trash_source_document_slug: str,
        source_title: str,
    ) -> None:
        changed = False
        updated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        for item in self._engine_adapter.state.basket.items:
            if not self._basket_item_matches_source(
                item,
                source_document_id=old_source_document_id,
                source_document_slug=old_source_document_slug,
            ):
                continue
            current = str(item.payload.get("source_status") or "current")
            if current == "source_deleted":
                continue
            item.payload["source_document_slug"] = trash_source_document_slug
            item.payload["source_title"] = source_title
            item.payload["source_status"] = "trashed"
            item.payload["source_status_updated_at"] = updated_at
            changed = True
        if changed:
            self._refresh_basket_from_engine()
            self._refresh_notebook_context_meter()

    def _category_for_document_id(self, document_id: str) -> str | None:
        top_level = Path(document_id).parts[0] if Path(document_id).parts else ""
        return {
            "drafts": "Drafts",
            "memos": "Memos",
            "summaries": "Summaries",
            "transcripts": "Transcripts",
            "literature": "Literature",
        }.get(top_level)

    def _category_slug_prefix(self, category: str) -> str:
        return {
            "Drafts": "draft",
            "Memos": "memo",
            "Summaries": "summary",
            "Transcripts": "transcript",
            "Literature": "literature",
        }[category]

    def _category_document_type(self, category: str) -> str:
        return self._category_slug_prefix(category)

    def _category_folder(self, category: str) -> str:
        return {
            "Drafts": "drafts",
            "Memos": "memos",
            "Summaries": "summaries",
            "Transcripts": "transcripts",
            "Literature": "literature",
        }[category]

    def _target_document_id(self, category: str, title: str, folder: str = "", *, allow_extensionless: bool = False) -> str:
        category_root = Path(self._category_folder(category))
        folder_path = self._safe_folder_path(folder)
        filename = self._safe_document_filename(
            title,
            self._category_document_type(category),
            allow_extensionless=allow_extensionless,
        )
        return str(category_root / folder_path / filename) if folder_path else str(category_root / filename)

    def _target_document_path(self, category: str, title: str, folder: str = "") -> Path:
        return self._project_child_path(self._target_document_id(category, title, folder))

    def _project_child_path(self, *parts: str | Path) -> Path:
        root = self._project_root.resolve()
        target = self._project_root.joinpath(*parts).resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"Project path escaped project root: {target}") from exc
        return target

    def _is_self_import(self, source: Path, category: str, folder: str = "") -> bool:
        target = self._target_document_path(category, source.name, folder)
        try:
            return source.resolve() == target.resolve()
        except OSError:
            return False

    def _safe_folder_path(self, folder: str | Path | None) -> Path:
        if folder is None:
            return Path("")
        raw = str(folder).strip().strip("/")
        if not raw or raw == ".":
            return Path("")
        parts: list[str] = []
        for part in Path(raw).parts:
            if part in {"", ".", ".."}:
                continue
            safe = re.sub(r"[^A-Za-z0-9._ -]+", "-", part).strip(" .-_")
            if safe:
                parts.append(safe)
        return Path(*parts) if parts else Path("")

    def _folder_path_has_suffix(self, folder_path: Path, suffix: Path) -> bool:
        folder_parts = folder_path.parts
        suffix_parts = suffix.parts
        return bool(folder_parts and suffix_parts and len(suffix_parts) <= len(folder_parts) and folder_parts[-len(suffix_parts) :] == suffix_parts)

    def _category_folder_path_exists(self, category: str, folder_path: Path) -> bool:
        if not folder_path.parts:
            return False
        return (self._project_root / self._category_folder(category) / folder_path).is_dir()

    def _resolve_model_document_folder_path(self, category: str, requested_folder: object | None) -> str:
        """Resolve model-supplied folder hints without accidentally nesting the active folder."""
        selected = self._safe_folder_path(self._selected_project_folder_path(category))
        if requested_folder is None:
            return selected.as_posix()
        requested = self._safe_folder_path(str(requested_folder))
        if not requested.parts:
            return ""
        if selected.parts and self._folder_path_has_suffix(selected, requested):
            return selected.as_posix()
        if selected.parts and requested.parts and requested.parts[0] == selected.parts[0]:
            return requested.as_posix()
        if (
            selected.parts
            and len(requested.parts) == 1
            and self._category_folder_path_exists(category, selected / requested)
            and not self._category_folder_path_exists(category, requested)
        ):
            return (selected / requested).as_posix()
        return requested.as_posix()

    def _resolve_model_folder_creation_path(self, category: str, name: str, parent_folder: object | None = None) -> Path:
        requested = self._safe_folder_path(name)
        if not requested.parts:
            return Path("")
        if parent_folder is None or not str(parent_folder).strip():
            parent = self._safe_folder_path(self._selected_project_folder_path(category))
            explicit_parent = False
        else:
            parent = self._safe_folder_path(str(parent_folder))
            explicit_parent = True
        if parent.parts and self._folder_path_has_suffix(parent, requested):
            return parent
        if parent.parts and requested.parts and requested.parts[0] == parent.parts[0]:
            return requested
        if not explicit_parent and len(requested.parts) > 1:
            return requested
        return self._safe_folder_path(parent / requested)

    def _folder_path_for_document_id(self, document_id: str) -> str:
        category = self._category_for_document_id(document_id)
        if category is None:
            return ""
        category_root = self._category_folder(category)
        parent = Path(document_id).parent
        if str(parent) in {"", ".", category_root}:
            return ""
        try:
            return Path(*parent.parts[1:]).as_posix()
        except TypeError:
            return ""

    def _folder_choices_for_document_id(self, document_id: str) -> tuple[str, ...]:
        category = self._category_for_document_id(document_id)
        if category is None:
            return ("",)
        category_dir = self._project_root / self._category_folder(category)
        folders = {"", self._folder_path_for_document_id(document_id)}
        if category_dir.exists():
            for path in category_dir.rglob("*"):
                if not path.is_dir():
                    continue
                try:
                    relative = path.relative_to(category_dir)
                except ValueError:
                    continue
                if any(part.startswith(".") for part in relative.parts):
                    continue
                folders.add(relative.as_posix())
        return tuple(sorted(folders, key=lambda folder: (Path(folder).parts, folder.casefold())))

    def _selected_project_folder_path(self, category: str) -> str:
        project_pane = self.query_one(ProjectPane)
        selected_category = project_pane.selected_category()
        if selected_category != category:
            return ""
        folder = project_pane.selected_folder_path()
        category_root = self._category_folder(category)
        if folder == category_root:
            return ""
        if folder.startswith(f"{category_root}/"):
            return folder[len(category_root) + 1 :]
        return folder

    def _safe_document_filename(self, title: str, default_stem: str = "document", *, allow_extensionless: bool = False) -> str:
        raw = Path(title.strip()).name
        suffix = Path(raw).suffix or ("" if allow_extensionless else ".md")
        stem = Path(raw).stem if Path(raw).suffix else raw
        safe_stem = re.sub(r"[^A-Za-z0-9._ -]+", "-", stem).strip(" .-_") or default_stem
        return f"{safe_stem}{suffix}"

    def _local_endpoint_configured(self) -> bool:
        try:
            return load_model_settings(self._repo_root()).local_endpoint_configured()
        except Exception:
            return False

    def _current_project_is_confidential(self) -> bool:
        return getattr(self, "_current_project_confidentiality", CONFIDENTIALITY_NON_CONFIDENTIAL) == CONFIDENTIALITY_CONFIDENTIAL

    def _handle_new_project_result(self, result: tuple[str, str] | str | None) -> None:
        if result is None:
            return
        if isinstance(result, tuple):
            name, confidentiality = result
        else:
            name = result
            confidentiality = CONFIDENTIALITY_NON_CONFIDENTIAL
        project_name = name.strip() or DEFAULT_EMPTY_PROJECT_NAME
        self._remove_initial_placeholder_project_root()
        project_slug = self._dedupe_project_folder_slug(project_name)
        self._prompt_for_initial_project = False
        self._switch_project(project_name, created=True, project_slug=project_slug, confidentiality=confidentiality)

    def _remove_initial_placeholder_project_root(self) -> None:
        placeholder = getattr(self, "_initial_placeholder_project_root", None)
        if placeholder is None:
            return
        self._initial_placeholder_project_root = None
        placeholder = Path(placeholder)
        if placeholder.name != self._safe_project_dir_name(DEFAULT_EMPTY_PROJECT_NAME):
            return
        try:
            placeholder.relative_to(self._projects_base_dir)
        except ValueError:
            return
        if not placeholder.exists():
            return
        try:
            shutil.rmtree(placeholder)
        except OSError:
            return

    def _handle_open_project_result(self, result: ProjectBrowserAction | str | None) -> None:
        if result is None:
            return
        self._refresh_project_names()
        if isinstance(result, tuple):
            action, slug_or_name = result
            record = self._project_record_for_slug(slug_or_name)
            if record is None:
                record = self._project_record_for_name(slug_or_name)
        else:
            action, slug_or_name = "open", result
            record = self._project_record_for_name(slug_or_name)
        if record is None:
            self._set_status(f"Project is not available in the Exegesis project folder: {slug_or_name}")
            return
        if action == "open":
            if record.is_confidential and not self._local_endpoint_configured():
                self._set_status("Configure a loopback Local OpenAI Compatible Endpoint before opening a confidential project.")
                return
            self._switch_project(record.name, created=False, project_slug=record.slug)
        elif action == "delete":
            self.push_screen(
                DeleteProjectConfirmModal(record),
                callback=lambda confirmed, record=record: self._handle_project_delete_confirmation(record, confirmed),
            )

    def _handle_import_result(self, result: tuple[object, ...] | None) -> None:
        if result is None:
            return
        path_payload, category, mode, source_root = self._parse_import_result(result)
        destination_folder = self._selected_project_folder_path(category)
        if isinstance(path_payload, str):
            self.run_worker(
                self._import_project_document(Path(path_payload), category=category, destination_folder=destination_folder),
                thread=False,
                exclusive=False,
                group="project-import",
            )
            return
        path_texts = path_payload
        self.run_worker(
            self._run_bulk_import(
                [Path(str(path_text)) for path_text in path_texts],
                category=category,
                destination_folder=destination_folder,
                mode=mode,
                source_root=source_root,
            ),
            thread=False,
            exclusive=False,
            group="project-import",
        )

    def _parse_import_result(self, result: tuple[object, ...]) -> tuple[object, str, str, Path | None]:
        path_payload = result[0]
        category = str(result[1]) if len(result) > 1 else DEFAULT_IMPORT_CATEGORY
        mode = str(result[2]) if len(result) > 2 and result[2] is not None else "selected"
        source_root = Path(str(result[3])).expanduser().resolve() if len(result) > 3 and result[3] else None
        return path_payload, category, mode, source_root

    async def _run_bulk_import(
        self,
        paths: list[Path],
        *,
        category: str,
        destination_folder: str = "",
        mode: str = "selected",
        source_root: Path | None = None,
    ) -> None:
        progress_modal = ImportProgressModal(total=len(paths), category=category)
        await self.push_screen(progress_modal)
        await self._import_project_documents(
            paths,
            category=category,
            destination_folder=destination_folder,
            mode=mode,
            source_root=source_root,
            progress_modal=progress_modal,
        )

    def _handle_projects_directory_result(self, projects_dir: Path | None) -> None:
        if projects_dir is None:
            return
        try:
            selected = projects_dir.expanduser().resolve()
            selected.mkdir(parents=True, exist_ok=True)
            save_textual_projects_dir(selected, self._repo_root())
        except OSError as exc:
            self._set_status(f"Could not change projects directory: {exc}")
            return
        self._projects_base_dir = selected
        if is_local_developer_mode():
            self._ensure_demo_project_available()
        elif not self._has_project_directories():
            self._set_status(f"Projects directory set to {selected}. Create a project to continue.")
            self.push_screen(NewProjectModal(local_endpoint_configured=self._local_endpoint_configured()), callback=self._handle_new_project_result)
            return
        self._refresh_project_names()
        project_name = self._project_names[0] if self._project_names else DEFAULT_EMPTY_PROJECT_NAME
        self._switch_project(project_name, created=False)
        self._set_status(f"Projects directory set to {selected}")

    def _handle_active_project_rename_result(self, result: str | None) -> None:
        if result is None:
            return
        new_name = result.strip()
        if not new_name or new_name == self._current_project_name:
            return
        self._rename_active_project(new_name, replace_existing=False)

    def _handle_duplicate_project_rename_result(
        self,
        requested_name: str,
        result: tuple[str, str | None] | None,
    ) -> None:
        if result is None:
            self._set_status("Project rename cancelled.")
            return
        action, replacement_name = result
        if action == "replace":
            self._rename_active_project(requested_name, replace_existing=True)
            return
        if action == "rename":
            next_name = (replacement_name or requested_name).strip()
            if not next_name:
                self._set_status("Project rename cancelled.")
                return
            self._rename_active_project(next_name, replace_existing=False)

    def _rename_active_project(self, new_name: str, *, replace_existing: bool) -> None:
        old_root = self._project_root
        new_root = self._project_root_for_name(new_name)
        try:
            same_root = old_root.resolve() == new_root.resolve()
        except OSError:
            same_root = old_root == new_root
        if same_root:
            self._write_project_manifest(old_root, new_name)
            self._current_project_name = new_name
            self.query_one(ProjectPane).set_project_name(new_name)
            self._refresh_project_names()
            save_textual_last_project_name(new_name, self._repo_root())
            self._set_status(f"Renamed project to {new_name}.")
            return
        if new_root.exists() and not replace_existing:
            self.push_screen(
                DuplicateProjectModal(new_name, new_root.name),
                callback=lambda duplicate_result, requested_name=new_name: self._handle_duplicate_project_rename_result(
                    requested_name,
                    duplicate_result,
                ),
            )
            self._set_status(f"Rename conflict: {new_root.name} already exists.")
            return
        self._save_dirty_documents()
        try:
            old_root.parent.mkdir(parents=True, exist_ok=True)
            if new_root.exists():
                shutil.rmtree(new_root)
            os.replace(old_root, new_root)
            self._write_project_manifest(new_root, new_name)
        except OSError as exc:
            self._set_status(f"Could not rename project: {exc}")
            return
        replaced = " Replaced the existing project folder." if replace_existing else ""
        self._current_project_name = new_name
        self._current_project_slug = new_root.name
        self._project_root = new_root
        self._engine_adapter.open_project(self._project_root)
        self.query_one(ProjectPane).set_project_name(new_name)
        self._refresh_project_names()
        save_textual_last_project_name(new_name, self._repo_root())
        self._set_status(f"Renamed project to {new_name}.{replaced}")

    def _handle_project_delete_confirmation(self, project: ProjectRecord, confirmed: bool) -> None:
        if not confirmed:
            self._set_status(f"Kept project: {project.name}.")
            self._open_project_browser_after_project_delete()
            return
        self._delete_project(project)
        self._open_project_browser_after_project_delete()

    def _open_project_browser_after_project_delete(self) -> None:
        if is_local_developer_mode():
            self._ensure_demo_project_available()
        self._refresh_project_names(include_fallback=False)
        if self._project_records:
            self.push_screen(OpenProjectModal(self._project_records, local_endpoint_configured=self._local_endpoint_configured()), callback=self._handle_open_project_result)
        else:
            self.push_screen(NewProjectModal(local_endpoint_configured=self._local_endpoint_configured()), callback=self._handle_new_project_result)

    def _handle_duplicate_import_result(
        self,
        path: Path,
        category: str,
        result: tuple[str, str | None] | None,
        destination_folder: str = "",
    ) -> None:
        if result is None:
            self._set_status("Import cancelled.")
            return
        action, new_title = result
        self.run_worker(
            self._import_project_document(
                path,
                category=category,
                destination_folder=destination_folder,
                duplicate_action=action,
                duplicate_title=new_title,
            ),
            thread=False,
            exclusive=False,
            group="project-import",
        )

    def _handle_duplicate_batch_import_result(
        self,
        paths: list[Path],
        category: str,
        index: int,
        result: tuple[str, str | None] | None,
        progress_modal: ImportProgressModal | None = None,
        imported_count: int = 0,
        skipped_count: int = 0,
        destination_folder: str = "",
        mode: str = "selected",
        source_root: Path | None = None,
        replace_all_duplicates: bool = False,
        skip_all_duplicates: bool = False,
    ) -> None:
        if result is None:
            self._finish_import_progress(progress_modal, "Import cancelled.")
            self._set_status("Import cancelled.")
            return
        action, _ = result
        if action == "cancel_import":
            message = f"Import stopped. Imported {imported_count} markdown files into {category}."
            if skipped_count:
                message = f"{message} Skipped {skipped_count}."
            if progress_modal is not None:
                progress_modal.update_progress(
                    current="Import stopped.",
                    processed=index,
                    imported=imported_count,
                    skipped=skipped_count,
                    status=message,
                )
            self._finish_import_progress(progress_modal, message)
            self._set_status(message)
            return
        self.run_worker(
            self._import_project_documents(
                paths,
                category=category,
                destination_folder=destination_folder,
                mode=mode,
                source_root=source_root,
                start_index=index,
                duplicate_result=result,
                progress_modal=progress_modal,
                imported_count=imported_count,
                skipped_count=skipped_count,
                replace_all_duplicates=replace_all_duplicates or action == "replace_all",
                skip_all_duplicates=skip_all_duplicates or action == "skip_all",
            ),
            thread=False,
            exclusive=False,
            group="project-import",
        )

    def _finish_import_progress(self, progress_modal: ImportProgressModal | None, message: str) -> None:
        if progress_modal is None:
            return
        progress_modal.complete(message)
        if self.screen is progress_modal:
            self.pop_screen()

    def _dedupe_project_folder_slug(self, raw_name: str) -> str:
        base = self._safe_project_dir_name(raw_name.strip() or DEFAULT_EMPTY_PROJECT_NAME)
        self._refresh_project_names()
        if not self._project_root_for_slug(base).exists():
            return base
        index = 2
        while self._project_root_for_slug(f"{base}-{index}").exists():
            index += 1
        return f"{base}-{index}"

    def _activate_local_openai_for_confidential_project(self) -> None:
        backend_getter = getattr(self, "_model_backend", None)
        if not callable(backend_getter):
            return
        backend = backend_getter()
        if backend is None:
            return
        settings = backend.model_settings()
        profile = provider_profile_from_settings(settings, LOCAL_OPENAI_PROVIDER)
        backend.save_model_settings(
            ModelSettings(
                provider=LOCAL_OPENAI_PROVIDER,
                model=profile.model,
                reasoning_effort=profile.reasoning_effort,
                context_window_tokens=profile.context_window_tokens,
                settings_prompt_dismissed=settings.settings_prompt_dismissed,
                endpoint_url=profile.endpoint_url,
                reasoning_start_tag=profile.reasoning_start_tag,
                reasoning_end_tag=profile.reasoning_end_tag,
                profiles=dict(settings.profiles),
            )
        )

    def _switch_project(
        self,
        project_name: str,
        *,
        created: bool,
        project_slug: str | None = None,
        confidentiality: str | None = None,
    ) -> None:
        self._save_dirty_documents()
        self._current_project_name = project_name
        self._current_project_slug = project_slug or self._project_slug_for_name(project_name)
        self._project_root = self._project_root_for_name(project_name)
        self._current_project_confidentiality = normalize_project_confidentiality(
            confidentiality if confidentiality is not None else self._project_confidentiality_from_root(self._project_root)
        )
        self._document_id_by_slug.clear()
        self._trash_id_by_slug.clear()
        self._trash_metadata_by_slug.clear()
        self._dirty_document_slugs.clear()
        if self._current_project_name == PROJECT_NAME:
            self._ensure_default_project_documents()
            self._map_default_project_documents()
            self.query_one(ProjectPane).reset_project_entries(PROJECT_ENTRIES)
        else:
            self._ensure_minimal_project_documents()
            self._map_minimal_project_documents()
            self.query_one(ProjectPane).reset_project_entries((NEW_PROJECT_CURRENT_DRAFT_ENTRY,))
        self._engine_adapter.open_project(self._project_root)
        self.query_one(BasketPane).clear_entries()
        self._refresh_notebook_context_meter()
        self.run_worker(
            self.query_one(DocumentPane).reset_for_project(),
            name="project-document-reset",
            group="project",
            exclusive=True,
        )
        self.query_one(ProjectPane).set_project_name(project_name)
        if self._current_project_is_confidential():
            self._activate_local_openai_for_confidential_project()
        self._refresh_project_names()
        save_textual_last_project_name(project_name, self._repo_root())
        verb = "Created" if created else "Opened"
        self._sync_footer_bar()
        mode = "confidential " if self._current_project_is_confidential() else ""
        self._set_status(f"{verb} {mode}project: {project_name}")
        self._show_subject(
            project_name,
            "Active project.",
            (
                f"Project name: {project_name}",
                "Documents are available from the project rail.",
                "Notebook actions use the active document and basket context.",
            ),
            None,
        )
        self._load_engine_project_entries()

    def _delete_project(self, project: ProjectRecord | str) -> None:
        project_name = project.name if isinstance(project, ProjectRecord) else project
        project_slug = project.slug if isinstance(project, ProjectRecord) else self._project_slug_for_name(project_name)
        if project_name == PROJECT_NAME:
            self._set_status("The clean demo project stays available for testing.")
            return
        project_root = self._project_root_for_slug(project_slug) if project_slug else self._project_root_for_name(project_name)
        if not project_root.exists():
            self._set_status(f"Project is already missing: {project_name}")
            self._refresh_project_names()
            return
        self._save_dirty_documents()
        try:
            shutil.rmtree(project_root)
        except OSError as exc:
            self._set_status(f"Could not delete project: {exc}")
            return
        self._refresh_project_names()
        if self._current_project_name == project_name and self._current_project_slug == project_slug:
            next_record = self._project_records[0] if self._project_records else None
            if next_record is not None:
                self._switch_project(next_record.name, created=False, project_slug=next_record.slug)
                self._set_status(f"Deleted project: {project_name}. Opened {next_record.name}.")
            else:
                self._current_project_name = DEFAULT_EMPTY_PROJECT_NAME
                self._current_project_slug = None
                self._project_root = self._project_root_for_name(DEFAULT_EMPTY_PROJECT_NAME)
                self.query_one(ProjectPane).set_project_name(DEFAULT_EMPTY_PROJECT_NAME)
                self._set_status(f"Deleted project: {project_name}. Create a new project to continue.")
        else:
            self._set_status(f"Deleted project: {project_name}.")

    def _slugify(self, text: str) -> str:
        return "".join(char.lower() if char.isalnum() else "-" for char in text).strip("-")

    def _handle_project_rename_result(self, slug: str, result: str | None) -> None:
        if result is None:
            return
        new_title = result.strip()
        if not new_title:
            return
        fixture = DOCUMENT_FIXTURES.get(slug)
        if fixture is None:
            return
        document_id = self._document_id_by_slug.get(slug)
        item_id = new_title
        if document_id is not None:
            try:
                item = self._engine_adapter.rename_document(document_id, new_title)
            except (FileExistsError, FileNotFoundError, RuntimeError, ValueError) as exc:
                self._set_status(f"Could not rename backing file: {exc}")
                return
            self._document_id_by_slug[slug] = item.id
            item_id = item.id
        renamed = self.query_one(ProjectPane).rename_entry(slug, new_title)
        if renamed is None:
            return
        self.query_one(DocumentPane).rename_document(slug, new_title, item_id)
        self._set_status(f"Renamed file to {new_title}.")
        self._show_subject(renamed.title, renamed.summary, renamed.bullets, None)

    def _selected_trash_slug(self) -> str | None:
        selected = self.query_one(ProjectPane).selected_entry_info()
        if selected is None or selected.kind != "trash_entry" or selected.slug is None:
            return None
        return selected.slug

    def _selected_trash_slugs(self) -> tuple[str, ...]:
        project_pane = self.query_one(ProjectPane)
        marked = tuple(info.slug for info in project_pane.marked_entry_infos(kinds={"trash_entry"}) if info.slug is not None)
        if marked:
            return marked
        selected = self._selected_trash_slug()
        if selected is not None:
            return (selected,)
        descendants = project_pane.selected_container_entry_infos(kinds={"trash_entry"})
        return tuple(info.slug for info in descendants if info.slug is not None)

    def _handle_trash_document_result(self, slug: str, result: str | None) -> None:
        if result is None:
            return
        trash_id = self._trash_id_by_slug.get(slug)
        if trash_id is None:
            self._set_status("Trash item is no longer available.")
            return
        if result == "restore":
            metadata = self._trash_metadata_by_slug.get(slug, {})
            original_id = str(metadata.get("original_id") or "")
            if original_id and (self._project_root / original_id).exists():
                self.push_screen(
                    DuplicateDocumentModal(Path(original_id).name, original_id),
                    callback=lambda duplicate_result, slug=slug: self._handle_duplicate_restore_result(slug, duplicate_result),
                )
                self._set_status(f"Restore conflict: {original_id} already exists.")
                return
            try:
                item = self._engine_adapter.restore_trash_document(trash_id)
                content = Path(item.path).read_text(encoding="utf-8", errors="replace")
            except (FileExistsError, FileNotFoundError, RuntimeError, ValueError, OSError) as exc:
                self._set_status(f"Could not restore trash item: {exc}")
                return
            self._finish_restored_trash_item(slug, item, content)
            return
        if result == "permanent_delete":
            self._confirm_permanent_delete_trash_items((slug,))

    def _confirm_permanent_delete_trash_items(self, slugs: tuple[str, ...]) -> None:
        available = tuple(slug for slug in slugs if slug in self._trash_id_by_slug)
        if not available:
            self._set_status("Trash item is no longer available.")
            return
        title = self._trash_title_for_confirm(available[0])
        self.push_screen(
            PermanentDeleteTrashConfirmModal(title, count=len(available)),
            callback=lambda confirmed, slugs=available: self._handle_permanent_delete_confirmed(slugs, confirmed),
        )

    def _trash_title_for_confirm(self, slug: str) -> str:
        fixture = DOCUMENT_FIXTURES.get(slug)
        if fixture is not None and fixture.title:
            return fixture.title
        metadata = self._trash_metadata_by_slug.get(slug, {})
        original_id = str(metadata.get("original_id") or "")
        return Path(original_id).name if original_id else "selected trash item"

    def _handle_permanent_delete_confirmed(self, slugs: tuple[str, ...], confirmed: bool | None) -> None:
        if not confirmed:
            self._set_status("Permanent delete cancelled.")
            return
        deleted_count = 0
        for slug in slugs:
            if self._permanently_delete_trash_item(slug):
                deleted_count += 1
        if deleted_count > 1:
            self._set_status(f"Permanently deleted {deleted_count} trash items. Audit trail retained.")

    def _permanently_delete_trash_item(self, slug: str) -> bool:
        trash_id = self._trash_id_by_slug.get(slug)
        if trash_id is None:
            self._set_status("Trash item is no longer available.")
            return False
        metadata = self._trash_metadata_by_slug.get(slug, {})
        original_id = str(metadata.get("original_id") or "")
        try:
            item = self._engine_adapter.permanently_delete_trash_document(trash_id)
        except (FileNotFoundError, RuntimeError, ValueError) as exc:
            self._set_status(f"Could not permanently delete trash item: {exc}")
            return False
        self._mark_basket_sources(
            source_document_id=original_id or None,
            source_document_slug=slug,
            status="source_deleted",
        )
        self._remove_document_tab(slug)
        self.query_one(ProjectPane).remove_entry(slug)
        self._trash_id_by_slug.pop(slug, None)
        self._trash_metadata_by_slug.pop(slug, None)
        self._set_status(f"Permanently deleted {item.label}. Audit trail retained.")
        return True

    def _handle_duplicate_restore_result(
        self,
        slug: str,
        result: tuple[str, str | None] | None,
    ) -> None:
        if result is None:
            self._set_status("Restore cancelled.")
            return
        trash_id = self._trash_id_by_slug.get(slug)
        metadata = self._trash_metadata_by_slug.get(slug, {})
        original_id = str(metadata.get("original_id") or "")
        if trash_id is None or not original_id:
            self._set_status("Trash item is no longer available.")
            return
        action, new_title = result
        try:
            if action == "replace":
                existing_slug = next((doc_slug for doc_slug, doc_id in self._document_id_by_slug.items() if doc_id == original_id), None)
                existing_title = self._project_title_for_slug(existing_slug) or Path(original_id).name
                replaced = self._engine_adapter.delete_document(original_id, display_label=existing_title)
                if existing_slug is not None:
                    self.query_one(ProjectPane).remove_entry(existing_slug)
                    self._document_id_by_slug.pop(existing_slug, None)
                    DOCUMENT_FIXTURES.pop(existing_slug, None)
                    self._mark_basket_sources(
                        source_document_id=original_id,
                        source_document_slug=existing_slug,
                        status="trashed",
                    )
                self._register_trash_entry(replaced.id, replaced.label, dict(replaced.metadata), old_source_slug=existing_slug)
                item = self._engine_adapter.restore_trash_document(trash_id)
            elif action == "rename":
                item = self._engine_adapter.restore_trash_document_as(trash_id, new_title or Path(original_id).name)
            else:
                self._set_status("Unknown restore conflict action.")
                return
            content = Path(item.path).read_text(encoding="utf-8", errors="replace")
        except (FileExistsError, FileNotFoundError, RuntimeError, ValueError, OSError) as exc:
            self._set_status(f"Could not resolve restore conflict: {exc}")
            return
        self._finish_restored_trash_item(slug, item, content)

    def _finish_restored_trash_item(self, trash_slug: str, item, content: str) -> None:
        metadata = self._trash_metadata_by_slug.get(trash_slug, {})
        original_id = str(metadata.get("original_id") or "") or None
        restored_title = str(metadata.get("display_label") or item.label)
        self._remove_document_tab(trash_slug)
        self.query_one(ProjectPane).remove_entry(trash_slug)
        self._trash_id_by_slug.pop(trash_slug, None)
        self._trash_metadata_by_slug.pop(trash_slug, None)
        category = self._category_for_document_id(item.id)
        if category is None:
            self._set_status(f"Restored {restored_title}, but it is outside a visible project category.")
            return
        restored_slug = self._next_dynamic_slug(self._category_slug_prefix(category))
        self._document_id_by_slug[restored_slug] = item.id
        summary = f"{restored_title} restored from trash."
        register_document_fixture(
            slug=restored_slug,
            title=restored_title,
            location=item.id,
            summary=summary,
            content=content,
            document_type=self._category_document_type(category),
            is_transcript=(category == "Transcripts"),
        )
        self.query_one(ProjectPane).add_project_entry(
            category=category,
            slug=restored_slug,
            title=restored_title,
            location=item.id,
            summary=summary,
            bullets=(
                f"Category: {category}",
                f"Location: {item.id}",
                "Restored from project trash.",
            ),
        )
        self._rebind_basket_sources_after_restore(
            old_source_document_id=original_id,
            old_source_document_slug=trash_slug,
            new_source_document_id=item.id,
            new_source_document_slug=restored_slug,
            source_title=restored_title,
        )
        self._set_status(f"Restored {restored_title} to {item.id}.")

    def _remove_document_tab(self, slug: str) -> None:
        self.run_worker(
            self.query_one(DocumentPane).remove_document(slug),
            thread=False,
            exclusive=False,
            group="document-tabs",
        )

    def _next_dynamic_slug(self, prefix: str) -> str:
        index = 1
        while (
            f"{prefix}-{index:02d}" in DOCUMENT_FIXTURES
            or f"{prefix}-{index:02d}" in self._document_id_by_slug
            or f"{prefix}-{index:02d}" in self._trash_id_by_slug
        ):
            index += 1
        return f"{prefix}-{index:02d}"

    async def _create_project_document(self, category: str) -> None:
        self._save_dirty_documents()
        specs = {
            "Drafts": ("draft", "working_draft", "Working Draft"),
            "Memos": ("memo", "memo", "Working Memo"),
            "Summaries": ("summary", "summary", "Summary"),
            "Transcripts": ("transcript", "transcript", "Transcript"),
            "Literature": ("literature", "literature_note", "Literature Note"),
        }
        prefix, filename_root, title_root = specs[category]
        slug = self._next_dynamic_slug(prefix)
        filename = f"{filename_root}_{slug.split('-')[-1]}.md"
        title = f"{title_root} {slug.split('-')[-1]}"
        summary = f"{title} in {category.lower()}."
        content = f"# {title}\n\nThis is a new {category[:-1].lower() if category.endswith('s') else category.lower()} document.\n"
        folder = self._selected_project_folder_path(category)
        relative_path = self._target_document_id(category, filename, folder)
        item = self._engine_adapter.create_document(
            category=category,
            title=filename,
            content=content,
            document_type=prefix,
            relative_path=relative_path,
        )
        self._document_id_by_slug[slug] = item.id
        register_document_fixture(
            slug=slug,
            title=filename,
            location=item.id,
            summary=summary,
            content=content,
            document_type=prefix,
            is_transcript=(category == "Transcripts"),
        )
        self.query_one(ProjectPane).add_project_entry(
            category=category,
            slug=slug,
            title=filename,
            location=item.id,
            summary=summary,
            bullets=(
                f"Category: {category}",
                f"Location: {item.id}",
                f"Document type: {prefix}",
            ),
        )
        await self.query_one(DocumentPane).open_document(slug)
        self._sync_save_controls()
        self._set_status(f"Created {filename} in {category}.")

    def _handle_new_folder_result(self, category: str, result: str | None) -> None:
        if result is None:
            return
        parent = self._selected_project_folder_path(category)
        folder_path = self._safe_folder_path(Path(parent) / result)
        if not folder_path:
            self._set_status("Folder name is required.")
            return
        target = self._project_root / self._category_folder(category) / folder_path
        try:
            target.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self._set_status(f"Could not create folder: {exc}")
            return
        project_pane = self.query_one(ProjectPane)
        project_pane.add_folder(category=category, folder_path=folder_path.as_posix())
        project_pane.select_folder(category=category, folder_path=folder_path.as_posix())
        self._set_status(f"Created folder {folder_path.as_posix()} in {category}.")

    def _handle_project_update_result(self, slug: str, result: tuple[str, str] | None) -> None:
        if result is None:
            return
        title, folder = result
        self._update_project_item(slug, title, folder)

    def _update_project_item(
        self,
        slug: str,
        title: str,
        folder: str,
        *,
        duplicate_action: str | None = None,
        duplicate_title: str | None = None,
    ) -> bool:
        fixture = DOCUMENT_FIXTURES.get(slug)
        document_id = self._document_id_by_slug.get(slug)
        if fixture is None or document_id is None:
            self._set_status("Selected project item is no longer available.")
            return False
        category = self._category_for_document_id(document_id)
        if category is None:
            self._set_status("Selected project item is outside a visible document category.")
            return False
        target_title = duplicate_title or title
        target_id = self._target_document_id(category, target_title, folder, allow_extensionless=True)
        if target_id == document_id:
            self._set_status(f"No changes for {fixture.title}.")
            return False
        existing_slug = next((candidate for candidate, candidate_id in self._document_id_by_slug.items() if candidate_id == target_id), None)
        if duplicate_action is None and (self._project_root / target_id).exists():
            self.push_screen(
                DuplicateDocumentModal(Path(target_id).name, target_id, cancel_label="Cancel", cancel_result=("cancel", None)),
                callback=lambda result, slug=slug, title=title, folder=folder: self._handle_duplicate_update_result(slug, title, folder, result),
            )
            self._set_status(f"Update conflict: {target_id} already exists.")
            return False
        try:
            if duplicate_action == "replace" and existing_slug is not None:
                existing_title = self._project_title_for_slug(existing_slug) or Path(target_id).name
                replaced = self._engine_adapter.delete_document(target_id, display_label=existing_title)
                self.query_one(ProjectPane).remove_entry(existing_slug)
                self._document_id_by_slug.pop(existing_slug, None)
                DOCUMENT_FIXTURES.pop(existing_slug, None)
                self._remove_document_tab(existing_slug)
                self._mark_basket_sources(source_document_id=target_id, source_document_slug=existing_slug, status="trashed")
                self._register_trash_entry(replaced.id, replaced.label, dict(replaced.metadata), old_source_slug=existing_slug)
            elif duplicate_action == "cancel":
                self._set_status("Update cancelled.")
                return False
            item = self._engine_adapter.move_document(document_id, target_id)
        except (FileExistsError, FileNotFoundError, RuntimeError, ValueError, OSError) as exc:
            self._set_status(f"Could not update project item: {exc}")
            return False
        self._document_id_by_slug[slug] = item.id
        fixture.title = item.label
        fixture.location = item.id
        self.query_one(ProjectPane).move_entry(slug, category=category, title=item.label, location=item.id)
        self.query_one(DocumentPane).rename_document(slug, item.label, item.id)
        self._mark_basket_sources(source_document_id=document_id, source_document_slug=slug, status="changed")
        self._set_status(f"Updated {item.label}: {item.id}.")
        self._show_document_subject(fixture)
        return True

    def _handle_duplicate_update_result(
        self,
        slug: str,
        title: str,
        folder: str,
        result: tuple[str, str | None] | None,
    ) -> None:
        if result is None:
            self._set_status("Update cancelled.")
            return
        action, new_title = result
        if action == "rename":
            self._update_project_item(slug, new_title or title, folder, duplicate_action="rename", duplicate_title=new_title or title)
        elif action in {"replace", "cancel"}:
            self._update_project_item(slug, title, folder, duplicate_action=action)
        else:
            self._set_status("Unknown update conflict action.")

    async def _import_project_document(
        self,
        path: Path,
        *,
        category: str | None = None,
        destination_folder: str = "",
        duplicate_action: str | None = None,
        duplicate_title: str | None = None,
        open_document: bool = True,
    ) -> bool:
        category = category or DEFAULT_IMPORT_CATEGORY
        if category not in IMPORTABLE_PROJECT_CATEGORIES:
            self._set_status(f"Cannot import into {category}. Choose a document type.")
            return False
        resolved = path.expanduser().resolve()
        if path_has_hidden_part(resolved):
            self._set_status("Cannot import hidden files or files from hidden folders.")
            return False
        if not is_markdown_file(resolved):
            self._set_status("Import only supports markdown files.")
            return False
        target_id = self._target_document_id(category, resolved.name, destination_folder)
        if self._is_self_import(resolved, category, destination_folder):
            self._set_status(f"Skipped already imported file: {target_id}.")
            return False
        if duplicate_action == "skip":
            self._set_status(f"Skipped duplicate import: {target_id}.")
            return False
        if duplicate_action is None and self._project_child_path(target_id).exists():
            self.push_screen(
                DuplicateDocumentModal(resolved.name, target_id),
                callback=lambda result, path=resolved, category=category, folder=destination_folder: self._handle_duplicate_import_result(path, category, result, folder),
            )
            self._set_status(f"Import conflict: {target_id} already exists.")
            return False
        try:
            content = resolved.read_text(encoding="utf-8")
            if duplicate_action == "replace":
                self._engine_adapter.open_document(target_id)
                self._engine_adapter.save_document(content)
                item_id = target_id
                item_label = Path(target_id).name
            elif duplicate_action == "rename":
                renamed_title = duplicate_title or resolved.name
                renamed_target = self._target_document_id(category, renamed_title, destination_folder)
                if self._project_child_path(renamed_target).exists():
                    self._set_status(f"Rename conflict: {renamed_target} already exists.")
                    return False
                item = self._engine_adapter.create_document(
                    category=category,
                    title=renamed_title,
                    content=content,
                    document_type=self._category_document_type(category),
                    relative_path=renamed_target,
                )
                item_id = item.id
                item_label = item.label
                item_path = Path(item.path)
            else:
                item = self._engine_adapter.import_markdown_document(source_path=resolved, category=category, relative_path=target_id)
                content = Path(item.path).read_text(encoding="utf-8", errors="replace")
                item_id = item.id
                item_label = item.label
                item_path = Path(item.path)
        except (OSError, RuntimeError, ValueError) as exc:
            self._set_status(f"Could not import {resolved.name}: {exc}")
            return False
        if duplicate_action == "replace":
            slug = next((slug for slug, document_id in self._document_id_by_slug.items() if document_id == item_id), None)
            existing_slug = slug
            if slug is None:
                slug = self._next_dynamic_slug("imported")
            filename = item_label
        else:
            existing_slug = None
            slug = self._next_dynamic_slug("imported")
            filename = item_label
        summary = f"Imported markdown file from {resolved} into {category.lower()}."
        self._document_id_by_slug[slug] = item_id
        register_document_fixture(
            slug=slug,
            title=filename,
            location=item_id,
            summary=summary,
            content=content,
            document_type={
                "Drafts": "draft",
                "Memos": "memo",
                "Summaries": "summary",
                "Transcripts": "transcript",
                "Literature": "literature",
            }[category],
            is_transcript=(category == "Transcripts"),
        )
        if existing_slug is None:
            self.query_one(ProjectPane).add_project_entry(
                category=category,
                slug=slug,
                title=filename,
                location=item_id,
                summary=summary,
                bullets=(
                    "Imported through the project rail import action.",
                    "Only markdown files are shown in the import browser.",
                    f"Original path: {resolved}.",
                    "The imported document opens in the document pane like any other project file.",
                ),
            )
        if open_document:
            await self.query_one(DocumentPane).open_document(slug)
            self._sync_save_controls()
        verb = "Replaced" if duplicate_action == "replace" else "Imported"
        self._set_status(f"{verb} {filename} in {category}.")
        return True

    def _destination_folder_for_import(
        self,
        path: Path,
        *,
        destination_folder: str = "",
        mode: str = "selected",
        source_root: Path | None = None,
    ) -> str:
        base = self._safe_folder_path(destination_folder)
        if mode != "folder_tree" or source_root is None:
            return base.as_posix() if base else ""
        try:
            relative_parent = path.resolve().relative_to(source_root.resolve()).parent
        except ValueError:
            relative_parent = Path("")
        source_folder = self._safe_folder_path(source_root.name)
        combined = base / source_folder / self._safe_folder_path(relative_parent)
        return combined.as_posix() if combined else ""

    async def _import_project_documents(
        self,
        paths: list[Path],
        *,
        category: str,
        destination_folder: str = "",
        mode: str = "selected",
        source_root: Path | None = None,
        start_index: int = 0,
        duplicate_result: tuple[str, str | None] | None = None,
        progress_modal: ImportProgressModal | None = None,
        imported_count: int = 0,
        skipped_count: int = 0,
        replace_all_duplicates: bool = False,
        skip_all_duplicates: bool = False,
    ) -> None:
        if not paths:
            self._set_status("No markdown files selected for import.")
            return
        total = len(paths)
        for index in range(start_index, len(paths)):
            if progress_modal is not None and progress_modal.cancel_requested:
                message = f"Import stopped. Imported {imported_count} markdown files into {category}."
                if skipped_count:
                    message = f"{message} Skipped {skipped_count}."
                progress_modal.update_progress(
                    current="Import stopped.",
                    processed=index,
                    imported=imported_count,
                    skipped=skipped_count,
                    status=message,
                )
                self._finish_import_progress(progress_modal, message)
                self._set_status(message)
                return
            path = paths[index]
            resolved = path.expanduser().resolve()
            target_folder = self._destination_folder_for_import(
                resolved,
                destination_folder=destination_folder,
                mode=mode,
                source_root=source_root,
            )
            if progress_modal is not None:
                progress_modal.update_progress(
                    current=f"Importing: {resolved.name}",
                    processed=index,
                    imported=imported_count,
                    skipped=skipped_count,
                )
            if path_has_hidden_part(resolved) or not is_markdown_file(resolved):
                skipped_count += 1
                if progress_modal is not None:
                    progress_modal.update_progress(
                        current=f"Skipped non-markdown file: {resolved.name}",
                        processed=index + 1,
                        imported=imported_count,
                        skipped=skipped_count,
                        status="Only markdown files are imported.",
                )
                continue
            target_id = self._target_document_id(category, resolved.name, target_folder)
            if self._is_self_import(resolved, category, target_folder):
                skipped_count += 1
                if progress_modal is not None:
                    progress_modal.update_progress(
                        current=f"Skipped already imported file: {resolved.name}",
                        processed=index + 1,
                        imported=imported_count,
                        skipped=skipped_count,
                        status="Already imported project files are skipped.",
                    )
                continue
            action: str | None = None
            new_title: str | None = None
            if duplicate_result is not None and index == start_index:
                action, new_title = duplicate_result
                if action == "replace_all":
                    replace_all_duplicates = True
                    action = "replace"
                elif action == "skip_all":
                    skip_all_duplicates = True
                    action = "skip"
            target_exists = self._project_child_path(target_id).exists()
            if action is None and replace_all_duplicates and target_exists:
                action = "replace"
            elif action is None and skip_all_duplicates and target_exists:
                action = "skip"
            elif action is None and target_exists:
                if progress_modal is not None:
                    progress_modal.update_progress(
                        current=f"Duplicate found: {resolved.name}",
                        processed=index,
                        imported=imported_count,
                        skipped=skipped_count,
                        status="Choose replace, rename, or skip to continue this batch.",
                    )

                def handle_duplicate_batch_result(
                    result: tuple[str, str | None] | None,
                    *,
                    paths: list[Path] = paths,
                    category: str = category,
                    index: int = index,
                    progress_modal: ImportProgressModal | None = progress_modal,
                    imported_count: int = imported_count,
                    skipped_count: int = skipped_count,
                    destination_folder: str = destination_folder,
                    mode: str = mode,
                    source_root: Path | None = source_root,
                    replace_all_duplicates: bool = replace_all_duplicates,
                    skip_all_duplicates: bool = skip_all_duplicates,
                ) -> None:
                    self._handle_duplicate_batch_import_result(
                        paths,
                        category,
                        index,
                        result,
                        progress_modal,
                        imported_count,
                        skipped_count,
                        destination_folder,
                        mode,
                        source_root,
                        replace_all_duplicates,
                        skip_all_duplicates,
                    )

                self.push_screen(
                    DuplicateDocumentModal(
                        resolved.name,
                        target_id,
                        cancel_label="Skip",
                        cancel_result=("skip", None),
                        replace_all_label="Replace all",
                        replace_all_result=("replace_all", None),
                        skip_all_label="Skip all",
                        skip_all_result=("skip_all", None),
                        cancel_import_label="Cancel",
                        cancel_import_result=("cancel_import", None),
                    ),
                    callback=handle_duplicate_batch_result,
                )
                self._set_status(f"Import conflict: {target_id} already exists.")
                return
            if action == "skip":
                skipped_count += 1
                if progress_modal is not None:
                    progress_modal.update_progress(
                        current=f"Skipped duplicate: {resolved.name}",
                        processed=index + 1,
                        imported=imported_count,
                        skipped=skipped_count,
                        status="Skipped duplicate file.",
                    )
                duplicate_result = None
                continue
            if await self._import_project_document(
                resolved,
                category=category,
                destination_folder=target_folder,
                duplicate_action=action,
                duplicate_title=new_title,
                open_document=False,
            ):
                imported_count += 1
                if progress_modal is not None:
                    progress_modal.update_progress(
                        current=f"Added: {resolved.name}",
                        processed=index + 1,
                        imported=imported_count,
                        skipped=skipped_count,
                        status="Importing selected markdown files...",
                    )
            else:
                skipped_count += 1
                if progress_modal is not None:
                    progress_modal.update_progress(
                        current=f"Skipped: {resolved.name}",
                        processed=index + 1,
                        imported=imported_count,
                        skipped=skipped_count,
                        status="Continuing import after skipped file.",
                    )
            duplicate_result = None
        message = f"Imported {imported_count} markdown files into {category}."
        if skipped_count:
            message = f"{message} Skipped {skipped_count}."
        if progress_modal is not None:
            progress_modal.update_progress(
                current="Import complete.",
                processed=total,
                imported=imported_count,
                skipped=skipped_count,
                status=message,
            )
            self._finish_import_progress(progress_modal, message)
        if len(paths) > 1 or progress_modal is not None:
            self._set_status(message)

    async def _delete_selected_project_document(self) -> None:
        self._save_dirty_documents()
        project_pane = self.query_one(ProjectPane)
        selected_infos = project_pane.marked_entry_infos(kinds={"entry"})
        if not selected_infos:
            selected = project_pane.selected_entry_info()
            selected_infos = () if selected is None else (selected,)
        if not selected_infos:
            await self._delete_selected_project_folder()
            return
        selected_infos = tuple(
            info
            for info in selected_infos
            if info.slug is not None and info.kind == "entry" and info.slug != CURRENT_DRAFT_SLUG
        )
        if not selected_infos:
            self._set_status("Select a deletable document in the project rail first.")
            return
        deleted_count = 0
        removed_titles: list[str] = []
        for selected in selected_infos:
            if await self._move_project_document_to_trash(selected):
                deleted_count += 1
                removed_titles.append(selected.title)
        if deleted_count == 0:
            self._set_status("Select a deletable document in the project rail first.")
        elif deleted_count == 1:
            self._set_status(f"Deleted {removed_titles[0]}.")
        else:
            self._set_status(f"Deleted {deleted_count} documents.")

    async def _delete_selected_project_folder(self) -> None:
        project_pane = self.query_one(ProjectPane)
        container = project_pane.selected_container_info()
        if container is None or container.kind != "folder":
            self._set_status("Select a deletable document or folder in the project rail first.")
            return
        descendants = tuple(
            info
            for info in project_pane.selected_container_entry_infos(kinds={"entry"})
            if info.slug is not None and info.slug != CURRENT_DRAFT_SLUG
        )
        category = project_pane.selected_category() or ""
        folder_path = project_pane.selected_folder_path()
        folder_label = container.note or container.title

        def handle_confirmation(confirmed: bool) -> None:
            self._handle_folder_delete_confirmation(
                folder_label,
                category,
                folder_path,
                descendants,
                confirmed,
            )

        await self.push_screen(
            DeleteFolderConfirmModal(folder_label, len(descendants)),
            callback=handle_confirmation,
        )

    def _handle_folder_delete_confirmation(
        self,
        folder_label: str,
        category: str,
        folder_path: str,
        descendants: tuple[ProjectNodeInfo, ...],
        confirmed: bool,
    ) -> None:
        if not confirmed:
            self._set_status(f"Kept folder: {folder_label}.")
            return
        if not descendants:
            self._delete_empty_project_folder(folder_label, category, folder_path)
            return
        self.run_worker(
            self._move_project_documents_to_trash(
                descendants,
                folder_label=folder_label,
                category=category,
                folder_path=folder_path,
            ),
            thread=False,
            exclusive=False,
            group="project-delete",
        )

    def _delete_empty_project_folder(self, folder_label: str, category: str, folder_path: str) -> None:
        if not category or not folder_path:
            self._set_status(f"Could not delete empty folder: {folder_label}.")
            return
        try:
            target = self._project_child_path(Path(self._category_folder(category)) / self._safe_folder_path(folder_path))
        except ValueError as exc:
            self._set_status(f"Could not delete empty folder: {exc}")
            return
        try:
            target.rmdir()
        except FileNotFoundError:
            pass
        except OSError as exc:
            self._set_status(f"Could not delete empty folder: {exc}")
            return
        self.query_one(ProjectPane).remove_folder(category=category, folder_path=folder_path)
        self._set_status(f"Deleted empty folder {folder_label}.")

    async def _move_project_documents_to_trash(
        self,
        selected_infos: tuple[ProjectNodeInfo, ...],
        *,
        folder_label: str,
        category: str,
        folder_path: str,
    ) -> None:
        deleted_count = 0
        for selected in selected_infos:
            if await self._move_project_document_to_trash(selected):
                deleted_count += 1
        if deleted_count:
            if category and folder_path:
                self.query_one(ProjectPane).remove_folder(category=category, folder_path=folder_path)
            self._set_status(f"Moved {deleted_count} documents from {folder_label} to trash.")
        else:
            self._set_status(f"No documents moved from {folder_label}.")

    async def _move_project_document_to_trash(self, selected: ProjectNodeInfo) -> bool:
        if selected.slug is None:
            return False
        project_pane = self.query_one(ProjectPane)
        document_id = self._document_id_by_slug.get(selected.slug)
        trashed_item = None
        if document_id is not None:
            try:
                trashed_item = self._engine_adapter.delete_document(document_id, display_label=selected.title)
            except (FileNotFoundError, RuntimeError, ValueError) as exc:
                self._set_status(f"Could not move backing file to trash: {exc}")
                return False
            self._mark_basket_sources(
                source_document_id=document_id,
                source_document_slug=selected.slug,
                status="trashed",
            )
            self._document_id_by_slug.pop(selected.slug, None)
        removed = project_pane.remove_entry(selected.slug)
        if removed is None or removed.slug is None:
            return False
        deleted = await self.query_one(DocumentPane).remove_document(removed.slug)
        if deleted:
            pass
        else:
            pass
        if trashed_item is not None:
            self._register_trash_entry(trashed_item.id, trashed_item.label, dict(trashed_item.metadata), old_source_slug=removed.slug)
        return True
