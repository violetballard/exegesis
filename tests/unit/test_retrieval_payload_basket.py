from __future__ import annotations

import hashlib
import unittest

from src.qual.engine.retrieval.payload import (
    _build_retrieval_context_bundle_from_payload,
    _stable_fingerprint,
)


def _complete_promotion_item(*, item_id: str = "excerpt-1") -> dict[str, object]:
    excerpt_text = "memo excerpt"
    excerpt_text_hash = hashlib.sha256(excerpt_text.encode("utf-8")).hexdigest()
    span = {"char_range": {"start": 0, "end": len(excerpt_text)}}
    excerpt_fingerprint = _stable_fingerprint(
        {
            "doc_id": "doc-1",
            "source_hash": "source-1",
            "excerpt_id": "excerpt-1",
            "span": span,
            "excerpt_text_hash": excerpt_text_hash,
        }
    )
    excerpt_lookup_fingerprint = _stable_fingerprint(
        {
            "excerpt_id": "excerpt-1",
            "doc_id": "doc-1",
            "source_hash": "source-1",
            "span": span,
            "text_hash": excerpt_text_hash,
            "source_strategy": "fts",
            "retrieval_backend": "sqlite_fts",
            "retrieval_mode": "fts_first",
            "lookup_resolution": "fts",
        }
    )
    return {
        "item_id": item_id,
        "item_type": "excerpt",
        "doc_id": "doc-1",
        "doc_type": "note",
        "source_type": "note",
        "source_hash": "source-1",
        "doc_identity_fingerprint": "doc-identity-1",
        "excerpt_id": "excerpt-1",
        "excerpt_text": excerpt_text,
        "snippet": excerpt_text,
        "excerpt_fingerprint": excerpt_fingerprint,
        "excerpt_lookup_fingerprint": excerpt_lookup_fingerprint,
        "excerpt_text_hash": excerpt_text_hash,
        "span": span,
        "source_strategy": "fts",
        "retrieval_backend": "sqlite_fts",
        "retrieval_mode": "fts_first",
    }


class RetrievalPayloadBasketTests(unittest.TestCase):
    def test_context_bundle_recovers_canonical_fts_basket_identity(self) -> None:
        payload = {
            "result_fingerprint": "result-1",
            "query": {"query_text": "memo", "scope": "vault", "intent": "compare"},
            "retrieval_summary": {"basket_item_ids": ["excerpt-1"]},
            "retrieval_evidence": {
                "basket_promotion_items": [
                    _complete_promotion_item()
                ]
            },
            "basket_promotion_items": [
                _complete_promotion_item()
            ],
            "basket_item_ids": ["excerpt-1"],
            "excerpt_hits": [
                _complete_promotion_item()
            ],
        }

        context_bundle = _build_retrieval_context_bundle_from_payload(payload)

        promotion_item = context_bundle["basket_promotion_items"][0]
        self.assertEqual(context_bundle["basket_item_ids"], ["retrieval:fts:excerpt-1"])
        self.assertEqual(promotion_item["item_id"], "retrieval:fts:excerpt-1")
        self.assertEqual(promotion_item["basket_item_id"], "retrieval:fts:excerpt-1")
        self.assertEqual(
            promotion_item["canonical_demo_path_steps"],
            ["retrieve_relevant_material", "promote_context_to_basket"],
        )

    def test_context_bundle_prefers_explicit_canonical_basket_identity(self) -> None:
        payload = {
            "basket_promotion_items": [
                {
                    **_complete_promotion_item(item_id="stale-id"),
                    "basket_item_id": "retrieval:fts:excerpt-1",
                }
            ],
            "basket_item_ids": ["stale-id"],
        }

        context_bundle = _build_retrieval_context_bundle_from_payload(payload)

        self.assertEqual(context_bundle["basket_item_ids"], ["retrieval:fts:excerpt-1"])
        self.assertEqual(
            context_bundle["basket_promotion_items"][0]["item_id"],
            "retrieval:fts:excerpt-1",
        )
