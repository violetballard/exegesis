from __future__ import annotations

from src.qual.engine.retrieval import build_retrieval_query as engine_build_retrieval_query
from src.qual.retrieval.service import (
    RetrievalConstraints,
    RetrievalDocHit,
    RetrievalHit,
    RetrievalQuery,
    RetrievalResult,
    RetrievalService,
)


def _build_retrieval_query(
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | RetrievalConstraints | None = None,
    confidentiality_profile: str = "confidential",
) -> RetrievalQuery:
    return engine_build_retrieval_query(
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
    )


def build_retrieval_query(
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | RetrievalConstraints | None = None,
    confidentiality_profile: str = "confidential",
) -> RetrievalQuery:
    """Return the canonical retrieval query used by both facades."""

    return engine_build_retrieval_query(
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
    )


def _call_fts_retrieval(
    service: RetrievalService,
    *,
    method_name: str,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
):
    query = _build_retrieval_query(
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
    )
    return getattr(service, method_name)(query)


def retrieve_fts(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
):
    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_fts",
    )


def retrieve_fts_payload(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return the canonical downstream payload for FTS-first retrieval."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_fts_payload",
    )


def retrieve_fts_context_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return the canonical retrieval context bundle for a single FTS retrieval."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_fts_context_bundle",
    )


def retrieve_fts_citation_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return the canonical citation/provenance bundle for a single FTS retrieval."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_fts_citation_bundle",
    )


def retrieve_fts_source_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return the canonical source bundle for a single FTS retrieval."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_fts_source_bundle",
    )


def retrieve_fts_doc_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return the canonical doc-focused bundle for a single FTS retrieval."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_fts_doc_bundle",
    )


def retrieve_fts_excerpt_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return the canonical excerpt-focused bundle for a single FTS retrieval."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_fts_excerpt_bundle",
    )


def retrieve_fts_excerpt(
    service: RetrievalService,
    *,
    excerpt_id: str,
) -> dict[str, object]:
    """Return an excerpt payload using the canonical FTS-only lookup path."""

    return service.retrieve_fts_excerpt(excerpt_id)


def fetch_fts_excerpt(
    service: RetrievalService,
    *,
    excerpt_id: str,
) -> dict[str, object]:
    """Backward-compatible alias for the canonical FTS-only excerpt lookup path."""

    return service.fetch_fts_excerpt(excerpt_id)


def retrieve_auto(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
):
    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_auto",
    )


def retrieve_auto_context_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return the canonical retrieval context bundle for the FTS-first auto path."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_auto_context_bundle",
    )


def retrieve_auto_citation_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return the canonical citation/provenance bundle for the FTS-first auto path."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_auto_citation_bundle",
    )


def retrieve_auto_source_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return the canonical source bundle for the FTS-first auto path."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_auto_source_bundle",
    )


def retrieve_auto_doc_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return the canonical doc-focused bundle for the FTS-first auto path."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_auto_doc_bundle",
    )


def retrieve_auto_excerpt_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return the canonical excerpt-focused bundle for the FTS-first auto path."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_auto_excerpt_bundle",
    )


def retrieve_auto_payload(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return the canonical downstream payload for FTS-first retrieval.

    Engine callers that need deterministic provenance for drafting or export
    should use this helper instead of reassembling the result object by hand.
    """

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_auto_payload",
    )

__all__ = [
    "RetrievalService",
    "RetrievalQuery",
    "RetrievalConstraints",
    "RetrievalDocHit",
    "RetrievalHit",
    "RetrievalResult",
    "build_retrieval_query",
    "retrieve_fts",
    "retrieve_fts_payload",
    "retrieve_fts_context_bundle",
    "retrieve_fts_source_bundle",
    "retrieve_fts_doc_bundle",
    "retrieve_fts_excerpt_bundle",
    "retrieve_fts_excerpt",
    "fetch_fts_excerpt",
    "retrieve_auto",
    "retrieve_auto_context_bundle",
    "retrieve_auto_citation_bundle",
    "retrieve_auto_source_bundle",
    "retrieve_auto_doc_bundle",
    "retrieve_auto_excerpt_bundle",
    "retrieve_auto_payload",
]
