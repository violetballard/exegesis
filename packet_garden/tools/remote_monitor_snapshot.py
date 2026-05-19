#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable
DAEMON_CTL = [PYTHON, "packet_garden/tools/daemon_ctl.py", "status"]
STATUS_CMD = [PYTHON, "packet_garden/tools/status.py"]
MONITOR_CMD = [PYTHON, "packet_garden/tools/daemon_monitor.py"]
PROCESS_MATCH_RE = re.compile(r"codex exec|opencode run|packet_garden/tools/agents_coordinator.py")
KEY_VALUE_RE = re.compile(r"^(?P<key>[A-Za-z0-9_.-]+)=(?P<value>.*)$")
TOTALS_RE = re.compile(
    r"Totals:\s+pending_feature=(?P<pending>\d+)\s+"
    r"reviewer_notes=(?P<reviewer>\d+)\s+"
    r"approved_for_integrator=(?P<approved>\d+)\s+"
    r"waiting_feature_update=(?P<waiting>\d+)\s+"
    r"ready_for_reemit=(?P<reemit>\d+)"
)
LANE_ROW_RE = re.compile(
    r"^(?P<lane>feat-[A-Za-z0-9_-]+)\s+"
    r"(?P<pending>\d+)\s+(?P<review>\d+)\s+(?P<approved>\d+)\s+"
    r"(?P<state>[A-Za-z0-9_-]+)\s+"
)
MILESTONE_HEADING_RE = re.compile(r"^## Milestone (?P<number>[1-5])(?P<suffix>[A-Z]?):\s*(?P<title>.+)$")
MILESTONE_STATUS_RE = re.compile(r"^Status:\s*(?P<status>.+)$")
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|authorization|bearer|secret|password)\s*[:=]\s*[^\s]+"),
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"(?i)(mistral|openai|anthropic|nanonets)[A-Za-z0-9_-]{20,}"),
]
PATH_PATTERN = re.compile(r"/Users/[^\s'\"]+")
ROUTER_STATE = REPO_ROOT / ".codex/packet_router/state.json"
ROUTER_CONFIG = REPO_ROOT / ".codex/packet_router/config.json"
FEATURE_STATE = REPO_ROOT / ".codex/feature_runner/state.json"
DAEMON_PID_FILE = REPO_ROOT / ".codex/packet_coordinator/daemon.pid"
DAEMON_LEASE_FILE = REPO_ROOT / ".codex/packet_coordinator/lease.json"
DAEMON_LEASE_FRESH_SECONDS = 3600
ROADMAP = REPO_ROOT / "ROADMAP.md"


@dataclass(frozen=True)
class CommandResult:
    rc: int
    output: str
    timed_out: bool = False


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sanitize_text(text: str, *, max_lines: int = 220, max_chars: int = 24000) -> str:
    scrubbed = text[:max_chars]
    for pattern in SECRET_PATTERNS:
        scrubbed = pattern.sub(lambda m: f"{m.group(1) if m.groups() else 'secret'}=<redacted>", scrubbed)
    scrubbed = PATH_PATTERN.sub("<path>", scrubbed)
    lines = scrubbed.splitlines()[:max_lines]
    return "\n".join(lines)


def _run_command(args: Sequence[str], *, timeout: float) -> CommandResult:
    try:
        proc = subprocess.run(
            list(args),
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout if isinstance(exc.stdout, str) else ""
        return CommandResult(rc=124, output=_sanitize_text(output), timed_out=True)
    except Exception as exc:
        return CommandResult(rc=1, output=f"error={type(exc).__name__}: {exc}")
    return CommandResult(rc=proc.returncode, output=_sanitize_text(proc.stdout or ""))


def _parse_key_values(output: str) -> Dict[str, str]:
    parsed: Dict[str, str] = {}
    for line in output.splitlines():
        match = KEY_VALUE_RE.match(line.strip())
        if match:
            parsed[match.group("key")] = match.group("value")
    return parsed


def _parse_pipeline(output: str) -> Dict[str, Any]:
    totals: Dict[str, int] = {}
    lanes: List[Dict[str, Any]] = []
    for line in output.splitlines():
        total_match = TOTALS_RE.search(line)
        if total_match:
            totals = {
                "pending_feature": int(total_match.group("pending")),
                "reviewer_notes": int(total_match.group("reviewer")),
                "approved_for_integrator": int(total_match.group("approved")),
                "waiting_feature_update": int(total_match.group("waiting")),
                "ready_for_reemit": int(total_match.group("reemit")),
            }
            continue
        lane_match = LANE_ROW_RE.match(line)
        if lane_match:
            lanes.append(
                {
                    "lane": lane_match.group("lane"),
                    "pending_feature": int(lane_match.group("pending")),
                    "reviewer_notes": int(lane_match.group("review")),
                    "approved_for_integrator": int(lane_match.group("approved")),
                    "state": lane_match.group("state"),
                }
            )
    return {"totals": totals, "lanes": lanes}


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _read_int_file(path: Path) -> int:
    try:
        return int(path.read_text().strip() or "0")
    except Exception:
        return 0


def _daemon_running_fallback() -> bool:
    lease = _load_json(DAEMON_LEASE_FILE, {})
    if not isinstance(lease, dict):
        lease = {}
    try:
        lease_pid = int(lease.get("pid") or 0)
    except (TypeError, ValueError):
        lease_pid = 0
    try:
        lease_ts = float(lease.get("ts") or 0)
    except (TypeError, ValueError):
        lease_ts = 0
    pid = _read_int_file(DAEMON_PID_FILE) or lease_pid
    if not pid or not _pid_alive(pid):
        return False
    if lease_pid != pid or not lease_ts:
        return False
    return (time.time() - lease_ts) <= DAEMON_LEASE_FRESH_SECONDS


def _lane_from_job_key(key: str, job: Mapping[str, Any]) -> str:
    lane = str(job.get("lane") or "")
    if lane:
        return lane
    return key.split(":", 1)[0]


def _cloud_profile_tier(profile: str) -> str:
    name = str(profile or "").strip()
    if not name:
        return ""
    if name == "integrator_cloud" or "high" in name:
        return "heavy"
    if "medium" in name:
        return "medium"
    if name == "worker_cloud" or "low" in name:
        return "light"
    return name


def _profile_name_for_job(cfg: Mapping[str, Any], role: str, *, provider: str, lane: str) -> str:
    local = provider == "local"
    suffix = "local" if local else "cloud"
    lanes = cfg.get("lanes") if isinstance(cfg.get("lanes"), dict) else {}
    lane_cfg = lanes.get(lane) if isinstance(lanes, dict) else {}
    if not isinstance(lane_cfg, dict):
        lane_cfg = {}
    role_profiles = cfg.get("role_profiles") if isinstance(cfg.get("role_profiles"), dict) else {}
    return str(
        lane_cfg.get(f"{role}_{suffix}_profile")
        or lane_cfg.get(f"{role}_profile")
        or role_profiles.get(f"{role}_{suffix}")
        or role_profiles.get(role)
        or ("worker_local" if local else "worker_cloud")
    )


def _add_lane_placement(
    placements: Dict[str, List[Dict[str, str]]],
    lane: str,
    *,
    provider: str,
    role: str,
    pid: int,
    profile: str = "",
) -> None:
    if not lane or not _pid_alive(pid):
        return
    item = {"provider": provider, "role": role, "pid": str(pid)}
    if profile:
        item["profile"] = profile
    if provider == "cloud":
        tier = _cloud_profile_tier(profile)
        if tier:
            item["tier"] = tier
    placements.setdefault(lane, []).append(item)


def _lane_placements() -> Dict[str, List[Dict[str, str]]]:
    placements: Dict[str, List[Dict[str, str]]] = {}
    feature_state = _load_json(FEATURE_STATE, {})
    feature_lanes = feature_state.get("lanes") if isinstance(feature_state, dict) else {}
    if isinstance(feature_lanes, dict):
        for lane, lane_state in feature_lanes.items():
            if not isinstance(lane_state, dict):
                continue
            if str(lane_state.get("status") or "") != "direct_exec_running":
                continue
            mode = str(lane_state.get("mode") or "")
            provider = "cloud" if mode == "cloud_primary" else "local" if mode == "local_fallback" else mode or "unknown"
            _add_lane_placement(
                placements,
                str(lane),
                provider=provider,
                role="feature",
                pid=int(lane_state.get("pid") or 0),
                profile=str(lane_state.get("profile") or ""),
            )

    router_state = _load_json(ROUTER_STATE, {})
    router_cfg = _load_json(ROUTER_CONFIG, {})
    if not isinstance(router_state, dict):
        return placements
    if not isinstance(router_cfg, dict):
        router_cfg = {}

    job_groups = [
        ("local_reviewer_jobs", "local", "reviewer"),
        ("cloud_reviewer_jobs", "cloud", "reviewer"),
        ("local_integrator_jobs", "local", "integrator"),
        ("cloud_integrator_jobs", "cloud", "integrator"),
    ]
    for key, provider, role in job_groups:
        jobs = router_state.get(key)
        if not isinstance(jobs, dict):
            continue
        for job_key, job in jobs.items():
            if not isinstance(job, dict):
                continue
            lane = _lane_from_job_key(str(job_key), job)
            _add_lane_placement(
                placements,
                lane,
                provider=provider,
                role=role,
                pid=int(job.get("pid") or 0),
                profile=_profile_name_for_job(router_cfg, role, provider=provider, lane=lane),
            )

    fixer_jobs = router_state.get("fixer_fallback_jobs")
    if isinstance(fixer_jobs, dict):
        for lane, job in fixer_jobs.items():
            if not isinstance(job, dict):
                continue
            provider = "local" if bool(job.get("local")) else "cloud"
            _add_lane_placement(
                placements,
                str(lane),
                provider=provider,
                role="fixer",
                pid=int(job.get("pid") or 0),
                profile=_profile_name_for_job(router_cfg, "fixer", provider=provider, lane=str(lane)),
            )
    return placements


def _count_active_pid_jobs(jobs: Any, *, local: bool | None = None) -> int:
    if not isinstance(jobs, dict):
        return 0
    count = 0
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        if local is not None and bool(job.get("local")) != local:
            continue
        try:
            pid = int(job.get("pid") or 0)
        except (TypeError, ValueError):
            pid = 0
        if _pid_alive(pid):
            count += 1
    return count


def _active_feature_mode_count(mode: str) -> int:
    feature_state = _load_json(FEATURE_STATE, {})
    lanes = feature_state.get("lanes") if isinstance(feature_state, dict) else {}
    if not isinstance(lanes, dict):
        return 0
    count = 0
    for lane_state in lanes.values():
        if not isinstance(lane_state, dict):
            continue
        if str(lane_state.get("status") or "") != "direct_exec_running":
            continue
        if str(lane_state.get("mode") or "") != mode:
            continue
        try:
            pid = int(lane_state.get("pid") or 0)
        except (TypeError, ValueError):
            pid = 0
        if _pid_alive(pid):
            count += 1
    return count


def _runtime_fallbacks(
    pipeline: Mapping[str, Any],
    monitor_values: Mapping[str, str],
) -> Dict[str, str]:
    router_state = _load_json(ROUTER_STATE, {})
    router_cfg = _load_json(ROUTER_CONFIG, {})
    if not isinstance(router_state, dict):
        router_state = {}
    if not isinstance(router_cfg, dict):
        router_cfg = {}

    local_cap = int(router_cfg.get("max_total_local_lms_jobs", 4) or 4)
    cloud_cap = int(router_cfg.get("max_total_cloud_jobs", 4) or 4)
    local_jobs = (
        _active_feature_mode_count("local_fallback")
        + _count_active_pid_jobs(router_state.get("local_reviewer_jobs"))
        + _count_active_pid_jobs(router_state.get("local_integrator_jobs"))
        + _count_active_pid_jobs(router_state.get("fixer_fallback_jobs"), local=True)
    )
    cloud_features = _active_feature_mode_count("cloud_primary")
    cloud_reviewers = _count_active_pid_jobs(router_state.get("cloud_reviewer_jobs"))
    cloud_integrators = _count_active_pid_jobs(router_state.get("cloud_integrator_jobs"))
    cloud_fixers = _count_active_pid_jobs(router_state.get("fixer_fallback_jobs"), local=False)
    cloud_total = cloud_features + cloud_reviewers + cloud_integrators + cloud_fixers

    totals = pipeline.get("totals", {}) if isinstance(pipeline, dict) else {}
    approved = int(totals.get("approved_for_integrator", 0) or 0)
    pending = int(totals.get("pending_feature", 0) or 0)
    reviewer = int(totals.get("reviewer_notes", 0) or 0)
    waiting = int(totals.get("waiting_feature_update", 0) or 0)
    reemit = int(totals.get("ready_for_reemit", 0) or 0)
    lanes = pipeline.get("lanes", []) if isinstance(pipeline, dict) else []
    dependency_blocked = sum(
        int(lane.get("approved_for_integrator", 0) or 0)
        for lane in lanes
        if isinstance(lane, dict) and str(lane.get("state") or "") == "integration_blocked"
    )
    runnable_approved = max(0, approved - dependency_blocked)
    if approved and runnable_approved <= 0 and dependency_blocked:
        blocker = (
            f"integration dependency hold "
            f"({dependency_blocked} approved packet(s) waiting on prerequisite lane merges)"
        )
    elif runnable_approved:
        blocker = (
            f"integrator backlog active "
            f"({runnable_approved} packet(s) ready, {dependency_blocked} dependency-held)"
        )
    elif pending:
        blocker = f"reviewer backlog active ({pending} packet(s) pending)"
    elif reviewer or waiting or reemit:
        blocker = f"feature rework needed ({reviewer + waiting + reemit} lane(s) still on reviewer notes)"
    else:
        blocker = "-"

    return {
        "runtime_mode": str(
            monitor_values.get("runtime_mode")
            or router_state.get("runtime_mode")
            or router_cfg.get("runtime_mode_default")
            or "-"
        ),
        "cloud_available": str(
            monitor_values.get("cloud_available")
            if monitor_values.get("cloud_available")
            else router_state.get("cloud_available", "-")
        ),
        "local_lms_jobs": monitor_values.get("local_lms_jobs") or f"{local_jobs} / {local_cap}",
        "cloud_jobs": monitor_values.get("cloud_jobs")
        or (
            f"{cloud_total}/{cloud_cap} total "
            f"(features {cloud_features}, reviewer {cloud_reviewers}, "
            f"integrator {cloud_integrators}, fixer {cloud_fixers})"
        ),
        "active_blocker": monitor_values.get("active_blocker") or blocker,
    }


def _parse_monitor(output: str) -> Dict[str, Any]:
    values: Dict[str, str] = {}
    current_section = ""
    focus_lines: List[str] = []
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.isupper() and len(stripped) < 80:
            current_section = stripped
            continue
        match = KEY_VALUE_RE.match(stripped)
        if match:
            values[match.group("key")] = match.group("value")
        if current_section in {"BACKLOG", "CONTROL PLANE", "COORDINATOR HEARTBEAT", "INTEGRATOR LIVE DISCUSSION"}:
            if len(focus_lines) < 60:
                focus_lines.append(stripped)
    return {
        "values": values,
        "focus": focus_lines,
    }


def _process_view() -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            ["ps", "-wwaxo", "pid=,rss=,etime=,command="],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2.0,
        )
    except Exception:
        return {"available": False, "counts": {}, "processes": []}
    counts = {"daemon": 0, "codex_exec": 0, "opencode": 0}
    processes: List[Dict[str, Any]] = []
    for raw_line in (proc.stdout or "").splitlines():
        if not PROCESS_MATCH_RE.search(raw_line):
            continue
        parts = raw_line.strip().split(None, 3)
        if len(parts) < 4:
            continue
        pid_text, rss_text, etime, command = parts
        try:
            pid = int(pid_text)
            rss_kb = int(rss_text)
        except ValueError:
            continue
        kind = "daemon" if "agents_coordinator.py" in command else "opencode" if "opencode run" in command else "codex_exec"
        counts[kind] = counts.get(kind, 0) + 1
        processes.append({"pid": pid, "kind": kind, "rss_kb": rss_kb, "etime": etime})
    return {"available": proc.returncode == 0, "counts": counts, "processes": processes[:40]}


def _memory_pressure() -> Dict[str, Any]:
    result = _run_command(["memory_pressure"], timeout=4.0)
    if result.rc != 0:
        return {"available": False, "summary": result.output.splitlines()[:3]}
    lines = result.output.splitlines()
    interesting = [line for line in lines if "System-wide memory free percentage" in line or "pressure" in line.lower()]
    return {"available": True, "summary": interesting[:8] or lines[:8]}


def _git_status() -> Dict[str, Any]:
    result = _run_command(["git", "status", "--short", "--untracked-files=no"], timeout=5.0)
    lines = [line for line in result.output.splitlines() if line.strip()]
    return {"clean_tracked": result.rc == 0 and not lines, "tracked_change_count": len(lines)}


def _pause_state() -> Dict[str, Any]:
    path = REPO_ROOT / ".codex/packet_coordinator/pause.json"
    if not path.exists():
        return {"paused": False}
    try:
        data = json.loads(path.read_text() or "{}")
    except Exception:
        data = {}
    return {
        "paused": True,
        "reason": str(data.get("reason") or ""),
        "operator": str(data.get("operator") or ""),
        "updated_at": str(data.get("updated_at") or ""),
    }


def _summary_from(daemon: Mapping[str, str], pipeline: Mapping[str, Any], monitor: Mapping[str, Any]) -> Dict[str, Any]:
    monitor_values = monitor.get("values", {}) if isinstance(monitor, dict) else {}
    totals = pipeline.get("totals", {}) if isinstance(pipeline, dict) else {}
    fallback = _runtime_fallbacks(pipeline, monitor_values)
    daemon_running = str(daemon.get("daemon_running", "False")) == "True" or _daemon_running_fallback()
    return {
        "daemon_running": daemon_running,
        "runtime_mode": fallback["runtime_mode"],
        "cloud_available": fallback["cloud_available"],
        "local_lms_jobs": fallback["local_lms_jobs"],
        "cloud_jobs": fallback["cloud_jobs"],
        "active_blocker": fallback["active_blocker"],
        "pending_feature": int(totals.get("pending_feature", 0) or 0),
        "reviewer_notes": int(totals.get("reviewer_notes", 0) or 0),
        "approved_for_integrator": int(totals.get("approved_for_integrator", 0) or 0),
    }


def _milestone_mark(number: int, status: str) -> str:
    normalized = status.lower()
    if number == 1 and "standing" in normalized:
        return "x"
    if "closed" in normalized or "complete" in normalized:
        return "x"
    if "in progress" in normalized:
        return "~"
    if number in {2, 4} and "planned" in normalized:
        return "~"
    return " "


def _milestone_details(number: int, mark: str) -> List[Dict[str, str]]:
    details: Dict[int, List[Dict[str, str]]] = {
        1: [
            {"mark": "x", "text": "5-pane Textual shell stands as a mockup baseline"},
            {"mark": "x", "text": "Focus model, shortcut bar, and pane boundaries are defined"},
            {"mark": "x", "text": "Shell remains explicitly mockup-only until engine wiring is enabled"},
        ],
        2: [
            {"mark": "~", "text": "Project/document/workflow/basket/inspector interaction contract is defined"},
            {"mark": "~", "text": "Selection model and inspector-follow-selection rule are specified"},
            {"mark": " ", "text": "Product-real pane actions wait on the Milestone 3 engine contract"},
        ],
        3: [
            {"mark": "~", "text": "Persist project/document/basket/session state"},
            {"mark": "~", "text": "Retrieve/search FTS-first through canonical engine contract"},
            {"mark": "~", "text": "Return structured retrieval results suitable for basket promotion"},
            {"mark": "~", "text": "Promote/gather context into basket through engine path"},
            {"mark": "~", "text": "Produce plan/draft/revision through canonical app service"},
            {"mark": "~", "text": "Preview patch/revision proposal"},
            {"mark": "~", "text": "Apply/reject patch through canonical service"},
            {"mark": "~", "text": "CLI can run the MVP loop while Textual remains disabled"},
            {"mark": " ", "text": "One engine-side retrieve -> basket -> plan/revise -> apply path works end to end"},
        ],
        4: [
            {"mark": "~", "text": "Engine state survives repeated sessions"},
            {"mark": "~", "text": "Workflow artifacts are durable/readable enough for real writing sessions"},
            {"mark": "~", "text": "Save-to-project workflow output paths are stable"},
            {"mark": "~", "text": "Minimal audit/proposal logging exists for traceability"},
            {"mark": "~", "text": "Command palette/client actions have corresponding engine contracts"},
            {"mark": "~", "text": "Future Textual client is unblocked by engine contract gaps"},
            {"mark": " ", "text": "Dogfooding can proceed without hand-editing state or relying on mock-only behavior"},
        ],
        5: [
            {"mark": " ", "text": "One clean 60-180 second retrieve -> basket -> plan -> revise -> apply demo path exists"},
            {"mark": " ", "text": "Demo project and repeatable scenario are prepared"},
            {"mark": " ", "text": "App reads as a writing environment rather than a terminal trick"},
        ],
    }
    if mark == "x" and number in {1}:
        return details[number]
    return details.get(number, [])


def _milestone_status() -> List[Dict[str, Any]]:
    fallback = [
        {"number": "1", "title": "Standing shell", "status": "standing", "mark": "x"},
        {"number": "2", "title": "Core pane interactions", "status": "planned", "mark": "~"},
        {"number": "3", "title": "Real workflow loop", "status": "in progress", "mark": "~"},
        {"number": "4", "title": "Dogfooding readiness", "status": "planned", "mark": "~"},
        {"number": "5", "title": "YC demo readiness", "status": "planned", "mark": " "},
    ]
    try:
        lines = ROADMAP.read_text(encoding="utf-8").splitlines()
    except Exception:
        for item in fallback:
            item["details"] = _milestone_details(int(item["number"]), item.get("mark", " "))
        return fallback

    milestones: List[Dict[str, str]] = []
    current: Dict[str, str] | None = None
    for line in lines:
        heading = MILESTONE_HEADING_RE.match(line.strip())
        if heading:
            if heading.group("suffix"):
                if current is not None:
                    milestones.append(current)
                current = None
                continue
            if current is not None:
                milestones.append(current)
            number = int(heading.group("number"))
            current = {
                "number": str(number),
                "title": heading.group("title").strip(),
                "status": "unknown",
                "mark": " ",
            }
            continue
        if current is None:
            continue
        status_match = MILESTONE_STATUS_RE.match(line.strip())
        if status_match:
            status = status_match.group("status").strip()
            current["status"] = status
            current["mark"] = _milestone_mark(int(current["number"]), status)
    if current is not None:
        milestones.append(current)

    by_number = {item.get("number"): item for item in milestones if item.get("number") in {"1", "2", "3", "4", "5"}}
    result = []
    for item in fallback:
        parsed = by_number.get(item["number"])
        selected = dict(parsed if parsed else item)
        selected["details"] = _milestone_details(int(selected["number"]), selected.get("mark", " "))
        result.append(selected)
    return result


def build_snapshot(*, include_monitor_output: bool = False) -> Dict[str, Any]:
    started = time.time()
    daemon_result = _run_command(DAEMON_CTL, timeout=5.0)
    status_result = _run_command(STATUS_CMD, timeout=12.0)
    monitor_result = _run_command(MONITOR_CMD, timeout=5.0)
    daemon = _parse_key_values(daemon_result.output)
    pipeline = _parse_pipeline(status_result.output)
    monitor = _parse_monitor(monitor_result.output)
    snapshot: Dict[str, Any] = {
        "generated_at": utc_now(),
        "age_seconds": 0,
        "duration_ms": int((time.time() - started) * 1000),
        "repository": "qual",
        "pause": _pause_state(),
        "daemon": {
            "rc": daemon_result.rc,
            "timed_out": daemon_result.timed_out,
            "fields": daemon,
        },
        "pipeline": {
            "rc": status_result.rc,
            "timed_out": status_result.timed_out,
            **pipeline,
        },
        "monitor": {
            "rc": monitor_result.rc,
            "timed_out": monitor_result.timed_out,
            **monitor,
        },
        "process_view": _process_view(),
        "memory_pressure": _memory_pressure(),
        "git": _git_status(),
        "lane_placements": _lane_placements(),
        "milestones": _milestone_status(),
    }
    snapshot["summary"] = _summary_from(daemon, pipeline, monitor)
    if include_monitor_output:
        snapshot["safe_command_output"] = {
            "daemon_ctl_status": daemon_result.output,
            "status": status_result.output,
            "daemon_monitor_focus": "\n".join(monitor.get("focus", [])),
        }
    return snapshot


def compact_summary(snapshot: Mapping[str, Any]) -> Dict[str, Any]:
    summary = dict(snapshot.get("summary", {}) if isinstance(snapshot.get("summary"), dict) else {})
    pipeline = snapshot.get("pipeline") if isinstance(snapshot.get("pipeline"), dict) else {}
    lanes = pipeline.get("lanes", []) if isinstance(pipeline.get("lanes"), list) else []
    lane_placements = snapshot.get("lane_placements", {})
    active_lanes = []
    for lane in lanes:
        if not isinstance(lane, dict):
            continue
        if str(lane.get("state", "")).lower() == "disabled":
            continue
        lane = dict(lane)
        placement = lane_placements.get(str(lane.get("lane") or "")) if isinstance(lane_placements, dict) else None
        lane["running"] = placement if isinstance(placement, list) else []
        active_lanes.append(lane)
    summary["generated_at"] = snapshot.get("generated_at", "")
    summary["pause"] = snapshot.get("pause", {"paused": False})
    summary["git"] = snapshot.get("git", {})
    summary["memory_pressure"] = snapshot.get("memory_pressure", {})
    summary["lanes"] = active_lanes
    summary["milestones"] = snapshot.get("milestones", [])
    return summary


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Build a sanitized remote monitor status snapshot.")
    parser.add_argument("--summary", action="store_true", help="Print compact summary only")
    parser.add_argument("--include-output", action="store_true", help="Include bounded sanitized command output")
    args = parser.parse_args()
    snapshot = build_snapshot(include_monitor_output=args.include_output)
    payload = compact_summary(snapshot) if args.summary else snapshot
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
