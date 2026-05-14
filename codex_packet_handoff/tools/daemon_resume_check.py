#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path


STATE_FILE = Path(" .codex/packet_coordinator/state.json".strip())


def _run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.stdout or ""
    if out:
        print(out, end="" if out.endswith("\n") else "\n")
    return p.returncode, out


def _load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {}


def _resume_epoch(state: dict) -> str:
    return str(state.get("current_resume_epoch") or "").strip()


def _resume_state(previous_state: dict, current_state: dict) -> str:
    previous_epoch = _resume_epoch(previous_state)
    current_epoch = _resume_epoch(current_state)
    if not current_epoch or current_epoch == previous_epoch:
        return "waiting"
    previous_last_cycle_at = str(previous_state.get("last_cycle_at") or "")
    current_last_cycle_at = str(current_state.get("last_cycle_at") or "")
    current_live_cycle_count = int(current_state.get("live_cycle_count") or 0)
    if current_live_cycle_count > 0 and current_last_cycle_at and current_last_cycle_at != previous_last_cycle_at:
        return "completed"
    return "started"


def _wait_for_first_cycle(previous_state: dict, *, timeout_seconds: float = 15.0) -> str:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        state = _load_state()
        resume_state = _resume_state(previous_state, state)
        if resume_state != "waiting":
            return resume_state
        time.sleep(0.5)
    final_state = _load_state()
    return _resume_state(previous_state, final_state)


def main() -> int:
    print("=== RESUME CHECK: START ===")
    previous_state = _load_state()
    _run([sys.executable, "codex_packet_handoff/tools/daemon_ctl.py", "start"])

    print("=== RESUME CHECK: STATUS ===")
    status_rc, status_out = _run([sys.executable, "codex_packet_handoff/tools/daemon_ctl.py", "status"])
    if "daemon_running=True" not in status_out:
        print("[resume-check] daemon is not running after start; aborting checks")
        return 1 if status_rc == 0 else status_rc

    resume_state = _wait_for_first_cycle(previous_state)
    if resume_state == "completed":
        print("[resume-check] first reconcile cycle completed")
    elif resume_state == "started":
        print("[resume-check] daemon resumed with a fresh run; first reconcile cycle is still in progress")
    else:
        print("[resume-check] daemon started, but no fresh resume epoch or reconcile cycle was observed before timeout")

    print("=== RESUME CHECK: MONITOR ===")
    _run([sys.executable, "codex_packet_handoff/tools/daemon_monitor.py"])

    print("=== RESUME CHECK: PIPELINE STATUS ===")
    _run([sys.executable, "codex_packet_handoff/tools/status.py"])

    print("=== RESUME CHECK: DONE ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
