from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.qual.audit import AuditLog
from src.qual.docindex.service import (
    DocIndexBuildOptions,
    DocIndexQueryConstraints,
    DocIndexService,
    LocalPageIndexNavigator,
    ModelCapabilities,
    RuntimeCapabilities,
)


class PageIndexDocIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.audit = AuditLog(self.root)
        self.navigator = LocalPageIndexNavigator()
        self.svc = DocIndexService(self.root, audit_log=self.audit, navigator=self.navigator)
        self.doc_id = "doc-1"
        self.source = (
            "# Methods\n"
            "Sampling details and recruitment constraints.\n"
            "# Findings\n"
            "Theme synthesis and implications for theory.\n"
        ).encode("utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_confidential_profile_rejects_non_localhost_endpoint(self) -> None:
        with self.assertRaises(PermissionError):
            self.svc.build(
                self.doc_id,
                self.source,
                DocIndexBuildOptions(
                    confidentiality_profile="confidential",
                    llm_endpoint="https://api.openai.com/v1",
                ),
            )

    def test_query_returns_node_path_and_excerpt_ids_shape(self) -> None:
        self.svc.build(self.doc_id, self.source, DocIndexBuildOptions())
        result = self.svc.query(
            self.doc_id,
            self.source,
            "findings synthesis",
            DocIndexQueryConstraints(max_results=2),
            options=DocIndexBuildOptions(),
        )
        self.assertEqual(result.doc_id, self.doc_id)
        self.assertTrue(result.hits)
        hit = result.hits[0]
        self.assertIn("node_path", hit)
        self.assertIn("excerpt_ids", hit)
        self.assertNotIn("text", hit)
        self.assertIsInstance(hit["excerpt_ids"], list)

    def test_source_hash_mismatch_marks_record_stale(self) -> None:
        self.svc.build(self.doc_id, self.source, DocIndexBuildOptions())
        modified = self.source + b"\nchanged"
        with self.assertRaises(ValueError):
            self.svc.query(
                self.doc_id,
                modified,
                "methods",
                DocIndexQueryConstraints(),
                options=DocIndexBuildOptions(),
            )
        self.assertEqual(self.svc.get_record_status(self.doc_id), "stale")

    def test_index_artifacts_are_encrypted_at_rest(self) -> None:
        self.svc.build(self.doc_id, self.source, DocIndexBuildOptions())
        docindex_dir = self.root / ".docindex"
        raw = (docindex_dir / "records_v1.enc.json").read_bytes()
        self.assertNotIn(b"Methods", raw)
        payload_raw = (docindex_dir / "payloads" / f"{self.doc_id}.enc").read_bytes()
        self.assertNotIn(b"Findings", payload_raw)
        source_raw = (docindex_dir / "source_blobs" / f"{self.doc_id}.enc").read_bytes()
        self.assertNotIn(b"Methods", source_raw)

    def test_query_cache_prevents_repeat_navigation(self) -> None:
        self.svc.build(self.doc_id, self.source, DocIndexBuildOptions())
        before = self.navigator.query_calls
        self.svc.query(
            self.doc_id,
            self.source,
            "methods",
            DocIndexQueryConstraints(max_results=3),
            options=DocIndexBuildOptions(),
        )
        mid = self.navigator.query_calls
        self.svc.query(
            self.doc_id,
            self.source,
            "methods",
            DocIndexQueryConstraints(max_results=3),
            options=DocIndexBuildOptions(),
        )
        after = self.navigator.query_calls
        self.assertEqual(mid, before + 1)
        self.assertEqual(after, mid)

    def test_audit_events_capture_build_and_query_without_raw_query(self) -> None:
        self.svc.build(self.doc_id, self.source, DocIndexBuildOptions())
        self.svc.query(
            self.doc_id,
            self.source,
            "sensitive user prompt",
            DocIndexQueryConstraints(),
            options=DocIndexBuildOptions(),
        )
        events = [json.loads(line) for line in (self.root / "audit_events.jsonl").read_text(encoding="utf-8").splitlines()]
        names = [entry["name"] for entry in events]
        self.assertIn("docindex_build_started", names)
        self.assertIn("docindex_build_completed", names)
        self.assertIn("docindex_query_executed", names)
        serialized = json.dumps(events, sort_keys=True)
        self.assertNotIn("sensitive user prompt", serialized)

    def test_fetch_excerpt_returns_text_and_provenance(self) -> None:
        self.svc.build(self.doc_id, self.source, DocIndexBuildOptions())
        result = self.svc.query(
            self.doc_id,
            self.source,
            "methods",
            DocIndexQueryConstraints(max_results=1),
            options=DocIndexBuildOptions(),
        )
        excerpt_id = result.hits[0]["excerpt_ids"][0]  # type: ignore[index]
        excerpt = self.svc.fetch_excerpt(str(excerpt_id))
        self.assertEqual(excerpt["excerpt_id"], str(excerpt_id))
        self.assertIn("text", excerpt)
        self.assertIn("provenance", excerpt)

    def test_scanned_pdf_without_vision_returns_alert(self) -> None:
        scanned = b"\x89PNG\x00\x01\x02" * 40
        self.svc.build("scan-1", scanned, DocIndexBuildOptions())
        result = self.svc.query(
            "scan-1",
            scanned,
            "methods",
            DocIndexQueryConstraints(max_results=2),
            options=DocIndexBuildOptions(),
        )
        self.assertEqual(result.hits, [])
        self.assertIn("alert", result.trace)
        record = self.svc.get_record("scan-1")
        self.assertIsNotNone(record)
        self.assertTrue(record.requires_ocr)  # type: ignore[union-attr]

    def test_scanned_pdf_with_vision_enabled_allows_vision_read(self) -> None:
        scanned = b"\x89PNG\x00\x01\x02" * 40
        svc = DocIndexService(
            self.root,
            audit_log=self.audit,
            navigator=self.navigator,
            runtime_capabilities=RuntimeCapabilities(image_input=True, tool_calling=True),
            model_capabilities={
                "magistral-small": ModelCapabilities(
                    model_id="magistral-small",
                    supports_vision=True,
                    max_ctx=8192,
                    default_kv_cache=2048,
                )
            },
        )
        svc.build("scan-2", scanned, DocIndexBuildOptions())
        result = svc.query(
            "scan-2",
            scanned,
            "page",
            DocIndexQueryConstraints(max_results=2),
            options=DocIndexBuildOptions(),
        )
        self.assertTrue(result.hits)
        first = result.hits[0]
        self.assertIn("page_range", first)
        self.assertTrue(first["excerpt_ids"])  # type: ignore[index]

        vision_events = [
            json.loads(line)
            for line in (self.root / "audit_events.jsonl").read_text(encoding="utf-8").splitlines()
            if json.loads(line)["name"] == "vision_read_pages_executed"
        ]
        self.assertTrue(vision_events)

    def test_vision_read_pages_rejects_when_capability_disabled(self) -> None:
        self.svc.build(self.doc_id, self.source, DocIndexBuildOptions())
        with self.assertRaises(PermissionError):
            self.svc.vision_read_pages(
                doc_id=self.doc_id,
                page_numbers=(1,),
                options=DocIndexBuildOptions(),
            )


if __name__ == "__main__":
    unittest.main()
