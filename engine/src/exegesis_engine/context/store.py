from __future__ import annotations

import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from collections import UserList
from collections.abc import Mapping as AbstractMapping
from collections.abc import MutableMapping as AbstractMutableMapping
from collections.abc import Set as AbstractSet
from collections.abc import ItemsView as AbstractItemsView
from collections.abc import KeysView as AbstractKeysView
from collections.abc import ValuesView as AbstractValuesView
from pathlib import Path
from typing import Union
import os

from exegesis_engine.context.basket import ContextBasket, _canonical_json_dumps, _has_non_finite_float, _mapping_wrapper_exposes_non_plain_json_shape, _payload_as_plain_dict, _payload_has_non_plain_json_shapes, _safe_json_value
from exegesis_engine.context.audit import (
    _audit_corrupt_path,
    _remove_live_audit_log,
    append_audit_record,
    audit_log_path,
    has_trailing_zulu,
    parse_recovered_timestamp,
    utc_now_iso,
)

UTC = timezone.utc

# Back‑compatibility shim: the original public API exposed several helper
# functions in this module.  The current implementation moved them to
# ``utils`` but the tests (and potentially downstream consumers) still
# import directly from :mod:`store`.  Re‑export minimal wrappers so that
# imports continue to work without changing behaviour.
from . import utils as _utils

def validate_and_quarantine(path: str | Path) -> bool:  # pragma: no cover - thin wrapper
    """Delegate to :func:`qual.context.utils.validate_and_quarantine`.

    The function simply forwards the call; it is defined here for backward
    compatibility with older code that imports it from ``store``.
    """

    return _utils.validate_and_quarantine(path)

__all__ = [
    "ContextBasketStore",
    "validate_and_quarantine",
    "clear_corrupt_files",
    "remove_all_corrupt_files",
    "purge_corrupt_state",
    "list_corrupt_files",
    "is_clean_state",
]

_SCHEMA_VERSION = 1
_CANONICAL_DICT_KEYS = {"schema_version", "updated_at", "item_ids", "recovered_from"}
_LOAD_WRAPPER_TEMP_SOURCE_PATH_ATTR = "_load_wrapper_temp_source_path"


def _reject_basket_state_root_alias(root_dir: Path) -> None:
    if _state_root_uses_nested_symlink_alias(root_dir):
        raise ValueError(f"context basket state root uses a symlink alias: {root_dir!r}")


def _fsync_basket_path(path: Path) -> None:
    # Named content-flush seam hardening tests patch in isolation; the body is
    # the shared :func:`_corrupt_artifacts.fsync_file_path` so the durability
    # flush stays one audited path across all stores.
    _fsync_file_path(path)


def _fsync_basket_parent(path: Path) -> None:
    # Named best-effort parent-fsync seam hardening tests patch in isolation; the
    # body is the shared :func:`_corrupt_artifacts.fsync_parent_path` so the
    # directory flush stays one audited path across all stores.
    _fsync_parent_path(path)


class ContextBasketStore:
    """Persist context basket state for scaffold CLI workflows."""

    def __init__(self, root_dir: Path | str) -> None:
        root_dir = Path(root_dir)
        if _state_root_uses_nested_symlink_alias(root_dir):
            raise ValueError(f"context basket state root uses a symlink alias: {root_dir!r}")
        root_dir.mkdir(parents=True, exist_ok=True)
        self._path = root_dir / "context_basket.json"
        self._backup_path = root_dir / "context_basket.bak.json"
        self._seed_path = root_dir / "context_basket.seed.json"

    def _corrupt_path(self) -> Path:
        return self._path.with_suffix(".corrupt.json")

    def _tmp_path(self) -> Path:
        return self._path.with_suffix(".tmp")

    def _backup_tmp_path(self) -> Path:
        return self._backup_path.with_suffix(".tmp")

    def _seed_tmp_path(self) -> Path:
        return self._seed_path.with_suffix(".tmp")

    def _seed_state_path(self) -> Path:
        return self._seed_path

    def _quarantine_missing_item_ids_payload(self, path: Path, payload: object) -> bool:
        if _basket_payload_missing_item_ids_is_recoverable(payload):
            return False
        if isinstance(payload, AbstractMapping) and type(payload) is not dict:
            payload = _payload_as_plain_dict(payload)
            if payload is None:
                self._quarantine_path(path)
                return True
        if isinstance(payload, dict) and "item_ids" not in payload:
            self._quarantine_path(path)
            return True
        return False

    def load(self) -> ContextBasket:
        primary_missing = not self._path.exists()
        backup_missing = not self._backup_path.exists()
        source_payloads: dict[Path, object] = {}

        def _remember_source_payload(path: Path, payload: object | None) -> None:
            if isinstance(payload, AbstractMapping) and type(payload) is not dict:
                source_payloads[path] = payload

        def _sync_source_payloads() -> None:
            wrapper_source_payloads = getattr(self, "_load_wrapper_source_payloads", None)
            payloads_to_sync = (
                wrapper_source_payloads
                if isinstance(wrapper_source_payloads, AbstractMutableMapping)
                else source_payloads
            )
            try:
                primary_payload = _load_json_payload(self._path)
            except Exception:
                primary_payload = None
            if isinstance(primary_payload, AbstractMapping) and type(primary_payload) is not dict:
                primary_payload = _payload_as_plain_dict(primary_payload)
            if isinstance(primary_payload, dict):
                primary_payload = dict(primary_payload)
                primary_payload.pop("recovered_from", None)
            for path, source_payload in payloads_to_sync.items():
                _sync_basket_source_payload_wrapper(
                    source_payload,
                    path,
                    primary_payload if isinstance(primary_payload, dict) else None,
                    preserve_equivalent_raw_wrapper=True,
                )
            _context_basket_store_sync_temp_source_payload(
                self,
                preserve_equivalent_raw_wrapper=True,
            )

        primary_payload, primary_quarantined = self._load_payload(self._path)
        _remember_source_payload(self._path, primary_payload)
        tmp_payload, _ = self._load_payload(self._tmp_path())
        _remember_source_payload(self._tmp_path(), tmp_payload)
        backup_tmp_payload, _ = self._load_payload(self._backup_tmp_path())
        _remember_source_payload(self._backup_tmp_path(), backup_tmp_payload)
        backup_payload, backup_quarantined = self._load_payload(self._backup_path)
        _remember_source_payload(self._backup_path, backup_payload)
        seed_tmp_payload, _ = self._load_payload(self._seed_tmp_path())
        _remember_source_payload(self._seed_tmp_path(), seed_tmp_payload)
        seed_payload, seed_quarantined = self._load_payload(self._seed_state_path())
        _remember_source_payload(self._seed_state_path(), seed_payload)
        if not _basket_payload_missing_item_ids_is_recoverable(tmp_payload):
            self._quarantine_missing_item_ids_payload(self._tmp_path(), tmp_payload)
        if not _basket_payload_missing_item_ids_is_recoverable(backup_tmp_payload):
            self._quarantine_missing_item_ids_payload(self._backup_tmp_path(), backup_tmp_payload)
        preserve_backup_corrupt = False
        preserve_seed_corrupt = False
        if not _basket_payload_missing_item_ids_is_recoverable(backup_payload):
            preserve_backup_corrupt = self._quarantine_missing_item_ids_payload(self._backup_path, backup_payload)
        if not _basket_payload_missing_item_ids_is_recoverable(seed_tmp_payload):
            self._quarantine_missing_item_ids_payload(self._seed_tmp_path(), seed_tmp_payload)
        if not _basket_payload_missing_item_ids_is_recoverable(seed_payload):
            preserve_seed_corrupt = self._quarantine_missing_item_ids_payload(self._seed_state_path(), seed_payload)
        preserve_backup_corrupt = (
            self._quarantine_unrecoverable_list_payload(self._backup_path, backup_payload) or preserve_backup_corrupt
        )
        preserve_seed_corrupt = (
            self._quarantine_unrecoverable_list_payload(self._seed_state_path(), seed_payload) or preserve_seed_corrupt
        )
        backup_needs_audit_quarantine = self._backup_needs_audit_quarantine(backup_payload)
        primary_missing_item_ids = isinstance(primary_payload, dict) and "item_ids" not in primary_payload
        primary_missing_item_ids_is_recoverable = _basket_payload_missing_item_ids_is_recoverable(primary_payload)
        primary_item_ids_need_recovery = self._primary_item_ids_need_recovery(primary_payload)
        primary_needs_quarantine = (
            primary_item_ids_need_recovery and not primary_missing_item_ids_is_recoverable
        ) or (
            isinstance(primary_payload, dict)
            and (
                (primary_missing_item_ids and not primary_missing_item_ids_is_recoverable)
                or self._has_unknown_fields(primary_payload)
                or not self._is_supported_payload(primary_payload)
                or (
                    isinstance(primary_payload.get("item_ids"), list)
                    and self._has_dropped_item_ids(primary_payload.get("item_ids"))
                )
            )
        )
        if primary_missing_item_ids and primary_missing_item_ids_is_recoverable:
            # Missing ``item_ids`` is a recoverable empty-envelope case, but
            # only when the payload is otherwise canonical. Keep malformed
            # envelopes quarantinable so we do not silently discard unknown
            # fields during an empty-state rewrite.
            primary_needs_quarantine = not self._is_supported_payload(primary_payload)

        payload: dict[str, object] | list[object] | None
        recovered_source: str | None
        materialized_empty_state = False
        if primary_needs_quarantine and not (
            primary_missing_item_ids and primary_missing_item_ids_is_recoverable
        ):
            self._quarantine_invalid_file()
        if isinstance(primary_payload, list) and primary_payload:
            self._quarantine_invalid_backup()
            preserve_backup_corrupt = True
            backup_items = None
            if isinstance(backup_payload, dict):
                backup_items = self._parse_item_ids(backup_payload.get("item_ids"))
            elif isinstance(backup_payload, list):
                backup_items = self._parse_item_ids(backup_payload)
            primary_items = self._parse_item_ids(primary_payload)
            if backup_items and primary_items is not None and backup_items != primary_items:
                self._quarantine_invalid_file()
                primary_payload = None
                primary_quarantined = True
        if primary_missing_item_ids or primary_item_ids_need_recovery:
            if isinstance(primary_payload, list):
                primary_items = self._parse_item_ids(primary_payload)
                if primary_items:
                    backup_items = None
                    if isinstance(backup_payload, dict):
                        backup_items = self._parse_item_ids(backup_payload.get("item_ids"))
                    elif isinstance(backup_payload, list):
                        backup_items = self._parse_item_ids(backup_payload)
                    if backup_items and backup_items != primary_items and not backup_needs_audit_quarantine:
                        payload = backup_payload
                        recovered_source = "backup"
                    else:
                        payload = primary_payload
                        recovered_source = None
                else:
                    payload, recovered_source = self._prefer_recovery_payload(
                        tmp_payload,
                        backup_tmp_payload,
                        backup_payload,
                        seed_tmp_payload,
                        seed_payload,
                    )
                    if payload is None or not self._has_recovery_payload_items(payload):
                        payload = primary_payload
                        recovered_source = None
            else:
                payload, recovered_source = self._prefer_recovery_payload(
                    tmp_payload,
                    backup_tmp_payload,
                    backup_payload,
                    seed_tmp_payload,
                    seed_payload,
                )
                if payload is None:
                    payload = primary_payload
                    recovered_source = None
        elif isinstance(primary_payload, list):
            primary_items = self._parse_item_ids(primary_payload)
            if primary_items:
                backup_items = None
                if isinstance(backup_payload, dict):
                    backup_items = self._parse_item_ids(backup_payload.get("item_ids"))
                elif isinstance(backup_payload, list):
                    backup_items = self._parse_item_ids(backup_payload)
                if backup_items and backup_items != primary_items and not backup_needs_audit_quarantine:
                    payload = backup_payload
                    recovered_source = "backup"
                else:
                    payload = primary_payload
                    recovered_source = None
            else:
                payload, recovered_source = self._prefer_recovery_payload(
                    tmp_payload,
                    backup_tmp_payload,
                    backup_payload,
                    seed_tmp_payload,
                    seed_payload,
                )
                if payload is None or not self._has_recovery_payload_items(payload):
                    payload = primary_payload
                    recovered_source = None
        elif primary_payload is not None:
            if (
                isinstance(primary_payload, dict)
                and self._has_explicit_empty_recovery_payload(primary_payload)
                and primary_needs_quarantine
            ):
                recovery_payload, recovery_source = self._prefer_recovery_payload(
                    tmp_payload,
                    backup_tmp_payload,
                    backup_payload,
                    seed_tmp_payload,
                    seed_payload,
                )
                if recovery_payload is not None and self._has_recovery_payload_items(recovery_payload):
                    payload = recovery_payload
                    recovered_source = recovery_source
                else:
                    payload = primary_payload
                    recovered_source = None
            elif (
                isinstance(primary_payload, dict)
                and "updated_at" not in primary_payload
                and not backup_needs_audit_quarantine
            ):
                primary_items = self._parse_item_ids(primary_payload.get("item_ids"))
                if isinstance(backup_payload, dict):
                    backup_items = self._parse_item_ids(backup_payload.get("item_ids"))
                elif isinstance(backup_payload, list):
                    backup_items = self._parse_item_ids(backup_payload)
                else:
                    backup_items = None
                if primary_items is not None and backup_items is not None and len(backup_items) > len(primary_items):
                    payload = backup_payload
                    recovered_source = "backup"
                else:
                    payload = primary_payload
                    recovered_source = None
            else:
                payload = primary_payload
                recovered_source = None
        elif primary_payload is None:
            payload, recovered_source = self._prefer_recovery_payload(
                tmp_payload,
                backup_tmp_payload,
                backup_payload,
                seed_tmp_payload,
                seed_payload,
            )
            if payload is None:
                if primary_quarantined or backup_quarantined or seed_quarantined:
                    # Keep a canonical empty basket on disk when quarantine
                    # found only malformed state and nothing recoverable.
                    payload = []
                    recovered_source = None
                    materialized_empty_state = True
                else:
                    self._clear_quarantine_file(
                        preserve_backup_corrupt=preserve_backup_corrupt,
                        preserve_seed_corrupt=preserve_seed_corrupt,
                    )
                    self._clear_temporary_files()
                    empty_basket = ContextBasket()
                    try:
                        self.save(empty_basket)
                    except OSError:
                        pass
                    _sync_source_payloads()
                    return empty_basket
        else:
            self._clear_quarantine_file(
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
            )
            self._clear_temporary_files()
            empty_basket = ContextBasket()
            try:
                self.save(empty_basket)
            except OSError:
                pass
            _sync_source_payloads()
            return empty_basket

        should_rewrite = False
        rewrite_empty_recovery = False
        explicit_empty_recovery = self._is_empty_recovery_payload(payload) and self._has_explicit_empty_recovery_payload(
            payload
        )
        audit_recovered_source = recovered_source
        temp_source_path = _context_basket_store_recovery_source_path(self, audit_recovered_source)
        if temp_source_path is not None:
            setattr(self, _LOAD_WRAPPER_TEMP_SOURCE_PATH_ATTR, temp_source_path)
        else:
            try:
                delattr(self, _LOAD_WRAPPER_TEMP_SOURCE_PATH_ATTR)
            except AttributeError:
                pass
        if explicit_empty_recovery:
            # Canonical empty state should still be materialized when it is the
            # only recoverable payload, but explicit empty recovery should not
            # claim provenance on the rewritten payload.
            rewrite_empty_recovery = recovered_source is not None or primary_payload is None
            if recovered_source is not None:
                recovered_source = None
        if isinstance(payload, list):
            parsed_items = self._parse_item_ids(payload)
            if parsed_items is None:
                self._discard_payload_source(recovered_source)
                _sync_source_payloads()
                return ContextBasket()
            basket = ContextBasket(item_ids=parsed_items)
            should_rewrite = True
        elif isinstance(payload, dict):
            schema_version = self._parse_schema_version(payload)
            if "item_ids" not in payload:
                basket = ContextBasket()
                should_rewrite = True
            else:
                raw_item_ids = payload.get("item_ids")
                parsed_items = self._parse_item_ids(raw_item_ids)
                if parsed_items is None:
                    basket = ContextBasket()
                    parsed_items = []
                    should_rewrite = True
                normalized_items = self._normalize_item_ids(parsed_items)
                basket = ContextBasket(item_ids=normalized_items)
                should_rewrite = (
                    should_rewrite
                    or schema_version != _SCHEMA_VERSION
                    or normalized_items != parsed_items
                )
                if not isinstance(raw_item_ids, list) or parsed_items != raw_item_ids:
                    should_rewrite = True
                if self._has_dropped_item_ids(raw_item_ids):
                    should_rewrite = True
            if self._has_unknown_fields(payload):
                should_rewrite = True
            if "updated_at" not in payload:
                should_rewrite = True
            if "updated_at" in payload:
                normalized_updated_at = self._parse_updated_at(payload.get("updated_at"))
                if normalized_updated_at is None:
                    should_rewrite = True
                elif payload.get("updated_at") != normalized_updated_at:
                    should_rewrite = True
            if "recovered_from" in payload:
                should_rewrite = True
        else:
            self._discard_payload_source(recovered_source)
            _sync_source_payloads()
            return ContextBasket()

        recovered_from = self._recovery_marker(
            primary_unavailable=(
                primary_missing
                or primary_payload is None
                or primary_missing_item_ids
                or primary_item_ids_need_recovery
                or recovered_source is not None
            ),
            recovered_source=recovered_source,
        )
        should_rewrite = should_rewrite or rewrite_empty_recovery
        cleanup_timestamp = self._recovery_marker_cleanup_timestamp(payload, basket)
        if (
            should_rewrite
            and isinstance(primary_payload, dict)
            and isinstance(backup_payload, dict)
            and not self._backup_needs_audit_quarantine(backup_payload)
        ):
            backup_item_ids = self._parse_item_ids(backup_payload.get("item_ids"))
            backup_updated_at = self._parse_updated_at(backup_payload.get("updated_at"))
            if backup_item_ids is not None and sorted(backup_item_ids) == sorted(basket.item_ids):
                primary_updated_at = self._parse_updated_at(primary_payload.get("updated_at"))
                candidate_timestamp = cleanup_timestamp
                if primary_updated_at is not None:
                    candidate_timestamp = (
                        primary_updated_at
                        if candidate_timestamp is None
                        else max(candidate_timestamp, primary_updated_at)
                    )
                if backup_updated_at is not None:
                    candidate_timestamp = (
                        backup_updated_at
                        if candidate_timestamp is None
                        else max(candidate_timestamp, backup_updated_at)
                    )
                cleanup_timestamp = candidate_timestamp
        recovered_persisted_missing_item_ids = (
            isinstance(payload, dict)
            and "item_ids" not in payload
            and recovered_source in {"backup", "seed"}
        )
        preserve_primary_corrupt = bool(
            primary_needs_quarantine
            and not (primary_missing_item_ids and primary_missing_item_ids_is_recoverable)
            and primary_payload is not None
            and (
                (
                    recovered_source is None
                    and isinstance(primary_payload, dict)
                    and (primary_item_ids_need_recovery or self._has_unknown_fields(primary_payload))
                )
                or (
                    isinstance(primary_payload, dict)
                    and recovered_source is not None
                    and self._has_explicit_empty_recovery_payload(primary_payload)
                    and self._has_recovery_payload_items(payload)
                )
                or (explicit_empty_recovery and recovered_source is not None and isinstance(primary_payload, dict))
            )
        )
        preserve_primary_corrupt = preserve_primary_corrupt or (materialized_empty_state and primary_quarantined)
        # When the primary file was unreadable (e.g. invalid UTF-8) and we
        # recovered basket state from another source, keep the quarantine
        # artifact so the caller can audit the original malformed bytes.
        preserve_primary_corrupt = preserve_primary_corrupt or (
            primary_quarantined
            and primary_payload is None
            and recovered_source is not None
            and self._has_recovery_payload_items(payload)
        )
        preserve_backup_corrupt = bool(
            preserve_backup_corrupt
            or backup_quarantined
            or (recovered_source == "backup" and recovered_persisted_missing_item_ids)
        )
        preserve_seed_corrupt = bool(
            preserve_seed_corrupt or seed_quarantined or (recovered_source == "seed" and recovered_persisted_missing_item_ids)
        )
        if isinstance(primary_payload, list):
            preserve_primary_corrupt = True
        if isinstance(primary_payload, list) and primary_payload and not self._has_recovery_payload_items(primary_payload):
            # Keep the original malformed legacy list available for audit when
            # it cannot contribute any recoverable item ids.
            preserve_primary_corrupt = True
        if (
            audit_recovered_source == "backup"
            and isinstance(backup_payload, list)
            and self._legacy_list_payload_has_dropped_item_ids(backup_payload)
        ):
            self._quarantine_invalid_backup()
            preserve_backup_corrupt = True
        if (
            audit_recovered_source == "seed"
            and isinstance(seed_payload, list)
            and self._legacy_list_payload_has_dropped_item_ids(seed_payload)
        ):
            self._quarantine_invalid_seed()
            preserve_seed_corrupt = True
        if audit_recovered_source == "backup" and backup_payload is not None and self._backup_needs_audit_quarantine(
            backup_payload
        ):
            self._quarantine_invalid_backup()
            preserve_backup_corrupt = True
        if audit_recovered_source == "seed" and seed_payload is not None and self._backup_needs_audit_quarantine(seed_payload):
            self._quarantine_invalid_seed()
            preserve_seed_corrupt = True
        if backup_payload is not None and self._backup_needs_audit_quarantine(backup_payload):
            self._quarantine_invalid_backup()
            preserve_backup_corrupt = True
        if seed_payload is not None and self._backup_needs_audit_quarantine(seed_payload):
            self._quarantine_invalid_seed()
            preserve_seed_corrupt = True
        if isinstance(primary_payload, list):
            preserve_primary_corrupt = True
        primary_payload_updated_at = (
            self._parse_updated_at(primary_payload.get("updated_at"))
            if isinstance(primary_payload, dict)
            else None
        )
        backup_payload_updated_at = (
            self._parse_updated_at(backup_payload.get("updated_at"))
            if isinstance(backup_payload, dict)
            else None
        )
        # When rewriting due to missing fields, ensure we preserve a valid
        # ``updated_at`` timestamp.  The original logic only used the
        # ``cleanup_timestamp`` derived from the recovery marker which is
        # absent when we recover directly from backup or seed files.
        # This caused many tests that expect the updated timestamp of the
        # backup to be retained to fail.  We now fall back to the backup's
        # ``updated_at`` value if present and valid.
        if recovered_source is not None or should_rewrite:
            # Keep the backup aligned with the latest canonical basket whenever we
            # rewrite state during load, not only when we recover from tmp/backup.
            # ``cleanup_timestamp`` may be ``None`` if the chosen payload
            # lacks a timestamp.  In that case, try to pull one from the
            # primary payload first and then the backup (if it exists) before
            # delegating to :meth:`save`.
            effective_updated_at = cleanup_timestamp
            if recovered_source in {"backup", "seed"}:
                effective_updated_at = (
                    backup_payload_updated_at
                    or effective_updated_at
                    or primary_payload_updated_at
                )
            elif (
                should_rewrite
                and isinstance(primary_payload, dict)
                and isinstance(backup_payload, dict)
                and not self._backup_needs_audit_quarantine(backup_payload)
            ):
                primary_item_ids = self._parse_item_ids(primary_payload.get("item_ids"))
                backup_item_ids = self._parse_item_ids(backup_payload.get("item_ids"))
                if (
                    primary_item_ids is not None
                    and backup_item_ids is not None
                    and sorted(primary_item_ids) == sorted(backup_item_ids)
                ):
                    if primary_payload_updated_at is None:
                        effective_updated_at = backup_payload_updated_at
                    elif backup_payload_updated_at is not None:
                        effective_updated_at = max(primary_payload_updated_at, backup_payload_updated_at)
            if effective_updated_at is None and isinstance(primary_payload, dict):
                effective_updated_at = self._parse_updated_at(primary_payload.get("updated_at"))
            if effective_updated_at is None and backup_payload is not None:
                effective_updated_at = self._parse_updated_at(
                    backup_payload.get("updated_at")
                )

            self.save(
                basket,
                recovered_from=recovered_from,
                refresh_backup=True,
                updated_at=effective_updated_at,
                preserve_primary_corrupt=preserve_primary_corrupt,
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
            )
        elif primary_payload is not None and (
            backup_payload is None
            or backup_missing
            or self._backup_needs_refresh(
                backup_payload,
                basket,
                payload if isinstance(payload, dict) else None,
            )
        ):
            if self._backup_needs_audit_quarantine(backup_payload):
                self._quarantine_invalid_backup()
                preserve_backup_corrupt = True
            if self._backup_needs_audit_quarantine(seed_payload):
                self._quarantine_invalid_seed()
                preserve_seed_corrupt = True
            backup_written = self._write_backup_payload(self._backup_payload(payload))
            self._clear_recovery_artifacts(
                preserve_seed=not backup_written,
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
            )
            if not backup_written:
                self._write_seed(self._backup_payload(payload))
        elif backup_payload is None or backup_missing or self._backup_needs_refresh(
            backup_payload,
            basket,
            payload if isinstance(payload, dict) else None,
        ):
            backup_written = False
            if isinstance(payload, dict):
                backup_written = self._write_backup_payload(self._backup_payload(payload))
            else:
                backup_written = self._write_backup()
            self._clear_recovery_artifacts(
                preserve_seed=not backup_written,
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
            )
            if not backup_written:
                self._write_seed(self._backup_payload(payload) if isinstance(payload, dict) else payload)
        else:
            self._clear_recovery_artifacts(
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
            )
        if (
            recovered_source is not None
            or primary_quarantined
            or backup_quarantined
            or seed_quarantined
            or materialized_empty_state
            or rewrite_empty_recovery
            or should_rewrite
        ):
            _sync_source_payloads()
        return _finish(basket)


def _is_corrupt_artifact_path(path: Path) -> bool:
    name = path.name
    return (
        name.endswith((".corrupt.json", ".corrupt"))
        or ".corrupt.json." in name
        or ".corrupt." in name
    )


_CORRUPT_ARTIFACT_SCAN_PATTERNS = (
    "*.corrupt.json",
    "*.corrupt.json.*",
    "*.corrupt",
    "*.corrupt.*",
)


def _dedupe_corrupt_paths(corrupt_paths: list[Path]) -> list[Path]:
    unique_paths: list[Path] = []
    seen_paths: set[str] = set()
    for path in sorted(corrupt_paths, key=str):
        path_key = _corrupt_path_key(path)
        if path_key in seen_paths:
            continue
        seen_paths.add(path_key)
        unique_paths.append(path)
    return unique_paths


def list_corrupt_files(state_root: Union[Path, str]) -> list[Path]:
    root = Path(state_root)
    corrupt_paths: list[Path] = []
    if _path_exists_or_is_symlink(root) and _is_corrupt_artifact_path(root):
        # Keep an explicitly supplied corrupt root visible even if the parent
        # scan later fails. That way the audit helpers still surface the
        # artifact that the caller pointed us at directly.
        corrupt_paths.append(root)
    scan_root = _corrupt_scan_root(root)
    try:
        scan_root_is_symlink = scan_root.is_symlink()
    except (OSError, RuntimeError):
        return corrupt_paths
    if scan_root_is_symlink and not _is_corrupt_artifact_path(scan_root):
        return corrupt_paths
    if scan_root.is_dir():
        for pattern in _CORRUPT_ARTIFACT_SCAN_PATTERNS:
            try:
                corrupt_paths.extend(scan_root.rglob(pattern))
            except (OSError, RuntimeError):
                # Best-effort audit helpers should fail closed per artifact
                # class rather than letting one blocked glob hide other corrupt
                # files that remain visible and removable.
                continue
    # Some callers can surface the same corrupt path through multiple scan
    # aliases. Keep the audit view deterministic by returning a stable unique
    # list rather than double-counting the same artefact.
    return _dedupe_corrupt_paths(corrupt_paths)


from collections import OrderedDict, UserList
from collections.abc import Iterable as AbstractIterable
from collections.abc import Mapping as AbstractMapping
from collections.abc import Set as AbstractSet
from collections.abc import ItemsView as AbstractItemsView
from collections.abc import KeysView as AbstractKeysView
from collections.abc import ValuesView as AbstractValuesView
import shutil
import weakref

from exegesis_engine.storage._corrupt_artifacts import quarantine_corrupt_artifact as _quarantine_corrupt_artifact
from exegesis_engine.storage._corrupt_artifacts import (
    clear_corrupt_artifact_family as _clear_corrupt_artifact_family,
    corrupt_artifact_path_for as _corrupt_artifact_path_for,
    legacy_json_temp_path as _legacy_json_temp_path,
    fsync_file_path as _fsync_file_path,
    fsync_parent_path as _fsync_parent_path,
    quarantine_blocking_corrupt_artifact as _quarantine_blocking_corrupt_artifact,
    quarantine_stale_corrupt_temp_artifact as _quarantine_stale_corrupt_temp_artifact,
    restore_corrupt_artifact_snapshots as _restore_corrupt_artifact_snapshots,
    snapshot_corrupt_artifact_bytes as _snapshot_corrupt_artifact_bytes,
    staged_atomic_write as _staged_atomic_write,
    state_root_uses_symlink_alias as _state_root_uses_nested_symlink_alias,
)

# BEGIN MATERIALIZED FROZEN BASELINE: src/qual/context/store.py @ 47cda4df831ac41867a8792f40d720e0cb109514
# Generated from the previous historical-source replacement block.
# Keep this code in this module so public class __module__ values and
# module-global patch seams match the old runtime exec behavior.

import json
import math
import re
from datetime import datetime, timezone
UTC = timezone.utc
from pathlib import Path

from exegesis_engine.context.basket import ContextBasket

_SCHEMA_VERSION = 1
_CANONICAL_DICT_KEYS = {"schema_version", "updated_at", "item_ids", "recovered_from"}


class ContextBasketStore:
    """Persist context basket state for scaffold CLI workflows."""

    def __init__(self, root_dir: Path) -> None:
        self._path = root_dir / "context_basket.json"
        self._backup_path = root_dir / "context_basket.bak.json"
        self._seed_path = root_dir / "context_basket.seed.json"

    def _corrupt_path(self) -> Path:
        return self._path.with_suffix(".corrupt.json")

    def _tmp_path(self) -> Path:
        return self._path.with_suffix(".tmp")

    def _backup_tmp_path(self) -> Path:
        return self._backup_path.with_suffix(".tmp")

    def _seed_tmp_path(self) -> Path:
        return self._seed_path.with_suffix(".tmp")

    def _seed_state_path(self) -> Path:
        return self._seed_path

    def _quarantine_missing_item_ids_payload(self, path: Path, payload: object) -> bool:
        if isinstance(payload, dict) and "item_ids" not in payload:
            self._quarantine_path(path)
            return True
        return False

    def load(self) -> ContextBasket:
        primary_missing = not self._path.exists()
        backup_missing = not self._backup_path.exists()
        primary_payload, primary_quarantined = self._load_payload(self._path)
        tmp_payload, _ = self._load_payload(self._tmp_path())
        backup_tmp_payload, _ = self._load_payload(self._backup_tmp_path())
        backup_payload, backup_quarantined = self._load_payload(self._backup_path)
        seed_tmp_payload, _ = self._load_payload(self._seed_tmp_path())
        seed_payload, seed_quarantined = self._load_payload(self._seed_state_path())
        self._quarantine_missing_item_ids_payload(self._tmp_path(), tmp_payload)
        self._quarantine_missing_item_ids_payload(self._backup_tmp_path(), backup_tmp_payload)
        preserve_backup_corrupt = self._quarantine_missing_item_ids_payload(self._backup_path, backup_payload)
        self._quarantine_missing_item_ids_payload(self._seed_tmp_path(), seed_tmp_payload)
        preserve_seed_corrupt = self._quarantine_missing_item_ids_payload(self._seed_state_path(), seed_payload)
        preserve_backup_corrupt = (
            self._quarantine_unrecoverable_list_payload(self._backup_path, backup_payload) or preserve_backup_corrupt
        )
        preserve_seed_corrupt = (
            self._quarantine_unrecoverable_list_payload(self._seed_state_path(), seed_payload) or preserve_seed_corrupt
        )
        primary_missing_item_ids = isinstance(primary_payload, dict) and "item_ids" not in primary_payload
        primary_item_ids_need_recovery = self._primary_item_ids_need_recovery(primary_payload)
        primary_needs_quarantine = primary_item_ids_need_recovery or (
            isinstance(primary_payload, dict)
            and (
                primary_missing_item_ids
                or self._has_unknown_fields(primary_payload)
                or not self._is_supported_payload(primary_payload)
            )
        )

        payload: dict[str, object] | list[object] | None
        recovered_source: str | None
        materialized_empty_state = False
        if primary_needs_quarantine:
            self._quarantine_invalid_file()
        if primary_missing_item_ids or primary_item_ids_need_recovery:
            if isinstance(primary_payload, list):
                primary_items = self._parse_item_ids(primary_payload)
                if primary_items:
                    payload = primary_payload
                    recovered_source = None
                else:
                    payload, recovered_source = self._prefer_recovery_payload(
                        tmp_payload,
                        backup_tmp_payload,
                        backup_payload,
                        seed_tmp_payload,
                        seed_payload,
                    )
                    if payload is None or not self._has_recovery_payload_items(payload):
                        payload = primary_payload
                        recovered_source = None
            else:
                payload, recovered_source = self._prefer_recovery_payload(
                    tmp_payload,
                    backup_tmp_payload,
                    backup_payload,
                    seed_tmp_payload,
                    seed_payload,
                )
                if payload is None:
                    payload = primary_payload
                    recovered_source = None
        elif isinstance(primary_payload, list):
            primary_items = self._parse_item_ids(primary_payload)
            if primary_items:
                backup_items = None
                if isinstance(backup_payload, dict):
                    backup_items = self._parse_item_ids(backup_payload.get("item_ids"))
                elif isinstance(backup_payload, list):
                    backup_items = self._parse_item_ids(backup_payload)
                if backup_items and backup_items != primary_items and not self._backup_needs_audit_quarantine(backup_payload):
                    payload = backup_payload
                    recovered_source = "backup"
                else:
                    payload = primary_payload
                    recovered_source = None
            else:
                payload, recovered_source = self._prefer_recovery_payload(
                    tmp_payload,
                    backup_tmp_payload,
                    backup_payload,
                    seed_tmp_payload,
                    seed_payload,
                )
                if payload is None or not self._has_recovery_payload_items(payload):
                    payload = primary_payload
                    recovered_source = None
        elif primary_payload is not None:
            if (
                isinstance(primary_payload, dict)
                and self._has_explicit_empty_recovery_payload(primary_payload)
                and primary_needs_quarantine
            ):
                recovery_payload, recovery_source = self._prefer_recovery_payload(
                    tmp_payload,
                    backup_tmp_payload,
                    backup_payload,
                    seed_tmp_payload,
                    seed_payload,
                )
                if recovery_payload is not None and self._has_recovery_payload_items(recovery_payload):
                    payload = recovery_payload
                    recovered_source = recovery_source
                else:
                    payload = primary_payload
                    recovered_source = None
            else:
                payload = primary_payload
                recovered_source = None
        elif primary_payload is None:
            payload, recovered_source = self._prefer_recovery_payload(
                tmp_payload,
                backup_tmp_payload,
                backup_payload,
                seed_tmp_payload,
                seed_payload,
            )
            if payload is None:
                if primary_quarantined or backup_quarantined or seed_quarantined:
                    # Keep a canonical empty basket on disk when quarantine
                    # found only malformed state and nothing recoverable.
                    payload = []
                    recovered_source = None
                    materialized_empty_state = True
                else:
                    self._clear_quarantine_file(
                        preserve_backup_corrupt=preserve_backup_corrupt,
                        preserve_seed_corrupt=preserve_seed_corrupt,
                    )
                    self._clear_temporary_files()
                    return ContextBasket()
        else:
            self._clear_quarantine_file(
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
            )
            self._clear_temporary_files()
            return ContextBasket()

        should_rewrite = False
        rewrite_empty_recovery = False
        explicit_empty_recovery = self._is_empty_recovery_payload(payload) and self._has_explicit_empty_recovery_payload(
            payload
        )
        audit_recovered_source = recovered_source
        if explicit_empty_recovery:
            # Canonical empty state should still be materialized when it is the
            # only recoverable payload, but explicit empty recovery should not
            # claim provenance on the rewritten payload.
            rewrite_empty_recovery = recovered_source is not None or primary_payload is None
            if recovered_source is not None:
                recovered_source = None
        if isinstance(payload, list):
            parsed_items = self._parse_item_ids(payload)
            if parsed_items is None:
                self._discard_payload_source(recovered_source)
                return ContextBasket()
            basket = ContextBasket(item_ids=parsed_items)
            should_rewrite = True
        elif isinstance(payload, dict):
            schema_version = self._parse_schema_version(payload)
            if "item_ids" not in payload:
                basket = ContextBasket()
                should_rewrite = True
            else:
                raw_item_ids = payload.get("item_ids")
                parsed_items = self._parse_item_ids(raw_item_ids)
                if parsed_items is None:
                    basket = ContextBasket()
                    parsed_items = []
                    should_rewrite = True
                normalized_items = self._normalize_item_ids(parsed_items)
                basket = ContextBasket(item_ids=normalized_items)
                should_rewrite = (
                    should_rewrite
                    or schema_version != _SCHEMA_VERSION
                    or normalized_items != parsed_items
                )
                if not isinstance(raw_item_ids, list) or parsed_items != raw_item_ids:
                    should_rewrite = True
                if self._has_dropped_item_ids(raw_item_ids):
                    should_rewrite = True
            if self._has_unknown_fields(payload):
                should_rewrite = True
            if "updated_at" not in payload:
                should_rewrite = True
            if "updated_at" in payload:
                normalized_updated_at = self._parse_updated_at(payload.get("updated_at"))
                if normalized_updated_at is None:
                    should_rewrite = True
                elif payload.get("updated_at") != normalized_updated_at:
                    should_rewrite = True
            if "recovered_from" in payload:
                should_rewrite = True
        else:
            self._discard_payload_source(recovered_source)
            return ContextBasket()

        recovered_from = self._recovery_marker(
            primary_unavailable=(
                primary_missing
                or primary_payload is None
                or primary_missing_item_ids
                or primary_item_ids_need_recovery
                or recovered_source is not None
            ),
            recovered_source=recovered_source,
        )
        should_rewrite = should_rewrite or rewrite_empty_recovery
        cleanup_timestamp = self._recovery_marker_cleanup_timestamp(payload, basket)
        if (
            should_rewrite
            and isinstance(primary_payload, dict)
            and isinstance(backup_payload, dict)
            and not self._backup_needs_audit_quarantine(backup_payload)
        ):
            backup_item_ids = self._parse_item_ids(backup_payload.get("item_ids"))
            backup_updated_at = self._parse_updated_at(backup_payload.get("updated_at"))
            if backup_item_ids is not None and sorted(backup_item_ids) == sorted(basket.item_ids):
                primary_updated_at = self._parse_updated_at(primary_payload.get("updated_at"))
                candidate_timestamp = cleanup_timestamp
                if primary_updated_at is not None:
                    candidate_timestamp = (
                        primary_updated_at
                        if candidate_timestamp is None
                        else max(candidate_timestamp, primary_updated_at)
                    )
                if backup_updated_at is not None:
                    candidate_timestamp = (
                        backup_updated_at
                        if candidate_timestamp is None
                        else max(candidate_timestamp, backup_updated_at)
                    )
                cleanup_timestamp = candidate_timestamp
        recovered_persisted_missing_item_ids = (
            isinstance(payload, dict)
            and "item_ids" not in payload
            and recovered_source in {"backup", "seed"}
        )
        preserve_primary_corrupt = bool(
            primary_needs_quarantine
            and primary_payload is not None
            and (
                (
                    recovered_source is None
                    and isinstance(primary_payload, dict)
                    and (primary_item_ids_need_recovery or self._has_unknown_fields(primary_payload))
                )
                or (
                    isinstance(primary_payload, dict)
                    and recovered_source is not None
                    and self._has_explicit_empty_recovery_payload(primary_payload)
                    and self._has_recovery_payload_items(payload)
                )
                or (explicit_empty_recovery and recovered_source is not None and isinstance(primary_payload, dict))
            )
        )
        preserve_primary_corrupt = preserve_primary_corrupt or (materialized_empty_state and primary_quarantined)
        preserve_backup_corrupt = bool(
            preserve_backup_corrupt
            or backup_quarantined
            or (recovered_source == "backup" and recovered_persisted_missing_item_ids)
        )
        preserve_seed_corrupt = bool(
            preserve_seed_corrupt or seed_quarantined or (recovered_source == "seed" and recovered_persisted_missing_item_ids)
        )
        if isinstance(primary_payload, list) and primary_payload and not self._has_recovery_payload_items(primary_payload):
            # Keep the original malformed legacy list available for audit when
            # it cannot contribute any recoverable item ids.
            preserve_primary_corrupt = True
        if (
            audit_recovered_source == "backup"
            and isinstance(backup_payload, list)
            and self._legacy_list_payload_has_dropped_item_ids(backup_payload)
        ):
            self._quarantine_invalid_backup()
            preserve_backup_corrupt = True
        if (
            audit_recovered_source == "seed"
            and isinstance(seed_payload, list)
            and self._legacy_list_payload_has_dropped_item_ids(seed_payload)
        ):
            self._quarantine_invalid_seed()
            preserve_seed_corrupt = True
        if audit_recovered_source == "backup" and backup_payload is not None and self._backup_needs_audit_quarantine(
            backup_payload
        ):
            self._quarantine_invalid_backup()
            preserve_backup_corrupt = True
        if audit_recovered_source == "seed" and seed_payload is not None and self._backup_needs_audit_quarantine(seed_payload):
            self._quarantine_invalid_seed()
            preserve_seed_corrupt = True
        if recovered_source is not None or should_rewrite:
            # Keep the backup aligned with the latest canonical basket whenever we
            # rewrite state during load, not only when we recover from tmp/backup.
            self.save(
                basket,
                recovered_from=recovered_from,
                refresh_backup=True,
                updated_at=cleanup_timestamp,
                preserve_primary_corrupt=preserve_primary_corrupt,
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
            )
        elif primary_payload is not None and (
            backup_payload is None
            or backup_missing
            or self._backup_needs_refresh(
                backup_payload,
                basket,
                payload if isinstance(payload, dict) else None,
            )
        ):
            if self._backup_needs_audit_quarantine(backup_payload):
                self._quarantine_invalid_backup()
                preserve_backup_corrupt = True
            if self._backup_needs_audit_quarantine(seed_payload):
                self._quarantine_invalid_seed()
                preserve_seed_corrupt = True
            backup_written = self._write_backup_payload(self._backup_payload(payload))
            self._clear_recovery_artifacts(
                preserve_seed=not backup_written,
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
            )
            if not backup_written:
                self._write_seed(self._backup_payload(payload))
        elif backup_payload is None or backup_missing or self._backup_needs_refresh(
            backup_payload,
            basket,
            payload if isinstance(payload, dict) else None,
        ):
            backup_written = False
            if isinstance(payload, dict):
                backup_written = self._write_backup_payload(self._backup_payload(payload))
            else:
                backup_written = self._write_backup()
            self._clear_recovery_artifacts(
                preserve_seed=not backup_written,
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
            )
            if not backup_written:
                self._write_seed(self._backup_payload(payload) if isinstance(payload, dict) else payload)
        else:
            self._clear_recovery_artifacts(
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
            )
        return basket


    def save(
        self,
        basket: ContextBasket,
        recovered_from: str | None = None,
        refresh_backup: bool = False,
        updated_at: str | None = None,
        preserve_primary_corrupt: bool = False,
        preserve_backup_corrupt: bool = False,
        preserve_seed_corrupt: bool = False,
    ) -> None:
        basket.normalize()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        normalized_recovered_from = self._parse_recovered_from(recovered_from)
        current_payload, _ = self._load_payload(self._path)
        current_backup_payload, _ = self._load_payload(self._backup_path)
        cleanup_timestamp = self._recovery_marker_cleanup_timestamp(current_payload, basket)
        if (
            normalized_recovered_from is None
            and cleanup_timestamp is not None
            and not preserve_primary_corrupt
            and not preserve_backup_corrupt
            and not preserve_seed_corrupt
        ):
            payload = {
                "schema_version": _SCHEMA_VERSION,
                "updated_at": cleanup_timestamp,
                "item_ids": list(basket.item_ids),
            }
            _write_basket_payload(self._path, payload)
            backup_payload = self._backup_payload(payload)
            if normalized_recovered_from is not None and normalized_recovered_from != "seed":
                backup_payload["recovered_from"] = normalized_recovered_from
            backup_written = (
                refresh_backup
                or current_backup_payload is None
                or self._backup_needs_refresh(current_backup_payload, basket, payload)
            )
            if backup_written:
                backup_written = self._write_backup_payload(backup_payload)
            if not backup_written:
                # Seed keeps the latest canonical basket recoverable if backup
                # rotation cannot be completed after the recovery marker is
                # stripped from an otherwise canonical payload.
                self._write_seed(backup_payload)
            self._clear_recovery_artifacts(preserve_seed=not backup_written)
            return
        if (
            normalized_recovered_from is None
            and not preserve_primary_corrupt
            and not preserve_backup_corrupt
            and not preserve_seed_corrupt
            and (updated_at is None or self._payload_updated_at(current_payload) == updated_at)
            and self._is_canonical_primary_payload(current_payload, basket)
        ):
            # A canonical primary should not churn updated_at just to resync the
            # backup or seed recovery path.
            backup_payload = self._backup_payload(current_payload)
            backup_written = (
                refresh_backup
                or current_backup_payload is None
                or self._backup_needs_refresh(current_backup_payload, basket, current_payload)
            )
            if backup_written:
                backup_written = self._write_backup_payload(backup_payload)
            if not backup_written:
                # Seed keeps the latest canonical basket recoverable if backup
                # rotation cannot be completed after confirming the primary is
                # already canonical.
                self._write_seed(backup_payload)
            self._clear_recovery_artifacts(preserve_seed=not backup_written)
            return
        payload = {
            "schema_version": _SCHEMA_VERSION,
            "updated_at": updated_at or _now_iso(),
            "item_ids": list(basket.item_ids),
        }
        if normalized_recovered_from is not None:
            payload["recovered_from"] = normalized_recovered_from
        _write_basket_payload(self._path, payload)
        backup_payload = self._backup_payload(payload)
        if normalized_recovered_from is not None and normalized_recovered_from != "seed":
            backup_payload["recovered_from"] = normalized_recovered_from
        backup_written = (
            refresh_backup
            or current_backup_payload is None
            or self._backup_needs_refresh(current_backup_payload, basket, payload)
        )
        if backup_written:
            backup_written = self._write_backup_payload(backup_payload)
        if not backup_written:
            # Seed keeps the latest canonical basket recoverable if backup
            # rotation cannot be completed after the primary rewrite.
            self._write_seed(backup_payload)
        self._clear_recovery_artifacts(
            preserve_seed=not backup_written,
            preserve_primary_corrupt=preserve_primary_corrupt,
            preserve_backup_corrupt=preserve_backup_corrupt,
            preserve_seed_corrupt=preserve_seed_corrupt,
        )

    def clear(self) -> None:
        for path in (
            self._path,
            self._backup_path,
            self._seed_state_path(),
            self._tmp_path(),
            self._backup_tmp_path(),
            self._seed_tmp_path(),
            self._corrupt_path(),
            self._corrupt_path_for(self._tmp_path()),
            self._corrupt_path_for(self._backup_tmp_path()),
            self._corrupt_path_for(self._seed_tmp_path()),
        ):
            self._unlink_if_exists(path)
        self._clear_quarantine_file()

    def _quarantine_invalid_file(self) -> None:
        if not self._path.exists():
            return
        self._quarantine_path(self._path)

    def _quarantine_invalid_backup(self) -> None:
        if not self._backup_path.exists():
            return
        self._quarantine_path(self._backup_path)

    def _quarantine_invalid_seed(self) -> None:
        if not self._seed_state_path().exists():
            return
        self._quarantine_path(self._seed_state_path())

    def _quarantine_path(self, path: Path) -> None:
        corrupt = self._corrupt_path_for(path)
        self._unlink_if_exists(corrupt)
        try:
            path.replace(corrupt)
        except OSError:
            return

    def _clear_quarantine_file(
        self,
        preserve_temporary: bool = False,
        preserve_primary_corrupt: bool = False,
        preserve_backup_corrupt: bool = False,
        preserve_seed_corrupt: bool = False,
    ) -> None:
        if not preserve_primary_corrupt:
            self._unlink_if_exists(self._corrupt_path())
        if not preserve_backup_corrupt:
            self._unlink_if_exists(self._corrupt_path_for(self._backup_path))
        if not preserve_seed_corrupt:
            self._unlink_if_exists(self._corrupt_path_for(self._seed_state_path()))
        if not preserve_temporary:
            self._unlink_if_exists(self._corrupt_path_for(self._tmp_path()))
            self._unlink_if_exists(self._corrupt_path_for(self._backup_tmp_path()))
            self._unlink_if_exists(self._corrupt_path_for(self._seed_tmp_path()))

    def _clear_temporary_files(self) -> None:
        self._unlink_if_exists(self._tmp_path())
        self._unlink_if_exists(self._backup_tmp_path())
        self._unlink_if_exists(self._seed_tmp_path())

    def _clear_recovery_artifacts(
        self,
        preserve_seed: bool = False,
        preserve_primary_corrupt: bool = False,
        preserve_backup_corrupt: bool = False,
        preserve_seed_corrupt: bool = False,
    ) -> None:
        self._clear_quarantine_file(
            preserve_primary_corrupt=preserve_primary_corrupt,
            preserve_backup_corrupt=preserve_backup_corrupt,
            preserve_seed_corrupt=preserve_seed_corrupt,
        )
        self._clear_temporary_files()
        if not preserve_seed:
            self._unlink_if_exists(self._seed_state_path())

    def _corrupt_path_for(self, path: Path) -> Path:
        if path.name.endswith(".tmp"):
            return path.with_name(f"{path.name}.corrupt.json")
        if path.name.endswith(".json"):
            return path.with_name(path.name[:-5] + ".corrupt.json")
        return path.with_name(f"{path.name}.corrupt")

    def _discard_payload_source(self, recovered_source: str | None) -> None:
        if recovered_source == "tmp":
            self._unlink_if_exists(self._tmp_path())
        elif recovered_source == "backup_tmp":
            self._unlink_if_exists(self._backup_tmp_path())
        elif recovered_source == "backup":
            self._unlink_if_exists(self._backup_path)
        elif recovered_source == "seed_tmp":
            self._unlink_if_exists(self._seed_tmp_path())
        elif recovered_source == "seed":
            self._unlink_if_exists(self._seed_state_path())
        else:
            self._quarantine_invalid_file()

    def _load_payload(
        self,
        path: Path,
    ) -> tuple[dict[str, object] | list[object] | None, bool]:
        if not path.exists():
            return None, False
        try:
            payload = _load_json_payload(path)
        except (json.JSONDecodeError, OSError):
            if path == self._path:
                self._quarantine_invalid_file()
            elif path.suffix == ".tmp":
                self._quarantine_path(path)
            elif path == self._backup_path:
                self._quarantine_invalid_backup()
            elif path == self._seed_state_path():
                self._quarantine_invalid_seed()
            return None, True
        if not self._is_loadable_payload(payload):
            if path == self._path:
                self._quarantine_invalid_file()
            elif path.suffix == ".tmp":
                self._quarantine_path(path)
            elif path == self._backup_path:
                self._quarantine_invalid_backup()
            elif path == self._seed_state_path():
                self._quarantine_invalid_seed()
            return None, True
        return payload, False

    def _write_backup(self) -> bool:
        if not self._path.exists():
            return False
        if not self._is_valid_payload(self._path):
            return False
        payload = _load_json_payload(self._path)
        if not isinstance(payload, dict):
            return False
        return self._write_backup_payload(payload)

    def _write_backup_payload(self, payload: dict[str, object]) -> bool:
        canonical_payload = self._backup_payload(payload)
        try:
            _write_basket_payload(self._backup_path, canonical_payload)
        except OSError:
            return False
        return True

    def _backup_payload(self, payload: dict[str, object]) -> dict[str, object]:
        backup_payload: dict[str, object] = {
            "schema_version": self._parse_schema_version(payload) or _SCHEMA_VERSION,
            "item_ids": self._normalize_item_ids(self._parse_item_ids(payload.get("item_ids")) or []),
        }
        normalized_updated_at = self._parse_updated_at(payload.get("updated_at"))
        if normalized_updated_at is not None:
            backup_payload["updated_at"] = normalized_updated_at
        return backup_payload

    def _write_seed(self, payload: dict[str, object] | list[object]) -> None:
        seed = self._seed_state_path()
        try:
            _write_basket_payload(seed, payload)
        except OSError:
            return

    def _is_valid_payload(self, path: Path) -> bool:
        try:
            payload = _load_json_payload(path)
        except (json.JSONDecodeError, OSError):
            return False
        return self._is_supported_payload(payload)

    def _is_loadable_payload(self, payload: object) -> bool:
        # Optional metadata can be malformed without invalidating the recoverable basket.
        if isinstance(payload, list):
            return self._parse_item_ids(payload) is not None
        if not isinstance(payload, dict):
            return False
        if "item_ids" in payload and self._parse_item_ids(payload.get("item_ids")) is None:
            return False
        return True

    def _is_supported_payload(self, payload: object) -> bool:
        # Backup rotation stays strict so we do not preserve malformed metadata as canonical.
        if not self._is_loadable_payload(payload):
            return False
        if not isinstance(payload, dict):
            return True
        if self._parse_schema_version(payload) is None:
            return False
        if "recovered_from" in payload and self._parse_recovered_from(payload.get("recovered_from")) is None:
            return False
        if "updated_at" in payload and self._parse_updated_at(payload.get("updated_at")) is None:
            return False
        return True

    def _is_canonical_primary_payload(self, payload: object, basket: ContextBasket) -> bool:
        if not isinstance(payload, dict):
            return False
        if self._parse_schema_version(payload) != _SCHEMA_VERSION:
            return False
        if self._has_unknown_fields(payload):
            return False
        if "recovered_from" in payload:
            return False
        if "updated_at" not in payload:
            return False
        normalized_updated_at = self._parse_updated_at(payload.get("updated_at"))
        if normalized_updated_at is None or payload.get("updated_at") != normalized_updated_at:
            return False
        raw_item_ids = payload.get("item_ids")
        if not isinstance(raw_item_ids, list):
            return False
        parsed_item_ids = self._parse_item_ids(raw_item_ids)
        if parsed_item_ids is None:
            return False
        if raw_item_ids != parsed_item_ids:
            return False
        return parsed_item_ids == basket.item_ids

    def _payload_updated_at(self, payload: object) -> str | None:
        if not isinstance(payload, dict):
            return None
        return self._parse_updated_at(payload.get("updated_at"))

    def _recovery_marker_cleanup_timestamp(self, payload: object, basket: ContextBasket) -> str | None:
        if not isinstance(payload, dict):
            return None
        if "recovered_from" not in payload:
            return None
        if self._parse_schema_version(payload) != _SCHEMA_VERSION:
            return None
        if self._has_unknown_fields(payload):
            return None
        if "updated_at" not in payload:
            return None
        normalized_updated_at = self._parse_updated_at(payload.get("updated_at"))
        if normalized_updated_at is None or payload.get("updated_at") != normalized_updated_at:
            return None
        raw_item_ids = payload.get("item_ids")
        if not isinstance(raw_item_ids, list):
            return None
        parsed_item_ids = self._parse_item_ids(raw_item_ids)
        if parsed_item_ids is None:
            return None
        if raw_item_ids != parsed_item_ids:
            return None
        if parsed_item_ids != basket.item_ids:
            return None
        return normalized_updated_at

    def _parse_item_ids(self, value: object) -> list[str] | None:
        if isinstance(value, list):
            parsed: list[str] = []
            for raw in value:
                normalized = self._normalize_item_id(raw)
                if not normalized:
                    continue
                parsed.append(normalized)
            return parsed
        normalized = self._normalize_item_id(value)
        if normalized:
            return [normalized]
        if isinstance(value, str):
            return []
        return None

    def _normalize_item_id(self, item_id: object) -> str:
        if isinstance(item_id, str):
            return item_id.strip()
        if isinstance(item_id, bool):
            return ""
        if isinstance(item_id, int):
            return str(item_id).strip()
        if isinstance(item_id, float):
            if not math.isfinite(item_id):
                return ""
            return str(item_id).strip()
        return ""

    def _parse_schema_version(self, payload: dict[str, object]) -> int | None:
        if "schema_version" not in payload:
            return 0
        value = payload.get("schema_version")
        if isinstance(value, bool) or not isinstance(value, int):
            return None
        if value < 0 or value > _SCHEMA_VERSION:
            return None
        return value

    def _parse_recovered_from(self, value: object) -> str | None:
        if not isinstance(value, str):
            return None
        normalized = re.sub(r"[-\s]+", "_", value.strip().lower())
        if normalized in {"tmp", "backup", "seed"}:
            return normalized
        if normalized == "backup_tmp":
            return "backup"
        if normalized == "seed_tmp":
            return "seed"
        return None

    def _parse_updated_at(self, value: object) -> str | None:
        if not isinstance(value, str):
            return None
        candidate = value.strip()
        if not candidate:
            return None
        try:
            parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC).isoformat()

    def _backup_needs_refresh(
        self,
        payload: dict[str, object] | list[object] | None,
        basket: ContextBasket,
        primary_payload: dict[str, object] | None = None,
    ) -> bool:
        if payload is None:
            return False
        if isinstance(payload, list):
            return True
        if self._parse_schema_version(payload) != _SCHEMA_VERSION:
            return True
        if "item_ids" not in payload:
            return True
        raw_item_ids = payload.get("item_ids")
        if not isinstance(raw_item_ids, list):
            return True
        parsed_items = self._parse_item_ids(raw_item_ids)
        if parsed_items is None:
            return True
        if parsed_items != raw_item_ids:
            return True
        if parsed_items != self._normalize_item_ids(parsed_items):
            return True
        if self._has_dropped_item_ids(raw_item_ids):
            return True
        if self._has_unknown_fields(payload):
            return True
        if "updated_at" not in payload:
            return True
        if "recovered_from" in payload:
            return True
        if self._normalize_item_ids(parsed_items) != basket.item_ids:
            return True
        normalized_updated_at = self._parse_updated_at(payload.get("updated_at"))
        if normalized_updated_at is None:
            return True
        if payload.get("updated_at") != normalized_updated_at:
            return True
        if primary_payload is not None:
            primary_updated_at = self._parse_updated_at(primary_payload.get("updated_at"))
            if primary_updated_at is not None and normalized_updated_at != primary_updated_at:
                return True
        return False

    def _backup_needs_audit_quarantine(self, payload: dict[str, object] | list[object] | None) -> bool:
        if payload is None:
            return False
        if isinstance(payload, list):
            return self._legacy_list_payload_has_dropped_item_ids(payload)
        if "updated_at" not in payload:
            return True
        if "item_ids" not in payload:
            return True
        raw_item_ids = payload.get("item_ids")
        if isinstance(raw_item_ids, list) and self._legacy_list_payload_has_dropped_item_ids(raw_item_ids):
            return True
        return not self._is_supported_payload(payload)

    def _normalize_item_ids(self, item_ids: list[str]) -> list[str]:
        return ContextBasket(item_ids=list(item_ids)).item_ids

    def _has_unknown_fields(self, payload: dict[str, object]) -> bool:
        return any(key not in _CANONICAL_DICT_KEYS for key in payload)

    def _has_dropped_item_ids(self, item_ids: object) -> bool:
        if not isinstance(item_ids, list):
            return True
        return any(not self._normalize_item_id(item_id) for item_id in item_ids)

    def _legacy_list_payload_has_dropped_item_ids(self, payload: object) -> bool:
        if not isinstance(payload, list):
            return False
        parsed_item_ids = self._parse_item_ids(payload)
        if parsed_item_ids is None:
            return False
        return len(parsed_item_ids) < len(payload)

    def _quarantine_unrecoverable_list_payload(self, path: Path, payload: object) -> bool:
        if path not in {self._backup_path, self._seed_state_path()}:
            return False
        if not isinstance(payload, list):
            return False
        if not payload:
            # An explicit empty legacy list is a recoverable empty basket, not
            # malformed state that should leave a stale quarantine trail.
            return False
        if self._has_recovery_payload_items(payload):
            return False
        self._quarantine_path(path)
        return True

    def _recovery_marker(self, *, primary_unavailable: bool, recovered_source: str | None) -> str | None:
        if not primary_unavailable:
            return None
        if recovered_source == "backup_tmp":
            return "backup"
        if recovered_source == "seed_tmp":
            return "seed"
        return self._parse_recovered_from(recovered_source)

    def _recovery_payload_updated_at(self, payload: dict[str, object] | list[object]) -> str | None:
        if isinstance(payload, dict):
            return self._parse_updated_at(payload.get("updated_at"))
        return None

    def _recovery_candidate_key(self, payload: dict[str, object] | list[object], position: int) -> tuple[bool, str, int]:
        updated_at = self._recovery_payload_updated_at(payload)
        return updated_at is not None, updated_at or "", -position

    def _prefer_recovery_payload(
        self,
        tmp_payload: dict[str, object] | list[object] | None,
        backup_tmp_payload: dict[str, object] | list[object] | None,
        backup_payload: dict[str, object] | list[object] | None,
        seed_tmp_payload: dict[str, object] | list[object] | None,
        seed_payload: dict[str, object] | list[object] | None,
    ) -> tuple[dict[str, object] | list[object] | None, str | None]:
        best_candidate: tuple[dict[str, object] | list[object] | None, str | None] = (None, None)
        best_candidate_key: tuple[bool, str, int] | None = None
        fallback_candidate: tuple[dict[str, object] | list[object] | None, str | None] = (None, None)
        fallback_candidate_key: tuple[bool, str, int] | None = None
        for position, (candidate, recovered_source) in enumerate(
            (
                (backup_tmp_payload, "backup_tmp"),
                (backup_payload, "backup"),
                (seed_tmp_payload, "seed_tmp"),
                (seed_payload, "seed"),
                (tmp_payload, "tmp"),
            )
        ):
            if candidate is None:
                continue
            if self._has_recovery_payload_items(candidate):
                candidate_key = self._recovery_candidate_key(candidate, position)
                if best_candidate_key is None or candidate_key > best_candidate_key:
                    best_candidate = (candidate, recovered_source)
                    best_candidate_key = candidate_key
                continue
            # Only explicit empty payloads should serve as a fallback recovery
            # source. Dicts missing the core item_ids key are malformed, not
            # recoverable state.
            if self._has_explicit_empty_recovery_payload(candidate):
                candidate_key = self._recovery_candidate_key(candidate, position)
                if fallback_candidate_key is None or candidate_key > fallback_candidate_key:
                    fallback_candidate = (candidate, recovered_source)
                    fallback_candidate_key = candidate_key
        if best_candidate != (None, None):
            return best_candidate
        return fallback_candidate

    def _has_recovery_payload_items(self, payload: dict[str, object] | list[object]) -> bool:
        if isinstance(payload, list):
            return bool(self._parse_item_ids(payload))
        item_ids = self._parse_item_ids(payload.get("item_ids")) if "item_ids" in payload else None
        return bool(item_ids)

    def _is_empty_recovery_payload(self, payload: dict[str, object] | list[object] | None) -> bool:
        return payload is not None and not self._has_recovery_payload_items(payload)

    def _has_explicit_empty_recovery_payload(self, payload: dict[str, object] | list[object]) -> bool:
        if isinstance(payload, list):
            return not payload
        if "item_ids" not in payload:
            return False
        raw_item_ids = payload.get("item_ids")
        # Only a truly empty list counts as an explicit empty recovery source.
        # Lists that only become empty after dropping malformed entries stay
        # quarantined instead of being promoted as recoverable state.
        return isinstance(raw_item_ids, list) and not raw_item_ids

    def _primary_item_ids_need_recovery(self, payload: dict[str, object] | list[object] | None) -> bool:
        if isinstance(payload, dict):
            if "item_ids" not in payload:
                return True
            raw_item_ids = payload.get("item_ids")
            parsed_item_ids = self._parse_item_ids(raw_item_ids)
            if parsed_item_ids is None:
                return True
            return not parsed_item_ids and self._has_dropped_item_ids(raw_item_ids)
        if isinstance(payload, list):
            return True
        return False

    def _unlink_if_exists(self, path: Path) -> None:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            return
# END MATERIALIZED FROZEN BASELINE: src/qual/context/store.py @ 47cda4df831ac41867a8792f40d720e0cb109514

_original_context_basket_store_init = ContextBasketStore.__init__


def _context_basket_store_init(self: ContextBasketStore, root_dir: Path | str) -> None:
    root_dir = Path(root_dir)
    if _state_root_uses_nested_symlink_alias(root_dir):
        raise ValueError(f"context basket state root uses a symlink alias: {root_dir!r}")
    root_dir.mkdir(parents=True, exist_ok=True)
    _original_context_basket_store_init(self, root_dir)


ContextBasketStore.__init__ = _context_basket_store_init


def _basket_corrupt_path_for(path: Path) -> Path:
    # Route through the shared corrupt-path namer rather than a basket-local copy
    # of the suffix logic. The legacy ``{stem}.tmp.json`` case -- which must keep
    # its full name so a non-file quarantine lands in the legacy temp's own
    # corrupt family that ``ContextBasketStore.clear`` sweeps, instead of
    # collapsing onto the canonical ``.tmp`` family -- now lives in the shared
    # namer ahead of its ``.json``-strip case, so a blocking alias quarantines
    # under the identical name whether the basket or a sibling store handles it.
    return _corrupt_artifact_path_for(path)


def _quarantine_blocking_basket_artifact(path: Path) -> None:
    # The blocking-alias and stale-temp guards are store-agnostic now that the
    # corrupt-path namer is shared, so both delegate to the shared helpers and
    # keep these thin wrappers only as the basket store's named entry points.
    _quarantine_blocking_corrupt_artifact(path)


def _quarantine_stale_basket_temp_artifact(path: Path) -> None:
    _quarantine_stale_corrupt_temp_artifact(path)


def _context_basket_legacy_tmp_paths(store: ContextBasketStore) -> tuple[Path, Path, Path]:
    return (
        _legacy_json_temp_path(store._path),
        _legacy_json_temp_path(store._backup_path),
        _legacy_json_temp_path(store._seed_path),
    )


def _unlink_basket_temp_path(path: Path) -> None:
    try:
        if path.is_symlink():
            _quarantine_blocking_basket_artifact(path)
        elif path.exists() and not path.is_file():
            _quarantine_blocking_basket_artifact(path)
        else:
            path.unlink(missing_ok=True)
    except OSError:
        return


def _staged_basket_write(path: Path, content: str | bytes, *, encoding: str | None) -> None:
    # Named per-store wrapper around the shared
    # :func:`_corrupt_artifacts.staged_atomic_write` body: the basket seams the
    # hardening tests patch in isolation (blocking/stale-temp quarantine, the
    # content and parent fsync, the torn-write temp cleanup) are passed in by name
    # so each resolves the patched module global at call time, while the
    # staged-temp + flush + atomic-replace contract stays one audited definition.
    _staged_atomic_write(
        path,
        content,
        encoding=encoding,
        quarantine_blocking=_quarantine_blocking_basket_artifact,
        quarantine_stale_temp=_quarantine_stale_basket_temp_artifact,
        fsync_content=_fsync_basket_path,
        fsync_parent=_fsync_basket_parent,
        remove_temp=_unlink_basket_temp_path,
        symlink_label="context basket",
    )


def _write_basket_payload(path: Path, payload: object) -> None:
    _staged_basket_write(path, _canonical_json_dumps(payload), encoding="utf-8")


def _write_basket_bytes(path: Path, data: bytes) -> None:
    """Write raw basket artifact bytes through the content-flush seam.

    Forensic corrupt-snapshot restores republish previously quarantined bytes
    verbatim rather than a re-encoded payload, so they cannot share
    :func:`_write_basket_payload`. They must still land atomically with the same
    staged-temp + ``_fsync_basket_path`` content flush + atomic replace + parent
    flush that canonical basket writes use: a raw ``write_bytes`` here would leave
    a torn restore half-written, and that partial artifact would itself
    masquerade as a valid forensic snapshot, defeating the snapshot's audit
    purpose and leaving non-deterministic recovery state for the engine loop. The
    ``encoding=None`` path opens the staged temp in binary mode so the bytes are
    republished without re-encoding.
    """

    _staged_basket_write(path, data, encoding=None)

_BASKET_RAW_ITEM_ID_SNAPSHOTS: weakref.WeakKeyDictionary[object, list[object]] = weakref.WeakKeyDictionary()
_BASKET_RAW_ITEM_ID_SNAPSHOT_IDS: OrderedDict[int, tuple[object, list[object]]] = OrderedDict()
_BASKET_RAW_ITEM_ID_CACHE_LIMIT = 1024


def _load_json_payload(path: Path) -> object:
    if path.is_symlink():
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _sync_basket_source_payload_wrapper(
    source_payload: object | None,
    path: Path,
    primary_payload: dict[str, object] | None,
    *,
    preserve_equivalent_raw_wrapper: bool = False,
) -> None:
    """Reconcile a caller-owned basket wrapper with the latest payload.

    When recovery rewrites the basket primary before an auxiliary source path
    is removed or quarantined, the original wrapper still needs to be updated
    from the rewritten primary payload. Falling back to the canonical primary
    keeps those wrappers aligned instead of leaving them stale.
    """

    if not isinstance(source_payload, AbstractMapping) or type(source_payload) is dict:
        return
    try:
        final_payload = _load_json_payload(path)
    except Exception:
        final_payload = None
    if isinstance(final_payload, AbstractMapping) and type(final_payload) is not dict:
        final_payload = _payload_as_plain_dict(final_payload)
    if final_payload is None and isinstance(primary_payload, dict):
        final_payload = dict(primary_payload)
    if (
        preserve_equivalent_raw_wrapper
        and _basket_payload_missing_item_ids_is_recoverable(source_payload)
        and isinstance(final_payload, dict)
        and "item_ids" in final_payload
    ):
        return
    if isinstance(final_payload, dict):
        _sync_basket_payload_mapping_wrapper(
            source_payload,
            final_payload,
            preserve_equivalent_raw_wrapper=preserve_equivalent_raw_wrapper,
        )


def _materialize_context_set_record_item_ids(raw_record: object) -> object:
    from . import set_store as _set_store

    return _set_store._materialize_context_set_record_item_ids(raw_record)


def _materialize_context_set_payload_records(raw_context_sets: object) -> object:
    from . import set_store as _set_store

    return _set_store._materialize_context_set_payload_records(raw_context_sets)


def _materialize_context_set_payload(payload: object) -> object:
    from . import set_store as _set_store

    return _set_store._materialize_context_set_payload(payload)


def _now_iso() -> str:
    # Delegate to the single shared ``utc_now_iso`` so the document store stamps
    # a fresh ``updated_at`` identically to the audit log, session, vault, and
    # context-set stores. The body that lived here was byte-identical to that
    # helper -- a second, independent definition of "current UTC now" in this
    # module, exactly the divergence risk the recovery consolidation has been
    # retiring (mirroring the ``_parse_updated_at`` -> ``parse_recovered_timestamp``
    # delegation). This stays the patch seam the recovery suites rebind, so the
    # consolidation holds even though tests still swap this name out wholesale.
    return utc_now_iso()


def _parse_updated_at(value: object) -> str | None:
    # Delegate to the single shared recovery parser so the document store
    # recovers a timestamp identically to the session store and any other
    # reader. The body that lived here was byte-identical to the helper; sharing
    # it removes a divergence risk like the one that once dropped folding from
    # the basket store's in-class copy.
    return parse_recovered_timestamp(value)


def _new_context_set_store() -> object:
    from .set_store import ContextSetStore

    store = object.__new__(ContextSetStore)
    dummy_root = Path("/tmp") / f".qual-context-set-store-{os.getpid()}-{id(store)}"
    store._path = dummy_root.with_suffix(".json")
    store._backup_path = dummy_root.with_suffix(".bak.json")
    store._seed_path = dummy_root.with_suffix(".seed.json")
    return store


def _is_context_set_primary_path(path: Path) -> bool:
    return path.name.startswith("context_sets") or path.name.startswith("context_set")


def _is_context_set_auxiliary_path(path: Path) -> bool:
    return (
        (path.name.startswith("context_sets") or path.name.startswith("context_set"))
        and (path.name.endswith(".bak.json") or path.name.endswith(".seed.json"))
    )


def _corrupt_path_for(path: Path) -> Path:
    return path.with_suffix(".corrupt.json")


def _quarantine_path(path: Path) -> None:
    _quarantine_corrupt_artifact(Path(path), _corrupt_path_for(Path(path)))


def _remove_corrupt_artifact(path: Path) -> bool:
    try:
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            os.remove(str(path))
        return True
    except Exception:
        return False


def _prune_empty_parent_dirs(start: Path, stop: Path) -> None:
    current = start
    while current != stop and current != current.parent:
        try:
            if not current.exists():
                current = current.parent
                continue
            if any(current.iterdir()):
                break
            current.rmdir()
        except Exception:
            break
        current = current.parent


def _is_under_removed_directory(path: Path, removed_dirs: list[Path]) -> bool:
    return any(path == removed_dir or removed_dir in path.parents for removed_dir in removed_dirs)


def _basket_raw_item_ids_snapshot(raw_item_ids: object) -> list[object] | None:
    if isinstance(raw_item_ids, list):
        return raw_item_ids
    if isinstance(raw_item_ids, tuple):
        return list(raw_item_ids)
    if isinstance(raw_item_ids, (AbstractKeysView, AbstractItemsView, AbstractValuesView)):
        # Mapping views are iterable but they expose dictionary structure, not
        # a durable basket payload. Treat them as malformed so keys are never
        # persisted as recoverable item ids.
        return None
    if isinstance(raw_item_ids, AbstractSet):
        try:
            sorted_values = sorted(
                raw_item_ids,
                key=lambda value: (ContextBasket._normalize_item_id(value), type(value).__name__, _safe_repr(value)),
            )
        except Exception:
            return None
        return sorted_values

    if not ContextBasket._is_one_shot_iterator(raw_item_ids):
        raw_values = ContextBasket._ordered_item_id_values(raw_item_ids)
        if raw_values is None:
            return None
        if not raw_values and not isinstance(raw_item_ids, list):
            return None
        return list(raw_values)
    try:
        cached_item_ids = _BASKET_RAW_ITEM_ID_SNAPSHOTS[raw_item_ids]
    except (KeyError, TypeError):
        payload_id = id(raw_item_ids)
        cached_entry = _BASKET_RAW_ITEM_ID_SNAPSHOT_IDS.get(payload_id)
        if cached_entry is not None:
            cached_payload, cached_item_ids = cached_entry
            if cached_payload is raw_item_ids:
                _BASKET_RAW_ITEM_ID_SNAPSHOT_IDS.move_to_end(payload_id)
                return cached_item_ids
        raw_values = ContextBasket._ordered_item_id_values(raw_item_ids)
        if raw_values is None or not raw_values:
            return None
        cached_item_ids = list(raw_values)
        try:
            _BASKET_RAW_ITEM_ID_SNAPSHOTS[raw_item_ids] = cached_item_ids
        except TypeError:
            _BASKET_RAW_ITEM_ID_SNAPSHOT_IDS[payload_id] = (raw_item_ids, cached_item_ids)
            _BASKET_RAW_ITEM_ID_SNAPSHOT_IDS.move_to_end(payload_id)
            if len(_BASKET_RAW_ITEM_ID_SNAPSHOT_IDS) > _BASKET_RAW_ITEM_ID_CACHE_LIMIT:
                _BASKET_RAW_ITEM_ID_SNAPSHOT_IDS.popitem(last=False)
    return cached_item_ids


def _snapshot_basket_item_ids(payload: object) -> list[str] | None:
    if isinstance(payload, tuple) and not payload:
        return []
    if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return None
    raw_item_ids = payload.get("item_ids") if isinstance(payload, dict) and "item_ids" in payload else payload
    if isinstance(payload, dict) and isinstance(raw_item_ids, tuple) and not raw_item_ids:
        return None
    raw_values = _basket_raw_item_ids_snapshot(raw_item_ids)
    if raw_values is None:
        return None
    normalized: list[str] = []
    for raw_item_id in raw_values:
        item_id = ContextBasket._normalize_item_id(raw_item_id)
        if not item_id:
            continue
        normalized.append(item_id)
    return normalized


def _snapshot_basket_payload(payload: object) -> object | None:
    if isinstance(payload, tuple) and not payload:
        return []
    if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return None
    if isinstance(payload, dict):
        if "item_ids" not in payload:
            return payload
        raw_values = _basket_raw_item_ids_snapshot(payload.get("item_ids"))
        if raw_values is None:
            return None
        snapshot = dict(payload)
        snapshot["item_ids"] = list(raw_values)
        return snapshot
    raw_values = _basket_raw_item_ids_snapshot(payload)
    if raw_values is None:
        return None
    return list(raw_values)


def _basket_schema_version_code_unsupported(schema_version: object) -> bool:
    """Return ``True`` when a stamped basket ``schema_version`` is not a recognized code.

    Recognized codes are the integers ``0`` (legacy/unstamped baskets the load
    path rewrites canonically) through ``_SCHEMA_VERSION``. ``bool`` is rejected
    explicitly so ``True``/``False`` never masquerade as the integer ``1``/``0``
    codes. Mirrors ``set_store._schema_version_code_unsupported`` so the basket
    recovery readers share one definition of "which codes are recoverable"
    instead of each re-deriving the range guard.
    """

    return (
        isinstance(schema_version, bool)
        or not isinstance(schema_version, int)
        or schema_version < 0
        or schema_version > _SCHEMA_VERSION
    )


def _basket_payload_needs_audit_quarantine(payload: object) -> bool:
    if isinstance(payload, UserList):
        payload = list(payload)
    if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return True

    def _item_ids_need_audit_quarantine(raw_item_ids: object) -> bool:
        if isinstance(raw_item_ids, tuple) and not raw_item_ids:
            return False
        raw_values = _basket_raw_item_ids_snapshot(raw_item_ids)
        if raw_values is None:
            if isinstance(raw_item_ids, str):
                return not raw_item_ids.strip()
            return not bool(ContextBasket._normalize_item_id(raw_item_ids))
        if not raw_values:
            return not isinstance(raw_item_ids, (list, AbstractSet))
        # Blank-only lists still represent malformed basket state: the load
        # path quarantines them instead of silently rewriting them into an
        # empty basket, so the validator should make the same call.
        return any(not ContextBasket._normalize_item_id(raw_item_id) for raw_item_id in raw_values)

    if isinstance(payload, dict):
        if "recovered_from" in payload:
            return True
        if any(key not in {"schema_version", "updated_at", "item_ids", "recovered_from"} for key in payload):
            return True
        if "item_ids" not in payload:
            return not _basket_payload_missing_item_ids_is_recoverable(payload)
        raw_item_ids = payload.get("item_ids")
        if _item_ids_need_audit_quarantine(raw_item_ids):
            return True
        schema_version = payload.get("schema_version")
        if "schema_version" in payload and _basket_schema_version_code_unsupported(schema_version):
            return True
        if "updated_at" in payload:
            raw_updated_at = payload.get("updated_at")
            if raw_updated_at is not None and not isinstance(raw_updated_at, str):
                return True
            if (
                isinstance(raw_updated_at, str)
                and raw_updated_at.strip()
                and _parse_updated_at(raw_updated_at) is None
                and not _basket_payload_is_rewriteable_without_updated_at(payload)
            ):
                return True
        return False
    if isinstance(payload, list):
        return _item_ids_need_audit_quarantine(payload)
    return True


def _basket_payload_is_rewriteable_without_updated_at(payload: object) -> bool:
    if _basket_payload_missing_item_ids_is_recoverable(payload) or _basket_payload_empty_envelope_is_recoverable(
        payload,
    ):
        return True
    # A payload with a well-formed, already-normalized item_ids list can be
    # rewritten with a fresh timestamp when the existing updated_at is unparseable.
    # Items must be non-empty strings with no leading/trailing whitespace so that
    # the rewrit does not silently discard or alter any item identifiers.
    if isinstance(payload, dict) and isinstance(payload.get("item_ids"), list):
        item_ids = payload["item_ids"]
        if all(
            isinstance(item, str)
            and item
            and item == ContextBasket._normalize_item_id(item)
            for item in item_ids
        ):
            return True
    return False


def _basket_payload_missing_item_ids_is_recoverable(payload: object) -> bool:
    if isinstance(payload, UserList):
        payload = list(payload)
    if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return False
    if not isinstance(payload, dict):
        return False
    if "item_ids" in payload or "recovered_from" in payload:
        return False
    if any(key not in {"schema_version", "updated_at"} for key in payload):
        return False
    schema_version = payload.get("schema_version")
    if schema_version is None:
        # Missing ``item_ids`` is recoverable even when the envelope no longer
        # carries a schema version. The load path will rewrite the canonical
        # empty basket deterministically, so a missing basket should not be
        # treated as corrupt just because the timestamp metadata is also
        # incomplete.
        return True
    if _basket_schema_version_code_unsupported(schema_version):
        return False
    return True


def _basket_payload_empty_envelope_is_recoverable(payload: object) -> bool:
    """Return ``True`` when an empty basket envelope can be rewritten canonically."""

    if isinstance(payload, UserList):
        payload = list(payload)
    if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return False
    if not isinstance(payload, dict):
        return False
    if "recovered_from" in payload:
        return False
    if any(key not in {"schema_version", "updated_at", "item_ids", "recovered_from"} for key in payload):
        return False
    schema_version = payload.get("schema_version")
    if schema_version is not None and _basket_schema_version_code_unsupported(schema_version):
        return False
    if "item_ids" not in payload:
        return _basket_payload_missing_item_ids_is_recoverable(payload)
    raw_item_ids = payload.get("item_ids")
    raw_values = _basket_raw_item_ids_snapshot(raw_item_ids)
    if raw_values is None or raw_values:
        return False
    return isinstance(raw_item_ids, (list, tuple, UserList, AbstractSet))


def _basket_payload_missing_schema_version_is_recoverable(payload: object) -> bool:
    if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return False
    return isinstance(payload, dict) and "schema_version" not in payload and not _basket_payload_needs_audit_quarantine(payload)


def _backup_payload_needs_audit_quarantine(payload: object) -> bool:
    if payload is None:
        return False
    if isinstance(payload, UserList):
        payload = list(payload)
    if isinstance(payload, list):
        if not payload:
            # Empty legacy backups are recoverable state, not malformed state.
            return False
        return True
    if not isinstance(payload, dict):
        return True
    if not _basket_payload_schema_version_is_canonical(payload):
        return True
    if "item_ids" not in payload:
        return not _basket_payload_missing_item_ids_is_recoverable(payload)
    raw_item_ids = payload.get("item_ids")
    if _record_item_ids_need_audit_quarantine(raw_item_ids):
        return True
    # Clean backup payloads that only lack ``updated_at`` are still
    # recoverable. Likewise, item ids that only need normalization should be
    # preserved so the load path can rewrite them canonically without creating
    # an unnecessary quarantine artifact. Malformed timestamps, by contrast,
    # should be quarantined so the rewrite path does not preserve a broken
    # timestamp string.
    raw_updated_at = payload.get("updated_at")
    if (
        "updated_at" in payload
        and raw_updated_at is not None
        and not (isinstance(raw_updated_at, str) and not raw_updated_at.strip())
        and _normalize_updated_at(raw_updated_at) is None
        and not _basket_payload_is_rewriteable_without_updated_at(payload)
    ):
        return True
    if "recovered_from" in payload:
        return True
    if any(key not in {"schema_version", "updated_at", "item_ids", "recovered_from"} for key in payload):
        return True
    return False


def _context_set_payload_as_list(payload: object) -> list[object] | None:
    from . import set_store as _set_store

    original_payload = payload if isinstance(payload, AbstractMapping) and type(payload) is not dict else None
    if isinstance(payload, (AbstractKeysView, AbstractItemsView, AbstractValuesView)):
        return None
    if original_payload is not None:
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return None
    if isinstance(payload, dict) and "context_sets" in payload:
        raw_context_sets = payload.get("context_sets")
        if isinstance(raw_context_sets, (AbstractKeysView, AbstractItemsView, AbstractValuesView)):
            return None
        materialized = _set_store._materialize_context_set_payload_records(payload.get("context_sets"))
        if isinstance(materialized, dict):
            materialized = [materialized]
    else:
        materialized = _set_store._materialize_context_set_payload_records(payload)
        if isinstance(materialized, dict):
            materialized = [materialized]
    if isinstance(materialized, list) and any(record is None for record in materialized):
        return None
    if materialized is _set_store._EMPTY_CONTEXT_SETS_ITERABLE:
        return None
    if isinstance(payload, dict) and "context_sets" in payload and isinstance(materialized, list):
        payload["context_sets"] = materialized
        if original_payload is not None:
            try:
                if original_payload == payload:
                    return materialized
                original_payload.clear()
                original_payload.update(payload)
            except Exception:
                pass
    return materialized if isinstance(materialized, list) else None


def _basket_family_payload_looks_like_context_set_records(payload: object) -> bool:
    materialized_context_sets = _context_set_payload_as_list(payload)
    if not materialized_context_sets:
        return False
    return all(isinstance(record, dict) and "context_set_id" in record for record in materialized_context_sets)


def _context_set_trim_materialized_item_ids_in_place(payload: object) -> object:
    from . import set_store as _set_store

    if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return payload
    if isinstance(payload, dict):
        raw_context_sets = payload.get("context_sets")
    else:
        raw_context_sets = payload
    if isinstance(raw_context_sets, dict):
        raw_context_sets = [raw_context_sets]
    if not isinstance(raw_context_sets, list):
        return payload
    for index, raw_record in enumerate(raw_context_sets):
        mapped_record = _set_store._context_set_record_mapping(raw_record)
        if mapped_record is not None:
            raw_record = mapped_record
            raw_context_sets[index] = raw_record
        if not isinstance(raw_record, dict) or "item_ids" not in raw_record:
            continue
        raw_item_ids = raw_record.get("item_ids")
        raw_values = _set_store._ordered_item_id_values(raw_item_ids)
        if raw_values is None:
            if isinstance(raw_item_ids, str):
                raw_record["item_ids"] = raw_item_ids.strip()
            continue
        trimmed_values: list[object] = []
        for raw_item_id in raw_values:
            if isinstance(raw_item_id, str):
                trimmed_values.append(raw_item_id.strip())
            else:
                trimmed_values.append(raw_item_id)
        if not isinstance(raw_item_ids, list) or raw_item_ids != trimmed_values:
            raw_record["item_ids"] = trimmed_values
    return payload


def _context_set_normalize_records_in_place(
    payload: object,
    records: list[object],
    parsed_records: list[object],
) -> None:
    from . import set_store as _set_store

    for index, (raw_record, parsed_record) in enumerate(zip(records, parsed_records)):
        mapped_record = _set_store._context_set_record_mapping(raw_record)
        if mapped_record is not None:
            raw_record = mapped_record
            records[index] = raw_record
        if not isinstance(raw_record, dict):
            continue
        raw_record.clear()
        raw_record.update(asdict(parsed_record))


def _context_set_payload_needs_audit_quarantine(
    path: Path | str,
    payload: object,
    is_auxiliary_path: bool = False,
) -> bool:
    from . import set_store as _set_store

    auxiliary_path = is_auxiliary_path or _is_context_set_auxiliary_path(Path(path))
    working_payload = dict(payload) if isinstance(payload, AbstractMapping) else payload
    original_payload = payload if isinstance(payload, AbstractMapping) else None
    # Inspect a working copy before materialization can collapse empty
    # non-list iterables into canonical empty lists on the caller's payload.
    if _set_store._payload_has_empty_non_list_context_set_item_ids(working_payload):
        return True
    store = _new_context_set_store()
    materialized_payload = working_payload
    if isinstance(working_payload, dict):
        materialized_payload = _set_store._materialize_context_set_payload(working_payload)
    else:
        materialized_list = _context_set_payload_as_list(working_payload)
        if materialized_list is None:
            return True
        materialized_payload = materialized_list
    if not auxiliary_path:
        materialized_payload = _context_set_trim_materialized_item_ids_in_place(materialized_payload)
    if (
        not (is_auxiliary_path or _is_context_set_auxiliary_path(Path(path)))
        and isinstance(materialized_payload, dict)
        and _set_store._payload_has_blank_scalar_context_set_item_ids(materialized_payload)
    ):
        return True
    auxiliary_path = is_auxiliary_path or _is_context_set_auxiliary_path(Path(path))
    if auxiliary_path:
        needs_quarantine = not _context_set_auxiliary_payload_is_recoverable_without_updated_at(materialized_payload)
        if not needs_quarantine and original_payload is not None and working_payload is not original_payload:
            original_payload.clear()
            original_payload.update(working_payload)
        return needs_quarantine
    if not isinstance(materialized_payload, (dict, list)):
        return True
    needs_quarantine = _set_store.ContextSetStore._primary_context_sets_need_audit_quarantine(store, materialized_payload)
    if not needs_quarantine and original_payload is not None and working_payload is not original_payload:
        original_payload.clear()
        original_payload.update(working_payload)
    return needs_quarantine


def _context_set_payload_can_recover_missing_updated_at(payload: object, store: object) -> bool:
    return _context_set_auxiliary_payload_is_recoverable_without_updated_at(payload)


def _context_set_auxiliary_payload_is_recoverable_without_updated_at(payload: object) -> bool:
    from . import set_store as _set_store

    store = _new_context_set_store()
    working_payload = dict(payload) if isinstance(payload, AbstractMapping) else payload
    original_payload = payload if isinstance(payload, AbstractMapping) else None
    if _set_store._payload_has_empty_non_list_context_set_item_ids(working_payload):
        return False
    if _set_store._payload_has_explicit_null_context_set_timestamps(working_payload):
        return False
    if isinstance(working_payload, dict) and "context_sets" in working_payload:
        raw_context_sets = working_payload.get("context_sets")
        if _set_store._materialize_context_set_payload_records(raw_context_sets) is _set_store._EMPTY_CONTEXT_SETS_ITERABLE:
            # Empty one-shot ``context_sets`` iterables are not durable
            # recovery sources. Treat them the same way the load path does so
            # preflight quarantine and load-time recovery stay aligned.
            return False
    materialized = _set_store._materialize_context_set_payload(working_payload)
    recoverable = False
    if isinstance(materialized, dict):
        if "context_sets" not in materialized:
            return _set_store._primary_context_sets_empty_envelope_is_recoverable(materialized)
        if _set_store._dict_payload_has_recoverable_blank_item_ids(store, materialized):
            recoverable = True
        elif _set_store._dict_payload_missing_schema_version_is_recoverable(store, materialized):
            recoverable = True
        elif _set_store._dict_payload_has_recoverable_malformed_updated_at(store, materialized):
            recoverable = True
        elif _set_store._dict_payload_single_record_missing_updated_at_is_recoverable(store, materialized):
            recoverable = True
        else:
            recoverable = not _set_store._dict_payload_needs_audit_quarantine(store, materialized)
    elif isinstance(materialized, list):
        if _set_store._list_payload_has_recoverable_blank_item_ids(store, materialized):
            recoverable = True
        else:
            recoverable = (
                not _set_store._list_payload_needs_audit_quarantine(store, materialized)
                and not _set_store._list_payload_records_need_audit_quarantine(store, materialized)
            )
    else:
        recoverable = False
    if recoverable and original_payload is not None and working_payload is not original_payload:
        try:
            original_payload.clear()
            original_payload.update(working_payload)
        except Exception:
            pass
    return recoverable


def _context_set_auxiliary_payload_is_recoverable_without_store(payload: object) -> bool:
    return _context_set_auxiliary_payload_is_recoverable_without_updated_at(payload)


def _context_set_single_record_payload_is_recoverable_with_updated_at(payload: object) -> bool:
    return _context_set_auxiliary_payload_is_recoverable_without_updated_at(payload)


def _context_set_single_record_payload_is_recoverable_without_updated_at(payload: object) -> bool:
    return _context_set_auxiliary_payload_is_recoverable_without_updated_at(payload)


def _context_set_primary_single_record_payload_needs_audit_quarantine_without_store(payload: object) -> bool:
    needs_quarantine = _context_set_payload_needs_audit_quarantine(Path("context_sets.json"), payload)
    if needs_quarantine:
        return True

    from . import set_store as _set_store

    store = _new_context_set_store()
    materialized_payload = payload
    if isinstance(payload, dict):
        materialized_payload = _set_store._materialize_context_set_payload(payload)
    else:
        materialized_list = _context_set_payload_as_list(payload)
        if materialized_list is None:
            return False
        materialized_payload = materialized_list

    if isinstance(materialized_payload, dict):
        raw_context_sets = materialized_payload.get("context_sets")
    else:
        raw_context_sets = materialized_payload

    if isinstance(raw_context_sets, dict):
        raw_records: list[object] = [raw_context_sets]
    elif isinstance(raw_context_sets, list):
        raw_records = raw_context_sets
    else:
        return False

    parsed_records = _set_store._materialize_context_set_records(store, materialized_payload)
    if parsed_records is not None and len(raw_records) == len(parsed_records):
        _context_set_normalize_records_in_place(materialized_payload, raw_records, parsed_records)
    return False


def _context_set_primary_payload_is_recoverable_with_timestamp_rewrite_without_store(payload: object) -> bool:
    return not _context_set_primary_single_record_payload_needs_audit_quarantine_without_store(payload)


def _record_item_ids_need_audit_quarantine(raw_item_ids: object) -> bool:
    raw_values = _basket_raw_item_ids_snapshot(raw_item_ids)
    if raw_values is None:
        if ContextBasket._is_one_shot_iterator(raw_item_ids):
            return True
        return not ContextBasket._normalize_item_id(raw_item_ids)
    if isinstance(raw_item_ids, list) and all(isinstance(item, str) and not item.strip() for item in raw_values):
        return False
    return any(not ContextBasket._normalize_item_id(item) for item in raw_values)


def _snapshot_existing_corrupt_artifacts(
    store: ContextBasketStore,
) -> tuple[tuple[Path, bool, bytes | None], ...]:
    snapshots: list[tuple[Path, bool, bytes | None]] = []
    for live_path, corrupt_path in (
        (store._path, store._corrupt_path()),
        (store._backup_path, store._corrupt_path_for(store._backup_path)),
        (store._seed_state_path(), store._corrupt_path_for(store._seed_state_path())),
        (store._tmp_path(), store._corrupt_path_for(store._tmp_path())),
        (store._backup_tmp_path(), store._corrupt_path_for(store._backup_tmp_path())),
        (store._seed_tmp_path(), store._corrupt_path_for(store._seed_tmp_path())),
    ):
        if not corrupt_path.exists():
            continue
        snapshots.append((corrupt_path, live_path.exists(), _snapshot_corrupt_artifact_bytes(corrupt_path)))
    return tuple(snapshots)


def _restore_existing_corrupt_artifacts(
    store: ContextBasketStore,
    snapshots: tuple[tuple[Path, bool, bytes | None], ...],
) -> None:
    # Plain forensic byte payloads flow through ``_write_basket_bytes`` so the
    # restore writer shares the ``_fsync_basket_path`` content-flush seam used by
    # canonical basket state. A raw ``write_bytes`` here would skip that seam, so
    # a torn restore during recovery rollback would republish a half-written
    # forensic artifact that itself masquerades as corrupt. Unlike the vault and
    # context-set floors, the basket store first clears a stale symlink standing
    # on the corrupt path (``unlink_symlinks``) so a swapped-in alias cannot
    # shadow the restored artifact. The restore loop is the canonical one shared
    # across stores; restore stays best-effort, so a rejected flush is swallowed.
    _restore_corrupt_artifact_snapshots(
        snapshots, _write_basket_bytes, unlink_symlinks=True
    )


def _normalize_recovery_candidate_payload(payload: object) -> object | None:
    """Return a recovery candidate with wrapper payloads materialized."""

    if isinstance(payload, UserList):
        return list(payload)
    if isinstance(payload, tuple):
        return list(payload)
    if isinstance(payload, AbstractMapping) and type(payload) is not dict:
        return _payload_as_plain_dict(payload)
    return payload


def _basket_payload_needs_recovery_marker_sync(original_payload: object, payload: object) -> bool:
    """Return ``True`` when a wrapper still needs its recovery marker reconciled."""

    if not isinstance(original_payload, AbstractMapping) or not isinstance(payload, dict):
        return False
    try:
        marker_sentinel = object()
        original_payload_snapshot = _payload_as_plain_dict(original_payload)
        # Compare every marker view the wrapper exposes -- both the
        # iteration-visible snapshot and a direct ``.get()`` -- against the
        # canonical payload. A wrapper whose backing store disagrees with its
        # own iteration view (hides the marker from ``__iter__`` or exposes a
        # divergent stale value) must still trigger reconciliation.
        payload_marker = payload.get("recovered_from", marker_sentinel)
        observed_markers = [original_payload.get("recovered_from", marker_sentinel)]
        if original_payload_snapshot is not None:
            observed_markers.append(
                original_payload_snapshot.get("recovered_from", marker_sentinel)
            )
        present_markers = [
            marker for marker in observed_markers if marker is not marker_sentinel
        ]
        if present_markers:
            return any(marker != payload_marker for marker in present_markers)
        return marker_sentinel != payload_marker
    except Exception:
        return True


def _basket_payload_has_non_plain_json_shapes(value: object) -> bool:
    """Return ``True`` when *value* still contains non-plain JSON container shapes.

    Delegates to the shared :func:`_payload_has_non_plain_json_shapes` so basket
    classification cannot drift from ``_vault_payload_has_non_plain_json_shapes``.
    """

    return _payload_has_non_plain_json_shapes(value)


def _sync_basket_payload_mapping_wrapper(
    original_payload: object | None,
    payload: object,
    *,
    preserve_equivalent_raw_wrapper: bool = False,
) -> None:
    """Copy a canonical basket payload back into a mapping wrapper."""

    if original_payload is None or original_payload is payload or not isinstance(payload, dict):
        return
    try:
        original_payload_snapshot = _payload_as_plain_dict(original_payload)
        needs_marker_sync = _basket_payload_needs_recovery_marker_sync(original_payload, payload)
        if preserve_equivalent_raw_wrapper:
            if original_payload_snapshot == payload and not needs_marker_sync:
                return
        elif (
            original_payload_snapshot == payload
            and not needs_marker_sync
            # A non-``str`` top-level key (e.g. a ``str`` subclass) serializes as
            # its plain ``str`` base, so the wrapper diverges from disk even when
            # dict equality and the marker views agree -- the shared guard
            # normalizes it rather than skipping reconciliation.
            and not _mapping_wrapper_exposes_non_plain_json_shape(original_payload)
        ):
            return
    except Exception:
        pass
    try:
        safe_payload = _safe_json_value(payload) if _has_non_finite_float(payload) else payload
        if safe_payload is not payload and isinstance(safe_payload, dict):
            payload = safe_payload
        original_payload.clear()
        original_payload.update(payload)
    except Exception:
        pass


def _context_basket_store_recovery_source_path(
    self: ContextBasketStore,
    recovered_source: str | None,
) -> Path | None:
    if recovered_source == "tmp":
        return self._tmp_path()
    if recovered_source == "backup_tmp":
        return self._backup_tmp_path()
    if recovered_source == "seed_tmp":
        return self._seed_tmp_path()
    return None


def _context_basket_store_sync_temp_source_payload(
    self: ContextBasketStore,
    source_payloads: AbstractMutableMapping[Path, object] | None = None,
    *,
    preserve_equivalent_raw_wrapper: bool = False,
) -> None:
    if source_payloads is None:
        source_payloads = getattr(self, "_load_wrapper_source_payloads", None)
    if not isinstance(source_payloads, AbstractMutableMapping):
        return
    try:
        final_payload = json.loads(self._path.read_text(encoding="utf-8"))
    except Exception:
        return
    if isinstance(final_payload, AbstractMapping) and type(final_payload) is not dict:
        final_payload = _payload_as_plain_dict(final_payload)
    if not isinstance(final_payload, dict):
        return
    cleaned_payload = dict(final_payload)
    cleaned_payload.pop("recovered_from", None)
    temp_source_path = getattr(self, _LOAD_WRAPPER_TEMP_SOURCE_PATH_ATTR, None)
    temp_source_paths: list[Path] = []
    if isinstance(temp_source_path, Path):
        temp_source_paths.append(temp_source_path)
    for candidate_path in (self._tmp_path(), self._backup_tmp_path(), self._seed_tmp_path()):
        if candidate_path not in temp_source_paths and candidate_path in source_payloads:
            temp_source_paths.append(candidate_path)
    for candidate_path in temp_source_paths:
        source_payload = source_payloads.get(candidate_path)
        if not isinstance(source_payload, AbstractMapping) or type(source_payload) is dict:
            continue
        _sync_basket_payload_mapping_wrapper(
            source_payload,
            cleaned_payload,
            preserve_equivalent_raw_wrapper=preserve_equivalent_raw_wrapper,
        )


def _validate_basket_payload(payload: object) -> bool:
    if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return False
    if _basket_payload_needs_audit_quarantine(payload):
        return False
    return True


def _validate_context_set_payload(path: Path, payload: object) -> bool:
    if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return False
    if _is_context_set_auxiliary_path(path):
        return _context_set_auxiliary_payload_is_recoverable_without_updated_at(payload)
    return not _context_set_payload_needs_audit_quarantine(path, payload)


def _is_basket_state_path(path: Path) -> bool:
    return path.name.split(".", 1)[0] == "context_basket"


def _is_basket_auxiliary_state_path(path: Path) -> bool:
    return _is_basket_state_path(path) and path.name.endswith(".json") and path.name != "context_basket.json"


def _is_basket_family_path(path: Path) -> bool:
    return _is_basket_state_path(path) or _is_basket_auxiliary_state_path(path)


def validate_and_quarantine(path: str | Path) -> bool:
    p = Path(path)
    if p.name.endswith((".corrupt.json", ".corrupt")):
        return False
    if p.is_symlink():
        _quarantine_path(p)
        return False
    try:
        payload = _load_json_payload(p)
    except Exception:
        _quarantine_path(p)
        return False

    original_payload = payload if isinstance(payload, AbstractMapping) and type(payload) is not dict else None
    if original_payload is not None:
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            _quarantine_path(p)
            return False

    def _sync_original_payload() -> None:
        if original_payload is None or not isinstance(payload, dict) or original_payload is payload:
            return
        try:
            original_payload.clear()
            original_payload.update(payload)
        except Exception:
            pass

    def _sync_original_payload_safe() -> None:
        if original_payload is None or not isinstance(payload, dict) or original_payload is payload:
            return
        safe_payload = _safe_json_value(payload)
        if not isinstance(safe_payload, dict):
            return
        try:
            original_payload.clear()
            original_payload.update(safe_payload)
        except Exception:
            pass

    if _is_context_set_auxiliary_path(p):
        if not _validate_context_set_payload(p, payload):
            _quarantine_path(p)
            _sync_original_payload_safe()
            return False
        _sync_original_payload()
        return True

    if _is_context_set_primary_path(p):
        if not _validate_context_set_payload(p, payload):
            _quarantine_path(p)
            _sync_original_payload_safe()
            return False
        _sync_original_payload()
        return True

    if _is_basket_family_path(p) and isinstance(payload, dict) and "context_sets" in payload:
        _quarantine_path(p)
        _sync_original_payload_safe()
        return False

    if isinstance(payload, dict) and "context_sets" in payload:
        if not _validate_context_set_payload(p, payload):
            _quarantine_path(p)
            _sync_original_payload_safe()
            return False
        _sync_original_payload()
        return True

    if _is_basket_family_path(p) and _basket_family_payload_looks_like_context_set_records(payload):
        _quarantine_path(p)
        _sync_original_payload_safe()
        return False

    if isinstance(payload, dict) and "item_ids" in payload:
        if _is_basket_auxiliary_state_path(p):
            raw_updated_at = payload.get("updated_at")
            if (
                isinstance(raw_updated_at, str)
                and raw_updated_at.strip()
                and _parse_updated_at(raw_updated_at) is None
            ):
                _quarantine_path(p)
                _sync_original_payload_safe()
                return False
        if not _validate_basket_payload(payload):
            _quarantine_path(p)
            _sync_original_payload_safe()
            return False
        _sync_original_payload()
        return True

    if isinstance(payload, (list, tuple)) or (
        isinstance(payload, AbstractIterable)
        and not isinstance(payload, (str, bytes, bytearray, memoryview, AbstractMapping))
    ):
        materialized_context_sets = _context_set_payload_as_list(payload)
        if materialized_context_sets is not None:
            if (
                materialized_context_sets
                and isinstance(materialized_context_sets[0], dict)
                and "context_set_id" in materialized_context_sets[0]
            ):
                if not _validate_context_set_payload(p, materialized_context_sets):
                    _quarantine_path(p)
                    _sync_original_payload_safe()
                    return False
                _sync_original_payload()
                return True
            if _is_context_set_primary_path(p):
                if not _validate_context_set_payload(p, materialized_context_sets):
                    _quarantine_path(p)
                    _sync_original_payload_safe()
                    return False
                _sync_original_payload()
                return True
        if not _validate_basket_payload(payload):
            _quarantine_path(p)
            _sync_original_payload_safe()
            return False
        _sync_original_payload()
        return True

    if not _validate_basket_payload(payload):
        _quarantine_path(p)
        _sync_original_payload_safe()
        return False
    _sync_original_payload()
    return True


def clear_corrupt_files(state_root: Union[Path, str]) -> int:
    root = Path(state_root)
    prune_stop = _corrupt_scan_root(root)
    removed = 0
    removed_paths: list[Path] = []
    for p in list_corrupt_files(root):
        if any(_path_is_descendant_of(p, removed_path) for removed_path in removed_paths):
            continue
        if _remove_corrupt_artifact(p):
            removed += 1
            removed_paths.append(p)
            _prune_empty_parent_dirs(p.parent, prune_stop)
    return removed


def _corrupt_path_key(path: Path) -> str:
    """Return a stable deduplication key for a corrupt-artifact path."""

    # Normalize spelling aliases like ``./`` without following symlinks. A
    # corrupt symlink and its corrupt target are distinct local artifacts, and
    # cleanup must surface both instead of collapsing the link to its target.
    return os.path.abspath(os.path.normpath(os.fspath(path)))


def _path_is_descendant_of(path: Path, ancestor: Path) -> bool:
    """Return ``True`` when *path* is nested beneath *ancestor*."""

    try:
        return path == ancestor or ancestor in path.parents
    except Exception:  # pragma: no cover - defensive path handling
        return False


def _path_exists_or_is_symlink(path: Path) -> bool:
    try:
        return path.exists() or path.is_symlink()
    except OSError:
        try:
            return path.is_symlink()
        except OSError:
            return False


def _corrupt_scan_root(root: Path) -> Path:
    """Return the directory that should be scanned for corrupt artefacts.

    The helper walks up from missing nested paths until it reaches an existing
    ancestor. That keeps sibling quarantine artefacts visible even when the
    caller points at a nested file path inside a quarantined directory alias.
    """

    scan_root = root
    while not _path_exists_or_is_symlink(scan_root) and scan_root.parent != scan_root:
        scan_root = scan_root.parent
    if _is_corrupt_artifact_path(scan_root):
        # Quarantined file and directory aliases should inspect their parent
        # so sibling corrupt artefacts remain visible even when the corrupt
        # path itself has not been recreated yet.
        return scan_root.parent
    if _path_is_concrete_state_file_or_unprobeable_json(scan_root):
        # Callers sometimes point the helper at a concrete state file instead
        # of the containing directory. In that case, inspect the parent
        # directory so sibling quarantine artefacts stay visible.
        return scan_root.parent
    if (
        not _path_exists_or_is_symlink(scan_root)
        and scan_root.suffix == ".json"
        and not scan_root.name.endswith(".corrupt.json")
    ):
        # A missing concrete state file should still expose sibling quarantine
        # artefacts. Treat it like the existing file-path case so cleanup
        # helpers can repair the surrounding state even when the live file has
        # not been created yet.
        return scan_root.parent
    return scan_root


def _path_is_concrete_state_file_or_unprobeable_json(path: Path) -> bool:
    try:
        return _path_exists_or_is_symlink(path) and path.is_file()
    except (OSError, RuntimeError):
        return path.suffix == ".json" and not path.name.endswith(".corrupt.json")


def purge_corrupt_state(state_root: Union[Path, str]) -> int:
    return clear_corrupt_files(state_root)


def remove_all_corrupt_files(state_root: Union[Path, str]) -> int:
    return clear_corrupt_files(state_root)


def is_clean_state(state_root: Union[Path, str]) -> bool:
    return not list_corrupt_files(state_root)


_ORIGINAL_CONTEXT_BASKET_STORE_PARSE_ITEM_IDS = ContextBasketStore._parse_item_ids
_ORIGINAL_CONTEXT_BASKET_STORE_LOAD_PAYLOAD = ContextBasketStore._load_payload
_ORIGINAL_CONTEXT_BASKET_STORE_LOAD = ContextBasketStore.load
_ORIGINAL_CONTEXT_BASKET_STORE_SAVE = ContextBasketStore.save
_ORIGINAL_CONTEXT_BASKET_STORE_IS_LOADABLE_PAYLOAD = ContextBasketStore._is_loadable_payload
_ORIGINAL_CONTEXT_BASKET_STORE_IS_SUPPORTED_PAYLOAD = ContextBasketStore._is_supported_payload
_ORIGINAL_CONTEXT_BASKET_STORE_PREFER_RECOVERY_PAYLOAD = ContextBasketStore._prefer_recovery_payload


def _quarantine_basket_artifact_for_path(store: ContextBasketStore, path: Path) -> None:
    if path == store._path:
        store._quarantine_invalid_file()
    elif path.suffix == ".tmp":
        store._quarantine_path(path)
    elif path == store._backup_path:
        store._quarantine_invalid_backup()
    elif path == store._seed_state_path():
        store._quarantine_invalid_seed()


def _context_basket_store_parse_item_ids(self: ContextBasketStore, value: object) -> list[str] | None:
    if isinstance(value, tuple) and not value:
        return []
    raw_values = _basket_raw_item_ids_snapshot(value)
    if raw_values is None:
        if isinstance(value, str):
            normalized = value.strip()
            return [normalized] if normalized else []
        normalized = ContextBasket._normalize_item_id(value)
        return [normalized] if normalized else None
    parsed: list[str] = []
    for raw_item_id in raw_values:
        normalized_item_id = ContextBasket._normalize_item_id(raw_item_id)
        if not normalized_item_id:
            continue
        parsed.append(normalized_item_id)
    if not parsed and not isinstance(value, list):
        return None
    return parsed


def _context_basket_store_normalize_item_id(self: ContextBasketStore, item_id: object) -> str:
    return ContextBasket._normalize_item_id(item_id)


def _context_basket_store_load_payload(
    self: ContextBasketStore,
    path: Path,
) -> tuple[dict[str, object] | list[object] | None, bool]:
    if path.is_symlink():
        _quarantine_basket_artifact_for_path(self, path)
        return None, True
    if not path.exists():
        return None, False
    try:
        payload = _load_json_payload(path)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        _quarantine_basket_artifact_for_path(self, path)
        return None, True
    load_wrapper_source_payloads = getattr(self, "_load_wrapper_source_payloads", None)
    if isinstance(payload, AbstractMapping) and type(payload) is not dict:
        original_payload = payload
        if isinstance(load_wrapper_source_payloads, AbstractMutableMapping):
            load_wrapper_source_payloads[path] = payload
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            _quarantine_basket_artifact_for_path(self, path)
            return None, True
        if "recovered_from" in payload and self._parse_updated_at(payload.get("updated_at")) is None:
            _quarantine_basket_artifact_for_path(self, path)
            return None, True
        if path == self._path:
            canonical_snapshot = _safe_json_value(payload)
            if isinstance(canonical_snapshot, dict):
                canonical_snapshot.pop("recovered_from", None)
                _sync_basket_payload_mapping_wrapper(
                    original_payload,
                    canonical_snapshot,
                    preserve_equivalent_raw_wrapper=True,
                )
        return payload, False
    if isinstance(payload, dict) and "recovered_from" in payload and self._parse_updated_at(payload.get("updated_at")) is None:
        # For the primary path with valid item_ids: sanitize in place rather
        # than quarantining — strip the malformed recovery metadata and return
        # the cleaned payload. The outer load will stamp a fresh timestamp.
        if path == self._path and "item_ids" in payload:
            raw_item_ids = payload.get("item_ids")
            salvaged_items = self._parse_item_ids(raw_item_ids)
            if salvaged_items:
                sanitized_payload: dict[str, object] = {"item_ids": raw_item_ids}
                if "schema_version" in payload:
                    sanitized_payload["schema_version"] = payload["schema_version"]
                return sanitized_payload, False
        canonical_snapshot = _snapshot_basket_payload(payload)
        if isinstance(canonical_snapshot, dict):
            canonical_snapshot = _safe_json_value(canonical_snapshot)
        if isinstance(canonical_snapshot, dict):
            canonical_snapshot.pop("recovered_from", None)
            _sync_basket_payload_mapping_wrapper(
                payload,
                canonical_snapshot,
                preserve_equivalent_raw_wrapper=True,
            )
        # A blank (whitespace-only) updated_at on a recovery artifact indicates
        # corrupt state written during a failed recovery pass; discard it entirely
        # rather than salvaging its items into a new recovery.
        raw_updated_at_for_salvage = payload.get("updated_at")
        if "updated_at" not in payload or (
            isinstance(raw_updated_at_for_salvage, str) and not raw_updated_at_for_salvage.strip()
        ):
            _quarantine_basket_artifact_for_path(self, path)
            return None, True
        # Salvage valid item_ids from backup/seed artifacts whose recovery
        # metadata is malformed. The artifact is quarantined, but returning
        # a stripped payload lets the load path promote those items rather
        # than discarding them and materializing an empty basket.
        if path in (self._backup_path, self._seed_state_path()) and "item_ids" in payload:
            raw_item_ids = payload.get("item_ids")
            salvaged_items = self._parse_item_ids(raw_item_ids)
            if salvaged_items:
                salvaged_payload: dict[str, object] = {"item_ids": raw_item_ids}
                if "schema_version" in payload:
                    salvaged_payload["schema_version"] = payload["schema_version"]
                _quarantine_basket_artifact_for_path(self, path)
                return salvaged_payload, True
        _quarantine_basket_artifact_for_path(self, path)
        return None, True
    if not isinstance(payload, (dict, list)):
        snapshot = _snapshot_basket_payload(payload)
        if snapshot is None:
            _quarantine_basket_artifact_for_path(self, path)
            return None, True
        _quarantine_basket_artifact_for_path(self, path)
        return snapshot, True
    return _ORIGINAL_CONTEXT_BASKET_STORE_LOAD_PAYLOAD(self, path)


def _context_basket_store_prefer_recovery_payload(
    self: ContextBasketStore,
    tmp_payload: dict[str, object] | list[object] | None,
    backup_tmp_payload: dict[str, object] | list[object] | None,
    backup_payload: dict[str, object] | list[object] | None,
    seed_tmp_payload: dict[str, object] | list[object] | None,
    seed_payload: dict[str, object] | list[object] | None,
) -> tuple[dict[str, object] | list[object] | None, str | None]:
    def _normalize_candidate(payload: dict[str, object] | list[object] | None) -> dict[str, object] | list[object] | None:
        if isinstance(payload, UserList):
            return list(payload)
        if isinstance(payload, tuple):
            return list(payload)
        if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
            payload = _payload_as_plain_dict(payload)
        return payload

    def _blank_recovered_payload(payload: dict[str, object] | list[object] | None) -> bool:
        if not isinstance(payload, dict) or "recovered_from" not in payload:
            return False
        raw_updated_at = payload.get("updated_at")
        return isinstance(raw_updated_at, str) and not raw_updated_at.strip()

    tmp_payload = _normalize_candidate(tmp_payload)
    backup_tmp_payload = _normalize_candidate(backup_tmp_payload)
    backup_payload = _normalize_candidate(backup_payload)
    seed_tmp_payload = _normalize_candidate(seed_tmp_payload)
    seed_payload = _normalize_candidate(seed_payload)

    if _blank_recovered_payload(backup_tmp_payload):
        backup_tmp_payload = None
    if _blank_recovered_payload(backup_payload):
        backup_payload = None
    if _blank_recovered_payload(seed_tmp_payload):
        seed_tmp_payload = None
    if _blank_recovered_payload(seed_payload):
        seed_payload = None
    if _blank_recovered_payload(tmp_payload):
        tmp_payload = None
    materialized_tmp_payload = _snapshot_basket_payload(tmp_payload) if tmp_payload is not None else None
    materialized_backup_tmp_payload = (
        _snapshot_basket_payload(backup_tmp_payload) if backup_tmp_payload is not None else None
    )
    materialized_backup_payload = _snapshot_basket_payload(backup_payload) if backup_payload is not None else None
    materialized_seed_tmp_payload = _snapshot_basket_payload(seed_tmp_payload) if seed_tmp_payload is not None else None
    materialized_seed_payload = _snapshot_basket_payload(seed_payload) if seed_payload is not None else None
    selected_payload, recovered_source = _ORIGINAL_CONTEXT_BASKET_STORE_PREFER_RECOVERY_PAYLOAD(
        self,
        materialized_tmp_payload if materialized_tmp_payload is not None else tmp_payload,
        materialized_backup_tmp_payload if materialized_backup_tmp_payload is not None else backup_tmp_payload,
        materialized_backup_payload if materialized_backup_payload is not None else backup_payload,
        materialized_seed_tmp_payload if materialized_seed_tmp_payload is not None else seed_tmp_payload,
        materialized_seed_payload if materialized_seed_payload is not None else seed_payload,
    )
    if isinstance(selected_payload, dict) and "recovered_from" in selected_payload and recovered_source in {"backup", "seed"}:
        selected_snapshot = _snapshot_basket_payload(selected_payload)
        selected_updated_at = (
            _context_basket_store_recovery_timestamp(self, selected_snapshot)
            if selected_snapshot is not None
            else None
        )
        if selected_updated_at is not None:
            for committed_source, committed_payload in (
                ("backup", materialized_backup_payload if materialized_backup_payload is not None else backup_payload),
                ("seed", materialized_seed_payload if materialized_seed_payload is not None else seed_payload),
            ):
                committed_snapshot = _snapshot_basket_payload(committed_payload)
                if committed_snapshot is None or not isinstance(committed_snapshot, dict):
                    continue
                if "recovered_from" in committed_snapshot:
                    continue
                committed_updated_at = _context_basket_store_recovery_timestamp(self, committed_snapshot)
                if committed_updated_at != selected_updated_at:
                    continue
                if not self._has_recovery_payload_items(committed_snapshot) and not self._has_explicit_empty_recovery_payload(
                    committed_snapshot
                ):
                    continue
                selected_payload = committed_snapshot
                recovered_source = committed_source
                break
    if recovered_source in {"backup_tmp", "seed_tmp", "tmp"}:
        selected_snapshot = _snapshot_basket_payload(selected_payload)
        selected_updated_at = (
            _context_basket_store_recovery_timestamp(self, selected_snapshot)
            if selected_snapshot is not None
            else None
        )
        if selected_updated_at is not None:
            for committed_source, committed_payload in (
                ("backup", materialized_backup_payload if materialized_backup_payload is not None else backup_payload),
                ("seed", materialized_seed_payload if materialized_seed_payload is not None else seed_payload),
            ):
                committed_snapshot = _snapshot_basket_payload(committed_payload)
                if committed_snapshot is None:
                    continue
                committed_updated_at = _context_basket_store_recovery_timestamp(self, committed_snapshot)
                if committed_updated_at != selected_updated_at:
                    continue
                selected_payload = committed_snapshot
                recovered_source = committed_source
                break
    return selected_payload, recovered_source


def _basket_payload_has_whitespace_trimmed_item_ids(payload: object) -> bool:
    if isinstance(payload, dict):
        raw_item_ids = payload.get("item_ids")
    else:
        raw_item_ids = payload
    raw_values = _basket_raw_item_ids_snapshot(raw_item_ids)
    if raw_values is None:
        return isinstance(raw_item_ids, str) and raw_item_ids.strip() != raw_item_ids
    return any(isinstance(raw_item_id, str) and raw_item_id.strip() != raw_item_id for raw_item_id in raw_values)


def _snapshot_basket_corrupt_payload(payload: object) -> object | None:
    snapshot = _snapshot_basket_payload(payload)
    if snapshot is not None:
        return _safe_json_value(snapshot)
    if isinstance(payload, AbstractMapping):
        return _safe_json_value(payload)
    return payload if isinstance(payload, (dict, list, tuple)) else None


def _snapshot_basket_raw_payload(path: Path) -> object | None:
    if path.is_symlink():
        return None
    if not path.exists():
        return None
    try:
        return _load_json_payload(path)
    except Exception:
        return None


def _write_basket_corrupt_snapshot(store: ContextBasketStore, path: Path, payload: object) -> None:
    corrupt_path = store._corrupt_path_for(path)
    corrupt_path = _next_basket_corrupt_snapshot_path(corrupt_path)
    snapshot = _snapshot_basket_corrupt_payload(payload)
    if snapshot is None:
        return
    try:
        encoded = _canonical_json_dumps(snapshot)
    except (TypeError, ValueError):
        return
    # Stage the forensic snapshot through the same content-flush seam the live
    # basket writer uses (temp + ``_fsync_basket_path`` + atomic replace) rather
    # than a raw ``write_text``. A torn direct write would leave a half-written
    # corrupt artifact that itself looks corrupt -- defeating the audit purpose
    # of the snapshot. This stays best-effort: any failure cleans up the staged
    # temp and reports nothing, never raising into the recovery path.
    tmp = corrupt_path.with_name(f"{corrupt_path.name}.tmp")
    try:
        corrupt_path.parent.mkdir(parents=True, exist_ok=True)
        _quarantine_stale_basket_temp_artifact(tmp)
        with tmp.open("x", encoding="utf-8") as file:
            file.write(encoded)
            file.flush()
        _fsync_basket_path(tmp)
        if tmp.is_symlink():
            raise FileExistsError(
                f"context basket corrupt-snapshot temp path became a symlink: {tmp}"
            )
        tmp.replace(corrupt_path)
        _fsync_basket_parent(corrupt_path)
    except (OSError, TypeError, ValueError):
        _unlink_basket_temp_path(tmp)


def _next_basket_corrupt_snapshot_path(corrupt_path: Path) -> Path:
    if not corrupt_path.exists() and not corrupt_path.is_symlink():
        return corrupt_path
    corrupt_json_suffix = ".corrupt.json"
    if corrupt_path.name.endswith(corrupt_json_suffix):
        stem = corrupt_path.name[: -len(corrupt_json_suffix)]
        for index in range(1, 1000):
            candidate = corrupt_path.with_name(f"{stem}.{index}{corrupt_json_suffix}")
            if not candidate.exists() and not candidate.is_symlink():
                return candidate
    for index in range(1, 1000):
        candidate = corrupt_path.with_name(f"{corrupt_path.name}.{index}")
        if not candidate.exists() and not candidate.is_symlink():
            return candidate
    raise FileExistsError(f"no free corrupt artifact path for {corrupt_path}")


def _context_basket_store_recovery_timestamp(
    self: ContextBasketStore,
    payload: object,
) -> str | None:
    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return None
    raw_updated_at = payload.get("updated_at")
    if not isinstance(raw_updated_at, str):
        return None
    parsed_updated_at = self._parse_updated_at(raw_updated_at)
    if parsed_updated_at is None:
        return None
    raw_item_ids = payload.get("item_ids")
    return parsed_updated_at


def _context_basket_store_load(self: ContextBasketStore) -> ContextBasket:
    _reject_basket_state_root_alias(self._path.parent)
    primary_raw = _snapshot_basket_raw_payload(self._path)
    backup_raw = _snapshot_basket_raw_payload(self._backup_path)
    seed_raw = _snapshot_basket_raw_payload(self._seed_state_path())
    backup_raw_payload = _payload_as_plain_dict(backup_raw) if isinstance(backup_raw, AbstractMapping) else None
    seed_raw_payload = _payload_as_plain_dict(seed_raw) if isinstance(seed_raw, AbstractMapping) else None
    corrupt_artifacts = _snapshot_existing_corrupt_artifacts(self)
    for temp_path in (self._tmp_path(), self._backup_tmp_path(), self._seed_tmp_path()):
        self._load_payload(temp_path)
    primary_snapshot = _snapshot_basket_payload(primary_raw)
    backup_snapshot = _snapshot_basket_payload(backup_raw)
    primary_items = _snapshot_basket_item_ids(primary_snapshot)
    backup_items = _snapshot_basket_item_ids(backup_snapshot)
    primary_updated_at = (
        self._parse_updated_at(primary_raw.get("updated_at"))
        if isinstance(primary_raw, AbstractMapping)
        else None
    )
    def _preferred_recovery_timestamp() -> str | None:
        normalized_updated_at = None
        if backup_raw is not None and not backup_needs_audit_quarantine:
            # Only let the backup donate its timestamp when the payload is
            # still recoverable enough to avoid quarantine. Completely
            # unrecoverable ``item_ids`` payloads should not backdate the
            # rewritten primary state.
            normalized_updated_at = _context_basket_store_recovery_timestamp(self, backup_raw)
        if normalized_updated_at is None:
            normalized_updated_at = primary_updated_at
        if normalized_updated_at is None:
            normalized_updated_at = _now_iso()
        return normalized_updated_at

    if isinstance(backup_raw_payload, dict) and "recovered_from" in backup_raw_payload:
        _write_basket_corrupt_snapshot(self, self._backup_path, backup_raw)
    backup_audit_payload = backup_raw if isinstance(backup_raw, dict) else backup_raw_payload
    backup_needs_audit_quarantine = False
    if isinstance(backup_audit_payload, dict):
        raw_item_ids = backup_audit_payload.get("item_ids") if "item_ids" in backup_audit_payload else None
        if ContextBasket._is_one_shot_iterator(raw_item_ids):
            backup_needs_audit_quarantine = backup_snapshot is None or self._backup_needs_audit_quarantine(
                backup_snapshot
            )
        else:
            backup_needs_audit_quarantine = self._backup_needs_audit_quarantine(backup_audit_payload)
    materialized_sequence_paths: set[Path] = set()
    source_payloads: dict[Path, object] = {}
    self._load_wrapper_source_payloads = source_payloads  # type: ignore[attr-defined]
    original_load_payload = self._load_payload

    def _sync_source_payloads() -> None:
        for path, source_payload in source_payloads.items():
            _sync_basket_source_payload_wrapper(
                source_payload,
                path,
                None,
                preserve_equivalent_raw_wrapper=True,
            )

    def _finish(basket: ContextBasket) -> ContextBasket:
        _sync_source_payloads()
        return basket

    def _normalized_load_payload(path: Path) -> tuple[object | None, bool]:
        payload, quarantined = original_load_payload(path)
        if isinstance(payload, dict):
            return payload, quarantined
        if isinstance(payload, list):
            return payload, quarantined
        if not isinstance(payload, AbstractMapping):
            normalized_payload = _snapshot_basket_payload(payload)
            if normalized_payload is not None:
                materialized_sequence_paths.add(path)
                return normalized_payload, quarantined
            return payload, quarantined
        normalized_payload = _snapshot_basket_payload(payload)
        if normalized_payload is not None:
            return normalized_payload, quarantined
        return payload, quarantined

    original_clear_quarantine_file = self._clear_quarantine_file

    def _preserve_temp_clear_quarantine_file(
        preserve_temporary: bool = False,
        preserve_primary_corrupt: bool = False,
        preserve_backup_corrupt: bool = False,
        preserve_seed_corrupt: bool = False,
    ) -> None:
        # During the inner load, always preserve temporary corrupt markers so
        # the outer load's post-processing block can decide which preexisting
        # ones to clear (only stale markers, not newly quarantined ones).
        original_clear_quarantine_file(
            preserve_temporary=True,
            preserve_primary_corrupt=preserve_primary_corrupt,
            preserve_backup_corrupt=preserve_backup_corrupt,
            preserve_seed_corrupt=preserve_seed_corrupt,
        )

    try:
        self._load_payload = _normalized_load_payload  # type: ignore[assignment]
        self._clear_quarantine_file = _preserve_temp_clear_quarantine_file  # type: ignore[assignment]
        basket = _ORIGINAL_CONTEXT_BASKET_STORE_LOAD(self)
        _context_basket_store_sync_temp_source_payload(
            self,
            source_payloads,
            preserve_equivalent_raw_wrapper=True,
        )
    finally:
        self._load_payload = original_load_payload  # type: ignore[assignment]
        self._clear_quarantine_file = original_clear_quarantine_file  # type: ignore[assignment]
        try:
            delattr(self, "_load_wrapper_source_payloads")
        except AttributeError:
            pass
        try:
            delattr(self, _LOAD_WRAPPER_TEMP_SOURCE_PATH_ATTR)
        except AttributeError:
            pass
    primary_sequence_materialized = self._path in materialized_sequence_paths
    if primary_sequence_materialized and backup_raw is None and basket.item_ids:
        primary_needs_quarantine = False
    # When primary is a legacy list with valid items and the backup is also a
    # legacy list that is strictly smaller, restore list-primary precedence: the
    # primary list is the user's live state and should not be silently replaced by
    # a stale legacy-list backup.
    if isinstance(primary_raw, list) and isinstance(backup_raw, list):
        parsed_primary_items = self._parse_item_ids(primary_raw)
        backup_item_count = len(backup_items) if backup_items is not None else 0
        primary_item_count = len(parsed_primary_items) if parsed_primary_items else 0
        if (
            parsed_primary_items
            and list(basket.item_ids) != list(parsed_primary_items)
            and backup_item_count < primary_item_count
        ):
            basket = ContextBasket(item_ids=list(parsed_primary_items))
            normalized_ts = _preferred_recovery_timestamp()
            canonical_primary = {
                "schema_version": _SCHEMA_VERSION,
                "updated_at": normalized_ts,
                "item_ids": list(basket.item_ids),
            }
            try:
                _write_basket_payload(self._path, canonical_primary)
            except OSError:
                pass
            try:
                _write_basket_payload(self._backup_path, dict(canonical_primary))
            except OSError:
                pass
    # The same precedence applies against a structured dict backup: the inner
    # load prefers a recoverable dict backup over the legacy list, and that is
    # correct when the backup is richer or poorer than the salvaged list (it is
    # then the authoritative last-good copy of a differently-sized state). But
    # when the dict backup carries the same number of items as the primary's own
    # salvaged list yet differs from it, the legacy list is the user's live state
    # and must win, rewriting both files canonically rather than yielding.
    #
    # INVARIANT (list-vs-dict backup precedence): the semantics here are
    # deliberately ASYMMETRIC from the list-vs-list case above. In list-vs-list,
    # only a strictly *smaller* backup loses to the live primary. In list-vs-dict,
    # only the equal-size-but-differing case favors the primary; a *differently*
    # sized dict backup -- whether larger OR smaller -- is treated as the
    # authoritative last-good copy and wins over the live legacy-list primary.
    # This means a strictly smaller structured dict backup can silently discard
    # live primary-list items: that is an intentional recovery choice (a parsed
    # structured snapshot is trusted as the canonical last-good state over an
    # un-upgraded legacy list), not a bug. Any change to this precedence is a
    # data-retention semantic and must be made deliberately.
    elif isinstance(primary_raw, list) and isinstance(backup_raw, AbstractMapping):
        # Canonicalize the legacy list (``_parse_item_ids`` keeps duplicates;
        # ``ContextBasket`` collapses them) so the comparison uses the list's
        # effective item set.
        canonical_primary_items = list(ContextBasket(item_ids=self._parse_item_ids(primary_raw)).item_ids)
        # The inner load already selected the competing dict backup, so the
        # current basket reflects the backup's effective item set; compare its
        # size (the raw backup snapshot may not have materialized here).
        selected_item_count = len(basket.item_ids)
        primary_item_count = len(canonical_primary_items)
        if (
            canonical_primary_items
            and list(basket.item_ids) != canonical_primary_items
            and selected_item_count == primary_item_count
        ):
            basket = ContextBasket(item_ids=list(canonical_primary_items))
            normalized_ts = _preferred_recovery_timestamp()
            canonical_primary = {
                "schema_version": _SCHEMA_VERSION,
                "updated_at": normalized_ts,
                "item_ids": list(basket.item_ids),
            }
            try:
                _write_basket_payload(self._path, canonical_primary)
            except OSError:
                pass
            try:
                _write_basket_payload(self._backup_path, dict(canonical_primary))
            except OSError:
                pass
    force_primary_corrupt = False
    if (
        isinstance(primary_raw, AbstractMapping)
        and primary_updated_at is not None
        and primary_items is not None
        and backup_items is not None
        and len(backup_items) > len(primary_items)
        and not self._primary_item_ids_need_recovery(primary_raw)
        and not backup_needs_audit_quarantine
    ):
        force_primary_corrupt = True

    if (
        isinstance(primary_raw, AbstractMapping)
        and "updated_at" not in primary_raw
        and primary_items is not None
        and backup_items
        and len(backup_items) > len(primary_items)
        and not backup_needs_audit_quarantine
    ):
        normalized_updated_at = _preferred_recovery_timestamp()
        basket = ContextBasket(item_ids=list(backup_items))
        force_primary_corrupt = True
        try:
            self.save(
                basket,
                recovered_from="backup",
                refresh_backup=True,
                updated_at=normalized_updated_at,
            )
        except OSError:
            pass
        force_primary_corrupt = True
        if primary_raw is not None:
            _write_basket_corrupt_snapshot(self, self._path, primary_raw)
        backup_after = _snapshot_basket_raw_payload(self._backup_path)
        if (
            primary_raw is not None
            and isinstance(backup_after, dict)
            and "recovered_from" in backup_after
            and not self._primary_item_ids_need_recovery(primary_raw)
        ):
            cleaned_backup_payload = dict(backup_after)
            cleaned_backup_payload.pop("recovered_from", None)
            try:
                _write_basket_payload(self._backup_path, cleaned_backup_payload)
            except OSError:
                pass

        if (
            isinstance(primary_raw, AbstractMapping)
            and "updated_at" not in primary_raw
            and primary_items is not None
            and backup_items is not None
            and len(backup_items) == len(primary_items)
            and isinstance(backup_audit_payload, dict)
            and not backup_needs_audit_quarantine
            and not isinstance(backup_audit_payload.get("item_ids"), list)
        ):
            normalized_updated_at = _preferred_recovery_timestamp()
            basket = ContextBasket(item_ids=list(backup_items))
            try:
                self.save(
                    basket,
                    refresh_backup=True,
                    updated_at=normalized_updated_at,
                )
            except OSError:
                pass
            _restore_existing_corrupt_artifacts(self, corrupt_artifacts)
            return _finish(basket)

    if (
        isinstance(primary_raw, dict)
        and primary_items is not None
        and backup_items
        and self._primary_item_ids_need_recovery(primary_raw)
        and not backup_needs_audit_quarantine
    ):
        normalized_updated_at = _preferred_recovery_timestamp()
        basket = ContextBasket(item_ids=list(backup_items))
        force_primary_corrupt = True
        try:
            self.save(
                basket,
                recovered_from="backup",
                refresh_backup=True,
                preserve_primary_corrupt=True,
                updated_at=normalized_updated_at,
            )
            if primary_raw is not None:
                _write_basket_corrupt_snapshot(self, self._path, primary_raw)
            backup_recovery_payload = {
                "schema_version": _SCHEMA_VERSION,
                "updated_at": normalized_updated_at,
                "item_ids": list(basket.item_ids),
                "recovered_from": "backup",
            }
            _write_basket_payload(self._backup_path, backup_recovery_payload)
        except OSError:
            pass
        _sync_source_payloads()
        return _finish(basket)
    if (
        isinstance(primary_raw, AbstractMapping)
        and primary_updated_at is not None
        and primary_items is not None
        and backup_items is not None
        and len(backup_items) > len(primary_items)
        and not self._primary_item_ids_need_recovery(primary_raw)
        and not backup_needs_audit_quarantine
        and not _basket_payload_has_whitespace_trimmed_item_ids(backup_audit_payload)
    ):
        normalized_updated_at = _preferred_recovery_timestamp()
        basket = ContextBasket(item_ids=list(backup_items))
        try:
            self.save(
                basket,
                recovered_from="backup",
                refresh_backup=True,
                updated_at=normalized_updated_at,
            )
        except OSError:
            pass
        clean_backup_payload: dict[str, object] = {
            "schema_version": _SCHEMA_VERSION,
            "item_ids": self._normalize_item_ids(list(basket.item_ids)),
        }
        if normalized_updated_at is not None:
            clean_backup_payload["updated_at"] = normalized_updated_at
        try:
            _write_basket_payload(self._backup_path, clean_backup_payload)
        except OSError:
            pass
        _write_basket_corrupt_snapshot(self, self._path, primary_raw)
        _restore_existing_corrupt_artifacts(self, corrupt_artifacts)
        return _finish(basket)

    if (
        isinstance(primary_raw, dict)
        and primary_updated_at is not None
        and primary_items is not None
        and isinstance(backup_audit_payload, dict)
        and _basket_payload_has_whitespace_trimmed_item_ids(backup_audit_payload)
        and not backup_needs_audit_quarantine
    ):
        parsed_backup_ids = self._parse_item_ids(backup_audit_payload.get("item_ids"))
        effective_backup = ContextBasket(item_ids=list(parsed_backup_ids or []))
        if list(effective_backup.item_ids) == list(basket.item_ids):
            backup_ts = backup_audit_payload.get("updated_at")
            backup_parsed_at = self._parse_updated_at(backup_ts)
            effective_ts: object = backup_parsed_at if backup_parsed_at is not None else primary_updated_at
            # The healthy primary was not rewritten. When the defective backup's
            # timestamp predates it, mirror the primary's timestamp rather than
            # carry the stale backup value forward (see the parallel non-whitespace
            # refresh below); a newer backup keeps its own normalized timestamp.
            raw_primary_ts = primary_raw.get("updated_at")
            if (
                isinstance(raw_primary_ts, str)
                and backup_parsed_at is not None
                and backup_parsed_at < primary_updated_at
            ):
                effective_ts = raw_primary_ts
            canonical_backup = {
                "schema_version": _SCHEMA_VERSION,
                "updated_at": effective_ts,
                "item_ids": list(basket.item_ids),
            }
            try:
                _write_basket_payload(self._backup_path, canonical_backup)
            except OSError:
                pass

    if (
        isinstance(primary_raw, dict)
        and primary_updated_at is not None
        and primary_items is not None
        and isinstance(backup_audit_payload, dict)
        and not _basket_payload_has_whitespace_trimmed_item_ids(backup_audit_payload)
        and not backup_needs_audit_quarantine
    ):
        parsed_backup_ids = self._parse_item_ids(backup_audit_payload.get("item_ids"))
        effective_backup = ContextBasket(item_ids=list(parsed_backup_ids or []))
        if list(effective_backup.item_ids) == list(basket.item_ids):
            raw_primary_ts = primary_raw.get("updated_at")
            backup_updated_at = backup_audit_payload.get("updated_at")
            if isinstance(raw_primary_ts, str) and backup_updated_at != raw_primary_ts:
                backup_parsed_at = self._parse_updated_at(backup_updated_at)
                if backup_parsed_at is not None and backup_parsed_at < primary_updated_at:
                    canonical_backup = {
                        "schema_version": _SCHEMA_VERSION,
                        "updated_at": raw_primary_ts,
                        "item_ids": list(basket.item_ids),
                    }
                    try:
                        _write_basket_payload(self._backup_path, canonical_backup)
                    except OSError:
                        pass

    recoverable_auxiliary_payloads = [
        (
            self._backup_path,
            _payload_as_plain_dict(backup_audit_payload)
            if isinstance(backup_audit_payload, AbstractMapping)
            else backup_audit_payload,
            backup_needs_audit_quarantine,
        ),
        (
            self._seed_state_path(),
            _payload_as_plain_dict(seed_raw_payload)
            if isinstance(seed_raw_payload, AbstractMapping)
            else seed_raw_payload,
            False,
        ),
    ]
    recoverable_empty_auxiliary_paths = [
        path
        for path, payload, needs_quarantine in recoverable_auxiliary_payloads
        if isinstance(payload, dict)
        and not needs_quarantine
        and _basket_payload_missing_item_ids_is_recoverable(payload)
    ]
    if recoverable_empty_auxiliary_paths:
        normalized_updated_at = _preferred_recovery_timestamp()
        canonical_auxiliary_payload = {
            "schema_version": _SCHEMA_VERSION,
            "updated_at": normalized_updated_at,
            "item_ids": list(basket.item_ids),
        }
        if primary_raw is None:
            try:
                self.save(basket, updated_at=normalized_updated_at)
            except OSError:
                pass
        else:
            try:
                _write_basket_payload(self._path, canonical_auxiliary_payload)
            except OSError:
                pass
        for auxiliary_path in recoverable_empty_auxiliary_paths:
            try:
                _write_basket_payload(auxiliary_path, canonical_auxiliary_payload)
            except OSError:
                pass
            source_payload = source_payloads.pop(auxiliary_path, None)
            if primary_raw is None and source_payload is not None:
                _sync_basket_payload_mapping_wrapper(
                    source_payload,
                    canonical_auxiliary_payload,
                    preserve_equivalent_raw_wrapper=True,
                )
        _restore_existing_corrupt_artifacts(self, corrupt_artifacts)
        self._unlink_if_exists(self._corrupt_path())
        self._unlink_if_exists(self._corrupt_path_for(self._backup_path))
        self._unlink_if_exists(self._corrupt_path_for(self._seed_state_path()))
        return _finish(basket)

    primary_is_list_like = isinstance(primary_raw, list)
    backup_is_list_like = isinstance(backup_raw, list)

    primary_needs_corrupt = False
    if primary_is_list_like:
        # A legacy-list primary whose entries are all strings (or ``None``) and
        # that salvages into a non-empty basket is the user's live state:
        # rewrite it canonically in place without leaving a ``.corrupt`` audit
        # artifact. Trimming whitespace and dropping blank/``None``/duplicate
        # string entries is routine normalization, not corruption. A non-string
        # scalar (e.g. an ``int`` coerced to its string form) or a structured
        # entry does lose fidelity on rewrite, so it is preserved for audit.
        # A competing backup also forces quarantine: the legacy list is then a
        # stale source that must be kept while the backup wins.
        primary_needs_corrupt = (
            not basket.item_ids
            or backup_raw is not None
            or any(entry is not None and not isinstance(entry, str) for entry in primary_raw)
        )
    elif isinstance(primary_raw, dict):
        primary_raw_item_ids = primary_raw.get("item_ids")
        primary_needs_corrupt = (
            force_primary_corrupt
            or (
                self._primary_item_ids_need_recovery(primary_raw)
                and not _basket_payload_missing_item_ids_is_recoverable(primary_raw)
            )
            or _basket_payload_has_whitespace_trimmed_item_ids(primary_raw)
            or (
                isinstance(primary_raw_item_ids, list)
                and self._has_dropped_item_ids(primary_raw_item_ids)
            )
        )
    if primary_sequence_materialized and backup_raw is None and basket.item_ids:
        primary_needs_corrupt = False
    if primary_needs_corrupt and primary_raw is not None:
        _write_basket_corrupt_snapshot(self, self._path, primary_raw)

    backup_needs_corrupt = False
    if backup_raw is not None:
        if backup_is_list_like:
            backup_needs_corrupt = len(backup_raw) > 0 and _basket_payload_has_whitespace_trimmed_item_ids(backup_raw)
        elif isinstance(backup_audit_payload, dict):
            backup_needs_corrupt = backup_needs_audit_quarantine
    if backup_needs_corrupt and backup_raw is not None:
        _write_basket_corrupt_snapshot(self, self._backup_path, backup_raw)
    if primary_is_list_like and backup_raw is not None:
        if backup_is_list_like and (len(backup_raw) > 0 or (primary_items is not None and len(primary_items) > 0)):
            _write_basket_corrupt_snapshot(self, self._backup_path, backup_raw)
        elif (
            isinstance(backup_audit_payload, dict)
            and backup_items is not None
            and primary_items is not None
            and len(backup_items) < len(primary_items)
        ):
            _write_basket_corrupt_snapshot(self, self._backup_path, backup_raw)

    primary_after = _snapshot_basket_raw_payload(self._path)
    backup_after = _snapshot_basket_raw_payload(self._backup_path)
    if (
        primary_raw is not None
        and isinstance(primary_after, dict)
        and primary_after.get("recovered_from") == "backup"
        and isinstance(backup_after, dict)
        and not (isinstance(backup_raw_payload, dict) and "recovered_from" in backup_raw_payload)
        and "recovered_from" not in backup_after
        and self._primary_item_ids_need_recovery(primary_raw)
        # Only stamp the backup with provenance when the primary carried a
        # present-but-malformed ``item_ids`` field. A primary that was missing
        # the field entirely recovers into a clean canonical backup mirror, so
        # the marker stays solely on the rewritten primary.
        and isinstance(_payload_as_plain_dict(primary_raw), dict)
        and "item_ids" in _payload_as_plain_dict(primary_raw)
    ):
        recovered_backup_payload = dict(backup_after)
        recovered_backup_payload["recovered_from"] = "backup"
        try:
            _write_basket_payload(self._backup_path, recovered_backup_payload)
        except OSError:
            pass
    if (
        primary_is_list_like
        and isinstance(primary_after, dict)
        and primary_after.get("recovered_from") == "backup"
        and isinstance(backup_after, dict)
        and "recovered_from" not in backup_after
    ):
        recovered_backup_payload = dict(backup_after)
        recovered_backup_payload["recovered_from"] = "backup"
        try:
            _write_basket_payload(self._backup_path, recovered_backup_payload)
        except OSError:
            pass
    if (
        primary_raw is not None
        and primary_is_list_like
        and isinstance(primary_after, dict)
        and "recovered_from" not in primary_after
        and isinstance(backup_audit_payload, dict)
        and isinstance(backup_after, dict)
        and _snapshot_basket_item_ids(backup_after) == _snapshot_basket_item_ids(backup_raw)
    ):
        raw_updated_at = backup_audit_payload.get("updated_at")
        if (
            isinstance(raw_updated_at, str)
            and self._parse_updated_at(raw_updated_at) is not None
            and not _basket_payload_has_whitespace_trimmed_item_ids(backup_raw)
        ):
            normalized_updated_at = _context_basket_store_recovery_timestamp(self, backup_raw)
            if normalized_updated_at is None and isinstance(primary_raw, dict):
                normalized_updated_at = self._parse_updated_at(primary_raw.get("updated_at"))
            if normalized_updated_at is None:
                normalized_updated_at = _now_iso()
            if backup_after.get("updated_at") != normalized_updated_at:
                restored_backup_payload = dict(backup_after)
                restored_backup_payload["updated_at"] = normalized_updated_at
                try:
                    _write_basket_payload(self._backup_path, restored_backup_payload)
                except OSError:
                    pass
    current_primary_after = _snapshot_basket_raw_payload(self._path)
    if (
        isinstance(primary_raw, AbstractMapping)
        and not isinstance(primary_raw, dict)
        and isinstance(primary_snapshot, dict)
        and "recovered_from" not in primary_snapshot
        and "item_ids" in primary_snapshot
        and _context_basket_store_recovery_timestamp(self, primary_snapshot) is not None
        and not (isinstance(current_primary_after, dict) and "recovered_from" in current_primary_after)
    ):
        canonical_primary_payload = dict(primary_snapshot)
        canonical_primary_payload["schema_version"] = _SCHEMA_VERSION
        canonical_primary_payload["updated_at"] = _context_basket_store_recovery_timestamp(self, primary_snapshot)
        canonical_primary_payload["item_ids"] = list(basket.item_ids)
        try:
            _write_basket_payload(self._path, canonical_primary_payload)
        except OSError:
            pass
    if (
        isinstance(primary_raw, dict)
        and isinstance(primary_after, dict)
        and isinstance(backup_audit_payload, dict)
        and "updated_at" in primary_raw
        and primary_raw.get("updated_at") is not None
        and not any(key not in _CANONICAL_DICT_KEYS for key in primary_raw)
        and not self._primary_item_ids_need_recovery(primary_raw)
        and "recovered_from" not in primary_after
        and "recovered_from" not in backup_after
        and primary_after.get("item_ids") == primary_raw.get("item_ids")
        and backup_after.get("item_ids") == backup_audit_payload.get("item_ids")
        and _snapshot_basket_item_ids(primary_after) == _snapshot_basket_item_ids(primary_raw)
        and _snapshot_basket_item_ids(backup_after) == _snapshot_basket_item_ids(backup_raw)
    ):
        raw_updated_at = backup_audit_payload.get("updated_at")
        if isinstance(raw_updated_at, str) and self._parse_updated_at(raw_updated_at) is not None:
            desired_updated_at = raw_updated_at
            if has_trailing_zulu(raw_updated_at.strip()):
                normalized_updated_at = _context_basket_store_recovery_timestamp(self, backup_audit_payload)
                if normalized_updated_at is not None:
                    desired_updated_at = normalized_updated_at
            if (
                backup_after.get("updated_at") != desired_updated_at
                and backup_after.get("updated_at") != primary_raw.get("updated_at")
            ):
                restored_backup_payload = dict(backup_after)
                restored_backup_payload["updated_at"] = desired_updated_at
                try:
                    _write_basket_payload(self._backup_path, restored_backup_payload)
                except OSError:
                    pass
    if (
        isinstance(primary_raw, dict)
        and isinstance(backup_audit_payload, dict)
        and "updated_at" in primary_raw
        and primary_raw.get("updated_at") is not None
        and any(key not in _CANONICAL_DICT_KEYS for key in primary_raw)
        and primary_items is not None
        and backup_items is not None
        and primary_items == backup_items
    ):
        normalized_updated_at = _context_basket_store_recovery_timestamp(self, backup_audit_payload)
        if normalized_updated_at is None and isinstance(primary_raw, dict):
            normalized_updated_at = self._parse_updated_at(primary_raw.get("updated_at"))
        if normalized_updated_at is None:
            normalized_updated_at = _now_iso()
        if backup_after.get("updated_at") != normalized_updated_at:
            restored_backup_payload = dict(backup_after)
            restored_backup_payload["updated_at"] = normalized_updated_at
            try:
                _write_basket_payload(self._backup_path, restored_backup_payload)
            except OSError:
                pass
    if (
        primary_raw is not None
        and isinstance(primary_after, dict)
        and self._primary_item_ids_need_recovery(primary_raw)
        and isinstance(backup_audit_payload, dict)
    ):
        normalized_updated_at = _preferred_recovery_timestamp()
        if primary_after.get("updated_at") != normalized_updated_at:
            repaired_primary_payload = dict(primary_after)
            repaired_primary_payload["updated_at"] = normalized_updated_at
            try:
                _write_basket_payload(self._path, repaired_primary_payload)
            except OSError:
                pass
    if (
        primary_needs_corrupt
        and primary_raw is not None
        and isinstance(primary_raw, dict)
        and isinstance(primary_raw.get("item_ids"), list)
        and self._has_dropped_item_ids(primary_raw.get("item_ids"))
        and isinstance(primary_after, dict)
        and primary_after.get("updated_at") == primary_raw.get("updated_at")
    ):
        # Primary had invalid item_id entries; the inner load rewrote it from
        # backup but preserved the old timestamp. Stamp a fresh time so callers
        # can detect the sanitization.
        repaired_primary_payload = dict(primary_after)
        repaired_primary_payload["updated_at"] = _now_iso()
        try:
            _write_basket_payload(self._path, repaired_primary_payload)
        except OSError:
            pass
    if not self._path.exists() and not self._backup_path.exists() and not basket.item_ids:
        try:
            self.save(basket)
        except OSError:
            pass
    _restore_existing_corrupt_artifacts(self, corrupt_artifacts)
    if not primary_needs_corrupt and not force_primary_corrupt and not backup_needs_corrupt:
        # A healthy load with no fresh quarantine should not leave stale corrupt
        # markers behind. Clear only the markers that pre-existed at load start
        # (captured in ``corrupt_artifacts``); markers written during this load by
        # the inner original load (e.g. ``_quarantine_unrecoverable_list_payload``)
        # are preserved for audit because they are absent from that snapshot.
        #
        # A primary/backup/seed marker is stale unless its source was a corruption
        # signal *at load start* -- the source existed yet failed to parse
        # (``*_raw is None`` for a path that existed when the load began). That
        # load-start state is what the marker attests to; re-reading the source in
        # this block would see the recovery rewrite instead and wrongly clear a
        # marker for a primary that was broken on entry (see
        # ``test_load_preserves_existing_basket_corrupt_artifact``). Orphaned
        # temp-staging markers have no surviving source after a healthy load, so
        # they are always stale here; markers freshly written this load are absent
        # from the snapshot below and survive for audit either way.
        preexisting_corrupt_paths = {path for path, _, _ in corrupt_artifacts}
        source_existed_at_load_start = {
            corrupt_path: source_existed for corrupt_path, source_existed, _ in corrupt_artifacts
        }

        def _source_corrupt_at_load_start(raw: object | None, corrupt_path: Path) -> bool:
            # The source attested to by ``corrupt_path`` was a corruption signal on
            # entry only if it existed then but did not parse. An absent source has
            # nothing to quarantine, and a source that parsed is healthy.
            return raw is None and source_existed_at_load_start.get(corrupt_path, False)

        clearable_corrupt_paths = []
        if not _source_corrupt_at_load_start(primary_raw, self._corrupt_path()):
            clearable_corrupt_paths.append(self._corrupt_path())
        if not _source_corrupt_at_load_start(backup_raw, self._corrupt_path_for(self._backup_path)):
            clearable_corrupt_paths.append(self._corrupt_path_for(self._backup_path))
        if not _source_corrupt_at_load_start(seed_raw, self._corrupt_path_for(self._seed_state_path())):
            clearable_corrupt_paths.append(self._corrupt_path_for(self._seed_state_path()))
        clearable_corrupt_paths.extend(
            (
                self._corrupt_path_for(self._tmp_path()),
                self._corrupt_path_for(self._backup_tmp_path()),
                self._corrupt_path_for(self._seed_tmp_path()),
            )
        )
        for corrupt_path in clearable_corrupt_paths:
            if corrupt_path in preexisting_corrupt_paths:
                self._unlink_if_exists(corrupt_path)
    if primary_raw is None and basket.item_ids:
        # Primary failed to parse at all (e.g. truncated JSON) — the original
        # load quarantined it during its own pass. If recovery from backup or
        # seed produced items, the corrupt artifact is stale and should be
        # removed so callers see a clean state.
        # Exception: binary-corrupt files (e.g. invalid UTF-8) contain
        # irreplaceable bytes and must be preserved for audit.
        corrupt_path = self._corrupt_path()
        should_remove_corrupt = True
        if corrupt_path.exists():
            try:
                corrupt_path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                should_remove_corrupt = False
        if should_remove_corrupt:
            self._unlink_if_exists(corrupt_path)
    if _basket_payload_missing_item_ids_is_recoverable(primary_raw):
        # Recoverable empty-envelope rewrites should not leave either corrupt
        # sibling behind unless the backup itself is a recovered or otherwise
        # meaningful audit artifact.
        self._unlink_if_exists(self._corrupt_path())
        if backup_raw is None or _basket_payload_missing_item_ids_is_recoverable(backup_raw):
            self._unlink_if_exists(self._corrupt_path_for(self._backup_path))
    if _basket_payload_missing_item_ids_is_recoverable(backup_raw):
        self._unlink_if_exists(self._corrupt_path_for(self._backup_path))
    return _finish(basket)


def _context_basket_store_save(
    self: ContextBasketStore,
    basket: ContextBasket,
    recovered_from: str | None = None,
    refresh_backup: bool = False,
    updated_at: str | None = None,
    preserve_primary_corrupt: bool = False,
    preserve_backup_corrupt: bool = False,
    preserve_seed_corrupt: bool = False,
) -> None:
    _reject_basket_state_root_alias(self._path.parent)
    preserve_primary_corrupt = preserve_primary_corrupt or self._corrupt_path().exists()
    preserve_backup_corrupt = preserve_backup_corrupt or self._corrupt_path_for(self._backup_path).exists()
    preserve_seed_corrupt = preserve_seed_corrupt or self._corrupt_path_for(self._seed_state_path()).exists()
    corrupt_artifacts = _snapshot_existing_corrupt_artifacts(self)
    if updated_at is None:
        for candidate_path in (
            self._path,
            self._corrupt_path(),
            self._backup_path,
            self._corrupt_path_for(self._backup_path),
        ):
            candidate_payload, _ = self._load_payload(candidate_path)
            if candidate_payload is None:
                continue
            updated_at = self._payload_updated_at(candidate_payload)
            if updated_at is not None:
                break
    _ORIGINAL_CONTEXT_BASKET_STORE_SAVE(
        self,
        basket,
        recovered_from=recovered_from,
        refresh_backup=refresh_backup,
        updated_at=updated_at,
        preserve_primary_corrupt=preserve_primary_corrupt,
        preserve_backup_corrupt=preserve_backup_corrupt,
        preserve_seed_corrupt=preserve_seed_corrupt,
    )
    # The seed file is a local last-resort fallback snapshot, not a provenance
    # record. When a backup-refresh failure during recovery falls back to the
    # seed, the rewritten payload can inherit the ``recovered_from`` marker from
    # the recovered state; strip it so the seed stays a clean canonical mirror
    # (the primary keeps the marker). The live seed never carries provenance.
    seed_path = self._seed_state_path()
    if seed_path.exists():
        seed_payload = _load_json_payload(seed_path)
        if isinstance(seed_payload, dict) and "recovered_from" in seed_payload:
            cleaned_seed_payload = {
                key: value for key, value in seed_payload.items() if key != "recovered_from"
            }
            try:
                _write_basket_payload(seed_path, cleaned_seed_payload)
            except OSError:
                pass
    for legacy_tmp_path in _context_basket_legacy_tmp_paths(self):
        _quarantine_stale_basket_temp_artifact(legacy_tmp_path)
    _context_basket_store_sync_temp_source_payload(self)
    try:
        record: dict[str, object] = {
            "event": "save",
            # Emit the canonical ``+00:00`` offset (the ``utc_now_iso`` contract)
            # rather than a ``Z`` suffix. Every store's audit log then shares one
            # timestamp spelling, and readers parse it with ``fromisoformat``
            # directly instead of stripping ``Z`` first the way the recovery
            # parsers in this module otherwise must.
            "timestamp": utc_now_iso(),
            "basket_id": None,
            "item_ids": list(basket.item_ids),
        }
        if recovered_from is not None:
            record["recovered_from"] = recovered_from
        append_audit_record(audit_log_path(self._path, self.__class__.__name__), record)
    except Exception:  # pragma: no cover - audit logging must not block persistence
        pass
    _restore_existing_corrupt_artifacts(self, corrupt_artifacts)


def _context_basket_store_quarantine_path(self: ContextBasketStore, path: Path) -> None:
    _quarantine_corrupt_artifact(Path(path), self._corrupt_path_for(Path(path)))


def _context_basket_store_quarantine_missing_item_ids_payload(
    self: ContextBasketStore,
    path: Path,
    payload: object,
) -> bool:
    original_payload = payload
    if _basket_payload_missing_item_ids_is_recoverable(payload):
        if isinstance(payload, AbstractMapping) and type(payload) is not dict:
            materialized_payload = _payload_as_plain_dict(payload)
            if materialized_payload is not None:
                materialized_payload["item_ids"] = []
                _sync_basket_payload_mapping_wrapper(
                    payload,
                    _safe_json_value(materialized_payload),
                    preserve_equivalent_raw_wrapper=True,
                )
        return False
    if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            self._quarantine_path(path)
            return True
    if isinstance(payload, dict) and "item_ids" not in payload:
        if isinstance(original_payload, AbstractMapping) and type(original_payload) is not dict:
            _sync_basket_payload_mapping_wrapper(
                original_payload,
                _safe_json_value({key: value for key, value in payload.items() if key != "recovered_from"}),
            )
        self._quarantine_path(path)
        return True
    return False


def _context_basket_store_is_loadable_payload(self: ContextBasketStore, payload: object) -> bool:
    if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return False
    if isinstance(payload, list):
        return self._parse_item_ids(payload) is not None
    if not isinstance(payload, dict):
        return False
    if "item_ids" in payload and self._parse_item_ids(payload.get("item_ids")) is None:
        return False
    return True


def _context_basket_store_is_supported_payload(self: ContextBasketStore, payload: object) -> bool:
    if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return False
    if _ORIGINAL_CONTEXT_BASKET_STORE_IS_SUPPORTED_PAYLOAD(self, payload):
        return True
    if not isinstance(payload, dict) or "updated_at" not in payload:
        return False
    raw_updated_at = payload.get("updated_at")
    payload_without_updated_at = dict(payload)
    payload_without_updated_at.pop("updated_at", None)
    if isinstance(raw_updated_at, str) and not raw_updated_at.strip():
        return _ORIGINAL_CONTEXT_BASKET_STORE_IS_SUPPORTED_PAYLOAD(self, payload_without_updated_at)
    if "schema_version" in payload and self._parse_schema_version(payload) is None:
        return False
    if _basket_payload_is_rewriteable_without_updated_at(payload):
        return True
    return False


def _context_basket_store_backup_needs_audit_quarantine(
    self: ContextBasketStore,
    payload: dict[str, object] | list[object] | None,
) -> bool:
    if payload is None:
        return False
    if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return True
    if isinstance(payload, list):
        return self._legacy_list_payload_has_dropped_item_ids(payload)
    if not isinstance(payload, dict):
        return True
    if "recovered_from" in payload and self._parse_updated_at(payload.get("updated_at")) is None:
        return True
    raw_updated_at = payload.get("updated_at")
    if "updated_at" not in payload or raw_updated_at is None:
        return False
    if isinstance(raw_updated_at, str) and not raw_updated_at.strip():
        return False
    if "item_ids" not in payload:
        return not _basket_payload_missing_item_ids_is_recoverable(payload)
    raw_item_ids = payload.get("item_ids")
    if isinstance(raw_item_ids, list) and self._legacy_list_payload_has_dropped_item_ids(raw_item_ids):
        return True
    return not self._is_supported_payload(payload)


def _context_basket_store_primary_item_ids_need_recovery(
    self: ContextBasketStore,
    payload: dict[str, object] | list[object] | None,
) -> bool:
    if isinstance(payload, AbstractMapping) and not isinstance(payload, dict):
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return True
    if isinstance(payload, dict):
        if "item_ids" not in payload:
            return True
        raw_item_ids = payload.get("item_ids")
        if isinstance(raw_item_ids, tuple) and not raw_item_ids:
            return False
        parsed_item_ids = self._parse_item_ids(raw_item_ids)
        if parsed_item_ids is None:
            return True
        return not parsed_item_ids and self._has_dropped_item_ids(raw_item_ids)
    if isinstance(payload, list):
        return not payload
    return False


def _context_basket_store_write_backup_payload(
    self: ContextBasketStore,
    payload: dict[str, object],
) -> bool:
    current_backup_payload, _ = self._load_payload(self._backup_path)
    canonical_payload = self._backup_payload(payload)
    current_backup_payload = _payload_as_plain_dict(current_backup_payload)
    if current_backup_payload is not None and "recovered_from" not in current_backup_payload:
        backup_timestamp = _context_basket_store_recovery_timestamp(self, current_backup_payload)
        if backup_timestamp is not None:
            canonical_payload["updated_at"] = backup_timestamp
    try:
        _write_basket_payload(self._backup_path, canonical_payload)
    except OSError:
        return False
    return True


def _context_basket_store_write_backup(self: ContextBasketStore) -> bool:
    if self._path.is_symlink():
        self._quarantine_invalid_file()
        return False
    if not self._path.exists():
        return False
    if not self._is_valid_payload(self._path):
        return False
    try:
        payload = _load_json_payload(self._path)
    except (json.JSONDecodeError, OSError):
        return False
    if not isinstance(payload, dict):
        return False
    return self._write_backup_payload(payload)


ContextBasketStore._parse_item_ids = _context_basket_store_parse_item_ids  # type: ignore[assignment]
ContextBasketStore._normalize_item_id = _context_basket_store_normalize_item_id  # type: ignore[assignment]
ContextBasketStore._load_payload = _context_basket_store_load_payload  # type: ignore[assignment]
ContextBasketStore._prefer_recovery_payload = _context_basket_store_prefer_recovery_payload  # type: ignore[assignment]
ContextBasketStore.load = _context_basket_store_load  # type: ignore[assignment]
ContextBasketStore.save = _context_basket_store_save  # type: ignore[assignment]
ContextBasketStore._quarantine_path = _context_basket_store_quarantine_path  # type: ignore[assignment]
ContextBasketStore._quarantine_missing_item_ids_payload = _context_basket_store_quarantine_missing_item_ids_payload  # type: ignore[assignment]
ContextBasketStore._is_loadable_payload = _context_basket_store_is_loadable_payload  # type: ignore[assignment]
ContextBasketStore._is_supported_payload = _context_basket_store_is_supported_payload  # type: ignore[assignment]
ContextBasketStore._backup_needs_audit_quarantine = _context_basket_store_backup_needs_audit_quarantine  # type: ignore[assignment]
ContextBasketStore._primary_item_ids_need_recovery = _context_basket_store_primary_item_ids_need_recovery  # type: ignore[assignment]
ContextBasketStore._write_backup = _context_basket_store_write_backup  # type: ignore[assignment]
ContextBasketStore._write_backup_payload = _context_basket_store_write_backup_payload  # type: ignore[assignment]


def _context_basket_store_parse_updated_at(self: ContextBasketStore, value: object) -> str | None:
    return _parse_updated_at(value)


ContextBasketStore._parse_updated_at = _context_basket_store_parse_updated_at  # type: ignore[assignment]


def _context_basket_store_payload_updated_at(self: ContextBasketStore, payload: object) -> str | None:
    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return None
    return self._parse_updated_at(payload.get("updated_at"))


ContextBasketStore._payload_updated_at = _context_basket_store_payload_updated_at  # type: ignore[assignment]


def _sorted_items(self: ContextBasketStore) -> list[str]:
    """Return the current basket item ids without rewriting on-disk state.

    This mirrors the recovery-aware snapshot behavior used by the context-set
    store: a clean primary payload should keep its own item ids, while a
    recoverable legacy list can still defer to a richer backup. Recovered
    primaries are treated as audit artefacts instead of canonical state.
    """

    primary_payload = _snapshot_basket_payload(_snapshot_basket_raw_payload(self._path))
    basket_item_ids = _snapshot_basket_item_ids(primary_payload)
    if isinstance(primary_payload, dict) and "recovered_from" in primary_payload:
        basket_item_ids = None
    if basket_item_ids is not None:
        if isinstance(primary_payload, list):
            if (
                basket_item_ids
                and len(basket_item_ids) == len(primary_payload)
                and not _record_item_ids_need_audit_quarantine(primary_payload)
            ):
                backup_payload = _snapshot_basket_payload(_snapshot_basket_raw_payload(self._backup_path))
                backup_item_ids = _snapshot_basket_item_ids(backup_payload)
                if (
                    isinstance(backup_payload, dict)
                    and backup_item_ids is not None
                    and self._backup_needs_audit_quarantine(backup_payload) is False
                ):
                    primary_item_set = set(basket_item_ids)
                    backup_item_set = set(backup_item_ids)
                    # A richer dict-shaped backup should win even when the
                    # legacy primary list is already clean.
                    if backup_item_set.issuperset(primary_item_set) and len(backup_item_ids) > len(basket_item_ids):
                        return sorted(backup_item_ids)
                return sorted(basket_item_ids)
            if basket_item_ids:
                backup_payload = _snapshot_basket_payload(_snapshot_basket_raw_payload(self._backup_path))
                backup_item_ids = _snapshot_basket_item_ids(backup_payload)
                if backup_item_ids is None or self._backup_needs_audit_quarantine(backup_payload):
                    return sorted(basket_item_ids)
                primary_item_set = set(basket_item_ids)
                backup_item_set = set(backup_item_ids)
                if (
                    backup_item_set.issubset(primary_item_set)
                    and len(basket_item_ids) > len(backup_item_ids)
                ):
                    return sorted(basket_item_ids)
                if primary_item_set == backup_item_set:
                    return sorted(basket_item_ids)
                return sorted(backup_item_ids)
        elif isinstance(primary_payload, dict):
            primary_updated_at = (
                self._parse_updated_at(primary_payload.get("updated_at"))
                if "updated_at" in primary_payload
                else None
            )
            if primary_updated_at is None:
                backup_payload = _snapshot_basket_payload(_snapshot_basket_raw_payload(self._backup_path))
                backup_item_ids = _snapshot_basket_item_ids(backup_payload)
                if backup_item_ids is not None and not self._backup_needs_audit_quarantine(backup_payload):
                    primary_item_set = set(basket_item_ids)
                    backup_item_set = set(backup_item_ids)
                    if backup_item_set.issuperset(primary_item_set) and len(backup_item_ids) > len(basket_item_ids):
                        return sorted(backup_item_ids)
                return sorted(basket_item_ids)
            backup_payload = _snapshot_basket_payload(_snapshot_basket_raw_payload(self._backup_path))
            backup_item_ids = _snapshot_basket_item_ids(backup_payload)
            if (
                isinstance(backup_payload, list)
                and backup_item_ids is not None
                and self._backup_needs_audit_quarantine(backup_payload) is False
            ):
                primary_item_set = set(basket_item_ids)
                backup_item_set = set(backup_item_ids)
                if backup_item_set.issuperset(primary_item_set) and len(backup_item_ids) > len(basket_item_ids):
                    return sorted(backup_item_ids)
            if not _basket_payload_needs_audit_quarantine(primary_payload):
                backup_payload = _snapshot_basket_payload(_snapshot_basket_raw_payload(self._backup_path))
                backup_item_ids = _snapshot_basket_item_ids(backup_payload)
                if (
                    isinstance(backup_payload, list)
                    and backup_item_ids is not None
                    and self._backup_needs_audit_quarantine(backup_payload) is False
                ):
                    primary_item_set = set(basket_item_ids)
                    backup_item_set = set(backup_item_ids)
                    if backup_item_set.issuperset(primary_item_set) and len(backup_item_ids) > len(basket_item_ids):
                        return sorted(backup_item_ids)
                return sorted(basket_item_ids)

    backup_payload = _snapshot_basket_payload(_snapshot_basket_raw_payload(self._backup_path))
    if isinstance(backup_payload, dict) and "recovered_from" in backup_payload:
        # Recovered backups are audit artefacts, not canonical snapshot
        # sources.
        backup_item_ids = None
    else:
        backup_item_ids = _snapshot_basket_item_ids(backup_payload)
    if backup_item_ids is None:
        seed_payload = _snapshot_basket_payload(_snapshot_basket_raw_payload(self._seed_state_path()))
        if isinstance(seed_payload, dict) and "recovered_from" in seed_payload:
            seed_item_ids = None
        else:
            seed_item_ids = _snapshot_basket_item_ids(seed_payload)
        if seed_item_ids is not None:
            return sorted(seed_item_ids)
        if basket_item_ids is None:
            return []
        return sorted(basket_item_ids)
    return sorted(backup_item_ids)


ContextBasketStore.sorted_items = _sorted_items  # type: ignore[assignment]


_ORIGINAL_CONTEXT_BASKET_STORE_CLEAR = ContextBasketStore.clear


def _context_basket_store_clear_with_quarantine_sweep(self: ContextBasketStore) -> None:
    _ORIGINAL_CONTEXT_BASKET_STORE_CLEAR(self)
    audit_path = self._path.parent / f"{self.__class__.__name__}_audit.jsonl"
    # Remove the live audit log whether it is a file, symlink, or a directory
    # squatting on the path: a bare ``unlink`` swallows ``IsADirectoryError`` and
    # would strand the directory for the next append to quarantine, so route
    # through the shared remover that also handles the non-file case.
    _remove_live_audit_log(audit_path)
    # A blocking alias on the audit-log path is quarantined to the sibling
    # ``{audit}.corrupt.jsonl`` family by ``audit._quarantine_blocking_audit_artifact``.
    # Unlinking only the live ``.jsonl`` would strand that quarantine, so
    # ``is_clean_state`` stays false after a reset that promises to remove all
    # persisted artifacts. Sweep the family from the producer's spelling.
    _clear_corrupt_artifact_family(_audit_corrupt_path(audit_path))
    for path in (
        self._path,
        self._backup_path,
        self._seed_state_path(),
        self._tmp_path(),
        self._backup_tmp_path(),
        self._seed_tmp_path(),
    ):
        _clear_corrupt_artifact_family(self._corrupt_path_for(path))
    # Legacy ``.tmp.json`` temp artifacts are stale-quarantined under their full
    # name (``{legacy}.stale.corrupt.json``) by _quarantine_stale_basket_temp_artifact,
    # so the family stem is the legacy name itself -- not the collapsed
    # ``.tmp`` stem that _corrupt_path_for would derive. Sweep each legacy
    # family with a corrupt path that preserves the full legacy name so those
    # stale quarantines (and their numbered collisions) are cleared instead of
    # stranded for a re-run to trip over.
    for legacy_tmp_path in _context_basket_legacy_tmp_paths(self):
        _clear_corrupt_artifact_family(
            legacy_tmp_path.with_name(f"{legacy_tmp_path.name}.corrupt.json")
        )


ContextBasketStore.clear = _context_basket_store_clear_with_quarantine_sweep
