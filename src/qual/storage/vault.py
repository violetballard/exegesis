from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from src.qual.config import validate_project_name

_STATE_FILE = ".vault_state.json"
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
        raw_state = self._read_state(project_root)
        is_locked = bool(raw_state.get("is_locked", False))
        if raw_state.get("project_name") not in {None, safe_project_name}:
            # If metadata does not match directory identity, prefer a safe default.
            is_locked = True
        state = VaultState(
            project_name=safe_project_name,
            root_dir=project_root,
            is_locked=is_locked,
        )
        self._write_state(state)
        return state

    def lock(self, state: VaultState) -> None:
        state.is_locked = True
        self._write_state(state)

    def unlock(self, state: VaultState) -> None:
        state.is_locked = False
        self._write_state(state)

    def _state_path(self, root_dir: Path) -> Path:
        return root_dir / _STATE_FILE

    def _read_state(self, root_dir: Path) -> dict[str, object]:
        state_path = self._state_path(root_dir)
        if not state_path.exists():
            return {}
        try:
            payload = json.loads(state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._quarantine_invalid_state(root_dir)
            return {}
        if not isinstance(payload, dict):
            return {}
        return payload

    def _write_state(self, state: VaultState) -> None:
        state.root_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": _SCHEMA_VERSION,
            "project_name": state.project_name,
            "is_locked": state.is_locked,
        }
        tmp = self._state_path(state.root_dir).with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self._state_path(state.root_dir))

    def _quarantine_invalid_state(self, root_dir: Path) -> None:
        state_path = self._state_path(root_dir)
        if not state_path.exists():
            return
        corrupt = state_path.with_suffix(".corrupt.json")
        if corrupt.exists():
            corrupt.unlink()
        state_path.replace(corrupt)
