from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from exegesis_textual.panes.document_pane import (
    CURRENT_DRAFT_SLUG,
    DOCUMENT_FIXTURES,
    load_document_fixture_content,
)


class DocumentFixtureTests(unittest.TestCase):
    def test_seeded_current_draft_loads_from_markdown_fixture(self) -> None:
        fixture = DOCUMENT_FIXTURES[CURRENT_DRAFT_SLUG]
        seed_content = load_document_fixture_content(Path(fixture.location).name)
        self.assertTrue(seed_content.strip())
        self.assertTrue(fixture.content.strip())
        self.assertEqual(Path(fixture.location).name, "current_draft.md")

    def test_document_fixture_loader_uses_configured_directory(self) -> None:
        old_value = os.environ.get("EXEGESIS_DOCUMENT_FIXTURE_DIR")
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "example.md").write_text("# From Disk\n", encoding="utf-8")
            os.environ["EXEGESIS_DOCUMENT_FIXTURE_DIR"] = tmpdir
            try:
                self.assertEqual(load_document_fixture_content("example.md"), "# From Disk\n")
            finally:
                if old_value is None:
                    os.environ.pop("EXEGESIS_DOCUMENT_FIXTURE_DIR", None)
                else:
                    os.environ["EXEGESIS_DOCUMENT_FIXTURE_DIR"] = old_value


if __name__ == "__main__":
    unittest.main()
