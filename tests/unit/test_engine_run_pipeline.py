from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone

from src.qual.audit import AuditLog
from src.qual.drafting.service import DraftingService
from src.qual.engine.run_pipeline import (
    EngineRunFlowResult,
    EngineRunRecord,
    EngineRunService,
    RunArtifact,
    RunEvent,
)
from src.qual.exporting.service import (
    ExportConfidentiality,
    ExportInclude,
    ExportLimits,
    ExportMetadata,
    ExportOptions,
    ExportScope,
    ExportService,
)
from src.qual.retrieval.service import RetrievalService


class EngineRunPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.audit = AuditLog(self.root)
        self.retrieval = RetrievalService(self.root, audit_log=self.audit)
        self.retrieval.add_or_update_document(
            doc_id="doc-1",
            doc_type="memo",
            title_hint="Run Notes",
            text="alpha evidence beta detail gamma summary",
        )
        self.export = ExportService(self.root, audit_log=self.audit)
        self.service = EngineRunService(
            vault_root=self.root,
            audit_log=self.audit,
            retrieval_service=self.retrieval,
            export_service=self.export,
            drafting_service=DraftingService(),
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_run_pipeline_keeps_artifacts_and_events_in_deterministic_order(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-1",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )

        retrieval = self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        patch = self.service.propose_patch(
            run.run_id,
            original="line one\n",
            proposed="line one\nline two\n",
            target_path="notes.md",
        )
        decision = self.service.record_patch_decision(
            run.run_id,
            decision="accepted",
            target_path="notes.md",
            reason="validated",
        )
        preview = self.service.preview_export(run.run_id, options=self._options())
        final_artifact = self.service.final_export(
            run.run_id,
            options=self._options(output_format="docx", confidentiality_profile="standard"),
            destination_path=self.root / "exports" / "draft.docx",
            export_approved=True,
        )
        completed = self.service.complete_run(run.run_id)

        self.assertTrue(retrieval.hits)
        self.assertIn("@@", patch)
        self.assertEqual(decision.name, "patch_applied")
        self.assertEqual(preview.output_format, "pdf")
        self.assertEqual(final_artifact.output_format, "docx")
        self.assertEqual(completed.status, "completed")

        stored = self.service.get_run(run.run_id)
        self.assertEqual(
            [artifact.kind for artifact in stored.artifacts],
            [
                "run_started",
                "run_plan",
                "retrieval_result",
                "patch_proposal",
                "patch_decision",
                "export_preview",
                "export_final",
                "run_provenance",
                "run_completed",
            ],
        )
        self.assertEqual(
            [event.name for event in stored.events],
            [
                "run_started",
                "run_planned",
                "retrieval_attached",
                "patch_proposed",
                "patch_applied",
                "export_preview_attached",
                "export_final_attached",
                "run_provenance_captured",
                "run_completed",
            ],
        )
        self.assertEqual(stored.artifacts[0].artifact_id, f"{run.run_id}:0001:run_started")
        self.assertEqual(stored.artifacts[1].artifact_id, f"{run.run_id}:0002:run_plan")
        self.assertEqual(stored.artifacts[2].artifact_id, f"{run.run_id}:0003:retrieval_result")
        self.assertEqual(stored.artifacts[4].artifact_id, f"{run.run_id}:0005:patch_decision")
        self.assertEqual(stored.artifacts[5].artifact_id, f"{run.run_id}:0006:export_preview")
        self.assertEqual(stored.artifacts[6].artifact_id, f"{run.run_id}:0007:export_final")
        self.assertEqual(stored.artifacts[7].artifact_id, f"{run.run_id}:0008:run_provenance")
        self.assertEqual(stored.artifacts[8].artifact_id, f"{run.run_id}:0009:run_completed")
        self.assertEqual(stored.events[-2].event_id, f"{run.run_id}:0008:run_provenance_captured")
        self.assertEqual(stored.events[-1].event_id, f"{run.run_id}:0009:run_completed")
        self.assertEqual(stored.artifacts[0].payload["status"], "running")
        self.assertEqual(stored.artifacts[0].payload["started_at"], stored.events[0].payload["started_at"])
        self.assertEqual(stored.artifacts[1].payload["plan_digest"], stored.events[1].payload["plan_digest"])
        self.assertEqual(stored.artifacts[2].payload["audit_ref"], retrieval.audit_ref)
        self.assertEqual(stored.artifacts[2].payload["retrieval_query_hash"], self.service._fingerprint_text("alpha summary"))
        self.assertEqual(
            stored.artifacts[2].payload["retrieval_constraints"],
            {
                "max_results": 10,
                "section_hint": None,
                "prefer_exact_matches": False,
            },
        )
        self.assertEqual(stored.artifacts[4].payload["decision"], "accepted")
        self.assertEqual(stored.artifacts[4].payload["decision_event_id"], f"{run.run_id}:0005:patch_applied")
        self.assertEqual(stored.events[4].payload["decision_event_id"], f"{run.run_id}:0005:patch_applied")
        self.assertEqual(
            stored.artifacts[5].payload["retrieval_evidence"],
            {
                "artifact_id": f"{run.run_id}:0003:retrieval_result",
                "audit_ref": retrieval.audit_ref,
                "query_scope": "doc:doc-1",
                "query_intent": "lookup",
                "retrieval_query_hash": self.service._fingerprint_text("alpha summary"),
                "retrieval_constraints": {
                    "max_results": 10,
                    "section_hint": None,
                    "prefer_exact_matches": False,
                },
                "hit_count": len(retrieval.hits),
                "strategies_used": retrieval.diagnostics["strategies_used"],
                "retrieval_artifact_ids": [f"{run.run_id}:0003:retrieval_result"],
                "retrieval_event_ids": [f"{run.run_id}:0003:retrieval_attached"],
            },
        )
        self.assertRegex(stored.artifacts[5].payload["options_fingerprint"], r"^[0-9a-f]{64}$")
        self.assertEqual(
            stored.artifacts[6].payload["retrieval_evidence"],
            {
                "artifact_id": f"{run.run_id}:0003:retrieval_result",
                "audit_ref": retrieval.audit_ref,
                "query_scope": "doc:doc-1",
                "query_intent": "lookup",
                "retrieval_query_hash": self.service._fingerprint_text("alpha summary"),
                "retrieval_constraints": {
                    "max_results": 10,
                    "section_hint": None,
                    "prefer_exact_matches": False,
                },
                "hit_count": len(retrieval.hits),
                "strategies_used": retrieval.diagnostics["strategies_used"],
                "retrieval_artifact_ids": [f"{run.run_id}:0003:retrieval_result"],
                "retrieval_event_ids": [f"{run.run_id}:0003:retrieval_attached"],
            },
        )
        self.assertEqual(stored.artifacts[6].payload["destination_path"], str(self.root / "exports" / "draft.docx"))
        self.assertTrue(stored.artifacts[6].payload["export_approved"])
        self.assertEqual(stored.events[4].payload["decision_artifact_id"], f"{run.run_id}:0005:patch_decision")
        self.assertEqual(
            stored.artifacts[-1].payload,
            {
                "status": "completed",
                "operation": "draft",
                "scope": "doc:doc-1",
                "intent": "outline",
                "request_fingerprint": "fp-1",
                "run_provenance_artifact_id": f"{run.run_id}:0008:run_provenance",
                "run_provenance_event_id": f"{run.run_id}:0008:run_provenance_captured",
                "run_lifecycle_digest": stored.artifacts[7].payload["run_lifecycle_digest"],
                "flow_digest": stored.artifacts[7].payload["flow_digest"],
            },
        )
        self.assertEqual(stored.artifacts[7].payload["planned_terminal_status"], "completed")
        self.assertEqual(stored.artifacts[7].payload["status"], "completed")
        self.assertEqual(stored.artifacts[7].payload["prior_status"], "running")
        self.assertEqual(stored.artifacts[7].payload["run_id"], run.run_id)
        self.assertEqual(stored.artifacts[7].payload["started_at"], stored.artifacts[0].payload["started_at"])
        self.assertEqual(stored.artifacts[7].payload["snapshot_updated_at"], stored.artifacts[6].created_at)
        self.assertEqual(stored.artifacts[7].payload["completed_at"], stored.artifacts[7].created_at)
        self.assertEqual(stored.artifacts[7].payload["terminal_artifact_count"], 9)
        self.assertEqual(stored.artifacts[7].payload["terminal_event_count"], 9)
        self.assertEqual(stored.events[7].payload["planned_terminal_status"], "completed")
        self.assertEqual(stored.events[7].payload["actual_terminal_status"], "completed")
        self.assertEqual(
            stored.artifacts[7].payload["retrieval_evidence"],
            {
                "artifact_id": f"{run.run_id}:0003:retrieval_result",
                "audit_ref": retrieval.audit_ref,
                "query_scope": "doc:doc-1",
                "query_intent": "lookup",
                "retrieval_query_hash": self.service._fingerprint_text("alpha summary"),
                "retrieval_constraints": {
                    "max_results": 10,
                    "section_hint": None,
                    "prefer_exact_matches": False,
                },
                "hit_count": len(retrieval.hits),
                "strategies_used": retrieval.diagnostics["strategies_used"],
                "retrieval_artifact_ids": [f"{run.run_id}:0003:retrieval_result"],
                "retrieval_event_ids": [f"{run.run_id}:0003:retrieval_attached"],
            },
        )
        self.assertEqual(
            stored.artifacts[7].payload["export_preview_artifacts"],
            [
                {
                    "artifact_id": f"{run.run_id}:0006:export_preview",
                    "output_format": "pdf",
                    "size_bytes": stored.artifacts[5].payload["size_bytes"],
                    "expires_at": stored.artifacts[5].payload["expires_at"],
                    "storage_ref": stored.artifacts[5].payload["storage_ref"],
                    "options_fingerprint": stored.artifacts[5].payload["options_fingerprint"],
                }
            ],
        )
        self.assertEqual(
            stored.artifacts[7].payload["export_final_artifacts"],
            [
                {
                    "artifact_id": f"{run.run_id}:0007:export_final",
                    "output_format": "docx",
                    "size_bytes": stored.artifacts[6].payload["size_bytes"],
                    "content_hash": stored.artifacts[6].payload["content_hash"],
                    "destination_path": str(self.root / "exports" / "draft.docx"),
                    "export_approved": True,
                }
            ],
        )
        self.assertEqual(
            stored.artifacts[7].payload["patch_decisions"],
            [
                {
                    "artifact_id": f"{run.run_id}:0005:patch_decision",
                    "decision_event_id": f"{run.run_id}:0005:patch_applied",
                    "target_path": "notes.md",
                    "decision": "accepted",
                    "reason": "validated",
                    "proposal_artifact_id": f"{run.run_id}:0004:patch_proposal",
                    "proposal_patch_hash": stored.artifacts[3].payload["patch_hash"],
                    "proposal_line_count": stored.artifacts[3].payload["line_count"],
                    "proposal_is_empty": stored.artifacts[3].payload["is_empty"],
                }
            ],
        )
        self.assertEqual(
            stored.artifacts[7].payload["artifact_refs"]["run_started"],
            [f"{run.run_id}:0001:run_started"],
        )
        self.assertEqual(
            stored.artifacts[7].payload["artifact_refs"]["retrieval_result"],
            [f"{run.run_id}:0003:retrieval_result"],
        )
        self.assertEqual(
            stored.artifacts[7].payload["artifact_refs"]["patch_decision"],
            [f"{run.run_id}:0005:patch_decision"],
        )
        self.assertEqual(
            stored.artifacts[7].payload["event_refs"]["run_started"],
            [f"{run.run_id}:0001:run_started"],
        )
        self.assertEqual(
            stored.artifacts[7].payload["event_refs"]["export_final_attached"],
            [f"{run.run_id}:0007:export_final_attached"],
        )
        self.assertEqual(
            stored.artifacts[7].payload["terminal_artifact_refs"],
            {
                "run_provenance": [f"{run.run_id}:0008:run_provenance"],
                "run_completed": [f"{run.run_id}:0009:run_completed"],
            },
        )
        self.assertEqual(
            stored.artifacts[7].payload["terminal_event_refs"],
            {
                "run_provenance_captured": [f"{run.run_id}:0008:run_provenance_captured"],
                "run_completed": [f"{run.run_id}:0009:run_completed"],
            },
        )
        self.assertEqual(
            stored.artifacts[7].payload["terminal_artifact_sequence"],
            ["run_provenance", "run_completed"],
        )
        self.assertEqual(
            stored.artifacts[7].payload["terminal_event_sequence"],
            ["run_provenance_captured", "run_completed"],
        )
        self.assertEqual(stored.events[7].payload["artifact_id"], f"{run.run_id}:0008:run_provenance")
        self.assertEqual(stored.events[-1].payload["artifact_id"], f"{run.run_id}:0009:run_completed")

        summary = self.service.summarize_run(run.run_id)
        self.assertEqual(summary.run_id, run.run_id)
        self.assertEqual(summary.status, "completed")
        self.assertEqual(summary.artifact_count, 9)
        self.assertEqual(summary.event_count, 9)
        self.assertEqual(summary.latest_artifact.artifact_id, f"{run.run_id}:0009:run_completed")
        self.assertEqual(summary.latest_event.event_id, f"{run.run_id}:0009:run_completed")
        self.assertIsNone(summary.latest_failure_artifact)

        lines = [json.loads(line) for line in (self.root / "audit_events.jsonl").read_text(encoding="utf-8").splitlines()]
        audit_names = [item["name"] for item in lines]
        self.assertIn("engine_run_artifact_attached", audit_names)
        self.assertIn("engine_patch_applied", audit_names)
        self.assertIn("engine_run_provenance_captured_summary", audit_names)
        self.assertIn("engine_run_completed_summary", audit_names)
        retrieval_artifact_event = next(
            item
            for item in lines
            if item["name"] == "engine_run_artifact_attached"
            and item["metadata"]["kind"] == "retrieval_result"
        )
        self.assertEqual(retrieval_artifact_event["metadata"]["audit_ref"], retrieval.audit_ref)
        self.assertEqual(retrieval_artifact_event["metadata"]["query_scope"], "doc:doc-1")
        self.assertEqual(retrieval_artifact_event["metadata"]["query_intent"], "lookup")
        self.assertEqual(
            retrieval_artifact_event["metadata"]["retrieval_query_hash"],
            self.service._fingerprint_text("alpha summary"),
        )
        self.assertEqual(
            retrieval_artifact_event["metadata"]["retrieval_constraints"],
            {
                "max_results": 10,
                "section_hint": None,
                "prefer_exact_matches": False,
            },
        )
        self.assertEqual(retrieval_artifact_event["metadata"]["hit_count"], len(retrieval.hits))
        self.assertEqual(
            retrieval_artifact_event["metadata"]["strategies_used"],
            retrieval.diagnostics["strategies_used"],
        )
        completed_event = next(item for item in lines if item["name"] == "engine_run_completed_summary")
        provenance_event = next(item for item in lines if item["name"] == "engine_run_provenance_captured_summary")
        self.assertEqual(completed_event["metadata"]["planned_terminal_status"], "completed")
        self.assertEqual(completed_event["metadata"]["actual_terminal_status"], "completed")
        self.assertEqual(completed_event["metadata"]["run_plan_digest"], stored.artifacts[1].payload["plan_digest"])
        self.assertEqual(completed_event["metadata"]["flow_digest"], stored.artifacts[7].payload["flow_digest"])
        self.assertEqual(
            completed_event["metadata"]["terminal_artifact_refs"],
            {
                "run_provenance": [f"{run.run_id}:0008:run_provenance"],
                "run_completed": [f"{run.run_id}:0009:run_completed"],
            },
        )
        self.assertEqual(
            completed_event["metadata"]["terminal_event_refs"],
            {
                "run_provenance_captured": [f"{run.run_id}:0008:run_provenance_captured"],
                "run_completed": [f"{run.run_id}:0009:run_completed"],
            },
        )
        self.assertEqual(provenance_event["metadata"]["planned_terminal_status"], "completed")
        self.assertEqual(provenance_event["metadata"]["actual_terminal_status"], "completed")
        self.assertEqual(provenance_event["metadata"]["run_plan_digest"], stored.artifacts[1].payload["plan_digest"])
        self.assertEqual(provenance_event["metadata"]["flow_digest"], stored.artifacts[7].payload["flow_digest"])

    def test_run_flow_executes_retrieval_patch_export_and_completion_in_one_call(self) -> None:
        result = self.service.run_flow(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-flow-1",
            retrieval_query_text="alpha summary",
            patch_original="line one\n",
            patch_proposed="line one\nline two\n",
            patch_target_path="notes.md",
            patch_decision="accepted",
            patch_reason="validated",
            export_options=self._options(output_format="docx"),
            export_destination_path=self.root / "exports" / "draft.docx",
            export_approved=True,
        )

        self.assertEqual(result.run.status, "completed")
        self.assertEqual(result.plan_event.name, "run_planned")
        self.assertEqual(result.plan_artifact.kind, "run_plan")
        self.assertEqual(result.plan_artifact.artifact_id, f"{result.run.run_id}:0002:run_plan")
        self.assertEqual(result.plan_artifact.payload["retrieval_query_hash"], result.plan_event.payload["retrieval_query_hash"])
        self.assertEqual(result.plan_artifact.payload["plan_digest"], result.plan_event.payload["plan_digest"])
        self.assertRegex(result.run_plan_digest, r"^[0-9a-f]{64}$")
        self.assertEqual(result.run_plan_digest, result.plan_event.payload["plan_digest"])
        self.assertTrue(result.retrieval_result.hits)
        self.assertIn("@@", result.patch_proposal)
        self.assertEqual(result.patch_decision_event.name, "patch_applied")
        self.assertEqual((self.root / "notes.md").read_text(encoding="utf-8"), "line one\nline two\n")
        self.assertEqual(result.preview_export.output_format, "pdf")
        self.assertEqual(result.final_export.output_format, "docx")
        self.assertRegex(result.preview_export.options_fingerprint, r"^[0-9a-f]{64}$")
        self.assertEqual(
            [artifact.kind for artifact in result.terminal_artifacts],
            ["run_provenance", "run_completed"],
        )
        self.assertEqual(
            [event.name for event in result.terminal_events],
            ["run_provenance_captured", "run_completed"],
        )
        self.assertEqual(result.terminal_artifacts[0].artifact_id, f"{result.run.run_id}:0008:run_provenance")
        self.assertEqual(result.terminal_artifacts[1].artifact_id, f"{result.run.run_id}:0009:run_completed")
        self.assertEqual(result.terminal_events[0].event_id, f"{result.run.run_id}:0008:run_provenance_captured")
        self.assertEqual(result.terminal_events[1].event_id, f"{result.run.run_id}:0009:run_completed")
        self.assertEqual(len(result.flow_snapshot.flow_steps), 9)
        self.assertEqual(
            result.flow_snapshot.flow_steps[0],
            {
                "sequence": 1,
                "artifact_id": f"{result.run.run_id}:0001:run_started",
                "artifact_kind": "run_started",
                "artifact_created_at": result.run.artifacts[0].created_at,
                "event_id": f"{result.run.run_id}:0001:run_started",
                "event_name": "run_started",
                "event_created_at": result.run.events[0].created_at,
            },
        )
        self.assertEqual(
            result.flow_snapshot.flow_steps[-1],
            {
                "sequence": 9,
                "artifact_id": f"{result.run.run_id}:0009:run_completed",
                "artifact_kind": "run_completed",
                "artifact_created_at": result.run.artifacts[-1].created_at,
                "event_id": f"{result.run.run_id}:0009:run_completed",
                "event_name": "run_completed",
                "event_created_at": result.run.events[-1].created_at,
            },
        )
        self.assertEqual(
            result.flow_snapshot.to_manifest()["flow_steps"],
            [dict(item) for item in result.flow_snapshot.flow_steps],
        )
        self.assertEqual(result.to_manifest()["flow_steps"], result.flow_snapshot.to_manifest()["flow_steps"])
        self.assertEqual(result.to_manifest()["run_summary"], result.flow_snapshot.to_manifest()["summary"])
        self.assertEqual(result.to_manifest()["run_provenance"], result.flow_snapshot.to_manifest()["run_provenance"])
        self.assertEqual(result.to_manifest()["run_lifecycle_digest"], result.flow_snapshot.run_lifecycle_digest)
        self.assertEqual(result.to_manifest()["run_lifecycle_digest"], result.flow_snapshot.to_manifest()["run_lifecycle_digest"])
        self.assertRegex(result.to_manifest()["run_lifecycle_digest"], r"^[0-9a-f]{64}$")
        self.assertEqual(
            result.to_manifest()["run_lifecycle_digest"],
            self.service._fingerprint_payload(result.to_manifest()["run_lifecycle"]),
        )
        self.assertRegex(result.run_flow_manifest_digest, r"^[0-9a-f]{64}$")
        self.assertEqual(result.run_flow_manifest_digest, result.to_manifest()["run_flow_manifest_digest"])
        self.assertEqual(
            result.run_flow_manifest_digest,
            self.service._fingerprint_payload(result.run_flow_manifest),
        )
        self.assertEqual(result.to_manifest()["artifact_sequence"], list(result.flow_snapshot.artifact_sequence))
        self.assertEqual(result.to_manifest()["event_sequence"], list(result.flow_snapshot.event_sequence))
        self.assertEqual(result.to_manifest()["artifact_refs"], result.flow_snapshot.to_manifest()["artifact_refs"])
        self.assertEqual(result.to_manifest()["event_refs"], result.flow_snapshot.to_manifest()["event_refs"])
        self.assertEqual(
            result.to_manifest()["terminal_artifact_sequence"],
            list(result.flow_snapshot.to_manifest()["terminal_artifact_sequence"]),
        )
        self.assertEqual(
            result.to_manifest()["terminal_event_sequence"],
            list(result.flow_snapshot.to_manifest()["terminal_event_sequence"]),
        )
        self.assertEqual(
            result.to_manifest()["terminal_artifact_refs"],
            result.flow_snapshot.to_manifest()["terminal_artifact_refs"],
        )
        self.assertEqual(
            result.to_manifest()["terminal_event_refs"],
            result.flow_snapshot.to_manifest()["terminal_event_refs"],
        )
        self.assertEqual(
            result.to_manifest()["pending_patch_proposals"],
            result.flow_snapshot.to_manifest()["pending_patch_proposals"],
        )
        self.assertEqual(result.run_lifecycle, result.flow_snapshot.to_manifest()["run_lifecycle"])
        self.assertEqual(result.run_lifecycle, result.to_manifest()["run_lifecycle"])
        self.assertEqual(result.to_manifest()["summary"], result.to_manifest()["run_summary"])
        self.assertEqual(result.run_lifecycle_digest, result.to_manifest()["run_lifecycle_digest"])
        self.assertEqual(result.to_manifest()["run_lifecycle"], result.flow_snapshot.to_manifest()["run_lifecycle"])
        legacy_result = EngineRunFlowResult(
            run=result.run,
            plan_event=result.plan_event,
            plan_artifact=result.plan_artifact,
            run_plan_digest=result.run_plan_digest,
            flow_digest=result.flow_digest,
            retrieval_result=result.retrieval_result,
            patch_proposal=result.patch_proposal,
            patch_decision_event=result.patch_decision_event,
            preview_export=result.preview_export,
            final_export=result.final_export,
            terminal_artifacts=result.terminal_artifacts,
            terminal_events=result.terminal_events,
            run_provenance=result.run_provenance,
            run_lifecycle=result.run_lifecycle,
            run_summary=result.run_summary,
            flow_snapshot=None,
            run_flow_manifest=result.run_flow_manifest,
        )
        legacy_manifest = legacy_result.to_manifest()
        self.assertEqual(
            legacy_manifest["run_lifecycle_digest"],
            self.service._fingerprint_payload(result.run_lifecycle),
        )
        self.assertEqual(legacy_manifest["run_flow_manifest_digest"], result.run_flow_manifest_digest)
        self.assertEqual(legacy_manifest["run_lifecycle"], result.run_lifecycle)
        self.assertEqual(legacy_manifest["artifact_sequence"], list(result.flow_snapshot.artifact_sequence))
        self.assertEqual(legacy_manifest["event_sequence"], list(result.flow_snapshot.event_sequence))
        self.assertEqual(
            legacy_manifest["flow_steps"],
            result.flow_snapshot.to_manifest()["flow_steps"],
        )
        self.assertEqual(
            legacy_manifest["artifact_refs"],
            result.flow_snapshot.to_manifest()["artifact_refs"],
        )
        self.assertEqual(
            legacy_manifest["event_refs"],
            result.flow_snapshot.to_manifest()["event_refs"],
        )
        self.assertEqual(
            legacy_manifest["terminal_artifact_sequence"],
            list(result.flow_snapshot.to_manifest()["terminal_artifact_sequence"]),
        )
        self.assertEqual(
            legacy_manifest["terminal_event_sequence"],
            list(result.flow_snapshot.to_manifest()["terminal_event_sequence"]),
        )
        self.assertEqual(
            legacy_manifest["terminal_artifact_refs"],
            result.flow_snapshot.to_manifest()["terminal_artifact_refs"],
        )
        self.assertEqual(
            legacy_manifest["terminal_event_refs"],
            result.flow_snapshot.to_manifest()["terminal_event_refs"],
        )
        self.assertEqual(
            legacy_manifest["pending_patch_proposals"],
            result.flow_snapshot.to_manifest()["pending_patch_proposals"],
        )
        self.assertEqual(result.to_manifest()["run_lifecycle"]["artifact_count"], 9)
        self.assertEqual(result.to_manifest()["run_lifecycle"]["event_count"], 9)
        self.assertEqual(
            result.to_manifest()["run_lifecycle"]["latest_artifact_id"],
            f"{result.run.run_id}:0009:run_completed",
        )
        self.assertEqual(
            result.to_manifest()["run_lifecycle"]["latest_event_id"],
            f"{result.run.run_id}:0009:run_completed",
        )
        self.assertEqual(
            result.to_manifest()["run_lifecycle"]["terminal_artifact_refs"],
            {
                "run_provenance": [f"{result.run.run_id}:0008:run_provenance"],
                "run_completed": [f"{result.run.run_id}:0009:run_completed"],
            },
        )
        self.assertEqual(
            result.to_manifest()["run_lifecycle"]["terminal_event_refs"],
            {
                "run_provenance_captured": [f"{result.run.run_id}:0008:run_provenance_captured"],
                "run_completed": [f"{result.run.run_id}:0009:run_completed"],
            },
        )
        self.assertEqual(result.plan_event.payload["artifact_id"], f"{result.run.run_id}:0002:run_plan")
        self.assertEqual(result.run_provenance["run_id"], result.run.run_id)
        self.assertEqual(result.run_provenance["status"], "completed")
        self.assertEqual(result.run_provenance["run_plan_digest"], result.run_plan_digest)
        self.assertEqual(
            result.run_provenance["artifact_sequence"],
            [
                "run_started",
                "run_plan",
                "retrieval_result",
                "patch_proposal",
                "patch_decision",
                "export_preview",
                "export_final",
            ],
        )
        self.assertEqual(
            result.run_provenance["event_sequence"],
            [
                "run_started",
                "run_planned",
                "retrieval_attached",
                "patch_proposed",
                "patch_applied",
                "export_preview_attached",
                "export_final_attached",
            ],
        )
        self.assertEqual(
            result.run_provenance["retrieval_evidence"]["retrieval_query_hash"],
            self.service._fingerprint_text("alpha summary"),
        )
        self.assertEqual(
            result.run_provenance["retrieval_evidence"]["retrieval_constraints"],
            {
                "max_results": 10,
                "section_hint": None,
                "prefer_exact_matches": False,
            },
        )
        self.assertEqual(result.flow_digest, result.run_provenance["flow_digest"])
        self.assertEqual(result.run_provenance["retrieval_evidence"]["artifact_id"], f"{result.run.run_id}:0003:retrieval_result")
        self.assertEqual(
            result.run_provenance["terminal_artifact_sequence"],
            ["run_provenance", "run_completed"],
        )
        self.assertEqual(
            result.run_provenance["terminal_event_sequence"],
            ["run_provenance_captured", "run_completed"],
        )
        self.assertEqual(
            result.run_provenance["export_preview_artifacts"],
            [
                {
                    "artifact_id": f"{result.run.run_id}:0006:export_preview",
                    "output_format": "pdf",
                    "size_bytes": result.preview_export.size_bytes,
                    "expires_at": result.preview_export.expires_at,
                    "storage_ref": result.preview_export.storage_ref,
                    "options_fingerprint": result.preview_export.options_fingerprint,
                }
            ],
        )
        self.assertEqual(
            result.run_provenance["export_final_artifacts"],
            [
                {
                    "artifact_id": f"{result.run.run_id}:0007:export_final",
                    "output_format": "docx",
                    "size_bytes": result.final_export.size_bytes,
                    "content_hash": result.final_export.content_hash,
                    "destination_path": str(self.root / "exports" / "draft.docx"),
                    "export_approved": True,
                }
            ],
        )
        self.assertEqual(
            result.run_provenance["patch_decisions"],
            [
                {
                    "artifact_id": f"{result.run.run_id}:0005:patch_decision",
                    "decision_event_id": f"{result.run.run_id}:0005:patch_applied",
                    "target_path": "notes.md",
                    "decision": "accepted",
                    "reason": "validated",
                    "proposal_artifact_id": f"{result.run.run_id}:0004:patch_proposal",
                    "proposal_patch_hash": result.flow_snapshot.run.artifacts[3].payload["patch_hash"],
                    "proposal_line_count": result.flow_snapshot.run.artifacts[3].payload["line_count"],
                    "proposal_is_empty": result.flow_snapshot.run.artifacts[3].payload["is_empty"],
                }
            ],
        )
        self.assertEqual(
            result.flow_snapshot.run.artifacts[4].payload["decision_event_id"],
            f"{result.run.run_id}:0005:patch_applied",
        )
        self.assertRegex(result.run_provenance["flow_digest"], r"^[0-9a-f]{64}$")
        self.assertEqual(result.run_provenance["flow_digest"], self.service.get_run_provenance(result.run.run_id)["flow_digest"])
        self.assertEqual(result.flow_digest, result.run_provenance["flow_digest"])
        self.assertEqual(result.flow_snapshot.flow_digest, result.run_provenance["flow_digest"])
        self.assertEqual(self.service.describe_run_manifest(result.run.run_id)["flow_digest"], result.flow_digest)
        self.assertEqual(result.run_provenance["flow_steps"], result.flow_snapshot.to_manifest()["flow_steps"])

        lines = [json.loads(line) for line in (self.root / "audit_events.jsonl").read_text(encoding="utf-8").splitlines()]
        audit_names = [item["name"] for item in lines]
        self.assertIn("engine_run_provenance_captured_summary", audit_names)
        self.assertIn("engine_run_completed_summary", audit_names)
        self.assertIn("engine_run_flow_completed_summary", audit_names)
        flow_event = next(item for item in lines if item["name"] == "engine_run_flow_completed_summary")
        self.assertEqual(flow_event["metadata"]["run_id"], result.run.run_id)
        self.assertEqual(flow_event["metadata"]["status"], "completed")
        self.assertEqual(flow_event["metadata"]["run_plan_digest"], result.run_plan_digest)
        self.assertEqual(flow_event["metadata"]["flow_digest"], result.flow_digest)
        self.assertEqual(flow_event["metadata"]["run_lifecycle_digest"], result.to_manifest()["run_lifecycle_digest"])
        self.assertEqual(flow_event["metadata"]["run_lifecycle"], result.to_manifest()["run_lifecycle"])
        self.assertEqual(
            flow_event["metadata"]["run_flow_manifest"]["run_lifecycle"],
            result.to_manifest()["run_lifecycle"],
        )
        self.assertEqual(
            flow_event["metadata"]["terminal_artifact_refs"],
            {
                "run_provenance": [f"{result.run.run_id}:0008:run_provenance"],
                "run_completed": [f"{result.run.run_id}:0009:run_completed"],
            },
        )
        self.assertEqual(
            flow_event["metadata"]["terminal_event_refs"],
            {
                "run_provenance_captured": [f"{result.run.run_id}:0008:run_provenance_captured"],
                "run_completed": [f"{result.run.run_id}:0009:run_completed"],
            },
        )

        stored = self.service.get_run(result.run.run_id)
        self.assertEqual(
            [artifact.kind for artifact in stored.artifacts],
            [
                "run_started",
                "run_plan",
                "retrieval_result",
                "patch_proposal",
                "patch_decision",
                "export_preview",
                "export_final",
                "run_provenance",
                "run_completed",
            ],
        )
        self.assertEqual(
            [event.name for event in stored.events],
            [
                "run_started",
                "run_planned",
                "retrieval_attached",
                "patch_proposed",
                "patch_applied",
                "export_preview_attached",
                "export_final_attached",
                "run_provenance_captured",
                "run_completed",
            ],
        )
        self.assertEqual(stored.artifacts[0].payload["status"], "running")
        self.assertEqual(stored.artifacts[1].payload["planned_terminal_status"], "completed")
        self.assertEqual(stored.artifacts[1].payload["patch_requested"], True)
        self.assertEqual(stored.artifacts[1].payload["export_requested"], True)
        self.assertEqual(
            stored.artifacts[2].payload["retrieval_query_hash"],
            self.service._fingerprint_text("alpha summary"),
        )
        self.assertEqual(
            stored.artifacts[2].payload["retrieval_constraints"],
            {
                "max_results": 10,
                "section_hint": None,
                "prefer_exact_matches": False,
            },
        )
        self.assertEqual(stored.artifacts[7].payload["planned_terminal_status"], "completed")
        self.assertEqual(stored.artifacts[8].payload["status"], "completed")
        self.assertEqual(stored.artifacts[7].payload["run_id"], result.run.run_id)
        self.assertEqual(stored.artifacts[7].payload["started_at"], stored.artifacts[0].payload["started_at"])
        self.assertEqual(stored.artifacts[7].payload["snapshot_updated_at"], stored.artifacts[6].created_at)
        self.assertEqual(stored.artifacts[7].payload["completed_at"], stored.artifacts[7].created_at)
        self.assertEqual(stored.artifacts[7].payload["terminal_artifact_count"], 9)
        self.assertEqual(stored.artifacts[7].payload["terminal_event_count"], 9)
        self.assertEqual(stored.events[7].payload["planned_terminal_status"], "completed")
        self.assertEqual(stored.events[7].payload["actual_terminal_status"], "completed")
        self.assertEqual(
            stored.artifacts[5].payload["retrieval_evidence"]["artifact_id"],
            f"{result.run.run_id}:0003:retrieval_result",
        )
        self.assertEqual(
            stored.artifacts[5].payload["retrieval_evidence"]["retrieval_constraints"],
            {
                "max_results": 10,
                "section_hint": None,
                "prefer_exact_matches": False,
            },
        )
        self.assertEqual(
            stored.artifacts[6].payload["retrieval_evidence"]["query_scope"],
            "doc:doc-1",
        )
        self.assertEqual(stored.artifacts[6].payload["retrieval_evidence"]["query_intent"], "outline_support")
        self.assertEqual(
            stored.artifacts[7].payload["retrieval_evidence"]["artifact_id"],
            f"{result.run.run_id}:0003:retrieval_result",
        )
        self.assertEqual(
            stored.artifacts[7].payload["retrieval_evidence"]["retrieval_constraints"],
            {
                "max_results": 10,
                "section_hint": None,
                "prefer_exact_matches": False,
            },
        )
        self.assertEqual(stored.artifacts[6].payload["destination_path"], str(self.root / "exports" / "draft.docx"))
        self.assertTrue(stored.artifacts[6].payload["export_approved"])
        self.assertEqual(stored.artifacts[7].payload["artifact_refs"]["run_plan"], [f"{result.run.run_id}:0002:run_plan"])
        self.assertEqual(stored.artifacts[7].payload["event_refs"]["run_planned"], [f"{result.run.run_id}:0002:run_planned"])
        self.assertEqual(
            stored.artifacts[7].payload["terminal_artifact_refs"],
            {
                "run_provenance": [f"{result.run.run_id}:0008:run_provenance"],
                "run_completed": [f"{result.run.run_id}:0009:run_completed"],
            },
        )
        self.assertEqual(
            stored.artifacts[7].payload["terminal_event_refs"],
            {
                "run_provenance_captured": [f"{result.run.run_id}:0008:run_provenance_captured"],
                "run_completed": [f"{result.run.run_id}:0009:run_completed"],
            },
        )
        self.assertRegex(stored.artifacts[7].payload["flow_digest"], r"^[0-9a-f]{64}$")

    def test_run_flow_accepted_patch_requires_matching_document_state(self) -> None:
        document_path = self.root / "notes.md"
        document_path.write_text("stale content\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "patch original text does not match current document content"):
            self.service.run_flow(
                operation="draft",
                scope="doc:doc-1",
                intent="outline",
                request_fingerprint="fp-flow-mismatch",
                retrieval_query_text="alpha summary",
                patch_original="line one\n",
                patch_proposed="line one\nline two\n",
                patch_target_path="notes.md",
                patch_decision="accepted",
            )

        self.assertEqual(document_path.read_text(encoding="utf-8"), "stale content\n")

    def test_run_flow_rejected_patch_leaves_document_state_unchanged(self) -> None:
        document_path = self.root / "notes.md"
        document_path.write_text("line one\n", encoding="utf-8")

        result = self.service.run_flow(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-flow-rejected",
            retrieval_query_text="alpha summary",
            patch_original="line one\n",
            patch_proposed="line one\nline two\n",
            patch_target_path="notes.md",
            patch_decision="rejected",
        )

        self.assertEqual(result.patch_decision_event.name, "patch_rejected")
        self.assertEqual(document_path.read_text(encoding="utf-8"), "line one\n")

    def test_run_flow_result_to_manifest_uses_run_flow_manifest_when_snapshot_is_missing(self) -> None:
        result = self.service.run_flow(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-legacy-manifest",
            retrieval_query_text="alpha summary",
            patch_original="line one\n",
            patch_proposed="line one\nline two\n",
            patch_target_path="notes.md",
            patch_decision="accepted",
            patch_reason="validated",
            export_options=self._options(output_format="docx"),
            export_destination_path=self.root / "exports" / "draft.docx",
            export_approved=True,
        )

        legacy_result = EngineRunFlowResult(
            run=result.run,
            plan_event=result.plan_event,
            plan_artifact=result.plan_artifact,
            run_plan_digest=result.run_plan_digest,
            flow_digest=result.flow_digest,
            retrieval_result=result.retrieval_result,
            patch_proposal=result.patch_proposal,
            patch_decision_event=result.patch_decision_event,
            preview_export=result.preview_export,
            final_export=result.final_export,
            terminal_artifacts=result.terminal_artifacts,
            terminal_events=result.terminal_events,
            run_provenance=None,
            run_lifecycle=None,
            run_summary=None,
            flow_snapshot=None,
            run_flow_manifest=result.run_flow_manifest,
            run_flow_manifest_digest=result.run_flow_manifest_digest,
        )

        legacy_manifest = legacy_result.to_manifest()
        self.assertEqual(legacy_manifest["summary"], result.run_flow_manifest["summary"])
        self.assertEqual(legacy_manifest["artifact_sequence"], list(result.flow_snapshot.artifact_sequence))
        self.assertEqual(legacy_manifest["event_sequence"], list(result.flow_snapshot.event_sequence))
        self.assertEqual(legacy_manifest["flow_steps"], result.run_flow_manifest["flow_steps"])
        self.assertEqual(legacy_manifest["artifact_refs"], result.run_flow_manifest["artifact_refs"])
        self.assertEqual(legacy_manifest["event_refs"], result.run_flow_manifest["event_refs"])
        self.assertEqual(
            legacy_manifest["terminal_artifact_sequence"],
            result.run_flow_manifest["terminal_artifact_sequence"],
        )
        self.assertEqual(
            legacy_manifest["terminal_event_sequence"],
            result.run_flow_manifest["terminal_event_sequence"],
        )
        self.assertEqual(
            legacy_manifest["terminal_artifact_refs"],
            result.run_flow_manifest["terminal_artifact_refs"],
        )
        self.assertEqual(
            legacy_manifest["terminal_event_refs"],
            result.run_flow_manifest["terminal_event_refs"],
        )
        self.assertEqual(
            legacy_manifest["pending_patch_proposals"],
            result.run_flow_manifest["pending_patch_proposals"],
        )
        self.assertEqual(legacy_manifest["run_lifecycle"], result.run_flow_manifest["run_lifecycle"])
        self.assertEqual(legacy_manifest["run_lifecycle_digest"], result.run_flow_manifest["run_lifecycle_digest"])
        self.assertEqual(legacy_manifest["run_flow_manifest_digest"], result.run_flow_manifest_digest)
        self.assertEqual(legacy_manifest["run_flow_manifest"], result.run_flow_manifest)

    def test_run_flow_result_to_manifest_ignores_unknown_legacy_summary_fields(self) -> None:
        result = self.service.run_flow(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-legacy-summary-extra-fields",
            retrieval_query_text="alpha summary",
            patch_original="line one\n",
            patch_proposed="line one\nline two\n",
            patch_target_path="notes.md",
            patch_decision="accepted",
            patch_reason="validated",
            export_options=self._options(output_format="docx"),
            export_destination_path=self.root / "exports" / "draft.docx",
            export_approved=True,
        )

        legacy_run_flow_manifest = json.loads(json.dumps(result.run_flow_manifest))
        legacy_run_flow_manifest["summary"]["unexpected_field"] = "ignored"
        legacy_run_flow_manifest["run_summary"]["unexpected_field"] = "ignored"
        legacy_run_flow_manifest["summary"]["latest_artifact"]["unexpected_field"] = "ignored"
        legacy_run_flow_manifest["summary"]["latest_event"]["unexpected_field"] = "ignored"

        legacy_result = EngineRunFlowResult(
            run=result.run,
            plan_event=result.plan_event,
            plan_artifact=result.plan_artifact,
            run_plan_digest=result.run_plan_digest,
            flow_digest=result.flow_digest,
            retrieval_result=result.retrieval_result,
            patch_proposal=result.patch_proposal,
            patch_decision_event=result.patch_decision_event,
            preview_export=result.preview_export,
            final_export=result.final_export,
            terminal_artifacts=result.terminal_artifacts,
            terminal_events=result.terminal_events,
            run_provenance=None,
            run_lifecycle=None,
            run_summary=None,
            flow_snapshot=None,
            run_flow_manifest=legacy_run_flow_manifest,
            run_flow_manifest_digest=None,
        )

        legacy_manifest = legacy_result.to_manifest()
        self.assertEqual(legacy_manifest["summary"]["run_id"], result.run.run_id)
        self.assertNotIn("unexpected_field", legacy_manifest["summary"])
        self.assertNotIn("unexpected_field", legacy_manifest["run_summary"])
        self.assertEqual(
            legacy_manifest["summary"]["latest_artifact"]["artifact_id"],
            result.run_flow_manifest["summary"]["latest_artifact"]["artifact_id"],
        )
        self.assertEqual(
            legacy_manifest["summary"]["latest_event"]["event_id"],
            result.run_flow_manifest["summary"]["latest_event"]["event_id"],
        )
        self.assertEqual(legacy_manifest["run_flow_manifest"], legacy_run_flow_manifest)

    def test_run_flow_result_to_manifest_can_synthesize_manifest_from_provenance_only(self) -> None:
        result = self.service.run_flow(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-provenance-only-manifest",
            retrieval_query_text="alpha summary",
            patch_original="line one\n",
            patch_proposed="line one\nline two\n",
            patch_target_path="notes.md",
            patch_decision="accepted",
            patch_reason="validated",
            export_options=self._options(output_format="docx"),
            export_destination_path=self.root / "exports" / "draft.docx",
            export_approved=True,
        )

        legacy_result = EngineRunFlowResult(
            run=result.run,
            plan_event=result.plan_event,
            plan_artifact=result.plan_artifact,
            run_plan_digest=result.run_plan_digest,
            flow_digest=result.flow_digest,
            retrieval_result=result.retrieval_result,
            patch_proposal=result.patch_proposal,
            patch_decision_event=result.patch_decision_event,
            preview_export=result.preview_export,
            final_export=result.final_export,
            terminal_artifacts=result.terminal_artifacts,
            terminal_events=result.terminal_events,
            run_provenance=result.run_provenance,
            run_lifecycle=None,
            run_summary=None,
            flow_snapshot=None,
            run_flow_manifest=None,
            run_flow_manifest_digest=None,
        )

        legacy_manifest = legacy_result.to_manifest()
        self.assertEqual(legacy_manifest["summary"]["status"], "completed")
        self.assertEqual(legacy_manifest["run_summary"]["status"], "completed")
        self.assertEqual(
            legacy_manifest["retrieval_evidence"],
            result.run_provenance["retrieval_evidence"],
        )
        self.assertEqual(
            legacy_manifest["run_provenance"]["retrieval_evidence"],
            result.run_provenance["retrieval_evidence"],
        )
        self.assertEqual(legacy_manifest["run_lifecycle"]["artifact_count"], 9)
        self.assertEqual(legacy_manifest["run_lifecycle"]["event_count"], 9)
        self.assertRegex(legacy_manifest["run_lifecycle_digest"], r"^[0-9a-f]{64}$")
        self.assertEqual(legacy_manifest["run_flow_manifest"]["run_provenance"], result.run_provenance)
        self.assertEqual(legacy_manifest["run_flow_manifest"]["summary"]["status"], "completed")
        self.assertEqual(legacy_manifest["run_flow_manifest"]["run_lifecycle"]["artifact_count"], 9)
        self.assertEqual(
            legacy_manifest["run_flow_manifest"]["terminal_artifact_sequence"],
            ["run_provenance", "run_completed"],
        )
        self.assertEqual(
            legacy_manifest["run_flow_manifest"]["terminal_event_sequence"],
            ["run_provenance_captured", "run_completed"],
        )
        self.assertEqual(legacy_manifest["run_flow_manifest_digest"], self.service._fingerprint_payload(legacy_manifest["run_flow_manifest"]))

    def test_run_flow_result_to_manifest_can_synthesize_manifest_from_run_lifecycle_only(self) -> None:
        result = self.service.run_flow(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-run-lifecycle-only-manifest",
            retrieval_query_text="alpha summary",
            patch_original="line one\n",
            patch_proposed="line one\nline two\n",
            patch_target_path="notes.md",
            patch_decision="accepted",
            patch_reason="validated",
            export_options=self._options(output_format="docx"),
            export_destination_path=self.root / "exports" / "draft.docx",
            export_approved=True,
        )

        legacy_result = EngineRunFlowResult(
            run=result.run,
            plan_event=result.plan_event,
            plan_artifact=result.plan_artifact,
            run_plan_digest=result.run_plan_digest,
            flow_digest=result.flow_digest,
            retrieval_result=result.retrieval_result,
            patch_proposal=result.patch_proposal,
            patch_decision_event=result.patch_decision_event,
            preview_export=result.preview_export,
            final_export=result.final_export,
            terminal_artifacts=result.terminal_artifacts,
            terminal_events=result.terminal_events,
            run_provenance=None,
            run_lifecycle=result.run_lifecycle,
            run_summary=result.run_summary,
            flow_snapshot=None,
            run_flow_manifest=None,
            run_flow_manifest_digest=None,
        )

        legacy_manifest = legacy_result.to_manifest()
        self.assertEqual(legacy_manifest["summary"]["status"], "completed")
        self.assertEqual(legacy_manifest["run_summary"]["status"], "completed")
        self.assertEqual(legacy_manifest["run_lifecycle"]["artifact_count"], 9)
        self.assertEqual(legacy_manifest["run_lifecycle"]["event_count"], 9)
        self.assertEqual(legacy_manifest["run_flow_manifest"]["run_lifecycle"], result.run_lifecycle)
        self.assertEqual(legacy_manifest["run_flow_manifest"]["summary"]["run_id"], result.run.run_id)
        self.assertEqual(legacy_manifest["run_flow_manifest"]["summary"]["status"], "completed")
        self.assertEqual(
            legacy_manifest["run_flow_manifest"]["terminal_artifact_sequence"],
            ["run_provenance", "run_completed"],
        )
        self.assertEqual(
            legacy_manifest["run_flow_manifest"]["terminal_event_sequence"],
            ["run_provenance_captured", "run_completed"],
        )
        self.assertRegex(legacy_manifest["run_flow_manifest_digest"], r"^[0-9a-f]{64}$")
        self.assertEqual(
            legacy_manifest["run_flow_manifest_digest"],
            self.service._fingerprint_payload(legacy_manifest["run_flow_manifest"]),
        )

    def test_run_flow_uses_completed_record_for_final_snapshot(self) -> None:
        original_describe_run_flow = self.service.describe_run_flow

        def failing_describe_run_flow(run_id: str):  # type: ignore[no-untyped-def]
            raise AssertionError(f"describe_run_flow should not be called by run_flow for {run_id}")

        self.service.describe_run_flow = failing_describe_run_flow  # type: ignore[method-assign]

        try:
            result = self.service.run_flow(
                operation="draft",
                scope="doc:doc-1",
                intent="outline",
                request_fingerprint="fp-flow-snapshot",
                retrieval_query_text="alpha summary",
                patch_original="line one\n",
                patch_proposed="line one\nline two\n",
                patch_target_path="notes.md",
                patch_decision="accepted",
                patch_reason="validated",
                export_options=self._options(output_format="docx"),
                export_destination_path=self.root / "exports" / "draft.docx",
                export_approved=True,
            )
        finally:
            self.service.describe_run_flow = original_describe_run_flow  # type: ignore[method-assign]

        self.assertEqual(result.run.status, "completed")
        self.assertEqual(result.run_summary.run_id, result.run.run_id)
        self.assertEqual(result.run_summary, self.service.summarize_run(result.run.run_id))
        self.assertEqual(result.run_summary.run_plan_digest, result.run_plan_digest)
        self.assertEqual(result.run_summary.flow_digest, result.flow_digest)
        self.assertEqual(result.flow_snapshot.run.run_id, result.run.run_id)
        self.assertEqual(result.flow_snapshot.summary.status, "completed")
        self.assertEqual(result.flow_snapshot.summary, result.run_summary)
        self.assertEqual(result.flow_snapshot.run_plan_digest, result.run_plan_digest)
        self.assertEqual(result.flow_snapshot.flow_digest, result.flow_digest)
        self.assertEqual(result.flow_snapshot.run_lifecycle_digest, result.to_manifest()["run_lifecycle_digest"])
        self.assertEqual(result.run_lifecycle, result.flow_snapshot.to_manifest()["run_lifecycle"])
        self.assertEqual(result.run_lifecycle_digest, result.flow_snapshot.run_lifecycle_digest)
        self.assertEqual(result.flow_snapshot.to_manifest()["flow_digest"], result.flow_digest)
        self.assertEqual(result.flow_snapshot.to_manifest()["run_lifecycle"], result.to_manifest()["run_lifecycle"])
        self.assertEqual(
            result.flow_snapshot.artifact_sequence,
            (
                "run_started",
                "run_plan",
                "retrieval_result",
                "patch_proposal",
                "patch_decision",
                "export_preview",
                "export_final",
                "run_provenance",
                "run_completed",
            ),
        )
        self.assertEqual(
            result.flow_snapshot.event_sequence,
            (
                "run_started",
                "run_planned",
                "retrieval_attached",
                "patch_proposed",
                "patch_applied",
                "export_preview_attached",
                "export_final_attached",
                "run_provenance_captured",
                "run_completed",
            ),
        )
        self.assertEqual(result.flow_snapshot.terminal_artifacts[0].kind, "run_provenance")
        self.assertEqual(result.flow_snapshot.terminal_events[1].name, "run_completed")
        self.assertEqual(
            self.service.describe_run_flow(result.run.run_id).summary,
            result.run_summary,
        )

    def test_build_flow_snapshot_rejects_terminal_records_missing_completion_artifacts(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-corrupt-terminal-snapshot",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        completed = self.service.complete_run(run.run_id)
        corrupted = EngineRunRecord(
            run_id=completed.run_id,
            status=completed.status,
            started_at=completed.started_at,
            updated_at=completed.updated_at,
            completed_at=completed.completed_at,
            operation=completed.operation,
            scope=completed.scope,
            intent=completed.intent,
            request_fingerprint=completed.request_fingerprint,
            artifacts=list(completed.artifacts[:-2]),
            events=list(completed.events[:-2]),
        )

        with self.assertRaisesRegex(ValueError, "run .* does not have a recorded run_provenance artifact"):
            EngineRunService._build_flow_snapshot(corrupted)

    def test_build_flow_snapshot_rejects_mismatched_artifact_and_event_counts(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-corrupt-flow-counts",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        stored = self.service.get_run(run.run_id)
        corrupted = EngineRunRecord(
            run_id=stored.run_id,
            status=stored.status,
            started_at=stored.started_at,
            updated_at=stored.updated_at,
            completed_at=stored.completed_at,
            operation=stored.operation,
            scope=stored.scope,
            intent=stored.intent,
            request_fingerprint=stored.request_fingerprint,
            artifacts=list(stored.artifacts),
            events=list(stored.events[:-1]),
        )

        with self.assertRaisesRegex(ValueError, "mismatched artifact/event counts"):
            EngineRunService._build_flow_snapshot(corrupted)

    def test_persisted_run_rejects_mismatched_artifact_and_event_counts(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-corrupt-persisted-counts",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )

        records = self.service._load_records()
        payload = records[run.run_id]
        payload["events"] = payload["events"][:-1]
        self.service._store.write_json("runs_v1.enc.json", records)

        with self.assertRaisesRegex(ValueError, "mismatched artifact/event counts"):
            self.service.get_run(run.run_id)

    def test_plan_run_rejects_non_terminal_statuses(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-plan-status",
        )

        with self.assertRaisesRegex(ValueError, "terminal run status must be one of"):
            self.service.plan_run(
                run.run_id,
                retrieval_query_text="alpha summary",
                final_status="running",  # type: ignore[arg-type]
            )

    def test_start_run_rejects_blank_required_fields(self) -> None:
        for field_name, kwargs in (
            ("operation", {"operation": " ", "scope": "doc:doc-1", "intent": "outline", "request_fingerprint": "fp"}),
            ("scope", {"operation": "draft", "scope": " ", "intent": "outline", "request_fingerprint": "fp"}),
            ("intent", {"operation": "draft", "scope": "doc:doc-1", "intent": " ", "request_fingerprint": "fp"}),
            (
                "request_fingerprint",
                {"operation": "draft", "scope": "doc:doc-1", "intent": "outline", "request_fingerprint": " "},
            ),
        ):
            with self.subTest(field=field_name):
                with self.assertRaisesRegex(ValueError, f"{field_name} is required"):
                    self.service.start_run(**kwargs)

        self.assertEqual(self.service._load_records(), {})

    def test_start_run_honors_explicit_run_id_and_rejects_collisions(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-explicit-run-id",
            run_id="run-fixed-1",
        )

        self.assertEqual(run.run_id, "run-fixed-1")
        self.assertEqual(self.service.get_run("run-fixed-1").run_id, "run-fixed-1")

        with self.assertRaisesRegex(ValueError, "run_id already exists: run-fixed-1"):
            self.service.start_run(
                operation="draft",
                scope="doc:doc-1",
                intent="outline",
                request_fingerprint="fp-explicit-run-id-2",
                run_id="run-fixed-1",
            )

        self.assertEqual(list(self.service._load_records()), ["run-fixed-1"])

    def test_run_flow_rejects_blank_retrieval_query_before_writing_state(self) -> None:
        with self.assertRaisesRegex(ValueError, "query_text is required"):
            self.service.run_flow(
                operation="draft",
                scope="doc:doc-1",
                intent="outline",
                request_fingerprint="fp-flow-blank-query",
                retrieval_query_text=" ",
            )

        self.assertEqual(self.service._load_records(), {})

    def test_run_flow_honors_explicit_run_id_through_terminalization(self) -> None:
        result = self.service.run_flow(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-flow-explicit-run-id",
            run_id="run-fixed-flow",
            retrieval_query_text="alpha summary",
            patch_original="line one\n",
            patch_proposed="line one\nline two\n",
            patch_target_path="notes.md",
            patch_decision="accepted",
            patch_reason="validated",
            export_options=self._options(output_format="docx"),
            export_destination_path=self.root / "exports" / "draft.docx",
            export_approved=True,
        )

        self.assertEqual(result.run.run_id, "run-fixed-flow")
        self.assertEqual(result.plan_artifact.artifact_id, "run-fixed-flow:0002:run_plan")
        self.assertEqual(result.retrieval_result.audit_ref, self.service.get_run("run-fixed-flow").artifacts[2].payload["audit_ref"])
        self.assertEqual(result.terminal_artifacts[0].artifact_id, "run-fixed-flow:0008:run_provenance")
        self.assertEqual(result.terminal_events[1].event_id, "run-fixed-flow:0009:run_completed")
        self.assertEqual(self.service.get_run("run-fixed-flow").run_id, "run-fixed-flow")

    def test_run_flow_rejects_invalid_retrieval_constraints_before_writing_state(self) -> None:
        with self.assertRaisesRegex(TypeError, "retrieval_constraints must be a dict when provided"):
            self.service.run_flow(
                operation="draft",
                scope="doc:doc-1",
                intent="outline",
                request_fingerprint="fp-invalid-constraints",
                retrieval_query_text="alpha summary",
                retrieval_constraints="invalid",  # type: ignore[arg-type]
            )

        self.assertEqual(self.service._load_records(), {})

    def test_run_flow_rejects_invalid_retrieval_confidentiality_profile_before_writing_state(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "retrieval_confidentiality_profile must be one of: confidential, standard",
        ):
            self.service.run_flow(
                operation="draft",
                scope="doc:doc-1",
                intent="outline",
                request_fingerprint="fp-invalid-profile",
                retrieval_query_text="alpha summary",
                retrieval_confidentiality_profile="public",
            )

        self.assertEqual(self.service._load_records(), {})

    def test_run_flow_normalizes_retrieval_constraints_before_persisting_plan(self) -> None:
        result = self.service.run_flow(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-normalized-constraints",
            retrieval_query_text="alpha summary",
            retrieval_constraints={
                "max_results": "7",
                "section_hint": "  discussion  ",
                "prefer_exact_matches": "yes",
            },
        )

        self.assertEqual(
            result.plan_event.payload["retrieval_constraints"],
            {
                "max_results": 7,
                "section_hint": "discussion",
                "prefer_exact_matches": True,
            },
        )
        self.assertEqual(result.plan_artifact.payload["retrieval_constraints"], result.plan_event.payload["retrieval_constraints"])
        self.assertEqual(result.retrieval_result.query.constraints.max_results, 7)
        self.assertEqual(result.retrieval_result.query.constraints.section_hint, "discussion")
        self.assertTrue(result.retrieval_result.query.constraints.prefer_exact_matches)

        stored = self.service.get_run(result.run.run_id)
        self.assertEqual(stored.artifacts[1].payload["retrieval_constraints"], result.plan_event.payload["retrieval_constraints"])

    def test_run_flow_rejects_blank_patch_target_path_before_writing_state(self) -> None:
        with self.assertRaisesRegex(ValueError, "patch_target_path is required"):
            self.service.run_flow(
                operation="draft",
                scope="doc:doc-1",
                intent="outline",
                request_fingerprint="fp-blank-patch-target",
                retrieval_query_text="alpha summary",
                patch_original="line one\n",
                patch_proposed="line one\nline two\n",
                patch_target_path=" ",
                patch_decision="accepted",
            )

        self.assertEqual(self.service._load_records(), {})

    def test_run_flow_rejects_invalid_patch_decision_before_writing_state(self) -> None:
        with self.assertRaisesRegex(ValueError, "patch decision must be one of: accepted, rejected"):
            self.service.run_flow(
                operation="draft",
                scope="doc:doc-1",
                intent="outline",
                request_fingerprint="fp-invalid-patch-decision",
                retrieval_query_text="alpha summary",
                patch_original="line one\n",
                patch_proposed="line one\nline two\n",
                patch_target_path="notes.md",
                patch_decision="maybe",  # type: ignore[arg-type]
                patch_reason="invalid decision",
            )

        self.assertEqual(self.service._load_records(), {})

    def test_run_flow_rejects_accepted_empty_patch_before_writing_state(self) -> None:
        with self.assertRaisesRegex(ValueError, "accepted patch decision requires a non-empty patch proposal"):
            self.service.run_flow(
                operation="draft",
                scope="doc:doc-1",
                intent="outline",
                request_fingerprint="fp-empty-patch-accepted",
                retrieval_query_text="alpha summary",
                patch_original="line one\n",
                patch_proposed="line one\n",
                patch_target_path="notes.md",
                patch_decision="accepted",
                patch_reason="no-op should not apply",
            )

        self.assertEqual(self.service._load_records(), {})

    def test_patch_flow_normalizes_target_path_before_persisting_artifacts(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-patch-target-normalization",
        )

        patch = self.service.propose_patch(
            run.run_id,
            original="line one\n",
            proposed="line one\nline two\n",
            target_path="  notes.md  ",
        )
        decision = self.service.record_patch_decision(
            run.run_id,
            decision="accepted",
            target_path="  notes.md  ",
            reason="validated",
        )

        self.assertIn("@@", patch)
        self.assertEqual(decision.name, "patch_applied")
        stored = self.service.get_run(run.run_id)
        self.assertEqual(stored.artifacts[1].payload["target_path"], "notes.md")
        self.assertEqual(stored.artifacts[2].payload["target_path"], "notes.md")
        self.assertEqual(stored.events[2].payload["target_path"], "notes.md")

    def test_retrieve_records_normalized_query_hash_in_artifacts_and_provenance(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-retrieve-query-hash",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )

        retrieval = self.service.retrieve(
            run.run_id,
            query_text="  alpha summary  ",
            scope="doc:doc-1",
            intent="lookup",
        )

        self.assertTrue(retrieval.hits)

        stored = self.service.get_run(run.run_id)
        expected_hash = self.service._fingerprint_text("alpha summary")
        self.assertEqual(stored.artifacts[2].payload["retrieval_query_hash"], expected_hash)
        self.assertEqual(stored.events[2].payload["retrieval_query_hash"], expected_hash)
        self.assertEqual(
            self.service.describe_run_flow(run.run_id).retrieval_evidence["retrieval_query_hash"],
            expected_hash,
        )
        self.assertEqual(
            stored.artifacts[2].payload["retrieval_constraints"],
            {
                "max_results": 10,
                "section_hint": None,
                "prefer_exact_matches": False,
            },
        )

    def test_retrieve_normalizes_scope_and_intent_before_querying(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-retrieve-normalized-scope-intent",
        )

        retrieval = self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="  doc:doc-1  ",
            intent="  lookup  ",
        )

        self.assertEqual(retrieval.query.scope, "doc:doc-1")
        self.assertEqual(retrieval.query.intent, "lookup")

        stored = self.service.get_run(run.run_id)
        self.assertEqual(stored.artifacts[1].payload["query_scope"], "doc:doc-1")
        self.assertEqual(stored.artifacts[1].payload["query_intent"], "lookup")
        self.assertEqual(
            self.service.describe_run_flow(run.run_id).retrieval_evidence,
            {
                "artifact_id": f"{run.run_id}:0002:retrieval_result",
                "audit_ref": retrieval.audit_ref,
                "query_scope": "doc:doc-1",
                "query_intent": "lookup",
                "retrieval_query_hash": self.service._fingerprint_text("alpha summary"),
                "retrieval_constraints": {
                    "max_results": 10,
                    "section_hint": None,
                    "prefer_exact_matches": False,
                },
                "hit_count": len(retrieval.hits),
                "strategies_used": retrieval.diagnostics["strategies_used"],
                "retrieval_artifact_ids": [f"{run.run_id}:0002:retrieval_result"],
                "retrieval_event_ids": [f"{run.run_id}:0002:retrieval_attached"],
            },
        )

    def test_retrieval_evidence_preserves_full_retrieval_chain(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-retrieval-chain",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )

        first = self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        second = self.service.retrieve(
            run.run_id,
            query_text="beta detail",
            scope="doc:doc-1",
            intent="lookup",
        )
        completed = self.service.complete_run(run.run_id)

        evidence = completed.artifacts[-2].payload["retrieval_evidence"]
        described_evidence = self.service.describe_run_flow(run.run_id).retrieval_evidence
        self.assertEqual(evidence["artifact_id"], f"{run.run_id}:0004:retrieval_result")
        self.assertEqual(described_evidence, evidence)
        self.assertEqual(self.service.get_run_provenance(run.run_id)["retrieval_evidence"], evidence)
        self.assertEqual(evidence["audit_ref"], second.audit_ref)
        self.assertEqual(evidence["retrieval_query_hash"], self.service._fingerprint_text("beta detail"))
        self.assertEqual(
            evidence["retrieval_artifact_ids"],
            [
                f"{run.run_id}:0003:retrieval_result",
                f"{run.run_id}:0004:retrieval_result",
            ],
        )
        self.assertEqual(
            evidence["retrieval_event_ids"],
            [
                f"{run.run_id}:0003:retrieval_attached",
                f"{run.run_id}:0004:retrieval_attached",
            ],
        )
        self.assertEqual(first.audit_ref, self.service.get_run(run.run_id).artifacts[2].payload["audit_ref"])

    def test_retrieval_result_validation_rejects_tampered_provenance_payload(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-tampered-retrieval-provenance",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        self.service.complete_run(run.run_id)

        records = self.service._load_records()
        payload = records[run.run_id]
        payload["artifacts"][2]["payload"]["query_scope"] = ""
        self.service._store.write_json("runs_v1.enc.json", records)

        with self.assertRaisesRegex(ValueError, "incomplete retrieval artifact payload for query_scope"):
            self.service.describe_run_flow(run.run_id)

    def test_retrieval_result_validation_rejects_tampered_query_hash_shape(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-tampered-retrieval-query-hash",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        self.service.complete_run(run.run_id)

        records = self.service._load_records()
        payload = records[run.run_id]
        payload["artifacts"][2]["payload"]["retrieval_query_hash"] = "not-a-sha256-digest"
        payload["events"][2]["payload"]["retrieval_query_hash"] = "not-a-sha256-digest"
        self.service._store.write_json("runs_v1.enc.json", records)

        with self.assertRaisesRegex(ValueError, "invalid retrieval artifact payload for retrieval_query_hash"):
            self.service.describe_run_flow(run.run_id)

    def test_retrieval_result_validation_rejects_tampered_strategy_payload(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-tampered-retrieval-strategy",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        self.service.complete_run(run.run_id)

        records = self.service._load_records()
        payload = records[run.run_id]
        payload["artifacts"][2]["payload"]["strategies_used"] = [""]
        self.service._store.write_json("runs_v1.enc.json", records)

        with self.assertRaisesRegex(ValueError, "invalid retrieval artifact payload for strategies_used"):
            self.service.describe_run_flow(run.run_id)

    def test_retrieval_result_validation_rejects_non_fts_strategy_payload(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-tampered-retrieval-non-fts-strategy",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        self.service.complete_run(run.run_id)

        records = self.service._load_records()
        payload = records[run.run_id]
        payload["artifacts"][2]["payload"]["strategies_used"] = ["semantic"]
        payload["events"][2]["payload"]["strategies_used"] = ["semantic"]
        self.service._store.write_json("runs_v1.enc.json", records)

        with self.assertRaisesRegex(ValueError, "invalid retrieval artifact payload for strategies_used"):
            self.service.describe_run_flow(run.run_id)

    def test_retrieval_result_validation_rejects_tampered_negative_hit_count(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-tampered-retrieval-hit-count",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        self.service.complete_run(run.run_id)

        records = self.service._load_records()
        payload = records[run.run_id]
        payload["artifacts"][2]["payload"]["hit_count"] = -1
        self.service._store.write_json("runs_v1.enc.json", records)

        with self.assertRaisesRegex(ValueError, "invalid retrieval artifact payload for hit_count"):
            self.service.describe_run_flow(run.run_id)

    def test_retrieval_result_validation_rejects_tampered_constraint_payload(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-tampered-retrieval-constraints",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        self.service.complete_run(run.run_id)

        records = self.service._load_records()
        payload = records[run.run_id]
        payload["artifacts"][2]["payload"]["retrieval_constraints"]["max_results"] = "10"
        payload["events"][2]["payload"]["retrieval_constraints"]["max_results"] = "10"
        self.service._store.write_json("runs_v1.enc.json", records)

        with self.assertRaisesRegex(ValueError, "invalid retrieval artifact payload for retrieval_constraints"):
            self.service.describe_run_flow(run.run_id)

    def test_retrieval_result_validation_rejects_tampered_event_provenance_payload(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-tampered-retrieval-event-provenance",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        self.service.complete_run(run.run_id)

        records = self.service._load_records()
        payload = records[run.run_id]
        payload["events"][2]["payload"]["audit_ref"] = "audit-tampered"
        self.service._store.write_json("runs_v1.enc.json", records)

        with self.assertRaisesRegex(ValueError, "inconsistent retrieval event payload for audit_ref"):
            self.service.describe_run_flow(run.run_id)

    def test_retrieval_result_validation_rejects_tampered_event_payload_shape(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-tampered-retrieval-event-shape",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        self.service.complete_run(run.run_id)

        records = self.service._load_records()
        payload = records[run.run_id]
        payload["events"][2]["payload"]["unvalidated_claim"] = "accepted"
        self.service._store.write_json("runs_v1.enc.json", records)

        with self.assertRaisesRegex(ValueError, "inconsistent retrieval event payload keys"):
            self.service.describe_run_flow(run.run_id)

    def test_retrieval_result_validation_rejects_tampered_event_timestamp(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-tampered-retrieval-event-timestamp",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        self.service.complete_run(run.run_id)

        records = self.service._load_records()
        payload = records[run.run_id]
        payload["events"][2]["created_at"] = "2026-01-01T00:00:00+00:00"
        self.service._store.write_json("runs_v1.enc.json", records)

        with self.assertRaisesRegex(ValueError, "inconsistent retrieval event timestamp"):
            self.service.describe_run_flow(run.run_id)

    def test_retrieve_rejects_scope_mismatches_before_querying(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-retrieve-scope-mismatch",
        )

        with self.assertRaisesRegex(ValueError, "retrieve requires scope doc:doc-1"):
            self.service.retrieve(
                run.run_id,
                query_text="alpha summary",
                scope="doc:doc-2",
                intent="lookup",
            )

        stored = self.service.get_run(run.run_id)
        self.assertEqual([artifact.kind for artifact in stored.artifacts], ["run_started"])
        self.assertEqual([event.name for event in stored.events], ["run_started"])

    def test_retrieve_rejects_invalid_retrieval_confidentiality_profile_before_querying(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-retrieve-invalid-profile",
        )

        with self.assertRaisesRegex(
            ValueError,
            "retrieval_confidentiality_profile must be one of: confidential, standard",
        ):
            self.service.retrieve(
                run.run_id,
                query_text="alpha summary",
                scope="doc:doc-1",
                intent="lookup",
                confidentiality_profile="public",
            )

        stored = self.service.get_run(run.run_id)
        self.assertEqual([artifact.kind for artifact in stored.artifacts], ["run_started"])
        self.assertEqual([event.name for event in stored.events], ["run_started"])

    def test_run_flow_finalizes_failed_runs_when_retrieval_raises(self) -> None:
        started_run_ids: list[str] = []
        original_start_run = self.service.start_run

        def tracking_start_run(
            *,
            operation: str,
            scope: str,
            intent: str,
            request_fingerprint: str,
            run_id: str | None = None,
        ):
            run = original_start_run(
                operation=operation,
                scope=scope,
                intent=intent,
                request_fingerprint=request_fingerprint,
                run_id=run_id,
            )
            started_run_ids.append(run.run_id)
            return run

        class FailingRetrievalService:
            def retrieve_auto(self, query):  # type: ignore[no-untyped-def]
                raise RuntimeError("retrieval exploded")

        self.service.start_run = tracking_start_run  # type: ignore[method-assign]
        original_retrieval = self.service._retrieval
        self.service._retrieval = FailingRetrievalService()  # type: ignore[assignment]

        try:
            with self.assertRaisesRegex(RuntimeError, "retrieval exploded"):
                self.service.run_flow(
                    operation="draft",
                    scope="doc:doc-1",
                    intent="outline",
                    request_fingerprint="fp-failure-1",
                    retrieval_query_text="alpha summary",
                    final_status="cancelled",
                )
        finally:
            self.service._retrieval = original_retrieval
            self.service.start_run = original_start_run  # type: ignore[method-assign]

        self.assertEqual(len(started_run_ids), 1)
        stored = self.service.get_run(started_run_ids[0])
        self.assertEqual(stored.status, "failed")
        self.assertEqual(
            [artifact.kind for artifact in stored.artifacts],
            ["run_started", "run_plan", "run_failure", "run_provenance", "run_completed"],
        )
        self.assertEqual(
            [event.name for event in stored.events],
            ["run_started", "run_planned", "run_failed", "run_provenance_captured", "run_completed"],
        )
        self.assertEqual(stored.artifacts[0].payload["status"], "running")
        self.assertEqual(stored.artifacts[1].payload["planned_terminal_status"], "cancelled")
        self.assertRegex(stored.artifacts[1].payload["plan_digest"], r"^[0-9a-f]{64}$")
        self.assertEqual(stored.artifacts[1].payload["patch_requested"], False)
        self.assertEqual(stored.artifacts[1].payload["export_requested"], False)
        self.assertEqual(stored.artifacts[2].payload["error_type"], "RuntimeError")
        self.assertEqual(stored.artifacts[2].payload["error_message"], "retrieval exploded")
        self.assertEqual(stored.artifacts[2].payload["failed_phase"], "retrieve")
        self.assertEqual(stored.artifacts[2].payload["planned_terminal_status"], "cancelled")
        self.assertEqual(stored.artifacts[2].payload["actual_terminal_status"], "failed")
        self.assertEqual(stored.artifacts[2].payload["run_plan_digest"], stored.artifacts[1].payload["plan_digest"])
        self.assertEqual(stored.artifacts[3].payload["planned_terminal_status"], "cancelled")
        self.assertEqual(stored.artifacts[3].payload["status"], "failed")
        self.assertEqual(stored.artifacts[3].payload["actual_terminal_status"], "failed")
        self.assertEqual(stored.artifacts[3].payload["run_plan_digest"], stored.artifacts[1].payload["plan_digest"])
        self.assertEqual(stored.artifacts[3].payload["request_fingerprint"], "fp-failure-1")
        manifest = self.service.describe_run_manifest(started_run_ids[0])
        summary = self.service.summarize_run(started_run_ids[0])
        self.assertEqual(summary.status, "failed")
        self.assertIsNotNone(summary.latest_failure_artifact)
        self.assertEqual(summary.latest_failure_artifact.artifact_id, f"{started_run_ids[0]}:0003:run_failure")
        self.assertRegex(manifest["run_lifecycle_digest"], r"^[0-9a-f]{64}$")
        self.assertEqual(manifest["summary"], manifest["run_summary"])
        self.assertEqual(
            manifest["run_lifecycle_digest"],
            self.service._fingerprint_payload(manifest["run_lifecycle"]),
        )
        lines = [json.loads(line) for line in (self.root / "audit_events.jsonl").read_text(encoding="utf-8").splitlines()]
        flow_failure_event = next(item for item in lines if item["name"] == "engine_run_flow_failed_summary")
        self.assertEqual(flow_failure_event["metadata"]["run_lifecycle"], manifest["run_lifecycle"])
        self.assertEqual(flow_failure_event["metadata"]["run_lifecycle_digest"], manifest["run_lifecycle_digest"])
        self.assertEqual(
            stored.artifacts[3].payload["run_failure_artifacts"],
            [
                {
                    "artifact_id": f"{started_run_ids[0]}:0003:run_failure",
                    "error_type": "RuntimeError",
                    "error_message": "retrieval exploded",
                    "failed_phase": "retrieve",
                    "planned_terminal_status": "cancelled",
                    "actual_terminal_status": "failed",
                    "run_plan_digest": stored.artifacts[1].payload["plan_digest"],
                }
            ],
        )
        self.assertEqual(
            stored.artifacts[2].payload["failure_context"]["artifact_sequence"],
            ["run_started", "run_plan"],
        )
        self.assertEqual(
            stored.artifacts[2].payload["failure_context"]["event_sequence"],
            ["run_started", "run_planned"],
        )
        self.assertEqual(
            stored.artifacts[2].payload["failure_context"]["artifact_refs"]["run_failure"],
            [],
        )
        self.assertEqual(
            stored.artifacts[2].payload["failure_context"]["event_refs"]["run_failed"],
            [],
        )
        self.assertEqual(stored.artifacts[2].payload["operation"], "draft")
        self.assertEqual(stored.artifacts[2].payload["scope"], "doc:doc-1")
        self.assertEqual(stored.artifacts[2].payload["intent"], "outline")
        self.assertEqual(stored.artifacts[2].payload["request_fingerprint"], "fp-failure-1")
        self.assertEqual(manifest["run_provenance"], stored.artifacts[3].payload)
        self.assertEqual(
            manifest["artifact_refs"]["run_failure"],
            [f"{started_run_ids[0]}:0003:run_failure"],
        )
        self.assertEqual(
            manifest["event_refs"]["run_failed"],
            [f"{started_run_ids[0]}:0003:run_failed"],
        )
        self.assertEqual(
            manifest["run_lifecycle"],
            {
                "artifact_count": 5,
                "event_count": 5,
                "artifact_sequence": [
                    "run_started",
                    "run_plan",
                    "run_failure",
                    "run_provenance",
                    "run_completed",
                ],
                "event_sequence": [
                    "run_started",
                    "run_planned",
                    "run_failed",
                    "run_provenance_captured",
                    "run_completed",
                ],
                "latest_artifact_id": f"{started_run_ids[0]}:0005:run_completed",
                "latest_event_id": f"{started_run_ids[0]}:0005:run_completed",
                "terminal_artifact_sequence": [
                    "run_provenance",
                    "run_completed",
                ],
                "terminal_event_sequence": [
                    "run_provenance_captured",
                    "run_completed",
                ],
                "terminal_artifact_refs": {
                    "run_provenance": [f"{started_run_ids[0]}:0004:run_provenance"],
                    "run_completed": [f"{started_run_ids[0]}:0005:run_completed"],
                },
                "terminal_event_refs": {
                    "run_provenance_captured": [f"{started_run_ids[0]}:0004:run_provenance_captured"],
                    "run_completed": [f"{started_run_ids[0]}:0005:run_completed"],
                },
                "pending_patch_proposals": [],
            },
        )
        self.assertEqual(stored.events[2].payload["run_plan_digest"], stored.artifacts[1].payload["plan_digest"])
        self.assertEqual(stored.events[2].payload["operation"], "draft")
        self.assertEqual(stored.events[2].payload["scope"], "doc:doc-1")
        self.assertEqual(stored.events[2].payload["intent"], "outline")
        self.assertEqual(stored.events[2].payload["request_fingerprint"], "fp-failure-1")
        self.assertEqual(
            stored.artifacts[3].payload["artifact_refs"]["run_failure"],
            [f"{started_run_ids[0]}:0003:run_failure"],
        )
        self.assertEqual(
            stored.artifacts[3].payload["event_refs"]["run_failed"],
            [f"{started_run_ids[0]}:0003:run_failed"],
        )
        lines = [
            json.loads(line)
            for line in (self.root / "audit_events.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        audit_names = [item["name"] for item in lines]
        self.assertIn("engine_run_failed_summary", audit_names)
        self.assertIn("engine_run_flow_failed_summary", audit_names)
        failed_event = next(item for item in lines if item["name"] == "engine_run_failed_summary")
        flow_failed_event = next(item for item in lines if item["name"] == "engine_run_flow_failed_summary")
        self.assertEqual(failed_event["metadata"]["operation"], "draft")
        self.assertEqual(failed_event["metadata"]["scope"], "doc:doc-1")
        self.assertEqual(failed_event["metadata"]["intent"], "outline")
        self.assertEqual(failed_event["metadata"]["request_fingerprint"], "fp-failure-1")
        self.assertEqual(failed_event["metadata"]["failed_phase"], "retrieve")
        self.assertEqual(failed_event["metadata"]["planned_terminal_status"], "cancelled")
        self.assertEqual(failed_event["metadata"]["actual_terminal_status"], "failed")
        self.assertEqual(failed_event["metadata"]["artifact_count"], 2)
        self.assertEqual(failed_event["metadata"]["event_count"], 2)
        self.assertEqual(failed_event["metadata"]["run_plan_digest"], stored.artifacts[1].payload["plan_digest"])
        self.assertEqual(
            failed_event["metadata"]["pending_patch_proposals"],
            [],
        )
        self.assertRegex(failed_event["metadata"]["flow_digest"], r"^[0-9a-f]{64}$")
        self.assertEqual(flow_failed_event["metadata"]["run_id"], started_run_ids[0])
        self.assertEqual(flow_failed_event["metadata"]["status"], "failed")
        self.assertEqual(flow_failed_event["metadata"]["failed_phase"], "retrieve")
        self.assertEqual(flow_failed_event["metadata"]["planned_terminal_status"], "cancelled")
        self.assertEqual(flow_failed_event["metadata"]["actual_terminal_status"], "failed")
        self.assertEqual(flow_failed_event["metadata"]["artifact_count"], 5)
        self.assertEqual(flow_failed_event["metadata"]["event_count"], 5)
        self.assertEqual(flow_failed_event["metadata"]["run_plan_digest"], stored.artifacts[1].payload["plan_digest"])
        self.assertEqual(
            flow_failed_event["metadata"]["terminal_artifact_refs"],
            {
                "run_provenance": [f"{started_run_ids[0]}:0004:run_provenance"],
                "run_completed": [f"{started_run_ids[0]}:0005:run_completed"],
            },
        )
        self.assertEqual(
            flow_failed_event["metadata"]["terminal_event_refs"],
            {
                "run_provenance_captured": [f"{started_run_ids[0]}:0004:run_provenance_captured"],
                "run_completed": [f"{started_run_ids[0]}:0005:run_completed"],
            },
        )
        self.assertRegex(flow_failed_event["metadata"]["flow_digest"], r"^[0-9a-f]{64}$")

    def test_run_flow_keeps_original_failure_when_failure_summary_snapshot_fails(self) -> None:
        started_run_ids: list[str] = []
        original_start_run = self.service.start_run
        original_describe_run_flow = self.service.describe_run_flow
        original_retrieval = self.service._retrieval

        def tracking_start_run(
            *,
            operation: str,
            scope: str,
            intent: str,
            request_fingerprint: str,
            run_id: str | None = None,
        ):
            run = original_start_run(
                operation=operation,
                scope=scope,
                intent=intent,
                request_fingerprint=request_fingerprint,
                run_id=run_id,
            )
            started_run_ids.append(run.run_id)
            return run

        class FailingRetrievalService:
            def retrieve_auto(self, query):  # type: ignore[no-untyped-def]
                raise RuntimeError("retrieval exploded")

        def failing_describe_run_flow(run_id: str):  # type: ignore[no-untyped-def]
            raise AssertionError(f"describe_run_flow exploded for {run_id}")

        self.service.start_run = tracking_start_run  # type: ignore[method-assign]
        self.service._retrieval = FailingRetrievalService()  # type: ignore[assignment]
        self.service.describe_run_flow = failing_describe_run_flow  # type: ignore[method-assign]

        try:
            with self.assertRaisesRegex(RuntimeError, "retrieval exploded"):
                self.service.run_flow(
                    operation="draft",
                    scope="doc:doc-1",
                    intent="outline",
                    request_fingerprint="fp-failure-summary",
                    retrieval_query_text="alpha summary",
                    final_status="cancelled",
                )
        finally:
            self.service._retrieval = original_retrieval
            self.service.start_run = original_start_run  # type: ignore[method-assign]
            self.service.describe_run_flow = original_describe_run_flow  # type: ignore[method-assign]

        self.assertEqual(len(started_run_ids), 1)
        stored = self.service.get_run(started_run_ids[0])
        self.assertEqual(stored.status, "failed")
        lines = [
            json.loads(line)
            for line in (self.root / "audit_events.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        flow_failed_event = next(item for item in lines if item["name"] == "engine_run_flow_failed_summary")
        self.assertEqual(flow_failed_event["metadata"]["summary_source"], "fallback")
        self.assertEqual(flow_failed_event["metadata"]["summary_error_type"], "AssertionError")
        self.assertIn("describe_run_flow exploded", flow_failed_event["metadata"]["summary_error_message"])
        self.assertEqual(flow_failed_event["metadata"]["error_type"], "RuntimeError")
        self.assertEqual(flow_failed_event["metadata"]["error_message"], "retrieval exploded")
        self.assertEqual(flow_failed_event["metadata"]["status"], "failed")

    def test_run_flow_records_export_context_when_final_export_fails(self) -> None:
        started_run_ids: list[str] = []
        original_start_run = self.service.start_run
        original_export = self.service._export

        def tracking_start_run(
            *,
            operation: str,
            scope: str,
            intent: str,
            request_fingerprint: str,
            run_id: str | None = None,
        ):
            run = original_start_run(
                operation=operation,
                scope=scope,
                intent=intent,
                request_fingerprint=request_fingerprint,
                run_id=run_id,
            )
            started_run_ids.append(run.run_id)
            return run

        class FailingExportService:
            def __init__(self, delegate):  # type: ignore[no-untyped-def]
                self._delegate = delegate

            def preview(self, options):  # type: ignore[no-untyped-def]
                return self._delegate.preview(options)

            def final(self, options, *, destination_path, export_approved=False):  # type: ignore[no-untyped-def]
                raise RuntimeError("export exploded")

        self.service.start_run = tracking_start_run  # type: ignore[method-assign]
        self.service._export = FailingExportService(self.export)  # type: ignore[assignment]

        try:
            with self.assertRaisesRegex(RuntimeError, "export exploded"):
                self.service.run_flow(
                    operation="draft",
                    scope="doc:doc-1",
                    intent="outline",
                    request_fingerprint="fp-failure-export",
                    retrieval_query_text="alpha summary",
                    export_options=self._options(output_format="docx"),
                    export_destination_path=self.root / "exports" / "draft.docx",
                    export_approved=True,
                )
        finally:
            self.service._export = original_export
            self.service.start_run = original_start_run  # type: ignore[method-assign]

        self.assertEqual(len(started_run_ids), 1)
        stored = self.service.get_run(started_run_ids[0])
        self.assertEqual(stored.status, "failed")
        self.assertEqual(
            [artifact.kind for artifact in stored.artifacts],
            ["run_started", "run_plan", "retrieval_result", "export_preview", "run_failure", "run_provenance", "run_completed"],
        )
        self.assertEqual(
            [event.name for event in stored.events],
            [
                "run_started",
                "run_planned",
                "retrieval_attached",
                "export_preview_attached",
                "run_failed",
                "run_provenance_captured",
                "run_completed",
            ],
        )
        self.assertEqual(
            stored.artifacts[4].payload["export_preview_artifacts"],
            [
                {
                    "artifact_id": f"{started_run_ids[0]}:0004:export_preview",
                    "output_format": "pdf",
                    "size_bytes": stored.artifacts[3].payload["size_bytes"],
                    "expires_at": stored.artifacts[3].payload["expires_at"],
                    "storage_ref": stored.artifacts[3].payload["storage_ref"],
                    "options_fingerprint": stored.artifacts[3].payload["options_fingerprint"],
                }
            ],
        )
        self.assertEqual(stored.artifacts[4].payload["failed_phase"], "export_final")
        self.assertEqual(stored.artifacts[4].payload["export_final_artifacts"], [])
        self.assertEqual(stored.artifacts[4].payload["patch_proposals"], [])
        self.assertEqual(stored.artifacts[4].payload["patch_decisions"], [])
        self.assertEqual(
            stored.artifacts[5].payload["run_failure_artifacts"],
            [
                {
                    "artifact_id": f"{started_run_ids[0]}:0005:run_failure",
                    "error_type": "RuntimeError",
                    "error_message": "export exploded",
                    "failed_phase": "export_final",
                    "planned_terminal_status": "completed",
                    "actual_terminal_status": "failed",
                    "run_plan_digest": stored.artifacts[1].payload["plan_digest"],
                }
            ],
        )
        self.assertEqual(stored.artifacts[4].payload["artifact_count"], 4)
        self.assertEqual(stored.artifacts[4].payload["event_count"], 4)
        self.assertEqual(
            stored.artifacts[4].payload["artifact_sequence"],
            ["run_started", "run_plan", "retrieval_result", "export_preview"],
        )
        self.assertEqual(
            stored.artifacts[4].payload["event_sequence"],
            ["run_started", "run_planned", "retrieval_attached", "export_preview_attached"],
        )
        self.assertEqual(
            stored.artifacts[4].payload["flow_steps"],
            [
                {
                    "sequence": 1,
                    "artifact_id": f"{started_run_ids[0]}:0001:run_started",
                    "artifact_kind": "run_started",
                    "artifact_created_at": stored.artifacts[0].created_at,
                    "event_id": f"{started_run_ids[0]}:0001:run_started",
                    "event_name": "run_started",
                    "event_created_at": stored.events[0].created_at,
                },
                {
                    "sequence": 2,
                    "artifact_id": f"{started_run_ids[0]}:0002:run_plan",
                    "artifact_kind": "run_plan",
                    "artifact_created_at": stored.artifacts[1].created_at,
                    "event_id": f"{started_run_ids[0]}:0002:run_planned",
                    "event_name": "run_planned",
                    "event_created_at": stored.events[1].created_at,
                },
                {
                    "sequence": 3,
                    "artifact_id": f"{started_run_ids[0]}:0003:retrieval_result",
                    "artifact_kind": "retrieval_result",
                    "artifact_created_at": stored.artifacts[2].created_at,
                    "event_id": f"{started_run_ids[0]}:0003:retrieval_attached",
                    "event_name": "retrieval_attached",
                    "event_created_at": stored.events[2].created_at,
                },
                {
                    "sequence": 4,
                    "artifact_id": f"{started_run_ids[0]}:0004:export_preview",
                    "artifact_kind": "export_preview",
                    "artifact_created_at": stored.artifacts[3].created_at,
                    "event_id": f"{started_run_ids[0]}:0004:export_preview_attached",
                    "event_name": "export_preview_attached",
                    "event_created_at": stored.events[3].created_at,
                },
            ],
        )

    def test_timestamp_normalizes_awareness_to_utc(self) -> None:
        aware_now = datetime(2026, 1, 1, 12, 30, tzinfo=timezone(timedelta(hours=-8)))
        service = EngineRunService(
            vault_root=self.root,
            audit_log=self.audit,
            retrieval_service=self.retrieval,
            export_service=self.export,
            drafting_service=DraftingService(),
            now_fn=lambda: aware_now,
        )

        run = service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-timestamp",
        )

        self.assertEqual(run.started_at, "2026-01-01T20:30:00+00:00")
        self.assertEqual(service.get_run(run.run_id).updated_at, "2026-01-01T20:30:00+00:00")

    def test_invalid_patch_decisions_and_terminal_statuses_are_rejected(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-4",
        )
        self.service.propose_patch(
            run.run_id,
            original="before\n",
            proposed="after\n",
            target_path="notes.md",
        )

        with self.assertRaisesRegex(ValueError, "patch decision must be one of"):
            self.service.record_patch_decision(
                run.run_id,
                decision="approve",  # type: ignore[arg-type]
                target_path="notes.md",
            )
        with self.assertRaisesRegex(ValueError, "terminal run status must be one of"):
            self.service.complete_run(
                run.run_id,
                status="done",  # type: ignore[arg-type]
            )

    def test_terminal_runs_reject_additional_mutations(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-2",
        )
        self.service.complete_run(run.run_id, status="failed")

        with self.assertRaisesRegex(ValueError, "not mutable: failed"):
            self.service.retrieve(
                run.run_id,
                query_text="alpha",
                scope="doc:doc-1",
                intent="lookup",
            )
        with self.assertRaisesRegex(ValueError, "not mutable: failed"):
            self.service.propose_patch(
                run.run_id,
                original="before\n",
                proposed="after\n",
                target_path="notes.md",
            )
        with self.assertRaisesRegex(ValueError, "not mutable: failed"):
            self.service.record_patch_decision(
                run.run_id,
                decision="rejected",
                target_path="notes.md",
            )
        with self.assertRaisesRegex(ValueError, "not mutable: failed"):
            self.service.preview_export(run.run_id, options=self._options())
        with self.assertRaisesRegex(ValueError, "not mutable: failed"):
            self.service.final_export(
                run.run_id,
                options=self._options(confidentiality_profile="standard"),
                destination_path=self.root / "exports" / "draft.pdf",
                export_approved=True,
            )
        with self.assertRaisesRegex(ValueError, "already terminal: failed"):
            self.service.complete_run(run.run_id, status="cancelled")

        stored = self.service.get_run(run.run_id)
        self.assertEqual(
            [artifact.kind for artifact in stored.artifacts],
            ["run_started", "run_provenance", "run_completed"],
        )
        self.assertEqual(
            [event.name for event in stored.events],
            ["run_started", "run_provenance_captured", "run_completed"],
        )
        self.assertEqual(stored.status, "failed")

    def test_terminal_cleanup_allows_failed_and_cancelled_completion_with_pending_proposals(self) -> None:
        for status in ("failed", "cancelled"):
            with self.subTest(status=status):
                run = self.service.start_run(
                    operation="draft",
                    scope="doc:doc-1",
                    intent="outline",
                    request_fingerprint=f"fp-cleanup-{status}",
                )
                self.service.propose_patch(
                    run.run_id,
                    original="before\n",
                    proposed="after\n",
                    target_path="notes.md",
                )

                completed = self.service.complete_run(run.run_id, status=status)  # type: ignore[arg-type]

                self.assertEqual(completed.status, status)
                self.assertEqual(
                    [artifact.kind for artifact in completed.artifacts],
                    ["run_started", "patch_proposal", "run_provenance", "run_completed"],
                )
                self.assertEqual(
                    completed.artifacts[-2].payload["pending_patch_proposals"],
                    [
                        {
                            "artifact_id": f"{run.run_id}:0002:patch_proposal",
                            "target_path": "notes.md",
                        }
                    ],
                )
                self.assertEqual(
                    completed.artifacts[-2].payload["terminal_artifact_sequence"],
                    ["run_provenance", "run_completed"],
                )
                self.assertEqual(
                    completed.artifacts[-2].payload["terminal_event_sequence"],
                    ["run_provenance_captured", "run_completed"],
                )

    def test_terminal_snapshots_reject_incomplete_completion_state(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-corrupt-terminal",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        self.service.complete_run(run.run_id)

        records = self.service._load_records()
        payload = records[run.run_id]
        payload["artifacts"] = payload["artifacts"][:-2]
        payload["events"] = payload["events"][:-2]
        self.service._store.write_json("runs_v1.enc.json", records)

        with self.assertRaisesRegex(ValueError, "inconsistent terminal artifact sequence"):
            self.service.describe_run_flow(run.run_id)

    def test_terminal_snapshots_reject_duplicate_terminal_artifacts_before_completion(self) -> None:
        corrupted = EngineRunRecord(
            run_id="run-duplicate-terminal",
            status="completed",
            started_at="2026-01-01T00:00:00+00:00",
            updated_at="2026-01-01T00:00:04+00:00",
            completed_at="2026-01-01T00:00:04+00:00",
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-duplicate-terminal",
            artifacts=[
                RunArtifact(
                    artifact_id="run-duplicate-terminal:0001:run_started",
                    kind="run_started",
                    created_at="2026-01-01T00:00:00+00:00",
                    payload={"status": "running"},
                ),
                RunArtifact(
                    artifact_id="run-duplicate-terminal:0002:run_plan",
                    kind="run_plan",
                    created_at="2026-01-01T00:00:01+00:00",
                    payload={"planned_terminal_status": "completed"},
                ),
                RunArtifact(
                    artifact_id="run-duplicate-terminal:0003:retrieval_result",
                    kind="retrieval_result",
                    created_at="2026-01-01T00:00:02+00:00",
                    payload={
                        "audit_ref": "audit-duplicate-terminal",
                        "query_scope": "doc:doc-1",
                        "query_intent": "lookup",
                        "retrieval_query_hash": "a" * 64,
                        "retrieval_constraints": {
                            "max_results": 10,
                            "section_hint": None,
                            "prefer_exact_matches": False,
                        },
                        "hit_count": 1,
                        "strategies_used": ["fts"],
                    },
                ),
                RunArtifact(
                    artifact_id="run-duplicate-terminal:0004:run_provenance",
                    kind="run_provenance",
                    created_at="2026-01-01T00:00:03+00:00",
                    payload={"status": "completed"},
                ),
                RunArtifact(
                    artifact_id="run-duplicate-terminal:0005:run_completed",
                    kind="run_completed",
                    created_at="2026-01-01T00:00:03+00:00",
                    payload={"status": "completed"},
                ),
                RunArtifact(
                    artifact_id="run-duplicate-terminal:0006:run_provenance",
                    kind="run_provenance",
                    created_at="2026-01-01T00:00:04+00:00",
                    payload={"status": "completed"},
                ),
                RunArtifact(
                    artifact_id="run-duplicate-terminal:0007:run_completed",
                    kind="run_completed",
                    created_at="2026-01-01T00:00:04+00:00",
                    payload={"status": "completed"},
                ),
            ],
            events=[
                RunEvent(
                    event_id="run-duplicate-terminal:0001:run_started",
                    name="run_started",
                    created_at="2026-01-01T00:00:00+00:00",
                    payload={"status": "running"},
                ),
                RunEvent(
                    event_id="run-duplicate-terminal:0002:run_planned",
                    name="run_planned",
                    created_at="2026-01-01T00:00:01+00:00",
                    payload={"planned_terminal_status": "completed"},
                ),
                RunEvent(
                    event_id="run-duplicate-terminal:0003:retrieval_attached",
                    name="retrieval_attached",
                    created_at="2026-01-01T00:00:02+00:00",
                    payload={
                        "artifact_id": "run-duplicate-terminal:0003:retrieval_result",
                        "audit_ref": "audit-duplicate-terminal",
                        "query_scope": "doc:doc-1",
                        "query_intent": "lookup",
                        "retrieval_query_hash": "a" * 64,
                        "retrieval_constraints": {
                            "max_results": 10,
                            "section_hint": None,
                            "prefer_exact_matches": False,
                        },
                        "hit_count": 1,
                        "strategies_used": ["fts"],
                    },
                ),
                RunEvent(
                    event_id="run-duplicate-terminal:0004:run_provenance_captured",
                    name="run_provenance_captured",
                    created_at="2026-01-01T00:00:03+00:00",
                    payload={"artifact_id": "run-duplicate-terminal:0004:run_provenance"},
                ),
                RunEvent(
                    event_id="run-duplicate-terminal:0005:run_completed",
                    name="run_completed",
                    created_at="2026-01-01T00:00:03+00:00",
                    payload={"artifact_id": "run-duplicate-terminal:0005:run_completed"},
                ),
                RunEvent(
                    event_id="run-duplicate-terminal:0006:run_provenance_captured",
                    name="run_provenance_captured",
                    created_at="2026-01-01T00:00:04+00:00",
                    payload={"artifact_id": "run-duplicate-terminal:0006:run_provenance"},
                ),
                RunEvent(
                    event_id="run-duplicate-terminal:0007:run_completed",
                    name="run_completed",
                    created_at="2026-01-01T00:00:04+00:00",
                    payload={"artifact_id": "run-duplicate-terminal:0007:run_completed"},
                ),
            ],
        )

        with self.assertRaisesRegex(ValueError, "inconsistent terminal artifact count"):
            EngineRunService._validate_record_state(corrupted)

    def test_terminal_snapshots_reject_tampered_run_lifecycle(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-tampered-lifecycle",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        self.service.complete_run(run.run_id)

        records = self.service._load_records()
        payload = records[run.run_id]
        payload["artifacts"][-2]["payload"]["run_lifecycle"]["artifact_count"] = 999
        self.service._store.write_json("runs_v1.enc.json", records)

        with self.assertRaisesRegex(ValueError, "inconsistent terminal provenance run_lifecycle"):
            self.service.describe_run_flow(run.run_id)

    def test_terminal_snapshots_reject_tampered_completion_digest(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-tampered-completion-digest",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        self.service.complete_run(run.run_id)

        records = self.service._load_records()
        payload = records[run.run_id]
        payload["artifacts"][-1]["payload"]["run_lifecycle_digest"] = "not-the-provenance-digest"
        self.service._store.write_json("runs_v1.enc.json", records)

        with self.assertRaisesRegex(ValueError, "inconsistent completion run_lifecycle_digest"):
            self.service.describe_run_flow(run.run_id)

    def test_running_record_rejects_corrupted_append_only_sequence(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-corrupt-running",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )

        records = self.service._load_records()
        payload = records[run.run_id]
        payload["artifacts"][1], payload["artifacts"][2] = payload["artifacts"][2], payload["artifacts"][1]
        self.service._store.write_json("runs_v1.enc.json", records)

        with self.assertRaisesRegex(ValueError, "inconsistent artifact sequence at position 2"):
            self.service.get_run(run.run_id)

    def test_running_record_rejects_terminal_artifacts_and_events(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-running-terminal",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )

        records = self.service._load_records()
        payload = records[run.run_id]
        terminal_at = payload["artifacts"][-1]["created_at"]
        payload["artifacts"].append(
            {
                "artifact_id": f"{run.run_id}:0004:run_provenance",
                "kind": "run_provenance",
                "created_at": terminal_at,
                "payload": {"status": "running"},
            }
        )
        self.service._store.write_json("runs_v1.enc.json", records)

        with self.assertRaisesRegex(ValueError, "is running but has terminal artifacts"):
            self.service.get_run(run.run_id)

        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-running-terminal-event",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )

        records = self.service._load_records()
        payload = records[run.run_id]
        terminal_at = payload["events"][-1]["created_at"]
        payload["events"].append(
            {
                "event_id": f"{run.run_id}:0004:run_provenance_captured",
                "name": "run_provenance_captured",
                "created_at": terminal_at,
                "payload": {"artifact_id": f"{run.run_id}:0004:run_provenance"},
            }
        )
        self.service._store.write_json("runs_v1.enc.json", records)

        with self.assertRaisesRegex(ValueError, "is running but has terminal events"):
            self.service.get_run(run.run_id)

    def test_completed_terminalization_and_exports_require_retrieval_evidence(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-retrieval-required",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )

        with self.assertRaisesRegex(ValueError, "export preview requires retrieval evidence"):
            self.service.preview_export(run.run_id, options=self._options())
        with self.assertRaisesRegex(ValueError, "final export requires retrieval evidence"):
            self.service.final_export(
                run.run_id,
                options=self._options(),
                destination_path=self.root / "exports" / "draft.pdf",
                export_approved=True,
            )
        with self.assertRaisesRegex(ValueError, "run completion requires retrieval evidence"):
            self.service.complete_run(run.run_id)

        failed = self.service.complete_run(run.run_id, status="failed")
        self.assertEqual(failed.status, "failed")
        self.assertEqual(
            [artifact.kind for artifact in failed.artifacts],
            ["run_started", "run_plan", "run_provenance", "run_completed"],
        )

    def test_completed_export_and_completion_require_a_run_plan(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-plan-required",
        )

        with self.assertRaisesRegex(ValueError, "export preview requires a recorded run plan"):
            self.service.preview_export(run.run_id, options=self._options())
        with self.assertRaisesRegex(ValueError, "final export requires a recorded run plan"):
            self.service.final_export(
                run.run_id,
                options=self._options(),
                destination_path=self.root / "exports" / "draft.pdf",
                export_approved=True,
            )
        with self.assertRaisesRegex(ValueError, "run completion requires a recorded run plan"):
            self.service.complete_run(run.run_id)

        stored = self.service.get_run(run.run_id)
        self.assertEqual([artifact.kind for artifact in stored.artifacts], ["run_started"])
        self.assertEqual([event.name for event in stored.events], ["run_started"])

    def test_patch_decision_requires_matching_proposal_and_deduplicates(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-3",
        )

        with self.assertRaisesRegex(ValueError, "no patch proposal recorded"):
            self.service.record_patch_decision(
                run.run_id,
                decision="accepted",
                target_path="notes.md",
            )

        self.service.propose_patch(
            run.run_id,
            original="before\n",
            proposed="after\n",
            target_path="notes.md",
        )
        event = self.service.record_patch_decision(
            run.run_id,
            decision="accepted",
            target_path="notes.md",
        )
        self.assertEqual(event.payload["proposal_artifact_id"], f"{run.run_id}:0002:patch_proposal")
        self.assertEqual(event.payload["decision_artifact_id"], f"{run.run_id}:0003:patch_decision")
        self.assertEqual(event.payload["decision_event_id"], f"{run.run_id}:0003:patch_applied")
        self.assertEqual(
            self.service.get_run(run.run_id).artifacts[2].payload["decision_event_id"],
            f"{run.run_id}:0003:patch_applied",
        )

        with self.assertRaisesRegex(ValueError, "patch decision already recorded"):
            self.service.record_patch_decision(
                run.run_id,
                decision="rejected",
                target_path="notes.md",
            )

    def test_patch_decision_rejects_accepted_empty_patch_proposal(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-empty-patch",
        )

        patch = self.service.propose_patch(
            run.run_id,
            original="before\n",
            proposed="before\n",
            target_path="notes.md",
        )

        self.assertEqual(patch, "")
        with self.assertRaisesRegex(ValueError, "accepted patch decision requires a non-empty patch proposal"):
            self.service.record_patch_decision(
                run.run_id,
                decision="accepted",
                target_path="notes.md",
            )

        stored_after_failed_decision = self.service.get_run(run.run_id)
        self.assertNotIn("patch_decision", [artifact.kind for artifact in stored_after_failed_decision.artifacts])
        self.assertNotIn("patch_applied", [event.name for event in stored_after_failed_decision.events])

        event = self.service.record_patch_decision(
            run.run_id,
            decision="rejected",
            target_path="notes.md",
            reason="no changes to apply",
        )

        self.assertEqual(event.name, "patch_rejected")
        self.assertEqual(event.payload["reason"], "no changes to apply")
        self.assertEqual(event.payload["proposal_line_count"], 0)
        self.assertTrue(event.payload["proposal_is_empty"])
        stored = self.service.get_run(run.run_id)
        self.assertEqual(stored.artifacts[-1].kind, "patch_decision")
        self.assertEqual(stored.artifacts[-1].payload["decision"], "rejected")
        self.assertEqual(stored.artifacts[-1].payload["reason"], "no changes to apply")
        self.assertEqual(stored.artifacts[-1].payload["proposal_line_count"], 0)
        self.assertTrue(stored.artifacts[-1].payload["proposal_is_empty"])

    def test_patch_proposals_require_resolution_before_reproposal_on_same_path(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-6",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )

        first_patch = self.service.propose_patch(
            run.run_id,
            original="before\n",
            proposed="after v1\n",
            target_path="notes.md",
        )
        self.assertIn("@@", first_patch)
        with self.assertRaisesRegex(ValueError, "patch proposal already pending for target path: notes.md"):
            self.service.propose_patch(
                run.run_id,
                original="before\n",
                proposed="after v2\n",
                target_path="notes.md",
            )

        decision = self.service.record_patch_decision(
            run.run_id,
            decision="accepted",
            target_path="notes.md",
            reason="latest proposal approved",
        )
        self.assertEqual(decision.payload["proposal_artifact_id"], f"{run.run_id}:0003:patch_proposal")

        second_patch = self.service.propose_patch(
            run.run_id,
            original="before\n",
            proposed="after v2\n",
            target_path="notes.md",
        )
        self.assertIn("@@", second_patch)

        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )
        with self.assertRaisesRegex(ValueError, "final export requires resolved patch proposals"):
            self.service.final_export(
                run.run_id,
                options=self._options(),
                destination_path=self.root / "exports" / "draft.pdf",
                export_approved=True,
            )
        with self.assertRaisesRegex(ValueError, "run completion requires resolved patch proposals"):
            self.service.complete_run(run.run_id)

        second_decision = self.service.record_patch_decision(
            run.run_id,
            decision="accepted",
            target_path="notes.md",
            reason="reproposal approved",
        )
        self.assertEqual(second_decision.payload["proposal_artifact_id"], f"{run.run_id}:0005:patch_proposal")

        export = self.service.final_export(
            run.run_id,
            options=self._options(),
            destination_path=self.root / "exports" / "draft.pdf",
            export_approved=True,
        )
        completed = self.service.complete_run(run.run_id)

        self.assertEqual(export.output_format, "pdf")
        self.assertEqual(completed.status, "completed")
        self.assertEqual(
            completed.artifacts[-2].payload["pending_patch_proposals"],
            [],
        )

    def test_final_export_and_completion_require_resolved_patch_proposals(self) -> None:
        run = self.service.start_run(
            operation="draft",
            scope="doc:doc-1",
            intent="outline",
            request_fingerprint="fp-5",
        )
        self.service.plan_run(
            run.run_id,
            retrieval_query_text="alpha summary",
        )
        self.service.propose_patch(
            run.run_id,
            original="before\n",
            proposed="after\n",
            target_path="notes.md",
        )
        self.service.retrieve(
            run.run_id,
            query_text="alpha summary",
            scope="doc:doc-1",
            intent="lookup",
        )

        with self.assertRaisesRegex(ValueError, "final export requires resolved patch proposals"):
            self.service.final_export(
                run.run_id,
                options=self._options(),
                destination_path=self.root / "exports" / "draft.pdf",
                export_approved=True,
            )
        with self.assertRaisesRegex(ValueError, "run completion requires resolved patch proposals"):
            self.service.complete_run(run.run_id)

        self.service.record_patch_decision(
            run.run_id,
            decision="rejected",
            target_path="notes.md",
            reason="not ready",
        )

        export = self.service.final_export(
            run.run_id,
            options=self._options(),
            destination_path=self.root / "exports" / "draft.pdf",
            export_approved=True,
        )
        self.assertEqual(export.output_format, "pdf")
        completed = self.service.complete_run(run.run_id)
        self.assertEqual(completed.status, "completed")
        self.assertEqual(
            completed.artifacts[-1].payload,
            {
                "status": "completed",
                "operation": "draft",
                "scope": "doc:doc-1",
                "intent": "outline",
                "request_fingerprint": "fp-5",
                "run_provenance_artifact_id": completed.artifacts[-2].artifact_id,
                "run_provenance_event_id": completed.events[-2].event_id,
                "run_lifecycle_digest": completed.artifacts[-2].payload["run_lifecycle_digest"],
                "flow_digest": completed.artifacts[-2].payload["flow_digest"],
            },
        )

    @staticmethod
    def _options(
        *,
        output_format: str = "pdf",
        confidentiality_profile: str = "standard",
    ) -> ExportOptions:
        return ExportOptions(
            style_id="apa",
            template_id="default",
            output_format=output_format,
            scope=ExportScope(type="section", id="sec-1"),
            include=ExportInclude(
                title_page=True,
                toc=False,
                figures_tables_list=False,
                bibliography=True,
            ),
            metadata=ExportMetadata(title="Run Pipeline"),
            confidentiality=ExportConfidentiality(profile=confidentiality_profile),
            engine_limits=ExportLimits(max_render_seconds=60, max_output_bytes=50 * 1024 * 1024),
        )


if __name__ == "__main__":
    unittest.main()
