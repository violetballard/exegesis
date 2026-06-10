from __future__ import annotations

try:
    from typing import TypeAlias
except ImportError:  # Python 3.9 compatibility for system test runners.
    from typing_extensions import TypeAlias  # type: ignore[assignment]
from typing import Union, cast


from exegesis_engine.retrieval.facade import build_retrieval_query as engine_build_retrieval_query
from exegesis_engine.retrieval.service import (
    RETRIEVAL_DEMO_PATH_STEPS,
    RetrievalConstraints,
    RetrievalDocHit,
    RetrievalHit,
    RetrievalQuery,
    RetrievalResult,
    RetrievalService,
    _basket_item_add_kwargs_from_promotion_item,
    _basket_item_add_kwargs_from_promotion_items,
)

RetrievalConstraintInput: TypeAlias = Union[dict[str, object], RetrievalConstraints, None]


def _build_retrieval_query(
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
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
    constraints: RetrievalConstraintInput = None,
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


def retrieve_fts_basket_promotion_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return FTS evidence items ready for context-basket promotion."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_fts_basket_promotion_bundle",
    )


def retrieve_fts_basket_promotion_items(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
    confidentiality_profile: str = "confidential",
) -> list[dict[str, object]]:
    """Return canonical FTS promotion items ready for context-basket insertion."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_fts_basket_promotion_items",
    )


def retrieve_fts_basket_item_add_kwargs(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
    confidentiality_profile: str = "confidential",
) -> list[dict[str, object]]:
    """Return validated add_basket_item kwargs for a single FTS retrieval."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_fts_basket_item_add_kwargs",
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


def fetch_excerpt(
    service: RetrievalService,
    *,
    excerpt_id: str,
) -> dict[str, object]:
    """Return an excerpt payload using the canonical FTS-only lookup path."""

    return service.fetch_excerpt(excerpt_id)


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


def retrieve_auto_basket_promotion_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Return FTS evidence items ready for context-basket promotion."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_auto_basket_promotion_bundle",
    )


def retrieve_auto_basket_promotion_items(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
    confidentiality_profile: str = "confidential",
) -> list[dict[str, object]]:
    """Return canonical FTS promotion items for the FTS-first auto path."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_auto_basket_promotion_items",
    )


def retrieve_auto_basket_item_add_kwargs(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
    confidentiality_profile: str = "confidential",
) -> list[dict[str, object]]:
    """Return validated add_basket_item kwargs for the FTS-first auto path."""

    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_auto_basket_item_add_kwargs",
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


def retrieve_relevant_material(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
    confidentiality_profile: str = "confidential",
) -> RetrievalResult:
    """Execute the FTS-first retrieval demo-path step (step 1 of 2).

    Returns a result with deterministic FTS provenance ready for basket
    promotion via promote_context_to_basket.
    """
    return _call_fts_retrieval(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
        method_name="retrieve_fts",
    )


def promote_context_to_basket(result: RetrievalResult) -> list[dict[str, object]]:
    """Extract promotion-ready items from an FTS retrieval result (step 2 of 2).

    Only items with complete sparse FTS provenance are included; items that
    fail provenance checks are excluded with rejection reasons tracked on the
    result.
    """
    return result.basket_promotion_items()


def build_basket_item_add_kwargs(
    promotion_item: dict[str, object],
) -> dict[str, object]:
    """Convert one basket promotion item to keyword arguments for add_basket_item.

    Bridges the output of promote_context_to_basket to the call signature of
    ExegesisAppService.add_basket_item so engine-run callers do not need to
    know the internal field names.

    The returned dict has exactly the keys that add_basket_item accepts:
    item_id, item_type, label, and payload (the full promotion item, safe for
    downstream provenance tracking).
    """
    return _basket_item_add_kwargs_from_promotion_item(promotion_item)


def basket_item_add_kwargs_from_result(result: RetrievalResult) -> list[dict[str, object]]:
    """Return add_basket_item kwargs for every promotion-ready item in a retrieval result.

    Combines promote_context_to_basket and build_basket_item_add_kwargs so
    engine-run callers get a flat list of ready-to-use kwargs without an
    explicit loop.  Items that fail provenance checks are silently excluded,
    matching the behaviour of promote_context_to_basket.
    """
    return [build_basket_item_add_kwargs(item) for item in promote_context_to_basket(result)]


def retrieve_relevant_material_basket_item_add_kwargs(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
    confidentiality_profile: str = "confidential",
) -> list[dict[str, object]]:
    """Run the named FTS demo path and return validated add_basket_item kwargs."""

    result = retrieve_relevant_material(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
    )
    return basket_item_add_kwargs_from_result(result)


def retrieve_relevant_material_context_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Run the named FTS demo path and return its basket-ready context bundle."""

    return retrieve_relevant_material(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
    ).retrieval_context_bundle()


def retrieve_relevant_material_basket_promotion_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Run the named FTS demo path and return its context-basket promotion bundle."""

    return retrieve_relevant_material(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
    ).retrieval_basket_promotion_bundle()


def retrieve_relevant_material_source_bundle(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: RetrievalConstraintInput = None,
    confidentiality_profile: str = "confidential",
) -> dict[str, object]:
    """Run the named FTS demo path and return its deterministic source bundle."""

    return retrieve_relevant_material(
        service,
        query_text=query_text,
        scope=scope,
        intent=intent,
        constraints=constraints,
        confidentiality_profile=confidentiality_profile,
    ).source_bundle()


def _required_bundle_text(
    promotion_bundle: dict[str, object],
    field_name: str,
) -> str:
    value = promotion_bundle.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"promotion_bundle must carry a non-empty {field_name}")
    return value


def _bundle_item_values(
    promotion_items: list[dict[str, object]],
    field_name: str,
) -> list[object]:
    return [item.get(field_name) for item in promotion_items]


def _validate_demo_path_steps(value: object, *, surface: str) -> None:
    if value != list(RETRIEVAL_DEMO_PATH_STEPS):
        raise ValueError(f"promotion_bundle {surface} canonical_demo_path_steps is stale")


def _validate_promotion_bundle_snapshot(
    promotion_bundle: dict[str, object],
    promotion_items: list[dict[str, object]],
) -> None:
    if _required_bundle_text(promotion_bundle, "promotion_target") != "context_basket":
        raise ValueError("promotion_bundle must target context_basket")
    if _required_bundle_text(promotion_bundle, "basket_promotion_source") not in {
        "fts_retrieval_result",
        "fts_excerpt_lookup",
    }:
        raise ValueError("promotion_bundle must carry FTS basket_promotion_source")
    if _required_bundle_text(promotion_bundle, "retrieval_backend") != "sqlite_fts":
        raise ValueError("promotion_bundle must carry sqlite_fts retrieval_backend")
    if _required_bundle_text(promotion_bundle, "retrieval_mode") != "fts_first":
        raise ValueError("promotion_bundle must carry fts_first retrieval_mode")
    _validate_demo_path_steps(
        promotion_bundle.get("canonical_demo_path_steps"),
        surface="top-level",
    )
    promotion_count = promotion_bundle.get("basket_promotion_count")
    if promotion_count != len(promotion_items):
        raise ValueError("promotion_bundle basket_promotion_count is stale")
    promotion_ready = promotion_bundle.get("basket_promotion_ready")
    if promotion_ready is not (len(promotion_items) > 0):
        raise ValueError("promotion_bundle basket_promotion_ready is stale")
    for bundle_field, item_field in (
        ("basket_item_ids", "basket_item_id"),
        ("basket_item_fingerprints", "basket_item_fingerprint"),
        ("basket_promotion_item_fingerprints", "promotion_item_fingerprint"),
    ):
        bundle_values = promotion_bundle.get(bundle_field)
        if bundle_values is not None and bundle_values != _bundle_item_values(promotion_items, item_field):
            raise ValueError(f"promotion_bundle {bundle_field} is stale")
    for item in promotion_items:
        _validate_demo_path_steps(
            item.get("canonical_demo_path_steps"),
            surface="item",
        )


def basket_item_add_kwargs_from_promotion_bundle(
    promotion_bundle: dict[str, object],
) -> list[dict[str, object]]:
    """Return add_basket_item kwargs from a structured FTS promotion bundle.

    This lets engine-run callers continue from retrieve_fts_basket_promotion_bundle
    without holding the RetrievalResult object.  The helper derives kwargs from
    basket_promotion_items instead of trusting any cached kwargs in the bundle,
    so each item is validated against the sparse FTS provenance contract.
    """
    promotion_items = promotion_bundle.get("basket_promotion_items")
    if not isinstance(promotion_items, list):
        raise ValueError("promotion_bundle must carry basket_promotion_items")
    if not all(isinstance(item, dict) for item in promotion_items):
        raise ValueError("promotion_bundle basket_promotion_items must be dictionaries")
    typed_promotion_items = cast(list[dict[str, object]], promotion_items)
    _validate_promotion_bundle_snapshot(promotion_bundle, typed_promotion_items)
    add_kwargs = _basket_item_add_kwargs_from_promotion_items(typed_promotion_items)
    cached_add_kwargs = promotion_bundle.get("basket_item_add_kwargs")
    if cached_add_kwargs is not None and cached_add_kwargs != add_kwargs:
        raise ValueError("promotion_bundle basket_item_add_kwargs is stale")
    return add_kwargs


__all__ = [
    "RETRIEVAL_DEMO_PATH_STEPS",
    "RetrievalConstraints",
    "RetrievalDocHit",
    "RetrievalHit",
    "RetrievalQuery",
    "RetrievalResult",
    "RetrievalService",
    "build_retrieval_query",
    "retrieve_fts",
    "retrieve_fts_payload",
    "retrieve_fts_context_bundle",
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
    "retrieve_fts_citation_bundle",
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
]
