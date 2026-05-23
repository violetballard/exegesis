from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from src.qual.audit import AuditLog
from src.qual.engine.retrieval.payload import _build_retrieval_basket_promotion_bundle_from_payload
from src.qual.engine.retrieval.payload import _stable_fingerprint
from src.qual.retrieval.service import RetrievalConstraints
from src.qual.retrieval.service import RetrievalQuery
from src.qual.retrieval.service import RetrievalService


class SparsePromotionProvenanceValidationTests(unittest.TestCase):
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
    def _strip_key(snapshot: object, key: str) -> None:
        if isinstance(snapshot, dict):
            snapshot.pop(key, None)
            for value in snapshot.values():
                SparsePromotionProvenanceValidationTests._strip_key(value, key)
        elif isinstance(snapshot, list):
            for value in snapshot:
                SparsePromotionProvenanceValidationTests._strip_key(value, key)

    @staticmethod
    def _replace_key(snapshot: object, key: str, value: object) -> None:
        if isinstance(snapshot, dict):
            if key in snapshot:
                snapshot[key] = value
            for nested in snapshot.values():
                SparsePromotionProvenanceValidationTests._replace_key(nested, key, value)
        elif isinstance(snapshot, list):
            for nested in snapshot:
                SparsePromotionProvenanceValidationTests._replace_key(nested, key, value)

    @staticmethod
    def _strip_doc_source_record_key(snapshot: object, key: str) -> None:
        if isinstance(snapshot, dict):
            if (
                snapshot.get("doc_id") == "doc-memo-1"
                and "excerpt_id" not in snapshot
                and "basket_item_id" not in snapshot
                and "item_id" not in snapshot
            ):
                snapshot.pop(key, None)
            for nested in snapshot.values():
                SparsePromotionProvenanceValidationTests._strip_doc_source_record_key(nested, key)
        elif isinstance(snapshot, list):
            for nested in snapshot:
                SparsePromotionProvenanceValidationTests._strip_doc_source_record_key(nested, key)

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

    def _assert_not_ready(self, bundle: dict[str, object]) -> None:
        self.assertEqual(bundle["promotion_items"], [])
        self.assertEqual(bundle["basket_promotion_items"], [])
        self.assertEqual(bundle["basket_promotion_count"], 0)
        self.assertFalse(bundle["basket_promotion_ready"])

    def test_existing_bundle_enrichment_requires_explicit_backend_and_mode(self) -> None:
        base_payload = self._payload()

        for required_key in ("retrieval_backend", "retrieval_mode"):
            payload = copy.deepcopy(base_payload)
            self._strip_key(payload, required_key)

            self._assert_not_ready(_build_retrieval_basket_promotion_bundle_from_payload(payload))

    def test_existing_bundle_enrichment_rejects_stale_lookup_fingerprint(self) -> None:
        payload = self._payload()
        self._replace_key(payload, "excerpt_lookup_fingerprint", "stale-fingerprint")

        self._assert_not_ready(_build_retrieval_basket_promotion_bundle_from_payload(payload))

    def test_live_basket_promotion_uses_canonical_doc_identity_fingerprint(self) -> None:
        payload = self._payload()
        basket_items = payload["retrieval_basket_promotion_bundle"]["basket_promotion_items"]
        self.assertTrue(basket_items)

        for item in basket_items:
            expected_fingerprint = _stable_fingerprint(
                {
                    "doc_id": item["doc_id"],
                    "source_hash": item["source_hash"],
                    "doc_type": item["doc_type"],
                }
            )
            self.assertEqual(item["doc_identity_fingerprint"], expected_fingerprint)
            self.assertEqual(item["source_type"], item["doc_type"])

    def test_existing_bundle_enrichment_rejects_stale_doc_identity_fingerprint(self) -> None:
        payload = self._payload()
        self._replace_key(payload, "doc_identity_fingerprint", "stale-doc-identity")

        self._assert_not_ready(_build_retrieval_basket_promotion_bundle_from_payload(payload))

    def test_existing_bundle_enrichment_rejects_incomplete_doc_source_record(self) -> None:
        payload = self._payload()
        self._strip_doc_source_record_key(payload, "source_hash")

        self._assert_not_ready(_build_retrieval_basket_promotion_bundle_from_payload(payload))

    def test_rebuild_requires_explicit_backend_and_mode(self) -> None:
        base_payload = self._payload()
        base_payload.pop("retrieval_basket_promotion_bundle", None)

        for required_key in ("retrieval_backend", "retrieval_mode"):
            payload = copy.deepcopy(base_payload)
            self._strip_key(payload, required_key)

            self._assert_not_ready(_build_retrieval_basket_promotion_bundle_from_payload(payload))

    def test_rebuild_rejects_stale_lookup_fingerprint(self) -> None:
        payload = self._payload()
        payload.pop("retrieval_basket_promotion_bundle", None)
        self._replace_key(payload, "excerpt_lookup_fingerprint", "stale-fingerprint")

        self._assert_not_ready(_build_retrieval_basket_promotion_bundle_from_payload(payload))

    def test_rebuild_rejects_stale_doc_identity_fingerprint(self) -> None:
        payload = self._payload()
        payload.pop("retrieval_basket_promotion_bundle", None)
        self._replace_key(payload, "doc_identity_fingerprint", "stale-doc-identity")

        self._assert_not_ready(_build_retrieval_basket_promotion_bundle_from_payload(payload))

    def test_rebuild_rejects_incomplete_doc_source_record(self) -> None:
        payload = self._payload()
        payload.pop("retrieval_basket_promotion_bundle", None)
        self._strip_doc_source_record_key(payload, "source_hash")

        self._assert_not_ready(_build_retrieval_basket_promotion_bundle_from_payload(payload))

    def test_live_basket_promotion_requires_explicit_source_type(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )
        self.assertTrue(result.basket_promotion_items())

        for hit in result.hits:
            hit.provenance.pop("source_type", None)

        self.assertEqual(result.basket_promotion_items(), [])
        self.assertFalse(result.retrieval_basket_promotion_bundle()["basket_promotion_ready"])


if __name__ == "__main__":
    unittest.main()
