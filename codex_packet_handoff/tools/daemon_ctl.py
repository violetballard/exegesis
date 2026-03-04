#!/usr/bin/env python3
from __future__ import annotations

import argparse
import errno
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
LEASE_FRESH_SECONDS = 3600


def _ensure_dirs() -> None:
    COORD_DIR.mkdir(parents=True, exist_ok=True)


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError as exc:
        # In sandboxed environments, EPERM can mean "process exists but cannot be signaled".
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
        return False
    if p.returncode != 0:
        return False
    cmd = (p.stdout or "").strip()
    return bool(cmd and PROC_MATCH in cmd)


def _read_pid() -> Optional[int]:
    try:
        raw = PID_FILE.read_text().strip()
        if not raw:
            return None
        return int(raw)
    except Exception:
        return None


def _find_matching_pids() -> list[int]:
    # Sandboxed environments may block process listing tools. Fall back to
    # pidfile-based checks when we cannot list the process table.
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
        if PROC_MATCH not in cmd:
            continue
        if "pgrep" in cmd or "daemon_ctl.py" in cmd:
            continue
        out.append(pid)
    return out


def _clear_stale_lease() -> None:
    try:
        if not LEASE_FILE.exists():
            return
        import json
        data = json.loads(LEASE_FILE.read_text() or "{}")
        pid = int(data.get("pid", 0) or 0)
        if not pid or not _pid_alive(pid) or not _pid_matches_daemon(pid):
            LEASE_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def _lease_state() -> tuple[int | None, float | None]:
    try:
        import json
        data = json.loads(LEASE_FILE.read_text() or "{}")
        pid = int(data.get("pid", 0) or 0) or None
        ts = float(data.get("ts", 0) or 0) or None
        return pid, ts
    except Exception:
        return None, None


def _is_running() -> bool:
    lease_pid, lease_ts = _lease_state()
    pid = _read_pid() or lease_pid
    if not pid:
        return False
    if not _pid_alive(pid) or not _pid_matches_daemon(pid):
        return False
    if lease_pid != pid or not lease_ts:
        return False
    return (time.time() - lease_ts) <= LEASE_FRESH_SECONDS


def _status() -> int:
    pid = _read_pid()
    pids = _find_matching_pids()
    running = _is_running()
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
    if _is_running():
        print(f"already_running pid={pid}")
        print(f"log={LOG_FILE}")
        return 0

    # Avoid false adoption in sandboxed environments where process listing may be noisy.
    # If daemon is truly live, _is_running() above already returned True.

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
    lease_pid, _ = _lease_state()
    pid = _read_pid() or lease_pid
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
