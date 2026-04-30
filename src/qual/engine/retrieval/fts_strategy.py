from __future__ import annotations

import time
from typing import Any, Callable

from src.qual.engine.retrieval.interface import StrategyRun


class FTSStrategy:
    id = "fts"

    def __init__(self, runner: Callable[[Any, tuple[str, ...]], list[Any]], *, now_fn=None) -> None:
        self._runner = runner
        self._now_fn = now_fn or time.perf_counter_ns

    def supports(self, query: Any) -> bool:
        return True

    def clear_cache(self) -> None:
        """Preserve the old mutation hook while FTS retrieval remains uncached."""

    def retrieve(self, query: Any, *, candidate_doc_ids: tuple[str, ...]) -> StrategyRun:
        """Execute the underlying ``runner`` against the current FTS index."""

        started = int(self._now_fn())
        hits = self._runner(query, candidate_doc_ids)
        elapsed_ns = max(0, int(self._now_fn()) - started)
        elapsed_ms = elapsed_ns // 1_000_000
        return StrategyRun(strategy_id=self.id, hits=hits, elapsed_ms=elapsed_ms, cache_used=False)
