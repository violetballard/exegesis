from __future__ import annotations

import os
from pathlib import Path
from importlib import resources
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence

RELEASE_MODE_ENV = "EXEGESIS_TEXTUAL_RELEASE_MODE"
LOCAL_DEVELOPER_ENV = "EXEGESIS_TEXTUAL_LOCAL_DEVELOPER"
SYSTEM_PROMPT_OVERRIDE_ENV = "EXEGESIS_SYSTEM_PROMPT_PATH"
BUNDLED_WEZTERM_ENV = "EXEGESIS_BUNDLED_WEZTERM"
TERMINAL_CHILD_ENV = "EXEGESIS_TEXTUAL_TERMINAL_CHILD"
APP_NAME = "Exegesis"


def release_child_environment(base: Mapping[str, str] | None = None) -> dict[str, str]:
    env = dict(base or os.environ)
    env.pop(LOCAL_DEVELOPER_ENV, None)
    env.pop(SYSTEM_PROMPT_OVERRIDE_ENV, None)
    env.pop("NO_COLOR", None)
    env[RELEASE_MODE_ENV] = "1"
    env[TERMINAL_CHILD_ENV] = "1"
    env.setdefault("COLORTERM", "truecolor")
    env.setdefault("TERM", "xterm-256color")
    return env


def _candidate_wezterm_paths(start: Path) -> list[Path]:
    candidates: list[Path] = []
    for parent in (start, *start.parents):
        resources_dir = parent / "Contents" / "Resources"
        candidates.extend(
            [
                resources_dir / "WezTerm.app" / "Contents" / "MacOS" / "wezterm-gui",
                resources_dir / "wezterm" / "WezTerm.app" / "Contents" / "MacOS" / "wezterm-gui",
                resources_dir / "support" / "WezTerm.app" / "Contents" / "MacOS" / "wezterm-gui",
            ]
        )
    return candidates


def find_bundled_wezterm(executable: Path | None = None) -> Path:
    override = os.environ.get(BUNDLED_WEZTERM_ENV)
    if override:
        path = Path(override).expanduser()
        if path.exists():
            return path
        raise FileNotFoundError(f"Configured bundled WezTerm does not exist: {path}")

    start = executable or Path(sys.executable).resolve()
    for candidate in _candidate_wezterm_paths(start):
        if candidate.exists():
            return candidate

    dev_fallback = shutil.which("wezterm")
    if dev_fallback:
        return Path(dev_fallback)
    raise FileNotFoundError("Bundled WezTerm runtime was not found inside Exegesis.app.")


def wezterm_config_path() -> Path:
    package_files = resources.files("exegesis_textual.desktop.resources")
    return Path(str(package_files.joinpath("wezterm.lua")))


def build_wezterm_command(
    wezterm_path: Path,
    config_path: Path,
    python_executable: Path | None = None,
    module: str = "exegesis_textual.app.main",
) -> list[str]:
    python_path = python_executable or Path(sys.executable)
    command = [
        str(wezterm_path),
        "--config-file",
        str(config_path),
        "start",
        "--always-new-process",
        "--cwd",
        str(Path.home()),
        "--",
        str(python_path),
    ]
    if python_path.name.casefold().startswith("python"):
        command.extend(["-m", module])
    return command


def main(argv: Sequence[str] | None = None) -> int:
    _ = argv
    wezterm_path = find_bundled_wezterm()
    config_path = wezterm_config_path()
    command = build_wezterm_command(wezterm_path, config_path)
    return subprocess.call(command, env=release_child_environment())


__all__ = [
    "APP_NAME",
    "BUNDLED_WEZTERM_ENV",
    "LOCAL_DEVELOPER_ENV",
    "RELEASE_MODE_ENV",
    "SYSTEM_PROMPT_OVERRIDE_ENV",
    "TERMINAL_CHILD_ENV",
    "build_wezterm_command",
    "find_bundled_wezterm",
    "main",
    "release_child_environment",
    "wezterm_config_path",
]
