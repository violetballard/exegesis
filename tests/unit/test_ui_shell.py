from __future__ import annotations

import unittest
from types import SimpleNamespace

from src.qual.ui.shell import ShellUI


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


if __name__ == "__main__":
    unittest.main()
