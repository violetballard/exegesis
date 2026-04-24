from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import TypeAlias

from src.qual.retrieval.service import (
    RetrievalConstraints,
    RetrievalDocHit,
    RetrievalHit,
    RetrievalQuery,
    RetrievalResult,
    RetrievalService,
)

RetrievalConstraintInput: TypeAlias = Mapping[str, object] | RetrievalConstraints | None


def _normalize_constraint_values(value: object, *, field_name: str) -> tuple[str, ...]:
    """Return a deterministic tuple for loose retrieval constraint payloads."""

    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (bytes, bytearray)):
        raise TypeError(f"{field_name} must be an iterable of text values")
    if isinstance(value, Mapping):
        raise TypeError(f"{field_name} must be an iterable of values, not a mapping")
    if not isinstance(value, Iterable):
        raise TypeError(f"{field_name} must be an iterable of values or None")

    items = [str(item) for item in value if item is not None]
    if isinstance(value, (set, frozenset)):
        return tuple(sorted(items))
    return tuple(items)


def _normalize_optional_int(value: object, *, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        raise TypeError("integer value must not be a boolean")
    return int(value)


def _normalize_optional_bool(value: object, *, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        if value in {0, 1}:
            return bool(value)
        raise ValueError(f"unsupported boolean value: {value}")
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if not normalized:
            return default
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
        raise ValueError(f"unsupported boolean value: {value}")
    raise ValueError(f"unsupported boolean value: {value}")


def _normalize_required_text(value: object, *, field_name: str, casefold: bool = False) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{field_name} must be a non-empty string")
    if casefold:
        return text.casefold()
    return text


def _build_retrieval_query(
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
    confidentiality_profile: str = "confidential",
) -> RetrievalQuery:
    return build_retrieval_query(
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
    constraints: RetrievalConstraintInput = None,
    confidentiality_profile: str = "confidential",
) -> RetrievalQuery:
    """Return the canonical retrieval query used by both facades.

    Constraint payloads are accepted as mapping-shaped payloads or
    RetrievalConstraints objects and normalized into the canonical query
    dataclass. Iterable doc_types/date_range values are normalized
    deterministically from those inputs.
    """

    if constraints is None:
        payload: dict[str, object] = {}
    elif isinstance(constraints, RetrievalConstraints):
        payload = {
            "max_results": constraints.max_results,
            "doc_types": constraints.doc_types,
            "date_range": constraints.date_range,
            "require_citations": constraints.require_citations,
            "section_hint": constraints.section_hint,
            "prefer_exact_matches": constraints.prefer_exact_matches,
        }
    elif isinstance(constraints, Mapping):
        payload = dict(constraints)
    else:
        raise TypeError("constraints must be a mapping or RetrievalConstraints")

    normalized_query_text = _normalize_required_text(query_text, field_name="query_text")
    normalized_intent = _normalize_required_text(intent, field_name="intent", casefold=True)
    normalized_confidentiality_profile = _normalize_required_text(
        confidentiality_profile,
        field_name="confidentiality_profile",
        casefold=True,
    )
    doc_types = _normalize_constraint_values(payload.get("doc_types"), field_name="doc_types")
    date_range = payload.get("date_range")
    if isinstance(date_range, str):
        date_range = (date_range,)
    if date_range is not None:
        date_range = _normalize_constraint_values(date_range, field_name="date_range")
    return RetrievalQuery(
        query_text=normalized_query_text,
        scope=scope,
        intent=normalized_intent,  # type: ignore[arg-type]
        constraints=RetrievalConstraints(
            max_results=_normalize_optional_int(payload.get("max_results"), default=10),
            doc_types=doc_types,
            date_range=date_range,  # type: ignore[arg-type]
            require_citations=_normalize_optional_bool(
                payload.get("require_citations"),
                default=False,
            ),
            section_hint=payload.get("section_hint"),  # type: ignore[arg-type]
            prefer_exact_matches=_normalize_optional_bool(
                payload.get("prefer_exact_matches"),
                default=False,
            ),
        ),
        confidentiality_profile=normalized_confidentiality_profile,  # type: ignore[arg-type]
    )


def _call_fts_retrieval(
    service: RetrievalService,
    *,
    method_name: str,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
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
    constraints: RetrievalConstraintInput = None,
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
    constraints: RetrievalConstraintInput = None,
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
    constraints: RetrievalConstraintInput = None,
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
    constraints: RetrievalConstraintInput = None,
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
    constraints: RetrievalConstraintInput = None,
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


def retrieve_fts_provenance_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return the canonical provenance bundle for a single FTS retrieval."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_fts_provenance_bundle",
    )


def retrieve_fts_doc_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
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
    constraints: RetrievalConstraintInput = None,
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
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return an excerpt payload using the canonical FTS-only lookup path."""

    return service.retrieve_fts_excerpt(
        excerpt_id,
        confidentiality_profile=confidentiality_profile,
    )


def fetch_fts_excerpt(
    service: RetrievalService,
    *,
    excerpt_id: str,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Backward-compatible alias for the canonical FTS-only excerpt lookup path."""

    return service.fetch_fts_excerpt(
        excerpt_id,
        confidentiality_profile=confidentiality_profile,
    )


def fetch_excerpt(
    service: RetrievalService,
    *,
    excerpt_id: str,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return an excerpt payload via the canonical FTS-only lookup path.

    This keeps the generic excerpt lookup surface importable while the MVP lane
    remains FTS-first underneath.
    """

    return service.fetch_excerpt(
        excerpt_id,
        confidentiality_profile=confidentiality_profile,
    )


def retrieve_auto_excerpt(
    service: RetrievalService,
    *,
    excerpt_id: str,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return an excerpt payload using the canonical FTS-first auto lookup path."""

    return service.retrieve_auto_excerpt(
        excerpt_id,
        confidentiality_profile=confidentiality_profile,
    )


def retrieve_auto(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
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
    constraints: RetrievalConstraintInput = None,
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
    constraints: RetrievalConstraintInput = None,
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
    constraints: RetrievalConstraintInput = None,
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


def retrieve_auto_provenance_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return the canonical provenance bundle for the FTS-first auto path."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_auto_provenance_bundle",
    )


def retrieve_auto_doc_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
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
    constraints: RetrievalConstraintInput = None,
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
    constraints: RetrievalConstraintInput = None,
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
    "retrieve_fts_provenance_bundle",
    "retrieve_fts_doc_bundle",
    "retrieve_fts_excerpt_bundle",
    "retrieve_fts_excerpt",
    "fetch_excerpt",
    "fetch_fts_excerpt",
    "retrieve_fts_citation_bundle",
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
