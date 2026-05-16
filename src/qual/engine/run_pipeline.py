from __future__ import annotations

import hashlib
import json
import uuid
from os import PathLike, fspath
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from src.qual.audit import AuditLog
from src.qual.drafting.service import DraftingService
from src.qual.engine.tools.retrieval_tools import retrieve_auto
from src.qual.engine.vault_store import VaultStore
from src.qual.exporting.service import ExportArtifactRef, ExportOptions, ExportService, PreviewArtifactRef
from src.qual.retrieval.service import RetrievalResult, RetrievalService

_RUN_NAMESPACE = ".engine_runs"
_RUNS_FILE = "runs_v1.enc.json"
_RUNS_KEY_FILE = "engine_runs_v1.key"

RunStatus = Literal["running", "completed", "failed", "cancelled"]
TerminalRunStatus = Literal["completed", "failed", "cancelled"]
PatchDecision = Literal["accepted", "rejected"]
_TERMINAL_RUN_STATUSES: tuple[TerminalRunStatus, ...] = ("completed", "failed", "cancelled")
_RETRIEVAL_INTENT_ALIASES = {"outline": "outline_support"}


@dataclass(frozen=True)
class RunArtifact:
    artifact_id: str
    kind: str
    created_at: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class RunEvent:
    event_id: str
    name: str
    created_at: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class EngineRunRecord:
    run_id: str
    status: RunStatus
    started_at: str
    updated_at: str
    completed_at: str | None
    operation: str
    scope: str
    intent: str
    request_fingerprint: str
    artifacts: list[RunArtifact] = field(default_factory=list)
    events: list[RunEvent] = field(default_factory=list)


@dataclass(frozen=True)
class RunSummary:
    run_id: str
    status: RunStatus
    started_at: str
    updated_at: str
    completed_at: str | None
    operation: str
    scope: str
    intent: str
    request_fingerprint: str
    artifact_count: int
    event_count: int
    latest_artifact: RunArtifact | None
    latest_event: RunEvent | None
    run_plan_digest: str | None = None
    flow_digest: str | None = None
    latest_failure_artifact: RunArtifact | None = None


@dataclass(frozen=True)
class EngineRunFlowResult:
    run: EngineRunRecord
    plan_event: RunEvent
    plan_artifact: RunArtifact
    run_plan_digest: str | None
    flow_digest: str | None
    retrieval_result: RetrievalResult | None
    patch_proposal: str | None
    patch_decision_event: RunEvent | None
    preview_export: PreviewArtifactRef | None
    final_export: ExportArtifactRef | None
    terminal_artifacts: tuple[RunArtifact, RunArtifact]
    terminal_events: tuple[RunEvent, RunEvent]
    run_provenance: dict[str, Any]
    run_lifecycle: dict[str, Any] | None = None
    run_lifecycle_digest: str | None = None
    run_summary: RunSummary | None = None
    flow_snapshot: EngineRunFlowSnapshot | None = None
    run_flow_manifest: dict[str, Any] | None = None
    run_flow_manifest_digest: str | None = None

    def to_manifest(self) -> dict[str, Any]:
        snapshot_manifest = self.flow_snapshot.to_manifest() if self.flow_snapshot is not None else None
        summary = self.run_summary or (self.flow_snapshot.summary if self.flow_snapshot is not None else None)
        summary_manifest = asdict(summary) if summary is not None else None
        run_provenance = self.run_provenance
        if run_provenance is None and self.run_flow_manifest is not None:
            candidate_provenance = self.run_flow_manifest.get("run_provenance")
            if isinstance(candidate_provenance, dict):
                run_provenance = candidate_provenance
        if run_provenance is None and snapshot_manifest is not None:
            candidate_provenance = snapshot_manifest.get("run_provenance")
            if isinstance(candidate_provenance, dict):
                run_provenance = candidate_provenance
        if run_provenance is None:
            run_provenance = EngineRunService._run_provenance_payload(self.run)
        retrieval_evidence = (
            snapshot_manifest["retrieval_evidence"]
            if snapshot_manifest is not None
            else run_provenance.get("retrieval_evidence") if run_provenance is not None else None
        )
        run_lifecycle = self.run_lifecycle
        if run_lifecycle is None and self.run_flow_manifest is not None:
            candidate_lifecycle = self.run_flow_manifest.get("run_lifecycle")
            if isinstance(candidate_lifecycle, dict):
                run_lifecycle = candidate_lifecycle
        if run_lifecycle is None and run_provenance is not None:
            candidate_lifecycle = run_provenance.get("run_lifecycle")
            if isinstance(candidate_lifecycle, dict):
                run_lifecycle = candidate_lifecycle
        if run_lifecycle is None and snapshot_manifest is not None:
            run_lifecycle = snapshot_manifest["run_lifecycle"]
        if summary is None and self.run_flow_manifest is not None:
            candidate_summary = self.run_flow_manifest.get("summary")
            if candidate_summary is None:
                candidate_summary = self.run_flow_manifest.get("run_summary")
            if isinstance(candidate_summary, dict):
                summary = EngineRunService._coerce_run_summary(candidate_summary)
                summary_manifest = asdict(summary)
        if summary is None and run_provenance is not None:
            candidate_summary = run_provenance.get("run_summary")
            if isinstance(candidate_summary, dict):
                expected_artifact_count = candidate_summary.get("artifact_count")
                expected_event_count = candidate_summary.get("event_count")
                if isinstance(expected_artifact_count, int) and isinstance(expected_event_count, int):
                    expected_terminal_artifact_count = expected_artifact_count + 2
                    expected_terminal_event_count = expected_event_count + 2
                    if len(self.run.artifacts) != expected_terminal_artifact_count:
                        raise ValueError("run record drifted from captured provenance")
                    if len(self.run.events) != expected_terminal_event_count:
                        raise ValueError("run record drifted from captured provenance")
            summary = EngineRunService._build_run_summary(self.run)
            summary_manifest = asdict(summary)
        if summary_manifest is not None:
            summary_manifest = EngineRunService._clone_jsonable(summary_manifest)
        run_plan_digest = EngineRunService._fingerprint_plan_artifact(self.plan_artifact)
        flow_digest = (
            EngineRunService._fingerprint_run_provenance(run_provenance)
            if run_provenance is not None
            else self.flow_digest
        )
        if flow_digest is None and snapshot_manifest is not None:
            flow_digest = snapshot_manifest["flow_digest"]
        run_lifecycle_digest = (
            EngineRunService._fingerprint_payload(run_lifecycle)
            if run_lifecycle is not None
            else self.run_lifecycle_digest
        )
        artifact_sequence = None
        event_sequence = None
        flow_steps = None
        artifact_refs = None
        event_refs = None
        terminal_artifact_sequence = None
        terminal_event_sequence = None
        terminal_artifact_refs = None
        terminal_event_refs = None
        pending_patch_proposals = None
        if snapshot_manifest is not None:
            artifact_sequence = snapshot_manifest["artifact_sequence"]
            event_sequence = snapshot_manifest["event_sequence"]
            flow_steps = snapshot_manifest["flow_steps"]
            artifact_refs = snapshot_manifest["artifact_refs"]
            event_refs = snapshot_manifest["event_refs"]
            terminal_artifact_sequence = snapshot_manifest["terminal_artifact_sequence"]
            terminal_event_sequence = snapshot_manifest["terminal_event_sequence"]
            terminal_artifact_refs = snapshot_manifest["terminal_artifact_refs"]
            terminal_event_refs = snapshot_manifest["terminal_event_refs"]
            pending_patch_proposals = snapshot_manifest["pending_patch_proposals"]
        elif self.run_flow_manifest is not None:
            artifact_sequence = self.run_flow_manifest.get("artifact_sequence")
            event_sequence = self.run_flow_manifest.get("event_sequence")
            flow_steps = self.run_flow_manifest.get("flow_steps")
            artifact_refs = self.run_flow_manifest.get("artifact_refs")
            event_refs = self.run_flow_manifest.get("event_refs")
            terminal_artifact_sequence = self.run_flow_manifest.get("terminal_artifact_sequence")
            terminal_event_sequence = self.run_flow_manifest.get("terminal_event_sequence")
            terminal_artifact_refs = self.run_flow_manifest.get("terminal_artifact_refs")
            terminal_event_refs = self.run_flow_manifest.get("terminal_event_refs")
            pending_patch_proposals = self.run_flow_manifest.get("pending_patch_proposals")
        elif run_provenance is not None:
            flow_steps = run_provenance.get("flow_steps")
            artifact_refs = run_provenance.get("artifact_refs")
            event_refs = run_provenance.get("event_refs")
        if artifact_sequence is None and run_lifecycle is not None:
            artifact_sequence = run_lifecycle.get("artifact_sequence")
        if event_sequence is None and run_lifecycle is not None:
            event_sequence = run_lifecycle.get("event_sequence")
        if terminal_artifact_sequence is None and run_lifecycle is not None:
            terminal_artifact_sequence = run_lifecycle.get("terminal_artifact_sequence")
        if terminal_event_sequence is None and run_lifecycle is not None:
            terminal_event_sequence = run_lifecycle.get("terminal_event_sequence")
        if terminal_artifact_refs is None and run_lifecycle is not None:
            terminal_artifact_refs = run_lifecycle.get("terminal_artifact_refs")
        if terminal_event_refs is None and run_lifecycle is not None:
            terminal_event_refs = run_lifecycle.get("terminal_event_refs")
        if pending_patch_proposals is None and run_lifecycle is not None:
            pending_patch_proposals = run_lifecycle.get("pending_patch_proposals")
        if artifact_sequence is None and run_provenance is not None:
            artifact_sequence = run_provenance.get("artifact_sequence")
        if event_sequence is None and run_provenance is not None:
            event_sequence = run_provenance.get("event_sequence")
        if terminal_artifact_sequence is None and run_provenance is not None:
            terminal_artifact_sequence = run_provenance.get("terminal_artifact_sequence")
        if terminal_event_sequence is None and run_provenance is not None:
            terminal_event_sequence = run_provenance.get("terminal_event_sequence")
        if terminal_artifact_refs is None and run_provenance is not None:
            terminal_artifact_refs = run_provenance.get("terminal_artifact_refs")
        if terminal_event_refs is None and run_provenance is not None:
            terminal_event_refs = run_provenance.get("terminal_event_refs")
        if pending_patch_proposals is None and run_provenance is not None:
            pending_patch_proposals = run_provenance.get("pending_patch_proposals")
        if artifact_refs is not None and run_lifecycle is not None:
            merged_artifact_refs = dict(artifact_refs)
            terminal_artifact_ref_values = run_lifecycle.get("terminal_artifact_refs")
            if isinstance(terminal_artifact_ref_values, dict):
                merged_artifact_refs.update(terminal_artifact_ref_values)
            artifact_refs = merged_artifact_refs
        if event_refs is not None and run_lifecycle is not None:
            merged_event_refs = dict(event_refs)
            terminal_event_ref_values = run_lifecycle.get("terminal_event_refs")
            if isinstance(terminal_event_ref_values, dict):
                merged_event_refs.update(terminal_event_ref_values)
            event_refs = merged_event_refs
        run_flow_manifest = self.run_flow_manifest
        if run_flow_manifest is None and snapshot_manifest is not None:
            run_flow_manifest = snapshot_manifest
        if snapshot_manifest is None and self.run_flow_manifest is None and summary is not None and run_provenance is not None:
            synthetic_artifact_refs = (
                {
                    name: tuple(values)
                    for name, values in artifact_refs.items()
                }
                if artifact_refs is not None
                else {}
            )
            synthetic_event_refs = (
                {
                    name: tuple(values)
                    for name, values in event_refs.items()
                }
                if event_refs is not None
                else {}
            )
            synthetic_flow_snapshot = EngineRunFlowSnapshot(
                run=self.run,
                summary=summary,
                run_plan_digest=self.run_plan_digest or run_provenance.get("run_plan_digest"),
                flow_digest=self.flow_digest or run_provenance.get("flow_digest"),
                run_lifecycle_digest=run_lifecycle_digest,
                retrieval_evidence=EngineRunService._clone_jsonable(run_provenance.get("retrieval_evidence")),
                run_provenance=EngineRunService._clone_jsonable(run_provenance),
                artifact_sequence=tuple(artifact_sequence or ()),
                event_sequence=tuple(event_sequence or ()),
                flow_steps=tuple(
                    EngineRunService._clone_jsonable(item) for item in (flow_steps or [])
                ),
                artifact_refs=synthetic_artifact_refs,
                event_refs=synthetic_event_refs,
                pending_patch_proposals=tuple(
                    EngineRunService._clone_jsonable(item) for item in (pending_patch_proposals or [])
                ),
                terminal_artifacts=self.terminal_artifacts,
                terminal_events=self.terminal_events,
            )
            synthetic_snapshot_manifest = synthetic_flow_snapshot.to_manifest()
            snapshot_manifest = synthetic_snapshot_manifest
            run_lifecycle = synthetic_snapshot_manifest["run_lifecycle"]
            run_lifecycle_digest = synthetic_snapshot_manifest["run_lifecycle_digest"]
            run_flow_manifest = _RunFlowBundle(
                run=self.run,
                summary=summary,
                flow_snapshot=synthetic_flow_snapshot,
                run_provenance=run_provenance,
                run_lifecycle=run_lifecycle,
            ).to_manifest()
        if (
            run_flow_manifest is None
            and summary is not None
            and run_lifecycle is not None
        ):
            run_flow_manifest = EngineRunService._synthesize_run_flow_manifest(
                run=self.run,
                summary=summary,
                run_plan_digest=run_plan_digest,
                flow_digest=flow_digest,
                run_lifecycle_digest=run_lifecycle_digest,
                retrieval_evidence=run_provenance.get("retrieval_evidence") if run_provenance is not None else None,
                run_provenance=run_provenance,
                artifact_sequence=artifact_sequence,
                event_sequence=event_sequence,
                flow_steps=flow_steps,
                artifact_refs=artifact_refs,
                event_refs=event_refs,
                pending_patch_proposals=pending_patch_proposals,
                terminal_artifact_sequence=terminal_artifact_sequence,
                terminal_event_sequence=terminal_event_sequence,
                terminal_artifact_refs=terminal_artifact_refs,
                terminal_event_refs=terminal_event_refs,
                terminal_artifacts=self.terminal_artifacts,
                terminal_events=self.terminal_events,
                run_lifecycle=run_lifecycle,
            )
        if run_flow_manifest is not None:
            run_flow_manifest = EngineRunService._clone_jsonable(run_flow_manifest)
        run_flow_manifest_digest = (
            EngineRunService._fingerprint_payload(run_flow_manifest)
            if run_flow_manifest is not None
            else self.run_flow_manifest_digest
        )
        return {
            "run": asdict(self.run),
            "plan_event": asdict(self.plan_event),
            "plan_artifact": asdict(self.plan_artifact),
            "run_plan_digest": run_plan_digest,
            "flow_digest": flow_digest,
            "retrieval_evidence": (
                EngineRunService._clone_jsonable(retrieval_evidence) if retrieval_evidence is not None else None
            ),
            "retrieval_result": asdict(self.retrieval_result) if self.retrieval_result is not None else None,
            "patch_proposal": self.patch_proposal,
            "patch_decision_event": (
                asdict(self.patch_decision_event) if self.patch_decision_event is not None else None
            ),
            "preview_export": asdict(self.preview_export) if self.preview_export is not None else None,
            "final_export": asdict(self.final_export) if self.final_export is not None else None,
            "terminal_artifacts": [asdict(item) for item in self.terminal_artifacts],
            "terminal_events": [asdict(item) for item in self.terminal_events],
            "run_provenance": EngineRunService._clone_jsonable(run_provenance),
            "summary": summary_manifest,
            "run_summary": summary_manifest,
            "flow_snapshot": snapshot_manifest,
            "run_lifecycle_digest": run_lifecycle_digest,
            "run_flow_manifest_digest": run_flow_manifest_digest,
            "flow_steps": flow_steps,
            "artifact_sequence": (
                list(artifact_sequence) if artifact_sequence is not None else None
            ),
            "event_sequence": list(event_sequence) if event_sequence is not None else None,
            "artifact_refs": (
                EngineRunService._clone_jsonable(artifact_refs) if artifact_refs is not None else None
            ),
            "event_refs": EngineRunService._clone_jsonable(event_refs) if event_refs is not None else None,
            "terminal_artifact_sequence": (
                list(terminal_artifact_sequence) if terminal_artifact_sequence is not None else None
            ),
            "terminal_event_sequence": (
                list(terminal_event_sequence) if terminal_event_sequence is not None else None
            ),
            "terminal_artifact_refs": (
                EngineRunService._clone_jsonable(terminal_artifact_refs)
                if terminal_artifact_refs is not None
                else None
            ),
            "terminal_event_refs": (
                EngineRunService._clone_jsonable(terminal_event_refs)
                if terminal_event_refs is not None
                else None
            ),
            "pending_patch_proposals": (
                EngineRunService._clone_jsonable(pending_patch_proposals)
                if pending_patch_proposals is not None
                else None
            ),
            "run_lifecycle": EngineRunService._clone_jsonable(run_lifecycle) if run_lifecycle is not None else None,
            "run_flow_manifest": EngineRunService._clone_jsonable(run_flow_manifest)
            if run_flow_manifest is not None
            else None,
        }


@dataclass(frozen=True)
class EngineRunFlowSnapshot:
    run: EngineRunRecord
    summary: RunSummary
    run_plan_digest: str | None
    flow_digest: str | None
    run_lifecycle_digest: str | None
    retrieval_evidence: dict[str, Any] | None
    run_provenance: dict[str, Any] | None
    artifact_sequence: tuple[str, ...]
    event_sequence: tuple[str, ...]
    flow_steps: tuple[dict[str, Any], ...]
    artifact_refs: dict[str, tuple[str, ...]]
    event_refs: dict[str, tuple[str, ...]]
    pending_patch_proposals: tuple[dict[str, Any], ...]
    terminal_artifacts: tuple[RunArtifact, RunArtifact] | None
    terminal_events: tuple[RunEvent, RunEvent] | None

    def to_manifest(self) -> dict[str, Any]:
        return {
            "run": asdict(self.run),
            "summary": asdict(self.summary),
            "run_summary": asdict(self.summary),
            "run_plan_digest": self.run_plan_digest,
            "flow_digest": self.flow_digest,
            "run_lifecycle_digest": self.run_lifecycle_digest,
            "retrieval_evidence": (
                EngineRunService._clone_jsonable(self.retrieval_evidence) if self.retrieval_evidence is not None else None
            ),
            "run_provenance": (
                EngineRunService._clone_jsonable(self.run_provenance) if self.run_provenance is not None else None
            ),
            "artifact_sequence": list(self.artifact_sequence),
            "event_sequence": list(self.event_sequence),
            "flow_steps": [EngineRunService._clone_jsonable(item) for item in self.flow_steps],
            "artifact_refs": {name: list(values) for name, values in self.artifact_refs.items()},
            "event_refs": {name: list(values) for name, values in self.event_refs.items()},
            "pending_patch_proposals": [
                EngineRunService._clone_jsonable(item) for item in self.pending_patch_proposals
            ],
            "terminal_artifact_sequence": (
                [artifact.kind for artifact in self.terminal_artifacts]
                if self.terminal_artifacts is not None
                else None
            ),
            "terminal_event_sequence": (
                [event.name for event in self.terminal_events] if self.terminal_events is not None else None
            ),
            "terminal_artifact_refs": (
                {
                    "run_provenance": [self.terminal_artifacts[0].artifact_id],
                    "run_completed": [self.terminal_artifacts[1].artifact_id],
                }
                if self.terminal_artifacts is not None
                else None
            ),
            "terminal_event_refs": (
                {
                    "run_provenance_captured": [self.terminal_events[0].event_id],
                    "run_completed": [self.terminal_events[1].event_id],
                }
                if self.terminal_events is not None
                else None
            ),
            "terminal_artifacts": (
                [asdict(item) for item in self.terminal_artifacts] if self.terminal_artifacts is not None else None
            ),
            "terminal_events": (
                [asdict(item) for item in self.terminal_events] if self.terminal_events is not None else None
            ),
            "run_lifecycle": EngineRunService._run_lifecycle_payload(
                self.run,
                terminal_artifacts=self.terminal_artifacts,
                terminal_events=self.terminal_events,
                pending_patch_proposals=self.pending_patch_proposals,
            ),
        }


@dataclass(frozen=True)
class _RunFlowBundle:
    run: EngineRunRecord
    summary: RunSummary
    flow_snapshot: EngineRunFlowSnapshot
    run_provenance: dict[str, Any] | None
    run_lifecycle: dict[str, Any]

    def to_manifest(self) -> dict[str, Any]:
        snapshot_manifest = self.flow_snapshot.to_manifest()
        return {
            "run": asdict(self.run),
            "summary": asdict(self.summary),
            "run_summary": asdict(self.summary),
            "run_plan_digest": self.flow_snapshot.run_plan_digest,
            "flow_digest": self.flow_snapshot.flow_digest,
            "run_lifecycle_digest": self.flow_snapshot.run_lifecycle_digest,
            "retrieval_evidence": snapshot_manifest["retrieval_evidence"],
            "run_provenance": (
                EngineRunService._clone_jsonable(self.run_provenance) if self.run_provenance is not None else None
            ),
            "artifact_sequence": list(self.flow_snapshot.artifact_sequence),
            "event_sequence": list(self.flow_snapshot.event_sequence),
            "flow_steps": [EngineRunService._clone_jsonable(item) for item in self.flow_snapshot.flow_steps],
            "artifact_refs": {name: list(values) for name, values in self.flow_snapshot.artifact_refs.items()},
            "event_refs": {name: list(values) for name, values in self.flow_snapshot.event_refs.items()},
            "pending_patch_proposals": [
                EngineRunService._clone_jsonable(item) for item in self.flow_snapshot.pending_patch_proposals
            ],
            "terminal_artifact_sequence": (
                [artifact.kind for artifact in self.flow_snapshot.terminal_artifacts]
                if self.flow_snapshot.terminal_artifacts is not None
                else None
            ),
            "terminal_event_sequence": (
                [event.name for event in self.flow_snapshot.terminal_events]
                if self.flow_snapshot.terminal_events is not None
                else None
            ),
            "terminal_artifact_refs": snapshot_manifest["terminal_artifact_refs"],
            "terminal_event_refs": snapshot_manifest["terminal_event_refs"],
            "terminal_artifacts": (
                [asdict(item) for item in self.flow_snapshot.terminal_artifacts]
                if self.flow_snapshot.terminal_artifacts is not None
                else None
            ),
            "terminal_events": (
                [asdict(item) for item in self.flow_snapshot.terminal_events]
                if self.flow_snapshot.terminal_events is not None
                else None
            ),
            "run_lifecycle": EngineRunService._clone_jsonable(self.run_lifecycle),
        }


@dataclass(frozen=True)
class _RunTerminalization:
    provenance_artifact: RunArtifact
    provenance_event: RunEvent
    completion_artifact: RunArtifact
    completion_event: RunEvent


class EngineRunService:
    """Engine-owned run lifecycle and artifact orchestration boundary."""

    def __init__(
        self,
        *,
        vault_root,
        audit_log: AuditLog,
        retrieval_service: RetrievalService,
        export_service: ExportService,
        drafting_service: DraftingService,
        now_fn=None,
    ) -> None:
        self._store = VaultStore(vault_root, namespace=_RUN_NAMESPACE, key_filename=_RUNS_KEY_FILE)
        self._audit = audit_log
        self._retrieval = retrieval_service
        self._export = export_service
        self._drafting = drafting_service
        self._now_fn = now_fn or (lambda: datetime.now(UTC))

    def start_run(
        self,
        *,
        operation: str,
        scope: str,
        intent: str,
        request_fingerprint: str,
        run_id: str | None = None,
    ) -> EngineRunRecord:
        normalized_operation = self._require_non_empty_text(operation, field_name="operation")
        normalized_scope = self._require_non_empty_text(scope, field_name="scope")
        normalized_intent = self._require_non_empty_text(intent, field_name="intent")
        normalized_request_fingerprint = self._require_non_empty_text(
            request_fingerprint,
            field_name="request_fingerprint",
        )
        normalized_run_id = self._require_non_empty_text(run_id, field_name="run_id") if run_id is not None else str(
            uuid.uuid4()
        )
        if normalized_run_id in self._load_records():
            raise ValueError(f"run_id already exists: {normalized_run_id}")
        instant = self._timestamp()
        record = EngineRunRecord(
            run_id=normalized_run_id,
            status="running",
            started_at=instant,
            updated_at=instant,
            completed_at=None,
            operation=normalized_operation,
            scope=normalized_scope,
            intent=normalized_intent,
            request_fingerprint=normalized_request_fingerprint,
        )
        self._save_record(record)
        artifact = self._append_artifact(
            record.run_id,
            kind="run_started",
            created_at=instant,
            payload={
                "operation": record.operation,
                "scope": record.scope,
                "intent": record.intent,
                "request_fingerprint": record.request_fingerprint,
                "status": record.status,
                "started_at": instant,
            },
        )
        self._record_event(
            record.run_id,
            name="run_started",
            created_at=instant,
            payload={
                "operation": record.operation,
                "scope": record.scope,
                "intent": record.intent,
                "request_fingerprint": record.request_fingerprint,
                "status": record.status,
                "started_at": instant,
            },
            metadata={
                "artifact_id": artifact.artifact_id,
                "operation": record.operation,
                "scope": record.scope,
                "intent": record.intent,
                "request_fingerprint": record.request_fingerprint,
                "status": record.status,
            },
        )
        return self.get_run(record.run_id)

    def plan_run(
        self,
        run_id: str,
        *,
        retrieval_query_text: str,
        retrieval_constraints: dict[str, object] | None = None,
        patch_requested: bool = False,
        export_requested: bool = False,
        final_status: RunStatus = "completed",
    ) -> RunEvent:
        record = self._require_running(run_id)
        self._validate_terminal_status(final_status)
        normalized_query_text = self._require_non_empty_text(retrieval_query_text, field_name="query_text")
        planned_at = self._timestamp()
        payload = {
            "operation": record.operation,
            "scope": record.scope,
            "intent": record.intent,
            "request_fingerprint": record.request_fingerprint,
            "retrieval_query_hash": self._fingerprint_text(normalized_query_text),
            "retrieval_constraints": self._normalize_plan_constraints(retrieval_constraints),
            "patch_requested": patch_requested,
            "export_requested": export_requested,
            "planned_terminal_status": final_status,
        }
        payload["plan_digest"] = self._fingerprint_payload(payload)
        artifact = self._append_artifact(
            run_id,
            kind="run_plan",
            created_at=planned_at,
            payload=payload,
        )
        return self._record_event(
            run_id,
            name="run_planned",
            created_at=planned_at,
            payload={"artifact_id": artifact.artifact_id, **payload},
            metadata={"artifact_id": artifact.artifact_id, **payload},
        )

    def retrieve(
        self,
        run_id: str,
        *,
        query_text: str,
        scope: str,
        intent: str,
        constraints: dict[str, object] | None = None,
        confidentiality_profile: str = "confidential",
    ) -> RetrievalResult:
        record = self._require_running(run_id)
        normalized_query_text = self._require_non_empty_text(query_text, field_name="query_text")
        normalized_scope = self._require_non_empty_text(scope, field_name="scope")
        normalized_intent = self._require_non_empty_text(intent, field_name="intent")
        retrieval_intent = _RETRIEVAL_INTENT_ALIASES.get(normalized_intent, normalized_intent)
        self._require_matching_scope(record, scope=normalized_scope, operation="retrieve")
        normalized_confidentiality_profile = self._validate_retrieval_confidentiality_profile(
            confidentiality_profile
        )
        normalized_constraints = self._normalize_retrieval_constraints(constraints)
        result = retrieve_auto(
            self._retrieval,
            query_text=normalized_query_text,
            scope=normalized_scope,
            intent=retrieval_intent,
            constraints=normalized_constraints,
            confidentiality_profile=normalized_confidentiality_profile,
        )
        query_hash = self._fingerprint_text(normalized_query_text)
        strategies = tuple(result.diagnostics.get("strategies_used", []))
        retrieved_at = self._timestamp()
        artifact = self._append_artifact(
            run_id,
            kind="retrieval_result",
            created_at=retrieved_at,
            payload={
                "audit_ref": result.audit_ref,
                "query_scope": result.query.scope,
                "query_intent": result.query.intent,
                "retrieval_query_hash": query_hash,
                "retrieval_constraints": normalized_constraints,
                "hit_count": len(result.hits),
                "strategies_used": list(strategies),
            },
        )
        self._record_event(
            run_id,
            name="retrieval_attached",
            created_at=retrieved_at,
            payload={
                "artifact_id": artifact.artifact_id,
                "hit_count": len(result.hits),
                "retrieval_query_hash": query_hash,
                "retrieval_constraints": normalized_constraints,
            },
            metadata={
                "artifact_id": artifact.artifact_id,
                "audit_ref": result.audit_ref,
                "query_scope": result.query.scope,
                "query_intent": result.query.intent,
                "retrieval_query_hash": query_hash,
                "retrieval_constraints": normalized_constraints,
                "hit_count": len(result.hits),
                "strategies_used": list(strategies),
            },
        )
        return result

    def propose_patch(
        self,
        run_id: str,
        *,
        original: str,
        proposed: str,
        target_path: str,
    ) -> str:
        record = self._require_running(run_id)
        normalized_target_path = self._require_non_empty_text(target_path, field_name="target_path")
        self._require_no_pending_patch_proposal_for_target_path(record, target_path=normalized_target_path)
        patch = self._drafting.propose_diff(original, proposed)
        patch_hash = self._fingerprint_text(patch)
        proposed_at = self._timestamp()
        artifact = self._append_artifact(
            run_id,
            kind="patch_proposal",
            created_at=proposed_at,
            payload={
                "target_path": normalized_target_path,
                "is_empty": patch == "",
                "line_count": len(patch.splitlines()),
                "patch_hash": patch_hash,
            },
        )
        self._record_event(
            run_id,
            name="patch_proposed",
            created_at=proposed_at,
            payload={
                "artifact_id": artifact.artifact_id,
                "target_path": normalized_target_path,
                "is_empty": patch == "",
                "line_count": len(patch.splitlines()),
                "patch_hash": patch_hash,
            },
            metadata={
                "artifact_id": artifact.artifact_id,
                "target_path": normalized_target_path,
                "is_empty": patch == "",
                "line_count": len(patch.splitlines()),
                "patch_hash": patch_hash,
            },
        )
        return patch

    def record_patch_decision(
        self,
        run_id: str,
        *,
        decision: PatchDecision,
        target_path: str,
        reason: str | None = None,
    ) -> RunEvent:
        self._validate_patch_decision(decision)
        record = self._require_running(run_id)
        normalized_target_path = self._require_non_empty_text(target_path, field_name="target_path")
        proposal = self._require_patch_proposal(record, target_path=normalized_target_path)
        self._ensure_patch_decision_not_recorded(record, proposal_artifact_id=proposal.artifact_id)
        proposal_summary = self._patch_proposal_summary(proposal)
        decision_reason = reason.strip() if isinstance(reason, str) and reason.strip() else None
        decision_at = self._timestamp()
        event_name = "patch_applied" if decision == "accepted" else "patch_rejected"
        decision_event_id = f"{run_id}:{len(record.events) + 1:04d}:{event_name}"
        decision_artifact = self._append_artifact(
            run_id,
            kind="patch_decision",
            created_at=decision_at,
            payload={
                "proposal_artifact_id": proposal.artifact_id,
                "target_path": normalized_target_path,
                "decision": decision,
                "reason": decision_reason,
                "decision_event_id": decision_event_id,
                "proposal_patch_hash": proposal_summary["patch_hash"],
                "proposal_line_count": proposal_summary["line_count"],
            },
            audit_metadata={
                "proposal_artifact_id": proposal.artifact_id,
                "target_path": normalized_target_path,
                "decision": decision,
                "decision_event_id": decision_event_id,
                "proposal_patch_hash": proposal_summary["patch_hash"],
                "proposal_line_count": proposal_summary["line_count"],
            },
        )
        return self._record_event(
            run_id,
            name=event_name,
            created_at=decision_at,
            payload={
                "proposal_artifact_id": proposal.artifact_id,
                "decision_artifact_id": decision_artifact.artifact_id,
                "decision_event_id": decision_event_id,
                "target_path": normalized_target_path,
                "decision": decision,
                "reason": decision_reason,
                "proposal_patch_hash": proposal_summary["patch_hash"],
                "proposal_line_count": proposal_summary["line_count"],
            },
            metadata={
                "proposal_artifact_id": proposal.artifact_id,
                "decision_artifact_id": decision_artifact.artifact_id,
                "target_path": normalized_target_path,
                "decision": decision,
                "decision_event_id": decision_event_id,
                "reason": decision_reason,
                "proposal_patch_hash": proposal_summary["patch_hash"],
                "proposal_line_count": proposal_summary["line_count"],
            },
        )

    def preview_export(self, run_id: str, *, options: ExportOptions) -> PreviewArtifactRef:
        record = self._require_running(run_id)
        self._require_run_plan(record, operation="export preview")
        self._require_no_pending_patch_proposals(record, operation="export preview")
        retrieval_evidence = self._require_retrieval_evidence(record, operation="export preview")
        run_plan_digest = self._run_plan_digest_payload(record)
        artifact = self._export.preview(options)
        preview_at = self._timestamp()
        stored = self._append_artifact(
            run_id,
            kind="export_preview",
            created_at=preview_at,
            payload={
                "run_id": run_id,
                "run_plan_digest": run_plan_digest,
                "artifact_id": artifact.artifact_id,
                "output_format": artifact.output_format,
                "size_bytes": artifact.size_bytes,
                "expires_at": artifact.expires_at,
                "storage_ref": artifact.storage_ref,
                "options_fingerprint": artifact.options_fingerprint,
                "retrieval_evidence": retrieval_evidence,
            },
        )
        self._record_event(
            run_id,
            name="export_preview_attached",
            created_at=preview_at,
            payload={"artifact_id": stored.artifact_id, "output_format": artifact.output_format},
            metadata={
                "run_id": run_id,
                "run_plan_digest": run_plan_digest,
                "artifact_id": stored.artifact_id,
                "output_format": artifact.output_format,
                "size_bytes": artifact.size_bytes,
                "expires_at": artifact.expires_at,
                "options_fingerprint": artifact.options_fingerprint,
            },
        )
        return artifact

    def final_export(
        self,
        run_id: str,
        *,
        options: ExportOptions,
        destination_path: Path | str | PathLike[str],
        export_approved: bool = False,
    ) -> ExportArtifactRef:
        record = self._require_running(run_id)
        self._require_run_plan(record, operation="final export")
        self._require_no_pending_patch_proposals(record, operation="final export")
        retrieval_evidence = self._require_retrieval_evidence(record, operation="final export")
        run_plan_digest = self._run_plan_digest_payload(record)
        normalized_destination_path = self._normalize_destination_path(
            destination_path,
            field_name="destination_path",
        )
        artifact = self._export.final(
            options,
            destination_path=normalized_destination_path,
            export_approved=export_approved,
        )
        export_at = self._timestamp()
        stored = self._append_artifact(
            run_id,
            kind="export_final",
            created_at=export_at,
            payload={
                "run_id": run_id,
                "run_plan_digest": run_plan_digest,
                "artifact_id": artifact.artifact_id,
                "output_format": artifact.output_format,
                "size_bytes": artifact.size_bytes,
                "content_hash": artifact.content_hash,
                "destination_path": str(normalized_destination_path),
                "export_approved": export_approved,
                "retrieval_evidence": retrieval_evidence,
            },
        )
        self._record_event(
            run_id,
            name="export_final_attached",
            created_at=export_at,
            payload={"artifact_id": stored.artifact_id, "output_format": artifact.output_format},
            metadata={
                "run_id": run_id,
                "run_plan_digest": run_plan_digest,
                "artifact_id": stored.artifact_id,
                "output_format": artifact.output_format,
                "size_bytes": artifact.size_bytes,
                "content_hash": artifact.content_hash,
                "destination_path": str(normalized_destination_path),
                "export_approved": export_approved,
            },
        )
        return artifact

    def run_flow(
        self,
        *,
        operation: str,
        scope: str,
        intent: str,
        request_fingerprint: str,
        run_id: str | None = None,
        retrieval_query_text: str,
        retrieval_constraints: dict[str, object] | None = None,
        retrieval_confidentiality_profile: str = "confidential",
        patch_original: str | None = None,
        patch_proposed: str | None = None,
        patch_target_path: str | None = None,
        patch_decision: PatchDecision | None = None,
        patch_reason: str | None = None,
        export_options: ExportOptions | None = None,
        export_destination_path: Path | str | PathLike[str] | None = None,
        export_approved: bool = False,
        final_status: RunStatus = "completed",
    ) -> EngineRunFlowResult:
        normalized_retrieval_constraints = self._normalize_retrieval_constraints(retrieval_constraints)
        normalized_retrieval_confidentiality_profile = self._validate_retrieval_confidentiality_profile(
            retrieval_confidentiality_profile
        )
        self._validate_run_flow_request(
            operation=operation,
            scope=scope,
            intent=intent,
            request_fingerprint=request_fingerprint,
            run_id=run_id,
            retrieval_query_text=retrieval_query_text,
            retrieval_confidentiality_profile=normalized_retrieval_confidentiality_profile,
            final_status=final_status,
            retrieval_constraints=normalized_retrieval_constraints,
            patch_original=patch_original,
            patch_proposed=patch_proposed,
            patch_target_path=patch_target_path,
            patch_decision=patch_decision,
            patch_reason=patch_reason,
            export_options=export_options,
            export_destination_path=export_destination_path,
        )
        run = self.start_run(
            operation=operation,
            scope=scope,
            intent=intent,
            request_fingerprint=request_fingerprint,
            run_id=run_id,
        )
        flow_phase = "plan_run"
        try:
            plan_event = self.plan_run(
                run.run_id,
                retrieval_query_text=retrieval_query_text,
                retrieval_constraints=normalized_retrieval_constraints,
                patch_requested=any(
                    value is not None
                    for value in (patch_original, patch_proposed, patch_target_path, patch_decision, patch_reason)
                ),
                export_requested=export_options is not None,
                final_status=final_status,
            )
            flow_phase = "retrieve"
            retrieval_result = self.retrieve(
                run.run_id,
                query_text=retrieval_query_text,
                scope=scope,
                intent=intent,
                constraints=normalized_retrieval_constraints,
                confidentiality_profile=normalized_retrieval_confidentiality_profile,
            )
            patch_text: str | None = None
            patch_decision_event: RunEvent | None = None
            if any(
                value is not None
                for value in (patch_original, patch_proposed, patch_target_path, patch_decision, patch_reason)
            ):
                flow_phase = "patch"
                (
                    patch_original_value,
                    patch_proposed_value,
                    patch_target_path_value,
                    patch_decision_value,
                ) = self._require_patch_flow_inputs(
                    patch_original=patch_original,
                    patch_proposed=patch_proposed,
                    patch_target_path=patch_target_path,
                    patch_decision=patch_decision,
                )
                patch_text = self.propose_patch(
                    run.run_id,
                    original=patch_original_value,
                    proposed=patch_proposed_value,
                    target_path=patch_target_path_value,
                )
                patch_decision_event = self.record_patch_decision(
                    run.run_id,
                    decision=patch_decision_value,
                    target_path=patch_target_path_value,
                    reason=patch_reason,
                )
            preview_export: PreviewArtifactRef | None = None
            final_export: ExportArtifactRef | None = None
            if export_options is not None:
                if export_destination_path is None:
                    raise ValueError("export flow requires destination_path when export_options are provided")
                if final_status != "completed":
                    raise ValueError("export flow requires completed terminal status")
                normalized_export_destination_path = self._normalize_destination_path(
                    export_destination_path,
                    field_name="export_destination_path",
                )
                flow_phase = "export_preview"
                preview_export = self.preview_export(run.run_id, options=export_options)
                flow_phase = "export_final"
                final_export = self.final_export(
                    run.run_id,
                    options=export_options,
                    destination_path=normalized_export_destination_path,
                    export_approved=export_approved,
            )
            flow_phase = "complete_run"
            completed_run = self.complete_run(run.run_id, status=final_status)
            run_bundle = self._build_run_bundle(completed_run)
            flow_snapshot = run_bundle.flow_snapshot
            run_flow_manifest = run_bundle.to_manifest()
            run_flow_manifest_digest = self._fingerprint_payload(run_flow_manifest)
            terminal_artifacts = flow_snapshot.terminal_artifacts
            terminal_events = flow_snapshot.terminal_events
            run_provenance = run_bundle.run_provenance
            run_lifecycle = run_bundle.run_lifecycle
            self._audit.record(
                name="engine_run_flow_completed_summary",
                metadata={
                    "run_id": completed_run.run_id,
                    "status": completed_run.status,
                    "operation": completed_run.operation,
                    "scope": completed_run.scope,
                    "intent": completed_run.intent,
                    "request_fingerprint": completed_run.request_fingerprint,
                    "run_plan_digest": flow_snapshot.run_plan_digest,
                    "flow_digest": flow_snapshot.flow_digest,
                    "run_lifecycle_digest": flow_snapshot.run_lifecycle_digest,
                    "artifact_count": flow_snapshot.summary.artifact_count,
                    "event_count": flow_snapshot.summary.event_count,
                    "artifact_sequence": list(flow_snapshot.artifact_sequence),
                    "event_sequence": list(flow_snapshot.event_sequence),
                    "run_lifecycle": run_lifecycle,
                    "terminal_artifact_refs": run_lifecycle["terminal_artifact_refs"],
                    "terminal_event_refs": run_lifecycle["terminal_event_refs"],
                    "retrieval_evidence": flow_snapshot.retrieval_evidence,
                    "run_flow_manifest": run_flow_manifest,
                    "run_flow_manifest_digest": run_flow_manifest_digest,
                    "patch_decisions": list(run_provenance.get("patch_decisions", []))
                    if run_provenance is not None
                    else [],
                    "export_preview_artifacts": list(
                        run_provenance.get("export_preview_artifacts", [])
                    )
                    if run_provenance is not None
                    else [],
                    "export_final_artifacts": list(run_provenance.get("export_final_artifacts", []))
                    if run_provenance is not None
                    else [],
                },
            )
            return EngineRunFlowResult(
                run=completed_run,
                run_summary=flow_snapshot.summary,
                run_plan_digest=flow_snapshot.run_plan_digest,
                flow_digest=flow_snapshot.flow_digest,
                retrieval_result=retrieval_result,
                patch_proposal=patch_text,
                patch_decision_event=patch_decision_event,
                preview_export=preview_export,
                final_export=final_export,
                terminal_artifacts=terminal_artifacts,
                terminal_events=terminal_events,
                run_provenance=EngineRunService._clone_jsonable(run_provenance)
                if run_provenance is not None
                else None,
                run_lifecycle=EngineRunService._clone_jsonable(run_lifecycle),
                run_lifecycle_digest=flow_snapshot.run_lifecycle_digest,
                plan_event=plan_event,
                plan_artifact=self._require_artifact_from_record(completed_run, kind="run_plan"),
                flow_snapshot=flow_snapshot,
                run_flow_manifest=EngineRunService._clone_jsonable(run_flow_manifest),
                run_flow_manifest_digest=run_flow_manifest_digest,
            )
        except Exception as exc:
            try:
                self._record_run_failure(
                    run.run_id,
                    error=exc,
                    final_status=final_status,
                    failed_phase=flow_phase,
                )
            except Exception as failure_error:
                self._audit.record(
                    name="engine_run_flow_failure_recording_failed",
                    metadata={
                        "run_id": run.run_id,
                        "error_type": type(failure_error).__name__,
                        "error_message": str(failure_error),
                    },
                )
            try:
                self.complete_run(run.run_id, status="failed")
            except Exception as finalize_error:
                self._audit.record(
                    name="engine_run_flow_finalize_failed",
                    metadata={
                        "run_id": run.run_id,
                        "error_type": type(finalize_error).__name__,
                        "error_message": str(finalize_error),
                    },
                )
            else:
                self._record_run_flow_failed_summary(
                    run.run_id,
                    error=exc,
                    failed_phase=flow_phase,
                    planned_terminal_status=final_status,
                )
            raise

    def _validate_run_flow_request(
        self,
        *,
        operation: str,
        scope: str,
        intent: str,
        request_fingerprint: str,
        run_id: str | None,
        retrieval_query_text: str,
        retrieval_confidentiality_profile: str,
        retrieval_constraints: dict[str, object] | None,
        patch_original: str | None,
        patch_proposed: str | None,
        patch_target_path: str | None,
        patch_decision: PatchDecision | None,
        patch_reason: str | None,
        export_options: ExportOptions | None,
        export_destination_path: Path | str | PathLike[str] | None,
        final_status: RunStatus,
    ) -> None:
        self._require_non_empty_text(operation, field_name="operation")
        self._require_non_empty_text(scope, field_name="scope")
        self._require_non_empty_text(intent, field_name="intent")
        self._require_non_empty_text(request_fingerprint, field_name="request_fingerprint")
        self._require_non_empty_text(retrieval_query_text, field_name="query_text")
        self._validate_retrieval_confidentiality_profile(retrieval_confidentiality_profile)
        self._normalize_retrieval_constraints(retrieval_constraints)
        self._validate_terminal_status(final_status)
        if run_id is not None:
            self._require_non_empty_text(run_id, field_name="run_id")
        patch_inputs_requested = any(
            value is not None
            for value in (patch_original, patch_proposed, patch_target_path, patch_decision, patch_reason)
        )
        if patch_inputs_requested:
            self._require_patch_flow_inputs(
                patch_original=patch_original,
                patch_proposed=patch_proposed,
                patch_target_path=patch_target_path,
                patch_decision=patch_decision,
            )
        if export_options is not None:
            if export_destination_path is None:
                raise ValueError("export flow requires destination_path when export_options are provided")
            self._normalize_destination_path(export_destination_path, field_name="export_destination_path")
            if final_status != "completed":
                raise ValueError("export flow requires completed terminal status")

    @staticmethod
    def _normalize_retrieval_constraints(
        constraints: dict[str, object] | None,
    ) -> dict[str, object]:
        if constraints is None:
            return {
                "max_results": 10,
                "section_hint": None,
                "prefer_exact_matches": False,
            }
        if not isinstance(constraints, dict):
            raise TypeError("retrieval_constraints must be a dict when provided")
        max_results = constraints.get("max_results")
        if max_results is None:
            normalized_max_results = 10
        elif isinstance(max_results, bool):
            raise TypeError("max_results must be an integer")
        elif isinstance(max_results, int):
            normalized_max_results = max_results
        elif isinstance(max_results, str) and max_results.strip():
            try:
                normalized_max_results = int(max_results.strip())
            except ValueError as exc:
                raise TypeError("max_results must be an integer") from exc
        else:
            raise TypeError("max_results must be an integer")
        if normalized_max_results < 1:
            raise ValueError("max_results must be >= 1")

        section_hint = constraints.get("section_hint")
        if section_hint is None:
            normalized_section_hint = None
        elif isinstance(section_hint, str):
            normalized_section_hint = section_hint.strip() or None
        else:
            raise TypeError("section_hint must be a string")

        prefer_exact_matches = constraints.get("prefer_exact_matches")
        if prefer_exact_matches is None:
            normalized_prefer_exact_matches = False
        elif isinstance(prefer_exact_matches, bool):
            normalized_prefer_exact_matches = prefer_exact_matches
        elif isinstance(prefer_exact_matches, str):
            lowered = prefer_exact_matches.strip().lower()
            if lowered in {"1", "true", "yes", "on"}:
                normalized_prefer_exact_matches = True
            elif lowered in {"0", "false", "no", "off", ""}:
                normalized_prefer_exact_matches = False
            else:
                raise TypeError("prefer_exact_matches must be a boolean")
        else:
            raise TypeError("prefer_exact_matches must be a boolean")

        return {
            "max_results": normalized_max_results,
            "section_hint": normalized_section_hint,
            "prefer_exact_matches": normalized_prefer_exact_matches,
        }

    def complete_run(self, run_id: str, *, status: RunStatus = "completed") -> EngineRunRecord:
        self._validate_terminal_status(status)
        try:
            record = self.get_run(run_id)
        except ValueError:
            if status != "failed" or not self._repair_partial_failed_run_state(run_id):
                raise
            record = self.get_run(run_id)
        if record.status != "running":
            raise ValueError(f"run {run_id} is already terminal: {record.status}")
        if status == "completed":
            self._require_run_plan(record, operation="run completion")
            self._require_retrieval_evidence(record, operation="run completion")
        if status == "completed":
            self._require_no_pending_patch_proposals(record, operation="run completion")
        completion_at = self._timestamp()
        terminalization = self._build_terminalization(record, captured_at=completion_at, terminal_status=status)
        updated = EngineRunRecord(
            run_id=record.run_id,
            status=status,
            started_at=record.started_at,
            updated_at=completion_at,
            completed_at=completion_at,
            operation=record.operation,
            scope=record.scope,
            intent=record.intent,
            request_fingerprint=record.request_fingerprint,
            artifacts=[*record.artifacts, terminalization.provenance_artifact, terminalization.completion_artifact],
            events=[*record.events, terminalization.provenance_event, terminalization.completion_event],
        )
        self._save_record(updated)
        run_bundle = self._build_run_bundle(updated)
        run_flow_manifest = run_bundle.to_manifest()
        run_flow_manifest_digest = self._fingerprint_payload(run_flow_manifest)
        self._audit.record(
            name="engine_run_artifact_attached",
            metadata={
                "run_id": run_id,
                "kind": "run_provenance",
                "artifact_id": terminalization.provenance_artifact.artifact_id,
            },
        )
        self._audit.record(
            name="engine_run_artifact_attached",
            metadata={
                "run_id": run_id,
                "kind": "run_completed",
                "artifact_id": terminalization.completion_artifact.artifact_id,
            },
        )
        self._audit.record(
            name="engine_run_provenance_captured_summary",
            metadata={
                "run_id": run_id,
                "artifact_id": terminalization.provenance_artifact.artifact_id,
                "status": status,
                "planned_terminal_status": terminalization.provenance_artifact.payload.get("planned_terminal_status"),
                "actual_terminal_status": terminalization.provenance_artifact.payload.get("actual_terminal_status"),
                "artifact_count": len(updated.artifacts),
                "event_count": len(updated.events),
                "run_plan_digest": terminalization.provenance_artifact.payload.get("run_plan_digest"),
                "flow_digest": terminalization.provenance_artifact.payload.get("flow_digest"),
                "run_flow_manifest": run_flow_manifest,
                "run_flow_manifest_digest": run_flow_manifest_digest,
                "terminal_artifact_refs": terminalization.provenance_artifact.payload.get("terminal_artifact_refs"),
                "terminal_event_refs": terminalization.provenance_artifact.payload.get("terminal_event_refs"),
            },
        )
        self._audit.record(
            name="engine_run_completed_summary",
            metadata={
                "run_id": run_id,
                "artifact_id": terminalization.completion_artifact.artifact_id,
                "status": status,
                "planned_terminal_status": terminalization.provenance_artifact.payload.get("planned_terminal_status"),
                "actual_terminal_status": terminalization.provenance_artifact.payload.get("actual_terminal_status"),
                "artifact_count": len(updated.artifacts),
                "event_count": len(updated.events),
                "run_plan_digest": terminalization.provenance_artifact.payload.get("run_plan_digest"),
                "flow_digest": terminalization.provenance_artifact.payload.get("flow_digest"),
                "run_flow_manifest": run_flow_manifest,
                "run_flow_manifest_digest": run_flow_manifest_digest,
                "terminal_artifact_refs": terminalization.provenance_artifact.payload.get("terminal_artifact_refs"),
                "terminal_event_refs": terminalization.provenance_artifact.payload.get("terminal_event_refs"),
            },
        )
        return updated

    def _repair_partial_failed_run_state(self, run_id: str) -> bool:
        record = self.get_run(run_id, validate=False)
        if record.status != "running":
            return False
        if len(record.artifacts) != len(record.events) + 1:
            return False
        if not record.artifacts:
            return False
        failure_artifact = record.artifacts[-1]
        if failure_artifact.kind != "run_failure":
            return False
        if record.events and record.events[-1].name == "run_failed":
            return False
        failure_payload = failure_artifact.payload
        failure_event_at = failure_artifact.created_at
        self._record_event(
            run_id,
            name="run_failed",
            created_at=failure_event_at,
            payload={
                "artifact_id": failure_artifact.artifact_id,
                "error_type": failure_payload.get("error_type"),
                "error_message": failure_payload.get("error_message"),
                "failed_phase": failure_payload.get("failed_phase"),
                "planned_terminal_status": failure_payload.get("planned_terminal_status"),
                "actual_terminal_status": failure_payload.get("actual_terminal_status"),
                "operation": record.operation,
                "scope": record.scope,
                "intent": record.intent,
                "request_fingerprint": record.request_fingerprint,
                "run_plan_digest": failure_payload.get("run_plan_digest"),
            },
            metadata={
                "artifact_id": failure_artifact.artifact_id,
                "error_type": failure_payload.get("error_type"),
                "error_message": failure_payload.get("error_message"),
                "failed_phase": failure_payload.get("failed_phase"),
                "planned_terminal_status": failure_payload.get("planned_terminal_status"),
                "actual_terminal_status": failure_payload.get("actual_terminal_status"),
                "operation": record.operation,
                "scope": record.scope,
                "intent": record.intent,
                "request_fingerprint": record.request_fingerprint,
                "run_plan_digest": failure_payload.get("run_plan_digest"),
            },
        )
        return True

    def summarize_run(self, run_id: str) -> RunSummary:
        record = self.get_run(run_id)
        return self._build_run_summary(record)

    def get_run_provenance(self, run_id: str) -> dict[str, Any]:
        record = self.get_run(run_id)
        provenance = self._run_provenance_payload(record)
        if provenance is None:
            raise ValueError(f"run {run_id} does not have captured provenance")
        return provenance

    def describe_run_flow(self, run_id: str) -> EngineRunFlowSnapshot:
        record = self.get_run(run_id)
        return self._build_flow_snapshot(record)

    def describe_run_bundle(self, run_id: str) -> _RunFlowBundle:
        record = self.get_run(run_id)
        return self._build_run_bundle(record)

    def describe_run_manifest(self, run_id: str) -> dict[str, Any]:
        return self.describe_run_bundle(run_id).to_manifest()

    def describe_run_flow_manifest(self, run_id: str) -> dict[str, Any]:
        return self.describe_run_flow(run_id).to_manifest()

    def describe_run_bundle_manifest(self, run_id: str) -> dict[str, Any]:
        return self.describe_run_bundle(run_id).to_manifest()

    @classmethod
    def _build_flow_snapshot(cls, record: EngineRunRecord) -> EngineRunFlowSnapshot:
        summary = cls._build_run_summary(record)
        run_provenance = cls._run_provenance_payload(record)
        terminal_artifacts: tuple[RunArtifact, RunArtifact] | None = None
        terminal_events: tuple[RunEvent, RunEvent] | None = None
        if record.status in _TERMINAL_RUN_STATUSES:
            terminal_artifacts = (
                cls._require_artifact_from_record(record, kind="run_provenance"),
                cls._require_artifact_from_record(record, kind="run_completed"),
            )
            terminal_events = (
                cls._require_event_from_record(record, name="run_provenance_captured"),
                cls._require_event_from_record(record, name="run_completed"),
            )
        run_lifecycle = cls._run_lifecycle_payload(
            record,
            terminal_artifacts=terminal_artifacts,
            terminal_events=terminal_events,
        )
        return EngineRunFlowSnapshot(
            run=record,
            summary=summary,
            run_plan_digest=cls._run_plan_digest_payload(record),
            flow_digest=run_provenance.get("flow_digest") if run_provenance is not None else None,
            run_lifecycle_digest=cls._fingerprint_payload(run_lifecycle),
            retrieval_evidence=cls._retrieval_evidence_payload(record),
            run_provenance=run_provenance,
            artifact_sequence=tuple(artifact.kind for artifact in record.artifacts),
            event_sequence=tuple(event.name for event in record.events),
            flow_steps=cls._flow_step_summaries(record),
            artifact_refs={
                "run_started": cls._artifact_ids(record, kind="run_started"),
                "run_plan": cls._artifact_ids(record, kind="run_plan"),
                "retrieval_result": cls._artifact_ids(record, kind="retrieval_result"),
                "patch_proposal": cls._artifact_ids(record, kind="patch_proposal"),
                "patch_decision": cls._artifact_ids(record, kind="patch_decision"),
                "run_failure": cls._artifact_ids(record, kind="run_failure"),
                "export_preview": cls._artifact_ids(record, kind="export_preview"),
                "export_final": cls._artifact_ids(record, kind="export_final"),
                "run_provenance": cls._artifact_ids(record, kind="run_provenance"),
                "run_completed": cls._artifact_ids(record, kind="run_completed"),
            },
            event_refs={
                "run_started": cls._event_ids(record, name="run_started"),
                "run_planned": cls._event_ids(record, name="run_planned"),
                "retrieval_attached": cls._event_ids(record, name="retrieval_attached"),
                "patch_proposed": cls._event_ids(record, name="patch_proposed"),
                "patch_applied": cls._event_ids(record, name="patch_applied"),
                "patch_rejected": cls._event_ids(record, name="patch_rejected"),
                "run_failed": cls._event_ids(record, name="run_failed"),
                "export_preview_attached": cls._event_ids(record, name="export_preview_attached"),
                "export_final_attached": cls._event_ids(record, name="export_final_attached"),
                "run_provenance_captured": cls._event_ids(record, name="run_provenance_captured"),
                "run_completed": cls._event_ids(record, name="run_completed"),
            },
            pending_patch_proposals=tuple(
                {
                    "artifact_id": artifact.artifact_id,
                    "target_path": artifact.payload.get("target_path"),
                }
                for artifact in cls._pending_patch_proposals(record)
            ),
            terminal_artifacts=terminal_artifacts,
            terminal_events=terminal_events,
        )

    @classmethod
    def _build_run_bundle(cls, record: EngineRunRecord) -> _RunFlowBundle:
        flow_snapshot = cls._build_flow_snapshot(record)
        run_lifecycle = cls._run_lifecycle_payload(
            record,
            terminal_artifacts=flow_snapshot.terminal_artifacts,
            terminal_events=flow_snapshot.terminal_events,
        )
        return _RunFlowBundle(
            run=record,
            summary=flow_snapshot.summary,
            flow_snapshot=flow_snapshot,
            run_provenance=flow_snapshot.run_provenance,
            run_lifecycle=run_lifecycle,
        )

    @staticmethod
    def _build_run_summary(record: EngineRunRecord) -> RunSummary:
        run_plan_digest = EngineRunService._run_plan_digest_payload(record)
        provenance = EngineRunService._run_provenance_payload(record)
        return RunSummary(
            run_id=record.run_id,
            status=record.status,
            started_at=record.started_at,
            updated_at=record.updated_at,
            completed_at=record.completed_at,
            operation=record.operation,
            scope=record.scope,
            intent=record.intent,
            request_fingerprint=record.request_fingerprint,
            artifact_count=len(record.artifacts),
            event_count=len(record.events),
            run_plan_digest=run_plan_digest,
            flow_digest=provenance.get("flow_digest") if provenance is not None else None,
            latest_artifact=record.artifacts[-1] if record.artifacts else None,
            latest_event=record.events[-1] if record.events else None,
            latest_failure_artifact=EngineRunService._latest_artifact(record, kind="run_failure"),
        )

    @staticmethod
    def _coerce_run_summary(payload: dict[str, Any]) -> RunSummary:
        summary_fields = RunSummary.__dataclass_fields__
        normalized_payload = {key: payload[key] for key in summary_fields if key in payload}
        latest_artifact = normalized_payload.get("latest_artifact")
        if isinstance(latest_artifact, dict):
            normalized_payload["latest_artifact"] = EngineRunService._coerce_run_artifact(latest_artifact)
        latest_event = normalized_payload.get("latest_event")
        if isinstance(latest_event, dict):
            normalized_payload["latest_event"] = EngineRunService._coerce_run_event(latest_event)
        latest_failure_artifact = normalized_payload.get("latest_failure_artifact")
        if isinstance(latest_failure_artifact, dict):
            normalized_payload["latest_failure_artifact"] = EngineRunService._coerce_run_artifact(
                latest_failure_artifact
            )
        return RunSummary(**normalized_payload)

    @staticmethod
    def _coerce_run_artifact(payload: dict[str, Any]) -> RunArtifact:
        return RunArtifact(
            artifact_id=str(payload["artifact_id"]),
            kind=str(payload["kind"]),
            created_at=str(payload["created_at"]),
            payload=dict(payload.get("payload") or {}),
        )

    @staticmethod
    def _coerce_run_event(payload: dict[str, Any]) -> RunEvent:
        return RunEvent(
            event_id=str(payload["event_id"]),
            name=str(payload["name"]),
            created_at=str(payload["created_at"]),
            payload=dict(payload.get("payload") or {}),
        )

    @staticmethod
    def _run_lifecycle_payload(
        record: EngineRunRecord,
        *,
        terminal_artifacts: tuple[RunArtifact, RunArtifact] | None = None,
        terminal_events: tuple[RunEvent, RunEvent] | None = None,
        pending_patch_proposals: tuple[dict[str, Any], ...] | None = None,
    ) -> dict[str, Any]:
        return {
            "artifact_count": len(record.artifacts),
            "event_count": len(record.events),
            "artifact_sequence": [artifact.kind for artifact in record.artifacts],
            "event_sequence": [event.name for event in record.events],
            "latest_artifact_id": record.artifacts[-1].artifact_id if record.artifacts else None,
            "latest_event_id": record.events[-1].event_id if record.events else None,
            "terminal_artifact_sequence": (
                [artifact.kind for artifact in terminal_artifacts] if terminal_artifacts is not None else None
            ),
            "terminal_event_sequence": (
                [event.name for event in terminal_events] if terminal_events is not None else None
            ),
            "terminal_artifact_refs": (
                {
                    "run_provenance": [terminal_artifacts[0].artifact_id],
                    "run_completed": [terminal_artifacts[1].artifact_id],
                }
                if terminal_artifacts is not None
                else None
            ),
            "terminal_event_refs": (
                {
                    "run_provenance_captured": [terminal_events[0].event_id],
                    "run_completed": [terminal_events[1].event_id],
                }
                if terminal_events is not None
                else None
            ),
            "pending_patch_proposals": (
                [EngineRunService._clone_jsonable(item) for item in pending_patch_proposals]
                if pending_patch_proposals is not None
                else [
                    {
                        "artifact_id": artifact.artifact_id,
                        "target_path": artifact.payload.get("target_path"),
                    }
                    for artifact in EngineRunService._pending_patch_proposals(record)
                ]
            ),
        }

    def get_run(self, run_id: str, *, validate: bool = True) -> EngineRunRecord:
        records = self._load_records()
        try:
            payload = records[run_id]
        except KeyError as exc:
            raise KeyError(f"unknown run_id: {run_id}") from exc
        return self._deserialize_record(payload, validate=validate)

    def _append_artifact(
        self,
        run_id: str,
        *,
        kind: str,
        payload: dict[str, Any],
        created_at: str | None = None,
        audit_metadata: dict[str, Any] | None = None,
    ) -> RunArtifact:
        record = self.get_run(run_id, validate=False)
        return self._append_artifact_to_record(
            record,
            kind=kind,
            payload=payload,
            created_at=created_at,
            audit_metadata=audit_metadata,
        )

    def _append_artifact_to_record(
        self,
        record: EngineRunRecord,
        *,
        kind: str,
        payload: dict[str, Any],
        created_at: str | None = None,
        audit_metadata: dict[str, Any] | None = None,
    ) -> RunArtifact:
        artifact_at = created_at or self._timestamp()
        artifact = RunArtifact(
            artifact_id=f"{record.run_id}:{len(record.artifacts) + 1:04d}:{kind}",
            kind=kind,
            created_at=artifact_at,
            payload=payload,
        )
        updated = EngineRunRecord(
            run_id=record.run_id,
            status=record.status,
            started_at=record.started_at,
            updated_at=artifact.created_at,
            completed_at=record.completed_at,
            operation=record.operation,
            scope=record.scope,
            intent=record.intent,
            request_fingerprint=record.request_fingerprint,
            artifacts=[*record.artifacts, artifact],
            events=record.events,
        )
        self._save_record(updated)
        audit_payload = {"run_id": record.run_id, "kind": kind, "artifact_id": artifact.artifact_id}
        if audit_metadata:
            audit_payload.update(audit_metadata)
        self._audit.record(name="engine_run_artifact_attached", metadata=audit_payload)
        return artifact

    def _record_event(
        self,
        run_id: str,
        *,
        name: str,
        payload: dict[str, Any],
        metadata: dict[str, Any] | None = None,
        created_at: str | None = None,
    ) -> RunEvent:
        record = self.get_run(run_id, validate=False)
        event_at = created_at or self._timestamp()
        event = RunEvent(
            event_id=f"{run_id}:{len(record.events) + 1:04d}:{name}",
            name=name,
            created_at=event_at,
            payload=payload,
        )
        updated = EngineRunRecord(
            run_id=record.run_id,
            status=record.status,
            started_at=record.started_at,
            updated_at=event.created_at,
            completed_at=record.completed_at,
            operation=record.operation,
            scope=record.scope,
            intent=record.intent,
            request_fingerprint=record.request_fingerprint,
            artifacts=record.artifacts,
            events=[*record.events, event],
        )
        self._save_record(updated)
        audit_metadata = {"run_id": run_id}
        if metadata:
            audit_metadata.update(metadata)
        self._audit.record(name=f"engine_{name}", metadata=audit_metadata)
        return event

    def _require_running(self, run_id: str) -> EngineRunRecord:
        record = self.get_run(run_id)
        if record.status != "running":
            raise ValueError(f"run {run_id} is not mutable: {record.status}")
        return record

    @staticmethod
    def _validate_terminal_status(status: RunStatus) -> None:
        if status not in _TERMINAL_RUN_STATUSES:
            raise ValueError("terminal run status must be one of: completed, failed, cancelled")

    @staticmethod
    def _validate_patch_decision(decision: PatchDecision) -> None:
        if decision not in {"accepted", "rejected"}:
            raise ValueError("patch decision must be one of: accepted, rejected")

    @staticmethod
    def _validate_retrieval_confidentiality_profile(profile: str) -> str:
        if not isinstance(profile, str):
            raise TypeError("retrieval_confidentiality_profile must be a string")
        normalized = profile.strip()
        if normalized not in {"confidential", "standard"}:
            raise ValueError(
                "retrieval_confidentiality_profile must be one of: confidential, standard"
            )
        return normalized

    @staticmethod
    def _require_non_empty_text(value: str, *, field_name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string")
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name} is required")
        return normalized

    @staticmethod
    def _require_patch_proposal(record: EngineRunRecord, *, target_path: str) -> RunArtifact:
        for artifact in reversed(record.artifacts):
            if artifact.kind != "patch_proposal":
                continue
            if str(artifact.payload.get("target_path")) == target_path:
                return artifact
        raise ValueError(f"no patch proposal recorded for target path: {target_path}")

    @staticmethod
    def _require_no_pending_patch_proposal_for_target_path(
        record: EngineRunRecord,
        *,
        target_path: str,
    ) -> None:
        resolved_proposal_ids = {
            str(artifact.payload.get("proposal_artifact_id"))
            for artifact in record.artifacts
            if artifact.kind == "patch_decision"
        }
        pending_proposals = [
            artifact
            for artifact in record.artifacts
            if artifact.kind == "patch_proposal"
            and str(artifact.payload.get("target_path")) == target_path
            and artifact.artifact_id not in resolved_proposal_ids
        ]
        if pending_proposals:
            raise ValueError(f"patch proposal already pending for target path: {target_path}")

    @staticmethod
    def _ensure_patch_decision_not_recorded(record: EngineRunRecord, *, proposal_artifact_id: str) -> None:
        for artifact in record.artifacts:
            if artifact.kind != "patch_decision":
                continue
            if str(artifact.payload.get("proposal_artifact_id")) == proposal_artifact_id:
                raise ValueError(f"patch decision already recorded for proposal: {proposal_artifact_id}")
        for event in record.events:
            if event.name not in {"patch_applied", "patch_rejected"}:
                continue
            if str(event.payload.get("proposal_artifact_id")) == proposal_artifact_id:
                raise ValueError(f"patch decision already recorded for proposal: {proposal_artifact_id}")

    @staticmethod
    def _require_patch_flow_inputs(
        *,
        patch_original: str | None,
        patch_proposed: str | None,
        patch_target_path: str | None,
        patch_decision: PatchDecision | None,
    ) -> tuple[str, str, str, PatchDecision]:
        missing = [
            name
            for name, value in (
                ("patch_original", patch_original),
                ("patch_proposed", patch_proposed),
                ("patch_target_path", patch_target_path),
                ("patch_decision", patch_decision),
            )
            if value is None
        ]
        if missing:
            raise ValueError(f"patch flow requires all patch inputs: {missing}")
        assert patch_original is not None
        assert patch_proposed is not None
        assert patch_target_path is not None
        assert patch_decision is not None
        normalized_target_path = EngineRunService._require_non_empty_text(
            patch_target_path,
            field_name="patch_target_path",
        )
        return patch_original, patch_proposed, normalized_target_path, patch_decision

    @classmethod
    def _require_run_plan(cls, record: EngineRunRecord, *, operation: str) -> RunArtifact:
        for artifact in reversed(record.artifacts):
            if artifact.kind == "run_plan":
                return artifact
        raise ValueError(f"{operation} requires a recorded run plan before proceeding")

    @classmethod
    def _pending_patch_proposals(cls, record: EngineRunRecord) -> list[RunArtifact]:
        latest_proposals_by_path = cls._latest_patch_proposals_by_target_path(record)
        resolved_proposal_ids = {
            str(artifact.payload.get("proposal_artifact_id"))
            for artifact in record.artifacts
            if artifact.kind == "patch_decision"
        }
        pending = [
            artifact
            for artifact in latest_proposals_by_path.values()
            if artifact.artifact_id not in resolved_proposal_ids
        ]
        return sorted(pending, key=lambda artifact: artifact.artifact_id)

    @staticmethod
    def _latest_patch_proposals_by_target_path(record: EngineRunRecord) -> dict[str, RunArtifact]:
        latest_proposals_by_path: dict[str, RunArtifact] = {}
        for artifact in record.artifacts:
            if artifact.kind != "patch_proposal":
                continue
            target_path = str(artifact.payload.get("target_path") or "")
            if not target_path:
                continue
            latest_proposals_by_path[target_path] = artifact
        return latest_proposals_by_path

    @classmethod
    def _require_no_pending_patch_proposals(cls, record: EngineRunRecord, *, operation: str) -> None:
        pending = cls._pending_patch_proposals(record)
        if not pending:
            return
        pending_targets = [
            str(artifact.payload.get("target_path") or artifact.artifact_id)
            for artifact in pending
        ]
        raise ValueError(f"{operation} requires resolved patch proposals before proceeding: {pending_targets}")

    @staticmethod
    def _build_terminalization(
        record: EngineRunRecord,
        *,
        captured_at: str,
        terminal_status: RunStatus,
    ) -> _RunTerminalization:
        planned_terminal_status = EngineRunService._planned_terminal_status_payload(record) or terminal_status
        provenance_sequence = len(record.artifacts) + 1
        completion_sequence = len(record.artifacts) + 2
        provenance_event_sequence = len(record.events) + 1
        completion_event_sequence = len(record.events) + 2
        provenance_artifact_id = f"{record.run_id}:{provenance_sequence:04d}:run_provenance"
        completion_artifact_id = f"{record.run_id}:{completion_sequence:04d}:run_completed"
        provenance_event_id = f"{record.run_id}:{provenance_event_sequence:04d}:run_provenance_captured"
        completion_event_id = f"{record.run_id}:{completion_event_sequence:04d}:run_completed"
        flow_steps = [
            *EngineRunService._flow_step_summaries(record),
            {
                "sequence": provenance_sequence,
                "artifact_id": provenance_artifact_id,
                "artifact_kind": "run_provenance",
                "artifact_created_at": captured_at,
                "event_id": provenance_event_id,
                "event_name": "run_provenance_captured",
                "event_created_at": captured_at,
            },
            {
                "sequence": completion_sequence,
                "artifact_id": completion_artifact_id,
                "artifact_kind": "run_completed",
                "artifact_created_at": captured_at,
                "event_id": completion_event_id,
                "event_name": "run_completed",
                "event_created_at": captured_at,
            },
        ]
        provenance_artifact = RunArtifact(
            artifact_id=provenance_artifact_id,
            kind="run_provenance",
            created_at=captured_at,
            payload=EngineRunService._build_provenance_payload(
                record,
                captured_at=captured_at,
                planned_terminal_status=planned_terminal_status,
                actual_terminal_status=terminal_status,
                terminal_artifact_count=len(record.artifacts) + 2,
                terminal_event_count=len(record.events) + 2,
                terminal_artifact_refs={
                    "run_provenance": (provenance_artifact_id,),
                    "run_completed": (completion_artifact_id,),
                },
                terminal_event_refs={
                    "run_provenance_captured": (provenance_event_id,),
                    "run_completed": (completion_event_id,),
                },
                flow_steps=tuple(flow_steps),
            ),
        )
        provenance_event = RunEvent(
            event_id=provenance_event_id,
            name="run_provenance_captured",
            created_at=captured_at,
            payload={
                "artifact_id": provenance_artifact.artifact_id,
                "planned_terminal_status": planned_terminal_status,
                "actual_terminal_status": terminal_status,
            },
        )
        completion_artifact = RunArtifact(
            artifact_id=completion_artifact_id,
            kind="run_completed",
            created_at=captured_at,
            payload={
                "status": terminal_status,
                "operation": record.operation,
                "scope": record.scope,
                "intent": record.intent,
                "request_fingerprint": record.request_fingerprint,
            },
        )
        completion_event = RunEvent(
            event_id=completion_event_id,
            name="run_completed",
            created_at=captured_at,
            payload={"status": terminal_status, "artifact_id": completion_artifact.artifact_id},
        )
        return _RunTerminalization(
            provenance_artifact=provenance_artifact,
            provenance_event=provenance_event,
            completion_artifact=completion_artifact,
            completion_event=completion_event,
        )

    @staticmethod
    def _build_provenance_payload(
        record: EngineRunRecord,
        *,
        captured_at: str,
        planned_terminal_status: RunStatus,
        actual_terminal_status: RunStatus,
        terminal_artifact_count: int,
        terminal_event_count: int,
        terminal_artifact_refs: dict[str, tuple[str, ...]],
        terminal_event_refs: dict[str, tuple[str, ...]],
        flow_steps: tuple[dict[str, Any], ...],
    ) -> dict[str, Any]:
        artifact_kinds = [artifact.kind for artifact in record.artifacts]
        event_names = [event.name for event in record.events]
        flow_step_payload = [EngineRunService._clone_jsonable(step) for step in flow_steps]
        flow_artifact_refs = EngineRunService._flow_artifact_refs(record)
        flow_event_refs = EngineRunService._flow_event_refs(record)
        run_lifecycle = EngineRunService._run_lifecycle_payload(
            record,
            terminal_artifacts=(
                RunArtifact(
                    artifact_id=terminal_artifact_refs["run_provenance"][0],
                    kind="run_provenance",
                    created_at=captured_at,
                    payload={},
                ),
                RunArtifact(
                    artifact_id=terminal_artifact_refs["run_completed"][0],
                    kind="run_completed",
                    created_at=captured_at,
                    payload={},
                ),
            ),
            terminal_events=(
                RunEvent(
                    event_id=terminal_event_refs["run_provenance_captured"][0],
                    name="run_provenance_captured",
                    created_at=captured_at,
                    payload={},
                ),
                RunEvent(
                    event_id=terminal_event_refs["run_completed"][0],
                    name="run_completed",
                    created_at=captured_at,
                    payload={},
                ),
            ),
        )
        payload = {
            "run_id": record.run_id,
            "captured_at": captured_at,
            "planned_terminal_status": planned_terminal_status,
            "status": actual_terminal_status,
            "actual_terminal_status": actual_terminal_status,
            "prior_status": record.status,
            "started_at": record.started_at,
            "snapshot_updated_at": record.updated_at,
            "completed_at": captured_at,
            "operation": record.operation,
            "scope": record.scope,
            "intent": record.intent,
            "request_fingerprint": record.request_fingerprint,
            "run_summary": EngineRunService._run_summary_payload(record),
            "run_plan_digest": EngineRunService._run_plan_digest_payload(record),
            "artifact_count": len(record.artifacts),
            "event_count": len(record.events),
            "terminal_artifact_count": terminal_artifact_count,
            "terminal_event_count": terminal_event_count,
            "patch_proposal_count": len([artifact for artifact in record.artifacts if artifact.kind == "patch_proposal"]),
            "patch_decision_count": len([artifact for artifact in record.artifacts if artifact.kind == "patch_decision"]),
            "patch_decisions": [
                EngineRunService._patch_decision_summary(record, artifact)
                for artifact in record.artifacts
                if artifact.kind == "patch_decision"
            ],
            "run_failure_artifacts": [
                EngineRunService._run_failure_summary(artifact)
                for artifact in record.artifacts
                if artifact.kind == "run_failure"
            ],
            "export_preview_artifacts": [
                EngineRunService._export_preview_summary(artifact)
                for artifact in record.artifacts
                if artifact.kind == "export_preview"
            ],
            "export_final_artifacts": [
                EngineRunService._export_final_summary(artifact)
                for artifact in record.artifacts
                if artifact.kind == "export_final"
            ],
            "retrieval_evidence": EngineRunService._retrieval_evidence_payload(record),
            "artifact_sequence": artifact_kinds,
            "event_sequence": event_names,
            "artifact_kinds": artifact_kinds,
            "event_names": event_names,
            "terminal_artifact_refs": {
                "run_provenance": list(terminal_artifact_refs["run_provenance"]),
                "run_completed": list(terminal_artifact_refs["run_completed"]),
            },
            "terminal_event_refs": {
                "run_provenance_captured": list(terminal_event_refs["run_provenance_captured"]),
                "run_completed": list(terminal_event_refs["run_completed"]),
            },
            "terminal_artifact_sequence": [
                "run_provenance",
                "run_completed",
            ],
            "terminal_event_sequence": [
                "run_provenance_captured",
                "run_completed",
            ],
            "run_lifecycle": run_lifecycle,
            "run_lifecycle_digest": EngineRunService._fingerprint_payload(run_lifecycle),
            "pending_patch_proposals": [
                {
                    "artifact_id": artifact.artifact_id,
                    "target_path": artifact.payload.get("target_path"),
                }
                for artifact in EngineRunService._pending_patch_proposals(record)
            ],
            "flow_steps": flow_step_payload,
            "patch_proposals": [
                EngineRunService._patch_proposal_summary(artifact)
                for artifact in record.artifacts
                if artifact.kind == "patch_proposal"
            ],
            "artifact_refs": flow_artifact_refs,
            "event_refs": flow_event_refs,
        }
        payload["flow_digest"] = EngineRunService._fingerprint_payload(payload)
        return payload

    @staticmethod
    def _retrieval_evidence_payload(record: EngineRunRecord) -> dict[str, Any] | None:
        for artifact in reversed(record.artifacts):
            if artifact.kind != "retrieval_result":
                continue
            return EngineRunService._clone_jsonable({
                "artifact_id": artifact.artifact_id,
                "audit_ref": artifact.payload.get("audit_ref"),
                "query_scope": artifact.payload.get("query_scope"),
                "query_intent": artifact.payload.get("query_intent"),
                "retrieval_query_hash": artifact.payload.get("retrieval_query_hash"),
                "retrieval_constraints": artifact.payload.get("retrieval_constraints"),
                "hit_count": artifact.payload.get("hit_count"),
                "strategies_used": list(artifact.payload.get("strategies_used", [])),
            })
        return None

    @staticmethod
    def _artifact_ids(record: EngineRunRecord, *, kind: str) -> tuple[str, ...]:
        return tuple(artifact.artifact_id for artifact in record.artifacts if artifact.kind == kind)

    @staticmethod
    def _latest_artifact(record: EngineRunRecord, *, kind: str) -> RunArtifact | None:
        return next((artifact for artifact in reversed(record.artifacts) if artifact.kind == kind), None)

    @staticmethod
    def _event_ids(record: EngineRunRecord, *, name: str) -> tuple[str, ...]:
        return tuple(event.event_id for event in record.events if event.name == name)

    @staticmethod
    def _flow_step_summaries(record: EngineRunRecord) -> tuple[dict[str, Any], ...]:
        EngineRunService._require_aligned_flow_record(record)
        steps: list[dict[str, Any]] = []
        for sequence, (artifact, event) in enumerate(zip(record.artifacts, record.events), start=1):
            steps.append(
                {
                    "sequence": sequence,
                    "artifact_id": artifact.artifact_id,
                    "artifact_kind": artifact.kind,
                    "artifact_created_at": artifact.created_at,
                    "event_id": event.event_id,
                    "event_name": event.name,
                    "event_created_at": event.created_at,
                }
            )
        return tuple(steps)

    @staticmethod
    def _require_aligned_flow_record(record: EngineRunRecord) -> None:
        if len(record.artifacts) != len(record.events):
            raise ValueError(
                f"run {record.run_id} has mismatched artifact/event counts: "
                f"{len(record.artifacts)} artifacts != {len(record.events)} events"
            )

    @staticmethod
    def _flow_step_summaries_with_gaps(record: EngineRunRecord) -> tuple[dict[str, Any], ...]:
        steps: list[dict[str, Any]] = []
        max_length = max(len(record.artifacts), len(record.events))
        for sequence in range(1, max_length + 1):
            artifact = record.artifacts[sequence - 1] if sequence <= len(record.artifacts) else None
            event = record.events[sequence - 1] if sequence <= len(record.events) else None
            steps.append(
                {
                    "sequence": sequence,
                    "artifact_id": artifact.artifact_id if artifact is not None else None,
                    "artifact_kind": artifact.kind if artifact is not None else None,
                    "artifact_created_at": artifact.created_at if artifact is not None else None,
                    "event_id": event.event_id if event is not None else None,
                    "event_name": event.name if event is not None else None,
                    "event_created_at": event.created_at if event is not None else None,
                }
            )
        return tuple(steps)

    @staticmethod
    def _flow_artifact_refs(record: EngineRunRecord) -> dict[str, list[str]]:
        return {
            "run_started": list(EngineRunService._artifact_ids(record, kind="run_started")),
            "run_plan": list(EngineRunService._artifact_ids(record, kind="run_plan")),
            "retrieval_result": list(EngineRunService._artifact_ids(record, kind="retrieval_result")),
            "patch_proposal": list(EngineRunService._artifact_ids(record, kind="patch_proposal")),
            "patch_decision": list(EngineRunService._artifact_ids(record, kind="patch_decision")),
            "run_failure": list(EngineRunService._artifact_ids(record, kind="run_failure")),
            "export_preview": list(EngineRunService._artifact_ids(record, kind="export_preview")),
            "export_final": list(EngineRunService._artifact_ids(record, kind="export_final")),
        }

    @staticmethod
    def _flow_event_refs(record: EngineRunRecord) -> dict[str, list[str]]:
        return {
            "run_started": list(EngineRunService._event_ids(record, name="run_started")),
            "run_planned": list(EngineRunService._event_ids(record, name="run_planned")),
            "retrieval_attached": list(EngineRunService._event_ids(record, name="retrieval_attached")),
            "patch_proposed": list(EngineRunService._event_ids(record, name="patch_proposed")),
            "patch_applied": list(EngineRunService._event_ids(record, name="patch_applied")),
            "patch_rejected": list(EngineRunService._event_ids(record, name="patch_rejected")),
            "run_failed": list(EngineRunService._event_ids(record, name="run_failed")),
            "export_preview_attached": list(EngineRunService._event_ids(record, name="export_preview_attached")),
            "export_final_attached": list(EngineRunService._event_ids(record, name="export_final_attached")),
        }

    @staticmethod
    def _patch_proposal_summary(artifact: RunArtifact) -> dict[str, Any]:
        return {
            "artifact_id": artifact.artifact_id,
            "target_path": artifact.payload.get("target_path"),
            "is_empty": artifact.payload.get("is_empty"),
            "line_count": artifact.payload.get("line_count"),
            "patch_hash": artifact.payload.get("patch_hash"),
        }

    @staticmethod
    def _patch_decision_summary(record: EngineRunRecord, artifact: RunArtifact) -> dict[str, Any]:
        decision_event_id = artifact.payload.get("decision_event_id")
        if decision_event_id is None:
            decision_event = next(
                (
                    event
                    for event in reversed(record.events)
                    if event.name in {"patch_applied", "patch_rejected"}
                    and str(event.payload.get("proposal_artifact_id")) == str(artifact.payload.get("proposal_artifact_id"))
                ),
                None,
            )
            decision_event_id = decision_event.event_id if decision_event is not None else None
        return {
            "artifact_id": artifact.artifact_id,
            "decision_event_id": decision_event_id,
            "target_path": artifact.payload.get("target_path"),
            "decision": artifact.payload.get("decision"),
            "reason": artifact.payload.get("reason"),
            "proposal_artifact_id": artifact.payload.get("proposal_artifact_id"),
            "proposal_patch_hash": artifact.payload.get("proposal_patch_hash"),
            "proposal_line_count": artifact.payload.get("proposal_line_count"),
        }

    @staticmethod
    def _export_preview_summary(artifact: RunArtifact) -> dict[str, Any]:
        return {
            "artifact_id": artifact.artifact_id,
            "output_format": artifact.payload.get("output_format"),
            "size_bytes": artifact.payload.get("size_bytes"),
            "expires_at": artifact.payload.get("expires_at"),
            "storage_ref": artifact.payload.get("storage_ref"),
            "options_fingerprint": artifact.payload.get("options_fingerprint"),
        }

    @staticmethod
    def _export_final_summary(artifact: RunArtifact) -> dict[str, Any]:
        return {
            "artifact_id": artifact.artifact_id,
            "output_format": artifact.payload.get("output_format"),
            "size_bytes": artifact.payload.get("size_bytes"),
            "content_hash": artifact.payload.get("content_hash"),
            "destination_path": artifact.payload.get("destination_path"),
            "export_approved": artifact.payload.get("export_approved"),
        }

    @staticmethod
    def _run_failure_summary(artifact: RunArtifact) -> dict[str, Any]:
        return {
            "artifact_id": artifact.artifact_id,
            "error_type": artifact.payload.get("error_type"),
            "error_message": artifact.payload.get("error_message"),
            "failed_phase": artifact.payload.get("failed_phase"),
            "planned_terminal_status": artifact.payload.get("planned_terminal_status"),
            "actual_terminal_status": artifact.payload.get("actual_terminal_status"),
            "run_plan_digest": artifact.payload.get("run_plan_digest"),
        }

    @staticmethod
    def _run_provenance_payload(record: EngineRunRecord) -> dict[str, Any] | None:
        for artifact in reversed(record.artifacts):
            if artifact.kind != "run_provenance":
                continue
            return EngineRunService._clone_jsonable(artifact.payload)
        return None

    @staticmethod
    def _run_plan_digest_payload(record: EngineRunRecord) -> str | None:
        for artifact in reversed(record.artifacts):
            if artifact.kind != "run_plan":
                continue
            plan_digest = artifact.payload.get("plan_digest")
            return str(plan_digest) if plan_digest is not None else None
        return None

    @staticmethod
    def _run_plan_payload(record: EngineRunRecord) -> dict[str, Any] | None:
        for artifact in reversed(record.artifacts):
            if artifact.kind != "run_plan":
                continue
            return EngineRunService._clone_jsonable(artifact.payload)
        return None

    @classmethod
    def _planned_terminal_status_payload(cls, record: EngineRunRecord) -> RunStatus | None:
        plan_payload = cls._run_plan_payload(record)
        if plan_payload is None:
            return None
        planned_terminal_status = plan_payload.get("planned_terminal_status")
        if planned_terminal_status is None:
            return None
        return str(planned_terminal_status)

    @staticmethod
    def _run_summary_payload(record: EngineRunRecord) -> dict[str, Any]:
        return asdict(EngineRunService._build_run_summary(record))

    @classmethod
    def _require_run_provenance(cls, record: EngineRunRecord) -> dict[str, Any]:
        provenance = cls._run_provenance_payload(record)
        if provenance is None:
            raise ValueError(f"run {record.run_id} does not have captured provenance")
        return provenance

    def _record_run_failure(
        self,
        run_id: str,
        *,
        error: Exception,
        final_status: RunStatus,
        failed_phase: str | None,
    ) -> None:
        record = self._require_running(run_id)
        failure_at = self._timestamp()
        error_type = type(error).__name__
        error_message = str(error)
        run_plan_digest = self._run_plan_digest_payload(record)
        normalized_failed_phase = failed_phase.strip() if isinstance(failed_phase, str) and failed_phase.strip() else None
        flow_steps = [
            EngineRunService._clone_jsonable(step)
            for step in EngineRunService._flow_step_summaries_with_gaps(record)
        ]
        artifact_refs = EngineRunService._flow_artifact_refs(record)
        event_refs = EngineRunService._flow_event_refs(record)
        pending_patch_proposals = [
            {
                "artifact_id": pending.artifact_id,
                "target_path": pending.payload.get("target_path"),
            }
            for pending in self._pending_patch_proposals(record)
        ]
        run_lifecycle = EngineRunService._run_lifecycle_payload(
            record,
            pending_patch_proposals=tuple(pending_patch_proposals),
        )
        failure_payload = {
            "error_type": error_type,
            "error_message": error_message,
            "failed_phase": normalized_failed_phase,
            "planned_terminal_status": final_status,
            "actual_terminal_status": "failed",
            "operation": record.operation,
            "scope": record.scope,
            "intent": record.intent,
            "request_fingerprint": record.request_fingerprint,
            "run_summary": self._run_summary_payload(record),
            "artifact_count": len(record.artifacts),
            "event_count": len(record.events),
            "run_plan_digest": run_plan_digest,
            "retrieval_evidence": self._retrieval_evidence_payload(record),
            "artifact_sequence": [artifact.kind for artifact in record.artifacts],
            "event_sequence": [event.name for event in record.events],
            "artifact_kinds": [artifact.kind for artifact in record.artifacts],
            "event_names": [event.name for event in record.events],
            "flow_steps": flow_steps,
            "artifact_refs": artifact_refs,
            "event_refs": event_refs,
            "patch_proposals": [
                EngineRunService._patch_proposal_summary(pending)
                for pending in record.artifacts
                if pending.kind == "patch_proposal"
            ],
            "patch_decisions": [
                EngineRunService._patch_decision_summary(record, decision)
                for decision in record.artifacts
                if decision.kind == "patch_decision"
            ],
            "export_preview_artifacts": [
                EngineRunService._export_preview_summary(export_artifact)
                for export_artifact in record.artifacts
                if export_artifact.kind == "export_preview"
            ],
            "export_final_artifacts": [
                EngineRunService._export_final_summary(export_artifact)
                for export_artifact in record.artifacts
                if export_artifact.kind == "export_final"
            ],
            "pending_patch_proposals": pending_patch_proposals,
            "run_lifecycle": run_lifecycle,
            "run_lifecycle_digest": self._fingerprint_payload(run_lifecycle),
            "failure_context": {
                "artifact_sequence": [artifact.kind for artifact in record.artifacts],
                "event_sequence": [event.name for event in record.events],
                "artifact_refs": artifact_refs,
                "event_refs": event_refs,
                "flow_steps": flow_steps,
                "pending_patch_proposals": pending_patch_proposals,
                "retrieval_evidence": self._retrieval_evidence_payload(record),
            },
        }
        failure_payload["flow_digest"] = self._fingerprint_payload(failure_payload)
        artifact = self._append_artifact(
            run_id,
            kind="run_failure",
            created_at=failure_at,
            payload=failure_payload,
        )
        self._record_event(
            run_id,
            name="run_failed",
            created_at=failure_at,
            payload={
                "artifact_id": artifact.artifact_id,
                "error_type": error_type,
                "error_message": error_message,
                "failed_phase": normalized_failed_phase,
                "planned_terminal_status": final_status,
                "actual_terminal_status": "failed",
                "operation": record.operation,
                "scope": record.scope,
                "intent": record.intent,
                "request_fingerprint": record.request_fingerprint,
                "run_plan_digest": run_plan_digest,
            },
            metadata={
                "artifact_id": artifact.artifact_id,
                "error_type": error_type,
                "error_message": error_message,
                "failed_phase": normalized_failed_phase,
                "planned_terminal_status": final_status,
                "actual_terminal_status": "failed",
                "operation": record.operation,
                "scope": record.scope,
                "intent": record.intent,
                "request_fingerprint": record.request_fingerprint,
                "run_plan_digest": run_plan_digest,
            },
        )
        self._audit.record(
            name="engine_run_failed_summary",
            metadata={
                "run_id": run_id,
                "artifact_id": artifact.artifact_id,
                "error_type": error_type,
                "error_message": error_message,
                "failed_phase": normalized_failed_phase,
                "planned_terminal_status": final_status,
                "actual_terminal_status": "failed",
                "operation": record.operation,
                "scope": record.scope,
                "intent": record.intent,
                "request_fingerprint": record.request_fingerprint,
                "artifact_count": len(record.artifacts),
                "event_count": len(record.events),
                "run_plan_digest": run_plan_digest,
                "flow_digest": failure_payload["flow_digest"],
                "run_lifecycle_digest": failure_payload["run_lifecycle_digest"],
                "artifact_refs": artifact_refs,
                "event_refs": event_refs,
                "pending_patch_proposals": failure_payload["pending_patch_proposals"],
            },
        )

    def _record_run_flow_failed_summary(
        self,
        run_id: str,
        *,
        error: Exception,
        failed_phase: str | None,
        planned_terminal_status: RunStatus,
    ) -> None:
        try:
            snapshot = self.describe_run_flow(run_id)
        except Exception as summary_error:
            record = self.get_run(run_id, validate=False)
            run_provenance = self._run_provenance_payload(record)
            latest_failure_artifact = self._latest_artifact(record, kind="run_failure")
            self._audit.record(
                name="engine_run_flow_failed_summary",
                metadata={
                    "run_id": run_id,
                    "status": record.status,
                    "operation": record.operation,
                    "scope": record.scope,
                    "intent": record.intent,
                    "request_fingerprint": record.request_fingerprint,
                    "failed_phase": failed_phase,
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "planned_terminal_status": planned_terminal_status,
                    "actual_terminal_status": record.status,
                    "artifact_count": len(record.artifacts),
                    "event_count": len(record.events),
                    "run_plan_digest": self._run_plan_digest_payload(record),
                    "flow_digest": run_provenance.get("flow_digest") if run_provenance is not None else None,
                    "run_lifecycle_digest": self._fingerprint_payload(self._run_lifecycle_payload(record)),
                    "run_lifecycle": self._run_lifecycle_payload(record),
                    "retrieval_evidence": self._retrieval_evidence_payload(record),
                    "terminal_artifact_refs": (
                        run_provenance.get("terminal_artifact_refs") if run_provenance is not None else None
                    ),
                    "terminal_event_refs": (
                        run_provenance.get("terminal_event_refs") if run_provenance is not None else None
                    ),
                    "latest_failure_artifact_id": (
                        latest_failure_artifact.artifact_id if latest_failure_artifact is not None else None
                    ),
                    "summary_error_type": type(summary_error).__name__,
                    "summary_error_message": str(summary_error),
                    "summary_source": "fallback",
                },
            )
            return
        run_provenance = snapshot.run_provenance or {}
        self._audit.record(
            name="engine_run_flow_failed_summary",
            metadata={
                "run_id": run_id,
                "status": snapshot.summary.status,
                "operation": snapshot.summary.operation,
                "scope": snapshot.summary.scope,
                "intent": snapshot.summary.intent,
                "request_fingerprint": snapshot.summary.request_fingerprint,
                "failed_phase": failed_phase,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "planned_terminal_status": planned_terminal_status,
                "actual_terminal_status": snapshot.summary.status,
                "artifact_count": snapshot.summary.artifact_count,
                "event_count": snapshot.summary.event_count,
                "run_plan_digest": snapshot.run_plan_digest,
                "flow_digest": snapshot.flow_digest,
                "run_lifecycle_digest": snapshot.run_lifecycle_digest,
                "run_lifecycle": snapshot.to_manifest()["run_lifecycle"],
                "retrieval_evidence": snapshot.retrieval_evidence,
                "terminal_artifact_refs": run_provenance.get("terminal_artifact_refs"),
                "terminal_event_refs": run_provenance.get("terminal_event_refs"),
                "latest_failure_artifact_id": (
                    snapshot.summary.latest_failure_artifact.artifact_id
                    if snapshot.summary.latest_failure_artifact is not None
                    else None
                ),
                "summary_source": "validated",
            },
        )

    @classmethod
    def _require_retrieval_evidence(cls, record: EngineRunRecord, *, operation: str) -> dict[str, Any]:
        retrieval_evidence = cls._retrieval_evidence_payload(record)
        if retrieval_evidence is None:
            raise ValueError(f"{operation} requires retrieval evidence before proceeding")
        if str(retrieval_evidence.get("query_scope")) != record.scope:
            raise ValueError(
                f"{operation} requires retrieval evidence for scope {record.scope}"
            )
        return retrieval_evidence

    @staticmethod
    def _require_matching_scope(record: EngineRunRecord, *, scope: str, operation: str) -> None:
        if scope != record.scope:
            raise ValueError(f"{operation} requires scope {record.scope}")

    def _load_records(self) -> dict[str, Any]:
        payload = self._store.read_json(_RUNS_FILE, default={})
        if isinstance(payload, dict):
            return payload
        return {}

    def _require_artifact(self, run_id: str, *, kind: str) -> RunArtifact:
        record = self.get_run(run_id)
        return self._require_artifact_from_record(record, kind=kind)

    @staticmethod
    def _require_artifact_from_record(record: EngineRunRecord, *, kind: str) -> RunArtifact:
        for artifact in reversed(record.artifacts):
            if artifact.kind == kind:
                return artifact
        raise ValueError(f"run {record.run_id} does not have a recorded {kind} artifact")

    def _require_event(self, run_id: str, *, name: str) -> RunEvent:
        record = self.get_run(run_id)
        return self._require_event_from_record(record, name=name)

    @staticmethod
    def _require_event_from_record(record: EngineRunRecord, *, name: str) -> RunEvent:
        for event in reversed(record.events):
            if event.name == name:
                return event
        raise ValueError(f"run {record.run_id} does not have a recorded {name} event")

    def _save_record(self, record: EngineRunRecord) -> None:
        records = self._load_records()
        records[record.run_id] = self._serialize_record(record)
        self._store.write_json(_RUNS_FILE, records)

    @staticmethod
    def _serialize_record(record: EngineRunRecord) -> dict[str, Any]:
        return asdict(record)

    @staticmethod
    def _deserialize_record(payload: dict[str, Any], *, validate: bool = True) -> EngineRunRecord:
        artifacts = [
            RunArtifact(
                artifact_id=str(item["artifact_id"]),
                kind=str(item["kind"]),
                created_at=str(item["created_at"]),
                payload=dict(item.get("payload", {})),
            )
            for item in payload.get("artifacts", [])
            if isinstance(item, dict)
        ]
        events = [
            RunEvent(
                event_id=str(item["event_id"]),
                name=str(item["name"]),
                created_at=str(item["created_at"]),
                payload=dict(item.get("payload", {})),
            )
            for item in payload.get("events", [])
            if isinstance(item, dict)
        ]
        record = EngineRunRecord(
            run_id=str(payload["run_id"]),
            status=payload.get("status", "running"),
            started_at=str(payload["started_at"]),
            updated_at=str(payload["updated_at"]),
            completed_at=str(payload["completed_at"]) if payload.get("completed_at") is not None else None,
            operation=str(payload.get("operation", "unspecified")),
            scope=str(payload.get("scope", "workspace")),
            intent=str(payload.get("intent", "unspecified")),
            request_fingerprint=str(payload.get("request_fingerprint", "none")),
            artifacts=artifacts,
            events=events,
        )
        if validate:
            EngineRunService._validate_record_state(record)
        return record

    @staticmethod
    def _validate_record_state(record: EngineRunRecord) -> None:
        if record.status not in {"running", "completed", "failed", "cancelled"}:
            raise ValueError(f"run {record.run_id} has invalid status: {record.status}")
        if record.status == "running" and record.completed_at is not None:
            raise ValueError(f"run {record.run_id} is running but has completed_at set")
        if record.status != "running" and record.completed_at is None:
            raise ValueError(f"run {record.run_id} is terminal but missing completed_at")
        EngineRunService._validate_append_only_sequence(record)
        EngineRunService._validate_patch_proposal_state(record)
        if record.status != "running":
            if len(record.artifacts) != len(record.events):
                raise ValueError(
                    f"run {record.run_id} has mismatched artifact/event counts: "
                    f"{len(record.artifacts)} artifacts != {len(record.events)} events"
                )
            if len(record.artifacts) < 2:
                raise ValueError(f"run {record.run_id} is terminal but missing completion artifacts")
            if len(record.events) < 2:
                raise ValueError(f"run {record.run_id} is terminal but missing completion events")
            if record.artifacts[-2].kind != "run_provenance" or record.artifacts[-1].kind != "run_completed":
                raise ValueError(f"run {record.run_id} has inconsistent terminal artifact sequence")
            if record.events[-2].name != "run_provenance_captured" or record.events[-1].name != "run_completed":
                raise ValueError(f"run {record.run_id} has inconsistent terminal event sequence")
            if record.updated_at != record.artifacts[-1].created_at:
                raise ValueError(f"run {record.run_id} has inconsistent updated_at timestamp")
            if record.completed_at != record.artifacts[-1].created_at:
                raise ValueError(f"run {record.run_id} has inconsistent completed_at timestamp")
            EngineRunService._validate_terminal_record_payloads(record)
        else:
            terminal_artifacts = [
                artifact.kind
                for artifact in record.artifacts
                if artifact.kind in {"run_provenance", "run_completed"}
            ]
            if terminal_artifacts:
                raise ValueError(
                    f"run {record.run_id} is running but has terminal artifacts: {terminal_artifacts}"
                )
            terminal_events = [
                event.name
                for event in record.events
                if event.name in {"run_provenance_captured", "run_completed"}
            ]
            if terminal_events:
                raise ValueError(f"run {record.run_id} is running but has terminal events: {terminal_events}")
            if record.artifacts and record.updated_at != record.artifacts[-1].created_at:
                raise ValueError(f"run {record.run_id} has inconsistent updated_at timestamp")
        if len(record.artifacts) != len(record.events):
            raise ValueError(
                f"run {record.run_id} has mismatched artifact/event counts: "
                f"{len(record.artifacts)} artifacts != {len(record.events)} events"
            )

    @staticmethod
    def _validate_patch_proposal_state(record: EngineRunRecord) -> None:
        resolved_proposal_ids = {
            str(artifact.payload.get("proposal_artifact_id"))
            for artifact in record.artifacts
            if artifact.kind == "patch_decision"
        }
        unresolved_by_path: dict[str, list[str]] = {}
        for artifact in record.artifacts:
            if artifact.kind != "patch_proposal":
                continue
            target_path = str(artifact.payload.get("target_path") or "")
            if not target_path or artifact.artifact_id in resolved_proposal_ids:
                continue
            unresolved_by_path.setdefault(target_path, []).append(artifact.artifact_id)
        duplicate_targets = {
            target_path: artifact_ids
            for target_path, artifact_ids in unresolved_by_path.items()
            if len(artifact_ids) > 1
        }
        if duplicate_targets:
            raise ValueError(
                f"run {record.run_id} has multiple unresolved patch proposals for target paths: "
                f"{sorted(duplicate_targets)}"
            )

    @staticmethod
    def _validate_terminal_record_payloads(record: EngineRunRecord) -> None:
        terminal_artifacts = [
            artifact
            for artifact in record.artifacts
            if artifact.kind in {"run_provenance", "run_completed"}
        ]
        terminal_events = [
            event
            for event in record.events
            if event.name in {"run_provenance_captured", "run_completed"}
        ]
        if len(terminal_artifacts) != 2:
            raise ValueError(f"run {record.run_id} has inconsistent terminal artifact count")
        if len(terminal_events) != 2:
            raise ValueError(f"run {record.run_id} has inconsistent terminal event count")
        if terminal_artifacts[-2].kind != "run_provenance" or terminal_artifacts[-1].kind != "run_completed":
            raise ValueError(f"run {record.run_id} has inconsistent terminal artifact sequence")
        if terminal_events[-2].name != "run_provenance_captured" or terminal_events[-1].name != "run_completed":
            raise ValueError(f"run {record.run_id} has inconsistent terminal event sequence")
        preterminal_artifacts = list(record.artifacts[:-2])
        preterminal_events = list(record.events[:-2])
        if not preterminal_artifacts or not preterminal_events:
            raise ValueError(f"run {record.run_id} has incomplete terminal provenance inputs")
        preterminal_updated_at = max(preterminal_artifacts[-1].created_at, preterminal_events[-1].created_at)
        preterminal_record = EngineRunRecord(
            run_id=record.run_id,
            status="running",
            started_at=record.started_at,
            updated_at=preterminal_updated_at,
            completed_at=None,
            operation=record.operation,
            scope=record.scope,
            intent=record.intent,
            request_fingerprint=record.request_fingerprint,
            artifacts=preterminal_artifacts,
            events=preterminal_events,
        )
        provenance_artifact = record.artifacts[-2]
        completion_artifact = record.artifacts[-1]
        provenance_event = record.events[-2]
        completion_event = record.events[-1]
        provenance_payload = provenance_artifact.payload
        completion_payload = completion_artifact.payload
        provenance_event_payload = provenance_event.payload
        completion_event_payload = completion_event.payload
        expected_summary = asdict(EngineRunService._build_run_summary(preterminal_record))
        expected_artifact_sequence = [artifact.kind for artifact in preterminal_record.artifacts]
        expected_event_sequence = [event.name for event in preterminal_record.events]
        expected_artifact_refs = EngineRunService._flow_artifact_refs(preterminal_record)
        expected_event_refs = EngineRunService._flow_event_refs(preterminal_record)
        expected_terminal_artifact_refs = {
            "run_provenance": [provenance_artifact.artifact_id],
            "run_completed": [completion_artifact.artifact_id],
        }
        expected_terminal_event_refs = {
            "run_provenance_captured": [provenance_event.event_id],
            "run_completed": [completion_event.event_id],
        }
        expected_pending_patch_proposals = [
            {
                "artifact_id": artifact.artifact_id,
                "target_path": artifact.payload.get("target_path"),
            }
            for artifact in EngineRunService._pending_patch_proposals(preterminal_record)
        ]
        expected_run_lifecycle = EngineRunService._run_lifecycle_payload(
            preterminal_record,
            terminal_artifacts=(
                RunArtifact(
                    artifact_id=provenance_artifact.artifact_id,
                    kind="run_provenance",
                    created_at=provenance_artifact.created_at,
                    payload={},
                ),
                RunArtifact(
                    artifact_id=completion_artifact.artifact_id,
                    kind="run_completed",
                    created_at=completion_artifact.created_at,
                    payload={},
                ),
            ),
            terminal_events=(
                RunEvent(
                    event_id=provenance_event.event_id,
                    name="run_provenance_captured",
                    created_at=provenance_event.created_at,
                    payload={},
                ),
                RunEvent(
                    event_id=completion_event.event_id,
                    name="run_completed",
                    created_at=completion_event.created_at,
                    payload={},
                ),
            ),
        )
        expected_patch_proposals = [
            EngineRunService._patch_proposal_summary(artifact)
            for artifact in preterminal_record.artifacts
            if artifact.kind == "patch_proposal"
        ]
        expected_patch_decisions = [
            EngineRunService._patch_decision_summary(preterminal_record, artifact)
            for artifact in preterminal_record.artifacts
            if artifact.kind == "patch_decision"
        ]
        expected_run_failure_artifacts = [
            EngineRunService._run_failure_summary(artifact)
            for artifact in preterminal_record.artifacts
            if artifact.kind == "run_failure"
        ]
        expected_export_preview_artifacts = [
            EngineRunService._export_preview_summary(artifact)
            for artifact in preterminal_record.artifacts
            if artifact.kind == "export_preview"
        ]
        expected_export_final_artifacts = [
            EngineRunService._export_final_summary(artifact)
            for artifact in preterminal_record.artifacts
            if artifact.kind == "export_final"
        ]
        expected_retrieval_evidence = EngineRunService._retrieval_evidence_payload(preterminal_record)
        expected_run_plan_digest = EngineRunService._run_plan_digest_payload(preterminal_record)
        if provenance_payload.get("run_id") != record.run_id:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance run_id")
        if provenance_payload.get("prior_status") != "running":
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance prior_status")
        if provenance_payload.get("status") != record.status:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance status")
        if provenance_payload.get("actual_terminal_status") != record.status:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance actual status")
        if provenance_payload.get("terminal_artifact_count") != len(record.artifacts):
            raise ValueError(f"run {record.run_id} has inconsistent terminal artifact count")
        if provenance_payload.get("terminal_event_count") != len(record.events):
            raise ValueError(f"run {record.run_id} has inconsistent terminal event count")
        if provenance_payload.get("artifact_count") != len(preterminal_artifacts):
            raise ValueError(f"run {record.run_id} has inconsistent provenance artifact count")
        if provenance_payload.get("event_count") != len(preterminal_events):
            raise ValueError(f"run {record.run_id} has inconsistent provenance event count")
        if provenance_payload.get("started_at") != record.started_at:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance started_at")
        if provenance_payload.get("snapshot_updated_at") != preterminal_updated_at:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance snapshot_updated_at")
        if provenance_payload.get("completed_at") != provenance_artifact.created_at:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance completed_at")
        if record.updated_at != completion_artifact.created_at:
            raise ValueError(f"run {record.run_id} has inconsistent terminal updated_at")
        if record.completed_at != completion_artifact.created_at:
            raise ValueError(f"run {record.run_id} has inconsistent terminal completed_at")
        if provenance_artifact.created_at != completion_artifact.created_at:
            raise ValueError(f"run {record.run_id} has inconsistent terminal capture timestamp")
        if provenance_event.created_at != completion_event.created_at:
            raise ValueError(f"run {record.run_id} has inconsistent terminal event timestamp")
        if provenance_payload.get("run_summary") != expected_summary:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance run_summary")
        if provenance_payload.get("run_plan_digest") != expected_run_plan_digest:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance run_plan_digest")
        if provenance_payload.get("retrieval_evidence") != expected_retrieval_evidence:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance retrieval_evidence")
        if provenance_payload.get("artifact_sequence") != expected_artifact_sequence:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance artifact_sequence")
        if provenance_payload.get("event_sequence") != expected_event_sequence:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance event_sequence")
        if provenance_payload.get("artifact_kinds") != expected_artifact_sequence:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance artifact_kinds")
        if provenance_payload.get("event_names") != expected_event_sequence:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance event_names")
        if provenance_payload.get("artifact_refs") != expected_artifact_refs:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance artifact_refs")
        if provenance_payload.get("event_refs") != expected_event_refs:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance event_refs")
        if provenance_payload.get("terminal_artifact_refs") != expected_terminal_artifact_refs:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance terminal_artifact_refs")
        if provenance_payload.get("terminal_event_refs") != expected_terminal_event_refs:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance terminal_event_refs")
        if provenance_payload.get("terminal_artifact_sequence") != ["run_provenance", "run_completed"]:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance terminal_artifact_sequence")
        if provenance_payload.get("terminal_event_sequence") != [
            "run_provenance_captured",
            "run_completed",
        ]:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance terminal_event_sequence")
        if provenance_payload.get("pending_patch_proposals") != expected_pending_patch_proposals:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance pending_patch_proposals")
        if provenance_payload.get("run_lifecycle") != expected_run_lifecycle:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance run_lifecycle")
        if provenance_payload.get("run_lifecycle_digest") != EngineRunService._fingerprint_payload(
            expected_run_lifecycle
        ):
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance run_lifecycle_digest")
        if provenance_payload.get("patch_proposals") != expected_patch_proposals:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance patch_proposals")
        if provenance_payload.get("patch_decisions") != expected_patch_decisions:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance patch_decisions")
        if provenance_payload.get("run_failure_artifacts") != expected_run_failure_artifacts:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance run_failure_artifacts")
        if provenance_payload.get("export_preview_artifacts") != expected_export_preview_artifacts:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance export_preview_artifacts")
        if provenance_payload.get("export_final_artifacts") != expected_export_final_artifacts:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance export_final_artifacts")
        flow_digest = provenance_payload.get("flow_digest")
        if flow_digest != EngineRunService._fingerprint_payload(
            {
                key: value
                for key, value in provenance_payload.items()
                if key != "flow_digest"
            }
        ):
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance flow_digest")
        if provenance_event_payload.get("artifact_id") != provenance_artifact.artifact_id:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance event artifact_id")
        if provenance_event_payload.get("planned_terminal_status") != provenance_payload.get("planned_terminal_status"):
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance event planned status")
        if provenance_event_payload.get("actual_terminal_status") != record.status:
            raise ValueError(f"run {record.run_id} has inconsistent terminal provenance event actual status")
        if completion_payload.get("status") != record.status:
            raise ValueError(f"run {record.run_id} has inconsistent completion status")
        if completion_payload.get("operation") != record.operation:
            raise ValueError(f"run {record.run_id} has inconsistent completion operation")
        if completion_payload.get("scope") != record.scope:
            raise ValueError(f"run {record.run_id} has inconsistent completion scope")
        if completion_payload.get("intent") != record.intent:
            raise ValueError(f"run {record.run_id} has inconsistent completion intent")
        if completion_payload.get("request_fingerprint") != record.request_fingerprint:
            raise ValueError(f"run {record.run_id} has inconsistent completion request_fingerprint")
        if completion_event_payload.get("artifact_id") != completion_artifact.artifact_id:
            raise ValueError(f"run {record.run_id} has inconsistent completion event artifact_id")
        if completion_event_payload.get("status") != record.status:
            raise ValueError(f"run {record.run_id} has inconsistent completion event status")

    @staticmethod
    def _validate_append_only_sequence(record: EngineRunRecord) -> None:
        for index, artifact in enumerate(record.artifacts, start=1):
            expected_prefix = f"{record.run_id}:{index:04d}:"
            if not artifact.artifact_id.startswith(expected_prefix):
                raise ValueError(
                    f"run {record.run_id} has inconsistent artifact sequence at position {index}: "
                    f"{artifact.artifact_id}"
                )
            expected_kind = artifact.artifact_id[len(expected_prefix) :]
            if expected_kind != artifact.kind:
                raise ValueError(
                    f"run {record.run_id} has inconsistent artifact kind at position {index}: "
                    f"{artifact.artifact_id}"
                )
        for index, event in enumerate(record.events, start=1):
            expected_prefix = f"{record.run_id}:{index:04d}:"
            if not event.event_id.startswith(expected_prefix):
                raise ValueError(
                    f"run {record.run_id} has inconsistent event sequence at position {index}: "
                    f"{event.event_id}"
                )
            expected_name = event.event_id[len(expected_prefix) :]
            if expected_name != event.name:
                raise ValueError(
                    f"run {record.run_id} has inconsistent event name at position {index}: "
                    f"{event.event_id}"
                )

    def _timestamp(self) -> str:
        instant = self._now_fn()
        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=UTC)
        else:
            instant = instant.astimezone(UTC)
        return instant.isoformat()

    @staticmethod
    def _fingerprint_text(value: str) -> str:
        import hashlib

        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    @staticmethod
    def _fingerprint_payload(payload: dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _fingerprint_plan_artifact(artifact: RunArtifact) -> str:
        payload = EngineRunService._clone_jsonable(artifact.payload)
        if isinstance(payload, dict):
            payload.pop("plan_digest", None)
        return EngineRunService._fingerprint_payload(payload)

    @staticmethod
    def _fingerprint_run_provenance(provenance: dict[str, Any]) -> str:
        payload = EngineRunService._clone_jsonable(provenance)
        if isinstance(payload, dict):
            payload.pop("flow_digest", None)
        return EngineRunService._fingerprint_payload(payload)

    @staticmethod
    def _clone_jsonable(value: Any) -> Any:
        return json.loads(json.dumps(value, sort_keys=True))

    @staticmethod
    def _synthesize_run_flow_manifest(
        *,
        run: EngineRunRecord,
        summary: RunSummary,
        run_plan_digest: str | None,
        flow_digest: str | None,
        run_lifecycle_digest: str | None,
        retrieval_evidence: dict[str, Any] | None,
        run_provenance: dict[str, Any] | None,
        artifact_sequence: list[str] | tuple[str, ...] | None,
        event_sequence: list[str] | tuple[str, ...] | None,
        flow_steps: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None,
        artifact_refs: dict[str, Any] | None,
        event_refs: dict[str, Any] | None,
        pending_patch_proposals: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None,
        terminal_artifact_sequence: list[str] | tuple[str, ...] | None,
        terminal_event_sequence: list[str] | tuple[str, ...] | None,
        terminal_artifact_refs: dict[str, Any] | None,
        terminal_event_refs: dict[str, Any] | None,
        terminal_artifacts: tuple[RunArtifact, RunArtifact] | None,
        terminal_events: tuple[RunEvent, RunEvent] | None,
        run_lifecycle: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "run": asdict(run),
            "summary": asdict(summary),
            "run_summary": asdict(summary),
            "run_plan_digest": run_plan_digest,
            "flow_digest": flow_digest,
            "run_lifecycle_digest": run_lifecycle_digest,
            "retrieval_evidence": (
                EngineRunService._clone_jsonable(retrieval_evidence) if retrieval_evidence is not None else None
            ),
            "run_provenance": (
                EngineRunService._clone_jsonable(run_provenance) if run_provenance is not None else None
            ),
            "artifact_sequence": list(artifact_sequence) if artifact_sequence is not None else None,
            "event_sequence": list(event_sequence) if event_sequence is not None else None,
            "flow_steps": [
                EngineRunService._clone_jsonable(item)
                for item in flow_steps
            ]
            if flow_steps is not None
            else None,
            "artifact_refs": (
                {name: list(values) for name, values in artifact_refs.items()}
                if artifact_refs is not None
                else None
            ),
            "event_refs": (
                {name: list(values) for name, values in event_refs.items()}
                if event_refs is not None
                else None
            ),
            "pending_patch_proposals": (
                [EngineRunService._clone_jsonable(item) for item in pending_patch_proposals]
                if pending_patch_proposals is not None
                else None
            ),
            "terminal_artifact_sequence": (
                list(terminal_artifact_sequence) if terminal_artifact_sequence is not None else None
            ),
            "terminal_event_sequence": (
                list(terminal_event_sequence) if terminal_event_sequence is not None else None
            ),
            "terminal_artifact_refs": (
                {name: list(values) for name, values in terminal_artifact_refs.items()}
                if terminal_artifact_refs is not None
                else None
            ),
            "terminal_event_refs": (
                {name: list(values) for name, values in terminal_event_refs.items()}
                if terminal_event_refs is not None
                else None
            ),
            "terminal_artifacts": (
                [asdict(item) for item in terminal_artifacts] if terminal_artifacts is not None else None
            ),
            "terminal_events": (
                [asdict(item) for item in terminal_events] if terminal_events is not None else None
            ),
            "run_lifecycle": EngineRunService._clone_jsonable(run_lifecycle),
        }

    @staticmethod
    def _normalize_plan_constraints(constraints: dict[str, object] | None) -> dict[str, object]:
        return EngineRunService._normalize_retrieval_constraints(constraints)

    @staticmethod
    def _normalize_destination_path(value: Path | str | PathLike[str], *, field_name: str) -> Path:
        if isinstance(value, Path):
            normalized = value
        elif isinstance(value, (str, PathLike)):
            raw_value = fspath(value)
            if not isinstance(raw_value, str):
                raise TypeError(f"{field_name} must be a string path-like value")
            stripped = raw_value.strip()
            if not stripped:
                raise ValueError(f"{field_name} is required")
            normalized = Path(stripped)
        else:
            raise TypeError(f"{field_name} must be a path-like value")
        if not str(normalized).strip():
            raise ValueError(f"{field_name} is required")
        return normalized
