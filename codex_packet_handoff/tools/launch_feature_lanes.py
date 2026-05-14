#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from codex_mcp_client import ApprovalPolicy, CodexMcpClient

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = REPO_ROOT / ".codex/packet_router/config.json"
STATE_FILE = REPO_ROOT / ".codex/packet_router/state.json"
KICKOFF_DIR = REPO_ROOT / ".codex/kickoff_packets"
FEATURE_ROOT = REPO_ROOT / ".codex/feature_runner"
FEATURE_STATE_FILE = FEATURE_ROOT / "state.json"
DEFAULT_LANES = [
    "feat-commands",
    "feat-context-storage",
    "feat-ux-flow",
    "feat-retrieval-fts",
    "feat-a2ui-contract",
    "feat-engine-runs",
    "feat-console",
]
STATE_LOCK = threading.Lock()


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def _enabled_lanes() -> List[str]:
    cfg = load_json(CONFIG_FILE, {})
    lanes = cfg.get("lanes") if isinstance(cfg, dict) else {}
    if isinstance(lanes, dict) and lanes:
        return [name for name, lane_cfg in lanes.items() if bool((lane_cfg or {}).get("enabled", True))]
    return list(DEFAULT_LANES)


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


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
    ap.add_argument("--lanes", nargs="*", default=None, help="Lane names to launch")
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
    local_profile_name = role_profiles["feature_local"]
    prof = profiles[profile_name]
    local_prof = profiles[local_profile_name]
    return {
        "mode": mode,
        "profile_name": profile_name,
        "launch_timeout_seconds": float(cfg.get("feature_launch_timeout_seconds", 120)),
        "local_profile_name": local_profile_name,
        "local_profile": local_prof,
        **prof,
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


def _spawn_direct_exec(profile_cfg: Dict[str, object], *, workdir: str, prompt: str, log_path: Path) -> int:
    cmd: List[str] = [str(profile_cfg["cmd"]), *[str(x) for x in list(profile_cfg["cmd_args"])], "exec"]
    model = str(profile_cfg.get("model") or "")
    if model:
        cmd.extend(["-m", model])
    cmd.extend([str(x) for x in list(profile_cfg.get("model_args") or [])])
    cmd.extend(["-s", "workspace-write", prompt])
    with log_path.open("a") as lf:
        proc = subprocess.Popen(
            cmd,
            cwd=workdir,
            stdout=lf,
            stderr=subprocess.STDOUT,
            text=True,
        )
    return proc.pid


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
    pid: int = 0,
) -> None:
    with STATE_LOCK:
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
            "pid": pid,
        }
        save_json(FEATURE_STATE_FILE, feature_state)


def _launch_one_lane(
    lane: str,
    *,
    args: argparse.Namespace,
    launch_cfg: Dict[str, object],
    worktrees: Dict[str, str],
    prompts_dir: Path,
    logs_dir: Path,
    feature_state: Dict[str, Any],
) -> Dict[str, Any]:
    branch = f"refs/heads/codex/{lane}"
    workdir = worktrees.get(branch)
    if not workdir:
        return {"lane": lane, "status": "skipped", "reason": f"no worktree for {branch}"}

    prompt = build_prompt(lane, workdir)
    prompt_path = prompts_dir / f"{lane}__{_ts()}.md"
    prompt_path.write_text(prompt)
    log_path = logs_dir / f"{lane}__{_ts()}.log"
    lane_state = feature_state.get("lanes", {}).get(lane) if isinstance(feature_state.get("lanes", {}).get(lane), dict) else {}
    if str(lane_state.get("status") or "") == "direct_exec_running":
        pid = int(lane_state.get("pid") or 0)
        if not _pid_alive(pid):
            _set_lane_state(
                feature_state,
                lane,
                status="error",
                mode=str(lane_state.get("mode") or launch_cfg["mode"]),
                profile=str(lane_state.get("profile") or launch_cfg["profile_name"]),
                workdir=str(lane_state.get("workdir") or workdir),
                prompt_path=Path(str(lane_state.get("prompt_path") or prompt_path)),
                log_path=Path(str(lane_state.get("log_path") or log_path)),
                thread_id="",
                error=f"stale direct exec pid {pid}",
                action="stale_direct_exec",
                pid=0,
            )
            lane_state = feature_state.get("lanes", {}).get(lane, {})
    thread_id = None if args.restart_existing else lane_state.get("thread_id")
    initial_action = "resume" if thread_id else "launch"
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
        action=initial_action,
        pid=0,
    )
    _write_log(
        log_path,
        {
            "lane": lane,
            "thread_id": str(thread_id or ""),
            "mode": launch_cfg["mode"],
            "profile": launch_cfg["profile_name"],
            "workdir": workdir,
            "action": initial_action,
            "launched_at": _ts(),
            "status": "launching",
        },
        "Managed feature lane launch started.",
    )
    def _attempt(profile_cfg: Dict[str, object], *, existing_thread_id: str | None) -> tuple[str, str, str]:
        client = _open_client(profile_cfg)
        try:
            if existing_thread_id:
                next_thread_id, content = client.codex_reply(
                    str(existing_thread_id),
                    "Resume work from the current lane branch and continue toward the next valid handoff.",
                    timeout=float(profile_cfg.get("launch_timeout_seconds", launch_cfg["launch_timeout_seconds"])),
                )
                return next_thread_id, content, "resumed"
            next_thread_id, content = client.codex(
                prompt=prompt,
                cwd=workdir,
                sandbox="workspace-write",
                approval_policy="never",
                model=str(profile_cfg["model"]),
                timeout=float(profile_cfg.get("launch_timeout_seconds", launch_cfg["launch_timeout_seconds"])),
            )
            return next_thread_id, content, "launched"
        finally:
            client.close()

    try:
        effective_cfg = dict(launch_cfg)
        if thread_id:
            thread_id, content, action = _attempt(effective_cfg, existing_thread_id=str(thread_id))
        else:
            thread_id, content, action = _attempt(effective_cfg, existing_thread_id=None)
        header = {
            "lane": lane,
            "thread_id": thread_id,
            "mode": effective_cfg["mode"],
            "profile": effective_cfg["profile_name"],
            "workdir": workdir,
            "action": action,
            "launched_at": _ts(),
        }
        _write_log(log_path, header, content)
        _set_lane_state(
            feature_state,
            lane,
            status="managed_thread",
            mode=str(effective_cfg["mode"]),
            profile=str(effective_cfg["profile_name"]),
            workdir=workdir,
            prompt_path=prompt_path,
            log_path=log_path,
            thread_id=str(thread_id),
            action=action,
        )
        return {
            "lane": lane,
            "status": action,
            "thread_id": thread_id,
            "mode": effective_cfg["mode"],
            "profile": effective_cfg["profile_name"],
            "workdir": workdir,
            "log": str(log_path),
        }
    except Exception as exc:
        if str(launch_cfg["mode"]) == "cloud_primary":
            fallback_cfg = dict(launch_cfg["local_profile"])
            fallback_cfg["mode"] = "local_fallback"
            fallback_cfg["profile_name"] = launch_cfg["local_profile_name"]
            fallback_cfg["launch_timeout_seconds"] = launch_cfg["launch_timeout_seconds"]
            _set_lane_state(
                feature_state,
                lane,
                status="launching",
                mode=str(fallback_cfg["mode"]),
                profile=str(fallback_cfg["profile_name"]),
                workdir=workdir,
                prompt_path=prompt_path,
                log_path=log_path,
                thread_id="",
                error=f"cloud launch failed: {exc}",
                action="local_fallback",
                pid=0,
            )
            _write_log(
                log_path,
                {
                    "lane": lane,
                    "thread_id": "",
                    "mode": fallback_cfg["mode"],
                    "profile": fallback_cfg["profile_name"],
                    "workdir": workdir,
                    "action": "local_fallback",
                    "launched_at": _ts(),
                    "status": "launching",
                },
                f"Cloud launch failed, retrying locally: {exc}",
            )
            try:
                thread_id, content, action = _attempt(fallback_cfg, existing_thread_id=None)
                header = {
                    "lane": lane,
                    "thread_id": thread_id,
                    "mode": fallback_cfg["mode"],
                    "profile": fallback_cfg["profile_name"],
                    "workdir": workdir,
                    "action": action,
                    "launched_at": _ts(),
                }
                _write_log(log_path, header, content)
                _set_lane_state(
                    feature_state,
                    lane,
                    status="managed_thread",
                    mode=str(fallback_cfg["mode"]),
                    profile=str(fallback_cfg["profile_name"]),
                    workdir=workdir,
                    prompt_path=prompt_path,
                    log_path=log_path,
                    thread_id=str(thread_id),
                    action=f"local_{action}",
                    pid=0,
                )
                return {
                    "lane": lane,
                    "status": f"local_{action}",
                    "thread_id": thread_id,
                    "mode": fallback_cfg["mode"],
                    "profile": fallback_cfg["profile_name"],
                    "workdir": workdir,
                    "log": str(log_path),
                }
            except Exception as fallback_exc:
                exc = RuntimeError(f"cloud launch failed: {exc}; local fallback failed: {fallback_exc}")
        direct_profile = dict(launch_cfg.get("local_profile") or launch_cfg)
        direct_profile["mode"] = "local_fallback"
        direct_profile["profile_name"] = str(launch_cfg.get("local_profile_name") or launch_cfg["profile_name"])
        pid = _spawn_direct_exec(direct_profile, workdir=workdir, prompt=prompt, log_path=log_path)
        _set_lane_state(
            feature_state,
            lane,
            status="direct_exec_running",
            mode=str(direct_profile["mode"]),
            profile=str(direct_profile["profile_name"]),
            workdir=workdir,
            prompt_path=prompt_path,
            log_path=log_path,
            thread_id="",
            error=str(exc),
            action="direct_exec_fallback",
            pid=pid,
        )
        _write_log(
            log_path,
            {
                "lane": lane,
                "thread_id": "",
                "mode": direct_profile["mode"],
                "profile": direct_profile["profile_name"],
                "workdir": workdir,
                "action": "direct_exec_fallback",
                "launched_at": _ts(),
                "status": "direct_exec_running",
                "pid": pid,
            },
            f"Managed launch failed, spawned direct exec fallback: {exc}",
        )
        return {
            "lane": lane,
            "status": "direct_exec_running",
            "mode": direct_profile["mode"],
            "profile": direct_profile["profile_name"],
            "workdir": workdir,
            "pid": pid,
            "log": str(log_path),
            "error": str(exc),
        }
def main() -> int:
    args = parse_args()
    if args.lanes is None:
        args.lanes = _enabled_lanes()
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

    max_workers = min(len(args.lanes), 5)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                _launch_one_lane,
                lane,
                args=args,
                launch_cfg=launch_cfg,
                worktrees=worktrees,
                prompts_dir=prompts_dir,
                logs_dir=logs_dir,
                feature_state=feature_state,
            )
            for lane in args.lanes
        ]
        for fut in as_completed(futures):
            launched.append(fut.result())

    print(json.dumps({"runtime_mode": launch_cfg["mode"], "launched": launched}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
