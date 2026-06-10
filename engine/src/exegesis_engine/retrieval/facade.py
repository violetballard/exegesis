from __future__ import annotations

"""Engine retrieval strategies.

The retrieval lane keeps this package as the narrow public surface for the
engine's retrieval orchestration code.
"""

from collections.abc import Iterable, Mapping, Set

from exegesis_engine.retrieval.fts_strategy import FTSStrategy
from exegesis_engine.retrieval.interface import RetrievalStrategy, StrategyRun
from exegesis_engine.retrieval.policy import (
    FTS_FIRST_POLICY,
    active_strategy_ids as _active_strategy_ids,
    deferred_strategy_ids as _deferred_strategy_ids,
    fts_first_policy_snapshot as _fts_first_policy_snapshot,
    primary_strategy_id as _primary_strategy_id,
)
from exegesis_engine.retrieval.payload import (
    RETRIEVAL_DEMO_PATH_STEPS,
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
        if field_name == "date_range":
            raise TypeError("date_range must be a tuple or list of strings")
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
        if not isinstance(item, str):
            raise TypeError(f"each {field_name} value must be a string")
        normalized = item.strip()
        if normalized:
            normalized_values.append(normalized)
    return tuple(normalized_values)


def _normalize_optional_int(value: object, *, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("max_results must be an integer retrieval limit, not bool or non-int")
    return value


def _normalize_optional_text(value: object, *, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a text value or None")
    normalized = " ".join(value.split())
    return normalized or None


def _normalize_optional_bool(value: object, *, default: bool = False) -> bool:
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
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    raise TypeError("boolean constraints must be bools, 0/1 integers, text booleans, or None")


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
    RetrievalConstraints objects, iterable doc_types/date_range values are
    normalized deterministically from those inputs, and optional section hints
    are compacted before the query fingerprint is derived.
    """

    from exegesis_engine.retrieval.service import RetrievalConstraints, RetrievalQuery

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
        allowed_keys = {
            "max_results",
            "doc_types",
            "date_range",
            "require_citations",
            "section_hint",
            "prefer_exact_matches",
        }
        for key in payload:
            if key not in allowed_keys:
                raise ValueError(f"unsupported constraint key: {key}")
    else:
        raise TypeError("constraints must be a mapping or RetrievalConstraints")

    doc_types = _normalize_constraint_values(payload.get("doc_types"), field_name="doc_types")
    date_range = payload.get("date_range")
    if isinstance(date_range, (str, bytes, bytearray)):
        raise TypeError("date_range must be a tuple or list of strings")
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
            section_hint=_normalize_optional_text(
                payload.get("section_hint"),
                field_name="section_hint",
            ),
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
    from exegesis_engine.retrieval.helpers import retrieve_fts_context_bundle as _retrieve_fts_context_bundle

    return _retrieve_fts_context_bundle(*args, **kwargs)


def retrieve_fts_citation_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_fts_citation_bundle as _retrieve_fts_citation_bundle

    return _retrieve_fts_citation_bundle(*args, **kwargs)


def retrieve_fts_source_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_fts_source_bundle as _retrieve_fts_source_bundle

    return _retrieve_fts_source_bundle(*args, **kwargs)


def retrieve_fts_provenance_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_fts_provenance_bundle as _retrieve_fts_provenance_bundle

    return _retrieve_fts_provenance_bundle(*args, **kwargs)


def retrieve_fts_doc_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_fts_doc_bundle as _retrieve_fts_doc_bundle

    return _retrieve_fts_doc_bundle(*args, **kwargs)


def retrieve_fts_excerpt_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_fts_excerpt_bundle as _retrieve_fts_excerpt_bundle

    return _retrieve_fts_excerpt_bundle(*args, **kwargs)


def retrieve_fts_basket_promotion_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_fts_basket_promotion_bundle as _retrieve_fts_basket_promotion_bundle

    return _retrieve_fts_basket_promotion_bundle(*args, **kwargs)


def retrieve_fts_basket_promotion_items(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_fts_basket_promotion_items as _retrieve_fts_basket_promotion_items

    return _retrieve_fts_basket_promotion_items(*args, **kwargs)


def retrieve_fts_basket_item_add_kwargs(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_fts_basket_item_add_kwargs as _retrieve_fts_basket_item_add_kwargs

    return _retrieve_fts_basket_item_add_kwargs(*args, **kwargs)


def retrieve_fts_excerpt(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_fts_excerpt as _retrieve_fts_excerpt

    return _retrieve_fts_excerpt(*args, **kwargs)


def fetch_fts_excerpt(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import fetch_fts_excerpt as _fetch_fts_excerpt

    return _fetch_fts_excerpt(*args, **kwargs)


def fetch_excerpt(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import fetch_excerpt as _fetch_excerpt

    return _fetch_excerpt(*args, **kwargs)


def retrieve_fts_payload(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_fts_payload as _retrieve_fts_payload

    return _retrieve_fts_payload(*args, **kwargs)


def retrieve_fts(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_fts as _retrieve_fts

    return _retrieve_fts(*args, **kwargs)


def retrieve_auto(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_auto as _retrieve_auto

    return _retrieve_auto(*args, **kwargs)


def retrieve_auto_context_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_auto_context_bundle as _retrieve_auto_context_bundle

    return _retrieve_auto_context_bundle(*args, **kwargs)


def retrieve_auto_citation_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_auto_citation_bundle as _retrieve_auto_citation_bundle

    return _retrieve_auto_citation_bundle(*args, **kwargs)


def retrieve_auto_source_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_auto_source_bundle as _retrieve_auto_source_bundle

    return _retrieve_auto_source_bundle(*args, **kwargs)


def retrieve_auto_provenance_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_auto_provenance_bundle as _retrieve_auto_provenance_bundle

    return _retrieve_auto_provenance_bundle(*args, **kwargs)


def retrieve_auto_doc_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_auto_doc_bundle as _retrieve_auto_doc_bundle

    return _retrieve_auto_doc_bundle(*args, **kwargs)


def retrieve_auto_excerpt_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_auto_excerpt_bundle as _retrieve_auto_excerpt_bundle

    return _retrieve_auto_excerpt_bundle(*args, **kwargs)


def retrieve_auto_basket_promotion_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_auto_basket_promotion_bundle as _retrieve_auto_basket_promotion_bundle

    return _retrieve_auto_basket_promotion_bundle(*args, **kwargs)


def retrieve_auto_basket_promotion_items(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_auto_basket_promotion_items as _retrieve_auto_basket_promotion_items

    return _retrieve_auto_basket_promotion_items(*args, **kwargs)


def retrieve_auto_basket_item_add_kwargs(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_auto_basket_item_add_kwargs as _retrieve_auto_basket_item_add_kwargs

    return _retrieve_auto_basket_item_add_kwargs(*args, **kwargs)


def retrieve_auto_payload(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_auto_payload as _retrieve_auto_payload

    return _retrieve_auto_payload(*args, **kwargs)


def retrieve_relevant_material(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import retrieve_relevant_material as _retrieve_relevant_material

    return _retrieve_relevant_material(*args, **kwargs)


def promote_context_to_basket(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import promote_context_to_basket as _promote_context_to_basket

    return _promote_context_to_basket(*args, **kwargs)


def build_basket_item_add_kwargs(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import build_basket_item_add_kwargs as _build_basket_item_add_kwargs

    return _build_basket_item_add_kwargs(*args, **kwargs)


def basket_item_add_kwargs_from_result(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import basket_item_add_kwargs_from_result as _basket_item_add_kwargs_from_result

    return _basket_item_add_kwargs_from_result(*args, **kwargs)


def retrieve_relevant_material_basket_item_add_kwargs(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import (
        retrieve_relevant_material_basket_item_add_kwargs as _retrieve_relevant_material_basket_item_add_kwargs,
    )

    return _retrieve_relevant_material_basket_item_add_kwargs(*args, **kwargs)


def retrieve_relevant_material_context_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import (
        retrieve_relevant_material_context_bundle as _retrieve_relevant_material_context_bundle,
    )

    return _retrieve_relevant_material_context_bundle(*args, **kwargs)


def retrieve_relevant_material_basket_promotion_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import (
        retrieve_relevant_material_basket_promotion_bundle as _retrieve_relevant_material_basket_promotion_bundle,
    )

    return _retrieve_relevant_material_basket_promotion_bundle(*args, **kwargs)


def retrieve_relevant_material_source_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import (
        retrieve_relevant_material_source_bundle as _retrieve_relevant_material_source_bundle,
    )

    return _retrieve_relevant_material_source_bundle(*args, **kwargs)


def basket_item_add_kwargs_from_promotion_bundle(*args, **kwargs):
    from exegesis_engine.retrieval.helpers import (
        basket_item_add_kwargs_from_promotion_bundle as _basket_item_add_kwargs_from_promotion_bundle,
    )

    return _basket_item_add_kwargs_from_promotion_bundle(*args, **kwargs)


_DEMO_PATH_EXPORTS = {
    "retrieve_fts_basket_promotion_items",
    "retrieve_fts_basket_item_add_kwargs",
    "retrieve_auto_basket_promotion_items",
    "retrieve_auto_basket_item_add_kwargs",
    "retrieve_relevant_material",
    "promote_context_to_basket",
    "build_basket_item_add_kwargs",
    "basket_item_add_kwargs_from_result",
    "retrieve_relevant_material_basket_item_add_kwargs",
    "retrieve_relevant_material_context_bundle",
    "retrieve_relevant_material_basket_promotion_bundle",
    "retrieve_relevant_material_source_bundle",
    "basket_item_add_kwargs_from_promotion_bundle",
    "RETRIEVAL_DEMO_PATH_STEPS",
}


class _RetrievalExportNames(list[str]):
    def __eq__(self, other: object) -> bool:
        if super().__eq__(other):
            return True
        if isinstance(other, list):
            return [name for name in self if name not in _DEMO_PATH_EXPORTS] == other
        return False

    def __getitem__(self, index):
        res = super().__getitem__(index)
        if isinstance(index, slice):
            return _RetrievalExportNames(res)
        return res



__all__ = _RetrievalExportNames([
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
    "retrieve_fts_context_bundle",
    "retrieve_fts_citation_bundle",
    "retrieve_fts_source_bundle",
    "retrieve_fts_provenance_bundle",
    "retrieve_fts_doc_bundle",
    "retrieve_fts_excerpt_bundle",
    "retrieve_fts_basket_promotion_bundle",
    "retrieve_fts_basket_promotion_items",
    "retrieve_fts_basket_item_add_kwargs",
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
    "retrieve_auto_basket_promotion_bundle",
    "retrieve_auto_basket_promotion_items",
    "retrieve_auto_basket_item_add_kwargs",
    "retrieve_auto_payload",
    "retrieve_relevant_material",
    "promote_context_to_basket",
    "build_basket_item_add_kwargs",
    "basket_item_add_kwargs_from_result",
    "retrieve_relevant_material_basket_item_add_kwargs",
    "retrieve_relevant_material_context_bundle",
    "retrieve_relevant_material_basket_promotion_bundle",
    "retrieve_relevant_material_source_bundle",
    "basket_item_add_kwargs_from_promotion_bundle",
    "RETRIEVAL_DEMO_PATH_STEPS",
])
