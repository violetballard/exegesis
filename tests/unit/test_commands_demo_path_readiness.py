from __future__ import annotations

import unittest

import src.qual.commands.catalog as command_catalog
from src.qual.commands.catalog import (
    command_demo_path_blocker_lines,
    command_demo_path_command_lookup_table,
    command_demo_path_handoff_evidence,
    command_demo_path_next_blocker,
    command_demo_path_next_blocker_line,
    command_demo_path_readiness,
)


class CommandDemoPathReadinessTests(unittest.TestCase):
    def test_command_demo_path_readiness_smoke(self) -> None:
        readiness = command_demo_path_readiness()
        self.assertIsNotNone(readiness)
        self.assertIsInstance(readiness.program, str)
        self.assertIsInstance(readiness.ready, bool)
        self.assertIsInstance(readiness.demo_steps, tuple)
        self.assertIsInstance(readiness.flow_steps, tuple)
        self.assertIsInstance(readiness.missing_demo_steps, tuple)
        self.assertIsInstance(readiness.steps, tuple)

    def test_command_demo_path_readiness_program_is_normalized(self) -> None:
        readiness = command_demo_path_readiness(program="qual-bootstrap")
        self.assertEqual(readiness.program, "qual-bootstrap")

    def test_command_demo_path_readiness_includes_expected_flow_steps(self) -> None:
        readiness = command_demo_path_readiness()
        for step in ("project-open", "retrieval", "patch-review", "export-handoff"):
            self.assertIn(step, readiness.flow_steps)

    def test_command_demo_path_readiness_fingerprint_is_deterministic(self) -> None:
        r1 = command_demo_path_readiness()
        r2 = command_demo_path_readiness()
        self.assertEqual(r1.fingerprint, r2.fingerprint)

    def test_command_demo_path_readiness_command_count_matches_flow_steps(self) -> None:
        readiness = command_demo_path_readiness()
        self.assertEqual(len(readiness.flow_steps), len(readiness.demo_steps))

    def test_command_demo_path_command_lookup_table_smoke(self) -> None:
        table = command_demo_path_command_lookup_table()
        self.assertIsNotNone(table)
        self.assertIsInstance(table, tuple)
        self.assertGreater(len(table), 0)
        for entry in table:
            argv_tuple, demo_step = entry
            self.assertIsInstance(argv_tuple, tuple)
            self.assertIsInstance(demo_step, str)
            self.assertTrue(len(argv_tuple) >= 1)

    def test_command_demo_path_command_lookup_table_maps_all_demo_entries(self) -> None:
        table = command_demo_path_command_lookup_table()
        # Each command tuple starts with the program, second element is the CLI token
        cli_tokens = {argv_tuple[1] for argv_tuple, _ in table if len(argv_tuple) > 1}
        for token in ("bootstrap", "context-basket", "diff-preview", "terminal"):
            self.assertIn(token, cli_tokens)

    def test_command_demo_path_handoff_evidence_smoke(self) -> None:
        evidence = command_demo_path_handoff_evidence()
        self.assertIsNotNone(evidence)
        self.assertIsInstance(evidence, tuple)
        for entry in evidence:
            label, value = entry
            self.assertIsInstance(label, str)
            self.assertIsInstance(value, str)

    def test_command_demo_path_handoff_evidence_is_non_empty(self) -> None:
        evidence = command_demo_path_handoff_evidence()
        self.assertGreater(len(evidence), 0)

    def test_command_demo_path_handoff_evidence_labels_are_unique(self) -> None:
        evidence = command_demo_path_handoff_evidence()
        labels = [label for label, _ in evidence]
        self.assertEqual(len(labels), len(set(labels)))

    def test_command_demo_path_readiness_apply_reject_gap_is_closed(self) -> None:
        # diff-preview apply/reject commands now cover all three patch-review
        # outcomes; the canonical step must no longer appear in missing_demo_steps.
        readiness = command_demo_path_readiness()
        missing = set(readiness.missing_demo_steps)
        self.assertNotIn(
            "preview-and-apply-or-reject-patch",
            missing,
            "apply/reject patch gap is closed: diff-preview apply/reject routes cover all outcomes",
        )

    def test_command_demo_path_handoff_evidence_pins_trusted_milestone3_surface(self) -> None:
        # Pins the stable Milestone 3 command surface. These four commands
        # are trusted for the CLI-first demo loop; any change to this mapping
        # requires explicit lane review.
        evidence = dict(command_demo_path_handoff_evidence())
        self.assertEqual(evidence["flow:project-open"], "qual-bootstrap bootstrap")
        self.assertEqual(evidence["flow:retrieval"], "qual-bootstrap context-basket list")
        self.assertEqual(evidence["flow:patch-review"], "qual-bootstrap diff-preview")
        self.assertEqual(evidence["flow:export-handoff"], "qual-bootstrap terminal")
        self.assertEqual(evidence["ready"], "false")
        # patch-review is now fully covered: preview, apply, and reject routes exist.
        self.assertEqual(evidence["patch-review-ready"], "true")
        self.assertEqual(evidence["patch-review-ready-outcomes"], "preview,apply,reject")
        self.assertEqual(evidence["patch-review-missing-outcomes"], "")
        self.assertEqual(
            evidence["next-blocker"],
            "produce-plan-or-revision: partial-command: qual-bootstrap revise; no stable command route produces a plan or revision through the engine loop",
        )

    def test_command_demo_path_next_blocker_is_produce_plan_or_revision(self) -> None:
        blocker = command_demo_path_next_blocker()
        self.assertIsNotNone(blocker)
        self.assertEqual(blocker.demo_step, "produce-plan-or-revision")
        # Thin command entrypoint exists (qual-bootstrap revise); engine loop not
        # yet wired — blocker type is partial-command, not missing-command.
        self.assertEqual(blocker.blocker_type, "partial-command")
        self.assertEqual(blocker.partial_command, "qual-bootstrap revise")

    def test_command_demo_path_next_blocker_line_matches_evidence_entry(self) -> None:
        # The next-blocker line is the canonical string signal for downstream
        # lanes; it must be identical to evidence["next-blocker"].
        line = command_demo_path_next_blocker_line()
        evidence = dict(command_demo_path_handoff_evidence())
        self.assertEqual(line, evidence["next-blocker"])

    def test_command_demo_path_next_blocker_line_is_pinned(self) -> None:
        # Pins the exact string that feat-engine-runs consumes to know which
        # command to wire the engine loop into. Any wording change requires
        # explicit lane review.
        line = command_demo_path_next_blocker_line()
        self.assertEqual(
            line,
            "produce-plan-or-revision: partial-command: qual-bootstrap revise; no stable command route produces a plan or revision through the engine loop",
        )

    def test_command_demo_path_blocker_lines_is_tuple_of_strings(self) -> None:
        lines = command_demo_path_blocker_lines()
        self.assertIsInstance(lines, tuple)
        for line in lines:
            self.assertIsInstance(line, str)
            self.assertGreater(len(line), 0)

    def test_command_demo_path_blocker_lines_first_matches_next_blocker_line(self) -> None:
        lines = command_demo_path_blocker_lines()
        next_line = command_demo_path_next_blocker_line()
        self.assertGreater(len(lines), 0)
        self.assertEqual(lines[0], next_line)

    def test_command_demo_path_blocker_lines_pins_full_gap_set(self) -> None:
        # Pins all three remaining partial-command blockers in demo-path order.
        # Each line names the thin command entrypoint that feat-engine-runs must
        # wire into the engine loop to close the gap.
        # preview-and-apply-or-reject-patch is closed: diff-preview apply/reject
        # commands now cover all three patch-review outcomes.
        lines = command_demo_path_blocker_lines()
        self.assertEqual(len(lines), 3)
        self.assertEqual(
            lines[0],
            "produce-plan-or-revision: partial-command: qual-bootstrap revise; no stable command route produces a plan or revision through the engine loop",
        )
        self.assertEqual(
            lines[1],
            "persist-updated-document-session-state: partial-command: qual-bootstrap session-save; no stable command route persists the updated document and session state",
        )
        self.assertEqual(
            lines[2],
            "continue-without-losing-context: partial-command: qual-bootstrap session-resume; no stable command route resumes the workflow without losing context",
        )

    def test_canonical_step_status_partial_command_field_pins_stub_commands(self) -> None:
        # Pins the partial_command field on CommandCanonicalStepStatus for the
        # three engine-loop steps. feat-engine-runs reads these to know which
        # command surface to wire the engine loop into.
        readiness = command_demo_path_readiness()
        by_step = {s.demo_step: s for s in readiness.canonical_step_statuses}
        self.assertEqual(
            by_step["produce-plan-or-revision"].partial_command,
            "qual-bootstrap revise",
        )
        self.assertEqual(
            by_step["persist-updated-document-session-state"].partial_command,
            "qual-bootstrap session-save",
        )
        self.assertEqual(
            by_step["continue-without-losing-context"].partial_command,
            "qual-bootstrap session-resume",
        )

    def test_canonical_step_status_partial_command_appears_in_handoff_evidence(self) -> None:
        # canonical:* evidence entries for partial-command steps now carry the
        # stub command name, not just "missing:". This makes the handoff evidence
        # consistent with the blocker:* entries.
        evidence = dict(command_demo_path_handoff_evidence())
        self.assertEqual(
            evidence["canonical:produce-plan-or-revision"],
            "partial-command: qual-bootstrap revise; no stable command route produces a plan or revision through the engine loop",
        )
        self.assertEqual(
            evidence["canonical:persist-updated-document-session-state"],
            "partial-command: qual-bootstrap session-save; no stable command route persists the updated document and session state",
        )
        self.assertEqual(
            evidence["canonical:continue-without-losing-context"],
            "partial-command: qual-bootstrap session-resume; no stable command route resumes the workflow without losing context",
        )


if __name__ == "__main__":
    unittest.main()
