from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Iterator, Literal

from src.qual.audit import AuditLog
from src.qual.docindex.service import DocIndexBuildOptions, DocIndexService
from src.qual.engine.retrieval.fts_strategy import FTSStrategy
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


@dataclass(frozen=True)
class RetrievalConstraints:
    max_results: int = 10
    doc_types: tuple[str, ...] = ()
    date_range: tuple[str, str] | None = None
    require_citations: bool = False
    section_hint: str | None = None
    prefer_exact_matches: bool = False


@dataclass(frozen=True)
class RetrievalQuery:
    query_text: str
    scope: str
    intent: Literal["lookup", "compare", "summarize", "quote_find", "outline_support"]
    constraints: RetrievalConstraints = field(default_factory=RetrievalConstraints)
    confidentiality_profile: Literal["confidential", "standard"] = "confidential"


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


@dataclass(frozen=True)
class RetrievalResult:
    query: RetrievalQuery
    doc_hits: list[RetrievalDocHit]
    hits: list[RetrievalHit]
    diagnostics: dict[str, object]
    audit_ref: str


class RetrievalService:
    def __init__(self, vault_root: Path, *, audit_log: AuditLog, now_fn=None) -> None:
        self._root = vault_root / _RETRIEVAL_DIR
        self._root.mkdir(parents=True, exist_ok=True)
        (self._root / _DOC_BLOBS).mkdir(exist_ok=True)
        self._audit = audit_log
        self._now_fn = now_fn or (lambda: datetime.now(UTC))
        self._key = self._load_or_create_key()
        self._docindex = DocIndexService(vault_root, audit_log=audit_log, now_fn=self._now_fn)
        self._fts = FTSStrategy(self._run_fts_hits, now_fn=self._now_fn)
        self._active_query_fingerprint: str | None = None

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

    def build_pageindex(self, *, doc_id: str, options: DocIndexBuildOptions | None = None) -> str:
        source = self._read_doc_text(doc_id)
        build_opts = options if options is not None else DocIndexBuildOptions()
        job = self._docindex.build(doc_id, source.encode("utf-8"), build_opts)
        return job.status

    def retrieve_auto(self, query: RetrievalQuery) -> RetrievalResult:
        self._validate_query(query)
        started = self._now_fn()
        query_fingerprint = self._query_fingerprint(query)
        fts_shortlist = self._candidate_docs_from_fts(query) if not self._is_doc_scoped(query.scope) else ()
        candidate_doc_ids = self._candidate_docs_from_scope(query.scope, fallback=fts_shortlist)
        effective_candidate_doc_count = self._effective_candidate_doc_count(query.scope, candidate_doc_ids)

        self._active_query_fingerprint = query_fingerprint
        try:
            fts_run = self._fts.retrieve(query, candidate_doc_ids=candidate_doc_ids)
            merged_hits = self._merge_hits([fts_run], max_results=query.constraints.max_results)
            doc_hits = self._build_doc_hits(query, merged_hits, query_fingerprint=query_fingerprint)
            elapsed_ms_total = max(0, int((self._now_fn() - started).total_seconds() * 1000))
            diagnostics = {
                "retrieval_backend": "sqlite_fts",
                "retrieval_mode": "fts_first",
                "query_fingerprint": query_fingerprint,
                "query_scope": query.scope,
                "query_intent": query.intent,
                "doc_scope_id": self._doc_scope_id(query.scope),
                "candidate_doc_count": effective_candidate_doc_count,
                "fts_shortlist_count": len(fts_shortlist),
                "strategies_used": [fts_run.strategy_id],
                "elapsed_ms_by_strategy": {fts_run.strategy_id: fts_run.elapsed_ms},
                "caches_used": {fts_run.strategy_id: fts_run.cache_used},
                "elapsed_ms_total": elapsed_ms_total,
                "doc_hits_count": len(doc_hits),
                "excerpt_hits_count": len(merged_hits),
            }
            query_hash = hashlib.sha256(query.query_text.encode("utf-8")).hexdigest()
            audit = self._audit.record(
                name="retrieval_executed",
                metadata={
                    "query_hash": query_hash,
                    "query_fingerprint": query_fingerprint,
                    "retrieval_mode": diagnostics["retrieval_mode"],
                    "query_scope": query.scope,
                    "strategies_used": diagnostics["strategies_used"],
                    "elapsed_ms_by_strategy": diagnostics["elapsed_ms_by_strategy"],
                    "doc_ids_count": len({hit.doc_id for hit in merged_hits}),
                    "hits_count": len(merged_hits),
                },
            )
        finally:
            self._active_query_fingerprint = None
        return RetrievalResult(
            query=query,
            doc_hits=doc_hits,
            hits=merged_hits,
            diagnostics=diagnostics,
            audit_ref=audit.event_id,
        )

    def fetch_excerpt(self, excerpt_id: str) -> dict[str, object]:
        fts_excerpt = self._find_fts_excerpt(excerpt_id)
        if fts_excerpt is not None:
            return self._normalize_excerpt_payload(fts_excerpt, source_strategy="fts")
        excerpt = self._docindex.fetch_excerpt(excerpt_id)
        if isinstance(excerpt, dict):
            return self._normalize_excerpt_payload(excerpt, source_strategy="pageindex")
        return excerpt

    def _run_fts_hits(self, query: RetrievalQuery, candidate_doc_ids: tuple[str, ...]) -> list[RetrievalHit]:
        match_query, query_terms = self._build_fts_match_query(query.query_text)
        exact_phrase = query.query_text.casefold().strip()
        scope_doc = self._doc_scope_id(query.scope)
        allowed_doc_types = tuple(query.constraints.doc_types)
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
            where_clauses.append(f"doc_type IN ({placeholders})")
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
                    provenance=self._build_fts_provenance(
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
                        query_fingerprint=self._active_query_fingerprint,
                        candidate_doc_count=effective_candidate_doc_count,
                    ),
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
                    combined.append(
                        RetrievalHit(
                            doc_id=str(hit["doc_id"]),
                            excerpt_id=hit.get("excerpt_id"),
                            excerpt_text=hit.get("excerpt_text"),
                            span=dict(hit.get("span", {})),
                            title_hint=hit.get("title_hint"),
                            score=float(hit.get("score", 0.0)),
                            source_strategy=hit.get("source_strategy", "fts"),  # type: ignore[arg-type]
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
            doc_hits.append(
                RetrievalDocHit(
                    doc_id=doc_id,
                    title_hint=top_hit.title_hint,
                    source_hash=str(doc_meta.get("source_hash", "")),
                    top_excerpt_id=top_hit.excerpt_id,
                    top_score=top_hit.score,
                    source_strategy="fts",
                    excerpt_count=len(doc_hit_list),
                    provenance={
                        "doc_id": doc_id,
                        "source_hash": str(doc_meta.get("source_hash", "")),
                        "query_fingerprint": query_fingerprint,
                        "excerpt_ids": [hit.excerpt_id for hit in doc_hit_list if hit.excerpt_id is not None],
                        "top_excerpt_id": top_hit.excerpt_id,
                        "top_excerpt_hash": top_hit.provenance.get("hash"),
                        "top_excerpt_span": top_hit.provenance.get("span"),
                        "top_matched_terms": top_hit.provenance.get("matched_terms"),
                        "top_match_count": top_hit.provenance.get("match_count"),
                        "top_excerpt_rank": top_hit.provenance.get("rank"),
                        "top_fts_rank": top_hit.provenance.get("fts_rank"),
                        "doc_rank": doc_rank,
                        "excerpt_count": len(doc_hit_list),
                        "source_strategy": "fts",
                        "retrieval_mode": "fts_first",
                        "query_scope": query.scope,
                        "query_intent": query.intent,
                    },
                )
            )
        return doc_hits

    def _candidate_docs_from_fts(self, query: RetrievalQuery) -> tuple[str, ...]:
        run = self._fts.retrieve(
            RetrievalQuery(
                query_text=query.query_text,
                scope=query.scope,
                intent=query.intent,
                constraints=RetrievalConstraints(max_results=25, doc_types=query.constraints.doc_types),
                confidentiality_profile=query.confidentiality_profile,
            ),
            candidate_doc_ids=(),
        )
        doc_ids: list[str] = []
        seen = set()
        for hit in run.hits:
            if hit.doc_id in seen:
                continue
            seen.add(hit.doc_id)
            doc_ids.append(hit.doc_id)
            if len(doc_ids) >= 25:
                break
        return tuple(doc_ids)

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

    @staticmethod
    def _effective_candidate_doc_count(scope: str, candidate_doc_ids: tuple[str, ...]) -> int:
        if scope.startswith("doc:"):
            return 1
        return len(candidate_doc_ids)

    @staticmethod
    def _is_doc_scoped(scope: str) -> bool:
        return scope.startswith("doc:")

    @staticmethod
    def _doc_scope_id(scope: str) -> str | None:
        if scope.startswith("doc:"):
            return scope.split(":", 1)[1]
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
            return {
                "excerpt_id": excerpt_id,
                "doc_id": doc_id,
                "doc_type": str(row["doc_type"]),
                "source_hash": str(self._load_doc_meta().get(doc_id, {}).get("source_hash", "")),
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
            }
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
        query_fingerprint: str | None = None,
        candidate_doc_count: int | None = None,
    ) -> dict[str, object]:
        meta = self._load_doc_meta().get(doc_id, {})
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        provenance = {
            "doc_id": doc_id,
            "source_hash": str(meta.get("source_hash", "")),
            "excerpt_id": excerpt_id,
            "span": {"char_range": {"start": char_start, "end": char_end}},
            "hash": text_hash,
            "excerpt_text_hash": text_hash,
            "matched_terms": matched_terms,
            "match_count": len(matched_terms),
            "rank": rank,
            "fts_rank": fts_rank,
            "source_strategy": "fts",
        }
        if query_scope is not None:
            provenance["query_scope"] = query_scope
        if query_intent is not None:
            provenance["query_intent"] = query_intent
        if query_fingerprint is not None:
            provenance["query_fingerprint"] = query_fingerprint
        if candidate_doc_count is not None:
            provenance["candidate_doc_count"] = candidate_doc_count
        return provenance

    @staticmethod
    def _normalize_excerpt_payload(
        excerpt: dict[str, object],
        *,
        source_strategy: Literal["fts", "pageindex"],
    ) -> dict[str, object]:
        provenance = excerpt.get("provenance", {})
        if not isinstance(provenance, dict):
            provenance = {}
        normalized = dict(excerpt)
        normalized["source_strategy"] = source_strategy
        normalized["text_hash"] = provenance.get("hash")
        if "doc_id" not in normalized and isinstance(provenance.get("doc_id"), str):
            normalized["doc_id"] = provenance["doc_id"]
        if "span" not in normalized and isinstance(provenance.get("span"), dict):
            normalized["span"] = dict(provenance["span"])
        if "provenance" in normalized:
            normalized["provenance"] = {
                **provenance,
                "source_strategy": source_strategy,
            }
        return normalized

    @staticmethod
    def _query_fingerprint(query: RetrievalQuery) -> str:
        normalized_constraints = {
            "max_results": query.constraints.max_results,
            "doc_types": list(query.constraints.doc_types),
            "date_range": list(query.constraints.date_range) if query.constraints.date_range is not None else None,
            "require_citations": query.constraints.require_citations,
            "section_hint": query.constraints.section_hint,
            "prefer_exact_matches": query.constraints.prefer_exact_matches,
        }
        payload = {
            "query_text": query.query_text.casefold().strip(),
            "scope": query.scope,
            "intent": query.intent,
            "constraints": normalized_constraints,
            "confidentiality_profile": query.confidentiality_profile,
        }
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

    def _validate_query(self, query: RetrievalQuery) -> None:
        if not query.query_text.strip():
            raise ValueError("query_text is required")
        if query.scope.startswith("section:"):
            raise ValueError("section scope is unsupported until FTS fallback can resolve section targets")
        if query.scope not in {"vault"} and not any(query.scope.startswith(prefix) for prefix in ("collection:", "doc:")):
            raise ValueError("unsupported scope")
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
        terms: list[str] = []
        seen: set[str] = set()
        for term in re.findall(r"\w+", query_text.casefold()):
            if term in seen:
                continue
            seen.add(term)
            terms.append(term)
        if terms:
            return " OR ".join(f'"{term}"' for term in terms), tuple(terms)
        cleaned = query_text.strip().casefold().replace('"', '""')
        return f'"{cleaned}"', ()

    @staticmethod
    def _matched_query_terms(query_terms: tuple[str, ...], text: str) -> tuple[str, ...]:
        text_lower = text.casefold()
        return tuple(term for term in query_terms if term in text_lower)
