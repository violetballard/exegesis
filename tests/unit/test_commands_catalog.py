from __future__ import annotations

import unittest

from src.qual.commands import (
    canonical_command,
    command_aliases,
    command_lookup_tokens,
    command_manifest,
    command_names,
    command_spec,
    command_specs,
)


class CommandCatalogTests(unittest.TestCase):
    def test_command_names_match_catalog_order(self) -> None:
        self.assertEqual(
            command_names(),
            ("bootstrap", "diff-preview", "context-basket", "terminal"),
        )

    def test_command_specs_and_names_stay_aligned(self) -> None:
        self.assertEqual(tuple(spec.name for spec in command_specs()), command_names())

    def test_known_aliases_resolve_to_canonical_command_names(self) -> None:
        cases = {
            "open": "bootstrap",
            "project-open": "bootstrap",
            "project": "bootstrap",
            "diff": "diff-preview",
            "diff_preview": "diff-preview",
            "context": "context-basket",
            "basket": "context-basket",
        }
        for alias, expected in cases.items():
            with self.subTest(alias=alias):
                self.assertEqual(canonical_command(alias), expected)

    def test_unknown_commands_are_normalized_deterministically(self) -> None:
        self.assertEqual(canonical_command("  New_Command  "), "new-command")
        self.assertEqual(canonical_command(""), "")

    def test_command_lookup_helpers_return_spec_metadata(self) -> None:
        spec = command_spec("project-open")
        self.assertIsNotNone(spec)
        self.assertEqual(spec.name, "bootstrap")
        self.assertEqual(command_aliases("project-open"), ("open", "project-open", "project"))
        self.assertEqual(command_lookup_tokens("project-open"), ("bootstrap", "open", "project-open", "project"))
        self.assertEqual(command_aliases("missing"), ())
        self.assertEqual(command_lookup_tokens("missing"), ())

    def test_command_manifest_entries_expose_canonical_lookup_tokens(self) -> None:
        manifest = command_manifest()
        self.assertEqual(
            tuple((entry.name, command_lookup_tokens(entry.name)) for entry in manifest),
            (
                ("bootstrap", ("bootstrap", "open", "project-open", "project")),
                ("diff-preview", ("diff-preview", "diff", "diff_preview")),
                ("context-basket", ("context-basket", "context", "basket")),
                ("terminal", ("terminal",)),
            ),
        )


if __name__ == "__main__":
    unittest.main()
