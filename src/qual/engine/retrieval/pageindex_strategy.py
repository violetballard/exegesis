"""Compatibility-only PageIndex strategy shim.

This module stays importable for legacy callers, but the active retrieval lane
remains FTS-first and does not wire PageIndex into engine orchestration.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.qual.docindex.service import DocIndexService
from src.qual.engine.retrieval.interface import StrategyRun


class PageIndexStrategy:
    id = "pageindex"

    def __init__(self, service: DocIndexService, read_doc_text, *, now_fn=None) -> None:
        self._service = service
        self._read_doc_text = read_doc_text
        self._now_fn = now_fn or (lambda: datetime.now(UTC))

    def supports(self, query: Any) -> bool:
        # Import-compatible shim only; engine routing must not select PageIndex
        # while the FTS-first retrieval lane is authoritative.
        return False

    def retrieve(self, query: Any, *, candidate_doc_ids: tuple[str, ...]) -> StrategyRun:
        raise NotImplementedError("PageIndex retrieval is deferred in the FTS-first MVP lane")


__all__ = ["PageIndexStrategy"]
