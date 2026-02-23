from __future__ import annotations

import unittest
from dataclasses import dataclass, field

from src.qual.engine.bulk_draft import (
    BEST_MODEL_ID,
    BulkDraftCapabilities,
    BulkDraftRequest,
    BulkDraftRoutingInput,
    BulkRunContext,
    DraftPassOutput,
    PackMetadata,
    compute_capabilities,
    execute_bulk_draft,
    route_bulk_draft,
)


@dataclass
class _RuntimeStub:
    supported: set[str]

    def supports_model(self, model_id: str) -> bool:
        return model_id in self.supported


@dataclass
class _ResidentStub:
    events: list[str] = field(default_factory=list)

    def snapshot(self) -> str:
        self.events.append("snapshot")
        return "snap-1"

    def unload_all(self) -> None:
        self.events.append("unload_all")

    def load_model(self, model_id: str, *, max_ctx: int | None = None) -> None:
        self.events.append(f"load:{model_id}:{max_ctx}")

    def restore(self, snapshot_id: str) -> bool:
        self.events.append(f"restore:{snapshot_id}")
        return True


class BulkDraftRoutingTests(unittest.TestCase):
    def test_128gb_pack_with_model_supports_ondemand_not_resident(self) -> None:
        pack = PackMetadata(memory_tier_gb=128, installed_models=(BEST_MODEL_ID,))
        caps = compute_capabilities(pack, _RuntimeStub({BEST_MODEL_ID}))
        self.assertTrue(caps.supports_best_bulk)
        self.assertFalse(caps.supports_best_bulk_resident)
        self.assertTrue(caps.supports_best_bulk_ondemand)

    def test_256gb_pack_supports_resident(self) -> None:
        pack = PackMetadata(memory_tier_gb=256, installed_models=(BEST_MODEL_ID,))
        caps = compute_capabilities(pack, _RuntimeStub({BEST_MODEL_ID}))
        self.assertTrue(caps.supports_best_bulk_resident)

    def test_discussion_conclusion_select_best_when_supported(self) -> None:
        caps = BulkDraftCapabilities(True, False, True)
        discussion = route_bulk_draft(
            _payload(section_type="discussion", target_word_count=1, capabilities=caps)
        )
        conclusion = route_bulk_draft(
            _payload(section_type="conclusion", target_word_count=1, capabilities=caps)
        )
        self.assertEqual(discussion.bulk_draft_tier, "best")
        self.assertEqual(discussion.bulk_draft_reason, "section_type_discussion")
        self.assertEqual(conclusion.bulk_draft_tier, "best")
        self.assertEqual(conclusion.bulk_draft_reason, "section_type_conclusion")

    def test_thresholds_methods_findings_2500_general_1500(self) -> None:
        caps = BulkDraftCapabilities(True, False, True)
        methods_below = route_bulk_draft(
            _payload(section_type="methods", target_word_count=2499, capabilities=caps)
        )
        methods_at = route_bulk_draft(
            _payload(section_type="methods", target_word_count=2500, capabilities=caps)
        )
        intro_below = route_bulk_draft(
            _payload(section_type="introduction", target_word_count=1499, capabilities=caps)
        )
        intro_at = route_bulk_draft(
            _payload(section_type="introduction", target_word_count=1500, capabilities=caps)
        )
        self.assertEqual(methods_below.bulk_draft_tier, "fast")
        self.assertEqual(methods_at.bulk_draft_tier, "best")
        self.assertEqual(intro_below.bulk_draft_tier, "fast")
        self.assertEqual(intro_at.bulk_draft_tier, "best")

    def test_op_not_allowed_forces_fast(self) -> None:
        caps = BulkDraftCapabilities(True, True, True)
        decision = route_bulk_draft(
            _payload(
                section_type="discussion",
                target_word_count=4000,
                operation_kind="other",
                capabilities=caps,
            )
        )
        self.assertEqual(decision.bulk_draft_tier, "fast")
        self.assertEqual(decision.bulk_draft_reason, "op_not_allowed")

    def test_best_on_128_triggers_drafting_mode_cycle(self) -> None:
        resident = _ResidentStub()
        fast_calls: list[str] = []
        best_calls: list[BulkRunContext] = []
        editor_calls: list[str] = []

        def run_fast(_: BulkDraftRequest, __: BulkRunContext) -> DraftPassOutput:
            fast_calls.append("fast")
            return DraftPassOutput("fast")

        def run_best(_: BulkDraftRequest, ctx: BulkRunContext) -> DraftPassOutput:
            best_calls.append(ctx)
            return DraftPassOutput("best draft")

        def run_editor(_: BulkDraftRequest, output: DraftPassOutput) -> DraftPassOutput:
            editor_calls.append("editor")
            return DraftPassOutput(output.text + " | edited")

        result = execute_bulk_draft(
            request=_request(section_type="discussion", target_word_count=3000),
            capabilities=BulkDraftCapabilities(True, False, True),
            resident_models=resident,
            run_fast=run_fast,
            run_best=run_best,
            run_editor=run_editor,
        )

        self.assertEqual(fast_calls, [])
        self.assertEqual(len(best_calls), 1)
        self.assertEqual(best_calls[0].mode, "drafting_mode")
        self.assertEqual(best_calls[0].max_ctx, 16_000)
        self.assertEqual(editor_calls, ["editor"])
        self.assertEqual(result.bulk_draft_mode, "drafting_mode")
        self.assertEqual(
            resident.events,
            [
                "snapshot",
                "unload_all",
                "load:gpt-oss-120b:12000",
                "unload_all",
                "restore:snap-1",
            ],
        )

    def test_bulk_drafting_requires_outline_id(self) -> None:
        with self.assertRaises(ValueError):
            execute_bulk_draft(
                request=_request(outline_id=""),
                capabilities=BulkDraftCapabilities(True, True, True),
                resident_models=_ResidentStub(),
                run_fast=lambda *_: DraftPassOutput("x"),
                run_best=lambda *_: DraftPassOutput("x"),
                run_editor=lambda _, out: out,
            )

    def test_editor_pass_always_executes(self) -> None:
        editor_calls: list[str] = []

        def run_editor(_: BulkDraftRequest, output: DraftPassOutput) -> DraftPassOutput:
            editor_calls.append(output.text)
            return DraftPassOutput(output.text + " edited")

        result = execute_bulk_draft(
            request=_request(section_type="methods", target_word_count=100),
            capabilities=BulkDraftCapabilities(True, True, True),
            resident_models=_ResidentStub(),
            run_fast=lambda *_: DraftPassOutput("fast draft"),
            run_best=lambda *_: DraftPassOutput("best draft"),
            run_editor=run_editor,
        )

        self.assertEqual(result.bulk_draft_tier, "fast")
        self.assertEqual(editor_calls, ["fast draft"])

    def test_best_model_never_used_outside_allowlist(self) -> None:
        best_calls: list[str] = []

        result = execute_bulk_draft(
            request=_request(operation_kind="other", section_type="discussion", target_word_count=5000),
            capabilities=BulkDraftCapabilities(True, True, True),
            resident_models=_ResidentStub(),
            run_fast=lambda *_: DraftPassOutput("fast"),
            run_best=lambda *_: _capture_best(best_calls),
            run_editor=lambda _, out: out,
        )

        self.assertEqual(result.bulk_draft_tier, "fast")
        self.assertEqual(best_calls, [])


def _capture_best(calls: list[str]) -> DraftPassOutput:
    calls.append("best")
    return DraftPassOutput("best")


def _payload(
    *,
    section_type: str = "other",
    target_word_count: int = 1,
    operation_kind: str = "draft_from_outline",
    capabilities: BulkDraftCapabilities,
):
    return BulkDraftRoutingInput(
        section_type=section_type,  # type: ignore[arg-type]
        target_word_count=target_word_count,
        operation_kind=operation_kind,  # type: ignore[arg-type]
        capabilities=capabilities,
    )


def _request(
    *,
    outline_id: str = "outline-1",
    section_id: str = "sec-1",
    section_type: str = "other",
    target_word_count: int = 1,
    operation_kind: str = "draft_from_outline",
) -> BulkDraftRequest:
    return BulkDraftRequest(
        outline_id=outline_id,
        section_id=section_id,
        section_type=section_type,  # type: ignore[arg-type]
        target_word_count=target_word_count,
        operation_kind=operation_kind,  # type: ignore[arg-type]
        context_set_ids=("ctx-1",),
    )


if __name__ == "__main__":
    unittest.main()
