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

try:
    from codex_mcp_client import ApprovalPolicy, CodexMcpClient
    from git_ops import run_git
    from lane_profiles import ENGINE_MILESTONE_FOCUS, engine_priority_lines, lane_priority_order
    from log_maintenance import prune_log_dir
    from local_codex_runtime import agent_runtime_env, isolated_codex_env
except ImportError:  # pragma: no cover - test/import fallback for package execution
    from .codex_mcp_client import ApprovalPolicy, CodexMcpClient
    from .git_ops import run_git
    from .lane_profiles import ENGINE_MILESTONE_FOCUS, engine_priority_lines, lane_priority_order
    from .log_maintenance import prune_log_dir
    from .local_codex_runtime import agent_runtime_env, isolated_codex_env

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = REPO_ROOT / ".codex/packet_router/config.json"
STATE_FILE = REPO_ROOT / ".codex/packet_router/state.json"
KICKOFF_DIR = REPO_ROOT / ".codex/kickoff_packets"
FEATURE_ROOT = REPO_ROOT / ".codex/feature_runner"
FEATURE_STATE_FILE = FEATURE_ROOT / "state.json"
COORD_STATE_FILE = REPO_ROOT / ".codex/packet_coordinator/state.json"
DEFAULT_LANES = [
    "feat-context-storage",
    "feat-commands",
    "feat-retrieval-fts",
    "feat-engine-runs",
    "feat-a2ui-contract",
    "feat-console-shell",
    "feat-console-workflow",
    "feat-ocr-import",
    "feat-literature-import",
    "feat-rag-index",
    "feat-qual-coding",
    "feat-editor-basics",
    "feat-citations",
    "feat-export",
    "feat-zotero-import",
    "feat-formatting-bar",
    "feat-developer-provider-config",
    "feat-project-transfer",
    "feat-desktop-packaging",
    "feat-cop-lite-licensing",
    "feat-browser-pdf-capture",
    "feat-python-sidecar-api",
    "feat-native-workstation",
    "feat-open-access-deep-research",
    "feat-quant-analysis",
    "feat-advanced-qual-visuals",
    "feat-confidential-collaboration",
    "feat-ipad-native-lite",
]
STATE_LOCK = threading.Lock()
STALE_THREAD_RE = "session not found for thread_id"
BAD_LOCAL_MCP_CONTENT_RE = (
    "not supported when using codex with a chatgpt account",
    "invalid_request_error",
    "missing_required_parameter",
    "text.format",
)
FEATURE_LOG_KEEP_RECENT = 24
FEATURE_LOG_MAX_TOTAL_BYTES = 12 * 1024 * 1024
FEATURE_LOG_MIN_AGE_SECONDS = 1800
MAX_INLINE_KICKOFF_CHARS = 6000


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def _current_resume_epoch() -> str:
    state = load_json(COORD_STATE_FILE, {})
    return str((state or {}).get("current_resume_epoch") or "").strip()


def _enabled_lanes() -> List[str]:
    cfg = load_json(CONFIG_FILE, {})
    lanes = cfg.get("lanes") if isinstance(cfg, dict) else {}
    if isinstance(lanes, dict) and lanes:
        enabled = [name for name, lane_cfg in lanes.items() if bool((lane_cfg or {}).get("enabled", True))]
        priority = cfg.get("feature_lane_priority") if isinstance(cfg, dict) else []
        if not isinstance(priority, list):
            priority = []
        return lane_priority_order(enabled, configured_priority=[str(name) for name in priority])
    return lane_priority_order(list(DEFAULT_LANES))


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    try:
        stat = subprocess.run(
            ["ps", "-p", str(pid), "-o", "stat="],
            text=True,
            capture_output=True,
            timeout=2,
        )
        if stat.returncode == 0 and stat.stdout.strip().startswith("Z"):
            return False
    except Exception:
        pass
    return True


def _normalize_profile(raw: Dict[str, object], fallback_cmd: str, fallback_model: str) -> Dict[str, object]:
    cmd_args = list(raw.get("codex_args") or [])
    if "model" in raw:
        model = str(raw.get("model") or "")
    else:
        model = fallback_model
    cmd = str(raw.get("codex_cmd") or fallback_cmd or "codex")
    return {
        "cmd": cmd,
        "cmd_args": [str(x) for x in cmd_args],
        "model": model,
        "model_args": [str(x) for x in list(raw.get("model_args") or [])],
        "harness": str(raw.get("harness") or ("opencode" if Path(cmd).name == "opencode" else "codex")),
    }


def _resolved_profiles(cfg: Dict[str, object]) -> Dict[str, Dict[str, object]]:
    cloud = {
        "cmd": str(cfg.get("codex_cmd") or "codex"),
        "cmd_args": [],
        "model": str(cfg.get("model") or ""),
        "model_args": [],
        "harness": "codex",
    }
    local_cmd = str(cfg.get("fallback_codex_cmd") or cfg.get("codex_cmd") or "codex")
    local = {
        "cmd": local_cmd,
        "cmd_args": [str(x) for x in list(cfg.get("fallback_codex_args") or [])],
        "model": str(cfg.get("fallback_model") or ""),
        "model_args": [str(x) for x in list(cfg.get("fallback_model_args") or [])],
        "harness": "opencode" if Path(local_cmd).name == "opencode" else "codex",
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
    ap.add_argument("--provider", choices=["auto", "local", "cloud"], default="auto", help="Worker provider pool to launch into")
    ap.add_argument("--restart-existing", action="store_true", help="Start a fresh managed session even if lane state exists")
    ap.add_argument("--dry-run", action="store_true", help="Print resolved launch plan without starting managed sessions")
    return ap.parse_args()


def branch_worktrees() -> Dict[str, str]:
    p = run_git(["worktree", "list", "--porcelain"], cwd=REPO_ROOT, timeout=120)
    if p.returncode != 0:
        raise RuntimeError(p.stdout.strip() or "git worktree list failed")
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


def _lane_profile_name(
    cfg: Dict[str, object],
    role_profiles: Dict[str, str],
    lane: str | None,
    *,
    local: bool,
) -> str:
    role_key = "feature_local" if local else "feature_cloud"
    default_name = str(role_profiles[role_key])
    if not lane:
        return default_name
    lane_cfg = dict(cfg.get("lanes") or {}).get(lane) or {}
    if not isinstance(lane_cfg, dict):
        return default_name
    override = lane_cfg.get(f"{role_key}_profile") or lane_cfg.get("feature_profile")
    return str(override or default_name)


def _cloud_available(cfg: Dict[str, object], state: Dict[str, object]) -> bool:
    mode = str(state.get("runtime_mode") or cfg.get("runtime_mode_default") or "cloud_primary")
    if mode == "local_fallback":
        return False
    if mode == "cloud_primary":
        return True
    return bool(state.get("cloud_available", True))


def _launch_mode_for_provider(cfg: Dict[str, object], state: Dict[str, object], provider: str) -> str:
    if provider == "local":
        return "local_fallback"
    if provider == "cloud":
        return "cloud_primary"
    mode = str(state.get("runtime_mode") or cfg.get("runtime_mode_default") or "cloud_primary")
    if mode == "hybrid":
        return "cloud_primary" if _cloud_available(cfg, state) else "local_fallback"
    return mode if mode in {"cloud_primary", "local_fallback"} else "cloud_primary"


def runtime_launch_config(lane: str | None = None, *, provider: str = "auto") -> Dict[str, object]:
    cfg = load_json(CONFIG_FILE, {})
    state = load_json(STATE_FILE, {})
    mode = _launch_mode_for_provider(cfg, state, provider)
    role_profiles = {
        "feature_cloud": "worker_cloud",
        "feature_local": "worker_local",
        **{str(k): str(v) for k, v in dict(cfg.get("role_profiles") or {}).items() if v},
    }
    profiles = _resolved_profiles(cfg)
    profile_name = _lane_profile_name(cfg, role_profiles, lane, local=mode == "local_fallback")
    local_profile_name = _lane_profile_name(cfg, role_profiles, lane, local=True)
    prof = profiles[profile_name]
    local_prof = profiles[local_profile_name]
    lane_cfg = dict(cfg.get("lanes") or {}).get(lane or "") or {}
    if not isinstance(lane_cfg, dict):
        lane_cfg = {}
    branch = str(lane_cfg.get("branch") or (f"codex/{lane}" if lane else ""))
    return {
        "lane": lane or "",
        "branch": branch,
        "mode": mode,
        "profile_name": profile_name,
        "launch_timeout_seconds": float(cfg.get("feature_launch_timeout_seconds", 120)),
        "max_parallel_feature_lanes_cloud": int(cfg.get("max_parallel_feature_lanes_cloud", 4)),
        "max_parallel_feature_lanes_local": int(cfg.get("max_parallel_feature_lanes_local", 1)),
        "max_cloud_feature_jobs": int(cfg.get("max_cloud_feature_jobs", 4)),
        "max_total_cloud_jobs": int(cfg.get("max_total_cloud_jobs", 4)),
        "max_total_local_lms_jobs": int(cfg.get("max_total_local_lms_jobs", 4)),
        "provider": "local" if mode == "local_fallback" else "cloud",
        "disable_local_fallback_on_cloud_timeout": bool(cfg.get("disable_local_fallback_on_cloud_timeout", False)),
        "prefer_direct_exec_cloud": bool(cfg.get("prefer_direct_exec_feature_cloud", True)),
        "local_profile_name": local_profile_name,
        "local_profile": local_prof,
        **prof,
    }


def _bounded_kickoff_text(lane: str) -> str:
    kickoff_path = KICKOFF_DIR / f"{lane}.md"
    kickoff = kickoff_path.read_text()
    _validate_kickoff_text(lane, kickoff_path, kickoff)
    if len(kickoff) <= MAX_INLINE_KICKOFF_CHARS:
        return kickoff
    head = kickoff[:MAX_INLINE_KICKOFF_CHARS]
    return (
        f"{head}\n\n"
        "[KICKOFF PACKET TRUNCATED FOR CONTEXT SAFETY]\n"
        f"The full packet is available at `{kickoff_path}`. Read only targeted sections from it if needed.\n"
    )


def _validate_kickoff_text(lane: str, kickoff_path: Path, kickoff: str) -> None:
    """Fail closed if stale handoff metadata would be used as a feature brief."""
    head = kickoff[:6000].lower()
    stale_markers = (
        "handoff metadata",
        "metadata-only handoff",
        "reviewed implementation range",
        "reviewed source range",
        "packet head role",
        "required fixes addressed",
        "handoff alignment",
    )
    if any(marker in head for marker in stale_markers):
        raise RuntimeError(
            f"Refusing to launch {lane}: {kickoff_path} appears to contain stale "
            "handoff/review metadata instead of a lane kickoff brief."
        )


def _lane_branch_ref(lane: str, launch_cfg: Dict[str, object]) -> str:
    branch_name = str(launch_cfg.get("branch") or f"codex/{lane}")
    return f"refs/heads/{branch_name}"


def build_prompt(lane: str, workdir: str) -> str:
    kickoff = _bounded_kickoff_text(lane)
    engine_priority = "\n".join(f"- {line}" for line in engine_priority_lines())
    return (
        f"You are the feature lane agent for {lane}.\n\n"
        f"Work only inside the lane worktree at:\n{workdir}\n\n"
        "Current program brief:\n"
        f"- {ENGINE_MILESTONE_FOCUS}\n"
        "- Textual UI lanes remain disabled until explicitly enabled.\n"
        "- Active engine execution order:\n"
        f"{engine_priority}\n\n"
        "Before making changes, gather only the narrow evidence needed from these documents.\n"
        "Do not use full-file `cat`, full-file Read, or broad document dumps on any of these docs. "
        "First use `rg -n` for the exact section headings or keywords you need, then read only the matching "
        "`nl -ba | sed -n '<start>,<end>p'` range, normally <=80 lines:\n"
        "- AGENTS.md\n"
        "- INTEGRATION.md\n"
        "- THREAD_OWNERSHIP.md\n"
        "- ROADMAP.md\n"
        "- PRODUCT_VISION.md\n"
        "- ARCHITECTURE.md\n"
        "- PIPELINE_RUNBOOK.md\n\n"
        "Local context discipline:\n"
        "- Never read a large source or markdown file with an unbounded `cat` or full-file Read.\n"
        "- Before reading any source file that may be large, run `wc -l <path>` and targeted `rg -n` first.\n"
        "- For files longer than roughly 20 KB or 250 lines, read only targeted ranges with `nl -ba | sed -n '<start>,<end>p'`; do not use full-file Read.\n"
        "- Keep source reads to the smallest relevant section, normally <=80 lines at a time and never more than 120 lines.\n"
        "- Prefer symbol/name searches over opening whole modules; inspect tests by exact test names or nearby assertions only.\n"
        "- Do not recursively search `.codex`, `.agents`, archives, or logs unless a named file is required.\n"
        "- Do not run broad historical `git diff` commands across old implementation ranges; use current `git status`, focused `git show --stat`, and path-scoped diffs only.\n"
        "- If a test failure prints a huge diff, rerun the single failing test with narrower assertions or inspect the expected/actual shape directly instead of expanding the full diff.\n"
        "- If any tool reports `Context size has been exceeded`, stop immediately, report that blocker in the lane log, and wait for a fresh launch instead of continuing.\n\n"
        "Use this kickoff packet as the operating brief:\n\n"
        f"{kickoff}\n\n"
        "Execution requirements:\n"
        "- Stay inside lane-owned paths only.\n"
        "- Treat any kickoff text that asks you to repair handoff metadata, packet metadata, shared packets, lane metadata, `THREAD_PACKET.md`, `.codex/**`, `packet_garden/**`, or scope policy as stale/non-actionable for a feature lane; report `control-plane metadata fix required` and stop instead of editing those files.\n"
        "- Do not edit or commit control-plane files from a feature branch, including `packet_garden/**`, `.codex/**`, `.agents/**`, `THREAD_PACKET.md`, `THREAD_OWNERSHIP.md`, `INTEGRATION.md`, `AGENTS.md`, or `scripts/scope-check.sh`.\n"
        "- If control-plane behavior must change, stop and report the blocker for integrator/control-plane handling instead of patching it in this lane.\n"
        "- Use the existing git worktree exactly as provided; do not replace `.git` or create `.git-local`, `.git-alt*`, shadow repos, or alternate object/index stores.\n"
        "- If normal git operations fail, stop and report the failure rather than inventing custom git plumbing.\n"
        "- When using `apply_patch`, pass the patch as a single patch string. Do not call `apply_patch` with no patch body and do not emit raw JSON-style tool calls for it.\n"
        "- If the same tool call fails twice with the same error, stop retrying the malformed call and report the blocker.\n"
        "- Use the kickoff budget and stop triggers exactly as written.\n"
        "- Make a real, meaningful code change from current lane HEAD.\n"
        "- Run the required gates before handoff.\n"
        "- Commit your completed work on the lane branch.\n"
        "- Provide the handoff fields required by INTEGRATION.md in your final message; do not edit THREAD_PACKET.md or .codex packet metadata from the feature branch.\n"
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
    prune_log_dir(
        log_path.parent,
        keep_recent=FEATURE_LOG_KEEP_RECENT,
        max_total_bytes=FEATURE_LOG_MAX_TOTAL_BYTES,
        min_age_seconds=FEATURE_LOG_MIN_AGE_SECONDS,
    )
    lines = [json.dumps(header, sort_keys=True), "", content.strip(), ""]
    log_path.write_text("\n".join(lines))


def _active_local_feature_jobs(feature_state: Dict[str, Any]) -> int:
    lanes = feature_state.get("lanes") if isinstance(feature_state, dict) else {}
    if not isinstance(lanes, dict):
        return 0
    active = 0
    for lane_state in lanes.values():
        if not isinstance(lane_state, dict):
            continue
        if str(lane_state.get("mode") or "") != "local_fallback":
            continue
        if _pid_alive(int(lane_state.get("pid") or 0)):
            active += 1
    return active


def _active_cloud_feature_jobs(feature_state: Dict[str, Any]) -> int:
    lanes = feature_state.get("lanes") if isinstance(feature_state, dict) else {}
    if not isinstance(lanes, dict):
        return 0
    active = 0
    for lane_state in lanes.values():
        if not isinstance(lane_state, dict):
            continue
        if str(lane_state.get("mode") or "") != "cloud_primary":
            continue
        if _pid_alive(int(lane_state.get("pid") or 0)):
            active += 1
    return active


def _active_cloud_router_jobs(router_state: Dict[str, Any]) -> int:
    active = 0
    for key in ("cloud_reviewer_jobs", "cloud_integrator_jobs"):
        jobs = router_state.get(key) if isinstance(router_state, dict) else {}
        if isinstance(jobs, dict):
            for job in jobs.values():
                if isinstance(job, dict) and _pid_alive(int(job.get("pid") or 0)):
                    active += 1
    fixer_jobs = router_state.get("fixer_fallback_jobs") if isinstance(router_state, dict) else {}
    if isinstance(fixer_jobs, dict):
        for job in fixer_jobs.values():
            if not isinstance(job, dict):
                continue
            if bool(job.get("local", True)):
                continue
            if _pid_alive(int(job.get("pid") or 0)):
                active += 1
    return active


def _active_local_router_jobs(router_state: Dict[str, Any]) -> int:
    active = 0
    for key in ("local_reviewer_jobs", "local_integrator_jobs"):
        jobs = router_state.get(key) if isinstance(router_state, dict) else {}
        if not isinstance(jobs, dict):
            continue
        for job in jobs.values():
            if isinstance(job, dict) and _pid_alive(int(job.get("pid") or 0)):
                active += 1
    fixer_jobs = router_state.get("fixer_fallback_jobs") if isinstance(router_state, dict) else {}
    if isinstance(fixer_jobs, dict):
        for job in fixer_jobs.values():
            if not isinstance(job, dict):
                continue
            if not bool(job.get("local", True)):
                continue
            if _pid_alive(int(job.get("pid") or 0)):
                active += 1
    return active


def _local_lms_launch_slots(launch_cfg: Dict[str, object], feature_state: Dict[str, Any]) -> int:
    if str(launch_cfg.get("mode") or "") != "local_fallback":
        return 999999
    cap = int(launch_cfg.get("max_total_local_lms_jobs") or 0)
    if cap <= 0:
        return 999999
    router_state = load_json(STATE_FILE, {})
    active = _active_local_feature_jobs(feature_state) + _active_local_router_jobs(router_state)
    return max(0, cap - active)


def _cloud_feature_launch_slots(launch_cfg: Dict[str, object], feature_state: Dict[str, Any]) -> int:
    cap = int(launch_cfg.get("max_cloud_feature_jobs") or 0)
    if cap <= 0:
        return 0
    router_state = load_json(STATE_FILE, {})
    total_cap = int(launch_cfg.get("max_total_cloud_jobs") or 0)
    feature_slots = max(0, cap - _active_cloud_feature_jobs(feature_state))
    if total_cap <= 0:
        return feature_slots
    active_total = _active_cloud_feature_jobs(feature_state) + _active_cloud_router_jobs(router_state)
    return min(feature_slots, max(0, total_cap - active_total))


def _spawn_direct_exec(
    profile_cfg: Dict[str, object],
    *,
    workdir: str,
    prompt: str,
    log_path: Path,
    prompt_path: Path | None = None,
) -> int:
    prune_log_dir(
        log_path.parent,
        keep_recent=FEATURE_LOG_KEEP_RECENT,
        max_total_bytes=FEATURE_LOG_MAX_TOTAL_BYTES,
        min_age_seconds=FEATURE_LOG_MIN_AGE_SECONDS,
    )
    cmd_args = [str(x) for x in list(profile_cfg["cmd_args"])]
    local_mode = str(profile_cfg.get("mode") or "") == "local_fallback"
    harness = str(profile_cfg.get("harness") or "codex")
    model = str(profile_cfg.get("model") or "")
    env = agent_runtime_env(str(REPO_ROOT), isolated_codex_env(str(REPO_ROOT)) if local_mode else None)
    resolved_prompt_path = prompt_path or log_path.with_suffix(".prompt.md")
    resolved_prompt_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_prompt_path.write_text(prompt)
    bootstrap = (
        "Do not answer in prose first. Use the shell tool immediately.\n"
        f"Your first shell command must be exactly: cat {resolved_prompt_path.resolve()}\n"
        "After reading that file, treat its contents as the real user prompt and follow it exactly.\n"
        "Begin real work immediately after reading the file.\n"
        "If the file is missing, report that exact blocker and stop."
    )
    if harness == "opencode":
        cmd = [str(profile_cfg["cmd"]), "run", *cmd_args]
        if model:
            opencode_model = model if "/" in model else f"lmstudio/{model}"
            cmd.extend(["--model", opencode_model])
        cmd.extend(["--dir", workdir, "--dangerously-skip-permissions"])
        cmd.extend([str(x) for x in list(profile_cfg.get("model_args") or [])])
        # OpenCode handles tool calls in a single run differently than Codex:
        # a "cat the prompt file first" bootstrap can be treated as the whole
        # job and exit after printing the file. Send the lane prompt directly.
        cmd.append(prompt)
    else:
        cmd = [str(profile_cfg["cmd"]), "exec", *cmd_args]
        if local_mode:
            cmd.append("--skip-git-repo-check")
        if model and "-m" not in cmd_args and "--model" not in cmd_args:
            cmd.extend(["-m", model])
        cmd.extend([str(x) for x in list(profile_cfg.get("model_args") or [])])
        if local_mode:
            cmd.extend(["--add-dir", str(resolved_prompt_path.parent.resolve())])
        cmd.extend(["-s", "workspace-write", bootstrap])
    with log_path.open("a") as lf:
        proc = subprocess.Popen(
            cmd,
            cwd=workdir,
            stdout=lf,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            env=env,
            start_new_session=True,
        )
    return proc.pid


def _is_bad_local_mcp_content(text: str) -> bool:
    lower = str(text or "").lower()
    return any(marker in lower for marker in BAD_LOCAL_MCP_CONTENT_RE)


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
    current_epoch = _current_resume_epoch()
    with STATE_LOCK:
        current_state = load_json(FEATURE_STATE_FILE, {})
        if not isinstance(current_state, dict):
            current_state = {}
        lanes_state = current_state.setdefault("lanes", {})
        lanes_state[lane] = {
            "lane": lane,
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
            "resume_epoch": current_epoch,
        }
        save_json(FEATURE_STATE_FILE, current_state)


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
    branch_ref = _lane_branch_ref(lane, launch_cfg)
    workdir = worktrees.get(branch_ref)
    if not workdir:
        return {"lane": lane, "status": "skipped", "reason": f"no worktree for {branch_ref}"}

    try:
        prompt = build_prompt(lane, workdir)
    except FileNotFoundError as exc:
        missing = Path(getattr(exc, "filename", "") or (KICKOFF_DIR / f"{lane}.md"))
        return {
            "lane": lane,
            "status": "skipped",
            "reason": f"missing kickoff packet: {missing}",
        }
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
    if (
        str(launch_cfg["mode"]) == "cloud_primary"
        and bool(launch_cfg.get("disable_local_fallback_on_cloud_timeout"))
        and str(lane_state.get("status") or "") == "error"
    ):
        pid = _spawn_direct_exec(launch_cfg, workdir=workdir, prompt=prompt, log_path=log_path)
        _set_lane_state(
            feature_state,
            lane,
            status="direct_exec_running",
            mode=str(launch_cfg["mode"]),
            profile=str(launch_cfg["profile_name"]),
            workdir=workdir,
            prompt_path=prompt_path,
            log_path=log_path,
            thread_id="",
            error=str(lane_state.get("error") or ""),
            action="direct_exec_cloud_restart",
            pid=pid,
        )
        _write_log(
            log_path,
            {
                "lane": lane,
                "thread_id": "",
                "mode": launch_cfg["mode"],
                "profile": launch_cfg["profile_name"],
                "workdir": workdir,
                "action": "direct_exec_cloud_restart",
                "launched_at": _ts(),
                "status": "direct_exec_running",
                "pid": pid,
            },
            f"Restarted lane with cloud direct exec after prior managed launch error: {lane_state.get('error', '')}",
        )
        return {
            "lane": lane,
            "status": "direct_exec_running",
            "mode": launch_cfg["mode"],
            "profile": launch_cfg["profile_name"],
            "workdir": workdir,
            "pid": pid,
            "log": str(log_path),
            "error": str(lane_state.get("error") or ""),
        }
    thread_id = None if args.restart_existing else lane_state.get("thread_id")
    # Local fallback has no durable managed threads to resume from LM Studio.
    # If we carry over a stale cloud-era thread id here, the launcher will spin
    # on a dead session instead of starting fresh local work.
    if str(launch_cfg["mode"]) == "local_fallback":
        thread_id = None
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

    def _is_stale_thread_error(exc: Exception) -> bool:
        return STALE_THREAD_RE in str(exc).lower()

    def _is_stale_thread_content(text: str) -> bool:
        return STALE_THREAD_RE in str(text).lower()

    try:
        if str(launch_cfg["mode"]) == "cloud_primary" and bool(launch_cfg.get("prefer_direct_exec_cloud")):
            pid = _spawn_direct_exec(launch_cfg, workdir=workdir, prompt=prompt, log_path=log_path)
            _set_lane_state(
                feature_state,
                lane,
                status="direct_exec_running",
                mode=str(launch_cfg["mode"]),
                profile=str(launch_cfg["profile_name"]),
                workdir=workdir,
                prompt_path=prompt_path,
                log_path=log_path,
                thread_id="",
                error="",
                action="direct_exec_cloud_default",
                pid=pid,
            )
            _write_log(
                log_path,
                {
                    "lane": lane,
                    "thread_id": "",
                    "mode": launch_cfg["mode"],
                    "profile": launch_cfg["profile_name"],
                    "workdir": workdir,
                    "action": "direct_exec_cloud_default",
                    "launched_at": _ts(),
                    "status": "direct_exec_running",
                    "pid": pid,
                },
                "Cloud feature lane launched as direct exec.",
            )
            return {
                "lane": lane,
                "status": "direct_exec_running",
                "mode": launch_cfg["mode"],
                "profile": launch_cfg["profile_name"],
                "workdir": workdir,
                "pid": pid,
                "log": str(log_path),
            }
        if str(launch_cfg["mode"]) == "local_fallback":
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
                error="",
                action="direct_exec_local_fallback",
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
                    "action": "direct_exec_local_fallback",
                    "launched_at": _ts(),
                    "status": "direct_exec_running",
                    "pid": pid,
                },
                "Local fallback launched as direct exec.",
            )
            return {
                "lane": lane,
                "status": "direct_exec_running",
                "mode": direct_profile["mode"],
                "profile": direct_profile["profile_name"],
                "workdir": workdir,
                "pid": pid,
                "log": str(log_path),
            }
        effective_cfg = dict(launch_cfg)
        if thread_id:
            try:
                thread_id, content, action = _attempt(effective_cfg, existing_thread_id=str(thread_id))
                if _is_stale_thread_content(content) or _is_bad_local_mcp_content(content):
                    stale_id = str(thread_id)
                    thread_id = None
                    _write_log(
                        log_path,
                        {
                            "lane": lane,
                            "thread_id": stale_id,
                            "mode": effective_cfg["mode"],
                            "profile": effective_cfg["profile_name"],
                            "workdir": workdir,
                            "action": "stale_thread_retry",
                            "launched_at": _ts(),
                            "status": "launching",
                        },
                        f"Managed feature resume returned stale thread content; relaunching fresh: {content}",
                    )
                    _set_lane_state(
                        feature_state,
                        lane,
                        status="launching",
                        mode=str(effective_cfg["mode"]),
                        profile=str(effective_cfg["profile_name"]),
                        workdir=workdir,
                        prompt_path=prompt_path,
                        log_path=log_path,
                        thread_id="",
                        error="",
                        action="stale_thread_retry",
                        pid=0,
                    )
                    thread_id, content, action = _attempt(effective_cfg, existing_thread_id=None)
            except Exception as exc:
                if not _is_stale_thread_error(exc):
                    raise
                stale_id = str(thread_id)
                thread_id = None
                _write_log(
                    log_path,
                    {
                        "lane": lane,
                        "thread_id": stale_id,
                        "mode": effective_cfg["mode"],
                        "profile": effective_cfg["profile_name"],
                        "workdir": workdir,
                        "action": "stale_thread_retry",
                        "launched_at": _ts(),
                        "status": "launching",
                    },
                    f"Managed feature resume failed with stale thread id; relaunching fresh: {exc}",
                )
                _set_lane_state(
                    feature_state,
                    lane,
                    status="launching",
                    mode=str(effective_cfg["mode"]),
                    profile=str(effective_cfg["profile_name"]),
                    workdir=workdir,
                    prompt_path=prompt_path,
                    log_path=log_path,
                    thread_id="",
                    error="",
                    action="stale_thread_retry",
                    pid=0,
                )
                thread_id, content, action = _attempt(effective_cfg, existing_thread_id=None)
        else:
            thread_id, content, action = _attempt(effective_cfg, existing_thread_id=None)
        if _is_stale_thread_content(content) or _is_bad_local_mcp_content(content):
            raise RuntimeError(f"stale thread content returned after launch: {content}")
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
        if str(launch_cfg["mode"]) == "cloud_primary" and bool(launch_cfg.get("disable_local_fallback_on_cloud_timeout")):
            pid = _spawn_direct_exec(launch_cfg, workdir=workdir, prompt=prompt, log_path=log_path)
            _set_lane_state(
                feature_state,
                lane,
                status="direct_exec_running",
                mode=str(launch_cfg["mode"]),
                profile=str(launch_cfg["profile_name"]),
                workdir=workdir,
                prompt_path=prompt_path,
                log_path=log_path,
                thread_id="",
                error=str(exc),
                action="direct_exec_cloud_fallback",
                pid=pid,
            )
            _write_log(
                log_path,
                {
                    "lane": lane,
                    "thread_id": "",
                    "mode": launch_cfg["mode"],
                    "profile": launch_cfg["profile_name"],
                    "workdir": workdir,
                    "action": "direct_exec_cloud_fallback",
                    "launched_at": _ts(),
                    "status": "direct_exec_running",
                    "pid": pid,
                },
                f"Managed cloud launch failed, spawned cloud direct exec fallback: {exc}",
            )
            return {
                "lane": lane,
                "status": "direct_exec_running",
                "mode": launch_cfg["mode"],
                "profile": launch_cfg["profile_name"],
                "workdir": workdir,
                "pid": pid,
                "log": str(log_path),
                "error": str(exc),
            }
        if (
            str(launch_cfg["mode"]) == "cloud_primary"
            and not bool(launch_cfg.get("disable_local_fallback_on_cloud_timeout"))
        ):
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
    launch_cfg = runtime_launch_config(provider=args.provider)
    lane_launch_cfgs = {lane: runtime_launch_config(lane, provider=args.provider) for lane in args.lanes}
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
            lane_launch_cfg = lane_launch_cfgs[lane]
            branch = _lane_branch_ref(lane, lane_launch_cfg)
            workdir = worktrees.get(branch)
            launched.append(
                {
                    "lane": lane,
                    "mode": lane_launch_cfg["mode"],
                    "profile": lane_launch_cfg["profile_name"],
                    "workdir": workdir,
                    "action": "launch" if args.restart_existing or lane not in lanes_state else "resume",
                }
            )
        print(json.dumps({"runtime_mode": launch_cfg["mode"], "launched": launched}, indent=2))
        return 0

    if str(launch_cfg["mode"]) == "local_fallback":
        parallel_limit = int(launch_cfg.get("max_parallel_feature_lanes_local", 1))
        parallel_limit = min(parallel_limit, _local_lms_launch_slots(launch_cfg, feature_state))
    else:
        parallel_limit = int(launch_cfg.get("max_parallel_feature_lanes_cloud", 4))
        parallel_limit = min(parallel_limit, _cloud_feature_launch_slots(launch_cfg, feature_state))
    if parallel_limit <= 0:
        print(json.dumps({"runtime_mode": launch_cfg["mode"], "launched": []}, indent=2))
        return 0
    launch_candidates: List[str] = []
    for lane in args.lanes:
        lane_launch_cfg = lane_launch_cfgs[lane]
        branch_ref = _lane_branch_ref(lane, lane_launch_cfg)
        if branch_ref not in worktrees:
            launched.append({"lane": lane, "status": "skipped", "reason": f"no worktree for {branch_ref}"})
            continue
        kickoff_path = KICKOFF_DIR / f"{lane}.md"
        if not kickoff_path.exists():
            launched.append({"lane": lane, "status": "skipped", "reason": f"missing kickoff packet: {kickoff_path}"})
            continue
        launch_candidates.append(lane)
    lanes_to_launch = launch_candidates[:parallel_limit]
    if not lanes_to_launch:
        print(json.dumps({"runtime_mode": launch_cfg["mode"], "launched": launched}, indent=2))
        return 0
    max_workers = min(len(lanes_to_launch), parallel_limit)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                _launch_one_lane,
                lane,
                args=args,
                launch_cfg=lane_launch_cfgs[lane],
                worktrees=worktrees,
                prompts_dir=prompts_dir,
                logs_dir=logs_dir,
                feature_state=feature_state,
            )
            for lane in lanes_to_launch
        ]
        for fut in as_completed(futures):
            launched.append(fut.result())

    print(json.dumps({"runtime_mode": launch_cfg["mode"], "launched": launched}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
