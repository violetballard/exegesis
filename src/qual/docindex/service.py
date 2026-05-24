from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone

UTC = timezone.utc
from pathlib import Path
from typing import Any, Literal

from src.qual.audit import AuditLog
from src.qual.engine.llm_client import ModelCapabilities, OpenAICompatClient, RuntimeCapabilities
from src.qual.engine.policy_gate import PolicyGate
from src.qual.engine.vault_store import VaultStore

_DOCINDEX_DIR = ".docindex"
_RECORDS_FILE = "records_v1.enc.json"
_EXCERPTS_FILE = "excerpts_v1.enc.json"
_QUERY_CACHE_FILE = "query_cache_v1.enc.json"
_PAYLOAD_DIR = "payloads"
_EXCERPT_BLOB_DIR = "excerpt_blobs"
_SOURCE_BLOB_DIR = "source_blobs"
_QUERY_CACHE_TTL = timedelta(hours=1)
_DEFAULT_PROMPT_HASH = "pageindex_prompt_v2"
_DEFAULT_MODEL_ID = "magistral-small"
_MIN_TEXT_THRESHOLD = 40
_MIN_PRINTABLE_RATIO = 0.82


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
    requires_ocr: bool
    vision_enabled_at_build: bool
    model_used: dict[str, object]


@dataclass(frozen=True)
class ExcerptRecord:
    excerpt_id: str
    doc_id: str
    span: dict[str, object]
    hash: str
    storage_ref: str


class LocalPageIndexNavigator(OpenAICompatClient):
    def __init__(self, *, model: str = _DEFAULT_MODEL_ID, prompt_hash: str = _DEFAULT_PROMPT_HASH) -> None:
        super().__init__(
            base_url="http://127.0.0.1:11434/v1",
            model_id=model,
            runtime_capabilities=RuntimeCapabilities(image_input=False, tool_calling=True),
            model_capabilities=ModelCapabilities(
                model_id=model,
                supports_vision=False,
                max_ctx=8192,
                default_kv_cache=2048,
            ),
            prompt_template_hash=prompt_hash,
        )


class DocIndexService:
    def __init__(
        self,
        vault_root: Path,
        *,
        audit_log: AuditLog,
        llm_client: OpenAICompatClient | None = None,
        navigator: OpenAICompatClient | None = None,
        runtime_capabilities: RuntimeCapabilities | None = None,
        model_capabilities: dict[str, ModelCapabilities] | None = None,
        now_fn=None,
    ) -> None:
        self._root = vault_root
        self._audit = audit_log
        self._runtime_caps = runtime_capabilities if runtime_capabilities is not None else RuntimeCapabilities(
            image_input=False,
            tool_calling=True,
            json_schema_mode=False,
        )
        self._model_caps = model_capabilities if model_capabilities is not None else {
            _DEFAULT_MODEL_ID: ModelCapabilities(
                model_id=_DEFAULT_MODEL_ID,
                supports_vision=False,
                max_ctx=8192,
                default_kv_cache=2048,
            )
        }
        default_model = self._model_caps.get(_DEFAULT_MODEL_ID, self._default_model_caps())
        effective_client = llm_client if llm_client is not None else navigator
        self._llm = effective_client if effective_client is not None else OpenAICompatClient(
            base_url="http://127.0.0.1:11434/v1",
            model_id=_DEFAULT_MODEL_ID,
            runtime_capabilities=self._runtime_caps,
            model_capabilities=default_model,
            prompt_template_hash=_DEFAULT_PROMPT_HASH,
        )
        self._policy_gate = PolicyGate(
            confidentiality_profile="confidential",
            llm_base_url=self._llm.base_url,
        )
        self._store = VaultStore(
            root=self._root,
            namespace=_DOCINDEX_DIR,
            key_filename="docindex_v1.key",
        )
        (self._store.path / _PAYLOAD_DIR).mkdir(exist_ok=True)
        (self._store.path / _EXCERPT_BLOB_DIR).mkdir(exist_ok=True)
        (self._store.path / _SOURCE_BLOB_DIR).mkdir(exist_ok=True)
        self._now_fn = now_fn or (lambda: datetime.now(UTC))
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
        self._write_source_blob(doc_id, source_bytes)

        records = self._load_records()
        existing = self._find_record(records, doc_id)
        now_iso = started.isoformat()
        building_record = DocumentIndexRecord(
            doc_id=doc_id,
            index_type="pageindex",
            version="pageindex_v2",
            created_at=existing.created_at if existing is not None else now_iso,
            updated_at=now_iso,
            source_hash=source_hash,
            index_hash="",
            status="building",
            error_summary=None,
            requires_ocr=False,
            vision_enabled_at_build=self._vision_enabled(),
            model_used=self._model_used_metadata(vision_used=False),
        )
        self._upsert_record(records, building_record)
        self._save_records(records)

        try:
            text = source_bytes.decode("utf-8", errors="ignore")
            has_text_layer = self._text_quality_ok(text)
            requires_ocr = not has_text_layer

            if has_text_layer:
                excerpt_records = self._build_excerpts(doc_id=doc_id, text=text, extraction_method="text_layer")
                tree, node_summaries = self._llm.build_pageindex_tree(
                    doc_id=doc_id,
                    text=text,
                    max_depth=options.max_depth,
                    target_granularity=options.target_granularity,
                    include_node_summaries=options.include_node_summaries,
                )
            else:
                excerpt_records = []
                tree, node_summaries = self._build_minimal_scanned_tree(doc_id=doc_id, source_bytes=source_bytes)

            payload = {
                "tree": tree,
                "node_summaries": node_summaries,
                "page_text_map": {
                    node["node_id"]: [
                        x.excerpt_id
                        for x in excerpt_records
                        if int(x.span.get("char_start", 10**9)) <= int(node.get("char_end", -1))
                    ]
                    for node in tree
                },
                "vision_artifacts": {},
                "build_metadata": {
                    "agent_model_id": self._llm.model_id,
                    "vision_model_id": self._llm.model_id if self._vision_enabled() else None,
                    "ctx": self._llm.model_capabilities.max_ctx,
                    "prompt_template_hash": self._llm.prompt_template_hash,
                    "runtime_id": "local-offline",
                    "build_time_seconds": max(0, int((self._now_fn() - started).total_seconds())),
                    "llm_endpoint": options.llm_endpoint,
                    "requires_ocr": requires_ocr,
                    "vision_enabled_at_build": self._vision_enabled(),
                },
            }
            index_hash = hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
            ).hexdigest()
            self._write_payload(doc_id, payload)
            if excerpt_records:
                self._upsert_excerpts(excerpt_records)

            ready = DocumentIndexRecord(
                doc_id=doc_id,
                index_type="pageindex",
                version="pageindex_v2",
                created_at=building_record.created_at,
                updated_at=self._now_fn().isoformat(),
                source_hash=source_hash,
                index_hash=index_hash,
                status="ready",
                error_summary=None,
                requires_ocr=requires_ocr,
                vision_enabled_at_build=self._vision_enabled(),
                model_used=self._model_used_metadata(vision_used=requires_ocr and self._vision_enabled()),
            )
            self._upsert_record(records, ready)
            self._save_records(records)
            self._audit.record(
                name="docindex_build_completed",
                metadata={"doc_id": doc_id, "job_id": job_id, "index_hash": index_hash, "requires_ocr": requires_ocr},
            )
            return JobRef(job_id=job_id, doc_id=doc_id, status="ready")
        except Exception:
            failed = DocumentIndexRecord(
                doc_id=doc_id,
                index_type="pageindex",
                version="pageindex_v2",
                created_at=building_record.created_at,
                updated_at=self._now_fn().isoformat(),
                source_hash=source_hash,
                index_hash="",
                status="failed",
                error_summary="docindex build failed",
                requires_ocr=False,
                vision_enabled_at_build=self._vision_enabled(),
                model_used=self._model_used_metadata(vision_used=False),
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
                requires_ocr=record.requires_ocr,
                vision_enabled_at_build=record.vision_enabled_at_build,
                model_used=record.model_used,
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

        if record.requires_ocr:
            if not self._vision_enabled():
                result = PageIndexResult(
                    doc_id=doc_id,
                    query=query,
                    hits=[],
                    trace={
                        "alert": "Scanned PDF requires OCR; vision not available in this runtime/model.",
                        "requires_ocr": True,
                    },
                    model_used=self._model_used_metadata(vision_used=False),
                    elapsed_ms=max(0, int((self._now_fn() - started).total_seconds() * 1000)),
                )
                self._set_cached_query(cache_key, result)
                self._audit.record(
                    name="docindex_query_executed",
                    metadata={"doc_id": doc_id, "query_hash": query_hash, "cached": False, "requires_ocr": True},
                )
                return result

            tree = payload.get("tree", [])
            node_summaries = payload.get("node_summaries", {})
            hits_nodes, trace = self._llm.query_pageindex_tree(
                tree=tree,
                node_summaries=node_summaries,
                query=query,
                section_hint=constraints.section_hint,
                max_results=constraints.max_results,
            )
            page_numbers: list[int] = []
            for node in hits_nodes:
                page_numbers.append(max(1, int(node.get("page_start", 1))))
            if not page_numbers:
                page_numbers = [1]
            vision = self.vision_read_pages(
                doc_id=doc_id,
                page_numbers=tuple(page_numbers),
                output_format="markdown",
                max_pages=max(1, min(3, constraints.max_results)),
                options=options,
            )
            hits = [
                {
                    "node_path": [{"node_id": f"{doc_id}:page:{item['page']}", "title": f"Page {item['page']}"}],
                    "page_range": item["page_range"],
                    "excerpt_ids": [item["excerpt_id"]],
                    "score": 1.0,
                    "rationale": "vision_page_match",
                    "doc_id": doc_id,
                }
                for item in vision["results"]
            ]
            result = PageIndexResult(
                doc_id=doc_id,
                query=query,
                hits=hits,
                trace={**trace, "vision_fallback": True},
                model_used=self._model_used_metadata(vision_used=True),
                elapsed_ms=max(0, int((self._now_fn() - started).total_seconds() * 1000)),
            )
            self._set_cached_query(cache_key, result)
            self._audit.record(
                name="docindex_query_executed",
                metadata={"doc_id": doc_id, "query_hash": query_hash, "cached": False, "requires_ocr": True},
            )
            return result

        tree = payload["tree"]
        node_summaries = payload.get("node_summaries", {})
        hits_nodes, trace = self._llm.query_pageindex_tree(
            tree=tree,
            node_summaries=node_summaries,
            query=query,
            section_hint=constraints.section_hint,
            max_results=constraints.max_results,
        )
        hits = [self._node_to_hit(doc_id=doc_id, node=node, constraints=constraints, payload=payload) for node in hits_nodes]
        result = PageIndexResult(
            doc_id=doc_id,
            query=query,
            hits=hits,
            trace=trace,
            model_used=self._model_used_metadata(vision_used=False),
            elapsed_ms=max(0, int((self._now_fn() - started).total_seconds() * 1000)),
        )
        self._set_cached_query(cache_key, result)
        self._audit.record(
            name="docindex_query_executed",
            metadata={"doc_id": doc_id, "query_hash": query_hash, "cached": False},
        )
        return result

    def vision_read_pages(
        self,
        *,
        doc_id: str,
        page_numbers: tuple[int, ...],
        output_format: str = "markdown",
        max_pages: int = 3,
        include_coordinates: bool = False,
        options: DocIndexBuildOptions,
    ) -> dict[str, object]:
        self._validate_build_options(options)
        if not self._vision_enabled():
            raise PermissionError("vision is not enabled for this runtime/model")
        if output_format not in {"markdown", "text"}:
            raise ValueError("output_format must be markdown or text")
        if max_pages < 1:
            raise ValueError("max_pages must be >= 1")

        unique_pages = []
        seen = set()
        for value in page_numbers:
            if value <= 0 or value in seen:
                continue
            seen.add(value)
            unique_pages.append(value)
            if len(unique_pages) >= min(10, max_pages):
                break
        if not unique_pages:
            raise ValueError("at least one valid page number is required")

        source_bytes = self._read_source_blob(doc_id)
        started = self._now_fn()
        page_text = self._llm.vision_read_pages(
            source_bytes=source_bytes,
            page_numbers=tuple(unique_pages),
            output_format=output_format,
        )
        results: list[dict[str, object]] = []
        new_excerpt_records: list[ExcerptRecord] = []
        payload = self._read_payload(doc_id)
        vision_artifacts = payload.get("vision_artifacts")
        if not isinstance(vision_artifacts, dict):
            vision_artifacts = {}

        for page in unique_pages:
            text = page_text.get(page, "")
            excerpt = self._store_excerpt_text(
                doc_id=doc_id,
                text=text,
                span={"page_start": page, "page_end": page, "extraction_method": "vision"},
            )
            new_excerpt_records.append(excerpt)
            key = str(page)
            prior = vision_artifacts.get(key)
            if not isinstance(prior, list):
                prior = []
            prior.append(excerpt.excerpt_id)
            vision_artifacts[key] = prior
            results.append(
                {
                    "page": page,
                    "excerpt_id": excerpt.excerpt_id,
                    "page_range": {"start": page, "end": page},
                    "coordinates": None if not include_coordinates else {},
                }
            )

        if new_excerpt_records:
            self._append_excerpts(new_excerpt_records)
            payload["vision_artifacts"] = vision_artifacts
            self._write_payload(doc_id, payload)

        elapsed_ms = max(0, int((self._now_fn() - started).total_seconds() * 1000))
        self._audit.record(
            name="vision_read_pages_executed",
            metadata={"doc_id": doc_id, "page_numbers": unique_pages, "count": len(unique_pages)},
        )
        return {
            "doc_id": doc_id,
            "results": results,
            "model_used": self._model_used_metadata(vision_used=True),
            "elapsed_ms": elapsed_ms,
        }

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
        return record.status if record is not None else None

    def get_record(self, doc_id: str) -> DocumentIndexRecord | None:
        return self._find_record(self._load_records(), doc_id)

    def _node_to_hit(
        self,
        *,
        doc_id: str,
        node: dict[str, object],
        constraints: DocIndexQueryConstraints,
        payload: dict[str, object],
    ) -> dict[str, object]:
        node_id = str(node["node_id"])
        page_text_map = payload.get("page_text_map")
        excerpt_ids: list[str] = []
        if isinstance(page_text_map, dict):
            values = page_text_map.get(node_id)
            if isinstance(values, list):
                excerpt_ids = [str(x) for x in values]
        if constraints.require_page_ranges:
            range_payload = {"start": int(node.get("page_start", 1)), "end": int(node.get("page_end", 1))}
            range_key = "page_range"
        else:
            range_payload = {"char_start": int(node.get("char_start", 0)), "char_end": int(node.get("char_end", 0))}
            range_key = "span_range"
        return {
            "node_path": [{"node_id": node_id, "title": str(node.get("title", ""))}],
            range_key: range_payload,
            "excerpt_ids": excerpt_ids,
            "score": 1.0,
            "rationale": "node_match",
            "doc_id": doc_id,
        }

    def _build_excerpts(self, *, doc_id: str, text: str, extraction_method: str) -> list[ExcerptRecord]:
        records: list[ExcerptRecord] = []
        chunk_size = 450
        for start in range(0, len(text), chunk_size):
            segment = text[start : start + chunk_size]
            if not segment:
                continue
            records.append(
                self._store_excerpt_text(
                    doc_id=doc_id,
                    text=segment,
                    span={"char_start": start, "char_end": start + len(segment), "extraction_method": extraction_method},
                )
            )
        if not records:
            records.append(
                self._store_excerpt_text(
                    doc_id=doc_id,
                    text="",
                    span={"char_start": 0, "char_end": 0, "extraction_method": extraction_method},
                )
            )
        return records

    def _store_excerpt_text(self, *, doc_id: str, text: str, span: dict[str, object]) -> ExcerptRecord:
        excerpt_id = str(uuid.uuid4())
        plaintext = text.encode("utf-8")
        hash_value = hashlib.sha256(plaintext).hexdigest()
        storage_ref = f"{excerpt_id}.enc"
        self._store.write_blob(f"{_EXCERPT_BLOB_DIR}/{storage_ref}", plaintext)
        return ExcerptRecord(
            excerpt_id=excerpt_id,
            doc_id=doc_id,
            span=span,
            hash=hash_value,
            storage_ref=storage_ref,
        )

    def _upsert_excerpts(self, excerpts: list[ExcerptRecord]) -> None:
        current = [x for x in self._load_excerpts() if x.doc_id != excerpts[0].doc_id]
        current.extend(excerpts)
        self._store.write_json(_EXCERPTS_FILE, [asdict(x) for x in current])

    def _append_excerpts(self, excerpts: list[ExcerptRecord]) -> None:
        current = self._load_excerpts()
        current.extend(excerpts)
        self._store.write_json(_EXCERPTS_FILE, [asdict(x) for x in current])

    def _find_excerpt(self, excerpt_id: str) -> ExcerptRecord | None:
        for item in self._load_excerpts():
            if item.excerpt_id == excerpt_id:
                return item
        return None

    def _load_excerpts(self) -> list[ExcerptRecord]:
        payload = self._store.read_json(_EXCERPTS_FILE, default=[])
        out: list[ExcerptRecord] = []
        if not isinstance(payload, list):
            return out
        for raw in payload:
            if not isinstance(raw, dict):
                continue
            span_raw = raw.get("span", {})
            if not isinstance(span_raw, dict):
                span_raw = {}
            out.append(
                ExcerptRecord(
                    excerpt_id=str(raw["excerpt_id"]),
                    doc_id=str(raw["doc_id"]),
                    span=dict(span_raw),
                    hash=str(raw["hash"]),
                    storage_ref=str(raw["storage_ref"]),
                )
            )
        return out

    def _read_excerpt_text(self, excerpt: ExcerptRecord) -> str:
        plaintext = self._store.read_blob(f"{_EXCERPT_BLOB_DIR}/{excerpt.storage_ref}")
        if hashlib.sha256(plaintext).hexdigest() != excerpt.hash:
            raise ValueError("excerpt integrity mismatch")
        return plaintext.decode("utf-8")

    def _build_minimal_scanned_tree(self, *, doc_id: str, source_bytes: bytes) -> tuple[list[dict[str, object]], dict[str, str]]:
        approx_pages = max(1, min(20, len(source_bytes) // 2048 + 1))
        tree: list[dict[str, object]] = []
        summaries: dict[str, str] = {}
        for page in range(1, approx_pages + 1):
            node_id = f"{doc_id}:page:{page}"
            tree.append(
                {
                    "node_id": node_id,
                    "title": f"Page {page}",
                    "depth": 1,
                    "page_start": page,
                    "page_end": page,
                    "char_start": 0,
                    "char_end": 0,
                    "children": [],
                }
            )
            summaries[node_id] = "scanned page"
        return tree, summaries

    def _text_quality_ok(self, text: str) -> bool:
        cleaned = text.strip()
        if len(cleaned) < _MIN_TEXT_THRESHOLD:
            return False
        printable = sum(1 for ch in cleaned if ch.isprintable())
        ratio = printable / max(1, len(cleaned))
        return ratio >= _MIN_PRINTABLE_RATIO

    def _vision_enabled(self) -> bool:
        model_caps = self._model_caps.get(_DEFAULT_MODEL_ID)
        if model_caps is None:
            return False
        return bool(self._runtime_caps.image_input and model_caps.supports_vision)

    def _model_used_metadata(self, *, vision_used: bool) -> dict[str, object]:
        model_caps = self._model_caps.get(_DEFAULT_MODEL_ID, self._default_model_caps())
        return {
            "agent_model_id": _DEFAULT_MODEL_ID,
            "vision_model_id": _DEFAULT_MODEL_ID if vision_used else None,
            "prompt_template_hash": self._llm.prompt_template_hash,
            "ctx": model_caps.max_ctx,
        }

    @staticmethod
    def _default_model_caps() -> ModelCapabilities:
        return ModelCapabilities(
            model_id=_DEFAULT_MODEL_ID,
            supports_vision=False,
            max_ctx=8192,
            default_kv_cache=2048,
        )

    def _cleanup_query_cache(self) -> None:
        now = self._now_fn()
        raw = self._store.read_json(_QUERY_CACHE_FILE, default=[])
        if not isinstance(raw, list):
            self._store.write_json(_QUERY_CACHE_FILE, [])
            return
        keep: list[dict[str, object]] = []
        for entry in raw:
            if not isinstance(entry, dict):
                continue
            expires = datetime.fromisoformat(str(entry["expires_at"]))
            if expires > now:
                keep.append(entry)
        self._store.write_json(_QUERY_CACHE_FILE, keep)

    def _get_cached_query(self, cache_key: str) -> PageIndexResult | None:
        entries = self._store.read_json(_QUERY_CACHE_FILE, default=[])
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
        entries = self._store.read_json(_QUERY_CACHE_FILE, default=[])
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
        self._store.write_json(_QUERY_CACHE_FILE, filtered)

    def _validate_build_options(self, options: DocIndexBuildOptions) -> None:
        if options.confidentiality_profile not in {"confidential", "standard"}:
            raise ValueError("confidentiality_profile must be confidential or standard")
        if options.confidentiality_profile == "confidential":
            gate = PolicyGate(confidentiality_profile="confidential", llm_base_url=self._llm.base_url)
            gate.enforce_local_only_ocr(mode=options.mode, pdf_text_extraction=options.pdf_text_extraction)
            if options.llm_provider != "openai_compat":
                raise PermissionError("confidential profile requires openai_compat provider")
            gate.enforce_localhost_llm()
            # Build-time endpoint override must also remain localhost in confidential mode.
            PolicyGate(confidentiality_profile="confidential", llm_base_url=options.llm_endpoint).enforce_localhost_llm()
        if options.max_depth < 1 or options.max_depth > 12:
            raise ValueError("max_depth must be within 1..12")
        if options.target_granularity not in {"section", "subsection"}:
            raise ValueError("target_granularity must be section or subsection")

    def _write_payload(self, doc_id: str, payload: dict[str, object]) -> None:
        self._store.write_json(f"{_PAYLOAD_DIR}/{doc_id}.enc", payload)

    def _read_payload(self, doc_id: str) -> dict[str, object]:
        payload = self._store.read_json(f"{_PAYLOAD_DIR}/{doc_id}.enc", default={})
        if not isinstance(payload, dict):
            raise ValueError("invalid payload")
        return payload

    def _write_source_blob(self, doc_id: str, source_bytes: bytes) -> None:
        self._store.write_blob(f"{_SOURCE_BLOB_DIR}/{doc_id}.enc", source_bytes)

    def _read_source_blob(self, doc_id: str) -> bytes:
        path = self._store.path / _SOURCE_BLOB_DIR / f"{doc_id}.enc"
        if not path.exists():
            raise KeyError(f"source blob missing for doc_id: {doc_id}")
        return self._store.read_blob(f"{_SOURCE_BLOB_DIR}/{doc_id}.enc")

    def _load_records(self) -> list[DocumentIndexRecord]:
        payload = self._store.read_json(_RECORDS_FILE, default=[])
        out: list[DocumentIndexRecord] = []
        if not isinstance(payload, list):
            return out
        for raw in payload:
            if not isinstance(raw, dict):
                continue
            model_used = raw.get("model_used")
            if not isinstance(model_used, dict):
                model_used = self._model_used_metadata(vision_used=False)
            out.append(
                DocumentIndexRecord(
                    doc_id=str(raw["doc_id"]),
                    index_type=str(raw.get("index_type", "pageindex")),
                    version=str(raw.get("version", "pageindex_v1")),
                    created_at=str(raw["created_at"]),
                    updated_at=str(raw["updated_at"]),
                    source_hash=str(raw["source_hash"]),
                    index_hash=str(raw["index_hash"]),
                    status=str(raw["status"]),  # type: ignore[arg-type]
                    error_summary=raw.get("error_summary"),
                    requires_ocr=bool(raw.get("requires_ocr", False)),
                    vision_enabled_at_build=bool(raw.get("vision_enabled_at_build", False)),
                    model_used=model_used,
                )
            )
        return out

    def _save_records(self, records: list[DocumentIndexRecord]) -> None:
        self._store.write_json(_RECORDS_FILE, [asdict(x) for x in records])

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
