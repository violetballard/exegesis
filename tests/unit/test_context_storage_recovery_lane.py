from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.qual.context.set_store import ContextSetStore
from src.qual.context.store import ContextBasketStore


class ContextBasketRecoveryLaneTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.store = ContextBasketStore(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_empty_tmp_payload_is_not_treated_as_recovery_source(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "recovered_from": "manual",
                }
            ),
            encoding="utf-8",
        )
        self.store._tmp_path().write_text("[]", encoding="utf-8")

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, [])
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("item_ids"), [])
        self.assertNotIn("recovered_from", primary_payload)
        self.assertTrue(self.store._path.with_suffix(".corrupt.json").exists())


class ContextSetRecoveryLaneTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.store = ContextSetStore(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_empty_tmp_payload_is_not_treated_as_recovery_source(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "recovered_from": "manual",
                }
            ),
            encoding="utf-8",
        )
        self.store._tmp_path().write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "context_sets": [],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded, [])
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("context_sets"), [])
        self.assertNotIn("recovered_from", primary_payload)
        self.assertTrue(self.store._path.with_suffix(".corrupt.json").exists())
