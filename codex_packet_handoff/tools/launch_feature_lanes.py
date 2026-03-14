#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = REPO_ROOT / ".codex/packet_router/config.json"
STATE_FILE = REPO_ROOT / ".codex/packet_router/state.json"
KICKOFF_DIR = REPO_ROOT / ".codex/kickoff_packets"
FEATURE_ROOT = REPO_ROOT / ".codex/feature_runner"
LANES = ["feat-commands", "feat-context-storage", "feat-ux-flow", "feat-webconsole-core", "feat-webconsole-ui"]


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Launch feature lane Codex CLI sessions using router runtime mode.")
    ap.add_argument("--lanes", nargs="*", default=LANES, help="Lane names to launch")
    ap.add_argument("--dry-run", action="store_true", help="Print resolved launch commands without starting them")
    return ap.parse_args()


def branch_worktrees() -> Dict[str, str]:
    p = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=True,
    )
    out: Dict[str, str] = {}
    wt = None
    br = None
    for ln in p.stdout.splitlines() + [""]:
        if ln.startswith("worktree "):
            wt = ln.split(" ", 1)[1].strip()
        elif ln.startswith("branch "):
            br = ln.split(" ", 1)[1].strip()
        elif not ln.strip():
            if wt and br:
                out[br] = wt
            wt = None
            br = None
    return out


def runtime_launch_config() -> Dict[str, object]:
    cfg = load_json(CONFIG_FILE, {})
    state = load_json(STATE_FILE, {})
    mode = str(state.get("runtime_mode") or cfg.get("runtime_mode_default") or "cloud_primary")
    if mode == "local_fallback":
        if "fallback_model" in cfg:
            fallback_model = str(cfg.get("fallback_model") or "")
        else:
            fallback_model = str(cfg.get("model") or "")
        fallback_cmd_args = list(cfg.get("fallback_codex_args") or [])
        if "--oss" in [str(x) for x in fallback_cmd_args] and fallback_model == str(cfg.get("model") or ""):
            fallback_model = ""
        return {
            "mode": mode,
            "cmd": str(cfg.get("fallback_codex_cmd") or cfg.get("codex_cmd") or "codex"),
            "cmd_args": fallback_cmd_args,
            "model": fallback_model,
            "model_args": list(cfg.get("fallback_model_args") or []),
        }
    return {
        "mode": mode,
        "cmd": str(cfg.get("codex_cmd") or "codex"),
        "cmd_args": [],
        "model": str(cfg.get("model") or ""),
        "model_args": [],
    }


def build_prompt(lane: str, workdir: str) -> str:
    kickoff = (KICKOFF_DIR / f"{lane}.md").read_text()
    return (
        f"You are the feature lane agent for {lane}.\n\n"
        f"Work only inside the lane worktree at:\n{workdir}\n\n"
        "Before making changes, read these documents from the worktree/repo root:\n"
        "- AGENTS.md\n"
        "- INTEGRATION.md\n"
        "- THREAD_OWNERSHIP.md\n"
        "- ROADMAP.md\n"
        "- PRODUCT_VISION.md\n"
        "- ARCHITECTURE.md\n"
        "- PIPELINE_RUNBOOK.md\n\n"
        "Use this kickoff packet as the operating brief:\n\n"
        f"{kickoff}\n\n"
        "Execution requirements:\n"
        "- Stay inside lane-owned paths only.\n"
        "- Use the kickoff budget and stop triggers exactly as written.\n"
        "- Make a real, meaningful code change from current lane HEAD.\n"
        "- Run the required gates before handoff.\n"
        "- Commit your completed work on the lane branch.\n"
        "- Update the handoff packet fields required by INTEGRATION.md.\n"
        "- Do not wait for more instruction if the next safe step is clear.\n"
    )


def main() -> int:
    args = parse_args()
    launch_cfg = runtime_launch_config()
    worktrees = branch_worktrees()
    prompts_dir = FEATURE_ROOT / "prompts"
    logs_dir = FEATURE_ROOT / "logs"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    launched = []
    for lane in args.lanes:
        branch = f"refs/heads/codex/{lane}"
        workdir = worktrees.get(branch)
        if not workdir:
            print(f"[skip] {lane}: no worktree for {branch}")
            continue
        prompt = build_prompt(lane, workdir)
        prompt_path = prompts_dir / f"{lane}__{ts}.md"
        log_path = logs_dir / f"{lane}__{ts}.log"
        prompt_path.write_text(prompt)
        cmd: List[str] = [str(launch_cfg["cmd"]), *list(launch_cfg["cmd_args"]), "exec"]
        if launch_cfg["model"]:
            cmd.extend(["-m", str(launch_cfg["model"])])
        cmd.extend(list(launch_cfg["model_args"]))
        cmd.extend(["-s", "workspace-write", prompt])
        if args.dry_run:
            print(json.dumps({"lane": lane, "mode": launch_cfg["mode"], "workdir": workdir, "cmd": cmd}, indent=2))
            continue
        with log_path.open("w") as lf:
            proc = subprocess.Popen(
                cmd,
                cwd=workdir,
                stdout=lf,
                stderr=subprocess.STDOUT,
                text=True,
            )
        launched.append({"lane": lane, "pid": proc.pid, "mode": launch_cfg["mode"], "workdir": workdir, "log": str(log_path)})
    print(json.dumps({"runtime_mode": launch_cfg["mode"], "launched": launched}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
