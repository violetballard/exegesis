from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import cast, get_args, get_type_hints

from src.qual.audit import AuditLog
from src.qual.docindex.service import DocIndexBuildOptions
from src.qual.docindex.service import DocIndexQueryConstraints
from src.qual.docindex.service import DocIndexService
from src.qual.engine.tools.excerpt_tools import fetch_excerpt as engine_tool_fetch_excerpt
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
from src.qual.engine.retrieval.payload import _build_retrieval_diagnostics_from_source_bundle
from src.qual.engine.retrieval.payload import _build_retrieval_citation_bundle_from_payload
from src.qual.engine.retrieval.payload import _build_retrieval_doc_bundle_from_payload
from src.qual.engine.retrieval.payload import _build_retrieval_excerpt_bundle_from_payload
from src.qual.engine.retrieval.payload import _build_retrieval_source_bundle_from_payload
from src.qual.engine.retrieval.payload import _build_retrieval_provenance_from_payload
import src.qual.retrieval as package_retrieval
from src.qual.retrieval import retrieve_auto as engine_retrieve_auto
from src.qual.retrieval import retrieve_auto_citation_bundle as engine_retrieve_auto_citation_bundle
from src.qual.retrieval import retrieve_auto_doc_bundle as engine_retrieve_auto_doc_bundle
from src.qual.retrieval import retrieve_auto_excerpt as engine_retrieve_auto_excerpt
from src.qual.retrieval import retrieve_auto_provenance_bundle as engine_retrieve_auto_provenance_bundle
from src.qual.retrieval import retrieve_auto_payload as engine_retrieve_auto_payload
from src.qual.retrieval import retrieve_auto_source_bundle as engine_retrieve_auto_source_bundle
from src.qual.retrieval import retrieve_fts as engine_retrieve_fts
from src.qual.retrieval import retrieve_fts_doc_bundle as engine_retrieve_fts_doc_bundle
from src.qual.retrieval import retrieve_fts_excerpt as engine_retrieve_fts_excerpt
from src.qual.retrieval import retrieve_fts_provenance_bundle as engine_retrieve_fts_provenance_bundle
from src.qual.retrieval import retrieve_fts_payload as engine_retrieve_fts_payload
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

    def test_retrieve_auto_normalizes_query_text_in_canonical_payloads(self) -> None:
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
                query_text="  Discussion   Theory  ",
                scope="doc:doc-pdf-1",
                intent="outline_support",
                constraints=RetrievalConstraints(max_results=6, section_hint="discussion", prefer_exact_matches=True),
                confidentiality_profile="confidential",
            )
        )

        compact_payload = compact.to_downstream_payload()
        spaced_payload = spaced.to_downstream_payload()
        compact_payload.pop("audit_ref")
        spaced_payload.pop("audit_ref")
        compact_payload["retrieval_diagnostics"].pop("elapsed_ms_total", None)
        spaced_payload["retrieval_diagnostics"].pop("elapsed_ms_total", None)
        compact_payload["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)
        spaced_payload["retrieval_diagnostics"].pop("elapsed_ms_by_strategy", None)

        self.assertEqual(compact_payload["query"]["query_text"], "discussion theory")
        self.assertEqual(spaced_payload["query"]["query_text"], "discussion theory")
        self.assertEqual(compact_payload, spaced_payload)
        self.assertEqual(compact.source_bundle()["query"]["query_text"], "discussion theory")
        self.assertEqual(spaced.source_bundle()["query"]["query_text"], "discussion theory")

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

    def test_retrieve_auto_normalizes_internal_query_text_and_section_hint_whitespace(self) -> None:
        self.service.add_or_update_document(
            doc_id="doc-memo-spaces",
            doc_type="memo",
            title_hint="Discussion Notes",
            text="Discussion notes cover theory comparison evidence.",
        )

        compact = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="discussion theory",
                scope="doc:doc-memo-spaces",
                intent="lookup",
                constraints=RetrievalConstraints(max_results=4, section_hint="discussion notes"),
                confidentiality_profile="confidential",
            )
        )
        spaced = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="  Discussion   Theory  ",
                scope="doc:doc-memo-spaces",
                intent="lookup",
                constraints=RetrievalConstraints(max_results=4, section_hint="  discussion   notes  "),
                confidentiality_profile="confidential",
            )
        )

        self.assertEqual(compact.query.query_text, "discussion theory")
        self.assertEqual(spaced.query.query_text, "Discussion Theory")
        self.assertEqual(compact.query.constraints.section_hint, "discussion notes")
        self.assertEqual(spaced.query.constraints.section_hint, "discussion notes")
        self.assertEqual(compact.diagnostics["query_fingerprint"], spaced.diagnostics["query_fingerprint"])
        self.assertEqual(compact.result_fingerprint, spaced.result_fingerprint)
        self.assertEqual([hit.excerpt_id for hit in compact.hits], [hit.excerpt_id for hit in spaced.hits])
        self.assertEqual(compact.hits[0].provenance["section_hint"], "discussion notes")
        self.assertEqual(spaced.hits[0].provenance["section_hint"], "discussion notes")
        self.assertEqual(
            compact.to_downstream_payload()["query"]["constraints"]["section_hint"],
            "discussion notes",
        )
        self.assertEqual(
            spaced.to_downstream_payload()["query"]["constraints"]["section_hint"],
            "discussion notes",
        )

    def test_retrieve_auto_normalizes_scope_whitespace_in_query_fingerprint(self) -> None:
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
                scope="  doc:doc-pdf-1  ",
                intent="outline_support",
                constraints=RetrievalConstraints(max_results=6, section_hint="discussion"),
                confidentiality_profile="confidential",
            )
        )
        self.assertEqual(compact.diagnostics["query_fingerprint"], spaced.diagnostics["query_fingerprint"])
        self.assertEqual(compact.result_fingerprint, spaced.result_fingerprint)
        self.assertEqual(spaced.query.scope, "doc:doc-pdf-1")
        self.assertEqual(spaced.to_downstream_payload()["query"]["scope"], "doc:doc-pdf-1")

    def test_retrieve_auto_normalizes_scope_prefix_case_in_query_fingerprint(self) -> None:
        canonical = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="discussion theory",
                scope="doc:doc-pdf-1",
                intent="outline_support",
                constraints=RetrievalConstraints(max_results=6, section_hint="discussion"),
                confidentiality_profile="confidential",
            )
        )
        mixed_case = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="discussion theory",
                scope="  DOC:doc-pdf-1  ",
                intent="outline_support",
                constraints=RetrievalConstraints(max_results=6, section_hint="discussion"),
                confidentiality_profile="confidential",
            )
        )

        self.assertEqual(canonical.diagnostics["query_fingerprint"], mixed_case.diagnostics["query_fingerprint"])
        self.assertEqual(canonical.result_fingerprint, mixed_case.result_fingerprint)
        self.assertEqual(mixed_case.query.scope, "doc:doc-pdf-1")
        self.assertEqual(mixed_case.to_downstream_payload()["query"]["scope"], "doc:doc-pdf-1")

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
            self.assertEqual(hit_payload["fts_rank"], hit.provenance["fts_rank"])
            self.assertEqual(hit_payload["match_count"], hit.provenance["match_count"])
            self.assertEqual(hit_payload["matched_terms"], hit.provenance["matched_terms"])
            self.assertEqual(hit_payload["section_hint"], "discussion")
            self.assertEqual(hit_payload["section_hint_rank"], hit.provenance["section_hint_rank"])

    def test_section_hint_biases_fts_ranking_and_provenance(self) -> None:
        self.service.add_or_update_document(
            doc_id="doc-alpha",
            doc_type="memo",
            title_hint="Alpha Notes",
            text="Methods notes cover theory comparison evidence.",
        )
        self.service.add_or_update_document(
            doc_id="doc-zeta",
            doc_type="memo",
            title_hint="Zeta Notes",
            text="Discussion notes cover theory comparison evidence.",
        )

        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="theory comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=5, doc_types=("memo",), section_hint="discussion"),
                confidentiality_profile="confidential",
            )
        )

        self.assertEqual(result.hits[0].doc_id, "doc-zeta")
        self.assertEqual(result.hits[0].provenance["section_hint"], "discussion")
        self.assertEqual(result.hits[0].provenance["section_hint_rank"], 0)
        alpha_hit = next(hit for hit in result.hits if hit.doc_id == "doc-alpha")
        self.assertEqual(alpha_hit.provenance["section_hint"], "discussion")
        self.assertEqual(alpha_hit.provenance["section_hint_rank"], 1)
        zeta_doc_hit = next(hit for hit in result.doc_hits if hit.doc_id == "doc-zeta")
        self.assertEqual(zeta_doc_hit.provenance["section_hint"], "discussion")
        self.assertEqual(zeta_doc_hit.provenance["top_section_hint_rank"], 0)
        alpha_doc_hit = next(hit for hit in result.doc_hits if hit.doc_id == "doc-alpha")
        self.assertEqual(alpha_doc_hit.provenance["top_section_hint_rank"], 1)

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

    def test_collection_scope_is_rejected_until_fts_can_resolve_it(self) -> None:
        with self.assertRaisesRegex(ValueError, "collection scope is unsupported"):
            self.service.retrieve_auto(
                RetrievalQuery(
                    query_text="discussion theory",
                    scope="collection:team-notes",
                    intent="lookup",
                    constraints=RetrievalConstraints(max_results=4, section_hint="discussion"),
                    confidentiality_profile="confidential",
                )
            )

    def test_collection_scope_is_rejected_via_canonical_package_entrypoint(self) -> None:
        with self.assertRaisesRegex(ValueError, "collection scope is unsupported"):
            engine_retrieve_auto(
                self.service,
                query_text="discussion theory",
                scope="collection:team-notes",
                intent="lookup",
                constraints=RetrievalConstraints(max_results=4, section_hint="discussion"),
                confidentiality_profile="confidential",
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
        self.assertEqual(doc_hit_payload["doc_rank"], doc_hit.provenance["doc_rank"])
        self.assertEqual(doc_hit_payload["top_excerpt_rank"], doc_hit.provenance["top_excerpt_rank"])
        self.assertIsNone(doc_hit_payload.get("section_hint"))
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
            payload["retrieval_summary"]["top_excerpt_ids"],
            [item.top_excerpt_id for item in result.doc_hits],
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
        self.assertEqual(payload["retrieval_diagnostics"]["retrieval_manifest"], result.diagnostics["retrieval_manifest"])
        self.assertEqual(payload["retrieval_diagnostics"]["retrieval_evidence"], result.diagnostics["retrieval_evidence"])
        self.assertEqual(payload["retrieval_manifest"], result.diagnostics["retrieval_manifest"])
        self.assertEqual(payload["retrieval_evidence"], result.evidence)
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
        self.assertEqual(bundle["basket_promotion"], result.to_downstream_payload()["basket_promotion"])
        bundle["retrieval_downstream_payload"]["retrieval_summary"]["doc_ids"].append("mutated-doc-id")
        bundle["retrieval_excerpt_bundle"]["excerpt_hits"][0]["provenance"]["doc_id"] = "mutated-doc-id"
        bundle["basket_promotion"]["doc_id"] = "mutated-doc-id"
        refreshed = engine_build_retrieval_context_bundle_from_result(_SourceBundleOnlySource(result.source_bundle()))
        self.assertNotIn("mutated-doc-id", refreshed["retrieval_downstream_payload"]["retrieval_summary"]["doc_ids"])
        self.assertNotEqual(
            refreshed["retrieval_excerpt_bundle"]["excerpt_hits"][0]["provenance"]["doc_id"],
            "mutated-doc-id",
        )
        self.assertNotEqual(refreshed["basket_promotion"]["doc_id"], "mutated-doc-id")

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
        self.assertEqual(excerpt["doc_id"], result.hits[0].doc_id)
        self.assertEqual(excerpt["span"], result.hits[0].span)
        self.assertEqual(excerpt["source_strategy"], "fts")
        self.assertEqual(excerpt["title_hint"], result.hits[0].title_hint)
        self.assertEqual(excerpt["retrieval_backend"], "sqlite_fts")
        self.assertEqual(excerpt["retrieval_mode"], "fts_first")
        self.assertEqual(excerpt["retrieval_policy"]["retrieval_backend"], "sqlite_fts")
        self.assertEqual(excerpt["retrieval_policy"]["retrieval_mode"], "fts_first")
        self.assertEqual(excerpt["source_hash"], result.hits[0].provenance["source_hash"])
        self.assertEqual(excerpt["text_hash"], result.hits[0].provenance["excerpt_text_hash"])
        self.assertEqual(excerpt["provenance"]["source_strategy"], "fts")
        self.assertEqual(excerpt["provenance"]["retrieval_backend"], "sqlite_fts")
        self.assertEqual(excerpt["provenance"]["retrieval_mode"], "fts_first")
        self.assertEqual(excerpt["provenance"]["hash"], result.hits[0].provenance["hash"])
        self.assertEqual(excerpt["provenance"]["excerpt_fingerprint"], result.hits[0].provenance["excerpt_fingerprint"])
        self.assertTrue(excerpt["text"])

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

    def test_engine_helper_fetch_excerpt_requires_an_fts_lookup_hit(self) -> None:
        docindex_service = DocIndexService(self.root, audit_log=self.audit)
        doc_id = "doc-pageindex-only-helper"
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
            engine_tool_fetch_excerpt(self.service, excerpt_id=str(excerpt_id))

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
        self.assertEqual(canonical["title_hint"], result.hits[0].title_hint)
        self.assertEqual(canonical["retrieval_backend"], "sqlite_fts")
        self.assertEqual(canonical["retrieval_mode"], "fts_first")
        self.assertEqual(canonical["retrieval_policy"]["retrieval_backend"], "sqlite_fts")
        self.assertEqual(canonical["retrieval_policy"]["retrieval_mode"], "fts_first")
        self.assertEqual(canonical["active_strategy_ids"], ["fts"])
        self.assertEqual(canonical["deferred_strategy_ids"], ["pageindex", "embeddings"])
        self.assertEqual(canonical["strategies_used"], ["fts"])
        self.assertEqual(canonical["provenance"]["source_strategy"], "fts")
        self.assertEqual(canonical["provenance"]["retrieval_backend"], "sqlite_fts")
        self.assertEqual(canonical["provenance"]["retrieval_mode"], "fts_first")
        self.assertEqual(canonical["provenance"]["active_strategy_ids"], ["fts"])
        self.assertEqual(canonical["provenance"]["deferred_strategy_ids"], ["pageindex", "embeddings"])
        self.assertEqual(canonical["provenance"]["strategies_used"], ["fts"])
        self.assertEqual(canonical["provenance"]["doc_id"], result.hits[0].doc_id)
        self.assertEqual(canonical["doc_fingerprint"], canonical["provenance"]["doc_fingerprint"])
        self.assertEqual(canonical["doc_identity_fingerprint"], canonical["provenance"]["doc_identity_fingerprint"])
        self.assertEqual(canonical["provenance"]["excerpt_fingerprint"], result.hits[0].provenance["excerpt_fingerprint"])
        self.assertEqual(
            canonical["provenance"]["excerpt_provenance_fingerprint"],
            result.hits[0].provenance["excerpt_provenance_fingerprint"],
        )
        self.assertEqual(
            canonical["excerpt_provenance_fingerprint"],
            result.hits[0].provenance["excerpt_provenance_fingerprint"],
        )
        self.assertEqual(canonical["provenance"]["hash"], result.hits[0].provenance["hash"])
        self.assertEqual(canonical["text_hash"], result.hits[0].provenance["excerpt_text_hash"])
        self.assertEqual(canonical["excerpt_text_hash"], result.hits[0].provenance["excerpt_text_hash"])
        self.assertEqual(canonical["lookup_fingerprint"], canonical["provenance"]["lookup_fingerprint"])
        self.assertEqual(canonical["basket_promotion"]["promotion_source"], "lookup_excerpt")
        self.assertTrue(canonical["basket_promotion"]["promotion_ready"])
        self.assertTrue(canonical["basket_promotion"]["citation_available"])
        self.assertEqual(canonical["basket_promotion"]["lookup_fingerprint"], canonical["lookup_fingerprint"])
        self.assertEqual(canonical["basket_promotion"]["doc_id"], canonical["doc_id"])
        self.assertEqual(canonical["basket_promotion"]["excerpt_id"], canonical["excerpt_id"])
        self.assertEqual(
            canonical["basket_promotion"]["excerpt_provenance_fingerprint"],
            canonical["excerpt_provenance_fingerprint"],
        )
        self.assertEqual(canonical["basket_promotion"]["span"], canonical["span"])

    def test_retrieve_auto_excerpt_routes_to_canonical_fts_lookup(self) -> None:
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

        direct = self.service.retrieve_auto_excerpt(excerpt_id or "")
        helper = engine_retrieval.retrieve_auto_excerpt(
            self.service,
            excerpt_id=excerpt_id or "",
        )
        package_helper = engine_retrieve_auto_excerpt(
            self.service,
            excerpt_id=excerpt_id or "",
        )
        canonical = self.service.retrieve_fts_excerpt(excerpt_id or "")

        self.assertEqual(direct, canonical)
        self.assertEqual(helper, canonical)
        self.assertEqual(package_helper, canonical)
        self.assertEqual(direct["retrieval_backend"], "sqlite_fts")
        self.assertEqual(direct["retrieval_mode"], "fts_first")
        self.assertEqual(direct["active_strategy_ids"], ["fts"])
        self.assertEqual(direct["deferred_strategy_ids"], ["pageindex", "embeddings"])
        self.assertEqual(direct["lookup_fingerprint"], direct["provenance"]["lookup_fingerprint"])

    def test_normalize_excerpt_payload_backfills_canonical_provenance_for_sparse_inputs(self) -> None:
        normalized = self.service._normalize_excerpt_payload(
            {
                "excerpt_id": "excerpt-sparse-1",
                "doc_id": "doc-pdf-1",
                "doc_type": "pdf",
                "text": "Methods section with recruitment constraints.",
                "span": {"char_range": {"start": "5", "end": "21"}},
                "provenance": {
                    "matched_terms": ("methods", "constraints"),
                    "query_fingerprint": "query-fingerprint-1",
                    "query_scope": "vault",
                    "query_intent": "lookup",
                    "query_date_range": ("2026-01-01", "2026-01-31"),
                    "candidate_doc_count": 2,
                    "rank": 1,
                    "fts_rank": -0.25,
                },
            },
            source_strategy="fts",
            lookup_resolution="fts",
        )

        self.assertEqual(normalized["retrieval_backend"], "sqlite_fts")
        self.assertEqual(normalized["retrieval_mode"], "fts_first")
        self.assertEqual(normalized["retrieval_policy"]["active_strategy_ids"], ["fts"])
        self.assertEqual(normalized["retrieval_policy"]["deferred_strategy_ids"], ["pageindex", "embeddings"])
        self.assertEqual(normalized["active_strategy_ids"], ["fts"])
        self.assertEqual(normalized["deferred_strategy_ids"], ["pageindex", "embeddings"])
        self.assertEqual(normalized["strategies_used"], ["fts"])
        self.assertEqual(normalized["span"], {"char_range": {"start": 5, "end": 21}})
        self.assertEqual(normalized["excerpt_text_hash"], normalized["text_hash"])
        self.assertEqual(normalized["matched_terms"], ["methods", "constraints"])
        self.assertEqual(normalized["match_count"], 2)
        self.assertEqual(normalized["query_fingerprint"], "query-fingerprint-1")
        self.assertEqual(normalized["query_scope"], "vault")
        self.assertEqual(normalized["query_intent"], "lookup")
        self.assertEqual(normalized["query_date_range"], ["2026-01-01", "2026-01-31"])
        self.assertEqual(normalized["candidate_doc_count"], 2)
        self.assertEqual(normalized["rank"], 1)
        self.assertEqual(normalized["fts_rank"], -0.25)
        self.assertTrue(normalized["doc_fingerprint"])
        self.assertEqual(normalized["basket_promotion"]["promotion_source"], "lookup_excerpt")
        self.assertTrue(normalized["basket_promotion"]["promotion_ready"])
        self.assertTrue(normalized["basket_promotion"]["citation_available"])
        self.assertEqual(normalized["basket_promotion"]["doc_id"], "doc-pdf-1")
        self.assertEqual(normalized["basket_promotion"]["excerpt_id"], "excerpt-sparse-1")
        self.assertEqual(normalized["basket_promotion"]["span"], {"char_range": {"start": 5, "end": 21}})
        self.assertEqual(
            normalized["basket_promotion"]["excerpt_provenance_fingerprint"],
            normalized["excerpt_provenance_fingerprint"],
        )
        self.assertEqual(normalized["doc_fingerprint"], normalized["provenance"]["doc_fingerprint"])
        self.assertEqual(normalized["provenance"]["excerpt_id"], "excerpt-sparse-1")
        self.assertEqual(normalized["provenance"]["doc_id"], "doc-pdf-1")
        self.assertEqual(normalized["provenance"]["doc_type"], "pdf")
        self.assertEqual(normalized["provenance"]["span"], {"char_range": {"start": 5, "end": 21}})
        self.assertEqual(normalized["provenance"]["source_strategy"], "fts")
        self.assertEqual(normalized["provenance"]["retrieval_source_strategy"], "fts")
        self.assertEqual(normalized["provenance"]["lookup_resolution"], "fts")
        self.assertEqual(normalized["provenance"]["retrieval_backend"], "sqlite_fts")
        self.assertEqual(normalized["provenance"]["retrieval_mode"], "fts_first")
        self.assertEqual(normalized["provenance"]["active_strategy_ids"], ["fts"])
        self.assertEqual(normalized["provenance"]["deferred_strategy_ids"], ["pageindex", "embeddings"])
        self.assertEqual(normalized["provenance"]["strategies_used"], ["fts"])
        self.assertEqual(
            normalized["provenance"]["retrieval_policy"]["deferred_strategy_ids"],
            ["pageindex", "embeddings"],
        )
        self.assertEqual(normalized["provenance"]["matched_terms"], ["methods", "constraints"])
        self.assertEqual(normalized["provenance"]["match_count"], 2)
        self.assertEqual(normalized["provenance"]["query_fingerprint"], "query-fingerprint-1")
        self.assertEqual(normalized["provenance"]["query_scope"], "vault")
        self.assertEqual(normalized["provenance"]["query_intent"], "lookup")
        self.assertEqual(normalized["provenance"]["query_date_range"], ["2026-01-01", "2026-01-31"])
        self.assertEqual(normalized["provenance"]["candidate_doc_count"], 2)
        self.assertEqual(normalized["provenance"]["rank"], 1)
        self.assertEqual(normalized["provenance"]["fts_rank"], -0.25)
        self.assertEqual(normalized["provenance"]["hash"], normalized["text_hash"])
        self.assertEqual(normalized["provenance"]["excerpt_text_hash"], normalized["text_hash"])
        self.assertEqual(normalized["provenance"]["excerpt_fingerprint"], normalized["excerpt_fingerprint"])
        self.assertEqual(
            normalized["provenance"]["excerpt_provenance_fingerprint"],
            normalized["excerpt_provenance_fingerprint"],
        )
        self.assertEqual(normalized["lookup_fingerprint"], normalized["provenance"]["lookup_fingerprint"])
        self.assertTrue(normalized["provenance"]["doc_identity_fingerprint"])

    def test_normalize_excerpt_payload_canonicalizes_sparse_query_metadata_types(self) -> None:
        normalized = self.service._normalize_excerpt_payload(
            {
                "excerpt_id": "excerpt-sparse-typed-1",
                "doc_id": "doc-pdf-1",
                "doc_type": "pdf",
                "text": "Discussion theory evidence stays deterministic.",
                "span": {"char_range": {"start": "7", "end": "38"}},
                "provenance": {
                    "matched_terms": ("discussion", "theory"),
                    "query_scope": "vault",
                    "query_intent": "compare",
                    "query_confidentiality_profile": "  StAnDaRd  ",
                    "query_date_range": ("2026-02-01", "2026-02-29"),
                    "candidate_doc_count": "3",
                    "rank": "4",
                    "fts_rank": "-0.75",
                    "section_hint": "  discussion   notes  ",
                    "section_hint_rank": "1",
                },
            },
            source_strategy="fts",
            lookup_resolution="fts",
        )

        self.assertEqual(normalized["query_confidentiality_profile"], "standard")
        self.assertEqual(normalized["candidate_doc_count"], 3)
        self.assertEqual(normalized["rank"], 4)
        self.assertEqual(normalized["fts_rank"], -0.75)
        self.assertEqual(normalized["section_hint"], "discussion notes")
        self.assertEqual(normalized["section_hint_rank"], 1)
        self.assertEqual(normalized["provenance"]["query_confidentiality_profile"], "standard")
        self.assertEqual(normalized["provenance"]["candidate_doc_count"], 3)
        self.assertEqual(normalized["provenance"]["rank"], 4)
        self.assertEqual(normalized["provenance"]["fts_rank"], -0.75)
        self.assertEqual(normalized["provenance"]["section_hint"], "discussion notes")
        self.assertEqual(normalized["provenance"]["section_hint_rank"], 1)

    def test_normalize_excerpt_payload_canonicalizes_lookup_metadata_for_fingerprints(self) -> None:
        compact = self.service._normalize_excerpt_payload(
            {
                "excerpt_id": "excerpt-sparse-lookup-1",
                "doc_id": "doc-pdf-1",
                "doc_type": "pdf",
                "text": "Discussion theory evidence stays deterministic.",
                "span": {"char_range": {"start": 7, "end": 38}},
            },
            source_strategy="fts",
            lookup_resolution="fts",
            lookup_confidentiality_profile="standard",
        )
        spaced = self.service._normalize_excerpt_payload(
            {
                "excerpt_id": "excerpt-sparse-lookup-1",
                "doc_id": "doc-pdf-1",
                "doc_type": "pdf",
                "text": "Discussion theory evidence stays deterministic.",
                "span": {"char_range": {"start": 7, "end": 38}},
                "lookup_resolution": "  FTS  ",
                "lookup_confidentiality_profile": "  StAnDaRd  ",
                "provenance": {
                    "lookup_resolution": "  FTS  ",
                    "lookup_confidentiality_profile": "  StAnDaRd  ",
                },
            },
            source_strategy="fts",
            lookup_resolution="  FTS  ",
            lookup_confidentiality_profile="  StAnDaRd  ",
        )

        self.assertEqual(compact["lookup_resolution"], "fts")
        self.assertEqual(compact["lookup_confidentiality_profile"], "standard")
        self.assertEqual(spaced["lookup_resolution"], "fts")
        self.assertEqual(spaced["lookup_confidentiality_profile"], "standard")
        self.assertEqual(spaced["provenance"]["lookup_resolution"], "fts")
        self.assertEqual(spaced["provenance"]["lookup_confidentiality_profile"], "standard")
        self.assertEqual(compact["lookup_fingerprint"], spaced["lookup_fingerprint"])
        self.assertEqual(compact["excerpt_provenance_fingerprint"], spaced["excerpt_provenance_fingerprint"])

    def test_retrieve_fts_excerpt_records_lookup_fingerprint_in_audit(self) -> None:
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

        excerpt = self.service.retrieve_fts_excerpt(excerpt_id or "")

        lines = [json.loads(line) for line in (self.root / "audit_events.jsonl").read_text(encoding="utf-8").splitlines()]
        event = next(item for item in lines if item["name"] == "excerpt_lookup_completed")

        self.assertEqual(event["metadata"]["lookup_entrypoint"], "retrieve_fts_excerpt")
        self.assertEqual(event["metadata"]["lookup_resolution"], "fts")
        self.assertEqual(event["metadata"]["lookup_confidentiality_profile"], "confidential")
        self.assertEqual(event["metadata"]["active_strategy_ids"], ["fts"])
        self.assertEqual(event["metadata"]["deferred_strategy_ids"], ["pageindex", "embeddings"])
        self.assertEqual(event["metadata"]["strategies_used"], ["fts"])
        self.assertEqual(event["metadata"]["doc_fingerprint"], excerpt["doc_fingerprint"])
        self.assertEqual(event["metadata"]["lookup_fingerprint"], excerpt["lookup_fingerprint"])

    def test_retrieve_fts_excerpt_honors_confidentiality_profile_for_title_hint(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="discussion theory",
                scope="doc:doc-pdf-1",
                intent="lookup",
                constraints=RetrievalConstraints(max_results=3),
                confidentiality_profile="standard",
            )
        )

        excerpt_id = result.hits[0].excerpt_id
        self.assertIsNotNone(excerpt_id)

        confidential = self.service.retrieve_fts_excerpt(excerpt_id or "")
        standard = self.service.retrieve_fts_excerpt(
            excerpt_id or "",
            confidentiality_profile="standard",
        )
        alias = self.service.fetch_fts_excerpt(
            excerpt_id or "",
            confidentiality_profile="standard",
        )
        helper = engine_retrieval.retrieve_fts_excerpt(
            self.service,
            excerpt_id=excerpt_id or "",
            confidentiality_profile="standard",
        )
        package_helper = engine_retrieve_fts_excerpt(
            self.service,
            excerpt_id=excerpt_id or "",
            confidentiality_profile="standard",
        )

        self.assertNotEqual(confidential["title_hint"], "Interview Packet")
        self.assertEqual(standard["title_hint"], "Interview Packet")
        self.assertEqual(alias["title_hint"], "Interview Packet")
        self.assertEqual(helper["title_hint"], "Interview Packet")
        self.assertEqual(package_helper["title_hint"], "Interview Packet")
        self.assertEqual(standard, alias)
        self.assertEqual(standard, helper)
        self.assertEqual(standard, package_helper)
        self.assertEqual(confidential["lookup_confidentiality_profile"], "confidential")
        self.assertEqual(confidential["provenance"]["lookup_confidentiality_profile"], "confidential")
        self.assertEqual(standard["lookup_confidentiality_profile"], "standard")
        self.assertEqual(standard["provenance"]["lookup_confidentiality_profile"], "standard")
        self.assertEqual(
            confidential["excerpt_provenance_fingerprint"],
            standard["excerpt_provenance_fingerprint"],
        )
        self.assertNotEqual(confidential["lookup_fingerprint"], standard["lookup_fingerprint"])

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
                "query_text": "  Memo   Comparison  ",
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

        self.assertEqual(provenance["query_date_range"], ["2026-01-01", "2026-01-31"])
        self.assertEqual(provenance["active_strategy_ids"], ["fts"])
        self.assertEqual(provenance["deferred_strategy_ids"], ["pageindex", "embeddings"])
        self.assertEqual(provenance["fts_shortlist_doc_ids"], ["doc-1", "doc-2"])
        self.assertEqual(source_bundle["query"]["query_text"], "memo comparison")
        self.assertEqual(source_bundle["query"]["constraints"]["doc_types"], ["memo", "pdf"])
        self.assertEqual(source_bundle["query"]["constraints"]["date_range"], ["2026-01-01", "2026-01-31"])
        self.assertEqual(source_bundle["policy"]["active_strategy_ids"], ["fts"])
        self.assertEqual(source_bundle["policy"]["deferred_strategy_ids"], ["pageindex", "embeddings"])
        self.assertEqual(excerpt_bundle["doc_count"], 1)
        self.assertEqual(excerpt_bundle["excerpt_count"], 1)
        self.assertIsInstance(excerpt_bundle["excerpt_hits"], list)
        self.assertIsInstance(excerpt_bundle["excerpt_citations"], list)
        self.assertEqual(excerpt_bundle["excerpt_hits"][0]["excerpt_id"], "excerpt-1")
        self.assertEqual(excerpt_bundle["excerpt_citations"][0]["excerpt_id"], "excerpt-1")

    def test_retrieval_source_bundle_normalizer_canonicalizes_query_confidentiality_and_bool_constraints(self) -> None:
        source_bundle = _build_retrieval_source_bundle_from_payload(
            {
                "retrieval_source_bundle": {
                    "query": {
                        "query_text": "  Memo   Comparison  ",
                        "scope": "vault",
                        "intent": "compare",
                        "confidentiality_profile": "  StAnDaRd  ",
                        "constraints": {
                            "doc_types": ("Memo", "pdf"),
                            "require_citations": "1",
                            "prefer_exact_matches": " off ",
                            "section_hint": "  discussion  ",
                        },
                    },
                    "policy": {
                        "retrieval_backend": "sqlite_fts",
                        "retrieval_mode": "fts_first",
                        "active_strategy_ids": ("fts",),
                        "deferred_strategy_ids": ("pageindex", "embeddings"),
                    },
                    "retrieval_summary": {},
                    "retrieval_manifest": {},
                    "retrieval_evidence": {},
                }
            }
        )

        self.assertEqual(source_bundle["query"]["query_text"], "memo comparison")
        self.assertEqual(source_bundle["query"]["confidentiality_profile"], "standard")
        self.assertEqual(source_bundle["query"]["constraints"]["doc_types"], ["memo", "pdf"])
        self.assertEqual(source_bundle["query"]["constraints"]["require_citations"], True)
        self.assertEqual(source_bundle["query"]["constraints"]["prefer_exact_matches"], False)
        self.assertEqual(source_bundle["query"]["constraints"]["section_hint"], "discussion")

    def test_retrieval_payload_normalizers_canonicalize_reversed_query_date_ranges(self) -> None:
        payload = {
            "query": {
                "query_text": "memo comparison",
                "scope": "vault",
                "intent": "compare",
                "confidentiality_profile": "standard",
                "constraints": {
                    "date_range": ["2026-01-31", "2026-01-01"],
                },
            },
            "retrieval_summary": {
                "query_date_range": ["2026-01-31", "2026-01-01"],
                "retrieval_backend": "sqlite_fts",
                "retrieval_mode": "fts_first",
                "active_strategy_ids": ["fts"],
                "deferred_strategy_ids": ["pageindex", "embeddings"],
            },
            "retrieval_diagnostics": {
                "date_range": ["2026-01-31", "2026-01-01"],
                "retrieval_backend": "sqlite_fts",
                "retrieval_mode": "fts_first",
                "active_strategy_ids": ["fts"],
                "deferred_strategy_ids": ["pageindex", "embeddings"],
            },
            "retrieval_provenance": {
                "query_date_range": ["2026-01-31", "2026-01-01"],
                "retrieval_backend": "sqlite_fts",
                "retrieval_mode": "fts_first",
                "active_strategy_ids": ["fts"],
                "deferred_strategy_ids": ["pageindex", "embeddings"],
            },
            "retrieval_source_bundle": {
                "query": {
                    "query_text": "memo comparison",
                    "scope": "vault",
                    "intent": "compare",
                    "confidentiality_profile": "standard",
                    "constraints": {
                        "date_range": ["2026-01-31", "2026-01-01"],
                    },
                },
                "policy": {
                    "retrieval_backend": "sqlite_fts",
                    "retrieval_mode": "fts_first",
                    "active_strategy_ids": ["fts"],
                    "deferred_strategy_ids": ["pageindex", "embeddings"],
                },
                "retrieval_summary": {
                    "query_date_range": ["2026-01-31", "2026-01-01"],
                },
                "retrieval_provenance": {
                    "query_date_range": ["2026-01-31", "2026-01-01"],
                },
                "retrieval_doc_bundle": {
                    "query_date_range": ["2026-01-31", "2026-01-01"],
                },
                "retrieval_excerpt_bundle": {
                    "query_date_range": ["2026-01-31", "2026-01-01"],
                },
                "retrieval_citation_bundle": {
                    "query_date_range": ["2026-01-31", "2026-01-01"],
                },
            },
        }

        source_bundle = _build_retrieval_source_bundle_from_payload(payload)
        provenance = _build_retrieval_provenance_from_payload(payload)
        diagnostics = _build_retrieval_diagnostics_from_source_bundle(source_bundle)

        self.assertEqual(source_bundle["query"]["constraints"]["date_range"], ["2026-01-01", "2026-01-31"])
        self.assertEqual(source_bundle["retrieval_summary"]["query_date_range"], ["2026-01-01", "2026-01-31"])
        self.assertEqual(source_bundle["retrieval_provenance"]["query_date_range"], ["2026-01-01", "2026-01-31"])
        self.assertEqual(
            source_bundle["retrieval_citation_bundle"]["query_date_range"],
            ["2026-01-01", "2026-01-31"],
        )
        self.assertEqual(
            source_bundle["retrieval_doc_bundle"]["query_date_range"],
            ["2026-01-01", "2026-01-31"],
        )
        self.assertEqual(
            source_bundle["retrieval_excerpt_bundle"]["query_date_range"],
            ["2026-01-01", "2026-01-31"],
        )
        self.assertEqual(provenance["query_date_range"], ["2026-01-01", "2026-01-31"])
        self.assertEqual(diagnostics["date_range"], ["2026-01-01", "2026-01-31"])

    def test_retrieval_payload_normalizers_canonicalize_unordered_iterables(self) -> None:
        source_bundle = _build_retrieval_source_bundle_from_payload(
            {
                "retrieval_source_bundle": {
                    "query": {
                        "query_text": "memo comparison",
                        "scope": "vault",
                        "intent": "compare",
                        "confidentiality_profile": "standard",
                        "constraints": {
                            "doc_types": {"pdf", "memo"},
                        },
                    },
                    "policy": {
                        "retrieval_backend": "sqlite_fts",
                        "retrieval_mode": "fts_first",
                        "active_strategy_ids": {"fts"},
                        "deferred_strategy_ids": {"embeddings", "pageindex"},
                    },
                    "retrieval_summary": {
                        "doc_ids": {"doc-b", "doc-a"},
                        "excerpt_ids": {"excerpt-b", "excerpt-a"},
                        "retrieval_backend": "sqlite_fts",
                        "retrieval_mode": "fts_first",
                        "active_strategy_ids": {"fts"},
                        "deferred_strategy_ids": {"embeddings", "pageindex"},
                    },
                }
            }
        )
        provenance = _build_retrieval_provenance_from_payload(
            {
                "retrieval_provenance": {
                    "fts_shortlist_doc_ids": {"doc-b", "doc-a"},
                    "active_strategy_ids": {"fts"},
                    "deferred_strategy_ids": {"embeddings", "pageindex"},
                    "retrieval_backend": "sqlite_fts",
                    "retrieval_mode": "fts_first",
                }
            }
        )

        self.assertEqual(source_bundle["query"]["constraints"]["doc_types"], ["memo", "pdf"])
        self.assertEqual(source_bundle["policy"]["active_strategy_ids"], ["fts"])
        self.assertEqual(source_bundle["policy"]["deferred_strategy_ids"], ["embeddings", "pageindex"])
        self.assertEqual(source_bundle["retrieval_summary"]["doc_ids"], ["doc-a", "doc-b"])
        self.assertEqual(source_bundle["retrieval_summary"]["excerpt_ids"], ["excerpt-a", "excerpt-b"])
        self.assertEqual(provenance["fts_shortlist_doc_ids"], ["doc-a", "doc-b"])
        self.assertEqual(provenance["active_strategy_ids"], ["fts"])
        self.assertEqual(provenance["deferred_strategy_ids"], ["embeddings", "pageindex"])

    def test_retrieval_source_bundle_normalizer_backfills_sparse_top_level_hits(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        sparse_source_bundle = result.source_bundle()
        sparse_source_bundle.pop("doc_hits", None)
        sparse_source_bundle.pop("excerpt_hits", None)

        normalized = _build_retrieval_source_bundle_from_payload(
            {"retrieval_source_bundle": sparse_source_bundle}
        )

        self.assertEqual(normalized["doc_hits"], result.to_downstream_payload()["doc_hits"])
        self.assertEqual(normalized["excerpt_hits"], result.to_downstream_payload()["excerpt_hits"])
        normalized["doc_hits"][0]["provenance"]["doc_id"] = "mutated-doc-id"
        normalized["excerpt_hits"][0]["provenance"]["doc_id"] = "mutated-doc-id"
        refreshed = _build_retrieval_source_bundle_from_payload(
            {"retrieval_source_bundle": sparse_source_bundle}
        )
        self.assertNotEqual(refreshed["doc_hits"][0]["provenance"]["doc_id"], "mutated-doc-id")
        self.assertNotEqual(refreshed["excerpt_hits"][0]["provenance"]["doc_id"], "mutated-doc-id")

    def test_citation_bundle_helper_rebuilds_citations_from_top_level_hits(self) -> None:
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
        payload.pop("retrieval_citation_bundle", None)
        payload.pop("retrieval_provenance", None)
        payload["retrieval_doc_bundle"] = {
            "doc_hits": json.loads(json.dumps(payload["doc_hits"])),
        }
        payload["retrieval_excerpt_bundle"] = {
            "excerpt_hits": json.loads(json.dumps(payload["excerpt_hits"])),
        }

        rebuilt = _build_retrieval_citation_bundle_from_payload(payload)

        self.assertEqual(
            rebuilt["doc_citations"],
            [
                {
                    "doc_id": item.doc_id,
                    "doc_type": item.provenance["doc_type"],
                    "source_hash": item.source_hash,
                    "doc_fingerprint": item.provenance["doc_fingerprint"],
                    "doc_identity_fingerprint": item.provenance["doc_identity_fingerprint"],
                    "doc_rank": item.provenance["doc_rank"],
                    "top_excerpt_id": item.top_excerpt_id,
                    "top_excerpt_fingerprint": item.provenance["top_excerpt_fingerprint"],
                    "top_excerpt_text_hash": item.provenance["top_excerpt_text_hash"],
                    "top_excerpt_span": item.provenance["top_excerpt_span"],
                    "top_excerpt_rank": item.provenance["top_excerpt_rank"],
                    "top_fts_rank": item.provenance["top_fts_rank"],
                    "excerpt_ids": item.provenance["excerpt_ids"],
                    "excerpt_count": item.excerpt_count,
                    "matched_terms": item.provenance["top_matched_terms"],
                    "source_strategy": item.provenance["source_strategy"],
                    "retrieval_backend": item.provenance["retrieval_backend"],
                    "retrieval_mode": item.provenance["retrieval_mode"],
                    **(
                        {"section_hint": item.provenance["section_hint"]}
                        if item.provenance.get("section_hint")
                        else {}
                    ),
                    **(
                        {"top_section_hint_rank": item.provenance["top_section_hint_rank"]}
                        if isinstance(item.provenance.get("top_section_hint_rank"), int)
                        else {}
                    ),
                }
                for item in result.doc_hits
            ],
        )
        self.assertEqual(rebuilt["excerpt_citations"], result.citation_bundle()["excerpt_citations"])
        rebuilt["doc_citations"][0]["doc_id"] = "mutated-doc-id"
        rebuilt["excerpt_citations"][0]["doc_id"] = "mutated-doc-id"

        refreshed = _build_retrieval_citation_bundle_from_payload(payload)
        self.assertNotEqual(refreshed["doc_citations"][0]["doc_id"], "mutated-doc-id")
        self.assertNotEqual(refreshed["excerpt_citations"][0]["doc_id"], "mutated-doc-id")

    def test_doc_and_excerpt_bundle_helpers_rebuild_citations_from_top_level_hits(self) -> None:
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
        payload.pop("retrieval_provenance", None)
        payload.pop("retrieval_citation_bundle", None)
        payload.pop("retrieval_doc_bundle", None)
        payload.pop("retrieval_excerpt_bundle", None)

        rebuilt_doc_bundle = _build_retrieval_doc_bundle_from_payload(payload)
        rebuilt_excerpt_bundle = _build_retrieval_excerpt_bundle_from_payload(payload)

        self.assertEqual(
            rebuilt_doc_bundle["doc_citations"],
            [
                {
                    "doc_id": item.doc_id,
                    "doc_type": item.provenance["doc_type"],
                    "source_hash": item.source_hash,
                    "doc_fingerprint": item.provenance["doc_fingerprint"],
                    "doc_identity_fingerprint": item.provenance["doc_identity_fingerprint"],
                    "doc_rank": item.provenance["doc_rank"],
                    "top_excerpt_id": item.top_excerpt_id,
                    "top_excerpt_fingerprint": item.provenance["top_excerpt_fingerprint"],
                    "top_excerpt_text_hash": item.provenance["top_excerpt_text_hash"],
                    "top_excerpt_span": item.provenance["top_excerpt_span"],
                    "top_excerpt_rank": item.provenance["top_excerpt_rank"],
                    "top_fts_rank": item.provenance["top_fts_rank"],
                    "excerpt_ids": item.provenance["excerpt_ids"],
                    "excerpt_count": item.excerpt_count,
                    "matched_terms": item.provenance["top_matched_terms"],
                    "source_strategy": item.provenance["source_strategy"],
                    "retrieval_backend": item.provenance["retrieval_backend"],
                    "retrieval_mode": item.provenance["retrieval_mode"],
                    **(
                        {"section_hint": item.provenance["section_hint"]}
                        if item.provenance.get("section_hint")
                        else {}
                    ),
                    **(
                        {"top_section_hint_rank": item.provenance["top_section_hint_rank"]}
                        if isinstance(item.provenance.get("top_section_hint_rank"), int)
                        else {}
                    ),
                }
                for item in result.doc_hits
            ],
        )
        self.assertEqual(rebuilt_excerpt_bundle["excerpt_citations"], result.citation_bundle()["excerpt_citations"])
        rebuilt_doc_bundle["doc_citations"][0]["doc_id"] = "mutated-doc-id"
        rebuilt_excerpt_bundle["excerpt_citations"][0]["excerpt_id"] = "mutated-excerpt-id"

        refreshed_doc_bundle = _build_retrieval_doc_bundle_from_payload(payload)
        refreshed_excerpt_bundle = _build_retrieval_excerpt_bundle_from_payload(payload)
        self.assertNotEqual(refreshed_doc_bundle["doc_citations"][0]["doc_id"], "mutated-doc-id")
        self.assertNotEqual(
            refreshed_excerpt_bundle["excerpt_citations"][0]["excerpt_id"],
            "mutated-excerpt-id",
        )

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
                "retrieve_fts_excerpt",
                "fetch_fts_excerpt",
                "fetch_excerpt",
                "retrieve_fts_payload",
                "retrieve_auto_excerpt",
                "retrieve_auto",
                "retrieve_auto_context_bundle",
                "retrieve_auto_citation_bundle",
                "retrieve_auto_source_bundle",
                "retrieve_auto_provenance_bundle",
                "retrieve_auto_doc_bundle",
                "retrieve_auto_excerpt_bundle",
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
        self.assertTrue(hasattr(engine_retrieval, "retrieve_fts_excerpt"))
        self.assertTrue(hasattr(engine_retrieval, "fetch_fts_excerpt"))
        self.assertTrue(hasattr(engine_retrieval, "fetch_excerpt"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_fts_payload"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_auto_excerpt"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_auto_context_bundle"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_auto_source_bundle"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_auto_provenance_bundle"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_auto_excerpt_bundle"))
        self.assertTrue(hasattr(engine_retrieval, "retrieve_auto_payload"))
        self.assertTrue(hasattr(package_retrieval, "retrieve_auto_citation_bundle"))

    def test_fts_strategy_refreshes_same_key_cache_after_uncached_read(self) -> None:
        runner_hits = [["stale-hit"], ["fresh-hit"]]
        strategy = engine_retrieval.FTSStrategy(lambda query, candidate_doc_ids: list(runner_hits.pop(0)))

        cached = strategy.retrieve("theory implications", candidate_doc_ids=("doc-b", "doc-a"))
        refreshed = strategy.retrieve(
            "theory implications",
            candidate_doc_ids=("doc-a", "doc-b"),
            use_cache=False,
        )
        replayed = strategy.retrieve("theory implications", candidate_doc_ids=("doc-b", "doc-a"))

        self.assertFalse(cached.cache_used)
        self.assertEqual(cached.hits, ["stale-hit"])
        self.assertFalse(refreshed.cache_used)
        self.assertEqual(refreshed.hits, ["fresh-hit"])
        self.assertTrue(replayed.cache_used)
        self.assertEqual(replayed.hits, ["fresh-hit"])
        self.assertEqual(runner_hits, [])

    def test_fts_strategy_primes_cache_after_uncached_read_without_prior_entry(self) -> None:
        runner_hits = [["fresh-hit"]]
        strategy = engine_retrieval.FTSStrategy(lambda query, candidate_doc_ids: list(runner_hits.pop(0)))

        uncached = strategy.retrieve(
            "theory implications",
            candidate_doc_ids=("doc-b", "doc-a"),
            use_cache=False,
        )
        replayed = strategy.retrieve("theory implications", candidate_doc_ids=("doc-a", "doc-b"))

        self.assertFalse(uncached.cache_used)
        self.assertEqual(uncached.hits, ["fresh-hit"])
        self.assertTrue(replayed.cache_used)
        self.assertEqual(replayed.hits, ["fresh-hit"])
        self.assertEqual(runner_hits, [])

    def test_fts_strategy_reuses_cache_for_semantically_equivalent_query_objects(self) -> None:
        runner_hits = [["fresh-hit"]]
        strategy = engine_retrieval.FTSStrategy(lambda query, candidate_doc_ids: list(runner_hits.pop(0)))
        compact = RetrievalQuery(
            query_text="discussion theory",
            scope="doc:doc-pdf-1",
            intent="outline_support",
            constraints=RetrievalConstraints(
                max_results=6,
                doc_types=("pdf", "memo"),
                date_range=("2026-01-01", "2026-01-31"),
                section_hint="discussion",
                prefer_exact_matches=True,
            ),
            confidentiality_profile="confidential",
        )
        spaced = RetrievalQuery(
            query_text="  Discussion   Theory  ",
            scope="  DOC:doc-pdf-1  ",
            intent="outline_support",
            constraints=RetrievalConstraints(
                max_results=6,
                doc_types=("Memo", "PDF", "memo"),
                date_range=("2026-01-31", "2026-01-01"),
                section_hint="  discussion  ",
                prefer_exact_matches=True,
            ),
            confidentiality_profile="CONFIDENTIAL",
        )

        first = strategy.retrieve(compact, candidate_doc_ids=("doc-b", "doc-a"))
        replayed = strategy.retrieve(spaced, candidate_doc_ids=("doc-a", "doc-b"))

        self.assertFalse(first.cache_used)
        self.assertEqual(first.hits, ["fresh-hit"])
        self.assertTrue(replayed.cache_used)
        self.assertEqual(replayed.hits, ["fresh-hit"])
        self.assertEqual(runner_hits, [])

    def test_fts_strategy_reuses_cache_between_mapping_query_and_dataclass_defaults(self) -> None:
        runner_hits = [["fresh-hit"]]
        strategy = engine_retrieval.FTSStrategy(lambda query, candidate_doc_ids: list(runner_hits.pop(0)))
        mapping_query = {
            "query_text": "  Discussion   Theory  ",
            "scope": "  DOC:doc-pdf-1  ",
            "intent": "outline_support",
            "constraints": {
                "doc_types": ["PDF", "memo", "pdf"],
                "date_range": ("2026-01-31", "2026-01-01"),
                "section_hint": "  discussion  ",
            },
        }
        dataclass_query = RetrievalQuery(
            query_text="discussion theory",
            scope="doc:doc-pdf-1",
            intent="outline_support",
            constraints=RetrievalConstraints(
                doc_types=("memo", "pdf"),
                date_range=("2026-01-01", "2026-01-31"),
                section_hint="discussion",
            ),
            confidentiality_profile="confidential",
        )

        first = strategy.retrieve(mapping_query, candidate_doc_ids=("doc-b", "doc-a"))
        replayed = strategy.retrieve(dataclass_query, candidate_doc_ids=("doc-a", "doc-b"))

        self.assertFalse(first.cache_used)
        self.assertEqual(first.hits, ["fresh-hit"])
        self.assertTrue(replayed.cache_used)
        self.assertEqual(replayed.hits, ["fresh-hit"])
        self.assertEqual(runner_hits, [])

    def test_fts_strategy_normalizes_candidate_doc_id_whitespace_for_runner_and_cache(self) -> None:
        runner_hits = [["fresh-hit"]]
        captured_candidate_doc_ids: list[tuple[str, ...]] = []

        def runner(query, candidate_doc_ids):
            captured_candidate_doc_ids.append(candidate_doc_ids)
            return list(runner_hits.pop(0))

        strategy = engine_retrieval.FTSStrategy(runner)

        first = strategy.retrieve(
            "discussion theory",
            candidate_doc_ids=(" doc-b ", "doc-a", "doc-a", "", "  "),
        )
        replayed = strategy.retrieve("discussion theory", candidate_doc_ids=("doc-a", "doc-b"))

        self.assertFalse(first.cache_used)
        self.assertEqual(first.hits, ["fresh-hit"])
        self.assertEqual(captured_candidate_doc_ids, [("doc-a", "doc-b")])
        self.assertTrue(replayed.cache_used)
        self.assertEqual(replayed.hits, ["fresh-hit"])
        self.assertEqual(runner_hits, [])

    def test_fts_strategy_normalizes_string_boolean_constraints_in_mapping_queries(self) -> None:
        runner_hits = [["fresh-hit"]]
        strategy = engine_retrieval.FTSStrategy(lambda query, candidate_doc_ids: list(runner_hits.pop(0)))
        mapping_query = {
            "query_text": "discussion theory",
            "scope": "doc:doc-pdf-1",
            "intent": "outline_support",
            "constraints": {
                "max_results": "6",
                "require_citations": "true",
                "prefer_exact_matches": "1",
                "section_hint": "discussion",
            },
            "confidentiality_profile": "CONFIDENTIAL",
        }
        dataclass_query = RetrievalQuery(
            query_text="discussion theory",
            scope="doc:doc-pdf-1",
            intent="outline_support",
            constraints=RetrievalConstraints(
                max_results=6,
                require_citations=True,
                section_hint="discussion",
                prefer_exact_matches=True,
            ),
            confidentiality_profile="confidential",
        )

        first = strategy.retrieve(mapping_query, candidate_doc_ids=("doc-a",))
        replayed = strategy.retrieve(dataclass_query, candidate_doc_ids=("doc-a",))

        self.assertFalse(first.cache_used)
        self.assertEqual(first.hits, ["fresh-hit"])
        self.assertTrue(replayed.cache_used)
        self.assertEqual(replayed.hits, ["fresh-hit"])
        self.assertEqual(runner_hits, [])

    def test_fts_strategy_normalizes_reversed_date_ranges_in_mapping_queries(self) -> None:
        runner_hits = [["fresh-hit"]]
        strategy = engine_retrieval.FTSStrategy(lambda query, candidate_doc_ids: list(runner_hits.pop(0)))
        mapping_query = {
            "query_text": "discussion theory",
            "scope": "vault",
            "intent": "outline_support",
            "constraints": {
                "max_results": 6,
                "date_range": ["2026-01-31", "2026-01-01"],
            },
            "confidentiality_profile": "CONFIDENTIAL",
        }
        dataclass_query = RetrievalQuery(
            query_text="discussion theory",
            scope="vault",
            intent="outline_support",
            constraints=RetrievalConstraints(
                max_results=6,
                date_range=("2026-01-01", "2026-01-31"),
            ),
            confidentiality_profile="confidential",
        )

        first = strategy.retrieve(mapping_query, candidate_doc_ids=("doc-a",))
        replayed = strategy.retrieve(dataclass_query, candidate_doc_ids=("doc-a",))

        self.assertFalse(first.cache_used)
        self.assertEqual(first.hits, ["fresh-hit"])
        self.assertTrue(replayed.cache_used)
        self.assertEqual(replayed.hits, ["fresh-hit"])
        self.assertEqual(runner_hits, [])

    def test_fts_strategy_does_not_alias_case_distinct_scoped_ids_in_cache(self) -> None:
        runner_hits = [["upper-hit"], ["lower-hit"]]
        strategy = engine_retrieval.FTSStrategy(lambda query, candidate_doc_ids: list(runner_hits.pop(0)))
        upper_scope = RetrievalQuery(
            query_text="discussion theory",
            scope="doc:Doc-PDF-1",
            intent="outline_support",
            constraints=RetrievalConstraints(max_results=6),
            confidentiality_profile="confidential",
        )
        lower_scope = RetrievalQuery(
            query_text="discussion theory",
            scope="doc:doc-pdf-1",
            intent="outline_support",
            constraints=RetrievalConstraints(max_results=6),
            confidentiality_profile="confidential",
        )

        first = strategy.retrieve(upper_scope, candidate_doc_ids=("doc-a",))
        second = strategy.retrieve(lower_scope, candidate_doc_ids=("doc-a",))

        self.assertFalse(first.cache_used)
        self.assertEqual(first.hits, ["upper-hit"])
        self.assertFalse(second.cache_used)
        self.assertEqual(second.hits, ["lower-hit"])
        self.assertEqual(runner_hits, [])

    def test_fts_strategy_does_not_alias_case_distinct_unknown_scopes_in_cache(self) -> None:
        runner_hits = [["upper-hit"], ["lower-hit"]]
        strategy = engine_retrieval.FTSStrategy(lambda query, candidate_doc_ids: list(runner_hits.pop(0)))
        upper_scope = RetrievalQuery(
            query_text="discussion theory",
            scope="Project:Alpha",
            intent="outline_support",
            constraints=RetrievalConstraints(max_results=6),
            confidentiality_profile="confidential",
        )
        lower_scope = RetrievalQuery(
            query_text="discussion theory",
            scope="project:alpha",
            intent="outline_support",
            constraints=RetrievalConstraints(max_results=6),
            confidentiality_profile="confidential",
        )

        first = strategy.retrieve(upper_scope, candidate_doc_ids=("doc-a",))
        second = strategy.retrieve(lower_scope, candidate_doc_ids=("doc-a",))

        self.assertFalse(first.cache_used)
        self.assertEqual(first.hits, ["upper-hit"])
        self.assertFalse(second.cache_used)
        self.assertEqual(second.hits, ["lower-hit"])
        self.assertEqual(runner_hits, [])

    def test_retrieve_auto_invalidates_fts_cache_after_document_update(self) -> None:
        query = RetrievalQuery(
            query_text="theory implications",
            scope="vault",
            intent="lookup",
            constraints=RetrievalConstraints(max_results=5),
            confidentiality_profile="confidential",
        )

        initial = self.service.retrieve_auto(query)
        self.assertTrue(any(hit.doc_id == "doc-pdf-1" for hit in initial.hits))

        self.service.add_or_update_document(
            doc_id="doc-pdf-1",
            doc_type="pdf",
            title_hint="Interview Packet Revised",
            text="Methods section with recruitment constraints and ethics notes only.",
        )

        refreshed = self.service.retrieve_auto(query)
        self.assertFalse(any(hit.doc_id == "doc-pdf-1" for hit in refreshed.hits))
        self.assertNotEqual(initial.result_fingerprint, refreshed.result_fingerprint)
        self.assertNotEqual(
            initial.diagnostics["excerpt_hits_fingerprint"],
            refreshed.diagnostics["excerpt_hits_fingerprint"],
        )

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
        self.assertEqual(engine_query.query_text, "memo comparison")
        self.assertEqual(engine_query.constraints.doc_types, ("memo", "pdf"))
        self.assertEqual(engine_query.constraints.date_range, ("2026-01-01", "2026-01-31"))
        self.assertEqual(engine_query.constraints.section_hint, "discussion")
        self.assertEqual(engine_query.scope, "vault")
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

    def test_retrieval_query_constructor_normalizes_scope_whitespace(self) -> None:
        engine_query = engine_retrieval.build_retrieval_query(
            query_text="memo comparison",
            scope="  doc:doc-memo-1  ",
            intent="compare",
            constraints={"max_results": 4},
            confidentiality_profile="standard",
        )
        package_query = package_retrieval.build_retrieval_query(
            query_text="memo comparison",
            scope="  doc:doc-memo-1  ",
            intent="compare",
            constraints={"max_results": 4},
            confidentiality_profile="standard",
        )

        self.assertEqual(engine_query, package_query)
        self.assertEqual(engine_query.scope, "doc:doc-memo-1")

    def test_retrieval_query_constructor_normalizes_scope_prefix_case(self) -> None:
        engine_query = engine_retrieval.build_retrieval_query(
            query_text="memo comparison",
            scope="  DOC:doc-memo-1  ",
            intent="compare",
            constraints={"max_results": 4},
            confidentiality_profile="standard",
        )
        package_query = package_retrieval.build_retrieval_query(
            query_text="memo comparison",
            scope=" Vault ",
            intent="compare",
            constraints={"max_results": 4},
            confidentiality_profile="standard",
        )

        self.assertEqual(engine_query.scope, "doc:doc-memo-1")
        self.assertEqual(package_query.scope, "vault")

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
        self.assertEqual(bundle["basket_promotion"], result.to_downstream_payload()["basket_promotion"])
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
        bundle["basket_promotion"]["doc_id"] = "mutated-doc-id"
        refreshed = engine_build_retrieval_context_bundle_from_result(result)
        self.assertNotEqual(refreshed["basket_promotion"]["doc_id"], "mutated-doc-id")

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

    def test_retrieval_provenance_helper_backfills_sparse_source_bundle_provenance_fields(self) -> None:
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
        retrieval_provenance = sparse_source_bundle.get("retrieval_provenance")
        self.assertIsInstance(retrieval_provenance, dict)
        retrieval_provenance["query_scope"] = None
        retrieval_provenance["query_intent"] = None
        retrieval_provenance["query_confidentiality_profile"] = None
        retrieval_provenance["active_strategy_ids"] = []
        retrieval_provenance["deferred_strategy_ids"] = []
        retrieval_provenance["fts_shortlist_doc_ids"] = []
        retrieval_provenance["primary_doc_id"] = None
        retrieval_provenance["primary_doc_fingerprint"] = None
        retrieval_provenance["primary_doc_identity_fingerprint"] = None
        retrieval_provenance["primary_excerpt_id"] = None
        retrieval_provenance["primary_excerpt_fingerprint"] = None
        retrieval_provenance["primary_excerpt_text_hash"] = None
        retrieval_provenance["citation_status"] = {}
        retrieval_provenance["doc_count"] = None
        retrieval_provenance["excerpt_count"] = None
        retrieval_provenance["doc_citations"] = []
        retrieval_provenance["excerpt_citations"] = []

        provenance = build_retrieval_provenance_from_result(
            _SparseSourceBundleOnlySource(sparse_source_bundle)
        )

        self.assertEqual(provenance, result.retrieval_provenance_bundle())

    def test_retrieval_provenance_helper_backfills_primary_fingerprints_from_citations(self) -> None:
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

        sparse_source_bundle = json.loads(json.dumps(result.source_bundle()))
        retrieval_provenance = sparse_source_bundle.get("retrieval_provenance")
        self.assertIsInstance(retrieval_provenance, dict)
        self.assertEqual(
            retrieval_provenance.get("primary_doc_id"),
            result.retrieval_provenance_bundle()["primary_doc_id"],
        )
        self.assertEqual(
            retrieval_provenance.get("primary_excerpt_id"),
            result.retrieval_provenance_bundle()["primary_excerpt_id"],
        )
        retrieval_provenance["primary_doc_fingerprint"] = None
        retrieval_provenance["primary_doc_identity_fingerprint"] = None
        retrieval_provenance["primary_excerpt_fingerprint"] = None
        retrieval_provenance["primary_excerpt_provenance_fingerprint"] = None
        retrieval_provenance["primary_excerpt_text_hash"] = None

        provenance = build_retrieval_provenance_from_result(
            _SourceBundleOnlySource(sparse_source_bundle)
        )

        self.assertEqual(
            provenance["primary_doc_id"],
            result.retrieval_provenance_bundle()["primary_doc_id"],
        )
        self.assertEqual(
            provenance["primary_excerpt_id"],
            result.retrieval_provenance_bundle()["primary_excerpt_id"],
        )
        self.assertEqual(
            provenance["primary_doc_fingerprint"],
            result.retrieval_provenance_bundle()["primary_doc_fingerprint"],
        )
        self.assertEqual(
            provenance["primary_doc_identity_fingerprint"],
            result.retrieval_provenance_bundle()["primary_doc_identity_fingerprint"],
        )
        self.assertEqual(
            provenance["primary_excerpt_fingerprint"],
            result.retrieval_provenance_bundle()["primary_excerpt_fingerprint"],
        )
        self.assertEqual(
            provenance["primary_excerpt_provenance_fingerprint"],
            result.retrieval_provenance_bundle()["primary_excerpt_provenance_fingerprint"],
        )
        self.assertEqual(
            provenance["primary_excerpt_text_hash"],
            result.retrieval_provenance_bundle()["primary_excerpt_text_hash"],
        )

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
        retrieval_summary.pop("top_excerpt_ids", None)
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

    def test_retrieval_downstream_payload_helper_normalizes_evidence_strategy_ids_from_source_bundle(self) -> None:
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

        mutated_source_bundle = json.loads(json.dumps(result.source_bundle()))
        retrieval_evidence = mutated_source_bundle.get("retrieval_evidence")
        self.assertIsInstance(retrieval_evidence, dict)
        retrieval_evidence["active_strategy_ids"] = ["fts", " fts ", "", None]
        retrieval_evidence["deferred_strategy_ids"] = ["pageindex", " embeddings ", "pageindex", None]

        payload = build_retrieval_downstream_payload_from_result(
            _SourceBundleOnlySource(mutated_source_bundle)
        )

        self.assertEqual(payload["retrieval_evidence"]["active_strategy_ids"], ["fts"])
        self.assertEqual(
            payload["retrieval_evidence"]["deferred_strategy_ids"],
            ["pageindex", "embeddings"],
        )
        self.assertEqual(payload["retrieval_provenance"]["active_strategy_ids"], ["fts"])
        self.assertEqual(
            payload["retrieval_provenance"]["deferred_strategy_ids"],
            ["pageindex", "embeddings"],
        )

    def test_retrieval_downstream_payload_helper_normalizes_nested_citation_fields(self) -> None:
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

        mutated_source_bundle = json.loads(json.dumps(result.source_bundle()))
        retrieval_citation_bundle = mutated_source_bundle.get("retrieval_citation_bundle")
        self.assertIsInstance(retrieval_citation_bundle, dict)

        doc_citations = retrieval_citation_bundle.get("doc_citations")
        self.assertIsInstance(doc_citations, list)
        self.assertTrue(doc_citations)
        first_doc_citation = doc_citations[0]
        self.assertIsInstance(first_doc_citation, dict)
        first_doc_citation["excerpt_ids"] = (
            first_doc_citation["excerpt_ids"][0],
            "  ",
            first_doc_citation["excerpt_ids"][0],
        )
        first_doc_citation["matched_terms"] = {
            " memo ",
            "comparison",
            "memo",
        }
        first_doc_citation["top_excerpt_span"] = {"char_range": {"start": 25, "end": 5}}
        first_doc_citation["section_hint"] = "  Findings  "

        excerpt_citations = retrieval_citation_bundle.get("excerpt_citations")
        self.assertIsInstance(excerpt_citations, list)
        self.assertTrue(excerpt_citations)
        first_excerpt_citation = excerpt_citations[0]
        self.assertIsInstance(first_excerpt_citation, dict)
        first_excerpt_citation["matched_terms"] = {
            " coding ",
            "comparison",
            "coding",
        }
        first_excerpt_citation["span"] = {"char_range": {"start": 40, "end": 10}}
        first_excerpt_citation["section_hint"] = "  Findings  "

        retrieval_provenance = mutated_source_bundle.get("retrieval_provenance")
        self.assertIsInstance(retrieval_provenance, dict)
        provenance_doc_citations = retrieval_provenance.get("doc_citations")
        self.assertIsInstance(provenance_doc_citations, list)
        self.assertTrue(provenance_doc_citations)
        first_provenance_doc_citation = provenance_doc_citations[0]
        self.assertIsInstance(first_provenance_doc_citation, dict)
        first_provenance_doc_citation["excerpt_ids"] = (
            first_provenance_doc_citation["excerpt_ids"][0],
            "  ",
            first_provenance_doc_citation["excerpt_ids"][0],
        )
        first_provenance_doc_citation["matched_terms"] = {
            " memo ",
            "comparison",
            "memo",
        }
        first_provenance_doc_citation["top_excerpt_span"] = {"char_range": {"start": 25, "end": 5}}
        first_provenance_doc_citation["section_hint"] = "  Findings  "

        provenance_excerpt_citations = retrieval_provenance.get("excerpt_citations")
        self.assertIsInstance(provenance_excerpt_citations, list)
        self.assertTrue(provenance_excerpt_citations)
        first_provenance_excerpt_citation = provenance_excerpt_citations[0]
        self.assertIsInstance(first_provenance_excerpt_citation, dict)
        first_provenance_excerpt_citation["matched_terms"] = {
            " coding ",
            "comparison",
            "coding",
        }
        first_provenance_excerpt_citation["span"] = {"char_range": {"start": 40, "end": 10}}
        first_provenance_excerpt_citation["section_hint"] = "  Findings  "

        payload = build_retrieval_downstream_payload_from_result(
            _SourceBundleOnlySource(mutated_source_bundle)
        )

        expected_doc_excerpt_ids = [first_doc_citation["excerpt_ids"][0]]
        expected_excerpt_matched_terms = ["coding", "comparison"]
        expected_doc_span = {"char_range": {"start": 5, "end": 25}}
        expected_excerpt_span = {"char_range": {"start": 10, "end": 40}}
        expected_section_hint = "Findings"
        doc_matched_terms = payload["retrieval_citation_bundle"]["doc_citations"][0]["matched_terms"]
        self.assertIsInstance(doc_matched_terms, list)
        self.assertEqual(len(doc_matched_terms), len(set(doc_matched_terms)))
        self.assertEqual([term.strip() for term in doc_matched_terms], doc_matched_terms)

        for field in (
            payload["retrieval_citation_bundle"]["doc_citations"][0],
            payload["retrieval_provenance"]["doc_citations"][0],
        ):
            self.assertEqual(field["excerpt_ids"], expected_doc_excerpt_ids)
            self.assertEqual(field["matched_terms"], doc_matched_terms)
            self.assertEqual(field["top_excerpt_span"], expected_doc_span)
            self.assertEqual(field["section_hint"], expected_section_hint)

        for field in (
            payload["retrieval_citation_bundle"]["excerpt_citations"][0],
            payload["retrieval_provenance"]["excerpt_citations"][0],
        ):
            self.assertEqual(field["matched_terms"], expected_excerpt_matched_terms)
            self.assertEqual(field["span"], expected_excerpt_span)
            self.assertEqual(field["section_hint"], expected_section_hint)

    def test_retrieval_downstream_payload_helper_backfills_basket_promotion_from_top_level_hits(self) -> None:
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

        sparse_source_bundle = json.loads(json.dumps(result.source_bundle()))
        basket_promotion = sparse_source_bundle.get("basket_promotion")
        self.assertIsInstance(basket_promotion, dict)
        basket_promotion["doc_fingerprint"] = None
        basket_promotion["doc_identity_fingerprint"] = None
        basket_promotion["source_hash"] = None
        basket_promotion["excerpt_fingerprint"] = None
        basket_promotion["excerpt_text_hash"] = None
        basket_promotion["span"] = None

        excerpt_hits = sparse_source_bundle.get("excerpt_hits")
        self.assertIsInstance(excerpt_hits, list)
        self.assertTrue(excerpt_hits)
        first_excerpt_hit = excerpt_hits[0]
        self.assertIsInstance(first_excerpt_hit, dict)
        excerpt_provenance = first_excerpt_hit.get("provenance")
        self.assertIsInstance(excerpt_provenance, dict)
        excerpt_provenance.pop("doc_fingerprint", None)
        excerpt_provenance.pop("doc_identity_fingerprint", None)
        excerpt_provenance.pop("source_hash", None)
        excerpt_provenance.pop("excerpt_fingerprint", None)
        excerpt_provenance.pop("excerpt_text_hash", None)
        excerpt_provenance.pop("hash", None)
        excerpt_provenance.pop("span", None)

        payload = build_retrieval_downstream_payload_from_result(
            _SourceBundleOnlySource(sparse_source_bundle)
        )

        self.assertEqual(payload["basket_promotion"], result.to_downstream_payload()["basket_promotion"])

    def test_retrieval_downstream_payload_helper_backfills_basket_promotion_from_nested_bundles(self) -> None:
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

        sparse_source_bundle = json.loads(json.dumps(result.source_bundle()))
        sparse_source_bundle["doc_hits"] = []
        sparse_source_bundle["excerpt_hits"] = []
        basket_promotion = sparse_source_bundle.get("basket_promotion")
        self.assertIsInstance(basket_promotion, dict)
        basket_promotion["doc_id"] = None
        basket_promotion["doc_fingerprint"] = None
        basket_promotion["doc_identity_fingerprint"] = None
        basket_promotion["source_hash"] = None
        basket_promotion["excerpt_id"] = None
        basket_promotion["excerpt_fingerprint"] = None
        basket_promotion["excerpt_text_hash"] = None
        basket_promotion["span"] = None

        payload = build_retrieval_downstream_payload_from_result(
            _SourceBundleOnlySource(sparse_source_bundle)
        )

        self.assertEqual(payload["basket_promotion"], result.to_downstream_payload()["basket_promotion"])

    def test_retrieval_downstream_payload_helper_backfills_doc_only_basket_policy_fields(self) -> None:
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

        sparse_source_bundle = json.loads(json.dumps(result.source_bundle()))
        sparse_source_bundle["retrieval_backend"] = None
        sparse_source_bundle["retrieval_mode"] = None
        sparse_source_bundle["excerpt_hits"] = []

        retrieval_excerpt_bundle = sparse_source_bundle.get("retrieval_excerpt_bundle")
        self.assertIsInstance(retrieval_excerpt_bundle, dict)
        retrieval_excerpt_bundle["excerpt_hits"] = []

        retrieval_citation_bundle = sparse_source_bundle.get("retrieval_citation_bundle")
        self.assertIsInstance(retrieval_citation_bundle, dict)
        retrieval_citation_bundle["excerpt_citations"] = []
        retrieval_citation_bundle["retrieval_backend"] = None
        retrieval_citation_bundle["retrieval_mode"] = None

        retrieval_provenance = sparse_source_bundle.get("retrieval_provenance")
        self.assertIsInstance(retrieval_provenance, dict)
        retrieval_provenance["primary_excerpt_id"] = None
        retrieval_provenance["primary_excerpt_fingerprint"] = None
        retrieval_provenance["primary_excerpt_provenance_fingerprint"] = None
        retrieval_provenance["primary_excerpt_text_hash"] = None
        retrieval_provenance["excerpt_citations"] = []
        retrieval_provenance["retrieval_backend"] = None
        retrieval_provenance["retrieval_mode"] = None

        basket_promotion = sparse_source_bundle.get("basket_promotion")
        self.assertIsInstance(basket_promotion, dict)
        basket_promotion["retrieval_backend"] = None
        basket_promotion["retrieval_mode"] = None

        payload = build_retrieval_downstream_payload_from_result(
            _SourceBundleOnlySource(sparse_source_bundle)
        )

        self.assertEqual(
            payload["basket_promotion"]["retrieval_backend"],
            result.to_downstream_payload()["basket_promotion"]["retrieval_backend"],
        )
        self.assertEqual(
            payload["basket_promotion"]["retrieval_mode"],
            result.to_downstream_payload()["basket_promotion"]["retrieval_mode"],
        )

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

    def test_result_citation_and_evidence_snapshots_are_copy_safe(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo coding comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        citation_bundle = result.citation_bundle()
        evidence = result.to_downstream_payload()["retrieval_evidence"]

        citation_bundle["excerpt_citations"][0]["matched_terms"].append("mutated-term")
        cast(dict[str, object], citation_bundle["excerpt_citations"][0]["span"])["char_range"] = {
            "start": -1,
            "end": -1,
        }
        evidence["doc_citations"][0]["matched_terms"].append("mutated-term")
        cast(dict[str, object], evidence["doc_citations"][0]["top_excerpt_span"])["char_range"] = {
            "start": -1,
            "end": -1,
        }
        evidence["excerpt_citations"][0]["matched_terms"].append("mutated-term")
        cast(dict[str, object], evidence["excerpt_citations"][0]["span"])["char_range"] = {
            "start": -1,
            "end": -1,
        }

        refreshed_citation_bundle = result.citation_bundle()
        refreshed_evidence = result.to_downstream_payload()["retrieval_evidence"]

        self.assertNotIn(
            "mutated-term",
            refreshed_citation_bundle["excerpt_citations"][0]["matched_terms"],
        )
        self.assertNotEqual(
            refreshed_citation_bundle["excerpt_citations"][0]["span"]["char_range"],
            {"start": -1, "end": -1},
        )
        self.assertNotIn(
            "mutated-term",
            refreshed_evidence["doc_citations"][0]["matched_terms"],
        )
        self.assertNotEqual(
            refreshed_evidence["doc_citations"][0]["top_excerpt_span"]["char_range"],
            {"start": -1, "end": -1},
        )
        self.assertNotIn(
            "mutated-term",
            refreshed_evidence["excerpt_citations"][0]["matched_terms"],
        )
        self.assertNotEqual(
            refreshed_evidence["excerpt_citations"][0]["span"]["char_range"],
            {"start": -1, "end": -1},
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
        self.assertEqual(provenance["query_confidentiality_profile"], "confidential")
        self.assertEqual(provenance["retrieval_backend"], "sqlite_fts")
        self.assertEqual(provenance["retrieval_mode"], "fts_first")

    def test_retrieval_evidence_surfaces_query_context_and_shortlist(self) -> None:
        updated_at = self.service._load_doc_meta()["doc-pdf-1"]["updated_at"]
        self.assertIsInstance(updated_at, str)
        query_day = str(updated_at)[:10]

        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="theory implications",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(
                    max_results=4,
                    date_range=(query_day, query_day),
                ),
                confidentiality_profile="confidential",
            )
        )

        evidence = result.to_downstream_payload()["retrieval_evidence"]
        self.assertEqual(evidence["query_fingerprint"], result.diagnostics["query_fingerprint"])
        self.assertEqual(evidence["query_scope"], "vault")
        self.assertEqual(evidence["query_intent"], "compare")
        self.assertEqual(evidence["query_confidentiality_profile"], "confidential")
        self.assertEqual(evidence["query_date_range"], [query_day, query_day])
        self.assertEqual(evidence["candidate_doc_count"], result.diagnostics["candidate_doc_count"])
        self.assertEqual(evidence["fts_shortlist_doc_ids"], result.diagnostics["fts_shortlist_doc_ids"])
        self.assertEqual(evidence["retrieval_backend"], "sqlite_fts")
        self.assertEqual(evidence["retrieval_mode"], "fts_first")
        self.assertEqual(evidence["doc_citations"], result.evidence["doc_citations"])
        self.assertEqual(evidence["excerpt_citations"], result.evidence["excerpt_citations"])
        self.assertEqual(
            evidence["doc_citations"],
            [
                {
                    "doc_id": item.doc_id,
                    "doc_type": item.provenance["doc_type"],
                    "source_hash": item.source_hash,
                    "doc_fingerprint": item.provenance["doc_fingerprint"],
                    "doc_identity_fingerprint": item.provenance["doc_identity_fingerprint"],
                    "doc_rank": item.provenance["doc_rank"],
                    "top_excerpt_id": item.top_excerpt_id,
                    "top_excerpt_fingerprint": item.provenance["top_excerpt_fingerprint"],
                    "top_excerpt_text_hash": item.provenance["top_excerpt_text_hash"],
                    "top_excerpt_span": item.provenance["top_excerpt_span"],
                    "top_excerpt_rank": item.provenance["top_excerpt_rank"],
                    "top_fts_rank": item.provenance["top_fts_rank"],
                    "excerpt_ids": item.provenance["excerpt_ids"],
                    "excerpt_count": item.excerpt_count,
                    "matched_terms": item.provenance["top_matched_terms"],
                    "source_strategy": item.provenance["source_strategy"],
                    "retrieval_backend": item.provenance["retrieval_backend"],
                    "retrieval_mode": item.provenance["retrieval_mode"],
                    **(
                        {"section_hint": item.provenance["section_hint"]}
                        if item.provenance.get("section_hint")
                        else {}
                    ),
                    **(
                        {"top_section_hint_rank": item.provenance["top_section_hint_rank"]}
                        if isinstance(item.provenance.get("top_section_hint_rank"), int)
                        else {}
                    ),
                }
                for item in result.doc_hits
            ],
        )

    def test_retrieve_auto_citation_bundle_surfaces_rich_doc_provenance(self) -> None:
        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="memo comparison",
                scope="vault",
                intent="compare",
                constraints=RetrievalConstraints(max_results=4),
                confidentiality_profile="confidential",
            )
        )

        citation_bundle = result.citation_bundle()
        self.assertEqual(
            citation_bundle["doc_citations"],
            [
                {
                    "doc_id": item.doc_id,
                    "doc_type": item.provenance["doc_type"],
                    "source_hash": item.source_hash,
                    "doc_fingerprint": item.provenance["doc_fingerprint"],
                    "doc_identity_fingerprint": item.provenance["doc_identity_fingerprint"],
                    "doc_rank": item.provenance["doc_rank"],
                    "top_excerpt_id": item.top_excerpt_id,
                    "top_excerpt_fingerprint": item.provenance["top_excerpt_fingerprint"],
                    "top_excerpt_text_hash": item.provenance["top_excerpt_text_hash"],
                    "top_excerpt_span": item.provenance["top_excerpt_span"],
                    "top_excerpt_rank": item.provenance["top_excerpt_rank"],
                    "top_fts_rank": item.provenance["top_fts_rank"],
                    "excerpt_ids": item.provenance["excerpt_ids"],
                    "excerpt_count": item.excerpt_count,
                    "matched_terms": item.provenance["top_matched_terms"],
                    "source_strategy": item.provenance["source_strategy"],
                    "retrieval_backend": item.provenance["retrieval_backend"],
                    "retrieval_mode": item.provenance["retrieval_mode"],
                    **(
                        {"section_hint": item.provenance["section_hint"]}
                        if item.provenance.get("section_hint")
                        else {}
                    ),
                    **(
                        {"top_section_hint_rank": item.provenance["top_section_hint_rank"]}
                        if isinstance(item.provenance.get("top_section_hint_rank"), int)
                        else {}
                    ),
                }
                for item in result.doc_hits
            ],
        )
        self.assertEqual(
            result.to_downstream_payload()["retrieval_provenance"]["doc_citations"],
            citation_bundle["doc_citations"],
        )

    def test_date_range_shortlist_keeps_late_qualifying_docs_in_fts_order(self) -> None:
        for index in range(120):
            self.service.add_or_update_document(
                doc_id=f"doc-{index:03d}",
                doc_type="memo",
                title_hint=f"Memo {index:03d}",
                text="date constrained needle evidence repeated for shortlist coverage",
            )
        self.service.add_or_update_document(
            doc_id="doc-zzz-target",
            doc_type="memo",
            title_hint="Target Memo",
            text="date constrained needle evidence repeated for shortlist coverage",
        )

        meta = self.service._load_doc_meta()
        for doc_id, payload in meta.items():
            if not doc_id.startswith("doc-") and doc_id != "doc-zzz-target":
                continue
            payload["updated_at"] = "2026-01-01T12:00:00+00:00"
        meta["doc-zzz-target"]["updated_at"] = "2026-02-15T12:00:00+00:00"
        self.service._write_encrypted_json(self.service._root / "doc_meta_v1.enc.json", meta)

        result = self.service.retrieve_auto(
            RetrievalQuery(
                query_text="date constrained needle",
                scope="vault",
                intent="lookup",
                constraints=RetrievalConstraints(
                    max_results=1,
                    date_range=("2026-02-15", "2026-02-15"),
                    doc_types=("memo",),
                ),
                confidentiality_profile="confidential",
            )
        )

        self.assertEqual([doc_hit.doc_id for doc_hit in result.doc_hits], ["doc-zzz-target"])
        self.assertEqual([hit.doc_id for hit in result.hits], ["doc-zzz-target"])
        self.assertEqual(result.diagnostics["fts_shortlist_doc_ids"], ["doc-zzz-target"])
        self.assertEqual(result.diagnostics["candidate_doc_count"], 1)

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
                    "doc_type": item["provenance"]["doc_type"],
                    "source_hash": item["source_hash"],
                    "doc_fingerprint": item["provenance"]["doc_fingerprint"],
                    "doc_identity_fingerprint": item["provenance"]["doc_identity_fingerprint"],
                    "doc_rank": item["provenance"]["doc_rank"],
                    "top_excerpt_id": item["top_excerpt_id"],
                    "top_excerpt_fingerprint": item["provenance"]["top_excerpt_fingerprint"],
                    "top_excerpt_text_hash": item["provenance"]["top_excerpt_text_hash"],
                    "top_excerpt_span": item["provenance"]["top_excerpt_span"],
                    "top_excerpt_rank": item["provenance"]["top_excerpt_rank"],
                    "top_fts_rank": item["provenance"]["top_fts_rank"],
                    "excerpt_ids": item["provenance"]["excerpt_ids"],
                    "excerpt_count": item["excerpt_count"],
                    "matched_terms": item["provenance"]["top_matched_terms"],
                    "source_strategy": item["provenance"]["source_strategy"],
                    "retrieval_backend": item["provenance"]["retrieval_backend"],
                    "retrieval_mode": item["provenance"]["retrieval_mode"],
                    **(
                        {"section_hint": item["provenance"]["section_hint"]}
                        if item["provenance"].get("section_hint")
                        else {}
                    ),
                    **(
                        {"top_section_hint_rank": item["provenance"]["top_section_hint_rank"]}
                        if isinstance(item["provenance"].get("top_section_hint_rank"), int)
                        else {}
                    ),
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
                    "doc_type": item["provenance"]["doc_type"],
                    "source_hash": item["source_hash"],
                    "excerpt_fingerprint": item["provenance"]["excerpt_fingerprint"],
                    "excerpt_provenance_fingerprint": item["provenance"]["excerpt_provenance_fingerprint"],
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
            payload["excerpt_hits"][0]["excerpt_provenance_fingerprint"],
            payload["excerpt_hits"][0]["provenance"]["excerpt_provenance_fingerprint"],
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
