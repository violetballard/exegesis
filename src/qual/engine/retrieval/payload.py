from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime
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
        return [copy.deepcopy(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return _normalize_unordered_iterable(value)
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, bytearray, Mapping)):
        return [copy.deepcopy(item) for item in value]
    if value is None:
        return []
    return [copy.deepcopy(value)]


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


def _normalize_optional_casefold_text(value: object) -> str | None:
    text = _normalize_optional_text(value)
    if text is None:
        return None
    return text.casefold()


def _normalize_span_snapshot(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    char_range = value.get("char_range")
    if not isinstance(char_range, dict):
        return None
    if "start" not in char_range or "end" not in char_range:
        return None
    start_raw = char_range["start"]
    end_raw = char_range["end"]
    if isinstance(start_raw, bool) or isinstance(end_raw, bool):
        return None
    try:
        start = int(start_raw)
        end = int(end_raw)
    except (TypeError, ValueError):
        return None
    if start > end:
        start, end = end, start
    return {
        "char_range": {
            "start": start,
            "end": end,
        }
    }


def _normalize_optional_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value == 0:
            return False
        if value == 1:
            return True
        return None
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
    return None


def _normalize_optional_int(value: object) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_optional_float(value: object) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_text_list_like(value: object) -> list[str]:
    raw_items = _normalize_list_like(value)
    normalized: list[str] = []
    for item in raw_items:
        text = _normalize_optional_text(item)
        if text is not None:
            normalized.append(text)
    if isinstance(value, (list, tuple)):
        return list(dict.fromkeys(normalized))
    return sorted(dict.fromkeys(normalized))


def _normalize_query_text(value: object) -> str | None:
    text = _normalize_optional_text(value)
    if text is None:
        return None
    return " ".join(text.casefold().split())


def _normalize_query_confidentiality_profile(value: object) -> str | None:
    text = _normalize_optional_text(value)
    if text is None:
        return None
    return text.casefold()


def _normalize_query_scope(value: object) -> str | None:
    text = _normalize_optional_text(value)
    if text is None:
        return None
    if text.casefold() == "vault":
        return "vault"
    prefix, separator, remainder = text.partition(":")
    normalized_prefix = prefix.strip().casefold()
    if separator and normalized_prefix in {"doc", "collection", "section"}:
        normalized_remainder = remainder.strip()
        if not normalized_remainder:
            return None
        return f"{normalized_prefix}:{normalized_remainder}"
    return text


def _normalize_query_intent(value: object) -> str | None:
    text = _normalize_optional_text(value)
    if text is None:
        return None
    return text.casefold()


def _parse_query_date_value(value: str) -> date | None:
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None


def _normalize_query_doc_types(value: object) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for item in _normalize_list_like(value):
        text = _normalize_optional_text(item)
        if text is None:
            continue
        canonical = text.casefold()
        if canonical in seen:
            continue
        seen.add(canonical)
        normalized.append(canonical)
    return sorted(normalized)


def _normalize_query_date_range(value: object) -> list[str] | None:
    normalized: list[str] = []
    for item in _normalize_list_like(value):
        text = _normalize_optional_text(item)
        if text is not None:
            normalized.append(text)
    if not normalized:
        return None
    if len(normalized) != 2:
        return normalized
    start_raw, end_raw = normalized
    start_date = _parse_query_date_value(start_raw)
    end_date = _parse_query_date_value(end_raw)
    normalized_start = start_date.isoformat() if start_date is not None else start_raw
    normalized_end = end_date.isoformat() if end_date is not None else end_raw
    if start_date is not None and end_date is not None and start_date > end_date:
        return [normalized_end, normalized_start]
    return [normalized_start, normalized_end]


def _first_text_value(*values: object) -> str | None:
    for value in values:
        text = _normalize_optional_text(value)
        if text is not None:
            return text
    return None


def _first_non_none_value(*values: object) -> object | None:
    for value in values:
        if value is not None:
            return copy.deepcopy(value)
    return None


def _first_dict_value(*values: object) -> dict[str, object] | None:
    empty_dict: dict[str, object] | None = None
    for value in values:
        if isinstance(value, dict):
            snapshot = copy.deepcopy(value)
            if snapshot:
                return snapshot
            if empty_dict is None:
                empty_dict = snapshot
    return empty_dict


def _stable_fingerprint(payload: object) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _stable_sort_key(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _normalize_unordered_iterable(value: set[object] | frozenset[object]) -> list[object]:
    items = [copy.deepcopy(item) for item in value]
    return sorted(items, key=_stable_sort_key)


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
    has_query_context = any(
        key in normalized
        for key in (
            "query_text",
            "scope",
            "intent",
            "confidentiality_profile",
            "constraints",
        )
    )
    normalized_query_text = _normalize_query_text(normalized.get("query_text"))
    if normalized_query_text is not None:
        normalized["query_text"] = normalized_query_text
    confidentiality_profile = _normalize_query_confidentiality_profile(
        normalized.get("confidentiality_profile")
    )
    if confidentiality_profile is not None:
        normalized["confidentiality_profile"] = confidentiality_profile
    elif has_query_context:
        # Sparse query snapshots should still fail closed for confidentiality so
        # downstream rehydration never assumes a less restrictive profile.
        normalized["confidentiality_profile"] = "confidential"
    normalized_scope = _normalize_query_scope(normalized.get("scope"))
    if normalized_scope is not None:
        normalized["scope"] = normalized_scope
    normalized_intent = _normalize_query_intent(normalized.get("intent"))
    if normalized_intent is not None:
        normalized["intent"] = normalized_intent
    constraints = normalized.get("constraints", {})
    if not isinstance(constraints, dict):
        constraints = {}
    else:
        constraints = copy.deepcopy(constraints)
    max_results = _normalize_optional_int(constraints.get("max_results"))
    if max_results is not None:
        constraints["max_results"] = max_results
    else:
        constraints["max_results"] = 10
    constraints["doc_types"] = _normalize_query_doc_types(constraints.get("doc_types"))
    constraints["date_range"] = _normalize_query_date_range(constraints.get("date_range"))
    constraints["section_hint"] = _normalize_optional_text(constraints.get("section_hint"))
    require_citations = _normalize_optional_bool(constraints.get("require_citations"))
    if require_citations is not None:
        constraints["require_citations"] = require_citations
    else:
        constraints["require_citations"] = False
    prefer_exact_matches = _normalize_optional_bool(constraints.get("prefer_exact_matches"))
    if prefer_exact_matches is not None:
        constraints["prefer_exact_matches"] = prefer_exact_matches
    else:
        constraints["prefer_exact_matches"] = False
    normalized["constraints"] = constraints
    return normalized


def _normalize_policy_snapshot(policy: object) -> dict[str, object]:
    if not isinstance(policy, dict):
        return {}
    normalized = copy.deepcopy(policy)
    normalized["active_strategy_ids"] = _normalize_text_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_text_list_like(normalized.get("deferred_strategy_ids"))
    return normalized


def _normalize_citation_bundle_snapshot(citation_bundle: dict[str, object]) -> dict[str, object]:
    normalized = copy.deepcopy(citation_bundle)
    for field_name in ("query_fingerprint", "result_fingerprint", "doc_hits_fingerprint", "excerpt_hits_fingerprint"):
        field_value = _normalize_optional_text(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
    query_scope = _normalize_query_scope(normalized.get("query_scope"))
    if query_scope is not None:
        normalized["query_scope"] = query_scope
    query_intent = _normalize_query_intent(normalized.get("query_intent"))
    if query_intent is not None:
        normalized["query_intent"] = query_intent
    query_confidentiality_profile = _normalize_query_confidentiality_profile(
        normalized.get("query_confidentiality_profile")
    )
    if query_confidentiality_profile is not None:
        normalized["query_confidentiality_profile"] = query_confidentiality_profile
    normalized["query_date_range"] = _normalize_query_date_range(normalized.get("query_date_range"))
    normalized["fts_shortlist_doc_ids"] = _normalize_text_list_like(normalized.get("fts_shortlist_doc_ids"))
    normalized["active_strategy_ids"] = _normalize_text_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_text_list_like(normalized.get("deferred_strategy_ids"))
    for field_name in ("candidate_doc_count", "doc_count", "excerpt_count"):
        field_value = _normalize_optional_int(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
    retrieval_backend = _normalize_optional_casefold_text(normalized.get("retrieval_backend"))
    if retrieval_backend is not None:
        normalized["retrieval_backend"] = retrieval_backend
    retrieval_mode = _normalize_optional_casefold_text(normalized.get("retrieval_mode"))
    if retrieval_mode is not None:
        normalized["retrieval_mode"] = retrieval_mode
    normalized["doc_citations"] = _normalize_doc_citations(normalized.get("doc_citations"))
    normalized["excerpt_citations"] = _normalize_excerpt_citations(normalized.get("excerpt_citations"))
    retrieval_policy = normalized.get("retrieval_policy")
    if isinstance(retrieval_policy, dict):
        normalized["retrieval_policy"] = _normalize_policy_snapshot(retrieval_policy)
    citation_status = normalized.get("citation_status")
    if isinstance(citation_status, dict):
        normalized["citation_status"] = copy.deepcopy(citation_status)
    elif "citation_status" in normalized:
        normalized["citation_status"] = {}
    return normalized


def _normalize_hit_shared_provenance_snapshot(provenance: object) -> dict[str, object]:
    if not isinstance(provenance, dict):
        return {}
    normalized = copy.deepcopy(provenance)
    query_fingerprint = _normalize_optional_text(normalized.get("query_fingerprint"))
    if query_fingerprint is not None:
        normalized["query_fingerprint"] = query_fingerprint
    query_scope = _normalize_query_scope(normalized.get("query_scope"))
    if query_scope is not None:
        normalized["query_scope"] = query_scope
    query_intent = _normalize_query_intent(normalized.get("query_intent"))
    if query_intent is not None:
        normalized["query_intent"] = query_intent
    query_confidentiality_profile = _normalize_query_confidentiality_profile(
        normalized.get("query_confidentiality_profile")
    )
    if query_confidentiality_profile is not None:
        normalized["query_confidentiality_profile"] = query_confidentiality_profile
    query_date_range = _normalize_query_date_range(normalized.get("query_date_range"))
    if query_date_range is not None:
        normalized["query_date_range"] = query_date_range
    candidate_doc_count = _normalize_optional_int(normalized.get("candidate_doc_count"))
    if candidate_doc_count is not None:
        normalized["candidate_doc_count"] = candidate_doc_count
    for field_name in (
        "fts_shortlist_doc_ids",
        "active_strategy_ids",
        "deferred_strategy_ids",
        "strategies_used",
        "retrieved_doc_ids",
        "retrieved_excerpt_ids",
    ):
        if field_name in normalized:
            normalized[field_name] = _normalize_text_list_like(normalized.get(field_name))
    retrieval_backend = _normalize_optional_casefold_text(normalized.get("retrieval_backend"))
    if retrieval_backend is not None:
        normalized["retrieval_backend"] = retrieval_backend
    retrieval_mode = _normalize_optional_casefold_text(normalized.get("retrieval_mode"))
    if retrieval_mode is not None:
        normalized["retrieval_mode"] = retrieval_mode
    retrieval_policy = normalized.get("retrieval_policy", normalized.get("policy"))
    if isinstance(retrieval_policy, dict):
        normalized["retrieval_policy"] = _normalize_policy_snapshot(retrieval_policy)
        normalized["policy"] = copy.deepcopy(normalized["retrieval_policy"])
    return normalized


def _normalize_excerpt_hit_provenance_snapshot(provenance: object) -> dict[str, object]:
    normalized = _normalize_hit_shared_provenance_snapshot(provenance)
    for field_name in (
        "doc_id",
        "excerpt_id",
        "source_hash",
        "doc_type",
        "doc_fingerprint",
        "doc_identity_fingerprint",
        "excerpt_fingerprint",
        "excerpt_provenance_fingerprint",
    ):
        field_value = _normalize_optional_text(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
    excerpt_text_hash = _normalize_optional_text(
        normalized.get("excerpt_text_hash") or normalized.get("hash")
    )
    if excerpt_text_hash is not None:
        normalized["excerpt_text_hash"] = excerpt_text_hash
        normalized["hash"] = excerpt_text_hash
    matched_terms = normalized.get("matched_terms")
    if matched_terms is not None:
        normalized["matched_terms"] = _normalize_text_list_like(matched_terms)
    for field_name in ("match_count", "rank", "section_hint_rank"):
        field_value = _normalize_optional_int(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
    fts_rank = normalized.get("fts_rank")
    if isinstance(fts_rank, str) and fts_rank.strip().isdigit():
        normalized["fts_rank"] = int(fts_rank.strip())
    else:
        normalized_fts_rank = _normalize_optional_float(fts_rank)
        if normalized_fts_rank is not None:
            normalized["fts_rank"] = normalized_fts_rank
    span = _normalize_span_snapshot(normalized.get("span"))
    if span is not None:
        normalized["span"] = span
    section_hint = _normalize_optional_text(normalized.get("section_hint"))
    if section_hint is not None:
        normalized["section_hint"] = section_hint
    source_strategy = _normalize_optional_casefold_text(
        normalized.get("source_strategy") or normalized.get("retrieval_source_strategy")
    )
    if source_strategy is not None:
        normalized["source_strategy"] = source_strategy
        normalized["retrieval_source_strategy"] = source_strategy
    return normalized


def _normalize_doc_hit_provenance_snapshot(provenance: object) -> dict[str, object]:
    normalized = _normalize_hit_shared_provenance_snapshot(provenance)
    for field_name in (
        "doc_id",
        "doc_type",
        "doc_fingerprint",
        "doc_identity_fingerprint",
        "top_excerpt_id",
        "top_excerpt_hash",
        "top_excerpt_fingerprint",
        "top_excerpt_provenance_fingerprint",
        "top_excerpt_text_hash",
    ):
        field_value = _normalize_optional_text(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
    top_excerpt_text_hash = _normalize_optional_text(
        normalized.get("top_excerpt_text_hash") or normalized.get("top_excerpt_hash")
    )
    if top_excerpt_text_hash is not None:
        normalized["top_excerpt_text_hash"] = top_excerpt_text_hash
        normalized["top_excerpt_hash"] = top_excerpt_text_hash
    for field_name in ("doc_rank", "top_excerpt_rank", "top_section_hint_rank", "top_match_count"):
        field_value = _normalize_optional_int(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
    top_fts_rank = normalized.get("top_fts_rank")
    if isinstance(top_fts_rank, str) and top_fts_rank.strip().isdigit():
        normalized["top_fts_rank"] = int(top_fts_rank.strip())
    else:
        normalized_top_fts_rank = _normalize_optional_float(top_fts_rank)
        if normalized_top_fts_rank is not None:
            normalized["top_fts_rank"] = normalized_top_fts_rank
    top_excerpt_span = _normalize_span_snapshot(normalized.get("top_excerpt_span"))
    if top_excerpt_span is not None:
        normalized["top_excerpt_span"] = top_excerpt_span
    excerpt_ids = normalized.get("excerpt_ids")
    if excerpt_ids is not None:
        normalized["excerpt_ids"] = _normalize_text_list_like(excerpt_ids)
    top_matched_terms = normalized.get("top_matched_terms", normalized.get("matched_terms"))
    if top_matched_terms is not None:
        normalized["top_matched_terms"] = _normalize_text_list_like(top_matched_terms)
        normalized["top_match_count"] = _normalize_optional_int(normalized.get("top_match_count")) or len(
            normalized["top_matched_terms"]
        )
    section_hint = _normalize_optional_text(normalized.get("section_hint"))
    if section_hint is not None:
        normalized["section_hint"] = section_hint
    source_strategy = _normalize_optional_casefold_text(
        normalized.get("source_strategy") or normalized.get("retrieval_source_strategy")
    )
    if source_strategy is not None:
        normalized["source_strategy"] = source_strategy
        normalized["retrieval_source_strategy"] = source_strategy
    return normalized


def _normalize_excerpt_hit_snapshot(hit: object) -> dict[str, object] | None:
    if not isinstance(hit, dict):
        return None
    normalized = copy.deepcopy(hit)
    for field_name in (
        "doc_id",
        "excerpt_id",
        "excerpt_text",
        "title_hint",
        "rationale",
        "query_fingerprint",
        "source_hash",
        "doc_type",
        "doc_fingerprint",
        "doc_identity_fingerprint",
        "excerpt_fingerprint",
        "excerpt_provenance_fingerprint",
        "excerpt_text_hash",
    ):
        field_value = _normalize_optional_text(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
    query_scope = _normalize_query_scope(normalized.get("query_scope"))
    if query_scope is not None:
        normalized["query_scope"] = query_scope
    query_intent = _normalize_query_intent(normalized.get("query_intent"))
    if query_intent is not None:
        normalized["query_intent"] = query_intent
    query_confidentiality_profile = _normalize_query_confidentiality_profile(
        normalized.get("query_confidentiality_profile")
    )
    if query_confidentiality_profile is not None:
        normalized["query_confidentiality_profile"] = query_confidentiality_profile
    query_date_range = _normalize_query_date_range(normalized.get("query_date_range"))
    if query_date_range is not None:
        normalized["query_date_range"] = query_date_range
    span = _normalize_span_snapshot(normalized.get("span"))
    if span is not None:
        normalized["span"] = span
    for field_name in ("rank", "match_count", "candidate_doc_count", "section_hint_rank"):
        field_value = _normalize_optional_int(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
    score = _normalize_optional_float(normalized.get("score"))
    if score is not None:
        normalized["score"] = score
    fts_rank = normalized.get("fts_rank")
    if isinstance(fts_rank, str) and fts_rank.strip().isdigit():
        normalized["fts_rank"] = int(fts_rank.strip())
    else:
        normalized_fts_rank = _normalize_optional_float(fts_rank)
        if normalized_fts_rank is not None:
            normalized["fts_rank"] = normalized_fts_rank
    source_strategy = _normalize_optional_casefold_text(
        normalized.get("source_strategy") or normalized.get("retrieval_source_strategy")
    )
    if source_strategy is not None:
        normalized["source_strategy"] = source_strategy
        normalized["retrieval_source_strategy"] = source_strategy
    matched_terms = normalized.get("matched_terms")
    if matched_terms is not None:
        normalized["matched_terms"] = _normalize_text_list_like(matched_terms)
    section_hint = _normalize_optional_text(normalized.get("section_hint"))
    if section_hint is not None:
        normalized["section_hint"] = section_hint
    retrieval_policy = normalized.get("retrieval_policy", normalized.get("policy"))
    if isinstance(retrieval_policy, dict):
        normalized["retrieval_policy"] = _normalize_policy_snapshot(retrieval_policy)
    for field_name in (
        "active_strategy_ids",
        "deferred_strategy_ids",
        "strategies_used",
        "retrieved_doc_ids",
        "retrieved_excerpt_ids",
    ):
        if field_name in normalized:
            normalized[field_name] = _normalize_text_list_like(normalized.get(field_name))
    provenance = normalized.get("provenance")
    normalized_provenance = _normalize_excerpt_hit_provenance_snapshot(provenance) if isinstance(provenance, dict) else {}
    fallback_provenance = _normalize_excerpt_hit_provenance_snapshot(
        {
            "query_fingerprint": normalized.get("query_fingerprint"),
            "query_scope": normalized.get("query_scope"),
            "query_intent": normalized.get("query_intent"),
            "query_confidentiality_profile": normalized.get("query_confidentiality_profile"),
            "query_date_range": normalized.get("query_date_range"),
            "candidate_doc_count": normalized.get("candidate_doc_count"),
            "fts_shortlist_doc_ids": normalized.get("fts_shortlist_doc_ids"),
            "doc_id": normalized.get("doc_id"),
            "excerpt_id": normalized.get("excerpt_id"),
            "source_hash": normalized.get("source_hash"),
            "doc_type": normalized.get("doc_type"),
            "doc_fingerprint": normalized.get("doc_fingerprint"),
            "doc_identity_fingerprint": normalized.get("doc_identity_fingerprint"),
            "excerpt_fingerprint": normalized.get("excerpt_fingerprint"),
            "excerpt_provenance_fingerprint": normalized.get("excerpt_provenance_fingerprint"),
            "excerpt_text_hash": normalized.get("excerpt_text_hash"),
            "excerpt_text_length": normalized.get("excerpt_text_length"),
            "hash": normalized.get("excerpt_text_hash"),
            "match_count": normalized.get("match_count"),
            "matched_terms": normalized.get("matched_terms"),
            "rank": normalized.get("rank"),
            "fts_rank": normalized.get("fts_rank"),
            "section_hint": normalized.get("section_hint"),
            "section_hint_rank": normalized.get("section_hint_rank"),
            "retrieval_backend": normalized.get("retrieval_backend"),
            "retrieval_mode": normalized.get("retrieval_mode"),
            "source_strategy": normalized.get("source_strategy"),
            "retrieval_source_strategy": normalized.get("retrieval_source_strategy"),
            "active_strategy_ids": normalized.get("active_strategy_ids"),
            "deferred_strategy_ids": normalized.get("deferred_strategy_ids"),
            "strategies_used": normalized.get("strategies_used"),
            "retrieved_doc_ids": normalized.get("retrieved_doc_ids"),
            "retrieved_excerpt_ids": normalized.get("retrieved_excerpt_ids"),
            "span": normalized.get("span"),
            "policy": normalized.get("retrieval_policy"),
            "retrieval_policy": normalized.get("retrieval_policy"),
        }
    )
    if normalized_provenance or fallback_provenance:
        normalized["provenance"] = _backfill_sparse_snapshot(
            normalized_provenance,
            {
                key: value
                for key, value in fallback_provenance.items()
                if not _is_missing_snapshot_value(value)
            },
        )
    return normalized


def _normalize_doc_hit_snapshot(hit: object) -> dict[str, object] | None:
    if not isinstance(hit, dict):
        return None
    normalized = copy.deepcopy(hit)
    for field_name in (
        "doc_id",
        "title_hint",
        "source_hash",
        "top_excerpt_id",
        "query_fingerprint",
        "doc_type",
        "doc_fingerprint",
        "doc_identity_fingerprint",
        "top_excerpt_hash",
        "top_excerpt_fingerprint",
        "top_excerpt_provenance_fingerprint",
        "top_excerpt_text_hash",
    ):
        field_value = _normalize_optional_text(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
    top_excerpt_text_hash = _normalize_optional_text(
        normalized.get("top_excerpt_text_hash") or normalized.get("top_excerpt_hash")
    )
    if top_excerpt_text_hash is not None:
        normalized["top_excerpt_text_hash"] = top_excerpt_text_hash
        normalized["top_excerpt_hash"] = top_excerpt_text_hash
    query_scope = _normalize_query_scope(normalized.get("query_scope"))
    if query_scope is not None:
        normalized["query_scope"] = query_scope
    query_intent = _normalize_query_intent(normalized.get("query_intent"))
    if query_intent is not None:
        normalized["query_intent"] = query_intent
    query_confidentiality_profile = _normalize_query_confidentiality_profile(
        normalized.get("query_confidentiality_profile")
    )
    if query_confidentiality_profile is not None:
        normalized["query_confidentiality_profile"] = query_confidentiality_profile
    query_date_range = _normalize_query_date_range(normalized.get("query_date_range"))
    if query_date_range is not None:
        normalized["query_date_range"] = query_date_range
    top_excerpt_span = _normalize_span_snapshot(normalized.get("top_excerpt_span"))
    if top_excerpt_span is not None:
        normalized["top_excerpt_span"] = top_excerpt_span
    for field_name in (
        "excerpt_count",
        "candidate_doc_count",
        "doc_rank",
        "top_excerpt_rank",
        "top_section_hint_rank",
        "top_match_count",
    ):
        field_value = _normalize_optional_int(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
    top_score = _normalize_optional_float(normalized.get("top_score"))
    if top_score is not None:
        normalized["top_score"] = top_score
    top_fts_rank = normalized.get("top_fts_rank")
    if isinstance(top_fts_rank, str) and top_fts_rank.strip().isdigit():
        normalized["top_fts_rank"] = int(top_fts_rank.strip())
    else:
        normalized_top_fts_rank = _normalize_optional_float(top_fts_rank)
        if normalized_top_fts_rank is not None:
            normalized["top_fts_rank"] = normalized_top_fts_rank
    source_strategy = _normalize_optional_casefold_text(
        normalized.get("source_strategy") or normalized.get("retrieval_source_strategy")
    )
    if source_strategy is not None:
        normalized["source_strategy"] = source_strategy
        normalized["retrieval_source_strategy"] = source_strategy
    excerpt_ids = normalized.get("excerpt_ids")
    if excerpt_ids is not None:
        normalized["excerpt_ids"] = _normalize_text_list_like(excerpt_ids)
    matched_terms = normalized.get("matched_terms")
    if matched_terms is not None:
        normalized["matched_terms"] = _normalize_text_list_like(matched_terms)
    top_matched_terms = normalized.get("top_matched_terms", normalized.get("matched_terms"))
    if top_matched_terms is not None:
        normalized["top_matched_terms"] = _normalize_text_list_like(top_matched_terms)
        normalized["top_match_count"] = _normalize_optional_int(normalized.get("top_match_count")) or len(
            normalized["top_matched_terms"]
        )
    section_hint = _normalize_optional_text(normalized.get("section_hint"))
    if section_hint is not None:
        normalized["section_hint"] = section_hint
    retrieval_policy = normalized.get("retrieval_policy", normalized.get("policy"))
    if isinstance(retrieval_policy, dict):
        normalized["retrieval_policy"] = _normalize_policy_snapshot(retrieval_policy)
    for field_name in (
        "active_strategy_ids",
        "deferred_strategy_ids",
        "strategies_used",
        "retrieved_doc_ids",
        "retrieved_excerpt_ids",
    ):
        if field_name in normalized:
            normalized[field_name] = _normalize_text_list_like(normalized.get(field_name))
    provenance = normalized.get("provenance")
    normalized_provenance = _normalize_doc_hit_provenance_snapshot(provenance) if isinstance(provenance, dict) else {}
    fallback_provenance = _normalize_doc_hit_provenance_snapshot(
        {
            "query_fingerprint": normalized.get("query_fingerprint"),
            "query_scope": normalized.get("query_scope"),
            "query_intent": normalized.get("query_intent"),
            "query_confidentiality_profile": normalized.get("query_confidentiality_profile"),
            "query_date_range": normalized.get("query_date_range"),
            "candidate_doc_count": normalized.get("candidate_doc_count"),
            "fts_shortlist_doc_ids": normalized.get("fts_shortlist_doc_ids"),
            "doc_id": normalized.get("doc_id"),
            "source_hash": normalized.get("source_hash"),
            "doc_type": normalized.get("doc_type"),
            "doc_fingerprint": normalized.get("doc_fingerprint"),
            "doc_identity_fingerprint": normalized.get("doc_identity_fingerprint"),
            "top_excerpt_id": normalized.get("top_excerpt_id"),
            "top_excerpt_hash": normalized.get("top_excerpt_hash"),
            "top_excerpt_fingerprint": normalized.get("top_excerpt_fingerprint"),
            "top_excerpt_provenance_fingerprint": normalized.get("top_excerpt_provenance_fingerprint"),
            "top_excerpt_text_hash": normalized.get("top_excerpt_text_hash"),
            "top_excerpt_text_length": normalized.get("top_excerpt_text_length"),
            "doc_rank": normalized.get("doc_rank"),
            "excerpt_count": normalized.get("excerpt_count"),
            "top_excerpt_rank": normalized.get("top_excerpt_rank"),
            "top_fts_rank": normalized.get("top_fts_rank"),
            "top_excerpt_span": normalized.get("top_excerpt_span"),
            "excerpt_ids": normalized.get("excerpt_ids"),
            "matched_terms": normalized.get("matched_terms"),
            "top_matched_terms": normalized.get("top_matched_terms"),
            "top_match_count": normalized.get("top_match_count"),
            "section_hint": normalized.get("section_hint"),
            "top_section_hint_rank": normalized.get("top_section_hint_rank"),
            "retrieval_backend": normalized.get("retrieval_backend"),
            "retrieval_mode": normalized.get("retrieval_mode"),
            "source_strategy": normalized.get("source_strategy"),
            "retrieval_source_strategy": normalized.get("retrieval_source_strategy"),
            "active_strategy_ids": normalized.get("active_strategy_ids"),
            "deferred_strategy_ids": normalized.get("deferred_strategy_ids"),
            "strategies_used": normalized.get("strategies_used"),
            "retrieved_doc_ids": normalized.get("retrieved_doc_ids"),
            "retrieved_excerpt_ids": normalized.get("retrieved_excerpt_ids"),
            "policy": normalized.get("retrieval_policy"),
            "retrieval_policy": normalized.get("retrieval_policy"),
        }
    )
    if normalized_provenance or fallback_provenance:
        normalized["provenance"] = _backfill_sparse_snapshot(
            normalized_provenance,
            {
                key: value
                for key, value in fallback_provenance.items()
                if not _is_missing_snapshot_value(value)
            },
        )
    return normalized


def _normalize_doc_hits(value: object) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    for item in _normalize_list_like(value):
        snapshot = _normalize_doc_hit_snapshot(item)
        if snapshot is not None:
            normalized.append(snapshot)
    return normalized


def _normalize_excerpt_hits(value: object) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    for item in _normalize_list_like(value):
        snapshot = _normalize_excerpt_hit_snapshot(item)
        if snapshot is not None:
            normalized.append(snapshot)
    return normalized


def _doc_hit_identity(snapshot: dict[str, object]) -> tuple[str | None, str | None]:
    return (
        _normalize_optional_text(snapshot.get("doc_id")),
        _normalize_optional_text(snapshot.get("top_excerpt_id")),
    )


def _excerpt_hit_identity(snapshot: dict[str, object]) -> tuple[str | None, str | None]:
    return (
        _normalize_optional_text(snapshot.get("doc_id")),
        _normalize_optional_text(snapshot.get("excerpt_id")),
    )


def _backfill_top_level_doc_hits_from_bundle_hits(
    doc_hits: object,
    bundle_doc_hits: object,
) -> list[dict[str, object]]:
    primary_hits = _normalize_doc_hits(doc_hits)
    fallback_hits = _normalize_doc_hits(bundle_doc_hits)
    fallback_by_identity = {_doc_hit_identity(item): item for item in fallback_hits}
    merged_hits: list[dict[str, object]] = []
    for index, hit in enumerate(primary_hits):
        fallback_hit = fallback_by_identity.get(_doc_hit_identity(hit))
        if fallback_hit is None and index < len(fallback_hits):
            fallback_hit = fallback_hits[index]
        if fallback_hit is not None:
            merged_hits.append(_backfill_sparse_snapshot(hit, fallback_hit))
        else:
            merged_hits.append(hit)
    return merged_hits


def _backfill_top_level_excerpt_hits_from_bundle_hits(
    excerpt_hits: object,
    bundle_excerpt_hits: object,
) -> list[dict[str, object]]:
    primary_hits = _normalize_excerpt_hits(excerpt_hits)
    fallback_hits = _normalize_excerpt_hits(bundle_excerpt_hits)
    fallback_by_identity = {_excerpt_hit_identity(item): item for item in fallback_hits}
    merged_hits: list[dict[str, object]] = []
    for index, hit in enumerate(primary_hits):
        fallback_hit = fallback_by_identity.get(_excerpt_hit_identity(hit))
        if fallback_hit is None and index < len(fallback_hits):
            fallback_hit = fallback_hits[index]
        if fallback_hit is not None:
            merged_hits.append(_backfill_sparse_snapshot(hit, fallback_hit))
        else:
            merged_hits.append(hit)
    return merged_hits


def _normalize_doc_bundle_snapshot(doc_bundle: dict[str, object]) -> dict[str, object]:
    normalized = copy.deepcopy(doc_bundle)
    normalized["query"] = _normalize_query_snapshot(normalized.get("query", {}))
    normalized["query_date_range"] = _normalize_query_date_range(normalized.get("query_date_range"))
    normalized["active_strategy_ids"] = _normalize_text_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_text_list_like(normalized.get("deferred_strategy_ids"))
    normalized["doc_hits"] = _normalize_doc_hits(normalized.get("doc_hits"))
    normalized["doc_citations"] = _normalize_doc_citations(normalized.get("doc_citations"))
    normalized["basket_promotion"] = _normalize_basket_promotion_snapshot(normalized.get("basket_promotion"))
    if isinstance(normalized["basket_promotion"], dict):
        normalized["basket_promotion"].pop("source_bundle_fingerprint", None)
    policy = normalized.get("policy")
    if isinstance(policy, dict):
        normalized["policy"] = _normalize_policy_snapshot(policy)
    elif "policy" in normalized:
        normalized["policy"] = {}
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
    normalized["query"] = _normalize_query_snapshot(normalized.get("query", {}))
    normalized["query_date_range"] = _normalize_query_date_range(normalized.get("query_date_range"))
    normalized["active_strategy_ids"] = _normalize_text_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_text_list_like(normalized.get("deferred_strategy_ids"))
    normalized["excerpt_hits"] = _normalize_excerpt_hits(normalized.get("excerpt_hits"))
    normalized["excerpt_citations"] = _normalize_excerpt_citations(normalized.get("excerpt_citations"))
    normalized["basket_promotion"] = _normalize_basket_promotion_snapshot(normalized.get("basket_promotion"))
    if isinstance(normalized["basket_promotion"], dict):
        normalized["basket_promotion"].pop("source_bundle_fingerprint", None)
    policy = normalized.get("policy")
    if isinstance(policy, dict):
        normalized["policy"] = _normalize_policy_snapshot(policy)
    elif "policy" in normalized:
        normalized["policy"] = {}
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
        normalized["query_date_range"] = _normalize_query_date_range(normalized.get("query_date_range"))
    if "primary_title_hint" in normalized:
        normalized["primary_title_hint"] = _normalize_optional_text(normalized.get("primary_title_hint"))
    normalized["doc_ids"] = _normalize_text_list_like(normalized.get("doc_ids"))
    normalized["doc_fingerprints"] = _normalize_text_list_like(normalized.get("doc_fingerprints"))
    normalized["doc_identity_fingerprints"] = _normalize_text_list_like(normalized.get("doc_identity_fingerprints"))
    normalized["excerpt_ids"] = _normalize_text_list_like(normalized.get("excerpt_ids"))
    normalized["excerpt_fingerprints"] = _normalize_text_list_like(normalized.get("excerpt_fingerprints"))
    normalized["excerpt_text_hashes"] = _normalize_text_list_like(normalized.get("excerpt_text_hashes"))
    normalized["top_excerpt_ids"] = _normalize_text_list_like(normalized.get("top_excerpt_ids"))
    normalized["top_excerpt_fingerprints"] = _normalize_text_list_like(normalized.get("top_excerpt_fingerprints"))
    normalized["top_excerpt_text_hashes"] = _normalize_text_list_like(normalized.get("top_excerpt_text_hashes"))
    normalized["active_strategy_ids"] = _normalize_text_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_text_list_like(normalized.get("deferred_strategy_ids"))
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
    normalized["doc_ids"] = _normalize_text_list_like(normalized.get("doc_ids"))
    normalized["doc_fingerprints"] = _normalize_text_list_like(normalized.get("doc_fingerprints"))
    normalized["doc_identity_fingerprints"] = _normalize_text_list_like(normalized.get("doc_identity_fingerprints"))
    normalized["top_excerpt_ids"] = _normalize_text_list_like(normalized.get("top_excerpt_ids"))
    normalized["top_excerpt_fingerprints"] = _normalize_text_list_like(normalized.get("top_excerpt_fingerprints"))
    normalized["top_excerpt_text_hashes"] = _normalize_text_list_like(normalized.get("top_excerpt_text_hashes"))
    normalized["excerpt_ids"] = _normalize_text_list_like(normalized.get("excerpt_ids"))
    normalized["excerpt_fingerprints"] = _normalize_text_list_like(normalized.get("excerpt_fingerprints"))
    normalized["excerpt_text_hashes"] = _normalize_text_list_like(normalized.get("excerpt_text_hashes"))
    normalized["active_strategy_ids"] = _normalize_text_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_text_list_like(normalized.get("deferred_strategy_ids"))
    retrieval_policy = normalized.get("retrieval_policy")
    if isinstance(retrieval_policy, dict):
        normalized["retrieval_policy"] = _normalize_policy_snapshot(retrieval_policy)
    return normalized


def _normalize_retrieval_evidence_snapshot(evidence: dict[str, object]) -> dict[str, object]:
    normalized = copy.deepcopy(evidence)
    normalized["query_date_range"] = _normalize_query_date_range(normalized.get("query_date_range"))
    normalized["fts_shortlist_doc_ids"] = _normalize_text_list_like(normalized.get("fts_shortlist_doc_ids"))
    normalized["active_strategy_ids"] = _normalize_text_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_text_list_like(normalized.get("deferred_strategy_ids"))
    normalized["doc_citations"] = _normalize_doc_citations(normalized.get("doc_citations"))
    normalized["excerpt_citations"] = _normalize_excerpt_citations(normalized.get("excerpt_citations"))
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


def _derive_doc_citations_from_hits(doc_hits: object) -> list[dict[str, object]]:
    derived: list[dict[str, object]] = []
    for item in _normalize_doc_hits(doc_hits):
        provenance = item.get("provenance")
        if not isinstance(provenance, dict):
            provenance = {}
        citation = {
            "doc_id": item.get("doc_id"),
            "doc_type": provenance.get("doc_type"),
            "source_hash": item.get("source_hash", provenance.get("source_hash")),
            "doc_fingerprint": provenance.get("doc_fingerprint"),
            "doc_identity_fingerprint": provenance.get("doc_identity_fingerprint"),
            "doc_rank": provenance.get("doc_rank"),
            "top_excerpt_id": item.get("top_excerpt_id"),
            "top_excerpt_fingerprint": provenance.get("top_excerpt_fingerprint"),
            "top_excerpt_text_hash": provenance.get("top_excerpt_text_hash"),
            "top_excerpt_span": copy.deepcopy(_normalize_span_snapshot(provenance.get("top_excerpt_span"))),
            "top_excerpt_rank": provenance.get("top_excerpt_rank"),
            "top_fts_rank": provenance.get("top_fts_rank"),
            "excerpt_ids": copy.deepcopy(provenance.get("excerpt_ids")),
            "excerpt_count": item.get("excerpt_count"),
            "matched_terms": copy.deepcopy(provenance.get("top_matched_terms")),
            "source_strategy": provenance.get("source_strategy"),
            "retrieval_backend": provenance.get("retrieval_backend"),
            "retrieval_mode": provenance.get("retrieval_mode"),
        }
        section_hint = _normalize_optional_text(provenance.get("section_hint"))
        if section_hint is not None:
            citation["section_hint"] = section_hint
        top_section_hint_rank = provenance.get("top_section_hint_rank")
        if isinstance(top_section_hint_rank, int):
            citation["top_section_hint_rank"] = top_section_hint_rank
        derived.append(_normalize_doc_citation(citation))
    return derived


def _derive_excerpt_citations_from_hits(excerpt_hits: object) -> list[dict[str, object]]:
    derived: list[dict[str, object]] = []
    for item in _normalize_excerpt_hits(excerpt_hits):
        excerpt_id = item.get("excerpt_id")
        if excerpt_id is None:
            continue
        provenance = item.get("provenance")
        if not isinstance(provenance, dict):
            provenance = {}
        citation = {
            "doc_id": item.get("doc_id"),
            "excerpt_id": excerpt_id,
            "doc_type": provenance.get("doc_type"),
            "source_hash": item.get("source_hash", provenance.get("source_hash")),
            "excerpt_fingerprint": provenance.get("excerpt_fingerprint"),
            "excerpt_provenance_fingerprint": provenance.get("excerpt_provenance_fingerprint"),
            "excerpt_text_hash": provenance.get("excerpt_text_hash", provenance.get("hash")),
            "match_count": provenance.get("match_count"),
            "matched_terms": copy.deepcopy(provenance.get("matched_terms")),
            "fts_rank": provenance.get("fts_rank"),
            "rank": provenance.get("rank"),
            "span": copy.deepcopy(_normalize_span_snapshot(provenance.get("span"))),
            "source_strategy": provenance.get("source_strategy"),
            "retrieval_backend": provenance.get("retrieval_backend"),
            "retrieval_mode": provenance.get("retrieval_mode"),
        }
        section_hint = _normalize_optional_text(provenance.get("section_hint"))
        if section_hint is not None:
            citation["section_hint"] = section_hint
        section_hint_rank = provenance.get("section_hint_rank")
        if isinstance(section_hint_rank, int):
            citation["section_hint_rank"] = section_hint_rank
        derived.append(_normalize_excerpt_citation(citation))
    return derived


def _normalize_doc_citations(value: object) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    for item in _normalize_list_like(value):
        if isinstance(item, dict):
            normalized.append(_normalize_doc_citation(item))
    return normalized


def _normalize_excerpt_citations(value: object) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    for item in _normalize_list_like(value):
        if isinstance(item, dict):
            normalized.append(_normalize_excerpt_citation(item))
    return normalized


def _normalize_doc_citation(citation: dict[str, object]) -> dict[str, object]:
    normalized = copy.deepcopy(citation)
    for field_name in (
        "doc_id",
        "doc_type",
        "source_hash",
        "doc_fingerprint",
        "doc_identity_fingerprint",
        "top_excerpt_id",
        "top_excerpt_fingerprint",
        "top_excerpt_text_hash",
    ):
        field_value = _normalize_optional_text(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
        elif field_name in normalized:
            normalized[field_name] = None
    excerpt_ids = normalized.get("excerpt_ids")
    if excerpt_ids is not None:
        normalized["excerpt_ids"] = _normalize_text_list_like(excerpt_ids)
    matched_terms = normalized.get("matched_terms")
    if matched_terms is not None:
        normalized["matched_terms"] = _normalize_text_list_like(matched_terms)
    for field_name in ("doc_rank", "top_excerpt_rank", "excerpt_count", "top_section_hint_rank"):
        field_value = _normalize_optional_int(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
        elif field_name in normalized:
            normalized[field_name] = None
    top_fts_rank = normalized.get("top_fts_rank")
    if isinstance(top_fts_rank, str) and top_fts_rank.strip().isdigit():
        normalized["top_fts_rank"] = int(top_fts_rank.strip())
    else:
        normalized_top_fts_rank = _normalize_optional_float(top_fts_rank)
        if normalized_top_fts_rank is not None:
            normalized["top_fts_rank"] = normalized_top_fts_rank
        elif "top_fts_rank" in normalized:
            normalized["top_fts_rank"] = None
    for field_name in ("source_strategy", "retrieval_backend", "retrieval_mode"):
        field_value = _normalize_optional_casefold_text(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
        elif field_name in normalized:
            normalized[field_name] = None
    top_excerpt_span = _normalize_span_snapshot(normalized.get("top_excerpt_span"))
    if top_excerpt_span is not None:
        normalized["top_excerpt_span"] = copy.deepcopy(top_excerpt_span)
    elif "top_excerpt_span" in normalized:
        normalized["top_excerpt_span"] = None
    section_hint = _normalize_optional_text(normalized.get("section_hint"))
    if section_hint is not None:
        normalized["section_hint"] = section_hint
    elif "section_hint" in normalized:
        normalized.pop("section_hint", None)
    return normalized


def _normalize_excerpt_citation(citation: dict[str, object]) -> dict[str, object]:
    normalized = copy.deepcopy(citation)
    for field_name in (
        "doc_id",
        "excerpt_id",
        "doc_type",
        "source_hash",
        "excerpt_fingerprint",
        "excerpt_provenance_fingerprint",
        "excerpt_text_hash",
    ):
        field_value = _normalize_optional_text(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
        elif field_name in normalized:
            normalized[field_name] = None
    matched_terms = normalized.get("matched_terms")
    if matched_terms is not None:
        normalized["matched_terms"] = _normalize_text_list_like(matched_terms)
    for field_name in ("rank", "match_count", "section_hint_rank"):
        field_value = _normalize_optional_int(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
        elif field_name in normalized:
            normalized[field_name] = None
    fts_rank = normalized.get("fts_rank")
    if isinstance(fts_rank, str) and fts_rank.strip().isdigit():
        normalized["fts_rank"] = int(fts_rank.strip())
    else:
        normalized_fts_rank = _normalize_optional_float(fts_rank)
        if normalized_fts_rank is not None:
            normalized["fts_rank"] = normalized_fts_rank
        elif "fts_rank" in normalized:
            normalized["fts_rank"] = None
    for field_name in ("source_strategy", "retrieval_backend", "retrieval_mode"):
        field_value = _normalize_optional_casefold_text(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
        elif field_name in normalized:
            normalized[field_name] = None
    span = _normalize_span_snapshot(normalized.get("span"))
    if span is not None:
        normalized["span"] = copy.deepcopy(span)
    elif "span" in normalized:
        normalized["span"] = None
    section_hint = _normalize_optional_text(normalized.get("section_hint"))
    if section_hint is not None:
        normalized["section_hint"] = section_hint
    elif "section_hint" in normalized:
        normalized.pop("section_hint", None)
    return normalized


def _normalize_basket_promotion_snapshot(snapshot: object) -> dict[str, object]:
    if not isinstance(snapshot, dict):
        return {}
    normalized = copy.deepcopy(snapshot)
    query_text = _normalize_query_text(normalized.get("query_text"))
    if query_text is not None:
        normalized["query_text"] = query_text
    elif "query_text" in normalized:
        normalized["query_text"] = None
    for field_name in (
        "query_fingerprint",
        "result_fingerprint",
        "promotion_fingerprint",
        "source_bundle_fingerprint",
        "lookup_fingerprint",
        "doc_id",
        "doc_fingerprint",
        "doc_identity_fingerprint",
        "source_hash",
        "excerpt_id",
        "excerpt_fingerprint",
        "excerpt_provenance_fingerprint",
        "excerpt_text_hash",
    ):
        field_value = _normalize_optional_text(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
        elif field_name in normalized:
            normalized[field_name] = None
    retrieval_policy = normalized.get("retrieval_policy")
    if isinstance(retrieval_policy, dict):
        normalized["retrieval_policy"] = _normalize_policy_snapshot(retrieval_policy)
    elif "retrieval_policy" in normalized:
        normalized["retrieval_policy"] = {}
    normalized["active_strategy_ids"] = _normalize_text_list_like(normalized.get("active_strategy_ids"))
    normalized["deferred_strategy_ids"] = _normalize_text_list_like(normalized.get("deferred_strategy_ids"))
    if "strategies_used" in normalized:
        normalized["strategies_used"] = _normalize_text_list_like(normalized.get("strategies_used"))
    if "retrieved_doc_ids" in normalized:
        normalized["retrieved_doc_ids"] = _normalize_text_list_like(normalized.get("retrieved_doc_ids"))
    if "retrieved_excerpt_ids" in normalized:
        normalized["retrieved_excerpt_ids"] = _normalize_text_list_like(normalized.get("retrieved_excerpt_ids"))
    doc_type = _normalize_optional_text(normalized.get("doc_type"))
    if doc_type is not None:
        normalized["doc_type"] = doc_type
    elif "doc_type" in normalized:
        normalized["doc_type"] = None
    title_hint = _normalize_optional_text(normalized.get("title_hint"))
    if title_hint is not None:
        normalized["title_hint"] = title_hint
    elif "title_hint" in normalized:
        normalized["title_hint"] = None
    excerpt_text = _normalize_optional_text(normalized.get("excerpt_text"))
    if excerpt_text is not None:
        normalized["excerpt_text"] = excerpt_text
    elif "excerpt_text" in normalized:
        normalized["excerpt_text"] = None
    span = _normalize_span_snapshot(normalized.get("span"))
    if span is not None:
        normalized["span"] = copy.deepcopy(span)
    elif "span" in normalized:
        normalized["span"] = None
    matched_terms = normalized.get("matched_terms")
    if matched_terms is not None:
        normalized["matched_terms"] = _normalize_text_list_like(matched_terms)
    elif "matched_terms" in normalized:
        normalized["matched_terms"] = None
    section_hint = _normalize_optional_text(normalized.get("section_hint"))
    if section_hint is not None:
        normalized["section_hint"] = section_hint
    elif "section_hint" in normalized:
        normalized["section_hint"] = None
    query_scope = _normalize_query_scope(normalized.get("query_scope"))
    if query_scope is not None:
        normalized["query_scope"] = query_scope
    elif "query_scope" in normalized:
        normalized["query_scope"] = None
    query_intent = _normalize_query_intent(normalized.get("query_intent"))
    if query_intent is not None:
        normalized["query_intent"] = query_intent
    elif "query_intent" in normalized:
        normalized["query_intent"] = None
    query_confidentiality_profile = _normalize_query_confidentiality_profile(
        normalized.get("query_confidentiality_profile")
    )
    if query_confidentiality_profile is not None:
        normalized["query_confidentiality_profile"] = query_confidentiality_profile
    elif "query_confidentiality_profile" in normalized:
        normalized["query_confidentiality_profile"] = None
    lookup_resolution = _normalize_optional_text(normalized.get("lookup_resolution"))
    if lookup_resolution is not None:
        normalized["lookup_resolution"] = lookup_resolution.casefold()
    elif "lookup_resolution" in normalized:
        normalized["lookup_resolution"] = None
    promotion_source = _normalize_optional_casefold_text(normalized.get("promotion_source"))
    if promotion_source is not None:
        normalized["promotion_source"] = promotion_source
    elif "promotion_source" in normalized:
        normalized["promotion_source"] = None
    source_strategy = _normalize_optional_casefold_text(normalized.get("source_strategy"))
    if source_strategy is not None:
        normalized["source_strategy"] = source_strategy
    elif "source_strategy" in normalized:
        normalized["source_strategy"] = None
    retrieval_backend = _normalize_optional_casefold_text(normalized.get("retrieval_backend"))
    if retrieval_backend is not None:
        normalized["retrieval_backend"] = retrieval_backend
    elif "retrieval_backend" in normalized:
        normalized["retrieval_backend"] = None
    retrieval_mode = _normalize_optional_casefold_text(normalized.get("retrieval_mode"))
    if retrieval_mode is not None:
        normalized["retrieval_mode"] = retrieval_mode
    elif "retrieval_mode" in normalized:
        normalized["retrieval_mode"] = None
    lookup_confidentiality_profile = _normalize_query_confidentiality_profile(
        normalized.get("lookup_confidentiality_profile")
    )
    if lookup_confidentiality_profile is not None:
        normalized["lookup_confidentiality_profile"] = lookup_confidentiality_profile
    elif "lookup_confidentiality_profile" in normalized:
        normalized["lookup_confidentiality_profile"] = None
    query_date_range = _normalize_query_date_range(normalized.get("query_date_range"))
    if query_date_range is not None:
        normalized["query_date_range"] = query_date_range
    elif "query_date_range" in normalized:
        normalized["query_date_range"] = None
    fts_shortlist_doc_ids = _normalize_optional_list_like(normalized.get("fts_shortlist_doc_ids"))
    if fts_shortlist_doc_ids is not None:
        normalized["fts_shortlist_doc_ids"] = _normalize_text_list_like(fts_shortlist_doc_ids)
    elif "fts_shortlist_doc_ids" in normalized:
        normalized["fts_shortlist_doc_ids"] = []
    promotion_ready = _normalize_optional_bool(normalized.get("promotion_ready"))
    if promotion_ready is not None:
        normalized["promotion_ready"] = promotion_ready
    elif "promotion_ready" in normalized:
        normalized["promotion_ready"] = None
    citation_available = _normalize_optional_bool(normalized.get("citation_available"))
    if citation_available is not None:
        normalized["citation_available"] = citation_available
    elif "citation_available" in normalized:
        normalized["citation_available"] = None
    for field_name in ("candidate_doc_count", "match_count", "rank", "doc_rank", "section_hint_rank"):
        field_value = _normalize_optional_int(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
        elif field_name in normalized:
            normalized[field_name] = None
    fts_rank = _normalize_optional_int(normalized.get("fts_rank"))
    if fts_rank is not None and str(normalized.get("fts_rank")).strip().isdigit():
        normalized["fts_rank"] = fts_rank
    else:
        normalized_fts_rank = _normalize_optional_float(normalized.get("fts_rank"))
        if normalized_fts_rank is not None:
            normalized["fts_rank"] = normalized_fts_rank
        elif "fts_rank" in normalized:
            normalized["fts_rank"] = None
    # Recompute from the normalized snapshot so sparse/backfilled payloads do
    # not carry a stale fingerprint after fields are canonicalized.
    normalized["promotion_fingerprint"] = _basket_promotion_fingerprint(normalized)
    return normalized


def _basket_promotion_fingerprint(snapshot: dict[str, object]) -> str:
    fingerprint_payload = copy.deepcopy(snapshot)
    fingerprint_payload.pop("promotion_fingerprint", None)
    fingerprint_payload.pop("source_bundle_fingerprint", None)
    return _stable_fingerprint(fingerprint_payload)


def _build_basket_promotion_from_payload(payload: dict[str, object]) -> dict[str, object]:
    primary_snapshot = _normalize_basket_promotion_snapshot(payload.get("basket_promotion"))
    retrieval_doc_bundle = payload.get("retrieval_doc_bundle", {})
    retrieval_excerpt_bundle = payload.get("retrieval_excerpt_bundle", {})
    retrieval_citation_bundle = payload.get("retrieval_citation_bundle", {})
    retrieval_provenance = payload.get("retrieval_provenance", {})
    retrieval_summary = payload.get("retrieval_summary", {})
    retrieval_source_bundle = payload.get("retrieval_source_bundle", payload.get("source_bundle", {}))
    if not isinstance(retrieval_doc_bundle, dict):
        retrieval_doc_bundle = {}
    if not isinstance(retrieval_excerpt_bundle, dict):
        retrieval_excerpt_bundle = {}
    if not isinstance(retrieval_citation_bundle, dict):
        retrieval_citation_bundle = {}
    if not isinstance(retrieval_provenance, dict):
        retrieval_provenance = {}
    if not isinstance(retrieval_summary, dict):
        retrieval_summary = {}
    if not isinstance(retrieval_source_bundle, dict):
        retrieval_source_bundle = {}
    query_payload = payload.get("query", retrieval_source_bundle.get("query", {}))
    if not isinstance(query_payload, dict):
        query_payload = {}
    retrieval_policy = _normalize_policy_snapshot(
        payload.get(
            "policy",
            payload.get(
                "retrieval_policy",
                retrieval_provenance.get("retrieval_policy", retrieval_summary.get("retrieval_policy", {})),
            ),
        )
    )

    doc_hits = _normalize_doc_hits(payload.get("doc_hits", []))
    if not doc_hits:
        doc_hits = _normalize_doc_hits(retrieval_doc_bundle.get("doc_hits", []))
    excerpt_hits = _normalize_excerpt_hits(payload.get("excerpt_hits", []))
    if not excerpt_hits:
        excerpt_hits = _normalize_excerpt_hits(retrieval_excerpt_bundle.get("excerpt_hits", []))
    first_doc_hit = doc_hits[0] if doc_hits and isinstance(doc_hits[0], dict) else {}
    first_excerpt_hit = excerpt_hits[0] if excerpt_hits and isinstance(excerpt_hits[0], dict) else {}
    first_doc_provenance = first_doc_hit.get("provenance", {}) if isinstance(first_doc_hit, dict) else {}
    if not isinstance(first_doc_provenance, dict):
        first_doc_provenance = {}
    first_excerpt_provenance = (
        first_excerpt_hit.get("provenance", {}) if isinstance(first_excerpt_hit, dict) else {}
    )
    if not isinstance(first_excerpt_provenance, dict):
        first_excerpt_provenance = {}
    first_doc_citation = {}
    doc_citations = _normalize_list_like(
        retrieval_citation_bundle.get(
            "doc_citations",
            retrieval_provenance.get("doc_citations", []),
        )
    )
    if doc_citations and isinstance(doc_citations[0], dict):
        first_doc_citation = doc_citations[0]
    first_excerpt_citation = {}
    excerpt_citations = _normalize_list_like(
        retrieval_citation_bundle.get(
            "excerpt_citations",
            retrieval_provenance.get("excerpt_citations", []),
        )
    )
    if excerpt_citations and isinstance(excerpt_citations[0], dict):
        first_excerpt_citation = excerpt_citations[0]
    promotion_source = "none"
    if first_excerpt_hit:
        promotion_source = "primary_ranked_excerpt"
    elif first_doc_hit:
        promotion_source = "primary_ranked_doc"
    elif first_excerpt_citation:
        promotion_source = "primary_ranked_excerpt"
    elif first_doc_citation:
        promotion_source = "primary_ranked_doc"
    lookup_resolution = _first_text_value(
        payload.get("lookup_resolution"),
        first_excerpt_hit.get("lookup_resolution") if isinstance(first_excerpt_hit, dict) else None,
        first_excerpt_provenance.get("lookup_resolution"),
        retrieval_provenance.get("lookup_resolution"),
    )
    lookup_confidentiality_profile = _normalize_query_confidentiality_profile(
        _first_text_value(
            payload.get("lookup_confidentiality_profile"),
            first_excerpt_hit.get("lookup_confidentiality_profile") if isinstance(first_excerpt_hit, dict) else None,
            first_excerpt_provenance.get("lookup_confidentiality_profile"),
            retrieval_provenance.get("lookup_confidentiality_profile"),
        )
    )
    derived = {
        "promotion_ready": bool(first_excerpt_hit or first_doc_hit or first_excerpt_citation or first_doc_citation),
        "promotion_source": promotion_source,
        # Rehydrated payloads can be doc-only while still exposing stable doc
        # citations, so treat either citation path as basket-promotion ready.
        "citation_available": bool(
            first_excerpt_hit or first_doc_hit or first_excerpt_citation or first_doc_citation
        ),
        "query_text": _normalize_query_text(
            _first_text_value(
                payload.get("query_text"),
                query_payload.get("query_text"),
            )
        ),
        "query_fingerprint": _first_text_value(
            payload.get("query_fingerprint"),
            retrieval_provenance.get("query_fingerprint"),
            retrieval_summary.get("query_fingerprint"),
        ),
        "query_scope": _first_text_value(
            payload.get("query_scope"),
            retrieval_provenance.get("query_scope"),
            retrieval_summary.get("query_scope"),
            retrieval_citation_bundle.get("query_scope"),
        ),
        "query_intent": _first_text_value(
            payload.get("query_intent"),
            retrieval_provenance.get("query_intent"),
            retrieval_summary.get("query_intent"),
            retrieval_citation_bundle.get("query_intent"),
        ),
        "query_confidentiality_profile": _normalize_query_confidentiality_profile(
            _first_text_value(
                payload.get("query_confidentiality_profile"),
                retrieval_provenance.get("query_confidentiality_profile"),
                retrieval_summary.get("query_confidentiality_profile"),
                retrieval_citation_bundle.get("query_confidentiality_profile"),
            )
        ),
        "query_date_range": _normalize_query_date_range(
            _first_non_none_value(
                payload.get("query_date_range"),
                retrieval_provenance.get("query_date_range"),
                retrieval_summary.get("query_date_range"),
                retrieval_citation_bundle.get("query_date_range"),
            )
        ),
        "candidate_doc_count": _first_non_none_value(
            payload.get("candidate_doc_count"),
            retrieval_provenance.get("candidate_doc_count"),
            retrieval_summary.get("candidate_doc_count"),
            retrieval_citation_bundle.get("candidate_doc_count"),
        ),
        "fts_shortlist_doc_ids": _normalize_text_list_like(
            _first_non_none_value(
                payload.get("fts_shortlist_doc_ids"),
                retrieval_provenance.get("fts_shortlist_doc_ids"),
                retrieval_summary.get("fts_shortlist_doc_ids"),
                retrieval_citation_bundle.get("fts_shortlist_doc_ids"),
            )
        ),
        "result_fingerprint": _first_text_value(
            payload.get("result_fingerprint"),
            retrieval_provenance.get("result_fingerprint"),
            retrieval_summary.get("result_fingerprint"),
        ),
        "source_bundle_fingerprint": _first_text_value(
            payload.get("source_bundle_fingerprint"),
            retrieval_source_bundle.get("source_bundle_fingerprint"),
        ),
        "doc_id": _first_text_value(
            first_excerpt_hit.get("doc_id") if isinstance(first_excerpt_hit, dict) else None,
            first_doc_hit.get("doc_id") if isinstance(first_doc_hit, dict) else None,
            first_excerpt_citation.get("doc_id"),
            first_doc_citation.get("doc_id"),
            retrieval_provenance.get("primary_doc_id"),
            retrieval_summary.get("primary_doc_id"),
        ),
        "doc_type": _first_text_value(
            first_excerpt_hit.get("doc_type") if isinstance(first_excerpt_hit, dict) else None,
            first_doc_hit.get("doc_type") if isinstance(first_doc_hit, dict) else None,
            first_excerpt_provenance.get("doc_type"),
            first_doc_provenance.get("doc_type"),
            first_excerpt_citation.get("doc_type"),
            first_doc_citation.get("doc_type"),
            retrieval_provenance.get("primary_doc_type"),
        ),
        "doc_fingerprint": _first_text_value(
            first_doc_hit.get("doc_fingerprint") if isinstance(first_doc_hit, dict) else None,
            first_excerpt_hit.get("doc_fingerprint") if isinstance(first_excerpt_hit, dict) else None,
            first_doc_provenance.get("doc_fingerprint"),
            first_excerpt_provenance.get("doc_fingerprint"),
            first_doc_citation.get("doc_fingerprint"),
            retrieval_provenance.get("primary_doc_fingerprint"),
            retrieval_summary.get("primary_doc_fingerprint"),
        ),
        "doc_identity_fingerprint": _first_text_value(
            first_doc_hit.get("doc_identity_fingerprint") if isinstance(first_doc_hit, dict) else None,
            first_excerpt_hit.get("doc_identity_fingerprint") if isinstance(first_excerpt_hit, dict) else None,
            first_doc_provenance.get("doc_identity_fingerprint"),
            first_excerpt_provenance.get("doc_identity_fingerprint"),
            first_doc_citation.get("doc_identity_fingerprint"),
            retrieval_provenance.get("primary_doc_identity_fingerprint"),
            retrieval_summary.get("primary_doc_identity_fingerprint"),
        ),
        "source_hash": _first_text_value(
            first_excerpt_hit.get("source_hash") if isinstance(first_excerpt_hit, dict) else None,
            first_excerpt_provenance.get("source_hash"),
            first_doc_hit.get("source_hash") if isinstance(first_doc_hit, dict) else None,
            first_doc_provenance.get("source_hash"),
            first_excerpt_citation.get("source_hash"),
            first_doc_citation.get("source_hash"),
            retrieval_provenance.get("primary_source_hash"),
        ),
        "title_hint": _first_text_value(
            first_excerpt_hit.get("title_hint") if isinstance(first_excerpt_hit, dict) else None,
            first_doc_hit.get("title_hint") if isinstance(first_doc_hit, dict) else None,
            retrieval_provenance.get("primary_title_hint"),
            retrieval_summary.get("primary_title_hint"),
        ),
        "excerpt_id": _first_text_value(
            first_excerpt_hit.get("excerpt_id") if isinstance(first_excerpt_hit, dict) else None,
            first_doc_hit.get("top_excerpt_id") if isinstance(first_doc_hit, dict) else None,
            first_excerpt_citation.get("excerpt_id"),
            first_doc_provenance.get("top_excerpt_id"),
            first_doc_citation.get("top_excerpt_id"),
            retrieval_provenance.get("primary_excerpt_id"),
            retrieval_summary.get("primary_excerpt_id"),
        ),
        "excerpt_fingerprint": _first_text_value(
            first_excerpt_hit.get("excerpt_fingerprint") if isinstance(first_excerpt_hit, dict) else None,
            first_excerpt_provenance.get("excerpt_fingerprint"),
            first_excerpt_citation.get("excerpt_fingerprint"),
            first_doc_hit.get("top_excerpt_fingerprint") if isinstance(first_doc_hit, dict) else None,
            first_doc_provenance.get("top_excerpt_fingerprint"),
            first_doc_citation.get("top_excerpt_fingerprint"),
            retrieval_provenance.get("primary_excerpt_fingerprint"),
            retrieval_summary.get("primary_excerpt_fingerprint"),
        ),
        "excerpt_provenance_fingerprint": _first_text_value(
            first_excerpt_hit.get("excerpt_provenance_fingerprint") if isinstance(first_excerpt_hit, dict) else None,
            first_excerpt_provenance.get("excerpt_provenance_fingerprint"),
            first_excerpt_citation.get("excerpt_provenance_fingerprint"),
            first_doc_hit.get("top_excerpt_provenance_fingerprint") if isinstance(first_doc_hit, dict) else None,
            first_doc_provenance.get("top_excerpt_provenance_fingerprint"),
            first_doc_citation.get("top_excerpt_provenance_fingerprint"),
            retrieval_provenance.get("primary_excerpt_provenance_fingerprint"),
            retrieval_summary.get("primary_excerpt_provenance_fingerprint"),
        ),
        "excerpt_text_hash": _first_text_value(
            first_excerpt_hit.get("excerpt_text_hash") if isinstance(first_excerpt_hit, dict) else None,
            first_excerpt_provenance.get("excerpt_text_hash"),
            first_excerpt_provenance.get("hash"),
            first_excerpt_citation.get("excerpt_text_hash"),
            first_doc_hit.get("top_excerpt_text_hash") if isinstance(first_doc_hit, dict) else None,
            first_doc_provenance.get("top_excerpt_text_hash"),
            first_doc_citation.get("top_excerpt_text_hash"),
            retrieval_provenance.get("primary_excerpt_text_hash"),
            retrieval_summary.get("primary_excerpt_text_hash"),
        ),
        "excerpt_text": _first_text_value(
            first_excerpt_hit.get("excerpt_text") if isinstance(first_excerpt_hit, dict) else None,
        ),
        "span": copy.deepcopy(
            _first_dict_value(
                first_excerpt_hit.get("span") if isinstance(first_excerpt_hit, dict) else None,
                first_excerpt_provenance.get("span"),
                first_excerpt_citation.get("span"),
                first_doc_hit.get("top_excerpt_span") if isinstance(first_doc_hit, dict) else None,
                first_doc_provenance.get("top_excerpt_span"),
                first_doc_citation.get("top_excerpt_span"),
                retrieval_provenance.get("primary_excerpt_span"),
            )
        ),
        "source_strategy": _first_text_value(
            first_excerpt_hit.get("source_strategy") if isinstance(first_excerpt_hit, dict) else None,
            first_doc_hit.get("source_strategy") if isinstance(first_doc_hit, dict) else None,
            first_excerpt_provenance.get("source_strategy"),
            first_doc_provenance.get("source_strategy"),
            first_excerpt_citation.get("source_strategy"),
            first_doc_citation.get("source_strategy"),
        ),
        "matched_terms": copy.deepcopy(
            first_excerpt_hit.get("matched_terms") if isinstance(first_excerpt_hit, dict) else None
        )
        or copy.deepcopy(first_excerpt_provenance.get("matched_terms"))
        or copy.deepcopy(first_excerpt_citation.get("matched_terms"))
        or copy.deepcopy(first_doc_provenance.get("top_matched_terms"))
        or copy.deepcopy(first_doc_citation.get("matched_terms")),
        "match_count": _first_non_none_value(
            first_excerpt_hit.get("match_count") if isinstance(first_excerpt_hit, dict) else None,
            first_excerpt_provenance.get("match_count"),
            first_excerpt_citation.get("match_count"),
            first_doc_provenance.get("top_match_count"),
            first_doc_citation.get("top_match_count"),
        ),
        "rank": _first_non_none_value(
            first_excerpt_hit.get("rank") if isinstance(first_excerpt_hit, dict) else None,
            first_excerpt_provenance.get("rank"),
            first_excerpt_citation.get("rank"),
            first_doc_hit.get("top_excerpt_rank") if isinstance(first_doc_hit, dict) else None,
            first_doc_provenance.get("top_excerpt_rank"),
            first_doc_citation.get("top_excerpt_rank"),
        ),
        "fts_rank": _first_non_none_value(
            first_excerpt_hit.get("fts_rank") if isinstance(first_excerpt_hit, dict) else None,
            first_excerpt_provenance.get("fts_rank"),
            first_excerpt_citation.get("fts_rank"),
            first_doc_hit.get("top_fts_rank") if isinstance(first_doc_hit, dict) else None,
            first_doc_provenance.get("top_fts_rank"),
            first_doc_citation.get("top_fts_rank"),
        ),
        "doc_rank": _first_non_none_value(
            first_doc_hit.get("doc_rank") if isinstance(first_doc_hit, dict) else None,
            first_doc_provenance.get("doc_rank"),
            first_doc_citation.get("doc_rank"),
        ),
        "section_hint": _first_text_value(
            first_excerpt_hit.get("section_hint") if isinstance(first_excerpt_hit, dict) else None,
            first_excerpt_provenance.get("section_hint"),
            first_excerpt_citation.get("section_hint"),
            first_doc_provenance.get("section_hint"),
            first_doc_citation.get("section_hint"),
        ),
        "section_hint_rank": _first_non_none_value(
            first_excerpt_hit.get("section_hint_rank") if isinstance(first_excerpt_hit, dict) else None,
            first_excerpt_provenance.get("section_hint_rank"),
            first_excerpt_citation.get("section_hint_rank"),
            first_doc_provenance.get("top_section_hint_rank"),
            first_doc_citation.get("top_section_hint_rank"),
        ),
        "retrieval_backend": _first_text_value(
            payload.get("retrieval_backend"),
            first_doc_provenance.get("retrieval_backend"),
            first_doc_citation.get("retrieval_backend"),
            first_excerpt_provenance.get("retrieval_backend"),
            first_excerpt_citation.get("retrieval_backend"),
            retrieval_summary.get("retrieval_backend"),
            retrieval_provenance.get("retrieval_backend"),
        ),
        "retrieval_mode": _first_text_value(
            payload.get("retrieval_mode"),
            first_doc_provenance.get("retrieval_mode"),
            first_doc_citation.get("retrieval_mode"),
            first_excerpt_provenance.get("retrieval_mode"),
            first_excerpt_citation.get("retrieval_mode"),
            retrieval_summary.get("retrieval_mode"),
            retrieval_provenance.get("retrieval_mode"),
        ),
        "retrieval_policy": retrieval_policy,
        "active_strategy_ids": _normalize_text_list_like(
            payload.get(
                "active_strategy_ids",
                retrieval_provenance.get(
                    "active_strategy_ids",
                    retrieval_summary.get("active_strategy_ids", retrieval_policy.get("active_strategy_ids", [])),
                ),
            )
        ),
        "deferred_strategy_ids": _normalize_text_list_like(
            payload.get(
                "deferred_strategy_ids",
                retrieval_provenance.get(
                    "deferred_strategy_ids",
                    retrieval_summary.get("deferred_strategy_ids", retrieval_policy.get("deferred_strategy_ids", [])),
                ),
            )
        ),
        "strategies_used": _normalize_text_list_like(
            _first_non_none_value(
                payload.get("strategies_used"),
                retrieval_provenance.get("strategies_used"),
                retrieval_summary.get("strategies_used"),
                retrieval_policy.get("active_strategy_ids", []),
            )
        ),
        "retrieved_doc_ids": _normalize_text_list_like(
            _first_non_none_value(
                payload.get("retrieved_doc_ids"),
                retrieval_provenance.get("retrieved_doc_ids"),
                retrieval_summary.get("retrieved_doc_ids"),
                retrieval_summary.get("doc_ids"),
                [item.get("doc_id") for item in doc_citations if isinstance(item, dict)],
                [item.get("doc_id") for item in doc_hits if isinstance(item, dict)],
            )
        ),
        "retrieved_excerpt_ids": _normalize_text_list_like(
            _first_non_none_value(
                payload.get("retrieved_excerpt_ids"),
                retrieval_provenance.get("retrieved_excerpt_ids"),
                retrieval_summary.get("retrieved_excerpt_ids"),
                retrieval_summary.get("excerpt_ids"),
                [item.get("excerpt_id") for item in excerpt_citations if isinstance(item, dict)],
                [item.get("excerpt_id") for item in excerpt_hits if isinstance(item, dict)],
            )
        ),
    }
    if lookup_resolution is not None:
        derived["lookup_resolution"] = lookup_resolution
    if lookup_confidentiality_profile is not None:
        derived["lookup_confidentiality_profile"] = lookup_confidentiality_profile
    if not primary_snapshot:
        return _normalize_basket_promotion_snapshot(derived)
    return _normalize_basket_promotion_snapshot(
        _backfill_sparse_snapshot(primary_snapshot, derived)
    )


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
    normalized["basket_promotion"] = _build_basket_promotion_from_payload(normalized)
    normalized["retrieval_citation_bundle"] = _build_retrieval_citation_bundle_from_payload(normalized)
    normalized["retrieval_doc_bundle"] = _build_retrieval_doc_bundle_from_payload(normalized)
    normalized["retrieval_excerpt_bundle"] = _build_retrieval_excerpt_bundle_from_payload(normalized)
    normalized["retrieval_provenance"] = _build_retrieval_provenance_from_payload(normalized)
    normalized["doc_hits"] = _normalize_doc_hits(normalized.get("doc_hits", []))
    normalized["excerpt_hits"] = _normalize_excerpt_hits(normalized.get("excerpt_hits", []))
    retrieval_doc_bundle = normalized.get("retrieval_doc_bundle", {})
    if not isinstance(retrieval_doc_bundle, dict):
        retrieval_doc_bundle = {}
    retrieval_excerpt_bundle = normalized.get("retrieval_excerpt_bundle", {})
    if not isinstance(retrieval_excerpt_bundle, dict):
        retrieval_excerpt_bundle = {}
    if not normalized["doc_hits"]:
        normalized["doc_hits"] = _normalize_doc_hits(retrieval_doc_bundle.get("doc_hits", []))
    if not normalized["excerpt_hits"]:
        normalized["excerpt_hits"] = _normalize_excerpt_hits(retrieval_excerpt_bundle.get("excerpt_hits", []))
    retrieval_summary = normalized.get("retrieval_summary", {})
    if not isinstance(retrieval_summary, dict):
        retrieval_summary = {}
    retrieval_provenance = normalized.get("retrieval_provenance", {})
    if not isinstance(retrieval_provenance, dict):
        retrieval_provenance = {}
    retrieval_citation_bundle = normalized.get("retrieval_citation_bundle", {})
    if not isinstance(retrieval_citation_bundle, dict):
        retrieval_citation_bundle = {}
    if isinstance(retrieval_doc_bundle, dict):
        retrieval_doc_bundle["doc_citations"] = copy.deepcopy(
            retrieval_citation_bundle.get("doc_citations", retrieval_doc_bundle.get("doc_citations", []))
        )
        normalized["retrieval_doc_bundle"] = _normalize_doc_bundle_snapshot(retrieval_doc_bundle)
        retrieval_doc_bundle = normalized["retrieval_doc_bundle"]
    if isinstance(retrieval_excerpt_bundle, dict):
        retrieval_excerpt_bundle["excerpt_citations"] = copy.deepcopy(
            retrieval_citation_bundle.get("excerpt_citations", retrieval_excerpt_bundle.get("excerpt_citations", []))
        )
        normalized["retrieval_excerpt_bundle"] = _normalize_excerpt_bundle_snapshot(retrieval_excerpt_bundle)
        retrieval_excerpt_bundle = normalized["retrieval_excerpt_bundle"]
    retrieval_policy = normalized.get("policy", normalized.get("retrieval_policy", {}))
    if not isinstance(retrieval_policy, dict):
        retrieval_policy = {}
    query_snapshot = normalized.get("query", {})
    if not isinstance(query_snapshot, dict):
        query_snapshot = {}
    query_constraints = query_snapshot.get("constraints", {})
    if not isinstance(query_constraints, dict):
        query_constraints = {}

    if _is_missing_snapshot_value(query_snapshot.get("scope")):
        query_snapshot["scope"] = _first_text_value(
            retrieval_citation_bundle.get("query_scope"),
            retrieval_provenance.get("query_scope"),
        )
    if _is_missing_snapshot_value(query_snapshot.get("intent")):
        query_snapshot["intent"] = _first_text_value(
            retrieval_citation_bundle.get("query_intent"),
            retrieval_provenance.get("query_intent"),
        )
    if _is_missing_snapshot_value(query_snapshot.get("confidentiality_profile")):
        query_confidentiality_profile = _normalize_query_confidentiality_profile(
            _first_text_value(
                retrieval_citation_bundle.get("query_confidentiality_profile"),
                retrieval_provenance.get("query_confidentiality_profile"),
            )
        )
        if query_confidentiality_profile is not None:
            query_snapshot["confidentiality_profile"] = query_confidentiality_profile
    if _is_missing_snapshot_value(query_constraints.get("date_range")):
        query_date_range = _normalize_query_date_range(
            retrieval_citation_bundle.get(
                "query_date_range",
                retrieval_provenance.get("query_date_range"),
            )
        )
        if query_date_range is not None:
            query_constraints["date_range"] = query_date_range
    query_snapshot["constraints"] = query_constraints
    normalized["query"] = _normalize_query_snapshot(query_snapshot)

    if _is_missing_snapshot_value(retrieval_policy):
        retrieval_policy = _normalize_policy_snapshot(
            _first_dict_value(
                retrieval_citation_bundle.get("retrieval_policy"),
                retrieval_summary.get("retrieval_policy"),
                retrieval_provenance.get("retrieval_policy"),
                normalized["retrieval_evidence"].get("retrieval_policy"),
                retrieval_doc_bundle.get("retrieval_policy"),
                retrieval_excerpt_bundle.get("retrieval_policy"),
            )
            or {}
        )
        normalized["policy"] = copy.deepcopy(retrieval_policy)

    citation_status = normalized.get("citation_status")
    if not isinstance(citation_status, dict):
        citation_status = {}
    if _is_missing_snapshot_value(citation_status):
        citation_status = _first_dict_value(
            retrieval_citation_bundle.get("citation_status"),
            retrieval_summary.get("citation_status"),
            retrieval_provenance.get("citation_status"),
            normalized["retrieval_evidence"].get("citation_status"),
            retrieval_doc_bundle.get("citation_status"),
            retrieval_excerpt_bundle.get("citation_status"),
        ) or {}
        normalized["citation_status"] = copy.deepcopy(citation_status)

    manifest_top_excerpt_ids = _normalize_list_like(normalized["retrieval_manifest"].get("top_excerpt_ids"))
    if not normalized["retrieval_summary"].get("top_excerpt_ids") and manifest_top_excerpt_ids:
        normalized["retrieval_summary"]["top_excerpt_ids"] = manifest_top_excerpt_ids

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

    fingerprint_payload = {
        key: value for key, value in normalized.items() if key != "source_bundle_fingerprint"
    }
    basket_promotion = fingerprint_payload.get("basket_promotion")
    if isinstance(basket_promotion, dict):
        basket_promotion = copy.deepcopy(basket_promotion)
        basket_promotion.pop("source_bundle_fingerprint", None)
        fingerprint_payload["basket_promotion"] = basket_promotion
    retrieval_provenance = fingerprint_payload.get("retrieval_provenance")
    if isinstance(retrieval_provenance, dict):
        retrieval_provenance = copy.deepcopy(retrieval_provenance)
        retrieval_provenance.pop("source_bundle_fingerprint", None)
        nested_basket_promotion = retrieval_provenance.get("basket_promotion")
        if isinstance(nested_basket_promotion, dict):
            nested_basket_promotion = copy.deepcopy(nested_basket_promotion)
            nested_basket_promotion.pop("source_bundle_fingerprint", None)
            retrieval_provenance["basket_promotion"] = nested_basket_promotion
        fingerprint_payload["retrieval_provenance"] = retrieval_provenance
    existing_source_bundle_fingerprint = _normalize_optional_text(normalized.get("source_bundle_fingerprint"))
    if existing_source_bundle_fingerprint is not None:
        normalized["source_bundle_fingerprint"] = existing_source_bundle_fingerprint
    else:
        normalized["source_bundle_fingerprint"] = _stable_fingerprint(fingerprint_payload)
    if isinstance(normalized.get("basket_promotion"), dict):
        normalized["basket_promotion"]["source_bundle_fingerprint"] = normalized["source_bundle_fingerprint"]
    return normalized


def _build_retrieval_citation_bundle_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return the deterministic citation bundle from a downstream payload snapshot."""

    citation_bundle = payload.get("retrieval_citation_bundle")
    primary_citation_bundle: dict[str, object] = {}
    if isinstance(citation_bundle, dict):
        primary_citation_bundle = _normalize_citation_bundle_snapshot(citation_bundle)

    query = payload.get("query", {})
    if not isinstance(query, dict):
        query = {}
    query_constraints = query.get("constraints", {})
    if not isinstance(query_constraints, dict):
        query_constraints = {}

    provenance = payload.get("retrieval_provenance", {})
    summary = payload.get("retrieval_summary", {})
    diagnostics = payload.get("retrieval_diagnostics", {})
    doc_bundle = payload.get("retrieval_doc_bundle", {})
    excerpt_bundle = payload.get("retrieval_excerpt_bundle", {})
    if not isinstance(provenance, dict):
        provenance = {}
    if not isinstance(summary, dict):
        summary = {}
    if not isinstance(diagnostics, dict):
        diagnostics = {}
    if not isinstance(doc_bundle, dict):
        doc_bundle = {}
    if not isinstance(excerpt_bundle, dict):
        excerpt_bundle = {}
    doc_bundle_manifest = doc_bundle.get("retrieval_manifest", {})
    excerpt_bundle_manifest = excerpt_bundle.get("retrieval_manifest", {})
    if not isinstance(doc_bundle_manifest, dict):
        doc_bundle_manifest = {}
    if not isinstance(excerpt_bundle_manifest, dict):
        excerpt_bundle_manifest = {}
    active_strategy_ids = provenance.get(
        "active_strategy_ids",
        summary.get(
            "active_strategy_ids",
            doc_bundle.get(
                "active_strategy_ids",
                excerpt_bundle.get("active_strategy_ids", diagnostics.get("active_strategy_ids", [])),
            ),
        ),
    )
    deferred_strategy_ids = provenance.get(
        "deferred_strategy_ids",
        summary.get(
            "deferred_strategy_ids",
            doc_bundle.get(
                "deferred_strategy_ids",
                excerpt_bundle.get("deferred_strategy_ids", diagnostics.get("deferred_strategy_ids", [])),
            ),
        ),
    )
    query_scope = _normalize_query_scope(
        query.get(
        "scope",
        provenance.get(
            "query_scope",
            summary.get(
                "query_scope",
                doc_bundle.get(
                    "query_scope",
                    excerpt_bundle.get("query_scope", diagnostics.get("query_scope")),
                ),
            ),
        ),
    )
    )
    query_intent = _normalize_query_intent(
        query.get(
        "intent",
        provenance.get(
            "query_intent",
            summary.get(
                "query_intent",
                doc_bundle.get(
                    "query_intent",
                    excerpt_bundle.get("query_intent", diagnostics.get("query_intent")),
                ),
            ),
        ),
    )
    )
    query_confidentiality_profile = _normalize_query_confidentiality_profile(
        query.get(
            "confidentiality_profile",
            provenance.get(
                "query_confidentiality_profile",
                summary.get(
                    "query_confidentiality_profile",
                    doc_bundle.get(
                        "query_confidentiality_profile",
                        excerpt_bundle.get(
                            "query_confidentiality_profile",
                            diagnostics.get("query_confidentiality_profile"),
                        ),
                    ),
                ),
            ),
        )
    )
    query_date_range = query_constraints.get(
        "date_range",
        provenance.get(
            "query_date_range",
            summary.get(
                "query_date_range",
                doc_bundle.get(
                    "query_date_range",
                    excerpt_bundle.get("query_date_range", diagnostics.get("date_range")),
                ),
            ),
        ),
    )
    query_date_range = _normalize_query_date_range(query_date_range)
    candidate_doc_count = provenance.get(
        "candidate_doc_count",
        summary.get(
            "candidate_doc_count",
            doc_bundle.get(
                "candidate_doc_count",
                excerpt_bundle.get("candidate_doc_count", diagnostics.get("candidate_doc_count")),
            ),
        ),
    )
    fts_shortlist_doc_ids = _normalize_list_like(
        provenance.get(
            "fts_shortlist_doc_ids",
            summary.get(
                "fts_shortlist_doc_ids",
                doc_bundle.get(
                    "fts_shortlist_doc_ids",
                    excerpt_bundle.get("fts_shortlist_doc_ids", diagnostics.get("fts_shortlist_doc_ids", [])),
                ),
            ),
        )
    )
    citation_status = _first_dict_value(
        summary.get("citation_status"),
        doc_bundle.get("citation_status"),
        excerpt_bundle.get("citation_status"),
        provenance.get("citation_status"),
    )
    retrieval_policy = _first_dict_value(
        provenance.get("retrieval_policy"),
        summary.get("retrieval_policy"),
        doc_bundle.get("retrieval_policy"),
        excerpt_bundle.get("retrieval_policy"),
        diagnostics.get("retrieval_policy", {}),
    )
    top_level_doc_hits = payload.get("doc_hits", [])
    top_level_excerpt_hits = payload.get("excerpt_hits", [])
    doc_citations = copy.deepcopy(doc_bundle.get("doc_citations", provenance.get("doc_citations", [])))
    if _is_missing_snapshot_value(doc_citations):
        doc_citations = _derive_doc_citations_from_hits(
            doc_bundle.get("doc_hits", top_level_doc_hits)
        )
    excerpt_citations = copy.deepcopy(excerpt_bundle.get("excerpt_citations", provenance.get("excerpt_citations", [])))
    if _is_missing_snapshot_value(excerpt_citations):
        excerpt_citations = _derive_excerpt_citations_from_hits(
            excerpt_bundle.get("excerpt_hits", top_level_excerpt_hits)
        )
    derived_citation_bundle = _normalize_citation_bundle_snapshot({
        "query_fingerprint": provenance.get(
            "query_fingerprint",
            summary.get(
                "query_fingerprint",
                doc_bundle.get(
                    "query_fingerprint",
                    excerpt_bundle.get("query_fingerprint", diagnostics.get("query_fingerprint")),
                ),
            ),
        ),
        "result_fingerprint": provenance.get(
            "result_fingerprint",
            summary.get(
                "result_fingerprint",
                doc_bundle.get(
                    "result_fingerprint",
                    excerpt_bundle.get("result_fingerprint", diagnostics.get("result_fingerprint")),
                ),
            ),
        ),
        "query_scope": query_scope,
        "query_intent": query_intent,
        "query_confidentiality_profile": query_confidentiality_profile,
        "query_date_range": query_date_range,
        "candidate_doc_count": candidate_doc_count,
        "fts_shortlist_doc_ids": fts_shortlist_doc_ids,
        "retrieval_backend": provenance.get(
            "retrieval_backend",
            summary.get(
                "retrieval_backend",
                doc_bundle.get(
                    "retrieval_backend",
                    excerpt_bundle.get("retrieval_backend", diagnostics.get("retrieval_backend")),
                ),
            ),
        ),
        "retrieval_mode": provenance.get(
            "retrieval_mode",
            summary.get(
                "retrieval_mode",
                doc_bundle.get(
                    "retrieval_mode",
                    excerpt_bundle.get("retrieval_mode", diagnostics.get("retrieval_mode")),
                ),
            ),
        ),
        "retrieval_policy": retrieval_policy or {},
        "active_strategy_ids": _normalize_text_list_like(active_strategy_ids),
        "deferred_strategy_ids": _normalize_text_list_like(deferred_strategy_ids),
        "citation_status": citation_status or {},
        "doc_count": provenance.get("doc_count", summary.get("doc_count", doc_bundle.get("doc_count", len(_normalize_list_like(doc_citations))))),
        "excerpt_count": provenance.get(
            "excerpt_count",
            summary.get("excerpt_count", excerpt_bundle.get("excerpt_count", len(_normalize_list_like(excerpt_citations)))),
        ),
        "doc_hits_fingerprint": provenance.get(
            "doc_hits_fingerprint",
            summary.get(
                "doc_hits_fingerprint",
                doc_bundle_manifest.get("doc_hits_fingerprint", diagnostics.get("doc_hits_fingerprint")),
            ),
        ),
        "excerpt_hits_fingerprint": provenance.get(
            "excerpt_hits_fingerprint",
            summary.get(
                "excerpt_hits_fingerprint",
                excerpt_bundle_manifest.get("excerpt_hits_fingerprint", diagnostics.get("excerpt_hits_fingerprint")),
            ),
        ),
        "doc_citations": doc_citations,
        "excerpt_citations": excerpt_citations,
    })
    if not primary_citation_bundle:
        return derived_citation_bundle
    return _normalize_citation_bundle_snapshot(
        _backfill_sparse_snapshot(primary_citation_bundle, derived_citation_bundle)
    )


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
        "doc_hits": _normalize_doc_hits(payload.get("doc_hits", [])),
        "excerpt_hits": _normalize_excerpt_hits(payload.get("excerpt_hits", [])),
        "retrieval_manifest": copy.deepcopy(payload.get("retrieval_manifest", {})),
        "retrieval_evidence": copy.deepcopy(payload.get("retrieval_evidence", {})),
        "retrieval_provenance": copy.deepcopy(payload.get("retrieval_provenance", {})),
        "basket_promotion": copy.deepcopy(payload.get("basket_promotion", {})),
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
        "source_bundle_fingerprint": context_bundle.get("source_bundle_fingerprint"),
        "retrieval_citation_bundle": context_bundle.get("retrieval_citation_bundle"),
        "retrieval_doc_bundle": context_bundle.get("retrieval_doc_bundle"),
        "retrieval_excerpt_bundle": context_bundle.get("retrieval_excerpt_bundle"),
        "retrieval_provenance": context_bundle.get("retrieval_provenance"),
        "retrieval_source_bundle": context_bundle.get("retrieval_source_bundle"),
        "retrieval_evidence": context_bundle.get("retrieval_evidence"),
        "basket_promotion": context_bundle.get("basket_promotion"),
    }
    return _backfill_sparse_snapshot(
        merged,
        {key: value for key, value in context_backfill.items() if value is not None},
    )


def _build_retrieval_downstream_payload_from_context_bundle(
    context_bundle: dict[str, object],
) -> dict[str, object]:
    """Return the canonical downstream payload from a context-bundle snapshot."""

    payload = {
        "audit_ref": context_bundle.get("audit_ref"),
        "result_fingerprint": context_bundle.get("result_fingerprint"),
        "query_fingerprint": context_bundle.get("query_fingerprint"),
        "source_bundle_fingerprint": context_bundle.get("source_bundle_fingerprint"),
        "query": copy.deepcopy(context_bundle.get("query", {})),
        "policy": copy.deepcopy(context_bundle.get("policy", {})),
        "retrieval_backend": context_bundle.get("retrieval_backend"),
        "retrieval_mode": context_bundle.get("retrieval_mode"),
        "citation_status": copy.deepcopy(context_bundle.get("citation_status", {})),
        "retrieval_summary": copy.deepcopy(context_bundle.get("retrieval_summary", {})),
        "retrieval_citation_bundle": copy.deepcopy(context_bundle.get("retrieval_citation_bundle", {})),
        "retrieval_doc_bundle": copy.deepcopy(context_bundle.get("retrieval_doc_bundle", {})),
        "retrieval_excerpt_bundle": copy.deepcopy(context_bundle.get("retrieval_excerpt_bundle", {})),
        "retrieval_provenance": copy.deepcopy(context_bundle.get("retrieval_provenance", {})),
        "retrieval_source_bundle": copy.deepcopy(context_bundle.get("retrieval_source_bundle", {})),
        "retrieval_evidence": copy.deepcopy(context_bundle.get("retrieval_evidence", {})),
        "basket_promotion": copy.deepcopy(context_bundle.get("basket_promotion", {})),
    }
    return _backfill_downstream_payload_from_context_bundle(payload, context_bundle)


def _build_retrieval_context_bundle_from_source_bundle(source_bundle: dict[str, object]) -> dict[str, object]:
    """Return the deterministic retrieval context bundle from a source-bundle snapshot."""

    source_bundle = _normalize_retrieval_source_bundle_snapshot(source_bundle)
    downstream_payload = _build_retrieval_downstream_payload_from_source_bundle(copy.deepcopy(source_bundle))
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
    basket_promotion = _build_basket_promotion_from_payload(source_bundle)
    query = copy.deepcopy(source_bundle.get("query", {}))
    policy = copy.deepcopy(source_bundle.get("policy", {}))
    citation_status = copy.deepcopy(source_bundle.get("citation_status", {}))
    retrieval_summary = copy.deepcopy(source_bundle.get("retrieval_summary", {}))
    return {
        # Source-bundle-only reconstruction keeps the top-level context auditless.
        "audit_ref": None,
        "result_fingerprint": source_bundle.get("result_fingerprint"),
        "query_fingerprint": source_bundle.get("query_fingerprint"),
        "source_bundle_fingerprint": source_bundle.get("source_bundle_fingerprint"),
        "query": query,
        "policy": policy,
        "retrieval_backend": source_bundle.get("retrieval_backend"),
        "retrieval_mode": source_bundle.get("retrieval_mode"),
        "citation_status": citation_status,
        "retrieval_summary": retrieval_summary,
        "retrieval_downstream_payload": downstream_payload,
        "retrieval_citation_bundle": copy.deepcopy(retrieval_citation_bundle),
        "retrieval_doc_bundle": copy.deepcopy(retrieval_doc_bundle),
        "retrieval_excerpt_bundle": copy.deepcopy(retrieval_excerpt_bundle),
        "retrieval_provenance": copy.deepcopy(retrieval_provenance),
        "retrieval_source_bundle": copy.deepcopy(source_bundle),
        "retrieval_evidence": copy.deepcopy(source_bundle.get("retrieval_evidence", {})),
        "basket_promotion": copy.deepcopy(basket_promotion),
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
        query = _first_dict_value(
            doc_bundle.get("query"),
            excerpt_bundle.get("query"),
            provenance.get("query"),
            summary.get("query"),
        )
    if not isinstance(query, dict):
        query = {}
    query_constraints = query.get("constraints", {})
    if not isinstance(query_constraints, dict):
        query_constraints = {}
    citation_bundle = _build_retrieval_citation_bundle_from_payload(payload)
    query_date_range = _normalize_query_date_range(
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
        "query": _normalize_query_snapshot(query),
        "query_scope": _normalize_query_scope(
            query.get(
                "scope",
                provenance.get("query_scope", summary.get("query_scope", diagnostics.get("query_scope"))),
            )
        ),
        "query_intent": _normalize_query_intent(
            query.get(
                "intent",
                provenance.get("query_intent", summary.get("query_intent", diagnostics.get("query_intent"))),
            )
        ),
        "query_confidentiality_profile": _normalize_query_confidentiality_profile(
            query.get(
                "confidentiality_profile",
                provenance.get(
                    "query_confidentiality_profile",
                    summary.get(
                        "query_confidentiality_profile",
                        diagnostics.get("query_confidentiality_profile"),
                    ),
                ),
            )
        ),
        "query_date_range": query_date_range,
        "retrieval_backend": payload.get("retrieval_backend", summary.get("retrieval_backend", diagnostics.get("retrieval_backend"))),
        "retrieval_mode": payload.get("retrieval_mode", summary.get("retrieval_mode", diagnostics.get("retrieval_mode"))),
        "policy": _normalize_policy_snapshot(
            payload.get(
                "policy",
                payload.get(
                    "retrieval_policy",
                    summary.get("policy", summary.get("retrieval_policy", diagnostics.get("policy", diagnostics.get("retrieval_policy", {})))),
                ),
            )
        ),
        "retrieval_policy": _normalize_policy_snapshot(
            payload.get("retrieval_policy", payload.get("policy", summary.get("retrieval_policy", diagnostics.get("retrieval_policy", {}))))
        ),
        "active_strategy_ids": _normalize_text_list_like(
            provenance.get("active_strategy_ids", summary.get("active_strategy_ids", diagnostics.get("active_strategy_ids", [])))
        ),
        "deferred_strategy_ids": _normalize_text_list_like(
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
        primary_doc_bundle = _normalize_doc_bundle_snapshot(doc_bundle)
        fallback_payload = copy.deepcopy(payload)
        fallback_payload.pop("retrieval_doc_bundle", None)
        if "doc_hits" not in fallback_payload and primary_doc_bundle.get("doc_hits"):
            fallback_payload["doc_hits"] = copy.deepcopy(primary_doc_bundle["doc_hits"])
        fallback_doc_bundle = _build_retrieval_doc_bundle_from_payload(fallback_payload)
        return _normalize_doc_bundle_snapshot(
            _backfill_sparse_snapshot(primary_doc_bundle, fallback_doc_bundle)
        )
    bundle_context = _build_retrieval_bundle_context_from_payload(payload)
    provenance = bundle_context["retrieval_provenance"]
    doc_hits = _normalize_list_like(payload.get("doc_hits", []))
    doc_citations: list[object] = []
    if isinstance(provenance, dict):
        doc_citations = _normalize_list_like(provenance.get("doc_citations", []))
    if not doc_citations and doc_hits:
        doc_citations = _derive_doc_citations_from_hits(doc_hits)
    return _normalize_doc_bundle_snapshot({
        **bundle_context,
        "doc_count": len(doc_hits),
        "doc_hits": doc_hits,
        "doc_citations": doc_citations,
        "basket_promotion": _build_basket_promotion_from_payload(payload),
    })


def _build_retrieval_excerpt_bundle_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return the deterministic excerpt-focused bundle from a downstream payload snapshot."""

    excerpt_bundle = payload.get("retrieval_excerpt_bundle")
    if isinstance(excerpt_bundle, dict):
        primary_excerpt_bundle = _normalize_excerpt_bundle_snapshot(excerpt_bundle)
        fallback_payload = copy.deepcopy(payload)
        fallback_payload.pop("retrieval_excerpt_bundle", None)
        if "excerpt_hits" not in fallback_payload and primary_excerpt_bundle.get("excerpt_hits"):
            fallback_payload["excerpt_hits"] = copy.deepcopy(primary_excerpt_bundle["excerpt_hits"])
        fallback_excerpt_bundle = _build_retrieval_excerpt_bundle_from_payload(fallback_payload)
        return _normalize_excerpt_bundle_snapshot(
            _backfill_sparse_snapshot(primary_excerpt_bundle, fallback_excerpt_bundle)
        )
    bundle_context = _build_retrieval_bundle_context_from_payload(payload)
    provenance = bundle_context["retrieval_provenance"]
    excerpt_hits = _normalize_list_like(payload.get("excerpt_hits", []))
    excerpt_citations: list[object] = []
    if isinstance(provenance, dict):
        excerpt_citations = _normalize_list_like(provenance.get("excerpt_citations", []))
    if not excerpt_citations and excerpt_hits:
        excerpt_citations = _derive_excerpt_citations_from_hits(excerpt_hits)
    return _normalize_excerpt_bundle_snapshot({
        **bundle_context,
        "doc_count": len(_normalize_list_like(payload.get("doc_hits", []))),
        "excerpt_count": len(excerpt_hits) if excerpt_hits else len(excerpt_citations),
        "excerpt_hits": excerpt_hits,
        "excerpt_citations": excerpt_citations,
        "basket_promotion": _build_basket_promotion_from_payload(payload),
    })


def _build_retrieval_context_bundle_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return the deterministic retrieval context bundle from a downstream payload snapshot."""

    retrieval_provenance = _build_retrieval_provenance_from_payload(payload)
    retrieval_summary = _normalize_retrieval_summary_snapshot(payload.get("retrieval_summary", {}))
    retrieval_source_bundle = _build_retrieval_source_bundle_from_payload(payload)
    source_query = retrieval_source_bundle.get("query", {})
    if not isinstance(source_query, dict):
        source_query = {}
    source_policy = retrieval_source_bundle.get("policy", retrieval_source_bundle.get("retrieval_policy", {}))
    if not isinstance(source_policy, dict):
        source_policy = {}
    source_citation_status = retrieval_source_bundle.get("citation_status", {})
    if not isinstance(source_citation_status, dict):
        source_citation_status = {}
    source_evidence = retrieval_source_bundle.get("retrieval_evidence", {})
    if not isinstance(source_evidence, dict):
        source_evidence = {}
    retrieval_backend = _first_text_value(
        payload.get("retrieval_backend"),
        retrieval_source_bundle.get("retrieval_backend"),
        retrieval_summary.get("retrieval_backend"),
        retrieval_provenance.get("retrieval_backend"),
    )
    retrieval_mode = _first_text_value(
        payload.get("retrieval_mode"),
        retrieval_source_bundle.get("retrieval_mode"),
        retrieval_summary.get("retrieval_mode"),
        retrieval_provenance.get("retrieval_mode"),
    )
    policy_snapshot = _normalize_policy_snapshot(
        payload.get("policy", payload.get("retrieval_policy", source_policy))
    )
    return {
        "audit_ref": payload.get("audit_ref"),
        "result_fingerprint": payload.get("result_fingerprint"),
        "query_fingerprint": _first_text_value(
            payload.get("query_fingerprint"),
            retrieval_provenance.get("query_fingerprint"),
            retrieval_summary.get("query_fingerprint"),
        ),
        "source_bundle_fingerprint": _first_text_value(
            payload.get("source_bundle_fingerprint"),
            retrieval_source_bundle.get("source_bundle_fingerprint"),
        ),
        "query": _normalize_query_snapshot(payload.get("query", source_query)),
        "policy": copy.deepcopy(policy_snapshot),
        "retrieval_policy": copy.deepcopy(policy_snapshot),
        "retrieval_backend": retrieval_backend,
        "retrieval_mode": retrieval_mode,
        "citation_status": copy.deepcopy(payload.get("citation_status", source_citation_status)),
        "retrieval_summary": retrieval_summary,
        "retrieval_downstream_payload": copy.deepcopy(payload),
        "retrieval_citation_bundle": _build_retrieval_citation_bundle_from_payload(payload),
        "retrieval_doc_bundle": _build_retrieval_doc_bundle_from_payload(payload),
        "retrieval_excerpt_bundle": _build_retrieval_excerpt_bundle_from_payload(payload),
        "retrieval_provenance": retrieval_provenance,
        "retrieval_source_bundle": retrieval_source_bundle,
        "retrieval_evidence": copy.deepcopy(payload.get("retrieval_evidence", source_evidence)),
        "basket_promotion": _build_basket_promotion_from_payload(payload),
    }


def _build_retrieval_diagnostics_from_source_bundle(source_bundle: dict[str, object]) -> dict[str, object]:
    """Return a best-effort diagnostics snapshot from a source bundle snapshot."""

    normalized = _normalize_retrieval_source_bundle_snapshot(source_bundle)
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
    active_strategy_ids = _normalize_text_list_like(
        citation_bundle.get("active_strategy_ids", retrieval_policy.get("active_strategy_ids", []))
    )
    deferred_strategy_ids = _normalize_text_list_like(
        citation_bundle.get("deferred_strategy_ids", retrieval_policy.get("deferred_strategy_ids", []))
    )
    query_scope = _normalize_query_scope(citation_bundle.get("query_scope", query.get("scope")))
    query_intent = _normalize_query_intent(citation_bundle.get("query_intent", query.get("intent")))
    query_confidentiality_profile = _normalize_query_confidentiality_profile(
        citation_bundle.get(
            "query_confidentiality_profile",
            query.get("confidentiality_profile"),
        )
    )
    query_date_range = _normalize_query_date_range(
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
        "query_fingerprint": citation_bundle.get(
            "query_fingerprint",
            normalized.get("query_fingerprint"),
        ),
        "query_scope": query_scope,
        "query_intent": query_intent,
        "query_confidentiality_profile": query_confidentiality_profile,
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
    query = payload.get("query", {})
    summary = payload.get("retrieval_summary", {})
    diagnostics = payload.get("retrieval_diagnostics", {})
    top_level_doc_hits = payload.get("doc_hits", [])
    top_level_excerpt_hits = payload.get("excerpt_hits", [])
    if not isinstance(query, dict):
        query = {}
    if not isinstance(summary, dict):
        summary = {}
    if not isinstance(diagnostics, dict):
        diagnostics = {}
    if not isinstance(top_level_doc_hits, list):
        top_level_doc_hits = []
    if not isinstance(top_level_excerpt_hits, list):
        top_level_excerpt_hits = []
    query_constraints = query.get("constraints", {})
    if not isinstance(query_constraints, dict):
        query_constraints = {}
    query_date_range = _normalize_query_date_range(normalized.get("query_date_range"))
    if _is_missing_snapshot_value(normalized.get("query_fingerprint")):
        normalized["query_fingerprint"] = summary.get("query_fingerprint", diagnostics.get("query_fingerprint"))
    if _is_missing_snapshot_value(normalized.get("query_scope")):
        normalized["query_scope"] = _normalize_query_scope(
            query.get("scope", summary.get("query_scope", diagnostics.get("query_scope")))
        )
    else:
        normalized["query_scope"] = _normalize_query_scope(normalized.get("query_scope"))
    if _is_missing_snapshot_value(normalized.get("query_intent")):
        normalized["query_intent"] = _normalize_query_intent(
            query.get("intent", summary.get("query_intent", diagnostics.get("query_intent")))
        )
    else:
        normalized["query_intent"] = _normalize_query_intent(normalized.get("query_intent"))
    if _is_missing_snapshot_value(normalized.get("query_confidentiality_profile")):
        normalized["query_confidentiality_profile"] = _normalize_query_confidentiality_profile(
            query.get(
                "confidentiality_profile",
                summary.get(
                    "query_confidentiality_profile",
                    diagnostics.get("query_confidentiality_profile"),
                ),
            )
        )
    else:
        normalized["query_confidentiality_profile"] = _normalize_query_confidentiality_profile(
            normalized.get("query_confidentiality_profile")
        )
    if "query_date_range" not in normalized or _is_missing_snapshot_value(query_date_range):
        normalized["query_date_range"] = _normalize_query_date_range(
            query_constraints.get("date_range", summary.get("query_date_range", diagnostics.get("date_range")))
        )
    else:
        normalized["query_date_range"] = query_date_range
    if _is_missing_snapshot_value(normalized.get("result_fingerprint")):
        normalized["result_fingerprint"] = summary.get("result_fingerprint", diagnostics.get("result_fingerprint"))
    else:
        normalized["result_fingerprint"] = _normalize_optional_text(normalized.get("result_fingerprint"))
    if _is_missing_snapshot_value(normalized.get("query_fingerprint")):
        normalized["query_fingerprint"] = _normalize_optional_text(normalized.get("query_fingerprint"))
    else:
        normalized["query_fingerprint"] = _normalize_optional_text(normalized.get("query_fingerprint"))
    if _is_missing_snapshot_value(normalized.get("retrieval_backend")):
        normalized["retrieval_backend"] = summary.get("retrieval_backend", diagnostics.get("retrieval_backend"))
    normalized["retrieval_backend"] = _normalize_optional_casefold_text(normalized.get("retrieval_backend"))
    if _is_missing_snapshot_value(normalized.get("retrieval_mode")):
        normalized["retrieval_mode"] = summary.get("retrieval_mode", diagnostics.get("retrieval_mode"))
    normalized["retrieval_mode"] = _normalize_optional_casefold_text(normalized.get("retrieval_mode"))
    if _is_missing_snapshot_value(normalized.get("retrieval_policy")):
        normalized["retrieval_policy"] = _normalize_policy_snapshot(
            summary.get("retrieval_policy", diagnostics.get("retrieval_policy", {}))
        )
    else:
        normalized["retrieval_policy"] = _normalize_policy_snapshot(normalized["retrieval_policy"])
    if "active_strategy_ids" not in normalized or _is_missing_snapshot_value(normalized.get("active_strategy_ids")):
        normalized["active_strategy_ids"] = _normalize_text_list_like(
            summary.get("active_strategy_ids", diagnostics.get("active_strategy_ids", []))
        )
    else:
        normalized["active_strategy_ids"] = _normalize_text_list_like(normalized["active_strategy_ids"])
    if "deferred_strategy_ids" not in normalized or _is_missing_snapshot_value(normalized.get("deferred_strategy_ids")):
        normalized["deferred_strategy_ids"] = _normalize_text_list_like(
            summary.get("deferred_strategy_ids", diagnostics.get("deferred_strategy_ids", []))
        )
    else:
        normalized["deferred_strategy_ids"] = _normalize_text_list_like(normalized["deferred_strategy_ids"])
    if _is_missing_snapshot_value(normalized.get("candidate_doc_count")):
        normalized["candidate_doc_count"] = diagnostics.get("candidate_doc_count")
    else:
        normalized["candidate_doc_count"] = _normalize_optional_int(normalized.get("candidate_doc_count"))
    if "fts_shortlist_doc_ids" not in normalized or _is_missing_snapshot_value(normalized.get("fts_shortlist_doc_ids")):
        normalized["fts_shortlist_doc_ids"] = _normalize_text_list_like(
            diagnostics.get("fts_shortlist_doc_ids", [])
        )
    else:
        normalized["fts_shortlist_doc_ids"] = _normalize_text_list_like(normalized["fts_shortlist_doc_ids"])
    if _is_missing_snapshot_value(normalized.get("primary_doc_id")):
        normalized["primary_doc_id"] = summary.get("primary_doc_id")
    else:
        normalized["primary_doc_id"] = _normalize_optional_text(normalized.get("primary_doc_id"))
    if _is_missing_snapshot_value(normalized.get("primary_title_hint")):
        normalized["primary_title_hint"] = summary.get("primary_title_hint")
    else:
        normalized["primary_title_hint"] = _normalize_optional_text(normalized.get("primary_title_hint"))
    if _is_missing_snapshot_value(normalized.get("primary_doc_type")):
        normalized["primary_doc_type"] = None
    else:
        normalized["primary_doc_type"] = _normalize_optional_text(normalized.get("primary_doc_type"))
    if _is_missing_snapshot_value(normalized.get("primary_source_hash")):
        normalized["primary_source_hash"] = None
    else:
        normalized["primary_source_hash"] = _normalize_optional_text(normalized.get("primary_source_hash"))
    if _is_missing_snapshot_value(normalized.get("primary_doc_fingerprint")):
        normalized["primary_doc_fingerprint"] = summary.get("primary_doc_fingerprint")
    else:
        normalized["primary_doc_fingerprint"] = _normalize_optional_text(normalized.get("primary_doc_fingerprint"))
    if _is_missing_snapshot_value(normalized.get("primary_doc_identity_fingerprint")):
        normalized["primary_doc_identity_fingerprint"] = summary.get("primary_doc_identity_fingerprint")
    else:
        normalized["primary_doc_identity_fingerprint"] = _normalize_optional_text(
            normalized.get("primary_doc_identity_fingerprint")
        )
    if _is_missing_snapshot_value(normalized.get("primary_excerpt_id")):
        normalized["primary_excerpt_id"] = summary.get("primary_excerpt_id")
    else:
        normalized["primary_excerpt_id"] = _normalize_optional_text(normalized.get("primary_excerpt_id"))
    if _is_missing_snapshot_value(normalized.get("primary_excerpt_fingerprint")):
        normalized["primary_excerpt_fingerprint"] = summary.get("primary_excerpt_fingerprint")
    else:
        normalized["primary_excerpt_fingerprint"] = _normalize_optional_text(
            normalized.get("primary_excerpt_fingerprint")
        )
    if _is_missing_snapshot_value(normalized.get("primary_excerpt_provenance_fingerprint")):
        normalized["primary_excerpt_provenance_fingerprint"] = summary.get("primary_excerpt_provenance_fingerprint")
    else:
        normalized["primary_excerpt_provenance_fingerprint"] = _normalize_optional_text(
            normalized.get("primary_excerpt_provenance_fingerprint")
        )
    if _is_missing_snapshot_value(normalized.get("primary_excerpt_text_hash")):
        normalized["primary_excerpt_text_hash"] = summary.get("primary_excerpt_text_hash")
    else:
        normalized["primary_excerpt_text_hash"] = _normalize_optional_text(
            normalized.get("primary_excerpt_text_hash")
        )
    if "primary_excerpt_span" not in normalized or _is_missing_snapshot_value(normalized.get("primary_excerpt_span")):
        normalized["primary_excerpt_span"] = None
    else:
        normalized["primary_excerpt_span"] = copy.deepcopy(
            _normalize_span_snapshot(normalized.get("primary_excerpt_span"))
        )
    if _is_missing_snapshot_value(normalized.get("doc_hits_fingerprint")):
        normalized["doc_hits_fingerprint"] = summary.get(
            "doc_hits_fingerprint",
            diagnostics.get("doc_hits_fingerprint"),
        )
    else:
        normalized["doc_hits_fingerprint"] = _normalize_optional_text(normalized.get("doc_hits_fingerprint"))
    if _is_missing_snapshot_value(normalized.get("excerpt_hits_fingerprint")):
        normalized["excerpt_hits_fingerprint"] = summary.get(
            "excerpt_hits_fingerprint",
            diagnostics.get("excerpt_hits_fingerprint"),
        )
    else:
        normalized["excerpt_hits_fingerprint"] = _normalize_optional_text(
            normalized.get("excerpt_hits_fingerprint")
        )
    if _is_missing_snapshot_value(normalized.get("citation_status")):
        normalized["citation_status"] = copy.deepcopy(summary.get("citation_status", {}))
    elif not isinstance(normalized.get("citation_status"), dict):
        normalized["citation_status"] = {}
    else:
        normalized["citation_status"] = copy.deepcopy(normalized.get("citation_status"))
    if _is_missing_snapshot_value(normalized.get("doc_count")):
        normalized["doc_count"] = summary.get("doc_count")
    else:
        normalized["doc_count"] = _normalize_optional_int(normalized.get("doc_count"))
    if _is_missing_snapshot_value(normalized.get("excerpt_count")):
        normalized["excerpt_count"] = summary.get("excerpt_count")
    else:
        normalized["excerpt_count"] = _normalize_optional_int(normalized.get("excerpt_count"))
    citation_bundle = _build_retrieval_citation_bundle_from_payload(payload)
    if _is_missing_snapshot_value(normalized.get("citation_status")):
        normalized["citation_status"] = copy.deepcopy(citation_bundle.get("citation_status", {}))
    if _is_missing_snapshot_value(normalized.get("doc_count")):
        normalized["doc_count"] = citation_bundle.get("doc_count")
    if _is_missing_snapshot_value(normalized.get("excerpt_count")):
        normalized["excerpt_count"] = citation_bundle.get("excerpt_count")
    if _is_missing_snapshot_value(normalized.get("candidate_doc_count")):
        normalized["candidate_doc_count"] = citation_bundle.get("candidate_doc_count")
    if "fts_shortlist_doc_ids" not in normalized or _is_missing_snapshot_value(normalized.get("fts_shortlist_doc_ids")):
        normalized["fts_shortlist_doc_ids"] = _normalize_text_list_like(
            citation_bundle.get("fts_shortlist_doc_ids", normalized.get("fts_shortlist_doc_ids", []))
        )
    doc_citations = citation_bundle.get("doc_citations", [])
    if not isinstance(doc_citations, list):
        doc_citations = []
    excerpt_citations = citation_bundle.get("excerpt_citations", [])
    if not isinstance(excerpt_citations, list):
        excerpt_citations = []
    if "doc_citations" not in normalized or _is_missing_snapshot_value(normalized.get("doc_citations")):
        normalized["doc_citations"] = copy.deepcopy(doc_citations)
    else:
        normalized["doc_citations"] = _normalize_doc_citations(normalized["doc_citations"])
    if "excerpt_citations" not in normalized or _is_missing_snapshot_value(normalized.get("excerpt_citations")):
        normalized["excerpt_citations"] = copy.deepcopy(excerpt_citations)
    else:
        normalized["excerpt_citations"] = _normalize_excerpt_citations(normalized["excerpt_citations"])
    if "retrieved_doc_ids" not in normalized or _is_missing_snapshot_value(normalized.get("retrieved_doc_ids")):
        normalized["retrieved_doc_ids"] = _normalize_text_list_like(
            _first_non_none_value(
                normalized.get("retrieved_doc_ids"),
                summary.get("retrieved_doc_ids"),
                summary.get("doc_ids"),
                [item.get("doc_id") for item in normalized["doc_citations"] if isinstance(item, dict)],
                [item.get("doc_id") for item in top_level_doc_hits if isinstance(item, dict)],
                [item.get("doc_id") for item in top_level_excerpt_hits if isinstance(item, dict)],
            )
        )
    else:
        normalized["retrieved_doc_ids"] = _normalize_text_list_like(normalized["retrieved_doc_ids"])
    if "retrieved_excerpt_ids" not in normalized or _is_missing_snapshot_value(
        normalized.get("retrieved_excerpt_ids")
    ):
        normalized["retrieved_excerpt_ids"] = _normalize_text_list_like(
            _first_non_none_value(
                normalized.get("retrieved_excerpt_ids"),
                summary.get("retrieved_excerpt_ids"),
                summary.get("excerpt_ids"),
                [item.get("excerpt_id") for item in normalized["excerpt_citations"] if isinstance(item, dict)],
                [item.get("excerpt_id") for item in top_level_excerpt_hits if isinstance(item, dict)],
            )
        )
    else:
        normalized["retrieved_excerpt_ids"] = _normalize_text_list_like(normalized["retrieved_excerpt_ids"])
    normalized["basket_promotion"] = _backfill_sparse_snapshot(
        _normalize_basket_promotion_snapshot(normalized.get("basket_promotion")),
        _build_basket_promotion_from_payload(payload),
    )
    if isinstance(normalized["basket_promotion"], dict):
        normalized["basket_promotion"].pop("source_bundle_fingerprint", None)
    if doc_citations:
        first_doc_citation = doc_citations[0]
        if isinstance(first_doc_citation, dict):
            if _is_missing_snapshot_value(normalized.get("primary_doc_id")):
                normalized["primary_doc_id"] = first_doc_citation.get("doc_id")
            if _is_missing_snapshot_value(normalized.get("primary_doc_type")):
                normalized["primary_doc_type"] = first_doc_citation.get("doc_type")
            if _is_missing_snapshot_value(normalized.get("primary_source_hash")):
                normalized["primary_source_hash"] = first_doc_citation.get("source_hash")
            if _is_missing_snapshot_value(normalized.get("primary_doc_fingerprint")):
                normalized["primary_doc_fingerprint"] = first_doc_citation.get("doc_fingerprint")
            if _is_missing_snapshot_value(normalized.get("primary_doc_identity_fingerprint")):
                normalized["primary_doc_identity_fingerprint"] = first_doc_citation.get("doc_identity_fingerprint")
    if excerpt_citations:
        first_excerpt_citation = excerpt_citations[0]
        if isinstance(first_excerpt_citation, dict):
            if _is_missing_snapshot_value(normalized.get("primary_doc_type")):
                normalized["primary_doc_type"] = first_excerpt_citation.get("doc_type")
            if _is_missing_snapshot_value(normalized.get("primary_source_hash")):
                normalized["primary_source_hash"] = first_excerpt_citation.get("source_hash")
            if _is_missing_snapshot_value(normalized.get("primary_excerpt_id")):
                normalized["primary_excerpt_id"] = first_excerpt_citation.get("excerpt_id")
            if _is_missing_snapshot_value(normalized.get("primary_excerpt_fingerprint")):
                normalized["primary_excerpt_fingerprint"] = first_excerpt_citation.get("excerpt_fingerprint")
            if _is_missing_snapshot_value(normalized.get("primary_excerpt_provenance_fingerprint")):
                normalized["primary_excerpt_provenance_fingerprint"] = first_excerpt_citation.get(
                    "excerpt_provenance_fingerprint"
                )
            if _is_missing_snapshot_value(normalized.get("primary_excerpt_text_hash")):
                normalized["primary_excerpt_text_hash"] = first_excerpt_citation.get("excerpt_text_hash")
            if _is_missing_snapshot_value(normalized.get("primary_excerpt_span")):
                normalized["primary_excerpt_span"] = copy.deepcopy(
                    _normalize_span_snapshot(first_excerpt_citation.get("span"))
                )
    if _is_missing_snapshot_value(normalized.get("primary_doc_type")):
        normalized["primary_doc_type"] = normalized["basket_promotion"].get("doc_type")
    if _is_missing_snapshot_value(normalized.get("primary_doc_id")):
        normalized["primary_doc_id"] = normalized["basket_promotion"].get("doc_id")
    if _is_missing_snapshot_value(normalized.get("primary_title_hint")):
        normalized["primary_title_hint"] = normalized["basket_promotion"].get("title_hint")
    if _is_missing_snapshot_value(normalized.get("primary_source_hash")):
        normalized["primary_source_hash"] = normalized["basket_promotion"].get("source_hash")
    if _is_missing_snapshot_value(normalized.get("primary_doc_fingerprint")):
        normalized["primary_doc_fingerprint"] = normalized["basket_promotion"].get("doc_fingerprint")
    if _is_missing_snapshot_value(normalized.get("primary_doc_identity_fingerprint")):
        normalized["primary_doc_identity_fingerprint"] = normalized["basket_promotion"].get(
            "doc_identity_fingerprint"
        )
    if _is_missing_snapshot_value(normalized.get("primary_excerpt_id")):
        normalized["primary_excerpt_id"] = normalized["basket_promotion"].get("excerpt_id")
    if _is_missing_snapshot_value(normalized.get("primary_excerpt_fingerprint")):
        normalized["primary_excerpt_fingerprint"] = normalized["basket_promotion"].get("excerpt_fingerprint")
    if _is_missing_snapshot_value(normalized.get("primary_excerpt_provenance_fingerprint")):
        normalized["primary_excerpt_provenance_fingerprint"] = normalized["basket_promotion"].get(
            "excerpt_provenance_fingerprint"
        )
    if _is_missing_snapshot_value(normalized.get("primary_excerpt_text_hash")):
        normalized["primary_excerpt_text_hash"] = normalized["basket_promotion"].get("excerpt_text_hash")
    if _is_missing_snapshot_value(normalized.get("primary_excerpt_span")):
        normalized["primary_excerpt_span"] = copy.deepcopy(normalized["basket_promotion"].get("span"))
    else:
        normalized["primary_excerpt_span"] = copy.deepcopy(
            _normalize_span_snapshot(normalized.get("primary_excerpt_span"))
        )
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
    basket_promotion: dict[str, object]
    source_bundle_fingerprint: str
    retrieval_source_bundle: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        policy = copy.deepcopy(self.policy)
        diagnostics = copy.deepcopy(self.retrieval_diagnostics)
        manifest = copy.deepcopy(self.retrieval_manifest)
        evidence = copy.deepcopy(self.retrieval_evidence)
        provenance = copy.deepcopy(self.retrieval_provenance)
        basket_promotion = copy.deepcopy(self.basket_promotion)
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
            "basket_promotion": basket_promotion,
            "source_bundle_fingerprint": self.source_bundle_fingerprint,
            "retrieval_source_bundle": source_bundle,
        }


def build_retrieval_provenance_from_result(
    result: RetrievalDownstreamPayloadSource | RetrievalProvenanceBundleSource | RetrievalSourceBundleSource,
) -> dict[str, object]:
    """Return the deterministic retrieval provenance snapshot for a result."""

    provenance_source = getattr(result, "retrieval_provenance_bundle", None)
    if callable(provenance_source):
        source_bundle = _build_retrieval_source_bundle_from_result_source(result)
        if source_bundle is not None:
            primary = _build_retrieval_provenance_from_payload(
                {"retrieval_provenance": provenance_source()}
            )
            fallback = _build_retrieval_provenance_from_payload(source_bundle)
            return _backfill_sparse_snapshot(primary, fallback)
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
    basket_promotion: dict[str, object],
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
        basket_promotion=basket_promotion,
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
            return _build_retrieval_downstream_payload_from_context_bundle(context_bundle)
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
    payload["policy"] = copy.deepcopy(policy_snapshot)
    payload["retrieval_policy"] = copy.deepcopy(policy_snapshot)
    payload["audit_ref"] = payload.get("audit_ref")
    payload["retrieval_diagnostics"] = _build_retrieval_diagnostics_from_source_bundle(normalized)
    payload["retrieval_source_bundle"] = copy.deepcopy(normalized)
    retrieval_doc_bundle = normalized.get("retrieval_doc_bundle")
    if isinstance(retrieval_doc_bundle, dict):
        payload["doc_hits"] = _backfill_top_level_doc_hits_from_bundle_hits(
            payload.get("doc_hits", []),
            retrieval_doc_bundle.get("doc_hits", []),
        )
    retrieval_excerpt_bundle = normalized.get("retrieval_excerpt_bundle")
    if isinstance(retrieval_excerpt_bundle, dict):
        payload["excerpt_hits"] = _backfill_top_level_excerpt_hits_from_bundle_hits(
            payload.get("excerpt_hits", []),
            retrieval_excerpt_bundle.get("excerpt_hits", []),
        )
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
        source_bundle = _build_retrieval_source_bundle_from_result_source(result)
        if source_bundle is not None:
            primary = _build_retrieval_citation_bundle_from_payload(
                {"retrieval_citation_bundle": bundle_source()}
            )
            fallback = _build_retrieval_citation_bundle_from_payload(source_bundle)
            return _normalize_citation_bundle_snapshot(_backfill_sparse_snapshot(primary, fallback))
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
        source_bundle = _build_retrieval_source_bundle_from_result_source(result)
        if source_bundle is not None:
            primary = _build_retrieval_doc_bundle_from_payload(
                {"retrieval_doc_bundle": bundle_source()}
            )
            fallback = _build_retrieval_doc_bundle_from_payload(source_bundle)
            return _normalize_doc_bundle_snapshot(_backfill_sparse_snapshot(primary, fallback))
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
        source_bundle = _build_retrieval_source_bundle_from_result_source(result)
        if source_bundle is not None:
            primary = _build_retrieval_excerpt_bundle_from_payload(
                {"retrieval_excerpt_bundle": bundle_source()}
            )
            fallback = _build_retrieval_excerpt_bundle_from_payload(source_bundle)
            return _normalize_excerpt_bundle_snapshot(_backfill_sparse_snapshot(primary, fallback))
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
            return _build_retrieval_context_bundle_from_payload(
                _build_retrieval_downstream_payload_from_context_bundle(context_bundle)
            )
        return copy.deepcopy(context_bundle)
    source_bundle = _build_retrieval_source_bundle_from_result_source(result)
    if source_bundle is not None:
        return _build_retrieval_context_bundle_from_source_bundle(copy.deepcopy(source_bundle))
    payload = build_retrieval_downstream_payload_from_result(result)
    return _build_retrieval_context_bundle_from_payload(payload)
