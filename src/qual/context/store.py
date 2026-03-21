from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from src.qual.context.basket import ContextBasket

_SCHEMA_VERSION = 1


class ContextBasketStore:
    """Persist context basket state for scaffold CLI workflows."""

    def __init__(self, root_dir: Path) -> None:
        self._path = root_dir / "context_basket.json"
        self._backup_path = root_dir / "context_basket.bak.json"

    def _corrupt_path(self) -> Path:
        return self._path.with_suffix(".corrupt.json")

    def _tmp_path(self) -> Path:
        return self._path.with_suffix(".tmp")

    def load(self) -> ContextBasket:
        primary_missing = not self._path.exists()
        backup_missing = not self._backup_path.exists()
        primary_payload = self._load_payload(self._path)
        tmp_payload = self._load_payload(self._tmp_path())
        backup_payload = self._load_payload(self._backup_path)

        candidates: tuple[tuple[dict[str, object] | list[object] | None, str | None], ...] = (
            (tmp_payload, "tmp"),
            (primary_payload, None),
            (backup_payload, "backup"),
        )
        for payload, recovered_source in candidates:
            if payload is None:
                continue

            should_rewrite = False
            if isinstance(payload, list):
                parsed_items = self._parse_item_ids(payload)
                if parsed_items is None:
                    self._discard_payload_source(recovered_source)
                    continue
                basket = ContextBasket(item_ids=parsed_items)
                should_rewrite = True
            elif isinstance(payload, dict):
                schema_version = self._parse_schema_version(payload)
                if schema_version is None:
                    self._discard_payload_source(recovered_source)
                    continue
                parsed_items = self._parse_item_ids(payload.get("item_ids", []))
                if parsed_items is None:
                    self._discard_payload_source(recovered_source)
                    continue
                basket = ContextBasket(item_ids=parsed_items)
                should_rewrite = schema_version != _SCHEMA_VERSION
                if "recovered_from" in payload and self._parse_recovered_from(payload.get("recovered_from")) is None:
                    should_rewrite = True
                if "updated_at" in payload and self._parse_updated_at(payload.get("updated_at")) is None:
                    should_rewrite = True
            else:
                self._discard_payload_source(recovered_source)
                continue

            prior = list(basket.item_ids)
            basket.normalize()
            if basket.item_ids != prior:
                should_rewrite = True

            recovered_from = self._recovery_marker(
                primary_missing=primary_missing,
                recovered_source=recovered_source,
            )
            if recovered_source is not None or should_rewrite:
                # Keep the backup aligned with the latest canonical basket whenever we
                # rewrite state during load, not only when we recover from tmp/backup.
                refresh_backup = recovered_source is not None or should_rewrite
                self.save(
                    basket,
                    recovered_from=recovered_from,
                    refresh_backup=refresh_backup,
                )
            elif backup_payload is None or backup_missing or self._backup_needs_refresh(backup_payload, basket):
                self._write_backup()
                self._clear_quarantine_file()
            else:
                self._clear_quarantine_file()
            return basket
        return ContextBasket()

    def save(
        self,
        basket: ContextBasket,
        recovered_from: str | None = None,
        refresh_backup: bool = False,
    ) -> None:
        basket.normalize()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": _SCHEMA_VERSION,
            "updated_at": datetime.now(UTC).isoformat(),
            "item_ids": list(basket.item_ids),
        }
        normalized_recovered_from = self._parse_recovered_from(recovered_from)
        if normalized_recovered_from is not None:
            payload["recovered_from"] = normalized_recovered_from
        self._write_backup()
        tmp = self._tmp_path()
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self._path)
        if refresh_backup:
            self._write_backup()
        self._clear_quarantine_file()

    def clear(self) -> None:
        for path in (
            self._path,
            self._backup_path,
            self._tmp_path(),
            self._corrupt_path(),
        ):
            self._unlink_if_exists(path)

    def _quarantine_invalid_file(self) -> None:
        if not self._path.exists():
            return
        self._quarantine_path(self._path)

    def _quarantine_invalid_backup(self) -> None:
        if not self._backup_path.exists():
            return
        self._quarantine_path(self._backup_path)

    def _quarantine_path(self, path: Path) -> None:
        corrupt = self._corrupt_path_for(path)
        self._unlink_if_exists(corrupt)
        try:
            path.replace(corrupt)
        except OSError:
            return

    def _clear_quarantine_file(self) -> None:
        self._unlink_if_exists(self._corrupt_path())
        self._unlink_if_exists(self._corrupt_path_for(self._backup_path))

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
        else:
            self._quarantine_invalid_file()

    def _load_payload(self, path: Path) -> dict[str, object] | list[object] | None:
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            if path == self._path:
                self._quarantine_invalid_file()
            elif path == self._tmp_path():
                self._unlink_if_exists(path)
            elif path == self._backup_path:
                self._quarantine_invalid_backup()
            return None
        if not self._is_loadable_payload(payload):
            if path == self._path:
                self._quarantine_invalid_file()
            elif path == self._tmp_path():
                self._unlink_if_exists(path)
            elif path == self._backup_path:
                self._quarantine_invalid_backup()
            return None
        return payload

    def _write_backup(self) -> None:
        if not self._path.exists():
            return
        if not self._is_valid_payload(self._path):
            return
        tmp = self._backup_path.with_suffix(".tmp")
        try:
            tmp.write_bytes(self._path.read_bytes())
            tmp.replace(self._backup_path)
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
        if self._parse_schema_version(payload) is None:
            return False
        if self._parse_item_ids(payload.get("item_ids", [])) is None:
            return False
        return True

    def _is_supported_payload(self, payload: object) -> bool:
        # Backup rotation stays strict so we do not preserve malformed metadata as canonical.
        if not self._is_loadable_payload(payload):
            return False
        if not isinstance(payload, dict):
            return True
        if "recovered_from" in payload and self._parse_recovered_from(payload.get("recovered_from")) is None:
            return False
        if "updated_at" in payload and self._parse_updated_at(payload.get("updated_at")) is None:
            return False
        return True

    def _parse_item_ids(self, value: object) -> list[str] | None:
        if not isinstance(value, list):
            return None
        parsed: list[str] = []
        saw_invalid = False
        for raw in value:
            if not isinstance(raw, str):
                saw_invalid = True
                continue
            parsed.append(raw)
        if saw_invalid and not parsed:
            return None
        return parsed

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
        if normalized in {"tmp", "backup"}:
            return normalized
        return None

    def _parse_updated_at(self, value: object) -> str | None:
        if not isinstance(value, str):
            return None
        candidate = value.strip()
        if not candidate:
            return None
        try:
            datetime.fromisoformat(candidate.replace("Z", "+00:00"))
        except ValueError:
            return None
        return candidate

    def _backup_needs_refresh(
        self,
        payload: dict[str, object] | list[object] | None,
        basket: ContextBasket,
    ) -> bool:
        if payload is None:
            return False
        if isinstance(payload, list):
            return True
        if self._parse_schema_version(payload) != _SCHEMA_VERSION:
            return True
        parsed_items = self._parse_item_ids(payload.get("item_ids", []))
        if parsed_items is None:
            return True
        if self._normalize_item_ids(parsed_items) != basket.item_ids:
            return True
        if "recovered_from" in payload and self._parse_recovered_from(payload.get("recovered_from")) is None:
            return True
        if "updated_at" in payload and self._parse_updated_at(payload.get("updated_at")) is None:
            return True
        return False

    def _normalize_item_ids(self, item_ids: list[str]) -> list[str]:
        basket = ContextBasket(item_ids=list(item_ids))
        basket.normalize()
        return basket.item_ids

    def _recovery_marker(self, *, primary_missing: bool, recovered_source: str | None) -> str | None:
        if not primary_missing:
            return None
        return self._parse_recovered_from(recovered_source)

    def _unlink_if_exists(self, path: Path) -> None:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            return
