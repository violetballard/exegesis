#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

COORD_DIR = Path(".codex/packet_coordinator")
PID_FILE = COORD_DIR / "daemon.pid"
LOG_FILE = COORD_DIR / "daemon.log"
LEASE_FILE = COORD_DIR / "lease.json"
CMD = [sys.executable, "codex_packet_handoff/tools/agents_coordinator.py", "--daemon"]
PROC_MATCH = "codex_packet_handoff/tools/agents_coordinator.py --daemon"


def _ensure_dirs() -> None:
    COORD_DIR.mkdir(parents=True, exist_ok=True)


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _read_pid() -> Optional[int]:
    try:
        raw = PID_FILE.read_text().strip()
        if not raw:
            return None
        return int(raw)
    except Exception:
        return None


def _find_matching_pids() -> list[int]:
    p = subprocess.run(
        ["pgrep", "-f", PROC_MATCH],
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


def _clear_stale_lease() -> None:
    try:
        if not LEASE_FILE.exists():
            return
        import json
        data = json.loads(LEASE_FILE.read_text() or "{}")
        pid = int(data.get("pid", 0) or 0)
        if not pid or not _pid_alive(pid):
            LEASE_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def _status() -> int:
    pid = _read_pid()
    pids = _find_matching_pids()
    running = bool((pid and _pid_alive(pid)) or pids)
    print(f"daemon_running={running}")
    print(f"pidfile_pid={pid or '-'}")
    print(f"matching_pids={','.join(str(x) for x in pids) if pids else '-'}")
    print(f"log={LOG_FILE}")
    if running:
        return 0
    return 1


def _start() -> int:
    _ensure_dirs()
    _clear_stale_lease()
    pid = _read_pid()
    if pid and _pid_alive(pid):
        print(f"already_running pid={pid}")
        print(f"log={LOG_FILE}")
        return 0

    # If pid file is stale but matching process exists, adopt it.
    pids = _find_matching_pids()
    if pids:
        PID_FILE.write_text(str(pids[0]))
        print(f"already_running pid={pids[0]} (adopted)")
        print(f"log={LOG_FILE}")
        return 0

    with LOG_FILE.open("a") as lf:
        proc = subprocess.Popen(
            CMD,
            stdout=lf,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            cwd=str(Path.cwd()),
        )
    PID_FILE.write_text(str(proc.pid))
    print(f"started pid={proc.pid}")
    print(f"log={LOG_FILE}")
    return 0


def _stop() -> int:
    pid = _read_pid()
    stopped_any = False
    if pid and _pid_alive(pid):
        os.kill(pid, signal.SIGTERM)
        stopped_any = True
        deadline = time.time() + 5
        while time.time() < deadline:
            if not _pid_alive(pid):
                break
            time.sleep(0.2)
        if _pid_alive(pid):
            os.kill(pid, signal.SIGKILL)

    # Ensure no stray matching daemons remain.
    for mpid in _find_matching_pids():
        try:
            os.kill(mpid, signal.SIGTERM)
            stopped_any = True
        except OSError:
            pass

    try:
        PID_FILE.unlink()
    except FileNotFoundError:
        pass

    if stopped_any:
        print("stopped")
        return 0
    print("not_running")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Start/stop/status for coordinator daemon.")
    ap.add_argument("action", choices=["start", "stop", "status"])
    args = ap.parse_args()
    if args.action == "start":
        return _start()
    if args.action == "stop":
        return _stop()
    return _status()


if __name__ == "__main__":
    raise SystemExit(main())
