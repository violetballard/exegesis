from __future__ import annotations

"""Engine retrieval strategies.

The retrieval lane keeps this package as the narrow public surface for the
engine's retrieval orchestration code.
"""

from collections.abc import Mapping
from functools import lru_cache
from importlib import import_module

from src.qual.engine.retrieval.fts_strategy import FTSStrategy
from src.qual.engine.retrieval.interface import RetrievalStrategy, StrategyRun
from src.qual.engine.retrieval.policy import (
    FTS_FIRST_POLICY,
    active_strategy_ids as _active_strategy_ids,
    deferred_strategy_ids as _deferred_strategy_ids,
    fts_first_policy_snapshot as _fts_first_policy_snapshot,
    primary_strategy_id as _primary_strategy_id,
)
from src.qual.engine.retrieval.payload import (
    build_retrieval_citation_bundle_from_result,
    build_retrieval_doc_bundle_from_result,
    build_retrieval_excerpt_bundle_from_result,
    build_retrieval_context_bundle_from_result,
    build_retrieval_downstream_payload,
    build_retrieval_downstream_payload_from_result,
    build_retrieval_provenance_from_result,
    build_retrieval_source_bundle_from_result,
)


def build_retrieval_query(
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: Mapping[str, object] | RetrievalConstraints | None = None,
    confidentiality_profile: str = "confidential",
) -> RetrievalQuery:
    """Return the canonical FTS-first retrieval query object.

    Delegate to the canonical retrieval package so engine callers share the same
    normalization path as the retrieval-owned facade.
    """

    _ensure_runtime_types()
    return _delegate_to_retrieval(
        "build_retrieval_query",
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
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


def primary_strategy_id() -> str:
    """Return the only active retrieval strategy used by the MVP."""

    return _primary_strategy_id()


@lru_cache(maxsize=1)
def _retrieval_module():
    """Resolve the canonical retrieval facade once for engine delegation."""

    return import_module("src.qual.retrieval")


def _bind_runtime_types() -> None:
    """Populate annotation globals without creating an eager import cycle."""

    service_module = import_module("src.qual.retrieval.service")
    globals()["RetrievalConstraints"] = service_module.RetrievalConstraints
    globals()["RetrievalQuery"] = service_module.RetrievalQuery


def _ensure_runtime_types() -> None:
    """Bind retrieval dataclasses once the retrieval service has finished importing."""

    if "RetrievalConstraints" in globals() and "RetrievalQuery" in globals():
        return
    _bind_runtime_types()


def __getattr__(name: str):
    """Lazily expose canonical retrieval dataclasses on the engine surface."""

    if name in {"RetrievalConstraints", "RetrievalQuery"}:
        _ensure_runtime_types()
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _delegate_to_retrieval(name: str, *args, **kwargs):
    return getattr(_retrieval_module(), name)(*args, **kwargs)


def retrieve_fts_context_bundle(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_fts_context_bundle", *args, **kwargs)


def retrieve_fts_citation_bundle(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_fts_citation_bundle", *args, **kwargs)


def retrieve_fts_source_bundle(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_fts_source_bundle", *args, **kwargs)


def retrieve_fts_provenance_bundle(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_fts_provenance_bundle", *args, **kwargs)


def retrieve_fts_doc_bundle(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_fts_doc_bundle", *args, **kwargs)


def retrieve_fts_excerpt_bundle(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_fts_excerpt_bundle", *args, **kwargs)


def retrieve_fts_excerpt(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_fts_excerpt", *args, **kwargs)


def fetch_fts_excerpt(*args, **kwargs):
    return _delegate_to_retrieval("fetch_fts_excerpt", *args, **kwargs)


def fetch_excerpt(*args, **kwargs):
    return _delegate_to_retrieval("fetch_excerpt", *args, **kwargs)


def retrieve_auto_excerpt(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_auto_excerpt", *args, **kwargs)


def retrieve_fts_payload(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_fts_payload", *args, **kwargs)


def retrieve_fts(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_fts", *args, **kwargs)


def retrieve_auto(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_auto", *args, **kwargs)


def retrieve_auto_context_bundle(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_auto_context_bundle", *args, **kwargs)


def retrieve_auto_citation_bundle(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_auto_citation_bundle", *args, **kwargs)


def retrieve_auto_source_bundle(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_auto_source_bundle", *args, **kwargs)


def retrieve_auto_provenance_bundle(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_auto_provenance_bundle", *args, **kwargs)


def retrieve_auto_doc_bundle(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_auto_doc_bundle", *args, **kwargs)


def retrieve_auto_excerpt_bundle(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_auto_excerpt_bundle", *args, **kwargs)


def retrieve_auto_payload(*args, **kwargs):
    return _delegate_to_retrieval("retrieve_auto_payload", *args, **kwargs)

__all__ = [
    "StrategyRun",
    "RetrievalStrategy",
    "FTSStrategy",
    "FTS_FIRST_POLICY",
    "ACTIVE_STRATEGY_IDS",
    "DEFERRED_STRATEGY_IDS",
    "active_strategy_ids",
    "deferred_strategy_ids",
    "build_retrieval_query",
    "retrieval_policy_snapshot",
    "primary_strategy_id",
    "build_retrieval_downstream_payload",
    "build_retrieval_downstream_payload_from_result",
    "build_retrieval_citation_bundle_from_result",
    "build_retrieval_doc_bundle_from_result",
    "build_retrieval_excerpt_bundle_from_result",
    "build_retrieval_context_bundle_from_result",
    "build_retrieval_provenance_from_result",
    "build_retrieval_source_bundle_from_result",
    "retrieve_fts",
    "retrieve_fts_citation_bundle",
    "retrieve_fts_context_bundle",
    "retrieve_fts_source_bundle",
    "retrieve_fts_provenance_bundle",
    "retrieve_fts_doc_bundle",
    "retrieve_fts_excerpt_bundle",
    "retrieve_fts_excerpt",
    "fetch_fts_excerpt",
    "fetch_excerpt",
    "retrieve_fts_payload",
    "retrieve_auto_excerpt",
    "retrieve_auto",
    "retrieve_auto_context_bundle",
    "retrieve_auto_citation_bundle",
    "retrieve_auto_source_bundle",
    "retrieve_auto_provenance_bundle",
    "retrieve_auto_doc_bundle",
    "retrieve_auto_excerpt_bundle",
    "retrieve_auto_payload",
]
