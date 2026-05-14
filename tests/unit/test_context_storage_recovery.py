from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.qual.context.basket import ContextBasket
from src.qual.context.store import ContextBasketStore
from src.qual.storage.vault import VaultService


class ContextStoreRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.store = ContextBasketStore(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_clear_removes_primary_backup_and_corrupt(self) -> None:
        self.store.save(ContextBasket(item_ids=["a"]))
        self.store.save(ContextBasket(item_ids=["b"]))  # Create backup.
        self.store._path.with_suffix(".corrupt.json").write_text("{bad", encoding="utf-8")

        self.store.clear()

        self.assertFalse(self.store._path.exists())
        self.assertFalse(self.store._backup_path.exists())
        self.assertFalse(self.store._path.with_suffix(".corrupt.json").exists())

    def test_future_schema_primary_not_rotated_into_backup(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps({"schema_version": 999, "item_ids": ["x"]}),
            encoding="utf-8",
        )

        self.store.save(ContextBasket(item_ids=["a"]))

        self.assertFalse(self.store._backup_path.exists())
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("schema_version"), 1)
        self.assertEqual(payload.get("item_ids"), ["a"])

    def test_corrupt_primary_quarantines_and_recovers_from_backup(self) -> None:
        self.store.save(ContextBasket(item_ids=["first"]))
        self.store.save(ContextBasket(item_ids=["second"]))  # Creates backup with "first".
        self.store._path.write_text("{bad", encoding="utf-8")

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first"])
        # Successful recovery rewrites primary and clears stale quarantine artifacts.
        self.assertFalse(self.store._path.with_suffix(".corrupt.json").exists())
        self.assertEqual(
            json.loads(self.store._path.read_text(encoding="utf-8")).get("item_ids"),
            ["first"],
        )


class VaultRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.svc = VaultService()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_clear_state_removes_all_state_files_and_relocks(self) -> None:
        state = self.svc.create_or_open(self.root, "p1")
        self.svc.unlock(state)
        self.svc.lock(state)  # Generates backup.
        (state.root_dir / ".vault_state.corrupt.json").write_text("{}", encoding="utf-8")

        self.svc.clear_state(state)

        self.assertTrue(state.is_locked)
        self.assertFalse((state.root_dir / ".vault_state.json").exists())
        self.assertFalse((state.root_dir / ".vault_state.bak.json").exists())
        self.assertFalse((state.root_dir / ".vault_state.corrupt.json").exists())

    def test_corrupt_primary_quarantines_and_recovers_from_backup(self) -> None:
        state = self.svc.create_or_open(self.root, "p2")
        self.svc.lock(state)
        self.svc.unlock(state)  # Backup now exists.
        state_path = state.root_dir / ".vault_state.json"
        state_path.write_text("{bad", encoding="utf-8")

        reopened = self.svc.create_or_open(self.root, "p2")

        # Successful recovery rewrites primary and clears stale quarantine artifacts.
        self.assertFalse((state.root_dir / ".vault_state.corrupt.json").exists())
        self.assertIsInstance(reopened.is_locked, bool)
        self.assertTrue((state.root_dir / ".vault_state.json").exists())

    def test_project_name_mismatch_forces_locked_state(self) -> None:
        state = self.svc.create_or_open(self.root, "p3")
        state_path = state.root_dir / ".vault_state.json"
        state_path.write_text(
            json.dumps({"schema_version": 1, "project_name": "other", "is_locked": False}),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p3")

        self.assertTrue(reopened.is_locked)


if __name__ == "__main__":
    unittest.main()
