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
        payload = self._load_payload(self._path)
        loaded_from_tmp = False
        loaded_from_backup = False
        if payload is None:
            payload = self._load_payload(self._tmp_path())
            loaded_from_tmp = payload is not None
        if payload is None:
            payload = self._load_payload(self._backup_path)
            loaded_from_backup = payload is not None
        if payload is None:
            return ContextBasket()

        should_rewrite = False
        if isinstance(payload, list):
            parsed_items = self._parse_item_ids(payload)
            if parsed_items is None:
                return ContextBasket()
            basket = ContextBasket(item_ids=parsed_items)
            should_rewrite = True
        elif isinstance(payload, dict):
            schema_version = payload.get("schema_version", 0)
            if isinstance(schema_version, int) and schema_version > _SCHEMA_VERSION:
                return ContextBasket()
            parsed_items = self._parse_item_ids(payload.get("item_ids", []))
            if parsed_items is None:
                return ContextBasket()
            basket = ContextBasket(item_ids=parsed_items)
            should_rewrite = schema_version != _SCHEMA_VERSION
            if "recovered_from" in payload and self._parse_recovered_from(payload.get("recovered_from")) is None:
                should_rewrite = True
            if "updated_at" in payload and self._parse_updated_at(payload.get("updated_at")) is None:
                should_rewrite = True
        else:
            return ContextBasket()

        prior = list(basket.item_ids)
        basket.normalize()
        if basket.item_ids != prior:
            should_rewrite = True

        recovered_from: str | None = None
        if loaded_from_tmp:
            recovered_from = "tmp"
        elif loaded_from_backup:
            recovered_from = "backup"
        if loaded_from_tmp or loaded_from_backup or should_rewrite:
            self.save(basket, recovered_from=recovered_from)
        return basket

    def save(self, basket: ContextBasket, recovered_from: str | None = None) -> None:
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
        corrupt = self._corrupt_path()
        self._unlink_if_exists(corrupt)
        try:
            self._path.replace(corrupt)
        except OSError:
            return

    def _clear_quarantine_file(self) -> None:
        self._unlink_if_exists(self._corrupt_path())

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
                self._unlink_if_exists(path)
            return None
        if isinstance(payload, (dict, list)):
            return payload
        if path == self._tmp_path():
            self._unlink_if_exists(path)
        elif path == self._backup_path:
            self._unlink_if_exists(path)
        return None

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
        if isinstance(payload, list):
            return self._parse_item_ids(payload) is not None
        if not isinstance(payload, dict):
            return False
        schema_version = payload.get("schema_version", 0)
        if isinstance(schema_version, int) and schema_version > _SCHEMA_VERSION:
            return False
        if self._parse_item_ids(payload.get("item_ids", [])) is None:
            return False
        if "recovered_from" in payload and self._parse_recovered_from(payload.get("recovered_from")) is None:
            return False
        if "updated_at" in payload and self._parse_updated_at(payload.get("updated_at")) is None:
            return False
        return True

    def _parse_item_ids(self, value: object) -> list[str] | None:
        if not isinstance(value, list):
            return None
        parsed: list[str] = []
        for raw in value:
            if isinstance(raw, (dict, list)):
                return None
            parsed.append(str(raw))
        return parsed

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

    def _unlink_if_exists(self, path: Path) -> None:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            return
