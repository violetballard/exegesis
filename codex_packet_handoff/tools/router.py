#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import subprocess
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from codex_mcp_client import ApprovalPolicy, CodexMcpClient
    from git_ops import run_git
    from git_hygiene import prune_stale_index_locks
    from log_maintenance import prune_log_dir
    from local_codex_runtime import isolated_codex_env
    from packet_progress import infer_last_submitted_sha
except ImportError:  # pragma: no cover - test/import fallback for package execution
    from .codex_mcp_client import ApprovalPolicy, CodexMcpClient
    from .git_ops import run_git
    from .git_hygiene import prune_stale_index_locks
    from .log_maintenance import prune_log_dir
    from .local_codex_runtime import isolated_codex_env
    from .packet_progress import infer_last_submitted_sha

PACKETS_ROOT = Path(".codex/packets/lanes")
ROUTER_ROOT = Path(".codex/packet_router")
STATE_FILE = ROUTER_ROOT / "state.json"
CONFIG_FILE = ROUTER_ROOT / "config.json"
CURSOR_FILE = ROUTER_ROOT / "cursor.json"
LEASE_FILE = ROUTER_ROOT / "lease.json"
REPO_ROOT = Path(__file__).resolve().parents[2]
COORD_STATE_FILE = REPO_ROOT / ".codex/packet_coordinator/state.json"
FEATURE_RUNNER_STATE_FILE = REPO_ROOT / ".codex/feature_runner/state.json"
LOCAL_CLI_WORKER = Path(__file__).resolve().with_name("local_cli_worker.py")
LOCAL_JOB_ROOT = ROUTER_ROOT / "local_jobs"

VERDICT_INLINE_RE = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?:\*\*)?(?:\d+\.\s*)?(?:\*\*)?Verdict(?:\*\*)?:?\s*`?(APPROVED|CHANGES_REQUESTED|CHANGES REQUESTED)`?\s*$",
    re.IGNORECASE,
)
VERDICT_ONLY_RE = re.compile(
    r"^\s*`?(APPROVED|CHANGES_REQUESTED|CHANGES REQUESTED)`?\s*$",
    re.IGNORECASE,
)
INVALID_REVIEWER_RE = re.compile(r"session not found for thread_id|thread not found", re.IGNORECASE)
REVIEWER_QUOTA_RE = re.compile(
    r"usage limit|quota exceeded|rate limit|too many requests|try again at",
    re.IGNORECASE,
)
REAL_QUOTA_LINE_RE = re.compile(
    r"you(?:'| a)ve hit your usage limit|quota exceeded|429 too many requests|rate limit|too many requests|try again at\s+[A-Za-z]{3}\s+\d{1,2}",
    re.IGNORECASE,
)
CODE_LIKE_QUOTA_CONTEXT_RE = re.compile(
    r"REVIEWER_QUOTA_RE|FIXER_QUOTA_RE|_apply_quota_text_safeguard|auto_switch_to_local_on_quota|"
    r"fixer_quota_retry_cooldown_seconds|reviewer quota/rate-limit response|quota text on lane|"
    r"self\.assert|def\s+_|^\s*[+\-]{1,3}\s|^\s*@@|^\s*diff --git|^\s*index\s|^\s*---\s|^\s*\+\+\+\s|"
    r"\br[\"'].*(usage limit|quota exceeded|rate limit|too many requests|try again at)",
    re.IGNORECASE,
)
BAD_LOCAL_CLI_CONTENT_MARKERS = (
    "not supported when using codex with a chatgpt account",
    "invalid_request_error",
    "missing_required_parameter",
    "text.format",
)
RETRY_LIMIT_WRAPPER_RE = re.compile(
    r"exceeded retry limit|retry limit reached",
    re.IGNORECASE,
)
PACKET_SHA_RE = re.compile(r"__(?P<sha>[0-9a-f]{7,40})__")
FIXER_QUOTA_RE = REVIEWER_QUOTA_RE
FIXER_RETRY_AT_RE = re.compile(
    r"try again at\s+([A-Za-z]{3}\s+\d{1,2}(?:st|nd|rd|th)?,\s+\d{4}\s+\d{1,2}:\d{2}\s+[AP]M)",
    re.IGNORECASE,
)
LOCAL_REVIEWER_MAX_ACTIVE = 1
LOCAL_INTEGRATOR_MAX_ACTIVE = 1
CLOUD_INTEGRATOR_MAX_ACTIVE = 1
LOCAL_INTEGRATOR_RETRY_COOLDOWN_SECONDS = 60.0
CLOUD_INTEGRATOR_RETRY_COOLDOWN_SECONDS = 60.0
ROUTER_LOG_KEEP_RECENT = 36
ROUTER_LOG_MAX_TOTAL_BYTES = 16 * 1024 * 1024
ROUTER_LOG_MIN_AGE_SECONDS = 1800

@dataclass
class RouterConfig:
    model: str
    codex_cmd: str
    fallback_model: str
    fallback_codex_cmd: str
    fallback_codex_args: List[str]
    fallback_model_args: List[str]
    runtime_mode_default: str
    auto_switch_to_local_on_quota: bool
    auto_probe_cloud_recovery: bool
    cloud_probe_cooldown_seconds: float
    cloud_probe_timeout_seconds: float
    reviewer_timeout: float
    integrator_timeout: float
    max_packets_per_run: int
    inline_fixer: bool
    kick_fixers_on_reviewer_backlog: bool
    fixer_kick_timeout_seconds: float
    reviewer_fixer_retry_cooldown_seconds: float
    fixer_quota_retry_cooldown_seconds: float
    max_cloud_fixer_kicks_per_run: int
    max_local_fixer_kicks_per_run: int
    max_cloud_fixer_jobs: int
    max_local_fixer_jobs: int
    prefer_cli_fixer: bool
    prefer_cli_reviewer: bool
    prefer_cli_integrator: bool
    use_cli_reviewer_fallback: bool
    use_cli_integrator_fallback: bool
    profiles: Dict[str, "LaunchProfile"]
    role_profiles: Dict[str, str]
    lanes: Dict[str, Dict[str, Any]]
    max_total_local_lms_jobs: int = 4


@dataclass
class LaunchProfile:
    codex_cmd: str
    codex_args: List[str]
    model: str
    model_args: List[str]

def load_json(p: Path, default: Any) -> Any:
    try:
        return json.loads(p.read_text())
    except Exception:
        return default

def save_json(p: Path, data: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def _current_resume_epoch() -> str:
    state = load_json(COORD_STATE_FILE, {})
    return str((state or {}).get("current_resume_epoch") or "").strip()

def acquire_lease(ttl: int = 20) -> bool:
    now = time.time()
    if LEASE_FILE.exists():
        d = load_json(LEASE_FILE, {})
        if now - float(d.get("ts", 0)) < ttl:
            return False
    save_json(LEASE_FILE, {"ts": now, "pid": os.getpid()})
    return True

def release_lease() -> None:
    try:
        if LEASE_FILE.exists():
            LEASE_FILE.unlink()
    except Exception:
        pass


def _normalize_profile(raw: Dict[str, Any], *, fallback_cmd: str = "codex", fallback_model: str = "") -> LaunchProfile:
    cmd = str(raw.get("codex_cmd") or fallback_cmd or "codex")
    cmd_args = [str(x) for x in list(raw.get("codex_args") or [])]
    if "model" in raw:
        model = str(raw.get("model") or "")
    else:
        model = str(fallback_model or "")
    model_args = [str(x) for x in list(raw.get("model_args") or [])]
    return LaunchProfile(codex_cmd=cmd, codex_args=cmd_args, model=model, model_args=model_args)


def _default_profiles(cfg: Dict[str, Any]) -> Dict[str, LaunchProfile]:
    cloud_cmd = str(cfg.get("codex_cmd", "codex"))
    cloud_model = str(cfg.get("model", "gpt-5.1-codex"))
    fallback_cmd = str(cfg.get("fallback_codex_cmd") or cloud_cmd)
    fallback_model = str(cfg.get("fallback_model") or "")
    fallback_cmd_args = [str(x) for x in list(cfg.get("fallback_codex_args") or [])]
    fallback_model_args = [str(x) for x in list(cfg.get("fallback_model_args") or [])]
    if "--oss" in fallback_cmd_args and fallback_model == cloud_model:
        fallback_model = ""
    return {
        "orchestrator": LaunchProfile(cloud_cmd, [], cloud_model, []),
        "worker_cloud": LaunchProfile(cloud_cmd, [], cloud_model, []),
        "worker_local": LaunchProfile(fallback_cmd, fallback_cmd_args, fallback_model, fallback_model_args),
    }


def _default_role_profiles() -> Dict[str, str]:
    return {
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
    }

def load_cfg() -> RouterConfig:
    cfg = load_json(CONFIG_FILE, None)
    if not cfg:
        raise SystemExit(f"Missing {CONFIG_FILE} (copy example.json).")
    fallback_cmd = str(cfg.get("fallback_codex_cmd") or os.environ.get("CODEX_FALLBACK_CMD") or cfg.get("codex_cmd", "codex"))
    env_fallback_model = os.environ.get("CODEX_FALLBACK_MODEL")
    if "fallback_model" in cfg:
        fallback_model = str(cfg.get("fallback_model") or "")
    elif env_fallback_model is not None:
        fallback_model = str(env_fallback_model)
    else:
        fallback_model = str(cfg.get("model", "gpt-5.1-codex"))
    fallback_cmd_args = cfg.get("fallback_codex_args")
    if not isinstance(fallback_cmd_args, list):
        env_args = (os.environ.get("CODEX_FALLBACK_ARGS") or "").strip()
        fallback_cmd_args = env_args.split() if env_args else []
    fallback_model_args = cfg.get("fallback_model_args")
    if not isinstance(fallback_model_args, list):
        env_model_args = (os.environ.get("CODEX_FALLBACK_MODEL_ARGS") or "").strip()
        fallback_model_args = env_model_args.split() if env_model_args else []
    if "--oss" in [str(x) for x in fallback_cmd_args] and fallback_model == cfg.get("model", "gpt-5.1-codex"):
        fallback_model = ""
    profiles = _default_profiles(cfg)
    for name, raw in dict(cfg.get("profiles") or {}).items():
        if isinstance(raw, dict):
            base = profiles.get(str(name), LaunchProfile("codex", [], "", []))
            profiles[str(name)] = _normalize_profile(
                raw,
                fallback_cmd=base.codex_cmd,
                fallback_model=base.model,
            )
    role_profiles = _default_role_profiles()
    for key, value in dict(cfg.get("role_profiles") or {}).items():
        if value:
            role_profiles[str(key)] = str(value)
    lane_cfg_map = {
        str(name): dict(lane_cfg or {})
        for name, lane_cfg in dict(cfg.get("lanes", {})).items()
        if bool((lane_cfg or {}).get("enabled", True))
    }
    return RouterConfig(
        model=str(cfg.get("model", "gpt-5.1-codex")),
        codex_cmd=str(cfg.get("codex_cmd", "codex")),
        fallback_model=fallback_model,
        fallback_codex_cmd=fallback_cmd,
        fallback_codex_args=[str(x) for x in fallback_cmd_args],
        fallback_model_args=[str(x) for x in fallback_model_args],
        runtime_mode_default=str(cfg.get("runtime_mode_default", "cloud_primary")),
        auto_switch_to_local_on_quota=bool(cfg.get("auto_switch_to_local_on_quota", True)),
        auto_probe_cloud_recovery=bool(cfg.get("auto_probe_cloud_recovery", True)),
        cloud_probe_cooldown_seconds=float(cfg.get("cloud_probe_cooldown_seconds", 300)),
        cloud_probe_timeout_seconds=float(cfg.get("cloud_probe_timeout_seconds", 30)),
        reviewer_timeout=float(cfg.get("reviewer_timeout", 180)),
        integrator_timeout=float(cfg.get("integrator_timeout", 900)),
        max_packets_per_run=int(cfg.get("max_packets_per_run", 1)),
        inline_fixer=bool(cfg.get("inline_fixer", False)),
        kick_fixers_on_reviewer_backlog=bool(cfg.get("kick_fixers_on_reviewer_backlog", True)),
        fixer_kick_timeout_seconds=float(cfg.get("fixer_kick_timeout_seconds", 8)),
        reviewer_fixer_retry_cooldown_seconds=float(cfg.get("reviewer_fixer_retry_cooldown_seconds", 900)),
        fixer_quota_retry_cooldown_seconds=float(cfg.get("fixer_quota_retry_cooldown_seconds", 3600)),
        max_cloud_fixer_kicks_per_run=int(cfg.get("max_cloud_fixer_kicks_per_run", 1)),
        max_local_fixer_kicks_per_run=int(cfg.get("max_local_fixer_kicks_per_run", 1)),
        max_cloud_fixer_jobs=int(cfg.get("max_cloud_fixer_jobs", 2)),
        max_local_fixer_jobs=int(cfg.get("max_local_fixer_jobs", 2)),
        max_total_local_lms_jobs=int(cfg.get("max_total_local_lms_jobs", 4)),
        prefer_cli_fixer=bool(cfg.get("prefer_cli_fixer", True)),
        prefer_cli_reviewer=bool(cfg.get("prefer_cli_reviewer", True)),
        prefer_cli_integrator=bool(cfg.get("prefer_cli_integrator", True)),
        use_cli_reviewer_fallback=bool(cfg.get("use_cli_reviewer_fallback", True)),
        use_cli_integrator_fallback=bool(cfg.get("use_cli_integrator_fallback", True)),
        profiles=profiles,
        role_profiles=role_profiles,
        lanes=lane_cfg_map,
    )

def ensure_lane_dirs(lane: str) -> Path:
    d = PACKETS_ROOT / lane
    (d/"inbox/feature").mkdir(parents=True, exist_ok=True)
    (d/"inbox/reviewer").mkdir(parents=True, exist_ok=True)
    (d/"outbox/integrator").mkdir(parents=True, exist_ok=True)
    (d/"archive").mkdir(parents=True, exist_ok=True)
    return d

def list_new(lane_dir: Path, last_seen: Optional[str]) -> List[Path]:
    files = sorted((lane_dir/"inbox/feature").glob("*.md"), key=lambda p: p.stat().st_mtime)
    if not last_seen:
        return files[-1:] if files else []
    if all(f.name != last_seen for f in files):
        return files[-1:] if files else []
    out: List[Path] = []
    seen = False
    for f in files:
        if seen:
            out.append(f)
        if f.name == last_seen:
            seen = True
    return out


def _packet_sha(name: str) -> str:
    m = PACKET_SHA_RE.search(name or "")
    return (m.group("sha") if m else "").lower()


def _branch_head_sha(repo_cwd: str, branch: str) -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", branch],
            cwd=repo_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
    except Exception:
        return ""
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").strip().lower()


def _latest_fixer_log(lane: str) -> Optional[Path]:
    logs = ROUTER_ROOT / "logs"
    files = sorted(logs.glob(f"fixer__{lane}__*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _parse_retry_epoch_from_quota_log(text: str) -> Optional[float]:
    m = FIXER_RETRY_AT_RE.search(text or "")
    if not m:
        return None
    token = re.sub(r"(\d{1,2})(st|nd|rd|th)", r"\1", m.group(1), flags=re.IGNORECASE)
    try:
        dt = datetime.strptime(token, "%b %d, %Y %I:%M %p")
        return dt.replace(tzinfo=datetime.now().astimezone().tzinfo).timestamp()
    except Exception:
        return None


def _quota_retry_epoch(cfg: RouterConfig, text: str, *, default_seconds: Optional[float] = None) -> float:
    retry_at = _parse_retry_epoch_from_quota_log(text)
    if retry_at is not None and retry_at > time.time():
        return retry_at
    seconds = default_seconds if default_seconds is not None else cfg.cloud_probe_cooldown_seconds
    return time.time() + float(seconds)


def _expired_explicit_quota_retry(text: str, *, now: Optional[float] = None) -> bool:
    retry_at = _parse_retry_epoch_from_quota_log(text)
    if retry_at is None:
        return False
    if now is None:
        now = time.time()
    return retry_at <= now


def _apply_quota_text_safeguard(
    cfg: RouterConfig,
    state: Dict[str, Any],
    text: str,
    *,
    reason: str,
    default_seconds: Optional[float] = None,
) -> Dict[str, Any]:
    if not _has_real_quota_signal(text):
        return state
    if RETRY_LIMIT_WRAPPER_RE.search(text):
        return state
    retry_at = _quota_retry_epoch(cfg, text, default_seconds=default_seconds)
    return _switch_to_local_fallback(cfg, state, reason, retry_at)


def _has_real_quota_signal(text: str) -> bool:
    if not text:
        return False
    for raw in text.splitlines()[-200:]:
        line = raw.strip()
        if not line:
            continue
        if RETRY_LIMIT_WRAPPER_RE.search(line):
            continue
        if CODE_LIKE_QUOTA_CONTEXT_RE.search(line):
            continue
        if REAL_QUOTA_LINE_RE.search(line):
            return True
    return False


def _extract_reviewer_verdict(text: str) -> Optional[str]:
    lines = (text or "").splitlines()
    for idx, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            continue
        m = VERDICT_INLINE_RE.match(line)
        if m:
            v = m.group(1).upper().replace(" ", "_")
            return "APPROVED" if v == "APPROVED" else "CHANGES_REQUESTED"
        if "verdict" in line.lower():
            for nxt in lines[idx + 1 : idx + 4]:
                nxt_line = nxt.strip()
                if not nxt_line:
                    continue
                m2 = VERDICT_ONLY_RE.match(nxt_line)
                if m2:
                    v = m2.group(1).upper().replace(" ", "_")
                    return "APPROVED" if v == "APPROVED" else "CHANGES_REQUESTED"
                break
    return None


def _last_verdict_line_index(text: str) -> Optional[int]:
    lines = (text or "").splitlines()
    last_idx: Optional[int] = None
    for idx, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            continue
        if VERDICT_INLINE_RE.match(line):
            last_idx = idx
            continue
        if "verdict" not in line.lower():
            continue
        for nxt in lines[idx + 1 : idx + 4]:
            nxt_line = nxt.strip()
            if not nxt_line:
                continue
            if VERDICT_ONLY_RE.match(nxt_line):
                last_idx = idx
            break
    return last_idx


def _extract_final_verdict_packet(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return ""
    start = _last_verdict_line_index(raw)
    if start is None or start <= 0:
        return raw
    return "\n".join(raw.splitlines()[start:]).strip()


def parse_verdict(text: str) -> str:
    verdict = _extract_reviewer_verdict(text)
    if verdict:
        return verdict
    return "CHANGES_REQUESTED"


def clear_stale_integrator_handoffs(lane_dir: Path, packet_name: str) -> int:
    outbox = lane_dir / "outbox" / "integrator"
    if not outbox.exists():
        return 0
    pattern = packet_name.replace("F__", "R__APPROVED__")
    moved = 0
    stale_dir = lane_dir / "archive" / "stale"
    stale_dir.mkdir(parents=True, exist_ok=True)
    for path in outbox.glob(pattern):
        target = stale_dir / path.name
        counter = 1
        while target.exists():
            target = stale_dir / f"{path.stem}__stale{counter}{path.suffix}"
            counter += 1
        path.rename(target)
        moved += 1
    return moved


def _invalid_reviewer_output(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    return bool(INVALID_REVIEWER_RE.search(t))


def _local_cli_output_rejection_reason(text: str, *, require_verdict: bool) -> Optional[str]:
    t = (text or "").strip()
    if not t:
        return "empty output"
    if INVALID_REVIEWER_RE.search(t):
        return "stale or missing thread reference"
    lower = t.lower()
    for marker in BAD_LOCAL_CLI_CONTENT_MARKERS:
        if marker in lower:
            return f"bad local cli marker: {marker}"
    if require_verdict and _extract_reviewer_verdict(t) is None:
        return "missing reviewer verdict"
    return None


def _is_reviewer_quota_output(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    return bool(REVIEWER_QUOTA_RE.search(t))


def _runtime_mode(cfg: RouterConfig, state: Dict[str, Any]) -> str:
    mode = str(state.get("runtime_mode") or cfg.runtime_mode_default or "cloud_primary")
    return mode if mode in ("cloud_primary", "local_fallback") else "cloud_primary"


def _profile_name_for_role(
    cfg: RouterConfig,
    role: str,
    *,
    local: Optional[bool] = None,
    lane: Optional[str] = None,
) -> str:
    lane_cfg = cfg.lanes.get(lane or "", {}) or {}
    if not isinstance(lane_cfg, dict):
        lane_cfg = {}
    if local is None:
        return str(lane_cfg.get(f"{role}_profile") or cfg.role_profiles.get(role) or role)
    suffix = "local" if local else "cloud"
    return str(
        lane_cfg.get(f"{role}_{suffix}_profile")
        or lane_cfg.get(f"{role}_profile")
        or cfg.role_profiles.get(f"{role}_{suffix}")
        or cfg.role_profiles.get(role)
        or ("worker_local" if local else "worker_cloud")
    )


def _profile_for_role(
    cfg: RouterConfig,
    role: str,
    *,
    local: Optional[bool] = None,
    lane: Optional[str] = None,
) -> LaunchProfile:
    name = _profile_name_for_role(cfg, role, local=local, lane=lane)
    prof = cfg.profiles.get(name)
    if prof:
        return prof
    defaults = _default_profiles({"codex_cmd": cfg.codex_cmd, "model": cfg.model, "fallback_codex_cmd": cfg.fallback_codex_cmd, "fallback_codex_args": cfg.fallback_codex_args, "fallback_model": cfg.fallback_model, "fallback_model_args": cfg.fallback_model_args})
    return defaults["worker_local" if local else "worker_cloud"]


def _build_mcp_client(profile: LaunchProfile, approval: ApprovalPolicy) -> CodexMcpClient:
    return CodexMcpClient(approval=approval, codex_cmd=profile.codex_cmd, codex_args=profile.codex_args)


def _set_runtime_mode(
    cfg: RouterConfig,
    state: Dict[str, Any],
    mode: str,
    *,
    reason: str = "",
    retry_at: Optional[float] = None,
) -> Dict[str, Any]:
    state["runtime_mode"] = mode
    state["last_mode_switch_at"] = time.time()
    if reason:
        state["last_quota_reason"] = reason
    if retry_at is not None:
        state["cloud_retry_at"] = retry_at
    elif mode == "cloud_primary":
        state["cloud_retry_at"] = 0
    return state


def _switch_to_local_fallback(
    cfg: RouterConfig,
    state: Dict[str, Any],
    reason: str,
    retry_at: Optional[float] = None,
) -> Dict[str, Any]:
    if retry_at is None or retry_at <= time.time():
        retry_at = time.time() + cfg.cloud_probe_cooldown_seconds
    return _set_runtime_mode(cfg, state, "local_fallback", reason=reason, retry_at=retry_at)


def _maybe_restore_cloud(
    cfg: RouterConfig,
    state: Dict[str, Any],
    repo_cwd: str,
) -> Dict[str, Any]:
    if _runtime_mode(cfg, state) != "local_fallback":
        return state
    if not cfg.auto_probe_cloud_recovery:
        return state
    retry_at = float(state.get("cloud_retry_at", 0) or 0)
    now = time.time()
    if retry_at > now:
        return state
    probe = _profile_for_role(cfg, "cloud_probe", local=False)
    try:
        rc, out = _run_cli_codex(
            probe.codex_cmd,
            probe.codex_args,
            probe.model,
            probe.model_args,
            "read-only",
            repo_cwd,
            "Reply with OK only.",
            cfg.cloud_probe_timeout_seconds,
        )
        if rc != 0:
            return _switch_to_local_fallback(cfg, state, f"cloud probe exited {rc}")
        text = (out or "").strip()
        if text and not _is_reviewer_quota_output(text) and not _invalid_reviewer_output(text):
            return _set_runtime_mode(cfg, state, "cloud_primary", reason="cloud probe succeeded", retry_at=0)
    except Exception as exc:
        return _switch_to_local_fallback(cfg, state, f"cloud probe failed: {exc}")
    return _switch_to_local_fallback(cfg, state, "cloud probe returned invalid/empty output")


def _offline_reviewer_fallback(pkt: str, reason: str) -> str:
    """Produce a deterministic reviewer packet when reviewer threads are unavailable.

    This keeps the pipeline moving during quota windows instead of stalling.
    """
    t = pkt or ""
    tl = t.lower()

    checks = [
        ("tasks completed", ["tasks completed"]),
        ("files changed", ["files changed"]),
        ("commands run and outcomes", ["commands run", "outcomes"]),
        ("risks or blockers", ["risk", "blocker"]),
    ]
    missing_fields: List[str] = []
    for label, needles in checks:
        if not all(n in tl for n in needles):
            missing_fields.append(label)

    required_cmds = [
        "./quality-format.sh --check",
        "./quality-lint.sh",
        "./quality-test.sh",
        "./typecheck-test.sh",
        "make ci",
    ]
    missing_cmds = [c for c in required_cmds if c.lower() not in tl]

    fail_markers = [
        "failed",
        "error",
        "traceback",
        "non-zero",
        "exit 1",
        "exit code 1",
    ]
    has_fail_markers = any(m in tl for m in fail_markers)
    has_blocker = "blocker" in tl and not ("no blocker" in tl or "none" in tl)

    approve = not missing_fields and not missing_cmds and not has_fail_markers and not has_blocker
    if approve:
        return (
            "Verdict: `APPROVED`\n\n"
            "Findings\n"
            "- Reviewer was unavailable; offline policy fallback validated packet structure and required gates.\n\n"
            "Missing handoff fields (if any)\n"
            "- none\n\n"
            "Required fixes before re-review (numbered, actionable)\n"
            "1. none\n\n"
            "If approved: merge order + any post-merge checks (include merge risk)\n"
            "1. Merge this lane after existing queued approvals.\n"
            "2. Re-run `make ci` on integrator branch.\n"
            "3. Merge risk: medium (reviewer fallback used due quota window).\n\n"
            f"Fallback reason: {reason}\n"
        )

    fixes: List[str] = []
    if missing_fields:
        fixes.append(f"Add missing handoff fields: {', '.join(missing_fields)}.")
    if missing_cmds:
        fixes.append(f"Run and report required gates: {', '.join(missing_cmds)}.")
    if has_fail_markers:
        fixes.append("Resolve failing gate output and include passing results.")
    if has_blocker:
        fixes.append("Address blocker(s) or clearly scope a minimal safe handoff.")
    if not fixes:
        fixes.append("Resubmit with complete evidence for required checks.")

    fixes_txt = "\n".join(f"{i+1}. {f}" for i, f in enumerate(fixes))
    return (
        "Verdict: `CHANGES_REQUESTED`\n\n"
        "Findings (highest severity first)\n"
        "- Reviewer was unavailable; offline policy fallback detected missing approval evidence.\n\n"
        "Missing handoff fields (if any)\n"
        + ("\n".join(f"- {m}" for m in missing_fields) if missing_fields else "- none")
        + "\n\nRequired fixes before re-review (numbered, actionable)\n"
        + fixes_txt
        + f"\n\nFallback reason: {reason}\n"
    )

def reviewer_prompt(pkt: str) -> str:
    return (
        "You are the REVIEWER. You are sandboxed read-only and MUST NOT modify files.\n"
        "You MUST enforce plan alignment by reading: ROADMAP.md, PRODUCT_VISION.md, ARCHITECTURE.md, INTEGRATION.md, AGENTS.md.\n"
        "If roadmap/vision mapping is unclear or off-plan, output CHANGES_REQUESTED with concrete scope-tightening.\n\n"
        "Output exactly one markdown packet with sections:\n"
        "1. Verdict: `APPROVED` or `CHANGES_REQUESTED`\n"
        "2. Findings (highest severity first)\n"
        "3. Missing handoff fields (if any)\n"
        "4. Required fixes before re-review (numbered, actionable)\n"
        "5. If approved: merge order + any post-merge checks (include merge risk)\n\n"
        f"Review this feature packet:\n\n{pkt}\n"
    )

def integrator_prompt(approved: str) -> str:
    packet = _extract_final_verdict_packet(approved)
    return (
        "You are the INTEGRATOR. You may write to the workspace.\n"
        "Consume this APPROVED packet, perform merge order + post-merge checks, report blockers.\n\n"
        f"{packet}\n"
    )


def _run_cli_codex(
    codex_cmd: str,
    codex_args: List[str],
    model: str,
    model_args: List[str],
    sandbox: str,
    cwd: str,
    prompt: str,
    timeout: float,
    *,
    env: Optional[Dict[str, str]] = None,
    skip_git_repo_check: bool = False,
) -> Tuple[int, str]:
    cmd = [codex_cmd, "exec", *codex_args]
    if skip_git_repo_check:
        cmd.append("--skip-git-repo-check")
    if model:
        cmd.extend(["-m", model])
    if model_args:
        cmd.extend(model_args)
    cmd.extend(["-s", sandbox, prompt])
    p = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        text=True,
        timeout=timeout,
        env=env,
    )
    return p.returncode, p.stdout or ""


def _run_cli_reviewer(
    cfg: RouterConfig,
    repo_cwd: str,
    pkt: str,
    reason: str,
    *,
    local: Optional[bool] = None,
    lane: Optional[str] = None,
) -> Optional[str]:
    if not cfg.use_cli_reviewer_fallback:
        return None
    runtime_local = bool(local)
    prof = _profile_for_role(cfg, "reviewer", local=local, lane=lane)
    env = isolated_codex_env(repo_cwd) if runtime_local else None
    try:
        rc, out = _run_cli_codex(
            prof.codex_cmd,
            prof.codex_args,
            prof.model,
            prof.model_args,
            "read-only",
            repo_cwd,
            reviewer_prompt(pkt),
            cfg.reviewer_timeout,
            env=env,
            skip_git_repo_check=runtime_local,
        )
    except Exception:
        return None
    if rc != 0:
        return None
    text = (out or "").strip()
    if not text:
        return None
    if runtime_local:
        rejection = _local_cli_output_rejection_reason(text, require_verdict=True)
        if rejection:
            print(f"[router] rejected local reviewer output ({reason}): {rejection}")
            return None
    return text


def _run_cli_integrator(
    cfg: RouterConfig,
    repo_cwd: str,
    approved: str,
    *,
    local: Optional[bool] = None,
    lane: Optional[str] = None,
) -> Optional[str]:
    if not cfg.use_cli_integrator_fallback:
        return None
    runtime_local = bool(local)
    prof = _profile_for_role(cfg, "integrator", local=local, lane=lane)
    env = isolated_codex_env(repo_cwd) if runtime_local else None
    try:
        rc, out = _run_cli_codex(
            prof.codex_cmd,
            prof.codex_args,
            prof.model,
            prof.model_args,
            "workspace-write",
            repo_cwd,
            integrator_prompt(approved),
            cfg.integrator_timeout,
            env=env,
            skip_git_repo_check=runtime_local,
        )
    except Exception:
        return None
    if rc != 0:
        return None
    text = (out or "").strip()
    if not text:
        return None
    if runtime_local:
        rejection = _local_cli_output_rejection_reason(text, require_verdict=False)
        if rejection:
            print(f"[router] rejected local integrator output: {rejection}")
            return None
    return text


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _safe_job_token(raw: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", raw or "job").strip("._") or "job"


def _local_job_map(state: Dict[str, Any], key: str) -> Dict[str, Dict[str, Any]]:
    jobs = state.get(key)
    if isinstance(jobs, dict):
        return jobs
    jobs = {}
    state[key] = jobs
    return jobs


def _count_active_local_jobs(job_map: Dict[str, Dict[str, Any]]) -> int:
    active = 0
    for job in job_map.values():
        result_path = Path(str(job.get("result_path") or ""))
        pid = int(job.get("pid") or 0)
        if result_path.exists():
            continue
        if _pid_alive(pid):
            active += 1
    return active


def _count_active_pid_jobs(job_map: Dict[str, Dict[str, Any]], *, local: Optional[bool] = None) -> int:
    active = 0
    for job in job_map.values():
        if not isinstance(job, dict):
            continue
        if local is not None and bool(job.get("local")) != local:
            continue
        pid = int(job.get("pid") or 0)
        if _pid_alive(pid):
            active += 1
    return active


def _count_active_feature_local_jobs() -> int:
    feature_state = load_json(FEATURE_RUNNER_STATE_FILE, {})
    lanes = feature_state.get("lanes") if isinstance(feature_state, dict) else {}
    if not isinstance(lanes, dict):
        return 0
    active = 0
    for lane_state in lanes.values():
        if not isinstance(lane_state, dict):
            continue
        if str(lane_state.get("mode") or "") != "local_fallback":
            continue
        pid = int(lane_state.get("pid") or 0)
        if _pid_alive(pid):
            active += 1
    return active


def _count_active_local_lms_jobs(state: Dict[str, Any]) -> int:
    active = _count_active_feature_local_jobs()
    active += _count_active_local_jobs(_local_job_map(state, "local_reviewer_jobs"))
    active += _count_active_local_jobs(_local_job_map(state, "local_integrator_jobs"))
    active += _count_active_pid_jobs(_local_job_map(state, "fixer_fallback_jobs"), local=True)
    return active


def _local_lms_slot_available(cfg: RouterConfig, state: Dict[str, Any]) -> bool:
    cap = int(getattr(cfg, "max_total_local_lms_jobs", 4) or 0)
    if cap <= 0:
        return True
    return _count_active_local_lms_jobs(state) < cap


def _build_cli_exec_cmd(
    profile: LaunchProfile,
    *,
    sandbox: str,
    prompt: str,
    local: bool,
    add_dirs: Optional[List[str]] = None,
) -> List[str]:
    cmd = [profile.codex_cmd, "exec", *profile.codex_args]
    if local:
        cmd.append("--skip-git-repo-check")
    if profile.model:
        cmd.extend(["-m", profile.model])
    if profile.model_args:
        cmd.extend(profile.model_args)
    for add_dir in add_dirs or []:
        if add_dir:
            cmd.extend(["--add-dir", str(add_dir)])
    cmd.extend(["-s", sandbox, prompt])
    return [str(x) for x in cmd]


def _prompt_file_bootstrap(prompt_path: Path) -> str:
    resolved = prompt_path.resolve()
    return (
        "Do not answer in prose first. Use the shell tool immediately.\n"
        f"Your first shell command must be exactly: cat {resolved}\n"
        "After reading that file, treat its contents as the real user prompt and follow it exactly.\n"
        "Begin real work immediately after reading the file.\n"
        "If the file is missing, report that exact blocker and stop."
    )


def _spawn_detached_cli_job(
    *,
    role: str,
    cfg: RouterConfig,
    repo_cwd: str,
    lane: str,
    packet_name: str,
    prompt: str,
    sandbox: str,
    timeout_seconds: float,
    local: bool,
) -> Dict[str, Any]:
    profile = _profile_for_role(cfg, role, local=local, lane=lane)
    resume_epoch = _current_resume_epoch()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    token = _safe_job_token(f"{lane}__{packet_name}")
    job_dir = LOCAL_JOB_ROOT / role
    job_dir.mkdir(parents=True, exist_ok=True)
    spec_path = job_dir / f"{ts}__{token}.spec.json"
    output_path = job_dir / f"{ts}__{token}.out.log"
    result_path = job_dir / f"{ts}__{token}.result.json"
    prompt_path = job_dir / f"{ts}__{token}.prompt.txt"
    write_text(prompt_path, prompt)
    spec = {
        "cmd": _build_cli_exec_cmd(
            profile,
            sandbox=sandbox,
            prompt=_prompt_file_bootstrap(prompt_path),
            local=local,
            add_dirs=[str(prompt_path.parent.resolve())] if local else None,
        ),
        "cwd": repo_cwd,
        "timeout_seconds": float(timeout_seconds),
        "env_overrides": {"CODEX_HOME": isolated_codex_env(repo_cwd)["CODEX_HOME"]} if local else {},
        "output_path": str(output_path),
        "result_path": str(result_path),
        "resume_epoch": resume_epoch,
    }
    save_json(spec_path, spec)
    proc = subprocess.Popen(
        [sys.executable, str(LOCAL_CLI_WORKER), "--spec", str(spec_path)],
        cwd=repo_cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
        start_new_session=True,
    )
    return {
        "lane": lane,
        "packet_name": packet_name,
        "pid": proc.pid,
        "spec_path": str(spec_path),
        "output_path": str(output_path),
        "result_path": str(result_path),
        "started_at": time.time(),
        "resume_epoch": resume_epoch,
    }


def _spawn_detached_local_cli_job(
    *,
    role: str,
    cfg: RouterConfig,
    repo_cwd: str,
    lane: str,
    packet_name: str,
    prompt: str,
    sandbox: str,
    timeout_seconds: float,
) -> Dict[str, Any]:
    return _spawn_detached_cli_job(
        role=role,
        cfg=cfg,
        repo_cwd=repo_cwd,
        lane=lane,
        packet_name=packet_name,
        prompt=prompt,
        sandbox=sandbox,
        timeout_seconds=timeout_seconds,
        local=True,
    )


def _poll_detached_local_cli_job(job: Dict[str, Any]) -> Dict[str, Any]:
    result_path = Path(str(job.get("result_path") or ""))
    output_path = Path(str(job.get("output_path") or ""))
    if result_path.exists():
        result = load_json(result_path, {})
        output = ""
        if output_path.exists():
            try:
                output = output_path.read_text()
            except Exception:
                output = ""
        return {
            "done": True,
            "status": str(result.get("status") or "error"),
            "rc": int(result.get("rc", 1) or 1),
            "error": str(result.get("error") or ""),
            "output": output.strip(),
        }
    pid = int(job.get("pid") or 0)
    if _pid_alive(pid):
        return {"done": False, "status": "running", "rc": 0, "error": "", "output": ""}
    output = ""
    if output_path.exists():
        try:
            output = output_path.read_text()
        except Exception:
            output = ""
    return {
        "done": True,
        "status": "error",
        "rc": 1,
        "error": "local cli worker exited before writing result",
        "output": output.strip(),
    }


def _prepare_local_reviewer_result(
    cfg: RouterConfig,
    state: Dict[str, Any],
    repo_cwd: str,
    lane: str,
    pkt_path: Path,
    pkt: str,
) -> Tuple[bool, str, Dict[str, Any]]:
    jobs = _local_job_map(state, "local_reviewer_jobs")
    packet_name = pkt_path.name
    job = jobs.get(lane)
    if isinstance(job, dict) and str(job.get("packet_name") or "") != packet_name:
        if not _pid_alive(int(job.get("pid") or 0)):
            jobs.pop(lane, None)
            job = None
        else:
            state["local_reviewer_jobs"] = jobs
            return False, "", state

    if isinstance(job, dict):
        polled = _poll_detached_local_cli_job(job)
        if not polled["done"]:
            state["local_reviewer_jobs"] = jobs
            return False, "", state
        jobs.pop(lane, None)
        state["local_reviewer_jobs"] = jobs
        text = str(polled.get("output") or "").strip()
        rejection = _local_cli_output_rejection_reason(text, require_verdict=True)
        if polled.get("status") == "ok" and not rejection:
            return True, text, state
        reason = str(polled.get("error") or rejection or "local reviewer job failed")
        print(f"[router] local reviewer job for {lane} failed, using offline fallback: {reason}")
        return True, _offline_reviewer_fallback(pkt, reason), state

    if _count_active_local_jobs(jobs) >= LOCAL_REVIEWER_MAX_ACTIVE:
        state["local_reviewer_jobs"] = jobs
        return False, "", state
    if not _local_lms_slot_available(cfg, state):
        state["local_reviewer_jobs"] = jobs
        return False, "", state

    jobs[lane] = _spawn_detached_local_cli_job(
        role="reviewer",
        cfg=cfg,
        repo_cwd=repo_cwd,
        lane=lane,
        packet_name=packet_name,
        prompt=reviewer_prompt(pkt),
        sandbox="read-only",
        timeout_seconds=cfg.reviewer_timeout,
    )
    state["local_reviewer_jobs"] = jobs
    print(f"[router] queued local reviewer job for {lane} ({packet_name})")
    return False, "", state


def _prepare_local_integrator_result(
    cfg: RouterConfig,
    state: Dict[str, Any],
    repo_cwd: str,
    lane: str,
    pkt: Path,
    approved_text: str,
) -> Tuple[bool, str, Dict[str, Any]]:
    jobs = _local_job_map(state, "local_integrator_jobs")
    retry_ts = state.get("local_integrator_retry_ts")
    if not isinstance(retry_ts, dict):
        retry_ts = {}
        state["local_integrator_retry_ts"] = retry_ts
    job_key = f"{lane}:{pkt.name}"
    job = jobs.get(job_key)
    if isinstance(job, dict):
        polled = _poll_detached_local_cli_job(job)
        if not polled["done"]:
            state["local_integrator_jobs"] = jobs
            return False, "", state
        jobs.pop(job_key, None)
        state["local_integrator_jobs"] = jobs
        text = str(polled.get("output") or "").strip()
        rejection = _local_cli_output_rejection_reason(text, require_verdict=False)
        if polled.get("status") == "ok" and not rejection and text:
            retry_ts.pop(job_key, None)
            state["local_integrator_retry_ts"] = retry_ts
            return True, text, state
        reason = str(polled.get("error") or rejection or "local integrator job failed")
        retry_ts[job_key] = time.time() + LOCAL_INTEGRATOR_RETRY_COOLDOWN_SECONDS
        state["local_integrator_retry_ts"] = retry_ts
        print(f"[router] local integrator job for {lane} failed; will retry later: {reason}")
        return False, "", state

    retry_at = float(retry_ts.get(job_key, 0) or 0)
    if retry_at > time.time():
        state["local_integrator_retry_ts"] = retry_ts
        return False, "", state
    if _count_active_local_jobs(jobs) >= LOCAL_INTEGRATOR_MAX_ACTIVE:
        state["local_integrator_jobs"] = jobs
        return False, "", state
    if not _local_lms_slot_available(cfg, state):
        state["local_integrator_jobs"] = jobs
        return False, "", state

    jobs[job_key] = _spawn_detached_local_cli_job(
        role="integrator",
        cfg=cfg,
        repo_cwd=repo_cwd,
        lane=lane,
        packet_name=pkt.name,
        prompt=integrator_prompt(approved_text),
        sandbox="workspace-write",
        timeout_seconds=cfg.integrator_timeout,
    )
    state["local_integrator_jobs"] = jobs
    print(f"[router] queued local integrator job for {lane} ({pkt.name})")
    return False, "", state


def _integrator_failure_handback_packet(
    lane: str,
    pkt: Path,
    *,
    reason: str,
    output: str,
) -> str:
    evidence = (output or "").strip()
    if len(evidence) > 6000:
        evidence = evidence[-6000:]
    evidence_block = evidence or "(no captured integrator output)"
    return (
        "Verdict: `CHANGES_REQUESTED`\n\n"
        "Findings (highest severity first)\n"
        f"- High: The approved `{lane}` packet failed during integrator merge/check execution, "
        "so it must go back through the feature fixer before another approval attempt.\n\n"
        "Missing handoff fields (if any)\n"
        "- none\n\n"
        "Required fixes before re-review (numbered, actionable)\n"
        "1. Reproduce the integrator failure locally in the lane worktree.\n"
        "2. Fix the failing integration gate or merge conflict that blocked integration.\n"
        "3. Re-run the required lane gates and resubmit a fresh feature packet for review.\n\n"
        "Integrator failure context\n"
        f"- Approval packet: `{pkt.name}`\n"
        f"- Failure reason: {reason}\n\n"
        "Captured integrator output\n"
        "```text\n"
        f"{evidence_block}\n"
        "```\n"
    )


def _write_integrator_failure_handback(
    lane_dir: Path,
    lane: str,
    pkt: Path,
    *,
    reason: str,
    output: str,
) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    sha = _packet_sha(pkt.name) or "unknown"
    note = lane_dir / "inbox" / "reviewer" / f"R__CHANGES__codex-{lane}__{sha}__{ts}.md"
    write_text(
        note,
        _integrator_failure_handback_packet(
            lane,
            pkt,
            reason=reason,
            output=output,
        ),
    )

    failed_dir = lane_dir / "archive" / "integrator_failed"
    failed_dir.mkdir(parents=True, exist_ok=True)
    target = failed_dir / pkt.name
    counter = 1
    while target.exists():
        target = failed_dir / f"{pkt.stem}__failed{counter}{pkt.suffix}"
        counter += 1
    try:
        pkt.rename(target)
    except Exception:
        if pkt.exists():
            target.write_text(pkt.read_text())
            pkt.unlink()
    return note


def _prepare_cli_integrator_result(
    cfg: RouterConfig,
    state: Dict[str, Any],
    repo_cwd: str,
    lane: str,
    pkt: Path,
    approved_text: str,
    *,
    local: bool,
) -> Tuple[bool, str, Dict[str, Any]]:
    jobs_key = "local_integrator_jobs" if local else "cloud_integrator_jobs"
    retry_key = "local_integrator_retry_ts" if local else "cloud_integrator_retry_ts"
    max_active = LOCAL_INTEGRATOR_MAX_ACTIVE if local else CLOUD_INTEGRATOR_MAX_ACTIVE
    mode_label = "local" if local else "cloud"
    jobs = _local_job_map(state, jobs_key)
    retry_ts = state.get(retry_key)
    if not isinstance(retry_ts, dict):
        retry_ts = {}
        state[retry_key] = retry_ts
    job_key = f"{lane}:{pkt.name}"
    job = jobs.get(job_key)
    if isinstance(job, dict):
        polled = _poll_detached_local_cli_job(job)
        if not polled["done"]:
            state[jobs_key] = jobs
            return False, "", state
        jobs.pop(job_key, None)
        state[jobs_key] = jobs
        text = str(polled.get("output") or "").strip()
        rejection = _local_cli_output_rejection_reason(text, require_verdict=False)
        if polled.get("status") == "ok" and not rejection and text:
            retry_ts.pop(job_key, None)
            state[retry_key] = retry_ts
            return True, text, state
        reason = str(polled.get("error") or rejection or f"{mode_label} integrator job failed")
        quota_text = "\n".join(part for part in (text, reason) if part)
        if not local and cfg.auto_switch_to_local_on_quota and _has_real_quota_signal(quota_text):
            state = _switch_to_local_fallback(
                cfg,
                state,
                f"cloud integrator job failed/timed out: {reason}",
                _quota_retry_epoch(cfg, quota_text),
            )
            retry_ts.pop(job_key, None)
            state[retry_key] = retry_ts
            print(f"[router] cloud integrator job for {lane} hit quota; switching to local fallback: {reason}")
            return False, "", state
        lane_dir = pkt.parents[2] if len(pkt.parents) > 2 else ensure_lane_dirs(lane)
        note = _write_integrator_failure_handback(
            lane_dir,
            lane,
            pkt,
            reason=reason,
            output=text,
        )
        retry_ts.pop(job_key, None)
        state[retry_key] = retry_ts
        print(f"[router] {mode_label} integrator job for {lane} failed; handed back to fixer via {note.name}: {reason}")
        return False, "", state

    retry_at = float(retry_ts.get(job_key, 0) or 0)
    if retry_at > time.time():
        state[retry_key] = retry_ts
        return False, "", state
    if _count_active_local_jobs(jobs) >= max_active:
        state[jobs_key] = jobs
        return False, "", state
    if local and not _local_lms_slot_available(cfg, state):
        state[jobs_key] = jobs
        return False, "", state

    jobs[job_key] = _spawn_detached_cli_job(
        role="integrator",
        cfg=cfg,
        repo_cwd=repo_cwd,
        lane=lane,
        packet_name=pkt.name,
        prompt=integrator_prompt(approved_text),
        sandbox="workspace-write",
        timeout_seconds=cfg.integrator_timeout,
        local=local,
    )
    state[jobs_key] = jobs
    print(f"[router] queued {mode_label} integrator job for {lane} ({pkt.name})")
    return False, "", state

def _find_worktree_for_branch(repo_cwd: str, branch: str) -> Optional[str]:
    # Normalize to refs/heads/...
    ref = branch
    if ref.startswith("refs/heads/"):
        want = ref
    else:
        want = f"refs/heads/{ref}"
    p = run_git(["worktree", "list", "--porcelain"], cwd=repo_cwd, timeout=120)
    if p.returncode != 0:
        return None
    blocks = p.stdout.split("\n\n")
    for b in blocks:
        wt = None
        br = None
        for ln in [x.strip() for x in b.splitlines() if x.strip()]:
            if ln.startswith("worktree "):
                wt = ln.split(" ",1)[1].strip()
            elif ln.startswith("branch "):
                br = ln.split(" ",1)[1].strip()
        if wt and br and br == want:
            return wt
    return None


def _sync_lane_runbook_files(repo_cwd: str, workdir: Optional[str]) -> None:
    """Ensure lane worktrees have required operator docs used by automation prompts.

    Some older lane worktrees were created before AGENTS.md existed, causing fixers
    to churn on missing-file lookups instead of applying requested changes.
    """
    if not workdir:
        return
    root = Path(repo_cwd)
    wt = Path(workdir)
    for name in (
        "AGENTS.md",
        "INTEGRATION.md",
        "THREAD.md",
        "THREAD_PACKET.md",
        "THREAD_OWNERSHIP.md",
        "ROADMAP.md",
        "PRODUCT_VISION.md",
        "ARCHITECTURE.md",
    ):
        src = root / name
        dst = wt / name
        try:
            if not src.exists():
                continue
            if dst.exists():
                continue
            dst.write_text(src.read_text())
        except Exception:
            # Best-effort only; fixer can still run without this sync.
            continue

def fixer_prompt(lane: str, branch: str, reviewer_packet: str, workdir: Optional[str]) -> str:
    lane_commit_helper = REPO_ROOT / "codex_packet_handoff/tools/lane_repo_commit.py"
    if workdir:
        return (
            f"You are the FEATURE FIXER for lane `{lane}`.\n"
            f"Apply the reviewer's REQUIRED FIXES to branch `{branch}`.\n\n"
            f"You are running inside the lane worktree at: {workdir}\n"
            "That worktree already has the branch checked out, so DO NOT detach or update-ref.\n"
            "Edit files, run gates, and commit normally.\n\n"
            "Execution guardrails:\n"
            "- Use only files that exist in this worktree.\n"
            "- If a referenced path is missing and non-essential, skip it and continue with available evidence.\n"
            "- Do not block on searching for reviewer metadata files; use the packet below as the source of truth.\n"
            "- Prioritize implementing numbered REQUIRED FIXES over exploratory file hunting.\n\n"
            "- Do not replace `.git`, create `.git-local`, or create shadow git repos/index/object directories.\n"
            f"- If normal `git add` / `git commit` fails on a stale lock or index error, use the approved helper instead:\n"
            f"  `python {lane_commit_helper} --message \\\"<commit message>\\\"`\n"
            "- Do not invent any other git plumbing beyond that helper.\n\n"
            "Run: make scope-check; ./quality-format.sh --check; ./quality-lint.sh; ./quality-test.sh; ./typecheck-test.sh; make ci\n\n"
            "Deliverable: a new commit that addresses the numbered required fixes, plus the final HEAD SHA.\n\n"
            "Reviewer packet to satisfy:\n\n"
            f"{reviewer_packet}\n"
        )
    return (
        f"You are the FEATURE FIXER for lane `{lane}`.\n"
        f"Apply the reviewer's REQUIRED FIXES to branch `{branch}`.\n\n"
        "Fallback: branch is checked out elsewhere.\n"
        "Resolve branch -> SHA, detach at SHA, make changes, commit, then update local branch ref:\n"
        "  git update-ref refs/heads/<branch> HEAD\n\n"
        "Execution guardrails:\n"
        "- Use only files available in the current checkout.\n"
        "- If a referenced path is missing and non-essential, skip it and continue with available evidence.\n"
        "- Do not block on searching for reviewer metadata files; use the packet below as the source of truth.\n"
        "- Prioritize implementing numbered REQUIRED FIXES over exploratory file hunting.\n\n"
        f"If normal git commit fails on stale locks, the approved helper is:\n"
        f"  python {lane_commit_helper} --message \"<commit message>\"\n\n"
        "Run: make scope-check; ./quality-format.sh --check; ./quality-lint.sh; ./quality-test.sh; ./typecheck-test.sh; make ci\n\n"
        "Reviewer packet to satisfy:\n\n"
        f"{reviewer_packet}\n"
    )

def run_fixer(
    client: CodexMcpClient,
    cfg: RouterConfig,
    state: dict,
    lane: str,
    reviewer_packet: str,
    repo_cwd: str,
    *,
    local_mode: Optional[bool] = None,
) -> dict:
    lane_cfg = cfg.lanes.get(lane, {}) or {}
    branch = str(lane_cfg.get("branch") or f"codex/{lane}")
    wt = _find_worktree_for_branch(repo_cwd, branch)
    _sync_lane_runbook_files(repo_cwd, wt)
    prune_stale_index_locks(Path(repo_cwd))
    runtime_local = _runtime_mode(cfg, state) == "local_fallback" if local_mode is None else bool(local_mode)
    if not runtime_local and not cfg.prefer_cli_fixer:
        fixer_map = state.get("fixer_thread_ids") or {}
        tid = fixer_map.get(lane)
        try:
            if not tid:
                tid, _ = client.codex(
                    prompt=f"You are the FEATURE FIXER for lane `{lane}`. You will apply reviewer-required fixes.",
                    cwd=(wt or repo_cwd),
                    sandbox="workspace-write",
                    approval_policy="never",
                    model=cfg.model,
                    timeout=cfg.fixer_kick_timeout_seconds,
                )
            tid, _ = client.codex_reply(
                tid,
                fixer_prompt(lane, branch, reviewer_packet, wt),
                timeout=cfg.fixer_kick_timeout_seconds,
            )
            fixer_map[lane] = tid
            state["fixer_thread_ids"] = fixer_map
            return state
        except Exception:
            pass

    # Fallback: detached CLI fixer so router ticks don't deadlock on MCP stalls.
    if runtime_local and not _local_lms_slot_available(cfg, state):
        print(f"[router] local fixer for {lane} deferred; LMS local job cap reached")
        return state

    prof = _profile_for_role(cfg, "fixer", local=runtime_local, lane=lane)
    logs = ROUTER_ROOT / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    prune_log_dir(
        logs,
        keep_recent=ROUTER_LOG_KEEP_RECENT,
        max_total_bytes=ROUTER_LOG_MAX_TOTAL_BYTES,
        min_age_seconds=ROUTER_LOG_MIN_AGE_SECONDS,
    )
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    logp = logs / f"fixer__{lane}__{ts}.log"
    env = isolated_codex_env(repo_cwd) if runtime_local else None
    with logp.open("w") as lf:
        prompt_text = fixer_prompt(lane, branch, reviewer_packet, wt)
        prompt_path = logs / f"fixer__{lane}__{ts}.prompt.txt"
        write_text(prompt_path, prompt_text)
        cmd = [
            prof.codex_cmd,
            "exec",
            *prof.codex_args,
            *(["--ignore-user-config"] if not runtime_local else []),
            *(["--skip-git-repo-check"] if runtime_local else []),
            *(["-m", prof.model] if prof.model else []),
            *prof.model_args,
            *(["--add-dir", str(prompt_path.parent.resolve())] if runtime_local else []),
            "-s",
            "workspace-write",
            "-",
        ]
        proc = subprocess.Popen(
            cmd,
            cwd=(wt or repo_cwd),
            stdout=lf,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            text=True,
            env=env,
            start_new_session=True,
        )
        proc_stdin = getattr(proc, "stdin", None)
        if proc_stdin is not None:
            try:
                proc_stdin.write(_prompt_file_bootstrap(prompt_path))
                proc_stdin.close()
            except BrokenPipeError:
                pass
    fallback = state.get("fixer_fallback_jobs") or {}
    fallback[lane] = {
        "log": str(logp),
        "ts": ts,
        "pid": proc.pid,
        "local": runtime_local,
        "prompt_path": str(prompt_path),
    }
    state["fixer_fallback_jobs"] = fallback
    return state

def write_text(p: Path, t: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(t)

def archive(src: Path, lane_dir: Path) -> None:
    if not src.exists():
        return
    dst = lane_dir/"archive"/src.name
    try:
        src.rename(dst)
    except Exception:
        if not src.exists():
            return
        dst.write_text(src.read_text())
        src.unlink()


def archive_reviewer_notes(lane_dir: Path, keep: Optional[Path] = None) -> int:
    """Archive reviewer notes in inbox/reviewer, optionally preserving one file.

    Prevents unbounded reviewer note pileups during feature->review->fix loops.
    """
    moved = 0
    notes = sorted((lane_dir / "inbox/reviewer").glob("*.md"), key=lambda p: p.stat().st_mtime)
    comp_dir = lane_dir / "archive" / "reviewer_compacted"
    comp_dir.mkdir(parents=True, exist_ok=True)
    for note in notes:
        if keep is not None and note.name == keep.name:
            continue
        dst = comp_dir / note.name
        try:
            note.rename(dst)
        except Exception:
            if not note.exists():
                continue
            dst.write_text(note.read_text())
            note.unlink()
        moved += 1
    return moved

def _materialize_reviewer_packet(lane_dir: Path, reviewer_note: Optional[Path], fallback_feature_pkt: Optional[str] = None) -> str:
    note_text = ""
    if reviewer_note is not None:
        try:
            note_text = reviewer_note.read_text().strip()
        except Exception:
            note_text = ""
    invalid_note = False
    if note_text:
        lower = note_text.lower()
        # Recovery path: thread/session lookup failures are not actionable reviewer packets.
        if "session not found for thread_id" in lower or "thread not found" in lower:
            invalid_note = True
    if note_text and not invalid_note:
        compact_note = _extract_final_verdict_packet(note_text)
        if compact_note:
            return compact_note
        return note_text

    archived_feature = ""
    try:
        feats = sorted((lane_dir / "archive").glob("F__*.md"), key=lambda p: p.stat().st_mtime)
        if feats:
            archived_feature = feats[-1].read_text().strip()
    except Exception:
        archived_feature = ""

    pkt = fallback_feature_pkt.strip() if (fallback_feature_pkt or "").strip() else archived_feature
    if pkt:
        return (
            "Reviewer packet was empty (automation recovery path).\n"
            "Generate REQUIRED FIXES from the feature packet below and apply them.\n\n"
            f"{pkt}\n"
        )
    return (
        "Reviewer packet was empty and no archived feature packet was found.\n"
        "Run required gates, identify likely defects in this lane branch, and prepare for re-review."
    )

def _ensure_lane_reviewer_thread(
    reviewer_client: CodexMcpClient,
    cfg: RouterConfig,
    repo_cwd: str,
    lane: str,
    reviewer_thread_ids: Dict[str, str],
    *,
    local: bool,
) -> str:
    tid = reviewer_thread_ids.get(lane)
    if tid:
        return tid
    reviewer_profile = _profile_for_role(cfg, "reviewer", local=local, lane=lane)
    tid, _ = reviewer_client.codex(
        prompt=f"Ready as reviewer for lane {lane}; I won't modify files.",
        cwd=repo_cwd,
        sandbox="read-only",
        approval_policy="on-request",
        model=reviewer_profile.model,
        timeout=cfg.reviewer_timeout,
    )
    reviewer_thread_ids[lane] = tid
    return tid


def ensure_all_reviewer_threads(
    reviewer_client: CodexMcpClient,
    cfg: RouterConfig,
    repo_cwd: str,
    state: Dict[str, Any],
    reviewer_thread_ids: Dict[str, str],
) -> Dict[str, str]:
    local_mode = _runtime_mode(cfg, state) == "local_fallback"
    if local_mode or cfg.prefer_cli_reviewer:
        return reviewer_thread_ids
    for lane in cfg.lanes.keys():
        try:
            _ensure_lane_reviewer_thread(
                reviewer_client,
                cfg,
                repo_cwd,
                lane,
                reviewer_thread_ids,
                local=local_mode,
            )
        except Exception as exc:
            print(f"[router] reviewer bootstrap skipped for {lane}: {exc}")
    return reviewer_thread_ids


def process_once(
    reviewer_client: CodexMcpClient,
    integrator_client: CodexMcpClient,
    cfg: RouterConfig,
    state: dict,
    repo_cwd: str,
    reviewer_thread_ids: Dict[str, str],
    integrator_tid: str,
) -> Tuple[int, dict, Dict[str, str], str]:
    state = _maybe_restore_cloud(cfg, state, repo_cwd)
    cursor = load_json(CURSOR_FILE, {})
    reviewer_quota_retry_ts = state.get("reviewer_quota_retry_ts") or {}
    global_quota_retry_ts = float(state.get("reviewer_quota_global_retry_ts", 0) or 0)
    processed = 0
    for lane in cfg.lanes.keys():
        lane_dir = ensure_lane_dirs(lane)
        for pkt_path in list_new(lane_dir, cursor.get(lane)):
            if processed >= cfg.max_packets_per_run:
                state["reviewer_quota_retry_ts"] = reviewer_quota_retry_ts
                state["reviewer_quota_global_retry_ts"] = global_quota_retry_ts
                return processed, state, reviewer_thread_ids, integrator_tid
            pkt = pkt_path.read_text()

            reviewer_text = ""
            now = time.time()
            quota_retry_at = float(reviewer_quota_retry_ts.get(lane, 0) or 0)
            runtime_local = _runtime_mode(cfg, state) == "local_fallback"
            if runtime_local:
                ready, reviewer_text, state = _prepare_local_reviewer_result(
                    cfg,
                    state,
                    repo_cwd,
                    lane,
                    pkt_path,
                    pkt,
                )
                if not ready:
                    continue
            in_quota_cooldown = quota_retry_at > now or global_quota_retry_ts > now
            if runtime_local:
                pass
            elif in_quota_cooldown:
                wait_s = int(max(quota_retry_at, global_quota_retry_ts) - now)
                reason = (
                    f"reviewer quota cooldown active ({wait_s}s remaining)"
                )
                reviewer_text = _run_cli_reviewer(
                    cfg, repo_cwd, pkt, reason, lane=lane
                ) or _offline_reviewer_fallback(
                    pkt, reason
                )
            elif not runtime_local and cfg.prefer_cli_reviewer:
                reviewer_text = _run_cli_reviewer(
                    cfg,
                    repo_cwd,
                    pkt,
                    "cloud direct exec reviewer",
                    local=runtime_local,
                    lane=lane,
                ) or ""
                if not reviewer_text:
                    reviewer_text = _offline_reviewer_fallback(
                        pkt,
                        "reviewer direct exec failed/timed out",
                    )
            else:
                try:
                    reviewer_tid = _ensure_lane_reviewer_thread(
                        reviewer_client,
                        cfg,
                        repo_cwd,
                        lane,
                        reviewer_thread_ids,
                        local=runtime_local,
                    )
                    reviewer_tid, reviewer_text = reviewer_client.codex_reply(
                        reviewer_tid, reviewer_prompt(pkt), timeout=cfg.reviewer_timeout
                    )
                    reviewer_thread_ids[lane] = reviewer_tid
                except Exception as exc:
                    retry_until = time.time() + 900
                    reviewer_quota_retry_ts[lane] = retry_until
                    global_quota_retry_ts = max(global_quota_retry_ts, retry_until)
                    if cfg.auto_switch_to_local_on_quota:
                        state = _switch_to_local_fallback(cfg, state, f"reviewer call failed/timed out: {exc}", retry_until)
                        reviewer_text = _run_cli_reviewer(
                            cfg, repo_cwd, pkt, f"reviewer call failed/timed out: {exc}", lane=lane
                        ) or _offline_reviewer_fallback(pkt, f"reviewer call failed/timed out: {exc}")
            state = _apply_quota_text_safeguard(
                cfg,
                state,
                reviewer_text,
                reason=f"reviewer output quota text on lane {lane}",
            )
            if _invalid_reviewer_output(reviewer_text):
                # Recover from dead/invalid reviewer thread and retry once.
                if cfg.prefer_cli_reviewer:
                    reviewer_text = _run_cli_reviewer(
                        cfg,
                        repo_cwd,
                        pkt,
                        "reviewer output invalid/unavailable",
                        local=runtime_local,
                        lane=lane,
                    ) or _offline_reviewer_fallback(pkt, "reviewer output invalid/unavailable")
                else:
                    try:
                        reviewer_profile = _profile_for_role(cfg, "reviewer", local=runtime_local, lane=lane)
                        reviewer_tid, _ = reviewer_client.codex(
                            prompt=f"Ready as reviewer for lane {lane}; I won't modify files.",
                            cwd=repo_cwd,
                            sandbox="read-only",
                            approval_policy="on-request",
                            model=reviewer_profile.model,
                            timeout=cfg.reviewer_timeout,
                        )
                        reviewer_thread_ids[lane] = reviewer_tid
                        reviewer_tid, reviewer_text = reviewer_client.codex_reply(
                            reviewer_tid, reviewer_prompt(pkt), timeout=cfg.reviewer_timeout
                        )
                        reviewer_thread_ids[lane] = reviewer_tid
                    except Exception as exc:
                        retry_until = time.time() + 900
                        reviewer_quota_retry_ts[lane] = retry_until
                        global_quota_retry_ts = max(global_quota_retry_ts, retry_until)
                        if cfg.auto_switch_to_local_on_quota:
                            state = _switch_to_local_fallback(cfg, state, f"reviewer retry failed/timed out: {exc}", retry_until)
                        reviewer_text = _run_cli_reviewer(
                            cfg, repo_cwd, pkt, f"reviewer retry failed/timed out: {exc}", lane=lane
                        ) or _offline_reviewer_fallback(pkt, f"reviewer retry failed/timed out: {exc}")
                if _invalid_reviewer_output(reviewer_text):
                    reviewer_text = _run_cli_reviewer(
                        cfg, repo_cwd, pkt, "reviewer output invalid/unavailable", lane=lane
                    ) or _offline_reviewer_fallback(pkt, "reviewer output invalid/unavailable")
            elif _is_reviewer_quota_output(reviewer_text):
                retry_until = time.time() + 900
                reviewer_quota_retry_ts[lane] = retry_until
                global_quota_retry_ts = max(global_quota_retry_ts, retry_until)
                if cfg.auto_switch_to_local_on_quota:
                    state = _switch_to_local_fallback(cfg, state, "reviewer quota/rate-limit response", retry_until)
                reviewer_text = _run_cli_reviewer(
                    cfg, repo_cwd, pkt, "reviewer quota/rate-limit response", lane=lane
                ) or _offline_reviewer_fallback(pkt, "reviewer quota/rate-limit response")
            reviewer_text = _extract_final_verdict_packet(reviewer_text) or reviewer_text
            verdict = parse_verdict(reviewer_text)

            if verdict == "APPROVED":
                # Clear stale reviewer notes now that this lane packet is approved.
                archive_reviewer_notes(lane_dir)
                write_text(lane_dir/"outbox/integrator"/pkt_path.name.replace("F__","R__APPROVED__"), reviewer_text)
                integ = ""
                runtime_local = _runtime_mode(cfg, state) == "local_fallback"
                if runtime_local:
                    integ = ""
                elif not cfg.prefer_cli_integrator and integrator_tid:
                    try:
                        integrator_tid, integ = integrator_client.codex_reply(
                            integrator_tid, integrator_prompt(reviewer_text), timeout=cfg.integrator_timeout
                        )
                    except Exception as exc:
                        if cfg.auto_switch_to_local_on_quota and REVIEWER_QUOTA_RE.search(str(exc)):
                            state = _switch_to_local_fallback(cfg, state, f"integrator call failed/timed out: {exc}")
                            runtime_local = True
                        integ = _run_cli_integrator(cfg, repo_cwd, reviewer_text, local=runtime_local, lane=lane) or ""
                        if not integ:
                            write_text(
                                lane_dir / "archive" / f"INTEGRATOR__ERROR__{pkt_path.name}",
                                f"Integrator call failed/timed out: {exc}",
                            )
                else:
                    integ = _run_cli_integrator(
                        cfg,
                        repo_cwd,
                        reviewer_text,
                        local=runtime_local,
                        lane=lane,
                    )
                state = _apply_quota_text_safeguard(
                    cfg,
                    state,
                    integ or "",
                    reason=f"integrator output quota text on lane {lane}",
                )
                if integ and integ.strip():
                    write_text(lane_dir/"archive"/f"INTEGRATOR__{pkt_path.name}", integ)
            else:
                if not (reviewer_text or "").strip():
                    reviewer_text = (
                        "Verdict: `CHANGES_REQUESTED`\n\n"
                        "Reviewer output was empty; router inserted recovery packet.\n"
                        "Required fixes: derive issues from the feature packet and resubmit.\n\n"
                        f"{pkt}\n"
                    )
                outp = lane_dir/"inbox/reviewer"/pkt_path.name.replace("F__","R__CHANGES__")
                # Keep a single active reviewer note per lane; archive any older notes.
                archive_reviewer_notes(lane_dir)
                clear_stale_integrator_handoffs(lane_dir, pkt_path.name)
                write_text(outp, reviewer_text)

            cursor[lane] = pkt_path.name
            save_json(CURSOR_FILE, cursor)
            archive(pkt_path, lane_dir)
            processed += 1

            # Inline fixer can be expensive; disabled by default for automation ticks.
            if verdict != "APPROVED" and cfg.inline_fixer:
                state = run_fixer(
                    reviewer_client,
                    cfg,
                    state,
                    lane,
                    reviewer_text,
                    repo_cwd,
                    local_mode=runtime_local,
                )
    state["reviewer_quota_retry_ts"] = reviewer_quota_retry_ts
    state["reviewer_quota_global_retry_ts"] = global_quota_retry_ts
    return processed, state, reviewer_thread_ids, integrator_tid

def process_reviewer_backlog(
    reviewer_client: CodexMcpClient,
    cfg: RouterConfig,
    state: dict,
    repo_cwd: str,
) -> Tuple[int, dict]:
    """If inline fixer is enabled, kick feature fixers for reviewer backlog packets.

    This handles the "stuck in reviewer notes with no new feature packet" state.
    One kick per lane per newest reviewer packet filename.
    """
    if not cfg.inline_fixer or not cfg.kick_fixers_on_reviewer_backlog:
        return 0, state

    cursor = state.get("reviewer_fixer_cursor") or {}
    retry_ts = state.get("reviewer_fixer_retry_ts") or {}
    quota_retry_ts = state.get("fixer_quota_retry_ts") or {}
    local_mode = _runtime_mode(cfg, state) == "local_fallback"
    kick_limit = cfg.max_local_fixer_kicks_per_run if local_mode else cfg.max_cloud_fixer_kicks_per_run
    max_active = cfg.max_local_fixer_jobs if local_mode else cfg.max_cloud_fixer_jobs
    kicked = 0
    for lane in cfg.lanes.keys():
        if kick_limit > 0 and kicked >= kick_limit:
            break
        fallback_jobs = state.get("fixer_fallback_jobs") or {}
        if not isinstance(fallback_jobs, dict):
            fallback_jobs = {}
        if max_active > 0 and _count_active_pid_jobs(fallback_jobs, local=local_mode) >= max_active:
            break
        lane_dir = ensure_lane_dirs(lane)
        now = time.time()
        lane_quota_until = float(quota_retry_ts.get(lane, 0) or 0)
        if local_mode:
            quota_retry_ts.pop(lane, None)
        elif lane_quota_until > now:
            continue
        notes = sorted((lane_dir / "inbox/reviewer").glob("*.md"), key=lambda p: p.stat().st_mtime)
        if not notes:
            continue
        newest_note = notes[-1]
        try:
            note_text = newest_note.read_text(errors="ignore")
        except Exception:
            note_text = ""
        if parse_verdict(note_text) == "APPROVED":
            # Approved reviewer notes belong to the integrator path; they are
            # not feature-fixer work and should not consume the one-kick budget.
            continue
        feature_pkts = sorted((lane_dir / "inbox/feature").glob("*.md"), key=lambda p: p.stat().st_mtime)
        if feature_pkts:
            newest_feature = feature_pkts[-1]
            f_sha = _packet_sha(newest_feature.name)
            r_sha = _packet_sha(newest_note.name)
            stale_reemit = bool(
                (f_sha and r_sha and f_sha == r_sha)
                or (newest_feature.stat().st_mtime <= newest_note.stat().st_mtime)
            )
            if stale_reemit:
                # Recovery: stale re-emits can block fixers indefinitely. Archive and continue.
                archive(newest_feature, lane_dir)
            else:
                # Fresh feature packet exists; let reviewer flow handle it first.
                continue
        latest_log = None if local_mode else _latest_fixer_log(lane)
        if latest_log:
            try:
                text = latest_log.read_text(errors="ignore")
            except Exception:
                text = ""
            if _expired_explicit_quota_retry(text, now=now):
                quota_retry_ts.pop(lane, None)
            elif _has_real_quota_signal(text):
                retry_at = _quota_retry_epoch(
                    cfg,
                    text,
                    default_seconds=cfg.fixer_quota_retry_cooldown_seconds,
                )
                quota_retry_ts[lane] = retry_at
                if cfg.auto_switch_to_local_on_quota:
                    state = _apply_quota_text_safeguard(
                        cfg,
                        state,
                        text,
                        reason=f"fixer log quota text on lane {lane}",
                        default_seconds=cfg.fixer_quota_retry_cooldown_seconds,
                    )
                continue
        branch = str((cfg.lanes.get(lane, {}) or {}).get("branch") or f"codex/{lane}")
        head_sha = _branch_head_sha(repo_cwd, branch)
        last_submitted_sha = infer_last_submitted_sha(lane_dir)
        if head_sha and last_submitted_sha and head_sha != last_submitted_sha.lower():
            print(f"[router] {lane}: branch advanced past reviewer note; waiting for planner re-emit instead of kicking fixer")
            continue
        if cursor.get(lane) == newest_note.name:
            last_kick = float(retry_ts.get(lane, 0) or 0)
            # Backward compatibility: if timestamp missing, allow one immediate retry.
            if last_kick > 0 and (now - last_kick) < cfg.reviewer_fixer_retry_cooldown_seconds:
                continue
        state = _maybe_restore_cloud(cfg, state, repo_cwd)
        reviewer_packet = _materialize_reviewer_packet(lane_dir, newest_note)
        state = run_fixer(
            reviewer_client,
            cfg,
            state,
            lane,
            reviewer_packet,
            repo_cwd,
            local_mode=local_mode,
        )
        cursor[lane] = newest_note.name
        retry_ts[lane] = now
        kicked += 1

    state["reviewer_fixer_cursor"] = cursor
    state["reviewer_fixer_retry_ts"] = retry_ts
    state["fixer_quota_retry_ts"] = quota_retry_ts
    return kicked, state


def process_integrator_backlog(
    integrator_client: CodexMcpClient,
    cfg: RouterConfig,
    state: dict,
    repo_cwd: str,
    integrator_tid: str,
) -> Tuple[int, dict, str]:
    state = _maybe_restore_cloud(cfg, state, repo_cwd)
    processed = 0
    approvals: List[Tuple[float, str, Path, Path]] = []
    for lane in cfg.lanes.keys():
        lane_dir = ensure_lane_dirs(lane)
        for pkt in (lane_dir / "outbox/integrator").glob("*.md"):
            approvals.append((pkt.stat().st_mtime, lane, lane_dir, pkt))
    approvals.sort(key=lambda item: item[0])

    for _, _lane, lane_dir, pkt in approvals:
        if processed >= cfg.max_packets_per_run:
            break
        approved_text = pkt.read_text()
        archive_hint = list((lane_dir / "archive").glob(f"INTEGRATOR__*{_packet_sha(pkt.name)}*.md"))
        if archive_hint:
            archive(pkt, lane_dir)
            processed += 1
            continue
        runtime_local = _runtime_mode(cfg, state) == "local_fallback"
        if runtime_local:
            ready, integ, state = _prepare_cli_integrator_result(
                cfg,
                state,
                repo_cwd,
                _lane,
                pkt,
                approved_text,
                local=True,
            )
            if not ready:
                continue
        elif cfg.prefer_cli_integrator or not integrator_tid:
            ready, integ, state = _prepare_cli_integrator_result(
                cfg,
                state,
                repo_cwd,
                _lane,
                pkt,
                approved_text,
                local=False,
            )
            if not ready:
                continue
        else:
            try:
                integrator_tid, integ = integrator_client.codex_reply(
                    integrator_tid, integrator_prompt(approved_text), timeout=cfg.integrator_timeout
                )
            except Exception as exc:
                runtime_local = _runtime_mode(cfg, state) == "local_fallback"
                if cfg.auto_switch_to_local_on_quota and REVIEWER_QUOTA_RE.search(str(exc)):
                    state = _switch_to_local_fallback(cfg, state, f"integrator backlog call failed/timed out: {exc}")
                    runtime_local = True
                integ = _run_cli_integrator(cfg, repo_cwd, approved_text, local=runtime_local, lane=_lane)
        state = _apply_quota_text_safeguard(
            cfg,
            state,
            integ or "",
            reason=f"integrator output quota text on approval packet {pkt.name}",
        )
        if integ and integ.strip():
            write_text(lane_dir / "archive" / f"INTEGRATOR__{pkt.name}", integ)
            archive(pkt, lane_dir)
            processed += 1
    return processed, state, integrator_tid


def _process_router_tick(
    reviewer_client: CodexMcpClient,
    integrator_client: CodexMcpClient,
    cfg: RouterConfig,
    state: dict,
    repo_cwd: str,
    reviewer_thread_ids: dict,
    integrator_tid: str,
) -> Tuple[int, int, int, dict, dict, str]:
    """Run one router cycle with deterministic scarce-worker priority.

    Ordering matters in local fallback mode where all roles share the same LMS
    worker cap: approvals unblock integration, fixers unblock reviewer notes,
    and speculative feature refill is handled by the coordinator after router
    work. Keep the precedence explicit here so fixers cannot steal the last
    slot from an integrator backlog.
    """
    n, state, reviewer_thread_ids, integrator_tid = process_once(
        reviewer_client, integrator_client, cfg, state, repo_cwd, reviewer_thread_ids, integrator_tid
    )
    integrated, state, integrator_tid = process_integrator_backlog(
        integrator_client, cfg, state, repo_cwd, integrator_tid
    )
    kicked, state = process_reviewer_backlog(reviewer_client, cfg, state, repo_cwd)
    state["reviewer_thread_ids"] = reviewer_thread_ids
    state["reviewer_thread_missing_lanes"] = [
        lane for lane in cfg.lanes.keys() if lane not in reviewer_thread_ids
    ]
    if reviewer_thread_ids:
        first_lane = sorted(reviewer_thread_ids.keys())[0]
        state["reviewer_thread_id"] = reviewer_thread_ids.get(first_lane)
    else:
        state["reviewer_thread_id"] = None
    state["integrator_thread_id"] = integrator_tid
    save_json(STATE_FILE, state)
    return n, kicked, integrated, state, reviewer_thread_ids, integrator_tid


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--daemon", action="store_true")
    args = ap.parse_args()

    cfg = load_cfg()
    state = load_json(STATE_FILE, {})
    repo_cwd = str(Path.cwd())
    state = _maybe_restore_cloud(cfg, state, repo_cwd)
    local_mode = _runtime_mode(cfg, state) == "local_fallback"

    reviewer_client = _build_mcp_client(_profile_for_role(cfg, "reviewer", local=local_mode), ApprovalPolicy(True, True))
    integrator_client = _build_mcp_client(_profile_for_role(cfg, "integrator", local=local_mode), ApprovalPolicy(True, True))

    reviewer_thread_ids = state.get("reviewer_thread_ids") or {}
    if not isinstance(reviewer_thread_ids, dict):
        reviewer_thread_ids = {}
    reviewer_thread_ids = ensure_all_reviewer_threads(reviewer_client, cfg, repo_cwd, state, reviewer_thread_ids)
    integrator_tid = state.get("integrator_thread_id")

    if (
        not integrator_tid
        and _runtime_mode(cfg, state) != "local_fallback"
        and not cfg.prefer_cli_integrator
    ):
        integrator_profile = _profile_for_role(cfg, "integrator", local=False)
        integrator_tid, _ = integrator_client.codex(
            prompt="Ready as integrator.",
            cwd=repo_cwd,
            sandbox="workspace-write",
            approval_policy="on-request",
            model=integrator_profile.model,
            timeout=cfg.integrator_timeout,
        )

    state["reviewer_thread_ids"] = reviewer_thread_ids
    state["reviewer_thread_missing_lanes"] = [
        lane for lane in cfg.lanes.keys() if lane not in reviewer_thread_ids
    ]
    if reviewer_thread_ids:
        # Backward-compatible status field.
        first_lane = sorted(reviewer_thread_ids.keys())[0]
        state["reviewer_thread_id"] = reviewer_thread_ids.get(first_lane)
    else:
        state["reviewer_thread_id"] = None
    state["integrator_thread_id"] = integrator_tid
    save_json(STATE_FILE, state)

    for lane in cfg.lanes.keys():
        ensure_lane_dirs(lane)

    try:
        if not args.daemon:
            if acquire_lease():
                try:
                    n, kicked, integrated, state, reviewer_thread_ids, integrator_tid = _process_router_tick(
                        reviewer_client,
                        integrator_client,
                        cfg,
                        state,
                        repo_cwd,
                        reviewer_thread_ids,
                        integrator_tid,
                    )
                    print(f"[router] processed {n} packet(s), kicked {kicked} reviewer-fixer task(s), integrated {integrated} approval packet(s)")
                finally:
                    release_lease()
            return

        print("[router] daemon mode")
        while True:
            if acquire_lease():
                try:
                    n, kicked, integrated, state, reviewer_thread_ids, integrator_tid = _process_router_tick(
                        reviewer_client,
                        integrator_client,
                        cfg,
                        state,
                        repo_cwd,
                        reviewer_thread_ids,
                        integrator_tid,
                    )
                    if n or kicked or integrated:
                        print(f"[router] processed {n} packet(s), kicked {kicked} reviewer-fixer task(s), integrated {integrated} approval packet(s)")
                finally:
                    release_lease()
            time.sleep(0.5)
    finally:
        reviewer_client.close()
        if integrator_client is not reviewer_client:
            integrator_client.close()

if __name__ == "__main__":
    main()
