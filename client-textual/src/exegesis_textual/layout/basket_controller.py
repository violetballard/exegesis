from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from urllib.parse import parse_qs, quote, unquote, urlencode, urlparse

from textual.widgets import Markdown, OptionList

from exegesis_textual.layout.modals import TranscriptWarningModal
from exegesis_engine.state.models import BasketItem
from exegesis_textual.panes.basket_pane import (
    BASKET_DOCUMENTS_LIST_ID,
    BASKET_EXCERPTS_LIST_ID,
    BasketEntry,
    BasketPane,
)
from exegesis_textual.panes.document_pane import DOCUMENT_FIXTURES, DocumentPane
from exegesis_textual.panes.project_pane import ProjectPane
from exegesis_textual.services.imports import is_safe_external_link


class BasketControllerMixin:
    async def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        basket_entry = self.query_one(BasketPane).get_entry(event.option.id)
        if basket_entry is not None:
            await self._handle_basket_selection(basket_entry)
            return
        label = event.option.prompt
        control_id = event.option_list.id or "pane"
        self._set_status(f"Selected {control_id} item: {label.plain if hasattr(label, 'plain') else label}")

    async def _handle_basket_selection(self, entry: BasketEntry) -> None:
        kind_label = "document" if entry.kind == "document" else "excerpt"
        self._set_status(f"Selected basket {kind_label} from {entry.source}")
        self._show_basket_subject(entry)

    async def on_markdown_link_clicked(self, event: Markdown.LinkClicked) -> None:
        href = event.href
        if not href.startswith("exegesis://document/"):
            if href.startswith("exegesis://basket/"):
                event.stop()
                event.prevent_default()
                await self._open_basket_snapshot_link(href)
                return
            if not is_safe_external_link(href):
                event.stop()
                event.prevent_default()
                self._set_status("Blocked unsafe link action.")
                return
            self.open_url(href)
            return
        event.stop()
        event.prevent_default()
        parsed = urlparse(href)
        slug = unquote(parsed.path.lstrip("/"))
        if not slug or slug not in DOCUMENT_FIXTURES:
            self._set_status("Linked document is no longer available.")
            return
        query = parse_qs(parsed.query)
        start = self._first_int_query_value(query, "start")
        end = self._first_int_query_value(query, "end")
        document_pane = self.query_one(DocumentPane)
        if start is not None and end is not None:
            await document_pane.open_document_with_selection(slug, (start, end))
        else:
            await document_pane.open_document(slug)
        self._sync_save_controls()
        self._show_document_subject(DOCUMENT_FIXTURES[slug])
        self._set_status(f"Opened {DOCUMENT_FIXTURES[slug].title} from inspector.")

    async def _open_basket_snapshot_link(self, href: str) -> None:
        parsed = urlparse(href)
        basket_slug = unquote(parsed.path.lstrip("/"))
        entry = self.query_one(BasketPane).get_entry(basket_slug)
        if entry is None:
            self._set_status("Basket snapshot is no longer available.")
            return
        document_pane = self.query_one(DocumentPane)
        await document_pane.open_readonly_snapshot(
            slug=self._basket_snapshot_slug(entry),
            title=entry.source,
            content=entry.content,
            document_type="excerpt" if entry.kind == "excerpt" else entry.source_document_type,
            status="source_deleted",
            focus=False,
        )
        self._sync_save_controls()
        self._set_status(f"Opened deleted-source basket snapshot: {entry.source}.")

    def _first_int_query_value(self, query: dict[str, list[str]], key: str) -> int | None:
        values = query.get(key)
        if not values:
            return None
        try:
            return int(values[0])
        except ValueError:
            return None

    def on_document_pane_excerpt_requested(self, message: DocumentPane.ExcerptRequested) -> None:
        active = DOCUMENT_FIXTURES.get(message.slug)
        if active is None:
            self._set_status("Selected document is no longer available.")
            return
        excerpt_text = message.excerpt_text.strip()
        if not excerpt_text:
            self._set_status("Select text or place the cursor in a non-empty document first.")
            return
        document_id = self._document_id_by_slug.get(message.slug, active.location)
        item_id = f"excerpt:{document_id}:{message.start}-{message.end}"
        items = self._engine_adapter.add_excerpt_to_basket(
            item_id=item_id,
            label=f"Excerpt from {active.title}",
            source_document_id=document_id,
            source_document_type=active.document_type,
            selected_text=excerpt_text,
            start=message.start,
            end=message.end,
            metadata={
                "source_document_slug": message.slug,
                "source_title": active.title,
                **self._basket_source_metadata(),
            },
        )
        entry = self._sync_basket_from_engine_items(items, selected_item_id=item_id)
        self._set_status(f"Added excerpt from {active.title} to the basket.")
        self._show_basket_subject(entry)

    def on_document_pane_document_requested(self, message: DocumentPane.DocumentRequested) -> None:
        active = DOCUMENT_FIXTURES.get(message.slug)
        if active is None:
            self._set_status("Selected document is no longer available.")
            return
        if not self._add_document_slug_to_basket(message.slug):
            return

    def _add_document_slug_to_basket(self, slug: str) -> bool:
        active = DOCUMENT_FIXTURES.get(slug)
        if active is None:
            return False
        if active.is_transcript:
            self.push_screen(TranscriptWarningModal())
            self._set_status("Transcript blocked from basket in online mode.")
            return False
        document_id = self._document_id_by_slug.get(slug, active.location)
        item_id = f"document:{document_id}"
        items = self._engine_adapter.add_document_to_basket(
            document_id=document_id,
            label=active.title,
            document_type=active.document_type,
            content=active.content,
            metadata={
                "source_document_slug": slug,
                "source_title": active.title,
                **self._basket_source_metadata(),
            },
        )
        entry = self._sync_basket_from_engine_items(items, selected_item_id=item_id)
        self._set_status(f"Added document {active.title} to the basket.")
        self._show_basket_subject(entry)
        return True

    def _sync_basket_from_engine_items(self, items: list[BasketItem], *, selected_item_id: str | None = None) -> BasketEntry:
        basket = self.query_one(BasketPane)
        seen = {item.id for item in items}
        for slug in list(basket.entries):
            if slug not in seen:
                basket.remove_entry(slug)
        selected_entry: BasketEntry | None = None
        for item in items:
            entry = self._basket_entry_from_engine_item(item)
            basket.add_entry(entry)
            if item.id == selected_item_id:
                selected_entry = entry
        self._refresh_notebook_context_meter()
        if selected_entry is not None:
            return selected_entry
        if items:
            return self._basket_entry_from_engine_item(items[-1])
        raise RuntimeError("basket sync requires at least one item")

    def _refresh_basket_from_engine(self) -> None:
        basket = self.query_one(BasketPane)
        items = list(self._engine_adapter.state.basket.items)
        seen = {item.id for item in items}
        for slug in list(basket.entries):
            if slug not in seen:
                basket.remove_entry(slug)
        for item in items:
            basket.add_entry(self._basket_entry_from_engine_item(item))
        self._refresh_notebook_context_meter()

    def _basket_source_metadata(self) -> dict[str, str]:
        return {
            "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "source_status": "current",
        }

    def _basket_entry_from_engine_item(self, item: BasketItem) -> BasketEntry:
        payload = dict(item.payload)
        if item.item_type == "document":
            document_id = str(payload.get("document_id") or "")
            shell_slug = str(payload.get("source_document_slug") or self._slug_for_document_id(document_id) or "")
            title = str(payload.get("source_title") or item.label)
            document_type = str(payload.get("document_type") or "document")
            content = str(payload.get("content") or "")
            source_status = str(payload.get("source_status") or "current")
            captured_at = str(payload.get("captured_at") or "")
            return BasketEntry(
                slug=item.id,
                kind="document",
                title="Document",
                source=title,
                source_document_slug=shell_slug or None,
                source_document_type=document_type,
                summary="",
                bullets=(
                    f"Source file: {document_id}",
                    f"Source status: {source_status.replace('_', ' ')}",
                    f"Captured at: {captured_at or 'unknown'}",
                ),
                content=content,
                document_slug=shell_slug or None,
                source_document_id=document_id or None,
                source_status=source_status,
                captured_at=captured_at or None,
            )
        source_document_id = str(payload.get("source_document_id") or "")
        shell_slug = str(payload.get("source_document_slug") or self._slug_for_document_id(source_document_id) or "")
        title = str(payload.get("source_title") or item.label)
        document_type = str(payload.get("source_document_type") or "document")
        selected_text = str(payload.get("selected_text") or "")
        source_status = str(payload.get("source_status") or "current")
        captured_at = str(payload.get("captured_at") or "")
        selection_start = self._coerce_optional_int(payload.get("start"))
        selection_end = self._coerce_optional_int(payload.get("end"))
        return BasketEntry(
            slug=item.id,
            kind="excerpt",
            title="Excerpt",
            source=title,
            source_document_slug=shell_slug or None,
            source_document_type=document_type,
            summary="",
            bullets=(
                f"Source file: {source_document_id}",
                f"Source status: {source_status.replace('_', ' ')}",
                f"Captured at: {captured_at or 'unknown'}",
            ),
            content=selected_text,
            document_slug=shell_slug or None,
            source_document_id=source_document_id or None,
            source_status=source_status,
            captured_at=captured_at or None,
            selection_start=selection_start,
            selection_end=selection_end,
        )

    def _slug_for_document_id(self, document_id: str) -> str | None:
        return next((slug for slug, candidate in self._document_id_by_slug.items() if candidate == document_id), None)

    def _basket_item_matches_source(
        self,
        item: BasketItem,
        *,
        source_document_id: str | None = None,
        source_document_slug: str | None = None,
    ) -> bool:
        payload = item.payload
        candidate_id = str(payload.get("document_id") or payload.get("source_document_id") or "")
        candidate_slug = str(payload.get("source_document_slug") or self._slug_for_document_id(candidate_id) or "")
        return bool(
            (source_document_id and candidate_id == source_document_id)
            or (source_document_slug and candidate_slug == source_document_slug)
        )

    def _mark_basket_sources(
        self,
        *,
        source_document_id: str | None = None,
        source_document_slug: str | None = None,
        status: str,
    ) -> None:
        changed = False
        updated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        for item in self._engine_adapter.state.basket.items:
            if not self._basket_item_matches_source(
                item,
                source_document_id=source_document_id,
                source_document_slug=source_document_slug,
            ):
                continue
            current = str(item.payload.get("source_status") or "current")
            if current == "source_deleted" or current == status:
                continue
            item.payload["source_status"] = status
            item.payload["source_status_updated_at"] = updated_at
            changed = True
        if changed:
            self._refresh_basket_from_engine()
            self._refresh_notebook_context_meter()

    def _rebind_basket_sources_after_restore(
        self,
        *,
        old_source_document_id: str | None,
        old_source_document_slug: str | None,
        new_source_document_id: str,
        new_source_document_slug: str,
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
            if item.item_type == "document":
                item.payload["document_id"] = new_source_document_id
            else:
                item.payload["source_document_id"] = new_source_document_id
            item.payload["source_document_slug"] = new_source_document_slug
            item.payload["source_title"] = source_title
            item.payload["source_status"] = "restored"
            item.payload["source_status_updated_at"] = updated_at
            changed = True
        if changed:
            self._refresh_basket_from_engine()
            self._refresh_notebook_context_meter()

    def _add_marked_project_documents_to_basket(self) -> bool:
        marked = self.query_one(ProjectPane).marked_entry_infos(kinds={"entry"})
        eligible = [info for info in marked if info.slug is not None and info.slug in DOCUMENT_FIXTURES]
        if not eligible:
            return False
        added = 0
        blocked = 0
        for info in eligible:
            if info.slug is None:
                continue
            fixture = DOCUMENT_FIXTURES.get(info.slug)
            if fixture is None:
                continue
            if fixture.is_transcript:
                blocked += 1
                continue
            if self._add_document_slug_to_basket(info.slug):
                added += 1
        if blocked:
            self.push_screen(TranscriptWarningModal())
        if added:
            self.query_one(ProjectPane).clear_marked_entries({info.slug for info in eligible if info.slug is not None})
        if added and blocked:
            self._set_status(f"Added {added} documents to the basket. Blocked {blocked} transcript documents.")
        elif added:
            self._set_status(f"Added {added} documents to the basket.")
        elif blocked:
            self._set_status("Transcript documents are blocked from basket in online mode.")
        return True

    def _delete_selected_basket_item(self) -> None:
        selected = self.query_one(BasketPane).selected_entry()
        if selected is None:
            self._set_status("Select a basket item first.")
            return
        items = self._engine_adapter.remove_basket_item(selected.slug)
        self.query_one(BasketPane).remove_entry(selected.slug)
        if items:
            self._sync_basket_from_engine_items(items, selected_item_id=items[-1].id)
        self._set_status(f"Removed {selected.source} from the basket.")
        self._show_subject(
            "Basket",
            "Promoted context.",
            (
                "Add excerpts or whole documents from the document pane.",
                "Selected basket items can be removed with Delete.",
            ),
            None,
        )
