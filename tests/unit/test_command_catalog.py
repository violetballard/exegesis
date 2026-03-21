from __future__ import annotations

import unittest

from src.qual.commands import (
    canonical_command,
    command_aliases,
    command_lookup_names,
    command_mvp_flow_names,
    command_mvp_role,
    command_mvp_roles,
    command_names,
    command_names_for_role,
    command_spec,
    command_specs_for_role,
)


class CommandCatalogTests(unittest.TestCase):
    def test_command_flow_covers_mvp_operator_sequence(self) -> None:
        self.assertEqual(
            command_mvp_flow_names(),
            ("bootstrap", "context-basket", "diff-preview", "terminal", "export-preview"),
        )

    def test_export_handoff_command_is_addressable_by_alias(self) -> None:
        spec = command_spec("export")
        self.assertIsNotNone(spec)
        self.assertEqual(spec.name, "export-preview")
        self.assertEqual(command_aliases("export-preview"), ("export", "handoff"))
        self.assertEqual(command_mvp_role("export-preview"), "export-handoff")
        self.assertEqual(command_names_for_role("export-handoff"), ("export-preview",))
        self.assertEqual(command_specs_for_role("export-handoff")[0].name, "export-preview")

    def test_lookup_names_and_roles_remain_deterministic(self) -> None:
        self.assertEqual(
            command_lookup_names(),
            (
                "bootstrap",
                "open",
                "project-open",
                "project",
                "diff-preview",
                "diff",
                "context-basket",
                "context",
                "basket",
                "terminal",
                "export-preview",
                "export",
                "handoff",
            ),
        )
        self.assertEqual(
            command_names(),
            ("bootstrap", "diff-preview", "context-basket", "terminal", "export-preview"),
        )
        self.assertEqual(
            command_mvp_roles(),
            ("project-open", "patch-review", "retrieval-staging", "a2ui-routing", "export-handoff"),
        )

    def test_unknown_role_returns_empty_sequences(self) -> None:
        self.assertEqual(command_names_for_role("missing"), ())
        self.assertEqual(command_specs_for_role("missing"), ())
        self.assertEqual(canonical_command(" missing "), "missing")


if __name__ == "__main__":
    unittest.main()
