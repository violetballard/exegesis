from __future__ import annotations

import json
import math
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

UTC = timezone.utc
from pathlib import Path

_SCHEMA_VERSION = 1
_CANONICAL_DICT_KEYS = {"schema_version", "updated_at", "context_sets", "recovered_from"}
_CANONICAL_RECORD_KEYS = {"context_set_id", "name", "item_ids", "created_at", "updated_at"}


@dataclass
class ContextSetRecord:
    context_set_id: str
    name: str
    item_ids: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def normalize(self) -> None:
        self.context_set_id = self._normalize_identifier(self.context_set_id)
        self.name = self._normalize_name(self.name)
        self.item_ids = self._normalize_item_ids(self.item_ids)
        normalized_created_at = self._normalize_timestamp(self.created_at)
        normalized_updated_at = self._normalize_timestamp(self.updated_at)
        self.created_at, self.updated_at = self._normalize_record_timestamps(
            normalized_created_at,
            normalized_updated_at,
        )

    @staticmethod
    def _normalize_text_scalar(value: object) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, bool):
            return ""
        if isinstance(value, int):
            return str(value).strip()
        if isinstance(value, float):
            if not math.isfinite(value):
                return ""
            return str(value).strip()
        return ""

    @classmethod
    def _normalize_identifier(cls, value: object) -> str:
        return cls._normalize_text_scalar(value)

    @staticmethod
    def _normalize_name(value: object) -> str:
        return ContextSetRecord._normalize_text_scalar(value)

    @staticmethod
    def _normalize_item_id(value: object) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, bool):
            return ""
        if isinstance(value, int):
            return str(value).strip()
        if isinstance(value, float):
            if not math.isfinite(value):
                return ""
            return str(value).strip()
        return ""

    @classmethod
    def _normalize_item_ids(cls, item_ids: object) -> list[str]:
        if not isinstance(item_ids, list):
            return []
        out: list[str] = []
        seen: set[str] = set()
        for raw in item_ids:
            item_id = cls._normalize_item_id(raw)
            if not item_id or item_id in seen:
                continue
            out.append(item_id)
            seen.add(item_id)
        return out

    @classmethod
    def _parse_item_ids(cls, item_ids: object) -> list[str]:
        if isinstance(item_ids, list):
            return cls._normalize_item_ids(item_ids)
        normalized = cls._normalize_item_id(item_ids)
        if normalized:
            return [normalized]
        return []

    @staticmethod
    def _normalize_timestamp(value: object) -> str:
        if not isinstance(value, str):
            return ""
        candidate = value.strip()
        if not candidate:
            return ""
        try:
            parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
        except ValueError:
            return ""
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC).isoformat()

    @staticmethod
    def _normalize_record_timestamps(created_at: str, updated_at: str) -> tuple[str, str]:
        if created_at and not updated_at:
            return created_at, created_at
        if updated_at and not created_at:
            return updated_at, updated_at
        if not created_at or not updated_at:
            return created_at, updated_at
        try:
            created_at_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            updated_at_dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        except ValueError:
            return created_at, updated_at
        if updated_at_dt < created_at_dt:
            return created_at, created_at
        return created_at, updated_at


class ContextSetStore:
    """Persist named context sets for excerpt selection and attachment workflows."""

    def __init__(self, root_dir: Path) -> None:
        self._path = root_dir / "context_sets.json"
        self._backup_path = root_dir / "context_sets.bak.json"
        self._seed_path = root_dir / "context_sets.seed.json"

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

    def _quarantine_missing_context_sets_payload(self, path: Path, payload: object) -> bool:
        if isinstance(payload, dict) and "context_sets" not in payload:
            self._quarantine_path(path)
            return True
        return False

    def load(self) -> list[ContextSetRecord]:
        primary_missing = not self._path.exists()
        backup_missing = not self._backup_path.exists()
        primary_payload, primary_quarantined = self._load_payload(self._path)
        tmp_payload, tmp_quarantined = self._load_payload(self._tmp_path())
        backup_tmp_payload, backup_tmp_quarantined = self._load_payload(self._backup_tmp_path())
        backup_payload, backup_quarantined = self._load_payload(self._backup_path)
        seed_tmp_payload, seed_tmp_quarantined = self._load_payload(self._seed_tmp_path())
        seed_payload, seed_quarantined = self._load_payload(self._seed_state_path())
        preserve_temporary_corrupt = tmp_quarantined or backup_tmp_quarantined or seed_tmp_quarantined
        tmp_missing_context_sets = self._quarantine_missing_context_sets_payload(self._tmp_path(), tmp_payload)
        backup_tmp_missing_context_sets = self._quarantine_missing_context_sets_payload(
            self._backup_tmp_path(),
            backup_tmp_payload,
        )
        preserve_backup_corrupt = self._quarantine_missing_context_sets_payload(self._backup_path, backup_payload)
        seed_tmp_missing_context_sets = self._quarantine_missing_context_sets_payload(
            self._seed_tmp_path(),
            seed_tmp_payload,
        )
        preserve_seed_corrupt = self._quarantine_missing_context_sets_payload(self._seed_state_path(), seed_payload)
        preserve_temporary_corrupt = (
            preserve_temporary_corrupt
            or tmp_missing_context_sets
            or backup_tmp_missing_context_sets
            or seed_tmp_missing_context_sets
        )
        preserve_backup_corrupt = (
            self._quarantine_unrecoverable_list_payload(self._backup_path, backup_payload) or preserve_backup_corrupt
        )
        preserve_seed_corrupt = (
            self._quarantine_unrecoverable_list_payload(self._seed_state_path(), seed_payload) or preserve_seed_corrupt
        )

        primary_needs_quarantine = self._primary_context_sets_need_recovery(primary_payload)
        if not primary_needs_quarantine and isinstance(primary_payload, dict) and self._has_unknown_fields(
            primary_payload
        ):
            primary_needs_quarantine = True
        if isinstance(primary_payload, list) and self._legacy_list_payload_has_dropped_records(primary_payload):
            primary_needs_quarantine = True
        if (
            not primary_needs_quarantine
            and isinstance(primary_payload, dict)
            and "context_sets" in primary_payload
            and not self._has_context_set_records(primary_payload)
            and not self._is_supported_payload(primary_payload)
        ):
            primary_needs_quarantine = True
        if primary_needs_quarantine:
            self._quarantine_invalid_file()

        payload: dict[str, object] | list[object] | None
        recovered_source: str | None
        materialized_empty_state = False
        if primary_needs_quarantine:
            if isinstance(primary_payload, list):
                primary_records = self._parse_context_sets(primary_payload)
                if primary_records:
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
                    if payload is None or not self._has_context_set_records(payload):
                        payload = primary_payload
                        recovered_source = None
            else:
                raw_context_sets = primary_payload.get("context_sets")
                parsed_records = self._parse_context_sets(raw_context_sets)
                has_explicit_empty_context_sets = isinstance(raw_context_sets, list) and not raw_context_sets
                has_salvageable_context_sets = parsed_records is not None and bool(parsed_records)
                if has_explicit_empty_context_sets:
                    recovery_payload, recovery_source = self._prefer_recovery_payload(
                        tmp_payload,
                        backup_tmp_payload,
                        backup_payload,
                        seed_tmp_payload,
                        seed_payload,
                    )
                    if recovery_payload is not None and self._has_context_set_records(recovery_payload):
                        payload = recovery_payload
                        recovered_source = recovery_source
                    else:
                        payload = primary_payload
                        recovered_source = None
                elif has_salvageable_context_sets:
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
                        if primary_quarantined or backup_quarantined or seed_quarantined:
                            # Keep a canonical empty context-set file on disk
                            # when quarantine found only malformed state.
                            payload = []
                            recovered_source = None
                            materialized_empty_state = True
                        else:
                            payload = primary_payload
                            recovered_source = None
        elif isinstance(primary_payload, list):
            primary_records = self._parse_context_sets(primary_payload)
            if primary_records:
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
                if payload is None or not self._has_context_set_records(payload):
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
                if recovery_payload is not None and self._has_context_set_records(recovery_payload):
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
                    # Keep a canonical empty context-set file on disk when
                    # quarantine found only malformed state.
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
                    return []
        else:
            self._clear_quarantine_file(
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
                preserve_temporary=preserve_temporary_corrupt,
            )
            self._clear_temporary_files()
            return []

        should_rewrite = False
        rewrite_empty_recovery = False
        explicit_empty_recovery = self._is_empty_recovery_payload(payload) and self._has_explicit_empty_recovery_payload(
            payload
        )
        audit_recovered_source = recovered_source
        rewrite_timestamp = datetime.now(UTC).isoformat()
        records: list[ContextSetRecord]
        if explicit_empty_recovery:
            # Materialize empty canonical state when it is the only usable
            # payload, but explicit empty recovery should not claim provenance
            # on the rewritten payload.
            rewrite_empty_recovery = recovered_source is not None or primary_payload is None
            if recovered_source is not None:
                recovered_source = None
        if isinstance(payload, list):
            parsed_records = self._parse_context_sets(payload)
            if parsed_records is None:
                self._discard_payload_source(recovered_source)
                return []
            records = self._normalize_records(parsed_records)
            if records and self._records_need_timestamp_backfill(records):
                records = self._backfill_record_timestamps(records, rewrite_timestamp)
                should_rewrite = True
            # Promote legacy list payloads into the canonical dict format even
            # when their record contents are already normalized.
            should_rewrite = True
        elif isinstance(payload, dict):
            schema_version = self._parse_schema_version(payload)
            if "context_sets" not in payload:
                records = []
                should_rewrite = True
            else:
                raw_context_sets = payload.get("context_sets")
                parsed_records = self._parse_context_sets(raw_context_sets)
                if parsed_records is None:
                    records = []
                    should_rewrite = True
                else:
                    records = self._normalize_records(parsed_records)
                    should_rewrite = (
                        should_rewrite
                        or schema_version != _SCHEMA_VERSION
                        or self._records_need_rewrite(raw_context_sets, parsed_records)
                        or records != parsed_records
                    )
            if records and self._records_need_timestamp_backfill(records):
                records = self._backfill_record_timestamps(records, rewrite_timestamp)
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
            return []

        cleanup_timestamp = self._recovery_marker_cleanup_timestamp(payload, records)
        if cleanup_timestamp is not None:
            rewrite_timestamp = cleanup_timestamp
        recovered_from = self._recovery_marker(
            primary_unavailable=primary_missing or primary_payload is None or recovered_source is not None,
            recovered_source=recovered_source,
        )
        should_rewrite = should_rewrite or rewrite_empty_recovery
        recovered_persisted_missing_context_sets = (
            isinstance(payload, dict)
            and "context_sets" not in payload
            and recovered_source in {"backup", "seed"}
        )
        preserve_primary_corrupt = bool(
            primary_needs_quarantine
            and primary_payload is not None
            and isinstance(primary_payload, dict)
        )
        preserve_primary_corrupt = preserve_primary_corrupt or (materialized_empty_state and primary_quarantined)
        preserve_backup_corrupt = bool(
            preserve_backup_corrupt
            or backup_quarantined
            or (recovered_source == "backup" and recovered_persisted_missing_context_sets)
        )
        preserve_seed_corrupt = bool(
            preserve_seed_corrupt
            or seed_quarantined
            or (recovered_source == "seed" and recovered_persisted_missing_context_sets)
        )
        if isinstance(primary_payload, list) and (
            not self._has_context_set_records(primary_payload)
            or self._list_payload_needs_audit_quarantine(primary_payload)
        ):
            # Keep the original malformed legacy list available for audit when
            # it cannot contribute cleanly recoverable context set records.
            preserve_primary_corrupt = True
        if (
            audit_recovered_source == "backup"
            and isinstance(backup_payload, list)
            and self._list_payload_needs_audit_quarantine(backup_payload)
        ):
            self._quarantine_invalid_backup()
            preserve_backup_corrupt = True
        if (
            audit_recovered_source == "seed"
            and isinstance(seed_payload, list)
            and self._list_payload_needs_audit_quarantine(seed_payload)
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
            self.save(
                records,
                recovered_from=recovered_from,
                refresh_backup=True,
                preserve_primary_corrupt=preserve_primary_corrupt,
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
                preserve_temporary_corrupt=preserve_temporary_corrupt,
                updated_at=rewrite_timestamp,
            )
        elif primary_payload is not None and (
            backup_payload is None
            or backup_missing
            or self._backup_needs_refresh(backup_payload, records, payload if isinstance(payload, dict) else None)
        ):
            if self._backup_needs_audit_quarantine(backup_payload):
                self._quarantine_invalid_backup()
                preserve_backup_corrupt = True
            if self._backup_needs_audit_quarantine(seed_payload):
                self._quarantine_invalid_seed()
                preserve_seed_corrupt = True
            backup_written = self._write_backup_payload(
                self._backup_payload_from_records(records, payload if isinstance(payload, dict) else {})
            )
            self._clear_recovery_artifacts(
                preserve_seed=not backup_written,
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
                preserve_temporary_corrupt=preserve_temporary_corrupt,
            )
            if not backup_written:
                self._write_seed(self._backup_payload_from_records(records, payload if isinstance(payload, dict) else {}))
        elif backup_payload is None or backup_missing or self._backup_needs_refresh(
            backup_payload,
            records,
            payload if isinstance(payload, dict) else None,
        ):
            backup_written = False
            if isinstance(payload, dict):
                backup_written = self._write_backup_payload(self._backup_payload_from_records(records, payload))
            else:
                backup_written = self._write_backup()
            self._clear_recovery_artifacts(
                preserve_seed=not backup_written,
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
                preserve_temporary_corrupt=preserve_temporary_corrupt,
            )
            if not backup_written:
                self._write_seed(
                    self._backup_payload_from_records(records, payload) if isinstance(payload, dict) else payload
                )
        else:
            self._clear_recovery_artifacts(
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
                preserve_temporary_corrupt=preserve_temporary_corrupt,
            )
        return records

    def save(
        self,
        records: list[ContextSetRecord],
        recovered_from: str | None = None,
        refresh_backup: bool = False,
        preserve_primary_corrupt: bool = False,
        preserve_backup_corrupt: bool = False,
        preserve_seed_corrupt: bool = False,
        preserve_temporary_corrupt: bool = False,
        updated_at: str | None = None,
    ) -> None:
        normalized_records = self._normalize_records(records)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        canonical_updated_at = self._parse_updated_at(updated_at) or datetime.now(UTC).isoformat()
        normalized_recovered_from = self._parse_recovered_from(recovered_from)
        current_payload, _ = self._load_payload(self._path)
        current_backup_payload, _ = self._load_payload(self._backup_path)
        cleanup_timestamp = self._recovery_marker_cleanup_timestamp(current_payload, normalized_records)
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
                "context_sets": [asdict(record) for record in normalized_records],
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
                or self._backup_needs_refresh(current_backup_payload, normalized_records, payload)
            )
            if backup_written:
                backup_written = self._write_backup_payload(backup_payload)
            if not backup_written:
                # Seed keeps the latest canonical context set recoverable if
                # backup rotation cannot be completed after the recovery
                # marker is removed from an otherwise canonical payload.
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
            and (updated_at is None or self._payload_updated_at(current_payload) == canonical_updated_at)
            and self._is_canonical_primary_payload(current_payload, normalized_records)
        ):
            # Rewriting an unchanged canonical store only obscures the last real
            # context mutation, so keep the primary stable and refresh recovery
            # artifacts in place.
            backup_payload = self._backup_payload(current_payload)
            backup_written = (
                refresh_backup
                or current_backup_payload is None
                or self._backup_needs_refresh(current_backup_payload, normalized_records, current_payload)
            )
            if backup_written:
                backup_written = self._write_backup_payload(backup_payload)
            if not backup_written:
                self._write_seed(backup_payload)
            self._clear_recovery_artifacts(
                preserve_seed=not backup_written,
                preserve_temporary_corrupt=preserve_temporary_corrupt,
            )
            return
        payload = {
            "schema_version": _SCHEMA_VERSION,
            "updated_at": canonical_updated_at,
            "context_sets": [asdict(record) for record in normalized_records],
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
            or self._backup_needs_refresh(current_backup_payload, normalized_records, payload)
        )
        if backup_written:
            backup_written = self._write_backup_payload(backup_payload)
        if not backup_written:
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

    def create_context_set(self, name: str, item_ids: list[object] | None = None) -> ContextSetRecord:
        records = self.load()
        now = datetime.now(UTC).isoformat()
        record = ContextSetRecord(
            context_set_id=str(uuid.uuid4()),
            name=name,
            item_ids=ContextSetRecord._normalize_item_ids(item_ids or []),
            created_at=now,
            updated_at=now,
        )
        record.normalize()
        if not record.name:
            raise ValueError("name is required")
        if any(existing.name == record.name for existing in records):
            raise ValueError(f"context set name already exists: {record.name}")
        self.save([*records, record])
        return record

    def pin_item(self, context_set_id: str, item_id: object) -> ContextSetRecord:
        records = self.load()
        normalized_id = ContextSetRecord._normalize_identifier(context_set_id)
        normalized_item_id = ContextSetRecord._normalize_item_id(item_id)
        if not normalized_id:
            raise ValueError("context_set_id is required")
        if not normalized_item_id:
            raise ValueError("item_id is required")
        for idx, record in enumerate(records):
            if record.context_set_id != normalized_id:
                continue
            if normalized_item_id not in record.item_ids:
                record.item_ids.append(normalized_item_id)
                record.updated_at = datetime.now(UTC).isoformat()
                record.normalize()
                records[idx] = record
                self.save(records)
                return record
            return record
        raise KeyError(f"unknown context_set_id: {context_set_id}")

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

    def _load_payload(self, path: Path) -> tuple[dict[str, object] | list[object] | None, bool]:
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

    def _write_seed(self, payload: dict[str, object] | list[object]) -> None:
        seed = self._seed_state_path()
        tmp = seed.with_suffix(".tmp")
        try:
            tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
            tmp.replace(seed)
        except OSError:
            self._unlink_if_exists(tmp)

    def _backup_payload(self, payload: dict[str, object]) -> dict[str, object]:
        return self._backup_payload_from_records(
            self._normalize_records(self._parse_context_sets(payload.get("context_sets")) or []),
            payload,
        )

    def _backup_payload_from_records(
        self,
        records: list[ContextSetRecord],
        payload: dict[str, object],
    ) -> dict[str, object]:
        backup_payload: dict[str, object] = {
            "schema_version": self._parse_schema_version(payload) or _SCHEMA_VERSION,
            "context_sets": self._normalize_context_sets(records),
        }
        normalized_updated_at = self._parse_updated_at(payload.get("updated_at"))
        if normalized_updated_at is not None:
            backup_payload["updated_at"] = normalized_updated_at
        return backup_payload

    def _is_valid_payload(self, path: Path) -> bool:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False
        return self._is_supported_payload(payload)

    def _is_loadable_payload(self, payload: object) -> bool:
        if isinstance(payload, list):
            return self._parse_context_sets(payload) is not None
        if not isinstance(payload, dict):
            return False
        if "context_sets" in payload and self._parse_context_sets(payload.get("context_sets")) is None:
            return False
        return True

    def _is_supported_payload(self, payload: object) -> bool:
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

    def _is_canonical_primary_payload(self, payload: object, records: list[ContextSetRecord]) -> bool:
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
        raw_context_sets = payload.get("context_sets")
        parsed_records = self._parse_context_sets(raw_context_sets)
        if parsed_records is None:
            return False
        if self._records_need_rewrite(raw_context_sets, parsed_records):
            return False
        return parsed_records == records

    def _recovery_marker_cleanup_timestamp(
        self,
        payload: object,
        records: list[ContextSetRecord],
    ) -> str | None:
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
        raw_context_sets = payload.get("context_sets")
        parsed_records = self._parse_context_sets(raw_context_sets)
        if parsed_records is None:
            return None
        if self._records_need_rewrite(raw_context_sets, parsed_records):
            return None
        if self._normalize_records(parsed_records) != records:
            return None
        return normalized_updated_at

    def _payload_updated_at(self, payload: object) -> str | None:
        if not isinstance(payload, dict):
            return None
        return self._parse_updated_at(payload.get("updated_at"))

    def _parse_context_sets(self, value: object) -> list[ContextSetRecord] | None:
        records: list[ContextSetRecord] = []
        raw_values: list[object]
        if isinstance(value, list):
            raw_values = value
        elif isinstance(value, dict):
            raw_values = [value]
        else:
            return None
        for raw in raw_values:
            record = self._parse_record(raw)
            if record is None:
                continue
            records.append(record)
        return records

    def _parse_record(self, raw: object) -> ContextSetRecord | None:
        if not isinstance(raw, dict):
            return None
        record = ContextSetRecord(
            context_set_id=ContextSetRecord._normalize_identifier(raw.get("context_set_id")),
            name=ContextSetRecord._normalize_name(raw.get("name")),
            item_ids=ContextSetRecord._parse_item_ids(raw.get("item_ids", [])),
            created_at=ContextSetRecord._normalize_timestamp(raw.get("created_at")),
            updated_at=ContextSetRecord._normalize_timestamp(raw.get("updated_at")),
        )
        record.normalize()
        if not record.context_set_id or not record.name:
            return None
        return record

    def _normalize_context_sets(self, records: list[ContextSetRecord]) -> list[dict[str, object]]:
        normalized: list[dict[str, object]] = []
        for record in self._normalize_records(records):
            normalized.append(asdict(record))
        return normalized

    def _normalize_records(self, records: list[ContextSetRecord]) -> list[ContextSetRecord]:
        normalized: list[ContextSetRecord] = []
        seen_ids: set[str] = set()
        seen_names: set[str] = set()
        for raw in records:
            record = ContextSetRecord(
                context_set_id=raw.context_set_id,
                name=raw.name,
                item_ids=list(raw.item_ids),
                created_at=raw.created_at,
                updated_at=raw.updated_at,
            )
            record.normalize()
            if (
                not record.context_set_id
                or not record.name
                or record.context_set_id in seen_ids
                or record.name in seen_names
            ):
                continue
            normalized.append(record)
            seen_ids.add(record.context_set_id)
            seen_names.add(record.name)
        return normalized

    def _records_need_timestamp_backfill(self, records: list[ContextSetRecord]) -> bool:
        return any(not record.created_at or not record.updated_at for record in records)

    def _backfill_record_timestamps(
        self,
        records: list[ContextSetRecord],
        fallback_timestamp: str,
    ) -> list[ContextSetRecord]:
        backfilled: list[ContextSetRecord] = []
        for raw in records:
            record = ContextSetRecord(
                context_set_id=raw.context_set_id,
                name=raw.name,
                item_ids=list(raw.item_ids),
                created_at=raw.created_at or fallback_timestamp,
                updated_at=raw.updated_at or fallback_timestamp,
            )
            record.normalize()
            backfilled.append(record)
        return backfilled

    def _records_need_rewrite(self, raw_records: object, parsed_records: list[ContextSetRecord]) -> bool:
        if not isinstance(raw_records, list):
            return True
        if len(parsed_records) != len(raw_records):
            return True
        for raw_record, parsed_record in zip(raw_records, parsed_records):
            if self._record_needs_rewrite(raw_record, parsed_record):
                return True
        if self._normalize_records(parsed_records) != parsed_records:
            return True
        return False

    def _record_needs_rewrite(self, raw_record: object, parsed_record: ContextSetRecord) -> bool:
        if not isinstance(raw_record, dict):
            return True
        return raw_record != asdict(parsed_record)

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
        records: list[ContextSetRecord],
        primary_payload: dict[str, object] | None = None,
    ) -> bool:
        if payload is None:
            return False
        if isinstance(payload, list):
            return True
        if self._parse_schema_version(payload) != _SCHEMA_VERSION:
            return True
        if "context_sets" not in payload:
            return True
        parsed_records = self._parse_context_sets(payload.get("context_sets"))
        if parsed_records is None:
            return True
        if self._records_need_rewrite(payload.get("context_sets"), parsed_records):
            return True
        if self._normalize_records(parsed_records) != self._normalize_records(records):
            return True
        if self._has_unknown_fields(payload):
            return True
        if "updated_at" not in payload:
            return True
        if "recovered_from" in payload:
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
            return self._list_payload_needs_audit_quarantine(payload)
        if "updated_at" not in payload:
            return True
        if "context_sets" not in payload:
            return True
        raw_context_sets = payload.get("context_sets")
        if isinstance(raw_context_sets, list) and self._list_payload_needs_audit_quarantine(raw_context_sets):
            return True
        if self._has_unknown_fields(payload):
            return True
        return not self._is_supported_payload(payload)

    def _has_unknown_fields(self, payload: dict[str, object]) -> bool:
        return any(key not in _CANONICAL_DICT_KEYS for key in payload)

    def _recovery_payload_updated_at(self, payload: dict[str, object] | list[object]) -> str | None:
        timestamps: list[str] = []
        if isinstance(payload, dict):
            normalized_updated_at = self._parse_updated_at(payload.get("updated_at"))
            if normalized_updated_at is not None:
                timestamps.append(normalized_updated_at)
            raw_context_sets = payload.get("context_sets") if "context_sets" in payload else None
        else:
            raw_context_sets = payload
        if raw_context_sets is not None:
            records = self._parse_context_sets(raw_context_sets)
            if records:
                timestamps.extend(
                    timestamp
                    for record in records
                    for timestamp in (record.updated_at, record.created_at)
                    if timestamp
                )
        if not timestamps:
            return None
        return max(timestamps)

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
            if self._has_context_set_records(candidate):
                candidate_key = self._recovery_candidate_key(candidate, position)
                if best_candidate_key is None or candidate_key > best_candidate_key:
                    best_candidate = (candidate, recovered_source)
                    best_candidate_key = candidate_key
                continue
            # Only explicit empty payloads should serve as a fallback recovery
            # source. Dicts missing the core context_sets key are malformed, not
            # recoverable state.
            if self._has_explicit_empty_recovery_payload(candidate):
                candidate_key = self._recovery_candidate_key(candidate, position)
                if fallback_candidate_key is None or candidate_key > fallback_candidate_key:
                    fallback_candidate = (candidate, recovered_source)
                    fallback_candidate_key = candidate_key
        if best_candidate != (None, None):
            return best_candidate
        return fallback_candidate

    def _has_context_set_records(self, payload: dict[str, object] | list[object]) -> bool:
        if isinstance(payload, list):
            return bool(self._parse_context_sets(payload))
        if "context_sets" not in payload:
            return False
        return bool(self._parse_context_sets(payload.get("context_sets")))

    def _legacy_list_payload_has_dropped_records(self, payload: object) -> bool:
        if not isinstance(payload, list):
            return False
        parsed_records = self._parse_context_sets(payload)
        if parsed_records is None:
            return False
        return len(parsed_records) < len(payload)

    def _list_payload_needs_audit_quarantine(self, payload: object) -> bool:
        if not isinstance(payload, list):
            return False
        parsed_records = self._parse_context_sets(payload)
        if parsed_records is None:
            return False
        if len(parsed_records) < len(payload):
            return True
        if any(self._record_has_unknown_fields(raw_record) for raw_record in payload):
            return True
        return len(self._normalize_records(parsed_records)) < len(parsed_records)

    def _record_has_unknown_fields(self, record: object) -> bool:
        if not isinstance(record, dict):
            return False
        return any(key not in _CANONICAL_RECORD_KEYS for key in record)

    def _quarantine_unrecoverable_list_payload(self, path: Path, payload: object) -> bool:
        if path not in {self._backup_path, self._seed_state_path()}:
            return False
        if not isinstance(payload, list):
            return False
        if not payload:
            # An explicit empty legacy list is a recoverable empty context-set
            # store, not malformed state that should survive as quarantine.
            return False
        if self._has_context_set_records(payload):
            return False
        self._quarantine_path(path)
        return True

    def _is_empty_recovery_payload(self, payload: dict[str, object] | list[object] | None) -> bool:
        return payload is not None and not self._has_context_set_records(payload)

    def _has_explicit_empty_recovery_payload(self, payload: dict[str, object] | list[object]) -> bool:
        if isinstance(payload, list):
            return not payload
        if "context_sets" not in payload:
            return False
        raw_context_sets = payload.get("context_sets")
        # Only a truly empty list counts as recoverable empty state. Lists
        # that only normalize to empty after dropping malformed records remain
        # quarantined instead of being treated as intentional recovery data.
        return isinstance(raw_context_sets, list) and not raw_context_sets

    def _primary_context_sets_need_recovery(self, payload: dict[str, object] | list[object] | None) -> bool:
        if isinstance(payload, dict):
            if "context_sets" not in payload:
                return True
            raw_context_sets = payload.get("context_sets")
            parsed_records = self._parse_context_sets(raw_context_sets)
            if parsed_records is None:
                return True
            return self._records_need_rewrite(raw_context_sets, parsed_records)
        if isinstance(payload, list):
            return True
        return False

    def _recovery_marker(self, *, primary_unavailable: bool, recovered_source: str | None) -> str | None:
        if not primary_unavailable:
            return None
        if recovered_source == "backup_tmp":
            return "backup"
        if recovered_source == "seed_tmp":
            return "seed"
        return self._parse_recovered_from(recovered_source)

    def _unlink_if_exists(self, path: Path) -> None:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            return
