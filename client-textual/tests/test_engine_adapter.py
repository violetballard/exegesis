from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
for package_root in (REPO_ROOT / "engine" / "src", REPO_ROOT / "shared" / "src", REPO_ROOT / "client-textual" / "src"):
    root_text = str(package_root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)

from exegesis_textual.engine_adapter import ShellEngineAdapter


class ShellEngineAdapterTests(unittest.TestCase):
    def test_opens_project_lists_documents_and_saves_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            draft = project_root / "drafts" / "current.md"
            draft.parent.mkdir()
            draft.write_text("# Draft\n\nOriginal body.", encoding="utf-8")

            adapter = ShellEngineAdapter()
            adapter.open_project(project_root)
            items = adapter.list_project_items()

            self.assertEqual([item.id for item in items], ["drafts/current.md"])
            self.assertEqual(items[0].metadata["project_id_or_path"], str(project_root))

            opened = adapter.open_document("drafts/current.md")
            self.assertEqual(opened.title, "current.md")
            self.assertIn("Original body", opened.content)

            saved = adapter.save_document("# Draft\n\nUpdated body.")
            self.assertFalse(saved.dirty)
            self.assertEqual(draft.read_text(encoding="utf-8"), "# Draft\n\nUpdated body.")

    def test_selection_and_basket_operations_delegate_to_engine_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            draft = project_root / "current.md"
            draft.write_text("Hello world", encoding="utf-8")

            adapter = ShellEngineAdapter()
            adapter.open_project(project_root)
            adapter.open_document("current.md")
            adapter.set_document_selection(0, 5)

            items = adapter.add_excerpt_to_basket(
                item_id="excerpt:current:0-5",
                label="Excerpt",
                source_document_id="current.md",
                source_document_type="draft",
                selected_text="Hello",
                start=0,
                end=5,
            )
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].payload["selected_text"], "Hello")

            adapter.add_document_to_basket(
                document_id="current.md",
                label="current.md",
                document_type="draft",
                content="Hello world",
            )
            self.assertEqual(len(adapter.state.basket.items), 2)

            adapter.remove_basket_item("excerpt:current:0-5")
            self.assertEqual([item.id for item in adapter.state.basket.items], ["document:current.md"])

            adapter.clear_basket()
            self.assertEqual(adapter.state.basket.items, [])

    def test_document_lifecycle_delegates_to_engine_service(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            adapter = ShellEngineAdapter()
            adapter.open_project(project_root)

            created = adapter.create_document(
                category="Drafts",
                title="Working Draft.md",
                content="# Working Draft\n",
                document_type="draft",
            )
            self.assertEqual(created.id, "drafts/Working Draft.md")
            self.assertTrue((project_root / "drafts" / "Working Draft.md").exists())

            source = project_root / "source.md"
            source.write_text("# Source\n", encoding="utf-8")
            imported = adapter.import_markdown_document(source_path=source, category="Literature")
            self.assertEqual(imported.id, "literature/source.md")

            renamed = adapter.rename_document(imported.id, "Renamed Source.md")
            self.assertEqual(renamed.id, "literature/Renamed Source.md")

            trashed = adapter.delete_document(created.id)
            self.assertTrue(trashed.metadata["trashed"])
            self.assertTrue(trashed.metadata["trashed_at"])
            self.assertFalse((project_root / "drafts" / "Working Draft.md").exists())
            self.assertTrue(Path(trashed.path).exists())
            self.assertEqual([item.id for item in adapter.list_trash_items()], [trashed.id])
            trash_snapshot = adapter.open_trash_document(trashed.id)
            self.assertEqual(trash_snapshot.document_id, trashed.id)
            self.assertIn("Working Draft", trash_snapshot.content)

            restored = adapter.restore_trash_document(trashed.id)
            self.assertEqual(restored.id, created.id)
            self.assertTrue((project_root / "drafts" / "Working Draft.md").exists())

            trashed_again = adapter.delete_document(restored.id)
            permanently_deleted = adapter.permanently_delete_trash_document(trashed_again.id)
            self.assertEqual(permanently_deleted.metadata["original_id"], restored.id)
            self.assertFalse(Path(permanently_deleted.path).exists())

    def test_document_lifecycle_accepts_explicit_relative_paths_for_folders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            adapter = ShellEngineAdapter()
            adapter.open_project(project_root)

            created = adapter.create_document(
                category="Memos",
                title="same.md",
                content="# A\n",
                document_type="memo",
                relative_path="memos/folder-a/same.md",
            )
            self.assertEqual(created.id, "memos/folder-a/same.md")

            source = project_root / "same.md"
            source.write_text("# B\n", encoding="utf-8")
            imported = adapter.import_markdown_document(
                source_path=source,
                category="Memos",
                relative_path="memos/folder-b/same.md",
            )
            self.assertEqual(imported.id, "memos/folder-b/same.md")

            moved = adapter.move_document(created.id, "memos/folder-c/same.md")
            self.assertEqual(moved.id, "memos/folder-c/same.md")
            self.assertFalse((project_root / "memos/folder-a/same.md").exists())
            self.assertTrue((project_root / "memos/folder-c/same.md").exists())



if __name__ == "__main__":
    unittest.main()
