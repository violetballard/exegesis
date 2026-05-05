"""Engine retrieval strategies.

The retrieval lane keeps this package as the narrow public surface for the
engine's retrieval orchestration code.
"""

from collections.abc import Iterable, Mapping, Set

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


def _normalize_constraint_values(
    value: object,
    *,
    field_name: str,
    allow_unordered: bool = True,
) -> tuple[str, ...]:
    """Return a deterministic tuple for loose retrieval constraint payloads."""

    if value is None:
        return ()
    if isinstance(value, str):
        normalized = value.strip()
        return (normalized,) if normalized else ()
    if isinstance(value, (bytes, bytearray)):
        raise TypeError(f"{field_name} must be an iterable of text values")
    if isinstance(value, Mapping):
        raise TypeError(f"{field_name} must be an iterable of values, not a mapping")
    if not allow_unordered and isinstance(value, Set):
        raise TypeError(f"{field_name} must be an ordered iterable of values")
    if not isinstance(value, Iterable):
        raise TypeError(f"{field_name} must be an iterable of values or None")
    normalized_values: list[str] = []
    for item in value:
        if item is None:
            continue
        normalized = str(item).strip()
        if normalized:
            normalized_values.append(normalized)
    return tuple(normalized_values)


def _normalize_optional_int(value: object, *, default: int) -> int:
    if value is None:
        return default
    return int(value)


def _normalize_optional_bool(value: object, *, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off", ""}:
            return False
        raise ValueError(f"unsupported boolean constraint value: {value}")
    if isinstance(value, (int, float)):
        return bool(value)
    raise TypeError("boolean retrieval constraints must be bool, number, text, or None")


def build_retrieval_query(
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: object | None = None,
    confidentiality_profile: str = "confidential",
) -> RetrievalQuery:
    """Return the canonical FTS-first retrieval query object.

    The helper normalizes the loose dict-shaped constraint payload used by the
    engine and public retrieval facades into the stable dataclass contract that
    the service layer consumes. Constraint payloads are mapping-shaped or
    RetrievalConstraints objects, and iterable doc_types/date_range values are
    normalized deterministically from those inputs.
    """

    from src.qual.retrieval.service import RetrievalConstraints, RetrievalQuery

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

    doc_types = _normalize_constraint_values(payload.get("doc_types"), field_name="doc_types")
    date_range = payload.get("date_range")
    if isinstance(date_range, str):
        date_range = (date_range,)
    if date_range is not None:
        date_range = _normalize_constraint_values(
            date_range,
            field_name="date_range",
            allow_unordered=False,
        )
    return RetrievalQuery(
        query_text=query_text,
        scope=scope,
        intent=intent,  # type: ignore[arg-type]
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
        confidentiality_profile=confidentiality_profile,  # type: ignore[arg-type]
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


def retrieve_fts_context_bundle(*args, **kwargs):
    from src.qual.retrieval import retrieve_fts_context_bundle as _retrieve_fts_context_bundle

    return _retrieve_fts_context_bundle(*args, **kwargs)


def retrieve_fts_citation_bundle(*args, **kwargs):
    from src.qual.retrieval import retrieve_fts_citation_bundle as _retrieve_fts_citation_bundle

    return _retrieve_fts_citation_bundle(*args, **kwargs)


def retrieve_fts_source_bundle(*args, **kwargs):
    from src.qual.retrieval import retrieve_fts_source_bundle as _retrieve_fts_source_bundle

    return _retrieve_fts_source_bundle(*args, **kwargs)


def retrieve_fts_provenance_bundle(*args, **kwargs):
    from src.qual.retrieval import retrieve_fts_provenance_bundle as _retrieve_fts_provenance_bundle

    return _retrieve_fts_provenance_bundle(*args, **kwargs)


def retrieve_fts_doc_bundle(*args, **kwargs):
    from src.qual.retrieval import retrieve_fts_doc_bundle as _retrieve_fts_doc_bundle

    return _retrieve_fts_doc_bundle(*args, **kwargs)


def retrieve_fts_excerpt_bundle(*args, **kwargs):
    from src.qual.retrieval import retrieve_fts_excerpt_bundle as _retrieve_fts_excerpt_bundle

    return _retrieve_fts_excerpt_bundle(*args, **kwargs)


def retrieve_fts_excerpt(*args, **kwargs):
    from src.qual.retrieval import retrieve_fts_excerpt as _retrieve_fts_excerpt

    return _retrieve_fts_excerpt(*args, **kwargs)


def fetch_fts_excerpt(*args, **kwargs):
    from src.qual.retrieval import fetch_fts_excerpt as _fetch_fts_excerpt

    return _fetch_fts_excerpt(*args, **kwargs)


def fetch_excerpt(*args, **kwargs):
    from src.qual.retrieval import fetch_excerpt as _fetch_excerpt

    return _fetch_excerpt(*args, **kwargs)


def retrieve_fts_payload(*args, **kwargs):
    from src.qual.retrieval import retrieve_fts_payload as _retrieve_fts_payload

    return _retrieve_fts_payload(*args, **kwargs)


def retrieve_fts(*args, **kwargs):
    from src.qual.retrieval import retrieve_fts as _retrieve_fts

    return _retrieve_fts(*args, **kwargs)


def retrieve_auto(*args, **kwargs):
    from src.qual.retrieval import retrieve_auto as _retrieve_auto

    return _retrieve_auto(*args, **kwargs)


def retrieve_auto_context_bundle(*args, **kwargs):
    from src.qual.retrieval import retrieve_auto_context_bundle as _retrieve_auto_context_bundle

    return _retrieve_auto_context_bundle(*args, **kwargs)


def retrieve_auto_citation_bundle(*args, **kwargs):
    from src.qual.retrieval import retrieve_auto_citation_bundle as _retrieve_auto_citation_bundle

    return _retrieve_auto_citation_bundle(*args, **kwargs)


def retrieve_auto_source_bundle(*args, **kwargs):
    from src.qual.retrieval import retrieve_auto_source_bundle as _retrieve_auto_source_bundle

    return _retrieve_auto_source_bundle(*args, **kwargs)


def retrieve_auto_provenance_bundle(*args, **kwargs):
    from src.qual.retrieval import retrieve_auto_provenance_bundle as _retrieve_auto_provenance_bundle

    return _retrieve_auto_provenance_bundle(*args, **kwargs)


def retrieve_auto_doc_bundle(*args, **kwargs):
    from src.qual.retrieval import retrieve_auto_doc_bundle as _retrieve_auto_doc_bundle

    return _retrieve_auto_doc_bundle(*args, **kwargs)


def retrieve_auto_excerpt_bundle(*args, **kwargs):
    from src.qual.retrieval import retrieve_auto_excerpt_bundle as _retrieve_auto_excerpt_bundle

    return _retrieve_auto_excerpt_bundle(*args, **kwargs)


def retrieve_auto_payload(*args, **kwargs):
    from src.qual.retrieval import retrieve_auto_payload as _retrieve_auto_payload

    return _retrieve_auto_payload(*args, **kwargs)


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
    "retrieve_auto",
    "retrieve_auto_context_bundle",
    "retrieve_auto_citation_bundle",
    "retrieve_auto_source_bundle",
    "retrieve_auto_provenance_bundle",
    "retrieve_auto_doc_bundle",
    "retrieve_auto_excerpt_bundle",
    "retrieve_auto_payload",
]
