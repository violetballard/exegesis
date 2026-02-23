from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Callable

from src.qual.engine.retrieval.interface import StrategyRun


class FTSStrategy:
    id = "fts"

    def __init__(self, runner: Callable[[Any, tuple[str, ...]], list[Any]], *, now_fn=None) -> None:
        self._runner = runner
        self._now_fn = now_fn or (lambda: datetime.now(UTC))

    def supports(self, query: Any) -> bool:
        return True

    def retrieve(self, query: Any, *, candidate_doc_ids: tuple[str, ...]) -> StrategyRun:
        started = self._now_fn()
        hits = self._runner(query, candidate_doc_ids)
        elapsed_ms = max(0, int((self._now_fn() - started).total_seconds() * 1000))
        return StrategyRun(strategy_id=self.id, hits=hits, elapsed_ms=elapsed_ms, cache_used=False)
