#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import errno
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

try:
    from log_maintenance import compact_log_file
    from local_exec_sweeper import (
        find_orphaned_repo_local_exec_pids,
        find_stale_repo_test_runner_pids,
        terminate_local_exec_pids,
        terminate_process_groups,
    )
except ImportError:  # pragma: no cover - package execution fallback
    from .log_maintenance import compact_log_file
    from .local_exec_sweeper import (
        find_orphaned_repo_local_exec_pids,
        find_stale_repo_test_runner_pids,
        terminate_local_exec_pids,
        terminate_process_groups,
    )

COORD_DIR = Path(".codex/packet_coordinator")
PID_FILE = COORD_DIR / "daemon.pid"
LOG_FILE = COORD_DIR / "daemon.log"
LEASE_FILE = COORD_DIR / "lease.json"
FEATURE_RUNNER_STATE_FILE = Path(".codex/feature_runner/state.json")
ROUTER_STATE_FILE = Path(".codex/packet_router/state.json")
CMD = [sys.executable, "codex_packet_handoff/tools/agents_coordinator.py", "--daemon"]
PROC_MATCH = "codex_packet_handoff/tools/agents_coordinator.py --daemon"
LEASE_FRESH_SECONDS = 3600
REPO_ROOT = Path(__file__).resolve().parents[2]
AUTOMATION_MARKERS = (
    "You are the REVIEWER.",
    "You are the FEATURE FIXER",
    "Ready as integrator.",
    "You are the INTEGRATOR",
    "codex mcp-server",
)
DAEMON_LOG_MAX_BYTES = 2 * 1024 * 1024
DAEMON_LOG_KEEP_BYTES = 512 * 1024
APP_CODEX_DIR = "/Applications/Codex.app/Contents/Resources"


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


def _load_json(path: Path) -> dict:
    try:
        import json

        data = json.loads(path.read_text() or "{}")
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _feature_runner_pids() -> list[int]:
    state = _load_json(FEATURE_RUNNER_STATE_FILE)
    lanes = state.get("lanes") if isinstance(state, dict) else {}
    if not isinstance(lanes, dict):
        return []
    pids: list[int] = []
    for lane_state in lanes.values():
        if not isinstance(lane_state, dict):
            continue
        pid = int(lane_state.get("pid", 0) or 0)
        if pid > 0:
            pids.append(pid)
    return pids


def _router_job_pids() -> list[int]:
    state = _load_json(ROUTER_STATE_FILE)
    pids: list[int] = []
    for key in ("fixer_fallback_jobs", "local_reviewer_jobs", "local_integrator_jobs", "cloud_integrator_jobs"):
        jobs = state.get(key) if isinstance(state, dict) else {}
        if not isinstance(jobs, dict):
            continue
        for job in jobs.values():
            if not isinstance(job, dict):
                continue
            pid = int(job.get("pid", 0) or 0)
            if pid > 0:
                pids.append(pid)
    return pids


def _find_automation_worker_pids() -> list[int]:
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
        if "codex exec" not in cmd and "codex mcp-server" not in cmd:
            continue
        if not any(marker in cmd for marker in AUTOMATION_MARKERS):
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
    compact_log_file(LOG_FILE, max_bytes=DAEMON_LOG_MAX_BYTES, keep_bytes=DAEMON_LOG_KEEP_BYTES)
    pid = _read_pid()
    if _is_running():
        print(f"already_running pid={pid}")
        print(f"log={LOG_FILE}")
        return 0

    # Avoid false adoption in sandboxed environments where process listing may be noisy.
    # If daemon is truly live, _is_running() above already returned True.

    with LOG_FILE.open("a") as lf:
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        current_path = env.get("PATH", "")
        path_parts = [p for p in current_path.split(os.pathsep) if p]
        path_parts = [p for p in path_parts if p != APP_CODEX_DIR]
        path_parts.insert(0, APP_CODEX_DIR)
        env["PATH"] = os.pathsep.join(path_parts)
        proc = subprocess.Popen(
            CMD,
            stdin=subprocess.DEVNULL,
            stdout=lf,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True,
            cwd=str(Path.cwd()),
            env=env,
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
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        except OSError:
            os.kill(pid, signal.SIGTERM)
        stopped_any = True
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

    # Ensure no stray matching daemons remain.
    for mpid in _find_matching_pids():
        try:
            os.kill(mpid, signal.SIGTERM)
            stopped_any = True
        except OSError:
            pass

    for worker_pid in sorted(set(_feature_runner_pids() + _find_automation_worker_pids())):
        if not _pid_alive(worker_pid):
            continue
        try:
            os.kill(worker_pid, signal.SIGTERM)
            stopped_any = True
        except OSError:
            continue
    deadline = time.time() + 5
    while time.time() < deadline:
        still_alive = [wpid for wpid in sorted(set(_feature_runner_pids() + _find_automation_worker_pids())) if _pid_alive(wpid)]
        if not still_alive:
            break
        time.sleep(0.2)
    for worker_pid in sorted(set(_feature_runner_pids() + _find_automation_worker_pids())):
        if not _pid_alive(worker_pid):
            continue
        try:
            os.kill(worker_pid, signal.SIGKILL)
            stopped_any = True
        except OSError:
            pass

    tracked_local_exec_pids = set(_feature_runner_pids() + _router_job_pids())
    orphaned_local_exec_pids = find_orphaned_repo_local_exec_pids(REPO_ROOT, tracked_local_exec_pids)
    if orphaned_local_exec_pids:
        terminate_local_exec_pids(orphaned_local_exec_pids)
        stopped_any = True

    stale_test_runner_pids = find_stale_repo_test_runner_pids(REPO_ROOT, tracked_local_exec_pids)
    if stale_test_runner_pids:
        terminate_process_groups(stale_test_runner_pids)
        stopped_any = True

    try:
        PID_FILE.unlink()
    except FileNotFoundError:
        pass

    if stopped_any:
        print("stopped")
        return 0
    print("not_running")
    return 0


def _launchd_run() -> int:
    _ensure_dirs()
    _clear_stale_lease()
    compact_log_file(LOG_FILE, max_bytes=DAEMON_LOG_MAX_BYTES, keep_bytes=DAEMON_LOG_KEEP_BYTES)
    devnull_fd = os.open(os.devnull, os.O_RDONLY)
    try:
        os.dup2(devnull_fd, 0)
    finally:
        with contextlib.suppress(OSError):
            os.close(devnull_fd)
    PID_FILE.write_text(str(os.getpid()))
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    os.execvpe(
        sys.executable,
        [sys.executable, str(REPO_ROOT / "codex_packet_handoff/tools/agents_coordinator.py"), "--daemon"],
        env,
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Start/stop/status for coordinator daemon.")
    ap.add_argument("action", choices=["start", "stop", "status", "launchd-run"])
    args = ap.parse_args()
    if args.action == "start":
        return _start()
    if args.action == "stop":
        return _stop()
    if args.action == "launchd-run":
        return _launchd_run()
    return _status()


if __name__ == "__main__":
    raise SystemExit(main())
