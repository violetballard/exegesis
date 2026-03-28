from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from exegesis_engine.audit.event_log import AuditLog
from src.qual.docindex.service import DocIndexBuildOptions, DocIndexService
from src.qual.engine.retrieval.fts_strategy import FTSStrategy
from src.qual.engine.retrieval.interface import StrategyRun
from src.qual.engine.retrieval.pageindex_strategy import PageIndexStrategy
from exegesis_engine.metrics.crypto import decrypt_bytes, encrypt_bytes

_RETRIEVAL_DIR = ".retrieval"
_KEY_FILE = "retrieval_v1.key"
_DOC_META_FILE = "doc_meta_v1.enc.json"
_FTS_FILE = "fts_entries_v1.enc.json"
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
        self._pageindex = PageIndexStrategy(self._docindex, self._read_doc_text, now_fn=self._now_fn)

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
        blob_path.parent.mkdir(parents=True, exist_ok=True)
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
        fts_shortlist = self._candidate_docs_from_fts(query) if not self._is_doc_scoped(query.scope) else ()
        candidate_doc_ids = self._candidate_docs_from_scope(query.scope, fallback=fts_shortlist)

        runs: list[StrategyRun] = []
        fts_run = self._fts.retrieve(query, candidate_doc_ids=candidate_doc_ids)
        runs.append(fts_run)

        if self._should_try_pageindex(query):
            pageindex_run = self._pageindex.retrieve(query, candidate_doc_ids=candidate_doc_ids)
            if pageindex_run.hits:
                runs.append(pageindex_run)

        merged_hits = self._merge_hits(runs, max_results=query.constraints.max_results)
        doc_hits = self._build_doc_hits(merged_hits)
        elapsed_ms_total = max(0, int((self._now_fn() - started).total_seconds() * 1000))
        diagnostics = {
            "strategies_used": [run.strategy_id for run in runs],
            "elapsed_ms_by_strategy": {run.strategy_id: run.elapsed_ms for run in runs},
            "caches_used": {run.strategy_id: run.cache_used for run in runs},
            "elapsed_ms_total": elapsed_ms_total,
            "doc_hits_count": len(doc_hits),
            "excerpt_hits_count": len(merged_hits),
        }
        query_hash = hashlib.sha256(query.query_text.encode("utf-8")).hexdigest()
        audit = self._audit.record(
            name="retrieval_executed",
            metadata={
                "query_hash": query_hash,
                "strategies_used": diagnostics["strategies_used"],
                "elapsed_ms_by_strategy": diagnostics["elapsed_ms_by_strategy"],
                "doc_ids_count": len({hit.doc_id for hit in merged_hits}),
                "hits_count": len(merged_hits),
            },
        )
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
            return fts_excerpt
        return self._docindex.fetch_excerpt(excerpt_id)

    def _run_fts_hits(self, query: RetrievalQuery, candidate_doc_ids: tuple[str, ...]) -> list[RetrievalHit]:
        all_entries = self._load_fts_entries()
        scope_doc = self._doc_scope_id(query.scope)
        candidate_doc_id_set = set(candidate_doc_ids)
        allowed_doc_types = set(query.constraints.doc_types)
        filtered = []
        for entry in all_entries:
            if scope_doc is not None and entry["doc_id"] != scope_doc:
                continue
            if candidate_doc_id_set and entry["doc_id"] not in candidate_doc_id_set:
                continue
            if allowed_doc_types and entry["doc_type"] not in allowed_doc_types:
                continue
            filtered.append(entry)
        tokens = [x for x in query.query_text.lower().split() if x]
        ranked: list[tuple[float, dict[str, object]]] = []
        for entry in filtered:
            score = 0.0
            text_lower = str(entry["text_lower"])
            matched_terms: list[str] = []
            for token in tokens:
                if token in text_lower:
                    score += 1.0
                    matched_terms.append(token)
            if query.constraints.prefer_exact_matches and query.query_text.lower() in text_lower:
                score += 2.0
            if score > 0:
                ranked.append((score, {**entry, "matched_terms": tuple(matched_terms)}))
        ranked.sort(
            key=lambda item: (
                -item[0],
                str(item[1]["doc_id"]),
                int(item[1]["char_start"]),
                int(item[1]["char_end"]),
                str(item[1]["excerpt_id"]),
            )
        )
        hits: list[RetrievalHit] = []
        for rank, (score, entry) in enumerate(ranked[: max(25, query.constraints.max_results)], start=1):
            doc_id = str(entry["doc_id"])
            excerpt_text = self._read_fts_excerpt_text(entry)
            hits.append(
                RetrievalHit(
                    doc_id=doc_id,
                    excerpt_id=str(entry["excerpt_id"]),
                    excerpt_text=excerpt_text,
                    span={"char_range": {"start": int(entry["char_start"]), "end": int(entry["char_end"])}},
                    title_hint=self._safe_title_hint(query, str(entry.get("title_hint") or "")),
                    score=min(1.0, round(score / max(1.0, len(tokens)), 3)),
                    source_strategy="fts",
                    rationale="token_overlap",
                    node_path=None,
                    provenance=self._build_fts_provenance(doc_id=doc_id, entry=entry, text=excerpt_text, rank=rank),
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

    def _build_doc_hits(self, hits: list[RetrievalHit]) -> list[RetrievalDocHit]:
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
                        "top_excerpt_id": top_hit.excerpt_id,
                        "top_excerpt_rank": top_hit.provenance.get("rank"),
                        "doc_rank": doc_rank,
                        "excerpt_count": len(doc_hit_list),
                        "source_strategy": "fts",
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

    def _should_try_pageindex(self, query: RetrievalQuery) -> bool:
        if query.scope.startswith("doc:"):
            return True
        if query.intent == "outline_support":
            return True
        return bool(query.constraints.section_hint)

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
        entries = [x for x in self._load_fts_entries() if x["doc_id"] != doc_id]
        for start, end, segment in self._iter_fts_segments(text):
            if not segment:
                continue
            entries.append(
                {
                    "doc_id": doc_id,
                    "doc_type": doc_type,
                    "title_hint": title_hint,
                    "excerpt_id": self._make_fts_excerpt_id(doc_id=doc_id, char_start=start, char_end=end, text=segment),
                    "char_start": start,
                    "char_end": end,
                    "text_lower": segment.lower(),
                }
            )
        self._write_encrypted_json(self._root / _FTS_FILE, entries)

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
        for entry in self._load_fts_entries():
            if str(entry.get("excerpt_id")) != excerpt_id:
                continue
            doc_id = str(entry["doc_id"])
            text = self._read_fts_excerpt_text(entry)
            return {
                "excerpt_id": excerpt_id,
                "text": text,
                "provenance": self._build_fts_provenance(doc_id=doc_id, entry=entry, text=text),
            }
        return None

    def _read_fts_excerpt_text(self, entry: dict[str, object]) -> str:
        doc_id = str(entry["doc_id"])
        char_start = int(entry["char_start"])
        char_end = int(entry["char_end"])
        return self._read_doc_text(doc_id)[char_start:char_end]

    def _build_fts_provenance(
        self,
        *,
        doc_id: str,
        entry: dict[str, object],
        text: str,
        rank: int | None = None,
    ) -> dict[str, object]:
        meta = self._load_doc_meta().get(doc_id, {})
        matched_terms = entry.get("matched_terms", ())
        if not isinstance(matched_terms, tuple):
            matched_terms = tuple(str(term) for term in matched_terms if isinstance(term, str))
        return {
            "doc_id": doc_id,
            "source_hash": str(meta.get("source_hash", "")),
            "excerpt_id": str(entry["excerpt_id"]),
            "span": {"char_range": {"start": int(entry["char_start"]), "end": int(entry["char_end"])}},
            "hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "matched_terms": matched_terms,
            "match_count": len(matched_terms),
            "rank": rank,
            "source_strategy": "fts",
        }

    def _load_fts_entries(self) -> list[dict[str, object]]:
        payload = self._read_encrypted_json(self._root / _FTS_FILE, default=[])
        if not isinstance(payload, list):
            return []
        out: list[dict[str, object]] = []
        for raw in payload:
            if isinstance(raw, dict):
                out.append(raw)
        return out

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
            raise ValueError("section scope is unsupported until PageIndex resolves section targets")
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
