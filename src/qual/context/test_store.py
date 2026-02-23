from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.qual.context.store import ContextBasketStore


class ContextBasketStoreTests(unittest.TestCase):
    def test_primary_load_scrubs_recovery_marker_and_invalid_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "context_basket.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "item_ids": ["a"],
                        "recovered_from": "tmp",
                        "updated_at": "not-a-timestamp",
                    }
                ),
                encoding="utf-8",
            )
            store = ContextBasketStore(root)

            basket = store.load()

            self.assertEqual(["a"], basket.item_ids)
            rewritten = json.loads(path.read_text(encoding="utf-8"))
            self.assertNotIn("recovered_from", rewritten)
            self.assertIn("updated_at", rewritten)

    def test_backup_recovery_records_recovered_from(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            backup = root / "context_basket.bak.json"
            backup.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "item_ids": ["b"],
                        "updated_at": "2026-01-01T00:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )
            store = ContextBasketStore(root)

            basket = store.load()

            self.assertEqual(["b"], basket.item_ids)
            rewritten = json.loads((root / "context_basket.json").read_text(encoding="utf-8"))
            self.assertEqual("backup", rewritten.get("recovered_from"))


if __name__ == "__main__":
    unittest.main()
