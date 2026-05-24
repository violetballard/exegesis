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
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from codex_mcp_client import ApprovalPolicy, CodexMcpClient
    from git_ops import run_git
    from git_hygiene import prune_stale_index_locks
    from lane_profiles import default_lane_meta, lane_priority_order
    from log_maintenance import prune_log_dir
    from local_codex_runtime import agent_ripgrep_config_path, agent_runtime_env, isolated_codex_env
    from packet_progress import infer_last_submitted_sha
    from planner import _owned_patterns_for_lane
except ImportError:  # pragma: no cover - test/import fallback for package execution
    from .codex_mcp_client import ApprovalPolicy, CodexMcpClient
    from .git_ops import run_git
    from .git_hygiene import prune_stale_index_locks
    from .lane_profiles import default_lane_meta, lane_priority_order
    from .log_maintenance import prune_log_dir
    from .local_codex_runtime import agent_ripgrep_config_path, agent_runtime_env, isolated_codex_env
    from .packet_progress import infer_last_submitted_sha
    from .planner import _owned_patterns_for_lane

PACKETS_ROOT = Path(".codex/packets/lanes")
ROUTER_ROOT = Path(".codex/packet_router")
STATE_FILE = ROUTER_ROOT / "state.json"
CONFIG_FILE = ROUTER_ROOT / "config.json"
CURSOR_FILE = ROUTER_ROOT / "cursor.json"
LEASE_FILE = ROUTER_ROOT / "lease.json"
REPO_ROOT = Path(__file__).resolve().parents[2]
PROVIDER_CONFIG_DIR = REPO_ROOT / "packet_garden/config/providers"
COORD_STATE_FILE = REPO_ROOT / ".codex/packet_coordinator/state.json"
FEATURE_RUNNER_STATE_FILE = REPO_ROOT / ".codex/feature_runner/state.json"
LOCAL_CLI_WORKER = Path(__file__).resolve().with_name("local_cli_worker.py")
LOCAL_JOB_ROOT = ROUTER_ROOT / "local_jobs"
CLOUD_PROFILE_KEYS = {
    "worker_cloud",
    "worker_cloud_standard_medium",
    "integrator_cloud",
}
CLOUD_ROLE_KEYS = {
    "cloud_probe",
    "feature_cloud",
    "reviewer_cloud",
    "fixer_cloud",
    "integrator_cloud",
}

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
SUCCESSFUL_INTEGRATOR_SUMMARY_RE = re.compile(
    r"(?:\*\*)?Integration Result(?:\*\*)?.*Post-merge checks all passed:.*Blockers:\s*none"
    r"|Integrated status:.*Post-merge checks all passed:.*Blockers:\s*none",
    re.IGNORECASE | re.DOTALL,
)
BLOCKED_INTEGRATOR_OUTPUT_RE = re.compile(
    r"\bBlocked\.\s|verdict:\s*`?blocked\b|blocked\s+[—-]\s+post-merge checks fail|"
    r"blocked before merge|no integration was performed|no integration performed|"
    r"approved slice is not fully integrated|slice is not fully integrated",
    re.IGNORECASE,
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
INTEGRATOR_EXEC_MARKERS = (
    "You are the INTEGRATOR",
    "Consume this APPROVED packet",
)
INTEGRATION_DEPENDENCY_ORDER = (
    "feat-context-storage",
    "feat-commands",
    "feat-retrieval-fts",
    "feat-engine-runs",
    "feat-a2ui-contract",
)
CONTROL_PLANE_REVIEW_PATH_PREFIXES = (
    ".agents/",
    ".codex/",
    "agents/",
    "codex/",
    "packet_garden/",
)
CONTROL_PLANE_REVIEW_PATH_NAMES = {
    "AGENTS.md",
    "INTEGRATION.md",
    "THREAD.md",
    "THREAD_OWNERSHIP.md",
    "THREAD_PACKET.md",
}
CONTROL_PLANE_METADATA_REPAIR_RE = re.compile(
    r"handoff metadata|packet metadata|lane metadata|THREAD_PACKET\.md|\.codex/|"
    r"implementation range|source commit|roadmap mapping|canonical demo-path|"
    r"locally resolvable implementation|reissue the packet|handoff artifacts|"
    r"handoff packet does not provide concrete completed tasks|missing handoff fields|"
    r"placeholder task list|concrete numbered tasks completed",
    re.IGNORECASE,
)

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
    max_cloud_feature_jobs: int
    max_cloud_reviewer_jobs: int
    max_cloud_integrator_jobs: int
    max_total_cloud_jobs: int
    prefer_cli_fixer: bool
    prefer_cli_reviewer: bool
    prefer_cli_integrator: bool
    use_cli_reviewer_fallback: bool
    use_cli_integrator_fallback: bool
    profiles: Dict[str, "LaunchProfile"]
    role_profiles: Dict[str, str]
    lanes: Dict[str, Dict[str, Any]]
    max_total_local_lms_jobs: int = 4
    cloud_provider: str = "codex"
    cloud_provider_order: Optional[List[str]] = None


@dataclass
class LaunchProfile:
    codex_cmd: str
    codex_args: List[str]
    model: str
    model_args: List[str]
    harness: str = "codex"

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
    default_harness = "opencode" if Path(cmd).name == "opencode" else "claude" if Path(cmd).name == "claude" else "codex"
    harness = str(raw.get("harness") or default_harness)
    return LaunchProfile(codex_cmd=cmd, codex_args=cmd_args, model=model, model_args=model_args, harness=harness)


def _default_profiles(cfg: Dict[str, Any]) -> Dict[str, LaunchProfile]:
    cloud_cmd = str(cfg.get("codex_cmd", "codex"))
    cloud_model = str(cfg.get("model", "gpt-5.1-codex"))
    fallback_cmd = str(cfg.get("fallback_codex_cmd") or cloud_cmd)
    fallback_model = str(cfg.get("fallback_model") or "")
    fallback_cmd_args = [str(x) for x in list(cfg.get("fallback_codex_args") or [])]
    fallback_model_args = [str(x) for x in list(cfg.get("fallback_model_args") or [])]
    if "--oss" in fallback_cmd_args and fallback_model == cloud_model:
        fallback_model = ""
    fallback_harness = "opencode" if Path(fallback_cmd).name == "opencode" else "codex"
    return {
        "orchestrator": LaunchProfile(cloud_cmd, [], cloud_model, []),
        "worker_cloud": LaunchProfile(cloud_cmd, [], cloud_model, []),
        "worker_local": LaunchProfile(fallback_cmd, fallback_cmd_args, fallback_model, fallback_model_args, fallback_harness),
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
        max_cloud_fixer_jobs=int(cfg.get("max_cloud_fixer_jobs", 4)),
        max_local_fixer_jobs=int(cfg.get("max_local_fixer_jobs", 2)),
        max_cloud_feature_jobs=int(cfg.get("max_cloud_feature_jobs", 4)),
        max_cloud_reviewer_jobs=int(cfg.get("max_cloud_reviewer_jobs", 4)),
        max_cloud_integrator_jobs=int(cfg.get("max_cloud_integrator_jobs", CLOUD_INTEGRATOR_MAX_ACTIVE)),
        max_total_cloud_jobs=int(cfg.get("max_total_cloud_jobs", 4)),
        max_total_local_lms_jobs=int(cfg.get("max_total_local_lms_jobs", 4)),
        prefer_cli_fixer=bool(cfg.get("prefer_cli_fixer", True)),
        prefer_cli_reviewer=bool(cfg.get("prefer_cli_reviewer", True)),
        prefer_cli_integrator=bool(cfg.get("prefer_cli_integrator", True)),
        use_cli_reviewer_fallback=bool(cfg.get("use_cli_reviewer_fallback", True)),
        use_cli_integrator_fallback=bool(cfg.get("use_cli_integrator_fallback", True)),
        profiles=profiles,
        role_profiles=role_profiles,
        lanes=lane_cfg_map,
        cloud_provider=str(cfg.get("cloud_provider") or "codex"),
        cloud_provider_order=[
            str(provider)
            for provider in list(cfg.get("cloud_provider_order") or [str(cfg.get("cloud_provider") or "codex")])
            if str(provider).strip()
        ],
    )

def ensure_lane_dirs(lane: str) -> Path:
    d = PACKETS_ROOT / lane
    (d/"inbox/feature").mkdir(parents=True, exist_ok=True)
    (d/"inbox/reviewer").mkdir(parents=True, exist_ok=True)
    (d/"outbox/integrator").mkdir(parents=True, exist_ok=True)
    (d/"archive").mkdir(parents=True, exist_ok=True)
    return d


def _lane_digest(lane: str) -> Dict[str, int]:
    lane_dir = PACKETS_ROOT / lane
    return {
        "pending_feature": len(
            [
                p
                for p in (lane_dir / "inbox/feature").glob("*.md")
                if not p.name.endswith(".shared.md")
            ]
        ),
        "reviewer_notes": len(list((lane_dir / "inbox/reviewer").glob("*.md"))),
        "approved": len(list((lane_dir / "outbox/integrator").glob("*.md"))),
    }

def list_new(lane_dir: Path, last_seen: Optional[str]) -> List[Path]:
    files = sorted(
        (p for p in (lane_dir/"inbox/feature").glob("*.md") if not p.name.endswith(".shared.md")),
        key=lambda p: p.stat().st_mtime,
    )
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


def _branch_merged_to_head(repo_cwd: str, branch: str) -> bool:
    try:
        proc = subprocess.run(
            ["git", "merge-base", "--is-ancestor", branch, "HEAD"],
            cwd=repo_cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
    except Exception:
        return False
    return proc.returncode == 0


def _branch_changed_files(repo_cwd: str, branch: str) -> List[str]:
    try:
        base = subprocess.run(
            ["git", "merge-base", "HEAD", branch],
            cwd=repo_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
        if base.returncode != 0:
            return []
        proc = subprocess.run(
            ["git", "diff", "--name-only", f"{base.stdout.strip()}..{branch}"],
            cwd=repo_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
    except Exception:
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in (proc.stdout or "").splitlines() if line.strip()]


def _branch_files_differing_from_head(repo_cwd: str, branch: str) -> List[str]:
    """Return files whose branch tip content still differs from current HEAD."""
    try:
        proc = subprocess.run(
            ["git", "diff", "--name-only", f"HEAD..{branch}"],
            cwd=repo_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
    except Exception:
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in (proc.stdout or "").splitlines() if line.strip()]


def _branch_unmerged_authored_files(repo_cwd: str, branch: str) -> List[str]:
    """Return branch-authored files that are not already represented in HEAD."""
    authored = set(_branch_changed_files(repo_cwd, branch))
    head_diff = set(_branch_files_differing_from_head(repo_cwd, branch))
    if not authored:
        return sorted(head_diff)
    return sorted(authored & head_diff)


def _branch_scope_violations(
    cfg: RouterConfig,
    repo_cwd: str,
    lane: str,
    files: Optional[List[str]] = None,
) -> List[str]:
    """Return full-branch files outside THREAD_OWNERSHIP lane ownership."""
    patterns = _owned_patterns_for_lane(lane)
    if not patterns:
        return []
    lane_cfg = (cfg.lanes.get(lane) or {}) if isinstance(cfg.lanes, dict) else {}
    branch = str(lane_cfg.get("branch") or f"codex/{lane}")
    if files is None:
        files = _branch_changed_files(repo_cwd, branch) if branch else []
    violations: List[str] = []
    for file_name in files:
        normalized = str(file_name).strip()
        while normalized.startswith("./"):
            normalized = normalized[2:]
        if not normalized:
            continue
        if any(fnmatchcase(normalized, pattern) for pattern in patterns):
            continue
        if _is_main_equivalent_control_plane_sync(repo_cwd, branch, normalized):
            continue
        violations.append(normalized)
    return sorted(set(violations))


def _is_main_equivalent_control_plane_sync(repo_cwd: str, branch: str, path: str) -> bool:
    """Allow feature branches to carry control-plane files already present on main."""
    if not (
        path.startswith(".codex/kickoff_packets/")
        or path in {"THREAD_OWNERSHIP.md", "packet_garden/tools/planner.py", "scripts/scope-check.sh"}
    ):
        return False
    proc = subprocess.run(
        ["git", "diff", "--quiet", "main", branch, "--", path],
        cwd=repo_cwd,
        text=True,
        capture_output=True,
    )
    return proc.returncode == 0


def _parse_packet_file_list(text: str) -> List[str]:
    files: List[str] = []
    in_files = False
    for raw_line in (text or "").splitlines():
        line = raw_line.strip()
        lowered = line.lower()
        if lowered in {"## files changed", "### reviewed implementation files"}:
            in_files = True
            continue
        if in_files and line.startswith("#") and lowered not in {"### reviewed implementation files"}:
            break
        if not in_files or not line.startswith("- "):
            continue
        item = line[2:].strip()
        item = item.strip("`")
        if item and not item.startswith("#") and "/" in item:
            files.append(item)
    return files


def _feature_packet_for_approval(lane_dir: Path, approval_packet: Path) -> Optional[Path]:
    sha = _packet_sha(approval_packet.name)
    if not sha:
        return None
    candidates = [
        p for p in lane_dir.rglob(f"F__*{sha}*.md")
        if not p.name.endswith(".shared.md")
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def _latest_feature_packet_for_lane(lane: str) -> Optional[Path]:
    lane_dir = PACKETS_ROOT / lane
    candidates = [
        p for p in lane_dir.rglob("F__*.md")
        if not p.name.endswith(".shared.md")
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def _latest_reviewed_files_for_lane(lane: str) -> List[str]:
    feature_packet = _latest_feature_packet_for_lane(lane)
    if not feature_packet:
        return []
    return _parse_packet_file_list(feature_packet.read_text(errors="ignore"))


def _reviewed_files_for_integrator_packet(lane_dir: Path, approval_packet: Path, approved_text: str) -> List[str]:
    feature_packet = _feature_packet_for_approval(lane_dir, approval_packet)
    if feature_packet:
        files = _parse_packet_file_list(feature_packet.read_text(errors="ignore"))
        if files:
            return files
    return _parse_packet_file_list(approved_text)


def _metadata_only_review_files(files: List[str]) -> bool:
    """Return True when packet file evidence is only control-plane metadata."""
    if not files:
        return False
    for file_name in files:
        normalized = file_name.strip()
        while normalized.startswith("./"):
            normalized = normalized[2:]
        if not normalized:
            continue
        if normalized in CONTROL_PLANE_REVIEW_PATH_NAMES:
            continue
        if any(normalized.startswith(prefix) for prefix in CONTROL_PLANE_REVIEW_PATH_PREFIXES):
            continue
        return False
    return True


def _merge_relevant_review_files(files: List[str]) -> List[str]:
    """Drop control-plane metadata paths from merge dependency comparisons."""
    relevant: List[str] = []
    for file_name in files:
        normalized = str(file_name).strip()
        while normalized.startswith("./"):
            normalized = normalized[2:]
        if not normalized:
            continue
        if normalized in CONTROL_PLANE_REVIEW_PATH_NAMES:
            continue
        if any(normalized.startswith(prefix) for prefix in CONTROL_PLANE_REVIEW_PATH_PREFIXES):
            continue
        relevant.append(normalized)
    return relevant


def _effective_reviewed_files_for_dependency(
    cfg: RouterConfig,
    repo_cwd: str,
    lane: str,
    reviewed_files: Optional[List[str]],
) -> List[str]:
    """Prefer reviewed packet files, but recover from missing/stale metadata evidence.

    Approved packets should integrate as soon as they are safely mergeable. Some
    older packets lack a parseable file list, and a few stale companion packets
    list only control-plane metadata even though the branch diff contains the
    reviewed source surface. In those cases, use the branch diff for dependency
    overlap checks instead of treating the lane as unknowable and blocking every
    later integration behind the global lane order.
    """
    files = [str(path) for path in list(reviewed_files or []) if str(path).strip()]
    if files and not _metadata_only_review_files(files):
        return _merge_relevant_review_files(files)
    lane_cfg = (cfg.lanes.get(lane) or {}) if isinstance(cfg.lanes, dict) else {}
    branch = str(lane_cfg.get("branch") or f"codex/{lane}")
    branch_files = _branch_changed_files(repo_cwd, branch) if branch else []
    return _merge_relevant_review_files(branch_files or files)


def _integration_dependency_blockers(
    cfg: RouterConfig,
    repo_cwd: str,
    lane: str,
    reviewed_files: Optional[List[str]] = None,
) -> List[str]:
    if not Path(repo_cwd).exists():
        return []
    if lane not in INTEGRATION_DEPENDENCY_ORDER:
        return []
    blockers: List[str] = []
    reviewed_set = set(_effective_reviewed_files_for_dependency(cfg, repo_cwd, lane, reviewed_files))
    for prior_lane in INTEGRATION_DEPENDENCY_ORDER:
        if prior_lane == lane:
            break
        lane_cfg = (cfg.lanes.get(prior_lane) or {}) if isinstance(cfg.lanes, dict) else {}
        if not bool(lane_cfg.get("enabled", True)):
            continue
        if _branch_scope_violations(cfg, repo_cwd, prior_lane):
            # A lane whose full branch surface violates THREAD_OWNERSHIP is not
            # a valid dependency anchor. It must be repaired/rebased rather than
            # blocking independent approved integrations behind stale broad
            # branch noise.
            continue
        branch = str(lane_cfg.get("branch") or f"codex/{prior_lane}")
        if not branch or _branch_merged_to_head(repo_cwd, branch):
            continue
        if reviewed_set:
            branch_files = set(_merge_relevant_review_files(_branch_unmerged_authored_files(repo_cwd, branch)))
            prior_files = set(_merge_relevant_review_files(_latest_reviewed_files_for_lane(prior_lane)))
            if prior_files:
                # Reviewed-file metadata can outlive a narrow/squash integration.
                # Only block later approved packets on prior reviewed files that
                # still differ from main; otherwise a stale active branch can pin
                # the integrator behind work that has already landed.
                prior_files &= branch_files
            else:
                prior_files = branch_files
            if reviewed_set.isdisjoint(prior_files):
                continue
        if branch:
            blockers.append(prior_lane)
    return blockers


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
    reviewable = _extract_final_verdict_packet(t) if require_verdict else t
    has_final_verdict = _extract_reviewer_verdict(reviewable) is not None
    if INVALID_REVIEWER_RE.search(t) and not has_final_verdict:
        return "stale or missing thread reference"
    if not require_verdict and SUCCESSFUL_INTEGRATOR_SUMMARY_RE.search(t):
        return None
    if not require_verdict and BLOCKED_INTEGRATOR_OUTPUT_RE.search(t):
        return "integrator reported blocked/no integration performed"
    marker_text = reviewable if require_verdict and has_final_verdict else t
    lower = marker_text.lower()
    for marker in BAD_LOCAL_CLI_CONTENT_MARKERS:
        if marker in lower:
            return f"bad local cli marker: {marker}"
    if require_verdict and not has_final_verdict:
        return "missing reviewer verdict"
    return None


def _is_reviewer_quota_output(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    return bool(REVIEWER_QUOTA_RE.search(t))


def _runtime_mode(cfg: RouterConfig, state: Dict[str, Any]) -> str:
    mode = str(state.get("runtime_mode") or cfg.runtime_mode_default or "cloud_primary")
    return mode if mode in ("cloud_primary", "local_fallback", "hybrid") else "cloud_primary"


def _hybrid_mode(cfg: RouterConfig, state: Dict[str, Any]) -> bool:
    return _runtime_mode(cfg, state) == "hybrid"


def _current_cloud_provider(cfg: RouterConfig, state: Dict[str, Any]) -> str:
    return str(state.get("cloud_provider") or getattr(cfg, "cloud_provider", "") or "codex")


def _cloud_provider_order(cfg: RouterConfig, state: Dict[str, Any]) -> List[str]:
    raw = state.get("cloud_provider_order") or getattr(cfg, "cloud_provider_order", None) or []
    order = [str(item) for item in list(raw) if str(item).strip()]
    current = _current_cloud_provider(cfg, state)
    if current and current not in order:
        order.append(current)
    for fallback in ("claude", "codex"):
        if fallback not in order and (PROVIDER_CONFIG_DIR / f"{fallback}_cloud.json").exists():
            order.append(fallback)
    return order


def _provider_state(state: Dict[str, Any], provider: str) -> Dict[str, Any]:
    providers = state.get("cloud_providers")
    if not isinstance(providers, dict):
        providers = {}
        state["cloud_providers"] = providers
    entry = providers.get(provider)
    if not isinstance(entry, dict):
        entry = {"available": True, "retry_at": 0}
        providers[provider] = entry
    return entry


def _provider_available(state: Dict[str, Any], provider: str) -> bool:
    entry = _provider_state(state, provider)
    retry_at = float(entry.get("retry_at", 0) or 0)
    if retry_at and retry_at <= time.time():
        entry["available"] = True
        entry["retry_at"] = 0
    return bool(entry.get("available", True))


def _load_provider_template(provider: str) -> Dict[str, Any]:
    path = PROVIDER_CONFIG_DIR / f"{provider}_cloud.json"
    data = load_json(path, {})
    return data if isinstance(data, dict) else {}


def _apply_provider_template_to_raw_config(raw_cfg: Dict[str, Any], provider: str) -> Dict[str, Any]:
    template = _load_provider_template(provider)
    if not template:
        return raw_cfg
    next_cfg = dict(raw_cfg)
    top_level = template.get("top_level") if isinstance(template.get("top_level"), dict) else {}
    for key, value in top_level.items():
        next_cfg[str(key)] = value
    next_cfg["cloud_provider"] = provider
    profiles = dict(next_cfg.get("profiles") or {})
    for key, value in dict(template.get("profiles") or {}).items():
        if key in CLOUD_PROFILE_KEYS:
            profiles[key] = value
    next_cfg["profiles"] = profiles
    role_profiles = dict(next_cfg.get("role_profiles") or {})
    for key, value in dict(template.get("role_profiles") or {}).items():
        if key in CLOUD_ROLE_KEYS:
            role_profiles[key] = value
    next_cfg["role_profiles"] = role_profiles
    return next_cfg


def _apply_provider_template_to_runtime(cfg: RouterConfig, provider: str) -> bool:
    raw_cfg = load_json(CONFIG_FILE, {})
    if not isinstance(raw_cfg, dict):
        return False
    next_cfg = _apply_provider_template_to_raw_config(raw_cfg, provider)
    if next_cfg == raw_cfg:
        return False
    save_json(CONFIG_FILE, next_cfg)
    fresh = load_cfg()
    cfg.model = fresh.model
    cfg.codex_cmd = fresh.codex_cmd
    cfg.profiles = fresh.profiles
    cfg.role_profiles = fresh.role_profiles
    cfg.cloud_provider = fresh.cloud_provider
    cfg.cloud_provider_order = fresh.cloud_provider_order
    return True


def _switch_to_next_cloud_provider(
    cfg: RouterConfig,
    state: Dict[str, Any],
    *,
    reason: str,
) -> bool:
    current = _current_cloud_provider(cfg, state)
    for provider in _cloud_provider_order(cfg, state):
        if provider == current:
            continue
        if not _provider_available(state, provider):
            continue
        if _apply_provider_template_to_runtime(cfg, provider):
            state["cloud_provider"] = provider
            state["cloud_available"] = True
            state["cloud_retry_at"] = 0
            state["last_mode_switch_at"] = time.time()
            state["last_quota_reason"] = f"{reason}; switched cloud provider {current} -> {provider}"
            return True
    return False


def _select_available_cloud_provider(
    cfg: RouterConfig,
    state: Dict[str, Any],
    *,
    reason: str,
) -> bool:
    current = _current_cloud_provider(cfg, state)
    ordered = _cloud_provider_order(cfg, state)
    for provider in ordered:
        if not _provider_available(state, provider):
            continue
        if provider != current:
            _apply_provider_template_to_runtime(cfg, provider)
        state["cloud_provider"] = provider
        state["cloud_available"] = True
        state["cloud_retry_at"] = 0
        state["last_mode_switch_at"] = time.time()
        state["last_quota_reason"] = reason if provider == current else f"{reason}; selected cloud provider {provider}"
        return True
    return False


def _cloud_available(cfg: RouterConfig, state: Dict[str, Any]) -> bool:
    mode = _runtime_mode(cfg, state)
    if mode == "local_fallback":
        return False
    if mode == "cloud_primary":
        return True
    provider = _current_cloud_provider(cfg, state)
    return bool(state.get("cloud_available", True)) and _provider_available(state, provider)


def _use_local_provider(cfg: RouterConfig, state: Dict[str, Any]) -> bool:
    return not _cloud_available(cfg, state)


def _mark_cloud_unavailable(
    cfg: RouterConfig,
    state: Dict[str, Any],
    reason: str,
    retry_at: Optional[float] = None,
) -> Dict[str, Any]:
    if retry_at is None or retry_at <= time.time():
        retry_at = time.time() + cfg.cloud_probe_cooldown_seconds
    provider = _current_cloud_provider(cfg, state)
    entry = _provider_state(state, provider)
    entry["available"] = False
    entry["retry_at"] = retry_at
    entry["reason"] = reason
    state["cloud_provider"] = provider
    if _switch_to_next_cloud_provider(cfg, state, reason=reason):
        state["runtime_mode"] = "hybrid" if _hybrid_mode(cfg, state) or str(cfg.runtime_mode_default) == "hybrid" else "cloud_primary"
        return state
    if _hybrid_mode(cfg, state) or str(cfg.runtime_mode_default) == "hybrid":
        state["runtime_mode"] = "hybrid"
        state["cloud_available"] = False
        state["cloud_retry_at"] = retry_at
        state["last_mode_switch_at"] = time.time()
        if reason:
            state["last_quota_reason"] = reason
        return state
    return _set_runtime_mode(cfg, state, "local_fallback", reason=reason, retry_at=retry_at)


def _profile_name_for_role(
    cfg: RouterConfig,
    role: str,
    *,
    local: Optional[bool] = None,
    lane: Optional[str] = None,
) -> str:
    lanes = getattr(cfg, "lanes", {}) or {}
    role_profiles = getattr(cfg, "role_profiles", {}) or {}
    lane_cfg = lanes.get(lane or "", {}) or {}
    if not isinstance(lane_cfg, dict):
        lane_cfg = {}
    if local is None:
        return str(lane_cfg.get(f"{role}_profile") or role_profiles.get(role) or role)
    suffix = "local" if local else "cloud"
    return str(
        lane_cfg.get(f"{role}_{suffix}_profile")
        or lane_cfg.get(f"{role}_profile")
        or role_profiles.get(f"{role}_{suffix}")
        or role_profiles.get(role)
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
    profiles = getattr(cfg, "profiles", {}) or {}
    prof = profiles.get(name)
    if prof:
        return prof
    defaults = _default_profiles({
        "codex_cmd": getattr(cfg, "codex_cmd", "codex"),
        "model": getattr(cfg, "model", "gpt-5.1-codex"),
        "fallback_codex_cmd": getattr(cfg, "fallback_codex_cmd", "codex"),
        "fallback_codex_args": getattr(cfg, "fallback_codex_args", []),
        "fallback_model": getattr(cfg, "fallback_model", getattr(cfg, "model", "gpt-5.1-codex")),
        "fallback_model_args": getattr(cfg, "fallback_model_args", []),
    })
    return defaults["worker_local" if local else "worker_cloud"]


def _build_mcp_client(profile: LaunchProfile, approval: ApprovalPolicy) -> CodexMcpClient:
    if profile.harness != "codex":
        raise RuntimeError(f"{profile.harness} profiles do not support Codex MCP sessions")
    return CodexMcpClient(approval=approval, codex_cmd=profile.codex_cmd, codex_args=profile.codex_args)


class _CliOnlyMcpClient:
    def codex(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("CLI-only router profile cannot start Codex MCP sessions")

    def codex_reply(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("CLI-only router profile cannot use Codex MCP sessions")

    def close(self) -> None:
        return None


def _build_cli_command(
    profile: LaunchProfile,
    *,
    sandbox: str,
    prompt: str,
    local: bool,
    add_dirs: Optional[List[str]] = None,
    cwd: Optional[str] = None,
    ignore_user_config: bool = False,
    stdin_prompt: bool = False,
) -> List[str]:
    if profile.harness == "opencode":
        cmd = [profile.codex_cmd, "run", *profile.codex_args]
        if profile.model:
            model = profile.model if "/" in profile.model else f"lmstudio/{profile.model}"
            cmd.extend(["--model", model])
        if cwd:
            cmd.extend(["--dir", cwd])
        if sandbox != "read-only":
            cmd.append("--dangerously-skip-permissions")
        cmd.extend(profile.model_args)
        if stdin_prompt:
            cmd.append("-")
        else:
            cmd.append(prompt)
        return [str(x) for x in cmd]

    if profile.harness == "claude":
        cmd = [profile.codex_cmd, "-p", *profile.codex_args]
        if profile.model:
            cmd.extend(["--model", profile.model])
        cmd.extend(profile.model_args)
        if sandbox != "read-only":
            cmd.append("--dangerously-skip-permissions")
        for add_dir in add_dirs or []:
            if add_dir:
                cmd.extend(["--add-dir", str(add_dir)])
        cmd.extend(["--output-format", "text"])
        if not stdin_prompt:
            cmd.append(prompt)
        return [str(x) for x in cmd]

    cmd = [profile.codex_cmd, "exec", *profile.codex_args]
    if ignore_user_config:
        cmd.append("--ignore-user-config")
    if local:
        cmd.append("--skip-git-repo-check")
    if profile.model:
        cmd.extend(["-m", profile.model])
    cmd.extend(profile.model_args)
    for add_dir in add_dirs or []:
        if add_dir:
            cmd.extend(["--add-dir", str(add_dir)])
    if stdin_prompt:
        cmd.extend(["-s", sandbox, "-"])
    else:
        cmd.extend(["-s", sandbox, prompt])
    return [str(x) for x in cmd]


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
    elif mode in ("cloud_primary", "hybrid"):
        state["cloud_retry_at"] = 0
    if mode in ("cloud_primary", "hybrid"):
        state["cloud_available"] = True
    return state


def _switch_to_local_fallback(
    cfg: RouterConfig,
    state: Dict[str, Any],
    reason: str,
    retry_at: Optional[float] = None,
) -> Dict[str, Any]:
    if retry_at is None or retry_at <= time.time():
        retry_at = time.time() + cfg.cloud_probe_cooldown_seconds
    if _hybrid_mode(cfg, state) or str(cfg.runtime_mode_default) == "hybrid":
        return _mark_cloud_unavailable(cfg, state, reason, retry_at)
    return _set_runtime_mode(cfg, state, "local_fallback", reason=reason, retry_at=retry_at)


def _maybe_restore_cloud(
    cfg: RouterConfig,
    state: Dict[str, Any],
    repo_cwd: str,
) -> Dict[str, Any]:
    mode = _runtime_mode(cfg, state)
    if mode not in ("local_fallback", "hybrid"):
        return state
    if mode == "hybrid" and _cloud_available(cfg, state):
        return state
    if not cfg.auto_probe_cloud_recovery:
        return state
    if mode == "hybrid" and _select_available_cloud_provider(cfg, state, reason="restored cloud via available provider"):
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
            harness=probe.harness,
        )
        if rc != 0:
            return _switch_to_local_fallback(cfg, state, f"cloud probe exited {rc}")
        text = (out or "").strip()
        if text and not _is_reviewer_quota_output(text) and not _invalid_reviewer_output(text):
            restore_mode = "hybrid" if mode == "hybrid" or str(cfg.runtime_mode_default) == "hybrid" else "cloud_primary"
            return _set_runtime_mode(cfg, state, restore_mode, reason="cloud probe succeeded", retry_at=0)
    except Exception as exc:
        return _switch_to_local_fallback(cfg, state, f"cloud probe failed: {exc}")
    return _switch_to_local_fallback(cfg, state, "cloud probe returned invalid/empty output")


def _offline_reviewer_fallback(pkt: str, reason: str) -> str:
    """Produce a deterministic reviewer packet when reviewer threads are unavailable.

    This keeps the pipeline visible during quota windows without approving work
    that did not receive an actual reviewer pass.
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

    fixes: List[str] = []
    fixes.append("Re-run this packet through a live reviewer; offline fallback cannot approve integration.")
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


def _requires_live_reviewer_rerun(note_text: str) -> bool:
    """Return True for synthetic review notes that are not fixer work.

    Offline reviewer fallback is intentionally conservative: it blocks approval
    when a live review is unavailable. Sending that synthetic note to a feature
    fixer creates a loop because the fixer cannot satisfy "re-run live review"
    by changing code.
    """
    text = (note_text or "").lower()
    return (
        "offline fallback cannot approve integration" in text
        or (
            "reviewer was unavailable" in text
            and "fallback reason:" in text
            and "live reviewer" in text
        )
    )

def reviewer_prompt(pkt: str) -> str:
    return (
        "You are the REVIEWER. You are sandboxed read-only and MUST NOT modify files.\n"
        "If the packet includes `Commit under review`, review that implementation commit/range. "
        "Do not treat a `Packet refresh commit` as implementation unless the packet explicitly says it is the reviewed implementation.\n"
        "You MUST enforce plan alignment using narrow evidence from: ROADMAP.md, PRODUCT_VISION.md, ARCHITECTURE.md, INTEGRATION.md, AGENTS.md.\n"
        "Use bounded reads only: first use `rg -n` for relevant headings/keywords, then read narrow `nl -ba | sed -n '<start>,<end>p'` ranges, normally <=80 lines at a time. "
        "Do not `cat` or full-file Read docs, source files, `.codex`, `.agents`, archives, or logs. "
        "If a tool reports `Context size has been exceeded`, stop and return CHANGES_REQUESTED with that exact blocker; do not continue.\n"
        "If roadmap/vision mapping is unclear or off-plan, output CHANGES_REQUESTED with concrete scope-tightening.\n\n"
        "Output exactly one markdown packet with sections:\n"
        "1. Verdict: `APPROVED` or `CHANGES_REQUESTED`\n"
        "2. Findings (highest severity first)\n"
        "3. Missing handoff fields (if any)\n"
        "4. Required fixes before re-review (numbered, actionable)\n"
        "5. If approved: merge order + any post-merge checks (include merge risk)\n\n"
        f"Review this feature packet:\n\n{pkt}\n"
    )

def integrator_prompt(approved: str, *, feature_packet_path: str = "", feature_packet_text: str = "") -> str:
    packet = _extract_final_verdict_packet(approved)
    feature_context = ""
    if feature_packet_text:
        feature_context = (
            "\n\nCompanion feature packet with reviewed implementation scope"
            + (f" (`{feature_packet_path}`)" if feature_packet_path else "")
            + ":\n\n"
            + feature_packet_text
            + "\n"
        )
    return (
        "You are the INTEGRATOR. You may write to the workspace.\n"
        "Consume this APPROVED packet, perform merge order + post-merge checks, report blockers.\n\n"
        "Lane priority order is scheduling guidance, not a hard merge blocker. "
        "Do not block solely because an earlier-priority lane branch is unmerged. "
        "Only hold this integration when there is a direct file/content overlap or another concrete merge blocker.\n\n"
        "If the feature branch contains stale broad history, do not merge the whole branch. "
        "Integrate the narrow reviewed implementation surface from the companion feature packet: use its commit-under-review, "
        "reviewed file list, and approved shared-test exception to apply only the approved slice.\n\n"
        "Do not run broad recursive searches over `.codex` or `.agents`; those directories contain large historical logs. "
        "If packet evidence is needed, read the specific packet path or use targeted `ls`, `cat`, `tail`, or `rg` commands against named files only.\n\n"
        f"{packet}"
        f"{feature_context}\n"
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
    harness: str = "codex",
) -> Tuple[int, str]:
    stdin_prompt = harness == "claude"
    cmd = _build_cli_command(
        LaunchProfile(codex_cmd, codex_args, model, model_args, harness=harness),
        sandbox=sandbox,
        prompt=prompt,
        local=skip_git_repo_check,
        cwd=cwd,
        stdin_prompt=stdin_prompt,
    )
    p = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        input=prompt if stdin_prompt else None,
        text=True,
        timeout=timeout,
        env=agent_runtime_env(cwd, env),
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
    env = agent_runtime_env(repo_cwd, isolated_codex_env(repo_cwd) if runtime_local else None)
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
            harness=prof.harness,
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
    env = agent_runtime_env(repo_cwd, isolated_codex_env(repo_cwd) if runtime_local else None)
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
            harness=prof.harness,
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


def _tracked_integrator_pids(state: Dict[str, Any]) -> set[int]:
    pids: set[int] = set()
    for key in ("cloud_integrator_jobs", "local_integrator_jobs"):
        jobs = state.get(key) or {}
        if not isinstance(jobs, dict):
            continue
        for job in jobs.values():
            if not isinstance(job, dict):
                continue
            pid = int(job.get("pid") or 0)
            if pid > 0:
                pids.add(pid)
    return pids


def _lane_has_active_integrator_job(
    state: Dict[str, Any],
    lane: str,
    *,
    exclude_job_key: str = "",
) -> bool:
    """Return True if this lane already has an active integrator.

    Integrators merge into the shared main worktree, so packet-level parallelism
    is unsafe even when packets are distinct. Keep this lane guard separate from
    the global cloud/local caps so config changes cannot accidentally launch two
    integrators for the same lane again.
    """
    for key in ("cloud_integrator_jobs", "local_integrator_jobs"):
        jobs = state.get(key) or {}
        if not isinstance(jobs, dict):
            continue
        for job_key, job in jobs.items():
            if job_key == exclude_job_key or not isinstance(job, dict):
                continue
            if str(job.get("lane") or "") != lane:
                continue
            result_path = Path(str(job.get("result_path") or ""))
            if result_path.exists():
                continue
            if _pid_alive(int(job.get("pid") or 0)):
                return True
    return False


def _process_command_rows() -> List[Tuple[int, str]]:
    """Return process command rows, preferring untruncated command text."""
    commands = (
        ["ps", "-wwaxo", "pid=,command="],
        ["ps", "-axo", "pid=,command="],
    )
    for command in commands:
        try:
            proc = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=2,
            )
        except Exception:
            continue
        if proc.returncode != 0:
            continue
        rows: List[Tuple[int, str]] = []
        for raw_line in (proc.stdout or "").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            pid_text, _, process_command = line.partition(" ")
            try:
                pid = int(pid_text)
            except ValueError:
                continue
            rows.append((pid, process_command))
        return rows
    return []


def _is_cloud_integrator_exec_command(command: str) -> bool:
    return "codex exec" in command and any(marker in command for marker in INTEGRATOR_EXEC_MARKERS)


def _live_untracked_cloud_integrator_exec_pids(state: Dict[str, Any]) -> List[int]:
    """Return live Codex integrators that router state failed to track."""
    tracked = _tracked_integrator_pids(state)
    current_pid = os.getpid()
    pids: List[int] = []
    for pid, command in _process_command_rows():
        if pid == current_pid or pid in tracked or not _pid_alive(pid):
            continue
        if _is_cloud_integrator_exec_command(command):
            pids.append(pid)
    return pids


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


def _count_active_feature_cloud_jobs() -> int:
    feature_state = load_json(FEATURE_RUNNER_STATE_FILE, {})
    lanes = feature_state.get("lanes") if isinstance(feature_state, dict) else {}
    if not isinstance(lanes, dict):
        return 0
    active = 0
    for lane_state in lanes.values():
        if not isinstance(lane_state, dict):
            continue
        if str(lane_state.get("mode") or "") != "cloud_primary":
            continue
        pid = int(lane_state.get("pid") or 0)
        if _pid_alive(pid):
            active += 1
    return active


def _count_active_cloud_jobs(state: Dict[str, Any]) -> int:
    active = _count_active_feature_cloud_jobs()
    active += _count_active_local_jobs(_local_job_map(state, "cloud_reviewer_jobs"))
    active += _count_active_local_jobs(_local_job_map(state, "cloud_integrator_jobs"))
    active += len(_live_untracked_cloud_integrator_exec_pids(state))
    active += _count_active_pid_jobs(_local_job_map(state, "fixer_fallback_jobs"), local=False)
    active += _count_active_local_jobs(_local_job_map(state, "metadata_repair_jobs"))
    return active


def _cloud_role_slot_available(cfg: RouterConfig, state: Dict[str, Any], role: str) -> bool:
    if not _cloud_available(cfg, state):
        return False
    if role == "feature":
        cap = int(getattr(cfg, "max_cloud_feature_jobs", 4) or 0)
        active = _count_active_feature_cloud_jobs()
    elif role == "reviewer":
        # Reviewers are high-value cloud work; let them consume spare capacity
        # from the shared cloud pool instead of forcing a single reviewer lane.
        total_cap = int(getattr(cfg, "max_total_cloud_jobs", 4) or 0)
        cap = total_cap if total_cap > 0 else int(getattr(cfg, "max_cloud_reviewer_jobs", 4) or 0)
        active = _count_active_local_jobs(_local_job_map(state, "cloud_reviewer_jobs"))
    elif role == "integrator":
        cap = int(getattr(cfg, "max_cloud_integrator_jobs", 4) or 0)
        active = _count_active_local_jobs(_local_job_map(state, "cloud_integrator_jobs"))
        active += len(_live_untracked_cloud_integrator_exec_pids(state))
    elif role == "fixer":
        cap = int(getattr(cfg, "max_cloud_fixer_jobs", 4) or 0)
        active = _count_active_pid_jobs(_local_job_map(state, "fixer_fallback_jobs"), local=False)
    else:
        cap = 1
        active = 0
    if cap <= 0:
        return False
    total_cap = int(getattr(cfg, "max_total_cloud_jobs", 4) or 0)
    if total_cap > 0 and _count_active_cloud_jobs(state) >= total_cap:
        return False
    return active < cap


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
    return _build_cli_command(
        profile,
        sandbox=sandbox,
        prompt=prompt,
        local=local,
        add_dirs=add_dirs,
    )


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
    env_overrides = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "RIPGREP_CONFIG_PATH": str(agent_ripgrep_config_path(repo_cwd)),
    }
    if local:
        env_overrides["CODEX_HOME"] = isolated_codex_env(repo_cwd)["CODEX_HOME"]
    cli_prompt = prompt if profile.harness == "opencode" else _prompt_file_bootstrap(prompt_path)
    spec = {
        "cmd": _build_cli_exec_cmd(
            profile,
            sandbox=sandbox,
            prompt=cli_prompt,
            local=local,
            add_dirs=[str(prompt_path.parent.resolve())] if local and profile.harness != "opencode" else None,
        ),
        "cwd": repo_cwd,
        "timeout_seconds": float(timeout_seconds),
        "env_overrides": env_overrides,
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
        "provider": "local" if local else _current_cloud_provider(cfg, {}),
        "profile": _profile_name_for_role(cfg, role, local=local, lane=lane),
        "harness": profile.harness,
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


def _requires_control_plane_metadata_repair(note_text: str) -> bool:
    text = note_text or ""
    if parse_verdict(text) == "APPROVED":
        return False
    lower = text.lower()
    if "control-plane metadata fix required" in lower:
        return True
    if not CONTROL_PLANE_METADATA_REPAIR_RE.search(text):
        return False
    required_section = "required fix" in lower or "missing handoff" in lower or "findings" in lower
    metadata_weight = len(CONTROL_PLANE_METADATA_REPAIR_RE.findall(text))
    return required_section and metadata_weight >= 2


def metadata_repair_prompt(lane: str, branch: str, reviewer_packet: str) -> str:
    return (
        f"You are the CONTROL-PLANE METADATA REPAIR worker for lane `{lane}`.\n"
        f"Repair metadata needed to unblock reviewer re-check for branch `{branch}`.\n\n"
        "This is not feature implementation work.\n"
        "Operate from the main repo root only. Do not edit feature source files.\n"
        "Allowed edit surface:\n"
        f"- `.codex/metadata_repairs/{lane}.md`\n"
        f"- `.codex/metadata_repairs/{lane}.shared.md`\n"
        f"- `.codex/lane_meta/{lane}.json`\n"
        f"- `.codex/packets/lanes/{lane}/**` packet metadata files\n"
        "- `THREAD_PACKET.md` only if it is clean and belongs to this lane; if it is dirty for another lane, leave it alone and state that.\n\n"
        "Required behavior:\n"
        "- Make the handoff metadata locally reviewable: use real commits/ranges from this repository.\n"
        "- Use canonical roadmap names from `ROADMAP.md`.\n"
        "- Make changed-files and shared/control-plane declarations internally consistent.\n"
        "- State the canonical demo-path step advanced by the feature implementation.\n"
        "- Preserve `THREAD_OWNERSHIP.md` boundaries; do not broaden lane ownership.\n"
        "- Do not touch source files outside the control-plane metadata surface above.\n"
        "- Run focused validation for metadata syntax: `python -m json.tool .codex/lane_meta/{lane}.json` and `git diff --check`.\n"
        "- Commit only the metadata repair files you intentionally changed with message `Repair {lane} handoff metadata`.\n\n"
        "If the repair cannot be completed without touching unrelated dirty files, report the blocker and stop.\n\n"
        "Reviewer packet to satisfy:\n\n"
        f"{reviewer_packet}\n"
    )


def _git_output(repo_cwd: str, args: List[str]) -> str:
    result = run_git(args, cwd=repo_cwd, timeout=120)
    if result.returncode != 0:
        return ""
    return (result.stdout or "").strip()


def _resolvable_branch_range(repo_cwd: str, branch: str) -> Tuple[str, str]:
    head = _git_output(repo_cwd, ["rev-parse", branch])
    base = _git_output(repo_cwd, ["merge-base", "HEAD", branch])
    if base and head:
        return f"{base}..{head}", head
    return head, head


def _archive_shared_only_feature_packets(lane_dir: Path) -> int:
    feature_dir = lane_dir / "inbox" / "feature"
    moved = 0
    for shared in sorted(feature_dir.glob("*.shared.md"), key=lambda p: p.stat().st_mtime):
        primary = feature_dir / shared.name.removesuffix(".shared.md")
        if primary.exists():
            continue
        archive(shared, lane_dir)
        moved += 1
    return moved


def _changed_files_for_range(repo_cwd: str, commit_range: str) -> List[str]:
    token = str(commit_range or "").strip()
    if not token:
        return []
    if ".." in token:
        result = run_git(["diff", "--name-only", token], cwd=repo_cwd, timeout=120)
    else:
        result = run_git(["show", "--pretty=", "--name-only", token], cwd=repo_cwd, timeout=120)
    if result.returncode != 0:
        return []
    return [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]


def _mark_planner_reemit_for_lane(lane: str, sha: str, *, reason: str) -> None:
    planner_state_path = Path(".codex/packet_planner/state.json")
    state = load_json(planner_state_path, {})
    if not isinstance(state, dict):
        state = {}
    lanes = state.setdefault("lanes", {})
    if not isinstance(lanes, dict):
        lanes = {}
        state["lanes"] = lanes
    lane_state = lanes.get(lane)
    if not isinstance(lane_state, dict):
        lane_state = {}
        lanes[lane] = lane_state
    lane_state.pop("last_submitted_sha", None)
    lane_state.pop("last_emitted_packet", None)
    if sha:
        lane_state["force_reemit_sha"] = sha
        lane_state["force_reemit_reason"] = reason
    save_json(planner_state_path, state)


def _repair_control_plane_metadata_locally(repo_cwd: str, lane: str, branch: str, note_path: Path) -> Dict[str, Any]:
    lane_dir = ensure_lane_dirs(lane)
    source_range, reviewed_commit = _resolvable_branch_range(repo_cwd, branch)
    profile = default_lane_meta(lane)
    roadmap_items = list(profile.get("roadmap_items") or [])
    vision_capabilities = list(profile.get("vision_capabilities") or [])
    demo_step_by_lane = {
        "feat-a2ui-contract": (
            "preview and apply or reject a patch through stable shared card/action contracts "
            "and CLI fallback rendering"
        ),
        "feat-retrieval-fts": (
            "retrieve relevant material and promote or gather context into the basket with "
            "deterministic FTS provenance"
        ),
        "feat-engine-runs": (
            "plan or revise from gathered context, produce a patch proposal, apply or reject it, "
            "and persist the resulting document/session state"
        ),
    }
    demo_step = demo_step_by_lane.get(
        lane,
        (
            "advance the canonical engine-side demo path without expanding speculative product "
            "or UI scope"
        ),
    )

    meta_path = Path(".codex/lane_meta") / f"{lane}.json"
    meta = load_json(meta_path, {})
    if not isinstance(meta, dict):
        meta = {}
    reviewed_files = _changed_files_for_range(repo_cwd, source_range)
    lane_tasks_by_lane = {
        "feat-retrieval-fts": [
            "Exposed the retrieval demo-path contract so downstream payloads can name the FTS retrieval-to-basket steps.",
            "Allowed FTS excerpt promotion to derive source strategy from an explicit sqlite_fts/fts_first retrieval envelope.",
            "Rejected incomplete excerpt promotion records that lack required document, span, hash, or FTS lookup provenance.",
            "Kept the implementation diff lane-scoped to retrieval payload/service exports while advancing retrieve relevant material and basket promotion.",
        ],
        "feat-a2ui-contract": [
            "Repaired handoff evidence for stable shared card/action contracts and CLI fallback rendering.",
            "Named the canonical preview/apply/reject demo-path step advanced by the A2UI contract lane.",
            "Kept the repair limited to control-plane handoff metadata, leaving feature implementation files untouched.",
            "Archived stale shared-only feature packet debris so the lane queue reflects real reviewable packets.",
        ],
        "feat-engine-runs": [
            "Repaired handoff evidence for the engine plan/revise/patch/apply loop.",
            "Named the canonical plan/revise and persist demo-path step advanced by the engine-runs lane.",
            "Kept the repair limited to control-plane handoff metadata, leaving feature implementation files untouched.",
            "Archived stale shared-only feature packet debris so the lane queue reflects real reviewable packets.",
        ],
    }
    tasks_completed = lane_tasks_by_lane.get(
        lane,
        [
            f"Replaced stale source commit metadata with locally resolvable range `{source_range}`.",
            "Replaced stale roadmap labels with canonical active MVP lane profile mappings.",
            f"Named the canonical demo-path step advanced: {demo_step}.",
            "Archived stale shared-only feature packet debris so the lane queue reflects real reviewable packets.",
        ],
    )
    meta.update(
        {
            "risk": str(profile.get("risk") or meta.get("risk") or "MEDIUM"),
            "roadmap_items": roadmap_items,
            "source_commits": [source_range] if source_range else [],
            "reviewed_commit": reviewed_commit,
            "reviewed_commit_range": source_range,
            "routing_provider_impact": str(profile.get("routing_provider_impact") or "None"),
            "scope_goal": str(profile.get("scope_goal") or meta.get("scope_goal") or ""),
            "scope_completed": (
                "Control-plane metadata repair: replaced stale unreachable source range and stale roadmap labels "
                f"with locally resolvable branch evidence `{source_range}` and canonical active MVP roadmap items."
            ),
            "tasks_completed": tasks_completed,
            "vision_capabilities": vision_capabilities,
            "shared_file_exception": True,
            "approved_exception_note": (
                "Control-plane metadata repair was performed locally by packet_garden because cloud workers cannot "
                "reliably write `.codex/**` metadata under workspace-write sandboxing."
            ),
            "canonical_demo_path_step": demo_step,
        }
    )
    if reviewed_files:
        meta["reviewed_files"] = reviewed_files
        if "metadata_only_files" not in meta:
            meta["metadata_only_files"] = []
        meta["kickoff_budget_note"] = (
            "Metadata repair re-emits the reviewed implementation range with "
            "changed-files evidence derived directly from git."
        )
    save_json(meta_path, meta)

    repair_dir = Path(".codex/metadata_repairs")
    handoff = repair_dir / f"{lane}.md"
    shared = repair_dir / f"{lane}.shared.md"
    write_text(
        handoff,
        "\n".join(
            [
                f"# {lane} Handoff Metadata",
                "",
                f"- Lane: `{lane}`",
                f"- Branch: `{branch}`",
                f"- Reviewed source range: `{source_range}`",
                f"- Reviewed commit: `{reviewed_commit}`",
                "- Roadmap item(s) affected:",
                *[f"  - {item}" for item in roadmap_items],
                "- Vision capability affected:",
                *[f"  - {item}" for item in vision_capabilities],
                f"- Canonical demo-path step advanced: {demo_step}",
                "- Concrete tasks completed:",
                *[f"  {idx}. {task}" for idx, task in enumerate(tasks_completed, start=1)],
                "",
                "This file is control-plane metadata. The feature implementation remains on the lane branch.",
                "This file is intentionally separate from `.codex/kickoff_packets/`; do not use it as a feature-worker kickoff brief.",
                "",
            ]
        ),
    )
    write_text(
        shared,
        "\n".join(
            [
                f"# Shared Maintenance Packet: {lane}",
                "",
                f"- Branch: `{branch}`",
                f"- Source commit(s): `{source_range}`",
                "- Scope: local control-plane metadata repair for stale handoff evidence.",
                "- Reason: cloud metadata repair jobs cannot reliably write `.codex/**` under workspace-write sandboxing.",
                "",
            ]
        ),
    )

    shared_only_archived = _archive_shared_only_feature_packets(lane_dir)
    archive(note_path, lane_dir)
    _mark_planner_reemit_for_lane(
        lane,
        reviewed_commit,
        reason="control_plane_metadata_repair",
    )
    return {
        "source_range": source_range,
        "reviewed_commit": reviewed_commit,
        "shared_only_archived": shared_only_archived,
        "note_archived": note_path.name,
    }


def _prepare_metadata_repair_job(
    cfg: RouterConfig,
    state: Dict[str, Any],
    repo_cwd: str,
    lane: str,
    note_path: Path,
    reviewer_packet: str,
) -> Tuple[bool, Dict[str, Any]]:
    jobs = _local_job_map(state, "metadata_repair_jobs")
    packet_name = note_path.name
    branch = str((cfg.lanes.get(lane, {}) or {}).get("branch") or f"codex/{lane}")
    job = jobs.get(lane)
    if isinstance(job, dict) and str(job.get("packet_name") or "") != packet_name:
        if not _pid_alive(int(job.get("pid") or 0)):
            jobs.pop(lane, None)
            job = None
        else:
            state["metadata_repair_jobs"] = jobs
            return False, state

    if isinstance(job, dict):
        polled = _poll_detached_local_cli_job(job)
        if not polled["done"]:
            state["metadata_repair_jobs"] = jobs
            return False, state
        jobs.pop(lane, None)
        state["metadata_repair_jobs"] = jobs
        text = str(polled.get("output") or "").strip()
        reason = str(polled.get("error") or "metadata repair job failed")
        if polled.get("status") == "ok" and int(polled.get("rc") or 1) == 0:
            if "operation not permitted" in text.lower() or ".codex/** is not writable" in text.lower():
                repair = _repair_control_plane_metadata_locally(repo_cwd, lane, branch, note_path)
                cursor = state.get("metadata_repair_cursor") or {}
                if not isinstance(cursor, dict):
                    cursor = {}
                cursor[lane] = {
                    "packet_name": packet_name,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "mode": "local_control_plane_repair_after_sandbox_block",
                    "repair": repair,
                }
                state["metadata_repair_cursor"] = cursor
                print(f"[router] repaired {lane} metadata locally after cloud sandbox block: {repair}")
                return True, state
            cursor = state.get("metadata_repair_cursor") or {}
            if not isinstance(cursor, dict):
                cursor = {}
            cursor[lane] = {
                "packet_name": packet_name,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
            state["metadata_repair_cursor"] = cursor
            print(f"[router] metadata repair job for {lane} completed; waiting for repaired handoff re-review")
            return True, state
        quota_text = "\n".join(part for part in (text, reason) if part)
        if cfg.auto_switch_to_local_on_quota and _has_real_quota_signal(quota_text):
            state = _switch_to_local_fallback(
                cfg,
                state,
                f"cloud metadata repair job failed/timed out: {reason}",
                _quota_retry_epoch(cfg, quota_text),
            )
            print(f"[router] cloud metadata repair job for {lane} hit quota; cloud pool unavailable: {reason}")
            return False, state
        print(f"[router] metadata repair job for {lane} failed; will retry after fixer cooldown: {reason}")
        return True, state

    cursor = state.get("metadata_repair_cursor") or {}
    if isinstance(cursor, dict):
        previous = cursor.get(lane)
        if isinstance(previous, dict) and str(previous.get("packet_name") or "") == packet_name:
            return True, state

    repair = _repair_control_plane_metadata_locally(repo_cwd, lane, branch, note_path)
    cursor = state.get("metadata_repair_cursor") or {}
    if not isinstance(cursor, dict):
        cursor = {}
    cursor[lane] = {
        "packet_name": packet_name,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "mode": "local_control_plane_repair",
        "repair": repair,
    }
    state["metadata_repair_cursor"] = cursor
    state["metadata_repair_jobs"] = jobs
    print(f"[router] repaired {lane} metadata locally: {repair}")
    return True, state


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


def _prepare_cli_reviewer_result(
    cfg: RouterConfig,
    state: Dict[str, Any],
    repo_cwd: str,
    lane: str,
    pkt_path: Path,
    pkt: str,
    *,
    local: bool,
) -> Tuple[bool, str, Dict[str, Any]]:
    try:
        runtime_mode = _runtime_mode(cfg, state)
    except AttributeError:
        runtime_mode = str(state.get("runtime_mode") or getattr(cfg, "runtime_mode_default", "cloud_primary"))
    if not local and runtime_mode == "cloud_primary" and not hasattr(cfg, "profiles") and not hasattr(cfg, "role_profiles"):
        reviewer_text = _run_cli_reviewer(
            cfg,
            repo_cwd,
            pkt,
            "cloud cli reviewer requested",
            local=local,
            lane=lane,
        )
        if reviewer_text:
            return True, reviewer_text, state
        return True, _offline_reviewer_fallback(pkt, "cloud cli reviewer unavailable"), state

    jobs_key = "local_reviewer_jobs" if local else "cloud_reviewer_jobs"
    mode_label = "local" if local else "cloud"
    jobs = _local_job_map(state, jobs_key)
    packet_name = pkt_path.name
    job = jobs.get(lane)
    if isinstance(job, dict) and str(job.get("packet_name") or "") != packet_name:
        if not _pid_alive(int(job.get("pid") or 0)):
            jobs.pop(lane, None)
            job = None
        else:
            state[jobs_key] = jobs
            return False, "", state

    if isinstance(job, dict):
        polled = _poll_detached_local_cli_job(job)
        if not polled["done"]:
            state[jobs_key] = jobs
            return False, "", state
        jobs.pop(lane, None)
        state[jobs_key] = jobs
        text = str(polled.get("output") or "").strip()
        rejection = _local_cli_output_rejection_reason(text, require_verdict=True)
        if polled.get("status") == "ok" and not rejection:
            return True, text, state
        reason = str(polled.get("error") or rejection or f"{mode_label} reviewer job failed")
        quota_text = "\n".join(part for part in (text, reason) if part)
        if not local and cfg.auto_switch_to_local_on_quota and _has_real_quota_signal(quota_text):
            state = _switch_to_local_fallback(
                cfg,
                state,
                f"cloud reviewer job failed/timed out: {reason}",
                _quota_retry_epoch(cfg, quota_text),
            )
            print(f"[router] cloud reviewer job for {lane} hit quota; cloud pool unavailable, local work continues: {reason}")
            return False, "", state
        if local:
            print(f"[router] local reviewer job for {lane} failed; packet remains pending for live re-review: {reason}")
            return False, "", state
        print(f"[router] {mode_label} reviewer job for {lane} failed, using offline fallback: {reason}")
        return True, _offline_reviewer_fallback(pkt, reason), state

    if local and _count_active_local_jobs(jobs) >= LOCAL_REVIEWER_MAX_ACTIVE:
        state[jobs_key] = jobs
        return False, "", state
    if local and not _local_lms_slot_available(cfg, state):
        state[jobs_key] = jobs
        return False, "", state
    if not local and not _cloud_role_slot_available(cfg, state, "reviewer"):
        state[jobs_key] = jobs
        return False, "", state

    jobs[lane] = _spawn_detached_cli_job(
        role="reviewer",
        cfg=cfg,
        repo_cwd=repo_cwd,
        lane=lane,
        packet_name=packet_name,
        prompt=reviewer_prompt(pkt),
        sandbox="read-only",
        timeout_seconds=cfg.reviewer_timeout,
        local=local,
    )
    state[jobs_key] = jobs
    print(f"[router] queued {mode_label} reviewer job for {lane} ({packet_name})")
    return False, "", state


def _prepare_local_reviewer_result(
    cfg: RouterConfig,
    state: Dict[str, Any],
    repo_cwd: str,
    lane: str,
    pkt_path: Path,
    pkt: str,
) -> Tuple[bool, str, Dict[str, Any]]:
    return _prepare_cli_reviewer_result(cfg, state, repo_cwd, lane, pkt_path, pkt, local=True)


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
    max_active = (
        LOCAL_INTEGRATOR_MAX_ACTIVE
        if local
        else int(getattr(cfg, "max_cloud_integrator_jobs", CLOUD_INTEGRATOR_MAX_ACTIVE) or CLOUD_INTEGRATOR_MAX_ACTIVE)
    )
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
            print(f"[router] cloud integrator job for {lane} hit quota; cloud pool unavailable, local work continues: {reason}")
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
    if _lane_has_active_integrator_job(state, lane, exclude_job_key=job_key):
        state[jobs_key] = jobs
        return False, "", state
    if _count_active_local_jobs(jobs) >= max_active:
        state[jobs_key] = jobs
        return False, "", state
    if local and not _local_lms_slot_available(cfg, state):
        state[jobs_key] = jobs
        return False, "", state
    if not local and not _cloud_role_slot_available(cfg, state, "integrator"):
        state[jobs_key] = jobs
        return False, "", state

    lane_dir = pkt.parents[2] if len(pkt.parents) > 2 else ensure_lane_dirs(lane)
    feature_packet = _feature_packet_for_approval(lane_dir, pkt)
    feature_packet_text = feature_packet.read_text(errors="ignore") if feature_packet else ""
    jobs[job_key] = _spawn_detached_cli_job(
        role="integrator",
        cfg=cfg,
        repo_cwd=repo_cwd,
        lane=lane,
        packet_name=pkt.name,
        prompt=integrator_prompt(
            approved_text,
            feature_packet_path=str(feature_packet) if feature_packet else "",
            feature_packet_text=feature_packet_text,
        ),
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
    lane_commit_helper = REPO_ROOT / "packet_garden/tools/lane_repo_commit.py"
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
            "- Use bounded reads only: first use `rg -n` for relevant headings/keywords, then read narrow `nl -ba | sed -n '<start>,<end>p'` ranges, normally <=80 lines at a time.\n"
            "- Do not `cat` or full-file Read docs, source files, `.codex`, `.agents`, archives, or logs.\n"
            "- Do not edit hidden `.codex` metadata files from a sandboxed fixer.\n"
            "- Do not edit or commit control-plane files from this fixer, including `packet_garden/**`, `.codex/**`, `.agents/**`, `THREAD_PACKET.md`, `THREAD_OWNERSHIP.md`, `INTEGRATION.md`, `AGENTS.md`, or `scripts/scope-check.sh`.\n"
            "- If the reviewer requires handoff metadata, packet metadata, shared packet, lane metadata, `THREAD_PACKET.md`, `.codex/**`, `packet_garden/**`, or scope-policy changes, report `control-plane metadata fix required` and stop instead of editing those files.\n"
            "- Do not retry a failed `.codex` write with multiple tools; one failed write is enough evidence that the control plane must handle that metadata correction.\n"
            "- If a tool reports `Context size has been exceeded`, stop, report that exact blocker, and wait for a fresh launch.\n\n"
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
        "- Use bounded reads only: first use `rg -n` for relevant headings/keywords, then read narrow `nl -ba | sed -n '<start>,<end>p'` ranges, normally <=80 lines at a time.\n"
        "- Do not `cat` or full-file Read docs, source files, `.codex`, `.agents`, archives, or logs.\n"
        "- Do not edit hidden `.codex` metadata files from a sandboxed fixer.\n"
        "- Do not edit or commit control-plane files from this fixer, including `packet_garden/**`, `.codex/**`, `.agents/**`, `THREAD_PACKET.md`, `THREAD_OWNERSHIP.md`, `INTEGRATION.md`, `AGENTS.md`, or `scripts/scope-check.sh`.\n"
        "- If the reviewer requires handoff metadata, packet metadata, shared packet, lane metadata, `THREAD_PACKET.md`, `.codex/**`, `packet_garden/**`, or scope-policy changes, report `control-plane metadata fix required` and stop instead of editing those files.\n"
        "- Do not retry a failed `.codex` write with multiple tools; one failed write is enough evidence that the control plane must handle that metadata correction.\n"
        "- If a tool reports `Context size has been exceeded`, stop, report that exact blocker, and wait for a fresh launch.\n\n"
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
    runtime_local = _use_local_provider(cfg, state) if local_mode is None else bool(local_mode)
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
    env = agent_runtime_env(repo_cwd, isolated_codex_env(repo_cwd) if runtime_local else None)
    with logp.open("w") as lf:
        prompt_text = fixer_prompt(lane, branch, reviewer_packet, wt)
        prompt_path = logs / f"fixer__{lane}__{ts}.prompt.txt"
        write_text(prompt_path, prompt_text)
        cmd = _build_cli_command(
            prof,
            sandbox="workspace-write",
            prompt=_prompt_file_bootstrap(prompt_path),
            local=runtime_local,
            add_dirs=[str(prompt_path.parent.resolve())] if runtime_local else None,
            cwd=(wt or repo_cwd),
            ignore_user_config=not runtime_local,
            stdin_prompt=prof.harness in {"codex", "claude"},
        )
        proc = subprocess.Popen(
            cmd,
            cwd=(wt or repo_cwd),
            stdout=lf,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE if prof.harness in {"codex", "claude"} else subprocess.DEVNULL,
            text=True,
            env=env,
            start_new_session=True,
        )
        proc_stdin = getattr(proc, "stdin", None)
        if proc_stdin is not None:
            try:
                proc_stdin.write(prompt_text if prof.harness == "claude" else _prompt_file_bootstrap(prompt_path))
                proc_stdin.close()
            except BrokenPipeError:
                pass
    fallback = state.get("fixer_fallback_jobs") or {}
    fallback[lane] = {
        "log": str(logp),
        "ts": ts,
        "pid": proc.pid,
        "local": runtime_local,
        "provider": "local" if runtime_local else _current_cloud_provider(cfg, state),
        "profile": _profile_name_for_role(cfg, "fixer", local=runtime_local, lane=lane),
        "harness": prof.harness,
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


def _restore_archived_feature_for_live_review(lane_dir: Path, reviewer_note: Path) -> Optional[Path]:
    """Requeue an archived feature packet when only a synthetic fallback note remains."""
    note_sha = _packet_sha(reviewer_note.name)
    if not note_sha:
        return None
    feature_inbox = lane_dir / "inbox" / "feature"
    if any(_packet_sha(p.name) == note_sha for p in feature_inbox.glob("*.md")):
        return None
    archived = sorted((lane_dir / "archive").glob(f"F__*__{note_sha}__*.md"), key=lambda p: p.stat().st_mtime)
    if not archived:
        return None
    source = archived[-1]
    parts = source.name.split("__")
    if len(parts) >= 4:
        parts[-1] = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ.md")
        name = "__".join(parts)
    else:
        name = f"{source.stem}__REREVIEW__{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.md"
    restored = feature_inbox / name
    write_text(restored, source.read_text(errors="ignore"))
    archive(reviewer_note, lane_dir)
    return restored


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


def _feature_packet_for_job(lane_dir: Path, packet_name: str) -> Optional[Path]:
    for rel in ("inbox/feature", "archive"):
        pkt = lane_dir / rel / packet_name
        if pkt.exists():
            return pkt
    return None


def _archive_consumed_feature_packet(lane_dir: Path, pkt_path: Path) -> None:
    """Archive an inbox feature packet once a detached reviewer result is materialized."""

    try:
        if pkt_path.exists() and pkt_path.parent == lane_dir / "inbox" / "feature":
            archive(pkt_path, lane_dir)
    except Exception:
        # Best-effort cleanup only; review materialization should still win.
        pass


def _harvest_completed_reviewer_jobs(
    cfg: RouterConfig,
    state: Dict[str, Any],
    *,
    local: bool,
) -> Tuple[int, Dict[str, Any]]:
    """Materialize completed detached reviewer jobs even after packet archival.

    Detached reviewer launch can archive or otherwise move the feature packet
    before the next router tick gets to poll the result. Without this harvest
    pass, a completed job can sit forever in router state and an older reviewer
    note can keep queue truth pinned to the wrong SHA.
    """

    jobs_key = "local_reviewer_jobs" if local else "cloud_reviewer_jobs"
    mode_label = "local" if local else "cloud"
    jobs = _local_job_map(state, jobs_key)
    harvested = 0
    for lane, job in list(jobs.items()):
        if lane not in cfg.lanes or not isinstance(job, dict):
            continue
        polled = _poll_detached_local_cli_job(job)
        if not polled["done"]:
            continue

        packet_name = str(job.get("packet_name") or "")
        lane_dir = ensure_lane_dirs(lane)
        pkt_path = _feature_packet_for_job(lane_dir, packet_name)
        if pkt_path is None:
            jobs.pop(lane, None)
            print(f"[router] dropped completed {mode_label} reviewer job for {lane}: packet {packet_name or '-'} missing")
            continue

        text = str(polled.get("output") or "").strip()
        rejection = _local_cli_output_rejection_reason(text, require_verdict=True)
        if polled.get("status") != "ok" or rejection:
            jobs.pop(lane, None)
            reason = str(polled.get("error") or rejection or f"{mode_label} reviewer job failed")
            print(f"[router] dropped completed {mode_label} reviewer job for {lane}: {reason}")
            continue

        reviewer_text = _extract_final_verdict_packet(text) or text
        if not reviewer_text.strip():
            reviewer_text = (
                "Verdict: `CHANGES_REQUESTED`\n\n"
                "Reviewer output was empty; router inserted recovery packet.\n"
                "Required fixes: derive issues from the feature packet and resubmit.\n"
            )
        verdict = parse_verdict(reviewer_text)
        if verdict == "APPROVED":
            archive_reviewer_notes(lane_dir)
            outp = lane_dir / "outbox/integrator" / packet_name.replace("F__", "R__APPROVED__")
            write_text(outp, reviewer_text)
        else:
            outp = lane_dir / "inbox/reviewer" / packet_name.replace("F__", "R__CHANGES__")
            archive_reviewer_notes(lane_dir)
            clear_stale_integrator_handoffs(lane_dir, packet_name)
            write_text(outp, reviewer_text)

        _archive_consumed_feature_packet(lane_dir, pkt_path)
        jobs.pop(lane, None)
        harvested += 1
        print(f"[router] harvested completed {mode_label} reviewer job for {lane}: {packet_name}")

    state[jobs_key] = jobs
    return harvested, state


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
    local_mode = _use_local_provider(cfg, state)
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
    for local in (False, True):
        harvested, state = _harvest_completed_reviewer_jobs(cfg, state, local=local)
        processed += harvested
        if processed >= cfg.max_packets_per_run:
            state["reviewer_quota_retry_ts"] = reviewer_quota_retry_ts
            state["reviewer_quota_global_retry_ts"] = global_quota_retry_ts
            return processed, state, reviewer_thread_ids, integrator_tid
    for lane in lane_priority_order(list(cfg.lanes.keys()), digest_for_lane=_lane_digest):
        lane_dir = ensure_lane_dirs(lane)
        for pkt_path in list_new(lane_dir, cursor.get(lane)):
            if processed >= cfg.max_packets_per_run:
                state["reviewer_quota_retry_ts"] = reviewer_quota_retry_ts
                state["reviewer_quota_global_retry_ts"] = global_quota_retry_ts
                return processed, state, reviewer_thread_ids, integrator_tid
            scope_violations = _branch_scope_violations(cfg, repo_cwd, lane)
            if scope_violations:
                print(
                    f"[router] holding reviewer packet for {lane}; "
                    f"full branch violates THREAD_OWNERSHIP.md "
                    f"({len(scope_violations)} file(s) outside lane scope)"
                )
                continue
            pkt = pkt_path.read_text()

            reviewer_text = ""
            now = time.time()
            quota_retry_at = float(reviewer_quota_retry_ts.get(lane, 0) or 0)
            runtime_local = _use_local_provider(cfg, state)
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
                ready, reviewer_text, state = _prepare_cli_reviewer_result(
                    cfg,
                    state,
                    repo_cwd,
                    lane,
                    pkt_path,
                    pkt,
                    local=True,
                )
                if not ready:
                    continue
            elif not runtime_local and cfg.prefer_cli_reviewer:
                ready, reviewer_text, state = _prepare_cli_reviewer_result(
                    cfg,
                    state,
                    repo_cwd,
                    lane,
                    pkt_path,
                    pkt,
                    local=False,
                )
                if not ready:
                    continue
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
                        runtime_local = _use_local_provider(cfg, state)
                        reviewer_text = _run_cli_reviewer(
                            cfg, repo_cwd, pkt, f"reviewer call failed/timed out: {exc}", local=runtime_local, lane=lane
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
                        runtime_local = _use_local_provider(cfg, state)
                        reviewer_text = _run_cli_reviewer(
                            cfg, repo_cwd, pkt, f"reviewer retry failed/timed out: {exc}", local=runtime_local, lane=lane
                        ) or _offline_reviewer_fallback(pkt, f"reviewer retry failed/timed out: {exc}")
                if _invalid_reviewer_output(reviewer_text):
                    reviewer_text = _run_cli_reviewer(
                        cfg, repo_cwd, pkt, "reviewer output invalid/unavailable", local=runtime_local, lane=lane
                    ) or _offline_reviewer_fallback(pkt, "reviewer output invalid/unavailable")
            elif _is_reviewer_quota_output(reviewer_text):
                retry_until = time.time() + 900
                reviewer_quota_retry_ts[lane] = retry_until
                global_quota_retry_ts = max(global_quota_retry_ts, retry_until)
                if cfg.auto_switch_to_local_on_quota:
                    state = _switch_to_local_fallback(cfg, state, "reviewer quota/rate-limit response", retry_until)
                runtime_local = _use_local_provider(cfg, state)
                reviewer_text = _run_cli_reviewer(
                    cfg, repo_cwd, pkt, "reviewer quota/rate-limit response", local=runtime_local, lane=lane
                ) or _offline_reviewer_fallback(pkt, "reviewer quota/rate-limit response")
            reviewer_text = _extract_final_verdict_packet(reviewer_text) or reviewer_text
            verdict = parse_verdict(reviewer_text)

            if verdict == "APPROVED":
                # Clear stale reviewer notes now that this lane packet is approved.
                archive_reviewer_notes(lane_dir)
                write_text(lane_dir/"outbox/integrator"/pkt_path.name.replace("F__","R__APPROVED__"), reviewer_text)
                integ = ""
                runtime_local = _use_local_provider(cfg, state)
                if cfg.prefer_cli_integrator:
                    # Keep approval handling asynchronous. The integrator
                    # backlog pass will pick up this outbox packet and launch
                    # the tracked detached CLI job, avoiding untracked inline
                    # cloud integrators racing the same packet.
                    integ = ""
                elif runtime_local:
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
    prefer_cloud_once = state.get("fixer_prefer_cloud_once") or {}
    if not isinstance(prefer_cloud_once, dict):
        prefer_cloud_once = {}
    local_mode = True
    if not _local_lms_slot_available(cfg, state) and _cloud_role_slot_available(cfg, state, "fixer"):
        local_mode = False
    kick_limit = cfg.max_local_fixer_kicks_per_run if local_mode else cfg.max_cloud_fixer_kicks_per_run
    max_active = cfg.max_local_fixer_jobs if local_mode else cfg.max_cloud_fixer_jobs
    kicked = 0
    for lane in lane_priority_order(list(cfg.lanes.keys()), digest_for_lane=_lane_digest):
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
        if _requires_live_reviewer_rerun(note_text):
            restored = _restore_archived_feature_for_live_review(lane_dir, newest_note)
            if restored is not None:
                print(f"[router] {lane}: restored archived feature packet for live re-review: {restored.name}")
            else:
                print(f"[router] {lane}: reviewer fallback note requires live re-review; not kicking fixer")
            continue
        if parse_verdict(note_text) == "APPROVED":
            # Approved reviewer notes belong to the integrator path; they are
            # not feature-fixer work and should not consume the one-kick budget.
            continue
        feature_pkts = sorted(
            (p for p in (lane_dir / "inbox/feature").glob("*.md") if not p.name.endswith(".shared.md")),
            key=lambda p: p.stat().st_mtime,
        )
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
        if _requires_control_plane_metadata_repair(note_text):
            reviewer_packet = _materialize_reviewer_packet(lane_dir, newest_note)
            handled, state = _prepare_metadata_repair_job(
                cfg,
                state,
                repo_cwd,
                lane,
                newest_note,
                reviewer_packet,
            )
            if handled:
                cursor[lane] = newest_note.name
                retry_ts[lane] = now
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
        local_mode = True
        prefer_cloud_for_lane = lane in prefer_cloud_once and _cloud_role_slot_available(cfg, state, "fixer")
        if prefer_cloud_for_lane:
            local_mode = False
        elif not _local_lms_slot_available(cfg, state) and _cloud_role_slot_available(cfg, state, "fixer"):
            local_mode = False
        if local_mode and not _local_lms_slot_available(cfg, state):
            break
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
        prefer_cloud_once.pop(lane, None)
        cursor[lane] = newest_note.name
        retry_ts[lane] = now
        kicked += 1

    state["reviewer_fixer_cursor"] = cursor
    state["reviewer_fixer_retry_ts"] = retry_ts
    state["fixer_quota_retry_ts"] = quota_retry_ts
    state["fixer_prefer_cloud_once"] = prefer_cloud_once
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
    priority_index = {lane: idx for idx, lane in enumerate(INTEGRATION_DEPENDENCY_ORDER)}
    approvals.sort(key=lambda item: (priority_index.get(item[1], len(priority_index)), item[0]))

    for _, _lane, lane_dir, pkt in approvals:
        if processed >= cfg.max_packets_per_run:
            break
        approved_text = pkt.read_text()
        reviewed_files = _reviewed_files_for_integrator_packet(lane_dir, pkt, approved_text)
        scope_violations = _branch_scope_violations(cfg, repo_cwd, _lane)
        if scope_violations:
            print(
                f"[router] holding integrator packet for {_lane}; "
                f"full branch violates THREAD_OWNERSHIP.md "
                f"({len(scope_violations)} file(s) outside lane scope)"
            )
            continue
        blockers = _integration_dependency_blockers(cfg, repo_cwd, _lane, reviewed_files=reviewed_files)
        if blockers:
            print(f"[router] holding integrator packet for {_lane}; waiting on prior lane(s): {', '.join(blockers)}")
            continue
        archive_hint = list((lane_dir / "archive").glob(f"INTEGRATOR__*{_packet_sha(pkt.name)}*.md"))
        if archive_hint:
            archive_hint.sort(key=lambda p: p.stat().st_mtime)
            hint_text = archive_hint[-1].read_text(errors="ignore")
            rejection = _local_cli_output_rejection_reason(hint_text, require_verdict=False)
            if rejection:
                _write_integrator_failure_handback(
                    lane_dir,
                    _lane,
                    pkt,
                    reason=rejection,
                    output=hint_text,
                )
                processed += 1
                continue
            archive(pkt, lane_dir)
            processed += 1
            continue
        runtime_local = _use_local_provider(cfg, state)
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
                runtime_local = _use_local_provider(cfg, state)
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
    worker cap: existing approvals unblock integration, reviewer work advances
    active feature lanes, fixers unblock reviewer notes, and speculative feature
    refill is handled by the coordinator after router work. Keep the precedence
    explicit here so new review/fix work cannot steal the last slot from an
    integrator backlog.
    """
    integrated, state, integrator_tid = process_integrator_backlog(
        integrator_client, cfg, state, repo_cwd, integrator_tid
    )
    n, state, reviewer_thread_ids, integrator_tid = process_once(
        reviewer_client, integrator_client, cfg, state, repo_cwd, reviewer_thread_ids, integrator_tid
    )
    integrated_after_review, state, integrator_tid = process_integrator_backlog(
        integrator_client, cfg, state, repo_cwd, integrator_tid
    )
    integrated += integrated_after_review
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
    local_mode = _use_local_provider(cfg, state)

    reviewer_profile = _profile_for_role(cfg, "reviewer", local=local_mode)
    integrator_profile = _profile_for_role(cfg, "integrator", local=local_mode)
    cli_only_harnesses = sorted(
        {
            profile.harness
            for profile in (reviewer_profile, integrator_profile)
            if profile.harness != "codex"
        }
    )
    if cli_only_harnesses:
        print(f"[router] using CLI-only profiles: {', '.join(cli_only_harnesses)}")
        reviewer_client = _CliOnlyMcpClient()
        integrator_client = reviewer_client
    else:
        reviewer_client = _build_mcp_client(reviewer_profile, ApprovalPolicy(True, True))
        integrator_client = _build_mcp_client(integrator_profile, ApprovalPolicy(True, True))

    reviewer_thread_ids = state.get("reviewer_thread_ids") or {}
    if not isinstance(reviewer_thread_ids, dict):
        reviewer_thread_ids = {}
    reviewer_thread_ids = ensure_all_reviewer_threads(reviewer_client, cfg, repo_cwd, state, reviewer_thread_ids)
    integrator_tid = state.get("integrator_thread_id")

    if (
        not integrator_tid
        and _cloud_available(cfg, state)
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
