from __future__ import annotations

import unittest

import src.qual.commands.catalog as command_catalog
from src.qual.commands.catalog import (
    command_demo_path_command_lookup_table,
    command_demo_path_handoff_evidence,
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

    def test_command_demo_path_readiness_missing_steps_includes_apply_reject_gap(self) -> None:
        readiness = command_demo_path_readiness()
        missing = set(readiness.missing_demo_steps)
        self.assertIn(
            "preview-and-apply-or-reject-patch",
            missing,
            "apply/reject patch gap must appear in missing_demo_steps until commands are implemented",
        )


if __name__ == "__main__":
    unittest.main()
