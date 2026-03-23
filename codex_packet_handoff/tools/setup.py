#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json

LANES = [
    'feat-context-storage',
    'feat-ux-flow',
    'feat-commands',
    'feat-retrieval-fts',
    'feat-a2ui-contract',
    'feat-engine-runs',
    'feat-console',
]

def ensure_dirs():
    for lane in LANES:
        base = Path(".codex/packets/lanes") / lane
        (base / "inbox/feature").mkdir(parents=True, exist_ok=True)
        (base / "inbox/reviewer").mkdir(parents=True, exist_ok=True)
        (base / "outbox/integrator").mkdir(parents=True, exist_ok=True)
        (base / "archive").mkdir(parents=True, exist_ok=True)
    Path(".codex/packet_router").mkdir(parents=True, exist_ok=True)
    Path(".codex/packet_planner").mkdir(parents=True, exist_ok=True)
    Path(".codex/lane_meta").mkdir(parents=True, exist_ok=True)

def write_example_config():
    lanes_cfg = {}
    for lane in LANES:
        lanes_cfg[lane] = {"branch": f"codex/{lane}", "enabled": True}
    lanes_cfg["feat-console"]["enabled"] = False
    example = {
        "model": "gpt-5.1-codex",
        "codex_cmd": "codex",
        "fallback_model": "",
        "fallback_codex_cmd": "",
        "fallback_codex_args": [],
        "fallback_model_args": [],
        "profiles": {
            "orchestrator": {
                "codex_cmd": "codex",
                "codex_args": [],
                "model": "gpt-5.1-codex",
                "model_args": [],
            },
            "worker_cloud": {
                "codex_cmd": "codex",
                "codex_args": [],
                "model": "gpt-5.1-codex",
                "model_args": [],
            },
            "worker_local": {
                "codex_cmd": "codex",
                "codex_args": [],
                "model": "",
                "model_args": [],
            },
        },
        "role_profiles": {
            "orchestrator": "orchestrator",
            "cloud_probe": "worker_cloud",
            "feature_cloud": "worker_cloud",
            "feature_local": "worker_local",
            "reviewer_cloud": "worker_cloud",
            "reviewer_local": "worker_local",
            "integrator_cloud": "worker_cloud",
            "integrator_local": "worker_local",
            "fixer_cloud": "worker_cloud",
            "fixer_local": "worker_local",
        },
        "runtime_mode_default": "cloud_primary",
        "auto_switch_to_local_on_quota": True,
        "auto_probe_cloud_recovery": True,
        "cloud_probe_cooldown_seconds": 1800,
        "cloud_probe_timeout_seconds": 30,
        "use_cli_reviewer_fallback": True,
        "use_cli_integrator_fallback": True,
        "idle_seconds": 1.2,
        "reviewer_timeout": 180,
        "integrator_timeout": 900,
        "lanes": lanes_cfg,
        "planner": {
            "base_ref": "codex/integrator",
            "required_gates": [
                "./quality-format.sh --check",
                "./quality-lint.sh",
                "./quality-test.sh",
                "./typecheck-test.sh",
                "make ci"
            ]
        }
    }
    out = Path(".codex/packet_router/example.json")
    out.write_text(json.dumps(example, indent=2))
    print(out)

def ensure_gitignore():
    gi = Path(".gitignore")
    line = ".codex/"
    if gi.exists():
        lines = gi.read_text().splitlines()
        if line not in lines:
            gi.write_text(gi.read_text().rstrip() + "\n" + line + "\n")
    else:
        gi.write_text(line + "\n")

if __name__ == "__main__":
    ensure_dirs()
    write_example_config()
    ensure_gitignore()
    print("[setup] done")
