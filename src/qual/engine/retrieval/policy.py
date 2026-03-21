from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalPolicy:
    retrieval_backend: str
    retrieval_mode: str
    active_strategy_ids: tuple[str, ...]
    deferred_strategy_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "retrieval_backend": self.retrieval_backend,
            "retrieval_mode": self.retrieval_mode,
            "active_strategy_ids": list(self.active_strategy_ids),
            "deferred_strategy_ids": list(self.deferred_strategy_ids),
        }


FTS_FIRST_POLICY = RetrievalPolicy(
    retrieval_backend="sqlite_fts",
    retrieval_mode="fts_first",
    active_strategy_ids=("fts",),
    deferred_strategy_ids=("pageindex", "embeddings"),
)
