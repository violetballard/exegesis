from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalPolicy:
    retrieval_backend: str
    retrieval_mode: str
    active_strategy_ids: tuple[str, ...]
    deferred_strategy_ids: tuple[str, ...]

    def as_snapshot(self) -> dict[str, object]:
        return {
            "retrieval_backend": self.retrieval_backend,
            "retrieval_mode": self.retrieval_mode,
            "active_strategy_ids": list(self.active_strategy_ids),
            "deferred_strategy_ids": list(self.deferred_strategy_ids),
        }

    def as_dict(self) -> dict[str, object]:
        """Backward-compatible alias for older retrieval callers."""

        return self.as_snapshot()


def active_strategy_ids() -> tuple[str, ...]:
    return FTS_FIRST_POLICY.active_strategy_ids


def deferred_strategy_ids() -> tuple[str, ...]:
    return FTS_FIRST_POLICY.deferred_strategy_ids


def primary_strategy_id() -> str:
    """Return the single active retrieval strategy for the MVP."""

    return FTS_FIRST_POLICY.active_strategy_ids[0]


def fts_first_policy_snapshot() -> dict[str, object]:
    return FTS_FIRST_POLICY.as_snapshot()


FTS_FIRST_POLICY = RetrievalPolicy(
    retrieval_backend="sqlite_fts",
    retrieval_mode="fts_first",
    active_strategy_ids=("fts",),
    # PageIndex and embeddings remain deferred identifiers for the MVP.
    # They are not active strategy implementations in this lane.
    deferred_strategy_ids=("pageindex", "embeddings"),
)
