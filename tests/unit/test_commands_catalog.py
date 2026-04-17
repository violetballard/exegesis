from __future__ import annotations

import unittest
from dataclasses import replace
from unittest.mock import patch

import src.qual.commands.catalog as command_catalog
from src.qual.commands import (
    CommandCliFlowContract,
    CommandInvocationPlanContract,
    CommandSpec,
    canonical_command,
    canonical_command_for,
    command_aliases,
    command_aliases_for,
    command_cli_contract,
    command_cli_flow_contract,
    command_cli_flow_lookup_table,
    command_cli_shim_catalog,
    command_cli_shim_contract,
    command_cli_shim_invocation_table,
    command_cli_shim_lookup_table,
    command_cli_shim_primary_token,
    command_cli_shim_primary_token_for,
    command_cli_shim_argv,
    command_cli_shim_argv_for,
    command_cli_entry_argv,
    command_cli_entry_argv_for,
    command_cli_surface_catalog,
    command_cli_surface_contract,
    command_cli_tokens,
    command_cli_tokens_for,
    command_cli_primary_tokens,
    command_cli_route_catalog,
    command_cli_route_contract,
    command_cli_route_flow_lookup_table,
    command_cli_route_lookup_table,
    command_cli_route_summary,
    command_flow_manifest,
    command_flow_catalog,
    command_flow_invocation_contract,
    command_flow_invocation_plan,
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
    command_resolution_lookup_index,
    command_resolution_lookup_table,
    command_lookup_table,
    command_lookup_tokens,
    command_lookup_tokens_for,
    command_resolve,
    command_resolve_argv,
    command_resolve_argv_for,
    command_resolve_for,
    command_resolution_lookup_tokens,
    command_resolution_tokens,
    command_resolution_tokens_for,
    command_manifest,
    command_mvp_flow,
    command_mvp_cli_flow_contract,
    command_mvp_cli_route_contract,
    command_mvp_flow_names,
    command_mvp_flow_catalog,
    command_mvp_flow_manifest,
    command_mvp_flow_contract,
    command_mvp_flow_invocation_contract,
    command_mvp_flow_invocation_plan,
    command_mvp_flow_lookup_surface,
    command_mvp_flow_route_catalog,
    command_mvp_flow_route_contract,
    command_mvp_flow_route_summary,
    command_mvp_flow_route_tokens,
    command_mvp_flow_surface_lookup_index,
    command_mvp_flow_surface_tokens,
    command_mvp_flow_lookup_table,
    command_mvp_flow_tokens,
    command_mvp_flow_sequence,
    command_mvp_flow_steps,
    command_mvp_lookup_index,
    command_mvp_surface_contract,
    command_surface_contract,
    command_demo_flow_route_catalog,
    command_demo_flow_invocation_contract,
    command_demo_flow_invocation_plan,
    command_demo_flow_route_contract,
    command_demo_flow_route_summary,
    command_demo_flow_route_tokens,
    command_demo_cli_flow_contract,
    command_demo_cli_entry_argv,
    command_demo_cli_shim_catalog,
    command_demo_cli_shim_contract,
    command_demo_cli_surface_catalog,
    command_demo_cli_surface_contract,
    command_demo_cli_route_catalog,
    command_demo_cli_route_contract,
    command_demo_cli_route_summary,
    command_demo_path_contract,
    command_demo_path_invocation_plan,
    command_demo_preferred_surface_invocation_table,
    command_demo_resolve,
    command_demo_resolve_argv,
    command_demo_flow_surface_tokens,
    command_demo_smoke_argv,
    command_demo_smoke_contract,
    command_demo_compatibility_contract,
    command_demo_compatibility_catalog,
    command_demo_compatibility_tokens,
    command_demo_compatibility_lookup_table,
    command_demo_compatibility_invocation_table,
    command_demo_loop_contract,
    command_demo_loop_catalog,
    command_demo_loop_invocation_plan,
    command_demo_loop_lookup_table,
    command_demo_loop_tokens,
    command_names,
    command_primary_cli_token_for,
    command_mvp_cli_shim_catalog,
    command_mvp_cli_shim_contract,
    command_mvp_cli_entry_argv,
    command_mvp_cli_surface_catalog,
    command_mvp_cli_surface_contract,
    command_mvp_cli_route_catalog,
    command_mvp_cli_route_summary,
    command_mvp_path_contract,
    command_mvp_preferred_surface_invocation_table,
    command_mvp_resolve,
    command_mvp_resolve_argv,
    command_spec,
    command_spec_for,
    command_specs,
    command_smoke_argv_for,
    command_smoke_entry_argv,
    command_smoke_contract,
    command_smoke_argv,
    command_tokens,
    command_flow_tokens,
    command_mvp_smoke_contract,
    command_mvp_compatibility_contract,
    command_mvp_compatibility_catalog,
    command_mvp_compatibility_tokens,
    command_mvp_compatibility_lookup_table,
    command_mvp_compatibility_invocation_table,
    command_mvp_loop_contract,
    command_mvp_loop_catalog,
    command_mvp_loop_invocation_plan,
    command_mvp_loop_lookup_table,
    command_mvp_loop_tokens,
    validate_command_catalog,
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
            "bootstrap-run": "bootstrap",
            "document-open": "bootstrap",
            "open-document": "bootstrap",
            "diff": "diff-preview",
            "diff_preview": "diff-preview",
            "review-patch": "diff-preview",
            "patch-review": "diff-preview",
            "context": "context-basket",
            "basket": "context-basket",
            "retrieval": "context-basket",
            "retrieve": "context-basket",
            "export": "terminal",
            "save-export": "terminal",
            "persist": "terminal",
            "persist-continue": "terminal",
            "apply-patch": "terminal",
            "patch-apply": "terminal",
            "reject-patch": "terminal",
            "patch-reject": "terminal",
            "export-handoff": "terminal",
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
        self.assertEqual(
            command_aliases("project-open"),
            ("open", "project-open", "project", "bootstrap-run", "document-open", "open-document"),
        )
        self.assertEqual(
            command_aliases("patch-review"),
            ("diff", "review-patch", "patch-review"),
        )
        self.assertEqual(
            command_aliases("export-handoff"),
            (
                "export",
                "save-export",
                "persist",
                "persist-continue",
                "apply-patch",
                "patch-apply",
                "reject-patch",
                "patch-reject",
                "export-handoff",
            ),
        )
        self.assertEqual(
            command_lookup_tokens("project-open"),
            ("bootstrap", "open", "project-open", "project", "bootstrap-run", "document-open", "open-document"),
        )
        self.assertEqual(command_aliases("missing"), ())
        self.assertEqual(command_lookup_tokens("missing"), ())
        self.assertEqual(
            command_resolution_lookup_tokens("project-open"),
            (
                "bootstrap",
                "open",
                "project-open",
                "project",
                "bootstrap-run",
                "document-open",
                "open-document",
                "bootstrap",
            ),
        )
        self.assertEqual(command_resolution_lookup_tokens("missing"), ())

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

    def test_command_cli_tokens_are_declared_per_command_spec(self) -> None:
        self.assertEqual(
            tuple((spec.name, spec.cli_tokens) for spec in command_specs()),
            (
                ("bootstrap", ("bootstrap",)),
                ("diff-preview", ("diff-preview", "diff")),
                ("context-basket", ("context-basket",)),
                ("terminal", ("terminal",)),
            ),
        )
        self.assertEqual(
            command_cli_tokens(),
            tuple(token for spec in command_specs() for token in spec.cli_tokens),
        )

    def test_command_cli_token_helpers_expose_deterministic_entrypoints(self) -> None:
        self.assertEqual(command_cli_tokens_for(command_specs(), "project-open"), ("bootstrap",))
        self.assertEqual(command_cli_tokens_for(command_specs(), "diff-preview"), ("diff-preview", "diff"))
        self.assertEqual(command_cli_tokens_for(command_specs(), "retrieval"), ("context-basket",))
        self.assertEqual(command_primary_cli_token_for(command_specs(), "export"), "terminal")
        self.assertEqual(
            command_cli_primary_tokens(),
            ("bootstrap", "diff-preview", "context-basket", "terminal"),
        )
        self.assertEqual(command_cli_tokens_for(command_specs(), "missing"), ())
        self.assertEqual(command_primary_cli_token_for(command_specs(), "missing"), "")

    def test_command_cli_contract_matches_the_catalog_order(self) -> None:
        contract = command_cli_contract()
        self.assertEqual(contract.tokens, command_cli_tokens())
        self.assertEqual(contract.canonical_names, ("bootstrap", "diff-preview", "context-basket", "terminal"))
        self.assertEqual(contract.lookup_table, command_cli_lookup_table())

    def test_command_cli_contract_rejects_missing_canonical_primary_token(self) -> None:
        command_catalog.command_cli_contract.cache_clear()
        with patch.object(
            command_catalog,
            "_validated_cli_entrypoints_for",
            return_value=(
                ("bootstrap", ("bootstrap",)),
                ("diff-preview", ("diff",)),
                ("context-basket", ("context-basket",)),
                ("terminal", ("terminal",)),
            ),
        ):
            with self.assertRaisesRegex(ValueError, "Command CLI parser surface is inconsistent"):
                command_catalog.command_cli_contract(command_specs())

    def test_command_cli_contract_rejects_alias_substitution_ahead_of_canonical_token(self) -> None:
        command_catalog.command_cli_contract.cache_clear()
        with patch.object(
            command_catalog,
            "_validated_cli_entrypoints_for",
            return_value=(
                ("bootstrap", ("bootstrap",)),
                ("diff-preview", ("diff", "diff-preview")),
                ("context-basket", ("context-basket",)),
                ("terminal", ("terminal",)),
            ),
        ):
            with self.assertRaisesRegex(ValueError, "Command CLI parser surface is inconsistent"):
                command_catalog.command_cli_contract(command_specs())

    def test_command_cli_contract_rejects_reordered_accepted_entrypoints(self) -> None:
        command_catalog.command_cli_contract.cache_clear()
        with patch.object(
            command_catalog,
            "_validated_cli_entrypoints_for",
            return_value=(
                ("bootstrap", ("bootstrap",)),
                ("diff-preview", ("diff", "diff-preview")),
                ("context-basket", ("context-basket",)),
                ("terminal", ("terminal",)),
            ),
        ):
            with self.assertRaisesRegex(ValueError, "Command CLI parser surface is inconsistent"):
                command_catalog.command_cli_contract(command_specs())

    def test_command_cli_contract_rejects_extra_accepted_entrypoint_drift(self) -> None:
        command_catalog.command_cli_contract.cache_clear()
        with patch.object(
            command_catalog,
            "_validated_cli_entrypoints_for",
            return_value=(
                ("bootstrap", ("bootstrap",)),
                ("diff-preview", ("diff-preview", "diff", "review-patch")),
                ("context-basket", ("context-basket",)),
                ("terminal", ("terminal",)),
            ),
        ):
            with self.assertRaisesRegex(ValueError, "Command CLI parser surface is inconsistent"):
                command_catalog.command_cli_contract(command_specs())

    def test_command_cli_contract_rejects_removed_expected_alias_entrypoint(self) -> None:
        command_catalog.command_cli_contract.cache_clear()
        with patch.object(
            command_catalog,
            "_validated_cli_entrypoints_for",
            return_value=(
                ("bootstrap", ("bootstrap",)),
                ("diff-preview", ("diff-preview",)),
                ("context-basket", ("context-basket",)),
                ("terminal", ("terminal",)),
            ),
        ):
            with self.assertRaisesRegex(ValueError, "Command CLI parser surface is inconsistent"):
                command_catalog.command_cli_contract(command_specs())

    def test_command_cli_contract_rejects_normalized_alias_substitution_drift(self) -> None:
        command_catalog.command_cli_contract.cache_clear()
        with patch.object(
            command_catalog,
            "_validated_cli_entrypoints_for",
            return_value=(
                ("bootstrap", ("bootstrap",)),
                ("diff-preview", ("diff-preview", "diff_preview")),
                ("context-basket", ("context-basket",)),
                ("terminal", ("terminal",)),
            ),
        ):
            with self.assertRaisesRegex(ValueError, "Command CLI parser surface is inconsistent"):
                command_catalog.command_cli_contract(command_specs())

    def test_command_cli_contract_rejects_primary_token_order_drift(self) -> None:
        command_catalog.command_cli_contract.cache_clear()
        with patch.object(
            command_catalog,
            "_validated_cli_entrypoints_for",
            return_value=(
                ("bootstrap", ("bootstrap",)),
                ("diff-preview", ("diff-preview", "diff")),
                ("context-basket", ("terminal",)),
                ("terminal", ("context-basket",)),
            ),
        ):
            with self.assertRaisesRegex(ValueError, "Command CLI parser surface is inconsistent"):
                command_catalog.command_cli_contract(command_specs())

    def test_command_cli_contract_preserves_cli_subset_order_without_requiring_full_catalog_equality(self) -> None:
        specs = (
            CommandSpec(
                name="bootstrap",
                aliases=("open",),
                cli_tokens=("project-open", "bootstrap-run"),
                flow_step="project-open",
            ),
            CommandSpec(
                name="catalog-only",
                aliases=("catalog",),
                cli_exposed=False,
                flow_step="internal-only",
            ),
            CommandSpec(
                name="review",
                aliases=("patch",),
                cli_tokens=("review-patch", "diff"),
                flow_step="patch-review",
            ),
        )

        contract = command_cli_contract(specs)
        self.assertEqual(
            command_names(specs),
            ("bootstrap", "catalog-only", "review"),
        )
        self.assertEqual(contract.canonical_names, ("bootstrap", "review"))
        self.assertEqual(contract.tokens, ("project-open", "bootstrap-run", "review-patch", "diff"))
        self.assertEqual(
            contract.lookup_table,
            (
                ("project-open", "bootstrap"),
                ("bootstrap-run", "bootstrap"),
                ("review-patch", "review"),
                ("diff", "review"),
            ),
        )
        self.assertEqual(command_cli_tokens_for(specs, "catalog-only"), ())
        self.assertEqual(command_primary_cli_token_for(specs, "catalog-only"), "")
        self.assertEqual(command_cli_primary_tokens(specs), ("project-open", "review-patch"))

    def test_command_cli_shim_lookup_table_rewrites_surface_tokens_to_primary_entrypoints(self) -> None:
        self.assertEqual(
            command_cli_shim_lookup_table(),
            (
                ("bootstrap", "bootstrap"),
                ("open", "bootstrap"),
                ("project-open", "bootstrap"),
                ("project", "bootstrap"),
                ("bootstrap-run", "bootstrap"),
                ("document-open", "bootstrap"),
                ("open-document", "bootstrap"),
                ("diff-preview", "diff-preview"),
                ("diff", "diff-preview"),
                ("review-patch", "diff-preview"),
                ("patch-review", "diff-preview"),
                ("context-basket", "context-basket"),
                ("context", "context-basket"),
                ("basket", "context-basket"),
                ("retrieval", "context-basket"),
                ("retrieve", "context-basket"),
                ("terminal", "terminal"),
                ("export", "terminal"),
                ("save-export", "terminal"),
                ("persist", "terminal"),
                ("persist-continue", "terminal"),
                ("apply-patch", "terminal"),
                ("patch-apply", "terminal"),
                ("reject-patch", "terminal"),
                ("patch-reject", "terminal"),
                ("export-handoff", "terminal"),
            ),
        )
        shim_invocations = dict(command_cli_shim_invocation_table())
        self.assertEqual(shim_invocations["bootstrap"], ("bootstrap",))
        self.assertEqual(
            shim_invocations["export"],
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Export handoff"),
        )
        self.assertEqual(
            shim_invocations["persist"],
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
        )
        self.assertEqual(
            shim_invocations["apply-patch"],
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
        )
        self.assertEqual(
            shim_invocations["patch-apply"],
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
        )
        self.assertEqual(
            shim_invocations["reject-patch"],
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
        )
        self.assertEqual(
            shim_invocations["patch-reject"],
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
        )

    def test_command_cli_shim_catalog_marks_surface_token_kinds(self) -> None:
        shim_catalog = command_cli_shim_catalog()
        shim_by_token = {entry.token: entry for entry in shim_catalog}
        self.assertEqual(shim_by_token["bootstrap"].kind, "primary")
        self.assertEqual(shim_by_token["open"].kind, "lookup")
        self.assertEqual(shim_by_token["project-open"].kind, "flow-step")
        self.assertEqual(shim_by_token["document-open"].kind, "lookup")
        self.assertEqual(shim_by_token["open-document"].kind, "lookup")
        self.assertEqual(shim_by_token["diff"].kind, "cli")
        self.assertEqual(shim_by_token["patch-review"].kind, "flow-step")
        self.assertEqual(
            shim_by_token["export-handoff"].argv,
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Export handoff"),
        )
        self.assertEqual(
            shim_by_token["persist"].argv,
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
        )
        self.assertEqual(
            shim_by_token["apply-patch"].argv,
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
        )
        self.assertEqual(shim_by_token["patch-apply"].kind, "lookup")
        self.assertEqual(
            shim_by_token["patch-apply"].argv,
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
        )
        self.assertEqual(shim_by_token["patch-reject"].kind, "lookup")
        self.assertEqual(
            shim_by_token["patch-reject"].argv,
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
        )

    def test_command_cli_shim_contract_matches_catalog_helpers(self) -> None:
        contract = command_cli_shim_contract()
        self.assertEqual(contract.entries, command_cli_shim_catalog())
        self.assertEqual(contract.lookup_table, command_cli_shim_lookup_table())
        self.assertEqual(contract.invocation_table, command_cli_shim_invocation_table())

    def test_command_cli_shim_validator_rejects_inconsistent_lookup_table(self) -> None:
        with self.assertRaisesRegex(ValueError, "Command CLI shim lookup table is inconsistent"):
            command_catalog._validate_command_cli_shim_contract(
                command_catalog.CommandCliShimContract(
                    entries=command_cli_shim_catalog(),
                    lookup_table=(("bootstrap", "diff-preview"),),
                    invocation_table=command_cli_shim_invocation_table(),
                ),
                command_specs(),
                None,
            )

    def test_command_cli_shim_helpers_rewrite_legacy_surface_tokens_to_primary_argv(self) -> None:
        self.assertEqual(command_cli_shim_primary_token("open"), "bootstrap")
        self.assertEqual(command_cli_shim_primary_token("project-open"), "bootstrap")
        self.assertEqual(command_cli_shim_primary_token("document-open"), "bootstrap")
        self.assertEqual(command_cli_shim_primary_token("open-document"), "bootstrap")
        self.assertEqual(command_cli_shim_primary_token("patch-review"), "diff-preview")
        self.assertEqual(command_cli_shim_primary_token("persist"), "terminal")
        self.assertEqual(command_cli_shim_primary_token("patch-apply"), "terminal")
        self.assertEqual(command_cli_shim_primary_token("patch-reject"), "terminal")
        self.assertEqual(command_cli_shim_primary_token("missing"), "")
        self.assertEqual(
            command_cli_shim_argv(["open", "--project", "demo"]),
            ("bootstrap", "--project", "demo"),
        )
        self.assertEqual(
            command_cli_shim_argv(("document-open", "--project", "demo")),
            ("bootstrap", "--project", "demo"),
        )
        self.assertEqual(
            command_cli_shim_argv(("open-document", "--project", "demo")),
            ("bootstrap", "--project", "demo"),
        )
        self.assertEqual(
            command_cli_shim_argv(("patch-review", "--original", "a", "--proposed", "b")),
            ("diff-preview", "--original", "a", "--proposed", "b"),
        )
        self.assertEqual(
            command_cli_shim_argv(("persist",)),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
        )
        self.assertEqual(
            command_cli_shim_argv(("terminal",)),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Export handoff"),
        )
        self.assertEqual(
            command_cli_shim_argv(("apply-patch",)),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
        )
        self.assertEqual(
            command_cli_shim_argv(("patch-apply",)),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
        )
        self.assertEqual(
            command_cli_shim_argv(("export", "--message", "Custom handoff")),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Custom handoff"),
        )
        self.assertEqual(
            command_cli_shim_argv(("persist", "--message", "Resume later")),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Resume later"),
        )
        self.assertEqual(
            command_cli_shim_argv(("export", "--message=Queued for export")),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message=Queued for export"),
        )
        self.assertEqual(
            command_cli_shim_argv(("apply-patch", "--operation-kind=terminal_synthesis_request")),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
        )
        self.assertEqual(
            command_cli_shim_argv(("patch-reject", "--operation-kind=terminal_synthesis_request")),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
        )
        self.assertEqual(
            command_cli_shim_argv(
                ("apply-patch", "--message", "Now", "--operation-kind", "terminal_synthesis_request")
            ),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Now"),
        )
        self.assertEqual(
            command_cli_shim_argv(("persist", "--operation-kind", "terminal_tool_orchestration")),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
        )
        self.assertEqual(command_cli_shim_argv(["--project", "demo"]), ("--project", "demo"))
        self.assertEqual(command_cli_shim_argv(()), ())

    def test_command_cli_entry_argv_normalizes_parser_ready_invocations(self) -> None:
        self.assertEqual(command_cli_entry_argv(()), ("bootstrap",))
        self.assertEqual(command_cli_entry_argv(["bootstrap"]), ("bootstrap",))
        self.assertEqual(command_cli_entry_argv(["context-basket"]), ("context-basket", "list"))
        self.assertEqual(command_cli_entry_argv(["retrieve"]), ("context-basket", "list"))
        self.assertEqual(command_cli_entry_argv(["retrieval"]), ("context-basket", "list"))
        self.assertEqual(
            command_cli_entry_argv(["terminal"]),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Export handoff"),
        )
        self.assertEqual(
            command_cli_entry_argv(["patch-review"]),
            ("diff-preview",),
        )
        self.assertEqual(
            command_cli_entry_argv(["export"]),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Export handoff"),
        )
        self.assertEqual(
            command_cli_entry_argv(["persist"]),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
        )
        self.assertEqual(
            command_cli_entry_argv(["apply-patch"]),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
        )
        self.assertEqual(
            command_cli_entry_argv(["patch-apply"]),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
        )
        self.assertEqual(
            command_cli_entry_argv(["reject-patch"]),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
        )
        self.assertEqual(
            command_cli_entry_argv(["patch-reject"]),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
        )
        self.assertEqual(
            command_cli_entry_argv(["--project", "demo"]),
            ("bootstrap", "--project", "demo"),
        )
        self.assertEqual(
            command_cli_entry_argv(["open", "--project", "demo"]),
            ("bootstrap", "--project", "demo"),
        )
        self.assertEqual(
            command_cli_entry_argv(("document-open", "--project", "demo")),
            ("bootstrap", "--project", "demo"),
        )
        self.assertEqual(
            command_cli_entry_argv(("open-document", "--project", "demo")),
            ("bootstrap", "--project", "demo"),
        )
        self.assertEqual(
            command_cli_entry_argv(("patch-review", "--original", "a", "--proposed", "b")),
            ("diff-preview", "--original", "a", "--proposed", "b"),
        )
        self.assertEqual(
            command_cli_entry_argv(("export-handoff", "--message", "Queued for export")),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Queued for export"),
        )
        self.assertEqual(
            command_cli_entry_argv(("persist", "--message=Resume later")),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message=Resume later"),
        )
        self.assertEqual(
            command_cli_entry_argv(("apply-patch", "--operation-kind", "terminal_synthesis_request")),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
        )
        self.assertEqual(
            command_cli_entry_argv(("patch-reject", "--operation-kind", "terminal_synthesis_request")),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
        )
        self.assertEqual(
            command_cli_entry_argv(("missing", "--format", "json")),
            ("missing", "--format", "json"),
        )
        self.assertEqual(
            command_cli_entry_argv(("terminal", "--operation-kind", "terminal_tool_orchestration")),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Export handoff"),
        )

    def test_command_resolve_reports_deterministic_surface_metadata(self) -> None:
        resolved = command_resolve("patch-review")
        self.assertTrue(resolved.matched)
        self.assertEqual(resolved.canonical_name, "diff-preview")
        self.assertEqual(resolved.flow_step, "patch-review")
        self.assertEqual(resolved.primary_cli_token, "diff-preview")
        self.assertEqual(resolved.argv, ("diff-preview",))
        self.assertEqual(resolved.cli_tokens, ("diff-preview", "diff"))
        self.assertEqual(
            resolved.lookup_tokens,
            ("diff-preview", "diff", "diff_preview", "review-patch"),
        )
        self.assertEqual(
            resolved.surface_tokens,
            ("diff-preview", "diff", "review-patch", "patch-review"),
        )
        self.assertEqual(resolved.kind, "flow-step")

        lookup_resolved = command_resolve("review-patch")
        self.assertTrue(lookup_resolved.matched)
        self.assertEqual(lookup_resolved.primary_cli_token, "diff-preview")
        self.assertEqual(lookup_resolved.argv, ("diff-preview",))
        self.assertEqual(lookup_resolved.kind, "lookup")

        normalized_lookup = command_resolve("diff_preview")
        self.assertTrue(normalized_lookup.matched)
        self.assertEqual(normalized_lookup.primary_cli_token, "diff-preview")
        self.assertEqual(normalized_lookup.kind, "lookup")

        document_open = command_resolve("document-open")
        self.assertTrue(document_open.matched)
        self.assertEqual(document_open.primary_cli_token, "bootstrap")
        self.assertEqual(document_open.kind, "lookup")
        self.assertEqual(
            document_open.surface_tokens,
            ("bootstrap", "open", "project-open", "project", "bootstrap-run", "document-open", "open-document"),
        )

        primary = command_resolve("DIFF-PREVIEW")
        self.assertTrue(primary.matched)
        self.assertEqual(primary.primary_cli_token, "diff-preview")
        self.assertEqual(primary.kind, "primary")

        persist = command_resolve("persist")
        self.assertTrue(persist.matched)
        self.assertEqual(persist.canonical_name, "terminal")
        self.assertEqual(persist.flow_step, "export-handoff")
        self.assertEqual(persist.primary_cli_token, "terminal")
        self.assertEqual(
            persist.argv,
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
        )
        self.assertEqual(
            persist.smoke_argv,
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
        )
        self.assertEqual(persist.kind, "lookup")

    def test_command_resolve_argv_rewrites_to_primary_cli_tokens(self) -> None:
        resolved = command_resolve_argv(("review-patch", "--format", "json"))
        self.assertTrue(resolved.matched)
        self.assertEqual(resolved.canonical_name, "diff-preview")
        self.assertEqual(resolved.argv, ("diff-preview", "--format", "json"))
        self.assertEqual(resolved.kind, "lookup")

        flag = command_resolve_argv(("--project", "demo"))
        self.assertFalse(flag.matched)
        self.assertEqual(flag.kind, "flag")
        self.assertEqual(flag.argv, ("--project", "demo"))

        unknown = command_resolve_argv(("missing", "--format", "json"))
        self.assertFalse(unknown.matched)
        self.assertEqual(unknown.canonical_name, "missing")
        self.assertEqual(unknown.kind, "unknown")
        self.assertEqual(unknown.argv, ("missing", "--format", "json"))

        normalized_lookup = command_resolve_argv(("diff_preview", "--format", "json"))
        self.assertTrue(normalized_lookup.matched)
        self.assertEqual(normalized_lookup.argv, ("diff-preview", "--format", "json"))
        self.assertEqual(normalized_lookup.kind, "lookup")

        document_open = command_resolve_argv(("document-open", "--project", "demo"))
        self.assertTrue(document_open.matched)
        self.assertEqual(document_open.argv, ("bootstrap", "--project", "demo"))
        self.assertEqual(document_open.kind, "lookup")

        persist = command_resolve_argv(("persist",))
        self.assertTrue(persist.matched)
        self.assertEqual(
            persist.argv,
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
        )
        self.assertEqual(persist.kind, "lookup")

        terminal = command_resolve_argv(("terminal", "--operation-kind", "terminal_tool_orchestration"))
        self.assertTrue(terminal.matched)
        self.assertEqual(
            terminal.argv,
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Export handoff"),
        )
        self.assertEqual(terminal.kind, "primary")

    def test_document_open_aliases_resolve_to_bootstrap_parser_entrypoint(self) -> None:
        for token in ("document-open", "open-document"):
            with self.subTest(token=token):
                resolved = command_resolve(token)
                self.assertTrue(resolved.matched)
                self.assertEqual(resolved.canonical_name, "bootstrap")
                self.assertEqual(resolved.flow_step, "project-open")
                self.assertEqual(resolved.primary_cli_token, "bootstrap")
                self.assertEqual(resolved.argv, ("bootstrap",))
                self.assertEqual(resolved.smoke_argv, ("bootstrap", "--project", "demo"))
                self.assertEqual(resolved.kind, "lookup")

                argv_resolved = command_resolve_argv((token, "--project", "demo"))
                self.assertTrue(argv_resolved.matched)
                self.assertEqual(argv_resolved.argv, ("bootstrap", "--project", "demo"))
                self.assertEqual(argv_resolved.kind, "lookup")

                self.assertEqual(command_cli_entry_argv((token,)), ("bootstrap",))
                self.assertEqual(
                    command_cli_entry_argv((token, "--project", "demo")),
                    ("bootstrap", "--project", "demo"),
                )

    def test_command_demo_resolve_helpers_preserve_parser_ready_smoke_defaults(self) -> None:
        resolved = command_demo_resolve("patch-review")
        self.assertTrue(resolved.matched)
        self.assertEqual(
            resolved.argv,
            ("diff-preview", "--original", "before", "--proposed", "after"),
        )
        self.assertEqual(resolved.kind, "flow-step")

        patch_review = command_demo_resolve_argv(("patch-review", "--format=json"))
        self.assertTrue(patch_review.matched)
        self.assertEqual(
            patch_review.argv,
            ("diff-preview", "--original", "before", "--proposed", "after", "--format=json"),
        )
        self.assertEqual(patch_review.smoke_argv, ("diff-preview", "--original", "before", "--proposed", "after"))

        project_open = command_demo_resolve_argv(("project-open", "--project", "workspace"))
        self.assertTrue(project_open.matched)
        self.assertEqual(project_open.argv, ("bootstrap", "--project", "workspace"))
        self.assertEqual(project_open.smoke_argv, ("bootstrap", "--project", "demo"))

        export_handoff = command_demo_resolve_argv(("export-handoff", "--message", "Queued for export"))
        self.assertTrue(export_handoff.matched)
        self.assertEqual(
            export_handoff.argv,
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Queued for export"),
        )
        self.assertEqual(
            export_handoff.smoke_argv,
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Export handoff"),
        )

        self.assertEqual(command_mvp_resolve("patch-review"), resolved)
        self.assertEqual(command_mvp_resolve_argv(("patch-review", "--format=json")), patch_review)

    def test_command_demo_resolve_helpers_preserve_requested_compatibility_tokens(self) -> None:
        review = command_demo_resolve("review")
        self.assertTrue(review.matched)
        self.assertEqual(review.token, "review")
        self.assertEqual(review.normalized_token, "review")
        self.assertEqual(review.kind, "flow-step")
        self.assertEqual(
            review.argv,
            ("diff-preview", "--original", "before", "--proposed", "after"),
        )

        save = command_demo_resolve("save")
        self.assertTrue(save.matched)
        self.assertEqual(save.token, "save")
        self.assertEqual(save.normalized_token, "save")
        self.assertEqual(save.kind, "lookup")
        self.assertEqual(
            save.argv,
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
        )

        resume = command_demo_resolve("resume")
        self.assertTrue(resume.matched)
        self.assertEqual(resume.token, "resume")
        self.assertEqual(resume.normalized_token, "resume")
        self.assertEqual(resume.kind, "lookup")
        self.assertEqual(
            resume.argv,
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
        )

        apply = command_demo_resolve_argv(("apply", "--message", "Now"))
        self.assertTrue(apply.matched)
        self.assertEqual(apply.token, "apply")
        self.assertEqual(apply.normalized_token, "apply")
        self.assertEqual(apply.kind, "lookup")
        self.assertEqual(
            apply.argv,
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Now"),
        )

        approve = command_demo_resolve_argv(("approve", "--message", "Ship it"))
        self.assertTrue(approve.matched)
        self.assertEqual(approve.token, "approve")
        self.assertEqual(approve.normalized_token, "approve")
        self.assertEqual(approve.kind, "lookup")
        self.assertEqual(
            approve.argv,
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Ship it"),
        )

        discard = command_demo_resolve_argv(("discard", "--message", "Try again"))
        self.assertTrue(discard.matched)
        self.assertEqual(discard.token, "discard")
        self.assertEqual(discard.normalized_token, "discard")
        self.assertEqual(discard.kind, "lookup")
        self.assertEqual(
            discard.argv,
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Try again"),
        )

        open_project = command_demo_resolve_argv(("open-project", "--project", "workspace"))
        self.assertTrue(open_project.matched)
        self.assertEqual(open_project.token, "open-project")
        self.assertEqual(open_project.normalized_token, "open-project")
        self.assertEqual(open_project.kind, "flow-step")
        self.assertEqual(open_project.argv, ("bootstrap", "--project", "workspace"))

        self.assertEqual(command_mvp_resolve("save"), save)
        self.assertEqual(command_mvp_resolve_argv(("apply", "--message", "Now")), apply)
        self.assertEqual(command_mvp_resolve("resume"), resume)
        self.assertEqual(command_mvp_resolve_argv(("approve", "--message", "Ship it")), approve)
        self.assertEqual(command_mvp_resolve_argv(("discard", "--message", "Try again")), discard)

    def test_command_demo_cli_entry_helpers_keep_demo_smoke_defaults_for_single_token_verbs(self) -> None:
        self.assertEqual(
            command_demo_cli_entry_argv(("project-open",)),
            ("bootstrap", "--project", "demo"),
        )
        self.assertEqual(
            command_demo_cli_entry_argv(("review",)),
            ("diff-preview", "--original", "before", "--proposed", "after"),
        )
        self.assertEqual(
            command_demo_cli_entry_argv(("save",)),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
        )
        self.assertEqual(
            command_demo_cli_entry_argv(("resume",)),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
        )
        self.assertEqual(
            command_mvp_cli_entry_argv(("apply",)),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
        )
        self.assertEqual(
            command_mvp_cli_entry_argv(("approve",)),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
        )
        self.assertEqual(
            command_mvp_cli_entry_argv(("discard",)),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
        )

    def test_command_resolve_helpers_support_custom_specs(self) -> None:
        specs = (
            CommandSpec(
                name="bootstrap",
                aliases=("open",),
                cli_tokens=("project-open", "bootstrap-run"),
                flow_step="project-open",
            ),
            CommandSpec(
                name="review",
                aliases=("patch",),
                cli_tokens=("review-patch",),
                flow_step="patch-review",
            ),
        )

        resolved = command_resolve_for(specs, "patch-review")
        self.assertTrue(resolved.matched)
        self.assertEqual(resolved.primary_cli_token, "review-patch")
        self.assertEqual(resolved.argv, ("review-patch",))
        self.assertEqual(resolved.kind, "flow-step")

        argv_resolved = command_resolve_argv_for(specs, ("patch", "--format", "json"))
        self.assertTrue(argv_resolved.matched)
        self.assertEqual(argv_resolved.argv, ("review-patch", "--format", "json"))
        self.assertEqual(argv_resolved.kind, "lookup")

    def test_command_cli_contract_supports_custom_specs(self) -> None:
        specs = (
            CommandSpec(
                name="bootstrap",
                aliases=("open",),
                cli_tokens=("project-open", "bootstrap-run"),
                flow_step="project-open",
            ),
            CommandSpec(
                name="review",
                aliases=("patch",),
                cli_tokens=("review-patch",),
                flow_step="patch-review",
            ),
        )

        self.assertEqual(
            command_cli_tokens(specs),
            ("project-open", "bootstrap-run", "review-patch"),
        )
        self.assertEqual(
            command_cli_lookup_table(specs),
            (
                ("project-open", "bootstrap"),
                ("bootstrap-run", "bootstrap"),
                ("review-patch", "review"),
            ),
        )
        self.assertEqual(
            command_cli_contract(specs),
            command_catalog.CommandCliContract(
                tokens=("project-open", "bootstrap-run", "review-patch"),
                canonical_names=("bootstrap", "review"),
                lookup_table=(
                    ("project-open", "bootstrap"),
                    ("bootstrap-run", "bootstrap"),
                    ("review-patch", "review"),
                ),
            ),
        )
        self.assertEqual(command_cli_tokens_for(specs, "open"), ("project-open", "bootstrap-run"))
        self.assertEqual(command_primary_cli_token_for(specs, "patch"), "review-patch")
        self.assertEqual(command_cli_primary_tokens(specs), ("project-open", "review-patch"))

    def test_command_cli_shim_contract_supports_custom_specs(self) -> None:
        specs = (
            CommandSpec(
                name="bootstrap",
                aliases=("open",),
                cli_tokens=("project-open", "bootstrap-run"),
                flow_step="project-open",
            ),
            CommandSpec(
                name="review",
                aliases=("patch",),
                cli_tokens=("review-patch",),
                flow_step="patch-review",
            ),
        )
        self.assertEqual(
            command_cli_shim_lookup_table(specs),
            (
                ("project-open", "project-open"),
                ("bootstrap-run", "project-open"),
                ("bootstrap", "project-open"),
                ("open", "project-open"),
                ("review-patch", "review-patch"),
                ("review", "review-patch"),
                ("patch", "review-patch"),
                ("patch-review", "review-patch"),
            ),
        )
        self.assertEqual(command_cli_shim_primary_token_for(specs, "open"), "project-open")
        self.assertEqual(
            command_cli_shim_argv_for(specs, ("patch", "--format", "json")),
            ("review-patch", "--format", "json"),
        )
        self.assertEqual(
            command_cli_shim_argv_for(specs, ("patch", "--format", "json"), ("project-open",)),
            ("patch", "--format", "json"),
        )
        self.assertEqual(command_cli_entry_argv_for(specs, ()), ("project-open",))
        self.assertEqual(
            command_cli_entry_argv_for(specs, ("--project", "demo")),
            ("project-open", "--project", "demo"),
        )
        self.assertEqual(
            command_cli_entry_argv_for(specs, ("review-patch",)),
            ("review-patch",),
        )
        self.assertEqual(
            command_cli_entry_argv_for(specs, ("patch", "--format", "json")),
            ("review-patch", "--format", "json"),
        )
        self.assertEqual(
            command_cli_entry_argv_for(specs, ("--format", "json"), ("patch-review", "project-open")),
            ("review-patch", "--format", "json"),
        )

    def test_command_cli_entry_argv_prefers_smoke_defaults_for_parser_required_subcommands(self) -> None:
        specs = (
            CommandSpec(
                name="bootstrap",
                aliases=("open",),
                cli_tokens=("project-open",),
                flow_step="project-open",
            ),
            CommandSpec(
                name="retrieve",
                aliases=("context",),
                cli_tokens=("context-basket",),
                smoke_argv=("context-basket", "list"),
                flow_step="retrieval",
            ),
        )

        self.assertEqual(
            command_cli_entry_argv_for(specs, ("context-basket",)),
            ("context-basket", "list"),
        )
        self.assertEqual(
            command_cli_entry_argv_for(specs, ("context",)),
            ("context-basket", "list"),
        )
        self.assertEqual(
            command_cli_entry_argv_for(specs, ("--format", "json"), ("retrieval",)),
            ("context-basket", "list", "--format", "json"),
        )

    def test_flag_only_default_route_preserves_required_terminal_defaults(self) -> None:
        specs = (
            CommandSpec(
                name="terminal",
                cli_tokens=("terminal",),
                smoke_argv=(
                    "terminal",
                    "--operation-kind",
                    "terminal_synthesis_request",
                    "--message",
                    "Export handoff",
                ),
                flow_step="export-handoff",
            ),
        )

        self.assertEqual(
            command_cli_entry_argv_for(specs, ("--message", "Queued for export")),
            (
                "terminal",
                "--operation-kind",
                "terminal_synthesis_request",
                "--message",
                "Queued for export",
            ),
        )
        self.assertEqual(
            command_smoke_argv_for(specs, ("--message", "Queued for export")),
            (
                "terminal",
                "--operation-kind",
                "terminal_synthesis_request",
                "--message",
                "Queued for export",
            ),
        )

    def test_command_demo_and_mvp_cli_shim_helpers_alias_the_public_contract(self) -> None:
        self.assertEqual(
            tuple(entry.token for entry in command_demo_cli_shim_contract().entries),
            (
                "bootstrap",
                "open",
                "project-open",
                "project",
                "bootstrap-run",
                "document-open",
                "open-document",
                "context-basket",
                "context",
                "basket",
                "retrieval",
                "retrieve",
                "diff-preview",
                "diff",
                "review-patch",
                "patch-review",
                "terminal",
                "export",
                "save-export",
                "persist",
                "persist-continue",
                "apply-patch",
                "patch-apply",
                "reject-patch",
                "patch-reject",
                "export-handoff",
            ),
        )
        self.assertEqual(command_mvp_cli_shim_contract(), command_demo_cli_shim_contract())
        self.assertNotEqual(command_demo_cli_shim_contract(), command_cli_shim_contract())
        self.assertEqual(command_mvp_cli_shim_catalog(), command_demo_cli_shim_catalog())
        self.assertEqual(
            tuple(entry.token for entry in command_cli_shim_catalog()),
            (
                "bootstrap",
                "open",
                "project-open",
                "project",
                "bootstrap-run",
                "document-open",
                "open-document",
                "diff-preview",
                "diff",
                "review-patch",
                "patch-review",
                "context-basket",
                "context",
                "basket",
                "retrieval",
                "retrieve",
                "terminal",
                "export",
                "save-export",
                "persist",
                "persist-continue",
                "apply-patch",
                "patch-apply",
                "reject-patch",
                "patch-reject",
                "export-handoff",
            ),
        )

    def test_command_cli_contract_rejects_alias_substitution_in_parser_surface_when_canonical_order_still_matches(
        self,
    ) -> None:
        command_catalog.command_cli_contract.cache_clear()
        with patch.object(
            command_catalog,
            "_validated_cli_entrypoints_for",
            return_value=(
                ("bootstrap", ("open",)),
                ("diff-preview", ("diff-preview", "diff", "review-patch")),
                ("context-basket", ("context-basket",)),
                ("terminal", ("terminal",)),
            ),
        ):
            self.assertEqual(
                tuple(name for name, _ in command_catalog._validated_cli_entrypoints_for()),
                command_names(),
            )
            with self.assertRaisesRegex(ValueError, "Command CLI parser surface is inconsistent"):
                command_catalog.command_cli_contract()

    def test_command_cli_contract_rejects_reordered_parser_surface(self) -> None:
        command_catalog.command_cli_contract.cache_clear()
        with patch.object(
            command_catalog,
            "_validated_cli_entrypoints_for",
            return_value=(
                ("bootstrap", ("bootstrap",)),
                ("diff-preview", ("diff", "diff-preview")),
                ("context-basket", ("context-basket",)),
                ("terminal", ("terminal",)),
            ),
        ):
            with self.assertRaisesRegex(ValueError, "Command CLI parser surface is inconsistent"):
                command_catalog.command_cli_contract()

    def test_command_cli_contract_rejects_extra_alias_entrypoint_when_canonical_order_still_matches(
        self,
    ) -> None:
        command_catalog.command_cli_contract.cache_clear()
        with patch.object(
            command_catalog,
            "_validated_cli_entrypoints_for",
            return_value=(
                ("bootstrap", ("bootstrap", "project-open")),
                ("diff-preview", ("diff-preview", "diff", "review-patch")),
                ("context-basket", ("context-basket", "context", "basket")),
                ("terminal", ("terminal",)),
            ),
        ):
            self.assertEqual(
                tuple(name for name, _ in command_catalog._validated_cli_entrypoints_for()),
                command_names(),
            )
            with self.assertRaisesRegex(ValueError, "Command CLI parser surface is inconsistent"):
                command_catalog.command_cli_contract()

    def test_command_cli_lookup_table_resolves_through_the_catalog(self) -> None:
        self.assertEqual(
            command_cli_lookup_table(),
            tuple((token, canonical_command(token)) for token in command_cli_tokens()),
        )

    def test_command_cli_tokens_accept_explicit_entrypoints_declared_on_specs(self) -> None:
        specs = (
            CommandSpec(name="bootstrap", cli_tokens=("bootstrap-run",), flow_step="project-open"),
        )
        self.assertEqual(command_catalog.command_cli_tokens(specs), ("bootstrap-run",))

    def test_command_cli_tokens_reject_duplicate_entrypoints(self) -> None:
        specs = (
            CommandSpec(name="bootstrap", cli_tokens=("bootstrap",), flow_step="project-open"),
            CommandSpec(name="diff-preview", cli_tokens=("bootstrap",), flow_step="patch-review"),
        )
        with self.assertRaisesRegex(ValueError, "Duplicate command lookup token: bootstrap"):
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
        self.assertEqual(
            tuple((entry.token, entry.canonical_name, entry.flow_step) for entry in command_mvp_cli_flow_contract().entries),
            (
                ("bootstrap", "bootstrap", "project-open"),
                ("diff-preview", "diff-preview", "patch-review"),
                ("diff", "diff-preview", "patch-review"),
                ("context-basket", "context-basket", "retrieval"),
                ("terminal", "terminal", "export-handoff"),
            ),
        )

    def test_command_cli_flow_validator_rejects_inconsistent_entries(self) -> None:
        with self.assertRaisesRegex(ValueError, "Command CLI flow entries are inconsistent"):
            command_catalog._validate_command_cli_flow_contract(
                CommandCliFlowContract(
                    entries=(
                        command_catalog.CommandCliFlowEntry(
                            token="bootstrap",
                            canonical_name="bootstrap",
                            flow_step="patch-review",
                        ),
                    )
                ),
                command_specs(),
            )

    def test_command_cli_flow_contract_supports_custom_specs(self) -> None:
        specs = (
            CommandSpec(
                name="bootstrap",
                aliases=("open",),
                cli_tokens=("bootstrap-run", "project-open"),
                flow_step="project-open",
            ),
            CommandSpec(
                name="review",
                aliases=("patch",),
                cli_tokens=("review-patch",),
                flow_step="patch-review",
            ),
        )

        contract = command_cli_flow_contract(specs)
        self.assertEqual(
            tuple((entry.token, entry.canonical_name, entry.flow_step) for entry in contract.entries),
            (
                ("bootstrap-run", "bootstrap", "project-open"),
                ("project-open", "bootstrap", "project-open"),
                ("review-patch", "review", "patch-review"),
            ),
        )
        self.assertEqual(
            command_cli_flow_lookup_table(specs),
            (
                ("bootstrap-run", "project-open"),
                ("project-open", "project-open"),
                ("review-patch", "patch-review"),
            ),
        )

    def test_command_demo_and_mvp_cli_flow_contracts_accept_custom_specs(self) -> None:
        specs = (
            CommandSpec(name="bootstrap", cli_tokens=("bootstrap-run",), flow_step="project-open"),
            CommandSpec(name="context-basket", cli_tokens=("retrieve",), flow_step="retrieval"),
            CommandSpec(name="diff-preview", cli_tokens=("review-patch",), flow_step="patch-review"),
        )

        expected = CommandCliFlowContract(
            entries=(
                command_catalog.CommandCliFlowEntry(
                    token="bootstrap-run",
                    canonical_name="bootstrap",
                    flow_step="project-open",
                ),
                command_catalog.CommandCliFlowEntry(
                    token="retrieve",
                    canonical_name="context-basket",
                    flow_step="retrieval",
                ),
                command_catalog.CommandCliFlowEntry(
                    token="review-patch",
                    canonical_name="diff-preview",
                    flow_step="patch-review",
                ),
            )
        )

        self.assertEqual(command_demo_cli_flow_contract(specs), expected)
        self.assertEqual(command_mvp_cli_flow_contract(specs), expected)

    def test_command_cli_surface_catalog_exposes_deterministic_parser_entries(self) -> None:
        self.assertEqual(
            tuple(
                (
                    entry.token,
                    entry.canonical_name,
                    entry.flow_step,
                    entry.aliases,
                    entry.lookup_tokens,
                )
                for entry in command_cli_surface_catalog()
            ),
            (
                (
                    "bootstrap",
                    "bootstrap",
                    "project-open",
                    ("open", "project-open", "project", "bootstrap-run", "document-open", "open-document"),
                    (
                        "bootstrap",
                        "open",
                        "project-open",
                        "project",
                        "bootstrap-run",
                        "document-open",
                        "open-document",
                    ),
                ),
                (
                    "diff-preview",
                    "diff-preview",
                    "patch-review",
                    ("diff", "diff_preview", "review-patch"),
                    ("diff-preview", "diff", "review-patch"),
                ),
                (
                    "diff",
                    "diff-preview",
                    "patch-review",
                    ("diff", "diff_preview", "review-patch"),
                    ("diff-preview", "diff", "review-patch"),
                ),
                (
                    "context-basket",
                    "context-basket",
                    "retrieval",
                    ("context", "basket", "retrieval", "retrieve"),
                    ("context-basket", "context", "basket", "retrieval", "retrieve"),
                ),
                (
                    "terminal",
                    "terminal",
                    "export-handoff",
                    (
                        "export",
                        "save-export",
                        "persist",
                        "persist-continue",
                        "apply-patch",
                        "patch-apply",
                        "reject-patch",
                        "patch-reject",
                    ),
                    (
                        "terminal",
                        "export",
                        "save-export",
                        "persist",
                        "persist-continue",
                        "apply-patch",
                        "patch-apply",
                        "reject-patch",
                        "patch-reject",
                    ),
                ),
            ),
        )
        self.assertEqual(
            tuple(entry.token for entry in command_demo_cli_surface_catalog()),
            ("bootstrap", "diff-preview", "diff", "context-basket", "terminal"),
        )
        self.assertEqual(command_demo_cli_surface_catalog(), command_mvp_cli_surface_catalog())

    def test_command_cli_surface_contract_bundles_the_parser_manifest(self) -> None:
        contract = command_cli_surface_contract()
        self.assertEqual(contract.entries, command_cli_surface_catalog())
        self.assertEqual(
            tuple(entry.token for entry in command_demo_cli_surface_contract().entries),
            ("bootstrap", "diff-preview", "diff", "context-basket", "terminal"),
        )
        self.assertEqual(command_demo_cli_surface_contract(), command_mvp_cli_surface_contract())

    def test_command_cli_surface_validator_rejects_inconsistent_entries(self) -> None:
        with self.assertRaisesRegex(ValueError, "Command CLI surface entries are inconsistent"):
            command_catalog._validate_command_cli_surface_contract(
                command_catalog.CommandCliSurfaceContract(
                    entries=(
                        command_catalog.CommandCliSurfaceEntry(
                            token="bootstrap",
                            canonical_name="bootstrap",
                            flow_step="patch-review",
                            aliases=("open",),
                            lookup_tokens=("bootstrap", "open"),
                            description="Run the project bootstrap flow.",
                        ),
                    )
                ),
                command_specs(),
            )

    def test_command_cli_surface_catalog_includes_parser_only_cli_tokens(self) -> None:
        specs = (
            CommandSpec(
                name="bootstrap",
                aliases=("open",),
                cli_tokens=("project-open", "bootstrap-run"),
                flow_step="project-open",
                description="Open the project bootstrap flow.",
            ),
            CommandSpec(
                name="review",
                aliases=("patch",),
                cli_tokens=("review-patch",),
                flow_step="patch-review",
                description="Review the patch output.",
            ),
        )

        self.assertEqual(
            tuple((entry.token, entry.lookup_tokens) for entry in command_cli_surface_catalog(specs)),
            (
                (
                    "project-open",
                    ("bootstrap", "open", "project-open", "bootstrap-run"),
                ),
                (
                    "bootstrap-run",
                    ("bootstrap", "open", "project-open", "bootstrap-run"),
                ),
                (
                    "review-patch",
                    ("review", "patch", "review-patch"),
                ),
            ),
        )

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

    def test_command_cli_route_lookup_tables_follow_mvp_route_order(self) -> None:
        self.assertEqual(
            command_cli_route_lookup_table(),
            (
                ("bootstrap", "bootstrap"),
                ("context-basket", "context-basket"),
                ("diff-preview", "diff-preview"),
                ("diff", "diff-preview"),
                ("terminal", "terminal"),
            ),
        )
        self.assertEqual(
            command_cli_route_flow_lookup_table(),
            (
                ("bootstrap", "project-open"),
                ("context-basket", "retrieval"),
                ("diff-preview", "patch-review"),
                ("diff", "patch-review"),
                ("terminal", "export-handoff"),
            ),
        )

    def test_command_cli_route_contract_tracks_the_smoke_surface(self) -> None:
        contract = command_cli_route_contract()
        surface_contract = command_surface_contract()
        self.assertEqual(contract.route_catalog, command_cli_route_catalog())
        self.assertEqual(contract.route_lookup_table, command_cli_route_lookup_table())
        self.assertEqual(contract.route_flow_lookup_table, command_cli_route_flow_lookup_table())
        self.assertEqual(contract.invocation_plan, command_flow_invocation_plan())
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
        self.assertEqual(contract.invocation_plan, surface_contract.invocation_plan)
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
        self.assertEqual(command_aliases_for(specs, "patch-review"), ("patch", "patch-review"))
        self.assertEqual(command_lookup_tokens_for(specs, "patch-review"), ("review", "patch"))
        self.assertEqual(command_resolution_tokens_for(specs, "patch-review"), ("review", "patch"))
        self.assertEqual(canonical_command_for(specs, " PATCH REVIEW "), "review")

    def test_command_resolution_helpers_include_parser_only_cli_tokens(self) -> None:
        specs = (
            CommandSpec(
                name="bootstrap",
                aliases=("open",),
                cli_tokens=("project-open", "bootstrap-run"),
                flow_step="project-open",
            ),
            CommandSpec(
                name="review",
                aliases=("patch",),
                cli_tokens=("review-patch",),
                flow_step="patch-review",
            ),
        )

        self.assertEqual(
            command_resolution_tokens(specs),
            ("bootstrap", "open", "project-open", "bootstrap-run", "review", "patch", "review-patch"),
        )
        self.assertEqual(
            command_resolution_lookup_index(specs),
            (
                ("bootstrap", "bootstrap"),
                ("open", "bootstrap"),
                ("project-open", "bootstrap"),
                ("bootstrap-run", "bootstrap"),
                ("review", "review"),
                ("patch", "review"),
                ("review-patch", "review"),
            ),
        )
        self.assertEqual(command_resolution_lookup_table(specs), command_resolution_lookup_index(specs))
        self.assertEqual(
            command_resolution_tokens_for(specs, "patch-review"),
            ("review", "patch", "review-patch"),
        )

    def test_command_manifest_entries_expose_canonical_lookup_tokens(self) -> None:
        manifest = command_manifest()
        self.assertEqual(
            tuple((entry.name, entry.lookup_tokens) for entry in manifest),
            (
                (
                    "bootstrap",
                    ("bootstrap", "open", "project-open", "project", "bootstrap-run", "document-open", "open-document"),
                ),
                ("diff-preview", ("diff-preview", "diff", "diff_preview", "review-patch")),
                (
                    "context-basket",
                    ("context-basket", "context", "basket", "retrieval", "retrieve"),
                ),
                (
                    "terminal",
                    (
                        "terminal",
                        "export",
                        "save-export",
                        "persist",
                        "persist-continue",
                        "apply-patch",
                        "patch-apply",
                        "reject-patch",
                        "patch-reject",
                    ),
                ),
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
                "bootstrap-run",
                "document-open",
                "open-document",
                "diff-preview",
                "diff",
                "diff_preview",
                "review-patch",
                "context-basket",
                "context",
                "basket",
                "retrieval",
                "retrieve",
                "terminal",
                "export",
                "save-export",
                "persist",
                "persist-continue",
                "apply-patch",
                "patch-apply",
                "reject-patch",
                "patch-reject",
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
                ("bootstrap-run", "bootstrap"),
                ("document-open", "bootstrap"),
                ("open-document", "bootstrap"),
                ("diff-preview", "diff-preview"),
                ("diff", "diff-preview"),
                ("review-patch", "diff-preview"),
                ("context-basket", "context-basket"),
                ("context", "context-basket"),
                ("basket", "context-basket"),
                ("retrieval", "context-basket"),
                ("retrieve", "context-basket"),
                ("terminal", "terminal"),
                ("export", "terminal"),
                ("save-export", "terminal"),
                ("persist", "terminal"),
                ("persist-continue", "terminal"),
                ("apply-patch", "terminal"),
                ("patch-apply", "terminal"),
                ("reject-patch", "terminal"),
                ("patch-reject", "terminal"),
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

    def test_command_smoke_contract_bundles_the_mvp_invocation_surface(self) -> None:
        contract = command_smoke_contract()
        self.assertEqual(contract, command_demo_smoke_contract())
        self.assertEqual(contract, command_mvp_smoke_contract())
        self.assertEqual(contract.flow_steps, command_mvp_flow_steps())
        self.assertEqual(contract.names, command_mvp_flow_names())
        self.assertEqual(
            tuple((entry.flow_step, entry.name, entry.smoke_argv) for entry in contract.entries),
            (
                ("project-open", "bootstrap", ("bootstrap", "--project", "demo")),
                ("retrieval", "context-basket", ("context-basket", "list")),
                ("patch-review", "diff-preview", ("diff-preview", "--original", "before", "--proposed", "after")),
                (
                    "export-handoff",
                    "terminal",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_synthesis_request",
                        "--message",
                        "Export handoff",
                    ),
                ),
            ),
        )
        self.assertEqual(
            tuple((entry.flow_step, entry.name, entry.argv) for entry in contract.invocation_plan),
            (
                ("project-open", "bootstrap", ("bootstrap",)),
                ("retrieval", "context-basket", ("context-basket",)),
                ("patch-review", "diff-preview", ("diff-preview",)),
                ("export-handoff", "terminal", ("terminal",)),
            ),
        )
        self.assertEqual(contract.invocation_plan, command_flow_invocation_plan())
        self.assertEqual(contract.route_summary, command_flow_route_summary())
        self.assertEqual(contract.lookup_surface, command_flow_lookup_surface())

    def test_command_smoke_helpers_expand_to_parser_ready_argv(self) -> None:
        self.assertEqual(command_smoke_entry_argv("bootstrap"), ("bootstrap", "--project", "demo"))
        self.assertEqual(
            command_smoke_entry_argv("diff-preview"),
            ("diff-preview", "--original", "before", "--proposed", "after"),
        )
        self.assertEqual(
            command_smoke_argv(("export",)),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Export handoff"),
        )
        self.assertEqual(
            command_smoke_argv_for(command_specs(), ("persist",), ("export-handoff",)),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
        )
        self.assertEqual(
            command_smoke_argv_for(command_specs(), ("apply-patch",), ("export-handoff",)),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
        )
        self.assertEqual(
            command_smoke_argv_for(command_specs(), ("patch-apply",), ("export-handoff",)),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
        )
        self.assertEqual(
            command_smoke_argv_for(command_specs(), ("reject-patch",), ("export-handoff",)),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
        )
        self.assertEqual(
            command_smoke_argv_for(command_specs(), ("patch-reject",), ("export-handoff",)),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
        )
        self.assertEqual(
            command_smoke_argv_for(command_specs(), ("export-handoff", "--message", "Queued for export"), ("export-handoff",)),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Queued for export"),
        )
        self.assertEqual(
            command_smoke_argv_for(command_specs(), ("apply-patch", "--message", "Apply immediately"), ("export-handoff",)),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply immediately"),
        )
        self.assertEqual(
            command_smoke_argv_for(command_specs(), ("apply-patch", "--operation-kind", "terminal_synthesis_request"), ("export-handoff",)),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
        )
        self.assertEqual(
            command_smoke_argv_for(command_specs(), ("patch-reject", "--operation-kind", "terminal_synthesis_request"), ("export-handoff",)),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
        )
        self.assertEqual(
            command_smoke_argv_for(command_specs(), ("export", "--message=Queued for export"), ("export-handoff",)),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message=Queued for export"),
        )
        self.assertEqual(
            command_smoke_argv(("terminal", "--operation-kind", "terminal_tool_orchestration")),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Export handoff"),
        )
        self.assertEqual(
            command_cli_entry_argv(("persist",)),
            ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
        )
        self.assertEqual(
            command_cli_entry_argv(("apply-patch",)),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
        )
        self.assertEqual(
            command_cli_entry_argv(("patch-reject",)),
            ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
        )

    def test_command_demo_path_contract_exposes_parser_ready_surface_invocations(self) -> None:
        contract = command_demo_path_contract()
        self.assertEqual(contract, command_mvp_path_contract())
        self.assertEqual(contract.invocation_plan, command_demo_path_invocation_plan())
        self.assertEqual(
            tuple((entry.flow_step, entry.name, entry.parser_argv) for entry in contract.entries),
            (
                ("project-open", "bootstrap", ("bootstrap", "--project", "demo")),
                ("retrieval", "context-basket", ("context-basket", "list")),
                ("patch-review", "diff-preview", ("diff-preview", "--original", "before", "--proposed", "after")),
                (
                    "export-handoff",
                    "terminal",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_synthesis_request",
                        "--message",
                        "Export handoff",
                    ),
                ),
            ),
        )
        self.assertEqual(
            contract.entries[0].surface_invocations,
            (
                ("bootstrap", ("bootstrap", "--project", "demo")),
                ("open", ("bootstrap", "--project", "demo")),
                ("project-open", ("bootstrap", "--project", "demo")),
                ("project", ("bootstrap", "--project", "demo")),
                ("bootstrap-run", ("bootstrap", "--project", "demo")),
                ("document-open", ("bootstrap", "--project", "demo")),
                ("open-document", ("bootstrap", "--project", "demo")),
            ),
        )
        self.assertEqual(contract.entries[0].preferred_surface_tokens, ("project-open",))
        self.assertEqual(
            contract.entries[1].surface_invocations,
            (
                ("context-basket", ("context-basket", "list")),
                ("context", ("context-basket", "list")),
                ("basket", ("context-basket", "list")),
                ("retrieval", ("context-basket", "list")),
                ("retrieve", ("context-basket", "list")),
            ),
        )
        self.assertEqual(contract.entries[1].preferred_surface_tokens, ("retrieval",))
        self.assertEqual(
            contract.entries[2].surface_invocations,
            (
                ("diff-preview", ("diff-preview", "--original", "before", "--proposed", "after")),
                ("diff", ("diff-preview", "--original", "before", "--proposed", "after")),
                ("review-patch", ("diff-preview", "--original", "before", "--proposed", "after")),
                ("patch-review", ("diff-preview", "--original", "before", "--proposed", "after")),
            ),
        )
        self.assertEqual(contract.entries[2].preferred_surface_tokens, ("patch-review",))
        self.assertEqual(
            contract.entries[3].surface_invocations,
            (
                (
                    "terminal",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_synthesis_request",
                        "--message",
                        "Export handoff",
                    ),
                ),
                (
                    "export",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_synthesis_request",
                        "--message",
                        "Export handoff",
                    ),
                ),
                (
                    "save-export",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_synthesis_request",
                        "--message",
                        "Export handoff",
                    ),
                ),
                (
                    "persist",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_synthesis_request",
                        "--message",
                        "Persist and continue",
                    ),
                ),
                (
                    "persist-continue",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_synthesis_request",
                        "--message",
                        "Persist and continue",
                    ),
                ),
                (
                    "apply-patch",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_tool_orchestration",
                        "--message",
                        "Apply patch",
                    ),
                ),
                (
                    "patch-apply",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_tool_orchestration",
                        "--message",
                        "Apply patch",
                    ),
                ),
                (
                    "reject-patch",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_tool_orchestration",
                        "--message",
                        "Reject patch",
                    ),
                ),
                (
                    "patch-reject",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_tool_orchestration",
                        "--message",
                        "Reject patch",
                    ),
                ),
                (
                    "export-handoff",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_synthesis_request",
                        "--message",
                        "Export handoff",
                    ),
                ),
            ),
        )
        self.assertEqual(
            contract.entries[3].preferred_surface_tokens,
            ("export-handoff", "export", "persist", "apply-patch", "reject-patch"),
        )
        self.assertEqual(
            tuple(entry.preferred_surface_invocations for entry in contract.entries),
            (
                (("project-open", ("bootstrap", "--project", "demo")),),
                (("retrieval", ("context-basket", "list")),),
                (
                    (
                        "patch-review",
                        ("diff-preview", "--original", "before", "--proposed", "after"),
                    ),
                ),
                (
                    (
                        "export-handoff",
                        (
                            "terminal",
                            "--operation-kind",
                            "terminal_synthesis_request",
                            "--message",
                            "Export handoff",
                        ),
                    ),
                    (
                        "export",
                        (
                            "terminal",
                            "--operation-kind",
                            "terminal_synthesis_request",
                            "--message",
                            "Export handoff",
                        ),
                    ),
                    (
                        "persist",
                        (
                            "terminal",
                            "--operation-kind",
                            "terminal_synthesis_request",
                            "--message",
                            "Persist and continue",
                        ),
                    ),
                    (
                        "apply-patch",
                        (
                            "terminal",
                            "--operation-kind",
                            "terminal_tool_orchestration",
                            "--message",
                            "Apply patch",
                        ),
                    ),
                    (
                        "reject-patch",
                        (
                            "terminal",
                            "--operation-kind",
                            "terminal_tool_orchestration",
                            "--message",
                            "Reject patch",
                        ),
                    ),
                ),
            ),
        )
        self.assertEqual(
            tuple(entry.parser_surface_invocations for entry in contract.entries),
            (
                (("bootstrap", ("bootstrap", "--project", "demo")),),
                (("context-basket", ("context-basket", "list")),),
                (("diff-preview", ("diff-preview", "--original", "before", "--proposed", "after")), ("diff", ("diff-preview", "--original", "before", "--proposed", "after"))),
                (
                    (
                        "terminal",
                        (
                            "terminal",
                            "--operation-kind",
                            "terminal_synthesis_request",
                            "--message",
                            "Export handoff",
                        ),
                    ),
                ),
            ),
        )
        self.assertEqual(
            command_demo_preferred_surface_invocation_table(),
            (
                ("project-open", ("bootstrap", "--project", "demo")),
                ("retrieval", ("context-basket", "list")),
                ("patch-review", ("diff-preview", "--original", "before", "--proposed", "after")),
                (
                    "export-handoff",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_synthesis_request",
                        "--message",
                        "Export handoff",
                    ),
                ),
                (
                    "export",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_synthesis_request",
                        "--message",
                        "Export handoff",
                    ),
                ),
                (
                    "persist",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_synthesis_request",
                        "--message",
                        "Persist and continue",
                    ),
                ),
                (
                    "apply-patch",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_tool_orchestration",
                        "--message",
                        "Apply patch",
                    ),
                ),
                (
                    "reject-patch",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_tool_orchestration",
                        "--message",
                        "Reject patch",
                    ),
                ),
            ),
        )
        self.assertEqual(
            command_mvp_preferred_surface_invocation_table(),
            command_demo_preferred_surface_invocation_table(),
        )

    def test_command_demo_loop_contract_exposes_the_canonical_milestone_three_verbs(self) -> None:
        contract = command_demo_loop_contract()
        self.assertEqual(contract, command_mvp_loop_contract())
        self.assertEqual(contract.entries, command_demo_loop_catalog())
        self.assertEqual(command_mvp_loop_catalog(), command_demo_loop_catalog())
        self.assertEqual(contract.lookup_table, command_demo_loop_lookup_table())
        self.assertEqual(command_mvp_loop_lookup_table(), command_demo_loop_lookup_table())
        self.assertEqual(contract.invocation_plan, command_demo_loop_invocation_plan())
        self.assertEqual(command_mvp_loop_invocation_plan(), command_demo_loop_invocation_plan())
        self.assertEqual(command_mvp_loop_tokens(), command_demo_loop_tokens())
        self.assertEqual(
            contract.tokens,
            (
                "project-open",
                "retrieval",
                "patch-review",
                "apply-patch",
                "reject-patch",
                "persist",
                "export-handoff",
            ),
        )
        self.assertEqual(
            tuple((entry.token, entry.canonical_name, entry.flow_step, entry.kind, entry.argv) for entry in contract.entries),
            (
                ("project-open", "bootstrap", "project-open", "flow-step", ("bootstrap", "--project", "demo")),
                ("retrieval", "context-basket", "retrieval", "flow-step", ("context-basket", "list")),
                (
                    "patch-review",
                    "diff-preview",
                    "patch-review",
                    "flow-step",
                    ("diff-preview", "--original", "before", "--proposed", "after"),
                ),
                (
                    "apply-patch",
                    "terminal",
                    "export-handoff",
                    "lookup",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
                ),
                (
                    "reject-patch",
                    "terminal",
                    "export-handoff",
                    "lookup",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
                ),
                (
                    "persist",
                    "terminal",
                    "export-handoff",
                    "lookup",
                    ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
                ),
                (
                    "export-handoff",
                    "terminal",
                    "export-handoff",
                    "flow-step",
                    ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Export handoff"),
                ),
            ),
        )
        self.assertEqual(
            command_demo_loop_lookup_table(),
            (
                ("project-open", "bootstrap"),
                ("retrieval", "context-basket"),
                ("patch-review", "diff-preview"),
                ("apply-patch", "terminal"),
                ("reject-patch", "terminal"),
                ("persist", "terminal"),
                ("export-handoff", "terminal"),
            ),
        )

    def test_command_demo_compatibility_contract_exposes_legacy_demo_verbs(self) -> None:
        contract = command_demo_compatibility_contract()
        self.assertEqual(contract, command_mvp_compatibility_contract())
        self.assertEqual(contract.entries, command_demo_compatibility_catalog())
        self.assertEqual(command_mvp_compatibility_catalog(), command_demo_compatibility_catalog())
        self.assertEqual(contract.lookup_table, command_demo_compatibility_lookup_table())
        self.assertEqual(command_mvp_compatibility_lookup_table(), command_demo_compatibility_lookup_table())
        self.assertEqual(command_mvp_compatibility_tokens(), command_demo_compatibility_tokens())
        self.assertEqual(
            contract.tokens,
            (
                "open-project",
                "review",
                "preview-patch",
                "save",
                "continue",
                "resume",
                "apply",
                "approve",
                "accept",
                "reject",
                "decline",
                "discard",
            ),
        )
        self.assertEqual(
            tuple(
                (entry.token, entry.canonical_token, entry.canonical_name, entry.flow_step, entry.kind, entry.argv)
                for entry in contract.entries
            ),
            (
                (
                    "open-project",
                    "project-open",
                    "bootstrap",
                    "project-open",
                    "compatibility",
                    ("bootstrap", "--project", "demo"),
                ),
                (
                    "review",
                    "patch-review",
                    "diff-preview",
                    "patch-review",
                    "compatibility",
                    ("diff-preview", "--original", "before", "--proposed", "after"),
                ),
                (
                    "preview-patch",
                    "patch-review",
                    "diff-preview",
                    "patch-review",
                    "compatibility",
                    ("diff-preview", "--original", "before", "--proposed", "after"),
                ),
                (
                    "save",
                    "persist",
                    "terminal",
                    "export-handoff",
                    "compatibility",
                    ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
                ),
                (
                    "continue",
                    "persist",
                    "terminal",
                    "export-handoff",
                    "compatibility",
                    ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
                ),
                (
                    "resume",
                    "persist",
                    "terminal",
                    "export-handoff",
                    "compatibility",
                    ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
                ),
                (
                    "apply",
                    "apply-patch",
                    "terminal",
                    "export-handoff",
                    "compatibility",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
                ),
                (
                    "approve",
                    "apply-patch",
                    "terminal",
                    "export-handoff",
                    "compatibility",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
                ),
                (
                    "accept",
                    "apply-patch",
                    "terminal",
                    "export-handoff",
                    "compatibility",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
                ),
                (
                    "reject",
                    "reject-patch",
                    "terminal",
                    "export-handoff",
                    "compatibility",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
                ),
                (
                    "decline",
                    "reject-patch",
                    "terminal",
                    "export-handoff",
                    "compatibility",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
                ),
                (
                    "discard",
                    "reject-patch",
                    "terminal",
                    "export-handoff",
                    "compatibility",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
                ),
            ),
        )
        self.assertEqual(
            command_demo_compatibility_invocation_table(),
            (
                ("open-project", ("bootstrap", "--project", "demo")),
                ("review", ("diff-preview", "--original", "before", "--proposed", "after")),
                ("preview-patch", ("diff-preview", "--original", "before", "--proposed", "after")),
                (
                    "save",
                    ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
                ),
                (
                    "continue",
                    ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
                ),
                (
                    "resume",
                    ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
                ),
                (
                    "apply",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
                ),
                (
                    "approve",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
                ),
                (
                    "accept",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
                ),
                (
                    "reject",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
                ),
                (
                    "decline",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
                ),
                (
                    "discard",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
                ),
            ),
        )

    def test_command_demo_compatibility_contract_tracks_custom_specs(self) -> None:
        specs = (
            CommandSpec(
                name="bootstrap",
                aliases=("open",),
                cli_tokens=("bootstrap-run",),
                smoke_argv=("bootstrap-run", "--project", "demo"),
                flow_step="project-open",
            ),
            CommandSpec(
                name="context-basket",
                aliases=("retrieve",),
                cli_tokens=("context-basket",),
                smoke_argv=("context-basket", "list"),
                flow_step="retrieval",
            ),
            CommandSpec(
                name="diff-preview",
                aliases=("review-patch",),
                cli_tokens=("review-diff",),
                smoke_argv=("review-diff", "--original", "before", "--proposed", "after"),
                flow_step="patch-review",
            ),
            CommandSpec(
                name="terminal",
                aliases=("save-export", "persist-continue", "patch-apply", "patch-reject"),
                cli_tokens=("terminal",),
                smoke_argv=(
                    "terminal",
                    "--operation-kind",
                    "terminal_synthesis_request",
                    "--message",
                    "Export handoff",
                ),
                surface_argv=(
                    "terminal",
                    "--operation-kind",
                    "terminal_synthesis_request",
                    "--message",
                    "Export handoff",
                ),
                shim_argv=(
                    (
                        "save-export",
                        (
                            "terminal",
                            "--operation-kind",
                            "terminal_synthesis_request",
                            "--message",
                            "Export handoff",
                        ),
                    ),
                    (
                        "persist-continue",
                        (
                            "terminal",
                            "--operation-kind",
                            "terminal_synthesis_request",
                            "--message",
                            "Persist and continue",
                        ),
                    ),
                    (
                        "patch-apply",
                        (
                            "terminal",
                            "--operation-kind",
                            "terminal_tool_orchestration",
                            "--message",
                            "Apply patch",
                        ),
                    ),
                    (
                        "patch-reject",
                        (
                            "terminal",
                            "--operation-kind",
                            "terminal_tool_orchestration",
                            "--message",
                            "Reject patch",
                        ),
                    ),
                ),
                shim_pinned_options=(
                    ("save-export", ("--operation-kind",)),
                    ("persist-continue", ("--operation-kind",)),
                    ("patch-apply", ("--operation-kind",)),
                    ("patch-reject", ("--operation-kind",)),
                ),
                flow_step="export-handoff",
            ),
        )

        contract = command_demo_compatibility_contract(specs)

        self.assertEqual(contract.tokens, command_demo_compatibility_tokens())
        self.assertEqual(
            contract.invocation_table,
            (
                ("open-project", ("bootstrap-run", "--project", "demo")),
                ("review", ("review-diff", "--original", "before", "--proposed", "after")),
                ("preview-patch", ("review-diff", "--original", "before", "--proposed", "after")),
                (
                    "save",
                    ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
                ),
                (
                    "continue",
                    ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
                ),
                (
                    "resume",
                    ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
                ),
                (
                    "apply",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
                ),
                (
                    "approve",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
                ),
                (
                    "accept",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
                ),
                (
                    "reject",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
                ),
                (
                    "decline",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
                ),
                (
                    "discard",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
                ),
            ),
        )

    def test_command_demo_loop_contract_falls_back_to_legacy_surface_tokens_for_custom_specs(self) -> None:
        specs = (
            CommandSpec(
                name="bootstrap",
                aliases=("open",),
                cli_tokens=("bootstrap-run",),
                smoke_argv=("bootstrap-run", "--project", "demo"),
                flow_step="project-open",
            ),
            CommandSpec(
                name="context-basket",
                aliases=("retrieve",),
                cli_tokens=("context-basket",),
                smoke_argv=("context-basket", "list"),
                flow_step="retrieval",
            ),
            CommandSpec(
                name="diff-preview",
                aliases=("review-patch",),
                cli_tokens=("review-diff",),
                smoke_argv=("review-diff", "--original", "before", "--proposed", "after"),
                flow_step="patch-review",
            ),
            CommandSpec(
                name="terminal",
                aliases=("save-export", "persist-continue", "patch-apply", "patch-reject"),
                cli_tokens=("terminal",),
                smoke_argv=(
                    "terminal",
                    "--operation-kind",
                    "terminal_synthesis_request",
                    "--message",
                    "Export handoff",
                ),
                surface_argv=(
                    "terminal",
                    "--operation-kind",
                    "terminal_synthesis_request",
                    "--message",
                    "Export handoff",
                ),
                shim_argv=(
                    (
                        "save-export",
                        (
                            "terminal",
                            "--operation-kind",
                            "terminal_synthesis_request",
                            "--message",
                            "Export handoff",
                        ),
                    ),
                    (
                        "persist-continue",
                        (
                            "terminal",
                            "--operation-kind",
                            "terminal_synthesis_request",
                            "--message",
                            "Persist and continue",
                        ),
                    ),
                    (
                        "patch-apply",
                        (
                            "terminal",
                            "--operation-kind",
                            "terminal_tool_orchestration",
                            "--message",
                            "Apply patch",
                        ),
                    ),
                    (
                        "patch-reject",
                        (
                            "terminal",
                            "--operation-kind",
                            "terminal_tool_orchestration",
                            "--message",
                            "Reject patch",
                        ),
                    ),
                ),
                shim_pinned_options=(
                    ("save-export", ("--operation-kind",)),
                    ("persist-continue", ("--operation-kind",)),
                    ("patch-apply", ("--operation-kind",)),
                    ("patch-reject", ("--operation-kind",)),
                ),
                flow_step="export-handoff",
            ),
        )

        contract = command_demo_loop_contract(specs)

        self.assertEqual(contract.tokens, command_demo_loop_tokens())
        self.assertEqual(
            tuple((entry.token, entry.argv) for entry in contract.entries),
            (
                ("project-open", ("bootstrap-run", "--project", "demo")),
                ("retrieval", ("context-basket", "list")),
                ("patch-review", ("review-diff", "--original", "before", "--proposed", "after")),
                (
                    "apply-patch",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Apply patch"),
                ),
                (
                    "reject-patch",
                    ("terminal", "--operation-kind", "terminal_tool_orchestration", "--message", "Reject patch"),
                ),
                (
                    "persist",
                    ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Persist and continue"),
                ),
                (
                    "export-handoff",
                    ("terminal", "--operation-kind", "terminal_synthesis_request", "--message", "Export handoff"),
                ),
            ),
        )

    def test_command_demo_path_validator_rejects_surface_invocation_argv_drift(self) -> None:
        contract = command_demo_path_contract()
        broken_entry = replace(
            contract.entries[3],
            surface_invocations=(
                (
                    "terminal",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_tool_orchestration",
                        "--message",
                        "Export handoff",
                    ),
                ),
                *contract.entries[3].surface_invocations[1:],
            ),
        )
        broken_contract = replace(contract, entries=(*contract.entries[:3], broken_entry))

        with self.assertRaisesRegex(ValueError, "Command demo path surface invocation argv is inconsistent"):
            command_catalog._validate_command_demo_path_contract(
                broken_contract,
                command_demo_smoke_contract(),
                specs=command_specs(),
            )

    def test_command_demo_path_validator_rejects_preferred_surface_invocation_argv_drift(self) -> None:
        contract = command_demo_path_contract()
        broken_entry = replace(
            contract.entries[3],
            preferred_surface_invocations=(
                (
                    "export-handoff",
                    (
                        "terminal",
                        "--operation-kind",
                        "terminal_synthesis_request",
                        "--message",
                        "Persist and continue",
                    ),
                ),
                *contract.entries[3].preferred_surface_invocations[1:],
            ),
        )
        broken_contract = replace(contract, entries=(*contract.entries[:3], broken_entry))

        with self.assertRaisesRegex(
            ValueError, "Command demo path preferred surface invocation argv is inconsistent"
        ):
            command_catalog._validate_command_demo_path_contract(
                broken_contract,
                command_demo_smoke_contract(),
                specs=command_specs(),
            )

    def test_command_demo_path_validator_rejects_parser_surface_invocation_argv_drift(self) -> None:
        contract = command_demo_path_contract()
        broken_entry = replace(
            contract.entries[2],
            parser_surface_invocations=(
                ("diff-preview", ("diff-preview",)),
                ("diff", ("diff-preview",)),
            ),
        )
        broken_contract = replace(contract, entries=(*contract.entries[:2], broken_entry, *contract.entries[3:]))

        with self.assertRaisesRegex(ValueError, "Command demo path parser surface invocation argv is inconsistent"):
            command_catalog._validate_command_demo_path_contract(
                broken_contract,
                command_demo_smoke_contract(),
                specs=command_specs(),
            )

    def test_custom_smoke_argv_preserves_flag_values(self) -> None:
        specs = (
            CommandSpec(
                name="terminal",
                cli_tokens=("terminal",),
                smoke_argv=("terminal", "--message", "Export Handoff"),
                surface_argv=("terminal",),
                flow_step="export-handoff",
            ),
        )

        self.assertEqual(
            command_cli_entry_argv_for(specs, ("terminal",)),
            ("terminal",),
        )
        self.assertEqual(
            command_smoke_argv_for(specs, ("terminal",), ("export-handoff",)),
            ("terminal", "--message", "Export Handoff"),
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

    def test_command_flow_invocation_plan_tracks_primary_route_tokens(self) -> None:
        self.assertEqual(
            tuple((entry.flow_step, entry.name, entry.argv) for entry in command_flow_invocation_plan()),
            (
                ("project-open", "bootstrap", ("bootstrap",)),
                ("retrieval", "context-basket", ("context-basket",)),
                ("patch-review", "diff-preview", ("diff-preview",)),
                ("export-handoff", "terminal", ("terminal",)),
            ),
        )
        self.assertEqual(command_flow_invocation_plan(), command_demo_flow_invocation_plan())
        self.assertEqual(command_flow_invocation_plan(), command_mvp_flow_invocation_plan())

    def test_command_flow_invocation_contract_bundles_the_smoke_sequence(self) -> None:
        contract = command_flow_invocation_contract()
        self.assertEqual(contract.entries, command_flow_invocation_plan())
        self.assertEqual(contract, command_demo_flow_invocation_contract())
        self.assertEqual(contract, command_mvp_flow_invocation_contract())
        self.assertEqual(
            contract,
            CommandInvocationPlanContract(entries=command_mvp_flow_invocation_plan()),
        )

    def test_command_flow_invocation_plan_supports_custom_cli_tokens(self) -> None:
        specs = (
            CommandSpec(name="context-basket", cli_tokens=("retrieve",), flow_step="retrieval"),
            CommandSpec(name="diff-preview", cli_tokens=("review-patch", "diff"), flow_step="patch-review"),
            CommandSpec(name="bootstrap", cli_tokens=("bootstrap-run", "project-open"), flow_step="project-open"),
            CommandSpec(name="terminal", cli_tokens=("terminal",), flow_step="export-handoff"),
        )

        self.assertEqual(
            tuple((entry.flow_step, entry.name, entry.argv) for entry in command_demo_flow_invocation_plan(specs)),
            (
                ("project-open", "bootstrap", ("bootstrap-run",)),
                ("retrieval", "context-basket", ("retrieve",)),
                ("patch-review", "diff-preview", ("review-patch",)),
                ("export-handoff", "terminal", ("terminal",)),
            ),
        )

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

    def test_command_flow_route_summary_prefers_explicit_custom_cli_tokens(self) -> None:
        specs = (
            CommandSpec(
                name="bootstrap",
                aliases=("open", "project"),
                cli_tokens=("bootstrap", "project-open"),
                flow_step="project-open",
            ),
            CommandSpec(
                name="review",
                aliases=("patch", "revise"),
                cli_tokens=("review-patch",),
                flow_step="patch-review",
            ),
        )

        self.assertEqual(
            command_flow_route_summary(specs, ("patch-review", "project-open")),
            (
                ("patch-review", "review", ("review-patch",)),
                ("project-open", "bootstrap", ("bootstrap", "project-open")),
            ),
        )
        self.assertEqual(
            tuple((entry.flow_step, entry.name, entry.cli_tokens) for entry in command_cli_route_catalog(specs)),
            (
                ("project-open", "bootstrap", ("bootstrap", "project-open")),
                ("patch-review", "review", ("review-patch",)),
            ),
        )

    def test_command_flow_route_summary_mixes_explicit_and_fallback_cli_tokens(self) -> None:
        specs = (
            CommandSpec(
                name="bootstrap",
                aliases=("open",),
                cli_tokens=("bootstrap",),
                flow_step="project-open",
            ),
            CommandSpec(name="export", aliases=("save",), flow_step="export-handoff"),
        )

        self.assertEqual(
            command_flow_route_summary(specs),
            (
                ("project-open", "bootstrap", ("bootstrap",)),
                ("export-handoff", "export", ("export", "save")),
            ),
        )

    def test_command_cli_route_contract_supports_explicit_custom_cli_tokens(self) -> None:
        specs = (
            CommandSpec(
                name="bootstrap",
                aliases=("open",),
                cli_tokens=("project-open", "bootstrap-run"),
                flow_step="project-open",
            ),
            CommandSpec(
                name="review",
                aliases=("patch",),
                cli_tokens=("review-patch",),
                flow_step="patch-review",
            ),
        )

        contract = command_cli_route_contract(specs)
        surface_contract = command_cli_surface_contract(specs)

        self.assertEqual(contract.tokens, ("project-open", "bootstrap-run", "review-patch"))
        self.assertEqual(
            contract.lookup_table,
            (
                ("project-open", "bootstrap"),
                ("bootstrap-run", "bootstrap"),
                ("review-patch", "review"),
            ),
        )
        self.assertEqual(
            contract.route_lookup_table,
            (
                ("project-open", "bootstrap"),
                ("bootstrap-run", "bootstrap"),
                ("review-patch", "review"),
            ),
        )
        self.assertEqual(
            contract.route_flow_lookup_table,
            (
                ("project-open", "project-open"),
                ("bootstrap-run", "project-open"),
                ("review-patch", "patch-review"),
            ),
        )
        self.assertEqual(
            contract.route_summary,
            (
                ("project-open", "bootstrap", ("project-open", "bootstrap-run")),
                ("patch-review", "review", ("review-patch",)),
            ),
        )
        self.assertEqual(
            tuple(
                (entry.token, entry.canonical_name, entry.flow_step, entry.lookup_tokens)
                for entry in surface_contract.entries
            ),
            (
                (
                    "project-open",
                    "bootstrap",
                    "project-open",
                    ("bootstrap", "open", "project-open", "bootstrap-run"),
                ),
                (
                    "bootstrap-run",
                    "bootstrap",
                    "project-open",
                    ("bootstrap", "open", "project-open", "bootstrap-run"),
                ),
                (
                    "review-patch",
                    "review",
                    "patch-review",
                    ("review", "patch", "review-patch"),
                ),
            ),
        )

    def test_command_flow_route_summary_normalizes_fallback_cli_tokens(self) -> None:
        specs = (
            CommandSpec(
                name=" Project Open ",
                aliases=("Open Project",),
                flow_step="Project Open",
            ),
            CommandSpec(
                name="Patch Review",
                aliases=("Review Patch",),
                flow_step="Patch Review",
            ),
        )

        self.assertEqual(
            command_flow_route_summary(specs, ("Patch Review", "Project Open")),
            (
                ("patch-review", "Patch Review", ("patch-review", "review-patch")),
                ("project-open", " Project Open ", ("project-open", "open-project")),
            ),
        )
        self.assertEqual(
            command_catalog.command_flow_route_tokens(specs, ("Patch Review", "Project Open")),
            ("patch-review", "project-open"),
        )

    def test_command_demo_cli_route_helpers_lock_demo_order_for_custom_specs(self) -> None:
        specs = (
            CommandSpec(name="context-basket", cli_tokens=("retrieve",), flow_step="retrieval"),
            CommandSpec(name="diff-preview", cli_tokens=("review-patch",), flow_step="patch-review"),
            CommandSpec(name="bootstrap", cli_tokens=("bootstrap-run",), flow_step="project-open"),
            CommandSpec(name="terminal", cli_tokens=("terminal",), flow_step="export-handoff"),
        )

        expected_summary = (
            ("project-open", "bootstrap", ("bootstrap-run",)),
            ("retrieval", "context-basket", ("retrieve",)),
            ("patch-review", "diff-preview", ("review-patch",)),
            ("export-handoff", "terminal", ("terminal",)),
        )

        self.assertEqual(command_demo_cli_route_summary(specs), expected_summary)
        self.assertEqual(command_mvp_cli_route_summary(specs), expected_summary)
        self.assertEqual(
            tuple((entry.flow_step, entry.name, entry.cli_tokens) for entry in command_demo_cli_route_catalog(specs)),
            expected_summary,
        )
        self.assertEqual(
            tuple((entry.flow_step, entry.name, entry.cli_tokens) for entry in command_mvp_cli_route_catalog(specs)),
            expected_summary,
        )
        self.assertEqual(command_demo_cli_route_contract(specs).route_summary, expected_summary)
        self.assertEqual(command_mvp_cli_route_contract(specs).route_summary, expected_summary)

    def test_command_demo_flow_route_helpers_lock_demo_order_for_custom_specs(self) -> None:
        specs = (
            CommandSpec(name="context-basket", cli_tokens=("retrieve",), flow_step="retrieval"),
            CommandSpec(name="diff-preview", cli_tokens=("review-patch",), flow_step="patch-review"),
            CommandSpec(name="bootstrap", cli_tokens=("bootstrap-run",), flow_step="project-open"),
            CommandSpec(name="terminal", cli_tokens=("terminal",), flow_step="export-handoff"),
        )

        expected_summary = (
            ("project-open", "bootstrap", ("bootstrap-run",)),
            ("retrieval", "context-basket", ("retrieve",)),
            ("patch-review", "diff-preview", ("review-patch",)),
            ("export-handoff", "terminal", ("terminal",)),
        )
        expected_route_tokens = ("bootstrap-run", "retrieve", "review-patch", "terminal")

        self.assertEqual(
            tuple((entry.flow_step, entry.name, entry.cli_tokens) for entry in command_demo_flow_route_catalog(specs)),
            expected_summary,
        )
        self.assertEqual(
            tuple((entry.flow_step, entry.name, entry.cli_tokens) for entry in command_mvp_flow_route_catalog(specs)),
            expected_summary,
        )
        self.assertEqual(command_demo_flow_route_summary(specs), expected_summary)
        self.assertEqual(command_mvp_flow_route_summary(specs), expected_summary)
        self.assertEqual(command_demo_flow_route_tokens(specs), expected_route_tokens)
        self.assertEqual(command_mvp_flow_route_tokens(specs), expected_route_tokens)
        self.assertEqual(
            tuple(entry.primary_cli_token for entry in command_demo_flow_route_contract(specs).entries),
            expected_route_tokens,
        )
        self.assertEqual(
            tuple(entry.primary_cli_token for entry in command_mvp_flow_route_contract(specs).entries),
            expected_route_tokens,
        )

    def test_command_lookup_helpers_resolve_explicit_custom_cli_tokens(self) -> None:
        specs = (
            CommandSpec(
                name="bootstrap",
                aliases=("open",),
                cli_tokens=("project-open", "bootstrap-run"),
                flow_step="project-open",
            ),
            CommandSpec(
                name="review",
                aliases=("patch",),
                cli_tokens=("review-patch",),
                flow_step="patch-review",
            ),
        )

        self.assertEqual(command_spec_for(specs, "bootstrap-run").name, "bootstrap")
        self.assertEqual(command_spec_for(specs, "review-patch").name, "review")
        self.assertEqual(canonical_command_for(specs, "bootstrap-run"), "bootstrap")
        self.assertEqual(canonical_command_for(specs, "review-patch"), "review")

    def test_validate_command_catalog_rejects_cli_token_collisions_with_lookup_tokens(self) -> None:
        specs = (
            CommandSpec(
                name="bootstrap",
                cli_tokens=("project-open",),
                flow_step="project-open",
            ),
            CommandSpec(
                name="review",
                aliases=("project-open",),
                flow_step="patch-review",
            ),
        )

        with self.assertRaisesRegex(ValueError, "Duplicate command lookup token: project-open"):
            validate_command_catalog(specs)

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
                ("bootstrap-run", "bootstrap"),
                ("document-open", "bootstrap"),
                ("open-document", "bootstrap"),
                ("context-basket", "context-basket"),
                ("context", "context-basket"),
                ("basket", "context-basket"),
                ("retrieval", "context-basket"),
                ("retrieve", "context-basket"),
                ("diff-preview", "diff-preview"),
                ("diff", "diff-preview"),
                ("review-patch", "diff-preview"),
                ("patch-review", "diff-preview"),
                ("terminal", "terminal"),
                ("export", "terminal"),
                ("save-export", "terminal"),
                ("persist", "terminal"),
                ("persist-continue", "terminal"),
                ("apply-patch", "terminal"),
                ("patch-apply", "terminal"),
                ("reject-patch", "terminal"),
                ("patch-reject", "terminal"),
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
                ("bootstrap", "open", "project-open", "project", "bootstrap-run", "document-open", "open-document"),
                ("context-basket", "context", "basket", "retrieval", "retrieve"),
                ("diff-preview", "diff", "review-patch", "patch-review"),
                (
                    "terminal",
                    "export",
                    "save-export",
                    "persist",
                    "persist-continue",
                    "apply-patch",
                    "patch-apply",
                    "reject-patch",
                    "patch-reject",
                    "export-handoff",
                ),
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
                ("bootstrap-run", "bootstrap"),
                ("document-open", "bootstrap"),
                ("open-document", "bootstrap"),
                ("context-basket", "context-basket"),
                ("context", "context-basket"),
                ("basket", "context-basket"),
                ("retrieval", "context-basket"),
                ("retrieve", "context-basket"),
                ("diff-preview", "diff-preview"),
                ("diff", "diff-preview"),
                ("review-patch", "diff-preview"),
                ("terminal", "terminal"),
                ("export", "terminal"),
                ("save-export", "terminal"),
                ("persist", "terminal"),
                ("persist-continue", "terminal"),
                ("apply-patch", "terminal"),
                ("patch-apply", "terminal"),
                ("reject-patch", "terminal"),
                ("patch-reject", "terminal"),
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
                ("bootstrap", "open", "project-open", "project", "bootstrap-run", "document-open", "open-document"),
                ("context-basket", "context", "basket", "retrieval", "retrieve"),
                ("diff-preview", "diff", "diff_preview", "review-patch"),
                (
                    "terminal",
                    "export",
                    "save-export",
                    "persist",
                    "persist-continue",
                    "apply-patch",
                    "patch-apply",
                    "reject-patch",
                    "patch-reject",
                ),
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
        self.assertEqual(contract.invocation_plan, command_mvp_flow_invocation_plan())
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
                ("bootstrap-run", "bootstrap"),
                ("document-open", "bootstrap"),
                ("open-document", "bootstrap"),
                ("context-basket", "context-basket"),
                ("context", "context-basket"),
                ("basket", "context-basket"),
                ("retrieval", "context-basket"),
                ("retrieve", "context-basket"),
                ("diff-preview", "diff-preview"),
                ("diff", "diff-preview"),
                ("review-patch", "diff-preview"),
                ("patch-review", "diff-preview"),
                ("terminal", "terminal"),
                ("export", "terminal"),
                ("save-export", "terminal"),
                ("persist", "terminal"),
                ("persist-continue", "terminal"),
                ("apply-patch", "terminal"),
                ("patch-apply", "terminal"),
                ("reject-patch", "terminal"),
                ("patch-reject", "terminal"),
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
