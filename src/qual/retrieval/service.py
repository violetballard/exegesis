from __future__ import annotations

import copy
import hashlib
import json
import re
import sqlite3
import uuid
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


def _required_compact_text(value: object, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be text")
    text = " ".join(value.split())
    if not text:
        raise ValueError(f"{field_name} is required")
    return text


def _optional_list_like(value: object) -> list[object] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return copy.deepcopy(value)
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _normalize_supported_value(value: object, *, field_name: str, allowed: set[str]) -> str:
    normalized = str(value).strip().casefold()
    if normalized not in allowed:
        raise ValueError(f"unsupported {field_name}: {normalized}")
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
            if len(normalized) != 2 or any(not value for value in normalized):
                raise ValueError("date_range must contain exactly two non-empty values")
            object.__setattr__(self, "date_range", normalized)
        object.__setattr__(self, "section_hint", _optional_text(self.section_hint))


@dataclass(frozen=True)
class RetrievalQuery:
    query_text: str
    scope: str
    intent: Literal["lookup", "compare", "summarize", "quote_find", "outline_support"]
    constraints: RetrievalConstraints = field(default_factory=RetrievalConstraints)
    confidentiality_profile: Literal["confidential", "standard"] = "confidential"

    def __post_init__(self) -> None:
        object.__setattr__(self, "query_text", _required_compact_text(self.query_text, field_name="query_text"))
        object.__setattr__(self, "scope", _required_compact_text(self.scope, field_name="scope"))
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
        excerpt_text_hash = self.provenance.get("excerpt_text_hash") or self.provenance.get("hash")
        if isinstance(excerpt_text_hash, str) and excerpt_text_hash:
            payload["excerpt_text_hash"] = excerpt_text_hash
        rank = self.provenance.get("rank")
        if isinstance(rank, int):
            payload["rank"] = rank
        matched_terms = self.provenance.get("matched_terms")
        if isinstance(matched_terms, list):
            payload["matched_terms"] = copy.deepcopy(matched_terms)
        match_count = self.provenance.get("match_count")
        if isinstance(match_count, int):
            payload["match_count"] = match_count
        retrieval_backend = self.provenance.get("retrieval_backend")
        if isinstance(retrieval_backend, str) and retrieval_backend:
            payload["retrieval_backend"] = retrieval_backend
        retrieval_mode = self.provenance.get("retrieval_mode")
        if isinstance(retrieval_mode, str) and retrieval_mode:
            payload["retrieval_mode"] = retrieval_mode
        retrieval_policy = self.provenance.get("retrieval_policy")
        if isinstance(retrieval_policy, dict):
            payload["retrieval_policy"] = copy.deepcopy(retrieval_policy)
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
        top_excerpt_text_hash = self.provenance.get("top_excerpt_text_hash")
        if isinstance(top_excerpt_text_hash, str) and top_excerpt_text_hash:
            payload["top_excerpt_text_hash"] = top_excerpt_text_hash
        top_excerpt_span = self.provenance.get("top_excerpt_span")
        if isinstance(top_excerpt_span, dict):
            payload["top_excerpt_span"] = copy.deepcopy(top_excerpt_span)
        top_excerpt_rank = self.provenance.get("top_excerpt_rank")
        if isinstance(top_excerpt_rank, int):
            payload["top_excerpt_rank"] = top_excerpt_rank
        top_fts_rank = self.provenance.get("top_fts_rank")
        if isinstance(top_fts_rank, (int, float)):
            payload["top_fts_rank"] = top_fts_rank
        retrieval_backend = self.provenance.get("retrieval_backend")
        if isinstance(retrieval_backend, str) and retrieval_backend:
            payload["retrieval_backend"] = retrieval_backend
        retrieval_mode = self.provenance.get("retrieval_mode")
        if isinstance(retrieval_mode, str) and retrieval_mode:
            payload["retrieval_mode"] = retrieval_mode
        retrieval_policy = self.provenance.get("retrieval_policy")
        if isinstance(retrieval_policy, dict):
            payload["retrieval_policy"] = copy.deepcopy(retrieval_policy)
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
        retrieval_source_bundle = self._retrieval_source_bundle_snapshot(
            query=query,
            retrieval_policy=retrieval_policy,
            citation_bundle=citation_bundle,
            citation_status=citation_status,
            retrieval_summary=retrieval_summary,
        )
        basket_promotion_items = self.basket_promotion_items()
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
            retrieval_diagnostics=dict(self.diagnostics),
            retrieval_manifest=dict(self.diagnostics["retrieval_manifest"]),
            retrieval_evidence=dict(self.evidence),
            retrieval_provenance=retrieval_provenance,
            source_bundle_fingerprint=cast(str, retrieval_source_bundle["source_bundle_fingerprint"]),
            retrieval_source_bundle=retrieval_source_bundle,
            basket_promotion_items=basket_promotion_items,
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
        fts_shortlist_doc_ids = self.diagnostics.get("fts_shortlist_doc_ids", [])
        if isinstance(fts_shortlist_doc_ids, list):
            fts_shortlist_doc_ids = copy.deepcopy(fts_shortlist_doc_ids)
        elif isinstance(fts_shortlist_doc_ids, tuple):
            fts_shortlist_doc_ids = list(fts_shortlist_doc_ids)
        else:
            fts_shortlist_doc_ids = []
        return {
            "query_fingerprint": self.diagnostics["query_fingerprint"],
            "result_fingerprint": self.result_fingerprint,
            "query_scope": self.query.scope,
            "query_intent": self.query.intent,
            "query_date_range": query_date_range,
            "candidate_doc_count": self.diagnostics.get("candidate_doc_count"),
            "fts_shortlist_doc_ids": fts_shortlist_doc_ids,
            "retrieval_backend": self.diagnostics["retrieval_backend"],
            "retrieval_mode": self.diagnostics["retrieval_mode"],
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
        return copy.deepcopy(
            self._retrieval_provenance_snapshot(
                citation_bundle=citation_bundle,
                citation_status=citation_status,
                retrieval_policy=self._retrieval_policy_snapshot(),
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
        }

    def retrieval_context_bundle(self) -> dict[str, object]:
        """Return the canonical retrieval context for drafting, patching, and research flows."""

        downstream_payload = self.to_downstream_payload()
        basket_promotion_items = self.basket_promotion_items()
        return {
            "audit_ref": self.audit_ref,
            "result_fingerprint": self.result_fingerprint,
            "retrieval_downstream_payload": copy.deepcopy(downstream_payload),
            "retrieval_citation_bundle": copy.deepcopy(downstream_payload["retrieval_citation_bundle"]),
            "retrieval_doc_bundle": copy.deepcopy(downstream_payload["retrieval_doc_bundle"]),
            "retrieval_excerpt_bundle": copy.deepcopy(downstream_payload["retrieval_excerpt_bundle"]),
            "retrieval_provenance": copy.deepcopy(downstream_payload["retrieval_provenance"]),
            "retrieval_source_bundle": copy.deepcopy(downstream_payload["retrieval_source_bundle"]),
            "retrieval_evidence": copy.deepcopy(downstream_payload["retrieval_evidence"]),
            "basket_promotion_items": copy.deepcopy(basket_promotion_items),
            "basket_item_ids": [str(item["item_id"]) for item in basket_promotion_items],
        }

    def basket_promotion_items(self) -> list[dict[str, object]]:
        """Return deterministic excerpt references ready for context-basket promotion."""

        items: list[dict[str, object]] = []
        for hit in self.hits:
            if hit.excerpt_id is None:
                continue
            items.append(
                {
                    "item_id": hit.excerpt_id,
                    "item_type": "excerpt",
                    "doc_id": hit.doc_id,
                    "doc_type": hit.provenance.get("doc_type"),
                    "title_hint": hit.title_hint,
                    "source_hash": hit.provenance.get("source_hash"),
                    "excerpt_id": hit.excerpt_id,
                    "excerpt_text": hit.excerpt_text,
                    "excerpt_fingerprint": hit.provenance.get("excerpt_fingerprint"),
                    "excerpt_text_hash": hit.provenance.get("excerpt_text_hash") or hit.provenance.get("hash"),
                    "span": copy.deepcopy(hit.provenance.get("span")),
                    "rank": hit.provenance.get("rank"),
                    "source_strategy": hit.source_strategy,
                    "retrieval_backend": hit.provenance.get("retrieval_backend"),
                    "retrieval_mode": hit.provenance.get("retrieval_mode"),
                    "query_scope": self.query.scope,
                    "query_intent": self.query.intent,
                    "query_fingerprint": hit.provenance.get("query_fingerprint"),
                    "result_fingerprint": self.result_fingerprint,
                }
            )
        return items

    def _query_snapshot(self) -> dict[str, object]:
        return {
            "query_text": self.query.query_text,
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

    def _citation_status_snapshot(self) -> dict[str, object]:
        return {
            "required": self.query.constraints.require_citations,
            "available": bool(self.hits),
            "satisfied": (not self.query.constraints.require_citations) or bool(self.hits),
            "doc_count": len(self.doc_hits),
            "excerpt_count": len(self.hits),
        }

    def _doc_citation_snapshots(self) -> list[dict[str, object]]:
        return [
            {
                "doc_id": doc_hit.doc_id,
                "source_hash": doc_hit.source_hash,
                "doc_fingerprint": doc_hit.provenance.get("doc_fingerprint"),
                "doc_identity_fingerprint": doc_hit.provenance.get("doc_identity_fingerprint"),
                "doc_rank": doc_hit.provenance.get("doc_rank"),
                "top_excerpt_id": doc_hit.top_excerpt_id,
                "top_excerpt_fingerprint": doc_hit.provenance.get("top_excerpt_fingerprint"),
                "top_excerpt_text_hash": doc_hit.provenance.get("top_excerpt_text_hash"),
                "source_strategy": doc_hit.provenance.get("source_strategy"),
            }
            for doc_hit in self.doc_hits
        ]

    def _excerpt_citation_snapshots(self) -> list[dict[str, object]]:
        return [
            {
                "doc_id": hit.doc_id,
                "excerpt_id": hit.excerpt_id,
                "doc_type": hit.provenance.get("doc_type"),
                "source_hash": hit.provenance.get("source_hash"),
                "excerpt_fingerprint": hit.provenance.get("excerpt_fingerprint"),
                "excerpt_text_hash": hit.provenance.get("excerpt_text_hash") or hit.provenance.get("hash"),
                "match_count": hit.provenance.get("match_count"),
                "matched_terms": hit.provenance.get("matched_terms"),
                "fts_rank": hit.provenance.get("fts_rank"),
                "rank": hit.provenance.get("rank"),
                "span": hit.provenance.get("span"),
                "source_strategy": hit.provenance.get("source_strategy"),
                "retrieval_backend": hit.provenance.get("retrieval_backend"),
                "retrieval_mode": hit.provenance.get("retrieval_mode"),
            }
            for hit in self.hits
            if hit.excerpt_id is not None
        ]

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
        return {
            "query_fingerprint": self.diagnostics["query_fingerprint"],
            "result_fingerprint": self.result_fingerprint,
            "retrieval_backend": self.diagnostics["retrieval_backend"],
            "retrieval_mode": self.diagnostics["retrieval_mode"],
            "retrieval_policy": copy.deepcopy(retrieval_policy),
            "doc_count": len(self.doc_hits),
            "excerpt_count": len(self.hits),
            "doc_ids": [doc_hit.doc_id for doc_hit in self.doc_hits],
            "doc_fingerprints": doc_fingerprints,
            "doc_identity_fingerprints": doc_identity_fingerprints,
            "excerpt_ids": [hit.excerpt_id for hit in self.hits if hit.excerpt_id is not None],
            "excerpt_fingerprints": excerpt_fingerprints,
            "excerpt_text_hashes": excerpt_text_hashes,
            "top_excerpt_fingerprints": top_excerpt_fingerprints,
            "top_excerpt_text_hashes": top_excerpt_text_hashes,
            "primary_doc_id": self.doc_hits[0].doc_id if self.doc_hits else None,
            "primary_excerpt_id": self.hits[0].excerpt_id if self.hits else None,
            "primary_doc_fingerprint": self.doc_hits[0].provenance.get("doc_fingerprint") if self.doc_hits else None,
            "primary_doc_identity_fingerprint": self.doc_hits[0].provenance.get("doc_identity_fingerprint")
            if self.doc_hits
            else None,
            "primary_excerpt_fingerprint": self.hits[0].provenance.get("excerpt_fingerprint") if self.hits else None,
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
    ) -> dict[str, object]:
        primary_doc_hit = self.doc_hits[0] if self.doc_hits else None
        primary_excerpt_hit = self.hits[0] if self.hits else None
        return {
            "query_fingerprint": self.diagnostics["query_fingerprint"],
            "query_scope": self.query.scope,
            "query_intent": self.query.intent,
            "query_date_range": (
                list(self.query.constraints.date_range)
                if self.query.constraints.date_range is not None
                else None
            ),
            "result_fingerprint": self.result_fingerprint,
            "retrieval_backend": self.diagnostics["retrieval_backend"],
            "retrieval_mode": self.diagnostics["retrieval_mode"],
            "retrieval_policy": retrieval_policy,
            "active_strategy_ids": list(self.diagnostics["active_strategy_ids"]),
            "deferred_strategy_ids": list(self.diagnostics["deferred_strategy_ids"]),
            "doc_hits_fingerprint": self.diagnostics["doc_hits_fingerprint"],
            "excerpt_hits_fingerprint": self.diagnostics["excerpt_hits_fingerprint"],
            "candidate_doc_count": self.diagnostics.get("candidate_doc_count"),
            "fts_shortlist_doc_ids": list(self.diagnostics.get("fts_shortlist_doc_ids", [])),
            "primary_doc_id": primary_doc_hit.doc_id if primary_doc_hit is not None else None,
            "primary_doc_fingerprint": primary_doc_hit.provenance.get("doc_fingerprint") if primary_doc_hit is not None else None,
            "primary_doc_identity_fingerprint": primary_doc_hit.provenance.get("doc_identity_fingerprint")
            if primary_doc_hit is not None
            else None,
            "primary_excerpt_id": primary_excerpt_hit.excerpt_id if primary_excerpt_hit is not None else None,
            "primary_excerpt_fingerprint": primary_excerpt_hit.provenance.get("excerpt_fingerprint")
            if primary_excerpt_hit is not None
            else None,
            "primary_excerpt_text_hash": (
                primary_excerpt_hit.provenance.get("excerpt_text_hash") or primary_excerpt_hit.provenance.get("hash")
                if primary_excerpt_hit is not None
                else None
            ),
            "citation_status": citation_status,
            "doc_count": citation_bundle["doc_count"],
            "excerpt_count": citation_bundle["excerpt_count"],
            "doc_citations": citation_bundle["doc_citations"],
            "excerpt_citations": citation_bundle["excerpt_citations"],
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
        retrieval_provenance = self._retrieval_provenance_snapshot(
            citation_bundle=citation_bundle,
            citation_status=citation_status,
            retrieval_policy=retrieval_policy,
        )
        return {
            "result_fingerprint": self.result_fingerprint,
            "query_fingerprint": self.diagnostics["query_fingerprint"],
            "query_scope": self.query.scope,
            "query_intent": self.query.intent,
            "query_date_range": query_date_range,
            "retrieval_backend": self.diagnostics["retrieval_backend"],
            "retrieval_mode": self.diagnostics["retrieval_mode"],
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
        }

    def _retrieval_source_bundle_snapshot(
        self,
        *,
        query: dict[str, object] | None = None,
        retrieval_policy: dict[str, object] | None = None,
        citation_bundle: dict[str, object] | None = None,
        citation_status: dict[str, object] | None = None,
        retrieval_summary: dict[str, object] | None = None,
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
        basket_promotion_items = self.basket_promotion_items()
        source_bundle = {
            "result_fingerprint": self.result_fingerprint,
            "query_fingerprint": self.diagnostics["query_fingerprint"],
            "query": query_snapshot,
            "policy": copy.deepcopy(retrieval_policy_snapshot),
            "retrieval_backend": self.diagnostics["retrieval_backend"],
            "retrieval_mode": self.diagnostics["retrieval_mode"],
            "citation_status": copy.deepcopy(citation_status_snapshot),
            "retrieval_citation_bundle": copy.deepcopy(citation_bundle_snapshot),
            "retrieval_summary": retrieval_summary_snapshot,
            "retrieval_doc_bundle": copy.deepcopy(self.retrieval_doc_bundle()),
            "retrieval_excerpt_bundle": copy.deepcopy(self.retrieval_excerpt_bundle()),
            "doc_hits": [doc_hit.as_dict() for doc_hit in self.doc_hits],
            "excerpt_hits": [hit.as_dict() for hit in self.hits],
            "retrieval_manifest": copy.deepcopy(self.diagnostics["retrieval_manifest"]),
            "retrieval_evidence": copy.deepcopy(self.evidence),
            "basket_promotion_items": copy.deepcopy(basket_promotion_items),
            "basket_item_ids": [str(item["item_id"]) for item in basket_promotion_items],
            "retrieval_provenance": copy.deepcopy(
                self._retrieval_provenance_snapshot(
                    citation_bundle=citation_bundle_snapshot,
                    citation_status=citation_status_snapshot,
                    retrieval_policy=retrieval_policy_snapshot,
                )
            ),
        }
        # Fingerprint the source snapshot itself so copies can be verified deterministically.
        source_bundle["source_bundle_fingerprint"] = RetrievalService._stable_fingerprint(
            {key: value for key, value in source_bundle.items() if key != "source_bundle_fingerprint"}
        )
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

    def add_or_update_document(
        self,
        *,
        doc_id: str,
        doc_type: str,
        text: str,
        title_hint: str | None = None,
    ) -> None:
        content = text.encode("utf-8")
        source_hash = hashlib.sha256(content).hexdigest()
        blob_path = self._root / _DOC_BLOBS / f"{doc_id}.enc"
        blob_path.write_bytes(encrypt_bytes(content, self._key))

        meta = self._load_doc_meta()
        meta[doc_id] = {
            "doc_id": doc_id,
            "doc_type": doc_type,
            "title_hint": title_hint,
            "source_hash": source_hash,
            "size_bytes": len(content),
            "updated_at": self._now_fn().isoformat(),
        }
        self._write_encrypted_json(self._root / _DOC_META_FILE, meta)
        self._upsert_fts_entries(doc_id=doc_id, doc_type=doc_type, title_hint=title_hint, text=text)
        self._fts.clear_cache()

    def build_pageindex(self, *, doc_id: str, options: DocIndexBuildOptions | None = None) -> str:
        source = self._read_doc_text(doc_id)
        build_opts = options if options is not None else DocIndexBuildOptions()
        job = self._docindex.build(doc_id, source.encode("utf-8"), build_opts)
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

        return self.retrieve_fts(query).citation_bundle()

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

        return self.retrieve_auto(query).citation_bundle()

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

    def fetch_fts_excerpt(self, excerpt_id: str) -> dict[str, object]:
        """Backward-compatible alias for the canonical FTS-only excerpt lookup path."""

        return self._lookup_fts_excerpt(excerpt_id, lookup_entrypoint="fetch_fts_excerpt")

    def retrieve_fts_excerpt(self, excerpt_id: str) -> dict[str, object]:
        """Return an excerpt payload using the canonical FTS-only lookup path."""

        return self._lookup_fts_excerpt(excerpt_id, lookup_entrypoint="retrieve_fts_excerpt")

    def _lookup_fts_excerpt(self, excerpt_id: str, *, lookup_entrypoint: str) -> dict[str, object]:
        fts_excerpt = self._find_fts_excerpt(excerpt_id)
        if fts_excerpt is None:
            raise KeyError(f"unknown excerpt_id: {excerpt_id}")
        self._record_excerpt_lookup_audit(
            fts_excerpt,
            lookup_entrypoint=lookup_entrypoint,
            lookup_resolution="fts",
        )
        return self._normalize_excerpt_payload(
            fts_excerpt,
            source_strategy="fts",
            lookup_resolution="fts",
        )

    def _record_excerpt_lookup_audit(
        self,
        excerpt: dict[str, object],
        *,
        lookup_entrypoint: str,
        lookup_resolution: str,
    ) -> None:
        """Record a compact audit trail for deterministic excerpt lookups."""

        span = excerpt.get("span")
        if not isinstance(span, dict):
            span = None
        self._audit.record(
            name="excerpt_lookup_completed",
            metadata={
                "excerpt_id": excerpt.get("excerpt_id"),
                "doc_id": excerpt.get("doc_id"),
                "doc_type": excerpt.get("doc_type"),
                "source_strategy": excerpt.get("source_strategy"),
                "lookup_entrypoint": lookup_entrypoint,
                "lookup_resolution": lookup_resolution,
                "retrieval_backend": excerpt.get("retrieval_backend"),
                "retrieval_mode": excerpt.get("retrieval_mode"),
                "retrieval_policy": copy.deepcopy(self._retrieval_policy.as_snapshot()),
                "source_hash": excerpt.get("source_hash"),
                "text_hash": excerpt.get("text_hash"),
                "excerpt_fingerprint": excerpt.get("excerpt_fingerprint"),
                "span": copy.deepcopy(span),
            },
        )

    def _run_fts_first_retrieval(self, query: RetrievalQuery) -> RetrievalResult:
        started = self._now_fn()
        query_fingerprint = self._query_fingerprint(query)
        retrieval_policy = retrieval_policy_snapshot()
        fts_shortlist_limit = self._fts_shortlist_limit(query.constraints.max_results)
        date_range = query.constraints.date_range
        fts_candidate_scan_limit = self._fts_candidate_scan_limit(fts_shortlist_limit, date_range=date_range)
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
            fts_shortlist_doc_ids=fts_shortlist,
        )
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
        result_fingerprint = self._build_result_fingerprint(
            query_fingerprint=query_fingerprint,
            retrieval_manifest=retrieval_manifest,
        )
        retrieval_evidence = self._build_retrieval_evidence(
            query=query,
            doc_hits=doc_hits,
            hits=merged_hits,
            retrieval_manifest=retrieval_manifest,
            query_fingerprint=query_fingerprint,
            result_fingerprint=result_fingerprint,
            retrieval_policy=retrieval_policy,
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
            "doc_scope_id": self._doc_scope_id(query.scope),
            "date_range": list(date_range) if date_range is not None else None,
            "fts_shortlist_limit": fts_shortlist_limit,
            "fts_candidate_scan_limit": fts_candidate_scan_limit,
            "candidate_doc_count": effective_candidate_doc_count,
            "fts_shortlist_count": len(fts_shortlist),
            "fts_shortlist_doc_ids": list(fts_shortlist),
            "strategies_used": list(retrieval_policy["active_strategy_ids"]),
            "elapsed_ms_by_strategy": {fts_run.strategy_id: fts_run.elapsed_ms},
            "caches_used": {fts_run.strategy_id: fts_run.cache_used},
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
                "date_range": diagnostics["date_range"],
                "active_strategy_ids": diagnostics["active_strategy_ids"],
                "deferred_strategy_ids": diagnostics["deferred_strategy_ids"],
                "strategies_used": diagnostics["strategies_used"],
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
        return RetrievalResult(
            query=query,
            doc_hits=doc_hits,
            hits=merged_hits,
            diagnostics=diagnostics,
            evidence=retrieval_evidence,
            audit_ref=audit.event_id,
            result_fingerprint=result_fingerprint,
        )

    def fetch_excerpt(self, excerpt_id: str) -> dict[str, object]:
        """Return an excerpt payload using the canonical FTS-only lookup path."""

        return self._lookup_fts_excerpt(excerpt_id, lookup_entrypoint="fetch_excerpt")

    def _run_fts_hits(self, query: RetrievalQuery, candidate_doc_ids: tuple[str, ...]) -> list[RetrievalHit]:
        match_query, query_terms = self._build_fts_match_query(query.query_text)
        exact_phrase = self._normalized_query_text(query.query_text)
        scope_doc = self._doc_scope_id(query.scope)
        allowed_doc_types = self._normalized_doc_types(query.constraints.doc_types)
        effective_candidate_doc_count = self._effective_candidate_doc_count(query.scope, candidate_doc_ids)
        select_exact_rank = "CASE WHEN instr(lower(text), ?) > 0 THEN 0 ELSE 1 END AS exact_rank" if query.constraints.prefer_exact_matches else "0 AS exact_rank"
        where_clauses = ["fts_entries MATCH ?"]
        params: list[object] = []
        if query.constraints.prefer_exact_matches:
            params.append(exact_phrase)
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
            f"bm25(fts_entries) AS fts_rank, {select_exact_rank} "
            "FROM fts_entries "
            f"WHERE {' AND '.join(where_clauses)} "
            "ORDER BY exact_rank ASC, fts_rank ASC, doc_id ASC, char_start ASC, char_end ASC, excerpt_id ASC "
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
                query_scope=query.scope,
                query_intent=query.intent,
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
                    title_hint=self._safe_title_hint(query, str(row["title_hint"] or "")),
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
                        "top_excerpt_span": top_hit.provenance.get("span"),
                        "top_matched_terms": top_hit.provenance.get("matched_terms"),
                        "top_match_count": top_hit.provenance.get("match_count"),
                        "top_excerpt_rank": top_hit.provenance.get("rank"),
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
        result_fingerprint: str,
        retrieval_policy: dict[str, object],
    ) -> dict[str, object]:
        doc_citations: list[dict[str, object]] = []
        for doc_hit in doc_hits:
            doc_citations.append(
                {
                    "doc_id": doc_hit.doc_id,
                    "doc_type": doc_hit.provenance.get("doc_type"),
                    "source_hash": doc_hit.source_hash,
                    "doc_fingerprint": doc_hit.provenance.get("doc_fingerprint"),
                    "doc_identity_fingerprint": doc_hit.provenance.get("doc_identity_fingerprint"),
                    "top_excerpt_id": doc_hit.top_excerpt_id,
                    "top_excerpt_fingerprint": doc_hit.provenance.get("top_excerpt_fingerprint"),
                    "top_excerpt_text_hash": doc_hit.provenance.get("top_excerpt_text_hash"),
                    "top_excerpt_span": doc_hit.provenance.get("top_excerpt_span"),
                    "excerpt_ids": list(doc_hit.provenance.get("excerpt_ids", [])),
                    "excerpt_count": doc_hit.excerpt_count,
                    "matched_terms": doc_hit.provenance.get("top_matched_terms"),
                }
            )

        excerpt_citations: list[dict[str, object]] = []
        for hit in hits:
            if hit.excerpt_id is None:
                continue
            excerpt_citations.append(
                {
                    "doc_id": hit.doc_id,
                    "excerpt_id": hit.excerpt_id,
                    "doc_type": hit.provenance.get("doc_type"),
                    "source_hash": hit.provenance.get("source_hash"),
                    "excerpt_fingerprint": hit.provenance.get("excerpt_fingerprint"),
                    "excerpt_text_hash": hit.provenance.get("excerpt_text_hash") or hit.provenance.get("hash"),
                    "span": hit.provenance.get("span"),
                    "matched_terms": hit.provenance.get("matched_terms"),
                    "match_count": hit.provenance.get("match_count"),
                    "rank": hit.provenance.get("rank"),
                    "fts_rank": hit.provenance.get("fts_rank"),
                    "source_strategy": hit.provenance.get("source_strategy"),
                    "retrieval_backend": hit.provenance.get("retrieval_backend"),
                    "retrieval_mode": hit.provenance.get("retrieval_mode"),
                }
            )

        return {
            "query_fingerprint": query_fingerprint,
            "result_fingerprint": result_fingerprint,
            "query_scope": query.scope,
            "query_intent": query.intent,
            "retrieval_policy": dict(retrieval_policy),
            "retrieval_backend": cast(str, retrieval_policy["retrieval_backend"]),
            "retrieval_mode": cast(str, retrieval_policy["retrieval_mode"]),
            "active_strategy_ids": list(cast(list[str], retrieval_policy["active_strategy_ids"])),
            "deferred_strategy_ids": list(cast(list[str], retrieval_policy["deferred_strategy_ids"])),
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
            "basket_promotion_items": [
                {
                    "item_id": item["excerpt_id"],
                    "item_type": "excerpt",
                    "doc_id": item["doc_id"],
                    "doc_type": item["doc_type"],
                    "source_hash": item["source_hash"],
                    "excerpt_id": item["excerpt_id"],
                    "excerpt_fingerprint": item["excerpt_fingerprint"],
                    "excerpt_text_hash": item["excerpt_text_hash"],
                    "span": copy.deepcopy(item["span"]),
                    "rank": item["rank"],
                    "source_strategy": item["source_strategy"],
                    "retrieval_backend": item["retrieval_backend"],
                    "retrieval_mode": item["retrieval_mode"],
                    "query_fingerprint": query_fingerprint,
                    "result_fingerprint": result_fingerprint,
                }
                for item in excerpt_citations
            ],
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
            run = self._fts.retrieve(shortlist_query, candidate_doc_ids=())
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

        effective_scan_limit = scan_limit if scan_limit is not None else self._fts_candidate_scan_limit(limit, date_range=date_range)
        doc_ids: list[str] = []
        seen: set[str] = set()
        batch_limit = max(25, min(limit, effective_scan_limit))
        while True:
            run = self._fts.retrieve(
                self._build_fts_shortlist_query(query, max_results=batch_limit),
                candidate_doc_ids=(),
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

    @staticmethod
    def _fts_candidate_scan_limit(limit: int, *, date_range: tuple[str, str] | None) -> int:
        if date_range is None:
            return limit
        return max(limit, limit * 4, 100)

    @staticmethod
    def _hit_sort_key(hit: RetrievalHit) -> tuple[float, str, str, int, int, str]:
        char_range = hit.span.get("char_range", {}) if isinstance(hit.span, dict) else {}
        if not isinstance(char_range, dict):
            char_range = {}
        return (
            -hit.score,
            hit.source_strategy,
            hit.doc_id,
            int(char_range.get("start", -1)),
            int(char_range.get("end", -1)),
            hit.excerpt_id or "",
        )

    def _candidate_docs_from_scope(self, scope: str, *, fallback: tuple[str, ...]) -> tuple[str, ...]:
        if scope.startswith("doc:"):
            return (scope.split(":", 1)[1],)
        if scope.startswith("collection:"):
            return fallback
        return fallback

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
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            try:
                return date.fromisoformat(value)
            except ValueError:
                return None

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

    def _find_fts_excerpt(self, excerpt_id: str) -> dict[str, object] | None:
        row = self._fetch_fts_row(excerpt_id)
        if row is not None:
            text = str(row["text"])
            text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            doc_id = str(row["doc_id"])
            return self._normalize_excerpt_payload(
                {
                    "excerpt_id": excerpt_id,
                    "doc_id": doc_id,
                    "doc_type": str(row["doc_type"]),
                    "source_hash": self._doc_source_hash(doc_id),
                    "source_strategy": "fts",
                    "span": {"char_range": {"start": int(row["char_start"]), "end": int(row["char_end"])}},
                    "text": text,
                    "text_hash": text_hash,
                    "provenance": self._build_fts_provenance(
                        doc_id=doc_id,
                        excerpt_id=excerpt_id,
                        char_start=int(row["char_start"]),
                        char_end=int(row["char_end"]),
                        text=text,
                    ),
                },
                source_strategy="fts",
                lookup_resolution="fts",
            )
        return None

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
        query_scope: str | None = None,
        query_intent: str | None = None,
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
        return provenance

    def _normalize_excerpt_payload(
        self,
        excerpt: dict[str, object],
        *,
        source_strategy: Literal["fts", "pageindex"],
        lookup_resolution: str,
    ) -> dict[str, object]:
        provenance = excerpt.get("provenance", {})
        if not isinstance(provenance, dict):
            provenance = {}
        normalized = dict(excerpt)
        normalized["source_strategy"] = source_strategy
        normalized["retrieval_source_strategy"] = source_strategy
        normalized["lookup_resolution"] = lookup_resolution
        text_hash = provenance.get("hash") or provenance.get("excerpt_text_hash") or normalized.get("text_hash")
        if not isinstance(text_hash, str) or not text_hash:
            text_value = normalized.get("text")
            if isinstance(text_value, str) and text_value:
                text_hash = hashlib.sha256(text_value.encode("utf-8")).hexdigest()
        normalized["text_hash"] = text_hash
        doc_id_value = normalized.get("doc_id")
        if (not isinstance(doc_id_value, str) or not doc_id_value) and isinstance(provenance.get("doc_id"), str):
            doc_id_value = str(provenance["doc_id"])
            normalized["doc_id"] = doc_id_value
        elif isinstance(doc_id_value, str) and doc_id_value:
            doc_id_value = str(doc_id_value)
        else:
            doc_id_value = None

        doc_meta = self._load_doc_meta().get(doc_id_value, {}) if doc_id_value is not None else {}

        source_hash = normalized.get("source_hash")
        if not isinstance(source_hash, str) or not source_hash:
            provenance_source_hash = provenance.get("source_hash")
            if isinstance(provenance_source_hash, str) and provenance_source_hash:
                source_hash = provenance_source_hash
            elif doc_id_value is not None:
                source_hash = self._doc_source_hash(doc_id_value, doc_meta=doc_meta)
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
            normalized["doc_type"] = doc_type
        else:
            doc_type = None

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
        if canonical_span is None and isinstance(normalized.get("span"), dict):
            canonical_span = dict(normalized["span"])
        if canonical_span is None and isinstance(provenance.get("span"), dict):
            canonical_span = RetrievalService._canonicalize_span(provenance["span"])
            if canonical_span is None:
                canonical_span = dict(provenance["span"])
        if canonical_span is not None:
            normalized["span"] = canonical_span
        retrieval_policy = self._retrieval_policy.as_snapshot()
        retrieval_backend = cast(str, retrieval_policy["retrieval_backend"])
        retrieval_mode = cast(str, retrieval_policy["retrieval_mode"])
        normalized["retrieval_backend"] = retrieval_backend
        normalized["retrieval_mode"] = retrieval_mode
        normalized["retrieval_policy"] = copy.deepcopy(retrieval_policy)
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
        if "provenance" in normalized:
            normalized_provenance = {
                **provenance,
                "source_strategy": source_strategy,
            }
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
            if isinstance(doc_identity_fingerprint, str) and doc_identity_fingerprint:
                normalized_provenance["doc_identity_fingerprint"] = doc_identity_fingerprint
            normalized_provenance["retrieval_backend"] = retrieval_backend
            normalized_provenance["retrieval_mode"] = retrieval_mode
            normalized_provenance["retrieval_policy"] = copy.deepcopy(retrieval_policy)
            normalized_provenance["retrieval_source_strategy"] = source_strategy
            normalized_provenance["lookup_resolution"] = lookup_resolution
            normalized["provenance"] = normalized_provenance
        return normalized

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
    def _canonicalize_span(span: object) -> dict[str, object] | None:
        if not isinstance(span, dict):
            return None
        char_range = span.get("char_range")
        if not isinstance(char_range, dict):
            return None
        if "start" not in char_range or "end" not in char_range:
            return None
        return {
            "char_range": {
                "start": int(char_range["start"]),
                "end": int(char_range["end"]),
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
        blob = self._root / _DOC_BLOBS / f"{doc_id}.enc"
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
        if query.scope.startswith("section:"):
            raise ValueError("section scope is unsupported until FTS fallback can resolve section targets")
        if query.scope not in {"vault"} and not any(query.scope.startswith(prefix) for prefix in ("collection:", "doc:")):
            raise ValueError("unsupported scope")
        if query.intent not in _SUPPORTED_RETRIEVAL_INTENTS:
            raise ValueError(f"unsupported intent: {query.intent}")
        if query.confidentiality_profile not in _SUPPORTED_CONFIDENTIALITY_PROFILES:
            raise ValueError(f"unsupported confidentiality_profile: {query.confidentiality_profile}")
        if query.confidentiality_profile == "confidential":
            # No network strategies are enabled in this retrieval implementation.
            pass

    @staticmethod
    def _safe_title_hint(query: RetrievalQuery, value: str) -> str | None:
        if not value:
            return None
        if query.confidentiality_profile == "confidential":
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
        rows = self._query_fts_db(
            "SELECT doc_id, excerpt_id, doc_type, title_hint, char_start, char_end, text FROM fts_entries "
            "WHERE excerpt_id = ? LIMIT 1",
            (excerpt_id,),
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
