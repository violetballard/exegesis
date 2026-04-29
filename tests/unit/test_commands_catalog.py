from __future__ import annotations

import unittest
from unittest.mock import patch

import src.qual.cli as cli
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
    command_mvp_smoke_argv,
    command_mvp_smoke_command_lines,
    command_mvp_smoke_commands,
    command_mvp_smoke_contract,
    command_mvp_smoke_lookup_table,
    command_mvp_demo_path_command_lines,
    command_mvp_demo_path_contract,
    command_mvp_demo_path_action_lookup_table,
    command_mvp_demo_path_cli_lookup_table,
    command_mvp_demo_path_command_lookup_table,
    command_mvp_demo_path_engine_handoffs,
    command_mvp_demo_path_handoff_lookup_table,
    command_mvp_demo_path_lookup_contract,
    command_mvp_demo_path_lookup_table,
    command_mvp_demo_path_steps,
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
    def _clear_cli_caches(self) -> None:
        command_catalog.command_cli_tokens.cache_clear()
        command_catalog.command_cli_lookup_table.cache_clear()
        command_catalog.command_cli_contract.cache_clear()

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

    def test_command_cli_lookup_table_exposes_the_parser_surface(self) -> None:
        self.assertEqual(
            command_cli_lookup_table(),
            (
                ("bootstrap", "bootstrap"),
                ("diff-preview", "diff-preview"),
                ("diff", "diff-preview"),
                ("context-basket", "context-basket"),
                ("terminal", "terminal"),
            ),
        )

    def test_actual_argparse_surface_matches_the_command_contract(self) -> None:
        self.assertEqual(cli.command_parser_lookup_table(), command_cli_lookup_table())
        self.assertEqual(cli.command_parser_tokens(), command_cli_tokens())

    def test_command_cli_contract_matches_the_catalog_order(self) -> None:
        contract = command_cli_contract()
        self.assertEqual(contract.tokens, command_cli_tokens())
        self.assertEqual(contract.canonical_names, command_names())
        self.assertEqual(contract.lookup_table, command_cli_lookup_table())
        self.assertEqual(cli.command_parser_lookup_table(), command_cli_lookup_table())

    def test_command_cli_contract_rejects_actual_add_parser_token_drift(self) -> None:
        self._clear_cli_caches()
        original_add_parser = cli.argparse._SubParsersAction.add_parser

        def drift_add_parser(
            subparsers: cli.argparse._SubParsersAction,
            name: str,
            *args: object,
            **kwargs: object,
        ) -> cli.argparse.ArgumentParser:
            if getattr(subparsers, "dest", None) == "command" and name == "diff-preview":
                name = "diff-live"
            return original_add_parser(subparsers, name, *args, **kwargs)

        with patch.object(cli.argparse._SubParsersAction, "add_parser", new=drift_add_parser):
            with self.assertRaisesRegex(ValueError, "Command CLI parser surface is inconsistent"):
                command_catalog.command_cli_contract()

    def test_command_cli_contract_rejects_actual_parser_extra_token_drift(self) -> None:
        self._clear_cli_caches()
        parser = cli._build_parser()
        choices = cli._command_subparser_action(parser).choices
        choices["diff-live"] = choices["diff-preview"]
        with patch.object(cli, "_build_parser", return_value=parser):
            with self.assertRaisesRegex(ValueError, "Command CLI parser surface is inconsistent"):
                command_catalog.command_cli_contract()

    def test_command_cli_contract_rejects_actual_parser_missing_token_drift(self) -> None:
        self._clear_cli_caches()
        parser = cli._build_parser()
        choices = cli._command_subparser_action(parser).choices
        choices.pop("terminal")
        with patch.object(cli, "_build_parser", return_value=parser):
            with self.assertRaisesRegex(ValueError, "Command CLI parser surface is inconsistent"):
                command_catalog.command_cli_contract()

    def test_command_cli_contract_rejects_catalog_drift(self) -> None:
        self._clear_cli_caches()
        with patch.object(command_catalog, "command_names", return_value=("bootstrap", "diff-preview")):
            with self.assertRaisesRegex(ValueError, "Command CLI canonical names are inconsistent"):
                command_catalog.command_cli_contract()

    def test_command_cli_tokens_reject_duplicate_entrypoints(self) -> None:
        specs = (
            CommandSpec(name="bootstrap", aliases=("open",), flow_step="project-open", cli_tokens=("bootstrap",)),
            CommandSpec(name="review", aliases=("patch",), flow_step="patch-review", cli_tokens=("bootstrap",)),
        )
        with self.assertRaisesRegex(ValueError, "Duplicate command CLI entrypoint: bootstrap"):
            command_catalog.command_cli_tokens(specs)

    def test_command_cli_lookup_table_resolves_through_the_catalog(self) -> None:
        self.assertEqual(
            command_cli_lookup_table(),
            tuple((token, canonical_command(token)) for token in command_cli_tokens()),
        )

    def test_command_cli_tokens_reject_unknown_entrypoints(self) -> None:
        command_catalog.command_cli_tokens.cache_clear()
        specs = (
            CommandSpec(name="bootstrap", aliases=("open",), flow_step="project-open", cli_tokens=("not-a-command",)),
        )
        with self.assertRaisesRegex(ValueError, "Unknown CLI command entrypoint: not-a-command"):
            command_catalog.command_cli_tokens(specs)

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
            ),
        )
        self.assertEqual(
            tuple(entry.lookup_tokens for entry in flow),
            (
                ("bootstrap", "open", "project-open", "project"),
                ("context-basket", "context", "basket"),
                ("diff-preview", "diff", "diff_preview"),
                ("terminal",),
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

    def test_public_mvp_smoke_exports_track_the_demo_path(self) -> None:
        contract = command_mvp_smoke_contract()
        self.assertEqual(
            tuple((step.flow_step, step.name, step.cli_token, step.argv) for step in contract.steps),
            (
                ("project-open", "bootstrap", "bootstrap", ("bootstrap",)),
                ("retrieval", "context-basket", "context-basket", ("context-basket", "list")),
                ("patch-review", "diff-preview", "diff-preview", ("diff-preview",)),
                ("export-handoff", "terminal", "terminal", ("terminal",)),
            ),
        )
        self.assertEqual(command_mvp_smoke_commands(), contract.command_tokens)
        self.assertEqual(command_mvp_smoke_argv(), contract.argv)
        self.assertEqual(command_mvp_smoke_command_lines(), contract.command_lines)
        self.assertEqual(command_mvp_smoke_lookup_table(), contract.lookup_table)
        self.assertEqual(
            command_mvp_smoke_command_lines(),
            ("bootstrap", "context-basket list", "diff-preview", "terminal"),
        )
        self.assertEqual(
            contract.lookup_table,
            (
                ("bootstrap", "project-open"),
                ("context-basket", "retrieval"),
                ("diff-preview", "patch-review"),
                ("terminal", "export-handoff"),
            ),
        )

    def test_public_mvp_demo_path_exports_document_engine_handoffs(self) -> None:
        contract = command_mvp_demo_path_contract()
        self.assertEqual(command_mvp_demo_path_steps(), contract.steps)
        self.assertEqual(command_mvp_demo_path_command_lines(), contract.command_lines)
        self.assertEqual(command_mvp_demo_path_engine_handoffs(), contract.engine_handoffs)
        self.assertEqual(
            tuple(
                (
                    step.flow_step,
                    step.command_line,
                    step.operator_checkpoint,
                    step.engine_handoff,
                )
                for step in contract.steps
            ),
            (
                (
                    "project-open",
                    "bootstrap",
                    "open project/document",
                    "engine project bootstrap/open",
                ),
                (
                    "retrieval",
                    "context-basket list",
                    "retrieve relevant material",
                    "engine retrieval context selection",
                ),
                (
                    "patch-review",
                    "diff-preview",
                    "preview and accept or reject patch",
                    "engine patch preview and apply/reject decision",
                ),
                (
                    "export-handoff",
                    "terminal",
                    "persist and continue through export handoff",
                    "engine export handoff routing",
                ),
            ),
        )

    def test_public_mvp_demo_path_lookup_exports_are_stable(self) -> None:
        contract = command_mvp_demo_path_lookup_contract()
        demo_path = command_mvp_demo_path_contract()

        self.assertEqual(command_mvp_demo_path_lookup_table(), contract.by_flow_step)
        self.assertEqual(command_mvp_demo_path_command_lookup_table(), contract.by_command_name)
        self.assertEqual(command_mvp_demo_path_cli_lookup_table(), contract.by_cli_token)
        self.assertEqual(command_mvp_demo_path_action_lookup_table(), contract.action_lookup)
        self.assertEqual(command_mvp_demo_path_handoff_lookup_table(), contract.handoff_lookup)
        self.assertEqual(
            contract.by_flow_step,
            tuple((step.flow_step, step) for step in demo_path.steps),
        )
        self.assertEqual(
            tuple((flow_step, step.name, step.cli_token) for flow_step, step in contract.by_flow_step),
            (
                ("project-open", "bootstrap", "bootstrap"),
                ("retrieval", "context-basket", "context-basket"),
                ("patch-review", "diff-preview", "diff-preview"),
                ("export-handoff", "terminal", "terminal"),
            ),
        )
        self.assertEqual(
            contract.action_lookup,
            (
                ("project-open", ("open_project",)),
                ("retrieval", ("retrieve_context",)),
                ("patch-review", ("preview_patch", "apply_patch", "reject_patch")),
                ("export-handoff", ("persist_session", "export_handoff")),
            ),
        )
        self.assertEqual(
            contract.handoff_lookup,
            (
                ("project-open", "engine project bootstrap/open"),
                ("retrieval", "engine retrieval context selection"),
                ("patch-review", "engine patch preview and apply/reject decision"),
                ("export-handoff", "engine export handoff routing"),
            ),
        )

    def test_command_manifest_keeps_catalog_order(self) -> None:
        manifest = command_manifest()
        self.assertEqual(
            tuple(entry.flow_step for entry in manifest),
            ("project-open", "patch-review", "retrieval", "export-handoff"),
        )
        self.assertEqual(
            tuple(entry.name for entry in manifest),
            ("bootstrap", "diff-preview", "context-basket", "terminal"),
        )

    def test_command_mvp_flow_manifest_matches_the_demo_sequence(self) -> None:
        manifest = command_mvp_flow_manifest()
        self.assertEqual(
            tuple(entry.flow_step for entry in manifest),
            ("project-open", "retrieval", "patch-review", "export-handoff"),
        )
        self.assertEqual(
            tuple(entry.name for entry in manifest),
            ("bootstrap", "context-basket", "diff-preview", "terminal"),
        )

    def test_mvp_flow_helpers_expose_the_expected_sequence(self) -> None:
        self.assertEqual(
            command_mvp_flow_steps(),
            ("project-open", "retrieval", "patch-review", "export-handoff"),
        )
        self.assertEqual(
            command_mvp_flow_names(),
            ("bootstrap", "context-basket", "diff-preview", "terminal"),
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
        )

        self.assertEqual(
            command_flow_steps(specs),
            ("project-open", "retrieval", "patch-review", "export-handoff"),
        )
        self.assertEqual(
            tuple(entry.flow_step for entry in command_flow_manifest(specs)),
            ("project-open", "retrieval", "patch-review", "export-handoff"),
        )
        self.assertEqual(
            command_flow_lookup_table(specs),
            (
                ("project-open", "bootstrap"),
                ("retrieval", "context-basket"),
                ("patch-review", "diff-preview"),
                ("export-handoff", "terminal"),
            ),
        )
        self.assertEqual(
            tuple(entry.flow_step for entry in command_mvp_flow_catalog(specs)),
            ("project-open", "retrieval", "patch-review", "export-handoff"),
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


if __name__ == "__main__":
    unittest.main()
