import tempfile
import unittest
from pathlib import Path

from src.qual.audit import AuditLog
from src.qual.retrieval.service import RetrievalService


class RetrievalFtsProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.service = RetrievalService(self.root, audit_log=AuditLog(self.root))
        self.service.add_or_update_document(
            doc_id="doc-pdf-1",
            doc_type="pdf",
            title_hint="Interview Packet",
            text=(
                "Methods section with recruitment constraints and ethics notes. "
                "Discussion includes theory implications and synthesis framing."
            ),
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_sparse_fts_excerpt_lookup_rejects_stale_source_hash(self) -> None:
        with self.assertRaisesRegex(ValueError, "stale FTS source_hash"):
            self.service._normalize_excerpt_payload(
                {
                    "excerpt_id": "fts_sparse_lookup",
                    "doc_id": "doc-pdf-1",
                    "span": {"char_range": {"start": 0, "end": 19}},
                    "text": "Methods section with",
                    "provenance": {"source_hash": "stale-source-hash"},
                },
                source_strategy="fts",
                lookup_resolution="fts",
            )

    def test_sparse_fts_excerpt_lookup_rejects_stale_doc_identity(self) -> None:
        with self.assertRaisesRegex(ValueError, "stale FTS doc_identity_fingerprint"):
            self.service._normalize_excerpt_payload(
                {
                    "excerpt_id": "fts_sparse_lookup",
                    "doc_id": "doc-pdf-1",
                    "span": {"char_range": {"start": 0, "end": 19}},
                    "text": "Methods section with",
                    "provenance": {"doc_identity_fingerprint": "stale-doc-identity"},
                },
                source_strategy="fts",
                lookup_resolution="fts",
            )


if __name__ == "__main__":
    unittest.main()
