#!/usr/bin/env python3
from __future__ import annotations

import json
import errno
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List

PACKETS_ROOT = Path(".codex/packets/lanes")
COORD_STATE = Path(".codex/packet_coordinator/state.json")
ROUTER_STATE = Path(".codex/packet_router/state.json")
ROUTER_CFG = Path(".codex/packet_router/config.json")
DAEMON_PID = Path(".codex/packet_coordinator/daemon.pid")
DAEMON_LOG = Path(".codex/packet_coordinator/daemon.log")
RUNS_DIR = Path(".codex/packet_coordinator/runs")
LOG_DIR = Path(".codex/packet_router/logs")
FEATURE_RUNNER_ROOT = Path(".codex/feature_runner")
FEATURE_STATE = FEATURE_RUNNER_ROOT / "state.json"
COORD_LEASE = Path(".codex/packet_coordinator/lease.json")
LEASE_FRESH_SECONDS = 3600
STALE_LOG_SECONDS = 1800
DEFAULT_LANES = [
    "feat-commands",
    "feat-context-storage",
    "feat-ux-flow",
    "feat-retrieval-fts",
    "feat-a2ui-contract",
    "feat-engine-runs",
    "feat-console",
]
VERDICT_RE = re.compile(
    r"(?:\*\*Verdict\*\*|Verdict:)\s*`?(APPROVED|CHANGES_REQUESTED|CHANGES REQUESTED)`?",
    re.IGNORECASE,
)
SHA_RE = re.compile(r"\b[0-9a-f]{40}\b", re.IGNORECASE)
EXEC_RESULT_RE = re.compile(r"exited (\d+)|succeeded", re.IGNORECASE)
REQUIRED_FIX_RE = re.compile(r"^\s*\d+\.\s+", re.MULTILINE)
LANE_NAME_RE = re.compile(r"feature lane agent for\s+`?([A-Za-z0-9._-]+)`?", re.IGNORECASE)
CODEX_EXEC_RE = re.compile(r"\bcodex\b.*\bexec\b", re.IGNORECASE)


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def _lane_config_map() -> Dict[str, Dict[str, Any]]:
    cfg = _load_json(ROUTER_CFG, {})
    lanes = cfg.get("lanes") if isinstance(cfg, dict) else {}
    if isinstance(lanes, dict) and lanes:
        return {str(name): dict(lane_cfg or {}) for name, lane_cfg in lanes.items()}
    return {lane: {"enabled": True} for lane in DEFAULT_LANES}


def _configured_lanes() -> List[str]:
    lane_map = _lane_config_map()
    return list(lane_map.keys()) if lane_map else list(DEFAULT_LANES)


def _enabled_lanes() -> List[str]:
    lane_map = _lane_config_map()
    return [lane for lane, lane_cfg in lane_map.items() if bool((lane_cfg or {}).get("enabled", True))]




def _read_pid() -> int | None:
    try:
        raw = DAEMON_PID.read_text().strip()
        return int(raw) if raw else None
    except Exception:
        return None


def _lease_pid_ts() -> tuple[int | None, float | None]:
    try:
        data = _load_json(COORD_LEASE, {})
        pid = int((data or {}).get("pid") or 0) or None
        ts = float((data or {}).get("ts") or 0) or None
        return pid, ts
    except Exception:
        return None, None


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError as exc:
        if getattr(exc, "errno", None) == errno.EPERM:
            return True
        return False


def _pid_matches_daemon(pid: int) -> bool:
    try:
        p = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except Exception:
        # In restricted environments, process table inspection may be blocked.
        # Treat as unknown-but-acceptable and rely on lease freshness.
        return True
    if p.returncode != 0:
        return True
    cmd = (p.stdout or "").strip()
    return bool(cmd and "codex_packet_handoff/tools/agents_coordinator.py --daemon" in cmd)


def _matching_pids() -> list[int]:
    # Sandboxed environments may block process listing tools. In that case,
    # monitor uses pidfile + kill(0) as the source of truth.
    try:
        p = subprocess.run(
            ["ps", "-axo", "pid=,command="],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except Exception:
        return []
    if p.returncode != 0:
        return []
    out: list[int] = []
    for ln in (p.stdout or "").splitlines():
        row = ln.strip()
        if not row:
            continue
        parts = row.split(None, 1)
        if len(parts) != 2 or not parts[0].isdigit():
            continue
        pid = int(parts[0])
        cmd = parts[1]
        if pid == os.getpid():
            continue
        if "codex_packet_handoff/tools/agents_coordinator.py --daemon" not in cmd:
            continue
        if "daemon_monitor.py" in cmd or "daemon_ctl.py" in cmd or "pgrep" in cmd:
            continue
        out.append(pid)
    return out


def _manual_feature_sessions() -> list[dict[str, str]]:
    try:
        p = subprocess.run(
            ["ps", "-axo", "pid=,etime=,command="],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except Exception:
        return []
    if p.returncode != 0:
        return []
    rows: list[dict[str, str]] = []
    for ln in (p.stdout or "").splitlines():
        row = ln.strip()
        if not row or not CODEX_EXEC_RE.search(row):
            continue
        if "FEATURE FIXER" in row:
            continue
        if "feature lane agent for" not in row:
            continue
        parts = row.split(None, 2)
        if len(parts) != 3 or not parts[0].isdigit():
            continue
        lane_match = LANE_NAME_RE.search(parts[2])
        rows.append(
            {
                "pid": parts[0],
                "etime": parts[1],
                "lane": lane_match.group(1) if lane_match else "-",
                "command": parts[2],
            }
        )
    return rows


def _latest_feature_runner_log(lane: str) -> Path | None:
    log_dir = FEATURE_RUNNER_ROOT / "logs"
    files = sorted(log_dir.glob(f"{lane}__*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _manual_feature_session_map() -> Dict[str, dict[str, str]]:
    out: Dict[str, dict[str, str]] = {}
    for row in _manual_feature_sessions():
        lane = row.get("lane") or "-"
        if lane != "-" and lane not in out:
            out[lane] = row
    return out


def _is_real_lane_path_error(line: str) -> bool:
    lowered = line.lower()
    if "no such file or directory" not in lowered:
        return False
    # Ignore Codex temp/snapshot cleanup noise; these are not lane worktree issues.
    if ".codex/shell_snapshots/" in lowered:
        return False
    if "failed to delete shell snapshot" in lowered:
        return False
    return True


def _manual_feature_logs(limit: int = 5) -> list[Path]:
    log_dir = FEATURE_RUNNER_ROOT / "logs"
    if not log_dir.exists():
        return []
    return sorted(log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def _feature_thread_state() -> Dict[str, Dict[str, Any]]:
    data = _load_json(FEATURE_STATE, {})
    lanes = data.get("lanes") if isinstance(data, dict) else {}
    return lanes if isinstance(lanes, dict) else {}


def _latest_run() -> Dict[str, Any] | None:
    state = _load_json(COORD_STATE, {})
    run_file = state.get("last_run_file")
    if run_file:
        p = Path(run_file)
        if not p.is_absolute():
            p = Path.cwd() / p
        if p.exists():
            return _load_json(p, {})
    runs = sorted(RUNS_DIR.glob("run__*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if runs:
        return _load_json(runs[0], {})
    return None


def _lane_counts(lane_dir: Path) -> Dict[str, int]:
    return {
        "pending": len(list((lane_dir / "inbox/feature").glob("*.md"))),
        "review": len(list((lane_dir / "inbox/reviewer").glob("*.md"))),
        "approved": len(list((lane_dir / "outbox/integrator").glob("*.md"))),
    }


def _collect_lane_totals() -> Dict[str, int]:
    totals = {
        "pending_feature": 0,
        "reviewer_notes": 0,
        "approved_for_integrator": 0,
        "waiting_feature_update": 0,
        "ready_for_reemit": 0,
    }
    if not PACKETS_ROOT.exists():
        return totals
    planner_state = _load_json(Path(".codex/packet_planner/state.json"), {})
    planner_lanes = (planner_state.get("lanes") or {}) if isinstance(planner_state, dict) else {}
    branch_map = _lane_branch_map()
    for lane in _enabled_lanes():
        lane_dir = PACKETS_ROOT / lane
        if not lane_dir.exists():
            continue
        c = _lane_counts(lane_dir)
        totals["pending_feature"] += c["pending"]
        totals["reviewer_notes"] += c["review"]
        totals["approved_for_integrator"] += c["approved"]

        if c["review"] <= 0:
            continue
        head = _branch_head(branch_map.get(lane, f"codex/{lane}"))
        last_sub = str(((planner_lanes.get(lane) or {}).get("last_submitted_sha") or ""))[:8]
        if head and last_sub and head != last_sub:
            totals["ready_for_reemit"] += 1
        else:
            totals["waiting_feature_update"] += 1
    return totals


def _cooldowns() -> Dict[str, int]:
    cfg = _load_json(ROUTER_CFG, {})
    state = _load_json(ROUTER_STATE, {})
    cooldown = int(cfg.get("reviewer_fixer_retry_cooldown_seconds", 900))
    ts_map = state.get("reviewer_fixer_retry_ts") or {}
    now = time.time()
    out: Dict[str, int] = {}
    for lane, ts in ts_map.items():
        try:
            remain = int(max(0, (float(ts) + cooldown) - now))
        except Exception:
            remain = 0
        out[lane] = remain
    return out


def _runtime_state() -> Dict[str, Any]:
    cfg = _load_json(ROUTER_CFG, {})
    state = _load_json(ROUTER_STATE, {})
    retry_at = float((state or {}).get("cloud_retry_at") or 0)
    now = time.time()
    retry_in = int(max(0, retry_at - now)) if retry_at else 0
    return {
        "mode": str((state or {}).get("runtime_mode") or (cfg or {}).get("runtime_mode_default") or "cloud_primary"),
        "retry_at": retry_at,
        "retry_in": retry_in,
        "reason": str((state or {}).get("last_quota_reason") or "-"),
    }


def _tail_log(lines: int = 15) -> str:
    if not DAEMON_LOG.exists():
        return "(no daemon log yet)"
    txt = DAEMON_LOG.read_text(errors="ignore").splitlines()
    return "\n".join(txt[-lines:]) if txt else "(daemon log empty)"


def _active_blocker_summary(totals: Dict[str, int]) -> str:
    if totals["approved_for_integrator"] > 0:
        return f"integrator backlog active ({totals['approved_for_integrator']} approved packet(s) waiting)"
    if totals["pending_feature"] > 0:
        return f"reviewer backlog active ({totals['pending_feature']} feature packet(s) waiting)"
    if totals["ready_for_reemit"] > 0:
        return f"planner re-emit needed ({totals['ready_for_reemit']} lane(s) advanced past review notes)"
    if totals["waiting_feature_update"] > 0:
        return f"feature rework needed ({totals['waiting_feature_update']} lane(s) still on reviewer notes)"
    return "none"


def _tail_scope_check_note(totals: Dict[str, int], tail: str) -> str:
    if not tail or tail.startswith("(no daemon log") or tail.startswith("(daemon log empty)"):
        return "daemon log has no recent scope-check lines"
    lowered = tail.lower()
    if "scope-check" not in lowered:
        return "daemon log tail has no scope-check chatter"
    if totals["pending_feature"] == 0 and totals["approved_for_integrator"] == 0 and totals["waiting_feature_update"] > 0:
        return "scope-check lines in daemon log tail look historical; current blocker is reviewer handback, not a live scope-check failure"
    if totals["pending_feature"] == 0 and totals["approved_for_integrator"] == 0 and totals["waiting_feature_update"] == 0:
        return "scope-check lines in daemon log tail look historical; queue truth shows no live scope-check blocker"
    return "scope-check lines appear in daemon log tail; confirm against queue truth before treating them as a live blocker"


def _branch_head(branch: str) -> str:
    p = subprocess.run(
        ["git", "rev-parse", branch],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if p.returncode != 0:
        return "-"
    return (p.stdout or "").strip()[:8]


def _lane_branch_map() -> Dict[str, str]:
    cfg = _load_json(ROUTER_CFG, {})
    lanes = (cfg.get("lanes") or {}) if isinstance(cfg, dict) else {}
    out: Dict[str, str] = {}
    for lane in _enabled_lanes():
        lane_cfg = lanes.get(lane, {}) if isinstance(lanes, dict) else {}
        out[lane] = str((lane_cfg or {}).get("branch") or f"codex/{lane}")
    return out


def _lane_latest_review_file(lane: str) -> Path | None:
    lane_dir = PACKETS_ROOT / lane / "inbox" / "reviewer"
    notes = sorted(lane_dir.glob("*.md"), key=lambda p: p.stat().st_mtime)
    if not notes:
        return None
    return notes[-1]


def _lane_latest_feature_archive(lane: str) -> Path | None:
    lane_dir = PACKETS_ROOT / lane / "archive"
    notes = sorted(lane_dir.glob("F__*.md"), key=lambda p: p.stat().st_mtime)
    if not notes:
        return None
    return notes[-1]


def _lane_latest_feature_pending(lane: str) -> Path | None:
    lane_dir = PACKETS_ROOT / lane / "inbox" / "feature"
    notes = sorted(lane_dir.glob("*.md"), key=lambda p: p.stat().st_mtime)
    if not notes:
        return None
    return notes[-1]


def _lane_verdict_summary(lane: str) -> str:
    note = _lane_latest_review_file(lane)
    if note is None:
        return "no reviewer note"
    txt = note.read_text(errors="ignore")
    m = VERDICT_RE.search(txt)
    if not m:
        return "review note present (verdict not explicit)"
    v = m.group(1).upper().replace(" ", "_")
    return v


def _review_history_summary(lane: str) -> Dict[str, Any]:
    rf = _lane_latest_review_file(lane)
    if rf is None:
        return {"state": "none", "required_fixes": 0, "age_s": None, "msg": "no reviewer note"}
    txt = rf.read_text(errors="ignore")
    lower = txt.lower()
    if "session not found for thread_id" in lower:
        state = "invalid_session_note"
    else:
        m = VERDICT_RE.search(txt)
        state = (m.group(1).upper().replace(" ", "_") if m else "changes_requested_implicit")
    required = len(REQUIRED_FIX_RE.findall(txt))
    age_s = int(max(0, time.time() - rf.stat().st_mtime))
    return {
        "state": state,
        "required_fixes": required,
        "age_s": age_s,
        "msg": rf.name,
    }


def _integrator_history_summary() -> Dict[str, Any]:
    approved_now = 0
    integrated_archived = 0
    newest_integrator: Path | None = None
    for lane in _enabled_lanes():
        lane_dir = PACKETS_ROOT / lane
        approved_now += len(list((lane_dir / "outbox" / "integrator").glob("*.md")))
        integ = sorted((lane_dir / "archive").glob("INTEGRATOR__*.md"), key=lambda p: p.stat().st_mtime)
        integrated_archived += len(integ)
        if integ and (newest_integrator is None or integ[-1].stat().st_mtime > newest_integrator.stat().st_mtime):
            newest_integrator = integ[-1]
    return {
        "approved_now": approved_now,
        "integrated_archived": integrated_archived,
        "latest_integrator_file": newest_integrator.name if newest_integrator else "-",
    }


def _first_nonempty_line(path: Path | None, max_len: int = 140) -> str:
    if path is None:
        return "-"
    try:
        for ln in path.read_text(errors="ignore").splitlines():
            s = ln.strip()
            if not s:
                continue
            s = s.lstrip("#- ").strip()
            if not s:
                continue
            if len(s) > max_len:
                s = s[: max_len - 3] + "..."
            return s
    except Exception:
        return "-"
    return "-"


def _reviewer_live_summary() -> Dict[str, Any]:
    pending_items: List[tuple[str, Path]] = []
    latest_review: tuple[str, Path] | None = None
    invalid_count = 0
    for lane in _enabled_lanes():
        pf = _lane_latest_feature_pending(lane)
        if pf is not None:
            pending_items.append((lane, pf))
        rf = _lane_latest_review_file(lane)
        if rf is not None:
            if latest_review is None or rf.stat().st_mtime > latest_review[1].stat().st_mtime:
                latest_review = (lane, rf)
            txt = rf.read_text(errors="ignore").lower()
            if "session not found for thread_id" in txt or "thread not found" in txt:
                invalid_count += 1
    pending_items.sort(key=lambda x: x[1].stat().st_mtime)
    queue_lanes = [x[0] for x in pending_items]
    if pending_items:
        focus_lane = pending_items[0][0]
        focus_age = int(max(0, time.time() - pending_items[0][1].stat().st_mtime))
    else:
        focus_lane = "-"
        focus_age = 0
    latest_note_lane = latest_review[0] if latest_review else "-"
    latest_note_line = _first_nonempty_line(latest_review[1] if latest_review else None)
    return {
        "queue_count": len(pending_items),
        "queue_lanes": queue_lanes,
        "focus_lane": focus_lane,
        "focus_age_s": focus_age,
        "latest_note_lane": latest_note_lane,
        "latest_note_line": latest_note_line,
        "invalid_notes": invalid_count,
    }


def _review_lane_status_row(lane: str, reviewer_map: Dict[str, str], cooldowns: Dict[str, int]) -> str:
    lane_dir = PACKETS_ROOT / lane
    counts = _lane_counts(lane_dir) if lane_dir.exists() else {"pending": 0, "review": 0, "approved": 0}
    hs = _review_history_summary(lane)
    detail = _detailed_conversation_summary(_latest_fixer_log(lane))
    verdict = hs["state"]
    age = hs["age_s"]
    age_txt = "-" if age is None else f"{age}s"
    tid = reviewer_map.get(lane, "-")
    cd = cooldowns.get(lane)
    cd_txt = "-" if cd is None else str(cd)
    return (
        f"{lane:22} "
        f"thread={tid} "
        f"queue=p{counts['pending']}/r{counts['review']} "
        f"verdict={verdict} "
        f"review_age={age_txt} "
        f"fixer={detail['progress']} "
        f"cooldown={cd_txt}"
    )


def _integrator_live_summary() -> Dict[str, Any]:
    approved_items: List[tuple[str, Path]] = []
    latest_integrator: tuple[str, Path] | None = None
    for lane in _enabled_lanes():
        out_dir = PACKETS_ROOT / lane / "outbox" / "integrator"
        for f in out_dir.glob("*.md"):
            approved_items.append((lane, f))
        arc_dir = PACKETS_ROOT / lane / "archive"
        integ = sorted(arc_dir.glob("INTEGRATOR__*.md"), key=lambda p: p.stat().st_mtime)
        if integ:
            f = integ[-1]
            if latest_integrator is None or f.stat().st_mtime > latest_integrator[1].stat().st_mtime:
                latest_integrator = (lane, f)
    approved_items.sort(key=lambda x: x[1].stat().st_mtime)
    queue_lanes = [x[0] for x in approved_items]
    if approved_items:
        focus_lane = approved_items[0][0]
        focus_age = int(max(0, time.time() - approved_items[0][1].stat().st_mtime))
    else:
        focus_lane = "-"
        focus_age = 0
    if approved_items:
        latest_lane = latest_integrator[0] if latest_integrator else "-"
        latest_line = _first_nonempty_line(latest_integrator[1] if latest_integrator else None)
    else:
        latest_lane = "-"
        latest_line = "-"
    return {
        "queue_count": len(approved_items),
        "queue_lanes": queue_lanes,
        "focus_lane": focus_lane,
        "focus_age_s": focus_age,
        "latest_lane": latest_lane,
        "latest_line": latest_line,
    }


def _latest_fixer_log(lane: str) -> Path | None:
    files = sorted(LOG_DIR.glob(f"fixer__{lane}__*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _conversation_summary(log_path: Path | None) -> str:
    if log_path is None:
        return "no fixer log"
    lines = log_path.read_text(errors="ignore").splitlines()
    picked: list[str] = []
    for ln in lines[-120:]:
        s = ln.strip()
        if not s:
            continue
        if s.startswith("thinking"):
            picked.append("thinking")
        elif s.startswith("exec"):
            picked.append("exec")
        elif "succeeded in" in s:
            picked.append("exec succeeded")
        elif "ERROR:" in s:
            picked.append(s)
        elif "hit your usage limit" in s:
            picked.append("ERROR: usage limit")
    if not picked:
        return "idle/no recent tool activity"
    # De-duplicate while keeping order.
    out: list[str] = []
    for item in picked:
        if not out or out[-1] != item:
            out.append(item)
    return " -> ".join(out[-5:])


def _compact_cmd(cmd_line: str) -> str:
    s = cmd_line.strip()
    s = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*\bWARN\b.*$", "", s).strip()
    if " -lc " in s:
        idx = s.find(" -lc ")
        s = s[idx + 5 :].strip()
    if s.startswith(("'", '"')) and s.endswith(("'", '"')) and len(s) >= 2:
        s = s[1:-1]
    s = " ".join(s.split())
    if len(s) > 90:
        s = s[:87] + "..."
    return s


def _detailed_conversation_summary(log_path: Path | None) -> Dict[str, Any]:
    if log_path is None:
        return {
            "objective": "no fixer run yet",
            "packet": "-",
            "phase": "-",
            "progress": "no activity",
            "recent": [],
            "blockers": [],
            "head_sha": None,
        }

    lines = log_path.read_text(errors="ignore").splitlines()
    log_age_seconds = int(max(0, time.time() - log_path.stat().st_mtime))
    objective = "Apply reviewer required fixes"
    packet = "review packet present"
    phase = "unknown"
    head_sha: str | None = None

    if any("Reviewer packet was empty" in ln for ln in lines):
        packet = "reviewer packet empty; generated fixes from feature packet"
    elif any("Session not found for thread_id" in ln for ln in lines):
        packet = "reviewer thread missing/session-not-found fallback"

    for ln in lines:
        if "Apply the reviewer's REQUIRED FIXES" in ln:
            objective = "Apply REQUIRED FIXES and produce a passing commit"
            break

    thinking_msgs: List[str] = []
    cmd_outcomes: List[str] = []
    blockers: List[str] = []
    success = 0
    fail = 0
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if ln.strip() == "thinking":
            if i + 1 < len(lines):
                nxt = lines[i + 1].strip()
                if nxt:
                    thinking_msgs.append(nxt.strip("* "))
            i += 1
            continue
        if ln.strip() == "exec":
            if i + 1 < len(lines):
                cmd_line = lines[i + 1].strip()
                compact = _compact_cmd(cmd_line)
                m = EXEC_RESULT_RE.search(cmd_line)
                if m and m.group(1):
                    rc = int(m.group(1))
                    fail += 1
                    cmd_outcomes.append(f"FAIL({rc}) {compact}")
                    if _is_real_lane_path_error(cmd_line):
                        blockers.append("missing file/path in lane worktree")
                else:
                    success += 1
                    cmd_outcomes.append(f"OK {compact}")
            i += 1
            continue
        if "ERROR:" in ln:
            blockers.append(ln.strip())
        if "hit your usage limit" in ln:
            blockers.append("usage limit hit")
        if _is_real_lane_path_error(ln):
            blockers.append("missing file/path in lane worktree")
        for sha in SHA_RE.findall(ln):
            head_sha = sha
        i += 1

    if thinking_msgs:
        phase = thinking_msgs[-1]
    elif cmd_outcomes:
        phase = "executing fixer commands"
    else:
        phase = "startup/no tool activity"

    recent = cmd_outcomes[-4:]
    if not recent and thinking_msgs:
        recent = [f"thinking: {x}" for x in thinking_msgs[-2:]]

    # Keep blocker list compact and de-duplicated.
    uniq_blockers: List[str] = []
    for b in blockers:
        if b not in uniq_blockers:
            uniq_blockers.append(b)
    uniq_blockers = uniq_blockers[:3]

    # Suppress stale blocker noise from old fixer logs after lane hygiene corrections.
    if log_age_seconds > 1800:
        uniq_blockers = []

    if success == 0 and fail == 0:
        progress = "no commands executed"
    else:
        progress = f"commands ok={success} fail={fail}"

    return {
        "objective": objective,
        "packet": packet,
        "phase": phase,
        "progress": progress,
        "recent": recent,
        "blockers": uniq_blockers,
        "head_sha": head_sha,
        "log_age_seconds": log_age_seconds,
    }


def _feature_runner_state(lane: str, live_sessions: Dict[str, dict[str, str]]) -> Dict[str, Any]:
    live = live_sessions.get(lane)
    if live:
        return {
            "state": "live",
            "summary": f"manual feature worker running pid={live['pid']} age={live['etime']}",
            "log": None,
            "age_s": None,
        }
    thread_state = _feature_thread_state().get(lane)
    if isinstance(thread_state, dict):
        log_name = Path(str(thread_state.get("log_path") or "")).name if thread_state.get("log_path") else None
        launched_at = str(thread_state.get("last_launch_at") or "-")
        if thread_state.get("thread_id"):
            return {
                "state": "managed_thread",
                "summary": f"managed feature thread={thread_state.get('thread_id')} last_action={thread_state.get('last_action', '-')} launched_at={launched_at}",
                "log": log_name,
                "age_s": None,
            }
        status = str(thread_state.get("status") or "")
        if status == "launching":
            return {
                "state": "launching",
                "summary": f"managed feature launch in progress last_action={thread_state.get('last_action', '-')} launched_at={launched_at}",
                "log": log_name,
                "age_s": None,
            }
        if status == "error":
            err = str(thread_state.get("error") or "launch failed")
            return {
                "state": "error",
                "summary": f"managed feature launch error: {err}",
                "log": log_name,
                "age_s": None,
            }
        if status == "direct_exec_running":
            pid = int(thread_state.get("pid") or 0)
            if _pid_alive(pid):
                return {
                    "state": "direct_exec_running",
                    "summary": f"direct exec fallback running pid={pid}",
                    "log": log_name,
                    "age_s": None,
                }
            return {
                "state": "error",
                "summary": f"stale direct exec state (pid {pid} is not alive)",
                "log": log_name,
                "age_s": None,
            }
    logp = _latest_feature_runner_log(lane)
    if logp is None:
        return {
            "state": "none",
            "summary": "no recent feature launch",
            "log": None,
            "age_s": None,
        }
    age_s = int(max(0, time.time() - logp.stat().st_mtime))
    size = logp.stat().st_size
    if age_s <= 300 and size == 0:
        return {
            "state": "recent_empty",
            "summary": f"recent feature launch exited/no output yet (log_age={age_s}s)",
            "log": logp.name,
            "age_s": age_s,
        }
    if age_s <= 300:
        return {
            "state": "recent_log",
            "summary": f"recent feature launch produced output (log_age={age_s}s)",
            "log": logp.name,
            "age_s": age_s,
        }
    return {
        "state": "stale",
        "summary": f"no live feature worker; last launch log is stale (log_age={age_s}s)",
        "log": logp.name,
        "age_s": age_s,
    }


def main() -> None:
    pid = _read_pid()
    lease_pid, lease_ts = _lease_pid_ts()
    if not pid and lease_pid:
        pid = lease_pid
    running = bool(
        pid
        and _pid_alive(pid)
        and _pid_matches_daemon(pid)
        and lease_pid == pid
        and lease_ts
        and (time.time() - lease_ts) <= LEASE_FRESH_SECONDS
    )
    mpids = _matching_pids()
    print("DAEMON")
    print(f"running={running}")
    print(f"pidfile_pid={pid or '-'}")
    print(f"matching_pids={','.join(str(x) for x in mpids) if mpids else '-'}")
    print(f"log={DAEMON_LOG}")
    print()

    run = _latest_run() or {}
    runtime = _runtime_state()
    print("LAST RUN")
    print(f"status={run.get('status', '-')}")
    print(f"mode={run.get('mode', '-')}")
    print(f"cycles={run.get('cycles', '-')}")
    print(f"planner_errors={run.get('planner_errors', '-')}")
    print(f"router_errors={run.get('router_errors', '-')}")
    print(f"router_processed_total={run.get('router_processed_total', '-')}")
    print(f"fixer_kicked_total={run.get('fixer_kicked_total', '-')}")
    print()

    router_state = _load_json(ROUTER_STATE, {})
    totals = _collect_lane_totals()
    reviewer_queue = totals["pending_feature"]
    integrator_queue = totals["approved_for_integrator"]
    if reviewer_queue > 0 and integrator_queue == 0:
        bottleneck = "reviewer"
    elif integrator_queue > 0 and reviewer_queue == 0:
        bottleneck = "integrator"
    elif reviewer_queue > 0 and integrator_queue > 0:
        bottleneck = "both"
    elif totals["reviewer_notes"] > 0:
        bottleneck = "reviewer/fixer handback loop"
    else:
        bottleneck = "none"

    print("BACKLOG")
    print(f"bottleneck={bottleneck}")
    print(f"active_blocker={_active_blocker_summary(totals)}")
    print(f"reviewer_queue_pending_feature={reviewer_queue}")
    print(f"reviewer_notes_waiting={totals['reviewer_notes']}")
    print(f"waiting_feature_update={totals['waiting_feature_update']}")
    print(f"ready_for_reemit={totals['ready_for_reemit']}")
    print(f"integrator_queue_approved={integrator_queue}")
    print()

    print("CONTROL PLANE")
    print(f"runtime_mode={runtime['mode']}")
    print(f"cloud_retry_in_seconds={runtime['retry_in']}")
    print(f"last_quota_reason={runtime['reason']}")
    reviewer_map = router_state.get("reviewer_thread_ids") or {}
    if isinstance(reviewer_map, dict) and reviewer_map:
        print(f"reviewer_thread_count={len(reviewer_map)}")
        for lane in _configured_lanes():
            print(f"reviewer_thread_{lane}={reviewer_map.get(lane, '-')}")
    else:
        print(f"reviewer_thread_id={router_state.get('reviewer_thread_id', '-')}")
    missing = router_state.get("reviewer_thread_missing_lanes")
    if isinstance(missing, list):
        print(f"reviewer_thread_missing_lanes={','.join(str(x) for x in missing) if missing else '-'}")
    print(f"integrator_thread_id={router_state.get('integrator_thread_id', '-')}")
    fallback_jobs = router_state.get("fixer_fallback_jobs") or {}
    print(f"fixer_fallback_jobs={len(fallback_jobs) if isinstance(fallback_jobs, dict) else 0}")
    print()

    manual_sessions = _manual_feature_sessions()
    manual_session_map = _manual_feature_session_map()
    feature_threads = _feature_thread_state()
    print("MANUAL FEATURE SESSIONS")
    print(f"running_count={len(manual_sessions)}")
    print(f"managed_thread_count={sum(1 for lane in _configured_lanes() if isinstance(feature_threads.get(lane), dict) and feature_threads.get(lane, {}).get('thread_id'))}")
    if manual_sessions:
        for row in manual_sessions:
            print(f"{row['lane']:22} pid={row['pid']} age={row['etime']}")
    else:
        print("(none)")
    print()

    rv_live = _reviewer_live_summary()
    print("REVIEWER LIVE DISCUSSION")
    print(f"queue_count={rv_live['queue_count']}")
    print(f"queue_lanes={','.join(rv_live['queue_lanes']) if rv_live['queue_lanes'] else '-'}")
    print(f"focus_lane={rv_live['focus_lane']}")
    print(f"focus_lane_age_seconds={rv_live['focus_age_s'] if rv_live['focus_lane'] != '-' else '-'}")
    print(f"latest_note_lane={rv_live['latest_note_lane']}")
    print(f"latest_note_summary={rv_live['latest_note_line']}")
    print(f"invalid_reviewer_notes={rv_live['invalid_notes']}")
    print()

    it_live = _integrator_live_summary()
    print("INTEGRATOR LIVE DISCUSSION")
    print(f"queue_count={it_live['queue_count']}")
    print(f"queue_lanes={','.join(it_live['queue_lanes']) if it_live['queue_lanes'] else '-'}")
    print(f"focus_lane={it_live['focus_lane']}")
    print(f"focus_lane_age_seconds={it_live['focus_age_s'] if it_live['focus_lane'] != '-' else '-'}")
    print(f"latest_lane={it_live['latest_lane']}")
    print(f"latest_summary={it_live['latest_line']}")
    print()

    cds = _cooldowns()
    print("REVIEW LANE STATUS")
    reviewer_map_typed = reviewer_map if isinstance(reviewer_map, dict) else {}
    for lane in _configured_lanes():
        print(_review_lane_status_row(lane, reviewer_map_typed, cds))
    print()

    print("REVIEWER HISTORY")
    for lane in _configured_lanes():
        hs = _review_history_summary(lane)
        age = hs["age_s"]
        age_txt = "-" if age is None else f"{age}s"
        print(
            f"{lane:22} state={hs['state']} required_fixes={hs['required_fixes']} age={age_txt} file={hs['msg']}"
        )
    print()

    integ_h = _integrator_history_summary()
    print("INTEGRATOR HISTORY")
    print(f"approved_waiting_now={integ_h['approved_now']}")
    print(f"integrated_archive_total={integ_h['integrated_archived']}")
    print(f"latest_integrator_file={integ_h['latest_integrator_file']}")
    print()

    print("LANES")
    if PACKETS_ROOT.exists():
        for lane_dir in sorted([p for p in PACKETS_ROOT.iterdir() if p.is_dir()], key=lambda p: p.name):
            c = _lane_counts(lane_dir)
            print(
                f"{lane_dir.name:22} pending={c['pending']} review={c['review']} approved={c['approved']}"
            )
    else:
        print("(no packet lanes found)")
    print()

    print("RETRY COOLDOWNS (seconds)")
    if cds:
        for lane in sorted(cds.keys()):
            print(f"{lane:22} {cds[lane]}")
    else:
        print("(none)")
    print()

    branch_map = _lane_branch_map()
    print("LANE LIVE SUMMARY")
    for lane in _configured_lanes():
        c = _lane_counts(PACKETS_ROOT / lane) if (PACKETS_ROOT / lane).exists() else {"pending": 0, "review": 0, "approved": 0}
        logp = _latest_fixer_log(lane)
        feature_state = _feature_runner_state(lane, manual_session_map)
        age = "-"
        stale_idle = False
        if logp is not None:
            age_s = int(max(0, time.time() - logp.stat().st_mtime))
            age = f"{age_s}s"
            stale_idle = c["pending"] == 0 and c["review"] == 0 and c["approved"] == 0 and age_s >= STALE_LOG_SECONDS
        detail = (
            {
                "phase": "no active packet",
                "progress": feature_state["summary"],
            }
            if stale_idle
            else _detailed_conversation_summary(logp)
        )
        if c["pending"] == 0 and c["review"] == 0 and c["approved"] == 0 and feature_state["state"] in {"live", "recent_empty", "recent_log", "managed_thread", "launching", "error", "direct_exec_running"}:
            detail = {
                "phase": "feature lane execution",
                "progress": feature_state["summary"],
            }
        print(
            f"{lane:22} queue=p{c['pending']}/r{c['review']}/a{c['approved']} "
            f"log_age={age} phase={detail['phase']} progress={detail['progress']}"
        )
    print()

    print("LANE CONVERSATIONS")
    for lane in _configured_lanes():
        branch = branch_map.get(lane, f"codex/{lane}")
        head = _branch_head(branch)
        verdict = _lane_verdict_summary(lane)
        logp = _latest_fixer_log(lane)
        log_name = logp.name if logp else "-"
        feature_state = _feature_runner_state(lane, manual_session_map)
        counts = _lane_counts(PACKETS_ROOT / lane) if (PACKETS_ROOT / lane).exists() else {"pending": 0, "review": 0, "approved": 0}
        stale_idle = False
        if logp is not None:
            age_s = int(max(0, time.time() - logp.stat().st_mtime))
            stale_idle = counts["pending"] == 0 and counts["review"] == 0 and counts["approved"] == 0 and age_s >= STALE_LOG_SECONDS
        if counts["pending"] == 0 and counts["review"] == 0 and counts["approved"] == 0 and feature_state["state"] in {"live", "recent_empty", "recent_log", "managed_thread", "launching", "error", "direct_exec_running"}:
            convo = feature_state["summary"]
            detail = {
                "objective": "produce the next lane commit and handoff packet",
                "packet": "-",
                "phase": "feature lane execution",
                "progress": feature_state["summary"],
                "recent": [feature_state["log"]] if feature_state["log"] else [],
                "blockers": [],
                "head_sha": None,
            }
        elif stale_idle:
            convo = "idle/no active lane packet"
            detail = {
                "objective": "no active fixer run",
                "packet": "-",
                "phase": "no active packet",
                "progress": feature_state["summary"],
                "recent": [],
                "blockers": [],
                "head_sha": None,
            }
        else:
            convo = _conversation_summary(logp)
            detail = _detailed_conversation_summary(logp)
        print(f"{lane:22} head={head} verdict={verdict} log={log_name}")
        print(f"  convo: {convo}")
        print(f"  objective: {detail['objective']}")
        print(f"  packet: {detail['packet']}")
        print(f"  phase: {detail['phase']}")
        print(f"  progress: {detail['progress']}")
        if detail["head_sha"]:
            print(f"  reported_sha: {detail['head_sha'][:8]}")
        if detail["recent"]:
            print("  recent:")
            for item in detail["recent"]:
                print(f"    - {item}")
        if detail["blockers"]:
            print("  blockers:")
            for item in detail["blockers"]:
                print(f"    - {item}")
    print()

    print("MANUAL FEATURE LOGS")
    logs = _manual_feature_logs()
    if not logs:
        print("(none)")
    else:
        for logp in logs:
            age = int(max(0, time.time() - logp.stat().st_mtime))
            print(f"{logp.name} age={age}s")
            try:
                tail = logp.read_text(errors="ignore").splitlines()[-5:]
            except Exception:
                tail = ["(unable to read log)"]
            for line in tail:
                print(f"  {line[:200]}")
    print()

    tail = _tail_log()
    print("DAEMON LOG TAIL")
    print(f"note={_tail_scope_check_note(totals, tail)}")
    print(tail)


if __name__ == "__main__":
    main()
