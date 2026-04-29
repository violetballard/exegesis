"""Compatibility-only embeddings strategy shim.

The embeddings lane is deferred for the MVP, so this module remains importable
without participating in the active engine retrieval path.
"""

from __future__ import annotations

from typing import Any

from src.qual.engine.retrieval.interface import StrategyRun


class EmbeddingsStrategy:
    id = "embeddings"

    def supports(self, query: Any) -> bool:
        return False

    def retrieve(self, query: Any, *, candidate_doc_ids: tuple[str, ...]) -> StrategyRun:
        raise NotImplementedError("Embeddings retrieval is deferred in the FTS-first MVP lane")


__all__ = ["EmbeddingsStrategy"]
