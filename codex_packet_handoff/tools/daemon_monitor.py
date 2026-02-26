#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any, Dict

PACKETS_ROOT = Path(".codex/packets/lanes")
COORD_STATE = Path(".codex/packet_coordinator/state.json")
ROUTER_STATE = Path(".codex/packet_router/state.json")
ROUTER_CFG = Path(".codex/packet_router/config.json")
DAEMON_PID = Path(".codex/packet_coordinator/daemon.pid")
DAEMON_LOG = Path(".codex/packet_coordinator/daemon.log")
RUNS_DIR = Path(".codex/packet_coordinator/runs")


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

    print("DAEMON LOG TAIL")
    print(_tail_log())


if __name__ == "__main__":
    main()

