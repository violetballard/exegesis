from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.qual.engine.retrieval.interface import StrategyRun


class PageIndexStrategy:
    id = "pageindex"

    def __init__(self, service: DocIndexService, read_doc_text, *, now_fn=None) -> None:
        self._service = service
        self._read_doc_text = read_doc_text
        self._now_fn = now_fn or (lambda: datetime.now(UTC))

    def supports(self, query: Any) -> bool:
        # PageIndex is intentionally deferred for the FTS-first MVP.
        return False

    def retrieve(self, query: Any, *, candidate_doc_ids: tuple[str, ...]) -> StrategyRun:
        # The retrieval lane keeps this path disabled until PageIndex is
        # reintroduced as an intentional follow-on beyond the MVP.
        return StrategyRun(strategy_id=self.id, hits=[], elapsed_ms=0, cache_used=False)
