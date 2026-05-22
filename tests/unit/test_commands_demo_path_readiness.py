from __future__ import annotations

import unittest

from src.qual.commands import command_demo_path_command_lookup_table, command_demo_path_readiness


class CommandDemoPathReadinessTests(unittest.TestCase):
    def test_readiness_requires_the_full_mvp_loop(self) -> None:
        readiness = command_demo_path_readiness(program="qual-bootstrap")

        self.assertTrue(readiness.ready)
        self.assertEqual(readiness.missing_demo_steps, ())
        self.assertEqual(
            readiness.command_lookup_table,
            (
                (("qual-bootstrap", "bootstrap"), "open-project-document"),
                (("qual-bootstrap", "context-basket", "list"), "retrieve-relevant-material"),
                (("qual-bootstrap", "diff-preview"), "preview-apply-or-reject-patch"),
                (("qual-bootstrap", "terminal"), "persist-and-continue"),
            ),
        )
        self.assertEqual(
            readiness.demo_steps,
            (
                "open-project-document",
                "retrieve-relevant-material",
                "preview-apply-or-reject-patch",
                "persist-and-continue",
            ),
        )

    def test_readiness_flags_partial_demo_paths(self) -> None:
        readiness = command_demo_path_readiness(
            program="qual-bootstrap",
            flow_steps=("project-open", "retrieval", "patch-review"),
        )

        self.assertFalse(readiness.ready)
        self.assertEqual(readiness.missing_demo_steps, ("persist-and-continue",))
        self.assertEqual(readiness.demo_steps[-1], "preview-apply-or-reject-patch")

    def test_command_lookup_table_maps_smoke_commands_to_demo_steps(self) -> None:
        self.assertEqual(
            command_demo_path_command_lookup_table(program="qual-bootstrap"),
            (
                (("qual-bootstrap", "bootstrap"), "open-project-document"),
                (("qual-bootstrap", "context-basket", "list"), "retrieve-relevant-material"),
                (("qual-bootstrap", "diff-preview"), "preview-apply-or-reject-patch"),
                (("qual-bootstrap", "terminal"), "persist-and-continue"),
            ),
        )


if __name__ == "__main__":
    unittest.main()
