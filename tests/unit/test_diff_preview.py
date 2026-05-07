from __future__ import annotations

import os
import unittest
from contextlib import contextmanager

from src.qual.commands.diff_preview import (
    INCLUDE_SUMMARY_ENV,
    MAX_DIFF_OUTPUT_CHARS_ENV,
    SUMMARY_ONLY_ENV,
    SUPPRESS_FILE_HEADERS_ENV,
    DiffPreviewInput,
    PatchReviewDecision,
    PatchReviewActionRouteValidation,
    build_diff_preview_result,
    build_patch_review_decision,
    build_patch_review_command_contract,
    run_diff_preview,
    run_patch_review_decision,
    run_patch_review_action_route_validation,
    validate_patch_review_action_routes,
    validate_patch_review_command_contract,
)


@contextmanager
def _env(**updates: str | None):
    saved: dict[str, str | None] = {key: os.environ.get(key) for key in updates}
    try:
        for key, value in updates.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


class DiffPreviewBehaviorTests(unittest.TestCase):
    def test_default_output_unchanged_when_env_unset(self) -> None:
        with _env(
            **{
                INCLUDE_SUMMARY_ENV: None,
                SUMMARY_ONLY_ENV: None,
                SUPPRESS_FILE_HEADERS_ENV: None,
                MAX_DIFF_OUTPUT_CHARS_ENV: None,
            }
        ):
            output = run_diff_preview(DiffPreviewInput("a\n", "b\n"))
        self.assertTrue(output.startswith("--- original\n+++ proposed\n"))
        self.assertNotIn("Diff summary:", output)

    def test_summary_counts_and_hunks_are_correct(self) -> None:
        with _env(**{INCLUDE_SUMMARY_ENV: "1", SUMMARY_ONLY_ENV: None}):
            output = run_diff_preview(DiffPreviewInput("a\nold\n", "a\nnew1\nnew2\n"))
        self.assertTrue(output.rstrip().endswith("Diff summary: +2 -1 (hunks: 1)"))

    def test_summary_only_takes_precedence(self) -> None:
        with _env(
            **{
                SUMMARY_ONLY_ENV: "true",
                INCLUDE_SUMMARY_ENV: "1",
                MAX_DIFF_OUTPUT_CHARS_ENV: "40",
            }
        ):
            output = run_diff_preview(
                DiffPreviewInput(
                    "\n".join(f"a{i}" for i in range(500)) + "\n",
                    "\n".join(f"b{i}" for i in range(500)) + "\n",
                )
            )
        self.assertTrue(output.startswith("Diff summary: +"))
        self.assertNotIn("diff truncated", output)

    def test_header_suppression_keeps_counts_stable(self) -> None:
        base = DiffPreviewInput("a\nold\n", "a\nnew1\nnew2\n")
        with _env(**{INCLUDE_SUMMARY_ENV: "1", SUPPRESS_FILE_HEADERS_ENV: "0"}):
            output_headers = run_diff_preview(base)
        with _env(**{INCLUDE_SUMMARY_ENV: "1", SUPPRESS_FILE_HEADERS_ENV: "yes"}):
            output_suppressed = run_diff_preview(base)
        self.assertTrue(output_headers.startswith("--- original\n+++ proposed\n"))
        self.assertFalse(output_suppressed.startswith("--- original\n+++ proposed\n"))
        self.assertEqual(output_headers.splitlines()[-1], output_suppressed.splitlines()[-1])

    def test_summary_only_does_not_override_no_diff_messages(self) -> None:
        with _env(**{SUMMARY_ONLY_ENV: "1"}):
            both_empty = run_diff_preview(DiffPreviewInput("", ""))
            identical = run_diff_preview(DiffPreviewInput("same\n", "same\n"))
        self.assertEqual(both_empty, "No diff: both inputs are empty.")
        self.assertEqual(identical, "No diff: inputs are identical after normalization.")


class PatchReviewDecisionTests(unittest.TestCase):
    """Validate the patch-review decision flow for the Milestone 3 demo loop.

    These tests ensure the patch review command surface correctly drives the
    apply/reject decision that the engine loop requires.
    """

    def test_changes_detected_yields_apply_reject_actions(self) -> None:
        decision = build_patch_review_decision(
            DiffPreviewInput("original line\n", "revised line\n")
        )
        self.assertEqual(decision.status, "changes-detected")
        self.assertEqual(decision.next_actions, ("apply", "reject"))
        self.assertTrue(decision.has_changes)
        self.assertFalse(decision.normalized_equal)

    def test_identical_inputs_yield_no_op(self) -> None:
        decision = build_patch_review_decision(
            DiffPreviewInput("same content\n", "same content\n")
        )
        self.assertEqual(decision.status, "no-op")
        self.assertEqual(decision.next_actions, ("continue",))
        self.assertFalse(decision.has_changes)
        self.assertTrue(decision.normalized_equal)

    def test_empty_inputs_yield_no_op(self) -> None:
        decision = build_patch_review_decision(DiffPreviewInput("", ""))
        self.assertEqual(decision.status, "no-op")
        self.assertEqual(decision.next_actions, ("continue",))
        self.assertFalse(decision.has_changes)
        self.assertTrue(decision.normalized_equal)

    def test_run_patch_review_decision_output_format(self) -> None:
        output = run_patch_review_decision(
            DiffPreviewInput("original\n", "revised\n")
        )
        self.assertIn("patch-review: changes-detected", output)
        self.assertIn("next-actions=apply,reject", output)
        self.assertIn("truncated=", output)

    def test_run_patch_review_decision_no_op_format(self) -> None:
        output = run_patch_review_decision(
            DiffPreviewInput("same\n", "same\n")
        )
        self.assertIn("patch-review: no-op", output)
        self.assertIn("next-actions=continue", output)

    def test_decision_truncated_flag_reflects_diff_result(self) -> None:
        decision = build_patch_review_decision(
            DiffPreviewInput("a\n", "b\n")
        )
        self.assertFalse(decision.truncated)

    def test_decision_summary_matches_diff_summary(self) -> None:
        result = build_diff_preview_result(
            DiffPreviewInput("a\nold\n", "a\nnew\n")
        )
        decision = build_patch_review_decision(
            DiffPreviewInput("a\nold\n", "a\nnew\n")
        )
        self.assertEqual(result.summary, decision.summary)

    def test_decision_is_frozen_dataclass(self) -> None:
        decision = build_patch_review_decision(
            DiffPreviewInput("a\n", "b\n")
        )
        self.assertIsInstance(decision, PatchReviewDecision)
        with self.assertRaises(Exception):
            decision.status = "modified"  # type: ignore[attr-defined]


class PatchReviewActionRouteValidationTests(unittest.TestCase):
    """Validate that patch review action routes are anchored to the demo path.

    These tests ensure the command surface cannot drift from the canonical
    engine actions defined in the command catalog.
    """

    def test_contract_validation_is_valid(self) -> None:
        validation = validate_patch_review_command_contract()
        self.assertIsInstance(validation, PatchReviewActionRouteValidation)
        self.assertTrue(
            validation.is_valid,
            f"All engine actions should be in the demo path; missing: {validation.missing_engine_actions}",
        )
        self.assertEqual(validation.missing_engine_actions, ())

    def test_contract_validation_covers_all_patch_review_actions(self) -> None:
        validation = validate_patch_review_command_contract()
        # The contract should cover all 4 patch-review engine actions.
        expected_actions = {
            "ExegesisAppService.revise_selection",
            "ExegesisAppService.apply_patch",
            "ExegesisAppService.reject_patch",
            "ExegesisAppService.save_document",
        }
        self.assertEqual(
            set(validation.engine_actions),
            expected_actions,
            "Contract should cover all patch-review engine actions",
        )

    def test_contract_validation_extra_actions_are_non_patch_review(self) -> None:
        validation = validate_patch_review_command_contract()
        # Extra actions are demo-path actions not in the patch-review contract.
        # These should be the non-patch-review engine actions.
        patch_review_actions = {
            "ExegesisAppService.revise_selection",
            "ExegesisAppService.apply_patch",
            "ExegesisAppService.reject_patch",
            "ExegesisAppService.save_document",
        }
        for extra in validation.extra_engine_actions:
            self.assertNotIn(
                extra,
                patch_review_actions,
                f"{extra} should not appear as extra if it is a patch-review action",
            )

    def test_route_validation_rejects_unknown_engine_action(self) -> None:
        invalid_routes = (
            ("apply", "ExegesisAppService.apply_patch"),
            ("unknown", "ExegesisAppService.nonexistent_action"),
        )
        validation = validate_patch_review_action_routes(invalid_routes)
        self.assertFalse(validation.is_valid)
        self.assertEqual(
            validation.missing_engine_actions,
            ("ExegesisAppService.nonexistent_action",),
        )
        self.assertEqual(
            validation.valid_engine_actions,
            ("ExegesisAppService.apply_patch",),
        )

    def test_route_validation_accepts_all_known_actions(self) -> None:
        contract = build_patch_review_command_contract()
        all_routes = contract.change_action_routes + contract.no_change_action_routes
        validation = validate_patch_review_action_routes(all_routes)
        self.assertTrue(validation.is_valid)
        self.assertEqual(validation.missing_engine_actions, ())

    def test_run_validation_output_format(self) -> None:
        output = run_patch_review_action_route_validation()
        self.assertIn("patch-review-route-validation:", output)
        self.assertIn("is_valid=true", output)
        self.assertIn("engine_actions=", output)
        self.assertIn("valid=", output)

    def test_validation_validation_is_frozen_dataclass(self) -> None:
        validation = validate_patch_review_command_contract()
        self.assertIsInstance(validation, PatchReviewActionRouteValidation)
        with self.assertRaises(Exception):
            validation.is_valid = False  # type: ignore[attr-defined]


if __name__ == "__main__":
    unittest.main()
