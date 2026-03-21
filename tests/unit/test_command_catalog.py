from __future__ import annotations

import unittest

from src.qual.commands import (
    CommandCatalogEntry,
    canonical_command,
    command_catalog_entries,
    command_catalog_entries_for_role,
    command_lookup_names,
    command_lookup_names_for_role,
    command_mvp_flow_entries,
    command_mvp_flow_lookup_index,
    command_mvp_flow_lookup_names,
    command_mvp_flow_names,
    command_mvp_roles,
    command_names,
    command_names_for_role,
    command_spec,
)


class CommandCatalogTests(unittest.TestCase):
    def test_catalog_entries_are_deterministic_and_machine_readable(self) -> None:
        entries = command_catalog_entries()

        self.assertEqual(
            command_names(),
            (
                "bootstrap",
                "retrieve",
                "diff-preview",
                "context-basket",
                "terminal",
                "export-preview",
            ),
        )
        self.assertTrue(all(isinstance(entry, CommandCatalogEntry) for entry in entries))
        self.assertEqual([entry.name for entry in entries], list(command_names()))
        self.assertEqual(
            entries[0],
            CommandCatalogEntry(
                name="bootstrap",
                aliases=("open", "project-open", "project"),
                description="Run the project bootstrap flow.",
                mvp_role="project-open",
                lookup_names=("bootstrap", "open", "project-open", "project"),
                in_mvp_flow=True,
            ),
        )
        self.assertEqual(
            entries[1],
            CommandCatalogEntry(
                name="retrieve",
                aliases=("retrieval", "lookup"),
                description="Run the project retrieval flow.",
                mvp_role="retrieval-invocation",
                lookup_names=("retrieve", "retrieval", "lookup"),
                in_mvp_flow=True,
            ),
        )
        self.assertTrue(entries[-1].in_mvp_flow)
        self.assertEqual(
            entries[-1].lookup_names,
            ("export-preview", "export", "handoff"),
        )

    def test_role_filtered_entries_match_role_helpers(self) -> None:
        for role in command_mvp_roles():
            role_entries = command_catalog_entries_for_role(role)
            self.assertEqual(
                tuple(entry.name for entry in role_entries),
                command_names_for_role(role),
            )
            self.assertEqual(
                tuple(name for entry in role_entries for name in entry.lookup_names),
                command_lookup_names_for_role(role),
            )

    def test_mvp_flow_entries_cover_all_smoke_commands(self) -> None:
        entries = command_mvp_flow_entries()

        self.assertEqual(command_mvp_flow_names(), tuple(entry.name for entry in entries))
        self.assertTrue(all(entry.in_mvp_flow for entry in entries))
        self.assertEqual(
            command_mvp_flow_lookup_names(),
            tuple(name for entry in entries for name in entry.lookup_names),
        )

    def test_mvp_flow_lookup_index_resolves_flow_aliases(self) -> None:
        lookup_index = command_mvp_flow_lookup_index()

        self.assertEqual(
            tuple(lookup_index),
            command_mvp_flow_lookup_names(),
        )
        self.assertEqual(lookup_index["bootstrap"].name, "bootstrap")
        self.assertEqual(lookup_index["project-open"].name, "bootstrap")
        self.assertEqual(lookup_index["retrieval"].name, "retrieve")
        self.assertEqual(lookup_index["diff-preview"].name, "diff-preview")
        self.assertEqual(lookup_index["handoff"].name, "export-preview")

    def test_alias_canonicalization_stays_tolerant_for_known_commands(self) -> None:
        self.assertEqual(canonical_command("project-open"), "bootstrap")
        self.assertEqual(canonical_command("diff_preview"), "diff-preview")
        self.assertEqual(canonical_command("lookup"), "retrieve")
        self.assertEqual(canonical_command("unknown-command"), "unknown-command")
        self.assertEqual(command_spec("open").name, "bootstrap")
        self.assertEqual(command_spec("lookup").name, "retrieve")
        self.assertIsNone(command_spec("not-a-command"))
        self.assertEqual(command_lookup_names()[0], "bootstrap")


if __name__ == "__main__":
    unittest.main()
