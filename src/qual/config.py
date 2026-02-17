from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


_SAFE_PROJECT_RE = re.compile(r"^[A-Za-z0-9._-]+$")


@dataclass(frozen=True)
class AppConfig:
    app_name: str
    app_data_dir: Path
    default_project_name: str


def validate_project_name(raw: str) -> str:
    project = raw.strip()
    if not project:
        raise ValueError("project name must not be empty")
    if project in {".", ".."}:
        raise ValueError("project name must not be '.' or '..'")
    if "/" in project or "\\" in project:
        raise ValueError("project name must not include path separators")
    if ".." in project:
        raise ValueError("project name must not include '..'")
    if not _SAFE_PROJECT_RE.fullmatch(project):
        raise ValueError("project name may contain only letters, numbers, '.', '_' or '-'")
    return project


def _project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "src").is_dir():
            return parent
    return Path.cwd()


def default_config() -> AppConfig:
    project_root = _project_root()
    return AppConfig(
        app_name="Qual Workstation",
        app_data_dir=project_root / ".local_app_data" / "qual_workstation",
        default_project_name="default-project",
    )
