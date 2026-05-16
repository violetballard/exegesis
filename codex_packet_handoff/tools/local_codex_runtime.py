#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import tomllib
from typing import Dict


AGENT_RIPGREP_CONFIG_TEXT = "\n".join(
    [
        "--glob",
        "!.codex/**",
        "--glob",
        "!.agents/**",
        "",
    ]
)


def _source_codex_home() -> Path:
    raw = os.environ.get("CODEX_HOME")
    if raw:
        return Path(raw).expanduser()
    return Path.home() / ".codex"


def isolated_codex_home(root: str) -> Path:
    return Path(root).resolve() / ".codex" / "local_codex_runtime"


def _toml_literal(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, list):
        return "[" + ", ".join(_toml_literal(item) for item in value) + "]"
    raise TypeError(f"unsupported TOML value: {type(value)!r}")


def _minimal_local_config_text(root: str, source_text: str | None) -> str:
    parsed = tomllib.loads(source_text) if source_text else {}
    repo_root = str(Path(root).resolve())

    model_providers = parsed.get("model_providers", {})
    lms_cfg = dict(model_providers.get("lms", {}))
    lms_cfg.setdefault("name", "LM Studio")
    lms_cfg.setdefault("base_url", "http://127.0.0.1:1234/v1")

    source_projects = parsed.get("projects", {})
    trust_level = "trusted"
    if isinstance(source_projects, dict):
        existing_project_cfg = source_projects.get(repo_root, {})
        if isinstance(existing_project_cfg, dict):
            trust_level = existing_project_cfg.get("trust_level", trust_level)

    source_profiles = parsed.get("profiles", {})
    local_profiles = {}
    if isinstance(source_profiles, dict):
        for name, profile in source_profiles.items():
            if isinstance(profile, dict) and profile.get("model_provider") == "lms":
                local_profiles[name] = profile

    if not local_profiles:
        local_profiles = {
            "gemma-4-31b-it-lms": {"model_provider": "lms", "model": "gemma-4-31b-it"},
            "gpt-oss-120b-lms": {"model_provider": "lms", "model": "gpt-oss-120b"},
        }
    else:
        local_profiles.setdefault("gemma-4-31b-it-lms", {"model_provider": "lms", "model": "gemma-4-31b-it"})

    lines: list[str] = [
        'model = "gemma-4-31b-it"',
        'oss_provider = "lmstudio"',
        "",
        f'[projects.{_toml_literal(repo_root)}]',
        f"trust_level = {_toml_literal(trust_level)}",
        "",
        "[model_providers.lms]",
    ]

    for key, value in lms_cfg.items():
        lines.append(f"{key} = {_toml_literal(value)}")

    for profile_name in sorted(local_profiles):
        profile = local_profiles[profile_name]
        lines.extend(["", f"[profiles.{profile_name}]"])
        for key, value in profile.items():
            lines.append(f"{key} = {_toml_literal(value)}")

    lines.extend(
        [
            "",
            "[features]",
            "plugins = false",
            "responses_websockets = false",
            "responses_websockets_v2 = false",
            "",
        ]
    )

    return "\n".join(lines)


def isolated_codex_env(root: str) -> Dict[str, str]:
    source_home = _source_codex_home()
    source_config = source_home / "config.toml"
    target_home = isolated_codex_home(root)
    target_home.mkdir(parents=True, exist_ok=True)
    target_config = target_home / "config.toml"
    source_text = source_config.read_text(encoding="utf-8") if source_config.exists() else None
    desired_text = _minimal_local_config_text(root, source_text)
    current_text = target_config.read_text(encoding="utf-8") if target_config.exists() else None
    if current_text != desired_text:
        target_config.write_text(desired_text, encoding="utf-8")

    env = os.environ.copy()
    env["CODEX_HOME"] = str(target_home)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["RIPGREP_CONFIG_PATH"] = str(agent_ripgrep_config_path(root))
    return env


def agent_ripgrep_config_path(root: str) -> Path:
    target = Path(root).resolve() / ".codex" / "agent_ripgrep_config"
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        target = Path(tempfile.gettempdir()) / "qual_agent_ripgrep_config"
    current_text = target.read_text(encoding="utf-8") if target.exists() else None
    if current_text != AGENT_RIPGREP_CONFIG_TEXT:
        target.write_text(AGENT_RIPGREP_CONFIG_TEXT, encoding="utf-8")
    return target


def agent_runtime_env(root: str, base: Dict[str, str] | None = None) -> Dict[str, str]:
    env = dict(base or os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["RIPGREP_CONFIG_PATH"] = str(agent_ripgrep_config_path(root))
    return env
