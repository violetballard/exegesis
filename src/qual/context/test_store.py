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

    def test_invalid_primary_without_fallback_self_heals_empty_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            primary = root / "context_basket.json"
            primary.write_text("{not-json", encoding="utf-8")
            store = ContextBasketStore(root)

            basket = store.load()

            self.assertEqual([], basket.item_ids)
            self.assertTrue(primary.exists())
            rewritten = json.loads(primary.read_text(encoding="utf-8"))
            self.assertEqual([], rewritten.get("item_ids"))
            self.assertNotIn("recovered_from", rewritten)

    def test_invalid_primary_with_backup_recovers_backup_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "context_basket.json").write_text("{bad-json", encoding="utf-8")
            (root / "context_basket.bak.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "item_ids": ["c1", "c2"],
                        "updated_at": "2026-01-01T00:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )
            store = ContextBasketStore(root)

            basket = store.load()

            self.assertEqual(["c1", "c2"], basket.item_ids)
            rewritten = json.loads((root / "context_basket.json").read_text(encoding="utf-8"))
            self.assertEqual("backup", rewritten.get("recovered_from"))

    def test_non_int_schema_version_is_rewritten_to_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            primary = root / "context_basket.json"
            primary.write_text(
                json.dumps(
                    {
                        "schema_version": "1",
                        "item_ids": ["x"],
                        "updated_at": "2026-01-01T00:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )
            store = ContextBasketStore(root)

            basket = store.load()

            self.assertEqual(["x"], basket.item_ids)
            rewritten = json.loads(primary.read_text(encoding="utf-8"))
            self.assertEqual(1, rewritten.get("schema_version"))

    def test_bool_schema_version_is_rewritten_to_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            primary = root / "context_basket.json"
            primary.write_text(
                json.dumps(
                    {
                        "schema_version": True,
                        "item_ids": ["y"],
                        "updated_at": "2026-01-01T00:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )
            store = ContextBasketStore(root)

            basket = store.load()

            self.assertEqual(["y"], basket.item_ids)
            rewritten = json.loads(primary.read_text(encoding="utf-8"))
            self.assertEqual(1, rewritten.get("schema_version"))


if __name__ == "__main__":
    unittest.main()
