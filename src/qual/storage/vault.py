from __future__ import annotations

import json
from datetime import UTC, datetime
from dataclasses import dataclass
from pathlib import Path

from src.qual.config import validate_project_name

_STATE_FILE = ".vault_state.json"
_BACKUP_STATE_FILE = ".vault_state.bak.json"
_SCHEMA_VERSION = 1


@dataclass
class VaultState:
    project_name: str
    root_dir: Path
    is_locked: bool = True


class VaultService:
    """Filesystem bootstrap service for per-project vault directories."""

    def create_or_open(self, root_dir: Path, project_name: str) -> VaultState:
        safe_project_name = validate_project_name(project_name)
        project_root = root_dir / safe_project_name
        project_root.mkdir(parents=True, exist_ok=True)
        (project_root / "attachments").mkdir(exist_ok=True)
        raw_state, recovered_from, invalid_primary = self._read_state(project_root)
        parsed_is_locked = self._parse_is_locked(raw_state.get("is_locked", False))
        is_locked = parsed_is_locked if parsed_is_locked is not None else False
        if invalid_primary and recovered_from is None:
            is_locked = True
        stored_project_name = self._parse_project_name(raw_state.get("project_name"))
        if "project_name" in raw_state and stored_project_name is None:
            is_locked = True
        elif stored_project_name is not None and stored_project_name != safe_project_name:
            # If metadata does not match directory identity, prefer a safe default.
            is_locked = True
        state = VaultState(
            project_name=safe_project_name,
            root_dir=project_root,
            is_locked=is_locked,
        )
        self._write_state(state, recovered_from=recovered_from)
        return state

    def lock(self, state: VaultState) -> None:
        state.is_locked = True
        self._write_state(state)

    def unlock(self, state: VaultState) -> None:
        state.is_locked = False
        self._write_state(state)

    def clear_state(self, state: VaultState) -> None:
        for path in (
            self._state_path(state.root_dir),
            self._backup_state_path(state.root_dir),
            self._tmp_state_path(state.root_dir),
            self._corrupt_state_path(state.root_dir),
        ):
            self._unlink_if_exists(path)
        state.is_locked = True

    def _state_path(self, root_dir: Path) -> Path:
        return root_dir / _STATE_FILE

    def _backup_state_path(self, root_dir: Path) -> Path:
        return root_dir / _BACKUP_STATE_FILE

    def _tmp_state_path(self, root_dir: Path) -> Path:
        return self._state_path(root_dir).with_suffix(".tmp")

    def _corrupt_state_path(self, root_dir: Path) -> Path:
        return self._state_path(root_dir).with_suffix(".corrupt.json")

    def _read_state(self, root_dir: Path) -> tuple[dict[str, object], str | None, bool]:
        state_path = self._state_path(root_dir)
        payload = self._load_payload(state_path)
        recovered_from: str | None = None
        invalid_primary = state_path.exists() and payload is None
        if payload is None:
            payload = self._load_payload(self._tmp_state_path(root_dir))
            if payload is not None:
                recovered_from = "tmp"
        if payload is None:
            payload = self._load_payload(self._backup_state_path(root_dir))
            if payload is not None:
                recovered_from = "backup"
        if payload is None:
            return {}, None, invalid_primary
        if not isinstance(payload, dict):
            return {}, None, invalid_primary
        return payload, recovered_from, invalid_primary

    def _write_state(self, state: VaultState, recovered_from: str | None = None) -> None:
        state.root_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": _SCHEMA_VERSION,
            "updated_at": datetime.now(UTC).isoformat(),
            "project_name": state.project_name,
            "is_locked": state.is_locked,
        }
        normalized_recovered_from = self._parse_recovered_from(recovered_from)
        if normalized_recovered_from is not None:
            payload["recovered_from"] = normalized_recovered_from
        self._write_backup(state.root_dir)
        tmp = self._state_path(state.root_dir).with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self._state_path(state.root_dir))
        self._clear_tmp_state(state.root_dir)
        self._clear_quarantine_state(state.root_dir)

    def _quarantine_invalid_state(self, root_dir: Path) -> None:
        state_path = self._state_path(root_dir)
        if not state_path.exists():
            return
        corrupt = self._corrupt_state_path(root_dir)
        self._unlink_if_exists(corrupt)
        try:
            state_path.replace(corrupt)
        except OSError:
            return

    def _clear_quarantine_state(self, root_dir: Path) -> None:
        self._unlink_if_exists(self._corrupt_state_path(root_dir))

    def _clear_tmp_state(self, root_dir: Path) -> None:
        self._unlink_if_exists(self._tmp_state_path(root_dir))

    def _load_payload(self, path: Path) -> dict[str, object] | None:
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            if path.name == _STATE_FILE:
                self._quarantine_invalid_state(path.parent)
            elif path == self._tmp_state_path(path.parent):
                self._unlink_if_exists(path)
            elif path == self._backup_state_path(path.parent):
                self._unlink_if_exists(path)
            return None
        if not isinstance(payload, dict):
            if path == self._tmp_state_path(path.parent):
                self._unlink_if_exists(path)
            elif path == self._backup_state_path(path.parent):
                self._unlink_if_exists(path)
            return None
        if not self._is_compatible_payload(payload, strict_schema=False):
            if path == self._tmp_state_path(path.parent):
                self._unlink_if_exists(path)
            elif path == self._backup_state_path(path.parent):
                self._unlink_if_exists(path)
            return None
        return payload

    def _write_backup(self, root_dir: Path) -> None:
        state_path = self._state_path(root_dir)
        if not state_path.exists():
            return
        if not self._is_valid_payload(state_path):
            return
        backup_path = self._backup_state_path(root_dir)
        tmp = backup_path.with_suffix(".tmp")
        try:
            tmp.write_bytes(state_path.read_bytes())
            tmp.replace(backup_path)
        except OSError:
            self._unlink_if_exists(tmp)

    def _is_valid_payload(self, path: Path) -> bool:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False
        if not isinstance(payload, dict):
            return False
        return self._is_compatible_payload(payload, strict_schema=True)

    def _is_compatible_payload(self, payload: dict[str, object], *, strict_schema: bool) -> bool:
        schema_version = payload.get("schema_version", 0)
        if type(schema_version) is not int:
            if strict_schema:
                return False
            schema_value = 0
        else:
            if schema_version < 0:
                if strict_schema:
                    return False
                schema_value = 0
            else:
                schema_value = schema_version
        if schema_value < 0:
            if strict_schema:
                return False
            schema_value = 0
        if schema_value > _SCHEMA_VERSION:
            return False
        if "is_locked" in payload and self._parse_is_locked(payload.get("is_locked")) is None:
            return False
        if "project_name" in payload and self._parse_project_name(payload.get("project_name")) is None:
            return False
        if "recovered_from" in payload and self._parse_recovered_from(payload.get("recovered_from")) is None:
            return False
        if "updated_at" in payload and self._parse_updated_at(payload.get("updated_at")) is None:
            return False
        return True

    def _unlink_if_exists(self, path: Path) -> None:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            return

    def _parse_is_locked(self, value: object) -> bool | None:
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            if value in {0, 1}:
                return bool(value)
            return None
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes", "on"}:
                return True
            if normalized in {"false", "0", "no", "off", ""}:
                return False
            return None
        return None

    def _parse_project_name(self, value: object) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            candidate = value.strip()
            if not candidate:
                return None
            try:
                return validate_project_name(candidate)
            except ValueError:
                return None
        return None

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
            parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return None
        return parsed.astimezone(UTC).isoformat()
