from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.qual.config import validate_project_name


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
        return VaultState(
            project_name=safe_project_name,
            root_dir=project_root,
            is_locked=False,
        )

    def lock(self, state: VaultState) -> None:
        state.is_locked = True

    def unlock(self, state: VaultState) -> None:
        state.is_locked = False
