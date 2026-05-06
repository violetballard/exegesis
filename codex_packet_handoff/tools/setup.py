#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json

APP_CODEX_CMD = "/Applications/Codex.app/Contents/Resources/codex"
APP_OPENCODE_CMD = "/opt/homebrew/bin/opencode"
LOCAL_QWEN_MODEL = "qwen3.6-27b"
CODEX_CLOUD_CONTEXT_ARGS = ["-c", "model_context_window=256000"]

LANES = [
    'feat-context-storage',
    'feat-commands',
    'feat-retrieval-fts',
    'feat-a2ui-contract',
    'feat-engine-runs',
    'feat-console-shell',
    'feat-console-workflow',
    'feat-ocr-import',
    'feat-literature-import',
    'feat-rag-index',
    'feat-qual-coding',
    'feat-editor-basics',
    'feat-citations',
    'feat-export',
    'feat-zotero-import',
    'feat-formatting-bar',
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
    lanes_cfg["feat-console-shell"]["enabled"] = False
    lanes_cfg["feat-console-workflow"]["enabled"] = False
    lanes_cfg["feat-ocr-import"]["enabled"] = False
    lanes_cfg["feat-literature-import"]["enabled"] = False
    lanes_cfg["feat-rag-index"]["enabled"] = False
    lanes_cfg["feat-qual-coding"]["enabled"] = False
    lanes_cfg["feat-editor-basics"]["enabled"] = False
    lanes_cfg["feat-citations"]["enabled"] = False
    lanes_cfg["feat-export"]["enabled"] = False
    lanes_cfg["feat-zotero-import"]["enabled"] = False
    lanes_cfg["feat-formatting-bar"]["enabled"] = False
    for lane in ("feat-commands", "feat-retrieval-fts"):
        lanes_cfg[lane].update(
            {
                "feature_cloud_profile": "worker_cloud_standard_medium",
                "reviewer_cloud_profile": "worker_cloud_standard_medium",
                "fixer_cloud_profile": "worker_cloud_standard_medium",
                "integrator_cloud_profile": "integrator_cloud",
            }
        )
    lanes_cfg["feat-retrieval-fts"].update(
        {
            "feature_local_profile": "worker_local_heavy",
            "reviewer_local_profile": "worker_local_heavy",
            "fixer_local_profile": "worker_local_heavy",
            "integrator_local_profile": "worker_local_heavy",
        }
    )
    for lane in ("feat-a2ui-contract", "feat-engine-runs"):
        lanes_cfg[lane].update(
            {
                "feature_local_profile": "worker_local_heavy",
                "reviewer_local_profile": "worker_local_heavy",
                "fixer_local_profile": "worker_local_heavy",
                "integrator_local_profile": "worker_local_heavy",
            }
        )
    example = {
        "model": "gpt-5.1-codex",
        "codex_cmd": APP_CODEX_CMD,
        "fallback_model": LOCAL_QWEN_MODEL,
        "fallback_codex_cmd": APP_OPENCODE_CMD,
        "fallback_codex_args": [],
        "fallback_model_args": [],
        "profiles": {
            "orchestrator": {
                "codex_cmd": APP_CODEX_CMD,
                "codex_args": ["--oss", "--local-provider", "lmstudio"],
                "model": "gpt-oss-120b",
                "model_args": [],
            },
            "worker_cloud": {
                "codex_cmd": APP_CODEX_CMD,
                "codex_args": CODEX_CLOUD_CONTEXT_ARGS,
                "model": "gpt-5.5",
                "model_args": ["-c", "model_reasoning_effort=low"],
            },
            "worker_cloud_standard_medium": {
                "codex_cmd": APP_CODEX_CMD,
                "codex_args": CODEX_CLOUD_CONTEXT_ARGS,
                "model": "gpt-5.5",
                "model_args": ["-c", "model_reasoning_effort=medium"],
            },
            "integrator_cloud": {
                "codex_cmd": APP_CODEX_CMD,
                "codex_args": CODEX_CLOUD_CONTEXT_ARGS,
                "model": "gpt-5.5",
                "model_args": ["-c", "model_reasoning_effort=high"],
            },
            "worker_local": {
                "harness": "opencode",
                "codex_cmd": APP_OPENCODE_CMD,
                "codex_args": [],
                "model": LOCAL_QWEN_MODEL,
                "model_args": [],
            },
            "worker_local_heavy": {
                "harness": "opencode",
                "codex_cmd": APP_OPENCODE_CMD,
                "codex_args": [],
                "model": LOCAL_QWEN_MODEL,
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
            "integrator_cloud": "integrator_cloud",
            "integrator_local": "worker_local",
            "fixer_cloud": "worker_cloud",
            "fixer_local": "worker_local",
        },
        "runtime_mode_default": "hybrid",
        "auto_switch_to_local_on_quota": True,
        "auto_probe_cloud_recovery": True,
        "disable_local_fallback_on_cloud_timeout": True,
        "cloud_probe_cooldown_seconds": 300,
        "cloud_probe_timeout_seconds": 30,
        "feature_launch_timeout_seconds": 300,
        "max_parallel_feature_lanes_cloud": 4,
        "max_parallel_feature_lanes_local": 3,
        "max_cloud_feature_jobs": 4,
        "max_cloud_reviewer_jobs": 4,
        "max_cloud_integrator_jobs": 4,
        "max_cloud_fixer_jobs": 4,
        "max_total_cloud_jobs": 4,
        "max_total_local_lms_jobs": 4,
        "prefer_direct_exec_feature_cloud": True,
        "prefer_cli_reviewer": True,
        "prefer_cli_integrator": True,
        "use_cli_reviewer_fallback": True,
        "use_cli_integrator_fallback": True,
        "idle_seconds": 1.2,
        "reviewer_timeout": 180,
        "integrator_timeout": 900,
        "max_cloud_fixer_kicks_per_run": 1,
        "max_local_fixer_kicks_per_run": 1,
        "max_local_fixer_jobs": 1,
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
