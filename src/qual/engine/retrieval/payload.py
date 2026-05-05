from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Protocol


class RetrievalDownstreamPayloadSource(Protocol):
    def to_downstream_payload(self) -> dict[str, object]:
        """Return the stable retrieval payload consumed by downstream engine flows."""


class RetrievalCitationBundleSource(Protocol):
    def citation_bundle(self) -> dict[str, object]:
        """Return the deterministic citation snapshot consumed by downstream engine flows."""


class RetrievalSourceBundleSource(Protocol):
    def source_bundle(self) -> dict[str, object]:
        """Return the deterministic doc and excerpt snapshot consumed by engine flows."""


class RetrievalDocBundleSource(Protocol):
    def retrieval_doc_bundle(self) -> dict[str, object]:
        """Return the deterministic doc-focused snapshot consumed by engine flows."""


class RetrievalExcerptBundleSource(Protocol):
    def retrieval_excerpt_bundle(self) -> dict[str, object]:
        """Return the deterministic excerpt-focused snapshot consumed by engine flows."""


class RetrievalContextBundleSource(Protocol):
    def retrieval_context_bundle(self) -> dict[str, object]:
        """Return the deterministic retrieval context consumed by engine flows."""


class RetrievalProvenanceBundleSource(Protocol):
    def retrieval_provenance_bundle(self) -> dict[str, object]:
        """Return the deterministic retrieval provenance snapshot consumed by engine flows."""


def _normalize_list_like(value: object) -> list[object]:
    if isinstance(value, list):
        return copy.deepcopy(value)
    if isinstance(value, tuple):
        return list(value)
    if value is None:
        return []
    return [value]


def _normalize_optional_list_like(value: object) -> list[object] | None:
    if value is None:
        return None
    return _normalize_list_like(value)


def _normalize_optional_text(value: object) -> str | None:
    if isinstance(value, str):
        text = value.strip()
        if text:
            return text
    return None


def _basket_item_ids_from_items(items: list[object]) -> list[str]:
    item_ids: list[str] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        item_id = item.get("item_id", item.get("excerpt_id"))
        if item_id is None:
            continue
        normalized = str(item_id)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        item_ids.append(normalized)
    return item_ids


def _basket_promotion_items_from_snapshot(snapshot: dict[str, object]) -> list[object]:
    """Return basket promotion refs from a sparse retrieval snapshot."""

    basket_promotion_items = _normalize_list_like(snapshot.get("basket_promotion_items", []))
    if basket_promotion_items:
        return basket_promotion_items

    retrieval_evidence = snapshot.get("retrieval_evidence")
    if isinstance(retrieval_evidence, dict):
        basket_promotion_items = _normalize_list_like(
            retrieval_evidence.get("basket_promotion_items", [])
        )
        if basket_promotion_items:
            return basket_promotion_items

    for bundle_key in ("retrieval_source_bundle", "source_bundle"):
        source_bundle = snapshot.get(bundle_key)
        if isinstance(source_bundle, dict):
            basket_promotion_items = _normalize_list_like(
                source_bundle.get("basket_promotion_items", [])
            )
            if basket_promotion_items:
                return basket_promotion_items

    return []


def _basket_item_ids_from_snapshot(
    snapshot: dict[str, object],
    *,
    basket_promotion_items: list[object],
) -> list[object]:
    basket_item_ids = _normalize_list_like(snapshot.get("basket_item_ids", []))
    if basket_item_ids:
        return [str(item_id) for item_id in basket_item_ids if item_id is not None]

    for bundle_key in ("retrieval_source_bundle", "source_bundle"):
        source_bundle = snapshot.get(bundle_key)
        if isinstance(source_bundle, dict):
            basket_item_ids = _normalize_list_like(source_bundle.get("basket_item_ids", []))
            if basket_item_ids:
                return [str(item_id) for item_id in basket_item_ids if item_id is not None]

    return _basket_item_ids_from_items(basket_promotion_items)


def _first_text_value(*values: object) -> str | None:
    for value in values:
        text = _normalize_optional_text(value)
        if text is not None:
            return text
    return None


def _stable_fingerprint(payload: object) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _normalized_query_text(value: object) -> str | None:
    text = _normalize_optional_text(value)
    if text is None:
        return None
    return " ".join(text.casefold().split())


def _canonical_query_doc_types(value: object) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for item in _normalize_list_like(value):
        doc_type = str(item).strip().casefold()
        if not doc_type or doc_type in seen:
            continue
        seen.add(doc_type)
        normalized.append(doc_type)
    return sorted(normalized)


def _normalize_query_bool(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off", ""}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return False


def _normalize_query_max_results(value: object) -> int:
    try:
        max_results = int(value) if value is not None else 10
    except (TypeError, ValueError):
        return 10
    return max(1, max_results)


def _query_fingerprint_from_query_snapshot(query: dict[str, object]) -> str | None:
    query_text = _normalized_query_text(query.get("query_text"))
    scope = _normalize_optional_text(query.get("scope"))
    intent = _normalize_optional_text(query.get("intent"))
    if query_text is None or scope is None or intent is None:
        return None

    constraints = query.get("constraints", {})
    if not isinstance(constraints, dict):
        constraints = {}
    payload = {
        "query_text": query_text,
        "scope": scope,
        "intent": intent.casefold(),
        "constraints": {
            "max_results": _normalize_query_max_results(constraints.get("max_results")),
            "doc_types": _canonical_query_doc_types(constraints.get("doc_types")),
            "date_range": _normalize_optional_list_like(constraints.get("date_range")),
            "require_citations": _normalize_query_bool(constraints.get("require_citations")),
            "section_hint": _normalize_optional_text(constraints.get("section_hint")),
            "prefer_exact_matches": _normalize_query_bool(constraints.get("prefer_exact_matches")),
        },
        "confidentiality_profile": str(query.get("confidentiality_profile", "confidential")).strip().casefold(),
    }
    return _stable_fingerprint(payload)


def _is_missing_snapshot_value(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value == ""
    if isinstance(value, (dict, list, tuple, set)):
        return len(value) == 0
    return False


def _backfill_sparse_snapshot(primary: dict[str, object], fallback: dict[str, object]) -> dict[str, object]:
    merged = copy.deepcopy(primary)
    for key, fallback_value in fallback.items():
        if key not in merged:
            merged[key] = copy.deepcopy(fallback_value)
            continue

        primary_value = merged[key]
        if isinstance(primary_value, dict) and isinstance(fallback_value, dict):
            merged[key] = _backfill_sparse_snapshot(primary_value, fallback_value)
            continue

        if _is_missing_snapshot_value(primary_value) and not _is_missing_snapshot_value(fallback_value):
            merged[key] = copy.deepcopy(fallback_value)
    return merged


def _normalize_query_snapshot(query: object) -> dict[str, object]:
    if not isinstance(query, dict):
        return {}
    normalized = copy.deepcopy(query)
    constraints = normalized.get("constraints", {})
    if not isinstance(constraints, dict):
        constraints = {}
    else:
        constraints = copy.deepcopy(constraints)
    constraints["doc_types"] = _normalize_list_like(constraints.get("doc_types"))
    constraints["date_range"] = _normalize_optional_list_like(constraints.get("date_range"))
    constraints["section_hint"] = _normalize_optional_text(constraints.get("section_hint"))
    normalized["constraints"] = constraints
    return normalized


def _normalize_policy_snapshot(policy: object) -> dict[str, object]:
    if not isinstance(policy, dict):
        return {}
    normalized = copy.deepcopy(policy)
    normalized["active_strategy_ids"] = _normalize_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_list_like(normalized.get("deferred_strategy_ids"))
    return normalized


def _normalize_citation_bundle_snapshot(citation_bundle: dict[str, object]) -> dict[str, object]:
    normalized = copy.deepcopy(citation_bundle)
    normalized["query_date_range"] = _normalize_optional_list_like(normalized.get("query_date_range"))
    normalized["fts_shortlist_doc_ids"] = _normalize_list_like(normalized.get("fts_shortlist_doc_ids"))
    normalized["active_strategy_ids"] = _normalize_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_list_like(normalized.get("deferred_strategy_ids"))
    normalized["doc_citations"] = _normalize_list_like(normalized.get("doc_citations"))
    normalized["excerpt_citations"] = _normalize_list_like(normalized.get("excerpt_citations"))
    retrieval_policy = normalized.get("retrieval_policy")
    if isinstance(retrieval_policy, dict):
        normalized["retrieval_policy"] = _normalize_policy_snapshot(retrieval_policy)
    citation_status = normalized.get("citation_status")
    if isinstance(citation_status, dict):
        normalized["citation_status"] = copy.deepcopy(citation_status)
    elif "citation_status" in normalized:
        normalized["citation_status"] = {}
    return normalized


def _normalize_doc_bundle_snapshot(doc_bundle: dict[str, object]) -> dict[str, object]:
    normalized = copy.deepcopy(doc_bundle)
    normalized["query_date_range"] = _normalize_optional_list_like(normalized.get("query_date_range"))
    normalized["active_strategy_ids"] = _normalize_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_list_like(normalized.get("deferred_strategy_ids"))
    normalized["doc_hits"] = _normalize_list_like(normalized.get("doc_hits"))
    normalized["doc_citations"] = _normalize_list_like(normalized.get("doc_citations"))
    retrieval_policy = normalized.get("retrieval_policy")
    if isinstance(retrieval_policy, dict):
        normalized["retrieval_policy"] = _normalize_policy_snapshot(retrieval_policy)
    citation_status = normalized.get("citation_status")
    if isinstance(citation_status, dict):
        normalized["citation_status"] = copy.deepcopy(citation_status)
    elif "citation_status" in normalized:
        normalized["citation_status"] = {}
    return normalized


def _normalize_excerpt_bundle_snapshot(excerpt_bundle: dict[str, object]) -> dict[str, object]:
    normalized = copy.deepcopy(excerpt_bundle)
    normalized["query_date_range"] = _normalize_optional_list_like(normalized.get("query_date_range"))
    normalized["active_strategy_ids"] = _normalize_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_list_like(normalized.get("deferred_strategy_ids"))
    normalized["excerpt_hits"] = _normalize_list_like(normalized.get("excerpt_hits"))
    normalized["excerpt_citations"] = _normalize_list_like(normalized.get("excerpt_citations"))
    retrieval_policy = normalized.get("retrieval_policy")
    if isinstance(retrieval_policy, dict):
        normalized["retrieval_policy"] = _normalize_policy_snapshot(retrieval_policy)
    citation_status = normalized.get("citation_status")
    if isinstance(citation_status, dict):
        normalized["citation_status"] = copy.deepcopy(citation_status)
    elif "citation_status" in normalized:
        normalized["citation_status"] = {}
    return normalized


def _normalize_retrieval_summary_snapshot(summary: dict[str, object]) -> dict[str, object]:
    normalized = copy.deepcopy(summary)
    if "query_date_range" in normalized:
        normalized["query_date_range"] = _normalize_optional_list_like(normalized.get("query_date_range"))
    normalized["doc_ids"] = _normalize_list_like(normalized.get("doc_ids"))
    normalized["doc_fingerprints"] = _normalize_list_like(normalized.get("doc_fingerprints"))
    normalized["doc_identity_fingerprints"] = _normalize_list_like(normalized.get("doc_identity_fingerprints"))
    normalized["excerpt_ids"] = _normalize_list_like(normalized.get("excerpt_ids"))
    normalized["excerpt_fingerprints"] = _normalize_list_like(normalized.get("excerpt_fingerprints"))
    normalized["excerpt_text_hashes"] = _normalize_list_like(normalized.get("excerpt_text_hashes"))
    normalized["top_excerpt_fingerprints"] = _normalize_list_like(normalized.get("top_excerpt_fingerprints"))
    normalized["top_excerpt_text_hashes"] = _normalize_list_like(normalized.get("top_excerpt_text_hashes"))
    normalized["active_strategy_ids"] = _normalize_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_list_like(normalized.get("deferred_strategy_ids"))
    retrieval_policy = normalized.get("retrieval_policy")
    if isinstance(retrieval_policy, dict):
        normalized["retrieval_policy"] = _normalize_policy_snapshot(retrieval_policy)
    citation_status = normalized.get("citation_status")
    if isinstance(citation_status, dict):
        normalized["citation_status"] = copy.deepcopy(citation_status)
    elif "citation_status" in normalized:
        normalized["citation_status"] = {}
    return normalized


def _normalize_retrieval_manifest_snapshot(manifest: dict[str, object]) -> dict[str, object]:
    normalized = copy.deepcopy(manifest)
    normalized["doc_ids"] = _normalize_list_like(normalized.get("doc_ids"))
    normalized["doc_fingerprints"] = _normalize_list_like(normalized.get("doc_fingerprints"))
    normalized["doc_identity_fingerprints"] = _normalize_list_like(normalized.get("doc_identity_fingerprints"))
    normalized["top_excerpt_ids"] = _normalize_list_like(normalized.get("top_excerpt_ids"))
    normalized["top_excerpt_fingerprints"] = _normalize_list_like(normalized.get("top_excerpt_fingerprints"))
    normalized["top_excerpt_text_hashes"] = _normalize_list_like(normalized.get("top_excerpt_text_hashes"))
    normalized["excerpt_ids"] = _normalize_list_like(normalized.get("excerpt_ids"))
    normalized["excerpt_fingerprints"] = _normalize_list_like(normalized.get("excerpt_fingerprints"))
    normalized["excerpt_text_hashes"] = _normalize_list_like(normalized.get("excerpt_text_hashes"))
    normalized["active_strategy_ids"] = _normalize_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_list_like(normalized.get("deferred_strategy_ids"))
    retrieval_policy = normalized.get("retrieval_policy")
    if isinstance(retrieval_policy, dict):
        normalized["retrieval_policy"] = _normalize_policy_snapshot(retrieval_policy)
    return normalized


def _normalize_retrieval_evidence_snapshot(evidence: dict[str, object]) -> dict[str, object]:
    normalized = copy.deepcopy(evidence)
    normalized["active_strategy_ids"] = _normalize_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_list_like(normalized.get("deferred_strategy_ids"))
    normalized["doc_citations"] = _normalize_list_like(normalized.get("doc_citations"))
    normalized["excerpt_citations"] = _normalize_list_like(normalized.get("excerpt_citations"))
    retrieval_policy = normalized.get("retrieval_policy")
    if isinstance(retrieval_policy, dict):
        normalized["retrieval_policy"] = _normalize_policy_snapshot(retrieval_policy)
    retrieval_manifest = normalized.get("retrieval_manifest")
    if isinstance(retrieval_manifest, dict):
        normalized["retrieval_manifest"] = _normalize_retrieval_manifest_snapshot(retrieval_manifest)
    citation_status = normalized.get("citation_status")
    if isinstance(citation_status, dict):
        normalized["citation_status"] = copy.deepcopy(citation_status)
    elif "citation_status" in normalized:
        normalized["citation_status"] = {}
    return normalized


def _normalize_retrieval_source_bundle_snapshot(source_bundle: dict[str, object]) -> dict[str, object]:
    normalized = copy.deepcopy(source_bundle)
    if not isinstance(normalized, dict):
        return {}
    normalized["query"] = _normalize_query_snapshot(normalized.get("query", {}))
    normalized["policy"] = _normalize_policy_snapshot(
        normalized.get("policy", normalized.get("retrieval_policy", {}))
    )
    citation_status = normalized.get("citation_status")
    if isinstance(citation_status, dict):
        normalized["citation_status"] = copy.deepcopy(citation_status)
    elif "citation_status" in normalized:
        normalized["citation_status"] = {}
    normalized["retrieval_summary"] = _normalize_retrieval_summary_snapshot(
        normalized.get("retrieval_summary", {})
    )
    normalized["retrieval_manifest"] = _normalize_retrieval_manifest_snapshot(
        normalized.get("retrieval_manifest", {})
    )
    normalized["retrieval_evidence"] = _normalize_retrieval_evidence_snapshot(
        normalized.get("retrieval_evidence", {})
    )
    normalized["retrieval_citation_bundle"] = _build_retrieval_citation_bundle_from_payload(normalized)
    normalized["retrieval_doc_bundle"] = _build_retrieval_doc_bundle_from_payload(normalized)
    normalized["retrieval_excerpt_bundle"] = _build_retrieval_excerpt_bundle_from_payload(normalized)
    normalized["retrieval_provenance"] = _build_retrieval_provenance_from_payload(normalized)
    normalized["doc_hits"] = _normalize_list_like(normalized.get("doc_hits", []))
    normalized["excerpt_hits"] = _normalize_list_like(normalized.get("excerpt_hits", []))
    normalized["basket_promotion_items"] = _basket_promotion_items_from_snapshot(normalized)
    normalized["basket_item_ids"] = _basket_item_ids_from_snapshot(
        normalized,
        basket_promotion_items=normalized["basket_promotion_items"],
    )
    retrieval_summary = normalized.get("retrieval_summary", {})
    if not isinstance(retrieval_summary, dict):
        retrieval_summary = {}
    retrieval_provenance = normalized.get("retrieval_provenance", {})
    if not isinstance(retrieval_provenance, dict):
        retrieval_provenance = {}
    retrieval_citation_bundle = normalized.get("retrieval_citation_bundle", {})
    if not isinstance(retrieval_citation_bundle, dict):
        retrieval_citation_bundle = {}
    retrieval_policy = normalized.get("policy", normalized.get("retrieval_policy", {}))
    if not isinstance(retrieval_policy, dict):
        retrieval_policy = {}

    result_fingerprint = _first_text_value(
        normalized.get("result_fingerprint"),
        retrieval_summary.get("result_fingerprint"),
        retrieval_provenance.get("result_fingerprint"),
        retrieval_citation_bundle.get("result_fingerprint"),
    )
    if result_fingerprint is not None:
        normalized["result_fingerprint"] = result_fingerprint

    query_fingerprint = _first_text_value(
        normalized.get("query_fingerprint"),
        retrieval_summary.get("query_fingerprint"),
        retrieval_provenance.get("query_fingerprint"),
        retrieval_citation_bundle.get("query_fingerprint"),
    )
    if query_fingerprint is not None:
        normalized["query_fingerprint"] = query_fingerprint

    retrieval_backend = _first_text_value(
        normalized.get("retrieval_backend"),
        retrieval_policy.get("retrieval_backend"),
        retrieval_summary.get("retrieval_backend"),
        retrieval_provenance.get("retrieval_backend"),
        retrieval_citation_bundle.get("retrieval_backend"),
    )
    if retrieval_backend is not None:
        normalized["retrieval_backend"] = retrieval_backend

    retrieval_mode = _first_text_value(
        normalized.get("retrieval_mode"),
        retrieval_policy.get("retrieval_mode"),
        retrieval_summary.get("retrieval_mode"),
        retrieval_provenance.get("retrieval_mode"),
        retrieval_citation_bundle.get("retrieval_mode"),
    )
    if retrieval_mode is not None:
        normalized["retrieval_mode"] = retrieval_mode

    normalized["source_bundle_fingerprint"] = _stable_fingerprint(
        {key: value for key, value in normalized.items() if key != "source_bundle_fingerprint"}
    )
    return normalized


def _build_retrieval_citation_bundle_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return the deterministic citation bundle from a downstream payload snapshot."""

    citation_bundle = payload.get("retrieval_citation_bundle")
    if isinstance(citation_bundle, dict):
        return copy.deepcopy(citation_bundle)

    query = payload.get("query", {})
    if not isinstance(query, dict):
        query = {}
    query_fingerprint = _query_fingerprint_from_query_snapshot(query)
    query_constraints = query.get("constraints", {})
    if not isinstance(query_constraints, dict):
        query_constraints = {}

    provenance = payload.get("retrieval_provenance", {})
    summary = payload.get("retrieval_summary", {})
    diagnostics = payload.get("retrieval_diagnostics", {})
    if not isinstance(provenance, dict):
        provenance = {}
    if not isinstance(summary, dict):
        summary = {}
    if not isinstance(diagnostics, dict):
        diagnostics = {}
    active_strategy_ids = provenance.get(
        "active_strategy_ids",
        summary.get("active_strategy_ids", diagnostics.get("active_strategy_ids", [])),
    )
    deferred_strategy_ids = provenance.get(
        "deferred_strategy_ids",
        summary.get("deferred_strategy_ids", diagnostics.get("deferred_strategy_ids", [])),
    )
    query_scope = query.get(
        "scope",
        provenance.get("query_scope", summary.get("query_scope", diagnostics.get("query_scope"))),
    )
    query_intent = query.get(
        "intent",
        provenance.get("query_intent", summary.get("query_intent", diagnostics.get("query_intent"))),
    )
    query_date_range = query_constraints.get(
        "date_range",
        provenance.get("query_date_range", summary.get("query_date_range", diagnostics.get("date_range"))),
    )
    query_date_range = _normalize_optional_list_like(query_date_range)
    candidate_doc_count = provenance.get(
        "candidate_doc_count",
        summary.get("candidate_doc_count", diagnostics.get("candidate_doc_count")),
    )
    fts_shortlist_doc_ids = _normalize_list_like(
        provenance.get(
            "fts_shortlist_doc_ids",
            summary.get("fts_shortlist_doc_ids", diagnostics.get("fts_shortlist_doc_ids", [])),
        )
    )
    return _normalize_citation_bundle_snapshot({
        "query_fingerprint": _first_text_value(
            provenance.get("query_fingerprint"),
            summary.get("query_fingerprint"),
            diagnostics.get("query_fingerprint"),
            query_fingerprint,
        ),
        "result_fingerprint": provenance.get(
            "result_fingerprint",
            summary.get("result_fingerprint", diagnostics.get("result_fingerprint")),
        ),
        "query_scope": query_scope,
        "query_intent": query_intent,
        "query_date_range": query_date_range,
        "candidate_doc_count": candidate_doc_count,
        "fts_shortlist_doc_ids": fts_shortlist_doc_ids,
        "retrieval_backend": provenance.get(
            "retrieval_backend",
            summary.get("retrieval_backend", diagnostics.get("retrieval_backend")),
        ),
        "retrieval_mode": provenance.get(
            "retrieval_mode",
            summary.get("retrieval_mode", diagnostics.get("retrieval_mode")),
        ),
        "retrieval_policy": copy.deepcopy(
            provenance.get(
                "retrieval_policy",
                summary.get("retrieval_policy", diagnostics.get("retrieval_policy", {})),
            )
        ),
        "active_strategy_ids": list(active_strategy_ids) if isinstance(active_strategy_ids, (list, tuple)) else [],
        "deferred_strategy_ids": list(deferred_strategy_ids) if isinstance(deferred_strategy_ids, (list, tuple)) else [],
        "citation_status": copy.deepcopy(summary.get("citation_status", provenance.get("citation_status", {}))),
        "doc_count": provenance.get("doc_count", summary.get("doc_count")),
        "excerpt_count": provenance.get("excerpt_count", summary.get("excerpt_count")),
        "doc_hits_fingerprint": provenance.get(
            "doc_hits_fingerprint", summary.get("doc_hits_fingerprint", diagnostics.get("doc_hits_fingerprint"))
        ),
        "excerpt_hits_fingerprint": provenance.get(
            "excerpt_hits_fingerprint",
            summary.get("excerpt_hits_fingerprint", diagnostics.get("excerpt_hits_fingerprint")),
        ),
        "doc_citations": copy.deepcopy(provenance.get("doc_citations", [])),
        "excerpt_citations": copy.deepcopy(provenance.get("excerpt_citations", [])),
    })


def _build_retrieval_source_bundle_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return the deterministic retrieval source bundle from a downstream payload snapshot."""

    source_bundle = payload.get("retrieval_source_bundle")
    if not isinstance(source_bundle, dict):
        source_bundle = payload.get("source_bundle")
    if isinstance(source_bundle, dict):
        return _normalize_retrieval_source_bundle_snapshot(source_bundle)
    retrieval_doc_bundle = payload.get("retrieval_doc_bundle")
    if not isinstance(retrieval_doc_bundle, dict):
        retrieval_doc_bundle = _build_retrieval_doc_bundle_from_payload(payload)
    retrieval_excerpt_bundle = payload.get("retrieval_excerpt_bundle")
    if not isinstance(retrieval_excerpt_bundle, dict):
        retrieval_excerpt_bundle = _build_retrieval_excerpt_bundle_from_payload(payload)
    query_snapshot = _normalize_query_snapshot(payload.get("query", {}))
    policy_snapshot = _normalize_policy_snapshot(payload.get("policy", payload.get("retrieval_policy", {})))
    basket_promotion_items = _basket_promotion_items_from_snapshot(payload)
    basket_item_ids = _basket_item_ids_from_snapshot(
        payload,
        basket_promotion_items=basket_promotion_items,
    )
    return _normalize_retrieval_source_bundle_snapshot({
        "result_fingerprint": payload.get("result_fingerprint"),
        "query_fingerprint": payload.get("query_fingerprint"),
        "query": query_snapshot,
        "policy": policy_snapshot,
        "retrieval_backend": payload.get("retrieval_backend"),
        "retrieval_mode": payload.get("retrieval_mode"),
        "citation_status": copy.deepcopy(payload.get("citation_status", {})),
        "retrieval_citation_bundle": copy.deepcopy(payload.get("retrieval_citation_bundle", {})),
        "retrieval_summary": copy.deepcopy(payload.get("retrieval_summary", {})),
        "retrieval_doc_bundle": copy.deepcopy(retrieval_doc_bundle),
        "retrieval_excerpt_bundle": copy.deepcopy(retrieval_excerpt_bundle),
        "doc_hits": copy.deepcopy(payload.get("doc_hits", [])),
        "excerpt_hits": copy.deepcopy(payload.get("excerpt_hits", [])),
        "retrieval_manifest": copy.deepcopy(payload.get("retrieval_manifest", {})),
        "retrieval_evidence": copy.deepcopy(payload.get("retrieval_evidence", {})),
        "retrieval_provenance": copy.deepcopy(payload.get("retrieval_provenance", {})),
        "basket_promotion_items": copy.deepcopy(basket_promotion_items),
        "basket_item_ids": copy.deepcopy(basket_item_ids),
    })


def _backfill_downstream_payload_from_context_bundle(
    payload: dict[str, object],
    context_bundle: dict[str, object],
) -> dict[str, object]:
    merged = copy.deepcopy(payload)
    source_bundle = context_bundle.get("retrieval_source_bundle")
    if isinstance(source_bundle, dict):
        merged = _backfill_sparse_snapshot(
            merged,
            _build_retrieval_downstream_payload_from_source_bundle(source_bundle),
        )
    context_backfill = {
        "audit_ref": context_bundle.get("audit_ref"),
        "result_fingerprint": context_bundle.get("result_fingerprint"),
        "retrieval_citation_bundle": context_bundle.get("retrieval_citation_bundle"),
        "retrieval_doc_bundle": context_bundle.get("retrieval_doc_bundle"),
        "retrieval_excerpt_bundle": context_bundle.get("retrieval_excerpt_bundle"),
        "retrieval_provenance": context_bundle.get("retrieval_provenance"),
        "retrieval_source_bundle": context_bundle.get("retrieval_source_bundle"),
        "retrieval_evidence": context_bundle.get("retrieval_evidence"),
        "basket_promotion_items": context_bundle.get("basket_promotion_items"),
        "basket_item_ids": context_bundle.get("basket_item_ids"),
    }
    return _backfill_sparse_snapshot(
        merged,
        {key: value for key, value in context_backfill.items() if value is not None},
    )


def _build_retrieval_context_bundle_from_source_bundle(source_bundle: dict[str, object]) -> dict[str, object]:
    """Return the deterministic retrieval context bundle from a source-bundle snapshot."""

    source_bundle = _normalize_retrieval_source_bundle_snapshot(source_bundle)
    downstream_payload = _build_retrieval_downstream_payload_from_source_bundle(source_bundle)
    retrieval_citation_bundle = source_bundle.get("retrieval_citation_bundle", {})
    if not isinstance(retrieval_citation_bundle, dict):
        retrieval_citation_bundle = _build_retrieval_citation_bundle_from_payload(source_bundle)
    retrieval_doc_bundle = source_bundle.get("retrieval_doc_bundle", {})
    if not isinstance(retrieval_doc_bundle, dict):
        retrieval_doc_bundle = _build_retrieval_doc_bundle_from_payload(source_bundle)
    retrieval_excerpt_bundle = source_bundle.get("retrieval_excerpt_bundle", {})
    if not isinstance(retrieval_excerpt_bundle, dict):
        retrieval_excerpt_bundle = _build_retrieval_excerpt_bundle_from_payload(source_bundle)
    retrieval_provenance = source_bundle.get("retrieval_provenance", {})
    if not isinstance(retrieval_provenance, dict):
        retrieval_provenance = _build_retrieval_provenance_from_payload(source_bundle)
    basket_promotion_items = _basket_promotion_items_from_snapshot(source_bundle)
    return {
        # Source-bundle-only reconstruction keeps the top-level context auditless.
        "audit_ref": None,
        "result_fingerprint": source_bundle.get("result_fingerprint"),
        "retrieval_downstream_payload": copy.deepcopy(downstream_payload),
        "retrieval_citation_bundle": copy.deepcopy(retrieval_citation_bundle),
        "retrieval_doc_bundle": copy.deepcopy(retrieval_doc_bundle),
        "retrieval_excerpt_bundle": copy.deepcopy(retrieval_excerpt_bundle),
        "retrieval_provenance": copy.deepcopy(retrieval_provenance),
        "retrieval_source_bundle": copy.deepcopy(source_bundle),
        "retrieval_evidence": copy.deepcopy(source_bundle.get("retrieval_evidence", {})),
        "basket_promotion_items": basket_promotion_items,
        "basket_item_ids": _basket_item_ids_from_snapshot(
            source_bundle,
            basket_promotion_items=basket_promotion_items,
        ),
    }


def _build_retrieval_bundle_context_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return the shared retrieval snapshot fields from a downstream payload snapshot."""

    provenance = payload.get("retrieval_provenance", {})
    summary = payload.get("retrieval_summary", {})
    diagnostics = payload.get("retrieval_diagnostics", {})
    if not isinstance(provenance, dict):
        provenance = {}
    if not isinstance(summary, dict):
        summary = {}
    if not isinstance(diagnostics, dict):
        diagnostics = {}
    query = payload.get("query", {})
    if not isinstance(query, dict):
        query = {}
    query_fingerprint = _query_fingerprint_from_query_snapshot(query)
    query_constraints = query.get("constraints", {})
    if not isinstance(query_constraints, dict):
        query_constraints = {}
    citation_bundle = payload.get("retrieval_citation_bundle", {})
    if not isinstance(citation_bundle, dict):
        citation_bundle = _build_retrieval_citation_bundle_from_payload(payload)
    query_date_range = _normalize_optional_list_like(
        query_constraints.get(
            "date_range",
            provenance.get("query_date_range", summary.get("query_date_range", diagnostics.get("date_range"))),
        )
    )
    return {
        "result_fingerprint": payload.get("result_fingerprint"),
        "query_fingerprint": _first_text_value(
            payload.get("query_fingerprint"),
            provenance.get("query_fingerprint"),
            summary.get("query_fingerprint"),
            diagnostics.get("query_fingerprint"),
            query_fingerprint,
        ),
        "query_scope": query.get(
            "scope",
            provenance.get("query_scope", summary.get("query_scope", diagnostics.get("query_scope"))),
        ),
        "query_intent": query.get(
            "intent",
            provenance.get("query_intent", summary.get("query_intent", diagnostics.get("query_intent"))),
        ),
        "query_date_range": query_date_range,
        "retrieval_backend": payload.get("retrieval_backend", summary.get("retrieval_backend", diagnostics.get("retrieval_backend"))),
        "retrieval_mode": payload.get("retrieval_mode", summary.get("retrieval_mode", diagnostics.get("retrieval_mode"))),
        "retrieval_policy": _normalize_policy_snapshot(
            payload.get("retrieval_policy", payload.get("policy", summary.get("retrieval_policy", diagnostics.get("retrieval_policy", {}))))
        ),
        "active_strategy_ids": _normalize_list_like(
            provenance.get("active_strategy_ids", summary.get("active_strategy_ids", diagnostics.get("active_strategy_ids", [])))
        ),
        "deferred_strategy_ids": _normalize_list_like(
            provenance.get("deferred_strategy_ids", summary.get("deferred_strategy_ids", diagnostics.get("deferred_strategy_ids", [])))
        ),
        "citation_status": copy.deepcopy(payload.get("citation_status", summary.get("citation_status", provenance.get("citation_status", {})))),
        "retrieval_citation_bundle": copy.deepcopy(citation_bundle),
        "retrieval_manifest": copy.deepcopy(payload.get("retrieval_manifest", {})),
        "retrieval_provenance": copy.deepcopy(provenance),
        "retrieval_evidence": copy.deepcopy(payload.get("retrieval_evidence", {})),
    }


def _build_retrieval_doc_bundle_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return the deterministic doc-focused bundle from a downstream payload snapshot."""

    doc_bundle = payload.get("retrieval_doc_bundle")
    if isinstance(doc_bundle, dict):
        return copy.deepcopy(doc_bundle)
    bundle_context = _build_retrieval_bundle_context_from_payload(payload)
    provenance = bundle_context["retrieval_provenance"]
    doc_hits = copy.deepcopy(payload.get("doc_hits", []))
    doc_citations: list[dict[str, object]] = []
    if isinstance(provenance, dict):
        doc_citations = copy.deepcopy(provenance.get("doc_citations", []))
    return {
        **bundle_context,
        "doc_count": len(doc_hits),
        "doc_hits": doc_hits,
        "doc_citations": doc_citations,
    }


def _build_retrieval_excerpt_bundle_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return the deterministic excerpt-focused bundle from a downstream payload snapshot."""

    excerpt_bundle = payload.get("retrieval_excerpt_bundle")
    if isinstance(excerpt_bundle, dict):
        return copy.deepcopy(excerpt_bundle)
    bundle_context = _build_retrieval_bundle_context_from_payload(payload)
    provenance = bundle_context["retrieval_provenance"]
    excerpt_hits = _normalize_list_like(payload.get("excerpt_hits", []))
    excerpt_citations: list[dict[str, object]] = []
    if isinstance(provenance, dict):
        excerpt_citations = _normalize_list_like(provenance.get("excerpt_citations", []))
    return {
        **bundle_context,
        "doc_count": len(_normalize_list_like(payload.get("doc_hits", []))),
        "excerpt_count": len(excerpt_hits) if excerpt_hits else len(excerpt_citations),
        "excerpt_hits": excerpt_hits,
        "excerpt_citations": excerpt_citations,
    }


def _build_retrieval_context_bundle_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return the deterministic retrieval context bundle from a downstream payload snapshot."""

    basket_promotion_items = _basket_promotion_items_from_snapshot(payload)
    basket_item_ids = _basket_item_ids_from_snapshot(
        payload,
        basket_promotion_items=basket_promotion_items,
    )
    return {
        "audit_ref": payload.get("audit_ref"),
        "result_fingerprint": payload.get("result_fingerprint"),
        "retrieval_downstream_payload": copy.deepcopy(payload),
        "retrieval_citation_bundle": _build_retrieval_citation_bundle_from_payload(payload),
        "retrieval_doc_bundle": _build_retrieval_doc_bundle_from_payload(payload),
        "retrieval_excerpt_bundle": _build_retrieval_excerpt_bundle_from_payload(payload),
        "retrieval_provenance": _build_retrieval_provenance_from_payload(payload),
        "retrieval_source_bundle": _build_retrieval_source_bundle_from_payload(payload),
        "retrieval_evidence": copy.deepcopy(payload.get("retrieval_evidence", {})),
        "basket_promotion_items": basket_promotion_items,
        "basket_item_ids": basket_item_ids,
    }


def _build_retrieval_diagnostics_from_source_bundle(source_bundle: dict[str, object]) -> dict[str, object]:
    """Return a best-effort diagnostics snapshot from a source bundle snapshot."""

    normalized = _normalize_retrieval_source_bundle_snapshot(source_bundle)
    citation_bundle = normalized.get("retrieval_citation_bundle", {})
    if not isinstance(citation_bundle, dict):
        citation_bundle = _build_retrieval_citation_bundle_from_payload(normalized)

    query = normalized.get("query", {})
    if not isinstance(query, dict):
        query = {}
    query_fingerprint = _query_fingerprint_from_query_snapshot(query)
    query_constraints = query.get("constraints", {})
    if not isinstance(query_constraints, dict):
        query_constraints = {}

    retrieval_policy = _normalize_policy_snapshot(
        normalized.get("policy", normalized.get("retrieval_policy", {}))
    )
    active_strategy_ids = _normalize_list_like(
        citation_bundle.get("active_strategy_ids", retrieval_policy.get("active_strategy_ids", []))
    )
    deferred_strategy_ids = _normalize_list_like(
        citation_bundle.get("deferred_strategy_ids", retrieval_policy.get("deferred_strategy_ids", []))
    )
    query_scope = citation_bundle.get("query_scope", query.get("scope"))
    query_intent = citation_bundle.get("query_intent", query.get("intent"))
    query_date_range = _normalize_optional_list_like(
        citation_bundle.get("query_date_range", query_constraints.get("date_range"))
    )
    max_results = query_constraints.get("max_results", citation_bundle.get("doc_count", 10))
    try:
        max_results_int = int(max_results)
    except (TypeError, ValueError):
        max_results_int = 10
    fts_shortlist_limit = max(25, max_results_int)
    fts_candidate_scan_limit = (
        fts_shortlist_limit
        if query_date_range is None
        else max(fts_shortlist_limit, fts_shortlist_limit * 4, 100)
    )
    fts_shortlist_doc_ids = _normalize_list_like(citation_bundle.get("fts_shortlist_doc_ids", []))
    strategies_used = list(active_strategy_ids)

    return {
        "retrieval_policy": copy.deepcopy(retrieval_policy),
        "retrieval_backend": citation_bundle.get(
            "retrieval_backend",
            normalized.get("retrieval_backend"),
        ),
        "retrieval_mode": citation_bundle.get(
            "retrieval_mode",
            normalized.get("retrieval_mode"),
        ),
        "active_strategy_ids": strategies_used,
        "deferred_strategy_ids": deferred_strategy_ids,
        "query_fingerprint": _first_text_value(
            citation_bundle.get("query_fingerprint"),
            normalized.get("query_fingerprint"),
            query_fingerprint,
        ),
        "query_scope": query_scope,
        "query_intent": query_intent,
        "doc_scope_id": query_scope.split(":", 1)[1] if isinstance(query_scope, str) and query_scope.startswith("doc:") else None,
        "date_range": query_date_range,
        "fts_shortlist_limit": fts_shortlist_limit,
        "fts_candidate_scan_limit": fts_candidate_scan_limit,
        "candidate_doc_count": citation_bundle.get("candidate_doc_count"),
        "fts_shortlist_count": len(fts_shortlist_doc_ids),
        "fts_shortlist_doc_ids": fts_shortlist_doc_ids,
        "strategies_used": strategies_used,
        "elapsed_ms_by_strategy": {strategy_id: 0 for strategy_id in strategies_used},
        "caches_used": {strategy_id: False for strategy_id in strategies_used},
        "elapsed_ms_total": 0,
        "doc_hits_count": citation_bundle.get("doc_count", len(_normalize_list_like(normalized.get("doc_hits", [])))),
        "excerpt_hits_count": citation_bundle.get("excerpt_count", len(_normalize_list_like(normalized.get("excerpt_hits", [])))),
        "doc_hits_fingerprint": citation_bundle.get("doc_hits_fingerprint"),
        "excerpt_hits_fingerprint": citation_bundle.get("excerpt_hits_fingerprint"),
        "citation_status": copy.deepcopy(
            citation_bundle.get("citation_status", normalized.get("citation_status", {}))
        ),
        "retrieval_manifest": copy.deepcopy(normalized.get("retrieval_manifest", {})),
        "retrieval_evidence": copy.deepcopy(normalized.get("retrieval_evidence", {})),
        "result_fingerprint": citation_bundle.get(
            "result_fingerprint",
            normalized.get("result_fingerprint"),
        ),
    }


def _build_retrieval_provenance_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return the deterministic retrieval provenance snapshot from a downstream payload snapshot."""

    provenance = payload.get("retrieval_provenance")
    if isinstance(provenance, dict):
        normalized = copy.deepcopy(provenance)
    else:
        normalized = {}
    summary = payload.get("retrieval_summary", {})
    diagnostics = payload.get("retrieval_diagnostics", {})
    if not isinstance(summary, dict):
        summary = {}
    if not isinstance(diagnostics, dict):
        diagnostics = {}
    query = payload.get("query", {})
    if not isinstance(query, dict):
        query = {}
    query_fingerprint = _query_fingerprint_from_query_snapshot(query)
    query_constraints = query.get("constraints", {})
    if not isinstance(query_constraints, dict):
        query_constraints = {}
    query_date_range = _normalize_optional_list_like(normalized.get("query_date_range"))
    if _is_missing_snapshot_value(normalized.get("query_fingerprint")):
        normalized["query_fingerprint"] = _first_text_value(
            summary.get("query_fingerprint"),
            diagnostics.get("query_fingerprint"),
            query_fingerprint,
        )
    if "query_scope" not in normalized:
        normalized["query_scope"] = summary.get("query_scope", diagnostics.get("query_scope", query.get("scope")))
    if "query_intent" not in normalized:
        normalized["query_intent"] = summary.get("query_intent", diagnostics.get("query_intent", query.get("intent")))
    if "query_date_range" not in normalized:
        normalized["query_date_range"] = _normalize_optional_list_like(
            summary.get(
                "query_date_range",
                diagnostics.get("date_range", query_constraints.get("date_range")),
            )
        )
    else:
        normalized["query_date_range"] = query_date_range
    if "result_fingerprint" not in normalized:
        normalized["result_fingerprint"] = summary.get("result_fingerprint", diagnostics.get("result_fingerprint"))
    if "retrieval_backend" not in normalized:
        normalized["retrieval_backend"] = summary.get("retrieval_backend", diagnostics.get("retrieval_backend"))
    if "retrieval_mode" not in normalized:
        normalized["retrieval_mode"] = summary.get("retrieval_mode", diagnostics.get("retrieval_mode"))
    if "retrieval_policy" not in normalized:
        normalized["retrieval_policy"] = _normalize_policy_snapshot(
            summary.get("retrieval_policy", diagnostics.get("retrieval_policy", {}))
        )
    else:
        normalized["retrieval_policy"] = _normalize_policy_snapshot(normalized["retrieval_policy"])
    if "active_strategy_ids" not in normalized:
        normalized["active_strategy_ids"] = _normalize_list_like(
            summary.get("active_strategy_ids", diagnostics.get("active_strategy_ids", []))
        )
    else:
        normalized["active_strategy_ids"] = _normalize_list_like(normalized["active_strategy_ids"])
    if "deferred_strategy_ids" not in normalized:
        normalized["deferred_strategy_ids"] = _normalize_list_like(
            summary.get("deferred_strategy_ids", diagnostics.get("deferred_strategy_ids", []))
        )
    else:
        normalized["deferred_strategy_ids"] = _normalize_list_like(normalized["deferred_strategy_ids"])
    if "candidate_doc_count" not in normalized:
        normalized["candidate_doc_count"] = diagnostics.get("candidate_doc_count")
    if "fts_shortlist_doc_ids" not in normalized:
        normalized["fts_shortlist_doc_ids"] = _normalize_list_like(
            diagnostics.get("fts_shortlist_doc_ids", [])
        )
    else:
        normalized["fts_shortlist_doc_ids"] = _normalize_list_like(normalized["fts_shortlist_doc_ids"])
    if "primary_doc_id" not in normalized:
        normalized["primary_doc_id"] = summary.get("primary_doc_id")
    if "primary_doc_fingerprint" not in normalized:
        normalized["primary_doc_fingerprint"] = summary.get("primary_doc_fingerprint")
    if "primary_doc_identity_fingerprint" not in normalized:
        normalized["primary_doc_identity_fingerprint"] = summary.get("primary_doc_identity_fingerprint")
    if "primary_excerpt_id" not in normalized:
        normalized["primary_excerpt_id"] = summary.get("primary_excerpt_id")
    if "primary_excerpt_fingerprint" not in normalized:
        normalized["primary_excerpt_fingerprint"] = summary.get("primary_excerpt_fingerprint")
    if "primary_excerpt_text_hash" not in normalized:
        normalized["primary_excerpt_text_hash"] = summary.get("primary_excerpt_text_hash")
    if "doc_hits_fingerprint" not in normalized:
        normalized["doc_hits_fingerprint"] = summary.get(
            "doc_hits_fingerprint",
            diagnostics.get("doc_hits_fingerprint"),
        )
    if "excerpt_hits_fingerprint" not in normalized:
        normalized["excerpt_hits_fingerprint"] = summary.get(
            "excerpt_hits_fingerprint",
            diagnostics.get("excerpt_hits_fingerprint"),
        )
    if "citation_status" not in normalized:
        normalized["citation_status"] = copy.deepcopy(summary.get("citation_status", {}))
    if "doc_count" not in normalized:
        normalized["doc_count"] = summary.get("doc_count")
    if "excerpt_count" not in normalized:
        normalized["excerpt_count"] = summary.get("excerpt_count")
    citation_bundle = payload.get("retrieval_citation_bundle", {})
    if not isinstance(citation_bundle, dict):
        citation_bundle = {}
    doc_citations = citation_bundle.get("doc_citations", [])
    if not isinstance(doc_citations, list):
        doc_citations = []
    excerpt_citations = citation_bundle.get("excerpt_citations", [])
    if not isinstance(excerpt_citations, list):
        excerpt_citations = []
    if "doc_citations" not in normalized:
        normalized["doc_citations"] = copy.deepcopy(doc_citations)
    if "excerpt_citations" not in normalized:
        normalized["excerpt_citations"] = copy.deepcopy(excerpt_citations)
    else:
        normalized["excerpt_citations"] = _normalize_list_like(normalized["excerpt_citations"])
    if _is_missing_snapshot_value(normalized.get("primary_doc_id")) and doc_citations:
        first_doc_citation = doc_citations[0]
        if isinstance(first_doc_citation, dict):
            normalized["primary_doc_id"] = first_doc_citation.get("doc_id")
            if _is_missing_snapshot_value(normalized.get("primary_doc_fingerprint")):
                normalized["primary_doc_fingerprint"] = first_doc_citation.get("doc_fingerprint")
            if _is_missing_snapshot_value(normalized.get("primary_doc_identity_fingerprint")):
                normalized["primary_doc_identity_fingerprint"] = first_doc_citation.get("doc_identity_fingerprint")
    if _is_missing_snapshot_value(normalized.get("primary_excerpt_id")) and excerpt_citations:
        first_excerpt_citation = excerpt_citations[0]
        if isinstance(first_excerpt_citation, dict):
            normalized["primary_excerpt_id"] = first_excerpt_citation.get("excerpt_id")
            if _is_missing_snapshot_value(normalized.get("primary_excerpt_fingerprint")):
                normalized["primary_excerpt_fingerprint"] = first_excerpt_citation.get("excerpt_fingerprint")
            if _is_missing_snapshot_value(normalized.get("primary_excerpt_text_hash")):
                normalized["primary_excerpt_text_hash"] = first_excerpt_citation.get("excerpt_text_hash")
    return normalized


@dataclass(frozen=True)
class RetrievalDownstreamPayload:
    """Deterministic downstream retrieval contract for engine consumers."""

    query: dict[str, object]
    policy: dict[str, object]
    audit_ref: str
    result_fingerprint: str
    retrieval_backend: str
    retrieval_mode: str
    citation_status: dict[str, object]
    retrieval_citation_bundle: dict[str, object]
    retrieval_doc_bundle: dict[str, object]
    retrieval_excerpt_bundle: dict[str, object]
    retrieval_summary: dict[str, object]
    doc_hits: list[dict[str, object]]
    excerpt_hits: list[dict[str, object]]
    retrieval_diagnostics: dict[str, object]
    retrieval_manifest: dict[str, object]
    retrieval_evidence: dict[str, object]
    retrieval_provenance: dict[str, object]
    retrieval_source_bundle: dict[str, object]
    basket_promotion_items: list[dict[str, object]] | None = None

    def as_dict(self) -> dict[str, object]:
        policy = copy.deepcopy(self.policy)
        diagnostics = copy.deepcopy(self.retrieval_diagnostics)
        manifest = copy.deepcopy(self.retrieval_manifest)
        evidence = copy.deepcopy(self.retrieval_evidence)
        provenance = copy.deepcopy(self.retrieval_provenance)
        summary = copy.deepcopy(self.retrieval_summary)
        source_bundle = copy.deepcopy(self.retrieval_source_bundle)
        basket_promotion_items = _normalize_list_like(self.basket_promotion_items)
        return {
            "query": copy.deepcopy(self.query),
            "policy": policy,
            "retrieval_policy": copy.deepcopy(policy),
            "audit_ref": self.audit_ref,
            "result_fingerprint": self.result_fingerprint,
            "retrieval_backend": self.retrieval_backend,
            "retrieval_mode": self.retrieval_mode,
            "citation_status": copy.deepcopy(self.citation_status),
            "retrieval_citation_bundle": copy.deepcopy(self.retrieval_citation_bundle),
            "retrieval_doc_bundle": copy.deepcopy(self.retrieval_doc_bundle),
            "retrieval_excerpt_bundle": copy.deepcopy(self.retrieval_excerpt_bundle),
            "retrieval_summary": summary,
            "doc_hits": [copy.deepcopy(doc_hit) for doc_hit in self.doc_hits],
            "excerpt_hits": [copy.deepcopy(hit) for hit in self.excerpt_hits],
            "retrieval_diagnostics": diagnostics,
            "retrieval_manifest": manifest,
            "retrieval_evidence": evidence,
            "retrieval_provenance": provenance,
            "retrieval_source_bundle": source_bundle,
            "basket_promotion_items": basket_promotion_items,
            "basket_item_ids": _basket_item_ids_from_items(basket_promotion_items),
        }


def build_retrieval_provenance_from_result(
    result: RetrievalDownstreamPayloadSource,
) -> dict[str, object]:
    """Return the deterministic retrieval provenance snapshot for a result."""

    provenance_source = getattr(result, "retrieval_provenance_bundle", None)
    if callable(provenance_source):
        return copy.deepcopy(provenance_source())
    payload = build_retrieval_downstream_payload_from_result(result)
    return _build_retrieval_provenance_from_payload(payload)


def build_retrieval_downstream_payload(
    *,
    query: dict[str, object],
    policy: dict[str, object],
    audit_ref: str,
    result_fingerprint: str,
    retrieval_backend: str,
    retrieval_mode: str,
    citation_status: dict[str, object],
    retrieval_citation_bundle: dict[str, object],
    retrieval_doc_bundle: dict[str, object],
    retrieval_excerpt_bundle: dict[str, object],
    retrieval_summary: dict[str, object],
    doc_hits: list[dict[str, object]],
    excerpt_hits: list[dict[str, object]],
    retrieval_diagnostics: dict[str, object],
    retrieval_manifest: dict[str, object],
    retrieval_evidence: dict[str, object],
    retrieval_provenance: dict[str, object],
    retrieval_source_bundle: dict[str, object],
    basket_promotion_items: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return RetrievalDownstreamPayload(
        query=query,
        policy=policy,
        audit_ref=audit_ref,
        result_fingerprint=result_fingerprint,
        retrieval_backend=retrieval_backend,
        retrieval_mode=retrieval_mode,
        citation_status=citation_status,
        retrieval_citation_bundle=retrieval_citation_bundle,
        retrieval_doc_bundle=retrieval_doc_bundle,
        retrieval_excerpt_bundle=retrieval_excerpt_bundle,
        retrieval_summary=retrieval_summary,
        doc_hits=doc_hits,
        excerpt_hits=excerpt_hits,
        retrieval_diagnostics=retrieval_diagnostics,
        retrieval_manifest=retrieval_manifest,
        retrieval_evidence=retrieval_evidence,
        retrieval_provenance=retrieval_provenance,
        retrieval_source_bundle=retrieval_source_bundle,
        basket_promotion_items=basket_promotion_items,
    ).as_dict()


def build_retrieval_downstream_payload_from_result(
    result: RetrievalDownstreamPayloadSource,
) -> dict[str, object]:
    """Return a snapshot-safe copy of a retrieval result payload.

    Engine callers use this helper when they want the canonical downstream
    retrieval contract without holding onto the mutable service object that
    produced it.
    """
    payload_source = getattr(result, "as_downstream_payload", None)
    if callable(payload_source):
        return copy.deepcopy(payload_source())
    payload_source = getattr(result, "as_dict", None)
    if callable(payload_source):
        return copy.deepcopy(payload_source())
    context_bundle_source = getattr(result, "retrieval_context_bundle", None)
    if callable(context_bundle_source):
        context_bundle = context_bundle_source()
        if isinstance(context_bundle, dict):
            downstream_payload = context_bundle.get("retrieval_downstream_payload")
            if isinstance(downstream_payload, dict):
                return _backfill_downstream_payload_from_context_bundle(
                    copy.deepcopy(downstream_payload),
                    context_bundle,
                )
            source_bundle = context_bundle.get("retrieval_source_bundle")
            if isinstance(source_bundle, dict):
                return _build_retrieval_downstream_payload_from_source_bundle(source_bundle)
    source_bundle = _build_retrieval_source_bundle_from_result_source(result)
    if source_bundle is not None:
        return _build_retrieval_downstream_payload_from_source_bundle(source_bundle)
    if not hasattr(result, "to_downstream_payload"):
        raise AttributeError(
            "result must expose a downstream payload, context bundle, or source bundle"
        )
    return copy.deepcopy(result.to_downstream_payload())


def _build_retrieval_downstream_payload_from_source_bundle(
    source_bundle: dict[str, object],
) -> dict[str, object]:
    normalized = _normalize_retrieval_source_bundle_snapshot(source_bundle)
    payload = copy.deepcopy(normalized)
    policy_snapshot = _normalize_policy_snapshot(payload.get("policy", payload.get("retrieval_policy", {})))
    payload.pop("retrieval_diagnostics", None)
    payload.pop("retrieval_source_bundle", None)
    payload.pop("query_fingerprint", None)
    payload.pop("source_bundle_fingerprint", None)
    payload["policy"] = copy.deepcopy(policy_snapshot)
    payload["retrieval_policy"] = copy.deepcopy(policy_snapshot)
    payload["audit_ref"] = payload.get("audit_ref")
    payload["retrieval_diagnostics"] = _build_retrieval_diagnostics_from_source_bundle(normalized)
    payload["retrieval_source_bundle"] = copy.deepcopy(normalized)
    return payload


def _build_retrieval_source_bundle_from_result_source(result: object) -> dict[str, object] | None:
    """Return a normalized source bundle from a result-like object when available."""

    for attr_name in ("retrieval_source_bundle", "source_bundle"):
        bundle_source = getattr(result, attr_name, None)
        if not callable(bundle_source):
            continue
        source_bundle = bundle_source()
        if isinstance(source_bundle, dict):
            return _build_retrieval_source_bundle_from_payload(
                {"retrieval_source_bundle": source_bundle}
            )
    return None


def build_retrieval_citation_bundle_from_result(
    result: RetrievalDownstreamPayloadSource | RetrievalCitationBundleSource | RetrievalSourceBundleSource,
) -> dict[str, object]:
    """Return the deterministic doc and excerpt citation snapshot for a result."""
    bundle_source = getattr(result, "citation_bundle", None)
    if callable(bundle_source):
        return copy.deepcopy(bundle_source())
    payload = build_retrieval_downstream_payload_from_result(result)
    return _build_retrieval_citation_bundle_from_payload(payload)


def build_retrieval_source_bundle_from_result(
    result: RetrievalDownstreamPayloadSource | RetrievalSourceBundleSource,
) -> dict[str, object]:
    """Return the deterministic retrieval source bundle for downstream engine flows."""
    source_bundle = _build_retrieval_source_bundle_from_result_source(result)
    if source_bundle is not None:
        return source_bundle
    payload = build_retrieval_downstream_payload_from_result(result)
    return _build_retrieval_source_bundle_from_payload(payload)


def build_retrieval_doc_bundle_from_result(
    result: RetrievalDownstreamPayloadSource | RetrievalDocBundleSource | RetrievalSourceBundleSource,
) -> dict[str, object]:
    """Return the deterministic doc-focused bundle for downstream engine flows."""

    bundle_source = getattr(result, "retrieval_doc_bundle", None)
    if callable(bundle_source):
        return _build_retrieval_doc_bundle_from_payload({"retrieval_doc_bundle": bundle_source()})
    source_bundle = _build_retrieval_source_bundle_from_result_source(result)
    if source_bundle is not None:
        return _build_retrieval_doc_bundle_from_payload(source_bundle)
    payload = build_retrieval_downstream_payload_from_result(result)
    return _build_retrieval_doc_bundle_from_payload(payload)


def build_retrieval_excerpt_bundle_from_result(
    result: RetrievalDownstreamPayloadSource | RetrievalExcerptBundleSource | RetrievalSourceBundleSource,
) -> dict[str, object]:
    """Return the deterministic excerpt-focused snapshot for downstream engine flows."""

    bundle_source = getattr(result, "retrieval_excerpt_bundle", None)
    if callable(bundle_source):
        return _build_retrieval_excerpt_bundle_from_payload({"retrieval_excerpt_bundle": bundle_source()})
    source_bundle = _build_retrieval_source_bundle_from_result_source(result)
    if source_bundle is not None:
        return _build_retrieval_excerpt_bundle_from_payload(source_bundle)
    payload = build_retrieval_downstream_payload_from_result(result)
    return _build_retrieval_excerpt_bundle_from_payload(payload)


def build_retrieval_context_bundle_from_result(
    result: (
        RetrievalDownstreamPayloadSource
        | RetrievalCitationBundleSource
        | RetrievalSourceBundleSource
        | RetrievalContextBundleSource
    ),
) -> dict[str, object]:
    """Return the deterministic retrieval context bundle for downstream engine flows."""

    context_source = getattr(result, "retrieval_context_bundle", None)
    if callable(context_source):
        context_bundle = context_source()
        if isinstance(context_bundle, dict):
            downstream_payload = context_bundle.get("retrieval_downstream_payload")
            if isinstance(downstream_payload, dict):
                downstream_payload = _backfill_downstream_payload_from_context_bundle(
                    copy.deepcopy(downstream_payload),
                    context_bundle,
                )
                return _build_retrieval_context_bundle_from_payload(downstream_payload)
            source_bundle = context_bundle.get("retrieval_source_bundle")
            if isinstance(source_bundle, dict):
                return _build_retrieval_context_bundle_from_source_bundle(copy.deepcopy(source_bundle))
    source_bundle = _build_retrieval_source_bundle_from_result_source(result)
    if source_bundle is not None:
        return _build_retrieval_context_bundle_from_source_bundle(copy.deepcopy(source_bundle))
    payload = build_retrieval_downstream_payload_from_result(result)
    return _build_retrieval_context_bundle_from_payload(payload)
