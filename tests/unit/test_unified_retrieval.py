from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from typing import cast, get_args, get_type_hints

from src.qual.audit import AuditLog
from src.qual.docindex.service import DocIndexBuildOptions
from src.qual.docindex.service import DocIndexQueryConstraints
from src.qual.docindex.service import DocIndexService
import src.qual.engine.retrieval as engine_retrieval
from src.qual.engine.retrieval import build_retrieval_citation_bundle_from_result as engine_build_retrieval_citation_bundle_from_result
from src.qual.engine.retrieval import build_retrieval_doc_bundle_from_result as engine_build_retrieval_doc_bundle_from_result
from src.qual.engine.retrieval import build_retrieval_context_bundle_from_result as engine_build_retrieval_context_bundle_from_result
from src.qual.engine.retrieval import build_retrieval_downstream_payload_from_result as engine_build_retrieval_downstream_payload_from_result
from src.qual.engine.retrieval import build_retrieval_provenance_from_result as engine_build_retrieval_provenance_from_result
from src.qual.engine.retrieval import build_retrieval_source_bundle_from_result as engine_build_retrieval_source_bundle_from_result
from src.qual.engine.retrieval.payload import build_retrieval_citation_bundle_from_result
from src.qual.engine.retrieval.payload import build_retrieval_downstream_payload_from_result
from src.qual.engine.retrieval.payload import build_retrieval_provenance_from_result
from src.qual.engine.retrieval.payload import _build_retrieval_basket_promotion_bundle_from_payload
from src.qual.engine.retrieval.payload import _build_retrieval_doc_bundle_from_payload
from src.qual.engine.retrieval.payload import _build_retrieval_excerpt_bundle_from_payload
from src.qual.engine.retrieval.payload import _build_retrieval_source_bundle_from_payload
from src.qual.engine.retrieval.payload import _build_retrieval_provenance_from_payload
import src.qual.retrieval as package_retrieval
from src.qual.retrieval import retrieve_auto as engine_retrieve_auto
from src.qual.retrieval import retrieve_auto_basket_promotion_bundle as engine_retrieve_auto_basket_promotion_bundle
from src.qual.retrieval import retrieve_auto_citation_bundle as engine_retrieve_auto_citation_bundle
from src.qual.retrieval import retrieve_auto_doc_bundle as engine_retrieve_auto_doc_bundle
from src.qual.retrieval import retrieve_auto_payload as engine_retrieve_auto_payload
from src.qual.retrieval import retrieve_auto_provenance_bundle as engine_retrieve_auto_provenance_bundle
from src.qual.retrieval import retrieve_auto_source_bundle as engine_retrieve_auto_source_bundle
from src.qual.retrieval import retrieve_fts as engine_retrieve_fts
from src.qual.retrieval import retrieve_fts_basket_promotion_bundle as engine_retrieve_fts_basket_promotion_bundle
from src.qual.retrieval import retrieve_fts_doc_bundle as engine_retrieve_fts_doc_bundle
from src.qual.retrieval import retrieve_fts_excerpt as engine_retrieve_fts_excerpt
from src.qual.retrieval import retrieve_fts_payload as engine_retrieve_fts_payload
from src.qual.retrieval import retrieve_fts_provenance_bundle as engine_retrieve_fts_provenance_bundle
from src.qual.retrieval import retrieve_fts_source_bundle as engine_retrieve_fts_source_bundle
from src.qual.retrieval.service import RetrievalConstraints, RetrievalQuery, RetrievalService
from src.qual.retrieval.service import RetrievalDocHit
from src.qual.retrieval.service import RetrievalHit


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
        self.assertEqual(result.diagnostics["active_strategy_ids"], ["fts"])
        self.assertIn("fts", result.diagnostics["strategies_used"])
        self.assertEqual(result.diagnostics["strategies_used"], ["fts"])
        self.assertEqual(result.diagnostics["query_scope"], "vault")
        self.assertEqual(result.diagnostics["query_intent"], "lookup")
        self.assertGreaterEqual(result.diagnostics["candidate_doc_count"], 0)
        self.assertGreaterEqual(result.diagnostics["fts_shortlist_count"], 0)
        self.assertIsInstance(result.diagnostics["fts_shortlist_doc_ids"], list)

    def test_retrieve_fts_is_the_canonical_entrypoint(self) -> None:
        query = RetrievalQuery(
            query_text="theory implications",
            scope="vault",
            intent="lookup",
            constraints=RetrievalConstraints(max_results=5),
            confidentiality_profile="confidential",
        )

        direct = self.service.retrieve_fts(query)
        auto = self.service.retrieve_auto(query)

        direct_payload = direct.to_downstream_payload()
        auto_payload = auto.to_downstream_payload()
        direct_payload.pop("audit_ref")
        auto_payload.pop("audit_ref")
        direct_payload["retrieval_diagnostics"].pop("elapsed_ms_total", None)
        auto_payload["retrieval_diagnostics"].pop("elapsed_ms_total", None)
        direct_payload["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)
        auto_payload["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)
        self.assertEqual(direct_payload, auto_payload)
        self.assertEqual(direct.result_fingerprint, auto.result_fingerprint)
        self.assertEqual(direct.diagnostics["retrieval_backend"], "sqlite_fts")
        self.assertEqual(direct.diagnostics["retrieval_mode"], "fts_first")

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
        self.assertEqual(first.result_fingerprint, second.result_fingerprint)

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
        self.assertNotEqual(first.result_fingerprint, variant.result_fingerprint)

    def test_retrieve_auto_normalizes_whitespace_in_query_fingerprint(self) -> None:
        compact = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="discussion theory",
                scope="doc:doc-pdf-1",
                intent="outline_support",
                constraints=RetrievalConstraints(max_results=6, section_hint="discussion", prefer_exact_matches=True),
                confidentiality_profile="confidential",
            )
        )
        spaced = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="  discussion   theory  ",
                scope="doc:doc-pdf-1",
                intent="outline_support",
                constraints=RetrievalConstraints(max_results=6, section_hint="discussion", prefer_exact_matches=True),
                confidentiality_profile="confidential",
            )
        )
        self.assertEqual(compact.diagnostics["query_fingerprint"], spaced.diagnostics["query_fingerprint"])
        self.assertEqual([hit.excerpt_id for hit in compact.hits], [hit.excerpt_id for hit in spaced.hits])
        self.assertEqual(compact.result_fingerprint, spaced.result_fingerprint)

    def test_retrieve_auto_normalizes_section_hint_in_query_fingerprint(self) -> None:
        compact = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="discussion theory",
                scope="doc:doc-pdf-1",
                intent="outline_support",
                constraints=RetrievalConstraints(max_results=6, section_hint="discussion"),
                confidentiality_profile="confidential",
            )
        )
        spaced = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="discussion theory",
                scope="doc:doc-pdf-1",
                intent="outline_support",
                constraints=RetrievalConstraints(max_results=6, section_hint="  discussion  "),
                confidentiality_profile="confidential",
            )
        )
        self.assertEqual(compact.diagnostics["query_fingerprint"], spaced.diagnostics["query_fingerprint"])
        self.assertEqual(compact.result_fingerprint, spaced.result_fingerprint)
        self.assertEqual(compact.query.constraints.section_hint, "discussion")
        self.assertEqual(spaced.query.constraints.section_hint, "discussion")
        self.assertEqual(compact.to_downstream_payload()["query"]["constraints"]["section_hint"], "discussion")
        self.assertEqual(spaced.to_downstream_payload()["query"]["constraints"]["section_hint"], "discussion")

    def test_retrieve_auto_reports_stable_fts_shortlist_doc_ids(self) -> None:
        query = RetrievalQuery(
            query_text="theory implications",
            scope="vault",
            intent="lookup",
            constraints=RetrievalConstraints(max_results=5),
            confidentiality_profile="confidential",
        )
        first = self.service.retrieve_auto(query)
        second = self.service.retrieve_auto(query)
        self.assertEqual(first.diagnostics["fts_shortlist_doc_ids"], second.diagnostics["fts_shortlist_doc_ids"])
        self.assertIn("doc-pdf-1", first.diagnostics["fts_shortlist_doc_ids"])

    def test_retrieve_auto_records_cache_use_in_diagnostics_and_audit(self) -> None:
        query = RetrievalQuery(
            query_text="theory implications",
            scope="doc:doc-pdf-1",
            intent="lookup",
            constraints=RetrievalConstraints(max_results=5),
            confidentiality_profile="confidential",
        )
        first = self.service.retrieve_auto(query)
        second = self.service.retrieve_auto(query)

        self.assertEqual(first.diagnostics["caches_used"], {"fts": False})
        self.assertEqual(second.diagnostics["caches_used"], {"fts": True})
        self.assertEqual(first.result_fingerprint, second.result_fingerprint)

        payload = second.to_downstream_payload()
        self.assertEqual(payload["retrieval_diagnostics"]["caches_used"], {"fts": True})
        audit_events = [
            json.loads(line)
            for line in (self.root / "audit_events.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        retrieval_events = [event for event in audit_events if event["name"] == "retrieval_executed"]
        self.assertEqual(retrieval_events[-1]["metadata"]["caches_used"], {"fts": True})

    def test_fts_strategy_cache_uses_stable_query_snapshots(self) -> None:
        calls: list[tuple[object, tuple[str, ...]]] = []

        class QueryShape:
            def __init__(self, *, query_text: str, constraints: dict[str, object]) -> None:
                self.query_text = query_text
                self.constraints = constraints

        def runner(query: object, candidate_doc_ids: tuple[str, ...]) -> list[dict[str, object]]:
            calls.append((query, candidate_doc_ids))
            return [{"doc_id": "doc-pdf-1", "query_text": getattr(query, "query_text")}]

        strategy = engine_retrieval.FTSStrategy(runner)
        first_query = QueryShape(
            query_text="theory implications",
            constraints={"doc_types": ["pdf"], "max_results": 5},
        )
        second_query = QueryShape(
            query_text="theory implications",
            constraints={"max_results": 5, "doc_types": ["pdf"]},
        )

        first = strategy.retrieve(first_query, candidate_doc_ids=("doc-pdf-1",))
        first_query.constraints["doc_types"].append("memo")
        second = strategy.retrieve(second_query, candidate_doc_ids=("doc-pdf-1",))

        self.assertFalse(first.cache_used)
        self.assertTrue(second.cache_used)
        self.assertEqual(len(calls), 1)
        self.assertEqual(second.hits, first.hits)

    def test_retrieval_hits_reject_non_fts_source_strategies(self) -> None:
        with self.assertRaisesRegex(ValueError, "source_strategy must be fts"):
            RetrievalHit(
                doc_id="doc-1",
                excerpt_id="excerpt-1",
                excerpt_text="excerpt text",
                span={"char_range": {"start": 0, "end": 12}},
                title_hint="Title",
                score=1.0,
                source_strategy="pageindex",
                rationale="unsupported",
                node_path=None,
                provenance={},
            )

        with self.assertRaisesRegex(ValueError, "source_strategy must be fts"):
            RetrievalDocHit(
                doc_id="doc-1",
                title_hint="Title",
                source_hash="hash",
                top_excerpt_id="excerpt-1",
                top_score=1.0,
                source_strategy="embeddings",
                excerpt_count=1,
                provenance={},
            )

    def test_retrieve_auto_canonicalizes_doc_type_filters_in_fingerprints(self) -> None:
        first = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4, doc_types=("Memo", "pdf")),
                confidentiality_profile="confidential",
            )
        )
        second = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4, doc_types=("pdf", "memo", "PDF")),
                confidentiality_profile="confidential",
            )
        )
        self.assertEqual(first.diagnostics["query_fingerprint"], second.diagnostics["query_fingerprint"])
        self.assertEqual(first.diagnostics["retrieval_manifest"], second.diagnostics["retrieval_manifest"])
        self.assertEqual([hit.doc_id for hit in first.hits], [hit.doc_id for hit in second.hits])

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
            hit_payload = hit.as_dict()
            self.assertEqual(hit_payload["excerpt_fingerprint"], hit.provenance["excerpt_fingerprint"])
            self.assertEqual(hit_payload["excerpt_text_hash"], hit.provenance["excerpt_text_hash"])
            self.assertEqual(hit_payload["rank"], hit.provenance["rank"])
            self.assertEqual(hit_payload["match_count"], hit.provenance["match_count"])
            self.assertEqual(hit_payload["matched_terms"], hit.provenance["matched_terms"])

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

    def test_empty_prefixed_scopes_fail_closed_before_fts_execution(self) -> None:
        for scope, message in (
            ("doc:", "doc scope id must be non-empty"),
            ("doc:   ", "doc scope id must be non-empty"),
            ("collection:", "collection scope id must be non-empty"),
            ("collection:   ", "collection scope id must be non-empty"),
        ):
            with self.subTest(scope=scope):
                with self.assertRaisesRegex(ValueError, message):
                    self.service.retrieve_auto(
                        RetrievalQuery(
                            query_text="discussion theory",
                            scope=scope,
                            intent="lookup",
                            constraints=RetrievalConstraints(max_results=4),
                            confidentiality_profile="confidential",
                        )
                    )

    def test_retrieve_auto_rejects_invalid_date_range_constraints(self) -> None:
        for date_range, message in (
            (("not-a-date", "2026-01-31"), "date_range values must be ISO dates or datetimes"),
            (("2026-02-01", "2026-01-31"), "date_range start must be on or before end"),
        ):
            with self.subTest(date_range=date_range):
                with self.assertRaisesRegex(ValueError, message):
                    self.service.retrieve_auto(
                        RetrievalQuery(
                            query_text="discussion theory",
                            scope="vault",
                            intent="lookup",
                            constraints=RetrievalConstraints(max_results=4, date_range=date_range),
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
        self.assertIn("doc_identity_fingerprint", doc_hit.provenance)
        self.assertIn("doc_fingerprint", doc_hit.provenance)
        self.assertEqual(doc_hit.provenance["source_strategy"], "fts")
        self.assertEqual(doc_hit.provenance["retrieval_mode"], "fts_first")
        self.assertEqual(doc_hit.provenance["query_scope"], "vault")
        self.assertEqual(doc_hit.provenance["query_intent"], "compare")
        self.assertEqual(doc_hit.provenance["query_fingerprint"], result.diagnostics["query_fingerprint"])
        self.assertIn("top_fts_rank", doc_hit.provenance)
        doc_hit_payload = doc_hit.as_dict()
        self.assertEqual(doc_hit_payload["doc_fingerprint"], doc_hit.provenance["doc_fingerprint"])
        self.assertEqual(doc_hit_payload["doc_identity_fingerprint"], doc_hit.provenance["doc_identity_fingerprint"])
        self.assertEqual(doc_hit_payload["top_excerpt_fingerprint"], doc_hit.provenance["top_excerpt_fingerprint"])
        self.assertEqual(doc_hit_payload["top_excerpt_text_hash"], doc_hit.provenance["top_excerpt_text_hash"])
        self.assertEqual(doc_hit_payload["top_excerpt_rank"], doc_hit.provenance["top_excerpt_rank"])
        self.assertEqual(doc_hit_payload["source_hash"], doc_hit.source_hash)
        self.assertEqual(result.diagnostics["doc_hits_count"], len(result.doc_hits))
        self.assertEqual(result.diagnostics["excerpt_hits_count"], len(result.hits))
        manifest = result.diagnostics["retrieval_manifest"]
        self.assertEqual(manifest["doc_ids"], [item.doc_id for item in result.doc_hits])
        self.assertEqual(manifest["doc_fingerprints"], [item.provenance["doc_fingerprint"] for item in result.doc_hits])
        self.assertEqual(
            manifest["doc_identity_fingerprints"],
            [item.provenance["doc_identity_fingerprint"] for item in result.doc_hits],
        )
        self.assertEqual(manifest["top_excerpt_ids"], [item.top_excerpt_id for item in result.doc_hits])
        self.assertEqual(
            manifest["top_excerpt_text_hashes"],
            [item.provenance["top_excerpt_text_hash"] for item in result.doc_hits],
        )
        self.assertEqual(manifest["excerpt_ids"], [item.excerpt_id for item in result.hits if item.excerpt_id is not None])
        self.assertEqual(
            manifest["excerpt_text_hashes"],
            [
                item.provenance["excerpt_text_hash"]
                for item in result.hits
                if item.excerpt_id is not None
            ],
        )
        self.assertIn("top_excerpt_text_hashes", manifest)
        self.assertIn("excerpt_text_hashes", manifest)

    def test_downstream_payload_exposes_policy_and_diagnostics_snapshot(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        payload = result.to_downstream_payload()
        expected_constraints_fingerprint = hashlib.sha256(
            json.dumps(
                payload["query"]["constraints"],
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(payload["policy"], payload["retrieval_policy"])
        self.assertEqual(payload["retrieval_policy"]["retrieval_backend"], "sqlite_fts")
        self.assertEqual(payload["retrieval_policy"]["retrieval_mode"], "fts_first")
        self.assertEqual(payload["retrieval_policy"]["active_strategy_ids"], ["fts"])
        self.assertEqual(payload["retrieval_policy"]["deferred_strategy_ids"], ["pageindex", "embeddings"])
        self.assertEqual(payload["retrieval_summary"]["query_fingerprint"], result.diagnostics["query_fingerprint"])
        self.assertEqual(payload["retrieval_summary"]["result_fingerprint"], result.result_fingerprint)
        self.assertEqual(payload["retrieval_summary"]["retrieval_backend"], "sqlite_fts")
        self.assertEqual(payload["retrieval_summary"]["retrieval_mode"], "fts_first")
        self.assertEqual(payload["retrieval_summary"]["doc_count"], len(result.doc_hits))
        self.assertEqual(payload["retrieval_summary"]["excerpt_count"], len(result.hits))
        self.assertEqual(payload["retrieval_summary"]["doc_ids"], [item.doc_id for item in result.doc_hits])
        self.assertEqual(
            payload["retrieval_summary"]["excerpt_ids"],
            [item.excerpt_id for item in result.hits if item.excerpt_id is not None],
        )
        self.assertEqual(
            payload["retrieval_summary"]["primary_doc_id"],
            result.doc_hits[0].doc_id if result.doc_hits else None,
        )
        self.assertEqual(
            payload["retrieval_summary"]["primary_excerpt_id"],
            result.hits[0].excerpt_id if result.hits else None,
        )
        self.assertEqual(payload["retrieval_diagnostics"]["result_fingerprint"], result.result_fingerprint)
        self.assertEqual(payload["retrieval_diagnostics"]["query_constraints_fingerprint"], expected_constraints_fingerprint)
        self.assertEqual(payload["retrieval_diagnostics"]["retrieval_manifest"], result.diagnostics["retrieval_manifest"])
        self.assertEqual(payload["retrieval_diagnostics"]["retrieval_evidence"], result.diagnostics["retrieval_evidence"])
        self.assertEqual(payload["retrieval_manifest"], result.diagnostics["retrieval_manifest"])
        self.assertEqual(payload["retrieval_evidence"], result.evidence)
        evidence_for_fingerprint = dict(payload["retrieval_evidence"])
        retrieval_evidence_fingerprint = evidence_for_fingerprint.pop("retrieval_evidence_fingerprint")
        self.assertEqual(
            retrieval_evidence_fingerprint,
            hashlib.sha256(
                json.dumps(
                    evidence_for_fingerprint,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=True,
                ).encode("utf-8")
            ).hexdigest(),
        )
        self.assertEqual(
            payload["retrieval_diagnostics"]["retrieval_evidence_fingerprint"],
            retrieval_evidence_fingerprint,
        )
        self.assertEqual(
            payload["retrieval_summary"]["retrieval_evidence_fingerprint"],
            retrieval_evidence_fingerprint,
        )
        self.assertEqual(
            payload["retrieval_provenance"]["retrieval_evidence_fingerprint"],
            retrieval_evidence_fingerprint,
        )
        self.assertEqual(
            payload["retrieval_source_bundle"]["retrieval_evidence_fingerprint"],
            retrieval_evidence_fingerprint,
        )
        self.assertEqual(payload["retrieval_evidence"]["query_constraints_fingerprint"], expected_constraints_fingerprint)
        self.assertEqual(
            payload["retrieval_citation_bundle"]["query_constraints_fingerprint"],
            expected_constraints_fingerprint,
        )
        self.assertEqual(payload["retrieval_provenance"]["query_constraints_fingerprint"], expected_constraints_fingerprint)
        self.assertEqual(payload["retrieval_source_bundle"]["query_constraints_fingerprint"], expected_constraints_fingerprint)
        self.assertEqual(payload["retrieval_doc_bundle"]["query_constraints_fingerprint"], expected_constraints_fingerprint)
        self.assertEqual(payload["retrieval_excerpt_bundle"]["query_constraints_fingerprint"], expected_constraints_fingerprint)
        self.assertEqual(payload["retrieval_provenance"]["citation_status"], payload["retrieval_summary"]["citation_status"])
        self.assertEqual(payload["retrieval_provenance"]["doc_count"], len(result.doc_hits))
        self.assertEqual(payload["retrieval_provenance"]["excerpt_count"], len(result.hits))
        self.assertEqual(payload["retrieval_evidence"]["citation_status"], payload["retrieval_summary"]["citation_status"])
        self.assertEqual(payload["retrieval_evidence"]["doc_count"], len(result.doc_hits))
        self.assertEqual(payload["retrieval_evidence"]["excerpt_count"], len(result.hits))
        self.assertEqual(payload["retrieval_citation_bundle"]["doc_citations"][0]["source_hash"], result.doc_hits[0].source_hash)
        self.assertEqual(payload["retrieval_doc_bundle"], result.retrieval_doc_bundle())
        self.assertEqual(
            payload["retrieval_citation_bundle"]["excerpt_citations"][0]["source_hash"],
            result.hits[0].provenance["source_hash"],
        )
        self.assertEqual(
            payload["retrieval_evidence"]["excerpt_citations"][0]["source_hash"],
            result.hits[0].provenance["source_hash"],
        )
        self.assertEqual(payload["retrieval_citation_bundle"], result.citation_bundle())
        self.assertEqual(
            payload["retrieval_citation_bundle"]["doc_citations"],
            payload["retrieval_provenance"]["doc_citations"],
        )
        self.assertEqual(
            payload["retrieval_citation_bundle"]["excerpt_citations"],
            payload["retrieval_provenance"]["excerpt_citations"],
        )

    def test_downstream_payload_is_snapshot_safe(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        payload = result.to_downstream_payload()
        payload["retrieval_summary"]["doc_ids"].append("mutated-doc-id")
        payload["doc_hits"][0]["provenance"]["doc_id"] = "mutated-doc-id"

        refreshed = result.to_downstream_payload()
        self.assertNotIn("mutated-doc-id", refreshed["retrieval_summary"]["doc_ids"])
        self.assertNotEqual(refreshed["doc_hits"][0]["provenance"]["doc_id"], "mutated-doc-id")

    def test_retrieval_citation_bundle_helper_is_snapshot_safe(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        bundle = build_retrieval_citation_bundle_from_result(result)
        self.assertEqual(bundle, result.citation_bundle())
        bundle["doc_citations"][0]["doc_id"] = "mutated-doc-id"
        self.assertNotEqual(
            build_retrieval_citation_bundle_from_result(result)["doc_citations"][0]["doc_id"],
            "mutated-doc-id",
        )

    def test_retrieval_result_as_dict_alias_matches_downstream_payload(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        payload = result.as_dict()
        baseline = result.to_downstream_payload()
        self.assertEqual(payload, baseline)
        payload["retrieval_summary"]["doc_ids"].append("mutated-doc-id")
        self.assertNotIn("mutated-doc-id", result.as_dict()["retrieval_summary"]["doc_ids"])

    def test_retrieval_payload_helper_accepts_as_dict_only_sources(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        class _DictOnlySource:
            def __init__(self, payload: dict[str, object]) -> None:
                self._payload = payload

            def as_dict(self) -> dict[str, object]:
                return self._payload

        payload = build_retrieval_downstream_payload_from_result(_DictOnlySource(result.as_dict()))
        self.assertEqual(payload["retrieval_summary"]["doc_ids"], [item.doc_id for item in result.doc_hits])
        payload["retrieval_summary"]["doc_ids"].append("mutated-doc-id")
        self.assertNotIn("mutated-doc-id", build_retrieval_downstream_payload_from_result(_DictOnlySource(result.as_dict()))["retrieval_summary"]["doc_ids"])

    def test_retrieval_source_bundle_helper_accepts_source_bundle_only_sources(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        class _SourceBundleOnlySource:
            def __init__(self, payload: dict[str, object]) -> None:
                self._payload = payload

            def source_bundle(self) -> dict[str, object]:
                return self._payload

        source_bundle = result.source_bundle()
        self.assertEqual(source_bundle["result_fingerprint"], result.result_fingerprint)
        self.assertEqual(source_bundle["query_fingerprint"], result.diagnostics["query_fingerprint"])
        self.assertEqual(source_bundle["retrieval_doc_bundle"], result.retrieval_doc_bundle())
        self.assertEqual(source_bundle["retrieval_excerpt_bundle"], result.retrieval_excerpt_bundle())

        bundle = engine_build_retrieval_source_bundle_from_result(_SourceBundleOnlySource(source_bundle))
        self.assertEqual(bundle["result_fingerprint"], result.result_fingerprint)
        self.assertEqual(bundle["query_fingerprint"], result.diagnostics["query_fingerprint"])
        self.assertEqual(bundle["retrieval_doc_bundle"], result.retrieval_doc_bundle())
        self.assertEqual(bundle["retrieval_excerpt_bundle"], result.retrieval_excerpt_bundle())
        self.assertEqual(bundle["retrieval_summary"]["doc_ids"], [item.doc_id for item in result.doc_hits])
        bundle["retrieval_summary"]["doc_ids"].append("mutated-doc-id")
        refreshed = engine_build_retrieval_source_bundle_from_result(_SourceBundleOnlySource(result.source_bundle()))
        self.assertNotIn("mutated-doc-id", refreshed["retrieval_summary"]["doc_ids"])

    def test_retrieval_source_bundle_payload_helper_accepts_source_bundle_shape(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        payload = result.to_downstream_payload()
        source_bundle = result.source_bundle()
        payload.pop("retrieval_source_bundle", None)
        payload["source_bundle"] = source_bundle

        bundle = _build_retrieval_source_bundle_from_payload(payload)
        self.assertEqual(bundle, source_bundle)
        bundle["retrieval_summary"]["doc_ids"].append("mutated-doc-id")
        self.assertNotIn("mutated-doc-id", _build_retrieval_source_bundle_from_payload(payload)["retrieval_summary"]["doc_ids"])

    def test_retrieval_context_bundle_helper_accepts_source_bundle_only_sources(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        class _SourceBundleOnlySource:
            def __init__(self, payload: dict[str, object]) -> None:
                self._payload = payload

            def source_bundle(self) -> dict[str, object]:
                return self._payload

        source_bundle = result.source_bundle()
        bundle = engine_build_retrieval_context_bundle_from_result(_SourceBundleOnlySource(source_bundle))
        self.assertIsNone(bundle["audit_ref"])
        self.assertEqual(bundle["result_fingerprint"], result.result_fingerprint)
        self.assertEqual(bundle["retrieval_downstream_payload"], source_bundle)
        self.assertEqual(bundle["retrieval_source_bundle"], source_bundle)
        self.assertEqual(bundle["retrieval_citation_bundle"], result.citation_bundle())
        self.assertEqual(bundle["retrieval_doc_bundle"], result.retrieval_doc_bundle())
        self.assertEqual(bundle["retrieval_excerpt_bundle"], result.retrieval_excerpt_bundle())
        bundle["retrieval_downstream_payload"]["retrieval_summary"]["doc_ids"].append("mutated-doc-id")
        bundle["retrieval_excerpt_bundle"]["excerpt_hits"][0]["provenance"]["doc_id"] = "mutated-doc-id"
        refreshed = engine_build_retrieval_context_bundle_from_result(_SourceBundleOnlySource(result.source_bundle()))
        self.assertNotIn("mutated-doc-id", refreshed["retrieval_downstream_payload"]["retrieval_summary"]["doc_ids"])
        self.assertNotEqual(
            refreshed["retrieval_excerpt_bundle"]["excerpt_hits"][0]["provenance"]["doc_id"],
            "mutated-doc-id",
        )

    def test_retrieve_auto_source_bundle_matches_result_snapshot(self) -> None:
        query = RetrievalQuery(
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints=RetrievalConstraints(max_results=4),
            confidentiality_profile="confidential",
        )

        result = self.service.retrieve_auto(query)
        direct = self.service.retrieve_auto_source_bundle(query)
        helper = engine_retrieve_auto_source_bundle(
            self.service,
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints={"max_results": 4},
            confidentiality_profile="confidential",
        )

        self.assertEqual(direct, result.source_bundle())
        self.assertEqual(helper, result.source_bundle())
        self.assertEqual(direct["retrieval_doc_bundle"], result.retrieval_doc_bundle())
        self.assertEqual(direct["retrieval_excerpt_bundle"], result.retrieval_excerpt_bundle())
        self.assertEqual(direct["retrieval_summary"]["doc_ids"], [item.doc_id for item in result.doc_hits])
        self.assertEqual(direct["retrieval_summary"]["excerpt_ids"], [item.excerpt_id for item in result.hits if item.excerpt_id is not None])
        direct["retrieval_summary"]["doc_ids"].append("mutated-doc-id")
        self.assertNotIn("mutated-doc-id", self.service.retrieve_auto_source_bundle(query)["retrieval_summary"]["doc_ids"])

    def test_retrieve_auto_provenance_bundle_matches_result_snapshot(self) -> None:
        query = RetrievalQuery(
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints=RetrievalConstraints(max_results=4),
            confidentiality_profile="confidential",
        )

        result = self.service.retrieve_auto(query)
        direct = self.service.retrieve_auto_provenance_bundle(query)
        helper = engine_retrieve_auto_provenance_bundle(
            self.service,
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints={"max_results": 4},
            confidentiality_profile="confidential",
        )

        self.assertEqual(direct, result.retrieval_provenance_bundle())
        self.assertEqual(helper, result.retrieval_provenance_bundle())
        self.assertEqual(direct["doc_citations"], result.citation_bundle()["doc_citations"])
        self.assertEqual(direct["excerpt_citations"], result.citation_bundle()["excerpt_citations"])
        direct["excerpt_citations"][0]["excerpt_id"] = "mutated-excerpt-id"
        self.assertNotEqual(
            self.service.retrieve_auto_provenance_bundle(query)["excerpt_citations"][0]["excerpt_id"],
            "mutated-excerpt-id",
        )

    def test_retrieve_fts_source_bundle_matches_result_snapshot(self) -> None:
        query = RetrievalQuery(
            query_text="theory implications",
            scope="doc:doc-pdf-1",
            intent="lookup",
            constraints=RetrievalConstraints(max_results=4),
            confidentiality_profile="confidential",
        )

        result = self.service.retrieve_fts(query)
        direct = self.service.retrieve_fts_source_bundle(query)
        helper = engine_retrieve_fts_source_bundle(
            self.service,
            query_text="theory implications",
            scope="doc:doc-pdf-1",
            intent="lookup",
            constraints={"max_results": 4},
            confidentiality_profile="confidential",
        )

        self.assertEqual(direct, result.source_bundle())
        self.assertEqual(helper, result.source_bundle())
        self.assertEqual(direct["retrieval_doc_bundle"], result.retrieval_doc_bundle())
        self.assertEqual(direct["retrieval_excerpt_bundle"], result.retrieval_excerpt_bundle())
        self.assertEqual(direct["retrieval_summary"]["doc_ids"], [item.doc_id for item in result.doc_hits])
        self.assertEqual(direct["retrieval_summary"]["excerpt_ids"], [item.excerpt_id for item in result.hits if item.excerpt_id is not None])
        direct["retrieval_summary"]["doc_ids"].append("mutated-doc-id")
        self.assertNotIn("mutated-doc-id", self.service.retrieve_fts_source_bundle(query)["retrieval_summary"]["doc_ids"])

    def test_retrieve_fts_provenance_bundle_matches_result_snapshot(self) -> None:
        query = RetrievalQuery(
            query_text="theory implications",
            scope="doc:doc-pdf-1",
            intent="lookup",
            constraints=RetrievalConstraints(max_results=4),
            confidentiality_profile="confidential",
        )

        result = self.service.retrieve_fts(query)
        direct = self.service.retrieve_fts_provenance_bundle(query)
        helper = engine_retrieve_fts_provenance_bundle(
            self.service,
            query_text="theory implications",
            scope="doc:doc-pdf-1",
            intent="lookup",
            constraints={"max_results": 4},
            confidentiality_profile="confidential",
        )

        self.assertEqual(direct, result.retrieval_provenance_bundle())
        self.assertEqual(helper, result.retrieval_provenance_bundle())
        self.assertEqual(direct["doc_citations"], result.citation_bundle()["doc_citations"])
        self.assertEqual(direct["excerpt_citations"], result.citation_bundle()["excerpt_citations"])
        direct["doc_citations"][0]["doc_id"] = "mutated-doc-id"
        self.assertNotEqual(
            self.service.retrieve_fts_provenance_bundle(query)["doc_citations"][0]["doc_id"],
            "mutated-doc-id",
        )

    def test_retrieve_fts_citation_bundle_matches_result_snapshot(self) -> None:
        query = RetrievalQuery(
            query_text="theory implications",
            scope="doc:doc-pdf-1",
            intent="lookup",
            constraints=RetrievalConstraints(max_results=4),
            confidentiality_profile="confidential",
        )

        result = self.service.retrieve_fts(query)
        direct = self.service.retrieve_fts_citation_bundle(query)
        helper = engine_retrieval.retrieve_fts_citation_bundle(
            self.service,
            query_text="theory implications",
            scope="doc:doc-pdf-1",
            intent="lookup",
            constraints={"max_results": 4},
            confidentiality_profile="confidential",
        )

        self.assertEqual(direct, result.citation_bundle())
        self.assertEqual(helper, result.citation_bundle())
        self.assertEqual(direct["doc_citations"], result.citation_bundle()["doc_citations"])
        self.assertEqual(direct["excerpt_citations"], result.citation_bundle()["excerpt_citations"])
        direct["doc_citations"][0]["doc_id"] = "mutated-doc-id"
        self.assertNotEqual(
            self.service.retrieve_fts_citation_bundle(query)["doc_citations"][0]["doc_id"],
            "mutated-doc-id",
        )

    def test_retrieve_fts_doc_bundle_matches_result_snapshot(self) -> None:
        query = RetrievalQuery(
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints=RetrievalConstraints(max_results=4),
            confidentiality_profile="confidential",
        )

        result = self.service.retrieve_fts(query)
        direct = self.service.retrieve_fts_doc_bundle(query)
        helper = engine_retrieve_fts_doc_bundle(
            self.service,
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints={"max_results": 4},
            confidentiality_profile="confidential",
        )
        auto_helper = engine_retrieve_auto_doc_bundle(
            self.service,
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints={"max_results": 4},
            confidentiality_profile="confidential",
        )

        self.assertEqual(direct, result.retrieval_doc_bundle())
        self.assertEqual(helper, result.retrieval_doc_bundle())
        self.assertEqual(auto_helper, result.retrieval_doc_bundle())
        self.assertEqual(engine_build_retrieval_doc_bundle_from_result(result), result.retrieval_doc_bundle())
        self.assertEqual(direct["query_scope"], "vault")
        self.assertEqual(direct["query_intent"], "compare")
        self.assertIsNone(direct["query_date_range"])
        self.assertEqual(direct["active_strategy_ids"], ["fts"])
        self.assertEqual(direct["deferred_strategy_ids"], ["pageindex", "embeddings"])
        self.assertEqual(direct["doc_hits"], [item.as_dict() for item in result.doc_hits])
        self.assertEqual(direct["doc_citations"], result.retrieval_doc_bundle()["doc_citations"])
        direct["doc_hits"][0]["provenance"]["doc_id"] = "mutated-doc-id"
        self.assertNotEqual(self.service.retrieve_fts_doc_bundle(query)["doc_hits"][0]["provenance"]["doc_id"], "mutated-doc-id")

    def test_retrieve_auto_excerpt_bundle_surfaces_query_context(self) -> None:
        query = RetrievalQuery(
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints=RetrievalConstraints(max_results=4),
            confidentiality_profile="confidential",
        )

        result = self.service.retrieve_auto(query)
        direct = self.service.retrieve_auto_excerpt_bundle(query)
        helper = engine_retrieval.retrieve_auto_excerpt_bundle(
            self.service,
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints={"max_results": 4},
            confidentiality_profile="confidential",
        )

        self.assertEqual(direct, result.retrieval_excerpt_bundle())
        self.assertEqual(helper, result.retrieval_excerpt_bundle())
        self.assertEqual(direct["query_scope"], "vault")
        self.assertEqual(direct["query_intent"], "compare")
        self.assertIsNone(direct["query_date_range"])
        self.assertEqual(direct["active_strategy_ids"], ["fts"])
        self.assertEqual(direct["deferred_strategy_ids"], ["pageindex", "embeddings"])
        self.assertEqual(direct["excerpt_hits"], [item.as_dict() for item in result.hits])
        self.assertEqual(direct["excerpt_citations"], result.retrieval_excerpt_bundle()["excerpt_citations"])
        direct["excerpt_hits"][0]["provenance"]["doc_id"] = "mutated-doc-id"
        self.assertNotEqual(self.service.retrieve_auto_excerpt_bundle(query)["excerpt_hits"][0]["provenance"]["doc_id"], "mutated-doc-id")

    def test_doc_identity_fingerprint_stays_stable_across_query_variants(self) -> None:
        long_doc_text = (
            "alpha marker opens the first retrieval window. "
            + "filler text " * 60
            + "omega marker closes the second retrieval window. "
            + "filler text " * 60
            + "tail marker for deterministic segmenting."
        )
        self.service.add_or_update_document(
            doc_id="doc-memo-identity",
            doc_type="memo",
            title_hint="Memo Identity",
            text=long_doc_text,
        )
        base = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="alpha marker",
                scope="doc:doc-memo-identity",
                intent="lookup",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )
        variant = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="omega marker",
                scope="doc:doc-memo-identity",
                intent="lookup",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )
        self.assertTrue(base.doc_hits)
        self.assertTrue(variant.doc_hits)
        self.assertEqual(
            base.doc_hits[0].provenance["doc_identity_fingerprint"],
            variant.doc_hits[0].provenance["doc_identity_fingerprint"],
        )
        self.assertNotEqual(
            base.doc_hits[0].provenance["top_excerpt_id"],
            variant.doc_hits[0].provenance["top_excerpt_id"],
        )
        self.assertNotEqual(
            base.doc_hits[0].provenance["top_excerpt_fingerprint"],
            variant.doc_hits[0].provenance["top_excerpt_fingerprint"],
        )
        self.assertNotEqual(
            base.doc_hits[0].provenance["doc_fingerprint"],
            variant.doc_hits[0].provenance["doc_fingerprint"],
        )

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
        self.assertEqual(excerpt["basket_item_id"], f"retrieval:fts:{excerpt_id}")
        self.assertEqual(excerpt["doc_id"], result.hits[0].doc_id)
        self.assertEqual(excerpt["span"], result.hits[0].span)
        self.assertEqual(excerpt["source_strategy"], "fts")
        self.assertEqual(excerpt["retrieval_backend"], "sqlite_fts")
        self.assertEqual(excerpt["retrieval_mode"], "fts_first")
        self.assertEqual(excerpt["retrieval_policy"]["retrieval_backend"], "sqlite_fts")
        self.assertEqual(excerpt["retrieval_policy"]["retrieval_mode"], "fts_first")
        self.assertEqual(excerpt["source_hash"], result.hits[0].provenance["source_hash"])
        self.assertEqual(excerpt["text_hash"], result.hits[0].provenance["excerpt_text_hash"])
        self.assertEqual(excerpt["lookup_fingerprint"], excerpt["provenance"]["lookup_fingerprint"])
        self.assertEqual(excerpt["provenance"]["source_strategy"], "fts")
        self.assertEqual(excerpt["provenance"]["basket_item_id"], f"retrieval:fts:{excerpt_id}")
        self.assertEqual(excerpt["provenance"]["retrieval_backend"], "sqlite_fts")
        self.assertEqual(excerpt["provenance"]["retrieval_mode"], "fts_first")
        self.assertEqual(excerpt["provenance"]["hash"], result.hits[0].provenance["hash"])
        self.assertEqual(excerpt["provenance"]["excerpt_fingerprint"], result.hits[0].provenance["excerpt_fingerprint"])
        self.assertTrue(excerpt["text"])

        fetched_again = self.service.fetch_excerpt(excerpt_id or "")
        self.assertEqual(fetched_again["lookup_fingerprint"], excerpt["lookup_fingerprint"])

        audit_events = [
            json.loads(line)
            for line in (self.root / "audit_events.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        lookup_events = [event for event in audit_events if event["name"] == "excerpt_lookup_completed"]
        self.assertEqual(lookup_events[-1]["metadata"]["lookup_fingerprint"], excerpt["lookup_fingerprint"])

    def test_fetch_excerpt_requires_an_fts_lookup_hit(self) -> None:
        docindex_service = DocIndexService(self.root, audit_log=self.audit)
        doc_id = "doc-pageindex-only"
        source = (
            "# Methods\n"
            "Sampling details and recruitment constraints.\n"
            "# Findings\n"
            "Theme synthesis and implications for theory.\n"
        ).encode("utf-8")
        docindex_service.build(doc_id, source, DocIndexBuildOptions())
        query = docindex_service.query(
            doc_id,
            source,
            "findings synthesis",
            DocIndexQueryConstraints(max_results=1),
            options=DocIndexBuildOptions(),
        )
        excerpt_id = query.hits[0]["excerpt_ids"][0]  # type: ignore[index]

        with self.assertRaisesRegex(KeyError, "unknown excerpt_id"):
            self.service.fetch_excerpt(str(excerpt_id))

    def test_fetch_excerpt_canonicalizes_fts_excerpt_ids(self) -> None:
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
        excerpt = self.service.fetch_excerpt(f"  {excerpt_id}  ")

        self.assertEqual(excerpt["excerpt_id"], excerpt_id)
        self.assertEqual(excerpt["basket_item_id"], f"retrieval:fts:{excerpt_id}")
        self.assertEqual(excerpt["provenance"]["excerpt_id"], excerpt_id)
        self.assertEqual(excerpt["provenance"]["basket_item_id"], f"retrieval:fts:{excerpt_id}")

        with self.assertRaisesRegex(ValueError, "excerpt_id must be non-empty"):
            self.service.fetch_excerpt("   ")

    def test_excerpt_payload_normalization_rejects_pageindex_resolution(self) -> None:
        with self.assertRaisesRegex(ValueError, "canonical FTS strategy"):
            self.service._normalize_excerpt_payload(
                {
                    "excerpt_id": "pageindex-excerpt",
                    "doc_id": "doc-pdf-1",
                    "text": "PageIndex-only excerpt text",
                    "provenance": {"source_strategy": "pageindex"},
                },
                source_strategy="pageindex",  # type: ignore[arg-type]
                lookup_resolution="pageindex",
            )

    def test_retrieve_fts_excerpt_returns_canonical_fts_payload(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        excerpt_id = result.hits[0].excerpt_id
        self.assertIsNotNone(excerpt_id)

        canonical = self.service.retrieve_fts_excerpt(excerpt_id or "")
        alias = self.service.fetch_fts_excerpt(excerpt_id or "")
        helper = engine_retrieval.retrieve_fts_excerpt(
            self.service,
            excerpt_id=excerpt_id or "",
        )
        package_helper = engine_retrieve_fts_excerpt(
            self.service,
            excerpt_id=excerpt_id or "",
        )

        self.assertEqual(canonical, alias)
        self.assertEqual(helper, canonical)
        self.assertEqual(package_helper, canonical)
        self.assertEqual(canonical["source_strategy"], "fts")
        self.assertEqual(canonical["basket_item_id"], f"retrieval:fts:{excerpt_id}")
        self.assertEqual(canonical["retrieval_backend"], "sqlite_fts")
        self.assertEqual(canonical["retrieval_mode"], "fts_first")
        self.assertEqual(canonical["retrieval_policy"]["retrieval_backend"], "sqlite_fts")
        self.assertEqual(canonical["retrieval_policy"]["retrieval_mode"], "fts_first")
        self.assertEqual(canonical["provenance"]["source_strategy"], "fts")
        self.assertEqual(canonical["provenance"]["basket_item_id"], f"retrieval:fts:{excerpt_id}")
        self.assertEqual(canonical["provenance"]["retrieval_backend"], "sqlite_fts")
        self.assertEqual(canonical["provenance"]["retrieval_mode"], "fts_first")
        self.assertEqual(canonical["provenance"]["doc_id"], result.hits[0].doc_id)
        self.assertEqual(canonical["provenance"]["excerpt_fingerprint"], result.hits[0].provenance["excerpt_fingerprint"])
        self.assertEqual(canonical["provenance"]["hash"], result.hits[0].provenance["hash"])
        self.assertEqual(canonical["text_hash"], result.hits[0].provenance["excerpt_text_hash"])

    def test_retrieval_hits_surface_top_level_retrieval_context(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        hit = result.hits[0].as_dict()
        doc_hit = result.doc_hits[0].as_dict()
        self.assertEqual(hit["retrieval_backend"], "sqlite_fts")
        self.assertEqual(hit["retrieval_mode"], "fts_first")
        self.assertEqual(hit["retrieval_policy"]["active_strategy_ids"], ["fts"])
        self.assertEqual(doc_hit["retrieval_backend"], "sqlite_fts")
        self.assertEqual(doc_hit["retrieval_mode"], "fts_first")
        self.assertEqual(doc_hit["retrieval_policy"]["deferred_strategy_ids"], ["pageindex", "embeddings"])

    def test_retrieval_service_rejects_pageindex_excerpt_payloads(self) -> None:
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

        with self.assertRaisesRegex(KeyError, "unknown excerpt_id"):
            self.service.fetch_excerpt(str(excerpt_ids[0]))

    def test_retrieval_payload_helpers_normalize_tuple_shaped_snapshots(self) -> None:
        payload = {
            "query": {
                "query_text": "memo comparison",
                "scope": "vault",
                "intent": "compare",
                "constraints": {
                    "doc_types": ("memo", "pdf"),
                    "date_range": ("2026-01-01", "2026-01-31"),
                },
            },
            "policy": {
                "retrieval_backend": "sqlite_fts",
                "retrieval_mode": "fts_first",
                "active_strategy_ids": ("fts",),
                "deferred_strategy_ids": ("pageindex", "embeddings"),
            },
            "retrieval_backend": "sqlite_fts",
            "retrieval_mode": "fts_first",
            "retrieval_summary": {
                "query_fingerprint": "query-fingerprint",
                "query_scope": "vault",
                "query_intent": "compare",
                "query_date_range": ("2026-01-01", "2026-01-31"),
                "active_strategy_ids": ("fts",),
                "deferred_strategy_ids": ("pageindex", "embeddings"),
                "citation_status": {"required": False, "available": True, "satisfied": True},
                "doc_count": 1,
                "excerpt_count": 1,
            },
            "retrieval_diagnostics": {
                "query_fingerprint": "query-fingerprint",
                "query_scope": "vault",
                "query_intent": "compare",
                "date_range": ("2026-01-01", "2026-01-31"),
                "retrieval_backend": "sqlite_fts",
                "retrieval_mode": "fts_first",
                "active_strategy_ids": ("fts",),
                "deferred_strategy_ids": ("pageindex", "embeddings"),
                "fts_shortlist_doc_ids": ("doc-1", "doc-2"),
            },
            "retrieval_provenance": {
                "query_fingerprint": "query-fingerprint",
                "query_scope": "vault",
                "query_intent": "compare",
                "query_date_range": ("2026-01-01", "2026-01-31"),
                "active_strategy_ids": ("fts",),
                "deferred_strategy_ids": ("pageindex", "embeddings"),
                "fts_shortlist_doc_ids": ("doc-1", "doc-2"),
                "excerpt_citations": (
                    {
                        "doc_id": "doc-1",
                        "excerpt_id": "excerpt-1",
                        "excerpt_fingerprint": "excerpt-fingerprint",
                    },
                ),
            },
            "doc_hits": (
                {"doc_id": "doc-1", "provenance": {"doc_fingerprint": "doc-fingerprint"}},
            ),
            "excerpt_hits": (
                {
                    "doc_id": "doc-1",
                    "excerpt_id": "excerpt-1",
                    "provenance": {"excerpt_fingerprint": "excerpt-fingerprint"},
                },
            ),
        }

        provenance = _build_retrieval_provenance_from_payload(payload)
        source_bundle = _build_retrieval_source_bundle_from_payload(payload)
        excerpt_bundle = _build_retrieval_excerpt_bundle_from_payload(payload)
        expected_constraints_fingerprint = hashlib.sha256(
            json.dumps(
                source_bundle["query"]["constraints"],
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()

        self.assertEqual(provenance["query_date_range"], ["2026-01-01", "2026-01-31"])
        self.assertEqual(provenance["active_strategy_ids"], ["fts"])
        self.assertEqual(provenance["deferred_strategy_ids"], ["pageindex", "embeddings"])
        self.assertEqual(provenance["fts_shortlist_doc_ids"], ["doc-1", "doc-2"])
        self.assertEqual(provenance["query_constraints_fingerprint"], expected_constraints_fingerprint)
        self.assertEqual(source_bundle["query"]["constraints"]["doc_types"], ["memo", "pdf"])
        self.assertEqual(source_bundle["query"]["constraints"]["date_range"], ["2026-01-01", "2026-01-31"])
        self.assertEqual(source_bundle["query_constraints_fingerprint"], expected_constraints_fingerprint)
        self.assertEqual(source_bundle["policy"]["active_strategy_ids"], ["fts"])
        self.assertEqual(source_bundle["policy"]["deferred_strategy_ids"], ["pageindex", "embeddings"])
        self.assertEqual(excerpt_bundle["doc_count"], 1)
        self.assertEqual(excerpt_bundle["excerpt_count"], 1)
        self.assertIsInstance(excerpt_bundle["excerpt_hits"], list)
        self.assertIsInstance(excerpt_bundle["excerpt_citations"], list)
        self.assertEqual(excerpt_bundle["excerpt_hits"][0]["excerpt_id"], "excerpt-1")
        self.assertEqual(excerpt_bundle["excerpt_citations"][0]["excerpt_id"], "excerpt-1")

    def test_engine_retrieval_package_exports_are_fts_only(self) -> None:
        self.assertEqual(
            engine_retrieval.__all__,
            [
                "StrategyRun",
                "RetrievalStrategy",
                "FTSStrategy",
                "FTS_FIRST_POLICY",
                "ACTIVE_STRATEGY_IDS",
                "DEFERRED_STRATEGY_IDS",
                "active_strategy_ids",
                "deferred_strategy_ids",
                "build_retrieval_query",
                "retrieval_policy_snapshot",
                "primary_strategy_id",
                "build_retrieval_downstream_payload",
                "build_retrieval_downstream_payload_from_result",
                "build_retrieval_citation_bundle_from_result",
                "build_retrieval_doc_bundle_from_result",
                "build_retrieval_excerpt_bundle_from_result",
                "build_retrieval_context_bundle_from_result",
                "build_retrieval_provenance_from_result",
                "build_retrieval_source_bundle_from_result",
                "retrieve_fts",
                "retrieve_fts_citation_bundle",
                "retrieve_fts_context_bundle",
                "retrieve_fts_source_bundle",
                "retrieve_fts_provenance_bundle",
                "retrieve_fts_doc_bundle",
                "retrieve_fts_excerpt_bundle",
                "retrieve_fts_basket_promotion_bundle",
                "retrieve_fts_excerpt",
                "fetch_fts_excerpt",
                "retrieve_fts_payload",
                "retrieve_auto",
                "retrieve_auto_context_bundle",
                "retrieve_auto_citation_bundle",
                "retrieve_auto_source_bundle",
                "retrieve_auto_provenance_bundle",
                "retrieve_auto_doc_bundle",
                "retrieve_auto_excerpt_bundle",
                "retrieve_auto_basket_promotion_bundle",
                "retrieve_auto_payload",
            ],
        )
        self.assertTrue(hasattr(package_retrieval, "build_retrieval_query"))
        self.assertTrue(hasattr(engine_retrieval, "build_retrieval_query"))
        self.assertTrue(hasattr(engine_retrieval, "FTSStrategy"))
        self.assertFalse(hasattr(engine_retrieval, "PageIndexStrategy"))
        self.assertFalse(hasattr(engine_retrieval, "EmbeddingsStrategy"))
        self.assertEqual(engine_retrieval.ACTIVE_STRATEGY_IDS, ("fts",))
        self.assertEqual(engine_retrieval.DEFERRED_STRATEGY_IDS, ("pageindex", "embeddings"))
        self.assertEqual(engine_retrieval.active_strategy_ids(), ("fts",))
        self.assertEqual(engine_retrieval.deferred_strategy_ids(), ("pageindex", "embeddings"))
        self.assertEqual(engine_retrieval.primary_strategy_id(), "fts")
        self.assertTrue(hasattr(engine_retrieval, "build_retrieval_downstream_payload"))
        self.assertTrue(hasattr(engine_retrieval, "build_retrieval_downstream_payload_from_result"))
        self.assertTrue(hasattr(engine_retrieval, "build_retrieval_citation_bundle_from_result"))
        self.assertTrue(hasattr(engine_retrieval, "build_retrieval_excerpt_bundle_from_result"))
        self.assertTrue(hasattr(engine_retrieval, "build_retrieval_context_bundle_from_result"))
        self.assertTrue(hasattr(engine_retrieval, "build_retrieval_source_bundle_from_result"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_fts"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_fts_citation_bundle"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_fts_context_bundle"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_auto"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_auto_citation_bundle"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_fts_source_bundle"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_fts_provenance_bundle"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_fts_excerpt_bundle"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_fts_basket_promotion_bundle"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_fts_excerpt"))
        self.assertTrue(hasattr(engine_retrieval, "fetch_fts_excerpt"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_fts_payload"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_auto_context_bundle"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_auto_source_bundle"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_auto_provenance_bundle"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_auto_excerpt_bundle"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_auto_basket_promotion_bundle"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_auto_payload"))
        self.assertTrue(hasattr(package_retrieval, "retrieve_auto_citation_bundle"))

    def test_retrieval_query_constructor_is_shared_by_both_facades(self) -> None:
        constraints = {
            "max_results": 7,
            "doc_types": ["Memo", "pdf", "memo"],
            "date_range": ["2026-01-01", "2026-01-31"],
            "require_citations": True,
            "section_hint": "  discussion  ",
            "prefer_exact_matches": True,
        }

        engine_query = engine_retrieval.build_retrieval_query(
            query_text="memo comparison",
            scope="vault",
            intent="compare",
            constraints=constraints,
            confidentiality_profile="standard",
        )
        package_query = package_retrieval.build_retrieval_query(
            query_text="memo comparison",
            scope="vault",
            intent="compare",
            constraints=constraints,
            confidentiality_profile="standard",
        )

        self.assertEqual(engine_query, package_query)
        self.assertEqual(engine_query.constraints.doc_types, ("memo", "pdf"))
        self.assertEqual(engine_query.constraints.date_range, ("2026-01-01", "2026-01-31"))
        self.assertEqual(engine_query.constraints.section_hint, "discussion")
        self.assertEqual(engine_query.confidentiality_profile, "standard")

    def test_retrieval_query_constructor_accepts_generic_iterable_constraint_values(self) -> None:
        def make_constraints() -> dict[str, object]:
            return {
                "max_results": 7,
                "doc_types": (value for value in ["Memo", "pdf", "memo"]),
                "date_range": (value for value in ["2026-01-01", "2026-01-31"]),
                "require_citations": True,
                "section_hint": "  discussion  ",
                "prefer_exact_matches": True,
            }

        engine_query = engine_retrieval.build_retrieval_query(
            query_text="memo comparison",
            scope="vault",
            intent="compare",
            constraints=make_constraints(),
            confidentiality_profile="standard",
        )
        package_query = package_retrieval.build_retrieval_query(
            query_text="memo comparison",
            scope="vault",
            intent="compare",
            constraints=make_constraints(),
            confidentiality_profile="standard",
        )

        self.assertEqual(engine_query, package_query)
        self.assertEqual(engine_query.constraints.doc_types, ("memo", "pdf"))
        self.assertEqual(engine_query.constraints.date_range, ("2026-01-01", "2026-01-31"))
        self.assertEqual(engine_query.constraints.section_hint, "discussion")
        self.assertEqual(engine_query.confidentiality_profile, "standard")

    def test_retrieval_query_constructor_accepts_constraints_dataclass(self) -> None:
        constraints = RetrievalConstraints(
            max_results=7,
            doc_types=("Memo", "pdf", "memo"),
            date_range=("2026-01-01", "2026-01-31"),
            require_citations=True,
            section_hint="  discussion  ",
            prefer_exact_matches=True,
        )

        engine_query = engine_retrieval.build_retrieval_query(
            query_text="memo comparison",
            scope="vault",
            intent="compare",
            constraints=constraints,
            confidentiality_profile="standard",
        )
        package_query = package_retrieval.build_retrieval_query(
            query_text="memo comparison",
            scope="vault",
            intent="compare",
            constraints=constraints,
            confidentiality_profile="standard",
        )

        self.assertEqual(engine_query, package_query)
        self.assertEqual(engine_query.constraints.doc_types, ("memo", "pdf"))
        self.assertEqual(engine_query.constraints.date_range, ("2026-01-01", "2026-01-31"))
        self.assertEqual(engine_query.constraints.section_hint, "discussion")
        self.assertEqual(engine_query.constraints.require_citations, True)
        self.assertEqual(engine_query.constraints.prefer_exact_matches, True)
        self.assertEqual(engine_query.confidentiality_profile, "standard")

    def test_retrieval_constraints_accept_scalar_doc_type_as_one_filter(self) -> None:
        constraints = RetrievalConstraints(doc_types="Memo")  # type: ignore[arg-type]

        self.assertEqual(constraints.doc_types, ("memo",))

        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo comparison",
                scope="vault",
                intent="compare",
                constraints=constraints,
                confidentiality_profile="confidential",
            )
        )

        self.assertTrue(result.hits)
        self.assertEqual(result.query.constraints.doc_types, ("memo",))
        self.assertEqual(result.diagnostics["retrieval_backend"], "sqlite_fts")
        self.assertEqual(result.diagnostics["retrieval_mode"], "fts_first")

    def test_add_document_canonicalizes_doc_type_before_fts_filtering(self) -> None:
        self.service.add_or_update_document(
            doc_id="doc-spaced-type",
            doc_type=" Memo ",
            title_hint="Spaced Type Memo",
            text="Memo evidence with canonical filter coverage.",
        )

        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="canonical filter",
                scope="vault",
                intent="lookup",
                constraints=RetrievalConstraints(max_results=4, doc_types="memo"),  # type: ignore[arg-type]
                confidentiality_profile="confidential",
            )
        )

        self.assertEqual(result.query.constraints.doc_types, ("memo",))
        self.assertIn("doc-spaced-type", [hit.doc_id for hit in result.hits])
        spaced_hit = next(hit for hit in result.hits if hit.doc_id == "doc-spaced-type")
        self.assertEqual(spaced_hit.provenance["doc_type"], "memo")
        self.assertEqual(spaced_hit.as_dict()["doc_type"], "memo")

    def test_retrieval_query_constructor_rejects_invalid_date_ranges_before_execution(self) -> None:
        for date_range, message in (
            (("not-a-date", "2026-01-31"), "date_range values must be ISO dates or datetimes"),
            (("2026-02-01", "2026-01-31"), "date_range start must be on or before end"),
        ):
            for facade in (engine_retrieval.build_retrieval_query, package_retrieval.build_retrieval_query):
                with self.subTest(date_range=date_range, facade=facade.__module__):
                    with self.assertRaisesRegex(ValueError, message):
                        facade(
                            query_text="memo comparison",
                            scope="vault",
                            intent="compare",
                            constraints={"date_range": date_range},
                            confidentiality_profile="standard",
                        )

    def test_retrieval_package_helpers_accept_constraints_dataclass(self) -> None:
        constraints = RetrievalConstraints(
            max_results=7,
            doc_types=("memo", "pdf"),
            date_range=("2026-01-01", "2026-01-31"),
            section_hint="discussion",
            prefer_exact_matches=True,
        )
        payload_constraints = {
            "max_results": 7,
            "doc_types": ["memo", "pdf"],
            "date_range": ["2026-01-01", "2026-01-31"],
            "section_hint": "discussion",
            "prefer_exact_matches": True,
        }

        for helper in (package_retrieval.retrieve_auto, package_retrieval.retrieve_fts):
            with self.subTest(helper=helper.__name__):
                object_result = helper(
                    self.service,
                    query_text="memo comparison",
                    scope="vault",
                    intent="compare",
                    constraints=constraints,
                    confidentiality_profile="standard",
                )
                payload_result = helper(
                    self.service,
                    query_text="memo comparison",
                    scope="vault",
                    intent="compare",
                    constraints=payload_constraints,
                    confidentiality_profile="standard",
                )

                object_payload = object_result.to_downstream_payload()
                payload_snapshot = payload_result.to_downstream_payload()
                object_payload.pop("audit_ref")
                payload_snapshot.pop("audit_ref")
                object_payload["retrieval_diagnostics"].pop("elapsed_ms_total", None)
                payload_snapshot["retrieval_diagnostics"].pop("elapsed_ms_total", None)
                object_payload["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)
                payload_snapshot["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)
                self.assertEqual(object_payload, payload_snapshot)
                self.assertEqual(object_result.query.constraints, constraints)
                self.assertIn(RetrievalConstraints, get_args(get_type_hints(helper)["constraints"]))

    def test_engine_retrieval_package_reexports_canonical_payload_helpers(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        self.assertEqual(
            engine_build_retrieval_downstream_payload_from_result(result),
            build_retrieval_downstream_payload_from_result(result),
        )
        self.assertEqual(
            engine_build_retrieval_citation_bundle_from_result(result),
            build_retrieval_citation_bundle_from_result(result),
        )
        self.assertEqual(
            engine_build_retrieval_provenance_from_result(result),
            build_retrieval_provenance_from_result(result),
        )
        self.assertEqual(
            engine_build_retrieval_context_bundle_from_result(result),
            result.retrieval_context_bundle(),
        )
        self.assertEqual(
            engine_build_retrieval_provenance_from_result(result),
            result.to_downstream_payload()["retrieval_provenance"],
        )
        self.assertEqual(
            engine_build_retrieval_source_bundle_from_result(result),
            result.source_bundle(),
        )
        fts_context_bundle = engine_retrieval.retrieve_fts_context_bundle(
            self.service,
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints={"max_results": 4, "doc_types": ["memo"]},
            confidentiality_profile="confidential",
        )
        fts_source_bundle = engine_retrieval.retrieve_fts_source_bundle(
            self.service,
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints={"max_results": 4, "doc_types": ["memo"]},
            confidentiality_profile="confidential",
        )
        fts_payload = engine_retrieval.retrieve_fts_payload(
            self.service,
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints={"max_results": 4, "doc_types": ["memo"]},
            confidentiality_profile="confidential",
        )
        auto_context_bundle = engine_retrieval.retrieve_auto_context_bundle(
            self.service,
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints={"max_results": 4, "doc_types": ["memo"]},
            confidentiality_profile="confidential",
        )
        auto_source_bundle = engine_retrieval.retrieve_auto_source_bundle(
            self.service,
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints={"max_results": 4, "doc_types": ["memo"]},
            confidentiality_profile="confidential",
        )
        auto_payload = engine_retrieval.retrieve_auto_payload(
            self.service,
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints={"max_results": 4, "doc_types": ["memo"]},
            confidentiality_profile="confidential",
        )

        def _normalize_payload(payload: dict[str, object]) -> dict[str, object]:
            normalized = json.loads(json.dumps(payload))
            normalized.pop("audit_ref", None)
            diagnostics = normalized.get("retrieval_diagnostics")
            if isinstance(diagnostics, dict):
                diagnostics.pop("elapsed_ms_total", None)
                diagnostics.pop("elapsed_ms_by_strategy", None)
            return normalized

        def _normalize_context_bundle(bundle: dict[str, object]) -> dict[str, object]:
            normalized = json.loads(json.dumps(bundle))
            normalized.pop("audit_ref", None)
            downstream_payload = normalized.get("retrieval_downstream_payload")
            if isinstance(downstream_payload, dict):
                downstream_payload.pop("audit_ref", None)
                diagnostics = downstream_payload.get("retrieval_diagnostics")
                if isinstance(diagnostics, dict):
                    diagnostics.pop("elapsed_ms_total", None)
                    diagnostics.pop("elapsed_ms_by_strategy", None)
            return normalized

        self.assertEqual(_normalize_context_bundle(fts_context_bundle), _normalize_context_bundle(auto_context_bundle))
        self.assertEqual(fts_source_bundle, auto_source_bundle)
        self.assertEqual(fts_source_bundle, self.service.retrieve_fts_source_bundle(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4, doc_types=("memo",)),
                confidentiality_profile="confidential",
            )
        ))
        self.assertEqual(_normalize_payload(fts_payload), _normalize_payload(auto_payload))
        self.assertEqual(_normalize_payload(fts_context_bundle["retrieval_downstream_payload"]), _normalize_payload(fts_payload))
        self.assertEqual(_normalize_payload(auto_context_bundle["retrieval_downstream_payload"]), _normalize_payload(auto_payload))

    def test_retrieval_context_bundle_helper_packages_payload_and_bundles(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        bundle = engine_build_retrieval_context_bundle_from_result(result)
        self.assertEqual(bundle["audit_ref"], result.audit_ref)
        self.assertEqual(bundle["result_fingerprint"], result.result_fingerprint)
        self.assertEqual(bundle["retrieval_downstream_payload"], result.to_downstream_payload())
        self.assertEqual(bundle["retrieval_citation_bundle"], result.citation_bundle())
        self.assertEqual(bundle["retrieval_doc_bundle"], result.retrieval_doc_bundle())
        self.assertEqual(bundle["retrieval_excerpt_bundle"], result.retrieval_excerpt_bundle())
        self.assertEqual(bundle["retrieval_provenance"], result.to_downstream_payload()["retrieval_provenance"])
        self.assertEqual(bundle["retrieval_source_bundle"], result.source_bundle())
        bundle["retrieval_downstream_payload"]["retrieval_summary"]["doc_ids"].append("mutated-doc-id")
        refreshed = engine_build_retrieval_context_bundle_from_result(result)
        self.assertNotIn("mutated-doc-id", refreshed["retrieval_downstream_payload"]["retrieval_summary"]["doc_ids"])
        bundle["retrieval_doc_bundle"]["doc_hits"][0]["provenance"]["doc_id"] = "mutated-doc-id"
        refreshed = engine_build_retrieval_context_bundle_from_result(result)
        self.assertNotEqual(refreshed["retrieval_doc_bundle"]["doc_hits"][0]["provenance"]["doc_id"], "mutated-doc-id")
        bundle["retrieval_excerpt_bundle"]["excerpt_hits"][0]["provenance"]["doc_id"] = "mutated-doc-id"
        refreshed = engine_build_retrieval_context_bundle_from_result(result)
        self.assertNotEqual(
            refreshed["retrieval_excerpt_bundle"]["excerpt_hits"][0]["provenance"]["doc_id"],
            "mutated-doc-id",
        )

    def test_retrieval_context_bundle_helper_reads_generic_sources_once(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        class _CountingDictOnlySource:
            def __init__(self, payload: dict[str, object]) -> None:
                self._payload = payload
                self.as_dict_calls = 0

            def as_dict(self) -> dict[str, object]:
                self.as_dict_calls += 1
                return self._payload

        source = _CountingDictOnlySource(result.as_dict())
        bundle = engine_build_retrieval_context_bundle_from_result(source)

        self.assertEqual(source.as_dict_calls, 1)
        self.assertEqual(bundle["audit_ref"], result.audit_ref)
        self.assertEqual(bundle["retrieval_downstream_payload"]["result_fingerprint"], result.result_fingerprint)
        bundle["retrieval_excerpt_bundle"]["excerpt_hits"][0]["provenance"]["doc_id"] = "mutated-doc-id"
        refreshed = engine_build_retrieval_context_bundle_from_result(source)
        self.assertEqual(source.as_dict_calls, 2)
        self.assertNotEqual(
            refreshed["retrieval_excerpt_bundle"]["excerpt_hits"][0]["provenance"]["doc_id"],
            "mutated-doc-id",
        )

    def test_retrieval_downstream_payload_helper_accepts_source_bundle_only_sources(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        class _SourceBundleOnlySource:
            def __init__(self, payload: dict[str, object]) -> None:
                self._payload = payload

            def source_bundle(self) -> dict[str, object]:
                return self._payload

        payload = build_retrieval_downstream_payload_from_result(_SourceBundleOnlySource(result.source_bundle()))
        expected = result.to_downstream_payload()
        payload = json.loads(json.dumps(payload))
        expected = json.loads(json.dumps(expected))
        payload.pop("audit_ref", None)
        expected.pop("audit_ref", None)
        payload["retrieval_diagnostics"].pop("elapsed_ms_total", None)
        expected["retrieval_diagnostics"].pop("elapsed_ms_total", None)
        payload["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)
        expected["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)
        self.assertEqual(payload, expected)

    def test_retrieval_downstream_payload_helper_backfills_sparse_source_bundle_fields(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        class _SparseSourceBundleOnlySource:
            def __init__(self, payload: dict[str, object]) -> None:
                self._payload = payload

            def source_bundle(self) -> dict[str, object]:
                return self._payload

        sparse_source_bundle = json.loads(json.dumps(result.source_bundle()))
        for key in (
            "result_fingerprint",
            "query_fingerprint",
            "retrieval_backend",
            "retrieval_mode",
            "source_bundle_fingerprint",
        ):
            sparse_source_bundle.pop(key, None)

        payload = build_retrieval_downstream_payload_from_result(_SparseSourceBundleOnlySource(sparse_source_bundle))
        expected = result.to_downstream_payload()
        payload = json.loads(json.dumps(payload))
        expected = json.loads(json.dumps(expected))
        payload.pop("audit_ref", None)
        expected.pop("audit_ref", None)
        payload["retrieval_diagnostics"].pop("elapsed_ms_total", None)
        expected["retrieval_diagnostics"].pop("elapsed_ms_total", None)
        payload["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)
        expected["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)

        self.assertEqual(payload["result_fingerprint"], result.result_fingerprint)
        self.assertNotIn("query_fingerprint", payload)
        self.assertEqual(payload["retrieval_backend"], "sqlite_fts")
        self.assertEqual(payload["retrieval_mode"], "fts_first")
        self.assertEqual(payload["retrieval_source_bundle"]["result_fingerprint"], result.result_fingerprint)
        self.assertEqual(payload["retrieval_source_bundle"]["query_fingerprint"], result.diagnostics["query_fingerprint"])
        self.assertEqual(payload["retrieval_source_bundle"]["retrieval_backend"], "sqlite_fts")
        self.assertEqual(payload["retrieval_source_bundle"]["retrieval_mode"], "fts_first")
        self.assertEqual(payload, expected)

    def test_retrieval_downstream_payload_helper_backfills_sparse_context_bundle_fields(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        sparse_context_bundle = json.loads(json.dumps(result.retrieval_context_bundle()))
        downstream_payload = sparse_context_bundle["retrieval_downstream_payload"]
        self.assertIsInstance(downstream_payload, dict)
        downstream_payload.pop("retrieval_backend", None)
        downstream_payload.pop("retrieval_mode", None)
        downstream_payload.pop("retrieval_policy", None)
        downstream_payload.pop("policy", None)
        downstream_payload.pop("retrieval_citation_bundle", None)
        downstream_payload.pop("retrieval_doc_bundle", None)
        downstream_payload.pop("retrieval_excerpt_bundle", None)
        downstream_payload.pop("retrieval_provenance", None)
        downstream_payload.pop("retrieval_source_bundle", None)
        downstream_payload.pop("retrieval_evidence", None)
        downstream_payload.pop("retrieval_manifest", None)
        retrieval_summary = downstream_payload.get("retrieval_summary")
        self.assertIsInstance(retrieval_summary, dict)
        retrieval_summary.pop("doc_ids", None)
        retrieval_summary.pop("excerpt_ids", None)
        retrieval_summary.pop("doc_fingerprints", None)
        retrieval_summary.pop("excerpt_fingerprints", None)
        retrieval_summary.pop("doc_identity_fingerprints", None)
        retrieval_summary.pop("top_excerpt_fingerprints", None)
        retrieval_summary.pop("top_excerpt_text_hashes", None)

        class _SparseContextBundleSource:
            def __init__(self, payload: dict[str, object]) -> None:
                self._payload = payload

            def retrieval_context_bundle(self) -> dict[str, object]:
                return self._payload

        source = _SparseContextBundleSource(sparse_context_bundle)

        payload = build_retrieval_downstream_payload_from_result(source)
        expected = result.to_downstream_payload()
        payload = json.loads(json.dumps(payload))
        expected = json.loads(json.dumps(expected))
        payload.pop("audit_ref", None)
        expected.pop("audit_ref", None)
        payload["retrieval_diagnostics"].pop("elapsed_ms_total", None)
        expected["retrieval_diagnostics"].pop("elapsed_ms_total", None)
        payload["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)
        expected["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)
        self.assertEqual(payload, expected)

        context_bundle = engine_build_retrieval_context_bundle_from_result(source)
        self.assertEqual(context_bundle["result_fingerprint"], result.result_fingerprint)
        self.assertEqual(context_bundle["retrieval_source_bundle"], result.source_bundle())
        self.assertEqual(
            context_bundle["retrieval_downstream_payload"]["retrieval_summary"]["doc_ids"],
            [item.doc_id for item in result.doc_hits],
        )
        self.assertEqual(
            context_bundle["retrieval_downstream_payload"]["retrieval_summary"]["excerpt_ids"],
            [item.excerpt_id for item in result.hits if item.excerpt_id is not None],
        )
        self.assertEqual(context_bundle["retrieval_downstream_payload"]["retrieval_citation_bundle"], result.citation_bundle())

    def test_sparse_payload_doc_and_excerpt_bundles_use_citation_fallbacks(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        payload = json.loads(json.dumps(result.to_downstream_payload()))
        payload.pop("retrieval_doc_bundle", None)
        payload.pop("retrieval_excerpt_bundle", None)
        payload["retrieval_provenance"].pop("doc_citations", None)
        payload["retrieval_provenance"].pop("excerpt_citations", None)

        doc_bundle = _build_retrieval_doc_bundle_from_payload(payload)
        excerpt_bundle = _build_retrieval_excerpt_bundle_from_payload(payload)

        self.assertEqual(doc_bundle["doc_citations"], result.citation_bundle()["doc_citations"])
        self.assertEqual(excerpt_bundle["excerpt_citations"], result.citation_bundle()["excerpt_citations"])
        self.assertEqual(doc_bundle["doc_hits"], payload["doc_hits"])
        self.assertEqual(excerpt_bundle["excerpt_hits"], payload["excerpt_hits"])

    def test_retrieve_auto_citation_bundle_matches_result_snapshot(self) -> None:
        query = RetrievalQuery(
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints=RetrievalConstraints(max_results=4),
            confidentiality_profile="confidential",
        )

        result = self.service.retrieve_auto(query)
        direct = self.service.retrieve_auto_citation_bundle(query)
        helper = engine_retrieve_auto_citation_bundle(
            self.service,
            query_text="memo coding comparison",
            scope="vault",
            intent="compare",
            constraints={"max_results": 4},
            confidentiality_profile="confidential",
        )

        self.assertEqual(direct, result.citation_bundle())
        self.assertEqual(helper, result.citation_bundle())
        self.assertEqual(direct["query_scope"], "vault")
        self.assertEqual(direct["query_intent"], "compare")
        self.assertEqual(direct["retrieval_backend"], "sqlite_fts")
        self.assertEqual(direct["retrieval_mode"], "fts_first")
        self.assertEqual(direct["active_strategy_ids"], ["fts"])
        self.assertEqual(direct["deferred_strategy_ids"], ["pageindex", "embeddings"])
        self.assertEqual(direct["doc_citations"], result.citation_bundle()["doc_citations"])
        self.assertEqual(direct["excerpt_citations"], result.citation_bundle()["excerpt_citations"])
        direct["doc_citations"][0]["doc_id"] = "mutated-doc-id"
        self.assertNotEqual(
            self.service.retrieve_auto_citation_bundle(query)["doc_citations"][0]["doc_id"],
            "mutated-doc-id",
        )

    def test_engine_retrieval_policy_snapshot_is_stable_and_copy_safe(self) -> None:
        first = engine_retrieval.retrieval_policy_snapshot()
        second = engine_retrieval.retrieval_policy_snapshot()

        self.assertEqual(first, second)
        self.assertEqual(first["retrieval_backend"], "sqlite_fts")
        self.assertEqual(first["retrieval_mode"], "fts_first")
        self.assertEqual(first["active_strategy_ids"], ["fts"])
        self.assertEqual(first["deferred_strategy_ids"], ["pageindex", "embeddings"])

        cast(list[str], first["active_strategy_ids"]).append("mutated")
        self.assertEqual(engine_retrieval.retrieval_policy_snapshot()["active_strategy_ids"], ["fts"])

    def test_engine_retrieval_tool_forwards_document_filters(self) -> None:
        result = engine_retrieve_auto(
            self.service,
            query_text="notes",
            scope="vault",
            intent="compare",
            constraints={"max_results": 5, "doc_types": ["pdf"]},
            confidentiality_profile="confidential",
        )

        self.assertTrue(result.doc_hits)
        self.assertEqual({hit.provenance["doc_type"] for hit in result.doc_hits}, {"pdf"})
        self.assertEqual(result.diagnostics["retrieval_manifest"]["doc_ids"], [hit.doc_id for hit in result.doc_hits])
        self.assertEqual(result.diagnostics["retrieval_backend"], "sqlite_fts")
        self.assertEqual(result.diagnostics["retrieval_mode"], "fts_first")

    def test_engine_retrieval_tool_exposes_explicit_fts_entrypoint(self) -> None:
        payload = {
            "max_results": 5,
            "doc_types": ["memo"],
            "prefer_exact_matches": True,
        }
        direct = engine_retrieve_fts(
            self.service,
            query_text="memo comparison",
            scope="vault",
            intent="compare",
            constraints=payload,
            confidentiality_profile="confidential",
        )
        auto = engine_retrieve_auto(
            self.service,
            query_text="memo comparison",
            scope="vault",
            intent="compare",
            constraints=payload,
            confidentiality_profile="confidential",
        )
        direct_payload = direct.to_downstream_payload()
        auto_payload = auto.to_downstream_payload()
        direct_payload.pop("audit_ref")
        auto_payload.pop("audit_ref")
        direct_payload["retrieval_diagnostics"].pop("elapsed_ms_total", None)
        auto_payload["retrieval_diagnostics"].pop("elapsed_ms_total", None)
        direct_payload["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)
        auto_payload["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)
        self.assertEqual(direct_payload, auto_payload)
        self.assertEqual(direct.diagnostics["retrieval_backend"], "sqlite_fts")
        self.assertEqual(direct.diagnostics["retrieval_mode"], "fts_first")

        direct_payload = engine_retrieve_fts_payload(
            self.service,
            query_text="memo comparison",
            scope="vault",
            intent="compare",
            constraints=payload,
            confidentiality_profile="confidential",
        )
        self.assertEqual(direct_payload["retrieval_summary"]["doc_ids"], [item.doc_id for item in direct.doc_hits])
        self.assertEqual(direct_payload["retrieval_summary"]["excerpt_ids"], [item.excerpt_id for item in direct.hits if item.excerpt_id is not None])

    def test_engine_retrieval_package_exposes_explicit_fts_entrypoint(self) -> None:
        payload = {
            "max_results": 5,
            "doc_types": ["memo"],
            "prefer_exact_matches": True,
        }
        direct = engine_retrieval.retrieve_fts(
            self.service,
            query_text="memo comparison",
            scope="vault",
            intent="compare",
            constraints=payload,
            confidentiality_profile="confidential",
        )
        expected = engine_retrieve_fts(
            self.service,
            query_text="memo comparison",
            scope="vault",
            intent="compare",
            constraints=payload,
            confidentiality_profile="confidential",
        )

        direct_payload = direct.to_downstream_payload()
        expected_payload = expected.to_downstream_payload()
        direct_payload.pop("audit_ref")
        expected_payload.pop("audit_ref")
        direct_payload["retrieval_diagnostics"].pop("elapsed_ms_total", None)
        expected_payload["retrieval_diagnostics"].pop("elapsed_ms_total", None)
        direct_payload["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)
        expected_payload["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)
        self.assertEqual(direct_payload, expected_payload)
        self.assertEqual(direct.diagnostics["retrieval_backend"], "sqlite_fts")
        self.assertEqual(direct.diagnostics["retrieval_mode"], "fts_first")

    def test_retrieve_auto_payload_matches_canonical_fts_payload(self) -> None:
        query = RetrievalQuery(
            query_text="memo comparison",
            scope="vault",
            intent="compare",
            constraints=RetrievalConstraints(max_results=4, doc_types=("memo",)),
            confidentiality_profile="confidential",
        )

        fts_payload = self.service.retrieve_fts_payload(query)
        auto_payload = self.service.retrieve_auto_payload(query)

        fts_payload = json.loads(json.dumps(fts_payload))
        auto_payload = json.loads(json.dumps(auto_payload))
        fts_payload.pop("audit_ref", None)
        auto_payload.pop("audit_ref", None)
        fts_payload["retrieval_diagnostics"].pop("elapsed_ms_total", None)
        auto_payload["retrieval_diagnostics"].pop("elapsed_ms_total", None)
        fts_payload["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)
        auto_payload["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)
        self.assertEqual(fts_payload, auto_payload)
        self.assertEqual(auto_payload["retrieval_summary"]["retrieval_backend"], "sqlite_fts")
        self.assertEqual(auto_payload["retrieval_summary"]["retrieval_mode"], "fts_first")

    def test_retrieval_provenance_surfaces_query_context(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        provenance = result.to_downstream_payload()["retrieval_provenance"]
        self.assertEqual(provenance["query_fingerprint"], result.diagnostics["query_fingerprint"])
        self.assertEqual(provenance["query_scope"], "vault")
        self.assertEqual(provenance["query_intent"], "compare")
        self.assertEqual(provenance["retrieval_backend"], "sqlite_fts")
        self.assertEqual(provenance["retrieval_mode"], "fts_first")

    def test_basket_promotion_items_backfill_query_context_from_bundle(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(
                    max_results=4,
                    date_range=("2026-01-01", "2026-12-31"),
                ),
                confidentiality_profile="confidential",
            )
        )
        direct_item = result.retrieval_basket_promotion_bundle()["promotion_items"][0]
        retrieval_evidence_fingerprint = result.evidence["retrieval_evidence_fingerprint"]
        expected_constraints = {
            "max_results": 4,
            "doc_types": [],
            "date_range": ["2026-01-01", "2026-12-31"],
            "require_citations": False,
            "section_hint": None,
            "prefer_exact_matches": False,
        }
        expected_constraints_fingerprint = hashlib.sha256(
            json.dumps(
                expected_constraints,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(direct_item["query_fingerprint"], result.diagnostics["query_fingerprint"])
        self.assertEqual(direct_item["query_scope"], "vault")
        self.assertEqual(direct_item["query_intent"], "compare")
        self.assertEqual(direct_item["query_constraints"], expected_constraints)
        self.assertEqual(direct_item["query_constraints_fingerprint"], expected_constraints_fingerprint)
        self.assertEqual(direct_item["query_date_range"], ["2026-01-01", "2026-12-31"])
        self.assertEqual(direct_item["retrieval_evidence_fingerprint"], retrieval_evidence_fingerprint)
        self.assertEqual(direct_item["retrieval_source_strategy"], "fts")
        self.assertEqual(direct_item["basket_item_id"], f"retrieval:fts:{direct_item['excerpt_id']}")
        self.assertEqual(direct_item["retrieval_policy"], result.diagnostics["retrieval_policy"])
        self.assertEqual(result.retrieval_basket_promotion_bundle()["query_constraints"], expected_constraints)
        self.assertEqual(
            result.retrieval_basket_promotion_bundle()["query_constraints_fingerprint"],
            expected_constraints_fingerprint,
        )
        self.assertEqual(
            result.retrieval_basket_promotion_bundle()["retrieval_evidence_fingerprint"],
            retrieval_evidence_fingerprint,
        )
        self.assertEqual(
            direct_item["citation_status"],
            result.retrieval_basket_promotion_bundle()["citation_status"],
        )
        self.assertEqual(direct_item["doc_type"], "memo")
        self.assertEqual(
            engine_retrieve_fts_basket_promotion_bundle(
                self.service,
                query_text="memo comparison",
                scope="vault",
                intent="compare",
                constraints={"max_results": 4, "date_range": ["2026-01-01", "2026-12-31"]},
                confidentiality_profile="confidential",
            ),
            result.retrieval_basket_promotion_bundle(),
        )
        self.assertEqual(
            engine_retrieve_auto_basket_promotion_bundle(
                self.service,
                query_text="memo comparison",
                scope="vault",
                intent="compare",
                constraints={"max_results": 4, "date_range": ["2026-01-01", "2026-12-31"]},
                confidentiality_profile="confidential",
            ),
            result.retrieval_basket_promotion_bundle(),
        )
        self.assertEqual(
            engine_retrieval.retrieve_fts_basket_promotion_bundle(
                self.service,
                query_text="memo comparison",
                scope="vault",
                intent="compare",
                constraints={"max_results": 4, "date_range": ["2026-01-01", "2026-12-31"]},
                confidentiality_profile="confidential",
            ),
            result.retrieval_basket_promotion_bundle(),
        )
        self.assertEqual(
            engine_retrieval.retrieve_auto_basket_promotion_bundle(
                self.service,
                query_text="memo comparison",
                scope="vault",
                intent="compare",
                constraints={"max_results": 4, "date_range": ["2026-01-01", "2026-12-31"]},
                confidentiality_profile="confidential",
            ),
            result.retrieval_basket_promotion_bundle(),
        )

        payload = result.to_downstream_payload()
        payload.pop("retrieval_basket_promotion_bundle", None)
        for hit in payload["excerpt_hits"]:
            hit.pop("query_fingerprint", None)
            hit.pop("query_scope", None)
            hit.pop("query_intent", None)
            hit.pop("query_date_range", None)
            hit.pop("citation_status", None)
            hit.pop("retrieval_evidence_fingerprint", None)
            hit.pop("retrieval_source_strategy", None)
            hit.pop("retrieval_policy", None)
            hit.pop("basket_item_id", None)
            hit["provenance"].pop("query_fingerprint", None)
            hit["provenance"].pop("query_scope", None)
            hit["provenance"].pop("query_intent", None)
            hit["provenance"].pop("query_date_range", None)
            hit["provenance"].pop("citation_status", None)
            hit["provenance"].pop("retrieval_evidence_fingerprint", None)
            hit["provenance"].pop("retrieval_source_strategy", None)
            hit["provenance"].pop("retrieval_policy", None)
            hit["provenance"].pop("basket_item_id", None)

        rehydrated_bundle = _build_retrieval_basket_promotion_bundle_from_payload(payload)
        rehydrated_item = rehydrated_bundle["promotion_items"][0]
        self.assertEqual(rehydrated_item["query_fingerprint"], result.diagnostics["query_fingerprint"])
        self.assertEqual(rehydrated_item["query_scope"], "vault")
        self.assertEqual(rehydrated_item["query_intent"], "compare")
        self.assertEqual(rehydrated_item["query_constraints"], expected_constraints)
        self.assertEqual(rehydrated_item["query_constraints_fingerprint"], expected_constraints_fingerprint)
        self.assertEqual(rehydrated_item["query_date_range"], ["2026-01-01", "2026-12-31"])
        self.assertEqual(rehydrated_item["retrieval_evidence_fingerprint"], retrieval_evidence_fingerprint)
        self.assertEqual(rehydrated_item["retrieval_source_strategy"], "fts")
        self.assertEqual(rehydrated_item["retrieval_policy"], result.diagnostics["retrieval_policy"])
        self.assertEqual(rehydrated_item["basket_item_id"], f"retrieval:fts:{rehydrated_item['excerpt_id']}")
        self.assertEqual(rehydrated_bundle["query_constraints"], expected_constraints)
        self.assertEqual(
            rehydrated_bundle["query_constraints_fingerprint"],
            expected_constraints_fingerprint,
        )
        self.assertEqual(rehydrated_bundle["retrieval_evidence_fingerprint"], retrieval_evidence_fingerprint)
        self.assertEqual(
            rehydrated_item["citation_status"],
            result.retrieval_basket_promotion_bundle()["citation_status"],
        )
        self.assertEqual(rehydrated_item["doc_type"], "memo")

    def test_basket_promotion_bundle_normalizes_query_constraints_snapshot(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(
                    max_results=4,
                    date_range=("2026-01-01", "2026-12-31"),
                ),
                confidentiality_profile="confidential",
            )
        )
        payload = result.to_downstream_payload()
        basket_bundle = payload["retrieval_basket_promotion_bundle"]
        self.assertIsInstance(basket_bundle, dict)
        cast(dict[str, object], basket_bundle)["query_constraints"] = {
            "max_results": 4,
            "doc_types": (),
            "date_range": ("2026-01-01", "2026-12-31"),
            "require_citations": False,
            "section_hint": "  ",
            "prefer_exact_matches": False,
        }
        promotion_items = cast(dict[str, object], basket_bundle)["promotion_items"]
        self.assertIsInstance(promotion_items, list)
        promotion_item = cast(list[dict[str, object]], promotion_items)[0]
        promotion_item.pop("basket_item_id", None)
        promotion_item["query_constraints"] = {
            "max_results": "4",
            "doc_types": ("memo",),
            "date_range": ("2026-01-01", "2026-12-31"),
            "require_citations": "false",
            "section_hint": "  ",
            "prefer_exact_matches": "false",
        }
        promotion_item["query_constraints_fingerprint"] = "stale-fingerprint"
        promotion_item.pop("promotion_item_fingerprint", None)
        cast(dict[str, object], basket_bundle).pop("query_constraints_fingerprint", None)

        normalized_bundle = _build_retrieval_basket_promotion_bundle_from_payload(payload)

        expected_constraints = {
            "max_results": 4,
            "doc_types": [],
            "date_range": ["2026-01-01", "2026-12-31"],
            "require_citations": False,
            "section_hint": None,
            "prefer_exact_matches": False,
        }
        expected_constraints_fingerprint = hashlib.sha256(
            json.dumps(
                expected_constraints,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(normalized_bundle["query_constraints"], expected_constraints)
        self.assertEqual(
            normalized_bundle["query_constraints_fingerprint"],
            expected_constraints_fingerprint,
        )
        normalized_item = normalized_bundle["promotion_items"][0]
        expected_item_constraints = {
            **expected_constraints,
            "doc_types": ["memo"],
        }
        expected_item_constraints_fingerprint = hashlib.sha256(
            json.dumps(
                expected_item_constraints,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(normalized_item["query_constraints"], expected_item_constraints)
        self.assertEqual(
            normalized_item["query_constraints_fingerprint"],
            expected_item_constraints_fingerprint,
        )
        self.assertEqual(normalized_item["basket_item_id"], f"retrieval:fts:{normalized_item['excerpt_id']}")
        self.assertNotEqual(normalized_item["promotion_item_fingerprint"], "stale-fingerprint")

    def test_basket_promotion_bundle_does_not_mint_non_fts_item_ids(self) -> None:
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
        basket_bundle = payload["retrieval_basket_promotion_bundle"]
        self.assertIsInstance(basket_bundle, dict)
        promotion_items = cast(dict[str, object], basket_bundle)["promotion_items"]
        self.assertIsInstance(promotion_items, list)
        promotion_item = cast(list[dict[str, object]], promotion_items)[0]
        promotion_item.pop("basket_item_id", None)
        promotion_item.pop("promotion_item_fingerprint", None)
        promotion_item["source_strategy"] = "pageindex"
        promotion_item["retrieval_source_strategy"] = "pageindex"

        normalized_bundle = _build_retrieval_basket_promotion_bundle_from_payload(payload)
        normalized_item = normalized_bundle["promotion_items"][0]

        self.assertEqual(normalized_item["source_strategy"], "pageindex")
        self.assertEqual(normalized_item["retrieval_source_strategy"], "pageindex")
        self.assertNotIn("basket_item_id", normalized_item)
        self.assertIn("promotion_item_fingerprint", normalized_item)

    def test_engine_retrieval_tool_returns_canonical_downstream_payload(self) -> None:
        payload = engine_retrieve_auto_payload(
            self.service,
            query_text="memo comparison",
            scope="vault",
            intent="compare",
            constraints={"max_results": 4, "doc_types": ["memo"]},
            confidentiality_profile="confidential",
        )

        self.assertEqual(payload["policy"], payload["retrieval_policy"])
        self.assertEqual(payload["retrieval_summary"]["retrieval_backend"], "sqlite_fts")
        self.assertEqual(payload["retrieval_summary"]["retrieval_mode"], "fts_first")
        self.assertEqual(payload["retrieval_summary"]["doc_ids"], [item["doc_id"] for item in payload["doc_hits"]])
        self.assertEqual(
            payload["retrieval_summary"]["excerpt_ids"],
            [item["excerpt_id"] for item in payload["excerpt_hits"] if item["excerpt_id"] is not None],
        )
        self.assertEqual(
            payload["retrieval_provenance"]["doc_citations"],
            [
                {
                    "doc_id": item["doc_id"],
                    "source_hash": item["source_hash"],
                    "doc_fingerprint": item["provenance"]["doc_fingerprint"],
                    "doc_identity_fingerprint": item["provenance"]["doc_identity_fingerprint"],
                    "doc_rank": item["provenance"]["doc_rank"],
                    "top_excerpt_id": item["top_excerpt_id"],
                    "top_excerpt_fingerprint": item["provenance"]["top_excerpt_fingerprint"],
                    "top_excerpt_text_hash": item["provenance"]["top_excerpt_text_hash"],
                    "source_strategy": item["provenance"]["source_strategy"],
                }
                for item in payload["doc_hits"]
            ],
        )
        self.assertEqual(
            payload["retrieval_provenance"]["excerpt_citations"],
            [
                {
                    "doc_id": item["doc_id"],
                    "excerpt_id": item["excerpt_id"],
                    "basket_item_id": item["basket_item_id"],
                    "doc_type": item["provenance"]["doc_type"],
                    "source_hash": item["source_hash"],
                    "excerpt_fingerprint": item["provenance"]["excerpt_fingerprint"],
                    "excerpt_text_hash": item["provenance"]["excerpt_text_hash"],
                    "rank": item["provenance"]["rank"],
                    "span": item["provenance"]["span"],
                    "match_count": item["provenance"]["match_count"],
                    "matched_terms": item["provenance"]["matched_terms"],
                    "fts_rank": item["provenance"]["fts_rank"],
                    "source_strategy": item["provenance"]["source_strategy"],
                    "retrieval_backend": item["provenance"]["retrieval_backend"],
                    "retrieval_mode": item["provenance"]["retrieval_mode"],
                }
                for item in payload["excerpt_hits"]
                if item["excerpt_id"] is not None
            ],
        )
        self.assertEqual(payload["doc_hits"][0]["doc_fingerprint"], payload["doc_hits"][0]["provenance"]["doc_fingerprint"])
        self.assertEqual(
            payload["doc_hits"][0]["doc_identity_fingerprint"],
            payload["doc_hits"][0]["provenance"]["doc_identity_fingerprint"],
        )
        self.assertEqual(
            payload["excerpt_hits"][0]["excerpt_fingerprint"],
            payload["excerpt_hits"][0]["provenance"]["excerpt_fingerprint"],
        )
        self.assertEqual(
            payload["excerpt_hits"][0]["excerpt_text_hash"],
            payload["excerpt_hits"][0]["provenance"]["excerpt_text_hash"],
        )
        payload["retrieval_summary"]["doc_ids"].append("mutated-doc-id")
        payload["doc_hits"][0]["provenance"]["doc_id"] = "mutated-doc-id"

        refreshed = engine_retrieve_auto_payload(
            self.service,
            query_text="memo comparison",
            scope="vault",
            intent="compare",
            constraints={"max_results": 4, "doc_types": ["memo"]},
            confidentiality_profile="confidential",
        )
        self.assertNotIn("mutated-doc-id", refreshed["retrieval_summary"]["doc_ids"])
        self.assertNotEqual(refreshed["doc_hits"][0]["provenance"]["doc_id"], "mutated-doc-id")

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
        self.assertIn("retrieval_manifest", event["metadata"])


if __name__ == "__main__":
    unittest.main()
