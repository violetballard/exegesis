#!/usr/bin/env python3
from __future__ import annotations

import json
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
LANES = ["feat-commands", "feat-context-storage", "feat-ux-flow", "feat-webconsole-core", "feat-webconsole-ui"]
VERDICT_RE = re.compile(r"Verdict:\s*`?(APPROVED|CHANGES_REQUESTED|CHANGES REQUESTED)`?", re.IGNORECASE)
SHA_RE = re.compile(r"\b[0-9a-f]{40}\b", re.IGNORECASE)
EXEC_RESULT_RE = re.compile(r"exited (\d+)|succeeded", re.IGNORECASE)


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def _read_pid() -> int | None:
    try:
        raw = DAEMON_PID.read_text().strip()
        return int(raw) if raw else None
    except Exception:
        return None


def _pid_alive(pid: int) -> bool:
    try:
        import os
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _matching_pids() -> list[int]:
    p = subprocess.run(
        ["pgrep", "-f", "codex_packet_handoff/tools/agents_coordinator.py --daemon"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if p.returncode != 0:
        return []
    out = []
    for ln in (p.stdout or "").splitlines():
        ln = ln.strip()
        if ln.isdigit():
            out.append(int(ln))
    return out


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
    for lane in LANES:
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


def _tail_log(lines: int = 15) -> str:
    if not DAEMON_LOG.exists():
        return "(no daemon log yet)"
    txt = DAEMON_LOG.read_text(errors="ignore").splitlines()
    return "\n".join(txt[-lines:]) if txt else "(daemon log empty)"


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
    for lane in LANES:
        lane_cfg = lanes.get(lane, {}) if isinstance(lanes, dict) else {}
        out[lane] = str((lane_cfg or {}).get("branch") or f"codex/{lane}")
    return out


def _lane_latest_review_file(lane: str) -> Path | None:
    lane_dir = PACKETS_ROOT / lane / "inbox" / "reviewer"
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
                    if "No such file or directory" in cmd_line:
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
        if "No such file or directory" in ln:
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
    }


def main() -> None:
    pid = _read_pid()
    running = bool(pid and _pid_alive(pid))
    mpids = _matching_pids()
    print("DAEMON")
    print(f"running={running}")
    print(f"pidfile_pid={pid or '-'}")
    print(f"matching_pids={','.join(str(x) for x in mpids) if mpids else '-'}")
    print(f"log={DAEMON_LOG}")
    print()

    run = _latest_run() or {}
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
    print(f"reviewer_queue_pending_feature={reviewer_queue}")
    print(f"reviewer_notes_waiting={totals['reviewer_notes']}")
    print(f"waiting_feature_update={totals['waiting_feature_update']}")
    print(f"ready_for_reemit={totals['ready_for_reemit']}")
    print(f"integrator_queue_approved={integrator_queue}")
    print()

    print("CONTROL PLANE")
    print(f"reviewer_thread_id={router_state.get('reviewer_thread_id', '-')}")
    print(f"integrator_thread_id={router_state.get('integrator_thread_id', '-')}")
    fallback_jobs = router_state.get("fixer_fallback_jobs") or {}
    print(f"fixer_fallback_jobs={len(fallback_jobs) if isinstance(fallback_jobs, dict) else 0}")
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

    cds = _cooldowns()
    print("RETRY COOLDOWNS (seconds)")
    if cds:
        for lane in sorted(cds.keys()):
            print(f"{lane:22} {cds[lane]}")
    else:
        print("(none)")
    print()

    branch_map = _lane_branch_map()
    print("LANE CONVERSATIONS")
    for lane in LANES:
        branch = branch_map.get(lane, f"codex/{lane}")
        head = _branch_head(branch)
        verdict = _lane_verdict_summary(lane)
        logp = _latest_fixer_log(lane)
        log_name = logp.name if logp else "-"
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

    print("DAEMON LOG TAIL")
    print(_tail_log())


if __name__ == "__main__":
    main()
