"""Engine retrieval strategies.

The retrieval lane keeps this package as the narrow public surface for the
engine's retrieval orchestration code.
"""

from src.qual.engine.retrieval.fts_strategy import FTSStrategy
from src.qual.engine.retrieval.interface import RetrievalStrategy, StrategyRun

ACTIVE_STRATEGY_IDS = ("fts",)


def active_strategy_ids() -> tuple[str, ...]:
    """Return the deterministic strategy set enabled for the MVP."""

    return ACTIVE_STRATEGY_IDS


__all__ = [
    "StrategyRun",
    "RetrievalStrategy",
    "FTSStrategy",
    "ACTIVE_STRATEGY_IDS",
    "active_strategy_ids",
]
