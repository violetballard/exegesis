from __future__ import annotations

import copy
import hashlib
import json
import re
import sqlite3
import uuid
from collections.abc import Iterable, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Iterator, Literal, cast

from src.qual.audit import AuditLog
from src.qual.docindex.service import DocIndexBuildOptions, DocIndexService
from src.qual.engine.retrieval import (
    FTS_FIRST_POLICY,
    FTSStrategy,
    build_retrieval_downstream_payload,
    primary_strategy_id,
    retrieval_policy_snapshot,
)
from src.qual.engine.retrieval.interface import StrategyRun
from src.qual.metrics.crypto import decrypt_bytes, encrypt_bytes

_RETRIEVAL_DIR = ".retrieval"
_KEY_FILE = "retrieval_v1.key"
_DOC_META_FILE = "doc_meta_v1.enc.json"
_EXCERPT_CONTEXT_FILE = "excerpt_context_v1.enc.json"
_FTS_DB_FILE = "fts_index_v1.enc.sqlite3"
_DOC_BLOBS = "doc_blobs"
_FTS_SEGMENT_CHARS = 400
_FTS_SEGMENT_OVERLAP_CHARS = 80
_FTS_BOUNDARY_SCAN_CHARS = 40
_SUPPORTED_RETRIEVAL_INTENTS = {"lookup", "compare", "summarize", "quote_find", "outline_support"}
_SUPPORTED_CONFIDENTIALITY_PROFILES = {"confidential", "standard"}
_FTS_SOURCE_STRATEGY = "fts"


def _canonicalize_doc_types(doc_types: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    normalized: list[str] = []
    for doc_type in doc_types:
        value = str(doc_type).strip().casefold()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return tuple(sorted(normalized))


def _optional_text(value: object) -> str | None:
    if isinstance(value, str):
        text = value.strip()
        if text:
            return text
    return None


def _normalized_text(value: object) -> str | None:
    text = _optional_text(value)
    if text is None:
        return None
    return " ".join(text.split())


def _normalized_profile_text(value: object) -> str | None:
    text = _normalized_text(value)
    if text is None:
        return None
    return text.casefold()


def _normalized_query_hint_text(value: object) -> str | None:
    text = _normalized_text(value)
    if text is None:
        return None
    return text.casefold()


def _looks_like_redacted_title_hint(value: object) -> bool:
    text = _optional_text(value)
    if text is None:
        return False
    return bool(re.fullmatch(r"doc:[0-9a-f]{10}", text))


def _normalize_doc_id(value: object) -> str:
    doc_id = _optional_text(value)
    if doc_id is None:
        raise ValueError("doc_id must be a non-empty string")
    return doc_id


def _normalize_excerpt_id(value: object) -> str:
    excerpt_id = _optional_text(value)
    if excerpt_id is None:
        raise ValueError("excerpt_id must be a non-empty string")
    return excerpt_id


def _normalize_doc_type(value: object) -> str:
    doc_type = _normalized_profile_text(value)
    if doc_type is None:
        raise ValueError("doc_type must be a non-empty string")
    return doc_type


def _normalize_source_strategy(value: object) -> Literal["fts"]:
    source_strategy = _normalized_profile_text(value)
    if source_strategy != _FTS_SOURCE_STRATEGY:
        raise ValueError("source_strategy must be fts for the FTS-first retrieval lane")
    return _FTS_SOURCE_STRATEGY


def _resolve_title_hint_confidentiality_profile(*values: object) -> str:
    for value in values:
        normalized = _normalized_profile_text(value)
        if normalized in _SUPPORTED_CONFIDENTIALITY_PROFILES:
            return normalized
    # Fail closed so sparse excerpt rehydration never leaks a raw title hint
    # when the original lookup confidentiality profile is absent.
    return "confidential"


def _optional_int(value: object) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_float(value: object) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_bool(value: object) -> bool | None:
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


def _parse_date_value(value: str) -> date | None:
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None


def _normalize_date_range(value: tuple[str, str]) -> tuple[str, str]:
    start_raw, end_raw = (str(item).strip() for item in value)
    if not start_raw or not end_raw:
        raise ValueError("date_range must contain exactly two non-empty values")

    start_date = _parse_date_value(start_raw)
    end_date = _parse_date_value(end_raw)
    normalized_start = start_date.isoformat() if start_date is not None else start_raw
    normalized_end = end_date.isoformat() if end_date is not None else end_raw
    if start_date is not None and end_date is not None and start_date > end_date:
        return (normalized_end, normalized_start)
    return (normalized_start, normalized_end)


def _normalize_scope(value: object) -> str:
    scope = str(value).strip()
    if not scope:
        raise ValueError("scope must be a non-empty string")

    canonical_scope = scope.casefold()
    if canonical_scope == "vault":
        return "vault"

    prefix, separator, remainder = scope.partition(":")
    if not separator:
        return scope
    normalized_prefix = prefix.strip().casefold()
    if normalized_prefix in {"doc", "collection", "section"}:
        normalized_remainder = remainder.strip()
        if not normalized_remainder:
            raise ValueError(f"{normalized_prefix} scope must include a non-empty identifier")
        return f"{normalized_prefix}:{normalized_remainder}"
    return scope


def _reject_deferred_scope(scope: str) -> str:
    if scope.startswith("section:"):
        raise ValueError("section scope is unsupported until FTS fallback can resolve section targets")
    if scope.startswith("collection:"):
        raise ValueError("collection scope is unsupported until the FTS lane can resolve collection targets")
    return scope


def _optional_list_like(value: object) -> list[object] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return copy.deepcopy(value)
    if isinstance(value, tuple):
        return [copy.deepcopy(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((copy.deepcopy(item) for item in value), key=_stable_sort_key)
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, bytearray, Mapping)):
        return [copy.deepcopy(item) for item in value]
    return [copy.deepcopy(value)]


def _stable_sort_key(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _normalize_supported_value(value: object, *, field_name: str, allowed: set[str]) -> str:
    normalized = str(value).strip().casefold()
    if normalized not in allowed:
        raise ValueError(f"unsupported {field_name}: {normalized}")
    return normalized


def _normalize_matched_terms(value: object) -> list[str] | None:
    raw_items = _optional_list_like(value)
    if raw_items is None:
        return None
    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        text = _normalized_profile_text(item)
        if text is None or text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return normalized


def _normalize_strategy_id_list_payload(value: object) -> list[str]:
    raw_items = _optional_list_like(value)
    if raw_items is None:
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        strategy_id = _normalized_profile_text(item)
        if strategy_id is None or strategy_id in seen:
            continue
        seen.add(strategy_id)
        normalized.append(strategy_id)
    return normalized


def _normalize_retrieval_policy_snapshot_payload(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}
    normalized = {
        "retrieval_backend": _normalized_profile_text(value.get("retrieval_backend")),
        "retrieval_mode": _normalized_profile_text(value.get("retrieval_mode")),
        "active_strategy_ids": _normalize_strategy_id_list_payload(value.get("active_strategy_ids")),
        "deferred_strategy_ids": _normalize_strategy_id_list_payload(value.get("deferred_strategy_ids")),
    }
    return {key: field_value for key, field_value in normalized.items() if field_value is not None}


def _normalize_query_date_range_payload(value: object) -> list[str] | None:
    raw_items = _optional_list_like(value)
    if raw_items is None:
        return None
    normalized = [text for item in raw_items if (text := _optional_text(item)) is not None]
    if not normalized:
        return None
    if len(normalized) != 2:
        return normalized
    return list(_normalize_date_range((normalized[0], normalized[1])))


def _normalize_query_scope_payload(value: object) -> str | None:
    scope = _optional_text(value)
    if scope is None:
        return None
    try:
        return _normalize_scope(scope)
    except ValueError:
        return scope


def _normalize_query_intent_payload(value: object) -> str | None:
    return _normalized_profile_text(value)


def _normalize_query_text_payload(value: object) -> str | None:
    text = _optional_text(value)
    if text is None:
        return None
    return RetrievalService._normalized_query_text(text)


def _normalize_query_doc_types_payload(value: object) -> list[str] | None:
    raw_items = _optional_list_like(value)
    if raw_items is None:
        return None
    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        doc_type = _normalized_profile_text(item)
        if doc_type is None or doc_type in seen:
            continue
        seen.add(doc_type)
        normalized.append(doc_type)
    return sorted(normalized)


def _basket_promotion_query_constraint_snapshot(query: RetrievalQuery) -> dict[str, object]:
    """Return the normalized retrieval constraints carried with basket promotion."""

    constraints: dict[str, object] = {
        "max_results": query.constraints.max_results,
        "doc_types": list(query.constraints.doc_types),
        "require_citations": query.constraints.require_citations,
        "prefer_exact_matches": query.constraints.prefer_exact_matches,
    }
    if query.constraints.date_range is not None:
        constraints["date_range"] = list(query.constraints.date_range)
    if query.constraints.section_hint is not None:
        constraints["section_hint"] = query.constraints.section_hint
    return constraints


def _normalize_hit_shared_provenance_payload(provenance: object) -> dict[str, object]:
    if not isinstance(provenance, dict):
        return {}
    normalized = copy.deepcopy(provenance)
    query_fingerprint = _optional_text(normalized.get("query_fingerprint"))
    if query_fingerprint is not None:
        normalized["query_fingerprint"] = query_fingerprint
    query_scope = _normalize_query_scope_payload(normalized.get("query_scope"))
    if query_scope is not None:
        normalized["query_scope"] = query_scope
    query_intent = _normalize_query_intent_payload(normalized.get("query_intent"))
    if query_intent is not None:
        normalized["query_intent"] = query_intent
    query_confidentiality_profile = _normalized_profile_text(
        normalized.get("query_confidentiality_profile")
    )
    if query_confidentiality_profile is not None:
        normalized["query_confidentiality_profile"] = query_confidentiality_profile
    query_date_range = _normalize_query_date_range_payload(normalized.get("query_date_range"))
    if query_date_range is not None:
        normalized["query_date_range"] = query_date_range
    candidate_doc_count = _optional_int(normalized.get("candidate_doc_count"))
    if candidate_doc_count is not None:
        normalized["candidate_doc_count"] = candidate_doc_count
    fts_shortlist_doc_ids = _normalize_doc_id_list_payload(normalized.get("fts_shortlist_doc_ids"))
    if fts_shortlist_doc_ids is not None:
        normalized["fts_shortlist_doc_ids"] = fts_shortlist_doc_ids
    retrieval_backend = _normalized_profile_text(normalized.get("retrieval_backend"))
    if retrieval_backend is not None:
        normalized["retrieval_backend"] = retrieval_backend
    retrieval_mode = _normalized_profile_text(normalized.get("retrieval_mode"))
    if retrieval_mode is not None:
        normalized["retrieval_mode"] = retrieval_mode
    retrieval_policy = _normalize_retrieval_policy_snapshot_payload(
        normalized.get("retrieval_policy", normalized.get("policy"))
    )
    if retrieval_policy:
        normalized["retrieval_policy"] = retrieval_policy
        normalized["policy"] = copy.deepcopy(retrieval_policy)
    normalized["active_strategy_ids"] = _normalize_strategy_id_list_payload(
        normalized.get("active_strategy_ids")
    )
    normalized["deferred_strategy_ids"] = _normalize_strategy_id_list_payload(
        normalized.get("deferred_strategy_ids")
    )
    normalized["strategies_used"] = _normalize_strategy_id_list_payload(
        normalized.get("strategies_used")
    )
    retrieved_doc_ids = _normalize_doc_id_list_payload(normalized.get("retrieved_doc_ids"))
    if retrieved_doc_ids is not None:
        normalized["retrieved_doc_ids"] = retrieved_doc_ids
    retrieved_excerpt_ids = _normalize_doc_id_list_payload(normalized.get("retrieved_excerpt_ids"))
    if retrieved_excerpt_ids is not None:
        normalized["retrieved_excerpt_ids"] = retrieved_excerpt_ids
    return normalized


def _normalize_excerpt_hit_provenance_payload(provenance: object) -> dict[str, object]:
    normalized = _normalize_hit_shared_provenance_payload(provenance)
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
        field_value = _optional_text(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
    excerpt_text_hash = _optional_text(
        normalized.get("excerpt_text_hash") or normalized.get("hash")
    )
    if excerpt_text_hash is not None:
        normalized["excerpt_text_hash"] = excerpt_text_hash
        normalized["hash"] = excerpt_text_hash
    matched_terms = _normalize_matched_terms(normalized.get("matched_terms"))
    if matched_terms is not None:
        normalized["matched_terms"] = matched_terms
        normalized["match_count"] = len(matched_terms)
    match_count = _optional_int(normalized.get("match_count"))
    if match_count is not None:
        normalized["match_count"] = match_count
    rank = _optional_int(normalized.get("rank"))
    if rank is not None:
        normalized["rank"] = rank
    fts_rank = _optional_float(normalized.get("fts_rank"))
    if fts_rank is not None:
        normalized["fts_rank"] = fts_rank
    section_hint = _normalized_query_hint_text(normalized.get("section_hint"))
    if section_hint is not None:
        normalized["section_hint"] = section_hint
    section_hint_rank = _optional_int(normalized.get("section_hint_rank"))
    if section_hint_rank is not None:
        normalized["section_hint_rank"] = section_hint_rank
    source_strategy = _normalized_profile_text(
        normalized.get("source_strategy") or normalized.get("retrieval_source_strategy")
    )
    if source_strategy is not None:
        normalized["source_strategy"] = source_strategy
        normalized["retrieval_source_strategy"] = source_strategy
    return normalized


def _normalize_doc_hit_provenance_payload(provenance: object) -> dict[str, object]:
    normalized = _normalize_hit_shared_provenance_payload(provenance)
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
        field_value = _optional_text(normalized.get(field_name))
        if field_value is not None:
            normalized[field_name] = field_value
    top_excerpt_text_hash = _optional_text(
        normalized.get("top_excerpt_text_hash") or normalized.get("top_excerpt_hash")
    )
    if top_excerpt_text_hash is not None:
        normalized["top_excerpt_text_hash"] = top_excerpt_text_hash
        normalized["top_excerpt_hash"] = top_excerpt_text_hash
    doc_rank = _optional_int(normalized.get("doc_rank"))
    if doc_rank is not None:
        normalized["doc_rank"] = doc_rank
    top_excerpt_rank = _optional_int(normalized.get("top_excerpt_rank"))
    if top_excerpt_rank is not None:
        normalized["top_excerpt_rank"] = top_excerpt_rank
    top_fts_rank = _optional_float(normalized.get("top_fts_rank"))
    if top_fts_rank is not None:
        normalized["top_fts_rank"] = top_fts_rank
    top_excerpt_span = RetrievalService._canonicalize_span(normalized.get("top_excerpt_span"))
    if top_excerpt_span is not None:
        normalized["top_excerpt_span"] = top_excerpt_span
    excerpt_ids = _normalize_doc_id_list_payload(normalized.get("excerpt_ids"))
    if excerpt_ids is not None:
        normalized["excerpt_ids"] = excerpt_ids
    top_matched_terms = _normalize_matched_terms(
        normalized.get("top_matched_terms") or normalized.get("matched_terms")
    )
    if top_matched_terms is not None:
        normalized["top_matched_terms"] = top_matched_terms
        normalized["top_match_count"] = len(top_matched_terms)
    top_match_count = _optional_int(normalized.get("top_match_count"))
    if top_match_count is not None:
        normalized["top_match_count"] = top_match_count
    section_hint = _normalized_query_hint_text(normalized.get("section_hint"))
    if section_hint is not None:
        normalized["section_hint"] = section_hint
    top_section_hint_rank = _optional_int(normalized.get("top_section_hint_rank"))
    if top_section_hint_rank is not None:
        normalized["top_section_hint_rank"] = top_section_hint_rank
    source_strategy = _normalized_profile_text(
        normalized.get("source_strategy") or normalized.get("retrieval_source_strategy")
    )
    if source_strategy is not None:
        normalized["source_strategy"] = source_strategy
        normalized["retrieval_source_strategy"] = source_strategy
    return normalized


def _normalize_lookup_resolution_payload(value: object) -> str | None:
    return _normalized_profile_text(value)


def _normalize_lookup_resolution(value: object) -> Literal["fts"]:
    lookup_resolution = _normalize_lookup_resolution_payload(value)
    if lookup_resolution != _FTS_SOURCE_STRATEGY:
        raise ValueError("lookup_resolution must be fts for the FTS-first retrieval lane")
    return _FTS_SOURCE_STRATEGY


def _normalize_lookup_confidentiality_profile_payload(value: object) -> str | None:
    return _normalized_profile_text(value)


def _normalize_doc_id_list_payload(value: object) -> list[str] | None:
    raw_items = _optional_list_like(value)
    if raw_items is None:
        return None
    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        doc_id = _optional_text(item)
        if doc_id is None or doc_id in seen:
            continue
        seen.add(doc_id)
        normalized.append(doc_id)
    # Preserve the FTS shortlist order so excerpt lookups and basket promotion
    # keep the same auditable candidate ordering as the canonical retrieval run.
    return normalized


def _normalized_doc_id_list_snapshot(value: object) -> list[str]:
    normalized = _normalize_doc_id_list_payload(value)
    if normalized is None:
        return []
    return normalized


@dataclass(frozen=True)
class RetrievalConstraints:
    max_results: int = 10
    doc_types: tuple[str, ...] = ()
    date_range: tuple[str, str] | None = None
    require_citations: bool = False
    section_hint: str | None = None
    prefer_exact_matches: bool = False

    def __post_init__(self) -> None:
        if self.max_results < 1:
            raise ValueError("max_results must be greater than zero")
        object.__setattr__(self, "doc_types", _canonicalize_doc_types(self.doc_types))
        if self.date_range is not None:
            normalized = tuple(str(value).strip() for value in self.date_range)
            if len(normalized) != 2:
                raise ValueError("date_range must contain exactly two non-empty values")
            object.__setattr__(self, "date_range", _normalize_date_range(normalized))
        # Normalize hint casing up front so engine-facing payloads, provenance,
        # and fingerprints stay aligned for equivalent retrieval queries.
        object.__setattr__(self, "section_hint", _normalized_query_hint_text(self.section_hint))


@dataclass(frozen=True)
class RetrievalQuery:
    query_text: str
    scope: str
    intent: Literal["lookup", "compare", "summarize", "quote_find", "outline_support"]
    constraints: RetrievalConstraints = field(default_factory=RetrievalConstraints)
    confidentiality_profile: Literal["confidential", "standard"] = "confidential"

    def __post_init__(self) -> None:
        normalized_query_text = _normalized_text(self.query_text)
        if normalized_query_text is None:
            raise ValueError("query_text is required")
        object.__setattr__(self, "query_text", normalized_query_text)
        object.__setattr__(self, "scope", _reject_deferred_scope(_normalize_scope(self.scope)))
        object.__setattr__(
            self,
            "intent",
            _normalize_supported_value(
                self.intent,
                field_name="intent",
                allowed=_SUPPORTED_RETRIEVAL_INTENTS,
            ),
        )
        object.__setattr__(
            self,
            "confidentiality_profile",
            _normalize_supported_value(
                self.confidentiality_profile,
                field_name="confidentiality_profile",
                allowed=_SUPPORTED_CONFIDENTIALITY_PROFILES,
            ),
        )


@dataclass(frozen=True)
class RetrievalHit:
    doc_id: str
    excerpt_id: str | None
    excerpt_text: str | None
    span: dict[str, object]
    title_hint: str | None
    score: float
    source_strategy: Literal["fts"]
    rationale: str | None
    node_path: list[dict[str, str]] | None
    provenance: dict[str, object]

    def __post_init__(self) -> None:
        if self.source_strategy != _FTS_SOURCE_STRATEGY:
            raise ValueError("source_strategy must be fts for the FTS-first retrieval lane")
        # Snapshot mutable payload fields at construction time so downstream
        # engine consumers cannot accidentally mutate the canonical retrieval
        # result by holding on to caller-owned dict/list instances.
        object.__setattr__(self, "span", copy.deepcopy(self.span))
        object.__setattr__(self, "node_path", copy.deepcopy(self.node_path))
        # Normalize loose dict-shaped provenance so compatibility shims and any
        # hit rehydration still emit the canonical deterministic FTS contract.
        object.__setattr__(self, "provenance", _normalize_excerpt_hit_provenance_payload(self.provenance))

    def as_dict(self) -> dict[str, object]:
        payload = {
            "doc_id": self.doc_id,
            "excerpt_id": self.excerpt_id,
            "excerpt_text": self.excerpt_text,
            "span": copy.deepcopy(self.span),
            "title_hint": self.title_hint,
            "score": self.score,
            "source_strategy": self.source_strategy,
            "retrieval_source_strategy": self.source_strategy,
            "rationale": self.rationale,
            "node_path": copy.deepcopy(self.node_path),
            "provenance": copy.deepcopy(self.provenance),
        }
        query_fingerprint = self.provenance.get("query_fingerprint")
        if isinstance(query_fingerprint, str) and query_fingerprint:
            payload["query_fingerprint"] = query_fingerprint
        query_scope = self.provenance.get("query_scope")
        if isinstance(query_scope, str) and query_scope:
            payload["query_scope"] = query_scope
        query_intent = self.provenance.get("query_intent")
        if isinstance(query_intent, str) and query_intent:
            payload["query_intent"] = query_intent
        query_confidentiality_profile = _normalized_profile_text(
            self.provenance.get("query_confidentiality_profile")
        )
        if query_confidentiality_profile is not None:
            payload["query_confidentiality_profile"] = query_confidentiality_profile
        query_date_range = self.provenance.get("query_date_range")
        normalized_query_date_range = _optional_list_like(query_date_range)
        if normalized_query_date_range is not None:
            payload["query_date_range"] = normalized_query_date_range
        source_hash = self.provenance.get("source_hash")
        if isinstance(source_hash, str) and source_hash:
            payload["source_hash"] = source_hash
        doc_type = self.provenance.get("doc_type")
        if isinstance(doc_type, str) and doc_type:
            payload["doc_type"] = doc_type
        candidate_doc_count = self.provenance.get("candidate_doc_count")
        if isinstance(candidate_doc_count, int):
            payload["candidate_doc_count"] = candidate_doc_count
        fts_shortlist_doc_ids = self.provenance.get("fts_shortlist_doc_ids")
        normalized_fts_shortlist_doc_ids = _optional_list_like(fts_shortlist_doc_ids)
        if normalized_fts_shortlist_doc_ids is not None:
            payload["fts_shortlist_doc_ids"] = normalized_fts_shortlist_doc_ids
        retrieval_backend = self.provenance.get("retrieval_backend")
        if isinstance(retrieval_backend, str) and retrieval_backend:
            payload["retrieval_backend"] = retrieval_backend
        retrieval_mode = self.provenance.get("retrieval_mode")
        if isinstance(retrieval_mode, str) and retrieval_mode:
            payload["retrieval_mode"] = retrieval_mode
        doc_fingerprint = self.provenance.get("doc_fingerprint")
        if isinstance(doc_fingerprint, str) and doc_fingerprint:
            payload["doc_fingerprint"] = doc_fingerprint
        doc_identity_fingerprint = self.provenance.get("doc_identity_fingerprint")
        if isinstance(doc_identity_fingerprint, str) and doc_identity_fingerprint:
            payload["doc_identity_fingerprint"] = doc_identity_fingerprint
        excerpt_fingerprint = self.provenance.get("excerpt_fingerprint")
        if isinstance(excerpt_fingerprint, str) and excerpt_fingerprint:
            payload["excerpt_fingerprint"] = excerpt_fingerprint
        excerpt_provenance_fingerprint = self.provenance.get("excerpt_provenance_fingerprint")
        if isinstance(excerpt_provenance_fingerprint, str) and excerpt_provenance_fingerprint:
            payload["excerpt_provenance_fingerprint"] = excerpt_provenance_fingerprint
        excerpt_text_hash = self.provenance.get("excerpt_text_hash") or self.provenance.get("hash")
        if isinstance(excerpt_text_hash, str) and excerpt_text_hash:
            payload["excerpt_text_hash"] = excerpt_text_hash
        rank = self.provenance.get("rank")
        if isinstance(rank, int):
            payload["rank"] = rank
        fts_rank = self.provenance.get("fts_rank")
        if isinstance(fts_rank, (int, float)):
            payload["fts_rank"] = fts_rank
        matched_terms = self.provenance.get("matched_terms")
        if isinstance(matched_terms, list):
            payload["matched_terms"] = copy.deepcopy(matched_terms)
        match_count = self.provenance.get("match_count")
        if isinstance(match_count, int):
            payload["match_count"] = match_count
        section_hint = self.provenance.get("section_hint")
        if isinstance(section_hint, str) and section_hint:
            payload["section_hint"] = section_hint
        section_hint_rank = self.provenance.get("section_hint_rank")
        if isinstance(section_hint_rank, int):
            payload["section_hint_rank"] = section_hint_rank
        retrieval_backend = self.provenance.get("retrieval_backend")
        if isinstance(retrieval_backend, str) and retrieval_backend:
            payload["retrieval_backend"] = retrieval_backend
        retrieval_mode = self.provenance.get("retrieval_mode")
        if isinstance(retrieval_mode, str) and retrieval_mode:
            payload["retrieval_mode"] = retrieval_mode
        retrieval_policy = self.provenance.get("retrieval_policy", self.provenance.get("policy"))
        if isinstance(retrieval_policy, dict):
            payload["retrieval_policy"] = copy.deepcopy(retrieval_policy)
        active_strategy_ids = _optional_list_like(self.provenance.get("active_strategy_ids"))
        if active_strategy_ids is not None:
            payload["active_strategy_ids"] = active_strategy_ids
        deferred_strategy_ids = _optional_list_like(self.provenance.get("deferred_strategy_ids"))
        if deferred_strategy_ids is not None:
            payload["deferred_strategy_ids"] = deferred_strategy_ids
        strategies_used = _optional_list_like(self.provenance.get("strategies_used"))
        if strategies_used is not None:
            payload["strategies_used"] = strategies_used
        retrieved_doc_ids = _optional_list_like(self.provenance.get("retrieved_doc_ids"))
        if retrieved_doc_ids is not None:
            payload["retrieved_doc_ids"] = retrieved_doc_ids
        retrieved_excerpt_ids = _optional_list_like(self.provenance.get("retrieved_excerpt_ids"))
        if retrieved_excerpt_ids is not None:
            payload["retrieved_excerpt_ids"] = retrieved_excerpt_ids
        return payload


@dataclass(frozen=True)
class RetrievalDocHit:
    doc_id: str
    title_hint: str | None
    source_hash: str
    top_excerpt_id: str | None
    top_score: float
    source_strategy: Literal["fts"]
    excerpt_count: int
    provenance: dict[str, object]

    def __post_init__(self) -> None:
        if self.source_strategy != _FTS_SOURCE_STRATEGY:
            raise ValueError("source_strategy must be fts for the FTS-first retrieval lane")
        object.__setattr__(self, "provenance", _normalize_doc_hit_provenance_payload(self.provenance))

    def as_dict(self) -> dict[str, object]:
        payload = {
            "doc_id": self.doc_id,
            "title_hint": self.title_hint,
            "source_hash": self.source_hash,
            "top_excerpt_id": self.top_excerpt_id,
            "top_score": self.top_score,
            "source_strategy": self.source_strategy,
            "retrieval_source_strategy": self.source_strategy,
            "excerpt_count": self.excerpt_count,
            "provenance": copy.deepcopy(self.provenance),
        }
        query_fingerprint = self.provenance.get("query_fingerprint")
        if isinstance(query_fingerprint, str) and query_fingerprint:
            payload["query_fingerprint"] = query_fingerprint
        query_scope = self.provenance.get("query_scope")
        if isinstance(query_scope, str) and query_scope:
            payload["query_scope"] = query_scope
        query_intent = self.provenance.get("query_intent")
        if isinstance(query_intent, str) and query_intent:
            payload["query_intent"] = query_intent
        query_confidentiality_profile = _normalized_profile_text(
            self.provenance.get("query_confidentiality_profile")
        )
        if query_confidentiality_profile is not None:
            payload["query_confidentiality_profile"] = query_confidentiality_profile
        query_date_range = self.provenance.get("query_date_range")
        normalized_query_date_range = _optional_list_like(query_date_range)
        if normalized_query_date_range is not None:
            payload["query_date_range"] = normalized_query_date_range
        candidate_doc_count = self.provenance.get("candidate_doc_count")
        if isinstance(candidate_doc_count, int):
            payload["candidate_doc_count"] = candidate_doc_count
        fts_shortlist_doc_ids = self.provenance.get("fts_shortlist_doc_ids")
        normalized_fts_shortlist_doc_ids = _optional_list_like(fts_shortlist_doc_ids)
        if normalized_fts_shortlist_doc_ids is not None:
            payload["fts_shortlist_doc_ids"] = normalized_fts_shortlist_doc_ids
        retrieval_backend = self.provenance.get("retrieval_backend")
        if isinstance(retrieval_backend, str) and retrieval_backend:
            payload["retrieval_backend"] = retrieval_backend
        retrieval_mode = self.provenance.get("retrieval_mode")
        if isinstance(retrieval_mode, str) and retrieval_mode:
            payload["retrieval_mode"] = retrieval_mode
        doc_rank = self.provenance.get("doc_rank")
        if isinstance(doc_rank, int):
            payload["doc_rank"] = doc_rank
        doc_type = self.provenance.get("doc_type")
        if isinstance(doc_type, str) and doc_type:
            payload["doc_type"] = doc_type
        doc_fingerprint = self.provenance.get("doc_fingerprint")
        if isinstance(doc_fingerprint, str) and doc_fingerprint:
            payload["doc_fingerprint"] = doc_fingerprint
        doc_identity_fingerprint = self.provenance.get("doc_identity_fingerprint")
        if isinstance(doc_identity_fingerprint, str) and doc_identity_fingerprint:
            payload["doc_identity_fingerprint"] = doc_identity_fingerprint
        top_excerpt_fingerprint = self.provenance.get("top_excerpt_fingerprint")
        if isinstance(top_excerpt_fingerprint, str) and top_excerpt_fingerprint:
            payload["top_excerpt_fingerprint"] = top_excerpt_fingerprint
        top_excerpt_provenance_fingerprint = self.provenance.get("top_excerpt_provenance_fingerprint")
        if isinstance(top_excerpt_provenance_fingerprint, str) and top_excerpt_provenance_fingerprint:
            payload["top_excerpt_provenance_fingerprint"] = top_excerpt_provenance_fingerprint
        top_excerpt_text_hash = self.provenance.get("top_excerpt_text_hash") or self.provenance.get(
            "top_excerpt_hash"
        )
        if isinstance(top_excerpt_text_hash, str) and top_excerpt_text_hash:
            payload["top_excerpt_text_hash"] = top_excerpt_text_hash
            payload["top_excerpt_hash"] = top_excerpt_text_hash
        top_excerpt_span = self.provenance.get("top_excerpt_span")
        if isinstance(top_excerpt_span, dict):
            payload["top_excerpt_span"] = copy.deepcopy(top_excerpt_span)
        top_excerpt_rank = self.provenance.get("top_excerpt_rank")
        if isinstance(top_excerpt_rank, int):
            payload["top_excerpt_rank"] = top_excerpt_rank
        top_matched_terms = self.provenance.get("top_matched_terms")
        if isinstance(top_matched_terms, list):
            payload["top_matched_terms"] = copy.deepcopy(top_matched_terms)
        top_match_count = self.provenance.get("top_match_count")
        if isinstance(top_match_count, int):
            payload["top_match_count"] = top_match_count
        section_hint = self.provenance.get("section_hint")
        if isinstance(section_hint, str) and section_hint:
            payload["section_hint"] = section_hint
        top_section_hint_rank = self.provenance.get("top_section_hint_rank")
        if isinstance(top_section_hint_rank, int):
            payload["top_section_hint_rank"] = top_section_hint_rank
        top_fts_rank = self.provenance.get("top_fts_rank")
        if isinstance(top_fts_rank, (int, float)):
            payload["top_fts_rank"] = top_fts_rank
        retrieval_backend = self.provenance.get("retrieval_backend")
        if isinstance(retrieval_backend, str) and retrieval_backend:
            payload["retrieval_backend"] = retrieval_backend
        retrieval_mode = self.provenance.get("retrieval_mode")
        if isinstance(retrieval_mode, str) and retrieval_mode:
            payload["retrieval_mode"] = retrieval_mode
        retrieval_policy = self.provenance.get("retrieval_policy", self.provenance.get("policy"))
        if isinstance(retrieval_policy, dict):
            payload["retrieval_policy"] = copy.deepcopy(retrieval_policy)
        active_strategy_ids = _optional_list_like(self.provenance.get("active_strategy_ids"))
        if active_strategy_ids is not None:
            payload["active_strategy_ids"] = active_strategy_ids
        deferred_strategy_ids = _optional_list_like(self.provenance.get("deferred_strategy_ids"))
        if deferred_strategy_ids is not None:
            payload["deferred_strategy_ids"] = deferred_strategy_ids
        strategies_used = _optional_list_like(self.provenance.get("strategies_used"))
        if strategies_used is not None:
            payload["strategies_used"] = strategies_used
        retrieved_doc_ids = _optional_list_like(self.provenance.get("retrieved_doc_ids"))
        if retrieved_doc_ids is not None:
            payload["retrieved_doc_ids"] = retrieved_doc_ids
        retrieved_excerpt_ids = _optional_list_like(self.provenance.get("retrieved_excerpt_ids"))
        if retrieved_excerpt_ids is not None:
            payload["retrieved_excerpt_ids"] = retrieved_excerpt_ids
        return payload


@dataclass(frozen=True)
class RetrievalResult:
    query: RetrievalQuery
    doc_hits: list[RetrievalDocHit]
    hits: list[RetrievalHit]
    diagnostics: dict[str, object]
    evidence: dict[str, object]
    audit_ref: str
    result_fingerprint: str

    def __post_init__(self) -> None:
        # Snapshot mutable collections at construction time so result-level
        # fingerprints, provenance, and basket-promotion payloads stay stable
        # even if the caller later mutates the objects originally passed in.
        object.__setattr__(self, "doc_hits", copy.deepcopy(self.doc_hits))
        object.__setattr__(self, "hits", copy.deepcopy(self.hits))
        object.__setattr__(self, "diagnostics", copy.deepcopy(self.diagnostics))
        object.__setattr__(self, "evidence", copy.deepcopy(self.evidence))

    def to_downstream_payload(self) -> dict[str, object]:
        """Return the stable retrieval contract for drafting/patching/research.

        The payload keeps the canonical query, policy, doc hits, excerpt hits,
        manifest, and evidence in one deterministic structure so downstream
        engine flows do not have to reassemble or reinterpret retrieval state.
        """
        query = self._query_snapshot()
        retrieval_policy = self._retrieval_policy_snapshot()
        citation_bundle = self.citation_bundle()
        retrieval_doc_bundle = self.retrieval_doc_bundle()
        retrieval_excerpt_bundle = self.retrieval_excerpt_bundle()
        citation_status = dict(citation_bundle["citation_status"])
        retrieval_summary = self._retrieval_summary_snapshot(
            retrieval_policy=retrieval_policy,
            citation_status=citation_status,
        )
        retrieval_provenance = self._retrieval_provenance_snapshot(
            citation_bundle=citation_bundle,
            citation_status=citation_status,
            retrieval_policy=retrieval_policy,
        )
        basket_promotion = self._basket_promotion_snapshot()
        retrieval_source_bundle = self._retrieval_source_bundle_snapshot(
            query=query,
            retrieval_policy=retrieval_policy,
            citation_bundle=citation_bundle,
            citation_status=citation_status,
            retrieval_summary=retrieval_summary,
            retrieval_doc_bundle=retrieval_doc_bundle,
            retrieval_excerpt_bundle=retrieval_excerpt_bundle,
            retrieval_provenance=retrieval_provenance,
            basket_promotion=basket_promotion,
        )
        basket_promotion = copy.deepcopy(retrieval_source_bundle["basket_promotion"])
        return build_retrieval_downstream_payload(
            query=query,
            policy=retrieval_policy,
            audit_ref=self.audit_ref,
            result_fingerprint=self.result_fingerprint,
            retrieval_backend=self.diagnostics["retrieval_backend"],
            retrieval_mode=self.diagnostics["retrieval_mode"],
            citation_status=citation_status,
            retrieval_citation_bundle=citation_bundle,
            retrieval_doc_bundle=retrieval_doc_bundle,
            retrieval_excerpt_bundle=retrieval_excerpt_bundle,
            retrieval_summary=retrieval_summary,
            doc_hits=[doc_hit.as_dict() for doc_hit in self.doc_hits],
            excerpt_hits=[hit.as_dict() for hit in self.hits],
            retrieval_diagnostics=self._public_diagnostics_snapshot(),
            retrieval_manifest=dict(self.diagnostics["retrieval_manifest"]),
            retrieval_evidence=dict(self.evidence),
            retrieval_provenance=retrieval_provenance,
            basket_promotion=basket_promotion,
            source_bundle_fingerprint=cast(str, retrieval_source_bundle["source_bundle_fingerprint"]),
            retrieval_source_bundle=retrieval_source_bundle,
        )

    def citation_bundle(self) -> dict[str, object]:
        """Return deterministic doc/excerpt citations and query context for downstream flows."""
        active_strategy_ids = list(self.diagnostics["active_strategy_ids"])
        deferred_strategy_ids = list(self.diagnostics["deferred_strategy_ids"])
        citation_status = self._citation_status_snapshot()
        query_date_range = (
            list(self.query.constraints.date_range)
            if self.query.constraints.date_range is not None
            else None
        )
        fts_shortlist_doc_ids = _normalized_doc_id_list_snapshot(self.diagnostics.get("fts_shortlist_doc_ids"))
        return {
            "query_fingerprint": self.diagnostics["query_fingerprint"],
            "result_fingerprint": self.result_fingerprint,
            "query_scope": self.query.scope,
            "query_intent": self.query.intent,
            "query_confidentiality_profile": self.query.confidentiality_profile,
            "query_date_range": query_date_range,
            "candidate_doc_count": self.diagnostics.get("candidate_doc_count"),
            "fts_shortlist_doc_ids": fts_shortlist_doc_ids,
            "retrieval_backend": self.diagnostics["retrieval_backend"],
            "retrieval_mode": self.diagnostics["retrieval_mode"],
            "policy": copy.deepcopy(self.diagnostics["retrieval_policy"]),
            "retrieval_policy": copy.deepcopy(self.diagnostics["retrieval_policy"]),
            "active_strategy_ids": active_strategy_ids,
            "deferred_strategy_ids": deferred_strategy_ids,
            "citation_status": citation_status,
            "doc_count": len(self.doc_hits),
            "excerpt_count": len(self.hits),
            "doc_hits_fingerprint": self.diagnostics["doc_hits_fingerprint"],
            "excerpt_hits_fingerprint": self.diagnostics["excerpt_hits_fingerprint"],
            "doc_citations": self._doc_citation_snapshots(),
            "excerpt_citations": self._excerpt_citation_snapshots(),
        }

    def retrieval_citation_bundle(self) -> dict[str, object]:
        """Return the canonical citation snapshot for downstream engine flows."""

        return self.citation_bundle()

    def as_downstream_payload(self) -> dict[str, object]:
        """Return the canonical downstream payload using result-oriented naming."""

        return self.to_downstream_payload()

    def as_dict(self) -> dict[str, object]:
        """Return the canonical downstream payload using dict-oriented naming.

        Retrieval consumers already treat hits and doc hits as dict-shaped
        snapshots. Keeping a plain ``as_dict`` alias on the result object makes
        the retrieval contract easier to consume in generic code without
        changing the underlying payload shape.
        """

        return self.to_downstream_payload()

    def source_bundle(self) -> dict[str, object]:
        """Return the deterministic retrieval source snapshot for downstream engine flows."""

        return self._retrieval_source_bundle_snapshot()

    def retrieval_source_bundle(self) -> dict[str, object]:
        """Return the canonical retrieval source snapshot for downstream engine flows."""

        return self.source_bundle()

    def retrieval_provenance_bundle(self) -> dict[str, object]:
        """Return the deterministic retrieval provenance snapshot for downstream engine flows."""
        citation_bundle = self.citation_bundle()
        citation_status = dict(citation_bundle["citation_status"])
        basket_promotion = self._basket_promotion_snapshot()
        return copy.deepcopy(
            self._retrieval_provenance_snapshot(
                citation_bundle=citation_bundle,
                citation_status=citation_status,
                retrieval_policy=self._retrieval_policy_snapshot(),
                basket_promotion=basket_promotion,
            )
        )

    def retrieval_doc_bundle(self) -> dict[str, object]:
        """Return the deterministic doc-focused snapshot for downstream engine flows."""

        bundle_context = self._retrieval_bundle_context_snapshot()
        return {
            **bundle_context,
            "doc_count": len(self.doc_hits),
            "doc_hits": [doc_hit.as_dict() for doc_hit in self.doc_hits],
            "doc_citations": self._doc_citation_snapshots(),
            "basket_promotion": copy.deepcopy(bundle_context["basket_promotion"]),
        }

    def retrieval_excerpt_bundle(self) -> dict[str, object]:
        """Return the deterministic excerpt-focused snapshot for downstream engine flows."""

        bundle_context = self._retrieval_bundle_context_snapshot()
        return {
            **bundle_context,
            "doc_count": len(self.doc_hits),
            "excerpt_count": len(self.hits),
            "excerpt_hits": [hit.as_dict() for hit in self.hits],
            "excerpt_citations": self._excerpt_citation_snapshots(),
            "basket_promotion": copy.deepcopy(bundle_context["basket_promotion"]),
        }

    def retrieval_context_bundle(self) -> dict[str, object]:
        """Return the canonical retrieval context for drafting, patching, and research flows."""

        downstream_payload = self.to_downstream_payload()
        source_bundle_fingerprint = downstream_payload["source_bundle_fingerprint"]
        return {
            "audit_ref": self.audit_ref,
            "result_fingerprint": self.result_fingerprint,
            "query_fingerprint": self.diagnostics["query_fingerprint"],
            "source_bundle_fingerprint": source_bundle_fingerprint,
            "query": copy.deepcopy(downstream_payload["query"]),
            "policy": copy.deepcopy(downstream_payload["policy"]),
            "retrieval_policy": copy.deepcopy(downstream_payload["retrieval_policy"]),
            "retrieval_backend": self.diagnostics["retrieval_backend"],
            "retrieval_mode": self.diagnostics["retrieval_mode"],
            "citation_status": copy.deepcopy(downstream_payload["citation_status"]),
            "retrieval_summary": copy.deepcopy(downstream_payload["retrieval_summary"]),
            "retrieval_downstream_payload": copy.deepcopy(downstream_payload),
            "retrieval_citation_bundle": copy.deepcopy(downstream_payload["retrieval_citation_bundle"]),
            "retrieval_doc_bundle": copy.deepcopy(downstream_payload["retrieval_doc_bundle"]),
            "retrieval_excerpt_bundle": copy.deepcopy(downstream_payload["retrieval_excerpt_bundle"]),
            "retrieval_provenance": copy.deepcopy(downstream_payload["retrieval_provenance"]),
            "retrieval_source_bundle": copy.deepcopy(downstream_payload["retrieval_source_bundle"]),
            "retrieval_evidence": copy.deepcopy(downstream_payload["retrieval_evidence"]),
            # Promote the canonical basket-ready record to the top level so
            # engine flows do not have to unpack the full downstream payload
            # before pinning retrieved context into the basket.
            "basket_promotion": copy.deepcopy(downstream_payload["basket_promotion"]),
        }

    def _query_snapshot(self) -> dict[str, object]:
        return {
            # Keep exported retrieval snapshots stable across whitespace-only
            # query variants that already share fingerprints and hit ordering.
            "query_text": RetrievalService._normalized_query_text(self.query.query_text),
            "scope": self.query.scope,
            "intent": self.query.intent,
            "constraints": {
                "max_results": self.query.constraints.max_results,
                "doc_types": list(self.query.constraints.doc_types),
                "date_range": list(self.query.constraints.date_range) if self.query.constraints.date_range is not None else None,
                "require_citations": self.query.constraints.require_citations,
                "section_hint": self.query.constraints.section_hint,
                "prefer_exact_matches": self.query.constraints.prefer_exact_matches,
            },
            "confidentiality_profile": self.query.confidentiality_profile,
        }

    def _retrieval_policy_snapshot(self) -> dict[str, object]:
        return copy.deepcopy(self.diagnostics["retrieval_policy"])

    def _public_diagnostics_snapshot(self) -> dict[str, object]:
        diagnostics = copy.deepcopy(self.diagnostics)
        strategies_used = diagnostics.get("strategies_used", [])
        if not isinstance(strategies_used, list):
            strategies_used = []
        # Keep the downstream retrieval contract deterministic across repeated
        # runs of the same query. Runtime timing stays available in audit
        # events, but engine-facing payloads should not drift on wall-clock
        # measurements alone.
        diagnostics["elapsed_ms_by_strategy"] = {str(strategy_id): 0 for strategy_id in strategies_used}
        diagnostics["elapsed_ms_total"] = 0
        diagnostics["caches_used"] = {str(strategy_id): False for strategy_id in strategies_used}
        return diagnostics

    def _citation_status_snapshot(self) -> dict[str, object]:
        return {
            "required": self.query.constraints.require_citations,
            "available": bool(self.hits),
            "satisfied": (not self.query.constraints.require_citations) or bool(self.hits),
            "doc_count": len(self.doc_hits),
            "excerpt_count": len(self.hits),
        }

    def _doc_citation_snapshots(self) -> list[dict[str, object]]:
        citations: list[dict[str, object]] = []
        for doc_hit in self.doc_hits:
            citation = {
                "doc_id": doc_hit.doc_id,
                "doc_type": doc_hit.provenance.get("doc_type"),
                "source_hash": doc_hit.source_hash,
                "doc_fingerprint": doc_hit.provenance.get("doc_fingerprint"),
                "doc_identity_fingerprint": doc_hit.provenance.get("doc_identity_fingerprint"),
                "doc_rank": doc_hit.provenance.get("doc_rank"),
                "top_excerpt_id": doc_hit.top_excerpt_id,
                "top_excerpt_fingerprint": doc_hit.provenance.get("top_excerpt_fingerprint"),
                "top_excerpt_text_hash": doc_hit.provenance.get("top_excerpt_text_hash"),
                "top_excerpt_span": copy.deepcopy(doc_hit.provenance.get("top_excerpt_span")),
                "top_excerpt_rank": doc_hit.provenance.get("top_excerpt_rank"),
                "top_fts_rank": doc_hit.provenance.get("top_fts_rank"),
                "excerpt_ids": copy.deepcopy(doc_hit.provenance.get("excerpt_ids")),
                "excerpt_count": doc_hit.excerpt_count,
                "matched_terms": copy.deepcopy(doc_hit.provenance.get("top_matched_terms")),
                "source_strategy": doc_hit.provenance.get("source_strategy"),
                "retrieval_backend": doc_hit.provenance.get("retrieval_backend"),
                "retrieval_mode": doc_hit.provenance.get("retrieval_mode"),
            }
            section_hint = doc_hit.provenance.get("section_hint")
            if isinstance(section_hint, str) and section_hint:
                citation["section_hint"] = section_hint
            top_section_hint_rank = doc_hit.provenance.get("top_section_hint_rank")
            if isinstance(top_section_hint_rank, int):
                citation["top_section_hint_rank"] = top_section_hint_rank
            citations.append(citation)
        return citations

    def _excerpt_citation_snapshots(self) -> list[dict[str, object]]:
        citations: list[dict[str, object]] = []
        for hit in self.hits:
            if hit.excerpt_id is None:
                continue
            citation = {
                "doc_id": hit.doc_id,
                "excerpt_id": hit.excerpt_id,
                "doc_type": hit.provenance.get("doc_type"),
                "source_hash": hit.provenance.get("source_hash"),
                "excerpt_fingerprint": hit.provenance.get("excerpt_fingerprint"),
                "excerpt_provenance_fingerprint": hit.provenance.get("excerpt_provenance_fingerprint"),
                "excerpt_text_hash": hit.provenance.get("excerpt_text_hash") or hit.provenance.get("hash"),
                "match_count": hit.provenance.get("match_count"),
                "matched_terms": copy.deepcopy(hit.provenance.get("matched_terms")),
                "fts_rank": hit.provenance.get("fts_rank"),
                "rank": hit.provenance.get("rank"),
                "span": copy.deepcopy(hit.provenance.get("span")),
                "source_strategy": hit.provenance.get("source_strategy"),
                "retrieval_backend": hit.provenance.get("retrieval_backend"),
                "retrieval_mode": hit.provenance.get("retrieval_mode"),
            }
            section_hint = hit.provenance.get("section_hint")
            if isinstance(section_hint, str) and section_hint:
                citation["section_hint"] = section_hint
            section_hint_rank = hit.provenance.get("section_hint_rank")
            if isinstance(section_hint_rank, int):
                citation["section_hint_rank"] = section_hint_rank
            citations.append(citation)
        return citations

    def _retrieval_summary_snapshot(
        self,
        *,
        retrieval_policy: dict[str, object],
        citation_status: dict[str, object],
    ) -> dict[str, object]:
        doc_fingerprints = [_optional_text(doc_hit.provenance.get("doc_fingerprint")) for doc_hit in self.doc_hits]
        doc_identity_fingerprints = [
            _optional_text(doc_hit.provenance.get("doc_identity_fingerprint")) for doc_hit in self.doc_hits
        ]
        top_excerpt_fingerprints = [
            _optional_text(doc_hit.provenance.get("top_excerpt_fingerprint")) for doc_hit in self.doc_hits
        ]
        top_excerpt_text_hashes = [
            _optional_text(doc_hit.provenance.get("top_excerpt_text_hash")) for doc_hit in self.doc_hits
        ]
        excerpt_fingerprints = [
            _optional_text(hit.provenance.get("excerpt_fingerprint")) for hit in self.hits if hit.excerpt_id is not None
        ]
        excerpt_text_hashes = [
            _optional_text(hit.provenance.get("excerpt_text_hash") or hit.provenance.get("hash"))
            for hit in self.hits
            if hit.excerpt_id is not None
        ]
        fts_shortlist_doc_ids = _normalized_doc_id_list_snapshot(self.diagnostics.get("fts_shortlist_doc_ids"))
        return {
            "query_fingerprint": self.diagnostics["query_fingerprint"],
            "result_fingerprint": self.result_fingerprint,
            "query_scope": self.query.scope,
            "query_intent": self.query.intent,
            "query_confidentiality_profile": self.query.confidentiality_profile,
            "query_date_range": (
                list(self.query.constraints.date_range)
                if self.query.constraints.date_range is not None
                else None
            ),
            "retrieval_backend": self.diagnostics["retrieval_backend"],
            "retrieval_mode": self.diagnostics["retrieval_mode"],
            "retrieval_policy": copy.deepcopy(retrieval_policy),
            "candidate_doc_count": self.diagnostics.get("candidate_doc_count"),
            "fts_shortlist_count": len(fts_shortlist_doc_ids),
            "fts_shortlist_doc_ids": fts_shortlist_doc_ids,
            "doc_count": len(self.doc_hits),
            "excerpt_count": len(self.hits),
            "doc_ids": [doc_hit.doc_id for doc_hit in self.doc_hits],
            # Mirror the ranked retrieval order under explicit keys so basket
            # promotion and later workflow stages do not need to infer that
            # ordering from the generic doc/excerpt ID lists.
            "retrieved_doc_ids": [doc_hit.doc_id for doc_hit in self.doc_hits],
            "doc_fingerprints": doc_fingerprints,
            "doc_identity_fingerprints": doc_identity_fingerprints,
            "excerpt_ids": [hit.excerpt_id for hit in self.hits if hit.excerpt_id is not None],
            "retrieved_excerpt_ids": [hit.excerpt_id for hit in self.hits if hit.excerpt_id is not None],
            "excerpt_fingerprints": excerpt_fingerprints,
            "excerpt_text_hashes": excerpt_text_hashes,
            "top_excerpt_ids": [doc_hit.top_excerpt_id for doc_hit in self.doc_hits],
            "top_excerpt_fingerprints": top_excerpt_fingerprints,
            "top_excerpt_text_hashes": top_excerpt_text_hashes,
            "primary_doc_id": self.doc_hits[0].doc_id if self.doc_hits else None,
            "primary_excerpt_id": self.hits[0].excerpt_id if self.hits else None,
            "primary_title_hint": (
                self.hits[0].title_hint
                if self.hits
                else self.doc_hits[0].title_hint if self.doc_hits else None
            ),
            "primary_doc_fingerprint": self.doc_hits[0].provenance.get("doc_fingerprint") if self.doc_hits else None,
            "primary_doc_identity_fingerprint": self.doc_hits[0].provenance.get("doc_identity_fingerprint")
            if self.doc_hits
            else None,
            "primary_excerpt_fingerprint": self.hits[0].provenance.get("excerpt_fingerprint") if self.hits else None,
            "primary_excerpt_provenance_fingerprint": (
                self.hits[0].provenance.get("excerpt_provenance_fingerprint") if self.hits else None
            ),
            "primary_excerpt_text_hash": (
                self.hits[0].provenance.get("excerpt_text_hash") or self.hits[0].provenance.get("hash")
                if self.hits
                else None
            ),
            "doc_hits_fingerprint": self.diagnostics["doc_hits_fingerprint"],
            "excerpt_hits_fingerprint": self.diagnostics["excerpt_hits_fingerprint"],
            "active_strategy_ids": list(self.diagnostics["active_strategy_ids"]),
            "deferred_strategy_ids": list(self.diagnostics["deferred_strategy_ids"]),
            "citation_status": citation_status,
        }

    def _retrieval_provenance_snapshot(
        self,
        *,
        citation_bundle: dict[str, object],
        citation_status: dict[str, object],
        retrieval_policy: dict[str, object],
        basket_promotion: dict[str, object] | None = None,
    ) -> dict[str, object]:
        primary_doc_hit = self.doc_hits[0] if self.doc_hits else None
        primary_excerpt_hit = self.hits[0] if self.hits else None
        primary_doc_provenance = primary_doc_hit.provenance if primary_doc_hit is not None else {}
        primary_excerpt_provenance = primary_excerpt_hit.provenance if primary_excerpt_hit is not None else {}
        basket_promotion_snapshot = (
            copy.deepcopy(basket_promotion)
            if basket_promotion is not None
            else self._basket_promotion_snapshot()
        )
        return {
            "query_fingerprint": self.diagnostics["query_fingerprint"],
            "query_scope": self.query.scope,
            "query_intent": self.query.intent,
            "query_confidentiality_profile": self.query.confidentiality_profile,
            "query_date_range": (
                list(self.query.constraints.date_range)
                if self.query.constraints.date_range is not None
                else None
            ),
            "result_fingerprint": self.result_fingerprint,
            "retrieval_backend": self.diagnostics["retrieval_backend"],
            "retrieval_mode": self.diagnostics["retrieval_mode"],
            "policy": copy.deepcopy(retrieval_policy),
            "retrieval_policy": retrieval_policy,
            "active_strategy_ids": list(self.diagnostics["active_strategy_ids"]),
            "deferred_strategy_ids": list(self.diagnostics["deferred_strategy_ids"]),
            "doc_hits_fingerprint": self.diagnostics["doc_hits_fingerprint"],
            "excerpt_hits_fingerprint": self.diagnostics["excerpt_hits_fingerprint"],
            "candidate_doc_count": self.diagnostics.get("candidate_doc_count"),
            "fts_shortlist_doc_ids": _normalized_doc_id_list_snapshot(self.diagnostics.get("fts_shortlist_doc_ids")),
            "primary_doc_id": primary_doc_hit.doc_id if primary_doc_hit is not None else None,
            "primary_doc_type": (
                primary_doc_provenance.get("doc_type")
                or primary_excerpt_provenance.get("doc_type")
            ),
            "primary_title_hint": (
                primary_excerpt_hit.title_hint
                if primary_excerpt_hit is not None
                else primary_doc_hit.title_hint if primary_doc_hit is not None else None
            ),
            "primary_source_hash": (
                primary_excerpt_provenance.get("source_hash")
                or primary_doc_provenance.get("source_hash")
            ),
            "primary_doc_fingerprint": primary_doc_provenance.get("doc_fingerprint")
            if primary_doc_hit is not None
            else primary_excerpt_provenance.get("doc_fingerprint"),
            "primary_doc_identity_fingerprint": primary_doc_provenance.get("doc_identity_fingerprint")
            if primary_doc_hit is not None
            else primary_excerpt_provenance.get("doc_identity_fingerprint"),
            "primary_excerpt_id": primary_excerpt_hit.excerpt_id if primary_excerpt_hit is not None else None,
            "primary_excerpt_fingerprint": primary_excerpt_hit.provenance.get("excerpt_fingerprint")
            if primary_excerpt_hit is not None
            else None,
            "primary_excerpt_provenance_fingerprint": (
                primary_excerpt_hit.provenance.get("excerpt_provenance_fingerprint")
                if primary_excerpt_hit is not None
                else None
            ),
            "primary_excerpt_text_hash": (
                primary_excerpt_hit.provenance.get("excerpt_text_hash") or primary_excerpt_hit.provenance.get("hash")
                if primary_excerpt_hit is not None
                else None
            ),
            "primary_excerpt_span": (
                copy.deepcopy(primary_excerpt_provenance.get("span"))
                if primary_excerpt_hit is not None
                else None
            ),
            "citation_status": citation_status,
            "doc_count": citation_bundle["doc_count"],
            "excerpt_count": citation_bundle["excerpt_count"],
            "retrieved_doc_ids": [doc_hit.doc_id for doc_hit in self.doc_hits],
            "retrieved_excerpt_ids": [hit.excerpt_id for hit in self.hits if hit.excerpt_id is not None],
            "doc_citations": citation_bundle["doc_citations"],
            "excerpt_citations": citation_bundle["excerpt_citations"],
            "basket_promotion": basket_promotion_snapshot,
        }

    def _retrieval_bundle_context_snapshot(self) -> dict[str, object]:
        """Return the shared retrieval snapshot fields used by doc and excerpt bundles."""

        query_date_range = (
            list(self.query.constraints.date_range)
            if self.query.constraints.date_range is not None
            else None
        )
        citation_bundle = self.citation_bundle()
        citation_status = dict(citation_bundle["citation_status"])
        retrieval_policy = self._retrieval_policy_snapshot()
        basket_promotion = self._basket_promotion_snapshot()
        retrieval_provenance = self._retrieval_provenance_snapshot(
            citation_bundle=citation_bundle,
            citation_status=citation_status,
            retrieval_policy=retrieval_policy,
            basket_promotion=basket_promotion,
        )
        return {
            "result_fingerprint": self.result_fingerprint,
            "query_fingerprint": self.diagnostics["query_fingerprint"],
            "query": self._query_snapshot(),
            "query_scope": self.query.scope,
            "query_intent": self.query.intent,
            "query_confidentiality_profile": self.query.confidentiality_profile,
            "query_date_range": query_date_range,
            "retrieval_backend": self.diagnostics["retrieval_backend"],
            "retrieval_mode": self.diagnostics["retrieval_mode"],
            "policy": copy.deepcopy(retrieval_policy),
            "retrieval_policy": copy.deepcopy(retrieval_policy),
            "active_strategy_ids": list(self.diagnostics["active_strategy_ids"]),
            "deferred_strategy_ids": list(self.diagnostics["deferred_strategy_ids"]),
            "citation_status": citation_status,
            # Keep the citation bundle inline so doc/excerpt snapshots remain
            # self-contained for downstream drafting and patching flows.
            "retrieval_citation_bundle": copy.deepcopy(citation_bundle),
            "retrieval_manifest": copy.deepcopy(self.diagnostics["retrieval_manifest"]),
            "retrieval_provenance": copy.deepcopy(retrieval_provenance),
            "retrieval_evidence": copy.deepcopy(self.evidence),
            # Keep the basket-ready promotion record next to the narrower
            # doc/excerpt bundles so basket/context consumers do not need the
            # larger downstream payload to pin retrieved material.
            "basket_promotion": copy.deepcopy(basket_promotion),
        }

    def _basket_promotion_snapshot(self) -> dict[str, object]:
        primary_doc_hit = self.doc_hits[0] if self.doc_hits else None
        primary_excerpt_hit = self.hits[0] if self.hits else None
        primary_doc_provenance = primary_doc_hit.provenance if primary_doc_hit is not None else {}
        primary_excerpt_provenance = primary_excerpt_hit.provenance if primary_excerpt_hit is not None else {}
        retrieval_policy = copy.deepcopy(self.diagnostics["retrieval_policy"])
        promotion_source = "none"
        if primary_excerpt_hit is not None:
            promotion_source = "primary_ranked_excerpt"
        elif primary_doc_hit is not None:
            promotion_source = "primary_ranked_doc"
        promotion = {
            "promotion_ready": primary_excerpt_hit is not None or primary_doc_hit is not None,
            "promotion_source": promotion_source,
            # Doc-ranked promotions still carry stable doc citations, so
            # basket/context consumers should treat them as auditable too.
            "citation_available": primary_excerpt_hit is not None or primary_doc_hit is not None,
            # Keep the normalized query text inline so basket promotion can be
            # replayed without unpacking the larger retrieval query payload.
            "query_text": RetrievalService._normalized_query_text(self.query.query_text),
            "query_fingerprint": self.diagnostics["query_fingerprint"],
            "query_scope": self.diagnostics["query_scope"],
            "query_intent": self.diagnostics["query_intent"],
            "query_confidentiality_profile": self.diagnostics["query_confidentiality_profile"],
            "query_constraints": _basket_promotion_query_constraint_snapshot(self.query),
            "query_max_results": self.query.constraints.max_results,
            "query_doc_types": list(self.query.constraints.doc_types),
            "query_require_citations": self.query.constraints.require_citations,
            "query_prefer_exact_matches": self.query.constraints.prefer_exact_matches,
            "query_date_range": copy.deepcopy(self.diagnostics["date_range"]),
            "candidate_doc_count": self.diagnostics["candidate_doc_count"],
            "fts_shortlist_doc_ids": _normalized_doc_id_list_snapshot(self.diagnostics.get("fts_shortlist_doc_ids")),
            "result_fingerprint": self.result_fingerprint,
            "doc_id": (
                primary_excerpt_hit.doc_id
                if primary_excerpt_hit is not None
                else primary_doc_hit.doc_id if primary_doc_hit is not None else None
            ),
            "doc_type": primary_excerpt_provenance.get("doc_type") or primary_doc_provenance.get("doc_type"),
            "doc_fingerprint": primary_doc_provenance.get("doc_fingerprint")
            or primary_excerpt_provenance.get("doc_fingerprint"),
            "doc_identity_fingerprint": primary_doc_provenance.get("doc_identity_fingerprint")
            or primary_excerpt_provenance.get("doc_identity_fingerprint"),
            "source_hash": primary_excerpt_provenance.get("source_hash")
            or primary_doc_provenance.get("source_hash"),
            "title_hint": (
                primary_excerpt_hit.title_hint
                if primary_excerpt_hit is not None
                else primary_doc_hit.title_hint if primary_doc_hit is not None else None
            ),
            "excerpt_id": primary_excerpt_hit.excerpt_id if primary_excerpt_hit is not None else None,
            "excerpt_fingerprint": primary_excerpt_provenance.get("excerpt_fingerprint")
            if primary_excerpt_hit is not None
            else None,
            "excerpt_provenance_fingerprint": (
                primary_excerpt_provenance.get("excerpt_provenance_fingerprint")
                if primary_excerpt_hit is not None
                else primary_doc_provenance.get("top_excerpt_provenance_fingerprint")
            ),
            "excerpt_text_hash": (
                primary_excerpt_provenance.get("excerpt_text_hash") or primary_excerpt_provenance.get("hash")
                if primary_excerpt_hit is not None
                else None
            ),
            "excerpt_text": primary_excerpt_hit.excerpt_text if primary_excerpt_hit is not None else None,
            "span": copy.deepcopy(primary_excerpt_hit.span) if primary_excerpt_hit is not None else None,
            "source_strategy": (
                primary_excerpt_hit.source_strategy
                if primary_excerpt_hit is not None
                else primary_doc_hit.source_strategy if primary_doc_hit is not None else None
            ),
            "matched_terms": copy.deepcopy(
                primary_excerpt_provenance.get("matched_terms")
                if primary_excerpt_hit is not None
                else primary_doc_provenance.get("top_matched_terms")
            ),
            "match_count": (
                primary_excerpt_provenance.get("match_count")
                if primary_excerpt_hit is not None
                else primary_doc_provenance.get("top_match_count")
            ),
            "rank": (
                primary_excerpt_provenance.get("rank")
                if primary_excerpt_hit is not None
                else primary_doc_provenance.get("top_excerpt_rank")
            ),
            "fts_rank": (
                primary_excerpt_provenance.get("fts_rank")
                if primary_excerpt_hit is not None
                else primary_doc_provenance.get("top_fts_rank")
            ),
            "doc_rank": primary_doc_provenance.get("doc_rank"),
            "section_hint": (
                primary_excerpt_provenance.get("section_hint")
                if primary_excerpt_hit is not None
                else primary_doc_provenance.get("section_hint")
            ),
            "section_hint_rank": (
                primary_excerpt_provenance.get("section_hint_rank")
                if primary_excerpt_hit is not None
                else primary_doc_provenance.get("top_section_hint_rank")
            ),
            "retrieval_backend": self.diagnostics["retrieval_backend"],
            "retrieval_mode": self.diagnostics["retrieval_mode"],
            "policy": copy.deepcopy(retrieval_policy),
            "retrieval_policy": retrieval_policy,
            "active_strategy_ids": list(self.diagnostics["active_strategy_ids"]),
            "deferred_strategy_ids": list(self.diagnostics["deferred_strategy_ids"]),
            "strategies_used": list(self.diagnostics["strategies_used"]),
            # Keep the ranked retrieval ids next to the primary promotion record
            # so basket/context consumers can preserve the authoritative FTS
            # ordering without unpacking the larger retrieval summary payload.
            "retrieved_doc_ids": [doc_hit.doc_id for doc_hit in self.doc_hits],
            "retrieved_excerpt_ids": [hit.excerpt_id for hit in self.hits if hit.excerpt_id is not None],
        }
        promotion["promotion_fingerprint"] = RetrievalService._build_basket_promotion_fingerprint(promotion)
        return promotion

    def _retrieval_source_bundle_snapshot(
        self,
        *,
        query: dict[str, object] | None = None,
        retrieval_policy: dict[str, object] | None = None,
        citation_bundle: dict[str, object] | None = None,
        citation_status: dict[str, object] | None = None,
        retrieval_summary: dict[str, object] | None = None,
        retrieval_doc_bundle: dict[str, object] | None = None,
        retrieval_excerpt_bundle: dict[str, object] | None = None,
        retrieval_provenance: dict[str, object] | None = None,
        basket_promotion: dict[str, object] | None = None,
    ) -> dict[str, object]:
        query_snapshot = query if query is not None else self._query_snapshot()
        retrieval_policy_snapshot = retrieval_policy if retrieval_policy is not None else self._retrieval_policy_snapshot()
        citation_bundle_snapshot = citation_bundle if citation_bundle is not None else self.citation_bundle()
        citation_status_snapshot = citation_status if citation_status is not None else self._citation_status_snapshot()
        retrieval_summary_snapshot = (
            retrieval_summary
            if retrieval_summary is not None
            else self._retrieval_summary_snapshot(
                retrieval_policy=retrieval_policy_snapshot,
                citation_status=citation_status_snapshot,
            )
        )
        basket_promotion_snapshot = (
            basket_promotion if basket_promotion is not None else self._basket_promotion_snapshot()
        )
        retrieval_doc_bundle_snapshot = (
            copy.deepcopy(retrieval_doc_bundle)
            if retrieval_doc_bundle is not None
            else copy.deepcopy(self.retrieval_doc_bundle())
        )
        retrieval_excerpt_bundle_snapshot = (
            copy.deepcopy(retrieval_excerpt_bundle)
            if retrieval_excerpt_bundle is not None
            else copy.deepcopy(self.retrieval_excerpt_bundle())
        )
        retrieval_provenance_snapshot = (
            copy.deepcopy(retrieval_provenance)
            if retrieval_provenance is not None
            else copy.deepcopy(
                self._retrieval_provenance_snapshot(
                    citation_bundle=citation_bundle_snapshot,
                    citation_status=citation_status_snapshot,
                    retrieval_policy=retrieval_policy_snapshot,
                    basket_promotion=basket_promotion_snapshot,
                )
            )
        )
        source_bundle = {
            "result_fingerprint": self.result_fingerprint,
            "query_fingerprint": self.diagnostics["query_fingerprint"],
            "query": query_snapshot,
            "policy": copy.deepcopy(retrieval_policy_snapshot),
            "retrieval_policy": copy.deepcopy(retrieval_policy_snapshot),
            "retrieval_backend": self.diagnostics["retrieval_backend"],
            "retrieval_mode": self.diagnostics["retrieval_mode"],
            "citation_status": copy.deepcopy(citation_status_snapshot),
            "retrieval_citation_bundle": copy.deepcopy(citation_bundle_snapshot),
            "retrieval_summary": retrieval_summary_snapshot,
            # Keep every engine-facing nested retrieval snapshot sourced from
            # the same canonical computation path so downstream consumers do
            # not see drift between the payload and the source bundle.
            "retrieval_doc_bundle": retrieval_doc_bundle_snapshot,
            "retrieval_excerpt_bundle": retrieval_excerpt_bundle_snapshot,
            "doc_hits": [doc_hit.as_dict() for doc_hit in self.doc_hits],
            "excerpt_hits": [hit.as_dict() for hit in self.hits],
            "retrieval_manifest": copy.deepcopy(self.diagnostics["retrieval_manifest"]),
            "retrieval_evidence": copy.deepcopy(self.evidence),
            "retrieval_provenance": retrieval_provenance_snapshot,
            "basket_promotion": copy.deepcopy(basket_promotion_snapshot),
        }
        # Fingerprint the source snapshot itself so copies can be verified deterministically.
        source_bundle["source_bundle_fingerprint"] = RetrievalService._stable_fingerprint(
            {key: value for key, value in source_bundle.items() if key != "source_bundle_fingerprint"}
        )
        source_bundle["basket_promotion"]["source_bundle_fingerprint"] = source_bundle["source_bundle_fingerprint"]
        return source_bundle


class RetrievalService:
    def __init__(self, vault_root: Path, *, audit_log: AuditLog, now_fn=None) -> None:
        self._root = vault_root / _RETRIEVAL_DIR
        self._root.mkdir(parents=True, exist_ok=True)
        (self._root / _DOC_BLOBS).mkdir(exist_ok=True)
        self._audit = audit_log
        self._now_fn = now_fn or (lambda: datetime.now(UTC))
        self._key = self._load_or_create_key()
        self._docindex = DocIndexService(vault_root, audit_log=audit_log, now_fn=self._now_fn)
        self._fts = FTSStrategy(self._run_fts_hits)
        self._retrieval_policy = FTS_FIRST_POLICY

    @staticmethod
    def _build_query_snapshot(query: RetrievalQuery) -> dict[str, object]:
        return {
            "query_text": RetrievalService._normalized_query_text(query.query_text),
            "scope": query.scope,
            "intent": query.intent,
            "constraints": {
                "max_results": query.constraints.max_results,
                "doc_types": list(query.constraints.doc_types),
                "date_range": list(query.constraints.date_range) if query.constraints.date_range is not None else None,
                "require_citations": query.constraints.require_citations,
                "section_hint": query.constraints.section_hint,
                "prefer_exact_matches": query.constraints.prefer_exact_matches,
            },
            "confidentiality_profile": query.confidentiality_profile,
        }

    def add_or_update_document(
        self,
        *,
        doc_id: str,
        doc_type: str,
        text: str,
        title_hint: str | None = None,
    ) -> None:
        normalized_doc_id = _normalize_doc_id(doc_id)
        normalized_doc_type = _normalize_doc_type(doc_type)
        normalized_title_hint = _normalized_text(title_hint)
        content = text.encode("utf-8")
        source_hash = hashlib.sha256(content).hexdigest()
        blob_path = self._root / _DOC_BLOBS / f"{normalized_doc_id}.enc"
        blob_path.write_bytes(encrypt_bytes(content, self._key))

        meta = self._load_doc_meta()
        raw_doc_id = str(doc_id)
        if raw_doc_id != normalized_doc_id:
            legacy_blob_path = self._root / _DOC_BLOBS / f"{raw_doc_id}.enc"
            legacy_blob_path.unlink(missing_ok=True)
            meta.pop(raw_doc_id, None)
        self._prune_excerpt_contexts_for_doc_ids((raw_doc_id, normalized_doc_id))
        meta[normalized_doc_id] = {
            "doc_id": normalized_doc_id,
            "doc_type": normalized_doc_type,
            "title_hint": normalized_title_hint,
            "source_hash": source_hash,
            "size_bytes": len(content),
            "updated_at": self._now_fn().isoformat(),
        }
        self._write_encrypted_json(self._root / _DOC_META_FILE, meta)
        self._upsert_fts_entries(
            doc_id=normalized_doc_id,
            doc_type=normalized_doc_type,
            title_hint=normalized_title_hint,
            text=text,
        )
        if raw_doc_id != normalized_doc_id:
            with self._connect_fts_db() as conn:
                conn.execute("DELETE FROM fts_entries WHERE doc_id = ?", (raw_doc_id,))
        self._fts.clear_cache()

    def build_pageindex(self, *, doc_id: str, options: DocIndexBuildOptions | None = None) -> str:
        source = self._read_doc_text(doc_id)
        build_opts = options if options is not None else DocIndexBuildOptions()
        job = self._docindex.build(_normalize_doc_id(doc_id), source.encode("utf-8"), build_opts)
        return job.status

    def retrieve_fts(self, query: RetrievalQuery) -> RetrievalResult:
        """Run the deterministic SQLite FTS retrieval path.

        The FTS-first MVP keeps this as the canonical retrieval entrypoint so
        downstream engine callers can depend on a single auditable strategy.
        """
        self._validate_query(query)
        return self._run_fts_first_retrieval(query)

    def retrieve_fts_payload(self, query: RetrievalQuery) -> dict[str, object]:
        """Return the canonical downstream payload for a single FTS retrieval."""

        return self.retrieve_fts(query).as_downstream_payload()

    def retrieve_fts_context_bundle(self, query: RetrievalQuery) -> dict[str, object]:
        """Return the canonical retrieval context bundle for a single FTS retrieval."""

        return self.retrieve_fts(query).retrieval_context_bundle()

    def retrieve_fts_citation_bundle(self, query: RetrievalQuery) -> dict[str, object]:
        """Return the canonical citation/provenance bundle for a single FTS retrieval."""

        return self.retrieve_fts(query).retrieval_citation_bundle()

    def retrieve_fts_source_bundle(self, query: RetrievalQuery) -> dict[str, object]:
        """Return the canonical retrieval source bundle for a single FTS retrieval."""

        return self.retrieve_fts(query).retrieval_source_bundle()

    def retrieve_fts_provenance_bundle(self, query: RetrievalQuery) -> dict[str, object]:
        """Return the canonical provenance bundle for a single FTS retrieval."""

        return self.retrieve_fts(query).retrieval_provenance_bundle()

    def retrieve_fts_doc_bundle(self, query: RetrievalQuery) -> dict[str, object]:
        """Return the canonical doc-focused bundle for a single FTS retrieval."""

        return self.retrieve_fts(query).retrieval_doc_bundle()

    def retrieve_fts_excerpt_bundle(self, query: RetrievalQuery) -> dict[str, object]:
        """Return the canonical excerpt-focused bundle for a single FTS retrieval."""

        return self.retrieve_fts(query).retrieval_excerpt_bundle()

    def retrieve_auto(self, query: RetrievalQuery) -> RetrievalResult:
        return self.retrieve_fts(query)

    def retrieve_auto_payload(self, query: RetrievalQuery) -> dict[str, object]:
        """Return the canonical downstream payload for the FTS-first auto path."""

        return self.retrieve_auto(query).as_downstream_payload()

    def retrieve_auto_context_bundle(self, query: RetrievalQuery) -> dict[str, object]:
        """Return the canonical retrieval context bundle for the FTS-first auto path."""

        return self.retrieve_auto(query).retrieval_context_bundle()

    def retrieve_auto_citation_bundle(self, query: RetrievalQuery) -> dict[str, object]:
        """Return the canonical citation/provenance bundle for the FTS-first auto path."""

        return self.retrieve_auto(query).retrieval_citation_bundle()

    def retrieve_auto_source_bundle(self, query: RetrievalQuery) -> dict[str, object]:
        """Return the canonical retrieval source bundle for the FTS-first auto path."""

        return self.retrieve_auto(query).retrieval_source_bundle()

    def retrieve_auto_provenance_bundle(self, query: RetrievalQuery) -> dict[str, object]:
        """Return the canonical provenance bundle for the FTS-first auto path."""

        return self.retrieve_auto(query).retrieval_provenance_bundle()

    def retrieve_auto_doc_bundle(self, query: RetrievalQuery) -> dict[str, object]:
        """Return the canonical doc-focused bundle for the FTS-first auto path."""

        return self.retrieve_auto(query).retrieval_doc_bundle()

    def retrieve_auto_excerpt_bundle(self, query: RetrievalQuery) -> dict[str, object]:
        """Return the canonical excerpt-focused bundle for the FTS-first auto path."""

        return self.retrieve_auto(query).retrieval_excerpt_bundle()

    def retrieve_auto_excerpt(
        self,
        excerpt_id: str,
        *,
        confidentiality_profile: str = "confidential",
    ) -> dict[str, object]:
        """Return an excerpt payload using the FTS-first auto lookup path."""

        return self._lookup_fts_excerpt(
            excerpt_id,
            lookup_entrypoint="retrieve_auto_excerpt",
            confidentiality_profile=confidentiality_profile,
        )

    def fetch_fts_excerpt(
        self,
        excerpt_id: str,
        *,
        confidentiality_profile: str = "confidential",
    ) -> dict[str, object]:
        """Backward-compatible alias for the canonical FTS-only excerpt lookup path."""

        return self._lookup_fts_excerpt(
            excerpt_id,
            lookup_entrypoint="fetch_fts_excerpt",
            confidentiality_profile=confidentiality_profile,
        )

    def retrieve_fts_excerpt(
        self,
        excerpt_id: str,
        *,
        confidentiality_profile: str = "confidential",
    ) -> dict[str, object]:
        """Return an excerpt payload using the canonical FTS-only lookup path."""

        return self._lookup_fts_excerpt(
            excerpt_id,
            lookup_entrypoint="retrieve_fts_excerpt",
            confidentiality_profile=confidentiality_profile,
        )

    def _lookup_fts_excerpt(
        self,
        excerpt_id: str,
        *,
        lookup_entrypoint: str,
        confidentiality_profile: str,
    ) -> dict[str, object]:
        normalized_excerpt_id = _normalize_excerpt_id(excerpt_id)
        normalized_confidentiality_profile = _normalize_supported_value(
            confidentiality_profile,
            field_name="confidentiality_profile",
            allowed=_SUPPORTED_CONFIDENTIALITY_PROFILES,
        )
        fts_excerpt = self._find_fts_excerpt(
            normalized_excerpt_id,
            confidentiality_profile=normalized_confidentiality_profile,
        )
        if fts_excerpt is None:
            self._record_excerpt_lookup_failure_audit(
                excerpt_id=normalized_excerpt_id,
                lookup_entrypoint=lookup_entrypoint,
                lookup_resolution="fts",
                lookup_confidentiality_profile=normalized_confidentiality_profile,
            )
            raise KeyError(f"unknown excerpt_id: {normalized_excerpt_id}")
        normalized_excerpt = self._normalize_excerpt_payload(
            fts_excerpt,
            source_strategy="fts",
            lookup_resolution="fts",
            lookup_confidentiality_profile=normalized_confidentiality_profile,
        )
        # Audit the canonical excerpt payload rather than the sparse raw FTS row
        # so basket promotion and provenance metadata stay aligned with the
        # engine-facing payload returned to downstream callers.
        self._record_excerpt_lookup_audit(
            normalized_excerpt,
            lookup_entrypoint=lookup_entrypoint,
            lookup_resolution="fts",
            lookup_confidentiality_profile=normalized_confidentiality_profile,
        )
        return normalized_excerpt

    def _record_excerpt_lookup_audit(
        self,
        excerpt: dict[str, object],
        *,
        lookup_entrypoint: str,
        lookup_resolution: str,
        lookup_confidentiality_profile: str,
    ) -> None:
        """Record a compact audit trail for deterministic excerpt lookups."""

        span = excerpt.get("span")
        if not isinstance(span, dict):
            span = None
        retrieval_policy = excerpt.get("retrieval_policy", excerpt.get("policy"))
        if not isinstance(retrieval_policy, dict):
            retrieval_policy = self._retrieval_policy.as_snapshot()
        basket_promotion = excerpt.get("basket_promotion")
        if not isinstance(basket_promotion, dict):
            basket_promotion = None
        self._audit.record(
            name="excerpt_lookup_completed",
            metadata={
                "excerpt_id": excerpt.get("excerpt_id"),
                "doc_id": excerpt.get("doc_id"),
                "doc_type": excerpt.get("doc_type"),
                "source_strategy": excerpt.get("source_strategy"),
                "lookup_entrypoint": lookup_entrypoint,
                "lookup_resolution": lookup_resolution,
                "lookup_confidentiality_profile": lookup_confidentiality_profile,
                "title_hint": excerpt.get("title_hint"),
                "retrieval_backend": excerpt.get("retrieval_backend"),
                "retrieval_mode": excerpt.get("retrieval_mode"),
                "retrieval_policy": copy.deepcopy(retrieval_policy),
                "active_strategy_ids": copy.deepcopy(excerpt.get("active_strategy_ids")),
                "deferred_strategy_ids": copy.deepcopy(excerpt.get("deferred_strategy_ids")),
                "strategies_used": copy.deepcopy(excerpt.get("strategies_used")),
                "source_hash": excerpt.get("source_hash"),
                "doc_fingerprint": excerpt.get("doc_fingerprint"),
                "result_fingerprint": excerpt.get("result_fingerprint"),
                "text_hash": excerpt.get("text_hash"),
                "excerpt_text_hash": excerpt.get("excerpt_text_hash"),
                "excerpt_fingerprint": excerpt.get("excerpt_fingerprint"),
                "excerpt_provenance_fingerprint": excerpt.get("excerpt_provenance_fingerprint"),
                "lookup_fingerprint": excerpt.get("lookup_fingerprint"),
                "doc_identity_fingerprint": excerpt.get("doc_identity_fingerprint"),
                "matched_terms": copy.deepcopy(excerpt.get("matched_terms")),
                "match_count": excerpt.get("match_count"),
                "rank": excerpt.get("rank"),
                "fts_rank": excerpt.get("fts_rank"),
                "doc_rank": excerpt.get("doc_rank"),
                "section_hint": excerpt.get("section_hint"),
                "section_hint_rank": excerpt.get("section_hint_rank"),
                "query_fingerprint": excerpt.get("query_fingerprint"),
                "query_scope": excerpt.get("query_scope"),
                "query_intent": excerpt.get("query_intent"),
                "query_confidentiality_profile": excerpt.get("query_confidentiality_profile"),
                "query_date_range": copy.deepcopy(excerpt.get("query_date_range")),
                "candidate_doc_count": excerpt.get("candidate_doc_count"),
                "fts_shortlist_doc_ids": copy.deepcopy(excerpt.get("fts_shortlist_doc_ids")),
                "retrieved_doc_ids": copy.deepcopy(excerpt.get("retrieved_doc_ids")),
                "retrieved_excerpt_ids": copy.deepcopy(excerpt.get("retrieved_excerpt_ids")),
                "promotion_fingerprint": (
                    basket_promotion.get("promotion_fingerprint") if basket_promotion is not None else None
                ),
                "basket_promotion": copy.deepcopy(basket_promotion),
                "span": copy.deepcopy(span),
            },
        )

    def _record_excerpt_lookup_failure_audit(
        self,
        *,
        excerpt_id: str,
        lookup_entrypoint: str,
        lookup_resolution: str,
        lookup_confidentiality_profile: str,
    ) -> None:
        """Record a deterministic audit trail for failed FTS-only excerpt lookups."""

        retrieval_policy = self._retrieval_policy.as_snapshot()
        active_strategy_ids = copy.deepcopy(retrieval_policy["active_strategy_ids"])
        deferred_strategy_ids = copy.deepcopy(retrieval_policy["deferred_strategy_ids"])
        attempt_fingerprint = RetrievalService._stable_fingerprint(
            {
                "excerpt_id": excerpt_id,
                "lookup_entrypoint": lookup_entrypoint,
                "lookup_resolution": lookup_resolution,
                "lookup_confidentiality_profile": lookup_confidentiality_profile,
                "retrieval_backend": retrieval_policy["retrieval_backend"],
                "retrieval_mode": retrieval_policy["retrieval_mode"],
                "active_strategy_ids": active_strategy_ids,
                "deferred_strategy_ids": deferred_strategy_ids,
            }
        )
        self._audit.record(
            name="excerpt_lookup_failed",
            metadata={
                "excerpt_id": excerpt_id,
                "lookup_entrypoint": lookup_entrypoint,
                "lookup_resolution": lookup_resolution,
                "lookup_confidentiality_profile": lookup_confidentiality_profile,
                "retrieval_backend": retrieval_policy["retrieval_backend"],
                "retrieval_mode": retrieval_policy["retrieval_mode"],
                "retrieval_policy": retrieval_policy,
                "active_strategy_ids": active_strategy_ids,
                "deferred_strategy_ids": deferred_strategy_ids,
                "lookup_attempt_fingerprint": attempt_fingerprint,
                "failure_reason": "unknown_excerpt_id",
            },
        )

    def _run_fts_first_retrieval(self, query: RetrievalQuery) -> RetrievalResult:
        started = self._now_fn()
        query_fingerprint = self._query_fingerprint(query)
        retrieval_policy = retrieval_policy_snapshot()
        fts_shortlist_limit = self._fts_shortlist_limit(query.constraints.max_results)
        date_range = query.constraints.date_range
        fts_candidate_scan_limit = self._fts_candidate_scan_limit(
            query,
            fts_shortlist_limit,
            date_range=date_range,
        )
        fts_shortlist = (
            self._candidate_docs_from_fts(
                query,
                limit=fts_shortlist_limit,
                date_range=date_range,
                scan_limit=fts_candidate_scan_limit,
            )
            if not self._is_doc_scoped(query.scope)
            else ()
        )
        if date_range is not None:
            fts_shortlist = self._filter_candidate_doc_ids_by_date_range(fts_shortlist, date_range)
        candidate_doc_ids = self._candidate_docs_from_scope(query.scope, fallback=fts_shortlist)
        if date_range is not None:
            candidate_doc_ids = self._filter_candidate_doc_ids_by_date_range(candidate_doc_ids, date_range)
        # Preserve the effective ordered candidate doc set even for doc-scoped
        # queries so downstream basket promotion and provenance snapshots can
        # audit the exact doc shortlist that fed the canonical FTS run.
        shortlist_doc_ids = candidate_doc_ids if self._is_doc_scoped(query.scope) else fts_shortlist
        effective_candidate_doc_count = self._effective_candidate_doc_count(query.scope, candidate_doc_ids)
        if candidate_doc_ids or date_range is None:
            fts_run = self._fts.retrieve(query, candidate_doc_ids=candidate_doc_ids)
        else:
            fts_run = StrategyRun(strategy_id=self._fts.id, hits=[], elapsed_ms=0, cache_used=False)
        merged_hits = self._merge_hits([fts_run], max_results=query.constraints.max_results)
        doc_hits = self._build_doc_hits(
            query,
            merged_hits,
            query_fingerprint=query_fingerprint,
            retrieval_policy=retrieval_policy,
            candidate_doc_count=effective_candidate_doc_count,
            fts_shortlist_doc_ids=shortlist_doc_ids,
        )
        retrieved_doc_ids = [doc_hit.doc_id for doc_hit in doc_hits]
        retrieved_excerpt_ids = [hit.excerpt_id for hit in merged_hits if hit.excerpt_id is not None]
        active_strategy_ids = list(cast(list[str], retrieval_policy["active_strategy_ids"]))
        deferred_strategy_ids = list(cast(list[str], retrieval_policy["deferred_strategy_ids"]))
        strategies_used = list(active_strategy_ids)
        for hit in merged_hits:
            hit.provenance["active_strategy_ids"] = list(active_strategy_ids)
            hit.provenance["deferred_strategy_ids"] = list(deferred_strategy_ids)
            hit.provenance["strategies_used"] = list(strategies_used)
            hit.provenance["retrieved_doc_ids"] = list(retrieved_doc_ids)
            hit.provenance["retrieved_excerpt_ids"] = list(retrieved_excerpt_ids)
        for doc_hit in doc_hits:
            doc_hit.provenance["active_strategy_ids"] = list(active_strategy_ids)
            doc_hit.provenance["deferred_strategy_ids"] = list(deferred_strategy_ids)
            doc_hit.provenance["strategies_used"] = list(strategies_used)
            doc_hit.provenance["retrieved_doc_ids"] = list(retrieved_doc_ids)
            doc_hit.provenance["retrieved_excerpt_ids"] = list(retrieved_excerpt_ids)
        citation_status = {
            "required": query.constraints.require_citations,
            "available": bool(merged_hits),
            "satisfied": (not query.constraints.require_citations) or bool(merged_hits),
            "doc_count": len(doc_hits),
            "excerpt_count": len(merged_hits),
        }
        if query.constraints.require_citations and not citation_status["satisfied"]:
            raise ValueError("citation-required retrieval returned no excerpt hits")
        retrieval_manifest = self._build_retrieval_manifest(
            doc_hits,
            merged_hits,
            retrieval_policy=retrieval_policy,
        )
        retrieval_evidence = self._build_retrieval_evidence(
            query=query,
            doc_hits=doc_hits,
            hits=merged_hits,
            retrieval_manifest=retrieval_manifest,
            query_fingerprint=query_fingerprint,
            retrieval_policy=retrieval_policy,
            candidate_doc_count=effective_candidate_doc_count,
            fts_shortlist_doc_ids=shortlist_doc_ids,
        )
        result_fingerprint = self._build_result_fingerprint(
            query_fingerprint=query_fingerprint,
            retrieval_manifest=retrieval_manifest,
        )
        elapsed_ms_total = max(0, int((self._now_fn() - started).total_seconds() * 1000))
        diagnostics = {
            "retrieval_policy": retrieval_policy,
            "retrieval_backend": retrieval_policy["retrieval_backend"],
            "retrieval_mode": retrieval_policy["retrieval_mode"],
            "active_strategy_ids": list(retrieval_policy["active_strategy_ids"]),
            "deferred_strategy_ids": list(retrieval_policy["deferred_strategy_ids"]),
            "query_fingerprint": query_fingerprint,
            "query_scope": query.scope,
            "query_intent": query.intent,
            "query_confidentiality_profile": query.confidentiality_profile,
            "doc_scope_id": self._doc_scope_id(query.scope),
            "date_range": list(date_range) if date_range is not None else None,
            "fts_shortlist_limit": fts_shortlist_limit,
            "fts_candidate_scan_limit": fts_candidate_scan_limit,
            "candidate_doc_count": effective_candidate_doc_count,
            "fts_shortlist_count": len(shortlist_doc_ids),
            "fts_shortlist_doc_ids": list(shortlist_doc_ids),
            "strategies_used": list(retrieval_policy["active_strategy_ids"]),
            "elapsed_ms_by_strategy": {fts_run.strategy_id: fts_run.elapsed_ms},
            # Cache use is an internal optimization detail; keep the public
            # diagnostics deterministic across equivalent retrieval calls.
            "caches_used": {fts_run.strategy_id: False},
            "elapsed_ms_total": elapsed_ms_total,
            "doc_hits_count": len(doc_hits),
            "excerpt_hits_count": len(merged_hits),
            "doc_hits_fingerprint": retrieval_manifest["doc_hits_fingerprint"],
            "excerpt_hits_fingerprint": retrieval_manifest["excerpt_hits_fingerprint"],
            "citation_status": citation_status,
            "retrieval_manifest": retrieval_manifest,
            "retrieval_evidence": retrieval_evidence,
            "result_fingerprint": result_fingerprint,
        }
        # Hash the canonical query text so audit keys stay stable across whitespace variants.
        normalized_query_text = self._normalized_query_text(query.query_text)
        query_hash = hashlib.sha256(normalized_query_text.encode("utf-8")).hexdigest()
        audit = self._audit.record(
            name="retrieval_executed",
            metadata={
                "query_hash": query_hash,
                "query_fingerprint": query_fingerprint,
                "retrieval_policy": retrieval_policy,
                "retrieval_mode": diagnostics["retrieval_mode"],
                "query_scope": query.scope,
                "query_confidentiality_profile": query.confidentiality_profile,
                "date_range": diagnostics["date_range"],
                "active_strategy_ids": diagnostics["active_strategy_ids"],
                "deferred_strategy_ids": diagnostics["deferred_strategy_ids"],
                "strategies_used": diagnostics["strategies_used"],
                # Keep runtime cache behavior in audit metadata even though the
                # downstream contract masks it for deterministic payloads.
                "caches_used": {fts_run.strategy_id: fts_run.cache_used},
                "elapsed_ms_by_strategy": diagnostics["elapsed_ms_by_strategy"],
                "doc_ids_count": len({hit.doc_id for hit in merged_hits}),
                "hits_count": len(merged_hits),
                "fts_shortlist_doc_ids": diagnostics["fts_shortlist_doc_ids"],
                "retrieval_manifest": retrieval_manifest,
                "retrieval_evidence": retrieval_evidence,
                "doc_hits_fingerprint": retrieval_manifest["doc_hits_fingerprint"],
                "excerpt_hits_fingerprint": retrieval_manifest["excerpt_hits_fingerprint"],
                "result_fingerprint": result_fingerprint,
            },
        )
        result = RetrievalResult(
            query=query,
            doc_hits=doc_hits,
            hits=merged_hits,
            diagnostics=diagnostics,
            evidence=retrieval_evidence,
            audit_ref=audit.event_id,
            result_fingerprint=result_fingerprint,
        )
        self._remember_excerpt_contexts(
            query=query,
            hits=merged_hits,
            query_fingerprint=query_fingerprint,
            candidate_doc_count=effective_candidate_doc_count,
            fts_shortlist_doc_ids=shortlist_doc_ids,
            retrieved_doc_ids=retrieved_doc_ids,
            retrieved_excerpt_ids=retrieved_excerpt_ids,
        )
        return result

    def fetch_excerpt(
        self,
        excerpt_id: str,
        *,
        confidentiality_profile: str = "confidential",
    ) -> dict[str, object]:
        """Return an excerpt payload using the canonical FTS-only lookup path."""

        return self._lookup_fts_excerpt(
            excerpt_id,
            lookup_entrypoint="fetch_excerpt",
            confidentiality_profile=confidentiality_profile,
        )

    def _run_fts_hits(self, query: RetrievalQuery, candidate_doc_ids: tuple[str, ...]) -> list[RetrievalHit]:
        match_query, query_terms = self._build_fts_match_query(query.query_text)
        exact_phrase = self._normalized_query_text(query.query_text)
        scope_doc = self._doc_scope_id(query.scope)
        allowed_doc_types = self._normalized_doc_types(query.constraints.doc_types)
        effective_candidate_doc_count = self._effective_candidate_doc_count(query.scope, candidate_doc_ids)
        select_exact_rank = (
            "CASE WHEN instr(lower(text), ?) > 0 THEN 0 ELSE 1 END AS exact_rank"
            if query.constraints.prefer_exact_matches
            else "0 AS exact_rank"
        )
        section_hint = query.constraints.section_hint.casefold() if query.constraints.section_hint is not None else None
        select_section_hint_rank = (
            "CASE WHEN instr(lower(text), ?) > 0 OR instr(lower(coalesce(title_hint, '')), ?) > 0 "
            "THEN 0 ELSE 1 END AS section_hint_rank"
            if section_hint is not None
            else "0 AS section_hint_rank"
        )
        where_clauses = ["fts_entries MATCH ?"]
        params: list[object] = []
        if query.constraints.prefer_exact_matches:
            params.append(exact_phrase)
        if section_hint is not None:
            params.extend((section_hint, section_hint))
        params.append(match_query)
        if scope_doc is not None:
            where_clauses.append("doc_id = ?")
            params.append(scope_doc)
        elif candidate_doc_ids:
            placeholders = ",".join("?" for _ in candidate_doc_ids)
            where_clauses.append(f"doc_id IN ({placeholders})")
            params.extend(candidate_doc_ids)
        if allowed_doc_types:
            placeholders = ",".join("?" for _ in allowed_doc_types)
            where_clauses.append(f"lower(doc_type) IN ({placeholders})")
            params.extend(allowed_doc_types)
        limit = max(25, query.constraints.max_results)
        params.append(limit)
        sql = (
            f"SELECT rowid, doc_id, excerpt_id, doc_type, title_hint, char_start, char_end, text, "
            f"bm25(fts_entries) AS fts_rank, {select_exact_rank}, {select_section_hint_rank} "
            "FROM fts_entries "
            f"WHERE {' AND '.join(where_clauses)} "
            "ORDER BY exact_rank ASC, section_hint_rank ASC, "
            "fts_rank ASC, doc_id ASC, char_start ASC, char_end ASC, excerpt_id ASC "
            "LIMIT ?"
        )
        rows = self._query_fts_db(sql, tuple(params))
        hits: list[RetrievalHit] = []
        for rank, row in enumerate(rows, start=1):
            doc_id = str(row["doc_id"])
            excerpt_text = str(row["text"])
            matched_terms = self._matched_query_terms(query_terms, excerpt_text)
            provenance = self._build_fts_provenance(
                doc_id=doc_id,
                excerpt_id=str(row["excerpt_id"]),
                char_start=int(row["char_start"]),
                char_end=int(row["char_end"]),
                text=excerpt_text,
                matched_terms=matched_terms,
                rank=rank,
                fts_rank=float(row["fts_rank"]),
                section_hint=query.constraints.section_hint,
                section_hint_rank=int(row["section_hint_rank"]) if section_hint is not None else None,
                query_scope=query.scope,
                query_intent=query.intent,
                query_confidentiality_profile=query.confidentiality_profile,
                query_fingerprint=self._query_fingerprint(query),
                candidate_doc_count=effective_candidate_doc_count,
                query_date_range=query.constraints.date_range,
            )
            hits.append(
                RetrievalHit(
                    doc_id=doc_id,
                    excerpt_id=str(row["excerpt_id"]),
                    excerpt_text=excerpt_text,
                    span={"char_range": {"start": int(row["char_start"]), "end": int(row["char_end"])}},
                    title_hint=self._safe_title_hint(
                        str(row["title_hint"] or ""),
                        confidentiality_profile=query.confidentiality_profile,
                    ),
                    score=round(1.0 / rank, 3),
                    source_strategy="fts",
                    rationale="sqlite_fts_match",
                    node_path=None,
                    provenance=provenance,
                )
            )
        return hits

    def _merge_hits(self, runs: list[StrategyRun], *, max_results: int) -> list[RetrievalHit]:
        combined: list[RetrievalHit] = []
        for run in runs:
            for hit in run.hits:
                if isinstance(hit, RetrievalHit):
                    combined.append(hit)
                    continue
                if isinstance(hit, dict):
                    source_strategy = str(hit.get("source_strategy", "fts"))
                    if source_strategy != "fts":
                        raise ValueError(f"unsupported retrieval strategy: {source_strategy}")
                    combined.append(
                        RetrievalHit(
                            doc_id=str(hit["doc_id"]),
                            excerpt_id=hit.get("excerpt_id"),
                            excerpt_text=hit.get("excerpt_text"),
                            span=dict(hit.get("span", {})),
                            title_hint=hit.get("title_hint"),
                            score=float(hit.get("score", 0.0)),
                            source_strategy="fts",
                            rationale=hit.get("rationale"),
                            node_path=hit.get("node_path"),
                            provenance=dict(hit.get("provenance", {})),
                        )
                    )
        with_excerpt = [hit for hit in combined if hit.excerpt_id is not None]
        without_excerpt = [hit for hit in combined if hit.excerpt_id is None]
        ordered = sorted(with_excerpt, key=self._hit_sort_key) + sorted(without_excerpt, key=self._hit_sort_key)
        seen: set[str] = set()
        out: list[RetrievalHit] = []
        for hit in ordered:
            dedupe_key = hit.excerpt_id if hit.excerpt_id is not None else f"doc:{hit.doc_id}:{hit.source_strategy}"
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            out.append(hit)
            if len(out) >= max_results:
                break
        return out

    def _build_doc_hits(
        self,
        query: RetrievalQuery,
        hits: list[RetrievalHit],
        *,
        query_fingerprint: str | None,
        retrieval_policy: dict[str, object],
        candidate_doc_count: int | None = None,
        fts_shortlist_doc_ids: tuple[str, ...] = (),
    ) -> list[RetrievalDocHit]:
        meta = self._load_doc_meta()
        grouped: dict[str, list[RetrievalHit]] = {}
        doc_order: list[str] = []
        for hit in hits:
            if hit.doc_id not in grouped:
                doc_order.append(hit.doc_id)
            grouped.setdefault(hit.doc_id, []).append(hit)

        doc_hits: list[RetrievalDocHit] = []
        for doc_id in doc_order:
            doc_meta = meta.get(doc_id, {})
            doc_hit_list = grouped[doc_id]
            top_hit = doc_hit_list[0]
            doc_rank = len(doc_hits) + 1
            doc_type = str(doc_meta.get("doc_type", ""))
            top_excerpt_fingerprint = str(top_hit.provenance.get("excerpt_fingerprint", ""))
            top_excerpt_text_hash = str(
                top_hit.provenance.get("excerpt_text_hash") or top_hit.provenance.get("hash") or ""
            )
            top_excerpt_text_length = len(top_hit.excerpt_text or "")
            source_hash = self._doc_source_hash(doc_id, doc_meta=doc_meta)
            doc_identity_fingerprint = self._build_doc_identity_fingerprint(
                doc_id=doc_id,
                source_hash=source_hash,
                doc_type=doc_type,
            )
            doc_hits.append(
                RetrievalDocHit(
                    doc_id=doc_id,
                    title_hint=top_hit.title_hint,
                    source_hash=source_hash,
                    top_excerpt_id=top_hit.excerpt_id,
                    top_score=top_hit.score,
                    source_strategy="fts",
                    excerpt_count=len(doc_hit_list),
                    provenance={
                        "doc_id": doc_id,
                        "source_hash": source_hash,
                        "doc_type": doc_type,
                        "query_fingerprint": query_fingerprint,
                        "excerpt_ids": [hit.excerpt_id for hit in doc_hit_list if hit.excerpt_id is not None],
                        "top_excerpt_id": top_hit.excerpt_id,
                        "top_excerpt_hash": top_hit.provenance.get("hash"),
                        "top_excerpt_text_hash": top_excerpt_text_hash,
                        "top_excerpt_text_length": top_excerpt_text_length,
                        "top_excerpt_fingerprint": top_excerpt_fingerprint,
                        "top_excerpt_provenance_fingerprint": top_hit.provenance.get(
                            "excerpt_provenance_fingerprint"
                        ),
                        "top_excerpt_span": top_hit.provenance.get("span"),
                        "top_matched_terms": top_hit.provenance.get("matched_terms"),
                        "top_match_count": top_hit.provenance.get("match_count"),
                        "top_excerpt_rank": top_hit.provenance.get("rank"),
                        "section_hint": query.constraints.section_hint,
                        "top_section_hint_rank": top_hit.provenance.get("section_hint_rank"),
                        "top_fts_rank": top_hit.provenance.get("fts_rank"),
                        "retrieval_backend": top_hit.provenance.get(
                            "retrieval_backend",
                            cast(str, retrieval_policy["retrieval_backend"]),
                        ),
                        "retrieval_policy": dict(retrieval_policy),
                        "doc_rank": doc_rank,
                        "doc_identity_fingerprint": doc_identity_fingerprint,
                        "doc_fingerprint": self._stable_fingerprint(
                            {
                                "doc_id": doc_id,
                                "source_hash": source_hash,
                                "doc_type": doc_type,
                                "top_excerpt_id": top_hit.excerpt_id,
                                "top_excerpt_fingerprint": top_excerpt_fingerprint,
                                "query_fingerprint": query_fingerprint,
                            }
                        ),
                        "excerpt_count": len(doc_hit_list),
                        "source_strategy": primary_strategy_id(),
                        "retrieval_mode": cast(str, retrieval_policy["retrieval_mode"]),
                        "query_scope": query.scope,
                        "query_intent": query.intent,
                        "query_confidentiality_profile": query.confidentiality_profile,
                        "query_date_range": list(query.constraints.date_range) if query.constraints.date_range is not None else None,
                        "candidate_doc_count": candidate_doc_count,
                        "fts_shortlist_doc_ids": list(fts_shortlist_doc_ids),
                    },
                )
            )
        return doc_hits

    def _build_retrieval_manifest(
        self,
        doc_hits: list[RetrievalDocHit],
        hits: list[RetrievalHit],
        *,
        retrieval_policy: dict[str, object],
    ) -> dict[str, object]:
        doc_fingerprints = [_optional_text(doc_hit.provenance.get("doc_fingerprint")) for doc_hit in doc_hits]
        doc_identity_fingerprints = [
            _optional_text(doc_hit.provenance.get("doc_identity_fingerprint")) for doc_hit in doc_hits
        ]
        top_excerpt_fingerprints = [
            _optional_text(doc_hit.provenance.get("top_excerpt_fingerprint")) for doc_hit in doc_hits
        ]
        top_excerpt_text_hashes = [
            _optional_text(doc_hit.provenance.get("top_excerpt_text_hash")) for doc_hit in doc_hits
        ]
        excerpt_fingerprints = [
            _optional_text(hit.provenance.get("excerpt_fingerprint")) for hit in hits if hit.excerpt_id is not None
        ]
        excerpt_text_hashes = [
            _optional_text(hit.provenance.get("excerpt_text_hash") or hit.provenance.get("hash"))
            for hit in hits
            if hit.excerpt_id is not None
        ]
        doc_hits_fingerprint = self._stable_fingerprint(
            [
                {
                    "doc_id": doc_hit.doc_id,
                    "doc_fingerprint": doc_hit.provenance.get("doc_fingerprint"),
                    "doc_identity_fingerprint": doc_hit.provenance.get("doc_identity_fingerprint"),
                    "doc_rank": doc_hit.provenance.get("doc_rank"),
                    "excerpt_count": doc_hit.excerpt_count,
                    "source_strategy": doc_hit.source_strategy,
                    "top_excerpt_fingerprint": doc_hit.provenance.get("top_excerpt_fingerprint"),
                    "top_excerpt_id": doc_hit.top_excerpt_id,
                }
                for doc_hit in doc_hits
            ]
        )
        excerpt_hits_fingerprint = self._stable_fingerprint(
            [
                {
                    "doc_id": hit.doc_id,
                    "excerpt_fingerprint": hit.provenance.get("excerpt_fingerprint"),
                    "excerpt_id": hit.excerpt_id,
                    "excerpt_text_hash": hit.provenance.get("excerpt_text_hash") or hit.provenance.get("hash"),
                    "rank": hit.provenance.get("rank"),
                    "score": hit.score,
                    "source_strategy": hit.source_strategy,
                }
                for hit in hits
                if hit.excerpt_id is not None
            ]
        )
        return {
            "doc_ids": [doc_hit.doc_id for doc_hit in doc_hits],
            "doc_fingerprints": doc_fingerprints,
            "doc_identity_fingerprints": doc_identity_fingerprints,
            "top_excerpt_ids": [doc_hit.top_excerpt_id for doc_hit in doc_hits],
            "top_excerpt_fingerprints": top_excerpt_fingerprints,
            "top_excerpt_text_hashes": top_excerpt_text_hashes,
            "excerpt_ids": [hit.excerpt_id for hit in hits if hit.excerpt_id is not None],
            "excerpt_fingerprints": excerpt_fingerprints,
            "excerpt_text_hashes": excerpt_text_hashes,
            "doc_hits_fingerprint": doc_hits_fingerprint,
            "excerpt_hits_fingerprint": excerpt_hits_fingerprint,
            "retrieval_policy": dict(retrieval_policy),
            "active_strategy_ids": list(cast(list[str], retrieval_policy["active_strategy_ids"])),
            "deferred_strategy_ids": list(cast(list[str], retrieval_policy["deferred_strategy_ids"])),
        }

    def _build_retrieval_evidence(
        self,
        *,
        query: RetrievalQuery,
        doc_hits: list[RetrievalDocHit],
        hits: list[RetrievalHit],
        retrieval_manifest: dict[str, object],
        query_fingerprint: str,
        retrieval_policy: dict[str, object],
        candidate_doc_count: int | None = None,
        fts_shortlist_doc_ids: tuple[str, ...] = (),
    ) -> dict[str, object]:
        doc_citations: list[dict[str, object]] = []
        for doc_hit in doc_hits:
            citation = {
                "doc_id": doc_hit.doc_id,
                "doc_type": doc_hit.provenance.get("doc_type"),
                "source_hash": doc_hit.source_hash,
                "doc_fingerprint": doc_hit.provenance.get("doc_fingerprint"),
                "doc_identity_fingerprint": doc_hit.provenance.get("doc_identity_fingerprint"),
                "doc_rank": doc_hit.provenance.get("doc_rank"),
                "top_excerpt_id": doc_hit.top_excerpt_id,
                "top_excerpt_fingerprint": doc_hit.provenance.get("top_excerpt_fingerprint"),
                "top_excerpt_text_hash": doc_hit.provenance.get("top_excerpt_text_hash"),
                "top_excerpt_span": copy.deepcopy(doc_hit.provenance.get("top_excerpt_span")),
                "top_excerpt_rank": doc_hit.provenance.get("top_excerpt_rank"),
                "top_fts_rank": doc_hit.provenance.get("top_fts_rank"),
                "excerpt_ids": list(doc_hit.provenance.get("excerpt_ids", [])),
                "excerpt_count": doc_hit.excerpt_count,
                "matched_terms": copy.deepcopy(doc_hit.provenance.get("top_matched_terms")),
                "source_strategy": doc_hit.provenance.get("source_strategy"),
                "retrieval_backend": doc_hit.provenance.get("retrieval_backend"),
                "retrieval_mode": doc_hit.provenance.get("retrieval_mode"),
            }
            section_hint = doc_hit.provenance.get("section_hint")
            if isinstance(section_hint, str) and section_hint:
                citation["section_hint"] = section_hint
            top_section_hint_rank = doc_hit.provenance.get("top_section_hint_rank")
            if isinstance(top_section_hint_rank, int):
                citation["top_section_hint_rank"] = top_section_hint_rank
            doc_citations.append(citation)

        excerpt_citations: list[dict[str, object]] = []
        for hit in hits:
            if hit.excerpt_id is None:
                continue
            citation = {
                "doc_id": hit.doc_id,
                "excerpt_id": hit.excerpt_id,
                "doc_type": hit.provenance.get("doc_type"),
                "source_hash": hit.provenance.get("source_hash"),
                "excerpt_fingerprint": hit.provenance.get("excerpt_fingerprint"),
                "excerpt_provenance_fingerprint": hit.provenance.get("excerpt_provenance_fingerprint"),
                "excerpt_text_hash": hit.provenance.get("excerpt_text_hash") or hit.provenance.get("hash"),
                "span": copy.deepcopy(hit.provenance.get("span")),
                "matched_terms": copy.deepcopy(hit.provenance.get("matched_terms")),
                "match_count": hit.provenance.get("match_count"),
                "rank": hit.provenance.get("rank"),
                "fts_rank": hit.provenance.get("fts_rank"),
                "source_strategy": hit.provenance.get("source_strategy"),
                "retrieval_backend": hit.provenance.get("retrieval_backend"),
                "retrieval_mode": hit.provenance.get("retrieval_mode"),
            }
            section_hint = hit.provenance.get("section_hint")
            if isinstance(section_hint, str) and section_hint:
                citation["section_hint"] = section_hint
            section_hint_rank = hit.provenance.get("section_hint_rank")
            if isinstance(section_hint_rank, int):
                citation["section_hint_rank"] = section_hint_rank
            excerpt_citations.append(citation)

        return {
            "query_fingerprint": query_fingerprint,
            "query_scope": query.scope,
            "query_intent": query.intent,
            "query_confidentiality_profile": query.confidentiality_profile,
            "query_date_range": (
                list(query.constraints.date_range)
                if query.constraints.date_range is not None
                else None
            ),
            "retrieval_policy": dict(retrieval_policy),
            "retrieval_backend": cast(str, retrieval_policy["retrieval_backend"]),
            "retrieval_mode": cast(str, retrieval_policy["retrieval_mode"]),
            "active_strategy_ids": list(cast(list[str], retrieval_policy["active_strategy_ids"])),
            "deferred_strategy_ids": list(cast(list[str], retrieval_policy["deferred_strategy_ids"])),
            "candidate_doc_count": candidate_doc_count,
            "fts_shortlist_doc_ids": list(fts_shortlist_doc_ids),
            "doc_hits_fingerprint": retrieval_manifest.get("doc_hits_fingerprint"),
            "excerpt_hits_fingerprint": retrieval_manifest.get("excerpt_hits_fingerprint"),
            "citation_status": {
                "required": query.constraints.require_citations,
                "available": bool(hits),
                "satisfied": (not query.constraints.require_citations) or bool(hits),
                "doc_count": len(doc_hits),
                "excerpt_count": len(hits),
            },
            "doc_count": len(doc_hits),
            "excerpt_count": len(hits),
            "doc_citations": doc_citations,
            "excerpt_citations": excerpt_citations,
            "retrieval_manifest": dict(retrieval_manifest),
        }

    @staticmethod
    def _build_result_fingerprint(
        *,
        query_fingerprint: str,
        retrieval_manifest: dict[str, object],
    ) -> str:
        payload = {
            "query_fingerprint": query_fingerprint,
            "retrieval_policy": retrieval_manifest.get("retrieval_policy", {}),
            "doc_fingerprints": retrieval_manifest.get("doc_fingerprints", []),
            "top_excerpt_fingerprints": retrieval_manifest.get("top_excerpt_fingerprints", []),
            "excerpt_fingerprints": retrieval_manifest.get("excerpt_fingerprints", []),
            "top_excerpt_text_hashes": retrieval_manifest.get("top_excerpt_text_hashes", []),
            "excerpt_text_hashes": retrieval_manifest.get("excerpt_text_hashes", []),
            "active_strategy_ids": retrieval_manifest.get("active_strategy_ids", []),
            "deferred_strategy_ids": retrieval_manifest.get("deferred_strategy_ids", []),
        }
        return RetrievalService._stable_fingerprint(payload)

    def _candidate_docs_from_fts(
        self,
        query: RetrievalQuery,
        *,
        limit: int,
        date_range: tuple[str, str] | None = None,
        scan_limit: int | None = None,
    ) -> tuple[str, ...]:
        shortlist_query = self._build_fts_shortlist_query(query, max_results=limit)
        if date_range is None:
            run = self._fts.retrieve(shortlist_query, candidate_doc_ids=(), use_cache=False)
            doc_ids: list[str] = []
            seen = set()
            for hit in run.hits:
                if hit.doc_id in seen:
                    continue
                seen.add(hit.doc_id)
                doc_ids.append(hit.doc_id)
                if len(doc_ids) >= limit:
                    break
            return tuple(doc_ids)

        effective_scan_limit = (
            scan_limit
            if scan_limit is not None
            else self._fts_candidate_scan_limit(query, limit, date_range=date_range)
        )
        doc_ids: list[str] = []
        seen: set[str] = set()
        batch_limit = max(25, min(limit, effective_scan_limit))
        while True:
            run = self._fts.retrieve(
                self._build_fts_shortlist_query(query, max_results=batch_limit),
                candidate_doc_ids=(),
                use_cache=False,
            )
            for hit in run.hits:
                if hit.doc_id in seen:
                    continue
                seen.add(hit.doc_id)
                if not self._doc_matches_date_range(hit.doc_id, date_range):
                    continue
                doc_ids.append(hit.doc_id)
                if len(doc_ids) >= limit:
                    return tuple(doc_ids)
            if len(run.hits) < batch_limit or batch_limit >= effective_scan_limit:
                break
            next_batch_limit = min(effective_scan_limit, max(batch_limit + 1, batch_limit * 2))
            if next_batch_limit == batch_limit:
                break
            batch_limit = next_batch_limit
        return tuple(doc_ids)

    @staticmethod
    def _build_fts_shortlist_query(query: RetrievalQuery, *, max_results: int) -> RetrievalQuery:
        """Preserve search-shaping constraints when deriving the shortlist query.

        The shortlist should stay aligned with the caller's intent so exact-match
        preferences and other query-shaping flags can influence the candidate
        document set before the final FTS retrieval pass.
        """

        return RetrievalQuery(
            query_text=query.query_text,
            scope=query.scope,
            intent=query.intent,
            constraints=RetrievalConstraints(
                max_results=max_results,
                doc_types=query.constraints.doc_types,
                require_citations=query.constraints.require_citations,
                section_hint=query.constraints.section_hint,
                prefer_exact_matches=query.constraints.prefer_exact_matches,
            ),
            confidentiality_profile=query.confidentiality_profile,
        )

    @staticmethod
    def _fts_shortlist_limit(max_results: int) -> int:
        return max(25, max_results)

    def _fts_candidate_scan_limit(
        self,
        query: RetrievalQuery,
        limit: int,
        *,
        date_range: tuple[str, str] | None,
    ) -> int:
        if date_range is None:
            return limit
        return max(limit, self._fts_matching_row_count(query))

    def _fts_matching_row_count(self, query: RetrievalQuery) -> int:
        match_query, _ = self._build_fts_match_query(query.query_text)
        scope_doc = self._doc_scope_id(query.scope)
        allowed_doc_types = self._normalized_doc_types(query.constraints.doc_types)
        where_clauses = ["fts_entries MATCH ?"]
        params: list[object] = []
        params.append(match_query)
        if scope_doc is not None:
            where_clauses.append("doc_id = ?")
            params.append(scope_doc)
        if allowed_doc_types:
            placeholders = ",".join("?" for _ in allowed_doc_types)
            where_clauses.append(f"lower(doc_type) IN ({placeholders})")
            params.extend(allowed_doc_types)

        sql = (
            "SELECT COUNT(*) AS row_count "
            "FROM fts_entries "
            f"WHERE {' AND '.join(where_clauses)}"
        )
        rows = self._query_fts_db(sql, tuple(params))
        if not rows:
            return 0
        return max(0, int(rows[0]["row_count"]))

    @staticmethod
    def _hit_sort_key(hit: RetrievalHit) -> tuple[int, float, float, str, str, int, int, str]:
        char_range = hit.span.get("char_range", {}) if isinstance(hit.span, dict) else {}
        if not isinstance(char_range, dict):
            char_range = {}
        rank = hit.provenance.get("rank")
        canonical_rank = rank if isinstance(rank, int) and rank > 0 else 2**31 - 1
        fts_rank = hit.provenance.get("fts_rank")
        canonical_fts_rank = (
            float(fts_rank)
            if isinstance(fts_rank, (int, float)) and not isinstance(fts_rank, bool)
            else float("inf")
        )
        return (
            canonical_rank,
            canonical_fts_rank,
            -hit.score,
            hit.source_strategy,
            hit.doc_id,
            int(char_range.get("start", -1)),
            int(char_range.get("end", -1)),
            hit.excerpt_id or "",
        )

    def _candidate_docs_from_scope(self, scope: str, *, fallback: tuple[str, ...]) -> tuple[str, ...]:
        if scope.startswith("doc:"):
            doc_id = scope.split(":", 1)[1]
            return (doc_id,) if self._doc_exists(doc_id) else ()
        if scope.startswith("collection:"):
            return fallback
        return fallback

    def _doc_exists(self, doc_id: str) -> bool:
        normalized_doc_id = _normalize_doc_id(doc_id)
        if normalized_doc_id in self._load_doc_meta():
            return True
        if (self._root / _DOC_BLOBS / f"{normalized_doc_id}.enc").exists():
            return True
        rows = self._query_fts_db(
            "SELECT 1 AS present FROM fts_entries WHERE doc_id = ? LIMIT 1",
            (normalized_doc_id,),
        )
        return bool(rows)

    def _filter_candidate_doc_ids_by_date_range(
        self,
        candidate_doc_ids: tuple[str, ...],
        date_range: tuple[str, str],
    ) -> tuple[str, ...]:
        if not candidate_doc_ids:
            return ()
        filtered: list[str] = []
        for doc_id in candidate_doc_ids:
            if self._doc_matches_date_range(doc_id, date_range):
                filtered.append(doc_id)
        return tuple(filtered)

    @staticmethod
    def _effective_candidate_doc_count(scope: str, candidate_doc_ids: tuple[str, ...]) -> int:
        return len(candidate_doc_ids)

    @staticmethod
    def _is_doc_scoped(scope: str) -> bool:
        return scope.startswith("doc:")

    @staticmethod
    def _doc_scope_id(scope: str) -> str | None:
        if scope.startswith("doc:"):
            return scope.split(":", 1)[1]
        return None

    def _doc_matches_date_range(self, doc_id: str, date_range: tuple[str, str]) -> bool:
        meta = self._load_doc_meta().get(doc_id)
        if meta is None:
            return False
        updated_at = meta.get("updated_at")
        if not isinstance(updated_at, str) or not updated_at:
            return False
        updated_date = self._parse_date_value(updated_at)
        if updated_date is None:
            return False
        start_date = self._parse_date_value(date_range[0])
        end_date = self._parse_date_value(date_range[1])
        if start_date is None or end_date is None:
            return False
        return start_date <= updated_date <= end_date

    @staticmethod
    def _parse_date_value(value: str) -> date | None:
        return _parse_date_value(value)

    def _is_long_structured_doc(self, doc_id: str) -> bool:
        meta = self._load_doc_meta().get(doc_id)
        if meta is None:
            return False
        doc_type = str(meta.get("doc_type", ""))
        size_bytes = int(meta.get("size_bytes", 0))
        if doc_type in {"pdf", "transcript"}:
            return True
        if doc_type == "text" and size_bytes >= 4000:
            return True
        return False

    def _upsert_fts_entries(self, *, doc_id: str, doc_type: str, title_hint: str | None, text: str) -> None:
        with self._connect_fts_db() as conn:
            conn.execute("DELETE FROM fts_entries WHERE doc_id = ?", (doc_id,))
            for start, end, segment in self._iter_fts_segments(text):
                if not segment:
                    continue
                conn.execute(
                    """
                    INSERT INTO fts_entries(
                      doc_id, excerpt_id, doc_type, title_hint, char_start, char_end, text
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        doc_id,
                        self._make_fts_excerpt_id(doc_id=doc_id, char_start=start, char_end=end, text=segment),
                        doc_type,
                        title_hint,
                        start,
                        end,
                        segment,
                    ),
                )

    def _iter_fts_segments(self, text: str) -> list[tuple[int, int, str]]:
        if not text:
            return []
        step = max(1, _FTS_SEGMENT_CHARS - _FTS_SEGMENT_OVERLAP_CHARS)
        segments: list[tuple[int, int, str]] = []
        seen_ranges: set[tuple[int, int]] = set()
        for raw_start in range(0, len(text), step):
            raw_end = min(len(text), raw_start + _FTS_SEGMENT_CHARS)
            start = self._segment_start(text, raw_start)
            end = self._segment_end(text, raw_end)
            if end <= start:
                continue
            segment_range = (start, end)
            if segment_range in seen_ranges:
                continue
            seen_ranges.add(segment_range)
            segments.append((start, end, text[start:end]))
            if raw_end >= len(text):
                break
        return segments

    @staticmethod
    def _segment_start(text: str, raw_start: int) -> int:
        if raw_start <= 0:
            return 0
        scan_start = max(0, raw_start - _FTS_BOUNDARY_SCAN_CHARS)
        for index in range(raw_start, scan_start, -1):
            if text[index - 1].isspace():
                return index
        return raw_start

    @staticmethod
    def _segment_end(text: str, raw_end: int) -> int:
        if raw_end >= len(text):
            return len(text)
        scan_end = min(len(text), raw_end + _FTS_BOUNDARY_SCAN_CHARS)
        for index in range(raw_end, scan_end):
            if text[index].isspace():
                return index
        return raw_end

    @staticmethod
    def _make_fts_excerpt_id(*, doc_id: str, char_start: int, char_end: int, text: str) -> str:
        payload = f"{doc_id}:{char_start}:{char_end}:{hashlib.sha256(text.encode('utf-8')).hexdigest()}"
        return f"fts_{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:24]}"

    def _find_fts_excerpt(
        self,
        excerpt_id: str,
        *,
        confidentiality_profile: str,
    ) -> dict[str, object] | None:
        row = self._fetch_fts_row(excerpt_id)
        if row is not None:
            text = str(row["text"])
            text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            doc_id = str(row["doc_id"])
            source_hash = self._doc_source_hash(doc_id)
            excerpt_context = self._load_excerpt_context(excerpt_id, doc_id=doc_id)
            provenance = self._build_fts_provenance(
                doc_id=doc_id,
                excerpt_id=excerpt_id,
                char_start=int(row["char_start"]),
                char_end=int(row["char_end"]),
                text=text,
            )
            query_snapshot = None
            if excerpt_context is not None:
                query_snapshot = copy.deepcopy(excerpt_context.get("query"))
                for key in (
                    "query_fingerprint",
                    "query_scope",
                    "query_intent",
                    "query_confidentiality_profile",
                    "query_date_range",
                    "candidate_doc_count",
                    "fts_shortlist_doc_ids",
                    "retrieved_doc_ids",
                    "retrieved_excerpt_ids",
                    "matched_terms",
                    "match_count",
                    "rank",
                    "fts_rank",
                    "section_hint",
                    "section_hint_rank",
                ):
                    value = excerpt_context.get(key)
                    if value is not None:
                        provenance[key] = copy.deepcopy(value)
            return self._normalize_excerpt_payload(
                {
                    "excerpt_id": excerpt_id,
                    "doc_id": doc_id,
                    "doc_type": str(row["doc_type"]),
                    "title_hint": self._safe_title_hint(
                        str(row["title_hint"] or ""),
                        confidentiality_profile=confidentiality_profile,
                    ),
                    "source_hash": source_hash,
                    "source_strategy": "fts",
                    "span": {"char_range": {"start": int(row["char_start"]), "end": int(row["char_end"])}},
                    "text": text,
                    "text_hash": text_hash,
                    "query": query_snapshot,
                    "provenance": provenance,
                },
                source_strategy="fts",
                lookup_resolution="fts",
                lookup_confidentiality_profile=confidentiality_profile,
            )
        return None

    def _remember_excerpt_contexts(
        self,
        *,
        query: RetrievalQuery,
        hits: list[RetrievalHit],
        query_fingerprint: str,
        candidate_doc_count: int,
        fts_shortlist_doc_ids: tuple[str, ...],
        retrieved_doc_ids: list[str],
        retrieved_excerpt_ids: list[str],
    ) -> None:
        if not hits:
            return
        context_by_excerpt = self._load_excerpt_context_map()
        query_snapshot = self._build_query_snapshot(query)
        query_date_range = list(query.constraints.date_range) if query.constraints.date_range is not None else None
        for hit in hits:
            if hit.excerpt_id is None:
                continue
            context_by_excerpt[hit.excerpt_id] = {
                "doc_id": hit.doc_id,
                "query": copy.deepcopy(query_snapshot),
                "query_fingerprint": query_fingerprint,
                "query_scope": query.scope,
                "query_intent": query.intent,
                "query_confidentiality_profile": query.confidentiality_profile,
                "query_date_range": copy.deepcopy(query_date_range),
                "candidate_doc_count": candidate_doc_count,
                "source_hash": hit.provenance.get("source_hash") or self._doc_source_hash(hit.doc_id),
                "fts_shortlist_doc_ids": list(fts_shortlist_doc_ids),
                "retrieved_doc_ids": list(retrieved_doc_ids),
                "retrieved_excerpt_ids": list(retrieved_excerpt_ids),
                "matched_terms": copy.deepcopy(hit.provenance.get("matched_terms")),
                "match_count": hit.provenance.get("match_count"),
                "rank": hit.provenance.get("rank"),
                "fts_rank": hit.provenance.get("fts_rank"),
                "section_hint": query.constraints.section_hint,
                "section_hint_rank": hit.provenance.get("section_hint_rank"),
            }
        self._write_encrypted_json(self._root / _EXCERPT_CONTEXT_FILE, context_by_excerpt)

    def _load_excerpt_context_map(self) -> dict[str, dict[str, object]]:
        payload = self._read_encrypted_json(self._root / _EXCERPT_CONTEXT_FILE, default={})
        if not isinstance(payload, dict):
            return {}
        normalized: dict[str, dict[str, object]] = {}
        for excerpt_id, context in payload.items():
            if not isinstance(excerpt_id, str) or not isinstance(context, dict):
                continue
            normalized[excerpt_id] = copy.deepcopy(context)
        return normalized

    def _load_excerpt_context(self, excerpt_id: str, *, doc_id: str) -> dict[str, object] | None:
        context = self._load_excerpt_context_map().get(excerpt_id)
        if not isinstance(context, dict):
            return None
        stored_doc_id = _optional_text(context.get("doc_id"))
        if stored_doc_id is not None and stored_doc_id != doc_id:
            return None
        stored_source_hash = _optional_text(context.get("source_hash"))
        if stored_source_hash is not None:
            current_source_hash = self._doc_source_hash(doc_id)
            if current_source_hash and current_source_hash != stored_source_hash:
                return None
        return copy.deepcopy(context)

    def _prune_excerpt_contexts_for_doc_ids(self, doc_ids: tuple[str, ...]) -> None:
        normalized_doc_ids = {
            normalized_doc_id
            for doc_id in doc_ids
            if (normalized_doc_id := _optional_text(doc_id)) is not None
        }
        if not normalized_doc_ids:
            return
        context_by_excerpt = self._load_excerpt_context_map()
        kept_contexts = {
            excerpt_id: context
            for excerpt_id, context in context_by_excerpt.items()
            if _optional_text(context.get("doc_id")) not in normalized_doc_ids
        }
        if len(kept_contexts) == len(context_by_excerpt):
            return
        self._write_encrypted_json(self._root / _EXCERPT_CONTEXT_FILE, kept_contexts)

    def _build_fts_provenance(
        self,
        *,
        doc_id: str,
        excerpt_id: str,
        char_start: int,
        char_end: int,
        text: str,
        matched_terms: tuple[str, ...] = (),
        rank: int | None = None,
        fts_rank: float | None = None,
        section_hint: str | None = None,
        section_hint_rank: int | None = None,
        query_scope: str | None = None,
        query_intent: str | None = None,
        query_confidentiality_profile: str | None = None,
        query_date_range: tuple[str, str] | None = None,
        query_fingerprint: str | None = None,
        candidate_doc_count: int | None = None,
    ) -> dict[str, object]:
        meta = self._load_doc_meta().get(doc_id, {})
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        source_hash = self._doc_source_hash(doc_id, doc_meta=meta)
        doc_type = str(meta.get("doc_type", ""))
        doc_identity_fingerprint = self._build_doc_identity_fingerprint(
            doc_id=doc_id,
            source_hash=source_hash,
            doc_type=doc_type,
        )
        provenance = {
            "doc_id": doc_id,
            "source_hash": source_hash,
            "doc_type": doc_type,
            "excerpt_id": excerpt_id,
            "span": {"char_range": {"start": char_start, "end": char_end}},
            "hash": text_hash,
            "excerpt_text_hash": text_hash,
            "excerpt_text_length": len(text),
            "matched_terms": list(matched_terms),
            "match_count": len(matched_terms),
            "rank": rank,
            "fts_rank": fts_rank,
            "source_strategy": "fts",
            "retrieval_backend": self._retrieval_policy.retrieval_backend,
            "retrieval_mode": self._retrieval_policy.retrieval_mode,
            "retrieval_policy": self._retrieval_policy.as_snapshot(),
            "doc_identity_fingerprint": doc_identity_fingerprint,
        }
        if query_scope is not None:
            provenance["query_scope"] = query_scope
        if query_intent is not None:
            provenance["query_intent"] = query_intent
        if query_confidentiality_profile is not None:
            provenance["query_confidentiality_profile"] = query_confidentiality_profile
        if section_hint is not None:
            provenance["section_hint"] = section_hint
        if section_hint_rank is not None:
            provenance["section_hint_rank"] = section_hint_rank
        if query_date_range is not None:
            provenance["query_date_range"] = list(query_date_range)
        if query_fingerprint is not None:
            provenance["query_fingerprint"] = query_fingerprint
        if candidate_doc_count is not None:
            provenance["candidate_doc_count"] = candidate_doc_count
        provenance["excerpt_fingerprint"] = self._stable_fingerprint(
            {
                "doc_id": doc_id,
                "source_hash": source_hash,
                "excerpt_id": excerpt_id,
                "span": provenance["span"],
                "excerpt_text_hash": text_hash,
            }
        )
        provenance["excerpt_provenance_fingerprint"] = self._build_excerpt_provenance_fingerprint(
            doc_id=doc_id,
            excerpt_id=excerpt_id,
            doc_type=doc_type,
            span=cast(dict[str, object], provenance["span"]),
            source_hash=source_hash,
            text_hash=text_hash,
            doc_identity_fingerprint=doc_identity_fingerprint,
        )
        return provenance

    def _normalize_excerpt_payload(
        self,
        excerpt: dict[str, object],
        *,
        source_strategy: Literal["fts"],
        lookup_resolution: str,
        lookup_confidentiality_profile: str | None = None,
    ) -> dict[str, object]:
        source_strategy = _normalize_source_strategy(source_strategy)
        provenance = excerpt.get("provenance", {})
        if not isinstance(provenance, dict):
            provenance = {}
        normalized = dict(excerpt)
        normalized["source_strategy"] = source_strategy
        normalized["retrieval_source_strategy"] = source_strategy
        canonical_lookup_resolution = _normalize_lookup_resolution(
            normalized.get("lookup_resolution", provenance.get("lookup_resolution", lookup_resolution))
        )
        normalized["lookup_resolution"] = canonical_lookup_resolution
        canonical_lookup_confidentiality_profile = _normalize_lookup_confidentiality_profile_payload(
            normalized.get(
                "lookup_confidentiality_profile",
                provenance.get("lookup_confidentiality_profile", lookup_confidentiality_profile),
            )
        )
        if canonical_lookup_confidentiality_profile is not None:
            normalized["lookup_confidentiality_profile"] = canonical_lookup_confidentiality_profile
        excerpt_text = _optional_text(normalized.get("text")) or _optional_text(normalized.get("excerpt_text"))
        if excerpt_text is not None:
            # Keep lookup payloads aligned with excerpt-hit payload naming so
            # basket promotion and downstream consumers can reuse one text field.
            normalized["text"] = excerpt_text
            normalized["excerpt_text"] = excerpt_text
        elif "excerpt_text" in normalized:
            normalized["excerpt_text"] = None
        text_hash = provenance.get("hash") or provenance.get("excerpt_text_hash") or normalized.get("text_hash")
        if not isinstance(text_hash, str) or not text_hash:
            if excerpt_text is not None:
                text_hash = hashlib.sha256(excerpt_text.encode("utf-8")).hexdigest()
        normalized["text_hash"] = text_hash
        doc_id_value = normalized.get("doc_id")
        if (not isinstance(doc_id_value, str) or not doc_id_value) and isinstance(provenance.get("doc_id"), str):
            doc_id_value = str(provenance["doc_id"])
        elif isinstance(doc_id_value, str) and doc_id_value:
            doc_id_value = str(doc_id_value)
        else:
            doc_id_value = None
        if doc_id_value is not None:
            doc_id_value = _normalize_doc_id(doc_id_value)
            normalized["doc_id"] = doc_id_value

        excerpt_id_value = normalized.get("excerpt_id")
        if (not isinstance(excerpt_id_value, str) or not excerpt_id_value) and isinstance(
            provenance.get("excerpt_id"), str
        ):
            excerpt_id_value = str(provenance["excerpt_id"])
        elif isinstance(excerpt_id_value, str) and excerpt_id_value:
            excerpt_id_value = str(excerpt_id_value)
        else:
            excerpt_id_value = None
        if excerpt_id_value is not None:
            excerpt_id_value = _normalize_excerpt_id(excerpt_id_value)
            normalized["excerpt_id"] = excerpt_id_value

        doc_meta = self._load_doc_meta().get(doc_id_value, {}) if doc_id_value is not None else {}

        source_hash = normalized.get("source_hash")
        if not isinstance(source_hash, str) or not source_hash:
            provenance_source_hash = provenance.get("source_hash")
            if isinstance(provenance_source_hash, str) and provenance_source_hash:
                source_hash = provenance_source_hash
            elif doc_id_value is not None:
                source_hash = self._doc_source_hash(doc_id_value, doc_meta=doc_meta)
        if isinstance(source_hash, str) and source_hash:
            source_hash = source_hash.strip()
        if isinstance(source_hash, str) and source_hash:
            normalized["source_hash"] = source_hash
        else:
            source_hash = None

        doc_type = normalized.get("doc_type")
        if not isinstance(doc_type, str) or not doc_type:
            provenance_doc_type = provenance.get("doc_type")
            if isinstance(provenance_doc_type, str) and provenance_doc_type:
                doc_type = provenance_doc_type
            else:
                meta_doc_type = doc_meta.get("doc_type")
                if isinstance(meta_doc_type, str) and meta_doc_type:
                    doc_type = meta_doc_type
        if isinstance(doc_type, str) and doc_type:
            doc_type = _normalize_doc_type(doc_type)
            normalized["doc_type"] = doc_type
        else:
            doc_type = None

        title_hint_confidentiality_profile = _resolve_title_hint_confidentiality_profile(
            canonical_lookup_confidentiality_profile,
            normalized.get("query_confidentiality_profile"),
            provenance.get("query_confidentiality_profile"),
        )
        explicit_title_hint_confidentiality_profile = (
            canonical_lookup_confidentiality_profile
            or _normalized_profile_text(normalized.get("query_confidentiality_profile"))
            or _normalized_profile_text(provenance.get("query_confidentiality_profile"))
        )
        title_hint = _normalized_text(normalized.get("title_hint"))
        if title_hint is None:
            title_hint = _normalized_text(provenance.get("title_hint"))
        if title_hint is not None:
            if (
                explicit_title_hint_confidentiality_profile is not None
                and not (
                    explicit_title_hint_confidentiality_profile == "confidential"
                    and _looks_like_redacted_title_hint(title_hint)
                )
            ):
                title_hint = self._safe_title_hint(
                    title_hint,
                    confidentiality_profile=explicit_title_hint_confidentiality_profile,
                )
        else:
            doc_meta_title_hint = _normalized_text(doc_meta.get("title_hint"))
            if doc_meta_title_hint is not None:
                title_hint = self._safe_title_hint(
                    doc_meta_title_hint,
                    confidentiality_profile=title_hint_confidentiality_profile,
                )
        if title_hint is not None:
            normalized["title_hint"] = title_hint
            if _normalized_text(provenance.get("title_hint")) is None:
                provenance = {**provenance, "title_hint": title_hint}
        elif "title_hint" in normalized:
            normalized["title_hint"] = None

        doc_identity_fingerprint = normalized.get("doc_identity_fingerprint")
        if not isinstance(doc_identity_fingerprint, str) or not doc_identity_fingerprint:
            provenance_doc_identity_fingerprint = provenance.get("doc_identity_fingerprint")
            if isinstance(provenance_doc_identity_fingerprint, str) and provenance_doc_identity_fingerprint:
                doc_identity_fingerprint = provenance_doc_identity_fingerprint
        if (
            (not isinstance(doc_identity_fingerprint, str) or not doc_identity_fingerprint)
            and doc_id_value is not None
            and isinstance(source_hash, str)
            and source_hash
            and isinstance(doc_type, str)
            and doc_type
        ):
            doc_identity_fingerprint = self._build_doc_identity_fingerprint(
                doc_id=doc_id_value,
                source_hash=source_hash,
                doc_type=doc_type,
            )
        if isinstance(doc_identity_fingerprint, str) and doc_identity_fingerprint:
            normalized["doc_identity_fingerprint"] = doc_identity_fingerprint

        canonical_span = RetrievalService._canonicalize_span(normalized.get("span"))
        if canonical_span is None:
            canonical_span = RetrievalService._canonicalize_span(provenance.get("span"))
        # Fail closed on malformed span payloads so lookup provenance and basket
        # promotion fingerprints stay deterministic across sparse rehydration.
        if canonical_span is not None:
            normalized["span"] = canonical_span
        retrieval_policy = self._retrieval_policy.as_snapshot()
        retrieval_backend = cast(str, retrieval_policy["retrieval_backend"])
        retrieval_mode = cast(str, retrieval_policy["retrieval_mode"])
        active_strategy_ids = list(cast(list[str], retrieval_policy["active_strategy_ids"]))
        deferred_strategy_ids = list(cast(list[str], retrieval_policy["deferred_strategy_ids"]))
        strategies_used = list(active_strategy_ids)
        normalized["retrieval_backend"] = retrieval_backend
        normalized["retrieval_mode"] = retrieval_mode
        normalized["retrieval_policy"] = copy.deepcopy(retrieval_policy)
        # Keep excerpt lookup payloads aligned with the canonical engine
        # retrieval surface so downstream promotion/revise flows do not need a
        # separate lookup-only policy field branch.
        normalized["policy"] = copy.deepcopy(retrieval_policy)
        normalized["active_strategy_ids"] = list(active_strategy_ids)
        normalized["deferred_strategy_ids"] = list(deferred_strategy_ids)
        normalized["strategies_used"] = list(strategies_used)
        excerpt_fingerprint = normalized.get("excerpt_fingerprint")
        if not isinstance(excerpt_fingerprint, str) or not excerpt_fingerprint:
            provenance_excerpt_fingerprint = provenance.get("excerpt_fingerprint")
            if isinstance(provenance_excerpt_fingerprint, str) and provenance_excerpt_fingerprint:
                excerpt_fingerprint = provenance_excerpt_fingerprint
        if not isinstance(excerpt_fingerprint, str) or not excerpt_fingerprint:
            excerpt_fingerprint = RetrievalService._build_excerpt_fingerprint(
                doc_id=str(normalized.get("doc_id") or provenance.get("doc_id") or ""),
                excerpt_id=str(normalized.get("excerpt_id") or provenance.get("excerpt_id") or ""),
                span=canonical_span,
                text_hash=str(text_hash or ""),
                source_hash=str(normalized.get("source_hash") or provenance.get("source_hash") or ""),
            )
        normalized["excerpt_fingerprint"] = excerpt_fingerprint
        doc_fingerprint = normalized.get("doc_fingerprint")
        if not isinstance(doc_fingerprint, str) or not doc_fingerprint:
            provenance_doc_fingerprint = provenance.get("doc_fingerprint")
            if isinstance(provenance_doc_fingerprint, str) and provenance_doc_fingerprint:
                doc_fingerprint = provenance_doc_fingerprint
        if (
            (not isinstance(doc_fingerprint, str) or not doc_fingerprint)
            and doc_id_value is not None
            and isinstance(source_hash, str)
            and source_hash
            and isinstance(doc_type, str)
            and doc_type
        ):
            doc_fingerprint = RetrievalService._build_lookup_doc_fingerprint(
                doc_id=doc_id_value,
                source_hash=source_hash,
                doc_type=doc_type,
                excerpt_id=str(normalized.get("excerpt_id") or provenance.get("excerpt_id") or ""),
                excerpt_fingerprint=excerpt_fingerprint,
                doc_identity_fingerprint=doc_identity_fingerprint,
            )
        if isinstance(doc_fingerprint, str) and doc_fingerprint:
            normalized["doc_fingerprint"] = doc_fingerprint
        excerpt_provenance_fingerprint = normalized.get("excerpt_provenance_fingerprint")
        if not isinstance(excerpt_provenance_fingerprint, str) or not excerpt_provenance_fingerprint:
            provenance_excerpt_provenance_fingerprint = provenance.get("excerpt_provenance_fingerprint")
            if (
                isinstance(provenance_excerpt_provenance_fingerprint, str)
                and provenance_excerpt_provenance_fingerprint
            ):
                excerpt_provenance_fingerprint = provenance_excerpt_provenance_fingerprint
        if not isinstance(excerpt_provenance_fingerprint, str) or not excerpt_provenance_fingerprint:
            excerpt_provenance_fingerprint = RetrievalService._build_excerpt_provenance_fingerprint(
                doc_id=doc_id_value,
                excerpt_id=str(normalized.get("excerpt_id") or provenance.get("excerpt_id") or ""),
                doc_type=doc_type,
                span=canonical_span,
                source_hash=source_hash,
                text_hash=str(text_hash or ""),
                doc_identity_fingerprint=doc_identity_fingerprint,
            )
        normalized["excerpt_provenance_fingerprint"] = excerpt_provenance_fingerprint
        normalized_provenance = {
            **provenance,
            "source_strategy": source_strategy,
        }
        if isinstance(excerpt_id_value, str) and excerpt_id_value:
            normalized_provenance["excerpt_id"] = excerpt_id_value
        if doc_id_value is not None:
            normalized_provenance["doc_id"] = doc_id_value
        if isinstance(source_hash, str) and source_hash:
            normalized_provenance["source_hash"] = source_hash
        if isinstance(doc_type, str) and doc_type:
            normalized_provenance["doc_type"] = doc_type
        if canonical_span is not None:
            normalized_provenance["span"] = canonical_span
        normalized_provenance["text_hash"] = text_hash
        if isinstance(text_hash, str) and text_hash:
            normalized_provenance["hash"] = text_hash
            normalized_provenance["excerpt_text_hash"] = text_hash
        normalized_provenance["excerpt_fingerprint"] = excerpt_fingerprint
        normalized_provenance["excerpt_provenance_fingerprint"] = excerpt_provenance_fingerprint
        if isinstance(doc_identity_fingerprint, str) and doc_identity_fingerprint:
            normalized_provenance["doc_identity_fingerprint"] = doc_identity_fingerprint
        if isinstance(doc_fingerprint, str) and doc_fingerprint:
            normalized_provenance["doc_fingerprint"] = doc_fingerprint
        normalized_provenance["retrieval_backend"] = retrieval_backend
        normalized_provenance["retrieval_mode"] = retrieval_mode
        normalized_provenance["retrieval_policy"] = copy.deepcopy(retrieval_policy)
        normalized_provenance["policy"] = copy.deepcopy(retrieval_policy)
        normalized_provenance["active_strategy_ids"] = list(active_strategy_ids)
        normalized_provenance["deferred_strategy_ids"] = list(deferred_strategy_ids)
        normalized_provenance["strategies_used"] = list(strategies_used)
        normalized_provenance["retrieval_source_strategy"] = source_strategy
        normalized_provenance["lookup_resolution"] = canonical_lookup_resolution
        if canonical_lookup_confidentiality_profile is not None:
            normalized_provenance["lookup_confidentiality_profile"] = canonical_lookup_confidentiality_profile
        top_level_query_fingerprint = _optional_text(normalized.get("query_fingerprint"))
        if (
            top_level_query_fingerprint is not None
            and _optional_text(normalized_provenance.get("query_fingerprint")) is None
        ):
            normalized_provenance["query_fingerprint"] = top_level_query_fingerprint
        top_level_query_text = _normalize_query_text_payload(normalized.get("query_text"))
        if top_level_query_text is not None:
            normalized["query_text"] = top_level_query_text
        if (
            top_level_query_text is not None
            and _normalize_query_text_payload(normalized_provenance.get("query_text")) is None
        ):
            normalized_provenance["query_text"] = top_level_query_text
        top_level_query_scope = _normalize_query_scope_payload(normalized.get("query_scope"))
        if top_level_query_scope is not None and _normalize_query_scope_payload(
            normalized_provenance.get("query_scope")
        ) is None:
            normalized_provenance["query_scope"] = top_level_query_scope
        top_level_query_intent = _normalize_query_intent_payload(normalized.get("query_intent"))
        if top_level_query_intent is not None and _normalize_query_intent_payload(
            normalized_provenance.get("query_intent")
        ) is None:
            normalized_provenance["query_intent"] = top_level_query_intent
        top_level_query_confidentiality_profile = _normalized_profile_text(
            normalized.get("query_confidentiality_profile")
        )
        if (
            top_level_query_confidentiality_profile is not None
            and _normalized_profile_text(normalized_provenance.get("query_confidentiality_profile")) is None
        ):
            normalized_provenance["query_confidentiality_profile"] = top_level_query_confidentiality_profile
        top_level_query_date_range = _normalize_query_date_range_payload(normalized.get("query_date_range"))
        if (
            top_level_query_date_range is not None
            and _normalize_query_date_range_payload(normalized_provenance.get("query_date_range")) is None
        ):
            normalized_provenance["query_date_range"] = top_level_query_date_range
        top_level_candidate_doc_count = _optional_int(normalized.get("candidate_doc_count"))
        if (
            top_level_candidate_doc_count is not None
            and _optional_int(normalized_provenance.get("candidate_doc_count")) is None
        ):
            normalized_provenance["candidate_doc_count"] = top_level_candidate_doc_count
        top_level_fts_shortlist_doc_ids = _normalize_doc_id_list_payload(normalized.get("fts_shortlist_doc_ids"))
        if (
            top_level_fts_shortlist_doc_ids is not None
            and _normalize_doc_id_list_payload(normalized_provenance.get("fts_shortlist_doc_ids")) is None
        ):
            normalized_provenance["fts_shortlist_doc_ids"] = top_level_fts_shortlist_doc_ids
        top_level_matched_terms = _normalize_matched_terms(normalized.get("matched_terms"))
        if top_level_matched_terms is not None and _normalize_matched_terms(
            normalized_provenance.get("matched_terms")
        ) is None:
            normalized_provenance["matched_terms"] = top_level_matched_terms
        top_level_match_count = _optional_int(normalized.get("match_count"))
        if (
            top_level_match_count is not None
            and _optional_int(normalized_provenance.get("match_count")) is None
        ):
            normalized_provenance["match_count"] = top_level_match_count
        top_level_rank = _optional_int(normalized.get("rank"))
        if top_level_rank is not None and _optional_int(normalized_provenance.get("rank")) is None:
            normalized_provenance["rank"] = top_level_rank
        top_level_fts_rank = _optional_float(normalized.get("fts_rank"))
        if top_level_fts_rank is not None and _optional_float(normalized_provenance.get("fts_rank")) is None:
            normalized_provenance["fts_rank"] = top_level_fts_rank
        top_level_section_hint = _normalized_query_hint_text(normalized.get("section_hint"))
        if (
            top_level_section_hint is not None
            and _normalized_query_hint_text(normalized_provenance.get("section_hint")) is None
        ):
            normalized_provenance["section_hint"] = top_level_section_hint
        top_level_section_hint_rank = _optional_int(normalized.get("section_hint_rank"))
        if (
            top_level_section_hint_rank is not None
            and _optional_int(normalized_provenance.get("section_hint_rank")) is None
        ):
            normalized_provenance["section_hint_rank"] = top_level_section_hint_rank
        matched_terms = _normalize_matched_terms(normalized_provenance.get("matched_terms"))
        if matched_terms is not None:
            normalized_provenance["matched_terms"] = matched_terms
            normalized_provenance["match_count"] = len(matched_terms)
        query_date_range = _normalize_query_date_range_payload(normalized_provenance.get("query_date_range"))
        if query_date_range is not None:
            normalized_provenance["query_date_range"] = query_date_range
        query_confidentiality_profile = _normalized_profile_text(
            normalized_provenance.get("query_confidentiality_profile")
        )
        if query_confidentiality_profile is not None:
            normalized_provenance["query_confidentiality_profile"] = query_confidentiality_profile
        query_scope = _normalize_query_scope_payload(normalized_provenance.get("query_scope"))
        if query_scope is not None:
            normalized_provenance["query_scope"] = query_scope
        query_intent = _normalize_query_intent_payload(normalized_provenance.get("query_intent"))
        if query_intent is not None:
            normalized_provenance["query_intent"] = query_intent
        section_hint = _normalized_query_hint_text(normalized_provenance.get("section_hint"))
        if section_hint is not None:
            normalized_provenance["section_hint"] = section_hint
        candidate_doc_count = _optional_int(normalized_provenance.get("candidate_doc_count"))
        if candidate_doc_count is not None:
            normalized_provenance["candidate_doc_count"] = candidate_doc_count
        fts_shortlist_doc_ids = _normalize_doc_id_list_payload(
            normalized_provenance.get("fts_shortlist_doc_ids")
        )
        if fts_shortlist_doc_ids is not None:
            normalized_provenance["fts_shortlist_doc_ids"] = fts_shortlist_doc_ids
        rank = _optional_int(normalized_provenance.get("rank"))
        if rank is not None:
            normalized_provenance["rank"] = rank
        fts_rank = _optional_float(normalized_provenance.get("fts_rank"))
        if fts_rank is not None:
            normalized_provenance["fts_rank"] = fts_rank
        section_hint_rank = _optional_int(normalized_provenance.get("section_hint_rank"))
        if section_hint_rank is not None:
            normalized_provenance["section_hint_rank"] = section_hint_rank
        retrieved_doc_ids = _normalize_doc_id_list_payload(
            normalized.get("retrieved_doc_ids")
            or normalized_provenance.get("retrieved_doc_ids")
            or [doc_id_value]
        )
        if retrieved_doc_ids is not None:
            normalized_provenance["retrieved_doc_ids"] = retrieved_doc_ids
        retrieved_excerpt_ids = _normalize_doc_id_list_payload(
            normalized.get("retrieved_excerpt_ids")
            or normalized_provenance.get("retrieved_excerpt_ids")
            or [excerpt_id_value]
        )
        if retrieved_excerpt_ids is not None:
            normalized_provenance["retrieved_excerpt_ids"] = retrieved_excerpt_ids
        query_snapshot = self._build_excerpt_query_snapshot(
            excerpt=normalized,
            provenance=normalized_provenance,
        )
        if query_snapshot is not None:
            normalized["query"] = copy.deepcopy(query_snapshot)
            normalized_provenance["query"] = copy.deepcopy(query_snapshot)
            derived_query_fingerprint = self._query_fingerprint_from_snapshot(query_snapshot)
            if derived_query_fingerprint is not None:
                normalized["query_fingerprint"] = derived_query_fingerprint
                normalized_provenance["query_fingerprint"] = derived_query_fingerprint
            if _optional_text(normalized.get("query_text")) is None and _optional_text(
                normalized_provenance.get("query_text")
            ) is None:
                query_text = _normalize_query_text_payload(query_snapshot.get("query_text"))
                if query_text is not None:
                    normalized["query_text"] = query_text
                    normalized_provenance["query_text"] = query_text
            if _normalize_query_scope_payload(normalized_provenance.get("query_scope")) is None:
                query_scope = _normalize_query_scope_payload(query_snapshot.get("scope"))
                if query_scope is not None:
                    normalized["query_scope"] = query_scope
                    normalized_provenance["query_scope"] = query_scope
            if _normalize_query_intent_payload(normalized_provenance.get("query_intent")) is None:
                query_intent = _normalize_query_intent_payload(query_snapshot.get("intent"))
                if query_intent is not None:
                    normalized["query_intent"] = query_intent
                    normalized_provenance["query_intent"] = query_intent
            if _normalized_profile_text(normalized_provenance.get("query_confidentiality_profile")) is None:
                query_confidentiality_profile = _normalized_profile_text(
                    query_snapshot.get("confidentiality_profile")
                )
                if query_confidentiality_profile is not None:
                    normalized["query_confidentiality_profile"] = query_confidentiality_profile
                    normalized_provenance["query_confidentiality_profile"] = query_confidentiality_profile
            query_constraints = query_snapshot.get("constraints", {})
            if not isinstance(query_constraints, dict):
                query_constraints = {}
            if _normalize_query_date_range_payload(normalized_provenance.get("query_date_range")) is None:
                query_date_range = _normalize_query_date_range_payload(query_constraints.get("date_range"))
                if query_date_range is not None:
                    normalized["query_date_range"] = query_date_range
                    normalized_provenance["query_date_range"] = query_date_range
            if _normalized_query_hint_text(normalized_provenance.get("section_hint")) is None:
                section_hint = _normalized_query_hint_text(query_constraints.get("section_hint"))
                if section_hint is not None:
                    normalized["section_hint"] = section_hint
                    normalized_provenance["section_hint"] = section_hint
        else:
            normalized.pop("query", None)
            normalized_provenance.pop("query", None)
        lookup_fingerprint = RetrievalService._stable_fingerprint(
            {
                "doc_id": doc_id_value,
                "excerpt_id": normalized.get("excerpt_id"),
                "source_strategy": source_strategy,
                "lookup_resolution": canonical_lookup_resolution,
                "lookup_confidentiality_profile": canonical_lookup_confidentiality_profile,
                # Include the canonical retrieval query context when it is
                # present so excerpt promotion/audit records stay unique across
                # materially different retrieval runs that land on the same
                # excerpt id.
                "query_fingerprint": normalized_provenance.get("query_fingerprint"),
                "query_scope": normalized_provenance.get("query_scope"),
                "query_intent": normalized_provenance.get("query_intent"),
                "query_confidentiality_profile": normalized_provenance.get(
                    "query_confidentiality_profile"
                ),
                "query_date_range": normalized_provenance.get("query_date_range"),
                "candidate_doc_count": normalized_provenance.get("candidate_doc_count"),
                "fts_shortlist_doc_ids": normalized_provenance.get("fts_shortlist_doc_ids"),
                "retrieved_doc_ids": normalized_provenance.get("retrieved_doc_ids"),
                "retrieved_excerpt_ids": normalized_provenance.get("retrieved_excerpt_ids"),
                "retrieval_backend": retrieval_backend,
                "retrieval_mode": retrieval_mode,
                "active_strategy_ids": active_strategy_ids,
                "deferred_strategy_ids": deferred_strategy_ids,
                "excerpt_fingerprint": excerpt_fingerprint,
                "excerpt_provenance_fingerprint": excerpt_provenance_fingerprint,
                "doc_identity_fingerprint": doc_identity_fingerprint,
            }
        )
        result_fingerprint = RetrievalService._build_excerpt_lookup_result_fingerprint(
            lookup_fingerprint=lookup_fingerprint,
            retrieval_policy=retrieval_policy,
            doc_fingerprint=doc_fingerprint,
            excerpt_fingerprint=excerpt_fingerprint,
            excerpt_provenance_fingerprint=excerpt_provenance_fingerprint,
            excerpt_text_hash=text_hash,
        )
        normalized["result_fingerprint"] = result_fingerprint
        normalized["lookup_fingerprint"] = lookup_fingerprint
        normalized_provenance["result_fingerprint"] = result_fingerprint
        normalized_provenance["lookup_fingerprint"] = lookup_fingerprint
        normalized["excerpt_text_hash"] = text_hash
        for key in (
            "result_fingerprint",
            "query_fingerprint",
            "query_scope",
            "query_intent",
            "query_confidentiality_profile",
            "query_date_range",
            "candidate_doc_count",
            "fts_shortlist_doc_ids",
            "matched_terms",
            "match_count",
            "rank",
            "fts_rank",
            "section_hint",
            "section_hint_rank",
            "lookup_confidentiality_profile",
            "retrieved_doc_ids",
            "retrieved_excerpt_ids",
        ):
            value = normalized_provenance.get(key)
            if value is not None:
                normalized[key] = copy.deepcopy(value)
        normalized["basket_promotion"] = self._build_excerpt_lookup_basket_promotion(
            excerpt=normalized,
            provenance=normalized_provenance,
            lookup_fingerprint=lookup_fingerprint,
        )
        normalized["provenance"] = normalized_provenance
        return normalized

    def _build_excerpt_query_snapshot(
        self,
        *,
        excerpt: dict[str, object],
        provenance: dict[str, object],
    ) -> dict[str, object] | None:
        query_payload = excerpt.get("query")
        if not isinstance(query_payload, dict):
            query_payload = provenance.get("query")
        if not isinstance(query_payload, dict):
            query_payload = {}
        query_constraints_payloads: list[dict[str, object]] = []
        for candidate in (
            provenance.get("constraints"),
            excerpt.get("constraints"),
            provenance.get("query_constraints"),
            excerpt.get("query_constraints"),
            query_payload.get("constraints"),
        ):
            if isinstance(candidate, dict):
                query_constraints_payloads.append(candidate)
        query_constraints_payload: dict[str, object] = {}
        for candidate in query_constraints_payloads:
            query_constraints_payload.update(candidate)
        query_text = _normalize_query_text_payload(
            excerpt.get("query_text", provenance.get("query_text", query_payload.get("query_text")))
        )
        query_scope = _normalize_query_scope_payload(
            excerpt.get("query_scope", provenance.get("query_scope", query_payload.get("scope")))
        )
        query_intent = _normalize_query_intent_payload(
            excerpt.get("query_intent", provenance.get("query_intent", query_payload.get("intent")))
        )
        query_confidentiality_profile = _normalized_profile_text(
            excerpt.get(
                "query_confidentiality_profile",
                provenance.get("query_confidentiality_profile", query_payload.get("confidentiality_profile")),
            )
        )
        query_date_range = _normalize_query_date_range_payload(
            excerpt.get(
                "query_date_range",
                provenance.get("query_date_range", query_constraints_payload.get("date_range")),
            )
        )
        section_hint = _normalized_query_hint_text(
            excerpt.get(
                "section_hint",
                provenance.get("section_hint", query_constraints_payload.get("section_hint")),
            )
        )
        max_results = _optional_int(
            query_constraints_payload.get(
                "max_results",
                excerpt.get("max_results", provenance.get("max_results")),
            )
        )
        doc_types = _normalize_query_doc_types_payload(
            query_constraints_payload.get(
                "doc_types",
                excerpt.get("doc_types", provenance.get("doc_types")),
            )
        )
        require_citations = _optional_bool(
            query_constraints_payload.get(
                "require_citations",
                excerpt.get("require_citations", provenance.get("require_citations")),
            )
        )
        prefer_exact_matches = _optional_bool(
            query_constraints_payload.get(
                "prefer_exact_matches",
                excerpt.get("prefer_exact_matches", provenance.get("prefer_exact_matches")),
            )
        )
        query_constraints: dict[str, object] = {}
        if max_results is not None:
            query_constraints["max_results"] = max_results
        if doc_types is not None:
            query_constraints["doc_types"] = doc_types
        if query_date_range is not None:
            query_constraints["date_range"] = query_date_range
        if require_citations is not None:
            query_constraints["require_citations"] = require_citations
        if section_hint is not None:
            query_constraints["section_hint"] = section_hint
        if prefer_exact_matches is not None:
            query_constraints["prefer_exact_matches"] = prefer_exact_matches
        # Fail closed when sparse lookup context cannot identify the original
        # retrieval contract. A partial ``query`` object looks canonical to
        # downstream basket-promotion flows even though it cannot be
        # fingerprinted or audited as a real retrieval request.
        if query_text is None or query_scope is None or query_intent is None:
            return None
        query_snapshot: dict[str, object] = {
            "query_text": query_text,
            "scope": query_scope,
            "intent": query_intent,
        }
        if query_constraints:
            query_snapshot["constraints"] = query_constraints
        query_snapshot["confidentiality_profile"] = query_confidentiality_profile or "confidential"
        return query_snapshot

    @staticmethod
    def _query_fingerprint_from_snapshot(query_snapshot: object) -> str | None:
        if not isinstance(query_snapshot, dict):
            return None
        query_text = _normalize_query_text_payload(query_snapshot.get("query_text"))
        query_scope = _normalize_query_scope_payload(query_snapshot.get("scope"))
        query_intent = _normalize_query_intent_payload(query_snapshot.get("intent"))
        query_confidentiality_profile = _normalized_profile_text(
            query_snapshot.get("confidentiality_profile")
        ) or "confidential"
        if (
            query_text is None
            or query_scope is None
            or query_intent is None
        ):
            return None
        query_constraints = query_snapshot.get("constraints", {})
        if not isinstance(query_constraints, dict):
            query_constraints = {}
        normalized_constraints = {
            "max_results": _optional_int(query_constraints.get("max_results")) or 10,
            "doc_types": _normalize_query_doc_types_payload(query_constraints.get("doc_types")) or [],
            "date_range": _normalize_query_date_range_payload(query_constraints.get("date_range")),
            "require_citations": _optional_bool(query_constraints.get("require_citations")) or False,
            "section_hint": _normalized_query_hint_text(query_constraints.get("section_hint")),
            "prefer_exact_matches": _optional_bool(query_constraints.get("prefer_exact_matches")) or False,
        }
        return RetrievalService._stable_fingerprint(
            {
                "query_text": query_text,
                "scope": query_scope,
                "intent": query_intent,
                "constraints": normalized_constraints,
                "confidentiality_profile": query_confidentiality_profile,
            }
        )

    def _build_excerpt_lookup_basket_promotion(
        self,
        *,
        excerpt: dict[str, object],
        provenance: dict[str, object],
        lookup_fingerprint: str,
    ) -> dict[str, object]:
        query_snapshot = self._build_excerpt_query_snapshot(excerpt=excerpt, provenance=provenance)
        query_constraints = query_snapshot.get("constraints", {}) if isinstance(query_snapshot, dict) else {}
        if not isinstance(query_constraints, dict):
            query_constraints = {}
        retrieval_policy = _normalize_retrieval_policy_snapshot_payload(
            copy.deepcopy(excerpt.get("retrieval_policy", self._retrieval_policy.as_snapshot()))
        )
        active_strategy_ids = _normalize_strategy_id_list_payload(
            excerpt.get("active_strategy_ids", retrieval_policy.get("active_strategy_ids", []))
        )
        deferred_strategy_ids = _normalize_strategy_id_list_payload(
            excerpt.get("deferred_strategy_ids", retrieval_policy.get("deferred_strategy_ids", []))
        )
        promotion = {
            "promotion_ready": True,
            "promotion_source": "lookup_excerpt",
            "citation_available": True,
            "query_text": _normalize_query_text_payload(
                excerpt.get("query_text") or provenance.get("query_text")
            ),
            "query_fingerprint": _optional_text(provenance.get("query_fingerprint")),
            "query_scope": _normalize_query_scope_payload(provenance.get("query_scope")),
            "query_intent": _normalize_query_intent_payload(provenance.get("query_intent")),
            "query_confidentiality_profile": _normalized_profile_text(
                provenance.get("query_confidentiality_profile")
            ),
            "query_constraints": copy.deepcopy(query_constraints),
            "query_max_results": _optional_int(query_constraints.get("max_results")),
            "query_doc_types": _normalize_query_doc_types_payload(query_constraints.get("doc_types")),
            "query_require_citations": _optional_bool(query_constraints.get("require_citations")),
            "query_prefer_exact_matches": _optional_bool(query_constraints.get("prefer_exact_matches")),
            "lookup_resolution": _normalize_lookup_resolution_payload(
                excerpt.get("lookup_resolution") or provenance.get("lookup_resolution")
            ),
            "lookup_confidentiality_profile": _normalize_lookup_confidentiality_profile_payload(
                excerpt.get("lookup_confidentiality_profile")
                or provenance.get("lookup_confidentiality_profile")
            ),
            "query_date_range": _normalize_query_date_range_payload(provenance.get("query_date_range")),
            "candidate_doc_count": _optional_int(provenance.get("candidate_doc_count")),
            "fts_shortlist_doc_ids": _normalize_doc_id_list_payload(provenance.get("fts_shortlist_doc_ids")),
            "result_fingerprint": _optional_text(excerpt.get("result_fingerprint"))
            or _optional_text(provenance.get("result_fingerprint"))
            or lookup_fingerprint,
            "lookup_fingerprint": lookup_fingerprint,
            "doc_id": _optional_text(excerpt.get("doc_id")) or _optional_text(provenance.get("doc_id")),
            "doc_type": _optional_text(excerpt.get("doc_type")) or _optional_text(provenance.get("doc_type")),
            "doc_fingerprint": _optional_text(excerpt.get("doc_fingerprint"))
            or _optional_text(provenance.get("doc_fingerprint")),
            "doc_identity_fingerprint": _optional_text(excerpt.get("doc_identity_fingerprint"))
            or _optional_text(provenance.get("doc_identity_fingerprint")),
            "source_hash": _optional_text(excerpt.get("source_hash")) or _optional_text(provenance.get("source_hash")),
            "title_hint": _optional_text(excerpt.get("title_hint")),
            "excerpt_id": _optional_text(excerpt.get("excerpt_id")) or _optional_text(provenance.get("excerpt_id")),
            "excerpt_fingerprint": _optional_text(excerpt.get("excerpt_fingerprint"))
            or _optional_text(provenance.get("excerpt_fingerprint")),
            "excerpt_provenance_fingerprint": _optional_text(excerpt.get("excerpt_provenance_fingerprint"))
            or _optional_text(provenance.get("excerpt_provenance_fingerprint")),
            "excerpt_text_hash": _optional_text(excerpt.get("excerpt_text_hash"))
            or _optional_text(provenance.get("excerpt_text_hash"))
            or _optional_text(provenance.get("hash")),
            "excerpt_text": _optional_text(excerpt.get("excerpt_text")) or _optional_text(excerpt.get("text")),
            "span": copy.deepcopy(RetrievalService._canonicalize_span(excerpt.get("span"))),
            "source_strategy": _normalize_source_strategy(
                excerpt.get("source_strategy") or provenance.get("source_strategy") or _FTS_SOURCE_STRATEGY
            ),
            "matched_terms": copy.deepcopy(_normalize_matched_terms(provenance.get("matched_terms"))),
            "match_count": provenance.get("match_count"),
            "rank": provenance.get("rank"),
            "fts_rank": provenance.get("fts_rank"),
            "doc_rank": provenance.get("doc_rank"),
            "section_hint": _optional_text(provenance.get("section_hint")),
            "section_hint_rank": provenance.get("section_hint_rank"),
            "retrieval_backend": _normalized_profile_text(
                excerpt.get("retrieval_backend") or provenance.get("retrieval_backend")
            ),
            "retrieval_mode": _normalized_profile_text(
                excerpt.get("retrieval_mode") or provenance.get("retrieval_mode")
            ),
            "policy": copy.deepcopy(retrieval_policy),
            "retrieval_policy": retrieval_policy,
            "active_strategy_ids": active_strategy_ids,
            "deferred_strategy_ids": deferred_strategy_ids,
            "strategies_used": copy.deepcopy(
                _normalize_strategy_id_list_payload(
                    excerpt.get("strategies_used")
                    or provenance.get("strategies_used")
                    or active_strategy_ids
                )
            ),
            "retrieved_doc_ids": _normalize_doc_id_list_payload(
                excerpt.get("retrieved_doc_ids")
                or provenance.get("retrieved_doc_ids")
                or [
                    _optional_text(excerpt.get("doc_id"))
                    or _optional_text(provenance.get("doc_id"))
                ]
            ),
            "retrieved_excerpt_ids": _normalize_doc_id_list_payload(
                excerpt.get("retrieved_excerpt_ids")
                or provenance.get("retrieved_excerpt_ids")
                or [
                    _optional_text(excerpt.get("excerpt_id"))
                    or _optional_text(provenance.get("excerpt_id"))
                ]
            ),
        }
        promotion["promotion_fingerprint"] = self._build_basket_promotion_fingerprint(promotion)
        return promotion

    @staticmethod
    def _build_basket_promotion_fingerprint(payload: dict[str, object]) -> str:
        fingerprint_payload = copy.deepcopy(payload)
        fingerprint_payload.pop("promotion_fingerprint", None)
        fingerprint_payload.pop("source_bundle_fingerprint", None)
        return RetrievalService._stable_fingerprint(fingerprint_payload)

    @staticmethod
    def _build_doc_identity_fingerprint(
        *,
        doc_id: str,
        source_hash: str,
        doc_type: str,
    ) -> str:
        return RetrievalService._stable_fingerprint(
            {
                "doc_id": doc_id,
                "source_hash": source_hash,
                "doc_type": doc_type,
            }
        )

    @staticmethod
    def _build_lookup_doc_fingerprint(
        *,
        doc_id: str,
        source_hash: str,
        doc_type: str,
        excerpt_id: str,
        excerpt_fingerprint: str | None,
        doc_identity_fingerprint: str | None,
    ) -> str:
        return RetrievalService._stable_fingerprint(
            {
                "doc_id": doc_id,
                "source_hash": source_hash,
                "doc_type": doc_type,
                "excerpt_id": excerpt_id,
                "excerpt_fingerprint": excerpt_fingerprint,
                "doc_identity_fingerprint": doc_identity_fingerprint,
            }
        )

    @staticmethod
    def _canonicalize_span(span: object) -> dict[str, object] | None:
        if not isinstance(span, dict):
            return None
        char_range = span.get("char_range")
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

    @staticmethod
    def _build_excerpt_fingerprint(
        *,
        doc_id: str | None,
        excerpt_id: str | None,
        span: dict[str, object] | None,
        text_hash: str | None,
        source_hash: str | None = None,
    ) -> str:
        payload = {
            "doc_id": doc_id,
            "excerpt_id": excerpt_id,
            "span": span,
            "text_hash": text_hash,
            "source_hash": source_hash,
        }
        return RetrievalService._stable_fingerprint(payload)

    @staticmethod
    def _build_excerpt_provenance_fingerprint(
        *,
        doc_id: str | None,
        excerpt_id: str | None,
        doc_type: str | None,
        span: dict[str, object] | None,
        source_hash: str | None,
        text_hash: str | None,
        doc_identity_fingerprint: str | None,
    ) -> str:
        payload = {
            "doc_id": doc_id,
            "excerpt_id": excerpt_id,
            "doc_type": doc_type,
            "span": span,
            "source_hash": source_hash,
            "text_hash": text_hash,
            "doc_identity_fingerprint": doc_identity_fingerprint,
        }
        return RetrievalService._stable_fingerprint(payload)

    @staticmethod
    def _build_excerpt_lookup_result_fingerprint(
        *,
        lookup_fingerprint: str,
        retrieval_policy: dict[str, object],
        doc_fingerprint: str | None,
        excerpt_fingerprint: str,
        excerpt_provenance_fingerprint: str,
        excerpt_text_hash: str,
    ) -> str:
        return RetrievalService._stable_fingerprint(
            {
                "lookup_fingerprint": lookup_fingerprint,
                "retrieval_policy": retrieval_policy,
                "doc_fingerprint": doc_fingerprint,
                "excerpt_fingerprint": excerpt_fingerprint,
                "excerpt_provenance_fingerprint": excerpt_provenance_fingerprint,
                "excerpt_text_hash": excerpt_text_hash,
            }
        )

    @staticmethod
    def _query_fingerprint(query: RetrievalQuery) -> str:
        normalized_constraints = {
            "max_results": query.constraints.max_results,
            "doc_types": list(RetrievalService._normalized_doc_types(query.constraints.doc_types)),
            "date_range": list(query.constraints.date_range) if query.constraints.date_range is not None else None,
            "require_citations": query.constraints.require_citations,
            "section_hint": query.constraints.section_hint,
            "prefer_exact_matches": query.constraints.prefer_exact_matches,
        }
        payload = {
            "query_text": RetrievalService._normalized_query_text(query.query_text),
            "scope": query.scope,
            "intent": query.intent,
            "constraints": normalized_constraints,
            "confidentiality_profile": query.confidentiality_profile,
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def _stable_fingerprint(payload: object) -> str:
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _load_doc_meta(self) -> dict[str, dict[str, object]]:
        payload = self._read_encrypted_json(self._root / _DOC_META_FILE, default={})
        if not isinstance(payload, dict):
            return {}
        out: dict[str, dict[str, object]] = {}
        for key, value in payload.items():
            if isinstance(key, str) and isinstance(value, dict):
                out[key] = value
        return out

    def _read_doc_text(self, doc_id: str) -> str:
        blob = self._root / _DOC_BLOBS / f"{_normalize_doc_id(doc_id)}.enc"
        if not blob.exists():
            raise KeyError(f"unknown doc_id: {doc_id}")
        return decrypt_bytes(blob.read_bytes(), self._key).decode("utf-8")

    def _doc_source_hash(self, doc_id: str, *, doc_meta: dict[str, object] | None = None) -> str:
        if doc_meta is None:
            doc_meta = self._load_doc_meta().get(doc_id, {})
        source_hash = doc_meta.get("source_hash")
        if isinstance(source_hash, str) and source_hash:
            return source_hash
        try:
            text = self._read_doc_text(doc_id)
        except KeyError:
            return ""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _validate_query(self, query: RetrievalQuery) -> None:
        if not query.query_text.strip():
            raise ValueError("query_text is required")
        if not self._query_terms(query.query_text):
            raise ValueError("query_text must contain at least one searchable term")
        if query.constraints.max_results < 1:
            raise ValueError("max_results must be greater than zero")
        _reject_deferred_scope(query.scope)
        if query.scope != "vault" and not any(query.scope.startswith(prefix) for prefix in ("collection:", "doc:")):
            raise ValueError("unsupported scope")
        if query.intent not in _SUPPORTED_RETRIEVAL_INTENTS:
            raise ValueError(f"unsupported intent: {query.intent}")
        if query.confidentiality_profile not in _SUPPORTED_CONFIDENTIALITY_PROFILES:
            raise ValueError(f"unsupported confidentiality_profile: {query.confidentiality_profile}")
        if query.confidentiality_profile == "confidential":
            # No network strategies are enabled in this retrieval implementation.
            pass

    @staticmethod
    def _safe_title_hint(value: str, *, confidentiality_profile: str) -> str | None:
        if not value:
            return None
        if confidentiality_profile == "confidential":
            return f"doc:{hashlib.sha256(value.encode('utf-8')).hexdigest()[:10]}"
        return value[:80]

    def _read_encrypted_json(self, path: Path, *, default: object) -> object:
        if not path.exists():
            return default
        plaintext = decrypt_bytes(path.read_bytes(), self._key)
        try:
            return json.loads(plaintext.decode("utf-8"))
        except json.JSONDecodeError:
            return default

    def _write_encrypted_json(self, path: Path, payload: object) -> None:
        plaintext = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        path.write_bytes(encrypt_bytes(plaintext, self._key))

    def _load_or_create_key(self) -> bytes:
        path = self._root / _KEY_FILE
        if path.exists():
            raw = path.read_bytes()
            if len(raw) < 32:
                raise ValueError("retrieval key file invalid")
            return raw[:32]
        raw = (uuid.uuid4().bytes + uuid.uuid4().bytes)[:32]
        path.write_bytes(raw)
        return raw

    @contextmanager
    def _connect_fts_db(self) -> Iterator[sqlite3.Connection]:
        with NamedTemporaryFile(prefix="retrieval_fts_", suffix=".sqlite3", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            db_path = self._root / _FTS_DB_FILE
            if db_path.exists():
                plaintext = decrypt_bytes(db_path.read_bytes(), self._key)
                tmp_path.write_bytes(plaintext)
            conn = sqlite3.connect(str(tmp_path))
            conn.row_factory = sqlite3.Row
            try:
                self._initialize_fts_schema(conn)
                yield conn
                conn.commit()
            finally:
                conn.close()
            encrypted = encrypt_bytes(tmp_path.read_bytes(), self._key)
            out_tmp = db_path.with_suffix(".tmp")
            out_tmp.write_bytes(encrypted)
            out_tmp.replace(db_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def _initialize_fts_schema(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS fts_entries USING fts5(
              doc_id UNINDEXED,
              excerpt_id UNINDEXED,
              doc_type UNINDEXED,
              title_hint UNINDEXED,
              char_start UNINDEXED,
              char_end UNINDEXED,
              text,
              tokenize = 'unicode61'
            )
            """
        )

    def _query_fts_db(self, sql: str, params: tuple[object, ...]) -> list[sqlite3.Row]:
        with self._connect_fts_db() as conn:
            rows = conn.execute(sql, params).fetchall()
        return rows

    def _fetch_fts_row(self, excerpt_id: str) -> sqlite3.Row | None:
        normalized_excerpt_id = _normalize_excerpt_id(excerpt_id)
        rows = self._query_fts_db(
            "SELECT doc_id, excerpt_id, doc_type, title_hint, char_start, char_end, text FROM fts_entries "
            "WHERE excerpt_id = ? LIMIT 1",
            (normalized_excerpt_id,),
        )
        return rows[0] if rows else None

    @staticmethod
    def _build_fts_match_query(query_text: str) -> tuple[str, tuple[str, ...]]:
        terms = RetrievalService._query_terms(query_text)
        if terms:
            return " OR ".join(f'"{term}"' for term in terms), tuple(terms)
        raise ValueError("query_text must contain at least one searchable term")

    @staticmethod
    def _normalized_doc_types(doc_types: tuple[str, ...]) -> tuple[str, ...]:
        return _canonicalize_doc_types(doc_types)

    @staticmethod
    def _matched_query_terms(query_terms: tuple[str, ...], text: str) -> tuple[str, ...]:
        text_lower = text.casefold()
        return tuple(term for term in query_terms if term in text_lower)

    @staticmethod
    def _query_terms(query_text: str) -> tuple[str, ...]:
        terms: list[str] = []
        seen: set[str] = set()
        for term in re.findall(r"\w+", query_text.casefold()):
            if term in seen:
                continue
            seen.add(term)
            terms.append(term)
        return tuple(terms)

    @staticmethod
    def _normalized_query_text(query_text: str) -> str:
        return " ".join(query_text.casefold().split())
