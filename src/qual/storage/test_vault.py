from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.qual.storage.vault import VaultService


class VaultServiceTests(unittest.TestCase):
    def test_primary_load_scrubs_stale_recovery_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_root = root / "demo"
            project_root.mkdir(parents=True, exist_ok=True)
            (project_root / ".vault_state.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "project_name": "demo",
                        "is_locked": False,
                        "recovered_from": "tmp",
                        "updated_at": "2026-01-01T00:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )
            service = VaultService()

            state = service.create_or_open(root, "demo")

            self.assertFalse(state.is_locked)
            rewritten = json.loads((project_root / ".vault_state.json").read_text(encoding="utf-8"))
            self.assertNotIn("recovered_from", rewritten)

    def test_backup_recovery_marks_recovered_from(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_root = root / "demo"
            project_root.mkdir(parents=True, exist_ok=True)
            (project_root / ".vault_state.bak.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "project_name": "demo",
                        "is_locked": False,
                        "updated_at": "2026-01-01T00:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )
            service = VaultService()

            state = service.create_or_open(root, "demo")

            self.assertFalse(state.is_locked)
            rewritten = json.loads((project_root / ".vault_state.json").read_text(encoding="utf-8"))
            self.assertEqual("backup", rewritten.get("recovered_from"))


if __name__ == "__main__":
    unittest.main()
