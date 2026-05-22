from __future__ import annotations

import unittest

from src.qual.commands import (
    command_demo_path_command_lookup_table,
    command_demo_path_compatibility_lookup_table,
    command_demo_path_handoff_summary,
    command_demo_path_readiness,
    command_mvp_demo_path_compatibility_lookup_table,
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
