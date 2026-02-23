from __future__ import annotations

import unittest

from src.qual.engine.bulk_draft import (
    BEST_MODEL_ID,
    BulkDraftRequest,
    BulkDraftRoutingInput,
    DraftPassOutput,
    PackMetadata,
    compute_supports_best_bulk,
    execute_bulk_draft,
    route_bulk_draft,
)


class BulkDraftRoutingTests(unittest.TestCase):
    def test_unsupported_tiers_always_fast(self) -> None:
        pack_128 = PackMetadata(memory_tier_gb=128, installed_models=(BEST_MODEL_ID,))
        self.assertFalse(compute_supports_best_bulk(pack_128))

        decision = route_bulk_draft(
            BulkDraftRoutingInput(
                section_type="discussion",
                target_word_count=4000,
                operation_kind="draft_from_outline",
                supports_best_bulk=False,
            )
        )
        self.assertEqual(decision.bulk_draft_tier, "fast")
        self.assertEqual(decision.bulk_draft_reason, "unsupported")

    def test_discussion_conclusion_best_when_supported(self) -> None:
        discussion = route_bulk_draft(
            BulkDraftRoutingInput(
                section_type="discussion",
                target_word_count=100,
                operation_kind="draft_from_outline",
                supports_best_bulk=True,
            )
        )
        conclusion = route_bulk_draft(
            BulkDraftRoutingInput(
                section_type="conclusion",
                target_word_count=100,
                operation_kind="draft_from_outline",
                supports_best_bulk=True,
            )
        )
        self.assertEqual(discussion.bulk_draft_reason, "section_type_discussion")
        self.assertEqual(conclusion.bulk_draft_reason, "section_type_conclusion")

    def test_methods_findings_threshold_2500(self) -> None:
        below = route_bulk_draft(
            BulkDraftRoutingInput(
                section_type="methods",
                target_word_count=2499,
                operation_kind="draft_from_outline",
                supports_best_bulk=True,
            )
        )
        at = route_bulk_draft(
            BulkDraftRoutingInput(
                section_type="findings",
                target_word_count=2500,
                operation_kind="draft_from_outline",
                supports_best_bulk=True,
            )
        )
        self.assertEqual(below.bulk_draft_tier, "fast")
        self.assertEqual(at.bulk_draft_tier, "best")
        self.assertEqual(at.bulk_draft_reason, "word_count_threshold_methods_findings")

    def test_general_threshold_1500(self) -> None:
        below = route_bulk_draft(
            BulkDraftRoutingInput(
                section_type="introduction",
                target_word_count=1499,
                operation_kind="draft_from_outline",
                supports_best_bulk=True,
            )
        )
        at = route_bulk_draft(
            BulkDraftRoutingInput(
                section_type="other",
                target_word_count=1500,
                operation_kind="draft_from_outline",
                supports_best_bulk=True,
            )
        )
        self.assertEqual(below.bulk_draft_tier, "fast")
        self.assertEqual(at.bulk_draft_tier, "best")
        self.assertEqual(at.bulk_draft_reason, "word_count_threshold_general")

    def test_op_not_allowed_forces_fast(self) -> None:
        decision = route_bulk_draft(
            BulkDraftRoutingInput(
                section_type="discussion",
                target_word_count=5000,
                operation_kind="other",
                supports_best_bulk=True,
            )
        )
        self.assertEqual(decision.bulk_draft_tier, "fast")
        self.assertEqual(decision.bulk_draft_reason, "op_not_allowed")

    def test_bulk_drafting_requires_outline_id(self) -> None:
        with self.assertRaises(ValueError):
            execute_bulk_draft(
                request=_request(outline_id=""),
                supports_best_bulk=True,
                run_fast=lambda _: DraftPassOutput("fast"),
                run_best=lambda _: DraftPassOutput("best"),
                run_editor=lambda _, out: out,
            )

    def test_best_model_never_used_outside_allowlist(self) -> None:
        best_calls: list[str] = []

        result = execute_bulk_draft(
            request=_request(operation_kind="other", section_type="discussion", target_word_count=4000),
            supports_best_bulk=True,
            run_fast=lambda _: DraftPassOutput("fast draft"),
            run_best=lambda _: _record_best(best_calls),
            run_editor=lambda _, out: out,
        )

        self.assertEqual(best_calls, [])
        self.assertEqual(result.bulk_draft_tier, "fast")

    def test_editor_pass_always_executes(self) -> None:
        editor_calls: list[str] = []

        def run_editor(_: BulkDraftRequest, output: DraftPassOutput) -> DraftPassOutput:
            editor_calls.append(output.text)
            return DraftPassOutput(output.text + " edited")

        result = execute_bulk_draft(
            request=_request(section_type="discussion", target_word_count=3000),
            supports_best_bulk=True,
            run_fast=lambda _: DraftPassOutput("fast draft"),
            run_best=lambda _: DraftPassOutput("best draft"),
            run_editor=run_editor,
        )

        self.assertEqual(editor_calls, ["best draft"])
        self.assertEqual(result.patch_proposal, "best draft edited")

    def test_agentrun_persists_tier_reason_and_ids(self) -> None:
        result = execute_bulk_draft(
            request=_request(section_type="methods", target_word_count=2500),
            supports_best_bulk=True,
            run_fast=lambda _: DraftPassOutput("fast draft"),
            run_best=lambda _: DraftPassOutput("best draft"),
            run_editor=lambda _, out: out,
        )

        self.assertEqual(result.bulk_draft_tier, "best")
        self.assertEqual(result.bulk_draft_reason, "word_count_threshold_methods_findings")
        self.assertEqual(result.planner_outline_id, "outline-1")
        self.assertEqual(result.model_id_bulk, "gpt-oss-120b")
        self.assertEqual(result.model_id_editor, "mistral-small")
        self.assertEqual(result.context_set_ids, ("ctx-1",))


def _record_best(calls: list[str]) -> DraftPassOutput:
    calls.append("best")
    return DraftPassOutput("best")


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
