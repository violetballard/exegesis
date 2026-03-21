from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.qual.audit import AuditLog
from src.qual.docindex.service import DocIndexBuildOptions
from src.qual.docindex.service import DocIndexQueryConstraints
import src.qual.engine.retrieval as engine_retrieval
from src.qual.engine.retrieval.pageindex_strategy import PageIndexStrategy
from src.qual.retrieval.service import RetrievalConstraints, RetrievalQuery, RetrievalService


class UnifiedRetrievalTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.audit = AuditLog(self.root)
        self.service = RetrievalService(self.root, audit_log=self.audit)

        self.service.add_or_update_document(
            doc_id="doc-pdf-1",
            doc_type="pdf",
            title_hint="Interview Packet",
            text=(
                "Methods section with recruitment constraints and ethics notes. "
                "Discussion includes theory implications and synthesis framing."
            ),
        )
        self.service.add_or_update_document(
            doc_id="doc-memo-1",
            doc_type="memo",
            title_hint="Memo Alpha",
            text="Memo about coding frame and comparison notes.",
        )
        self.service.build_pageindex(doc_id="doc-pdf-1", options=DocIndexBuildOptions(confidentiality_profile="confidential"))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_single_retrieve_auto_interface(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="theory implications",
                scope="vault",
                intent="lookup",
                constraints=RetrievalConstraints(max_results=5),
                confidentiality_profile="confidential",
            )
        )
        self.assertTrue(result.hits)
        self.assertTrue(result.doc_hits)
        self.assertEqual(result.diagnostics["retrieval_backend"], "sqlite_fts")
        self.assertEqual(result.diagnostics["retrieval_mode"], "fts_first")
        self.assertIn("fts", result.diagnostics["strategies_used"])
        self.assertEqual(result.diagnostics["strategies_used"], ["fts"])
        self.assertEqual(result.diagnostics["query_scope"], "vault")
        self.assertEqual(result.diagnostics["query_intent"], "lookup")
        self.assertGreaterEqual(result.diagnostics["candidate_doc_count"], 0)
        self.assertGreaterEqual(result.diagnostics["fts_shortlist_count"], 0)

    def test_retrieve_auto_emits_stable_query_fingerprint(self) -> None:
        query = RetrievalQuery(
            query_text="discussion theory",
            scope="doc:doc-pdf-1",
            intent="outline_support",
            constraints=RetrievalConstraints(max_results=6, section_hint="discussion"),
            confidentiality_profile="confidential",
        )
        first = self.service.retrieve_auto(query)
        second = self.service.retrieve_auto(query)
        first_fingerprint = first.diagnostics["query_fingerprint"]
        self.assertEqual(first_fingerprint, second.diagnostics["query_fingerprint"])
        self.assertEqual(first_fingerprint, first.hits[0].provenance["query_fingerprint"])
        self.assertEqual(first_fingerprint, first.doc_hits[0].provenance["query_fingerprint"])
        self.assertEqual(first.hits[0].provenance["excerpt_fingerprint"], second.hits[0].provenance["excerpt_fingerprint"])
        self.assertEqual(first.doc_hits[0].provenance["doc_fingerprint"], second.doc_hits[0].provenance["doc_fingerprint"])

        variant = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="discussion theory",
                scope="doc:doc-pdf-1",
                intent="outline_support",
                constraints=RetrievalConstraints(max_results=6, section_hint="discussion", prefer_exact_matches=True),
                confidentiality_profile="confidential",
            )
        )
        self.assertNotEqual(first_fingerprint, variant.diagnostics["query_fingerprint"])

    def test_fts_returns_excerpt_hits_with_deterministic_provenance(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="discussion theory",
                scope="doc:doc-pdf-1",
                intent="outline_support",
                constraints=RetrievalConstraints(max_results=6, section_hint="discussion"),
                confidentiality_profile="confidential",
            )
        )
        self.assertEqual(result.diagnostics["strategies_used"], ["fts"])
        self.assertEqual(result.diagnostics["retrieval_backend"], "sqlite_fts")
        for index, hit in enumerate(result.hits, start=1):
            self.assertIsNotNone(hit.excerpt_id)
            self.assertEqual(hit.source_strategy, "fts")
            self.assertIsNotNone(hit.excerpt_text)
            self.assertIn("char_range", hit.span)
            self.assertEqual(hit.provenance["doc_id"], hit.doc_id)
            self.assertEqual(hit.provenance["excerpt_id"], hit.excerpt_id)
            self.assertEqual(hit.provenance["source_strategy"], "fts")
            self.assertEqual(hit.provenance["rank"], index)
            self.assertIn("fts_rank", hit.provenance)
            self.assertEqual(hit.provenance["query_scope"], "doc:doc-pdf-1")
            self.assertEqual(hit.provenance["query_intent"], "outline_support")
            self.assertEqual(hit.provenance["query_fingerprint"], result.diagnostics["query_fingerprint"])
            self.assertIn("candidate_doc_count", hit.provenance)
            self.assertIn("excerpt_fingerprint", hit.provenance)
            self.assertIsInstance(hit.provenance["matched_terms"], list)
            self.assertEqual(hit.provenance["match_count"], len(hit.provenance["matched_terms"]))
            self.assertTrue(hit.provenance["matched_terms"])

    def test_doc_scope_falls_back_to_fts_when_pageindex_missing(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="coding comparison",
                scope="doc:doc-memo-1",
                intent="lookup",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )
        self.assertTrue(result.hits)
        self.assertEqual({hit.source_strategy for hit in result.hits}, {"fts"})

    def test_section_scope_is_rejected_until_pageindex_can_resolve_it(self) -> None:
        with self.assertRaisesRegex(ValueError, "section scope is unsupported"):
            self.service.retrieve_auto(
                RetrievalQuery(
                    query_text="discussion theory",
                    scope="section:discussion",
                    intent="lookup",
                    constraints=RetrievalConstraints(max_results=4, section_hint="discussion"),
                    confidentiality_profile="confidential",
                )
            )

    def test_retrieve_auto_returns_stable_doc_hits_for_downstream_consumers(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )
        self.assertTrue(result.doc_hits)
        doc_hit = next(item for item in result.doc_hits if item.doc_id == "doc-memo-1")
        self.assertEqual(doc_hit.source_strategy, "fts")
        self.assertTrue(doc_hit.source_hash)
        self.assertIsNotNone(doc_hit.top_excerpt_id)
        self.assertGreaterEqual(doc_hit.excerpt_count, 1)
        self.assertEqual(doc_hit.provenance["doc_id"], doc_hit.doc_id)
        self.assertEqual(doc_hit.provenance["top_excerpt_id"], doc_hit.top_excerpt_id)
        self.assertIn("top_excerpt_hash", doc_hit.provenance)
        self.assertIn("top_excerpt_fingerprint", doc_hit.provenance)
        self.assertIn("top_excerpt_span", doc_hit.provenance)
        self.assertIn("top_matched_terms", doc_hit.provenance)
        self.assertIn("top_match_count", doc_hit.provenance)
        self.assertEqual(doc_hit.provenance["doc_type"], "memo")
        self.assertIn("doc_fingerprint", doc_hit.provenance)
        self.assertEqual(doc_hit.provenance["source_strategy"], "fts")
        self.assertEqual(doc_hit.provenance["retrieval_mode"], "fts_first")
        self.assertEqual(doc_hit.provenance["query_scope"], "vault")
        self.assertEqual(doc_hit.provenance["query_intent"], "compare")
        self.assertEqual(doc_hit.provenance["query_fingerprint"], result.diagnostics["query_fingerprint"])
        self.assertIn("top_fts_rank", doc_hit.provenance)
        self.assertEqual(result.diagnostics["doc_hits_count"], len(result.doc_hits))
        self.assertEqual(result.diagnostics["excerpt_hits_count"], len(result.hits))

    def test_doc_hits_follow_top_ranked_excerpt_order(self) -> None:
        self.service.add_or_update_document(
            doc_id="doc-memo-2",
            doc_type="memo",
            title_hint="Memo Beta",
            text="coding comparison",
        )
        self.service.add_or_update_document(
            doc_id="doc-memo-3",
            doc_type="memo",
            title_hint="Memo Gamma",
            text="memo comparison",
        )

        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="coding comparison memo alpha",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=6),
                confidentiality_profile="confidential",
            )
        )

        self.assertGreaterEqual(len(result.doc_hits), 2)
        self.assertEqual(result.doc_hits[0].doc_id, result.hits[0].doc_id)
        self.assertEqual(result.doc_hits[0].top_excerpt_id, result.hits[0].excerpt_id)
        self.assertEqual(result.doc_hits[0].provenance["top_excerpt_rank"], 1)
        self.assertEqual(result.doc_hits[0].provenance["doc_rank"], 1)
        self.assertIn("doc_fingerprint", result.doc_hits[0].provenance)
        ordered_doc_ids = []
        seen_doc_ids = set()
        for hit in result.hits:
            if hit.doc_id in seen_doc_ids:
                continue
            seen_doc_ids.add(hit.doc_id)
            ordered_doc_ids.append(hit.doc_id)
        self.assertEqual([doc_hit.doc_id for doc_hit in result.doc_hits], ordered_doc_ids)

    def test_retrieval_service_fetches_fts_excerpt_ids(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="discussion theory",
                scope="doc:doc-pdf-1",
                intent="lookup",
                constraints=RetrievalConstraints(max_results=3),
                confidentiality_profile="confidential",
            )
        )

        excerpt_id = result.hits[0].excerpt_id
        self.assertIsNotNone(excerpt_id)
        excerpt = self.service.fetch_excerpt(excerpt_id or "")
        self.assertEqual(excerpt["excerpt_id"], excerpt_id)
        self.assertEqual(excerpt["doc_id"], result.hits[0].doc_id)
        self.assertEqual(excerpt["span"], result.hits[0].span)
        self.assertEqual(excerpt["source_strategy"], "fts")
        self.assertEqual(excerpt["retrieval_backend"], "sqlite_fts")
        self.assertEqual(excerpt["retrieval_mode"], "fts_first")
        self.assertEqual(excerpt["source_hash"], result.hits[0].provenance["source_hash"])
        self.assertEqual(excerpt["text_hash"], result.hits[0].provenance["excerpt_text_hash"])
        self.assertEqual(excerpt["provenance"]["source_strategy"], "fts")
        self.assertEqual(excerpt["provenance"]["retrieval_backend"], "sqlite_fts")
        self.assertEqual(excerpt["provenance"]["retrieval_mode"], "fts_first")
        self.assertEqual(excerpt["provenance"]["hash"], result.hits[0].provenance["hash"])
        self.assertEqual(excerpt["provenance"]["excerpt_fingerprint"], result.hits[0].provenance["excerpt_fingerprint"])
        self.assertTrue(excerpt["text"])

    def test_retrieval_service_normalizes_pageindex_excerpt_payloads(self) -> None:
        query_result = self.service._docindex.query(
            "doc-pdf-1",
            self.service._read_doc_text("doc-pdf-1").encode("utf-8"),
            "theory",
            DocIndexQueryConstraints(max_results=1),
            options=DocIndexBuildOptions(),
        )
        self.assertTrue(query_result.hits)
        excerpt_ids = query_result.hits[0]["excerpt_ids"]
        self.assertTrue(excerpt_ids)

        excerpt = self.service.fetch_excerpt(str(excerpt_ids[0]))
        self.assertEqual(excerpt["source_strategy"], "pageindex")
        self.assertEqual(excerpt["doc_id"], "doc-pdf-1")
        self.assertIn("span", excerpt)
        self.assertIn("text_hash", excerpt)
        self.assertEqual(excerpt["provenance"]["source_strategy"], "pageindex")
        self.assertEqual(excerpt["provenance"]["doc_id"], "doc-pdf-1")

    def test_pageindex_strategy_is_deferred_for_fts_first_mvp(self) -> None:
        strategy = PageIndexStrategy(self.service._docindex, self.service._read_doc_text)
        query = RetrievalQuery(
            query_text="discussion theory",
            scope="vault",
            intent="lookup",
            constraints=RetrievalConstraints(max_results=4),
            confidentiality_profile="confidential",
        )
        self.assertFalse(strategy.supports(query))
        run = strategy.retrieve(query, candidate_doc_ids=("doc-pdf-1",))
        self.assertEqual(run.strategy_id, "pageindex")
        self.assertEqual(run.hits, [])
        self.assertEqual(run.elapsed_ms, 0)

    def test_engine_retrieval_package_exports_are_fts_only(self) -> None:
        self.assertEqual(
            engine_retrieval.__all__,
            ["StrategyRun", "RetrievalStrategy", "FTSStrategy"],
        )
        self.assertTrue(hasattr(engine_retrieval, "FTSStrategy"))
        self.assertFalse(hasattr(engine_retrieval, "PageIndexStrategy"))
        self.assertFalse(hasattr(engine_retrieval, "EmbeddingsStrategy"))

    def test_retrieval_audit_uses_query_hash_not_plaintext(self) -> None:
        query_text = "highly sensitive question text"
        self.service.retrieve_auto(
            RetrievalQuery(
                query_text=query_text,
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=3),
                confidentiality_profile="confidential",
            )
        )
        payload = (self.root / "audit_events.jsonl").read_text(encoding="utf-8")
        self.assertIn("retrieval_executed", payload)
        self.assertNotIn(query_text, payload)
        lines = [json.loads(line) for line in payload.splitlines()]
        event = next(item for item in lines if item["name"] == "retrieval_executed")
        self.assertIn("query_hash", event["metadata"])
        self.assertIn("query_fingerprint", event["metadata"])
        self.assertIn("strategies_used", event["metadata"])
        self.assertIn("elapsed_ms_by_strategy", event["metadata"])


if __name__ == "__main__":
    unittest.main()
