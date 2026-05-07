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


class RetrievalBasketPromotionBundleSource(Protocol):
    def retrieval_basket_promotion_bundle(self) -> dict[str, object]:
        """Return deterministic retrieval evidence items ready for context-basket promotion."""


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


def _normalize_int_like(value: object) -> object:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text:
            try:
                return int(text)
            except ValueError:
                return value
    return value


def _normalize_bool_like(value: object) -> object:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().casefold()
        if text in {"1", "true", "yes", "on"}:
            return True
        if text in {"0", "false", "no", "off"}:
            return False
    return value


def _normalize_bool_map(value: object) -> dict[str, bool]:
    if not isinstance(value, dict):
        return {}
    return {str(key): bool(item) for key, item in value.items()}


def _first_text_value(*values: object) -> str | None:
    for value in values:
        text = _normalize_optional_text(value)
        if text is not None:
            return text
    return None


def _stable_fingerprint(payload: object) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


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
    if "max_results" in constraints:
        constraints["max_results"] = _normalize_int_like(constraints.get("max_results"))
    constraints["doc_types"] = _normalize_list_like(constraints.get("doc_types"))
    constraints["date_range"] = _normalize_optional_list_like(constraints.get("date_range"))
    if "require_citations" in constraints:
        constraints["require_citations"] = _normalize_bool_like(constraints.get("require_citations"))
    constraints["section_hint"] = _normalize_optional_text(constraints.get("section_hint"))
    if "prefer_exact_matches" in constraints:
        constraints["prefer_exact_matches"] = _normalize_bool_like(constraints.get("prefer_exact_matches"))
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
    query_constraints = normalized.get("query_constraints")
    if isinstance(query_constraints, dict):
        normalized["query_constraints"] = _normalize_query_snapshot({"constraints": query_constraints})["constraints"]
        normalized.setdefault("query_constraints_fingerprint", _stable_fingerprint(normalized["query_constraints"]))
    normalized["query_date_range"] = _normalize_optional_list_like(normalized.get("query_date_range"))
    normalized["fts_shortlist_doc_ids"] = _normalize_list_like(normalized.get("fts_shortlist_doc_ids"))
    normalized["active_strategy_ids"] = _normalize_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_list_like(normalized.get("deferred_strategy_ids"))
    if "caches_used" in normalized:
        normalized["caches_used"] = _normalize_bool_map(normalized.get("caches_used"))
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
    if "caches_used" in normalized:
        normalized["caches_used"] = _normalize_bool_map(normalized.get("caches_used"))
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
    if "caches_used" in normalized:
        normalized["caches_used"] = _normalize_bool_map(normalized.get("caches_used"))
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
    if "caches_used" in normalized:
        normalized["caches_used"] = _normalize_bool_map(normalized.get("caches_used"))
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
    if "caches_used" in normalized:
        normalized["caches_used"] = _normalize_bool_map(normalized.get("caches_used"))
    retrieval_policy = normalized.get("retrieval_policy")
    if isinstance(retrieval_policy, dict):
        normalized["retrieval_policy"] = _normalize_policy_snapshot(retrieval_policy)
    if _is_missing_snapshot_value(normalized.get("retrieval_manifest_fingerprint")):
        normalized["retrieval_manifest_fingerprint"] = _stable_fingerprint(
            {
                key: value
                for key, value in normalized.items()
                if key != "retrieval_manifest_fingerprint"
            }
        )
    return normalized


def _normalize_retrieval_evidence_snapshot(evidence: dict[str, object]) -> dict[str, object]:
    normalized = copy.deepcopy(evidence)
    query_constraints = normalized.get("query_constraints")
    if isinstance(query_constraints, dict):
        normalized["query_constraints"] = _normalize_query_snapshot({"constraints": query_constraints})["constraints"]
        normalized.setdefault("query_constraints_fingerprint", _stable_fingerprint(normalized["query_constraints"]))
    normalized["active_strategy_ids"] = _normalize_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_list_like(normalized.get("deferred_strategy_ids"))
    if "caches_used" in normalized:
        normalized["caches_used"] = _normalize_bool_map(normalized.get("caches_used"))
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
    if _is_missing_snapshot_value(normalized.get("retrieval_evidence_fingerprint")):
        normalized["retrieval_evidence_fingerprint"] = _stable_fingerprint(
            {
                key: value
                for key, value in normalized.items()
                if key != "retrieval_evidence_fingerprint"
            }
        )
    return normalized


def _normalize_basket_promotion_bundle_snapshot(bundle: dict[str, object]) -> dict[str, object]:
    normalized = copy.deepcopy(bundle)
    if not isinstance(normalized, dict):
        return {}
    query_constraints = normalized.get("query_constraints")
    if not isinstance(query_constraints, dict):
        query = normalized.get("query")
        if isinstance(query, dict):
            query_constraints = query.get("constraints", {})
        else:
            query_constraints = {}
    if isinstance(query_constraints, dict):
        normalized["query_constraints"] = _normalize_query_snapshot({"constraints": query_constraints})[
            "constraints"
        ]
    else:
        normalized["query_constraints"] = {}
    normalized.setdefault("query_constraints_fingerprint", _stable_fingerprint(normalized["query_constraints"]))
    normalized["query_date_range"] = _normalize_optional_list_like(normalized.get("query_date_range"))
    normalized["active_strategy_ids"] = _normalize_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_list_like(normalized.get("deferred_strategy_ids"))
    if "caches_used" in normalized:
        normalized["caches_used"] = _normalize_bool_map(normalized.get("caches_used"))
    normalized["promotion_target"] = _first_text_value(normalized.get("promotion_target")) or "context_basket"
    promotion_items: list[object] = []
    for item in _normalize_list_like(normalized.get("promotion_items")):
        if not isinstance(item, dict):
            promotion_items.append(copy.deepcopy(item))
            continue
        normalized_item = copy.deepcopy(item)
        item_fallbacks = {
            "result_fingerprint": normalized.get("result_fingerprint"),
            "query_fingerprint": normalized.get("query_fingerprint"),
            "query_scope": normalized.get("query_scope"),
            "query_intent": normalized.get("query_intent"),
            "query_constraints": normalized.get("query_constraints"),
            "query_constraints_fingerprint": normalized.get("query_constraints_fingerprint"),
            "query_date_range": normalized.get("query_date_range"),
            "citation_status": normalized.get("citation_status"),
            "retrieval_evidence_fingerprint": normalized.get("retrieval_evidence_fingerprint"),
            "retrieval_manifest_fingerprint": normalized.get("retrieval_manifest_fingerprint"),
            "retrieval_backend": normalized.get("retrieval_backend"),
            "retrieval_mode": normalized.get("retrieval_mode"),
            "retrieval_policy": normalized.get("retrieval_policy"),
        }
        for key, fallback_value in item_fallbacks.items():
            if _is_missing_snapshot_value(normalized_item.get(key)) and not _is_missing_snapshot_value(fallback_value):
                normalized_item[key] = copy.deepcopy(fallback_value)
        if _is_missing_snapshot_value(normalized_item.get("retrieval_source_strategy")):
            source_strategy = normalized_item.get("source_strategy")
            if not _is_missing_snapshot_value(source_strategy):
                normalized_item["retrieval_source_strategy"] = copy.deepcopy(source_strategy)
        item_policy = normalized_item.get("retrieval_policy")
        if isinstance(item_policy, dict):
            normalized_item["retrieval_policy"] = _normalize_policy_snapshot(item_policy)
        item_constraints = normalized_item.get("query_constraints")
        if isinstance(item_constraints, dict):
            normalized_item["query_constraints"] = _normalize_query_snapshot({"constraints": item_constraints})[
                "constraints"
            ]
        elif not _is_missing_snapshot_value(normalized.get("query_constraints")):
            normalized_item["query_constraints"] = copy.deepcopy(normalized["query_constraints"])
        if isinstance(normalized_item.get("query_constraints"), dict):
            normalized_item["query_constraints_fingerprint"] = _stable_fingerprint(
                normalized_item["query_constraints"]
            )
        normalized_item["query_date_range"] = _normalize_optional_list_like(
            normalized_item.get("query_date_range")
        )
        if "matched_terms" in normalized_item:
            normalized_item["matched_terms"] = _normalize_list_like(
                normalized_item.get("matched_terms")
            )
        if _is_missing_snapshot_value(normalized_item.get("promotion_item_fingerprint")):
            normalized_item["promotion_item_fingerprint"] = _stable_fingerprint(
                {
                    key: value
                    for key, value in normalized_item.items()
                    if key != "promotion_item_fingerprint"
                }
            )
        promotion_items.append(normalized_item)
    normalized["promotion_items"] = promotion_items
    normalized["promotion_item_count"] = len(normalized["promotion_items"])
    if _is_missing_snapshot_value(normalized.get("promotion_bundle_fingerprint")):
        normalized["promotion_bundle_fingerprint"] = _stable_fingerprint(
            {
                "promotion_target": normalized.get("promotion_target"),
                "result_fingerprint": normalized.get("result_fingerprint"),
                "query_fingerprint": normalized.get("query_fingerprint"),
                "retrieval_evidence_fingerprint": normalized.get("retrieval_evidence_fingerprint"),
                "promotion_item_fingerprints": [
                    item.get("promotion_item_fingerprint")
                    for item in promotion_items
                    if isinstance(item, dict)
                ],
            }
        )
    retrieval_policy = normalized.get("retrieval_policy")
    if isinstance(retrieval_policy, dict):
        normalized["retrieval_policy"] = _normalize_policy_snapshot(retrieval_policy)
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
    normalized["query_constraints"] = copy.deepcopy(normalized["query"].get("constraints", {}))
    normalized.setdefault("query_constraints_fingerprint", _stable_fingerprint(normalized["query_constraints"]))
    normalized["policy"] = _normalize_policy_snapshot(
        normalized.get("policy", normalized.get("retrieval_policy", {}))
    )
    if "caches_used" in normalized:
        normalized["caches_used"] = _normalize_bool_map(normalized.get("caches_used"))
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
    normalized["retrieval_basket_promotion_bundle"] = _build_retrieval_basket_promotion_bundle_from_payload(
        normalized
    )
    normalized["doc_hits"] = _normalize_list_like(normalized.get("doc_hits", []))
    normalized["excerpt_hits"] = _normalize_list_like(normalized.get("excerpt_hits", []))
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

    retrieval_evidence = normalized.get("retrieval_evidence", {})
    if not isinstance(retrieval_evidence, dict):
        retrieval_evidence = {}
    retrieval_evidence = _normalize_retrieval_evidence_snapshot(retrieval_evidence)
    retrieval_evidence_fingerprint = _first_text_value(
        normalized.get("retrieval_evidence_fingerprint"),
        retrieval_evidence.get("retrieval_evidence_fingerprint"),
        retrieval_summary.get("retrieval_evidence_fingerprint"),
        retrieval_provenance.get("retrieval_evidence_fingerprint"),
    )
    if retrieval_evidence_fingerprint is not None:
        normalized["retrieval_evidence_fingerprint"] = retrieval_evidence_fingerprint

    retrieval_manifest = normalized.get("retrieval_manifest", {})
    if not isinstance(retrieval_manifest, dict):
        retrieval_manifest = {}
    retrieval_manifest = _normalize_retrieval_manifest_snapshot(retrieval_manifest)
    retrieval_manifest_fingerprint = _first_text_value(
        normalized.get("retrieval_manifest_fingerprint"),
        retrieval_manifest.get("retrieval_manifest_fingerprint"),
        retrieval_evidence.get("retrieval_manifest_fingerprint"),
        retrieval_summary.get("retrieval_manifest_fingerprint"),
        retrieval_provenance.get("retrieval_manifest_fingerprint"),
    )
    if retrieval_manifest_fingerprint is not None:
        normalized["retrieval_manifest_fingerprint"] = retrieval_manifest_fingerprint

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
        return _normalize_citation_bundle_snapshot(citation_bundle)

    query = payload.get("query", {})
    if not isinstance(query, dict):
        query = {}
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
        "query_fingerprint": provenance.get(
            "query_fingerprint",
            summary.get("query_fingerprint", diagnostics.get("query_fingerprint")),
        ),
        "result_fingerprint": provenance.get(
            "result_fingerprint",
            summary.get("result_fingerprint", diagnostics.get("result_fingerprint")),
        ),
        "query_scope": query_scope,
        "query_intent": query_intent,
        "query_constraints": copy.deepcopy(query_constraints),
        "query_constraints_fingerprint": provenance.get(
            "query_constraints_fingerprint",
            _stable_fingerprint(query_constraints),
        ),
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
        "retrieval_evidence_fingerprint": payload.get("retrieval_evidence_fingerprint"),
        "retrieval_provenance": copy.deepcopy(payload.get("retrieval_provenance", {})),
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
        "retrieval_basket_promotion_bundle": context_bundle.get("retrieval_basket_promotion_bundle"),
        "retrieval_source_bundle": context_bundle.get("retrieval_source_bundle"),
        "retrieval_evidence": context_bundle.get("retrieval_evidence"),
    }
    return _backfill_sparse_snapshot(
        merged,
        {key: value for key, value in context_backfill.items() if value is not None},
    )


def _build_retrieval_context_bundle_from_source_bundle(source_bundle: dict[str, object]) -> dict[str, object]:
    """Return the deterministic retrieval context bundle from a source-bundle snapshot."""

    source_bundle = _normalize_retrieval_source_bundle_snapshot(source_bundle)
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
    retrieval_basket_promotion_bundle = source_bundle.get("retrieval_basket_promotion_bundle", {})
    if not isinstance(retrieval_basket_promotion_bundle, dict):
        retrieval_basket_promotion_bundle = _build_retrieval_basket_promotion_bundle_from_payload(source_bundle)
    return {
        # Source-bundle-only reconstruction keeps the top-level context auditless.
        "audit_ref": None,
        "result_fingerprint": source_bundle.get("result_fingerprint"),
        "source_bundle_fingerprint": source_bundle.get("source_bundle_fingerprint"),
        "retrieval_manifest_fingerprint": source_bundle.get("retrieval_manifest_fingerprint"),
        "retrieval_downstream_payload": copy.deepcopy(source_bundle),
        "retrieval_citation_bundle": copy.deepcopy(retrieval_citation_bundle),
        "retrieval_doc_bundle": copy.deepcopy(retrieval_doc_bundle),
        "retrieval_excerpt_bundle": copy.deepcopy(retrieval_excerpt_bundle),
        "retrieval_provenance": copy.deepcopy(retrieval_provenance),
        "retrieval_basket_promotion_bundle": copy.deepcopy(retrieval_basket_promotion_bundle),
        "retrieval_source_bundle": copy.deepcopy(source_bundle),
        "retrieval_evidence": copy.deepcopy(source_bundle.get("retrieval_evidence", {})),
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
    query_constraints = query.get("constraints", {})
    if not isinstance(query_constraints, dict):
        query_constraints = {}
    normalized_query_constraints = _normalize_query_snapshot({"constraints": query_constraints})["constraints"]
    citation_bundle = payload.get("retrieval_citation_bundle", {})
    if not isinstance(citation_bundle, dict):
        citation_bundle = _build_retrieval_citation_bundle_from_payload(payload)
    evidence = payload.get("retrieval_evidence", {})
    if not isinstance(evidence, dict):
        evidence = {}
    evidence = _normalize_retrieval_evidence_snapshot(evidence)
    retrieval_manifest = payload.get("retrieval_manifest", {})
    if not isinstance(retrieval_manifest, dict):
        retrieval_manifest = {}
    retrieval_manifest = _normalize_retrieval_manifest_snapshot(retrieval_manifest)
    query_date_range = _normalize_optional_list_like(
        query_constraints.get(
            "date_range",
            provenance.get("query_date_range", summary.get("query_date_range", diagnostics.get("date_range"))),
        )
    )
    return {
        "result_fingerprint": payload.get("result_fingerprint"),
        "query_fingerprint": payload.get(
            "query_fingerprint",
            provenance.get("query_fingerprint", summary.get("query_fingerprint", diagnostics.get("query_fingerprint"))),
        ),
        "query_scope": query.get(
            "scope",
            provenance.get("query_scope", summary.get("query_scope", diagnostics.get("query_scope"))),
        ),
        "query_intent": query.get(
            "intent",
            provenance.get("query_intent", summary.get("query_intent", diagnostics.get("query_intent"))),
        ),
        "query_constraints": normalized_query_constraints,
        "query_constraints_fingerprint": _stable_fingerprint(normalized_query_constraints),
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
        "retrieval_evidence_fingerprint": (
            evidence.get("retrieval_evidence_fingerprint")
            or provenance.get("retrieval_evidence_fingerprint")
            or summary.get("retrieval_evidence_fingerprint")
            or diagnostics.get("retrieval_evidence_fingerprint")
        ),
        "retrieval_manifest_fingerprint": (
            evidence.get("retrieval_manifest_fingerprint")
            or provenance.get("retrieval_manifest_fingerprint")
            or summary.get("retrieval_manifest_fingerprint")
            or diagnostics.get("retrieval_manifest_fingerprint")
            or retrieval_manifest.get("retrieval_manifest_fingerprint")
        ),
        "retrieval_citation_bundle": copy.deepcopy(citation_bundle),
        "retrieval_manifest": copy.deepcopy(retrieval_manifest),
        "retrieval_provenance": copy.deepcopy(provenance),
        "retrieval_evidence": copy.deepcopy(evidence),
    }


def _build_retrieval_doc_bundle_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return the deterministic doc-focused bundle from a downstream payload snapshot."""

    doc_bundle = payload.get("retrieval_doc_bundle")
    if isinstance(doc_bundle, dict):
        return _normalize_doc_bundle_snapshot(doc_bundle)
    bundle_context = _build_retrieval_bundle_context_from_payload(payload)
    provenance = bundle_context["retrieval_provenance"]
    doc_hits = _normalize_list_like(payload.get("doc_hits", []))
    doc_citations: list[object] = []
    if isinstance(provenance, dict):
        doc_citations = _normalize_list_like(provenance.get("doc_citations", []))
    return _normalize_doc_bundle_snapshot({
        **bundle_context,
        "doc_count": len(doc_hits),
        "doc_hits": doc_hits,
        "doc_citations": doc_citations,
    })


def _build_retrieval_excerpt_bundle_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return the deterministic excerpt-focused bundle from a downstream payload snapshot."""

    excerpt_bundle = payload.get("retrieval_excerpt_bundle")
    if isinstance(excerpt_bundle, dict):
        return _normalize_excerpt_bundle_snapshot(excerpt_bundle)
    bundle_context = _build_retrieval_bundle_context_from_payload(payload)
    provenance = bundle_context["retrieval_provenance"]
    excerpt_hits = _normalize_list_like(payload.get("excerpt_hits", []))
    excerpt_citations: list[object] = []
    if isinstance(provenance, dict):
        excerpt_citations = _normalize_list_like(provenance.get("excerpt_citations", []))
    return _normalize_excerpt_bundle_snapshot({
        **bundle_context,
        "doc_count": len(_normalize_list_like(payload.get("doc_hits", []))),
        "excerpt_count": len(excerpt_hits) if excerpt_hits else len(excerpt_citations),
        "excerpt_hits": excerpt_hits,
        "excerpt_citations": excerpt_citations,
    })


def _build_retrieval_basket_promotion_bundle_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return deterministic FTS evidence items ready for context-basket promotion."""

    basket_bundle = payload.get("retrieval_basket_promotion_bundle")
    if isinstance(basket_bundle, dict):
        return _normalize_basket_promotion_bundle_snapshot(basket_bundle)
    bundle_context = _build_retrieval_bundle_context_from_payload(payload)
    promotion_items: list[dict[str, object]] = []
    for hit in _normalize_list_like(payload.get("excerpt_hits", [])):
        if not isinstance(hit, dict):
            continue
        excerpt_id = hit.get("excerpt_id")
        if excerpt_id is None:
            continue
        provenance = hit.get("provenance", {})
        if not isinstance(provenance, dict):
            provenance = {}
        promotion_item = {
            "doc_id": hit.get("doc_id"),
            "excerpt_id": excerpt_id,
            "title_hint": hit.get("title_hint"),
            "excerpt_text": hit.get("excerpt_text"),
            "span": copy.deepcopy(hit.get("span", provenance.get("span", {}))),
            "score": hit.get("score"),
            "rank": provenance.get("rank", hit.get("rank")),
            "source_strategy": hit.get("source_strategy", provenance.get("source_strategy")),
            "retrieval_source_strategy": hit.get(
                "retrieval_source_strategy",
                provenance.get(
                    "retrieval_source_strategy",
                    hit.get("source_strategy", provenance.get("source_strategy")),
                ),
            ),
            "result_fingerprint": hit.get(
                "result_fingerprint",
                provenance.get("result_fingerprint", bundle_context["result_fingerprint"]),
            ),
            "query_fingerprint": hit.get(
                "query_fingerprint",
                provenance.get("query_fingerprint", bundle_context["query_fingerprint"]),
            ),
            "query_scope": hit.get("query_scope", provenance.get("query_scope", bundle_context["query_scope"])),
            "query_intent": hit.get("query_intent", provenance.get("query_intent", bundle_context["query_intent"])),
            "query_constraints": copy.deepcopy(
                hit.get(
                    "query_constraints",
                    provenance.get("query_constraints", bundle_context["query_constraints"]),
                )
            ),
            "query_constraints_fingerprint": hit.get(
                "query_constraints_fingerprint",
                provenance.get(
                    "query_constraints_fingerprint",
                    bundle_context["query_constraints_fingerprint"],
                ),
            ),
            "query_date_range": copy.deepcopy(
                hit.get(
                    "query_date_range",
                    provenance.get("query_date_range", bundle_context["query_date_range"]),
                )
            ),
            "citation_status": copy.deepcopy(
                hit.get(
                    "citation_status",
                    provenance.get("citation_status", bundle_context["citation_status"]),
                )
            ),
            "retrieval_evidence_fingerprint": hit.get(
                "retrieval_evidence_fingerprint",
                provenance.get(
                    "retrieval_evidence_fingerprint",
                    bundle_context["retrieval_evidence_fingerprint"],
                ),
            ),
            "retrieval_manifest_fingerprint": hit.get(
                "retrieval_manifest_fingerprint",
                provenance.get(
                    "retrieval_manifest_fingerprint",
                    bundle_context["retrieval_manifest_fingerprint"],
                ),
            ),
            "retrieval_backend": hit.get("retrieval_backend", provenance.get("retrieval_backend")),
            "retrieval_mode": hit.get("retrieval_mode", provenance.get("retrieval_mode")),
            "retrieval_policy": copy.deepcopy(
                hit.get(
                    "retrieval_policy",
                    provenance.get("retrieval_policy", bundle_context.get("retrieval_policy")),
                )
            ),
            "source_hash": hit.get("source_hash", provenance.get("source_hash")),
            "doc_type": hit.get("doc_type", provenance.get("doc_type")),
            "doc_fingerprint": hit.get("doc_fingerprint", provenance.get("doc_fingerprint")),
            "doc_identity_fingerprint": hit.get(
                "doc_identity_fingerprint",
                provenance.get("doc_identity_fingerprint"),
            ),
            "excerpt_fingerprint": hit.get("excerpt_fingerprint", provenance.get("excerpt_fingerprint")),
            "excerpt_text_hash": hit.get(
                "excerpt_text_hash",
                provenance.get("excerpt_text_hash", provenance.get("hash")),
            ),
            "matched_terms": copy.deepcopy(hit.get("matched_terms", provenance.get("matched_terms"))),
            "match_count": hit.get("match_count", provenance.get("match_count")),
        }
        promotion_item["promotion_item_fingerprint"] = _stable_fingerprint(promotion_item)
        promotion_items.append(promotion_item)
    return _normalize_basket_promotion_bundle_snapshot(
        {
            **bundle_context,
            "promotion_target": "context_basket",
            "promotion_item_count": len(promotion_items),
            "promotion_items": promotion_items,
        }
    )


def _build_retrieval_context_bundle_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return the deterministic retrieval context bundle from a downstream payload snapshot."""

    source_bundle = _build_retrieval_source_bundle_from_payload(payload)
    return {
        "audit_ref": payload.get("audit_ref"),
        "result_fingerprint": payload.get("result_fingerprint"),
        "source_bundle_fingerprint": payload.get(
            "source_bundle_fingerprint",
            source_bundle.get("source_bundle_fingerprint"),
        ),
        "retrieval_manifest_fingerprint": source_bundle.get("retrieval_manifest_fingerprint"),
        "retrieval_downstream_payload": copy.deepcopy(payload),
        "retrieval_citation_bundle": _build_retrieval_citation_bundle_from_payload(payload),
        "retrieval_doc_bundle": _build_retrieval_doc_bundle_from_payload(payload),
        "retrieval_excerpt_bundle": _build_retrieval_excerpt_bundle_from_payload(payload),
        "retrieval_provenance": _build_retrieval_provenance_from_payload(payload),
        "retrieval_basket_promotion_bundle": _build_retrieval_basket_promotion_bundle_from_payload(payload),
        "retrieval_source_bundle": source_bundle,
        "retrieval_evidence": copy.deepcopy(payload.get("retrieval_evidence", {})),
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
    caches_used = _normalize_bool_map(citation_bundle.get("caches_used", normalized.get("caches_used", {})))
    if not caches_used:
        caches_used = {strategy_id: False for strategy_id in strategies_used}
    retrieval_evidence = normalized.get("retrieval_evidence", {})
    if not isinstance(retrieval_evidence, dict):
        retrieval_evidence = {}
    fts_shortlist_query_fingerprint = _first_text_value(
        normalized.get("fts_shortlist_query_fingerprint"),
        citation_bundle.get("fts_shortlist_query_fingerprint"),
        retrieval_evidence.get("fts_shortlist_query_fingerprint"),
    )

    diagnostics = {
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
        "query_fingerprint": citation_bundle.get(
            "query_fingerprint",
            normalized.get("query_fingerprint"),
        ),
        "query_constraints_fingerprint": citation_bundle.get(
            "query_constraints_fingerprint",
            _stable_fingerprint(query_constraints),
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
        "caches_used": caches_used,
        "elapsed_ms_total": 0,
        "doc_hits_count": citation_bundle.get("doc_count", len(_normalize_list_like(normalized.get("doc_hits", [])))),
        "excerpt_hits_count": citation_bundle.get("excerpt_count", len(_normalize_list_like(normalized.get("excerpt_hits", [])))),
        "doc_hits_fingerprint": citation_bundle.get("doc_hits_fingerprint"),
        "excerpt_hits_fingerprint": citation_bundle.get("excerpt_hits_fingerprint"),
        "retrieval_manifest_fingerprint": normalized.get("retrieval_manifest_fingerprint"),
        "citation_status": copy.deepcopy(
            citation_bundle.get("citation_status", normalized.get("citation_status", {}))
        ),
        "retrieval_manifest": copy.deepcopy(normalized.get("retrieval_manifest", {})),
        "retrieval_evidence": copy.deepcopy(retrieval_evidence),
        "retrieval_evidence_fingerprint": retrieval_evidence.get("retrieval_evidence_fingerprint"),
        "result_fingerprint": citation_bundle.get(
            "result_fingerprint",
            normalized.get("result_fingerprint"),
        ),
    }
    if fts_shortlist_query_fingerprint is not None:
        diagnostics["fts_shortlist_query_fingerprint"] = fts_shortlist_query_fingerprint
    return diagnostics


def _build_retrieval_provenance_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return the deterministic retrieval provenance snapshot from a downstream payload snapshot."""

    provenance = payload.get("retrieval_provenance")
    if isinstance(provenance, dict):
        normalized = copy.deepcopy(provenance)
    else:
        normalized = {}
    summary = payload.get("retrieval_summary", {})
    diagnostics = payload.get("retrieval_diagnostics", {})
    evidence = payload.get("retrieval_evidence", {})
    if not isinstance(summary, dict):
        summary = {}
    if not isinstance(diagnostics, dict):
        diagnostics = {}
    if not isinstance(evidence, dict):
        evidence = {}
    evidence = _normalize_retrieval_evidence_snapshot(evidence)
    query_date_range = _normalize_optional_list_like(normalized.get("query_date_range"))
    if "query_fingerprint" not in normalized:
        normalized["query_fingerprint"] = summary.get("query_fingerprint", diagnostics.get("query_fingerprint"))
    if "query_scope" not in normalized:
        normalized["query_scope"] = summary.get("query_scope", diagnostics.get("query_scope"))
    if "query_intent" not in normalized:
        normalized["query_intent"] = summary.get("query_intent", diagnostics.get("query_intent"))
    if "query_constraints" not in normalized:
        query = payload.get("query", {})
        if isinstance(query, dict):
            normalized["query_constraints"] = _normalize_query_snapshot(query).get("constraints", {})
        else:
            normalized["query_constraints"] = {}
    elif isinstance(normalized["query_constraints"], dict):
        normalized["query_constraints"] = _normalize_query_snapshot({"constraints": normalized["query_constraints"]})[
            "constraints"
        ]
    if "query_constraints_fingerprint" not in normalized:
        normalized["query_constraints_fingerprint"] = _stable_fingerprint(normalized["query_constraints"])
    if "query_date_range" not in normalized:
        normalized["query_date_range"] = _normalize_optional_list_like(
            summary.get("query_date_range", diagnostics.get("date_range"))
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
    if "caches_used" in normalized:
        normalized["caches_used"] = _normalize_bool_map(normalized["caches_used"])
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
    if "retrieval_evidence_fingerprint" not in normalized:
        normalized["retrieval_evidence_fingerprint"] = (
            evidence.get("retrieval_evidence_fingerprint")
            or summary.get("retrieval_evidence_fingerprint")
            or diagnostics.get("retrieval_evidence_fingerprint")
        )
    if "retrieval_manifest_fingerprint" not in normalized:
        normalized["retrieval_manifest_fingerprint"] = (
            evidence.get("retrieval_manifest_fingerprint")
            or summary.get("retrieval_manifest_fingerprint")
            or diagnostics.get("retrieval_manifest_fingerprint")
        )
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
    else:
        normalized["doc_citations"] = _normalize_list_like(normalized["doc_citations"])
    if "excerpt_citations" not in normalized:
        normalized["excerpt_citations"] = copy.deepcopy(excerpt_citations)
    else:
        normalized["excerpt_citations"] = _normalize_list_like(normalized["excerpt_citations"])
    if "primary_doc_id" not in normalized and doc_citations:
        first_doc_citation = doc_citations[0]
        if isinstance(first_doc_citation, dict):
            normalized["primary_doc_id"] = first_doc_citation.get("doc_id")
            if "primary_doc_fingerprint" not in normalized:
                normalized["primary_doc_fingerprint"] = first_doc_citation.get("doc_fingerprint")
            if "primary_doc_identity_fingerprint" not in normalized:
                normalized["primary_doc_identity_fingerprint"] = first_doc_citation.get("doc_identity_fingerprint")
    if "primary_excerpt_id" not in normalized and excerpt_citations:
        first_excerpt_citation = excerpt_citations[0]
        if isinstance(first_excerpt_citation, dict):
            normalized["primary_excerpt_id"] = first_excerpt_citation.get("excerpt_id")
            if "primary_excerpt_fingerprint" not in normalized:
                normalized["primary_excerpt_fingerprint"] = first_excerpt_citation.get("excerpt_fingerprint")
            if "primary_excerpt_text_hash" not in normalized:
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
    retrieval_basket_promotion_bundle: dict[str, object]
    retrieval_manifest_fingerprint: str | None
    source_bundle_fingerprint: str
    retrieval_source_bundle: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        policy = copy.deepcopy(self.policy)
        diagnostics = copy.deepcopy(self.retrieval_diagnostics)
        manifest = copy.deepcopy(self.retrieval_manifest)
        evidence = copy.deepcopy(self.retrieval_evidence)
        provenance = copy.deepcopy(self.retrieval_provenance)
        basket_promotion_bundle = copy.deepcopy(self.retrieval_basket_promotion_bundle)
        summary = copy.deepcopy(self.retrieval_summary)
        source_bundle = copy.deepcopy(self.retrieval_source_bundle)
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
            "retrieval_basket_promotion_bundle": basket_promotion_bundle,
            "retrieval_manifest_fingerprint": self.retrieval_manifest_fingerprint,
            "source_bundle_fingerprint": self.source_bundle_fingerprint,
            "retrieval_source_bundle": source_bundle,
        }


def build_retrieval_provenance_from_result(
    result: RetrievalDownstreamPayloadSource | RetrievalProvenanceBundleSource | RetrievalSourceBundleSource,
) -> dict[str, object]:
    """Return the deterministic retrieval provenance snapshot for a result."""

    provenance_source = getattr(result, "retrieval_provenance_bundle", None)
    if callable(provenance_source):
        return _build_retrieval_provenance_from_payload({"retrieval_provenance": provenance_source()})
    source_bundle = _build_retrieval_source_bundle_from_result_source(result)
    if source_bundle is not None:
        return _build_retrieval_provenance_from_payload(source_bundle)
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
    retrieval_basket_promotion_bundle: dict[str, object],
    retrieval_manifest_fingerprint: str | None,
    source_bundle_fingerprint: str,
    retrieval_source_bundle: dict[str, object],
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
        retrieval_basket_promotion_bundle=retrieval_basket_promotion_bundle,
        retrieval_manifest_fingerprint=retrieval_manifest_fingerprint,
        source_bundle_fingerprint=source_bundle_fingerprint,
        retrieval_source_bundle=retrieval_source_bundle,
    ).as_dict()


def build_retrieval_downstream_payload_from_result(
    result: RetrievalDownstreamPayloadSource | RetrievalContextBundleSource | RetrievalSourceBundleSource,
) -> dict[str, object]:
    """Return a snapshot-safe copy of a retrieval result payload.

    Engine callers use this helper when they want the canonical downstream
    retrieval contract without holding onto the mutable service object that
    produced it.
    """
    payload_source = getattr(result, "as_downstream_payload", None)
    if callable(payload_source):
        payload = copy.deepcopy(payload_source())
        context_source = getattr(result, "retrieval_context_bundle", None)
        if callable(context_source):
            context_bundle = context_source()
            if isinstance(context_bundle, dict):
                payload = _backfill_downstream_payload_from_context_bundle(payload, context_bundle)
        source_bundle = _build_retrieval_source_bundle_from_result_source(result)
        if source_bundle is not None:
            payload = _backfill_sparse_snapshot(
                payload,
                _build_retrieval_downstream_payload_from_source_bundle(source_bundle),
            )
        return payload
    payload_source = getattr(result, "as_dict", None)
    if callable(payload_source):
        payload = copy.deepcopy(payload_source())
        context_source = getattr(result, "retrieval_context_bundle", None)
        if callable(context_source):
            context_bundle = context_source()
            if isinstance(context_bundle, dict):
                payload = _backfill_downstream_payload_from_context_bundle(payload, context_bundle)
        source_bundle = _build_retrieval_source_bundle_from_result_source(result)
        if source_bundle is not None:
            payload = _backfill_sparse_snapshot(
                payload,
                _build_retrieval_downstream_payload_from_source_bundle(source_bundle),
            )
        return payload
    payload_source = getattr(result, "to_downstream_payload", None)
    if callable(payload_source):
        payload = copy.deepcopy(payload_source())
        context_source = getattr(result, "retrieval_context_bundle", None)
        if callable(context_source):
            context_bundle = context_source()
            if isinstance(context_bundle, dict):
                payload = _backfill_downstream_payload_from_context_bundle(payload, context_bundle)
        source_bundle = _build_retrieval_source_bundle_from_result_source(result)
        if source_bundle is not None:
            payload = _backfill_sparse_snapshot(
                payload,
                _build_retrieval_downstream_payload_from_source_bundle(source_bundle),
            )
        return payload
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
    raise AttributeError(
        "result must expose a downstream payload, context bundle, or source bundle"
    )


def _build_retrieval_downstream_payload_from_source_bundle(
    source_bundle: dict[str, object],
) -> dict[str, object]:
    normalized = _normalize_retrieval_source_bundle_snapshot(source_bundle)
    payload = copy.deepcopy(normalized)
    policy_snapshot = _normalize_policy_snapshot(payload.get("policy", payload.get("retrieval_policy", {})))
    payload.pop("retrieval_diagnostics", None)
    payload.pop("retrieval_source_bundle", None)
    payload.pop("query_fingerprint", None)
    payload.pop("query_constraints", None)
    payload.pop("query_constraints_fingerprint", None)
    payload.pop("retrieval_evidence_fingerprint", None)
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
        return _build_retrieval_citation_bundle_from_payload({"retrieval_citation_bundle": bundle_source()})
    source_bundle = _build_retrieval_source_bundle_from_result_source(result)
    if source_bundle is not None:
        return _build_retrieval_citation_bundle_from_payload(source_bundle)
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
        # Normalize the direct bundle snapshot so compatibility sources still
        # round-trip through the canonical doc bundle shape.
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
        # Normalize the direct bundle snapshot so compatibility sources still
        # round-trip through the canonical excerpt bundle shape.
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
        return copy.deepcopy(context_bundle)
    source_bundle = _build_retrieval_source_bundle_from_result_source(result)
    if source_bundle is not None:
        return _build_retrieval_context_bundle_from_source_bundle(copy.deepcopy(source_bundle))
    payload = build_retrieval_downstream_payload_from_result(result)
    return _build_retrieval_context_bundle_from_payload(payload)
