from __future__ import annotations

import unittest

from src.qual.commands import command_demo_path_readiness


class CommandDemoPathReadinessTests(unittest.TestCase):
    def test_readiness_requires_the_full_mvp_loop(self) -> None:
        readiness = command_demo_path_readiness(program="qual-bootstrap")

        self.assertTrue(readiness.ready)
        self.assertEqual(readiness.missing_demo_steps, ())
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


if __name__ == "__main__":
    unittest.main()
