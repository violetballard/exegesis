from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from textwrap import wrap

from rich.segment import Segment
from rich.style import Style
from rich.text import Text
from textual import events, on
from textual._loop import loop_last
from textual._segment_tools import line_pad
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.geometry import Size
from textual.message import Message
from textual.strip import Strip
from textual.widgets import Button, Static, Tree
from textual.widgets._tree import _TreeLine

from exegesis_textual.panes import PaneCopy

PROJECT_PANE_COPY = PaneCopy(
    pane_id="project-pane",
    title="Project",
    summary="Project browser with drafts, source materials, and supporting writing artifacts.",
    bullets=(
        "The current project name should stay visible at the top of the rail.",
        "Drafts should feel like first-class writing outputs, not a special one-off box.",
        "Supporting materials should stay grouped underneath without competing with the draft.",
    ),
)

PROJECT_NEW_PROJECT_ID = "project-new-project"
PROJECT_OPEN_PROJECT_ID = "project-open-project"
PROJECT_NEW_DRAFT_ID = "project-new-draft"
PROJECT_NEW_MEMO_ID = "project-new-memo"
PROJECT_NEW_SUMMARY_ID = "project-new-summary"
PROJECT_NEW_TRANSCRIPT_ID = "project-new-transcript"
PROJECT_NEW_LITERATURE_ID = "project-new-literature"
PROJECT_NEW_FOLDER_ID = "project-new-folder"
PROJECT_IMPORT_ID = "project-import"
PROJECT_DELETE_ID = "project-delete"
PROJECT_TRASH_DELETE_ID = "project-trash-delete"
PROJECT_TRASH_RESTORE_ID = "project-trash-restore"


@dataclass(frozen=True)
class ProjectEntry:
    slug: str
    category: str
    title: str
    location: str
    summary: str
    bullets: tuple[str, ...]


@dataclass(frozen=True)
class ProjectNodeInfo:
    kind: str
    title: str
    summary: str
    bullets: tuple[str, ...]
    note: str | None = None
    slug: str | None = None


PROJECT_NAME = "Demo Project"
PROJECT_BROWSER_ID = "project-browser"
PROJECT_BROWSER_LABEL_WRAP_WIDTH = 33
CURRENT_DRAFT_NAME = "current_draft.md"
CURRENT_DRAFT_LOCATION = "current_draft.md"
CURRENT_DRAFT_SUMMARY = (
    "The one primary manuscript for this project. Other materials support it, but this file stays"
    " at the top as the center of gravity."
)
CURRENT_DRAFT_BULLETS = (
    "This is the main draft the shell should privilege.",
    "The document pane should feel anchored to this file first.",
    "Everything else in the project rail supports this draft, not the other way around.",
)


PROJECT_SECTION_INFO = {
    "Drafts": ProjectNodeInfo(
        "section",
        "Drafts",
        "Project outputs that stay editable and close to the main writing flow.",
        (
            "The current draft should always be present here.",
            "Future output drafts can live beside it without looking like memos.",
            "This keeps the left rail aligned with writing work rather than storage categories.",
        ),
        "Project browser section",
    ),
    "Memos": ProjectNodeInfo(
        "section",
        "Memos",
        "Quick editorial notes and working memos for active drafts.",
        (
            "Good home for scratch thinking and guidance to the revision loop.",
            "Should feel lightweight and easy to scan in the left rail.",
            "Lets the browser read like a writing project, not a file dump.",
        ),
        "Project browser section",
    ),
    "Summaries": ProjectNodeInfo(
        "section",
        "Summaries",
        "Short synthesis documents and generated summaries that support drafting.",
        (
            "Useful later for retrieval-driven supporting context.",
            "Makes the browser structure clearer than a flat document list.",
            "Keeps the shell aligned with how a writer organizes support material.",
        ),
        "Project browser section",
    ),
    "Transcripts": ProjectNodeInfo(
        "section",
        "Transcripts",
        "Source conversations and interviews that may feed retrieval or quotation.",
        (
            "Important for provenance-aware retrieval later on.",
            "Helps the left rail look like a real project archive.",
            "Gives us a place for source-heavy writing inputs.",
        ),
        "Project browser section",
    ),
    "Literature": ProjectNodeInfo(
        "section",
        "Literature",
        "Papers, references, and supporting research material.",
        (
            "Natural category for retrieval-backed evidence.",
            "Useful when we start making the basket feel research-aware.",
            "Helps tomorrow's UI notes focus on structure rather than filler text.",
        ),
        "Project browser section",
    ),
    "Trash": ProjectNodeInfo(
        "section",
        "Trash",
        "Deleted project documents staged for restore or permanent deletion.",
        (
            "Deleted documents move here first instead of disappearing immediately.",
            "Double-select a trash item to restore it or permanently delete it.",
            "Permanent deletion is audited and should be an extra-step action.",
        ),
        "Project browser section",
    ),
}


PROJECT_ENTRIES = (
    ProjectEntry(
        "current-draft",
        "Drafts",
        "current_draft.md",
        "current_draft.md",
        "The primary manuscript for the project and the default writing tab.",
        (
            "This is the anchored main draft for the shell.",
            "It should remain easy to find and impossible to mistake for support material.",
            "The document pane should feel centered around this file first.",
        ),
    ),
    ProjectEntry(
        "project-demo-essay",
        "Memos",
        "Data Memo 1",
        "fieldwork/round_1/data_memo_1.md",
        "The draft we will use for the canonical retrieve -> basket -> revise loop.",
        (
            "Primary playground for tomorrow's shell iteration.",
            "Represents the browser-first demo path we care about most.",
            "Keeps the shell focused on one believable writing flow.",
        ),
    ),
    ProjectEntry(
        "project-root-memo",
        "Memos",
        "Root Memo Example",
        "root_memo_example.md",
        "A root-level memo that keeps the demo category from looking folder-only.",
        (
            "Useful for testing root-level organization beside nested folders.",
            "Shows that folders are optional within each document category.",
            "Gives import and move flows an easy visible root target.",
        ),
    ),
    ProjectEntry(
        "project-compaction-filler-1",
        "Memos",
        "Compaction Filler 1",
        "compaction_test_files/compaction_filler_1.md",
        "Large non-confidential memo for pushing the notebook context meter toward compaction prompts.",
        (
            "Add this to the basket when testing notebook compaction thresholds.",
            "The content is generated locally so the repo does not store giant fixture blobs.",
            "Use with the other compaction filler memos to trigger 75% and 90% warning cards.",
        ),
    ),
    ProjectEntry(
        "project-compaction-filler-2",
        "Memos",
        "Compaction Filler 2",
        "compaction_test_files/compaction_filler_2.md",
        "Large non-confidential memo for pushing the notebook context meter toward compaction prompts.",
        (
            "Add this to the basket when testing notebook compaction thresholds.",
            "The content is generated locally so the repo does not store giant fixture blobs.",
            "Use with the other compaction filler memos to trigger 75% and 90% warning cards.",
        ),
    ),
    ProjectEntry(
        "project-compaction-filler-3",
        "Memos",
        "Compaction Filler 3",
        "compaction_test_files/compaction_filler_3.md",
        "Large non-confidential memo for pushing the notebook context meter toward compaction prompts.",
        (
            "Add this to the basket when testing notebook compaction thresholds.",
            "The content is generated locally so the repo does not store giant fixture blobs.",
            "Use with the other compaction filler memos to trigger 75% and 90% warning cards.",
        ),
    ),
    ProjectEntry(
        "project-compaction-filler-4",
        "Memos",
        "Compaction Filler 4",
        "compaction_test_files/compaction_filler_4.md",
        "Large non-confidential memo for pushing the notebook context meter toward compaction prompts.",
        (
            "Add this to the basket when testing notebook compaction thresholds.",
            "The content is generated locally so the repo does not store giant fixture blobs.",
            "Use with the other compaction filler memos to trigger 75% and 90% warning cards.",
        ),
    ),
    ProjectEntry(
        "project-longform-essay",
        "Summaries",
        "Summary 1",
        "summary_1.md",
        "A slower editorial surface with a heavier document and context basket.",
        (
            "Useful for testing longer text in the writing pane.",
            "Lets us see whether the shell still reads as a writing environment.",
            "Good fallback once the demo manuscript path feels stable.",
        ),
    ),
    ProjectEntry(
        "project-notebook",
        "Transcripts",
        "Transcript 1 - Participant 1 - 5.1.26",
        "interviews/2026/participant_1/transcript_1_participant_1_5_1_26.md",
        "A notebook-shaped input for retrieval and source promotion experiments.",
        (
            "Makes the left rail feel like a real project selector.",
            "Provides a second document archetype without extra plumbing.",
            "Helps us test navigation labels before engine integration lands.",
        ),
    ),
    ProjectEntry(
        "project-root-transcript",
        "Transcripts",
        "Transcript Root Example",
        "transcript_root_example.md",
        "A root-level transcript placeholder beside the nested interview archive.",
        (
            "Shows that transcripts can live directly inside Transcripts.",
            "Keeps the nested interview example from being the only transcript shape.",
            "Useful for testing transcript restrictions without folder navigation.",
        ),
    ),
    ProjectEntry(
        "project-lit-review",
        "Literature",
        "Article 1 - Last, First - Title",
        "literature_reviews/leadership/article_1_last_first_title.md",
        "A source-heavy document for literature tracking, notes, and evidence selection.",
        (
            "Makes the literature section immediately visible in the browser.",
            "Gives tomorrow's browser iteration a stronger research-oriented shape.",
            "Useful once retrieval results start mapping to source documents.",
        ),
    ),
    ProjectEntry(
        "project-root-literature",
        "Literature",
        "Article Root Example",
        "article_root_example.md",
        "A root-level literature item beside the nested literature review folder.",
        (
            "Shows that literature files can live outside folders.",
            "Makes duplicate and move testing easier directly inside Literature.",
            "Keeps the demo browser from looking artificially folder-only.",
        ),
    ),
)

PROJECT_ENTRY_MAP = {entry.slug: entry for entry in PROJECT_ENTRIES}
PROJECT_CATEGORY_FOLDERS = {
    "Drafts": "drafts",
    "Memos": "memos",
    "Summaries": "summaries",
    "Transcripts": "transcripts",
    "Literature": "literature",
}


class ProjectBrowserTree(Tree[ProjectNodeInfo]):
    BINDINGS = [
        *(binding for binding in Tree.BINDINGS if binding.key not in {"enter", "space"}),
        Binding("enter", "request_update", "Update item", priority=True),
        Binding("space", "toggle_marked_cursor", "Select", priority=True),
        Binding("delete", "request_delete", "Delete", priority=True),
        Binding("backspace", "request_delete", "Delete", priority=True),
    ]

    class DeleteRequested(Message):
        def __init__(self, project_browser: "ProjectBrowserTree") -> None:
            super().__init__()
            self.project_browser = project_browser

    class UpdateRequested(Message):
        def __init__(self, project_browser: "ProjectBrowserTree") -> None:
            super().__init__()
            self.project_browser = project_browser

    class DoubleSelected(Message):
        def __init__(self, project_browser: "ProjectBrowserTree", info: ProjectNodeInfo) -> None:
            super().__init__()
            self.project_browser = project_browser
            self.info = info

    def __init__(self) -> None:
        self._wrapped_continuations: dict[int, Text] = {}
        super().__init__("Project Browser", id=PROJECT_BROWSER_ID)
        self.show_root = False
        self.auto_expand = False
        self._section_nodes: dict[str, Tree.Node[ProjectNodeInfo]] = {}
        self._folder_nodes: dict[tuple[str, str], Tree.Node[ProjectNodeInfo]] = {}
        self._entry_nodes: dict[str, Tree.Node[ProjectNodeInfo]] = {}
        self._dynamic_slugs: set[str] = set()
        self._marked_slugs: set[str] = set()
        self._normal_click_anchor_slug: str | None = None
        self._last_click_signature: tuple[int | None, bool, bool, bool, int, int] | None = None
        self._last_click_time: float = 0.0
        self._suppress_next_select_cursor_line: int | None = None
        self._build_tree()

    def _build_tree(self, entries: tuple[ProjectEntry, ...] = PROJECT_ENTRIES) -> None:
        root = self.root
        for category, section_info in PROJECT_SECTION_INFO.items():
            section = root.add(category, data=section_info)
            self._section_nodes[category] = section
            section.expand()
            for entry in entries:
                if entry.category != category:
                    continue
                parent = self._ensure_folder_node(category, str(Path(entry.location).parent))
                leaf = parent.add_leaf(
                    self._entry_label(entry.title, entry.slug),
                    data=ProjectNodeInfo(
                        "entry",
                        entry.title,
                        entry.summary,
                        entry.bullets,
                        entry.location,
                        entry.slug,
                    ),
                )
                self._entry_nodes[entry.slug] = leaf
        root.expand()

    def reset_entries(self, entries: tuple[ProjectEntry, ...]) -> None:
        self.root.remove_children()
        self._wrapped_continuations.clear()
        self._section_nodes.clear()
        self._folder_nodes.clear()
        self._entry_nodes.clear()
        self._dynamic_slugs.clear()
        self._marked_slugs.clear()
        self._normal_click_anchor_slug = None
        self._last_click_signature = None
        self._last_click_time = 0.0
        self._suppress_next_select_cursor_line = None
        self._build_tree(entries)
        self.refresh()

    def add_dynamic_entry(
        self,
        *,
        category: str,
        slug: str,
        title: str,
        location: str,
        summary: str,
        bullets: tuple[str, ...],
    ) -> None:
        if slug in self._dynamic_slugs:
            return
        display_location = self._display_location(category, location)
        parent = self._ensure_folder_node(category, str(Path(display_location).parent))
        if parent is None:
            return
        leaf = parent.add_leaf(
            self._entry_label(title, slug),
            data=ProjectNodeInfo(
                "entry",
                title,
                summary,
                bullets,
                display_location,
                slug,
            ),
        )
        parent.expand()
        self._entry_nodes[slug] = leaf
        self._dynamic_slugs.add(slug)

    def _ensure_folder_node(self, category: str, folder_path: str | None) -> Tree.Node[ProjectNodeInfo] | None:
        section = self._section_nodes.get(category)
        if section is None:
            return None
        normalized = "" if folder_path in {None, "", "."} else str(Path(str(folder_path)))
        if not normalized or normalized == ".":
            return section
        current = section
        accumulated: list[str] = []
        for part in Path(normalized).parts:
            if part in {"", "."}:
                continue
            accumulated.append(part)
            key = (category, str(Path(*accumulated)))
            existing = self._folder_nodes.get(key)
            if existing is None:
                folder_info = ProjectNodeInfo(
                    "folder",
                    part,
                    f"Folder in {category.lower()}.",
                    (f"Folder path: {key[1]}",),
                    key[1],
                    None,
                )
                existing = current.add(part, data=folder_info)
                existing.expand()
                self._folder_nodes[key] = existing
            current = existing
        section.expand()
        return current

    def _display_location(self, category: str, location: str) -> str:
        category_root = PROJECT_CATEGORY_FOLDERS.get(category)
        if not category_root:
            return location
        path = Path(location)
        parts = path.parts
        if parts and parts[0] == category_root:
            relative = Path(*parts[1:]) if len(parts) > 1 else Path("")
            return relative.as_posix()
        return location

    def add_folder(self, *, category: str, folder_path: str) -> None:
        self._ensure_folder_node(category, folder_path)
        self.refresh()

    def select_folder(self, *, category: str, folder_path: str) -> bool:
        normalized = str(Path(folder_path))
        node = self._folder_nodes.get((category, normalized))
        if node is None:
            return False
        current = node.parent
        while current is not None:
            current.expand()
            current = current.parent
        node.expand()
        _ = self._tree_lines
        self.move_cursor(node, animate=False)
        self.refresh()
        return True

    def remove_folder(self, *, category: str, folder_path: str) -> bool:
        normalized = str(Path(folder_path))
        key = (category, normalized)
        node = self._folder_nodes.get(key)
        if node is None:
            return False
        for child in tuple(node.children):
            child.remove()
        node.remove()
        for folder_key in tuple(self._folder_nodes):
            folder_category, folder_note = folder_key
            if folder_category == category and (folder_note == normalized or folder_note.startswith(f"{normalized}/")):
                self._folder_nodes.pop(folder_key, None)
        self.refresh()
        return True

    def add_trash_entry(
        self,
        *,
        slug: str,
        title: str,
        location: str,
        summary: str,
        bullets: tuple[str, ...],
        category: str | None = None,
        folder_path: str = "",
    ) -> None:
        if slug in self._dynamic_slugs:
            return
        section = self._section_nodes.get("Trash")
        if section is None:
            return
        parent = self._ensure_trash_parent(section, category=category, folder_path=folder_path)
        leaf = parent.add_leaf(
            self._entry_label(title, slug),
            data=ProjectNodeInfo(
                "trash_entry",
                title,
                summary,
                bullets,
                location,
                slug,
            ),
        )
        parent.expand()
        self._entry_nodes[slug] = leaf
        self._dynamic_slugs.add(slug)

    def _ensure_trash_parent(
        self,
        section: Tree.Node[ProjectNodeInfo],
        *,
        category: str | None,
        folder_path: str,
    ) -> Tree.Node[ProjectNodeInfo]:
        if not category:
            section.expand()
            return section
        category_key = ("Trash", category)
        category_node = self._folder_nodes.get(category_key)
        if category_node is None:
            category_node = section.add(
                category,
                data=ProjectNodeInfo(
                    "trash_category",
                    category,
                    f"Deleted {category.lower()} staged for restore or permanent deletion.",
                    ("Trash mirror category.",),
                    category,
                    None,
                ),
            )
            category_node.expand()
            self._folder_nodes[category_key] = category_node
        current = category_node
        normalized = "" if folder_path in {"", "."} else str(Path(folder_path))
        accumulated: list[str] = []
        for part in Path(normalized).parts:
            if part in {"", "."}:
                continue
            accumulated.append(part)
            key = ("Trash", str(Path(category, *accumulated)))
            existing = self._folder_nodes.get(key)
            if existing is None:
                folder_note = str(Path(category, *accumulated))
                existing = current.add(
                    part,
                    data=ProjectNodeInfo(
                        "trash_folder",
                        part,
                        f"Deleted folder in {category.lower()}.",
                        (f"Trash folder path: {folder_note}",),
                        folder_note,
                        None,
                    ),
                )
                existing.expand()
                self._folder_nodes[key] = existing
            current = existing
        section.expand()
        return current

    def selected_entry_info(self) -> ProjectNodeInfo | None:
        info = self.selected_info()
        if info is None or info.kind not in {"entry", "trash_entry"}:
            return None
        return info

    def rename_entry(self, slug: str, title: str) -> ProjectNodeInfo | None:
        node = self._entry_nodes.get(slug)
        if node is None or node.data is None or node.data.kind != "entry":
            return None
        new_location = str(Path(*(Path(node.data.note or title).parts[:-1])) / title) if node.data.note else title
        updated = replace(node.data, title=title, note=new_location)
        node.data = updated
        node.set_label(self._entry_label(title, slug))
        return updated

    def move_entry(self, slug: str, *, category: str, title: str, location: str) -> ProjectNodeInfo | None:
        old_node = self._entry_nodes.get(slug)
        if old_node is None or old_node.data is None or old_node.data.kind != "entry":
            return None
        old_summary = old_node.data.summary
        old_bullets = old_node.data.bullets
        display_location = self._display_location(category, location)
        old_node.remove()
        parent = self._ensure_folder_node(category, str(Path(display_location).parent))
        if parent is None:
            return None
        leaf = parent.add_leaf(
            self._entry_label(title, slug),
            data=ProjectNodeInfo("entry", title, old_summary, old_bullets, display_location, slug),
        )
        parent.expand()
        self._entry_nodes[slug] = leaf
        return leaf.data

    def _entry_label(self, title: str, slug: str | None, *, width: int | None = None) -> Text:
        prefix = "[*] " if slug in self._marked_slugs else ""
        label = Text(f"{prefix}{self._wrapped_title_lines(title, width=width, prefix_width=len(prefix))[0]}")
        if slug == "current-draft":
            label.stylize("bold")
        return label

    def _wrapped_title_lines(self, title: str, *, width: int | None = None, prefix_width: int = 0) -> tuple[str, ...]:
        usable_width = max(8, (width or PROJECT_BROWSER_LABEL_WRAP_WIDTH) - prefix_width)
        lines = wrap(
            title,
            width=usable_width,
            break_long_words=True,
            break_on_hyphens=False,
        )
        return tuple(lines) or (title,)

    def _available_label_width(self, path: list[Tree.Node[ProjectNodeInfo]]) -> int:
        line = _TreeLine(path, True)
        indent_width = line._get_guide_width(self.guide_depth, self.show_root)
        # Tree labels include the entry text after guide/branch characters.
        return max(8, min(PROJECT_BROWSER_LABEL_WRAP_WIDTH, self.size.width - indent_width - 1))

    def _build(self) -> None:
        """Build visible tree lines, including continuation rows for long file names."""
        self._wrapped_continuations.clear()
        lines: list[_TreeLine[ProjectNodeInfo]] = []
        add_line = lines.append

        def add_node(
            path: list[Tree.Node[ProjectNodeInfo]],
            node: Tree.Node[ProjectNodeInfo],
            last: bool,
        ) -> None:
            child_path = [*path, node]
            node._line = len(lines)
            label_width = self._available_label_width(child_path)
            if node.data is not None and node.data.kind in {"entry", "trash_entry"}:
                node.set_label(self._entry_label(node.data.title, node.data.slug, width=label_width))
            add_line(_TreeLine(child_path, last))
            if node.data is not None and node.data.kind in {"entry", "trash_entry"}:
                for title_line in self._wrapped_title_lines(
                    node.data.title,
                    width=label_width,
                    prefix_width=len("[*] ") if node.data.slug in self._marked_slugs else 0,
                )[1:]:
                    line_number = len(lines)
                    self._wrapped_continuations[line_number] = Text(title_line)
                    add_line(_TreeLine(child_path, last))
            if node._expanded:
                for child_last, child in loop_last(node._children):
                    add_node(child_path, child, child_last)

        if self.show_root:
            add_node([], self.root, True)
        else:
            for last, node in loop_last(self.root._children):
                add_node([], node, last)

        self._tree_lines_cached = lines

        def get_line_width(line: _TreeLine[ProjectNodeInfo]) -> int:
            return self.get_label_width(line.node) + line._get_guide_width(
                self.guide_depth,
                self.show_root,
            )

        width = max([get_line_width(line) for line in lines], default=self.size.width)
        self.virtual_size = Size(width, len(lines))
        if self.cursor_line != -1:
            if self.cursor_node is not None:
                self.cursor_line = self.cursor_node._line
            if self.cursor_line >= len(lines):
                self.cursor_line = -1

    def _render_line(self, y: int, x1: int, x2: int, base_style) -> Strip:
        continuation = self._wrapped_continuations.get(y)
        if continuation is None:
            return super()._render_line(y, x1, x2, base_style)
        width = self.size.width
        line = self._tree_lines[y]
        indent_width = line._get_guide_width(self.guide_depth, self.show_root)
        line_style = (base_style or Style.null()) + Style(meta={"line": y})
        label_style = self.get_component_rich_style("tree--label", partial=True)
        if line.node._selected and self.has_focus:
            label_style += self.get_component_rich_style("tree--cursor", partial=False)
        label_style += Style(meta={"node": line.node._id})
        fallback_style = line_style
        text = Text(" " * indent_width, style=line_style)
        continuation_text = continuation.copy()
        continuation_text.stylize(label_style)
        text.append(continuation_text)
        segments = [
            Segment(segment.text, segment.style or fallback_style, segment.control)
            for segment in text.render(self.app.console)
        ]
        segments = line_pad(segments, 0, max(width - text.cell_len, 0), fallback_style)
        return Strip(segments).crop(x1, x2)

    def action_cursor_down(self) -> None:
        if self.cursor_line == -1:
            self.cursor_line = 0
        else:
            line = self.cursor_line + 1
            while line in self._wrapped_continuations:
                line += 1
            self.cursor_line = line
        self.scroll_to_line(self.cursor_line, animate=False)

    def action_cursor_up(self) -> None:
        if self.cursor_line == -1:
            self.cursor_line = self.last_line
        else:
            line = self.cursor_line - 1
            while line in self._wrapped_continuations:
                line -= 1
            self.cursor_line = line
        self.scroll_to_line(self.cursor_line, animate=False)

    def action_request_delete(self) -> None:
        self.post_message(self.DeleteRequested(self))

    def action_request_update(self) -> None:
        node = self.get_node_at_line(self.cursor_line) if self.cursor_line >= 0 else self.cursor_node
        info = None if node is None else node.data
        if info is not None and info.kind in {"section", "folder", "trash_category", "trash_folder"} and node is not None:
            self._toggle_node(node)
            return
        if info is not None and info.kind == "entry":
            self.post_message(self.UpdateRequested(self))
            return
        super().action_select_cursor()

    def action_select_cursor(self) -> None:
        node = self.get_node_at_line(self.cursor_line) if self.cursor_line >= 0 else self.cursor_node
        if self.cursor_line == self._suppress_next_select_cursor_line:
            self._suppress_next_select_cursor_line = None
            return
        info = None if node is None else node.data
        if info is not None and info.kind in {"section", "folder", "trash_category", "trash_folder"} and node is not None:
            self._toggle_node(node)
            return
        super().action_select_cursor()

    def action_toggle_marked_cursor(self) -> None:
        node = self.get_node_at_line(self.cursor_line) if self.cursor_line >= 0 else self.cursor_node
        info = None if node is None else node.data
        if info is None:
            return
        if info.kind in {"section", "folder", "trash_category", "trash_folder"} and node is not None:
            self._toggle_node(node)
            return
        if info.kind not in {"entry", "trash_entry"}:
            return
        self.toggle_marked_entry(info.slug)

    async def _on_click(self, event: events.Click) -> None:
        handled = self._handle_project_browser_click(event)
        if handled:
            self._mark_click_handled(event)
            return
        await super()._on_click(event)

    @on(events.Click)
    def on_click(self, event: events.Click) -> None:
        if self._click_was_handled(event):
            return
        if self._handle_project_browser_click(event):
            self._mark_click_handled(event)

    def _click_was_handled(self, event: events.Click) -> bool:
        return bool(getattr(event, "_exegesis_project_browser_handled", False))

    def _mark_click_handled(self, event: events.Click) -> None:
        setattr(event, "_exegesis_project_browser_handled", True)

    def _handle_project_browser_click(self, event: events.Click) -> bool:
        line = self._event_line(event)
        if self._is_duplicate_click(event, line):
            event.stop()
            return True
        node = self.get_node_at_line(line) if line is not None else None
        info = None if node is None else node.data
        if event.shift and line is not None:
            if info is not None and info.kind in {"entry", "trash_entry"}:
                anchor_info = self._multi_select_anchor_info(clicked_slug=info.slug)
                if anchor_info is None:
                    self.toggle_marked_entry(info.slug)
                    self.cursor_line = self._canonical_line_for_node(node, line)
                    event.stop()
                    return True
                previous_count = len(self._marked_slugs)
                if anchor_info.slug != info.slug:
                    self._marked_slugs.add(anchor_info.slug)
                if info.slug in self._marked_slugs:
                    self._marked_slugs.remove(info.slug)
                else:
                    self._marked_slugs.add(info.slug)
                self._collapse_single_marked_entry(previous_count=previous_count)
                self._refresh_entry_labels({anchor_info.slug, info.slug, *self._marked_slugs})
                self.cursor_line = self._canonical_line_for_node(node, line)
                event.stop()
                return True
        if event.chain >= 2 and line is not None:
            if info is not None and info.kind in {"entry", "trash_entry"}:
                self.cursor_line = self._canonical_line_for_node(node, line)
                self._normal_click_anchor_slug = info.slug
                self.post_message(self.DoubleSelected(self, info))
                event.stop()
                return True
        if line is not None:
            if info is not None and info.kind in {"section", "folder", "trash_category", "trash_folder"}:
                self.cursor_line = self._canonical_line_for_node(node, line)
                self._suppress_next_select_cursor_line = self.cursor_line
                self._toggle_node(node)
                event.stop()
                return True
            if info is not None and info.kind in {"entry", "trash_entry"}:
                self._select_entry_node(node, line=line, remember_anchor=True)
                event.stop()
                return True
        return False

    def _is_duplicate_click(self, event: events.Click, line: int | None) -> bool:
        signature = (line, event.shift, event.ctrl, event.meta, event.chain, event.button)
        event_time = event.time
        is_duplicate = (
            self._last_click_signature == signature
            and event_time >= self._last_click_time
            and event_time - self._last_click_time < 0.025
        )
        self._last_click_signature = signature
        self._last_click_time = event_time
        return is_duplicate

    def _select_entry_node(
        self,
        node: Tree.Node[ProjectNodeInfo],
        *,
        line: int,
        remember_anchor: bool,
    ) -> None:
        info = node.data
        self.cursor_line = self._canonical_line_for_node(node, line)
        if info is not None and remember_anchor:
            self._normal_click_anchor_slug = info.slug
        if self._marked_slugs:
            self.clear_marked_entries()
        self.post_message(Tree.NodeSelected(node))

    def _canonical_line_for_node(self, node: Tree.Node[ProjectNodeInfo], line: int) -> int:
        return node._line if node._line >= 0 else line

    def _multi_select_anchor_info(self, *, clicked_slug: str | None) -> ProjectNodeInfo | None:
        anchor_info = self._entry_info_for_slug(self._normal_click_anchor_slug)
        if anchor_info is not None and anchor_info.slug != clicked_slug:
            return anchor_info
        return None

    def _entry_info_for_slug(self, slug: str | None) -> ProjectNodeInfo | None:
        if slug is None:
            return None
        node = self._entry_nodes.get(slug)
        if node is None or node.data is None or node.data.kind not in {"entry", "trash_entry"}:
            return None
        return node.data

    def _event_line(self, event: events.Click) -> int | None:
        line = event.style.meta.get("line")
        if isinstance(line, int):
            return line
        node_id = event.style.meta.get("node")
        if node_id is not None:
            try:
                node = self.get_node_by_id(node_id)
            except Exception:
                node = None
            if node is not None and node._line >= 0:
                return node._line
        return int(event.y + self.scroll_y)

    def selected_info(self) -> ProjectNodeInfo | None:
        node = self.cursor_node
        return None if node is None else node.data

    def toggle_marked_entry(self, slug: str | None) -> None:
        if slug is None:
            return
        node = self._entry_nodes.get(slug)
        if node is None or node.data is None or node.data.kind not in {"entry", "trash_entry"}:
            return
        previous_count = len(self._marked_slugs)
        if slug in self._marked_slugs:
            self._marked_slugs.remove(slug)
        else:
            self._marked_slugs.add(slug)
        self._collapse_single_marked_entry(previous_count=previous_count)
        self._refresh_entry_labels({slug, *self._marked_slugs})
        self.refresh()

    def mark_entry(self, slug: str | None) -> None:
        if slug is None or slug in self._marked_slugs:
            return
        node = self._entry_nodes.get(slug)
        if node is None or node.data is None or node.data.kind not in {"entry", "trash_entry"}:
            return
        self._marked_slugs.add(slug)
        node.set_label(self._entry_label(node.data.title, slug))
        self.refresh()

    def _collapse_single_marked_entry(self, *, previous_count: int) -> None:
        if previous_count <= 1 or len(self._marked_slugs) != 1:
            return
        remaining_slug = next(iter(self._marked_slugs))
        self._marked_slugs.clear()
        self._normal_click_anchor_slug = None
        self._refresh_entry_labels({remaining_slug})

    def _refresh_entry_labels(self, slugs: set[str]) -> None:
        for slug in slugs:
            marked_node = self._entry_nodes.get(slug)
            if marked_node is not None and marked_node.data is not None:
                marked_node.set_label(self._entry_label(marked_node.data.title, slug))

    def marked_entry_infos(self, *, kinds: set[str] | None = None) -> tuple[ProjectNodeInfo, ...]:
        infos: list[ProjectNodeInfo] = []
        for slug in self._marked_slugs:
            node = self._entry_nodes.get(slug)
            if node is None or node.data is None:
                continue
            if kinds is not None and node.data.kind not in kinds:
                continue
            infos.append(node.data)
        return tuple(sorted(infos, key=lambda info: info.title.casefold()))

    def clear_marked_entries(self, slugs: set[str] | None = None) -> None:
        clearing = set(self._marked_slugs if slugs is None else slugs)
        self._marked_slugs.difference_update(clearing)
        for slug in clearing:
            node = self._entry_nodes.get(slug)
            if node is not None and node.data is not None:
                node.set_label(self._entry_label(node.data.title, slug))
        self.refresh()

    def selected_category(self) -> str | None:
        info = self.selected_info()
        if info is None:
            return None
        if info.kind == "section":
            return info.title
        if info.kind == "folder":
            return self._category_for_node(self.cursor_node)
        node = self.cursor_node
        return self._category_for_node(node)

    def selected_folder_path(self) -> str:
        info = self.selected_info()
        if info is None:
            return ""
        if info.kind == "folder":
            return info.note or ""
        if info.kind == "entry":
            parent = Path(info.note or info.title).parent
            return "" if str(parent) == "." else parent.as_posix()
        return ""

    def selected_container_info(self) -> ProjectNodeInfo | None:
        info = self.selected_info()
        if info is None or info.kind not in {"folder", "trash_category", "trash_folder"}:
            return None
        return info

    def selected_container_entry_infos(self, *, kinds: set[str]) -> tuple[ProjectNodeInfo, ...]:
        node = self.cursor_node
        if node is None or node.data is None or node.data.kind not in {"folder", "trash_category", "trash_folder"}:
            return ()
        return self.descendant_entry_infos(node, kinds=kinds)

    def descendant_entry_infos(
        self,
        node: Tree.Node[ProjectNodeInfo],
        *,
        kinds: set[str],
    ) -> tuple[ProjectNodeInfo, ...]:
        infos: list[ProjectNodeInfo] = []
        for child in node.children:
            if child.data is None:
                continue
            if child.data.kind in kinds:
                infos.append(child.data)
            elif child.children:
                infos.extend(self.descendant_entry_infos(child, kinds=kinds))
        return tuple(sorted(infos, key=lambda info: (info.note or "", info.title.casefold())))

    def _category_for_node(self, node: Tree.Node[ProjectNodeInfo] | None) -> str | None:
        current = node
        while current is not None:
            if current.data is not None and current.data.kind == "section":
                return current.data.title
            current = current.parent
        return None

    def remove_selected_entry(self) -> ProjectNodeInfo | None:
        node = self.cursor_node
        if node is None or node.data is None or node.data.kind != "entry" or node.data.slug == "current-draft":
            return None
        removed = node.data
        if removed.slug is not None:
            self._entry_nodes.pop(removed.slug, None)
            self._marked_slugs.discard(removed.slug)
        if removed.slug in self._dynamic_slugs:
            self._dynamic_slugs.remove(removed.slug)
        parent = node.parent
        sibling = node.previous_sibling or node.next_sibling or parent
        node.remove()
        if sibling is not None:
            self.move_cursor(sibling, animate=False)
        return removed

    def remove_entry(self, slug: str) -> ProjectNodeInfo | None:
        node = self._entry_nodes.get(slug)
        if node is None or node.data is None or node.data.slug == "current-draft":
            return None
        removed = node.data
        self._entry_nodes.pop(slug, None)
        self._marked_slugs.discard(slug)
        self._dynamic_slugs.discard(slug)
        parent = node.parent
        sibling = node.previous_sibling or node.next_sibling or parent
        node.remove()
        if removed.kind == "trash_entry" and parent is not None:
            self._prune_empty_trash_containers(parent)
            sibling = None
        if sibling is not None:
            self.move_cursor(sibling, animate=False)
        return removed

    def _prune_empty_trash_containers(self, node: Tree.Node[ProjectNodeInfo]) -> None:
        current = node
        while current is not None and current.data is not None and current.data.kind in {"trash_folder", "trash_category"}:
            parent = current.parent
            if current.children:
                break
            folder_note = current.data.note or current.data.title
            for folder_key, folder_node in tuple(self._folder_nodes.items()):
                if folder_node is current or (folder_key[0] == "Trash" and folder_key[1] == folder_note):
                    self._folder_nodes.pop(folder_key, None)
            current.remove()
            current = parent


class ProjectPane(Vertical):
    class NewProjectRequested(Message):
        def __init__(self, project_pane: "ProjectPane") -> None:
            super().__init__()
            self.project_pane = project_pane

    class OpenProjectRequested(Message):
        def __init__(self, project_pane: "ProjectPane") -> None:
            super().__init__()
            self.project_pane = project_pane

    class CreateRequested(Message):
        def __init__(self, project_pane: "ProjectPane", category: str) -> None:
            super().__init__()
            self.project_pane = project_pane
            self.category = category

    class ImportRequested(Message):
        def __init__(self, project_pane: "ProjectPane") -> None:
            super().__init__()
            self.project_pane = project_pane

    class DeleteRequested(Message):
        def __init__(self, project_pane: "ProjectPane") -> None:
            super().__init__()
            self.project_pane = project_pane

    class RestoreRequested(Message):
        def __init__(self, project_pane: "ProjectPane") -> None:
            super().__init__()
            self.project_pane = project_pane

    class RenameProjectRequested(Message):
        def __init__(self, project_pane: "ProjectPane") -> None:
            super().__init__()
            self.project_pane = project_pane

    class UpdateItemRequested(Message):
        def __init__(self, project_pane: "ProjectPane") -> None:
            super().__init__()
            self.project_pane = project_pane

    def __init__(self) -> None:
        super().__init__(id=PROJECT_PANE_COPY.pane_id, classes="shell-pane")
        self.border_title = PROJECT_PANE_COPY.title
        self._project_name = PROJECT_NAME

    def compose(self) -> ComposeResult:
        with Vertical(id="project-project-actions"):
            yield Button("New Project", id=PROJECT_NEW_PROJECT_ID, variant="primary")
            yield Button("Project Browser", id=PROJECT_OPEN_PROJECT_ID, variant="primary")
        yield ProjectTitle(f"[b]{self._project_name}[/b]", id="project-header")
        yield ProjectBrowserTree()
        with Vertical(id="project-actions"):
            with Horizontal(classes="project-action-row"):
                yield Button("New Draft", id=PROJECT_NEW_DRAFT_ID, variant="primary")
            with Horizontal(classes="project-action-row"):
                yield Button("New Memo", id=PROJECT_NEW_MEMO_ID, variant="primary")
            with Horizontal(classes="project-action-row"):
                yield Button("New Summary", id=PROJECT_NEW_SUMMARY_ID, variant="primary")
            with Horizontal(classes="project-action-row"):
                yield Button("New Transcript", id=PROJECT_NEW_TRANSCRIPT_ID, variant="primary")
            with Horizontal(classes="project-action-row"):
                yield Button("New Literature", id=PROJECT_NEW_LITERATURE_ID, variant="primary")
            with Horizontal(classes="project-action-row"):
                yield Button("New Folder", id=PROJECT_NEW_FOLDER_ID, variant="primary")
            with Horizontal(classes="project-action-row"):
                yield Button("Import", id=PROJECT_IMPORT_ID, variant="primary")
            with Horizontal(id="project-delete-action-row", classes="project-action-row"):
                yield Button("Delete", id=PROJECT_DELETE_ID, variant="warning")
                yield Button("Delete Forever", id=PROJECT_TRASH_DELETE_ID, variant="error", classes="trash-context-action")
                yield Button("Restore", id=PROJECT_TRASH_RESTORE_ID, variant="warning", classes="trash-context-action")

    def on_mount(self) -> None:
        self.set_trash_action_mode(False)

    def set_project_name(self, project_name: str) -> None:
        self._project_name = project_name
        self.query_one("#project-header", ProjectTitle).update(f"[b]{project_name}[/b]")

    def reset_project_entries(self, entries: tuple[ProjectEntry, ...]) -> None:
        self.query_one(ProjectBrowserTree).reset_entries(entries)
        self.set_trash_action_mode(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == PROJECT_NEW_PROJECT_ID:
            self.post_message(self.NewProjectRequested(self))
        elif button_id == PROJECT_OPEN_PROJECT_ID:
            self.post_message(self.OpenProjectRequested(self))
        elif button_id == PROJECT_NEW_DRAFT_ID:
            self.post_message(self.CreateRequested(self, "Drafts"))
        elif button_id == PROJECT_NEW_MEMO_ID:
            self.post_message(self.CreateRequested(self, "Memos"))
        elif button_id == PROJECT_NEW_SUMMARY_ID:
            self.post_message(self.CreateRequested(self, "Summaries"))
        elif button_id == PROJECT_NEW_TRANSCRIPT_ID:
            self.post_message(self.CreateRequested(self, "Transcripts"))
        elif button_id == PROJECT_NEW_LITERATURE_ID:
            self.post_message(self.CreateRequested(self, "Literature"))
        elif button_id == PROJECT_NEW_FOLDER_ID:
            self.post_message(self.CreateRequested(self, "Folder"))
        elif button_id == PROJECT_IMPORT_ID:
            self.post_message(self.ImportRequested(self))
        elif button_id == PROJECT_DELETE_ID:
            self.post_message(self.DeleteRequested(self))
        elif button_id == PROJECT_TRASH_DELETE_ID:
            self.post_message(self.DeleteRequested(self))
        elif button_id == PROJECT_TRASH_RESTORE_ID:
            self.post_message(self.RestoreRequested(self))

    def on_project_browser_tree_delete_requested(self, message: ProjectBrowserTree.DeleteRequested) -> None:
        self.post_message(self.DeleteRequested(self))

    def on_project_browser_tree_update_requested(self, message: ProjectBrowserTree.UpdateRequested) -> None:
        self.post_message(self.UpdateItemRequested(self))

    def on_project_title_rename_requested(self, message: "ProjectTitle.RenameRequested") -> None:
        message.stop()
        self.post_message(self.RenameProjectRequested(self))

    def add_project_entry(
        self,
        *,
        category: str,
        slug: str,
        title: str,
        location: str,
        summary: str,
        bullets: tuple[str, ...],
    ) -> None:
        self.query_one(ProjectBrowserTree).add_dynamic_entry(
            category=category,
            slug=slug,
            title=title,
            location=location,
            summary=summary,
            bullets=bullets,
        )

    def add_folder(self, *, category: str, folder_path: str) -> None:
        self.query_one(ProjectBrowserTree).add_folder(category=category, folder_path=folder_path)

    def select_folder(self, *, category: str, folder_path: str) -> bool:
        return self.query_one(ProjectBrowserTree).select_folder(category=category, folder_path=folder_path)

    def remove_folder(self, *, category: str, folder_path: str) -> bool:
        return self.query_one(ProjectBrowserTree).remove_folder(category=category, folder_path=folder_path)

    def add_trash_entry(
        self,
        *,
        slug: str,
        title: str,
        location: str,
        summary: str,
        bullets: tuple[str, ...],
        category: str | None = None,
        folder_path: str = "",
    ) -> None:
        self.query_one(ProjectBrowserTree).add_trash_entry(
            slug=slug,
            title=title,
            location=location,
            summary=summary,
            bullets=bullets,
            category=category,
            folder_path=folder_path,
        )

    def add_transcript_entry(
        self,
        *,
        slug: str,
        title: str,
        location: str,
        summary: str,
        bullets: tuple[str, ...],
    ) -> None:
        self.add_project_entry(
            category="Transcripts",
            slug=slug,
            title=title,
            location=location,
            summary=summary,
            bullets=bullets,
        )

    def selected_category(self) -> str | None:
        return self.query_one(ProjectBrowserTree).selected_category()

    def selected_entry_info(self) -> ProjectNodeInfo | None:
        return self.query_one(ProjectBrowserTree).selected_entry_info()

    def set_trash_action_mode(self, enabled: bool) -> None:
        self.query_one(f"#{PROJECT_DELETE_ID}", Button).display = not enabled
        self.query_one(f"#{PROJECT_TRASH_DELETE_ID}", Button).display = enabled
        self.query_one(f"#{PROJECT_TRASH_RESTORE_ID}", Button).display = enabled

    def selected_folder_path(self) -> str:
        return self.query_one(ProjectBrowserTree).selected_folder_path()

    def selected_container_info(self) -> ProjectNodeInfo | None:
        return self.query_one(ProjectBrowserTree).selected_container_info()

    def selected_container_entry_infos(self, *, kinds: set[str]) -> tuple[ProjectNodeInfo, ...]:
        return self.query_one(ProjectBrowserTree).selected_container_entry_infos(kinds=kinds)

    def marked_entry_infos(self, *, kinds: set[str] | None = None) -> tuple[ProjectNodeInfo, ...]:
        return self.query_one(ProjectBrowserTree).marked_entry_infos(kinds=kinds)

    def clear_marked_entries(self, slugs: set[str] | None = None) -> None:
        self.query_one(ProjectBrowserTree).clear_marked_entries(slugs)

    def rename_entry(self, slug: str, title: str) -> ProjectNodeInfo | None:
        return self.query_one(ProjectBrowserTree).rename_entry(slug, title)

    def move_entry(self, slug: str, *, category: str, title: str, location: str) -> ProjectNodeInfo | None:
        return self.query_one(ProjectBrowserTree).move_entry(slug, category=category, title=title, location=location)

    def remove_selected_entry(self) -> ProjectNodeInfo | None:
        return self.query_one(ProjectBrowserTree).remove_selected_entry()

    def remove_entry(self, slug: str) -> ProjectNodeInfo | None:
        return self.query_one(ProjectBrowserTree).remove_entry(slug)


class ProjectTitle(Static, can_focus=True):
    BINDINGS = [
        Binding("enter", "rename_project", "Rename project", show=False),
    ]

    class RenameRequested(Message):
        def __init__(self, title: "ProjectTitle") -> None:
            super().__init__()
            self.title = title

    def on_click(self, event: events.Click) -> None:
        self.focus()
        if event.chain >= 2:
            event.stop()
            self.post_message(self.RenameRequested(self))

    def action_rename_project(self) -> None:
        self.post_message(self.RenameRequested(self))


__all__ = [
    "CURRENT_DRAFT_BULLETS",
    "CURRENT_DRAFT_LOCATION",
    "CURRENT_DRAFT_NAME",
    "CURRENT_DRAFT_SUMMARY",
    "PROJECT_DELETE_ID",
    "PROJECT_TRASH_DELETE_ID",
    "PROJECT_TRASH_RESTORE_ID",
    "PROJECT_ENTRIES",
    "PROJECT_ENTRY_MAP",
    "PROJECT_IMPORT_ID",
    "PROJECT_NAME",
    "PROJECT_NEW_DRAFT_ID",
    "PROJECT_NEW_LITERATURE_ID",
    "PROJECT_NEW_FOLDER_ID",
    "PROJECT_NEW_MEMO_ID",
    "PROJECT_NEW_PROJECT_ID",
    "PROJECT_NEW_SUMMARY_ID",
    "PROJECT_NEW_TRANSCRIPT_ID",
    "PROJECT_OPEN_PROJECT_ID",
    "PROJECT_PANE_COPY",
    "PROJECT_SECTION_INFO",
    "ProjectEntry",
    "ProjectNodeInfo",
    "ProjectPane",
    "ProjectBrowserTree",
    "ProjectTitle",
]
