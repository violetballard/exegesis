from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from src.qual.config import validate_project_name

_STATE_FILE = ".vault_state.json"


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
        is_locked = self._read_is_locked(project_root)
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

    def _read_is_locked(self, root_dir: Path) -> bool:
        state_path = self._state_path(root_dir)
        if not state_path.exists():
            return False
        try:
            payload = json.loads(state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False
        if not isinstance(payload, dict):
            return False
        return bool(payload.get("is_locked", False))

    def _write_state(self, state: VaultState) -> None:
        state.root_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "project_name": state.project_name,
            "is_locked": state.is_locked,
        }
        tmp = self._state_path(state.root_dir).with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self._state_path(state.root_dir))
