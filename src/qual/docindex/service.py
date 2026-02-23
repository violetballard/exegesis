from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Literal, Protocol
from urllib.parse import urlparse

from src.qual.audit import AuditLog
from src.qual.metrics.crypto import decrypt_bytes, encrypt_bytes

_DOCINDEX_DIR = ".docindex"
_KEY_FILE = "docindex_v1.key"
_RECORDS_FILE = "records_v1.enc.json"
_EXCERPTS_FILE = "excerpts_v1.enc.json"
_QUERY_CACHE_FILE = "query_cache_v1.enc.json"
_PAYLOAD_DIR = "payloads"
_EXCERPT_BLOB_DIR = "excerpt_blobs"
_QUERY_CACHE_TTL = timedelta(hours=1)
_DEFAULT_PROMPT_HASH = "pageindex_prompt_v1"
_DEFAULT_MODEL_ID = "magistral-small"


@dataclass(frozen=True)
class DocIndexBuildOptions:
    mode: str = "offline_only"
    max_depth: int = 6
    target_granularity: str = "subsection"
    include_node_summaries: bool = True
    pdf_text_extraction: str = "local"
    llm_provider: str = "openai_compat"
    confidentiality_profile: str = "confidential"
    llm_endpoint: str = "http://127.0.0.1:11434/v1"


@dataclass(frozen=True)
class DocIndexQueryConstraints:
    max_results: int = 5
    prefer_recent_nodes: bool = False
    require_page_ranges: bool = False
    section_hint: str | None = None


@dataclass(frozen=True)
class JobRef:
    job_id: str
    doc_id: str
    status: str


@dataclass(frozen=True)
class PageIndexResult:
    doc_id: str
    query: str
    hits: list[dict[str, object]]
    trace: dict[str, object]
    model_used: dict[str, object]
    elapsed_ms: int


@dataclass(frozen=True)
class DocumentIndexRecord:
    doc_id: str
    index_type: str
    version: str
    created_at: str
    updated_at: str
    source_hash: str
    index_hash: str
    status: Literal["ready", "building", "failed", "stale"]
    error_summary: str | None


@dataclass(frozen=True)
class ExcerptRecord:
    excerpt_id: str
    doc_id: str
    span: dict[str, int]
    hash: str
    storage_ref: str


class PageIndexNavigator(Protocol):
    def model_id(self) -> str:
        ...

    def prompt_template_hash(self) -> str:
        ...

    def build_tree(
        self,
        *,
        doc_id: str,
        text: str,
        max_depth: int,
        target_granularity: str,
        include_node_summaries: bool,
    ) -> tuple[list[dict[str, object]], dict[str, str]]:
        ...

    def query_tree(
        self,
        *,
        tree: list[dict[str, object]],
        node_summaries: dict[str, str],
        query: str,
        constraints: DocIndexQueryConstraints,
    ) -> tuple[list[dict[str, object]], dict[str, object]]:
        ...


class LocalPageIndexNavigator:
    def __init__(self, *, model: str = _DEFAULT_MODEL_ID, prompt_hash: str = _DEFAULT_PROMPT_HASH) -> None:
        self._model = model
        self._prompt_hash = prompt_hash
        self.query_calls = 0

    def model_id(self) -> str:
        return self._model

    def prompt_template_hash(self) -> str:
        return self._prompt_hash

    def build_tree(
        self,
        *,
        doc_id: str,
        text: str,
        max_depth: int,
        target_granularity: str,
        include_node_summaries: bool,
    ) -> tuple[list[dict[str, object]], dict[str, str]]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        chunks: list[str] = []
        chunk_size = 1200 if target_granularity == "subsection" else 2200
        if not lines:
            chunks = ["<empty-document>"]
        else:
            buf = ""
            for line in lines:
                if len(buf) + len(line) + 1 > chunk_size and buf:
                    chunks.append(buf)
                    buf = line
                else:
                    buf = f"{buf}\n{line}" if buf else line
            if buf:
                chunks.append(buf)
        tree: list[dict[str, object]] = []
        summaries: dict[str, str] = {}
        cursor = 0
        for idx, chunk in enumerate(chunks, start=1):
            node_id = f"{doc_id}:n{idx}"
            node = {
                "node_id": node_id,
                "title": f"Section {idx}",
                "depth": min(max_depth, 2),
                "page_start": idx,
                "page_end": idx,
                "char_start": cursor,
                "char_end": cursor + len(chunk),
                "children": [],
            }
            tree.append(node)
            cursor += len(chunk) + 1
            if include_node_summaries:
                summaries[node_id] = chunk[:160]
        return tree, summaries

    def query_tree(
        self,
        *,
        tree: list[dict[str, object]],
        node_summaries: dict[str, str],
        query: str,
        constraints: DocIndexQueryConstraints,
    ) -> tuple[list[dict[str, object]], dict[str, object]]:
        self.query_calls += 1
        lowered = query.lower()
        ranked: list[tuple[int, dict[str, object]]] = []
        visited: list[str] = []
        for node in tree:
            node_id = str(node["node_id"])
            visited.append(node_id)
            title = str(node["title"]).lower()
            summary = node_summaries.get(node_id, "").lower()
            score = 0
            for token in lowered.split():
                if token in title:
                    score += 2
                if token in summary:
                    score += 1
            if constraints.section_hint and constraints.section_hint.lower() in title:
                score += 2
            ranked.append((score, node))
        ranked.sort(key=lambda item: item[0], reverse=True)
        best = [node for score, node in ranked if score > 0][: constraints.max_results]
        if not best:
            best = [node for _, node in ranked[: constraints.max_results]]
        trace = {"visited_node_ids": visited[:50], "decision_log": f"ranked:{len(ranked)}"}
        return best, trace


class DocIndexService:
    def __init__(
        self,
        vault_root: Path,
        *,
        audit_log: AuditLog,
        navigator: PageIndexNavigator | None = None,
        now_fn=None,
    ) -> None:
        self._root = vault_root / _DOCINDEX_DIR
        self._root.mkdir(parents=True, exist_ok=True)
        (self._root / _PAYLOAD_DIR).mkdir(exist_ok=True)
        (self._root / _EXCERPT_BLOB_DIR).mkdir(exist_ok=True)
        self._audit = audit_log
        self._navigator = navigator if navigator is not None else LocalPageIndexNavigator()
        self._now_fn = now_fn or (lambda: datetime.now(UTC))
        self._key = self._load_or_create_key()
        self._cleanup_query_cache()

    def build(self, doc_id: str, source_bytes: bytes, options: DocIndexBuildOptions) -> JobRef:
        job_id = str(uuid.uuid4())
        self._validate_build_options(options)
        source_hash = hashlib.sha256(source_bytes).hexdigest()
        started = self._now_fn()
        self._audit.record(
            name="docindex_build_started",
            metadata={"doc_id": doc_id, "job_id": job_id, "source_hash": source_hash},
        )
        records = self._load_records()
        existing = self._find_record(records, doc_id)
        now_iso = started.isoformat()
        building_record = DocumentIndexRecord(
            doc_id=doc_id,
            index_type="pageindex",
            version="pageindex_v1",
            created_at=existing.created_at if existing is not None else now_iso,
            updated_at=now_iso,
            source_hash=source_hash,
            index_hash="",
            status="building",
            error_summary=None,
        )
        self._upsert_record(records, building_record)
        self._save_records(records)

        try:
            text = source_bytes.decode("utf-8", errors="ignore")
            excerpt_records = self._build_excerpts(doc_id=doc_id, text=text)
            tree, node_summaries = self._navigator.build_tree(
                doc_id=doc_id,
                text=text,
                max_depth=options.max_depth,
                target_granularity=options.target_granularity,
                include_node_summaries=options.include_node_summaries,
            )
            payload = {
                "tree": tree,
                "node_summaries": node_summaries,
                "page_text_map": {
                    node["node_id"]: [x.excerpt_id for x in excerpt_records if x.span["char_start"] <= int(node["char_end"])]
                    for node in tree
                },
                "build_metadata": {
                    "model_id": self._navigator.model_id(),
                    "ctx": 8192,
                    "prompt_template_hash": self._navigator.prompt_template_hash(),
                    "runtime_id": "local-offline",
                    "build_time_seconds": max(0, int((self._now_fn() - started).total_seconds())),
                    "llm_endpoint": options.llm_endpoint,
                },
            }
            index_hash = hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
            ).hexdigest()
            self._write_payload(doc_id, payload)
            self._upsert_excerpts(excerpt_records)
            ready = DocumentIndexRecord(
                doc_id=doc_id,
                index_type="pageindex",
                version="pageindex_v1",
                created_at=building_record.created_at,
                updated_at=self._now_fn().isoformat(),
                source_hash=source_hash,
                index_hash=index_hash,
                status="ready",
                error_summary=None,
            )
            self._upsert_record(records, ready)
            self._save_records(records)
            self._audit.record(
                name="docindex_build_completed",
                metadata={"doc_id": doc_id, "job_id": job_id, "index_hash": index_hash},
            )
            return JobRef(job_id=job_id, doc_id=doc_id, status="ready")
        except Exception:
            failed = DocumentIndexRecord(
                doc_id=doc_id,
                index_type="pageindex",
                version="pageindex_v1",
                created_at=building_record.created_at,
                updated_at=self._now_fn().isoformat(),
                source_hash=source_hash,
                index_hash="",
                status="failed",
                error_summary="docindex build failed",
            )
            self._upsert_record(records, failed)
            self._save_records(records)
            self._audit.record(
                name="docindex_build_failed",
                metadata={"doc_id": doc_id, "job_id": job_id, "error_summary": "docindex build failed"},
            )
            raise

    def query(
        self,
        doc_id: str,
        source_bytes: bytes,
        query: str,
        constraints: DocIndexQueryConstraints,
        *,
        options: DocIndexBuildOptions,
    ) -> PageIndexResult:
        self._validate_build_options(options)
        source_hash = hashlib.sha256(source_bytes).hexdigest()
        records = self._load_records()
        record = self._find_record(records, doc_id)
        if record is None or record.status != "ready":
            raise ValueError("pageindex is not ready for this document")
        if record.source_hash != source_hash:
            stale = DocumentIndexRecord(
                doc_id=record.doc_id,
                index_type=record.index_type,
                version=record.version,
                created_at=record.created_at,
                updated_at=self._now_fn().isoformat(),
                source_hash=record.source_hash,
                index_hash=record.index_hash,
                status="stale",
                error_summary="source_hash changed",
            )
            self._upsert_record(records, stale)
            self._save_records(records)
            raise ValueError("pageindex is stale: source_hash mismatch")

        query_hash = hashlib.sha256(query.encode("utf-8")).hexdigest()
        constraints_hash = hashlib.sha256(
            json.dumps(asdict(constraints), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest()
        cache_key = hashlib.sha256(f"{doc_id}|{query_hash}|{constraints_hash}|{record.index_hash}".encode("utf-8")).hexdigest()
        cached = self._get_cached_query(cache_key)
        if cached is not None:
            self._audit.record(
                name="docindex_query_executed",
                metadata={"doc_id": doc_id, "query_hash": query_hash, "cached": True},
            )
            return cached

        started = self._now_fn()
        payload = self._read_payload(doc_id)
        tree = payload["tree"]
        node_summaries = payload.get("node_summaries", {})
        hits_nodes, trace = self._navigator.query_tree(
            tree=tree,
            node_summaries=node_summaries,
            query=query,
            constraints=constraints,
        )
        hits = [self._node_to_hit(doc_id=doc_id, node=node, constraints=constraints, payload=payload) for node in hits_nodes]
        result = PageIndexResult(
            doc_id=doc_id,
            query=query,
            hits=hits,
            trace=trace,
            model_used={
                "model_id": payload["build_metadata"]["model_id"],
                "ctx": payload["build_metadata"]["ctx"],
                "prompt_template_hash": payload["build_metadata"]["prompt_template_hash"],
            },
            elapsed_ms=max(0, int((self._now_fn() - started).total_seconds() * 1000)),
        )
        self._set_cached_query(cache_key, result)
        self._audit.record(
            name="docindex_query_executed",
            metadata={"doc_id": doc_id, "query_hash": query_hash, "cached": False},
        )
        return result

    def fetch_excerpt(self, excerpt_id: str) -> dict[str, object]:
        excerpt = self._find_excerpt(excerpt_id)
        if excerpt is None:
            raise KeyError(f"unknown excerpt_id: {excerpt_id}")
        text = self._read_excerpt_text(excerpt)
        return {
            "excerpt_id": excerpt.excerpt_id,
            "text": text,
            "provenance": {"doc_id": excerpt.doc_id, "span": excerpt.span, "hash": excerpt.hash},
        }

    def pin_to_context_set(self, context_set_id: str, excerpt_id: str) -> dict[str, object]:
        excerpt = self._find_excerpt(excerpt_id)
        if excerpt is None:
            raise KeyError(f"unknown excerpt_id: {excerpt_id}")
        return {"context_set_id": context_set_id, "excerpt_id": excerpt_id, "status": "pinned"}

    def get_record_status(self, doc_id: str) -> str | None:
        record = self._find_record(self._load_records(), doc_id)
        if record is None:
            return None
        return record.status

    def _node_to_hit(
        self,
        *,
        doc_id: str,
        node: dict[str, object],
        constraints: DocIndexQueryConstraints,
        payload: dict[str, object],
    ) -> dict[str, object]:
        node_id = str(node["node_id"])
        excerpt_ids = payload.get("page_text_map", {}).get(node_id, [])
        page_or_span: dict[str, int]
        if constraints.require_page_ranges:
            page_or_span = {"start": int(node.get("page_start", 1)), "end": int(node.get("page_end", 1))}
            range_key = "page_range"
        else:
            page_or_span = {"char_start": int(node.get("char_start", 0)), "char_end": int(node.get("char_end", 0))}
            range_key = "span_range"
        return {
            "node_path": [{"node_id": node_id, "title": str(node.get("title", ""))}],
            range_key: page_or_span,
            "excerpt_ids": list(excerpt_ids),
            "score": 1.0,
            "rationale": "node_match",
            "doc_id": doc_id,
        }

    def _build_excerpts(self, *, doc_id: str, text: str) -> list[ExcerptRecord]:
        records: list[ExcerptRecord] = []
        chunk_size = 450
        cursor = 0
        for start in range(0, len(text), chunk_size):
            segment = text[start : start + chunk_size]
            if not segment:
                continue
            excerpt_id = str(uuid.uuid4())
            hash_value = hashlib.sha256(segment.encode("utf-8")).hexdigest()
            storage_ref = f"{excerpt_id}.enc"
            blob_path = self._root / _EXCERPT_BLOB_DIR / storage_ref
            blob_path.write_bytes(encrypt_bytes(segment.encode("utf-8"), self._key))
            records.append(
                ExcerptRecord(
                    excerpt_id=excerpt_id,
                    doc_id=doc_id,
                    span={"char_start": start, "char_end": start + len(segment)},
                    hash=hash_value,
                    storage_ref=storage_ref,
                )
            )
            cursor += len(segment)
        if not records:
            excerpt_id = str(uuid.uuid4())
            storage_ref = f"{excerpt_id}.enc"
            blob_path = self._root / _EXCERPT_BLOB_DIR / storage_ref
            blob_path.write_bytes(encrypt_bytes(b"", self._key))
            records.append(
                ExcerptRecord(
                    excerpt_id=excerpt_id,
                    doc_id=doc_id,
                    span={"char_start": 0, "char_end": 0},
                    hash=hashlib.sha256(b"").hexdigest(),
                    storage_ref=storage_ref,
                )
            )
        return records

    def _upsert_excerpts(self, excerpts: list[ExcerptRecord]) -> None:
        current = [x for x in self._load_excerpts() if x.doc_id != excerpts[0].doc_id]
        current.extend(excerpts)
        payload = [asdict(x) for x in current]
        self._write_encrypted_json(self._root / _EXCERPTS_FILE, payload)

    def _find_excerpt(self, excerpt_id: str) -> ExcerptRecord | None:
        for item in self._load_excerpts():
            if item.excerpt_id == excerpt_id:
                return item
        return None

    def _load_excerpts(self) -> list[ExcerptRecord]:
        payload = self._read_encrypted_json(self._root / _EXCERPTS_FILE, default=[])
        out: list[ExcerptRecord] = []
        if not isinstance(payload, list):
            return out
        for raw in payload:
            if not isinstance(raw, dict):
                continue
            out.append(
                ExcerptRecord(
                    excerpt_id=str(raw["excerpt_id"]),
                    doc_id=str(raw["doc_id"]),
                    span={"char_start": int(raw["span"]["char_start"]), "char_end": int(raw["span"]["char_end"])},
                    hash=str(raw["hash"]),
                    storage_ref=str(raw["storage_ref"]),
                )
            )
        return out

    def _read_excerpt_text(self, excerpt: ExcerptRecord) -> str:
        path = self._root / _EXCERPT_BLOB_DIR / excerpt.storage_ref
        plaintext = decrypt_bytes(path.read_bytes(), self._key)
        text = plaintext.decode("utf-8")
        if hashlib.sha256(plaintext).hexdigest() != excerpt.hash:
            raise ValueError("excerpt integrity mismatch")
        return text

    def _cleanup_query_cache(self) -> None:
        now = self._now_fn()
        raw = self._read_encrypted_json(self._root / _QUERY_CACHE_FILE, default=[])
        if not isinstance(raw, list):
            self._write_encrypted_json(self._root / _QUERY_CACHE_FILE, [])
            return
        keep: list[dict[str, object]] = []
        for entry in raw:
            if not isinstance(entry, dict):
                continue
            expires = datetime.fromisoformat(str(entry["expires_at"]))
            if expires > now:
                keep.append(entry)
        self._write_encrypted_json(self._root / _QUERY_CACHE_FILE, keep)

    def _get_cached_query(self, cache_key: str) -> PageIndexResult | None:
        entries = self._read_encrypted_json(self._root / _QUERY_CACHE_FILE, default=[])
        if not isinstance(entries, list):
            return None
        now = self._now_fn()
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            if str(entry.get("cache_key")) != cache_key:
                continue
            if datetime.fromisoformat(str(entry["expires_at"])) <= now:
                continue
            payload = entry.get("result")
            if not isinstance(payload, dict):
                continue
            return PageIndexResult(
                doc_id=str(payload["doc_id"]),
                query=str(payload["query"]),
                hits=list(payload["hits"]),
                trace=dict(payload["trace"]),
                model_used=dict(payload["model_used"]),
                elapsed_ms=int(payload["elapsed_ms"]),
            )
        return None

    def _set_cached_query(self, cache_key: str, result: PageIndexResult) -> None:
        entries = self._read_encrypted_json(self._root / _QUERY_CACHE_FILE, default=[])
        if not isinstance(entries, list):
            entries = []
        filtered = [x for x in entries if isinstance(x, dict) and str(x.get("cache_key")) != cache_key]
        filtered.append(
            {
                "cache_key": cache_key,
                "expires_at": (self._now_fn() + _QUERY_CACHE_TTL).isoformat(),
                "result": asdict(result),
            }
        )
        self._write_encrypted_json(self._root / _QUERY_CACHE_FILE, filtered)

    def _validate_build_options(self, options: DocIndexBuildOptions) -> None:
        if options.confidentiality_profile not in {"confidential", "standard"}:
            raise ValueError("confidentiality_profile must be confidential or standard")
        if options.confidentiality_profile == "confidential":
            if options.mode != "offline_only":
                raise PermissionError("confidential profile requires offline_only mode")
            if options.pdf_text_extraction != "local":
                raise PermissionError("confidential profile requires local text extraction")
            if options.llm_provider != "openai_compat":
                raise PermissionError("confidential profile requires openai_compat provider")
            if not _is_localhost_endpoint(options.llm_endpoint):
                raise PermissionError("confidential profile requires localhost llm endpoint")
        if options.max_depth < 1 or options.max_depth > 12:
            raise ValueError("max_depth must be within 1..12")
        if options.target_granularity not in {"section", "subsection"}:
            raise ValueError("target_granularity must be section or subsection")

    def _write_payload(self, doc_id: str, payload: dict[str, object]) -> None:
        path = self._root / _PAYLOAD_DIR / f"{doc_id}.enc"
        self._write_encrypted_json(path, payload)

    def _read_payload(self, doc_id: str) -> dict[str, object]:
        path = self._root / _PAYLOAD_DIR / f"{doc_id}.enc"
        payload = self._read_encrypted_json(path, default={})
        if not isinstance(payload, dict):
            raise ValueError("invalid payload")
        return payload

    def _load_records(self) -> list[DocumentIndexRecord]:
        payload = self._read_encrypted_json(self._root / _RECORDS_FILE, default=[])
        out: list[DocumentIndexRecord] = []
        if not isinstance(payload, list):
            return out
        for raw in payload:
            if not isinstance(raw, dict):
                continue
            out.append(
                DocumentIndexRecord(
                    doc_id=str(raw["doc_id"]),
                    index_type=str(raw["index_type"]),
                    version=str(raw["version"]),
                    created_at=str(raw["created_at"]),
                    updated_at=str(raw["updated_at"]),
                    source_hash=str(raw["source_hash"]),
                    index_hash=str(raw["index_hash"]),
                    status=str(raw["status"]),  # type: ignore[arg-type]
                    error_summary=raw.get("error_summary"),
                )
            )
        return out

    def _save_records(self, records: list[DocumentIndexRecord]) -> None:
        payload = [asdict(x) for x in records]
        self._write_encrypted_json(self._root / _RECORDS_FILE, payload)

    @staticmethod
    def _find_record(records: list[DocumentIndexRecord], doc_id: str) -> DocumentIndexRecord | None:
        for record in records:
            if record.doc_id == doc_id:
                return record
        return None

    @staticmethod
    def _upsert_record(records: list[DocumentIndexRecord], value: DocumentIndexRecord) -> None:
        for idx, record in enumerate(records):
            if record.doc_id == value.doc_id:
                records[idx] = value
                return
        records.append(value)

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
        encrypted = encrypt_bytes(plaintext, self._key)
        path.write_bytes(encrypted)

    def _load_or_create_key(self) -> bytes:
        path = self._root / _KEY_FILE
        if path.exists():
            raw = path.read_bytes()
            if len(raw) < 32:
                raise ValueError("docindex key file is invalid")
            return raw[:32]
        raw = (uuid.uuid4().bytes + uuid.uuid4().bytes)[:32]
        path.write_bytes(raw)
        return raw


def _is_localhost_endpoint(raw: str) -> bool:
    parsed = urlparse(raw)
    host = parsed.hostname
    if host not in {"127.0.0.1", "localhost"}:
        return False
    return parsed.scheme in {"http", "https"}
