from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from src.qual.audit import AuditLog
from src.qual.docindex.service import DocIndexBuildOptions, DocIndexService
from src.qual.engine.retrieval.embeddings_strategy import EmbeddingsStrategy
from src.qual.engine.retrieval.fts_strategy import FTSStrategy
from src.qual.engine.retrieval.interface import StrategyRun
from src.qual.engine.retrieval.pageindex_strategy import PageIndexStrategy
from src.qual.metrics.crypto import decrypt_bytes, encrypt_bytes

_RETRIEVAL_DIR = ".retrieval"
_KEY_FILE = "retrieval_v1.key"
_DOC_META_FILE = "doc_meta_v1.enc.json"
_FTS_FILE = "fts_entries_v1.enc.json"
_DOC_BLOBS = "doc_blobs"


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
    span: dict[str, object]
    title_hint: str | None
    score: float
    source_strategy: Literal["fts", "pageindex", "embeddings"]
    rationale: str | None
    node_path: list[dict[str, str]] | None


@dataclass(frozen=True)
class RetrievalResult:
    query: RetrievalQuery
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
        self._embeddings = EmbeddingsStrategy()

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
        fts_shortlist = self._candidate_docs_from_fts(query) if not self._is_doc_scoped(query.scope) else ()
        candidate_doc_ids = self._candidate_docs_from_scope(query.scope, fallback=fts_shortlist)

        strategy_runs: list[StrategyRun] = []
        fts_run = self._fts.retrieve(query, candidate_doc_ids=candidate_doc_ids)
        strategy_runs.append(fts_run)

        pageindex_run = self._pageindex.retrieve(query, candidate_doc_ids=candidate_doc_ids)
        if pageindex_run.hits:
            strategy_runs.append(pageindex_run)

        if self._embeddings.supports(query):
            strategy_runs.append(self._embeddings.retrieve(query, candidate_doc_ids=candidate_doc_ids))

        merged_hits = self._merge_hits(strategy_runs, max_results=query.constraints.max_results)
        elapsed_ms_total = max(0, int((self._now_fn() - started).total_seconds() * 1000))
        diagnostics = {
            "strategies_used": [run.strategy_id for run in strategy_runs],
            "elapsed_ms_by_strategy": {run.strategy_id: run.elapsed_ms for run in strategy_runs},
            "caches_used": {run.strategy_id: run.cache_used for run in strategy_runs},
            "elapsed_ms_total": elapsed_ms_total,
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
        return RetrievalResult(query=query, hits=merged_hits, diagnostics=diagnostics, audit_ref=audit.event_id)

    def _run_fts_hits(self, query: RetrievalQuery, candidate_doc_ids: tuple[str, ...]) -> list[RetrievalHit]:
        all_entries = self._load_fts_entries()
        scope_doc = self._doc_scope_id(query.scope)
        filtered = []
        for entry in all_entries:
            if scope_doc is not None and entry["doc_id"] != scope_doc:
                continue
            if candidate_doc_ids and entry["doc_id"] not in set(candidate_doc_ids):
                continue
            if query.constraints.doc_types and entry["doc_type"] not in set(query.constraints.doc_types):
                continue
            filtered.append(entry)
        tokens = [x for x in query.query_text.lower().split() if x]
        ranked: list[tuple[float, dict[str, object]]] = []
        for entry in filtered:
            score = 0.0
            text_lower = str(entry["text_lower"])
            for token in tokens:
                if token in text_lower:
                    score += 1.0
            if query.constraints.prefer_exact_matches and query.query_text.lower() in text_lower:
                score += 2.0
            if score > 0:
                ranked.append((score, entry))
        ranked.sort(key=lambda item: item[0], reverse=True)
        hits: list[RetrievalHit] = []
        for score, entry in ranked[: max(25, query.constraints.max_results)]:
            hits.append(
                RetrievalHit(
                    doc_id=str(entry["doc_id"]),
                    excerpt_id=str(entry["excerpt_id"]),
                    span={"char_range": {"start": int(entry["char_start"]), "end": int(entry["char_end"])}},
                    title_hint=self._safe_title_hint(query, str(entry.get("title_hint") or "")),
                    score=min(1.0, round(score / max(1.0, len(tokens)), 3)),
                    source_strategy="fts",
                    rationale="token_overlap",
                    node_path=None,
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
                            span=dict(hit.get("span", {})),
                            title_hint=hit.get("title_hint"),
                            score=float(hit.get("score", 0.0)),
                            source_strategy=hit.get("source_strategy", "fts"),  # type: ignore[arg-type]
                            rationale=hit.get("rationale"),
                            node_path=hit.get("node_path"),
                        )
                    )
        with_excerpt = [hit for hit in combined if hit.excerpt_id is not None]
        without_excerpt = [hit for hit in combined if hit.excerpt_id is None]
        ordered = sorted(with_excerpt, key=lambda h: h.score, reverse=True) + sorted(
            without_excerpt, key=lambda h: h.score, reverse=True
        )
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

    def _candidate_docs_from_scope(self, scope: str, *, fallback: tuple[str, ...]) -> tuple[str, ...]:
        if scope.startswith("doc:"):
            return (scope.split(":", 1)[1],)
        if scope.startswith("section:"):
            # section->doc resolution is deferred; use shortlist fallback now.
            return fallback
        if scope.startswith("collection:"):
            return fallback
        return fallback

    @staticmethod
    def _is_doc_scoped(scope: str) -> bool:
        return scope.startswith("doc:") or scope.startswith("section:")

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
        for start in range(0, len(text), 400):
            segment = text[start : start + 400]
            if not segment:
                continue
            entries.append(
                {
                    "doc_id": doc_id,
                    "doc_type": doc_type,
                    "title_hint": title_hint,
                    "excerpt_id": str(uuid.uuid4()),
                    "char_start": start,
                    "char_end": start + len(segment),
                    "text_lower": segment.lower(),
                }
            )
        self._write_encrypted_json(self._root / _FTS_FILE, entries)

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
        if query.scope not in {"vault"} and not any(
            query.scope.startswith(prefix) for prefix in ("collection:", "doc:", "section:")
        ):
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
