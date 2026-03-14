#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from codex_mcp_client import ApprovalPolicy, CodexMcpClient

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = REPO_ROOT / ".codex/packet_router/config.json"
STATE_FILE = REPO_ROOT / ".codex/packet_router/state.json"
KICKOFF_DIR = REPO_ROOT / ".codex/kickoff_packets"
FEATURE_ROOT = REPO_ROOT / ".codex/feature_runner"
FEATURE_STATE_FILE = FEATURE_ROOT / "state.json"
LANES = ["feat-commands", "feat-context-storage", "feat-ux-flow", "feat-webconsole-core", "feat-webconsole-ui"]


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def _normalize_profile(raw: Dict[str, object], fallback_cmd: str, fallback_model: str) -> Dict[str, object]:
    cmd_args = list(raw.get("codex_args") or [])
    if "model" in raw:
        model = str(raw.get("model") or "")
    else:
        model = fallback_model
    if "--oss" in [str(x) for x in cmd_args] and model == fallback_model:
        model = ""
    return {
        "cmd": str(raw.get("codex_cmd") or fallback_cmd or "codex"),
        "cmd_args": [str(x) for x in cmd_args],
        "model": model,
        "model_args": [str(x) for x in list(raw.get("model_args") or [])],
    }


def _resolved_profiles(cfg: Dict[str, object]) -> Dict[str, Dict[str, object]]:
    cloud = {
        "cmd": str(cfg.get("codex_cmd") or "codex"),
        "cmd_args": [],
        "model": str(cfg.get("model") or ""),
        "model_args": [],
    }
    local = {
        "cmd": str(cfg.get("fallback_codex_cmd") or cfg.get("codex_cmd") or "codex"),
        "cmd_args": [str(x) for x in list(cfg.get("fallback_codex_args") or [])],
        "model": str(cfg.get("fallback_model") or ""),
        "model_args": [str(x) for x in list(cfg.get("fallback_model_args") or [])],
    }
    out = {
        "orchestrator": cloud,
        "worker_cloud": cloud,
        "worker_local": local,
    }
    for name, raw in dict(cfg.get("profiles") or {}).items():
        if isinstance(raw, dict):
            base = out.get(str(name), cloud)
            out[str(name)] = _normalize_profile(raw, str(base["cmd"]), str(base["model"]))
    return out


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Launch or resume feature lane managed Codex sessions.")
    ap.add_argument("--lanes", nargs="*", default=LANES, help="Lane names to launch")
    ap.add_argument("--restart-existing", action="store_true", help="Start a fresh managed session even if lane state exists")
    ap.add_argument("--dry-run", action="store_true", help="Print resolved launch plan without starting managed sessions")
    return ap.parse_args()


def branch_worktrees() -> Dict[str, str]:
    import subprocess

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
    role_profiles = {
        "feature_cloud": "worker_cloud",
        "feature_local": "worker_local",
        **{str(k): str(v) for k, v in dict(cfg.get("role_profiles") or {}).items() if v},
    }
    profiles = _resolved_profiles(cfg)
    profile_name = role_profiles["feature_local" if mode == "local_fallback" else "feature_cloud"]
    prof = profiles[profile_name]
    return {"mode": mode, "profile_name": profile_name, **prof}


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


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _open_client(launch_cfg: Dict[str, object]) -> CodexMcpClient:
    return CodexMcpClient(
        approval=ApprovalPolicy(allow_exec=True, allow_apply_patch=True),
        codex_cmd=str(launch_cfg["cmd"]),
        codex_args=[str(x) for x in list(launch_cfg["cmd_args"])],
    )


def _write_log(log_path: Path, header: Dict[str, Any], content: str) -> None:
    lines = [json.dumps(header, sort_keys=True), "", content.strip(), ""]
    log_path.write_text("\n".join(lines))


def _set_lane_state(
    feature_state: Dict[str, Any],
    lane: str,
    *,
    status: str,
    mode: str,
    profile: str,
    workdir: str,
    prompt_path: Path,
    log_path: Path,
    thread_id: str = "",
    error: str = "",
    action: str = "",
) -> None:
    lanes_state = feature_state.setdefault("lanes", {})
    lanes_state[lane] = {
        "status": status,
        "thread_id": thread_id,
        "mode": mode,
        "profile": profile,
        "workdir": workdir,
        "prompt_path": str(prompt_path),
        "log_path": str(log_path),
        "last_launch_at": _ts(),
        "last_action": action or status,
        "error": error,
    }
    save_json(FEATURE_STATE_FILE, feature_state)


def main() -> int:
    args = parse_args()
    launch_cfg = runtime_launch_config()
    worktrees = branch_worktrees()
    prompts_dir = FEATURE_ROOT / "prompts"
    logs_dir = FEATURE_ROOT / "logs"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    feature_state = load_json(FEATURE_STATE_FILE, {"lanes": {}})
    if not isinstance(feature_state, dict):
        feature_state = {"lanes": {}}
    lanes_state = feature_state.setdefault("lanes", {})
    launched: List[Dict[str, Any]] = []

    if args.dry_run:
        for lane in args.lanes:
            branch = f"refs/heads/codex/{lane}"
            workdir = worktrees.get(branch)
            launched.append(
                {
                    "lane": lane,
                    "mode": launch_cfg["mode"],
                    "profile": launch_cfg["profile_name"],
                    "workdir": workdir,
                    "action": "launch" if args.restart_existing or lane not in lanes_state else "resume",
                }
            )
        print(json.dumps({"runtime_mode": launch_cfg["mode"], "launched": launched}, indent=2))
        return 0

    client = _open_client(launch_cfg)
    try:
        for lane in args.lanes:
            branch = f"refs/heads/codex/{lane}"
            workdir = worktrees.get(branch)
            if not workdir:
                launched.append({"lane": lane, "status": "skipped", "reason": f"no worktree for {branch}"})
                continue
            prompt = build_prompt(lane, workdir)
            prompt_path = prompts_dir / f"{lane}__{_ts()}.md"
            prompt_path.write_text(prompt)
            log_path = logs_dir / f"{lane}__{_ts()}.log"
            lane_state = lanes_state.get(lane) if isinstance(lanes_state.get(lane), dict) else {}
            thread_id = None if args.restart_existing else lane_state.get("thread_id")
            _set_lane_state(
                feature_state,
                lane,
                status="launching",
                mode=str(launch_cfg["mode"]),
                profile=str(launch_cfg["profile_name"]),
                workdir=workdir,
                prompt_path=prompt_path,
                log_path=log_path,
                thread_id=str(thread_id or ""),
                action="resume" if thread_id else "launch",
            )
            _write_log(
                log_path,
                {
                    "lane": lane,
                    "thread_id": str(thread_id or ""),
                    "mode": launch_cfg["mode"],
                    "profile": launch_cfg["profile_name"],
                    "workdir": workdir,
                    "action": "resume" if thread_id else "launch",
                    "launched_at": _ts(),
                    "status": "launching",
                },
                "Managed feature lane launch started.",
            )
            try:
                if thread_id:
                    thread_id, content = client.codex_reply(
                        str(thread_id),
                        "Resume work from the current lane branch and continue toward the next valid handoff.",
                        timeout=900.0,
                    )
                    action = "resumed"
                else:
                    thread_id, content = client.codex(
                        prompt=prompt,
                        cwd=workdir,
                        sandbox="workspace-write",
                        approval_policy="never",
                        model=str(launch_cfg["model"]),
                        timeout=900.0,
                    )
                    action = "launched"
                header = {
                    "lane": lane,
                    "thread_id": thread_id,
                    "mode": launch_cfg["mode"],
                    "profile": launch_cfg["profile_name"],
                    "workdir": workdir,
                    "action": action,
                    "launched_at": _ts(),
                }
                _write_log(log_path, header, content)
                _set_lane_state(
                    feature_state,
                    lane,
                    status="managed_thread",
                    mode=str(launch_cfg["mode"]),
                    profile=str(launch_cfg["profile_name"]),
                    workdir=workdir,
                    prompt_path=prompt_path,
                    log_path=log_path,
                    thread_id=str(thread_id),
                    action=action,
                )
                launched.append(
                    {
                        "lane": lane,
                        "status": action,
                        "thread_id": thread_id,
                        "mode": launch_cfg["mode"],
                        "profile": launch_cfg["profile_name"],
                        "workdir": workdir,
                        "log": str(log_path),
                    }
                )
            except Exception as exc:
                _set_lane_state(
                    feature_state,
                    lane,
                    status="error",
                    mode=str(launch_cfg["mode"]),
                    profile=str(launch_cfg["profile_name"]),
                    workdir=workdir,
                    prompt_path=prompt_path,
                    log_path=log_path,
                    thread_id=str(thread_id or ""),
                    error=str(exc),
                    action="resume" if thread_id else "launch",
                )
                _write_log(
                    log_path,
                    {
                        "lane": lane,
                        "thread_id": str(thread_id or ""),
                        "mode": launch_cfg["mode"],
                        "profile": launch_cfg["profile_name"],
                        "workdir": workdir,
                        "action": "resume" if thread_id else "launch",
                        "launched_at": _ts(),
                        "status": "error",
                    },
                    str(exc),
                )
                launched.append(
                    {
                        "lane": lane,
                        "status": "error",
                        "mode": launch_cfg["mode"],
                        "profile": launch_cfg["profile_name"],
                        "workdir": workdir,
                        "error": str(exc),
                    }
                )
    finally:
        client.close()

    print(json.dumps({"runtime_mode": launch_cfg["mode"], "launched": launched}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
