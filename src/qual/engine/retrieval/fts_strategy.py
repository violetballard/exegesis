from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass
import time
from typing import Any, Callable

from src.qual.engine.retrieval.interface import StrategyRun


class FTSStrategy:
    id = "fts"

    # NOTE: ``FTSStrategy`` is the canonical entry‑point for FTS‑first retrieval.
    # It previously executed the supplied ``runner`` on every call without any
    # caching. For many interactive workloads the same query (including the
    # candidate doc set) can be issued repeatedly – e.g. a UI that polls for new
    # results while the user is typing. Adding a tiny in‑memory cache reduces the
    # number of expensive SQLite look‑ups while keeping the implementation simple
    # and deterministic.
    #
    # The cache stores **one** recent request – the most recent ``(query,
    # candidate_doc_ids)`` tuple and its resulting hits. If a subsequent call
    # provides an equivalent query snapshot and the same ordered
    # ``candidate_doc_ids``, we return the
    # cached hits and set ``cache_used=True`` in the ``StrategyRun`` payload.
    # The cache is deliberately tiny to avoid unbounded memory growth and to keep
    # the behaviour easy to reason about for tests.
    def __init__(self, runner: Callable[[Any, tuple[str, ...]], list[Any]], *, now_fn=None) -> None:
        self._runner = runner
        self._now_fn = now_fn or time.perf_counter_ns
        # Simple one‑entry cache – ``_cache_key`` stores a (query, candidate_doc_ids)
        # pair and ``_cache_hits`` the corresponding list of hits.
        self._cache_key: tuple[Any, tuple[str, ...]] | None = None
        self._cache_hits: list[Any] | None = None

    def supports(self, query: Any) -> bool:
        return True

    def clear_cache(self) -> None:
        """Drop the cached FTS run after the underlying index changes."""

        self._cache_key = None
        self._cache_hits = None

    def retrieve(self, query: Any, *, candidate_doc_ids: tuple[str, ...]) -> StrategyRun:
        """Execute the underlying ``runner`` or return a cached result.

        The function measures execution time in milliseconds. If the incoming
        request matches the most‑recent cache entry we bypass the runner and mark
        ``cache_used=True``; otherwise we invoke the runner, store the result in
        the one‑slot cache and report ``cache_used=False``.
        """
        cache_key = self._make_cache_key(query, candidate_doc_ids)
        # Check for a cache hit before measuring time – a cached path is fast
        # enough that timing it would be misleading.
        if self._cache_key == cache_key and self._cache_hits is not None:
            return StrategyRun(
                strategy_id=self.id,
                hits=copy.deepcopy(self._cache_hits),
                elapsed_ms=0,
                cache_used=True,
            )

        started = int(self._now_fn())
        hits = self._runner(query, candidate_doc_ids)
        hit_snapshot = copy.deepcopy(hits)
        # Update the one-slot cache with the fresh result.
        self._cache_key = cache_key
        self._cache_hits = copy.deepcopy(hit_snapshot)

        elapsed_ns = max(0, int(self._now_fn()) - started)
        elapsed_ms = elapsed_ns // 1_000_000
        return StrategyRun(strategy_id=self.id, hits=hit_snapshot, elapsed_ms=elapsed_ms, cache_used=False)

    @staticmethod
    def _make_cache_key(query: Any, candidate_doc_ids: tuple[str, ...]) -> tuple[Any, tuple[str, ...]]:
        """Return a defensive snapshot for the one-entry cache key.

        Retrieval queries are usually immutable dataclasses, but some callers may
        still hand in mutable query-shaped objects. Snapshotting public query
        state keeps later caller mutations from silently altering the cached key
        and lets equivalent query-shaped inputs share one deterministic FTS run.
        """

        query_snapshot = FTSStrategy._snapshot_cache_value(query)
        return query_snapshot, tuple(candidate_doc_ids)

    @staticmethod
    def _snapshot_cache_value(value: Any) -> Any:
        if is_dataclass(value) and not isinstance(value, type):
            return FTSStrategy._snapshot_cache_value(asdict(value))
        if isinstance(value, Mapping):
            return tuple(
                (str(key), FTSStrategy._snapshot_cache_value(item))
                for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
            )
        if isinstance(value, tuple):
            return tuple(FTSStrategy._snapshot_cache_value(item) for item in value)
        if isinstance(value, list):
            return tuple(FTSStrategy._snapshot_cache_value(item) for item in value)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return tuple(FTSStrategy._snapshot_cache_value(item) for item in value)
        if hasattr(value, "__dict__"):
            return FTSStrategy._snapshot_cache_value(vars(value))
        try:
            return copy.deepcopy(value)
        except Exception:
            return repr(value)
