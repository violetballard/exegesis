"""Engine retrieval strategies.

The retrieval lane keeps this package as the narrow public surface for the
engine's retrieval orchestration code.
"""

from src.qual.engine.retrieval.fts_strategy import FTSStrategy
from src.qual.engine.retrieval.interface import RetrievalStrategy, StrategyRun
from src.qual.engine.retrieval.policy import FTS_FIRST_POLICY

ACTIVE_STRATEGY_IDS = FTS_FIRST_POLICY.active_strategy_ids


def active_strategy_ids() -> tuple[str, ...]:
    """Return the deterministic strategy set enabled for the MVP."""

    return FTS_FIRST_POLICY.active_strategy_ids


__all__ = [
    "StrategyRun",
    "RetrievalStrategy",
    "FTSStrategy",
    "ACTIVE_STRATEGY_IDS",
    "active_strategy_ids",
]
