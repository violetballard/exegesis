from __future__ import annotations

import unittest

from textual.app import App, ComposeResult
from textual.widgets import Markdown, Static

from exegesis_textual.panes.inspector_pane import (
    INSPECTOR_EXCERPT_TEXT_ID,
    INSPECTOR_MARKDOWN_ID,
    INSPECTOR_SAVE_SHORT_SUMMARY_ID,
    INSPECTOR_SUMMARY_ACTIONS_ID,
    InspectorPane,
    default_inspector_markdown,
    render_inspector_markdown,
)


class InspectorPaneRenderTests(unittest.TestCase):
    def test_renders_selection_type_word_count_and_token_count(self) -> None:
        output = render_inspector_markdown(
            "Excerpt",
            "Selected excerpt from current_draft.md.",
            ("Saved from the current document selection.",),
            "Actual excerpt text.",
            selection_type="draft",
            word_count=11,
            token_count=42,
        )
        self.assertIn("Document type: **Draft**", output)
        self.assertIn("Words: **11**", output)
        self.assertIn("Tokens: **~42**", output)
        self.assertNotIn("### Excerpt", output)
        self.assertNotIn("Actual excerpt text.", output)
        self.assertIn("Selected excerpt from current_draft.md.", output)
        self.assertIn("- Saved from the current document selection.", output)

    def test_renders_without_optional_metadata(self) -> None:
        output = render_inspector_markdown(
            "Document",
            "Primary manuscript for the project.",
            ("The document pane should feel centered around this file first.",),
        )
        self.assertNotIn("Document type:", output)
        self.assertNotIn("Tokens:", output)
        self.assertIn("Primary manuscript for the project.", output)
        self.assertIn("- The document pane should feel centered around this file first.", output)

    def test_renders_token_capacity_when_provided(self) -> None:
        output = render_inspector_markdown(
            "Main chat",
            "Chat state.",
            (),
            token_count=12,
            token_capacity=256 * 1024,
        )
        self.assertIn("Tokens: **~12 / 256k**", output)

    def test_default_state_has_no_scaffold_explanation(self) -> None:
        output = default_inspector_markdown()
        self.assertIn("No selection.", output)
        self.assertNotIn("protocol", output.lower())
        self.assertNotIn("scaffold", output.lower())


class InspectorPaneBehaviorTests(unittest.IsolatedAsyncioTestCase):
    async def test_excerpt_text_is_static_and_summary_buttons_can_be_hidden(self) -> None:
        class TestApp(App[None]):
            def compose(self) -> ComposeResult:
                yield InspectorPane()

        app = TestApp()
        async with app.run_test() as pilot:
            inspector = app.query_one(InspectorPane)
            inspector.show_subject(
                "current_draft.md",
                "",
                (),
                "Actual excerpt text.",
                selection_type="draft",
                word_count=5,
                token_count=42,
                allow_summary_actions=False,
            )
            await pilot.pause()
            self.assertEqual(str(app.query_one(f"#{INSPECTOR_EXCERPT_TEXT_ID}", Static).render()), "Actual excerpt text.")
            self.assertFalse(app.query_one(f"#{INSPECTOR_SUMMARY_ACTIONS_ID}").display)
            self.assertTrue(app.query_one(f"#{INSPECTOR_SAVE_SHORT_SUMMARY_ID}").disabled)

    async def test_document_selection_can_show_summary_buttons(self) -> None:
        class TestApp(App[None]):
            def compose(self) -> ComposeResult:
                yield InspectorPane()

        app = TestApp()
        async with app.run_test() as pilot:
            inspector = app.query_one(InspectorPane)
            inspector.show_subject(
                "current_draft.md",
                "",
                (),
                "Document excerpt.",
                selection_type="draft",
                word_count=5,
                token_count=42,
                allow_summary_actions=True,
            )
            await pilot.pause()
            self.assertTrue(app.query_one(f"#{INSPECTOR_SUMMARY_ACTIONS_ID}").display)
            self.assertFalse(app.query_one(f"#{INSPECTOR_SAVE_SHORT_SUMMARY_ID}").disabled)

    async def test_inspector_markdown_does_not_auto_open_links(self) -> None:
        class TestApp(App[None]):
            def compose(self) -> ComposeResult:
                yield InspectorPane()

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            markdown = app.query_one(f"#{INSPECTOR_MARKDOWN_ID}", Markdown)
            self.assertFalse(markdown._open_links)


if __name__ == "__main__":
    unittest.main()
