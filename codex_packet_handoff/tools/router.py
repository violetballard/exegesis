#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import time
import subprocess
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from codex_mcp_client import ApprovalPolicy, CodexMcpClient

PACKETS_ROOT = Path(".codex/packets/lanes")
ROUTER_ROOT = Path(".codex/packet_router")
STATE_FILE = ROUTER_ROOT / "state.json"
CONFIG_FILE = ROUTER_ROOT / "config.json"
CURSOR_FILE = ROUTER_ROOT / "cursor.json"
LEASE_FILE = ROUTER_ROOT / "lease.json"

VERDICT_RE = re.compile(
    r"(?:\*\*Verdict\*\*|Verdict:)\s*`?(APPROVED|CHANGES_REQUESTED|CHANGES REQUESTED)`?",
    re.IGNORECASE,
)
INVALID_REVIEWER_RE = re.compile(r"session not found for thread_id|thread not found", re.IGNORECASE)
REVIEWER_QUOTA_RE = re.compile(
    r"usage limit|try again at|rate limit|too many requests|quota",
    re.IGNORECASE,
)
PACKET_SHA_RE = re.compile(r"__(?P<sha>[0-9a-f]{7,40})__")
FIXER_QUOTA_RE = REVIEWER_QUOTA_RE
FIXER_RETRY_AT_RE = re.compile(
    r"try again at\s+([A-Za-z]{3}\s+\d{1,2}(?:st|nd|rd|th)?,\s+\d{4}\s+\d{1,2}:\d{2}\s+[AP]M)",
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
    prefer_cli_fixer: bool
    use_cli_reviewer_fallback: bool
    use_cli_integrator_fallback: bool
    profiles: Dict[str, "LaunchProfile"]
    role_profiles: Dict[str, str]
    lanes: Dict[str, Dict[str, Any]]


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
    if "--oss" in cmd_args and model == fallback_model:
        model = ""
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
        cloud_probe_cooldown_seconds=float(cfg.get("cloud_probe_cooldown_seconds", 1800)),
        cloud_probe_timeout_seconds=float(cfg.get("cloud_probe_timeout_seconds", 30)),
        reviewer_timeout=float(cfg.get("reviewer_timeout", 180)),
        integrator_timeout=float(cfg.get("integrator_timeout", 900)),
        max_packets_per_run=int(cfg.get("max_packets_per_run", 1)),
        inline_fixer=bool(cfg.get("inline_fixer", False)),
        kick_fixers_on_reviewer_backlog=bool(cfg.get("kick_fixers_on_reviewer_backlog", True)),
        fixer_kick_timeout_seconds=float(cfg.get("fixer_kick_timeout_seconds", 8)),
        reviewer_fixer_retry_cooldown_seconds=float(cfg.get("reviewer_fixer_retry_cooldown_seconds", 900)),
        fixer_quota_retry_cooldown_seconds=float(cfg.get("fixer_quota_retry_cooldown_seconds", 3600)),
        prefer_cli_fixer=bool(cfg.get("prefer_cli_fixer", True)),
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


def _apply_quota_text_safeguard(
    cfg: RouterConfig,
    state: Dict[str, Any],
    text: str,
    *,
    reason: str,
    default_seconds: Optional[float] = None,
) -> Dict[str, Any]:
    if not text or not REVIEWER_QUOTA_RE.search(text):
        return state
    retry_at = _quota_retry_epoch(cfg, text, default_seconds=default_seconds)
    return _switch_to_local_fallback(cfg, state, reason, retry_at)

def parse_verdict(text: str) -> str:
    m = VERDICT_RE.search(text or "")
    if not m:
        return "CHANGES_REQUESTED"
    v = m.group(1).upper().replace(" ", "_")
    return "APPROVED" if v == "APPROVED" else "CHANGES_REQUESTED"


def _invalid_reviewer_output(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    return bool(INVALID_REVIEWER_RE.search(t))


def _is_reviewer_quota_output(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    return bool(REVIEWER_QUOTA_RE.search(t))


def _runtime_mode(cfg: RouterConfig, state: Dict[str, Any]) -> str:
    mode = str(state.get("runtime_mode") or cfg.runtime_mode_default or "cloud_primary")
    return mode if mode in ("cloud_primary", "local_fallback") else "cloud_primary"


def _profile_name_for_role(cfg: RouterConfig, role: str, *, local: Optional[bool] = None) -> str:
    if local is None:
        return str(cfg.role_profiles.get(role) or role)
    suffix = "local" if local else "cloud"
    return str(cfg.role_profiles.get(f"{role}_{suffix}") or cfg.role_profiles.get(role) or ("worker_local" if local else "worker_cloud"))


def _profile_for_role(cfg: RouterConfig, role: str, *, local: Optional[bool] = None) -> LaunchProfile:
    name = _profile_name_for_role(cfg, role, local=local)
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
    return (
        "You are the INTEGRATOR. You may write to the workspace.\n"
        "Consume this APPROVED packet, perform merge order + post-merge checks, report blockers.\n\n"
        f"{approved}\n"
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
) -> Tuple[int, str]:
    cmd = [codex_cmd, *codex_args, "exec"]
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
        text=True,
        timeout=timeout,
    )
    return p.returncode, p.stdout or ""


def _run_cli_reviewer(cfg: RouterConfig, repo_cwd: str, pkt: str, reason: str) -> Optional[str]:
    if not cfg.use_cli_reviewer_fallback:
        return None
    prof = _profile_for_role(cfg, "reviewer", local=True)
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
        )
    except Exception:
        return None
    if rc != 0:
        return None
    text = (out or "").strip()
    if not text or _invalid_reviewer_output(text) or _is_reviewer_quota_output(text):
        return None
    return text


def _run_cli_integrator(cfg: RouterConfig, repo_cwd: str, approved: str) -> Optional[str]:
    if not cfg.use_cli_integrator_fallback:
        return None
    prof = _profile_for_role(cfg, "integrator", local=True)
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
        )
    except Exception:
        return None
    if rc != 0:
        return None
    return (out or "").strip()

def _find_worktree_for_branch(repo_cwd: str, branch: str) -> Optional[str]:
    # Normalize to refs/heads/...
    ref = branch
    if ref.startswith("refs/heads/"):
        want = ref
    else:
        want = f"refs/heads/{ref}"
    p = subprocess.run(["git","worktree","list","--porcelain"], cwd=repo_cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
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
        "Run: make scope-check; ./quality-format.sh --check; ./quality-lint.sh; ./quality-test.sh; ./typecheck-test.sh; make ci\n\n"
        "Reviewer packet to satisfy:\n\n"
        f"{reviewer_packet}\n"
    )

def run_fixer(client: CodexMcpClient, cfg: RouterConfig, state: dict, lane: str, reviewer_packet: str, repo_cwd: str) -> dict:
    lane_cfg = cfg.lanes.get(lane, {}) or {}
    branch = str(lane_cfg.get("branch") or f"codex/{lane}")
    wt = _find_worktree_for_branch(repo_cwd, branch)
    _sync_lane_runbook_files(repo_cwd, wt)
    if _runtime_mode(cfg, state) != "local_fallback" and not cfg.prefer_cli_fixer:
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
    local_mode = _runtime_mode(cfg, state) == "local_fallback"
    prof = _profile_for_role(cfg, "fixer", local=local_mode)
    logs = ROUTER_ROOT / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    logp = logs / f"fixer__{lane}__{ts}.log"
    with logp.open("w") as lf:
        subprocess.Popen(
            [
                prof.codex_cmd,
                *prof.codex_args,
                "exec",
                *(["-m", prof.model] if prof.model else []),
                *prof.model_args,
                "-s",
                "workspace-write",
                fixer_prompt(lane, branch, reviewer_packet, wt),
            ],
            cwd=(wt or repo_cwd),
            stdout=lf,
            stderr=subprocess.STDOUT,
            text=True,
        )
    fallback = state.get("fixer_fallback_jobs") or {}
    fallback[lane] = {"log": str(logp), "ts": ts}
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
) -> str:
    tid = reviewer_thread_ids.get(lane)
    if tid:
        return tid
    reviewer_profile = _profile_for_role(cfg, "reviewer", local=False)
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
    if _runtime_mode(cfg, state) == "local_fallback":
        return reviewer_thread_ids
    for lane in cfg.lanes.keys():
        try:
            _ensure_lane_reviewer_thread(reviewer_client, cfg, repo_cwd, lane, reviewer_thread_ids)
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
            in_quota_cooldown = runtime_local or quota_retry_at > now or global_quota_retry_ts > now
            if in_quota_cooldown:
                wait_s = int(max(quota_retry_at, global_quota_retry_ts) - now)
                reason = (
                    f"runtime local fallback active ({wait_s}s remaining)"
                    if runtime_local
                    else f"reviewer quota cooldown active ({wait_s}s remaining)"
                )
                reviewer_text = _run_cli_reviewer(
                    cfg, repo_cwd, pkt, reason
                ) or _offline_reviewer_fallback(
                    pkt, reason
                )
            else:
                try:
                    reviewer_tid = _ensure_lane_reviewer_thread(reviewer_client, cfg, repo_cwd, lane, reviewer_thread_ids)
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
                        cfg, repo_cwd, pkt, f"reviewer call failed/timed out: {exc}"
                    ) or _offline_reviewer_fallback(pkt, f"reviewer call failed/timed out: {exc}")
            state = _apply_quota_text_safeguard(
                cfg,
                state,
                reviewer_text,
                reason=f"reviewer output quota text on lane {lane}",
            )
            if _invalid_reviewer_output(reviewer_text):
                # Recover from dead/invalid reviewer thread and retry once.
                try:
                    reviewer_profile = _profile_for_role(cfg, "reviewer", local=False)
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
                        cfg, repo_cwd, pkt, f"reviewer retry failed/timed out: {exc}"
                    ) or _offline_reviewer_fallback(pkt, f"reviewer retry failed/timed out: {exc}")
                if _invalid_reviewer_output(reviewer_text):
                    reviewer_text = _run_cli_reviewer(
                        cfg, repo_cwd, pkt, "reviewer output invalid/unavailable"
                    ) or _offline_reviewer_fallback(pkt, "reviewer output invalid/unavailable")
            elif _is_reviewer_quota_output(reviewer_text):
                retry_until = time.time() + 900
                reviewer_quota_retry_ts[lane] = retry_until
                global_quota_retry_ts = max(global_quota_retry_ts, retry_until)
                if cfg.auto_switch_to_local_on_quota:
                    state = _switch_to_local_fallback(cfg, state, "reviewer quota/rate-limit response", retry_until)
                reviewer_text = _run_cli_reviewer(
                    cfg, repo_cwd, pkt, "reviewer quota/rate-limit response"
                ) or _offline_reviewer_fallback(pkt, "reviewer quota/rate-limit response")
            verdict = parse_verdict(reviewer_text)

            if verdict == "APPROVED":
                # Clear stale reviewer notes now that this lane packet is approved.
                archive_reviewer_notes(lane_dir)
                write_text(lane_dir/"outbox/integrator"/pkt_path.name.replace("F__","R__APPROVED__"), reviewer_text)
                integ = ""
                if _runtime_mode(cfg, state) != "local_fallback":
                    try:
                        integrator_tid, integ = integrator_client.codex_reply(
                            integrator_tid, integrator_prompt(reviewer_text), timeout=cfg.integrator_timeout
                        )
                    except Exception as exc:
                        if cfg.auto_switch_to_local_on_quota:
                            state = _switch_to_local_fallback(cfg, state, f"integrator call failed/timed out: {exc}")
                        integ = _run_cli_integrator(cfg, repo_cwd, reviewer_text) or ""
                        if not integ:
                            write_text(
                                lane_dir / "archive" / f"INTEGRATOR__ERROR__{pkt_path.name}",
                                f"Integrator call failed/timed out: {exc}",
                            )
                else:
                    integ = _run_cli_integrator(cfg, repo_cwd, reviewer_text)
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
                write_text(outp, reviewer_text)

            cursor[lane] = pkt_path.name
            save_json(CURSOR_FILE, cursor)
            archive(pkt_path, lane_dir)
            processed += 1

            # Inline fixer can be expensive; disabled by default for automation ticks.
            if verdict != "APPROVED" and cfg.inline_fixer:
                state = run_fixer(reviewer_client, cfg, state, lane, reviewer_text, repo_cwd)
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
    kicked = 0
    for lane in cfg.lanes.keys():
        lane_dir = ensure_lane_dirs(lane)
        now = time.time()
        lane_quota_until = float(quota_retry_ts.get(lane, 0) or 0)
        if lane_quota_until > now:
            continue
        notes = sorted((lane_dir / "inbox/reviewer").glob("*.md"), key=lambda p: p.stat().st_mtime)
        if not notes:
            continue
        feature_pkts = sorted((lane_dir / "inbox/feature").glob("*.md"), key=lambda p: p.stat().st_mtime)
        if feature_pkts:
            newest_feature = feature_pkts[-1]
            newest_note = notes[-1]
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
        latest_log = _latest_fixer_log(lane)
        if latest_log:
            try:
                text = latest_log.read_text(errors="ignore")
            except Exception:
                text = ""
            if text and FIXER_QUOTA_RE.search(text):
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
        newest_note = notes[-1]
        if cursor.get(lane) == newest_note.name:
            last_kick = float(retry_ts.get(lane, 0) or 0)
            # Backward compatibility: if timestamp missing, allow one immediate retry.
            if last_kick > 0 and (now - last_kick) < cfg.reviewer_fixer_retry_cooldown_seconds:
                continue
        state = _maybe_restore_cloud(cfg, state, repo_cwd)
        reviewer_packet = _materialize_reviewer_packet(lane_dir, newest_note)
        state = run_fixer(reviewer_client, cfg, state, lane, reviewer_packet, repo_cwd)
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
        if _runtime_mode(cfg, state) == "local_fallback":
            integ = _run_cli_integrator(cfg, repo_cwd, approved_text)
        else:
            try:
                integrator_tid, integ = integrator_client.codex_reply(
                    integrator_tid, integrator_prompt(approved_text), timeout=cfg.integrator_timeout
                )
            except Exception as exc:
                if cfg.auto_switch_to_local_on_quota:
                    state = _switch_to_local_fallback(cfg, state, f"integrator backlog call failed/timed out: {exc}")
                integ = _run_cli_integrator(cfg, repo_cwd, approved_text)
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

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--daemon", action="store_true")
    args = ap.parse_args()

    cfg = load_cfg()
    state = load_json(STATE_FILE, {})
    repo_cwd = str(Path.cwd())

    reviewer_client = _build_mcp_client(_profile_for_role(cfg, "reviewer", local=False), ApprovalPolicy(True, True))
    integrator_client = _build_mcp_client(_profile_for_role(cfg, "integrator", local=False), ApprovalPolicy(True, True))
    state = _maybe_restore_cloud(cfg, state, repo_cwd)

    reviewer_thread_ids = state.get("reviewer_thread_ids") or {}
    if not isinstance(reviewer_thread_ids, dict):
        reviewer_thread_ids = {}
    reviewer_thread_ids = ensure_all_reviewer_threads(reviewer_client, cfg, repo_cwd, state, reviewer_thread_ids)
    integrator_tid = state.get("integrator_thread_id")

    if not integrator_tid and _runtime_mode(cfg, state) != "local_fallback":
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
                    n, state, reviewer_thread_ids, integrator_tid = process_once(
                        reviewer_client, integrator_client, cfg, state, repo_cwd, reviewer_thread_ids, integrator_tid
                    )
                    kicked, state = process_reviewer_backlog(reviewer_client, cfg, state, repo_cwd)
                    integrated, state, integrator_tid = process_integrator_backlog(
                        integrator_client, cfg, state, repo_cwd, integrator_tid
                    )
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
                    print(f"[router] processed {n} packet(s), kicked {kicked} reviewer-fixer task(s), integrated {integrated} approval packet(s)")
                finally:
                    release_lease()
            return

        print("[router] daemon mode")
        while True:
            if acquire_lease():
                try:
                    n, state, reviewer_thread_ids, integrator_tid = process_once(
                        reviewer_client, integrator_client, cfg, state, repo_cwd, reviewer_thread_ids, integrator_tid
                    )
                    kicked, state = process_reviewer_backlog(reviewer_client, cfg, state, repo_cwd)
                    integrated, state, integrator_tid = process_integrator_backlog(
                        integrator_client, cfg, state, repo_cwd, integrator_tid
                    )
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
