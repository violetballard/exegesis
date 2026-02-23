from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal, Protocol

SectionType = Literal[
    "introduction",
    "literature_review",
    "methods",
    "findings",
    "discussion",
    "conclusion",
    "other",
]
OperationKind = Literal[
    "draft_from_outline",
    "expand_outline",
    "rewrite_section_from_outline",
    "synthesis_lookup_from_outline",
    "other",
]
BulkDraftTier = Literal["fast", "best"]
BulkDraftMode = Literal["normal", "drafting_mode"]
BulkDraftReason = Literal[
    "unsupported",
    "op_not_allowed",
    "section_type_discussion",
    "section_type_conclusion",
    "word_count_threshold_general",
    "word_count_threshold_methods_findings",
    "default_fast",
]

BEST_MODEL_ID = "gpt-oss-120b"
FAST_MODEL_ID = "magistral-small"
EDITOR_MODEL_ID = "mistral-small"
_BEST_ALLOWLIST: set[str] = {
    "draft_from_outline",
    "expand_outline",
    "rewrite_section_from_outline",
    "synthesis_lookup_from_outline",
}
_DRAFTING_MODE_DEFAULT_CTX = 12_000
_DRAFTING_MODE_MAX_CTX = 16_000


@dataclass(frozen=True)
class PackMetadata:
    memory_tier_gb: int
    installed_models: tuple[str, ...]

    def contains_model(self, model_id: str) -> bool:
        return model_id in set(self.installed_models)


class RuntimeSupport(Protocol):
    def supports_model(self, model_id: str) -> bool:
        ...


@dataclass(frozen=True)
class BulkDraftCapabilities:
    supports_best_bulk: bool
    supports_best_bulk_resident: bool
    supports_best_bulk_ondemand: bool


@dataclass(frozen=True)
class BulkDraftRoutingInput:
    section_type: SectionType
    target_word_count: int
    operation_kind: OperationKind
    capabilities: BulkDraftCapabilities


@dataclass(frozen=True)
class BulkDraftRoutingDecision:
    bulk_draft_tier: BulkDraftTier
    bulk_draft_reason: BulkDraftReason
    bulk_draft_mode: BulkDraftMode


@dataclass(frozen=True)
class BulkDraftRequest:
    outline_id: str
    section_id: str
    section_type: SectionType
    target_word_count: int
    operation_kind: OperationKind
    context_set_ids: tuple[str, ...]


@dataclass(frozen=True)
class DraftPassOutput:
    text: str
    evidence_refs: tuple[str, ...] = ()
    open_questions: tuple[str, ...] = ()


@dataclass(frozen=True)
class BulkRunContext:
    mode: BulkDraftMode
    max_ctx: int | None = None


@dataclass(frozen=True)
class BulkDraftRunResult:
    patch_proposal: str
    evidence_refs: tuple[str, ...]
    open_questions: tuple[str, ...]
    bulk_draft_tier: BulkDraftTier
    bulk_draft_reason: BulkDraftReason
    bulk_draft_mode: BulkDraftMode
    planner_outline_id: str
    target_word_count: int
    section_type: SectionType
    operation_kind: OperationKind
    model_id_bulk: str
    model_id_editor: str
    context_set_ids: tuple[str, ...]
    restore_success: bool | None


class ResidentModelManager(Protocol):
    def snapshot(self) -> str:
        ...

    def unload_all(self) -> None:
        ...

    def load_model(self, model_id: str, *, max_ctx: int | None = None) -> None:
        ...

    def restore(self, snapshot_id: str) -> bool:
        ...


BulkRunner = Callable[[BulkDraftRequest, BulkRunContext], DraftPassOutput]
EditorRunner = Callable[[BulkDraftRequest, DraftPassOutput], DraftPassOutput]


def compute_capabilities(pack: PackMetadata, runtime: RuntimeSupport) -> BulkDraftCapabilities:
    runtime_supports_best = runtime.supports_model(BEST_MODEL_ID)
    supports_best_bulk = pack.contains_model(BEST_MODEL_ID) and runtime_supports_best
    supports_best_bulk_resident = supports_best_bulk and pack.memory_tier_gb >= 256
    supports_best_bulk_ondemand = supports_best_bulk and pack.memory_tier_gb >= 128
    return BulkDraftCapabilities(
        supports_best_bulk=supports_best_bulk,
        supports_best_bulk_resident=supports_best_bulk_resident,
        supports_best_bulk_ondemand=supports_best_bulk_ondemand,
    )


def route_bulk_draft(payload: BulkDraftRoutingInput) -> BulkDraftRoutingDecision:
    caps = payload.capabilities
    if not caps.supports_best_bulk or not caps.supports_best_bulk_ondemand:
        return BulkDraftRoutingDecision("fast", "unsupported", "normal")

    if payload.operation_kind not in _BEST_ALLOWLIST:
        return BulkDraftRoutingDecision("fast", "op_not_allowed", "normal")

    if payload.section_type == "discussion":
        return _best_decision("section_type_discussion", caps)

    if payload.section_type == "conclusion":
        return _best_decision("section_type_conclusion", caps)

    if payload.section_type in {"methods", "findings"}:
        if payload.target_word_count >= 2500:
            return _best_decision("word_count_threshold_methods_findings", caps)
        return BulkDraftRoutingDecision("fast", "default_fast", "normal")

    if payload.target_word_count >= 1500:
        return _best_decision("word_count_threshold_general", caps)

    return BulkDraftRoutingDecision("fast", "default_fast", "normal")


def execute_bulk_draft(
    *,
    request: BulkDraftRequest,
    capabilities: BulkDraftCapabilities,
    resident_models: ResidentModelManager,
    run_fast: BulkRunner,
    run_best: BulkRunner,
    run_editor: EditorRunner,
) -> BulkDraftRunResult:
    if not request.outline_id:
        raise ValueError("outline_id is required for bulk drafting")

    decision = route_bulk_draft(
        BulkDraftRoutingInput(
            section_type=request.section_type,
            target_word_count=request.target_word_count,
            operation_kind=request.operation_kind,
            capabilities=capabilities,
        )
    )

    restore_success: bool | None = None
    if decision.bulk_draft_tier == "fast":
        bulk_out = run_fast(request, BulkRunContext(mode="normal"))
        edited = run_editor(request, bulk_out)
        return _to_result(request, decision, edited, FAST_MODEL_ID, restore_success)

    if decision.bulk_draft_mode == "drafting_mode":
        snapshot = resident_models.snapshot()
        resident_models.unload_all()
        resident_models.load_model(BEST_MODEL_ID, max_ctx=_DRAFTING_MODE_DEFAULT_CTX)
        bulk_out = run_best(
            request,
            BulkRunContext(mode="drafting_mode", max_ctx=_DRAFTING_MODE_MAX_CTX),
        )
        resident_models.unload_all()
        restore_success = resident_models.restore(snapshot)
    else:
        bulk_out = run_best(request, BulkRunContext(mode="normal"))

    edited = run_editor(request, bulk_out)
    return _to_result(request, decision, edited, BEST_MODEL_ID, restore_success)


def _best_decision(reason: BulkDraftReason, caps: BulkDraftCapabilities) -> BulkDraftRoutingDecision:
    mode: BulkDraftMode = "normal" if caps.supports_best_bulk_resident else "drafting_mode"
    return BulkDraftRoutingDecision("best", reason, mode)


def _to_result(
    request: BulkDraftRequest,
    decision: BulkDraftRoutingDecision,
    output: DraftPassOutput,
    bulk_model_id: str,
    restore_success: bool | None,
) -> BulkDraftRunResult:
    return BulkDraftRunResult(
        patch_proposal=output.text,
        evidence_refs=output.evidence_refs,
        open_questions=output.open_questions,
        bulk_draft_tier=decision.bulk_draft_tier,
        bulk_draft_reason=decision.bulk_draft_reason,
        bulk_draft_mode=decision.bulk_draft_mode,
        planner_outline_id=request.outline_id,
        target_word_count=request.target_word_count,
        section_type=request.section_type,
        operation_kind=request.operation_kind,
        model_id_bulk=bulk_model_id,
        model_id_editor=EDITOR_MODEL_ID,
        context_set_ids=request.context_set_ids,
        restore_success=restore_success,
    )
