from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from src.qual.audit import AuditLog
from src.qual.docindex.service import DocIndexBuildOptions, DocIndexQueryConstraints, DocIndexService, LocalPageIndexNavigator


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


if __name__ == "__main__":
    unittest.main()
