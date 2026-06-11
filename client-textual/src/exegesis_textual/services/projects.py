from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys


LOCAL_DEVELOPER_ENV = "EXEGESIS_TEXTUAL_LOCAL_DEVELOPER"
RELEASE_MODE_ENV = "EXEGESIS_TEXTUAL_RELEASE_MODE"
TEXTUAL_SETTINGS_PATH_ENV = "EXEGESIS_TEXTUAL_SETTINGS_PATH"
CONFIDENTIALITY_NON_CONFIDENTIAL = "non_confidential"
CONFIDENTIALITY_CONFIDENTIAL = "confidential"
CONFIDENTIALITY_VALUES = (CONFIDENTIALITY_NON_CONFIDENTIAL, CONFIDENTIALITY_CONFIDENTIAL)


@dataclass(frozen=True)
class ProjectRecord:
    name: str
    slug: str
    confidentiality: str = CONFIDENTIALITY_NON_CONFIDENTIAL

    @property
    def display_label(self) -> str:
        expected_slug = safe_project_dir_name(self.name)
        base = self.name if self.slug == expected_slug else f"{self.name} ({self.slug})"
        tag = "[Confidential]" if self.confidentiality == CONFIDENTIALITY_CONFIDENTIAL else "[Non-Confidential]"
        return f"{base} {tag}"

    @property
    def is_confidential(self) -> bool:
        return self.confidentiality == CONFIDENTIALITY_CONFIDENTIAL


def normalize_project_confidentiality(raw: object) -> str:
    return raw if isinstance(raw, str) and raw in CONFIDENTIALITY_VALUES else CONFIDENTIALITY_NON_CONFIDENTIAL


def textual_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def textual_projects_dir(repo_root: Path | None = None) -> Path:
    env_value = os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR")
    if env_value:
        return Path(env_value).expanduser()
    configured = _textual_settings_projects_dir(repo_root or textual_repo_root())
    if configured:
        return configured
    if is_release_mode():
        return Path.home() / "Documents" / "Exegesis"
    return Path.home() / "exegesis"


def is_local_developer_mode() -> bool:
    return os.environ.get(LOCAL_DEVELOPER_ENV) == "1" and not is_release_mode()


def is_release_mode() -> bool:
    return os.environ.get(RELEASE_MODE_ENV) == "1"


def textual_settings_path(repo_root: Path | None = None) -> Path:
    override = os.environ.get(TEXTUAL_SETTINGS_PATH_ENV)
    if override:
        return Path(override).expanduser()
    if is_local_developer_mode():
        return (repo_root or textual_repo_root()) / ".codex" / "shell" / "settings.json"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Exegesis" / "settings.json"
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        base = Path(appdata).expanduser() if appdata else Path.home() / "AppData" / "Roaming"
        return base / "Exegesis" / "settings.json"
    return Path.home() / ".config" / "Exegesis" / "settings.json"


def load_textual_settings(repo_root: Path | None = None) -> dict[str, object]:
    try:
        raw = json.loads(textual_settings_path(repo_root).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def save_textual_settings(settings: dict[str, object], repo_root: Path | None = None) -> None:
    settings_path = textual_settings_path(repo_root)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(settings, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _load_textual_settings(repo_root: Path) -> dict[str, object]:
    return load_textual_settings(repo_root)


def _save_textual_settings(settings: dict[str, object], repo_root: Path) -> None:
    save_textual_settings(settings, repo_root)


def _textual_settings_projects_dir(repo_root: Path) -> Path | None:
    raw = _load_textual_settings(repo_root)
    projects_dir = raw.get("projects_dir")
    if not isinstance(projects_dir, str) or not projects_dir.strip():
        return None
    return Path(projects_dir).expanduser()


def save_textual_projects_dir(projects_dir: Path, repo_root: Path | None = None) -> None:
    root = repo_root or textual_repo_root()
    settings = _load_textual_settings(root)
    settings["projects_dir"] = str(projects_dir.expanduser().resolve())
    _save_textual_settings(settings, root)


def textual_last_project_name(repo_root: Path | None = None) -> str | None:
    if os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR"):
        return None
    value = _load_textual_settings(repo_root or textual_repo_root()).get("last_project_name")
    return value if isinstance(value, str) and value.strip() else None


def save_textual_last_project_name(project_name: str, repo_root: Path | None = None) -> None:
    if os.environ.get("EXEGESIS_TEXTUAL_PROJECTS_DIR"):
        return
    root = repo_root or textual_repo_root()
    settings = _load_textual_settings(root)
    settings["last_project_name"] = project_name
    _save_textual_settings(settings, root)


def safe_project_dir_name(project_name: str) -> str:
    safe = "".join(char.lower() if char.isalnum() else "-" for char in project_name).strip("-")
    return safe or "untitled-project"
