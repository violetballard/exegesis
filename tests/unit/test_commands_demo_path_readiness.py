from __future__ import annotations

import unittest
from unittest.mock import patch

import src.qual.commands.catalog as command_catalog
from src.qual.commands import (
    command_demo_path_command_lookup_table,
    command_demo_path_compatibility_lookup_table,
    command_demo_path_handoff_evidence,
    command_demo_path_handoff_summary,
    command_demo_path_readiness,
    command_mvp_demo_path_compatibility_lookup_table,
    command_mvp_demo_path_handoff_evidence,
    command_patch_review_outcome_contract,
)


class CommandDemoPathReadinessTests(unittest.TestCase):
    def test_readiness_requires_the_actual_canonical_demo_path(self) -> None:
        readiness = command_demo_path_readiness(program="qual-bootstrap")

        self.assertFalse(readiness.ready)
        self.assertEqual(
            readiness.missing_demo_steps,
            (
                "produce-plan-or-revision",
                "preview-and-apply-or-reject-patch",
                "persist-updated-document-session-state",
                "continue-without-losing-context",
            ),
        )
        self.assertEqual(
            readiness.command_lookup_table,
            (
                (("qual-bootstrap", "bootstrap"), "open-project-document"),
                (("qual-bootstrap", "context-basket", "list"), "retrieve-relevant-material"),
                (("qual-bootstrap", "diff-preview"), "preview-patch"),
                (("qual-bootstrap", "terminal"), "export-handoff"),
            ),
        )
        self.assertEqual(
            readiness.demo_steps,
            (
                "open-project-document",
                "retrieve-relevant-material",
                "preview-patch",
                "export-handoff",
            ),
        )
        self.assertEqual(
            tuple(
                (
                    blocker.demo_step,
                    blocker.blocker_type,
                    blocker.partial_command,
                    blocker.reason,
                )
                for blocker in readiness.canonical_step_blockers
            ),
            (
                (
                    "produce-plan-or-revision",
                    "missing-command",
                    "",
                    "no stable command route produces a plan or revision through the engine loop",
                ),
                (
                    "preview-and-apply-or-reject-patch",
                    "partial-command",
                    "qual-bootstrap diff-preview",
                    "the current patch-review route previews diffs but does not apply or reject patches",
                ),
                (
                    "persist-updated-document-session-state",
                    "missing-command",
                    "",
                    "no stable command route persists the updated document and session state",
                ),
                (
                    "continue-without-losing-context",
                    "missing-command",
                    "",
                    "no stable command route resumes the workflow without losing context",
                ),
            ),
        )

    def test_readiness_flags_partial_demo_paths(self) -> None:
        readiness = command_demo_path_readiness(
            program="qual-bootstrap",
            flow_steps=("project-open", "retrieval", "patch-review"),
        )

        self.assertFalse(readiness.ready)
        self.assertEqual(
            readiness.missing_demo_steps,
            (
                "produce-plan-or-revision",
                "preview-and-apply-or-reject-patch",
                "persist-updated-document-session-state",
                "continue-without-losing-context",
            ),
        )
        self.assertEqual(readiness.demo_steps[-1], "preview-patch")

    def test_command_lookup_table_maps_smoke_commands_to_demo_steps(self) -> None:
        self.assertEqual(
            command_demo_path_command_lookup_table(program="qual-bootstrap"),
            (
                (("qual-bootstrap", "bootstrap"), "open-project-document"),
                (("qual-bootstrap", "context-basket", "list"), "retrieve-relevant-material"),
                (("qual-bootstrap", "diff-preview"), "preview-patch"),
                (("qual-bootstrap", "terminal"), "export-handoff"),
            ),
        )

    def test_handoff_summary_exposes_stable_smoke_command_lines(self) -> None:
        summary = command_demo_path_handoff_summary(program="qual-bootstrap")

        self.assertFalse(summary.ready)
        self.assertEqual(summary.command_count, 4)
        self.assertEqual(
            summary.command_lines,
            (
                "qual-bootstrap bootstrap",
                "qual-bootstrap context-basket list",
                "qual-bootstrap diff-preview",
                "qual-bootstrap terminal",
            ),
        )
        self.assertEqual(
            summary.compatibility_command_lines,
            (
                "qual-bootstrap bootstrap",
                "qual-bootstrap open",
                "qual-bootstrap project-open",
                "qual-bootstrap project",
                "qual-bootstrap context-basket list",
                "qual-bootstrap context list",
                "qual-bootstrap basket list",
                "qual-bootstrap retrieval list",
                "qual-bootstrap diff-preview",
                "qual-bootstrap diff",
                "qual-bootstrap patch-review",
                "qual-bootstrap terminal",
                "qual-bootstrap export-handoff",
            ),
        )
        self.assertEqual(
            summary.compatibility_normalized_command_lines,
            (
                "qual-bootstrap bootstrap",
                "qual-bootstrap bootstrap",
                "qual-bootstrap bootstrap",
                "qual-bootstrap bootstrap",
                "qual-bootstrap context-basket list",
                "qual-bootstrap context-basket list",
                "qual-bootstrap context-basket list",
                "qual-bootstrap context-basket list",
                "qual-bootstrap diff-preview",
                "qual-bootstrap diff-preview",
                "qual-bootstrap diff-preview",
                "qual-bootstrap terminal",
                "qual-bootstrap terminal",
            ),
        )
        self.assertEqual(
            summary.flow_step_commands,
            (
                ("project-open", "qual-bootstrap bootstrap"),
                ("retrieval", "qual-bootstrap context-basket list"),
                ("patch-review", "qual-bootstrap diff-preview"),
                ("export-handoff", "qual-bootstrap terminal"),
            ),
        )
        self.assertEqual(
            summary.demo_step_commands,
            (
                ("open-project-document", "qual-bootstrap bootstrap"),
                ("retrieve-relevant-material", "qual-bootstrap context-basket list"),
                ("preview-patch", "qual-bootstrap diff-preview"),
                ("export-handoff", "qual-bootstrap terminal"),
            ),
        )
        self.assertEqual(
            summary.supplemental_canonical_step_commands,
            (("promote-or-gather-context-into-basket", "qual-bootstrap context-basket add demo-context-item"),),
        )
        self.assertIn(
            ("promote-or-gather-context-into-basket", "qual-bootstrap context-basket add demo-context-item"),
            summary.covered_canonical_step_commands,
        )

    def test_handoff_summary_orders_covered_commands_by_canonical_demo_path(self) -> None:
        command_catalog.command_flow_route_catalog.cache_clear()
        command_catalog.command_cli_smoke_steps.cache_clear()
        command_catalog.command_cli_smoke_plan.cache_clear()
        with patch.object(
            command_catalog,
            "DEMO_PATH_STEPS_BY_FLOW_STEP",
            (
                ("project-open", "open-project-document"),
                ("retrieval", "retrieve-relevant-material"),
                ("patch-review", "preview-patch"),
                ("export-handoff", "continue-without-losing-context"),
            ),
        ):
            summary = command_demo_path_handoff_summary(program="qual-bootstrap")
        command_catalog.command_flow_route_catalog.cache_clear()
        command_catalog.command_cli_smoke_steps.cache_clear()
        command_catalog.command_cli_smoke_plan.cache_clear()

        self.assertEqual(
            summary.covered_canonical_step_commands,
            (
                ("open-project-document", "qual-bootstrap bootstrap"),
                ("retrieve-relevant-material", "qual-bootstrap context-basket list"),
                ("promote-or-gather-context-into-basket", "qual-bootstrap context-basket add demo-context-item"),
                ("continue-without-losing-context", "qual-bootstrap terminal"),
            ),
        )

    def test_handoff_summary_carries_missing_demo_steps_for_partial_paths(self) -> None:
        summary = command_demo_path_handoff_summary(
            program="qual-bootstrap",
            flow_steps=("project-open", "retrieval", "patch-review"),
        )

        self.assertFalse(summary.ready)
        self.assertEqual(
            summary.missing_demo_steps,
            (
                "produce-plan-or-revision",
                "preview-and-apply-or-reject-patch",
                "persist-updated-document-session-state",
                "continue-without-losing-context",
            ),
        )
        self.assertEqual(summary.command_lines[-1], "qual-bootstrap diff-preview")
        self.assertNotIn("qual-bootstrap terminal", summary.compatibility_command_lines)

    def test_handoff_evidence_exposes_deterministic_canonical_gap_rows(self) -> None:
        evidence = command_demo_path_handoff_evidence(program="qual-bootstrap")

        self.assertEqual(evidence[0], ("ready", "false"))
        self.assertIn(("command:1", "qual-bootstrap bootstrap"), evidence)
        self.assertIn(("patch-review-ready", "false"), evidence)
        self.assertIn(("patch-review:preview", "qual-bootstrap diff-preview"), evidence)
        self.assertIn(
            ("patch-review:apply", "missing: no stable command route applies reviewed patches"),
            evidence,
        )
        self.assertIn(
            ("patch-review:reject", "missing: no stable command route rejects reviewed patches"),
            evidence,
        )
        self.assertIn(("flow:retrieval", "qual-bootstrap context-basket list"), evidence)
        self.assertIn(
            (
                "canonical:open-project-document",
                "qual-bootstrap bootstrap",
            ),
            evidence,
        )
        self.assertIn(
            (
                "canonical:promote-or-gather-context-into-basket",
                "qual-bootstrap context-basket add demo-context-item",
            ),
            evidence,
        )
        self.assertIn(
            (
                "gap:1",
                "produce-plan-or-revision: no stable command route produces a plan or revision through the engine loop",
            ),
            evidence,
        )
        self.assertIn(
            (
                "canonical:preview-and-apply-or-reject-patch",
                "missing: the current patch-review route previews diffs but does not apply or reject patches",
            ),
            evidence,
        )
        self.assertIn(
            (
                "blocker:preview-and-apply-or-reject-patch",
                (
                    "partial-command: qual-bootstrap diff-preview; "
                    "the current patch-review route previews diffs but does not apply or reject patches"
                ),
            ),
            evidence,
        )

    def test_handoff_evidence_scopes_patch_review_outcomes_to_requested_flow_steps(self) -> None:
        evidence = command_demo_path_handoff_evidence(
            program="qual-bootstrap",
            flow_steps=("project-open", "retrieval"),
        )

        self.assertIn(("flow:project-open", "qual-bootstrap bootstrap"), evidence)
        self.assertIn(("flow:retrieval", "qual-bootstrap context-basket list"), evidence)
        self.assertNotIn(("patch-review:preview", "qual-bootstrap diff-preview"), evidence)
        self.assertIn(
            ("patch-review:preview", "missing: no stable command route is available"),
            evidence,
        )
        self.assertNotIn(("flow:patch-review", "qual-bootstrap diff-preview"), evidence)

    def test_patch_review_outcome_contract_keeps_apply_reject_gaps_smoke_testable(self) -> None:
        contract = command_patch_review_outcome_contract(program="qual-bootstrap")

        self.assertFalse(contract.ready)
        self.assertEqual(contract.missing_outcomes, ("apply", "reject"))
        self.assertEqual(
            tuple((status.outcome, status.ready, status.command, status.gap_reason) for status in contract.statuses),
            (
                ("preview", True, "qual-bootstrap diff-preview", ""),
                ("apply", False, "", "no stable command route applies reviewed patches"),
                ("reject", False, "", "no stable command route rejects reviewed patches"),
            ),
        )

    def test_mvp_handoff_evidence_matches_demo_path_evidence(self) -> None:
        self.assertEqual(
            command_mvp_demo_path_handoff_evidence(program="qual-bootstrap"),
            command_demo_path_handoff_evidence(program="qual-bootstrap"),
        )

    def test_handoff_evidence_carries_reviewer_replay_identity(self) -> None:
        summary = command_demo_path_handoff_summary(program="qual-bootstrap")
        evidence = command_demo_path_handoff_evidence(program="qual-bootstrap")

        self.assertIn(("fingerprint", summary.fingerprint), evidence)
        self.assertIn((f"command:{summary.command_count}", summary.command_lines[-1]), evidence)
        for demo_step, command_line in summary.covered_canonical_step_commands:
            self.assertIn((f"canonical:{demo_step}", command_line), evidence)

    def test_compatibility_lookup_table_maps_alias_commands_to_canonical_smoke_commands(self) -> None:
        lookup_table = command_demo_path_compatibility_lookup_table(program="qual-bootstrap")

        self.assertEqual(lookup_table, command_mvp_demo_path_compatibility_lookup_table(program="qual-bootstrap"))
        self.assertIn(
            (
                ("qual-bootstrap", "project-open"),
                ("qual-bootstrap", "bootstrap"),
                "open-project-document",
            ),
            lookup_table,
        )
        self.assertIn(
            (
                ("qual-bootstrap", "retrieval", "list"),
                ("qual-bootstrap", "context-basket", "list"),
                "retrieve-relevant-material",
            ),
            lookup_table,
        )
        self.assertIn(
            (
                ("qual-bootstrap", "patch-review"),
                ("qual-bootstrap", "diff-preview"),
                "preview-patch",
            ),
            lookup_table,
        )
        self.assertIn(
            (
                ("qual-bootstrap", "export-handoff"),
                ("qual-bootstrap", "terminal"),
                "export-handoff",
            ),
            lookup_table,
        )


if __name__ == "__main__":
    unittest.main()
