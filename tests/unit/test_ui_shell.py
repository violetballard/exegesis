from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.qual.ui.a2ui import describe_terminal_artifact_cli_fallback_route_contract
from src.qual.ui.a2ui import describe_terminal_artifact_cli_fallback_route_contract_manifest
from src.qual.ui.a2ui import describe_terminal_artifact_cli_fallback_route_contract_manifest_fingerprints
from src.qual.ui.a2ui import terminal_artifact_cli_fallback_route_contract_manifest_fingerprints_fingerprint
from src.qual.ui.shell import ShellUI, describe_shell_ui_contract
from src.qual.ui.shell import describe_shell_ui_contract_fingerprints


class ShellUITests(unittest.TestCase):
    def test_format_item_id_handles_blank_and_non_string_values(self) -> None:
        self.assertEqual(ShellUI._format_item_id(None), "<blank>")
        self.assertEqual(ShellUI._format_item_id(42), "42")

    def test_format_item_id_quotes_and_truncates_preview_safely(self) -> None:
        self.assertEqual(ShellUI._format_item_id("  alpha,\n beta  "), '"alpha, beta"')
        self.assertEqual(ShellUI._format_item_id("x" * 30), "xxxxxxxxxxxxxxxxxxxxx...")

    def test_render_startup_keeps_context_preview_stable_for_malformed_item_ids(self) -> None:
        runtime = SimpleNamespace(
            vault=SimpleNamespace(project_name="Demo", root_dir="/tmp/demo", is_locked=False),
            basket=SimpleNamespace(item_ids=[None, "  alpha,\n beta  ", "x" * 30, "ignored"]),
        )

        text = ShellUI().render_startup(runtime)

        self.assertIn("- context_items: 4", text)
        self.assertIn('- context_preview: <blank>, "alpha, beta", xxxxxxxxxxxxxxxxxxxxx..., +1 more item', text)

    def test_render_startup_treats_mappings_as_single_malformed_items(self) -> None:
        runtime = SimpleNamespace(
            vault=SimpleNamespace(project_name="Demo", root_dir="/tmp/demo", is_locked=False),
            basket=SimpleNamespace(item_ids={"first": "alpha"}),
        )

        text = ShellUI().render_startup(runtime)

        self.assertIn("- context_items: 1", text)
        self.assertIn("- context_preview: {'first': 'alpha'}", text)

    def test_render_cli_fallback_uses_shared_resolver_for_clean_card_hints(self) -> None:
        shell = ShellUI()
        artifact = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "json"},
        }

        with patch(
            "src.qual.ui.shell.resolve_terminal_artifact_cli_fallback_target",
            return_value=(artifact, "card"),
        ) as resolver:
            with patch(
                "src.qual.ui.shell.render_terminal_cli_fallback",
                return_value="cli-fallback",
            ) as cli_fallback:
                text = shell.render_cli_fallback(artifact, kind="card")

        self.assertEqual(text, "cli-fallback")
        resolver.assert_called_once_with(artifact, kind="card")
        cli_fallback.assert_called_once_with(artifact, kind="card")

    def test_shell_contract_route_precedence_matches_the_public_route_contract_snapshot(self) -> None:
        shell_contract = describe_shell_ui_contract()
        route_contract = describe_terminal_artifact_cli_fallback_route_contract()

        self.assertEqual(shell_contract["route_precedence"], route_contract["route_precedence"])
        self.assertEqual(
            shell_contract["route_precedence_contract"],
            route_contract["route_precedence_contract"],
        )
        self.assertEqual(
            shell_contract["route_precedence_contract_fingerprint"],
            route_contract["route_precedence_contract_fingerprint"],
        )

    def test_shell_contract_can_embed_the_canonical_route_manifest_snapshot(self) -> None:
        shell_contract = describe_shell_ui_contract(include_terminal_artifact_cli_fallback_route=True)
        route_manifest = describe_terminal_artifact_cli_fallback_route_contract_manifest()

        self.assertEqual(
            shell_contract["terminal_artifact_cli_fallback_route_contract_manifest"],
            route_manifest,
        )
        self.assertEqual(
            shell_contract["terminal_artifact_cli_fallback_route_contract_manifest_fingerprint"],
            route_manifest["contract_fingerprint"],
        )

    def test_shell_contract_mirrors_the_route_manifest_fingerprints_slice(self) -> None:
        shell_contract = describe_shell_ui_contract(include_terminal_artifact_cli_fallback_route=True)
        shell_fingerprints = describe_shell_ui_contract_fingerprints(
            include_terminal_artifact_cli_fallback_route=True,
        )
        route_manifest_fingerprints = describe_terminal_artifact_cli_fallback_route_contract_manifest_fingerprints()

        self.assertEqual(
            shell_contract["terminal_artifact_cli_fallback_route_contract_manifest_fingerprints"],
            route_manifest_fingerprints,
        )
        self.assertEqual(
            shell_contract["terminal_artifact_cli_fallback_route_contract_manifest_fingerprints_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_manifest_fingerprints_fingerprint(),
        )
        self.assertEqual(
            shell_fingerprints["terminal_artifact_cli_fallback_route_contract_manifest_fingerprints"],
            terminal_artifact_cli_fallback_route_contract_manifest_fingerprints_fingerprint(),
        )
        self.assertEqual(
            shell_fingerprints["terminal_artifact_cli_fallback_route_contract_manifest_fingerprints_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_manifest_fingerprints_fingerprint(),
        )


if __name__ == "__main__":
    unittest.main()
