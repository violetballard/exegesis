from __future__ import annotations

from math import ceil
import re
from urllib.parse import quote, urlencode

from exegesis_textual.layout.modals import SummaryProgressModal
from exegesis_textual.panes.basket_pane import BasketEntry
from exegesis_textual.panes.document_pane import DOCUMENT_FIXTURES, DocumentPane, register_document_fixture
from exegesis_textual.panes.inspector_pane import InspectorPane
from exegesis_textual.panes.project_pane import ProjectNodeInfo, ProjectPane
from exegesis_textual.workflow.mistral_chat import ChatMessage
from exegesis_textual.workflow.workflow_pane import TERMINAL_CONTEXT_WINDOW_TOKENS


class InspectorControllerMixin:
    def on_inspector_pane_summary_requested(self, message: InspectorPane.SummaryRequested) -> None:
        self._request_summary(message.size, message.word_count)

    def on_summary_progress_modal_cancel_requested(self, message: SummaryProgressModal.CancelRequested) -> None:
        self._workflow_backend.cancel(message.chat_slug)
        self._set_status("Cancelling summary generation.")

    def _request_summary(self, size: str, word_count: int) -> None:
        self._save_dirty_documents()
        if not self._workflow_backend.is_configured():
            self._set_status("Open Model Settings and save a Mistral API key before generating summaries.")
            request_settings = getattr(self, "shell_request_model_settings", None)
            if callable(request_settings):
                request_settings()
            return
        self.run_worker(
            self._save_summary_from_inspector(size, word_count),
            thread=False,
            exclusive=True,
            group="inspector-summary",
        )

    def _show_subject(
        self,
        title: str,
        summary: str,
        bullets: tuple[str, ...],
        note: str | None = None,
        *,
        title_href: str | None = None,
        selection_type: str | None = None,
        word_count: int | None = None,
        token_count: int | None = None,
        token_capacity: int | None = None,
        allow_summary_actions: bool = False,
    ) -> None:
        self.query_one(InspectorPane).show_subject(
            title,
            summary,
            bullets,
            note,
            title_href=title_href,
            selection_type=selection_type,
            word_count=word_count,
            token_count=token_count,
            token_capacity=token_capacity,
            allow_summary_actions=allow_summary_actions,
        )

    def _show_document_subject(
        self,
        fixture,
        *,
        summary: str | None = None,
        bullets: tuple[str, ...] | None = None,
        note: str | None = None,
        refresh_notebook_context: bool = True,
    ) -> None:
        self._show_subject(
            fixture.title,
            summary or "",
            bullets or (),
            note or self._document_excerpt(fixture.content),
            title_href=self._document_link_href(fixture.slug),
            selection_type=fixture.document_type,
            word_count=self._count_words(fixture.content),
            token_count=self._estimate_tokens(fixture.content),
            allow_summary_actions=True,
        )
        self._sync_save_controls()
        if refresh_notebook_context:
            self._refresh_notebook_context_meter()

    def _show_trash_subject(self, info: ProjectNodeInfo) -> None:
        fixture = DOCUMENT_FIXTURES.get(info.slug or "")
        content = fixture.content if fixture is not None else self._read_trash_document_content(info.slug)
        metadata = self._trash_metadata_by_slug.get(info.slug or "", {})
        original_id = str(metadata.get("original_id") or info.note or "")
        trashed_at = str(metadata.get("trashed_at") or "")
        document_type = self._document_type_for_document_id(original_id)
        bullets = (
            *info.bullets,
            f"Original location: {original_id or 'Unknown'}",
            f"Deleted at: {trashed_at or 'Unknown'}",
        )
        note = self._document_excerpt(content) if content else "Trash file content is unavailable."
        self._show_subject(
            info.title,
            info.summary,
            bullets,
            note,
            selection_type=document_type,
            word_count=self._count_words(content) if content else None,
            token_count=self._estimate_tokens(content) if content else None,
            allow_summary_actions=bool(content),
        )

    def _read_trash_document_content(self, slug: str | None) -> str:
        if slug is None:
            return ""
        trash_id = self._trash_id_by_slug.get(slug)
        return self._read_trash_document_content_by_id(trash_id)

    def _read_trash_document_content_by_id(self, trash_id: str | None) -> str:
        if trash_id is None:
            return ""
        try:
            return self._engine_adapter.open_trash_document(trash_id).content
        except (FileNotFoundError, RuntimeError, ValueError, OSError):
            return ""

    def _document_type_for_document_id(self, document_id: str) -> str:
        category = self._category_for_document_id(document_id)
        return {
            "Drafts": "draft",
            "Memos": "memo",
            "Summaries": "summary",
            "Transcripts": "transcript",
            "Literature": "literature",
        }.get(category or "", "document")

    def _show_chat_subject(self, chat) -> None:
        self._show_subject(
            chat.title,
            chat.summary,
            chat.bullets,
            None,
            token_count=self._estimate_chat_tokens(chat),
            token_capacity=TERMINAL_CONTEXT_WINDOW_TOKENS,
        )

    def _document_excerpt(self, text: str) -> str:
        excerpt = " ".join(text.strip().split())
        if len(excerpt) > 480:
            return f"{excerpt[:479].rstrip()}…"
        return excerpt

    def _document_link_href(self, slug: str, selection_range: tuple[int, int] | None = None) -> str:
        href = f"exegesis://document/{quote(slug, safe='')}"
        if selection_range is None:
            return href
        start, end = selection_range
        return f"{href}?{urlencode({'start': start, 'end': end})}"

    def _basket_entry_link_href(self, entry: BasketEntry) -> str | None:
        if entry.source_status == "source_deleted":
            return f"exegesis://basket/{quote(entry.slug, safe='')}"
        if entry.source_document_slug is None or entry.source_document_slug not in DOCUMENT_FIXTURES:
            return None
        if entry.kind == "excerpt" and entry.selection_start is not None and entry.selection_end is not None:
            return self._document_link_href(entry.source_document_slug, (entry.selection_start, entry.selection_end))
        return self._document_link_href(entry.source_document_slug)

    def _basket_snapshot_slug(self, entry: BasketEntry) -> str:
        safe_slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", entry.slug).strip("-") or "snapshot"
        return f"basket-snapshot-{safe_slug}"

    def _coerce_optional_int(self, value: object) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _show_basket_subject(self, entry: BasketEntry) -> None:
        note = entry.content if entry.kind == "excerpt" else self._document_excerpt(entry.content)
        summary = entry.summary
        if entry.source_status != "current":
            status_summary = f"Source status: {entry.source_status.replace('_', ' ')}"
            summary = f"{summary} {status_summary}".strip()
        selection_type = "excerpt" if entry.kind == "excerpt" else entry.source_document_type
        bullets = entry.bullets
        if entry.kind == "document":
            bullets = (
                f"Source file: {entry.source_document_id or 'unknown'}",
                f"Source status: {entry.source_status.replace('_', ' ')}",
                f"Captured at: {entry.captured_at or 'unknown'}",
            )
        self._show_subject(
            entry.source,
            summary,
            bullets,
            note,
            title_href=self._basket_entry_link_href(entry),
            selection_type=selection_type,
            word_count=self._count_words(entry.content),
            token_count=self._estimate_tokens(entry.content),
            allow_summary_actions=False,
        )

    async def _save_summary_from_inspector(self, size: str, word_count: int) -> None:
        document_pane = self.query_one(DocumentPane)
        active = document_pane.active_document
        chat_slug = f"inspector-summary-{size}"
        progress_modal = SummaryProgressModal(size=size, title=active.title, chat_slug=chat_slug)
        await self.push_screen(progress_modal)
        self._set_status(f"Generating {size} summary for {active.title}.")
        try:
            context = self._shell_chat_context_model()
            prompt = (
                f"Write a {size} summary of approximately {word_count} words for "
                f"{active.title}. Save-ready summary text only."
            )
            chunks: list[str] = []
            async for event in self._workflow_backend.stream_reply(
                chat_slug,
                [ChatMessage("user", prompt)],
                context,
                request_mode="summary",
            ):
                if progress_modal.cancel_requested:
                    self._set_status("Summary generation cancelled.")
                    return
                if event.kind == "assistant_delta":
                    chunks.append(event.text)
                elif event.kind == "error":
                    self._set_status(event.error)
                    return
            if progress_modal.cancel_requested:
                self._set_status("Summary generation cancelled.")
                return
            summary_text = "".join(chunks).strip()
            if not summary_text:
                self._set_status(f"{size.capitalize()} summary returned no text.")
                return
            slug = self._next_dynamic_slug(f"summary-{size}")
            filename = f"{active.title.removesuffix('.md')}_{size}_summary_{slug.split('-')[-1]}.md"
            title = f"{size.capitalize()} summary of {active.title}"
            content = f"# {title}\n\n{summary_text}\n"
            item = self._engine_adapter.create_document(
                category="Summaries",
                title=filename,
                content=content,
                document_type="summary",
            )
            self._document_id_by_slug[slug] = item.id
            register_document_fixture(
                slug=slug,
                title=filename,
                location=item.id,
                summary=f"{size.capitalize()} summary generated from {active.title}.",
                content=content,
                document_type="summary",
            )
            self.query_one(ProjectPane).add_project_entry(
                category="Summaries",
                slug=slug,
                title=filename,
                location=item.id,
                summary=f"{size.capitalize()} summary generated from {active.title}.",
                bullets=(
                    f"Source document: {active.title}",
                    f"Target length: ~{word_count} words",
                    "Document type: summary",
                ),
            )
            await document_pane.open_document(slug)
            self._sync_save_controls()
            self._set_status(f"Saved {size} summary to Summaries: {filename}.")
            self._show_document_subject(DOCUMENT_FIXTURES[slug])
        finally:
            self._finish_summary_progress(progress_modal)

    def _finish_summary_progress(self, progress_modal: SummaryProgressModal | None) -> None:
        if progress_modal is not None and self.screen is progress_modal:
            self.pop_screen()

    def _estimate_tokens(self, text: str) -> int:
        stripped = text.strip()
        if not stripped:
            return 0
        return max(1, ceil(len(stripped) / 4))

    def _count_words(self, text: str) -> int:
        return len(re.findall(r"\b[\w'-]+\b", text))

    def _estimate_chat_tokens(self, chat) -> int:
        total_chars = sum(len(message.content) for message in chat.messages)
        structural_overhead = max(1, len(chat.messages)) * 12
        return max(0, ceil((total_chars / 4) + structural_overhead))
