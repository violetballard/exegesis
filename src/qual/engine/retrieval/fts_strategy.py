from __future__ import annotations

import copy
import time
from collections.abc import Mapping
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
    # provides an identical query object (equality is based on ``==`` for the
    # supplied type) and the same candidate doc ID set, we return the cached
    # hits and set ``cache_used=True`` in the ``StrategyRun`` payload.
    #
    # ``use_cache=False`` bypasses cache reads for that call, but the fresh
    # result still replaces the one-slot cache entry. That keeps the cache
    # coherent if a caller forces a fresh read before a later default cached
    # call for the same retrieval key.
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

    def retrieve(self, query: Any, *, candidate_doc_ids: tuple[str, ...], use_cache: bool = True) -> StrategyRun:
        """Execute the underlying ``runner`` or return a cached result.

        The function measures execution time in milliseconds. If the incoming
        request matches the most‑recent cache entry we bypass the runner and mark
        ``cache_used=True``; otherwise we invoke the runner, refresh the
        one-slot cache with the fresh result, and report ``cache_used=False``.
        """
        normalized_candidate_doc_ids = self._normalize_candidate_doc_ids(candidate_doc_ids)
        cache_key = self._make_cache_key(query, normalized_candidate_doc_ids)
        # Check for a cache hit before measuring time – a cached path is fast
        # enough that timing it would be misleading.
        if use_cache and self._cache_key == cache_key and self._cache_hits is not None:
            return StrategyRun(
                strategy_id=self.id,
                hits=copy.deepcopy(self._cache_hits),
                elapsed_ms=0,
                cache_used=True,
            )

        started = int(self._now_fn())
        hits = self._runner(query, normalized_candidate_doc_ids)
        # Keep the one-slot cache coherent even when the caller bypasses cache
        # reads for this request.
        self._cache_key = cache_key
        self._cache_hits = copy.deepcopy(hits)

        elapsed_ns = max(0, int(self._now_fn()) - started)
        elapsed_ms = elapsed_ns // 1_000_000
        return StrategyRun(strategy_id=self.id, hits=hits, elapsed_ms=elapsed_ms, cache_used=False)

    def clear_cache(self) -> None:
        """Drop the one-entry cache after any retrieval corpus change."""

        self._cache_key = None
        self._cache_hits = None

    @staticmethod
    def _make_cache_key(query: Any, candidate_doc_ids: tuple[str, ...]) -> tuple[Any, tuple[str, ...]]:
        """Return a defensive snapshot for the one-entry cache key.

        Retrieval queries are usually immutable dataclasses, but some callers may
        still hand in mutable query-shaped objects. Snapshotting the query keeps
        later caller mutations from silently altering the cached key.
        """

        query_snapshot = FTSStrategy._canonicalize_query_for_cache(query)
        return query_snapshot, FTSStrategy._normalize_candidate_doc_ids(candidate_doc_ids)

    @staticmethod
    def _normalize_candidate_doc_ids(candidate_doc_ids: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted({str(doc_id) for doc_id in candidate_doc_ids}))

    @staticmethod
    def _canonicalize_query_for_cache(query: Any) -> Any:
        """Normalize query-shaped objects so equivalent requests share the cache key."""

        payload = FTSStrategy._query_payload(query)
        if payload is None:
            try:
                return copy.deepcopy(query)
            except Exception:
                return query
        return payload

    @staticmethod
    def _query_payload(query: Any) -> dict[str, object] | None:
        if isinstance(query, Mapping):
            payload = dict(query)
        elif all(hasattr(query, field) for field in ("query_text", "scope", "intent", "constraints")):
            payload = {
                "query_text": getattr(query, "query_text"),
                "scope": getattr(query, "scope"),
                "intent": getattr(query, "intent"),
                "constraints": getattr(query, "constraints"),
                "confidentiality_profile": getattr(query, "confidentiality_profile", None),
            }
        else:
            return None

        constraints = FTSStrategy._constraint_payload(payload.get("constraints"))
        return {
            "query_text": FTSStrategy._normalize_query_text(payload.get("query_text")),
            "scope": FTSStrategy._normalize_scope(payload.get("scope")),
            "intent": FTSStrategy._normalize_text(payload.get("intent")),
            "constraints": constraints,
            "confidentiality_profile": FTSStrategy._normalize_text(payload.get("confidentiality_profile")),
        }

    @staticmethod
    def _constraint_payload(constraints: object) -> dict[str, object]:
        if isinstance(constraints, Mapping):
            payload = dict(constraints)
        elif constraints is None:
            payload = {}
        else:
            payload = {
                "max_results": getattr(constraints, "max_results", None),
                "doc_types": getattr(constraints, "doc_types", None),
                "date_range": getattr(constraints, "date_range", None),
                "require_citations": getattr(constraints, "require_citations", None),
                "section_hint": getattr(constraints, "section_hint", None),
                "prefer_exact_matches": getattr(constraints, "prefer_exact_matches", None),
            }
        return {
            "max_results": int(payload.get("max_results", 0) or 0),
            "doc_types": FTSStrategy._normalize_list_like(payload.get("doc_types")),
            "date_range": FTSStrategy._normalize_optional_list_like(payload.get("date_range")),
            "require_citations": bool(payload.get("require_citations", False)),
            "section_hint": FTSStrategy._normalize_text(payload.get("section_hint")),
            "prefer_exact_matches": bool(payload.get("prefer_exact_matches", False)),
        }

    @staticmethod
    def _normalize_query_text(value: object) -> str | None:
        text = FTSStrategy._normalize_text(value)
        if text is None:
            return None
        return " ".join(text.split())

    @staticmethod
    def _normalize_scope(value: object) -> str | None:
        text = FTSStrategy._normalize_text(value)
        if text is None:
            return None
        prefix, separator, remainder = text.partition(":")
        if separator and prefix in {"doc", "collection", "section"}:
            return f"{prefix}:{remainder.strip()}"
        return text

    @staticmethod
    def _normalize_list_like(value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            items = [value]
        else:
            try:
                items = [item for item in value if item is not None]  # type: ignore[arg-type]
            except TypeError:
                items = [value]
        normalized = {
            text for item in items if (text := FTSStrategy._normalize_text(item)) is not None
        }
        return sorted(normalized)

    @staticmethod
    def _normalize_optional_list_like(value: object) -> list[str] | None:
        if value is None:
            return None
        return FTSStrategy._normalize_list_like(value)

    @staticmethod
    def _normalize_text(value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip().casefold()
        if not text:
            return None
        return text
