from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

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


@dataclass(frozen=True)
class PackMetadata:
    memory_tier_gb: int
    installed_models: tuple[str, ...]

    def contains_model(self, model_id: str) -> bool:
        return model_id in set(self.installed_models)


@dataclass(frozen=True)
class BulkDraftRoutingInput:
    section_type: SectionType
    target_word_count: int
    operation_kind: OperationKind
    supports_best_bulk: bool


@dataclass(frozen=True)
class BulkDraftRoutingDecision:
    bulk_draft_tier: BulkDraftTier
    bulk_draft_reason: BulkDraftReason


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
class BulkDraftRunResult:
    patch_proposal: str
    evidence_refs: tuple[str, ...]
    open_questions: tuple[str, ...]
    bulk_draft_tier: BulkDraftTier
    bulk_draft_reason: BulkDraftReason
    planner_outline_id: str
    target_word_count: int
    section_type: SectionType
    operation_kind: OperationKind
    model_id_bulk: str
    model_id_editor: str
    context_set_ids: tuple[str, ...]


BulkRunner = Callable[[BulkDraftRequest], DraftPassOutput]
EditorRunner = Callable[[BulkDraftRequest, DraftPassOutput], DraftPassOutput]


def compute_supports_best_bulk(pack: PackMetadata) -> bool:
    return pack.contains_model(BEST_MODEL_ID) and pack.memory_tier_gb >= 256


def route_bulk_draft(payload: BulkDraftRoutingInput) -> BulkDraftRoutingDecision:
    if not payload.supports_best_bulk:
        return BulkDraftRoutingDecision("fast", "unsupported")

    if payload.operation_kind not in _BEST_ALLOWLIST:
        return BulkDraftRoutingDecision("fast", "op_not_allowed")

    if payload.section_type == "discussion":
        return BulkDraftRoutingDecision("best", "section_type_discussion")

    if payload.section_type == "conclusion":
        return BulkDraftRoutingDecision("best", "section_type_conclusion")

    if payload.section_type in {"methods", "findings"}:
        if payload.target_word_count >= 2500:
            return BulkDraftRoutingDecision("best", "word_count_threshold_methods_findings")
        return BulkDraftRoutingDecision("fast", "default_fast")

    if payload.target_word_count >= 1500:
        return BulkDraftRoutingDecision("best", "word_count_threshold_general")
    return BulkDraftRoutingDecision("fast", "default_fast")


def execute_bulk_draft(
    *,
    request: BulkDraftRequest,
    supports_best_bulk: bool,
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
            supports_best_bulk=supports_best_bulk,
        )
    )

    if decision.bulk_draft_tier == "best":
        bulk_out = run_best(request)
        bulk_model_id = BEST_MODEL_ID
    else:
        bulk_out = run_fast(request)
        bulk_model_id = FAST_MODEL_ID

    edited = run_editor(request, bulk_out)

    return BulkDraftRunResult(
        patch_proposal=edited.text,
        evidence_refs=edited.evidence_refs,
        open_questions=edited.open_questions,
        bulk_draft_tier=decision.bulk_draft_tier,
        bulk_draft_reason=decision.bulk_draft_reason,
        planner_outline_id=request.outline_id,
        target_word_count=request.target_word_count,
        section_type=request.section_type,
        operation_kind=request.operation_kind,
        model_id_bulk=bulk_model_id,
        model_id_editor=EDITOR_MODEL_ID,
        context_set_ids=request.context_set_ids,
    )
