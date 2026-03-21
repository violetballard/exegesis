"""Engine retrieval strategies.

The retrieval lane keeps this package as the narrow public surface for the
engine's retrieval orchestration code.
"""

from src.qual.engine.retrieval.fts_strategy import FTSStrategy
from src.qual.engine.retrieval.interface import RetrievalStrategy, StrategyRun
from src.qual.engine.retrieval.policy import (
    FTS_FIRST_POLICY,
    active_strategy_ids as _active_strategy_ids,
    deferred_strategy_ids as _deferred_strategy_ids,
    fts_first_policy_snapshot as _fts_first_policy_snapshot,
)

ACTIVE_STRATEGY_IDS = _active_strategy_ids()
DEFERRED_STRATEGY_IDS = _deferred_strategy_ids()


def active_strategy_ids() -> tuple[str, ...]:
    """Return the deterministic strategy set enabled for the MVP."""

    return _active_strategy_ids()


def deferred_strategy_ids() -> tuple[str, ...]:
    """Return the deferred retrieval strategies for the MVP."""

    return _deferred_strategy_ids()


def retrieval_policy_snapshot() -> dict[str, object]:
    """Return the canonical FTS-first retrieval policy snapshot."""

    return _fts_first_policy_snapshot()


__all__ = [
    "StrategyRun",
    "RetrievalStrategy",
    "FTSStrategy",
    "FTS_FIRST_POLICY",
    "ACTIVE_STRATEGY_IDS",
    "DEFERRED_STRATEGY_IDS",
    "active_strategy_ids",
    "deferred_strategy_ids",
    "retrieval_policy_snapshot",
]
