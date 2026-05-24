from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone

UTC = timezone.utc
from pathlib import Path

from src.qual.context.basket import ContextBasket

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
        tmp_payload, tmp_quarantined = self._load_payload(self._tmp_path())
        backup_tmp_payload, backup_tmp_quarantined = self._load_payload(self._backup_tmp_path())
        backup_payload, backup_quarantined = self._load_payload(self._backup_path)
        seed_tmp_payload, seed_tmp_quarantined = self._load_payload(self._seed_tmp_path())
        seed_payload, seed_quarantined = self._load_payload(self._seed_state_path())
        preserve_temporary_corrupt = tmp_quarantined or backup_tmp_quarantined or seed_tmp_quarantined
        tmp_missing_item_ids = self._quarantine_missing_item_ids_payload(self._tmp_path(), tmp_payload)
        backup_tmp_missing_item_ids = self._quarantine_missing_item_ids_payload(
            self._backup_tmp_path(),
            backup_tmp_payload,
        )
        preserve_backup_corrupt = self._quarantine_missing_item_ids_payload(self._backup_path, backup_payload)
        seed_tmp_missing_item_ids = self._quarantine_missing_item_ids_payload(self._seed_tmp_path(), seed_tmp_payload)
        preserve_seed_corrupt = self._quarantine_missing_item_ids_payload(self._seed_state_path(), seed_payload)
        preserve_temporary_corrupt = (
            preserve_temporary_corrupt
            or tmp_missing_item_ids
            or backup_tmp_missing_item_ids
            or seed_tmp_missing_item_ids
        )
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
                        preserve_temporary=preserve_temporary_corrupt,
                    )
                    self._clear_temporary_files()
                    return ContextBasket()
        else:
            self._clear_quarantine_file(
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
                preserve_temporary=preserve_temporary_corrupt,
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
            if self._backup_needs_audit_quarantine(backup_payload):
                self._quarantine_invalid_backup()
                preserve_backup_corrupt = True
            if self._backup_needs_audit_quarantine(seed_payload):
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
                preserve_temporary_corrupt=preserve_temporary_corrupt,
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
                preserve_temporary_corrupt=preserve_temporary_corrupt,
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
                preserve_temporary_corrupt=preserve_temporary_corrupt,
            )
            if not backup_written:
                self._write_seed(self._backup_payload(payload) if isinstance(payload, dict) else payload)
        else:
            self._clear_recovery_artifacts(
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
                preserve_temporary_corrupt=preserve_temporary_corrupt,
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
        preserve_temporary_corrupt: bool = False,
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
            tmp = self._tmp_path()
            tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
            try:
                tmp.replace(self._path)
            except OSError:
                self._unlink_if_exists(tmp)
                raise
            backup_payload = self._backup_payload(payload)
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
            self._clear_recovery_artifacts(
                preserve_seed=not backup_written,
                preserve_temporary_corrupt=preserve_temporary_corrupt,
            )
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
            self._clear_recovery_artifacts(
                preserve_seed=not backup_written,
                preserve_temporary_corrupt=preserve_temporary_corrupt,
            )
            return
        payload = {
            "schema_version": _SCHEMA_VERSION,
            "updated_at": updated_at or datetime.now(UTC).isoformat(),
            "item_ids": list(basket.item_ids),
        }
        if normalized_recovered_from is not None:
            payload["recovered_from"] = normalized_recovered_from
        tmp = self._tmp_path()
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        try:
            tmp.replace(self._path)
        except OSError:
            self._unlink_if_exists(tmp)
            raise
        backup_payload = self._backup_payload(payload)
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
            preserve_temporary_corrupt=preserve_temporary_corrupt,
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
        preserve_temporary_corrupt: bool = False,
    ) -> None:
        self._clear_quarantine_file(
            preserve_primary_corrupt=preserve_primary_corrupt,
            preserve_backup_corrupt=preserve_backup_corrupt,
            preserve_seed_corrupt=preserve_seed_corrupt,
            preserve_temporary=preserve_temporary_corrupt,
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
            payload = json.loads(path.read_text(encoding="utf-8"))
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
        payload = json.loads(self._path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return False
        return self._write_backup_payload(payload)

    def _write_backup_payload(self, payload: dict[str, object]) -> bool:
        tmp = self._backup_path.with_suffix(".tmp")
        canonical_payload = self._backup_payload(payload)
        try:
            tmp.write_text(json.dumps(canonical_payload, indent=2, sort_keys=True), encoding="utf-8")
            tmp.replace(self._backup_path)
        except OSError:
            self._unlink_if_exists(tmp)
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
        tmp = seed.with_suffix(".tmp")
        try:
            tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
            tmp.replace(seed)
        except OSError:
            self._unlink_if_exists(tmp)

    def _is_valid_payload(self, path: Path) -> bool:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
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
        if self._has_unknown_fields(payload):
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
