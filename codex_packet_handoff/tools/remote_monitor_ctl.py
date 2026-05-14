#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REMOTE_ROOT = REPO_ROOT / ".codex/remote_monitor"
PID_FILE = REMOTE_ROOT / "server.pid"
LOG_FILE = REMOTE_ROOT / "server.log"
SERVER = REPO_ROOT / "codex_packet_handoff/tools/remote_monitor_server.py"
DEFAULT_CONFIG = REMOTE_ROOT / "config.json"


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _read_pid() -> int | None:
    try:
        raw = PID_FILE.read_text().strip()
        return int(raw) if raw else None
    except Exception:
        return None


def status() -> int:
    pid = _read_pid()
    running = bool(pid and _pid_alive(pid))
    print(f"remote_monitor_running={running}")
    print(f"pid={pid or '-'}")
    print(f"log={LOG_FILE}")
    return 0 if running else 1


def start(config: Path) -> int:
    REMOTE_ROOT.mkdir(parents=True, exist_ok=True)
    pid = _read_pid()
    if pid and _pid_alive(pid):
        print(f"already_running pid={pid}")
        return 0
    with LOG_FILE.open("a") as log:
        proc = subprocess.Popen(
            [sys.executable, str(SERVER), "--config", str(config)],
            cwd=REPO_ROOT,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True,
        )
    PID_FILE.write_text(str(proc.pid))
    print(f"started pid={proc.pid}")
    print(f"log={LOG_FILE}")
    return 0


def stop() -> int:
    pid = _read_pid()
    if not pid or not _pid_alive(pid):
        PID_FILE.unlink(missing_ok=True)
        print("not_running")
        return 0
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
    except OSError:
        os.kill(pid, signal.SIGTERM)
    deadline = time.time() + 5
    while time.time() < deadline:
        if not _pid_alive(pid):
            break
        time.sleep(0.2)
    if _pid_alive(pid):
        try:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        except OSError:
            os.kill(pid, signal.SIGKILL)
    PID_FILE.unlink(missing_ok=True)
    print("stopped")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Start/stop/status for the qual remote monitor server.")
    parser.add_argument("action", choices=["start", "stop", "status"])
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    if args.action == "start":
        return start(args.config)
    if args.action == "stop":
        return stop()
    return status()


if __name__ == "__main__":
    raise SystemExit(main())
