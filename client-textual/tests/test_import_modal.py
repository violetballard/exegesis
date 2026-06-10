from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Footer

from exegesis_textual.layout.shell import (
    IMPORT_BROWSER_OPTIONS_ID,
    ImportMarkdownModal,
)
from exegesis_textual.services.imports import (
    browseable_import_entries,
    importable_markdown_files_in_folder,
    is_safe_external_link,
    is_safe_markdown_import_source,
    is_markdown_file,
)


class ImportModalTests(unittest.TestCase):
    def test_is_markdown_file_accepts_markdown_extensions_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            markdown = root / "draft.md"
            other = root / "notes.txt"
            markdown.write_text("# Draft\n", encoding="utf-8")
            other.write_text("notes\n", encoding="utf-8")
            self.assertTrue(is_markdown_file(markdown))
            self.assertFalse(is_markdown_file(other))

    def test_browseable_import_entries_shows_markdown_files_first_then_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "alpha.md").write_text("# Alpha\n", encoding="utf-8")
            (root / "draft.md").write_text("# Draft\n", encoding="utf-8")
            (root / "notes.txt").write_text("notes\n", encoding="utf-8")
            (root / ".hidden.md").write_text("# Hidden\n", encoding="utf-8")
            names = [entry.name for entry in browseable_import_entries(root)]
            self.assertEqual(names, ["alpha.md", "draft.md", "docs"])
            self.assertNotIn("notes.txt", names)
            self.assertNotIn(".hidden.md", names)

    def test_browseable_import_entries_filters_by_current_directory_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "fieldnotes").mkdir()
            (root / "field_memo.md").write_text("# Field\n", encoding="utf-8")
            (root / "draft.md").write_text("# Draft\n", encoding="utf-8")

            names = [entry.name for entry in browseable_import_entries(root, "field")]

            self.assertEqual(names, ["field_memo.md", "fieldnotes"])

    def test_importable_markdown_files_in_folder_recurses_without_hidden_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            nested = root / "nested"
            nested.mkdir()
            hidden = root / ".hidden"
            hidden.mkdir()
            (root / "root.md").write_text("# Root\n", encoding="utf-8")
            (nested / "nested.md").write_text("# Nested\n", encoding="utf-8")
            (hidden / "secret.md").write_text("# Secret\n", encoding="utf-8")
            (root / "notes.txt").write_text("notes\n", encoding="utf-8")

            names = [path.relative_to(root).as_posix() for path in importable_markdown_files_in_folder(root)]

            self.assertEqual(names, ["nested/nested.md", "root.md"])

    def test_safe_markdown_import_source_rejects_hidden_files_and_folders(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            visible = root / "visible.md"
            hidden_file = root / ".hidden.md"
            hidden_dir = root / ".hidden"
            hidden_dir.mkdir()
            hidden_nested = hidden_dir / "nested.md"
            visible.write_text("# Visible\n", encoding="utf-8")
            hidden_file.write_text("# Hidden\n", encoding="utf-8")
            hidden_nested.write_text("# Hidden nested\n", encoding="utf-8")

            self.assertTrue(is_safe_markdown_import_source(visible))
            self.assertFalse(is_safe_markdown_import_source(hidden_file))
            self.assertFalse(is_safe_markdown_import_source(hidden_nested))

    def test_safe_external_link_allows_only_web_and_local_file_urls(self) -> None:
        self.assertTrue(is_safe_external_link("https://example.com/source.pdf"))
        self.assertTrue(is_safe_external_link("http://example.com/source.pdf"))
        self.assertTrue(is_safe_external_link("file:///tmp/source.pdf"))
        self.assertFalse(is_safe_external_link("javascript:alert(1)"))
        self.assertFalse(is_safe_external_link("exegesis://settings/secret"))
        self.assertFalse(is_safe_external_link("file://evil.example/tmp/source.pdf"))


class ImportModalInteractionTests(unittest.IsolatedAsyncioTestCase):
    async def test_mouse_clicking_folder_navigates_without_stale_option_crash(self) -> None:
        class TestApp(App[None]):
            def compose(self) -> ComposeResult:
                yield Footer()

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            imports = root / "imports"
            imports.mkdir()
            (imports / "sample.md").write_text("# Sample\n", encoding="utf-8")
            (root / "demo-project").mkdir()

            app = TestApp()
            async with app.run_test(size=(100, 30)) as pilot:
                await app.push_screen(ImportMarkdownModal(root))
                await pilot.pause()

                clicked = await pilot.click(f"#{IMPORT_BROWSER_OPTIONS_ID}", offset=(2, 3))
                await pilot.pause()

                self.assertTrue(clicked)
                self.assertEqual(app.screen._current_dir, imports)
                option_list = app.screen.query_one(f"#{IMPORT_BROWSER_OPTIONS_ID}")
                self.assertIn("sample.md", [str(option.prompt) for option in option_list._options])


if __name__ == "__main__":
    unittest.main()
