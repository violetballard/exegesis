from __future__ import annotations

import unittest
from unittest.mock import patch

import src.qual.commands.catalog as command_catalog
from src.qual.commands import (
    CommandSpec,
    canonical_command,
    canonical_command_for,
    command_aliases,
    command_aliases_for,
    command_cli_contract,
    command_cli_flow_contract,
    command_cli_flow_lookup_table,
    command_cli_tokens,
    command_cli_route_catalog,
    command_cli_route_contract,
    command_cli_route_summary,
    command_flow_manifest,
    command_flow_catalog,
    command_flow_route_summary,
    command_cli_lookup_table,
    command_flow_lookup_index,
    command_flow_lookup_surface,
    command_flow_lookup_table,
    command_flow_surface_lookup_index,
    command_flow_surface_tokens,
    command_flow_steps,
    command_flow_sequence,
    command_lookup_index,
    command_lookup_table,
    command_lookup_tokens,
    command_lookup_tokens_for,
    command_manifest,
    command_mvp_flow,
    command_mvp_cli_flow_contract,
    command_mvp_cli_route_contract,
    command_mvp_flow_names,
    command_mvp_flow_catalog,
    command_mvp_flow_manifest,
    command_mvp_flow_contract,
    command_mvp_flow_lookup_surface,
    command_mvp_flow_route_catalog,
    command_mvp_flow_route_summary,
    command_mvp_flow_surface_lookup_index,
    command_mvp_flow_surface_tokens,
    command_mvp_flow_lookup_table,
    command_mvp_flow_tokens,
    command_mvp_flow_sequence,
    command_mvp_flow_steps,
    command_mvp_lookup_index,
    command_mvp_surface_contract,
    command_surface_contract,
    command_demo_flow_route_summary,
    command_demo_flow_surface_tokens,
    command_names,
    command_spec,
    command_spec_for,
    command_specs,
    command_tokens,
    command_flow_tokens,
    validate_command_catalog,
)


class CommandCatalogTests(unittest.TestCase):
    def test_command_names_match_catalog_order(self) -> None:
        self.assertEqual(
            command_names(),
            ("bootstrap", "diff-preview", "context-basket", "terminal", "revise", "session-save", "session-resume"),
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

    def test_command_cli_lookup_table_exposes_the_parser_surface(self) -> None:
        self.assertEqual(
            command_cli_lookup_table(),
            (
                ("bootstrap", "bootstrap"),
                ("diff-preview", "diff-preview"),
                ("diff", "diff-preview"),
                ("context-basket", "context-basket"),
                ("terminal", "terminal"),
                ("revise", "revise"),
                ("session-save", "session-save"),
                ("session-resume", "session-resume"),
            ),
        )

    def test_command_cli_contract_matches_the_catalog_order(self) -> None:
        contract = command_cli_contract()
        self.assertEqual(contract.tokens, command_cli_tokens())
        self.assertEqual(contract.canonical_names, command_names())
        self.assertEqual(contract.lookup_table, command_cli_lookup_table())

    def test_command_cli_contract_rejects_catalog_drift(self) -> None:
        command_catalog.command_cli_contract.cache_clear()
        with patch.object(command_catalog, "command_names", return_value=("bootstrap", "diff-preview")):
            with self.assertRaisesRegex(ValueError, "Command CLI canonical names are inconsistent"):
                command_catalog.command_cli_contract()

    def test_command_cli_lookup_table_resolves_through_the_catalog(self) -> None:
        self.assertEqual(
            command_cli_lookup_table(),
            tuple((token, canonical_command(token)) for token in command_cli_tokens()),
        )

    def test_command_cli_tokens_reject_unknown_entrypoints(self) -> None:
        command_catalog.command_cli_tokens.cache_clear()
        with patch.object(command_catalog, "_CLI_ENTRYPOINTS", ("bootstrap", "not-a-command")):
            with self.assertRaisesRegex(ValueError, "Unknown CLI command entrypoint: not-a-command"):
                command_catalog.command_cli_tokens()

    def test_command_cli_flow_contract_maps_parser_tokens_to_mvp_flow_steps(self) -> None:
        contract = command_cli_flow_contract()
        self.assertEqual(
            tuple((entry.token, entry.canonical_name, entry.flow_step) for entry in contract.entries),
            (
                ("bootstrap", "bootstrap", "project-open"),
                ("diff-preview", "diff-preview", "patch-review"),
                ("diff", "diff-preview", "patch-review"),
                ("context-basket", "context-basket", "retrieval"),
                ("terminal", "terminal", "export-handoff"),
                ("revise", "revise", "plan-revision"),
                ("session-save", "session-save", "persist-save"),
                ("session-resume", "session-resume", "session-resume"),
            ),
        )
        self.assertEqual(
            command_cli_flow_lookup_table(),
            (
                ("bootstrap", "project-open"),
                ("diff-preview", "patch-review"),
                ("diff", "patch-review"),
                ("context-basket", "retrieval"),
                ("terminal", "export-handoff"),
                ("revise", "plan-revision"),
                ("session-save", "persist-save"),
                ("session-resume", "session-resume"),
            ),
        )
        self.assertEqual(contract, command_mvp_cli_flow_contract())

    def test_command_cli_route_summary_tracks_the_smoke_route(self) -> None:
        self.assertEqual(
            command_cli_route_summary(),
            (
                ("project-open", "bootstrap", ("bootstrap",)),
                ("retrieval", "context-basket", ("context-basket",)),
                ("patch-review", "diff-preview", ("diff-preview", "diff")),
                ("export-handoff", "terminal", ("terminal",)),
                ("plan-revision", "revise", ("revise",)),
                ("persist-save", "session-save", ("session-save",)),
                ("session-resume", "session-resume", ("session-resume",)),
            ),
        )
        self.assertEqual(command_cli_route_summary(), command_surface_contract().route_summary)

    def test_command_cli_route_contract_tracks_the_smoke_surface(self) -> None:
        contract = command_cli_route_contract()
        surface_contract = command_surface_contract()
        self.assertEqual(contract.route_catalog, command_cli_route_catalog())
        self.assertEqual(
            tuple((entry.flow_step, entry.name, entry.cli_tokens) for entry in contract.route_catalog),
            (
                ("project-open", "bootstrap", ("bootstrap",)),
                ("retrieval", "context-basket", ("context-basket",)),
                ("patch-review", "diff-preview", ("diff-preview", "diff")),
                ("export-handoff", "terminal", ("terminal",)),
                ("plan-revision", "revise", ("revise",)),
                ("persist-save", "session-save", ("session-save",)),
                ("session-resume", "session-resume", ("session-resume",)),
            ),
        )
        self.assertEqual(contract.route_catalog, surface_contract.route_catalog)
        self.assertEqual(contract.route_catalog, command_mvp_flow_route_catalog())
        self.assertEqual(contract.lookup_surface, surface_contract.lookup_surface)
        self.assertEqual(contract.flow_surface_tokens, surface_contract.flow_surface_tokens)
        self.assertEqual(contract, command_mvp_cli_route_contract())

    def test_command_lookup_helpers_support_custom_catalogs(self) -> None:
        specs = (
            CommandSpec(name="bootstrap", aliases=("open",), flow_step="project-open"),
            CommandSpec(name="review", aliases=("patch",), flow_step="patch-review"),
        )

        self.assertEqual(command_spec_for(specs, "project-open").name, "bootstrap")
        self.assertEqual(command_aliases_for(specs, "patch-review"), ("patch",))
        self.assertEqual(command_lookup_tokens_for(specs, "patch-review"), ("review", "patch"))
        self.assertEqual(canonical_command_for(specs, " PATCH REVIEW "), "review")

    def test_command_manifest_entries_expose_canonical_lookup_tokens(self) -> None:
        manifest = command_manifest()
        self.assertEqual(
            tuple((entry.name, entry.lookup_tokens) for entry in manifest),
            (
                ("bootstrap", ("bootstrap", "open", "project-open", "project")),
                ("diff-preview", ("diff-preview", "diff", "diff_preview")),
                ("context-basket", ("context-basket", "context", "basket")),
                ("terminal", ("terminal",)),
                ("revise", ("revise", "revision")),
                ("session-save", ("session-save", "save")),
                ("session-resume", ("session-resume", "resume")),
            ),
        )
        self.assertEqual(
            tuple(command_lookup_tokens(entry.name) for entry in manifest),
            tuple(entry.lookup_tokens for entry in manifest),
        )

    def test_command_tokens_flatten_the_catalog_in_order(self) -> None:
        self.assertEqual(
            command_tokens(),
            (
                "bootstrap",
                "open",
                "project-open",
                "project",
                "diff-preview",
                "diff",
                "diff_preview",
                "context-basket",
                "context",
                "basket",
                "terminal",
                "revise",
                "revision",
                "session-save",
                "save",
                "session-resume",
                "resume",
            ),
        )

    def test_command_names_reject_ambiguous_custom_catalogs(self) -> None:
        with self.assertRaisesRegex(ValueError, "Duplicate command name"):
            command_names(
                (
                    CommandSpec(name="bootstrap", flow_step="project-open"),
                    CommandSpec(name="bootstrap", flow_step="retrieval"),
                )
            )

    def test_command_flow_steps_reject_ambiguous_custom_catalogs(self) -> None:
        with self.assertRaisesRegex(ValueError, "Duplicate command flow step"):
            command_flow_steps(
                (
                    CommandSpec(name="bootstrap", flow_step="project-open"),
                    CommandSpec(name="context-basket", flow_step="project-open"),
                )
            )

    def test_command_lookup_projections_reject_ambiguous_catalog_definitions(self) -> None:
        with self.assertRaisesRegex(ValueError, "Duplicate command name"):
            command_lookup_table(
                (
                    CommandSpec(name="bootstrap", flow_step="project-open"),
                    CommandSpec(name="bootstrap", flow_step="retrieval"),
                )
            )

        with self.assertRaisesRegex(ValueError, "Duplicate command flow step"):
            command_lookup_index(
                (
                    CommandSpec(name="bootstrap", flow_step="project-open"),
                    CommandSpec(name="context-basket", flow_step="project-open"),
                )
            )

        with self.assertRaisesRegex(ValueError, "Duplicate command lookup alias"):
            command_tokens(
                (
                    CommandSpec(name="bootstrap", aliases=("open",), flow_step="project-open"),
                    CommandSpec(name="diff-preview", aliases=("open",), flow_step="patch-review"),
                )
            )

    def test_command_lookup_table_deduplicates_normalized_lookup_tokens(self) -> None:
        self.assertEqual(command_lookup_table(), command_lookup_index())
        self.assertEqual(
            command_lookup_table(),
            (
                ("bootstrap", "bootstrap"),
                ("open", "bootstrap"),
                ("project-open", "bootstrap"),
                ("project", "bootstrap"),
                ("diff-preview", "diff-preview"),
                ("diff", "diff-preview"),
                ("context-basket", "context-basket"),
                ("context", "context-basket"),
                ("basket", "context-basket"),
                ("terminal", "terminal"),
                ("revise", "revise"),
                ("revision", "revise"),
                ("session-save", "session-save"),
                ("save", "session-save"),
                ("session-resume", "session-resume"),
                ("resume", "session-resume"),
            ),
        )

    def test_command_flow_sequence_bundles_the_demo_smoke_contract(self) -> None:
        sequence = command_flow_sequence()
        self.assertEqual(sequence, command_mvp_flow_sequence())
        self.assertEqual(sequence.flow_steps, command_mvp_flow_steps())
        self.assertEqual(sequence.names, command_mvp_flow_sequence().names)
        self.assertEqual(sequence.lookup_table, command_mvp_flow_lookup_table())
        self.assertEqual(
            sequence.lookup_tokens,
            tuple(entry.lookup_tokens for entry in command_mvp_flow()),
        )

    def test_command_flow_helpers_default_to_the_demo_route(self) -> None:
        self.assertEqual(command_flow_manifest(), command_mvp_flow_manifest())
        self.assertEqual(command_flow_catalog(), command_mvp_flow_catalog())
        self.assertEqual(command_flow_lookup_table(), command_mvp_flow_lookup_table())
        self.assertEqual(command_flow_lookup_index(), command_mvp_lookup_index())
        self.assertEqual(command_flow_lookup_surface(), command_mvp_flow_lookup_surface())
        self.assertEqual(command_flow_surface_lookup_index(), command_mvp_flow_surface_lookup_index())
        self.assertEqual(command_flow_surface_tokens(), command_mvp_flow_surface_tokens())
        self.assertEqual(command_flow_tokens(), command_mvp_flow_tokens())

    def test_command_flow_route_summary_tracks_the_smoke_route(self) -> None:
        self.assertEqual(
            command_flow_route_summary(),
            (
                ("project-open", "bootstrap", ("bootstrap",)),
                ("retrieval", "context-basket", ("context-basket",)),
                ("patch-review", "diff-preview", ("diff-preview", "diff")),
                ("export-handoff", "terminal", ("terminal",)),
                ("plan-revision", "revise", ("revise",)),
                ("persist-save", "session-save", ("session-save",)),
                ("session-resume", "session-resume", ("session-resume",)),
            ),
        )
        self.assertEqual(command_flow_route_summary(), command_cli_route_summary())
        self.assertEqual(command_flow_route_summary(), command_demo_flow_route_summary())
        self.assertEqual(command_demo_flow_route_summary(), command_mvp_flow_route_summary())
        self.assertEqual(command_flow_route_summary(), command_surface_contract().route_summary)

    def test_command_flow_route_summary_supports_custom_catalogs(self) -> None:
        specs = (
            CommandSpec(name="bootstrap", aliases=("open",), flow_step="project-open"),
            CommandSpec(name="review", aliases=("patch",), flow_step="patch-review"),
        )

        self.assertEqual(
            command_flow_route_summary(specs, ("patch-review", "project-open")),
            (
                ("patch-review", "review", ("review", "patch")),
                ("project-open", "bootstrap", ("bootstrap", "open")),
            ),
        )

    def test_command_flow_lookup_index_reuses_the_manifest_contract(self) -> None:
        self.assertEqual(command_flow_lookup_index(), command_mvp_lookup_index())
        self.assertEqual(
            command_flow_lookup_index(flow_steps=command_mvp_flow_steps()),
            command_mvp_lookup_index(),
        )

    def test_command_flow_lookup_surface_includes_flow_steps_for_smoke_checks(self) -> None:
        self.assertEqual(command_flow_lookup_surface(), command_mvp_flow_lookup_surface())
        self.assertEqual(
            command_mvp_flow_lookup_surface(),
            (
                ("bootstrap", "bootstrap"),
                ("open", "bootstrap"),
                ("project-open", "bootstrap"),
                ("project", "bootstrap"),
                ("context-basket", "context-basket"),
                ("context", "context-basket"),
                ("basket", "context-basket"),
                ("retrieval", "context-basket"),
                ("diff-preview", "diff-preview"),
                ("diff", "diff-preview"),
                ("patch-review", "diff-preview"),
                ("terminal", "terminal"),
                ("export-handoff", "terminal"),
                ("revise", "revise"),
                ("revision", "revise"),
                ("plan-revision", "revise"),
                ("session-save", "session-save"),
                ("save", "session-save"),
                ("persist-save", "session-save"),
                ("session-resume", "session-resume"),
                ("resume", "session-resume"),
            ),
        )

    def test_command_mvp_flow_route_catalog_locks_the_cli_route(self) -> None:
        route_catalog = command_mvp_flow_route_catalog()
        self.assertEqual(
            tuple((entry.flow_step, entry.name, entry.cli_tokens) for entry in route_catalog),
            (
                ("project-open", "bootstrap", ("bootstrap",)),
                ("retrieval", "context-basket", ("context-basket",)),
                ("patch-review", "diff-preview", ("diff-preview", "diff")),
                ("export-handoff", "terminal", ("terminal",)),
                ("plan-revision", "revise", ("revise",)),
                ("persist-save", "session-save", ("session-save",)),
                ("session-resume", "session-resume", ("session-resume",)),
            ),
        )
        self.assertEqual(command_surface_contract().route_catalog, route_catalog)
        self.assertEqual(command_mvp_surface_contract().route_catalog, route_catalog)

    def test_command_flow_surface_tokens_group_the_smoke_surface_by_step(self) -> None:
        self.assertEqual(command_flow_surface_tokens(), command_mvp_flow_surface_tokens())
        self.assertEqual(
            command_flow_surface_tokens(flow_steps=command_mvp_flow_steps()),
            command_mvp_flow_surface_tokens(),
        )
        self.assertEqual(command_flow_tokens(), command_mvp_flow_tokens())
        self.assertEqual(
            command_mvp_flow_surface_tokens(),
            (
                ("bootstrap", "open", "project-open", "project"),
                ("context-basket", "context", "basket", "retrieval"),
                ("diff-preview", "diff", "patch-review"),
                ("terminal", "export-handoff"),
                ("revise", "revision", "plan-revision"),
                ("session-save", "save", "persist-save"),
                ("session-resume", "resume"),
            ),
        )
        self.assertEqual(command_demo_flow_surface_tokens(), command_mvp_flow_surface_tokens())

    def test_command_mvp_lookup_index_stays_command_only(self) -> None:
        self.assertEqual(
            command_mvp_lookup_index(),
            (
                ("bootstrap", "bootstrap"),
                ("open", "bootstrap"),
                ("project-open", "bootstrap"),
                ("project", "bootstrap"),
                ("context-basket", "context-basket"),
                ("context", "context-basket"),
                ("basket", "context-basket"),
                ("diff-preview", "diff-preview"),
                ("diff", "diff-preview"),
                ("terminal", "terminal"),
                ("revise", "revise"),
                ("revision", "revise"),
                ("session-save", "session-save"),
                ("save", "session-save"),
                ("session-resume", "session-resume"),
                ("resume", "session-resume"),
            ),
        )
        self.assertEqual(
            command_flow_lookup_index(flow_steps=command_mvp_flow_steps()),
            command_mvp_lookup_index(),
        )

    def test_command_mvp_flow_surface_lookup_index_includes_flow_tokens(self) -> None:
        self.assertEqual(
            command_mvp_flow_surface_lookup_index(),
            command_mvp_flow_lookup_surface(),
        )
        self.assertEqual(
            command_flow_surface_lookup_index(flow_steps=command_mvp_flow_steps()),
            command_mvp_flow_surface_lookup_index(),
        )

    def test_command_mvp_flow_catalog_exposes_the_demo_sequence(self) -> None:
        flow = command_mvp_flow_catalog()
        self.assertEqual(
            tuple((entry.flow_step, entry.name) for entry in flow),
            (
                ("project-open", "bootstrap"),
                ("retrieval", "context-basket"),
                ("patch-review", "diff-preview"),
                ("export-handoff", "terminal"),
                ("plan-revision", "revise"),
                ("persist-save", "session-save"),
                ("session-resume", "session-resume"),
            ),
        )
        self.assertEqual(
            tuple(entry.lookup_tokens for entry in flow),
            (
                ("bootstrap", "open", "project-open", "project"),
                ("context-basket", "context", "basket"),
                ("diff-preview", "diff", "diff_preview"),
                ("terminal",),
                ("revise", "revision"),
                ("session-save", "save"),
                ("session-resume", "resume"),
            ),
        )

    def test_command_mvp_flow_lookup_table_is_ordered_for_smoke_checks(self) -> None:
        self.assertEqual(
            command_mvp_flow_lookup_table(),
            (
                ("project-open", "bootstrap"),
                ("retrieval", "context-basket"),
                ("patch-review", "diff-preview"),
                ("export-handoff", "terminal"),
                ("plan-revision", "revise"),
                ("persist-save", "session-save"),
                ("session-resume", "session-resume"),
            ),
        )

    def test_command_mvp_flow_sequence_bundles_the_demo_smoke_contract(self) -> None:
        sequence = command_mvp_flow_sequence()
        self.assertEqual(sequence.flow_steps, command_mvp_flow_steps())
        self.assertEqual(sequence.names, command_mvp_flow_names())
        self.assertEqual(sequence.lookup_table, command_mvp_flow_lookup_table())
        self.assertEqual(
            sequence.lookup_tokens,
            tuple(entry.lookup_tokens for entry in command_mvp_flow()),
        )

    def test_command_surface_contract_bundles_the_mvp_smoke_surface(self) -> None:
        contract = command_surface_contract()
        self.assertEqual(contract.flow_steps, command_mvp_flow_steps())
        self.assertEqual(contract.names, command_mvp_flow_names())
        self.assertEqual(contract.manifest, command_mvp_flow_manifest())
        self.assertEqual(contract.lookup_table, command_mvp_flow_lookup_table())
        self.assertEqual(
            contract.lookup_index,
            command_mvp_flow_surface_lookup_index(),
        )
        self.assertEqual(contract.lookup_index, contract.lookup_surface)
        self.assertEqual(
            contract.lookup_surface,
            command_mvp_flow_lookup_surface(),
        )
        self.assertEqual(contract.flow_surface_tokens, command_mvp_flow_surface_tokens())
        self.assertEqual(
            contract.lookup_index,
            (
                ("bootstrap", "bootstrap"),
                ("open", "bootstrap"),
                ("project-open", "bootstrap"),
                ("project", "bootstrap"),
                ("context-basket", "context-basket"),
                ("context", "context-basket"),
                ("basket", "context-basket"),
                ("retrieval", "context-basket"),
                ("diff-preview", "diff-preview"),
                ("diff", "diff-preview"),
                ("patch-review", "diff-preview"),
                ("terminal", "terminal"),
                ("export-handoff", "terminal"),
                ("revise", "revise"),
                ("revision", "revise"),
                ("plan-revision", "revise"),
                ("session-save", "session-save"),
                ("save", "session-save"),
                ("persist-save", "session-save"),
                ("session-resume", "session-resume"),
                ("resume", "session-resume"),
            ),
        )
        self.assertEqual(
            contract.lookup_tokens,
            tuple(entry.lookup_tokens for entry in command_mvp_flow()),
        )
        self.assertEqual(contract.route_catalog, command_mvp_flow_route_catalog())

    def test_command_mvp_surface_contract_stays_aligned_with_public_contract(self) -> None:
        public_contract = command_surface_contract()
        mvp_contract = command_mvp_surface_contract()
        self.assertEqual(mvp_contract, public_contract)
        self.assertEqual(mvp_contract, command_mvp_flow_contract())
        self.assertEqual(mvp_contract.flow_catalog, command_mvp_flow_catalog())
        self.assertEqual(mvp_contract.lookup_surface, command_mvp_flow_lookup_surface())
        self.assertEqual(mvp_contract.flow_surface_tokens, command_mvp_flow_surface_tokens())

    def test_command_manifest_keeps_catalog_order(self) -> None:
        manifest = command_manifest()
        self.assertEqual(
            tuple(entry.flow_step for entry in manifest),
            ("project-open", "patch-review", "retrieval", "export-handoff", "plan-revision", "persist-save", "session-resume"),
        )
        self.assertEqual(
            tuple(entry.name for entry in manifest),
            ("bootstrap", "diff-preview", "context-basket", "terminal", "revise", "session-save", "session-resume"),
        )

    def test_command_mvp_flow_manifest_matches_the_demo_sequence(self) -> None:
        manifest = command_mvp_flow_manifest()
        self.assertEqual(
            tuple(entry.flow_step for entry in manifest),
            ("project-open", "retrieval", "patch-review", "export-handoff", "plan-revision", "persist-save", "session-resume"),
        )
        self.assertEqual(
            tuple(entry.name for entry in manifest),
            ("bootstrap", "context-basket", "diff-preview", "terminal", "revise", "session-save", "session-resume"),
        )

    def test_mvp_flow_helpers_expose_the_expected_sequence(self) -> None:
        self.assertEqual(
            command_mvp_flow_steps(),
            ("project-open", "retrieval", "patch-review", "export-handoff", "plan-revision", "persist-save", "session-resume"),
        )
        self.assertEqual(
            command_mvp_flow_names(),
            ("bootstrap", "context-basket", "diff-preview", "terminal", "revise", "session-save", "session-resume"),
        )
        self.assertEqual(
            tuple(entry.name for entry in command_mvp_flow()),
            command_mvp_flow_names(),
        )

    def test_mvp_flow_catalog_rejects_missing_flow_steps(self) -> None:
        with self.assertRaisesRegex(ValueError, "Missing command flow steps"):
            command_mvp_flow_catalog(
                (
                    CommandSpec(name="bootstrap", flow_step="project-open"),
                    CommandSpec(name="diff-preview", flow_step="patch-review"),
                    CommandSpec(name="terminal", flow_step="export-handoff"),
                )
            )

    def test_command_flow_manifest_rejects_duplicate_requested_flow_steps(self) -> None:
        with self.assertRaisesRegex(ValueError, "Duplicate command flow step order"):
            command_flow_manifest(flow_steps=("project-open", "project-open"))

    def test_command_flow_manifest_rejects_empty_requested_flow_steps(self) -> None:
        with self.assertRaisesRegex(ValueError, "Command flow steps must not be empty"):
            command_flow_manifest(flow_steps=("project-open", " ", "export-handoff"))

    def test_command_flow_projections_normalize_custom_flow_steps(self) -> None:
        specs = (
            CommandSpec(name="bootstrap", flow_step=" Project Open "),
            CommandSpec(name="context-basket", flow_step="Retrieval"),
            CommandSpec(name="diff-preview", flow_step="Patch Review"),
            CommandSpec(name="terminal", flow_step="Export Handoff"),
            CommandSpec(name="revise", flow_step=" Plan Revision "),
            CommandSpec(name="session-save", flow_step="Persist Save"),
            CommandSpec(name="session-resume", flow_step="Session Resume"),
        )

        self.assertEqual(
            command_flow_steps(specs),
            ("project-open", "retrieval", "patch-review", "export-handoff", "plan-revision", "persist-save", "session-resume"),
        )
        self.assertEqual(
            tuple(entry.flow_step for entry in command_flow_manifest(specs)),
            ("project-open", "retrieval", "patch-review", "export-handoff", "plan-revision", "persist-save", "session-resume"),
        )
        self.assertEqual(
            command_flow_lookup_table(specs),
            (
                ("project-open", "bootstrap"),
                ("retrieval", "context-basket"),
                ("patch-review", "diff-preview"),
                ("export-handoff", "terminal"),
                ("plan-revision", "revise"),
                ("persist-save", "session-save"),
                ("session-resume", "session-resume"),
            ),
        )
        self.assertEqual(
            tuple(entry.flow_step for entry in command_mvp_flow_catalog(specs)),
            ("project-open", "retrieval", "patch-review", "export-handoff", "plan-revision", "persist-save", "session-resume"),
        )

    def test_validate_command_catalog_rejects_ambiguous_definitions(self) -> None:
        with self.assertRaisesRegex(ValueError, "Duplicate command name"):
            validate_command_catalog(
                (
                    CommandSpec(name="bootstrap", flow_step="project-open"),
                    CommandSpec(name="bootstrap", flow_step="retrieval"),
                )
            )

        with self.assertRaisesRegex(ValueError, "Duplicate command flow step"):
            validate_command_catalog(
                (
                    CommandSpec(name="bootstrap", flow_step="project-open"),
                    CommandSpec(name="context-basket", flow_step="project-open"),
                )
            )

        with self.assertRaisesRegex(ValueError, "Duplicate command lookup alias"):
            validate_command_catalog(
                (
                    CommandSpec(name="bootstrap", aliases=("open",), flow_step="project-open"),
                    CommandSpec(name="diff-preview", aliases=("open",), flow_step="patch-review"),
                )
            )

        with self.assertRaisesRegex(ValueError, "Duplicate command lookup token"):
            validate_command_catalog(
                (
                    CommandSpec(name="bootstrap", aliases=("open",), flow_step="project-open"),
                    CommandSpec(name="project-open", flow_step="retrieval"),
                )
            )

    def test_canonical_demo_path_gap_reasons_exclude_supplemental_steps(self) -> None:
        supplemental_steps = {
            demo_step
            for demo_step, _flow_step, _argv
            in command_catalog.CANONICAL_DEMO_PATH_SUPPLEMENTAL_COMMANDS
        }
        gap_reason_steps = {
            step for step, _reason in command_catalog.CANONICAL_DEMO_PATH_GAP_REASONS
        }
        overlap = supplemental_steps & gap_reason_steps
        self.assertEqual(
            overlap,
            set(),
            f"Gap reasons include steps already covered by supplemental commands: {overlap}",
        )

    def test_canonical_step_statuses_match_coverage(self) -> None:
        from src.qual.commands.catalog import command_demo_path_handoff_summary
        summary = command_demo_path_handoff_summary()
        covered = {s.demo_step for s in summary.canonical_step_statuses if s.covered}
        missing = {s.demo_step for s in summary.canonical_step_statuses if not s.covered}
        self.assertIn("open-project-document", covered)
        self.assertIn("retrieve-relevant-material", covered)
        self.assertIn("promote-or-gather-context-into-basket", covered)
        # patch-review gap is closed: diff-preview apply/reject cover all three outcomes.
        self.assertIn("preview-and-apply-or-reject-patch", covered)
        self.assertIn("produce-plan-or-revision", missing)
        self.assertIn("persist-updated-document-session-state", missing)
        self.assertIn("continue-without-losing-context", missing)


class CommandArgvNormalizationScopeTests(unittest.TestCase):
    def _load_engine_cli(self) -> object:
        import importlib.util
        import os
        import types

        engine_cli_key = "exegesis_engine.api.cli._isolated_smoke"
        sys_mod = __import__("sys")
        if engine_cli_key not in sys_mod.modules:
            if "exegesis_engine" not in sys_mod.modules:
                stub = types.ModuleType("exegesis_engine")
                stub.__path__ = [os.path.join(os.path.dirname(__file__), "..", "..", "engine", "src", "exegesis_engine")]  # type: ignore[attr-defined]
                stub.__package__ = "exegesis_engine"
                sys_mod.modules["exegesis_engine"] = stub
            worktree = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
            cli_path = os.path.join(worktree, "engine", "src", "exegesis_engine", "api", "cli.py")
            spec = importlib.util.spec_from_file_location(engine_cli_key, cli_path)
            mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
            sys_mod.modules[engine_cli_key] = mod
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return sys_mod.modules[engine_cli_key]

    def test_command_argv_normalization_is_used_by_the_executable_cli_parser(self) -> None:
        # _normalize_argv in cli.py calls normalize_command_argv so catalog
        # aliases reach argparse as canonical subcommand names.
        engine_cli = self._load_engine_cli()

        cases = [
            (["open"], "bootstrap"),
            (["project-open"], "bootstrap"),
            (["bootstrap"], "bootstrap"),
            (["basket", "list"], "context-basket"),
        ]
        for alias_argv, expected_command in cases:
            with self.subTest(alias_argv=alias_argv):
                result = engine_cli.parse_args(alias_argv)  # type: ignore[union-attr]
                self.assertEqual(result.command, expected_command)

    def test_patch_review_outcome_contract_all_outcomes_are_covered(self) -> None:
        # apply and reject gaps are closed: diff-preview apply/reject routes now exist.
        from src.qual.commands.catalog import (
            PATCH_REVIEW_OUTCOME_COMMANDS,
            PATCH_REVIEW_REQUIRED_OUTCOMES,
        )
        covered_outcomes = {outcome for outcome, _ in PATCH_REVIEW_OUTCOME_COMMANDS}
        for outcome in ("preview", "apply", "reject"):
            self.assertIn(outcome, covered_outcomes, f"{outcome} must have a route in PATCH_REVIEW_OUTCOME_COMMANDS")
            self.assertIn(outcome, PATCH_REVIEW_REQUIRED_OUTCOMES)

    def test_patch_review_outcome_commands_are_parseable_by_the_cli(self) -> None:
        engine_cli = self._load_engine_cli()

        from src.qual.commands.catalog import PATCH_REVIEW_OUTCOME_COMMANDS

        for outcome, argv in PATCH_REVIEW_OUTCOME_COMMANDS:
            with self.subTest(outcome=outcome, argv=argv):
                result = engine_cli.parse_args(list(argv))
                self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
