from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.qual.docindex.service import DocIndexBuildOptions, DocIndexQueryConstraints, DocIndexService
from src.qual.engine.retrieval.interface import StrategyRun


class PageIndexStrategy:
    id = "pageindex"

    def __init__(self, service: DocIndexService, read_doc_text, *, now_fn=None) -> None:
        self._service = service
        self._read_doc_text = read_doc_text
        self._now_fn = now_fn or (lambda: datetime.now(UTC))

    def supports(self, query: Any) -> bool:
        return True

    def retrieve(self, query: Any, *, candidate_doc_ids: tuple[str, ...]) -> StrategyRun:
        started = self._now_fn()
        hits: list[Any] = []
        for doc_id in candidate_doc_ids:
            if self._service.get_record_status(doc_id) != "ready":
                continue
            try:
                result = self._service.query(
                    doc_id,
                    self._read_doc_text(doc_id).encode("utf-8"),
                    query.query_text,
                    DocIndexQueryConstraints(
                        max_results=3,
                        section_hint=query.constraints.section_hint,
                        require_page_ranges=True,
                    ),
                    options=DocIndexBuildOptions(confidentiality_profile=query.confidentiality_profile),
                )
            except Exception:
                continue
            for item in result.hits:
                excerpt_ids = item.get("excerpt_ids", [])
                excerpt_id = str(excerpt_ids[0]) if excerpt_ids else None
                span = {"page_range": dict(item["page_range"])} if "page_range" in item else {
                    "char_range": dict(item.get("span_range", {}))
                }
                hits.append(
                    {
                        "doc_id": doc_id,
                        "excerpt_id": excerpt_id,
                        "span": span,
                        "title_hint": None,
                        "score": float(item.get("score", 0.5)),
                        "source_strategy": "pageindex",
                        "rationale": str(item.get("rationale", "")),
                        "node_path": item.get("node_path"),
                    }
                )
        elapsed_ms = max(0, int((self._now_fn() - started).total_seconds() * 1000))
        return StrategyRun(strategy_id=self.id, hits=hits, elapsed_ms=elapsed_ms, cache_used=False)
