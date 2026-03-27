from __future__ import annotations

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
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
) -> RetrievalQuery:
    payload = constraints if constraints is not None else {}
    doc_types = payload.get("doc_types", ())
    if isinstance(doc_types, str):
        doc_types = (doc_types,)
    date_range = payload.get("date_range")
    if isinstance(date_range, str):
        date_range = (date_range,)
    if date_range is not None:
        date_range = tuple(str(value) for value in date_range)
    return RetrievalQuery(
        query_text=query_text,
        scope=scope,
        intent=intent,  # type: ignore[arg-type]
        constraints=RetrievalConstraints(
            max_results=int(payload.get("max_results", 10)),
            doc_types=tuple(str(value) for value in doc_types),
            date_range=date_range,  # type: ignore[arg-type]
            require_citations=bool(payload.get("require_citations", False)),
            section_hint=payload.get("section_hint"),  # type: ignore[arg-type]
            prefer_exact_matches=bool(payload.get("prefer_exact_matches", False)),
        ),
        confidentiality_profile=confidentiality_profile,  # type: ignore[arg-type]
    )


def retrieve_fts(
    service: RetrievalService,
    *,
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
    return service.retrieve_fts(query)


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

    query = _build_retrieval_query(
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
    )
    return service.retrieve_fts_payload(query)


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

    query = _build_retrieval_query(
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
    )
    return service.retrieve_fts_context_bundle(query)


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

    query = _build_retrieval_query(
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
    )
    return service.retrieve_fts_source_bundle(query)


def retrieve_auto(
    service: RetrievalService,
    *,
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
    return service.retrieve_auto(query)


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

    query = _build_retrieval_query(
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
    )
    return service.retrieve_auto_context_bundle(query)


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

    query = _build_retrieval_query(
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
    )
    return service.retrieve_auto_source_bundle(query)


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

    query = _build_retrieval_query(
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
    )
    return service.retrieve_auto_payload(query)

__all__ = [
    "RetrievalService",
    "RetrievalQuery",
    "RetrievalConstraints",
    "RetrievalDocHit",
    "RetrievalHit",
    "RetrievalResult",
    "retrieve_fts",
    "retrieve_fts_payload",
    "retrieve_fts_context_bundle",
    "retrieve_fts_source_bundle",
    "retrieve_auto",
    "retrieve_auto_context_bundle",
    "retrieve_auto_source_bundle",
    "retrieve_auto_payload",
]
