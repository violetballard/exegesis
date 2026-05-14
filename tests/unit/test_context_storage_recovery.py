from __future__ import annotations

import math
import json
import tempfile
import time
import unittest
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.qual.context.basket import ContextBasket
from src.qual.context.store import ContextBasketStore
from src.qual.context.set_store import ContextSetStore
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

    def test_save_refreshes_backup_to_latest_primary(self) -> None:
        self.store.save(ContextBasket(item_ids=["first"]))
        self.store.save(ContextBasket(item_ids=["second"]))

        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))

        self.assertEqual(primary_payload.get("item_ids"), ["second"])
        self.assertEqual(backup_payload.get("item_ids"), ["second"])
        self.assertEqual(backup_payload.get("schema_version"), 1)

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

        self.assertTrue(self.store._backup_path.exists())
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("schema_version"), 1)
        self.assertEqual(payload.get("item_ids"), ["a"])
        self.assertEqual(backup_payload.get("schema_version"), 1)
        self.assertEqual(backup_payload.get("item_ids"), ["a"])

    def test_corrupt_primary_quarantines_and_recovers_from_backup(self) -> None:
        self.store.save(ContextBasket(item_ids=["first"]))
        self.store.save(ContextBasket(item_ids=["second"]))  # Creates backup with "first".
        self.store._path.write_text("{bad", encoding="utf-8")

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["second"])
        # Successful recovery rewrites primary and clears stale quarantine artifacts.
        self.assertFalse(self.store._path.with_suffix(".corrupt.json").exists())
        self.assertEqual(
            json.loads(self.store._path.read_text(encoding="utf-8")).get("item_ids"),
            ["second"],
        )

    def test_corrupt_primary_recovery_from_backup_records_recovery_source(self) -> None:
        self.store.save(ContextBasket(item_ids=["first"]))
        self.store.save(ContextBasket(item_ids=["second"]))  # Creates backup with "first".
        self.store._path.write_text("{bad", encoding="utf-8")

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["second"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["second"])
        self.assertEqual(payload.get("recovered_from"), "backup")

    def test_legacy_list_primary_prefers_its_own_items_over_stale_backup(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(json.dumps(["primary", "primary"]), encoding="utf-8")
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "item_ids": ["backup"],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["primary"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["primary"])
        self.assertNotIn("recovered_from", payload)
        self.assertEqual(backup_payload.get("item_ids"), ["primary"])

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

    def test_empty_tmp_payload_does_not_override_backup_recovery(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._tmp_path().write_text("[]", encoding="utf-8")
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "item_ids": ["backup"],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["backup"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["backup"])

    def test_legacy_empty_primary_list_recovers_from_backup_before_rewrite(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text("[]", encoding="utf-8")
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "item_ids": ["backup"],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["backup"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["backup"])
        self.assertEqual(payload.get("recovered_from"), "backup")

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
        self.assertFalse(self.store._path.with_suffix(".corrupt.json").exists())

    def test_legacy_list_payload_with_only_invalid_entries_is_preserved_for_audit(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps([None, "", {"bad": "value"}]),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, [])
        self.assertTrue(self.store._path.with_suffix(".corrupt.json").exists())
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(self.store._path.with_suffix(".corrupt.json").read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), [])
        self.assertEqual(payload.get("schema_version"), 1)
        self.assertEqual(quarantined_payload, [None, "", {"bad": "value"}])

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

    def test_recovered_from_only_cleanup_preserves_existing_updated_at(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        original_updated_at = "2026-03-20T12:00:00+00:00"
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": original_updated_at,
                    "recovered_from": "manual",
                    "item_ids": ["first", "second"],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first", "second"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["first", "second"])
        self.assertNotIn("recovered_from", payload)
        self.assertEqual(payload.get("updated_at"), original_updated_at)
        self.assertEqual(backup_payload.get("updated_at"), original_updated_at)

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

    def test_empty_basket_with_malformed_metadata_is_rewritten_without_leaving_corrupt_artifacts(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "recovered_from": "manual",
                    "item_ids": [],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, [])
        self.assertFalse(self.store._path.with_suffix(".corrupt.json").exists())
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), [])
        self.assertNotIn("recovered_from", payload)

    def test_empty_basket_with_unknown_metadata_preserves_audit_quarantine(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "item_ids": [],
                    "extra": "ignored",
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, [])
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(self.store._path.with_suffix(".corrupt.json").read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("item_ids"), [])
        self.assertEqual(primary_payload.get("schema_version"), 1)
        self.assertTrue(self.store._path.with_suffix(".corrupt.json").exists())
        self.assertEqual(quarantined_payload.get("extra"), "ignored")

    def test_empty_basket_primary_with_unknown_metadata_prefers_recovery_payload(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "item_ids": [],
                    "extra": "ignored",
                }
            ),
            encoding="utf-8",
        )
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
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(self.store._path.with_suffix(".corrupt.json").read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("item_ids"), ["first"])
        self.assertEqual(primary_payload.get("recovered_from"), "backup")
        self.assertEqual(backup_payload.get("item_ids"), ["first"])
        self.assertNotIn("recovered_from", backup_payload)
        self.assertTrue(self.store._path.with_suffix(".corrupt.json").exists())
        self.assertEqual(quarantined_payload.get("item_ids"), [])
        self.assertEqual(quarantined_payload.get("extra"), "ignored")

    def test_empty_recovery_payload_does_not_claim_recovery_provenance(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "recovered_from": "manual",
                    "item_ids": [],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, [])
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("item_ids"), [])
        self.assertNotIn("recovered_from", primary_payload)
        self.assertEqual(backup_payload.get("item_ids"), [])
        self.assertNotIn("recovered_from", backup_payload)

    def test_empty_legacy_seed_payload_is_promoted_without_stale_quarantine(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text("1", encoding="utf-8")
        self.store._seed_state_path().write_text("[]", encoding="utf-8")

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, [])
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        first_updated_at = primary_payload.get("updated_at")
        self.assertEqual(primary_payload.get("item_ids"), [])
        self.assertFalse(self.store._seed_state_path().with_name("context_basket.seed.corrupt.json").exists())

        time.sleep(0.01)
        loaded_again = self.store.load()

        self.assertEqual(loaded_again.item_ids, [])
        second_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(second_payload.get("updated_at"), first_updated_at)
        self.assertFalse(self.store._seed_state_path().with_name("context_basket.seed.corrupt.json").exists())

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

    def test_backup_legacy_list_with_only_invalid_entries_is_preserved_for_audit(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store.save(ContextBasket(item_ids=["primary"]))
        corrupt_path = self.store._backup_path.with_suffix(".corrupt.json")
        self.store._backup_path.write_text(
            json.dumps([None, "", {"bad": "value"}]),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["primary"])
        self.assertTrue(corrupt_path.exists())
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(corrupt_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["primary"])
        self.assertEqual(backup_payload.get("item_ids"), ["primary"])
        self.assertEqual(quarantined_payload, [None, "", {"bad": "value"}])

    def test_backup_legacy_list_with_dropped_item_ids_is_preserved_for_audit(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store.save(ContextBasket(item_ids=["primary"]))
        corrupt_path = self.store._backup_path.with_suffix(".corrupt.json")
        self.store._path.write_text("{bad", encoding="utf-8")
        self.store._backup_path.write_text(
            json.dumps([" keep ", None, "second", "keep"]),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["keep", "second"])
        self.assertTrue(corrupt_path.exists())
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(corrupt_path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("item_ids"), ["keep", "second"])
        self.assertEqual(backup_payload.get("item_ids"), ["keep", "second"])
        self.assertEqual(quarantined_payload, [" keep ", None, "second", "keep"])

    def test_backup_with_malformed_optional_metadata_is_rewritten_canonically(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text("{bad", encoding="utf-8")
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": " 2026-03-20T12:00:00+00:00 ",
                    "recovered_from": " BACKUP ",
                    "item_ids": [" first ", "second", "first"],
                    "extra": "ignored",
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
        self.assertEqual(primary_payload.get("schema_version"), 1)
        self.assertEqual(primary_payload.get("updated_at"), primary_payload.get("updated_at").strip())
        self.assertNotEqual(primary_payload.get("updated_at"), " 2026-03-20T12:00:00+00:00 ")
        self.assertNotIn("extra", primary_payload)
        self.assertEqual(backup_payload.get("item_ids"), ["first", "second"])
        self.assertEqual(backup_payload.get("schema_version"), 1)
        self.assertEqual(backup_payload.get("updated_at"), primary_payload.get("updated_at"))
        self.assertNotIn("recovered_from", backup_payload)
        self.assertNotIn("extra", backup_payload)

    def test_primary_missing_item_ids_recovers_from_backup_before_empty_rewrite(self) -> None:
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
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "item_ids": [" first ", "second", "first"],
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
        self.assertEqual(primary_payload.get("schema_version"), 1)
        self.assertEqual(backup_payload.get("item_ids"), ["first", "second"])
        self.assertEqual(backup_payload.get("schema_version"), 1)
        self.assertNotIn("recovered_from", backup_payload)

    def test_primary_missing_item_ids_quarantines_before_empty_rewrite_when_no_backup_exists(self) -> None:
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

        with patch.object(
            ContextBasketStore,
            "_quarantine_invalid_file",
            wraps=self.store._quarantine_invalid_file,
        ) as quarantine:
            loaded = self.store.load()

        self.assertEqual(loaded.item_ids, [])
        quarantine.assert_called_once()
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), [])
        self.assertEqual(payload.get("schema_version"), 1)
        self.assertTrue(self.store._path.with_suffix(".corrupt.json").exists())
        quarantined_payload = json.loads(self.store._path.with_suffix(".corrupt.json").read_text(encoding="utf-8"))
        self.assertNotIn("item_ids", quarantined_payload)

    def test_backup_missing_item_ids_does_not_claim_recovery_provenance(self) -> None:
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
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "recovered_from": "manual",
                    "extra": "ignored",
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, [])
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("item_ids"), [])
        self.assertNotIn("recovered_from", primary_payload)
        self.assertEqual(backup_payload.get("item_ids"), [])
        self.assertNotIn("recovered_from", backup_payload)

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

    def test_primary_load_refreshes_stale_backup_without_rereading_primary(self) -> None:
        self.store.save(ContextBasket(item_ids=["first"]))
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "recovered_from": "manual",
                    "item_ids": ["first"],
                }
            ),
            encoding="utf-8",
        )

        with (
            patch.object(ContextBasketStore, "_write_backup", wraps=self.store._write_backup) as write_backup,
            patch.object(
                ContextBasketStore,
                "_write_backup_payload",
                wraps=self.store._write_backup_payload,
            ) as write_backup_payload,
        ):
            loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first"])
        write_backup.assert_not_called()
        self.assertEqual(write_backup_payload.call_count, 1)
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(backup_payload.get("item_ids"), ["first"])
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

    def test_save_skips_canonical_backup_rewrite_without_forced_refresh(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        fixed_now = datetime(2026, 3, 20, 12, 0, 0, tzinfo=UTC)
        payload = {
            "schema_version": 1,
            "updated_at": fixed_now.isoformat(),
            "item_ids": ["first"],
        }
        self.store._path.write_text(json.dumps(payload), encoding="utf-8")
        self.store._backup_path.write_text(json.dumps(payload), encoding="utf-8")

        with (
            patch(
                "src.qual.context.store.datetime",
                new=SimpleNamespace(now=lambda tz=None: fixed_now, fromisoformat=datetime.fromisoformat),
            ),
            patch.object(ContextBasketStore, "_write_backup_payload", wraps=self.store._write_backup_payload) as write_backup,
        ):
            self.store.save(ContextBasket(item_ids=["first"]))

        self.assertEqual(write_backup.call_count, 0)
        self.assertEqual(json.loads(self.store._backup_path.read_text(encoding="utf-8")), payload)

    def test_save_preserves_seed_when_backup_refresh_fails_after_primary_rewrite(self) -> None:
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

        with patch.object(ContextBasketStore, "_write_backup_payload", return_value=False):
            self.store.save(ContextBasket(item_ids=["current"]))

        self.assertTrue(self.store._seed_state_path().exists())
        seed_payload = json.loads(self.store._seed_state_path().read_text(encoding="utf-8"))
        self.assertEqual(seed_payload.get("schema_version"), 1)
        self.assertEqual(seed_payload.get("item_ids"), ["current"])
        self.assertNotIn("recovered_from", seed_payload)
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(backup_payload.get("item_ids"), ["stale"])

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

    def test_corrupt_temporary_backup_payload_is_preserved_for_audit(self) -> None:
        self.store.save(ContextBasket(item_ids=["first"]))
        self.store._backup_tmp_path().write_text("{bad", encoding="utf-8")

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["first"])
        self.assertFalse(self.store._backup_tmp_path().exists())
        self.assertTrue(
            self.store._backup_tmp_path().with_name("context_basket.bak.tmp.corrupt.json").exists()
        )

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

    def test_backup_legacy_list_with_only_invalid_entries_is_preserved_for_audit(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store.save(ContextBasket(item_ids=["primary"]))
        corrupt_path = self.store._backup_path.with_suffix(".corrupt.json")
        self.store._backup_path.write_text(
            json.dumps([None, "", {"context_set_id": "", "name": "drop me"}]),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["primary"])
        self.assertTrue(corrupt_path.exists())
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(corrupt_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["primary"])
        self.assertEqual(backup_payload.get("item_ids"), ["primary"])
        self.assertEqual(
            quarantined_payload,
            [None, "", {"context_set_id": "", "name": "drop me"}],
        )

    def test_seed_legacy_list_with_dropped_item_ids_is_preserved_for_audit(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text("{bad", encoding="utf-8")
        self.store._seed_state_path().write_text(
            json.dumps(
                [" keep ", None, "second", "keep"]
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["keep", "second"])
        corrupt_path = self.store._seed_state_path().with_suffix(".corrupt.json")
        self.assertTrue(corrupt_path.exists())
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(corrupt_path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("item_ids"), ["keep", "second"])
        self.assertEqual(quarantined_payload, [" keep ", None, "second", "keep"])

    def test_seed_with_invalid_metadata_is_salvaged_and_rewritten(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._seed_state_path().write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "not-a-timestamp",
                    "recovered_from": "manual",
                    "item_ids": [" keep ", None, "second"],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded.item_ids, ["keep", "second"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("item_ids"), ["keep", "second"])
        self.assertEqual(payload.get("recovered_from"), "seed")
        self.assertNotEqual(payload.get("updated_at"), "not-a-timestamp")
        self.assertEqual(backup_payload.get("item_ids"), ["keep", "second"])
        self.assertNotIn("recovered_from", backup_payload)
        self.assertFalse(self.store._seed_state_path().exists())

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


class ContextSetStoreRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.store = ContextSetStore(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_create_context_set_normalizes_and_persists_item_ids(self) -> None:
        record = self.store.create_context_set("  Evidence  ", [" keep ", 7, None, "7", 2.5, 2.5])

        self.assertEqual(record.name, "Evidence")
        self.assertEqual(record.item_ids, ["keep", "7", "2.5"])
        loaded = self.store.load()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, record.context_set_id)
        self.assertEqual(loaded[0].name, "Evidence")
        self.assertEqual(loaded[0].item_ids, ["keep", "7", "2.5"])

    def test_pin_item_updates_existing_set_and_rewrites_canonical_state(self) -> None:
        record = self.store.create_context_set("Evidence", ["first"])

        updated = self.store.pin_item(record.context_set_id, " second ")

        self.assertEqual(updated.context_set_id, record.context_set_id)
        self.assertEqual(updated.item_ids, ["first", "second"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("context_sets")[0]["item_ids"], ["first", "second"])
        self.assertEqual(payload.get("schema_version"), 1)

    def test_corrupt_primary_recovers_from_backup_and_records_recovery_source(self) -> None:
        self.store._path.write_text("{bad", encoding="utf-8")
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "context_sets": [
                        {
                            "context_set_id": " set-1 ",
                            "name": " Evidence ",
                            "item_ids": [" first ", None, "second", "first"],
                            "created_at": "2026-03-20T11:00:00+00:00",
                            "updated_at": "2026-03-20T12:00:00+00:00",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "set-1")
        self.assertEqual(loaded[0].name, "Evidence")
        self.assertEqual(loaded[0].item_ids, ["first", "second"])
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("recovered_from"), "backup")
        self.assertEqual(primary_payload.get("context_sets")[0]["item_ids"], ["first", "second"])
        self.assertEqual(backup_payload.get("context_sets")[0]["item_ids"], ["first", "second"])
        self.assertNotIn("recovered_from", backup_payload)

    def test_malformed_context_set_entries_are_salvaged_and_rewritten(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "not-a-timestamp",
                    "context_sets": [
                        {
                            "context_set_id": " set-1 ",
                            "name": " Evidence ",
                            "item_ids": [" keep ", "", None, "keep", 7],
                            "created_at": "2026-03-20T11:00:00+00:00",
                            "updated_at": "2026-03-20T12:00:00+00:00",
                        },
                        {"context_set_id": "", "name": "drop me", "item_ids": ["x"]},
                        "discard",
                    ],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "set-1")
        self.assertEqual(loaded[0].name, "Evidence")
        self.assertEqual(loaded[0].item_ids, ["keep", "7"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("schema_version"), 1)
        self.assertEqual(payload.get("context_sets")[0]["item_ids"], ["keep", "7"])
        self.assertEqual(payload.get("context_sets")[0]["name"], "Evidence")

    def test_scalar_context_set_metadata_is_salvaged_and_rewritten(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "context_sets": [
                        {
                            "context_set_id": 123,
                            "name": 456,
                            "item_ids": [1, " keep ", False, 1.5],
                            "created_at": "2026-03-20T11:00:00+00:00",
                            "updated_at": "2026-03-20T12:00:00+00:00",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "123")
        self.assertEqual(loaded[0].name, "456")
        self.assertEqual(loaded[0].item_ids, ["1", "keep", "1.5"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("context_sets")[0]["context_set_id"], "123")
        self.assertEqual(payload.get("context_sets")[0]["name"], "456")
        self.assertEqual(payload.get("context_sets")[0]["item_ids"], ["1", "keep", "1.5"])

    def test_context_set_entries_with_extra_metadata_are_rewritten_canonically(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "context_sets": [
                        {
                            "context_set_id": " set-1 ",
                            "name": " Evidence ",
                            "item_ids": [" first ", "first", "second"],
                            "created_at": " 2026-03-20T11:00:00+00:00 ",
                            "updated_at": " 2026-03-20T12:00:00+00:00 ",
                            "extra": "ignored",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "set-1")
        self.assertEqual(loaded[0].name, "Evidence")
        self.assertEqual(loaded[0].item_ids, ["first", "second"])
        self.assertEqual(loaded[0].created_at, "2026-03-20T11:00:00+00:00")
        self.assertEqual(loaded[0].updated_at, "2026-03-20T12:00:00+00:00")
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("schema_version"), 1)
        self.assertEqual(payload.get("context_sets")[0]["context_set_id"], "set-1")
        self.assertEqual(payload.get("context_sets")[0]["name"], "Evidence")
        self.assertEqual(payload.get("context_sets")[0]["item_ids"], ["first", "second"])
        self.assertEqual(payload.get("context_sets")[0]["created_at"], "2026-03-20T11:00:00+00:00")
        self.assertEqual(payload.get("context_sets")[0]["updated_at"], "2026-03-20T12:00:00+00:00")
        self.assertNotIn("extra", payload.get("context_sets")[0])

    def test_duplicate_context_set_entries_are_collapsed_and_rewritten(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "context_sets": [
                        {
                            "context_set_id": "set-1",
                            "name": "Evidence",
                            "item_ids": ["first"],
                            "created_at": "2026-03-20T11:00:00+00:00",
                            "updated_at": "2026-03-20T12:00:00+00:00",
                        },
                        {
                            "context_set_id": "set-1",
                            "name": "Evidence",
                            "item_ids": ["second"],
                            "created_at": "2026-03-20T11:05:00+00:00",
                            "updated_at": "2026-03-20T12:05:00+00:00",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "set-1")
        self.assertEqual(loaded[0].item_ids, ["first"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(len(payload.get("context_sets", [])), 1)
        self.assertEqual(payload.get("context_sets")[0]["item_ids"], ["first"])
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(len(backup_payload.get("context_sets", [])), 1)
        self.assertEqual(backup_payload.get("context_sets")[0]["item_ids"], ["first"])

    def test_legacy_list_payload_with_duplicate_context_set_ids_preserves_audit_quarantine(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                [
                    {
                        "context_set_id": "set-1",
                        "name": "Evidence",
                        "item_ids": ["first"],
                        "created_at": "2026-03-20T11:00:00+00:00",
                        "updated_at": "2026-03-20T12:00:00+00:00",
                    },
                    {
                        "context_set_id": "set-1",
                        "name": "Evidence",
                        "item_ids": ["second"],
                        "created_at": "2026-03-20T11:05:00+00:00",
                        "updated_at": "2026-03-20T12:05:00+00:00",
                    },
                ]
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "set-1")
        self.assertEqual(loaded[0].item_ids, ["first"])
        corrupt_path = self.store._path.with_suffix(".corrupt.json")
        self.assertTrue(corrupt_path.exists())
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(corrupt_path.read_text(encoding="utf-8"))
        self.assertEqual(len(payload.get("context_sets", [])), 1)
        self.assertEqual(payload.get("context_sets")[0]["item_ids"], ["first"])
        self.assertEqual(len(backup_payload.get("context_sets", [])), 1)
        self.assertEqual(backup_payload.get("context_sets")[0]["item_ids"], ["first"])
        self.assertEqual(len(quarantined_payload), 2)
        self.assertEqual(quarantined_payload[1]["item_ids"], ["second"])

    def test_backup_with_duplicate_context_set_ids_is_preserved_for_audit(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text("{bad", encoding="utf-8")
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:05:00+00:00",
                    "context_sets": [
                        {
                            "context_set_id": "set-backup",
                            "name": "Backup Evidence",
                            "item_ids": ["first"],
                            "created_at": "2026-03-20T11:00:00+00:00",
                            "updated_at": "2026-03-20T12:00:00+00:00",
                        },
                        {
                            "context_set_id": "set-backup",
                            "name": "Backup Evidence",
                            "item_ids": ["second"],
                            "created_at": "2026-03-20T11:05:00+00:00",
                            "updated_at": "2026-03-20T12:05:00+00:00",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "set-backup")
        self.assertEqual(loaded[0].item_ids, ["first"])
        corrupt_path = self.store._backup_path.with_suffix(".corrupt.json")
        self.assertTrue(corrupt_path.exists())
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(corrupt_path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("recovered_from"), "backup")
        self.assertEqual(len(primary_payload.get("context_sets", [])), 1)
        self.assertEqual(primary_payload.get("context_sets")[0]["item_ids"], ["first"])
        self.assertEqual(len(backup_payload.get("context_sets", [])), 1)
        self.assertEqual(backup_payload.get("context_sets")[0]["item_ids"], ["first"])
        self.assertEqual(len(quarantined_payload.get("context_sets", [])), 2)
        self.assertEqual(quarantined_payload.get("context_sets")[1]["item_ids"], ["second"])

    def test_empty_tmp_payload_does_not_override_backup_recovery(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._tmp_path().write_text("[]", encoding="utf-8")
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "context_sets": [
                        {
                            "context_set_id": "set-1",
                            "name": "Evidence",
                            "item_ids": ["backup"],
                            "created_at": "2026-03-20T11:00:00+00:00",
                            "updated_at": "2026-03-20T12:00:00+00:00",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "set-1")
        self.assertEqual(loaded[0].item_ids, ["backup"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("context_sets")[0]["item_ids"], ["backup"])

    def test_legacy_empty_primary_list_recovers_from_backup_before_rewrite(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text("[]", encoding="utf-8")
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "context_sets": [
                        {
                            "context_set_id": "set-1",
                            "name": "Evidence",
                            "item_ids": ["backup"],
                            "created_at": "2026-03-20T11:00:00+00:00",
                            "updated_at": "2026-03-20T12:00:00+00:00",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "set-1")
        self.assertEqual(loaded[0].item_ids, ["backup"])
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("recovered_from"), "backup")
        self.assertEqual(primary_payload.get("context_sets")[0]["item_ids"], ["backup"])

    def test_legacy_list_payload_salvages_valid_entries_without_leaving_quarantine(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                [
                    {
                        "context_set_id": " set-1 ",
                        "name": " Evidence ",
                        "item_ids": [" first ", None, "second", "first"],
                        "created_at": "2026-03-20T11:00:00+00:00",
                        "updated_at": "2026-03-20T12:00:00+00:00",
                    }
                ]
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "set-1")
        self.assertEqual(loaded[0].name, "Evidence")
        self.assertEqual(loaded[0].item_ids, ["first", "second"])
        self.assertFalse(self.store._path.with_suffix(".corrupt.json").exists())
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("context_sets")[0]["item_ids"], ["first", "second"])

    def test_legacy_list_payload_missing_timestamps_is_backfilled_and_rewritten(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                [
                    {
                        "context_set_id": " set-1 ",
                        "name": " Evidence ",
                        "item_ids": [" first ", "second"],
                    }
                ]
            ),
            encoding="utf-8",
        )
        fixed_now = datetime(2026, 3, 20, 12, 0, 0, tzinfo=UTC)

        with patch(
            "src.qual.context.set_store.datetime",
            new=SimpleNamespace(now=lambda tz=None: fixed_now, fromisoformat=datetime.fromisoformat),
        ):
            loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "set-1")
        self.assertEqual(loaded[0].name, "Evidence")
        self.assertEqual(loaded[0].created_at, fixed_now.isoformat())
        self.assertEqual(loaded[0].updated_at, fixed_now.isoformat())
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("context_sets")[0]["created_at"], fixed_now.isoformat())
        self.assertEqual(payload.get("context_sets")[0]["updated_at"], fixed_now.isoformat())

    def test_legacy_list_payload_with_dropped_records_preserves_audit_quarantine(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                [
                    {
                        "context_set_id": " set-1 ",
                        "name": " Evidence ",
                        "item_ids": [" first ", None, "second", "first"],
                        "created_at": "2026-03-20T11:00:00+00:00",
                        "updated_at": "2026-03-20T12:00:00+00:00",
                    },
                    {
                        "context_set_id": "",
                        "name": "drop me",
                    },
                ]
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "set-1")
        self.assertEqual(loaded[0].item_ids, ["first", "second"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(self.store._path.with_suffix(".corrupt.json").read_text(encoding="utf-8"))
        self.assertEqual(payload.get("context_sets")[0]["item_ids"], ["first", "second"])
        self.assertTrue(self.store._path.with_suffix(".corrupt.json").exists())
        self.assertEqual(len(quarantined_payload), 2)
        self.assertEqual(quarantined_payload[1]["name"], "drop me")

    def test_backup_legacy_list_with_dropped_records_is_preserved_for_audit(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text("{bad", encoding="utf-8")
        self.store._backup_path.write_text(
            json.dumps(
                [
                    {
                        "context_set_id": " set-backup ",
                        "name": " Backup Evidence ",
                        "item_ids": [" first ", None, "second", "first"],
                        "created_at": "2026-03-20T11:00:00+00:00",
                        "updated_at": "2026-03-20T12:00:00+00:00",
                    },
                    {"context_set_id": "", "name": "drop me"},
                ]
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "set-backup")
        self.assertEqual(loaded[0].item_ids, ["first", "second"])
        corrupt_path = self.store._backup_path.with_suffix(".corrupt.json")
        self.assertTrue(corrupt_path.exists())
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(corrupt_path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("context_sets")[0]["context_set_id"], "set-backup")
        self.assertEqual(primary_payload.get("context_sets")[0]["item_ids"], ["first", "second"])
        self.assertEqual(backup_payload.get("context_sets")[0]["context_set_id"], "set-backup")
        self.assertEqual(backup_payload.get("context_sets")[0]["item_ids"], ["first", "second"])
        self.assertEqual(len(quarantined_payload), 2)
        self.assertEqual(quarantined_payload[1]["name"], "drop me")

    def test_legacy_list_primary_prefers_its_own_records_over_stale_backup(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                [
                    {
                        "context_set_id": " set-primary ",
                        "name": " Primary Evidence ",
                        "item_ids": [" primary ", "primary"],
                        "created_at": "2026-03-20T11:00:00+00:00",
                        "updated_at": "2026-03-20T12:00:00+00:00",
                    }
                ]
            ),
            encoding="utf-8",
        )
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "context_sets": [
                        {
                            "context_set_id": "set-backup",
                            "name": "Backup Evidence",
                            "item_ids": ["backup"],
                            "created_at": "2026-03-20T11:30:00+00:00",
                            "updated_at": "2026-03-20T12:00:00+00:00",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "set-primary")
        self.assertEqual(loaded[0].name, "Primary Evidence")
        self.assertEqual(loaded[0].item_ids, ["primary"])
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("context_sets")[0]["context_set_id"], "set-primary")
        self.assertEqual(payload.get("context_sets")[0]["item_ids"], ["primary"])
        self.assertEqual(backup_payload.get("context_sets")[0]["context_set_id"], "set-primary")
        self.assertEqual(backup_payload.get("context_sets")[0]["item_ids"], ["primary"])

    def test_legacy_list_payload_with_only_invalid_entries_is_preserved_for_audit(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps([None, "", {"context_set_id": "", "name": "drop me"}]),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded, [])
        self.assertTrue(self.store._path.with_suffix(".corrupt.json").exists())
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(self.store._path.with_suffix(".corrupt.json").read_text(encoding="utf-8"))
        self.assertEqual(payload.get("context_sets"), [])
        self.assertEqual(payload.get("schema_version"), 1)
        self.assertEqual(quarantined_payload, [None, "", {"context_set_id": "", "name": "drop me"}])

    def test_primary_missing_context_sets_recovers_from_backup_before_empty_rewrite(self) -> None:
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
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "context_sets": [
                        {
                            "context_set_id": "set-1",
                            "name": "Evidence",
                            "item_ids": ["first", "second"],
                            "created_at": "2026-03-20T11:00:00+00:00",
                            "updated_at": "2026-03-20T12:00:00+00:00",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "set-1")
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(self.store._path.with_suffix(".corrupt.json").read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("context_sets")[0]["item_ids"], ["first", "second"])
        self.assertEqual(primary_payload.get("recovered_from"), "backup")
        self.assertEqual(backup_payload.get("context_sets")[0]["item_ids"], ["first", "second"])
        self.assertNotIn("recovered_from", backup_payload)
        self.assertTrue(self.store._path.with_suffix(".corrupt.json").exists())
        self.assertNotIn("context_sets", quarantined_payload)

    def test_primary_missing_context_sets_preserves_audit_quarantine_after_backup_recovery(self) -> None:
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
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "context_sets": [
                        {
                            "context_set_id": "set-1",
                            "name": "Evidence",
                            "item_ids": ["first", "second"],
                            "created_at": "2026-03-20T11:00:00+00:00",
                            "updated_at": "2026-03-20T12:00:00+00:00",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "set-1")
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(self.store._path.with_suffix(".corrupt.json").read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("context_sets")[0]["item_ids"], ["first", "second"])
        self.assertEqual(primary_payload.get("recovered_from"), "backup")
        self.assertTrue(self.store._path.with_suffix(".corrupt.json").exists())
        self.assertNotIn("context_sets", quarantined_payload)

    def test_primary_missing_context_sets_preserves_audit_quarantine(self) -> None:
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

        loaded = self.store.load()

        self.assertEqual(loaded, [])
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(self.store._path.with_suffix(".corrupt.json").read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("context_sets"), [])
        self.assertEqual(primary_payload.get("schema_version"), 1)
        self.assertTrue(self.store._path.with_suffix(".corrupt.json").exists())
        self.assertNotIn("context_sets", quarantined_payload)

    def test_backup_missing_context_sets_does_not_claim_recovery_provenance(self) -> None:
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
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "recovered_from": "manual",
                    "extra": "ignored",
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded, [])
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("context_sets"), [])
        self.assertNotIn("recovered_from", primary_payload)
        self.assertEqual(backup_payload.get("context_sets"), [])
        self.assertNotIn("recovered_from", backup_payload)

    def test_empty_context_sets_with_invalid_metadata_preserves_audit_quarantine(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "not-a-timestamp",
                    "recovered_from": "manual",
                    "context_sets": [],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded, [])
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(self.store._path.with_suffix(".corrupt.json").read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("context_sets"), [])
        self.assertEqual(primary_payload.get("schema_version"), 1)
        self.assertTrue(self.store._path.with_suffix(".corrupt.json").exists())
        self.assertEqual(quarantined_payload.get("context_sets"), [])
        self.assertEqual(quarantined_payload.get("updated_at"), "not-a-timestamp")

    def test_empty_context_sets_with_unknown_metadata_preserves_audit_quarantine(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "context_sets": [],
                    "extra": "ignored",
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded, [])
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(self.store._path.with_suffix(".corrupt.json").read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("context_sets"), [])
        self.assertEqual(primary_payload.get("schema_version"), 1)
        self.assertTrue(self.store._path.with_suffix(".corrupt.json").exists())
        self.assertEqual(quarantined_payload.get("extra"), "ignored")

    def test_empty_context_sets_primary_with_unknown_metadata_prefers_recovery_payload(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "context_sets": [],
                    "extra": "ignored",
                }
            ),
            encoding="utf-8",
        )
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "context_sets": [
                        {
                            "context_set_id": "set-1",
                            "name": "Evidence",
                            "item_ids": ["first"],
                            "created_at": "2026-03-20T11:00:00+00:00",
                            "updated_at": "2026-03-20T12:00:00+00:00",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, "set-1")
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(self.store._path.with_suffix(".corrupt.json").read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("context_sets")[0]["item_ids"], ["first"])
        self.assertEqual(primary_payload.get("recovered_from"), "backup")
        self.assertEqual(backup_payload.get("context_sets")[0]["item_ids"], ["first"])
        self.assertNotIn("recovered_from", backup_payload)
        self.assertTrue(self.store._path.with_suffix(".corrupt.json").exists())
        self.assertEqual(quarantined_payload.get("context_sets"), [])
        self.assertEqual(quarantined_payload.get("extra"), "ignored")

    def test_empty_recovery_payload_does_not_claim_recovery_provenance(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "recovered_from": "manual",
                    "context_sets": [],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(loaded, [])
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("context_sets"), [])
        self.assertNotIn("recovered_from", primary_payload)
        self.assertEqual(backup_payload.get("context_sets"), [])
        self.assertNotIn("recovered_from", backup_payload)

    def test_empty_legacy_seed_payload_is_promoted_without_rewrite_churn(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store._path.write_text("1", encoding="utf-8")
        self.store._seed_state_path().write_text("[]", encoding="utf-8")

        loaded = self.store.load()

        self.assertEqual(loaded, [])
        primary_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        first_updated_at = primary_payload.get("updated_at")
        self.assertEqual(primary_payload.get("context_sets"), [])
        self.assertFalse(self.store._seed_state_path().with_name("context_sets.seed.corrupt.json").exists())

        time.sleep(0.01)
        loaded_again = self.store.load()

        self.assertEqual(loaded_again, [])
        second_payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        self.assertEqual(second_payload.get("updated_at"), first_updated_at)
        self.assertFalse(self.store._seed_state_path().with_name("context_sets.seed.corrupt.json").exists())

    def test_corrupt_temporary_seed_payload_is_preserved_for_audit(self) -> None:
        record = self.store.create_context_set("Evidence", ["first"])
        self.store._seed_tmp_path().write_text("{bad", encoding="utf-8")

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].context_set_id, record.context_set_id)
        self.assertFalse(self.store._seed_tmp_path().exists())
        self.assertTrue(self.store._seed_tmp_path().with_name("context_sets.seed.tmp.corrupt.json").exists())

    def test_recovered_from_only_cleanup_preserves_existing_updated_at(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        original_updated_at = "2026-03-20T12:00:00+00:00"
        self.store._path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "updated_at": original_updated_at,
                    "recovered_from": "manual",
                    "context_sets": [
                        {
                            "context_set_id": "set-1",
                            "name": "Evidence",
                            "item_ids": ["first"],
                            "created_at": "2026-03-20T11:00:00+00:00",
                            "updated_at": original_updated_at,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        loaded = self.store.load()

        self.assertEqual(len(loaded), 1)
        payload = json.loads(self.store._path.read_text(encoding="utf-8"))
        backup_payload = json.loads(self.store._backup_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("updated_at"), original_updated_at)
        self.assertNotIn("recovered_from", payload)
        self.assertEqual(backup_payload.get("updated_at"), original_updated_at)


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

    def test_healthy_primary_load_refreshes_backup_without_rereading_primary(self) -> None:
        state = self.svc.create_or_open(self.root, "p2-backup-refresh")
        self.svc.lock(state)
        self.svc.unlock(state)
        backup_path = state.root_dir / ".vault_state.bak.json"
        backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "p2-backup-refresh",
                    "is_locked": False,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "recovered_from": "manual",
                }
            ),
            encoding="utf-8",
        )

        with (
            patch.object(VaultService, "_write_backup", wraps=self.svc._write_backup) as write_backup,
            patch.object(
                VaultService,
                "_write_backup_payload",
                wraps=self.svc._write_backup_payload,
            ) as write_backup_payload,
        ):
            reopened = self.svc.create_or_open(self.root, "p2-backup-refresh")

        self.assertIsInstance(reopened.is_locked, bool)
        write_backup.assert_not_called()
        self.assertEqual(write_backup_payload.call_count, 1)
        payload = json.loads(backup_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p2-backup-refresh")
        self.assertNotIn("recovered_from", payload)

    def test_missing_primary_prefers_backup_over_stale_tmp_payload(self) -> None:
        state = self.svc.create_or_open(self.root, "p2-backup-wins")
        state_path = state.root_dir / ".vault_state.json"
        backup_path = state.root_dir / ".vault_state.bak.json"
        tmp_path = state.root_dir / ".vault_state.tmp"

        backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "p2-backup-wins",
                    "is_locked": False,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                }
            ),
            encoding="utf-8",
        )
        tmp_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "p2-backup-wins",
                    "is_locked": True,
                }
            ),
            encoding="utf-8",
        )
        state_path.unlink()

        reopened = self.svc.create_or_open(self.root, "p2-backup-wins")

        self.assertFalse(reopened.is_locked)
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p2-backup-wins")
        self.assertEqual(payload.get("recovered_from"), "backup")
        self.assertFalse(tmp_path.exists())

    def test_corrupt_tmp_does_not_override_valid_backup_recovery(self) -> None:
        state = self.svc.create_or_open(self.root, "p2-corrupt-tmp")
        state_path = state.root_dir / ".vault_state.json"
        backup_path = state.root_dir / ".vault_state.bak.json"
        tmp_path = state.root_dir / ".vault_state.tmp"

        backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "p2-corrupt-tmp",
                    "is_locked": False,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                }
            ),
            encoding="utf-8",
        )
        tmp_path.write_text("{bad", encoding="utf-8")
        state_path.unlink()

        reopened = self.svc.create_or_open(self.root, "p2-corrupt-tmp")

        self.assertFalse(reopened.is_locked)
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p2-corrupt-tmp")
        self.assertEqual(payload.get("recovered_from"), "backup")
        self.assertFalse(tmp_path.exists())

    def test_healthy_primary_load_clears_stale_temporary_corrupt_markers(self) -> None:
        state = self.svc.create_or_open(self.root, "p2-clean")
        state.root_dir.joinpath(".vault_state.tmp.corrupt.json").write_text("{bad", encoding="utf-8")
        state.root_dir.joinpath(".vault_state.bak.tmp.corrupt.json").write_text("{bad", encoding="utf-8")

        reopened = self.svc.create_or_open(self.root, "p2-clean")

        self.assertIsInstance(reopened.is_locked, bool)
        self.assertFalse((state.root_dir / ".vault_state.tmp.corrupt.json").exists())
        self.assertFalse((state.root_dir / ".vault_state.bak.tmp.corrupt.json").exists())

    def test_corrupt_temporary_backup_payload_is_preserved_for_audit(self) -> None:
        state = self.svc.create_or_open(self.root, "p2-temp-audit")
        state.root_dir.joinpath(".vault_state.bak.tmp").write_text("{bad", encoding="utf-8")

        reopened = self.svc.create_or_open(self.root, "p2-temp-audit")

        self.assertIsInstance(reopened.is_locked, bool)
        self.assertFalse((state.root_dir / ".vault_state.bak.tmp").exists())
        self.assertTrue((state.root_dir / ".vault_state.bak.tmp.corrupt.json").exists())

    def test_empty_load_clears_orphaned_quarantine_and_temporary_files(self) -> None:
        state_root = self.root / "p2-empty"
        state_root.mkdir(parents=True, exist_ok=True)
        state_root.joinpath(".vault_state.corrupt.json").write_text("{bad", encoding="utf-8")
        state_root.joinpath(".vault_state.tmp").write_text(
            json.dumps({"schema_version": 1, "project_name": "p2-empty", "is_locked": True}),
            encoding="utf-8",
        )
        state_root.joinpath(".vault_state.tmp.corrupt.json").write_text("{bad", encoding="utf-8")

        reopened = self.svc.create_or_open(self.root, "p2-empty")

        self.assertIsInstance(reopened.is_locked, bool)
        self.assertFalse(state_root.joinpath(".vault_state.corrupt.json").exists())
        self.assertFalse(state_root.joinpath(".vault_state.tmp").exists())
        self.assertFalse(state_root.joinpath(".vault_state.tmp.corrupt.json").exists())

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

        with patch.object(
            VaultService,
            "_quarantine_invalid_state",
            wraps=self.svc._quarantine_invalid_state,
        ) as quarantine:
            reopened = self.svc.create_or_open(self.root, "p3-invalid")

        self.assertTrue(reopened.is_locked)
        quarantine.assert_called_once()
        self.assertFalse((state.root_dir / ".vault_state.corrupt.json").exists())
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p3-invalid")
        self.assertTrue(payload.get("is_locked"))

    def test_backup_with_invalid_project_name_metadata_is_salvaged_and_rewritten(self) -> None:
        state = self.svc.create_or_open(self.root, "p3-backup-project")
        state_path = state.root_dir / ".vault_state.json"
        backup_path = state.root_dir / ".vault_state.bak.json"
        state_path.write_text("{bad", encoding="utf-8")
        backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "../bad",
                    "is_locked": False,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                    "recovered_from": "manual",
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p3-backup-project")

        self.assertTrue(reopened.is_locked)
        self.assertFalse((state.root_dir / ".vault_state.corrupt.json").exists())
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        backup_payload = json.loads(backup_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p3-backup-project")
        self.assertTrue(payload.get("is_locked"))
        self.assertEqual(backup_payload.get("project_name"), "p3-backup-project")
        self.assertTrue(backup_payload.get("is_locked"))
        self.assertNotIn("recovered_from", backup_payload)

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

    def test_missing_is_locked_metadata_preserves_audit_quarantine(self) -> None:
        state_root = self.root / "p3-audit"
        state_root.mkdir(parents=True, exist_ok=True)
        state_path = state_root / ".vault_state.json"
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "p3-audit",
                    "updated_at": "2026-03-20T12:00:00+00:00",
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p3-audit")

        self.assertTrue(reopened.is_locked)
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads((state_root / ".vault_state.corrupt.json").read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p3-audit")
        self.assertTrue(payload.get("is_locked"))
        self.assertTrue((state_root / ".vault_state.corrupt.json").exists())
        self.assertNotIn("is_locked", quarantined_payload)

    def test_missing_updated_at_metadata_is_salvaged_and_rewritten(self) -> None:
        state = self.svc.create_or_open(self.root, "p3-missing-updated")
        state_path = state.root_dir / ".vault_state.json"
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "p3-missing-updated",
                    "is_locked": False,
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p3-missing-updated")

        self.assertFalse(reopened.is_locked)
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p3-missing-updated")
        self.assertFalse(payload.get("is_locked"))
        self.assertIn("updated_at", payload)
        self.assertIsInstance(payload.get("updated_at"), str)
        self.assertEqual(payload.get("updated_at"), payload.get("updated_at").strip())

    def test_missing_is_locked_metadata_quarantines_before_locked_rewrite(self) -> None:
        state = self.svc.create_or_open(self.root, "p3-missing-lock-quarantine")
        state_path = state.root_dir / ".vault_state.json"
        state_path.write_text(
            json.dumps({"schema_version": 1, "project_name": "p3-missing-lock-quarantine"}),
            encoding="utf-8",
        )

        with patch.object(
            VaultService,
            "_quarantine_invalid_state",
            wraps=self.svc._quarantine_invalid_state,
        ) as quarantine:
            reopened = self.svc.create_or_open(self.root, "p3-missing-lock-quarantine")

        self.assertTrue(reopened.is_locked)
        quarantine.assert_called_once()
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p3-missing-lock-quarantine")
        self.assertTrue(payload.get("is_locked"))

    def test_missing_project_name_metadata_recovers_from_backup_before_safe_rewrite(self) -> None:
        state = self.svc.create_or_open(self.root, "p3-missing-project")
        state_path = state.root_dir / ".vault_state.json"
        backup_path = state.root_dir / ".vault_state.bak.json"
        state_path.write_text(
            json.dumps({"schema_version": 1, "is_locked": False}),
            encoding="utf-8",
        )
        backup_path.write_text(
            json.dumps({"schema_version": 1, "project_name": "p3-missing-project", "is_locked": False}),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p3-missing-project")

        self.assertFalse(reopened.is_locked)
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p3-missing-project")
        self.assertFalse(payload.get("is_locked"))
        self.assertEqual(payload.get("recovered_from"), "backup")

    def test_missing_is_locked_metadata_recovers_from_backup_before_safe_rewrite(self) -> None:
        state = self.svc.create_or_open(self.root, "p3-missing-lock-backup")
        state_path = state.root_dir / ".vault_state.json"
        backup_path = state.root_dir / ".vault_state.bak.json"
        state_path.write_text(
            json.dumps({"schema_version": 1, "project_name": "p3-missing-lock-backup"}),
            encoding="utf-8",
        )
        backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "p3-missing-lock-backup",
                    "is_locked": False,
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p3-missing-lock-backup")

        self.assertFalse(reopened.is_locked)
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p3-missing-lock-backup")
        self.assertFalse(payload.get("is_locked"))
        self.assertEqual(payload.get("recovered_from"), "backup")

    def test_missing_required_metadata_backup_is_quarantined_and_rewritten_safely(self) -> None:
        state = self.svc.create_or_open(self.root, "p3-backup-missing")
        state_path = state.root_dir / ".vault_state.json"
        backup_path = state.root_dir / ".vault_state.bak.json"
        backup_corrupt_path = backup_path.with_suffix(".corrupt.json")
        state_path.unlink()
        backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "is_locked": False,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p3-backup-missing")

        self.assertTrue(reopened.is_locked)
        self.assertTrue(backup_corrupt_path.exists())
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        backup_payload = json.loads(backup_path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(backup_corrupt_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p3-backup-missing")
        self.assertTrue(payload.get("is_locked"))
        self.assertNotIn("recovered_from", payload)
        self.assertEqual(backup_payload.get("project_name"), "p3-backup-missing")
        self.assertTrue(backup_payload.get("is_locked"))
        self.assertEqual(quarantined_payload.get("is_locked"), False)
        self.assertNotIn("project_name", quarantined_payload)

    def test_missing_required_metadata_seed_is_quarantined_and_rewritten_safely(self) -> None:
        with patch.object(VaultService, "_write_backup_payload", return_value=False):
            state = self.svc.create_or_open(self.root, "p3-seed-missing")
        state_path = state.root_dir / ".vault_state.json"
        seed_path = state.root_dir / ".vault_state.seed.json"
        seed_corrupt_path = seed_path.with_suffix(".corrupt.json")
        state_path.unlink()
        seed_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "is_locked": False,
                    "updated_at": "2026-03-20T12:00:00+00:00",
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p3-seed-missing")

        self.assertTrue(reopened.is_locked)
        self.assertFalse(seed_path.exists())
        self.assertTrue(seed_corrupt_path.exists())
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        backup_payload = json.loads((state.root_dir / ".vault_state.bak.json").read_text(encoding="utf-8"))
        quarantined_payload = json.loads(seed_corrupt_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p3-seed-missing")
        self.assertTrue(payload.get("is_locked"))
        self.assertNotIn("recovered_from", payload)
        self.assertEqual(backup_payload.get("project_name"), "p3-seed-missing")
        self.assertTrue(backup_payload.get("is_locked"))
        self.assertEqual(quarantined_payload.get("is_locked"), False)
        self.assertNotIn("project_name", quarantined_payload)

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

    def test_recovered_from_only_cleanup_preserves_existing_updated_at(self) -> None:
        state = self.svc.create_or_open(self.root, "p6-cleanup")
        state_path = state.root_dir / ".vault_state.json"
        backup_path = state.root_dir / ".vault_state.bak.json"
        original_updated_at = "2026-03-20T12:00:00+00:00"
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": "p6-cleanup",
                    "is_locked": False,
                    "updated_at": original_updated_at,
                    "recovered_from": "manual",
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p6-cleanup")

        self.assertFalse(reopened.is_locked)
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        backup_payload = json.loads(backup_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p6-cleanup")
        self.assertFalse(payload.get("is_locked"))
        self.assertNotIn("recovered_from", payload)
        self.assertEqual(payload.get("updated_at"), original_updated_at)
        self.assertEqual(backup_payload.get("updated_at"), original_updated_at)

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

    def test_backup_legacy_list_with_only_invalid_entries_is_preserved_for_audit(self) -> None:
        state = self.svc.create_or_open(self.root, "p7-backup-audit")
        state_path = state.root_dir / ".vault_state.json"
        backup_path = state.root_dir / ".vault_state.bak.json"
        corrupt_path = backup_path.with_suffix(".corrupt.json")
        backup_path.write_text(
            json.dumps([None, "", {"bad": "value"}]),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p7-backup-audit")

        self.assertEqual(reopened.is_locked, state.is_locked)
        self.assertTrue(corrupt_path.exists())
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        backup_payload = json.loads(backup_path.read_text(encoding="utf-8"))
        quarantined_payload = json.loads(corrupt_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p7-backup-audit")
        self.assertEqual(backup_payload.get("project_name"), "p7-backup-audit")
        self.assertEqual(quarantined_payload, [None, "", {"bad": "value"}])

    def test_backup_with_malformed_optional_metadata_is_rewritten_canonically(self) -> None:
        state = self.svc.create_or_open(self.root, "p7-metadata")
        state_path = state.root_dir / ".vault_state.json"
        backup_path = state.root_dir / ".vault_state.bak.json"
        state_path.write_text("{bad", encoding="utf-8")
        backup_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": " p7-metadata ",
                    "is_locked": "false",
                    "updated_at": " 2026-03-20T12:00:00+00:00 ",
                    "recovered_from": " BACKUP ",
                    "extra": "ignored",
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p7-metadata")

        self.assertFalse(reopened.is_locked)
        primary_payload = json.loads(state_path.read_text(encoding="utf-8"))
        backup_payload = json.loads(backup_path.read_text(encoding="utf-8"))
        self.assertEqual(primary_payload.get("project_name"), "p7-metadata")
        self.assertIs(primary_payload.get("is_locked"), False)
        self.assertEqual(primary_payload.get("recovered_from"), "backup")
        self.assertEqual(primary_payload.get("schema_version"), 1)
        self.assertEqual(primary_payload.get("updated_at"), primary_payload.get("updated_at").strip())
        self.assertNotEqual(primary_payload.get("updated_at"), " 2026-03-20T12:00:00+00:00 ")
        self.assertNotIn("extra", primary_payload)
        self.assertEqual(backup_payload.get("project_name"), "p7-metadata")
        self.assertIs(backup_payload.get("is_locked"), False)
        self.assertEqual(backup_payload.get("schema_version"), 1)
        self.assertEqual(backup_payload.get("updated_at"), primary_payload.get("updated_at"))
        self.assertNotIn("recovered_from", backup_payload)
        self.assertNotIn("extra", backup_payload)

    def test_seed_with_invalid_metadata_is_salvaged_and_rewritten(self) -> None:
        state_root = self.root / "p7-seed"
        state_root.mkdir(parents=True, exist_ok=True)
        state_root.joinpath(".vault_state.seed.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_name": " p7-seed ",
                    "is_locked": "false",
                    "updated_at": "not-a-timestamp",
                    "recovered_from": "manual",
                }
            ),
            encoding="utf-8",
        )

        reopened = self.svc.create_or_open(self.root, "p7-seed")

        self.assertFalse(reopened.is_locked)
        state_path = state_root / ".vault_state.json"
        backup_path = state_root / ".vault_state.bak.json"
        seed_path = state_root / ".vault_state.seed.json"
        self.assertFalse((state_root / ".vault_state.corrupt.json").exists())
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        backup_payload = json.loads(backup_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("project_name"), "p7-seed")
        self.assertFalse(payload.get("is_locked"))
        self.assertEqual(payload.get("recovered_from"), "seed")
        self.assertNotEqual(payload.get("updated_at"), "not-a-timestamp")
        self.assertEqual(backup_payload.get("project_name"), "p7-seed")
        self.assertFalse(backup_payload.get("is_locked"))
        self.assertNotIn("recovered_from", backup_payload)
        self.assertFalse(seed_path.exists())

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
