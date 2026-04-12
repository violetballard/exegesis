#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import fnmatch
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from git_hygiene import run_hygiene
except ImportError:  # pragma: no cover - package execution fallback
    from .git_hygiene import run_hygiene

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True, write_through=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(line_buffering=True, write_through=True)

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent.parent
PLANNER_PATH = REPO_ROOT / "codex_packet_handoff/tools/planner.py"
ROUTER_PATH = REPO_ROOT / "codex_packet_handoff/tools/router.py"
INIT_META_PATH = REPO_ROOT / "codex_packet_handoff/tools/init_lane_meta.py"
LAUNCH_FEATURE_LANES_PATH = REPO_ROOT / "codex_packet_handoff/tools/launch_feature_lanes.py"

PLANNER_CMD = [sys.executable, str(PLANNER_PATH)]
ROUTER_CMD = [sys.executable, str(ROUTER_PATH)]
INIT_META_CMD = [sys.executable, str(INIT_META_PATH)]
LAUNCH_FEATURE_LANES_CMD = [sys.executable, str(LAUNCH_FEATURE_LANES_PATH)]

EMITTED_RE = re.compile(r"\[planner\] emitted (?P<path>\S+)")
ROUTER_RE = re.compile(
    r"\[router\]\s+processed\s+(?P<processed>\d+)\s+packet\(s\)"
    r"(?:,\s+kicked\s+(?P<kicked>\d+)\s+reviewer-fixer task\(s\))?"
    r"(?:,\s+integrated\s+(?P<integrated>\d+)\s+approval packet\(s\))?"
)
LANE_FILE_RE = re.compile(
    r"\.codex/packets/lanes/(?P<lane>[^/]+)/inbox/feature/(?P<filename>[^/\s]+\.md)"
)

COORD_ROOT = REPO_ROOT / ".codex/packet_coordinator"
RUNS_DIR = COORD_ROOT / "runs"
STATE_FILE = COORD_ROOT / "state.json"
LEASE_FILE = COORD_ROOT / "lease.json"
ROUTER_CONFIG_FILE = REPO_ROOT / ".codex/packet_router/config.json"
ROUTER_EXAMPLE_FILE = REPO_ROOT / ".codex/packet_router/example.json"
ROUTER_STATE_FILE = REPO_ROOT / ".codex/packet_router/state.json"
FEATURE_RUNNER_ROOT = REPO_ROOT / ".codex/feature_runner"
FEATURE_RUNNER_STATE_FILE = FEATURE_RUNNER_ROOT / "state.json"
FEATURE_RELAUNCH_COOLDOWN_SECONDS = 60
WORKTREE_RECOVERY_ROOT = REPO_ROOT / ".codex/worktree_recovery"
ROUTER_JOB_STATE_KEYS = (
    "fixer_fallback_jobs",
    "local_reviewer_jobs",
    "local_integrator_jobs",
    "cloud_integrator_jobs",
)
DEFAULT_LANES = [
    "feat-context-storage",
    "feat-commands",
    "feat-retrieval-fts",
    "feat-a2ui-contract",
    "feat-engine-runs",
    "feat-console-shell",
    "feat-console-workflow",
]

WORKTREE_TEMP_PATTERNS = (
    ".git-alt*",
    ".git-bisect*",
    ".git-commit*",
    ".git-feature-fixer*",
    ".git-fix*",
    ".git-head-tree",
    ".git-index*",
    ".git-local*",
    ".git-manual-reviewfix*",
    ".git-meta*",
    ".git-objects*",
    ".git-plumb*",
    ".git-review*",
    ".git-reviewer*",
    ".git-reviewfix*",
    ".git-run*",
    ".git-sandbox*",
    ".git-shadow*",
    ".git-standalone-test*",
    ".git-temp*",
    ".lane-meta.*",
    ".root-tree-*",
    ".write-test",
    "visible-temp.txt",
    "worktree-commit*.txt",
    "worktree-probe*.txt",
)


@dataclass
class DirectRouterCtx:
    router_mod: object
    cfg: object
    state: Dict
    repo_cwd: str
    reviewer_client: object
    integrator_client: object
    reviewer_thread_ids: Dict[str, str]
    integrator_tid: str
    local_mode: bool


def _bootstrap_direct_integrator_thread(
    router_mod: object,
    cfg: object,
    repo_cwd: str,
    state: Dict,
    integrator_client: object,
    integrator_tid: str,
) -> str:
    if integrator_tid:
        return integrator_tid
    if router_mod._runtime_mode(cfg, state) == "local_fallback":
        return integrator_tid
    if bool(getattr(cfg, "prefer_cli_integrator", False)):
        return integrator_tid
    integrator_profile = router_mod._profile_for_role(cfg, "integrator", local=False)
    timeout = float(getattr(cfg, "integrator_timeout", 600.0))
    integrator_tid, _ = integrator_client.codex(
        prompt="Ready as integrator.",
        cwd=repo_cwd,
        sandbox="workspace-write",
        approval_policy="on-request",
        model=integrator_profile.model,
        timeout=timeout,
    )
    state["integrator_thread_id"] = integrator_tid
    router_mod.save_json(router_mod.STATE_FILE, state)
    return integrator_tid


def _build_direct_router_clients(router_mod: object, cfg: object, state: Dict) -> Tuple[bool, object, object]:
    local_mode = router_mod._runtime_mode(cfg, state) == "local_fallback"
    reviewer_client = router_mod._build_mcp_client(
        router_mod._profile_for_role(cfg, "reviewer", local=local_mode),
        router_mod.ApprovalPolicy(True, True),
    )
    integrator_client = router_mod._build_mcp_client(
        router_mod._profile_for_role(cfg, "integrator", local=local_mode),
        router_mod.ApprovalPolicy(True, True),
    )
    return local_mode, reviewer_client, integrator_client


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_cmd(cmd: List[str]) -> Tuple[int, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(REPO_ROOT))
    out = p.stdout or ""
    if out:
        print(out, end="" if out.endswith("\n") else "\n")
    return p.returncode, out


def _load_tool_module(module_name: str, relpath: str):
    path = Path(relpath)
    if not path.is_absolute():
        path = REPO_ROOT / path
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_json(path: Path, default: Dict) -> Dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def save_json(path: Path, data: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _job_result_exists(job: Dict[str, object]) -> bool:
    result_path = str(job.get("result_path") or "")
    if not result_path:
        return False
    return Path(result_path).exists()


def _reconcile_feature_runner_state() -> List[str]:
    state = load_json(FEATURE_RUNNER_STATE_FILE, {})
    lanes = state.get("lanes") if isinstance(state, dict) else {}
    if not isinstance(lanes, dict):
        return []

    removed: List[str] = []
    for lane, lane_state in list(lanes.items()):
        if not isinstance(lane_state, dict):
            lanes.pop(lane, None)
            removed.append(str(lane))
            continue
        if str(lane_state.get("status") or "") != "direct_exec_running":
            continue
        pid = int(lane_state.get("pid") or 0)
        if _pid_alive(pid):
            continue
        lanes.pop(lane, None)
        removed.append(str(lane))

    if removed:
        state["lanes"] = lanes
        save_json(FEATURE_RUNNER_STATE_FILE, state)
    return sorted(removed)


def _reconcile_router_state() -> Dict[str, List[str]]:
    state = load_json(ROUTER_STATE_FILE, {})
    if not isinstance(state, dict):
        return {}

    removed: Dict[str, List[str]] = {}
    changed = False
    for key in ROUTER_JOB_STATE_KEYS:
        jobs = state.get(key)
        if not isinstance(jobs, dict):
            continue
        stale: List[str] = []
        for job_name, job in list(jobs.items()):
            if not isinstance(job, dict):
                jobs.pop(job_name, None)
                stale.append(str(job_name))
                continue
            if _job_result_exists(job):
                continue
            pid = int(job.get("pid") or 0)
            if _pid_alive(pid):
                continue
            jobs.pop(job_name, None)
            stale.append(str(job_name))
        if stale:
            removed[key] = sorted(stale)
            state[key] = jobs
            changed = True

    if changed:
        save_json(ROUTER_STATE_FILE, state)
    return removed


def _reconcile_control_plane_state() -> Dict[str, object]:
    feature_runner_removed = _reconcile_feature_runner_state()
    router_removed = _reconcile_router_state()
    worktree_reconcile = _reconcile_lane_worktrees()
    git_hygiene = run_hygiene(REPO_ROOT)
    if feature_runner_removed:
        print(f"[reconcile] pruned stale feature-runner state: {', '.join(feature_runner_removed)}")
    for key, names in sorted(router_removed.items()):
        print(f"[reconcile] pruned stale router state from {key}: {', '.join(names)}")
    for repaired in worktree_reconcile["gitdir_repaired"]:
        print(f"[reconcile] restored shared gitdir for {repaired}")
    for backup in worktree_reconcile["gitdir_backups"]:
        print(f"[reconcile] preserved shadow git repo at {backup}")
    for lane, names in sorted(worktree_reconcile["artifacts_removed"].items()):
        print(f"[reconcile] pruned generated worktree artifacts for {lane}: {', '.join(names)}")
    if git_hygiene["stale_git_pids"]:
        print(f"[reconcile] reaped stale git helpers: {', '.join(str(pid) for pid in git_hygiene['stale_git_pids'])}")
    if git_hygiene["temp_worktrees_removed"]:
        print(f"[reconcile] pruned stale temp worktrees: {', '.join(git_hygiene['temp_worktrees_removed'])}")
    return {
        "feature_runner_removed": feature_runner_removed,
        "router_removed": router_removed,
        "worktree_reconcile": worktree_reconcile,
        "git_hygiene": git_hygiene,
    }


def _all_configured_lanes() -> List[str]:
    cfg = load_json(ROUTER_CONFIG_FILE, {})
    lanes = cfg.get("lanes") if isinstance(cfg, dict) else {}
    if isinstance(lanes, dict) and lanes:
        return list(lanes.keys())
    return list(DEFAULT_LANES)


def _lane_branch_map() -> Dict[str, str]:
    cfg = load_json(ROUTER_CONFIG_FILE, {})
    lanes = cfg.get("lanes") if isinstance(cfg, dict) else {}
    if not isinstance(lanes, dict):
        return {lane: f"codex/{lane}" for lane in DEFAULT_LANES}
    return {
        str(lane): str((lane_cfg or {}).get("branch") or f"codex/{lane}")
        for lane, lane_cfg in lanes.items()
    }


def _git_worktree_branch_map() -> Dict[str, str]:
    proc = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return {}
    out: Dict[str, str] = {}
    current_worktree: Optional[str] = None
    current_branch: Optional[str] = None
    for raw in proc.stdout.splitlines():
        line = raw.strip()
        if not line:
            if current_worktree and current_branch:
                out[current_branch] = current_worktree
            current_worktree = None
            current_branch = None
            continue
        if line.startswith("worktree "):
            current_worktree = line.split(" ", 1)[1].strip()
        elif line.startswith("branch "):
            current_branch = line.split(" ", 1)[1].strip()
    if current_worktree and current_branch:
        out[current_branch] = current_worktree
    return out


def _shared_gitdir_for_worktree(worktree: Path) -> Optional[Path]:
    base = REPO_ROOT / ".git" / "worktrees"
    if not base.exists():
        return None
    target = str(worktree / ".git")
    for entry in base.iterdir():
        gitdir_file = entry / "gitdir"
        try:
            content = gitdir_file.read_text().strip()
        except Exception:
            continue
        if content == target:
            return entry
    return None


def _repair_shadow_gitdir(worktree: Path, lane: str) -> Tuple[bool, Optional[str]]:
    git_file = worktree / ".git"
    try:
        content = git_file.read_text().strip()
    except Exception:
        return False, None
    if ".git-local" not in content:
        return False, None
    shared_gitdir = _shared_gitdir_for_worktree(worktree)
    if shared_gitdir is None:
        return False, None
    shadow_gitdir = content.split("gitdir:", 1)[1].strip() if "gitdir:" in content else ""
    backup_path: Optional[str] = None
    if shadow_gitdir:
        shadow_path = Path(shadow_gitdir)
        if shadow_path.exists():
            WORKTREE_RECOVERY_ROOT.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            target = WORKTREE_RECOVERY_ROOT / f"{lane}__git-local__{stamp}"
            shutil.move(str(shadow_path), target)
            backup_path = str(target)
    git_file.write_text(f"gitdir: {shared_gitdir}\n")
    return True, backup_path


def _prune_generated_worktree_artifacts(worktree: Path) -> List[str]:
    removed: List[str] = []
    for child in sorted(worktree.iterdir(), key=lambda p: p.name):
        name = child.name
        if not any(fnmatch.fnmatch(name, pattern) for pattern in WORKTREE_TEMP_PATTERNS):
            continue
        try:
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink()
            removed.append(name)
        except FileNotFoundError:
            continue
        except Exception:
            continue
    packets_dir = worktree / ".codex" / "packets"
    if packets_dir.exists():
        try:
            shutil.rmtree(packets_dir)
            removed.append(".codex/packets")
        except Exception:
            pass
    return removed


def _reconcile_lane_worktrees() -> Dict[str, object]:
    repaired: List[str] = []
    backups: List[str] = []
    removed: Dict[str, List[str]] = {}
    branch_map = _lane_branch_map()
    worktree_map = _git_worktree_branch_map()
    for lane, branch in branch_map.items():
        worktree_path = worktree_map.get(f"refs/heads/{branch}") or worktree_map.get(branch)
        if not worktree_path:
            continue
        worktree = Path(worktree_path)
        if not worktree.exists():
            continue
        did_repair, backup = _repair_shadow_gitdir(worktree, lane)
        if did_repair:
            repaired.append(str(worktree))
        if backup:
            backups.append(backup)
        pruned = _prune_generated_worktree_artifacts(worktree)
        if pruned:
            removed[lane] = pruned
    return {
        "gitdir_repaired": repaired,
        "gitdir_backups": backups,
        "artifacts_removed": removed,
    }


def _enabled_lanes() -> List[str]:
    cfg = load_json(ROUTER_CONFIG_FILE, {})
    lanes = cfg.get("lanes") if isinstance(cfg, dict) else {}
    if isinstance(lanes, dict) and lanes:
        return [name for name, lane_cfg in lanes.items() if bool((lane_cfg or {}).get("enabled", True))]
    return list(DEFAULT_LANES)


def acquire_lease(ttl_seconds: int) -> bool:
    now = time.time()
    if LEASE_FILE.exists():
        lease = load_json(LEASE_FILE, {})
        ts = float(lease.get("ts", 0))
        if now - ts < ttl_seconds:
            return False
    save_json(LEASE_FILE, {"ts": now, "pid": os.getpid(), "updated_at": utc_now()})
    return True


def touch_lease() -> None:
    save_json(LEASE_FILE, {"ts": time.time(), "pid": os.getpid(), "updated_at": utc_now()})


def release_lease() -> None:
    try:
        if LEASE_FILE.exists():
            LEASE_FILE.unlink()
    except Exception:
        pass


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "Multi-agent coordinator for planner/reviewer/fixer/integrator handoff. "
            "Daemon mode keeps cycling; once mode drains until idle."
        )
    )
    ap.add_argument("--daemon", action="store_true", help="Run continuously and keep cycling while alive")
    ap.add_argument("--once", action="store_true", help="Run event-driven drain cycle once and exit")
    ap.add_argument("--poll-seconds", type=float, default=2.0, help="Polling interval for event detection (default: 2s)")
    ap.add_argument(
        "--idle-grace-seconds",
        type=float,
        default=6.0,
        help="In --once mode, idle time before exit after no changes (default: 6s)",
    )
    ap.add_argument("--max-cycles", type=int, default=200, help="Safety cap for cycles in --once mode")
    ap.add_argument("--stop-on-error", action="store_true", help="Exit immediately on planner/router error")
    ap.add_argument("--planner-retries", type=int, default=1, help="Planner retries per cycle (default: 1)")
    ap.add_argument("--router-retries", type=int, default=1, help="Router retries per cycle (default: 1)")
    ap.add_argument("--lease-ttl", type=int, default=300, help="Lease TTL in seconds (default: 300)")
    ap.add_argument("--preflight-only", action="store_true", help="Run preflight checks and exit")
    ap.add_argument(
        "--execution-mode",
        choices=("direct", "subprocess"),
        default="direct",
        help="Execution mode for planner/router runtime (default: direct)",
    )
    return ap.parse_args()


def _validate_inputs(args: argparse.Namespace) -> int:
    if args.poll_seconds <= 0:
        print("[error] --poll-seconds must be > 0")
        return 2
    if args.idle_grace_seconds < 0:
        print("[error] --idle-grace-seconds must be >= 0")
        return 2
    if args.max_cycles <= 0:
        print("[error] --max-cycles must be > 0")
        return 2
    if args.planner_retries < 0 or args.router_retries < 0:
        print("[error] retries must be >= 0")
        return 2
    if not PLANNER_PATH.exists():
        print(f"[error] Missing planner tool: {PLANNER_PATH}")
        return 2
    if not ROUTER_PATH.exists():
        print(f"[error] Missing router tool: {ROUTER_PATH}")
        return 2
    if not args.daemon and not args.once:
        args.once = True
    if args.daemon and args.once:
        print("[error] use only one of --daemon or --once")
        return 2
    return 0


def _collect_emissions(planner_output: str) -> List[Tuple[str, str]]:
    emissions: List[Tuple[str, str]] = []
    for line in planner_output.splitlines():
        m = EMITTED_RE.search(line)
        if not m:
            continue
        emitted_path = m.group("path")
        m2 = LANE_FILE_RE.search(emitted_path)
        if m2:
            emissions.append((m2.group("lane"), m2.group("filename")))
        else:
            emissions.append(("unknown", Path(emitted_path).name))
    return emissions


def _collect_router_stats(router_output: str) -> Dict[str, int]:
    out = {"processed": 0, "kicked": 0, "integrated": 0}
    for line in router_output.splitlines():
        m = ROUTER_RE.search(line)
        if not m:
            continue
        out["processed"] += int(m.group("processed"))
        kicked = m.group("kicked")
        if kicked:
            out["kicked"] += int(kicked)
        integrated = m.group("integrated")
        if integrated:
            out["integrated"] += int(integrated)
    return out


def _ensure_router_config() -> None:
    if ROUTER_CONFIG_FILE.exists():
        return
    if ROUTER_EXAMPLE_FILE.exists():
        ROUTER_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROUTER_EXAMPLE_FILE, ROUTER_CONFIG_FILE)
        print("[preflight] created .codex/packet_router/config.json from example")


def _load_lane_branches() -> Dict[str, str]:
    cfg = load_json(ROUTER_CONFIG_FILE, {})
    lanes = (cfg.get("lanes") or {}) if isinstance(cfg, dict) else {}
    out: Dict[str, str] = {}
    for lane in _enabled_lanes():
        lane_cfg = lanes.get(lane, {}) if isinstance(lanes, dict) else {}
        branch = str((lane_cfg or {}).get("branch") or f"codex/{lane}")
        out[lane] = branch
    return out


def _ensure_dirs() -> None:
    for lane in _all_configured_lanes():
        base = REPO_ROOT / ".codex/packets/lanes" / lane
        (base / "inbox/feature").mkdir(parents=True, exist_ok=True)
        (base / "inbox/reviewer").mkdir(parents=True, exist_ok=True)
        (base / "outbox/integrator").mkdir(parents=True, exist_ok=True)
        (base / "archive").mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / ".codex/packet_router").mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / ".codex/packet_planner").mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / ".codex/lane_meta").mkdir(parents=True, exist_ok=True)


def _permission_probe() -> None:
    probe = REPO_ROOT / ".codex/packets/_coordinator_write_probe"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text("ok")
    probe.unlink()


def _preflight_bootstrap() -> Tuple[bool, str]:
    COORD_ROOT.mkdir(parents=True, exist_ok=True)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    _ensure_dirs()
    rc, out = run_cmd(INIT_META_CMD)
    if rc != 0:
        return False, f"init_lane_meta failed: {rc}\n{out}"
    _ensure_router_config()
    try:
        _permission_probe()
    except Exception as exc:
        return False, f"filesystem write probe failed: {exc}"
    return True, "ok"


def _run_planner_subprocess(retries: int) -> Tuple[int, str, int]:
    attempts = 0
    while True:
        attempts += 1
        rc, out = run_cmd(PLANNER_CMD)
        if rc == 0:
            return rc, out, attempts
        if "Missing .codex/lane_meta/" in out:
            run_cmd(INIT_META_CMD)
        if attempts > retries + 1:
            return rc, out, attempts
        print(f"[planner] retry attempt {attempts}/{retries + 1}")
        time.sleep(1)


def _run_router_subprocess(retries: int) -> Tuple[int, str, int]:
    attempts = 0
    while True:
        attempts += 1
        rc, out = run_cmd(ROUTER_CMD)
        if rc == 0:
            return rc, out, attempts
        if attempts > retries + 1:
            return rc, out, attempts
        print(f"[router] retry attempt {attempts}/{retries + 1}")
        time.sleep(1)


def _run_planner_direct_once() -> Tuple[int, str]:
    buf = io.StringIO()
    rc = 0
    try:
        planner_mod = _load_tool_module("packet_planner_runtime", str(PLANNER_PATH))
        with contextlib.redirect_stdout(buf):
            planner_mod.main()
    except SystemExit as exc:
        code = exc.code
        rc = int(code) if isinstance(code, int) else 1
    except Exception:
        rc = 1
        traceback.print_exc(file=buf)
    out = buf.getvalue()
    if out:
        print(out, end="" if out.endswith("\n") else "\n")
    return rc, out


def _run_planner_direct(retries: int) -> Tuple[int, str, int]:
    attempts = 0
    while True:
        attempts += 1
        rc, out = _run_planner_direct_once()
        if rc == 0:
            return rc, out, attempts
        if "Missing .codex/lane_meta/" in out:
            run_cmd(INIT_META_CMD)
        if attempts > retries + 1:
            return rc, out, attempts
        print(f"[planner] retry attempt {attempts}/{retries + 1}")
        time.sleep(1)


def _init_direct_router_ctx() -> DirectRouterCtx:
    router_mod = _load_tool_module("packet_router_runtime", str(ROUTER_PATH))
    cfg = router_mod.load_cfg()
    state = router_mod.load_json(router_mod.STATE_FILE, {})
    repo_cwd = str(REPO_ROOT)
    state = router_mod._maybe_restore_cloud(cfg, state, repo_cwd)
    local_mode, reviewer_client, integrator_client = _build_direct_router_clients(router_mod, cfg, state)

    reviewer_thread_ids = state.get("reviewer_thread_ids") or {}
    if not isinstance(reviewer_thread_ids, dict):
        reviewer_thread_ids = {}
    integrator_tid = state.get("integrator_thread_id")
    integrator_tid = _bootstrap_direct_integrator_thread(
        router_mod,
        cfg,
        repo_cwd,
        state,
        integrator_client,
        integrator_tid,
    )

    state["reviewer_thread_ids"] = reviewer_thread_ids
    if reviewer_thread_ids:
        first_lane = sorted(reviewer_thread_ids.keys())[0]
        state["reviewer_thread_id"] = reviewer_thread_ids.get(first_lane)
    else:
        state["reviewer_thread_id"] = None
    state["integrator_thread_id"] = integrator_tid
    router_mod.save_json(router_mod.STATE_FILE, state)
    for lane in cfg.lanes.keys():
        router_mod.ensure_lane_dirs(lane)

    return DirectRouterCtx(
        router_mod=router_mod,
        cfg=cfg,
        state=state,
        repo_cwd=repo_cwd,
        reviewer_client=reviewer_client,
        integrator_client=integrator_client,
        reviewer_thread_ids=reviewer_thread_ids,
        integrator_tid=integrator_tid,
        local_mode=local_mode,
    )


def _refresh_direct_router_clients(ctx: DirectRouterCtx) -> None:
    ctx.state = ctx.router_mod._maybe_restore_cloud(ctx.cfg, ctx.state, ctx.repo_cwd)
    desired_local_mode = ctx.router_mod._runtime_mode(ctx.cfg, ctx.state) == "local_fallback"
    if desired_local_mode == ctx.local_mode:
        return

    seen: set[int] = set()
    for client in (ctx.reviewer_client, ctx.integrator_client):
        ident = id(client)
        if ident in seen:
            continue
        seen.add(ident)
        with contextlib.suppress(Exception):
            client.close()

    ctx.local_mode, ctx.reviewer_client, ctx.integrator_client = _build_direct_router_clients(
        ctx.router_mod,
        ctx.cfg,
        ctx.state,
    )
    ctx.integrator_tid = _bootstrap_direct_integrator_thread(
        ctx.router_mod,
        ctx.cfg,
        ctx.repo_cwd,
        ctx.state,
        ctx.integrator_client,
        ctx.integrator_tid,
    )


def _run_router_direct_once(ctx: DirectRouterCtx) -> Tuple[int, str]:
    try:
        _refresh_direct_router_clients(ctx)
        n, ctx.state, ctx.reviewer_thread_ids, ctx.integrator_tid = ctx.router_mod.process_once(
            ctx.reviewer_client,
            ctx.integrator_client,
            ctx.cfg,
            ctx.state,
            ctx.repo_cwd,
            ctx.reviewer_thread_ids,
            ctx.integrator_tid,
        )
        kicked, ctx.state = ctx.router_mod.process_reviewer_backlog(
            ctx.reviewer_client,
            ctx.cfg,
            ctx.state,
            ctx.repo_cwd,
        )
        integrated, ctx.state, ctx.integrator_tid = ctx.router_mod.process_integrator_backlog(
            ctx.integrator_client,
            ctx.cfg,
            ctx.state,
            ctx.repo_cwd,
            ctx.integrator_tid,
        )
        ctx.state["reviewer_thread_ids"] = ctx.reviewer_thread_ids
        if ctx.reviewer_thread_ids:
            first_lane = sorted(ctx.reviewer_thread_ids.keys())[0]
            ctx.state["reviewer_thread_id"] = ctx.reviewer_thread_ids.get(first_lane)
        else:
            ctx.state["reviewer_thread_id"] = None
        ctx.state["integrator_thread_id"] = ctx.integrator_tid
        ctx.router_mod.save_json(ctx.router_mod.STATE_FILE, ctx.state)
        out = f"[router] processed {n} packet(s), kicked {kicked} reviewer-fixer task(s), integrated {integrated} approval packet(s)\n"
        print(out, end="")
        return 0, out
    except Exception:
        buf = io.StringIO()
        traceback.print_exc(file=buf)
        out = buf.getvalue()
        if out:
            print(out, end="" if out.endswith("\n") else "\n")
        return 1, out


def _run_router_direct(ctx: DirectRouterCtx, retries: int) -> Tuple[int, str, int]:
    attempts = 0
    while True:
        attempts += 1
        rc, out = _run_router_direct_once(ctx)
        if rc == 0:
            return rc, out, attempts
        if attempts > retries + 1:
            return rc, out, attempts
        print(f"[router] retry attempt {attempts}/{retries + 1}")
        time.sleep(1)


def _git_rev(branch: str) -> str:
    p = subprocess.run(["git", "rev-parse", branch], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    if p.returncode != 0:
        return ""
    return (p.stdout or "").strip()


def _lane_digest(lane: str) -> Dict[str, object]:
    base = REPO_ROOT / ".codex/packets/lanes" / lane
    feat = sorted((base / "inbox/feature").glob("*.md"))
    rev = sorted((base / "inbox/reviewer").glob("*.md"))
    appr = sorted((base / "outbox/integrator").glob("*.md"))
    arch = sorted((base / "archive").glob("*.md"))
    def newest_name(paths: List[Path]) -> str:
        if not paths:
            return ""
        return max(paths, key=lambda p: p.stat().st_mtime).name
    return {
        "pending_feature": len(feat),
        "reviewer_notes": len(rev),
        "approved": len(appr),
        "archive": len(arch),
        "latest_feature": newest_name(feat),
        "latest_review": newest_name(rev),
        "latest_approved": newest_name(appr),
    }


def _lane_queue_empty(lane: str) -> bool:
    d = _lane_digest(lane)
    return (
        int(d.get("pending_feature", 0)) == 0
        and int(d.get("reviewer_notes", 0)) == 0
        and int(d.get("approved", 0)) == 0
    )


def _feature_thread_state() -> Dict[str, Dict[str, object]]:
    state = load_json(FEATURE_RUNNER_STATE_FILE, {})
    lanes = state.get("lanes") if isinstance(state, dict) else {}
    return lanes if isinstance(lanes, dict) else {}


def _lane_has_active_feature_session(
    lane: str,
    *,
    feature_threads: Optional[Dict[str, Dict[str, object]]] = None,
) -> bool:
    if feature_threads is None:
        feature_threads = _feature_thread_state()
    lane_state = feature_threads.get(lane) if isinstance(feature_threads, dict) else None
    if isinstance(lane_state, dict):
        status = str(lane_state.get("status") or "")
        if status in {"managed_thread", "launching"}:
            return True
        if status == "direct_exec_running":
            return _pid_alive(int(lane_state.get("pid") or 0))
    return False


def _launch_free_lanes(state_doc: Dict[str, object]) -> List[str]:
    lane_refill = state_doc.setdefault("lane_refill", {})
    if not isinstance(lane_refill, dict):
        lane_refill = {}
        state_doc["lane_refill"] = lane_refill

    feature_threads = _feature_thread_state()
    now = time.time()
    to_launch: List[str] = []
    for lane in _enabled_lanes():
        queue_empty = _lane_queue_empty(lane)
        feature_active = _lane_has_active_feature_session(lane, feature_threads=feature_threads)
        lane_state = lane_refill.get(lane)
        if not isinstance(lane_state, dict):
            lane_state = {}
        last_launch_attempt_ts = float(lane_state.get("last_launch_attempt_ts", 0) or 0)
        if (
            queue_empty
            and not feature_active
            and (now - last_launch_attempt_ts) >= FEATURE_RELAUNCH_COOLDOWN_SECONDS
        ):
            to_launch.append(lane)
            lane_state["last_launch_attempt_ts"] = now
            lane_state["last_launch_reason"] = "queue_empty_without_active_feature_session"
        lane_state["queue_empty"] = queue_empty
        lane_state["feature_active"] = feature_active
        lane_state["last_seen_at"] = utc_now()
        lane_refill[lane] = lane_state

    if not to_launch:
        return []

    rc, out = run_cmd(LAUNCH_FEATURE_LANES_CMD + ["--lanes", *to_launch])
    if rc != 0:
        print(f"[coordinator] feature lane launch failed for {to_launch}: rc={rc}")
        if out:
            print(out, end="" if out.endswith("\n") else "\n")
        return []
    print(f"[coordinator] launched free lanes: {', '.join(to_launch)}")
    return to_launch


def _has_lane_backlog() -> bool:
    """Return True when any lane has packets waiting for reviewer/fixer/integrator."""
    for lane in _enabled_lanes():
        d = _lane_digest(lane)
        if int(d.get("pending_feature", 0)) > 0:
            return True
        if int(d.get("reviewer_notes", 0)) > 0:
            return True
        if int(d.get("approved", 0)) > 0:
            return True
    return False


def _should_run_cycle(args: argparse.Namespace, snapshot: str, prev_snapshot: str, cycles: int, backlog_active: bool) -> bool:
    """Daemon mode keeps the loop alive even when there is no queue delta."""
    if args.daemon:
        return True
    return (snapshot != prev_snapshot) or (cycles == 0) or backlog_active


def _compute_snapshot(branch_map: Dict[str, str]) -> str:
    planner_state = load_json(REPO_ROOT / ".codex/packet_planner/state.json", {})
    router_state = load_json(REPO_ROOT / ".codex/packet_router/state.json", {})
    payload: Dict[str, object] = {
        "planner_state": planner_state,
        "router_state_keys": sorted(router_state.keys()),
        "lanes": {},
        "heads": {},
    }
    lanes_payload: Dict[str, object] = {}
    heads: Dict[str, str] = {}
    for lane in _enabled_lanes():
        lanes_payload[lane] = _lane_digest(lane)
        heads[lane] = _git_rev(branch_map.get(lane, f"codex/{lane}"))
    payload["lanes"] = lanes_payload
    payload["heads"] = heads
    return json.dumps(payload, sort_keys=True)


def _run_cycle(
    args: argparse.Namespace,
    direct_ctx: Optional[DirectRouterCtx],
    coordinator_state: Dict[str, object],
) -> Dict[str, object]:
    cycle_event: Dict[str, object] = {"started_at": utc_now()}
    cycle_event["reconcile"] = _reconcile_control_plane_state()
    if args.execution_mode == "direct" and direct_ctx is not None:
        direct_ctx.state = direct_ctx.router_mod.load_json(direct_ctx.router_mod.STATE_FILE, {})

    print("[planner]")
    if args.execution_mode == "direct":
        planner_rc, planner_out, planner_attempts = _run_planner_direct(args.planner_retries)
    else:
        planner_rc, planner_out, planner_attempts = _run_planner_subprocess(args.planner_retries)
    emissions = _collect_emissions(planner_out)
    cycle_event["planner"] = {
        "rc": planner_rc,
        "attempts": planner_attempts,
        "emitted": [{"lane": lane, "file": fn} for lane, fn in emissions],
    }

    print("[router]")
    if args.execution_mode == "direct":
        assert direct_ctx is not None
        router_rc, router_out, router_attempts = _run_router_direct(direct_ctx, args.router_retries)
    else:
        router_rc, router_out, router_attempts = _run_router_subprocess(args.router_retries)
    router_stats = _collect_router_stats(router_out)
    cycle_event["router"] = {
        "rc": router_rc,
        "attempts": router_attempts,
        "processed": router_stats["processed"],
        "kicked": router_stats["kicked"],
        "integrated": router_stats["integrated"],
    }

    launched_lanes = _launch_free_lanes(coordinator_state)
    cycle_event["launcher"] = {
        "launched": launched_lanes,
    }

    cycle_event["activity"] = bool(
        emissions
        or router_stats["processed"]
        or router_stats["kicked"]
        or router_stats["integrated"]
        or launched_lanes
    )
    cycle_event["ended_at"] = utc_now()
    return cycle_event


def main() -> int:
    args = parse_args()
    rc = _validate_inputs(args)
    if rc != 0:
        return rc

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_file = RUNS_DIR / f"run__{run_id}.json"
    direct_ctx: Optional[DirectRouterCtx] = None

    if not acquire_lease(args.lease_ttl):
        print("[coordinator] lease busy: another run is active")
        return 0

    try:
        ok, msg = _preflight_bootstrap()
        if not ok:
            print(f"[coordinator] preflight failed: {msg}")
            save_json(
                run_file,
                {
                    "run_id": run_id,
                    "started_at": utc_now(),
                    "status": "preflight_failed",
                    "error": msg,
                },
            )
            return 1
        if args.preflight_only:
            print("[coordinator] preflight ok")
            return 0

        branch_map = _load_lane_branches()
        if args.execution_mode == "direct":
            try:
                direct_ctx = _init_direct_router_ctx()
            except Exception as exc:
                print(f"[coordinator] direct router init failed; falling back to subprocess mode: {exc}")
                args.execution_mode = "subprocess"
                direct_ctx = None

        planner_errors = 0
        router_errors = 0
        emitted_all: List[Tuple[str, str]] = []
        router_processed_total = 0
        fixer_kicked_total = 0
        integrator_processed_total = 0
        launched_lanes_total: List[str] = []
        cycle_events: List[Dict[str, object]] = []

        run_start = time.time()
        mode_label = f"event_driven_{args.execution_mode}"
        print(f"[coordinator] mode={mode_label}")

        coord_state = load_json(STATE_FILE, {})
        coord_state["daemon_mode"] = args.daemon
        coord_state["last_cycle_at"] = utc_now()
        coord_state["last_cycle_activity"] = False
        coord_state["live_cycle_count"] = 0
        save_json(STATE_FILE, coord_state)

        prev_snapshot = ""
        idle_start = time.time()
        cycles = 0

        while True:
            touch_lease()
            snapshot = _compute_snapshot(branch_map)
            backlog_active = _has_lane_backlog()
            should_run = _should_run_cycle(args, snapshot, prev_snapshot, cycles, backlog_active)

            if should_run:
                print(f"=== EVENT CYCLE {cycles + 1} START {utc_now()} ===")
                coord_state = load_json(STATE_FILE, {})
                event = _run_cycle(args, direct_ctx, coord_state)
                cycles += 1
                cycle_events.append(event)
                prev_snapshot = _compute_snapshot(branch_map)

                p = event.get("planner", {}) if isinstance(event.get("planner"), dict) else {}
                r = event.get("router", {}) if isinstance(event.get("router"), dict) else {}
                if int(p.get("rc", 0)) != 0:
                    planner_errors += 1
                    if args.stop_on_error:
                        break
                if int(r.get("rc", 0)) != 0:
                    router_errors += 1
                    if args.stop_on_error:
                        break

                for item in p.get("emitted", []):
                    if isinstance(item, dict):
                        emitted_all.append((str(item.get("lane", "unknown")), str(item.get("file", ""))))
                router_processed_total += int(r.get("processed", 0))
                fixer_kicked_total += int(r.get("kicked", 0))
                integrator_processed_total += int(r.get("integrated", 0))
                for lane in (event.get("launcher", {}) or {}).get("launched", []):
                    if isinstance(lane, str):
                        launched_lanes_total.append(lane)

                if bool(event.get("activity")) or args.daemon:
                    idle_start = time.time()

                coord_state["daemon_mode"] = args.daemon
                coord_state["last_cycle_at"] = event.get("ended_at", utc_now())
                coord_state["last_cycle_activity"] = bool(event.get("activity"))
                coord_state["live_cycle_count"] = cycles
                save_json(STATE_FILE, coord_state)

                print(f"=== EVENT CYCLE {cycles} END ===")
            else:
                if args.once and (time.time() - idle_start) >= args.idle_grace_seconds:
                    break
                if args.once and cycles >= args.max_cycles:
                    print("[coordinator] max cycles reached in --once mode")
                    break
                if not args.daemon and args.once:
                    time.sleep(args.poll_seconds)
                else:
                    time.sleep(args.poll_seconds)
                    continue

            if args.once and cycles >= args.max_cycles:
                print("[coordinator] max cycles reached in --once mode")
                break
            if args.once and (time.time() - idle_start) >= args.idle_grace_seconds:
                break
            if args.daemon:
                time.sleep(args.poll_seconds)
                continue

        wall = int(time.time() - run_start)
        status = "ok" if (planner_errors == 0 and router_errors == 0) else "errors"

        run_doc: Dict[str, object] = {
            "run_id": run_id,
            "started_at": utc_now(),
            "status": status,
            "mode": mode_label,
            "planner_errors": planner_errors,
            "router_errors": router_errors,
            "router_processed_total": router_processed_total,
            "fixer_kicked_total": fixer_kicked_total,
            "integrator_processed_total": integrator_processed_total,
            "lanes_relaunched": launched_lanes_total,
            "planner_emitted": [{"lane": lane, "file": fn} for lane, fn in emitted_all],
            "cycle_events": cycle_events,
            "cycles": cycles,
            "wall_seconds": wall,
        }
        save_json(run_file, run_doc)
        final_state = load_json(STATE_FILE, {})
        final_state.update(
            {
                "last_run_id": run_id,
                "last_status": status,
                "last_run_file": str(run_file),
                "last_updated_at": utc_now(),
                "last_mode": mode_label,
            }
        )
        save_json(STATE_FILE, final_state)

        print("=== COORDINATOR SUMMARY ===")
        print(f"[summary] mode: {mode_label}")
        if emitted_all:
            print("[summary] planner emitted packets:")
            for lane, fn in emitted_all:
                print(f"- lane={lane} file={fn}")
        else:
            print("[summary] planner emitted packets: none")
        print(f"[summary] router processed total packets: {router_processed_total}")
        print(f"[summary] fixer kicked total tasks: {fixer_kicked_total}")
        print(f"[summary] integrator processed total approvals: {integrator_processed_total}")
        if launched_lanes_total:
            print(f"[summary] lanes relaunched: {', '.join(launched_lanes_total)}")
        else:
            print("[summary] lanes relaunched: none")
        if not emitted_all and router_processed_total == 0 and fixer_kicked_total == 0 and integrator_processed_total == 0:
            print("[summary] no activity this run")
        print(f"[summary] planner errors: {planner_errors}")
        print(f"[summary] router errors: {router_errors}")
        print(f"[summary] cycles: {cycles}")
        print(f"[summary] wall seconds: {wall}")
        print(f"[summary] run artifact: {run_file}")

        return 0 if status == "ok" else 1
    finally:
        if direct_ctx is not None:
            try:
                direct_ctx.reviewer_client.close()
            except Exception:
                pass
            try:
                if direct_ctx.integrator_client is not direct_ctx.reviewer_client:
                    direct_ctx.integrator_client.close()
            except Exception:
                pass
        release_lease()


if __name__ == "__main__":
    raise SystemExit(main())
