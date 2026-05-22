from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from src.qual.audit import AuditLog
from src.qual.engine.retrieval.payload import _build_retrieval_basket_promotion_bundle_from_payload
from src.qual.retrieval.service import RetrievalConstraints
from src.qual.retrieval.service import RetrievalQuery
from src.qual.retrieval.service import RetrievalService


class SparsePromotionProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.service = RetrievalService(self.root, audit_log=AuditLog(self.root))
        self.service.add_or_update_document(
            doc_id="doc-memo-1",
            doc_type="memo",
            title_hint="Memo Alpha",
            text="Memo about coding frame and comparison notes.",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @staticmethod
    def _strip_sparse_promotion_key(snapshot: object, key: str) -> None:
        if isinstance(snapshot, dict):
            snapshot.pop(key, None)
            for value in snapshot.values():
                SparsePromotionProvenanceTests._strip_sparse_promotion_key(value, key)
        elif isinstance(snapshot, list):
            for value in snapshot:
                SparsePromotionProvenanceTests._strip_sparse_promotion_key(value, key)

    def _payload(self) -> dict[str, object]:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )
        payload = result.to_downstream_payload()
        self.assertTrue(result.basket_promotion_items())
        self.assertIn("retrieval_basket_promotion_bundle", payload)
        return payload

    def test_existing_sparse_promotion_bundle_requires_doc_and_source_type(self) -> None:
        base_payload = self._payload()

        for required_key in ("doc_type", "source_type"):
            payload = copy.deepcopy(base_payload)
            self._strip_sparse_promotion_key(payload, required_key)

            normalized_bundle = _build_retrieval_basket_promotion_bundle_from_payload(payload)

            self.assertEqual(normalized_bundle["promotion_items"], [])
            self.assertEqual(normalized_bundle["basket_promotion_items"], [])
            self.assertEqual(normalized_bundle["basket_promotion_count"], 0)
            self.assertFalse(normalized_bundle["basket_promotion_ready"])

    def test_sparse_promotion_rebuild_requires_doc_and_source_type(self) -> None:
        base_payload = self._payload()
        base_payload.pop("retrieval_basket_promotion_bundle", None)

        for required_key in ("doc_type", "source_type"):
            payload = copy.deepcopy(base_payload)
            self._strip_sparse_promotion_key(payload, required_key)

            rebuilt_bundle = _build_retrieval_basket_promotion_bundle_from_payload(payload)

            self.assertEqual(rebuilt_bundle["promotion_items"], [])
            self.assertEqual(rebuilt_bundle["basket_promotion_items"], [])
            self.assertEqual(rebuilt_bundle["basket_promotion_count"], 0)
            self.assertFalse(rebuilt_bundle["basket_promotion_ready"])


if __name__ == "__main__":
    unittest.main()
