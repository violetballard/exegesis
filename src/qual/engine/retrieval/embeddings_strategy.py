from __future__ import annotations

from typing import Any

from src.qual.engine.retrieval.interface import StrategyRun


class EmbeddingsStrategy:
    id = "embeddings"

    def supports(self, query: Any) -> bool:
        return False

    def retrieve(self, query: Any, *, candidate_doc_ids: tuple[str, ...]) -> StrategyRun:
        return StrategyRun(strategy_id=self.id, hits=[], elapsed_ms=0, cache_used=False)
