from __future__ import annotations

import json
import math
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

_SCHEMA_VERSION = 1
_CANONICAL_DICT_KEYS = {"schema_version", "updated_at", "context_sets", "recovered_from"}


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
        self.created_at = self._normalize_timestamp(self.created_at)
        self.updated_at = self._normalize_timestamp(self.updated_at)

    @staticmethod
    def _normalize_identifier(value: object) -> str:
        if not isinstance(value, str):
            return ""
        return value.strip()

    @staticmethod
    def _normalize_name(value: object) -> str:
        if not isinstance(value, str):
            return ""
        return value.strip()

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
            return ""
        return parsed.astimezone(UTC).isoformat()


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

    def load(self) -> list[ContextSetRecord]:
        primary_missing = not self._path.exists()
        backup_missing = not self._backup_path.exists()
        primary_payload, _ = self._load_payload(self._path)
        tmp_payload, _ = self._load_payload(self._tmp_path())
        backup_tmp_payload, _ = self._load_payload(self._backup_tmp_path())
        backup_payload, _ = self._load_payload(self._backup_path)
        seed_tmp_payload, _ = self._load_payload(self._seed_tmp_path())
        seed_payload, _ = self._load_payload(self._seed_state_path())

        primary_needs_quarantine = self._primary_context_sets_need_recovery(primary_payload)
        if primary_needs_quarantine:
            self._quarantine_invalid_file()

        payload: dict[str, object] | list[object] | None
        recovered_source: str | None
        if primary_needs_quarantine:
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
        elif primary_payload is not None:
            payload = primary_payload
            recovered_source = None
        elif tmp_payload is not None:
            payload = tmp_payload
            recovered_source = "tmp"
        elif backup_tmp_payload is not None:
            payload = backup_tmp_payload
            recovered_source = "backup"
        elif backup_payload is not None:
            payload = backup_payload
            recovered_source = "backup"
        elif seed_tmp_payload is not None:
            payload = seed_tmp_payload
            recovered_source = "seed"
        elif seed_payload is not None:
            payload = seed_payload
            recovered_source = "seed"
        else:
            self._clear_quarantine_file()
            self._clear_temporary_files()
            return []

        should_rewrite = False
        normalized_recovered_from = None
        records: list[ContextSetRecord]
        if isinstance(payload, list):
            records = self._parse_context_sets(payload)
            if records is None:
                self._discard_payload_source(recovered_source)
                return []
            should_rewrite = True
        elif isinstance(payload, dict):
            schema_version = self._parse_schema_version(payload)
            if "context_sets" not in payload:
                records = []
                should_rewrite = True
            else:
                raw_context_sets = payload.get("context_sets")
                records = self._parse_context_sets(raw_context_sets)
                if records is None:
                    records = []
                    should_rewrite = True
                should_rewrite = (
                    should_rewrite
                    or schema_version != _SCHEMA_VERSION
                    or self._records_need_rewrite(raw_context_sets, records)
                )
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
                normalized_recovered_from = self._parse_recovered_from(payload.get("recovered_from"))
                if normalized_recovered_from is None:
                    should_rewrite = True
                elif primary_missing:
                    if payload.get("recovered_from") != normalized_recovered_from:
                        should_rewrite = True
                else:
                    normalized_recovered_from = None
                    should_rewrite = True
        else:
            self._discard_payload_source(recovered_source)
            return []

        recovered_from = self._recovery_marker(
            primary_unavailable=primary_missing or primary_payload is None,
            recovered_source=recovered_source,
        ) or normalized_recovered_from
        if recovered_source is not None or should_rewrite:
            self.save(records, recovered_from=recovered_from, refresh_backup=True)
        elif primary_payload is not None and (
            backup_payload is None
            or backup_missing
            or self._backup_needs_refresh(backup_payload, records, payload if isinstance(payload, dict) else None)
        ):
            backup_written = self._write_backup_payload(self._backup_payload(payload))
            self._clear_recovery_artifacts(preserve_seed=not backup_written)
            if not backup_written:
                self._write_seed(self._backup_payload(payload))
        elif backup_payload is None or backup_missing or self._backup_needs_refresh(
            backup_payload,
            records,
            payload if isinstance(payload, dict) else None,
        ):
            backup_written = False
            if isinstance(payload, dict):
                backup_written = self._write_backup_payload(self._backup_payload(payload))
            else:
                backup_written = self._write_backup()
            self._clear_recovery_artifacts(preserve_seed=not backup_written)
            if not backup_written:
                self._write_seed(self._backup_payload(payload) if isinstance(payload, dict) else payload)
        else:
            self._clear_recovery_artifacts()
        return records

    def save(
        self,
        records: list[ContextSetRecord],
        recovered_from: str | None = None,
        refresh_backup: bool = False,
    ) -> None:
        normalized_records = self._normalize_records(records)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": _SCHEMA_VERSION,
            "updated_at": datetime.now(UTC).isoformat(),
            "context_sets": [asdict(record) for record in normalized_records],
        }
        normalized_recovered_from = self._parse_recovered_from(recovered_from)
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
        current_backup_payload, _ = self._load_payload(self._backup_path)
        backup_written = (
            refresh_backup
            or current_backup_payload is None
            or self._backup_needs_refresh(current_backup_payload, normalized_records, payload)
        )
        if backup_written:
            backup_written = self._write_backup_payload(backup_payload)
        if not backup_written:
            self._write_seed(backup_payload)
        self._clear_recovery_artifacts(preserve_seed=not backup_written)

    def create_context_set(self, name: str, item_ids: list[object] | None = None) -> ContextSetRecord:
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
        self.save([*self.load(), record])
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
            record.updated_at = datetime.now(UTC).isoformat()
            record.normalize()
            records[idx] = record
            self.save(records)
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

    def _clear_quarantine_file(self, preserve_temporary: bool = False) -> None:
        self._unlink_if_exists(self._corrupt_path())
        self._unlink_if_exists(self._corrupt_path_for(self._backup_path))
        self._unlink_if_exists(self._corrupt_path_for(self._seed_state_path()))
        if not preserve_temporary:
            self._unlink_if_exists(self._corrupt_path_for(self._tmp_path()))
            self._unlink_if_exists(self._corrupt_path_for(self._backup_tmp_path()))
            self._unlink_if_exists(self._corrupt_path_for(self._seed_tmp_path()))

    def _clear_temporary_files(self) -> None:
        self._unlink_if_exists(self._tmp_path())
        self._unlink_if_exists(self._backup_tmp_path())
        self._unlink_if_exists(self._seed_tmp_path())

    def _clear_recovery_artifacts(self, preserve_seed: bool = False) -> None:
        self._clear_quarantine_file()
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
        elif recovered_source == "backup":
            self._unlink_if_exists(self._backup_path)
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
            return None, path.suffix == ".tmp"
        if not self._is_loadable_payload(payload):
            if path == self._path:
                self._quarantine_invalid_file()
            elif path.suffix == ".tmp":
                self._quarantine_path(path)
            elif path == self._backup_path:
                self._quarantine_invalid_backup()
            elif path == self._seed_state_path():
                self._quarantine_invalid_seed()
            return None, path.suffix == ".tmp"
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
        backup_payload: dict[str, object] = {
            "schema_version": self._parse_schema_version(payload) or _SCHEMA_VERSION,
            "context_sets": self._normalize_context_sets(self._parse_context_sets(payload.get("context_sets")) or []),
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

    def _parse_context_sets(self, value: object) -> list[ContextSetRecord] | None:
        if not isinstance(value, list):
            return None
        records: list[ContextSetRecord] = []
        for raw in value:
            record = self._parse_record(raw)
            if record is None:
                continue
            records.append(record)
        return records

    def _parse_record(self, raw: object) -> ContextSetRecord | None:
        if not isinstance(raw, dict):
            return None
        record = ContextSetRecord(
            context_set_id=str(raw.get("context_set_id", "")),
            name=str(raw.get("name", "")),
            item_ids=list(raw.get("item_ids", [])) if isinstance(raw.get("item_ids", []), list) else [],
            created_at=str(raw.get("created_at", "")),
            updated_at=str(raw.get("updated_at", "")),
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
        seen: set[str] = set()
        for raw in records:
            record = ContextSetRecord(
                context_set_id=raw.context_set_id,
                name=raw.name,
                item_ids=list(raw.item_ids),
                created_at=raw.created_at,
                updated_at=raw.updated_at,
            )
            record.normalize()
            if not record.context_set_id or not record.name or record.context_set_id in seen:
                continue
            normalized.append(record)
            seen.add(record.context_set_id)
        return normalized

    def _records_need_rewrite(self, raw_records: object, parsed_records: list[ContextSetRecord]) -> bool:
        if not isinstance(raw_records, list):
            return True
        if len(parsed_records) != len(raw_records):
            return True
        normalized_records = self._normalize_records(parsed_records)
        return [asdict(record) for record in normalized_records] != [asdict(record) for record in parsed_records]

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
        normalized = value.strip().lower()
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
            return None
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

    def _has_unknown_fields(self, payload: dict[str, object]) -> bool:
        return any(key not in _CANONICAL_DICT_KEYS for key in payload)

    def _prefer_recovery_payload(
        self,
        tmp_payload: dict[str, object] | list[object] | None,
        backup_tmp_payload: dict[str, object] | list[object] | None,
        backup_payload: dict[str, object] | list[object] | None,
        seed_tmp_payload: dict[str, object] | list[object] | None,
        seed_payload: dict[str, object] | list[object] | None,
    ) -> tuple[dict[str, object] | list[object] | None, str | None]:
        for candidate, recovered_source in (
            (tmp_payload, "tmp"),
            (backup_tmp_payload, "backup_tmp"),
            (backup_payload, "backup"),
            (seed_tmp_payload, "seed_tmp"),
            (seed_payload, "seed"),
        ):
            if candidate is None:
                continue
            if isinstance(candidate, dict) and "context_sets" not in candidate:
                continue
            return candidate, recovered_source
        return None, None

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
            parsed_records = self._parse_context_sets(payload)
            if parsed_records is None:
                return True
            return self._records_need_rewrite(payload, parsed_records)
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
