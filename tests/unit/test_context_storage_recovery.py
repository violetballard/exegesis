from __future__ import annotations

import math
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_context_basket_normalizes_numeric_item_ids(self) -> None:
        basket = ContextBasket(item_ids=[" keep ", 7, 2.5, False, None, "7"])

        self.assertEqual(basket.item_ids, ["keep", "7", "2.5"])

    def test_context_basket_add_and_remove_numeric_item_ids(self) -> None:
        basket = ContextBasket()

        basket.add(7)
        basket.add(" 7 ")
        basket.add(2.5)
        basket.remove(7)

        self.assertEqual(basket.item_ids, ["2.5"])

    def test_context_basket_drops_non_finite_numeric_item_ids(self) -> None:
        basket = ContextBasket(item_ids=[" keep ", math.nan, math.inf, -math.inf, 7])

        self.assertEqual(basket.item_ids, ["keep", "7"])

    def test_numeric_item_ids_survive_store_round_trip(self) -> None:
        basket = ContextBasket(item_ids=[" keep ", 7, 2.5, False, None, "7"])

        self.store.save(basket)
        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["keep", "7", "2.5"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["keep", "7", "2.5"])

    def test_non_finite_numeric_item_ids_are_dropped_and_rewritten_on_load(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "item_ids": [" keep ", math.nan, math.inf, -math.inf, 7],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["keep", "7"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["keep", "7"])
        self.assertEqual(payload.get("schema_version"), 1)

    def test_clear_removes_primary_backup_and_corrupt(self) -> None:
        self.store.save(ContextBasket(item_ids=["a"]))
        self.store.save(ContextBasket(item_ids=["b"]))  # Create backup.
        self.store._path.with_suffix(".corrupt.json").write_text("{bad", encoding="utf-8")

        self.store.clear()

        self.assertFalse(self.store._path.exists())
        self.assertFalse(self.store._backup_path.exists())
        self.assertFalse(self.store._path.with_suffix(".corrupt.json").exists())

    def test_clear_removes_quarantined_backup_and_seed_files(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._backup_path.with_name("context_basket.bak.corrupt.json").write_text(
            "{bad",
            encoding="utf-8",
        )
        self.store._seed_state_path().with_name("context_basket.seed.corrupt.json").write_text(
            "{bad",
            encoding="utf-8",
        )

        self.store.clear()

        self.assertFalse(self.store._backup_path.with_name("context_basket.bak.corrupt.json").exists())
        self.assertFalse(self.store._seed_state_path().with_name("context_basket.seed.corrupt.json").exists())

    def test_clear_removes_temporary_primary_backup_and_seed_files(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._tmp_path().write_text("{\"schema_version\": 1}", encoding="utf-8")
        self.store._backup_tmp_path().write_text("{\"schema_version\": 1}", encoding="utf-8")
        self.store._seed_tmp_path().write_text("{\"schema_version\": 1}", encoding="utf-8")

        self.store.clear()

        self.assertFalse(self.store._tmp_path().exists())
        self.assertFalse(self.store._backup_tmp_path().exists())
        self.assertFalse(self.store._seed_tmp_path().exists())

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

    def test_corrupt_primary_recovery_from_backup_records_recovery_source(self) -> None:
        self.store.save(ContextBasket(item_ids=["first"]))
        self.store.save(ContextBasket(item_ids=["second"]))  # Creates backup with "first".
        self.store._path.write_text("{bad", encoding="utf-8")

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["first"])
        self.assertEqual(payload.get("recovered_from"), "backup")

    def test_mixed_scalar_and_non_scalar_item_ids_are_salvaged_and_rewritten(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "item_ids": [" keep ", 7, {"id": "discard"}, "", 2.5, None, "keep", " second "],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["keep", "7", "2.5", "second"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["keep", "7", "2.5", "second"])
        self.assertEqual(payload.get("schema_version"), 1)

    def test_invalid_item_id_entries_force_primary_rewrite_even_when_remaining_ids_match(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "item_ids": ["first", None],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["first"])
        self.assertEqual(payload.get("schema_version"), 1)
        self.assertNotEqual(payload.get("updated_at"), "2026-03-20T12:00:00+00:00")

    def test_valid_primary_wins_over_stale_tmp_payload(self) -> None:
        self.store.save(ContextBasket(item_ids=["primary"]))
        self.store._tmp_path().write_text(
            json.dumps({"schema_version": 1, "item_ids": ["tmp"]}),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["primary"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["primary"])
        self.assertFalse(self.store._tmp_path().exists())

    def test_legacy_list_payload_salvages_valid_entries(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps([" first ", None, "second", "first", "  "]),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first", "second"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["first", "second"])
        self.assertEqual(payload.get("schema_version"), 1)

    def test_explicit_legacy_schema_version_zero_is_salvaged_and_rewritten(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps({"schema_version": 0, "item_ids": [" first ", "second", "first"]}),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first", "second"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("schema_version"), 1)
        self.assertEqual(payload.get("item_ids"), ["first", "second"])

    def test_invalid_metadata_is_salvaged_and_rewritten(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "not-a-timestamp",
                    "recovered_from": "manual",
                    "item_ids": ["first", "second"],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first", "second"])
        self.assertFalse(self.store._path.with_suffix(".corrupt.json").exists())
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["first", "second"])
        self.assertNotIn("recovered_from", payload)
        self.assertNotEqual(payload.get("updated_at"), "not-a-timestamp")

    def test_valid_metadata_is_canonicalized_when_rewritten(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": " 2026-03-20T12:00:00+00:00 ",
                    "recovered_from": " BACKUP ",
                    "item_ids": ["first", "second"],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first", "second"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["first", "second"])
        self.assertNotIn("recovered_from", payload)
        self.assertEqual(payload.get("updated_at"), payload.get("updated_at").strip())
        self.assertNotEqual(payload.get("updated_at"), " 2026-03-20T12:00:00+00:00 ")

    def test_valid_recovered_from_is_dropped_when_primary_is_healthy_and_rewrite_is_needed(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": " 2026-03-20T12:00:00+00:00 ",
                    "recovered_from": " BACKUP ",
                    "item_ids": ["first", "second"],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first", "second"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["first", "second"])
        self.assertNotIn("recovered_from", payload)
        self.assertEqual(payload.get("updated_at"), payload.get("updated_at").strip())
        self.assertNotEqual(payload.get("updated_at"), " 2026-03-20T12:00:00+00:00 ")

    def test_invalid_updated_at_only_is_salvaged_and_rewritten(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "not-a-timestamp",
                    "item_ids": ["first", "second"],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first", "second"])
        self.assertFalse(self.store._path.with_suffix(".corrupt.json").exists())
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["first", "second"])
        self.assertNotEqual(payload.get("updated_at"), "not-a-timestamp")

    def test_invalid_recovered_from_only_is_salvaged_and_rewritten(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "recovered_from": "manual",
                    "item_ids": ["first", "second"],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first", "second"])
        self.assertFalse(self.store._path.with_suffix(".corrupt.json").exists())
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["first", "second"])
        self.assertNotIn("recovered_from", payload)

    def test_backup_with_invalid_metadata_is_salvaged_and_promoted(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text("{bad", encoding="utf-8")
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "not-a-timestamp",
                    "recovered_from": "manual",
                    "item_ids": ["first", "second"],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first", "second"])
        self.assertFalse(self.store._path.with_suffix(".corrupt.json").exists())
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["first", "second"])
        self.assertNotIn("recovered_from", payload)
        self.assertNotEqual(payload.get("updated_at"), "not-a-timestamp")

    def test_primary_load_refreshes_malformed_backup_without_rewriting_primary(self) -> None:
        self.store.save(ContextBasket(item_ids=["first"]))
        primary_payload_before = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "not-a-timestamp",
                    "recovered_from": "manual",
                    "item_ids": [" first "],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first"])
        primary_payload_after = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload_after.get("updated_at"), primary_payload_before.get("updated_at"))
        self.assertEqual(primary_payload_after.get("item_ids"), ["first"])
        self.assertEqual(backup_payload.get("item_ids"), ["first"])
        self.assertEqual(backup_payload.get("schema_version"), 1)
        self.assertEqual(backup_payload.get("updated_at"), primary_payload_after.get("updated_at"))
        self.assertNotEqual(backup_payload.get("updated_at"), "not-a-timestamp")
        self.assertNotIn("recovered_from", backup_payload)

    def test_primary_load_refreshes_stale_backup_updated_at_without_rewriting_primary(self) -> None:
        self.store.save(ContextBasket(item_ids=["first"]))
        primary_payload_before = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "item_ids": ["first"],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first"])
        primary_payload_after = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload_after.get("updated_at"), primary_payload_before.get("updated_at"))
        self.assertEqual(primary_payload_after.get("item_ids"), ["first"])
        self.assertEqual(backup_payload.get("item_ids"), ["first"])
        self.assertEqual(backup_payload.get("schema_version"), 1)
        self.assertEqual(backup_payload.get("updated_at"), primary_payload_after.get("updated_at"))
        self.assertNotEqual(backup_payload.get("updated_at"), "2026-03-20T12:00:00+00:00")

    def test_primary_load_refreshes_duplicate_backup_item_ids_without_rewriting_primary(self) -> None:
        self.store.save(ContextBasket(item_ids=["first"]))
        primary_payload_before = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "item_ids": ["first", " first ", "first"],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first"])
        primary_payload_after = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload_after.get("updated_at"), primary_payload_before.get("updated_at"))
        self.assertEqual(primary_payload_after.get("item_ids"), ["first"])
        self.assertEqual(backup_payload.get("item_ids"), ["first"])
        self.assertEqual(backup_payload.get("schema_version"), 1)
        self.assertEqual(backup_payload.get("updated_at"), primary_payload_after.get("updated_at"))
        self.assertNotIn("recovered_from", backup_payload)

    def test_primary_load_refreshes_invalid_backup_item_ids_without_rewriting_primary(self) -> None:
        self.store.save(ContextBasket(item_ids=["first"]))
        primary_payload_before = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "item_ids": ["first", None],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first"])
        primary_payload_after = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload_after.get("updated_at"), primary_payload_before.get("updated_at"))
        self.assertEqual(primary_payload_after.get("item_ids"), ["first"])
        self.assertEqual(backup_payload.get("item_ids"), ["first"])
        self.assertEqual(backup_payload.get("schema_version"), 1)
        self.assertEqual(backup_payload.get("updated_at"), primary_payload_after.get("updated_at"))
        self.assertNotIn("recovered_from", backup_payload)

    def test_refresh_backup_failure_preserves_seed_fallback(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        with (
            patch.object(ContextBasketStore, "_write_backup", return_value=None),
            patch.object(ContextBasketStore, "_write_backup_payload", return_value=False),
        ):
            self.store.save(ContextBasket(item_ids=["first"]), refresh_backup=True)

        self.assertTrue(self.store._path.exists())
        self.assertFalse(self.store._backup_path.exists())
        self.assertTrue(self.store._seed_state_path().exists())
        payload = json.loads(self.store._seed_state_path().read_text(encoding="utf-8"))
        self.assertEqual(payload.get("schema_version"), 1)
        self.assertEqual(payload.get("item_ids"), ["first"])
        self.assertNotIn("recovered_from", payload)

    def test_save_preserves_seed_when_backup_refresh_fails_before_primary_rewrite(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "item_ids": ["stale"],
                }
            ),
            encoding="utf-8",
        )

        with patch.object(ContextBasketStore, "_write_backup", return_value=False):
            self.store.save(ContextBasket(item_ids=["current"]))

        self.assertTrue(self.store._seed_state_path().exists())
        seed_payload = json.loads(self.store._seed_state_path().read_text(encoding="utf-8"))
        self.assertEqual(seed_payload.get("schema_version"), 1)
        self.assertEqual(seed_payload.get("item_ids"), ["current"])
        self.assertNotIn("recovered_from", seed_payload)

    def test_refresh_backup_failure_seed_fallback_omits_recovered_from(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "item_ids": ["first"],
                }
            ),
            encoding="utf-8",
        )
        self.store._path.unlink(missing_ok=True)

        with patch.object(ContextBasketStore, "_write_backup_payload", return_value=False):
            loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first"])
        payload = json.loads(self.store._seed_state_path().read_text(encoding="utf-8"))
        self.assertEqual(payload.get("schema_version"), 1)
        self.assertEqual(payload.get("item_ids"), ["first"])
        self.assertNotIn("recovered_from", payload)

    def test_healthy_primary_load_clears_stale_corrupt_marker(self) -> None:
        self.store.save(ContextBasket(item_ids=["first"]))
        self.store._path.with_suffix(".corrupt.json").write_text("{bad", encoding="utf-8")

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first"])
        self.assertFalse(self.store._path.with_suffix(".corrupt.json").exists())
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["first"])

    def test_healthy_primary_load_clears_stale_backup_and_seed_corrupt_markers(self) -> None:
        self.store.save(ContextBasket(item_ids=["first"]))
        self.store._backup_path.with_name("context_basket.bak.corrupt.json").write_text(
            "{bad",
            encoding="utf-8",
        )
        self.store._seed_state_path().with_name("context_basket.seed.corrupt.json").write_text(
            "{bad",
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first"])
        self.assertFalse(self.store._backup_path.with_name("context_basket.bak.corrupt.json").exists())
        self.assertFalse(self.store._seed_state_path().with_name("context_basket.seed.corrupt.json").exists())

    def test_healthy_primary_load_clears_stale_seed_file(self) -> None:
        self.store.save(ContextBasket(item_ids=["first"]))
        self.store._seed_state_path().write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "item_ids": ["stale"],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first"])
        self.assertFalse(self.store._seed_state_path().exists())

    def test_healthy_primary_load_clears_stale_temporary_corrupt_markers(self) -> None:
        self.store.save(ContextBasket(item_ids=["first"]))
        self.store._tmp_path().with_name("context_basket.tmp.corrupt.json").write_text(
            "{bad",
            encoding="utf-8",
        )
        self.store._backup_tmp_path().with_name("context_basket.bak.tmp.corrupt.json").write_text(
            "{bad",
            encoding="utf-8",
        )
        self.store._seed_tmp_path().with_name("context_basket.seed.tmp.corrupt.json").write_text(
            "{bad",
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first"])
        self.assertFalse(self.store._tmp_path().with_name("context_basket.tmp.corrupt.json").exists())
        self.assertFalse(self.store._backup_tmp_path().with_name("context_basket.bak.tmp.corrupt.json").exists())
        self.assertFalse(self.store._seed_tmp_path().with_name("context_basket.seed.tmp.corrupt.json").exists())

    def test_empty_load_clears_orphaned_quarantine_markers(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.with_suffix(".corrupt.json").write_text("{bad", encoding="utf-8")
        self.store._backup_path.with_name("context_basket.bak.corrupt.json").write_text(
            "{bad",
            encoding="utf-8",
        )
        self.store._seed_state_path().with_name("context_basket.seed.corrupt.json").write_text(
            "{bad",
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, [])
        self.assertFalse(self.store._path.with_suffix(".corrupt.json").exists())
        self.assertFalse(self.store._backup_path.with_name("context_basket.bak.corrupt.json").exists())
        self.assertFalse(self.store._seed_state_path().with_name("context_basket.seed.corrupt.json").exists())

    def test_backup_with_invalid_metadata_is_salvaged_and_promoted(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "not-a-timestamp",
                    "recovered_from": "manual",
                    "item_ids": ["first", "second"],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first", "second"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["first", "second"])
        self.assertEqual(payload.get("recovered_from"), "backup")
        self.assertNotEqual(payload.get("updated_at"), "not-a-timestamp")

    def test_missing_primary_recovery_resyncs_backup_to_canonical_state(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "not-a-timestamp",
                    "recovered_from": "manual",
                    "item_ids": ["first", "second"],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first", "second"])
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("item_ids"), ["first", "second"])
        self.assertEqual(primary_payload.get("recovered_from"), "backup")
        self.assertEqual(backup_payload.get("item_ids"), ["first", "second"])
        self.assertNotEqual(backup_payload.get("updated_at"), "not-a-timestamp")
        self.assertEqual(backup_payload.get("schema_version"), 1)


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
        (state.root_dir / ".vault_state.bak.corrupt.json").write_text("{}", encoding="utf-8")

        self.svc.clear_state(state)

        self.assertTrue(state.is_locked)
        self.assertFalse((state.root_dir / ".vault_state.json").exists())
        self.assertFalse((state.root_dir / ".vault_state.bak.json").exists())
        self.assertFalse((state.root_dir / ".vault_state.corrupt.json").exists())
        self.assertFalse((state.root_dir / ".vault_state.bak.corrupt.json").exists())

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

    def test_corrupt_primary_recovery_from_backup_records_recovery_source(self) -> None:
        state = self.svc.create_or_open(self.root, "p2-provenance")
        self.svc.lock(state)
        self.svc.unlock(state)  # Backup now exists.
        state_path = state.root_dir / ".vault_state.json"
        state_path.write_text("{bad", encoding="utf-8")

        reopened = self.svc.create_or_open(self.root, "p2-provenance")

        self.assertIsInstance(reopened.is_locked, bool)
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p2-provenance")
        self.assertEqual(payload.get("recovered_from"), "backup")

    def test_valid_primary_wins_over_stale_tmp_payload(self) -> None:
        state = self.svc.create_or_open(self.root, "p2-tmp")
        state_path = state.root_dir / ".vault_state.json"
        tmp_path = state.root_dir / ".vault_state.tmp"
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "p2-tmp",
                    "is_locked": False,
                }
            ),
            encoding="utf-8",
        )
        tmp_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "p2-tmp",
                    "is_locked": True,
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p2-tmp")

        self.assertFalse(reopened.is_locked)
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertFalse(payload.get("is_locked"))
        self.assertFalse(tmp_path.exists())

    def test_healthy_primary_load_clears_stale_temporary_corrupt_markers(self) -> None:
        state = self.svc.create_or_open(self.root, "p2-clean")
        state.root_dir.joinpath(".vault_state.tmp.corrupt.json").write_text("{bad", encoding="utf-8")
        state.root_dir.joinpath(".vault_state.bak.tmp.corrupt.json").write_text("{bad", encoding="utf-8")

        reopened = self.svc.create_or_open(self.root, "p2-clean")

        self.assertIsInstance(reopened.is_locked, bool)
        self.assertFalse((state.root_dir / ".vault_state.tmp.corrupt.json").exists())
        self.assertFalse((state.root_dir / ".vault_state.bak.tmp.corrupt.json").exists())

    def test_project_name_mismatch_forces_locked_state(self) -> None:
        state = self.svc.create_or_open(self.root, "p3")
        state_path = state.root_dir / ".vault_state.json"
        state_path.write_text(
            json.dumps({"schema_version": 1, "project_name": "other", "is_locked": False}),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p3")

        self.assertTrue(reopened.is_locked)

    def test_invalid_project_name_metadata_forces_locked_state_and_rewrites(self) -> None:
        state = self.svc.create_or_open(self.root, "p3-invalid")
        state_path = state.root_dir / ".vault_state.json"
        state_path.write_text(
            json.dumps({"schema_version": 1, "project_name": "../bad", "is_locked": False}),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p3-invalid")

        self.assertTrue(reopened.is_locked)
        self.assertFalse((state.root_dir / ".vault_state.corrupt.json").exists())
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p3-invalid")
        self.assertTrue(payload.get("is_locked"))

    def test_missing_is_locked_metadata_forces_locked_state_and_rewrites(self) -> None:
        state = self.svc.create_or_open(self.root, "p3-missing-lock")
        state_path = state.root_dir / ".vault_state.json"
        state_path.write_text(
            json.dumps({"schema_version": 1, "project_name": "p3-missing-lock"}),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p3-missing-lock")

        self.assertTrue(reopened.is_locked)
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p3-missing-lock")
        self.assertTrue(payload.get("is_locked"))

    def test_explicit_legacy_schema_version_zero_is_salvaged_and_rewritten(self) -> None:
        state = self.svc.create_or_open(self.root, "p3-legacy")
        state_path = state.root_dir / ".vault_state.json"
        state_path.write_text(
            json.dumps({"schema_version": 0, "project_name": "p3-legacy", "is_locked": 0}),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p3-legacy")

        self.assertFalse(reopened.is_locked)
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("schema_version"), 1)
        self.assertEqual(payload.get("project_name"), "p3-legacy")
        self.assertFalse(payload.get("is_locked"))

    def test_invalid_metadata_is_salvaged_and_rewritten(self) -> None:
        state = self.svc.create_or_open(self.root, "p4")
        state_path = state.root_dir / ".vault_state.json"
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "p4",
                    "is_locked": False,
                    "updated_at": "not-a-timestamp",
                    "recovered_from": "manual",
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p4")

        self.assertFalse(reopened.is_locked)
        self.assertFalse((state.root_dir / ".vault_state.corrupt.json").exists())
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p4")
        self.assertFalse(payload.get("is_locked"))
        self.assertNotIn("recovered_from", payload)
        self.assertNotEqual(payload.get("updated_at"), "not-a-timestamp")

    def test_valid_metadata_is_canonicalized_when_rewritten(self) -> None:
        state = self.svc.create_or_open(self.root, "p4-canonical")
        state_path = state.root_dir / ".vault_state.json"
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": " p4-canonical ",
                    "is_locked": "false",
                    "updated_at": " 2026-03-20T12:00:00+00:00 ",
                    "recovered_from": " BACKUP ",
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p4-canonical")

        self.assertFalse(reopened.is_locked)
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p4-canonical")
        self.assertIs(payload.get("is_locked"), False)
        self.assertNotIn("recovered_from", payload)
        self.assertEqual(payload.get("updated_at"), payload.get("updated_at").strip())
        self.assertNotEqual(payload.get("updated_at"), " 2026-03-20T12:00:00+00:00 ")

    def test_valid_recovered_from_is_dropped_when_primary_is_healthy_and_rewrite_is_needed(self) -> None:
        state = self.svc.create_or_open(self.root, "p4-canonical-drop")
        state_path = state.root_dir / ".vault_state.json"
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": " p4-canonical-drop ",
                    "is_locked": "false",
                    "updated_at": " 2026-03-20T12:00:00+00:00 ",
                    "recovered_from": " BACKUP ",
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p4-canonical-drop")

        self.assertFalse(reopened.is_locked)
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p4-canonical-drop")
        self.assertIs(payload.get("is_locked"), False)
        self.assertNotIn("recovered_from", payload)
        self.assertEqual(payload.get("updated_at"), payload.get("updated_at").strip())
        self.assertNotEqual(payload.get("updated_at"), " 2026-03-20T12:00:00+00:00 ")

    def test_invalid_updated_at_only_is_salvaged_and_rewritten(self) -> None:
        state = self.svc.create_or_open(self.root, "p5")
        state_path = state.root_dir / ".vault_state.json"
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "p5",
                    "is_locked": False,
                    "updated_at": "not-a-timestamp",
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p5")

        self.assertFalse(reopened.is_locked)
        self.assertFalse((state.root_dir / ".vault_state.corrupt.json").exists())
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p5")
        self.assertFalse(payload.get("is_locked"))
        self.assertNotEqual(payload.get("updated_at"), "not-a-timestamp")

    def test_invalid_recovered_from_only_is_salvaged_and_rewritten(self) -> None:
        state = self.svc.create_or_open(self.root, "p6")
        state_path = state.root_dir / ".vault_state.json"
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "p6",
                    "is_locked": False,
                    "recovered_from": "manual",
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p6")

        self.assertFalse(reopened.is_locked)
        self.assertFalse((state.root_dir / ".vault_state.corrupt.json").exists())
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p6")
        self.assertFalse(payload.get("is_locked"))
        self.assertNotIn("recovered_from", payload)

    def test_backup_with_invalid_metadata_is_salvaged_and_promoted(self) -> None:
        state = self.svc.create_or_open(self.root, "p7")
        state_path = state.root_dir / ".vault_state.json"
        backup_path = state.root_dir / ".vault_state.bak.json"
        state_path.write_text("{bad", encoding="utf-8")
        backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "p7",
                    "is_locked": False,
                    "updated_at": "not-a-timestamp",
                    "recovered_from": "manual",
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p7")

        self.assertFalse(reopened.is_locked)
        self.assertFalse((state.root_dir / ".vault_state.corrupt.json").exists())
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p7")
        self.assertFalse(payload.get("is_locked"))
        self.assertEqual(payload.get("recovered_from"), "backup")
        self.assertNotEqual(payload.get("updated_at"), "not-a-timestamp")

    def test_backup_write_failure_preserves_seed_fallback(self) -> None:
        with patch.object(VaultService, "_write_backup_payload", return_value=False):
            state = self.svc.create_or_open(self.root, "p8")

        state_path = state.root_dir / ".vault_state.json"
        backup_path = state.root_dir / ".vault_state.bak.json"
        seed_path = state.root_dir / ".vault_state.seed.json"

        self.assertTrue(state_path.exists())
        self.assertFalse(backup_path.exists())
        self.assertTrue(seed_path.exists())
        payload = json.loads(seed_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p8")
        self.assertIs(payload.get("is_locked"), True)
        self.assertNotIn("recovered_from", payload)

        state_path.unlink()

        reopened = self.svc.create_or_open(self.root, "p8")

        self.assertIsInstance(reopened.is_locked, bool)
        primary_payload = json.loads(state_path.read_text(encoding="utf-8"))
        backup_payload = json.loads(backup_path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("project_name"), "p8")
        self.assertEqual(primary_payload.get("recovered_from"), "seed")
        self.assertEqual(backup_payload.get("project_name"), "p8")
        self.assertNotIn("recovered_from", backup_payload)
        self.assertFalse(seed_path.exists())

    def test_healthy_primary_load_clears_stale_seed_state(self) -> None:
        state = self.svc.create_or_open(self.root, "p8-clean")
        seed_path = state.root_dir / ".vault_state.seed.json"
        seed_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "p8-clean",
                    "is_locked": False,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p8-clean")

        self.assertIsInstance(reopened.is_locked, bool)
        self.assertFalse(seed_path.exists())

    def test_backup_with_invalid_metadata_is_salvaged_and_rewritten_after_primary_missing(self) -> None:
        state = self.svc.create_or_open(self.root, "p7")
        backup_path = state.root_dir / ".vault_state.bak.json"
        backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "p7",
                    "is_locked": False,
                    "updated_at": "not-a-timestamp",
                    "recovered_from": "manual",
                }
            ),
            encoding="utf-8",
        )
        (state.root_dir / ".vault_state.json").unlink()

        reopened = self.svc.create_or_open(self.root, "p7")

        self.assertFalse(reopened.is_locked)
        payload = json.loads((state.root_dir / ".vault_state.json").read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p7")
        self.assertFalse(payload.get("is_locked"))
        self.assertEqual(payload.get("recovered_from"), "backup")
        self.assertNotEqual(payload.get("updated_at"), "not-a-timestamp")


if __name__ == "__main__":
    unittest.main()
