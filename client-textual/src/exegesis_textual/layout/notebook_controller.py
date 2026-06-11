from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from exegesis_textual.cards.patch_card import PatchReviewCardData
from exegesis_textual.panes.basket_pane import BasketPane
from exegesis_textual.panes.document_pane import (
    CURRENT_DRAFT_SLUG,
    DOCUMENT_FIXTURES,
    DocumentPane,
    PendingRewritePreview,
    clean_generated_rewrite_text,
    register_document_fixture,
)
from exegesis_textual.panes.project_pane import ProjectPane
from exegesis_textual.workflow.mistral_chat import ShellChatContext
from exegesis_textual.workflow.workflow_pane import (
    TERMINAL_CONTEXT_WINDOW_TOKENS,
    WORKFLOW_CARD_MAP,
    WorkflowPane,
)


class NotebookControllerMixin:
    def on_workflow_pane_chat_created(self, message: WorkflowPane.ChatCreated) -> None:
        chat = message.chat
        self._set_status(f"Created new notebook chat: {chat.title}")
        self._show_chat_subject(chat)

    def on_workflow_pane_chat_activated(self, message: WorkflowPane.ChatActivated) -> None:
        chat = message.chat
        self._show_chat_subject(chat)

    def on_workflow_pane_rewrite_proposal_ready(self, message: WorkflowPane.RewriteProposalReady) -> None:
        document_pane = self.query_one(DocumentPane)
        workflow_pane = self.query_one(WorkflowPane)
        self._rewrite_adapter.set_selection(
            document_id=message.document_slug,
            start=message.target_range[0],
            end=message.target_range[1],
            selected_text=message.original_text,
        )
        patch = self._rewrite_adapter.revise_selection(
            document_id=message.document_slug,
            instruction_text=message.instruction_text,
            source_chat_slug=message.chat_slug,
            proposed_text=clean_generated_rewrite_text(
                DOCUMENT_FIXTURES[message.document_slug].content,
                message.proposed_text,
            ),
        )
        preview = PendingRewritePreview(
            patch_id=patch.patch_id,
            document_slug=patch.document_id,
            target_range=patch.target_range,
            original_text=patch.original_text,
            proposed_text=patch.proposed_text,
            instruction_text=patch.instruction_text,
            source_chat_slug=patch.source_chat_slug,
            block_insert=message.block_insert,
        )
        document_pane.show_pending_rewrite(preview)
        workflow_pane.show_patch_review(
            PatchReviewCardData(
                patch_id=patch.patch_id,
                document_title=message.document_title,
                instruction_text=patch.instruction_text,
                source_chat_slug=patch.source_chat_slug,
                original_text=patch.original_text,
                proposed_text=patch.proposed_text,
                document_slug=patch.document_id,
                target_range=patch.target_range,
                block_insert=preview.block_insert,
            )
        )
        self._show_subject(
            "Revision Proposal",
            f"Pending rewrite for {message.document_title}.",
            (
                "Original and proposed text are shown inline in the document.",
                "The document stays read-only until you apply or reject the revision.",
                "Apply or reject the change from the Notebook card.",
            ),
            None,
        )

    async def on_workflow_pane_search_result_selected(self, message: WorkflowPane.SearchResultSelected) -> None:
        self._save_dirty_documents()
        document_pane = self.query_one(DocumentPane)
        self._navigating_search_result = True
        try:
            await document_pane.open_document_with_selection(message.document_slug, message.match_range, focus=False)
        finally:
            self._navigating_search_result = False
        self._sync_save_controls()
        active = document_pane.active_document
        self._set_status(f"Opened search result: {message.document_title}. Selection is ready to add to the basket.")
        self._show_document_subject(active, refresh_notebook_context=False)

    async def on_workflow_pane_search_result_add_to_basket_requested(self, message: WorkflowPane.SearchResultAddToBasketRequested) -> None:
        result = await self.dispatch_app_action(
            "add_document_to_basket",
            {
                "document": message.document_slug,
            },
            source="notebook",
            confirmed=True,
        )
        self.query_one(WorkflowPane).set_status(result.message)
        self._set_status(result.message)

    def on_workflow_pane_draft_requested(self, message: WorkflowPane.DraftRequested) -> None:
        document_pane = self.query_one(DocumentPane)
        workflow_pane = self.query_one(WorkflowPane)
        active_document = document_pane.active_document
        preview = document_pane.show_pending_generated_text(
            slug=active_document.slug,
            patch_id=f"draft-{uuid4()}",
            generated_text=message.generated_text,
            instruction_text=message.instruction_text,
            source_chat_slug=message.chat_slug,
            target_range=message.target_range,
            block_insert=message.block_insert,
        )
        if preview is None:
            workflow_pane.set_status("Draft generation finished, but the proposal could not be prepared.")
            return
        workflow_pane.show_patch_review(
            PatchReviewCardData(
                patch_id=preview.patch_id,
                document_title=active_document.title,
                instruction_text=preview.instruction_text,
                source_chat_slug=preview.source_chat_slug,
                original_text=preview.original_text,
                proposed_text=preview.proposed_text,
                document_slug=preview.document_slug,
                target_range=preview.target_range,
                block_insert=preview.block_insert,
            )
        )
        self._show_subject(
            "Draft Proposal",
            f"Pending draft suggestion for {active_document.title}.",
            (
                "The generated text is shown inline before it becomes part of the document.",
                "Apply or reject the draft from the Notebook card.",
                "Drafting uses the basket plus the current document as context.",
            ),
            None,
        )

    def on_workflow_pane_patch_decision_requested(self, message: WorkflowPane.PatchDecisionRequested) -> None:
        document_pane = self.query_one(DocumentPane)
        workflow_pane = self.query_one(WorkflowPane)
        is_draft_patch = message.patch_id.startswith("draft-")
        if message.decision == "apply":
            if not is_draft_patch:
                self._rewrite_adapter.apply_patch(message.patch_id)
            preview = document_pane.apply_pending_rewrite(message.patch_id, focus_selection=False)
            if preview is not None:
                self._dirty_document_slugs.add(preview.document_slug)
                self._sync_save_controls()
                self._refresh_notebook_context_meter()
                action_label = "draft" if is_draft_patch else "rewrite"
                workflow_pane.set_status(f"Applied {action_label} to {DOCUMENT_FIXTURES[preview.document_slug].title}.")
                workflow_pane.clear_patch_review(message.patch_id)
                workflow_pane.note_patch_resolution(
                    preview.source_chat_slug,
                    f"Applied {action_label} to {DOCUMENT_FIXTURES[preview.document_slug].title}.",
                )
        else:
            if not is_draft_patch:
                self._rewrite_adapter.reject_patch(message.patch_id)
            preview = document_pane.reject_pending_rewrite(message.patch_id)
            if preview is not None:
                action_label = "draft" if is_draft_patch else "rewrite"
                workflow_pane.set_status(f"Rejected {action_label} for {DOCUMENT_FIXTURES[preview.document_slug].title}.")
                workflow_pane.clear_patch_review(message.patch_id)
                workflow_pane.note_patch_resolution(
                    preview.source_chat_slug,
                    f"Rejected {action_label} for {DOCUMENT_FIXTURES[preview.document_slug].title}.",
                )
        self._sync_terminal_patch_card()
        workflow_pane.focus_editor()

    def on_workflow_pane_transcript_saved(self, message: WorkflowPane.TranscriptSaved) -> None:
        chat = message.chat
        try:
            content = message.path.read_text(encoding="utf-8")
        except OSError:
            content = f"# {chat.title}\n\n{chat.status_note}\n"
        transcript_slug = self._next_dynamic_slug("transcript")
        item = self._engine_adapter.create_document(
            category="Transcripts",
            title=chat.transcript_name,
            content=content,
            document_type="transcript",
        )
        self._document_id_by_slug[transcript_slug] = item.id
        register_document_fixture(
            slug=transcript_slug,
            title=item.label,
            location=item.id,
            summary=f"Saved transcript from {chat.title.lower()} in the notebook pane.",
            content=content,
            document_type="transcript",
            is_transcript=True,
        )
        project_pane = self.query_one(ProjectPane)
        project_pane.add_transcript_entry(
            slug=transcript_slug,
            title=item.label,
            location=item.id,
            summary=f"Saved transcript from {chat.title.lower()} in the notebook pane.",
            bullets=(
                "Saved from the active notebook tab.",
                f"Context snapshot at save time: {chat.context_available}.",
                "Opens like any other project document in the document tabs.",
            ),
        )
        self._set_status(f"Saved transcript: {chat.transcript_name}")
        self._show_subject(
            chat.transcript_name,
            f"Saved transcript from {chat.title.lower()} in the notebook pane.",
            (
                "Transcript saved as markdown from the active notebook chat.",
                f"Context snapshot at save time: {chat.context_available}.",
                "The project browser now lists it under Transcripts.",
            ),
            None,
        )

    def on_workflow_pane_chat_compacted(self, message: WorkflowPane.ChatCompacted) -> None:
        chat = message.chat
        try:
            content = message.path.read_text(encoding="utf-8")
        except OSError:
            content = f"# {chat.title}\n\n{chat.status_note}\n"
        transcript_slug = self._next_dynamic_slug("transcript")
        item = self._engine_adapter.create_document(
            category="Transcripts",
            title=message.path.name,
            content=content,
            document_type="transcript",
            relative_path=f"transcripts/Compacted Conversations/{message.path.name}",
        )
        self._document_id_by_slug[transcript_slug] = item.id
        summary = f"Full raw notebook transcript saved before compacting {chat.title.lower()}."
        register_document_fixture(
            slug=transcript_slug,
            title=item.label,
            location=item.id,
            summary=summary,
            content=content,
            document_type="transcript",
            is_transcript=True,
        )
        self.query_one(ProjectPane).add_transcript_entry(
            slug=transcript_slug,
            title=item.label,
            location=item.id,
            summary=summary,
            bullets=(
                "Saved automatically before notebook compaction.",
                "Double-select or use Restore to start a new chat from the full transcript.",
                f"Context snapshot at compaction: {chat.context_available}.",
            ),
        )
        self._set_status(f"Compacted chat and saved full transcript: {item.id}")

    def _shell_chat_context_model(self) -> ShellChatContext:
        raw = self.shell_chat_context()
        return ShellChatContext(
            project_name=str(raw.get("project_name", "Current Project")),
            document_title=str(raw.get("document_title", "current_draft.md")),
            document_type=str(raw.get("document_type", "draft")),
            document_content=str(raw.get("document_content", "")),
            confidentiality_mode=str(raw.get("confidentiality_mode", "non-confidential")),
            basket_context=str(raw.get("basket_context", "")),
            selected_text=str(raw.get("selected_text", "")),
            selection_start=raw.get("selection_start") if isinstance(raw.get("selection_start"), int) else None,
            selection_end=raw.get("selection_end") if isinstance(raw.get("selection_end"), int) else None,
        )

    def shell_chat_context(self) -> dict[str, object]:
        document = self.query_one(DocumentPane).active_document
        selection = self.query_one(DocumentPane).current_selection_snapshot()
        confidential = self._current_project_is_confidential()
        document_content = "" if document.is_transcript and not confidential else document.content
        return {
            "project_name": self._current_project_name,
            "document_title": document.title,
            "document_type": document.document_type,
            "document_content": document_content,
            "confidentiality_mode": "local-confidential" if confidential else "non-confidential",
            "basket_context": self._serialize_basket_context(),
            "selected_text": selection.selected_text if selection is not None else "",
            "selection_start": selection.start if selection is not None else None,
            "selection_end": selection.end if selection is not None else None,
        }

    def _refresh_notebook_context_meter(self) -> None:
        try:
            self.query_one(WorkflowPane).refresh_context_meter()
        except Exception:
            return

    def shell_rewrite_context(self) -> dict[str, object] | None:
        document_pane = self.query_one(DocumentPane)
        active = document_pane.active_document
        selection = document_pane.current_selection_snapshot()
        if selection is None:
            return None
        return {
            "document_slug": active.slug,
            "document_title": active.title,
            "target_range": (selection.start, selection.end),
            "original_text": selection.selected_text,
        }

    def shell_search_documents(self, query: str) -> list[dict[str, object]]:
        self._refresh_searchable_document_fixtures()
        needle = query.strip().casefold()
        if not needle:
            return []
        results: list[dict[str, object]] = []
        for fixture in DOCUMENT_FIXTURES.values():
            haystack = fixture.content.casefold()
            matches: list[dict[str, object]] = []
            start_index = 0
            while True:
                index = haystack.find(needle, start_index)
                if index == -1:
                    break
                matches.append(
                    {
                        "snippet": self._match_snippet(fixture.content, index, len(query)),
                        "match_range": (index, index + len(query)),
                    }
                )
                start_index = index + max(1, len(needle))
            if not matches:
                continue
            first_match = matches[0]
            results.append(
                {
                    "document_slug": fixture.slug,
                    "title": fixture.title,
                    "document_type": fixture.document_type,
                    "snippet": first_match["snippet"],
                    "token_count": self._estimate_tokens(fixture.content),
                    "location": fixture.location,
                    "match_range": first_match["match_range"],
                    "matches": matches,
                }
            )
        return results

    def _refresh_searchable_document_fixtures(self) -> None:
        for slug, document_id in self._document_id_by_slug.items():
            if slug in self._dirty_document_slugs:
                continue
            fixture = DOCUMENT_FIXTURES.get(slug)
            if fixture is None:
                continue
            path = self._project_root / document_id
            if not path.exists() or not path.is_file():
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if content != fixture.content:
                fixture.content = content

    def _match_snippet(self, content: str, start: int, query_length: int) -> str:
        window = 140
        snippet_start = max(0, start - window)
        snippet_end = min(len(content), start + query_length + window)
        snippet = content[snippet_start:snippet_end].replace("\n", " ")
        snippet = " ".join(snippet.split())
        if snippet_start > 0:
            snippet = f"…{snippet}"
        if snippet_end < len(content):
            snippet = f"{snippet}…"
        return snippet

    def _is_compacted_conversation_slug(self, slug: str | None) -> bool:
        if slug is None:
            return False
        document_id = self._document_id_by_slug.get(slug)
        if not document_id:
            return False
        path = Path(document_id)
        return len(path.parts) >= 3 and path.parts[0] == "transcripts" and path.parts[1] == "Compacted Conversations"

    def _restore_selected_compacted_conversation(self) -> bool:
        selected = self.query_one(ProjectPane).selected_entry_info()
        if selected is None or selected.kind != "entry" or not self._is_compacted_conversation_slug(selected.slug):
            return False
        self._restore_compacted_conversation_chat(selected.slug)
        return True

    def _restore_compacted_conversation_chat(self, slug: str | None) -> None:
        if slug is None or not self._is_compacted_conversation_slug(slug):
            self._set_status("Select a compacted conversation transcript first.")
            return
        fixture = DOCUMENT_FIXTURES.get(slug)
        if fixture is None:
            self._set_status("Compacted conversation transcript is no longer available.")
            return
        self.run_worker(
            self._restore_compacted_conversation_chat_async(slug, fixture.title, fixture.content, fixture.location),
            thread=False,
            exclusive=True,
            group="workflow-restore",
        )

    async def _restore_compacted_conversation_chat_async(
        self,
        slug: str,
        title: str,
        content: str,
        location: str,
    ) -> None:
        workflow = self.query_one(WorkflowPane)
        chat = await workflow.new_chat_from_transcript(title=title, transcript_content=content, location=location)
        self._set_status(f"Started {chat.title} from {title}.")
        self._show_chat_subject(chat)

    def _serialize_basket_context(self) -> str:
        priority = {"draft": 0, "memo": 1, "summary": 2, "transcript": 3, "literature": 4}
        entries = list(self.query_one(BasketPane).entries.values())
        entries.sort(
            key=lambda entry: (
                priority.get(entry.source_document_type, 99),
                0 if entry.kind == "excerpt" else 1,
                entry.source.lower(),
                entry.slug,
            )
        )
        chunks: list[str] = []
        remaining = self._workflow_context_window_tokens() * 4
        for index, entry in enumerate(entries, start=1):
            header = (
                f"[{index}] kind={entry.kind}\n"
                f"source_title={entry.source}\n"
                f"source_slug={entry.source_document_slug or entry.document_slug or ''}\n"
                f"source_type={entry.source_document_type}\n"
                f"source_status={entry.source_status}\n"
                f"captured_at={entry.captured_at or ''}\n"
                "content:\n"
            )
            content = entry.content.strip()
            budget = max(0, remaining - len(header))
            if budget <= 0:
                break
            if len(content) > budget:
                content = content[: max(0, budget - 1)].rstrip() + "…"
            chunk = f"{header}{content}".strip()
            chunks.append(chunk)
            remaining -= len(chunk) + 2
            if remaining <= 0:
                break
        return "\n\n".join(chunks)

    def _workflow_context_window_tokens(self) -> int:
        try:
            workflow = self.query_one(WorkflowPane)
        except Exception:
            return TERMINAL_CONTEXT_WINDOW_TOKENS
        context_window = getattr(workflow, "_context_window_tokens", None)
        if callable(context_window):
            try:
                return int(context_window())
            except (TypeError, ValueError):
                return TERMINAL_CONTEXT_WINDOW_TOKENS
        return TERMINAL_CONTEXT_WINDOW_TOKENS
