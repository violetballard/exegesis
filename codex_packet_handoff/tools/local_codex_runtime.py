#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict


def _source_codex_home() -> Path:
    raw = os.environ.get("CODEX_HOME")
    if raw:
        return Path(raw).expanduser()
    return Path.home() / ".codex"


def isolated_codex_home(root: str) -> Path:
    return Path(root).resolve() / ".codex" / "local_codex_runtime"


def isolated_codex_env(root: str) -> Dict[str, str]:
    source_home = _source_codex_home()
    source_config = source_home / "config.toml"
    target_home = isolated_codex_home(root)
    target_home.mkdir(parents=True, exist_ok=True)
    target_config = target_home / "config.toml"

    if source_config.exists():
        source_text = source_config.read_text(encoding="utf-8")
        current_text = target_config.read_text(encoding="utf-8") if target_config.exists() else None
        if current_text != source_text:
            target_config.write_text(source_text, encoding="utf-8")

    env = os.environ.copy()
    env["CODEX_HOME"] = str(target_home)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env
