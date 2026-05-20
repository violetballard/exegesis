#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from secrets import token_urlsafe

REPO_ROOT = Path(__file__).resolve().parents[2]
REMOTE_ROOT = REPO_ROOT / ".codex/remote_monitor"
PID_FILE = REMOTE_ROOT / "server.pid"
LOG_FILE = REMOTE_ROOT / "server.log"
SERVER = REPO_ROOT / "packet_garden/tools/remote_monitor_server.py"
DEFAULT_CONFIG = REMOTE_ROOT / "config.json"
DEFAULT_TOKEN_FILE = REMOTE_ROOT / "token"


def init_config(
    config: Path,
    *,
    host: str,
    port: int,
    allowed_cidr: list[str],
    token_file: Path,
    force: bool,
    print_token: bool,
) -> int:
    REMOTE_ROOT.mkdir(parents=True, exist_ok=True)
    resolved_token_file = token_file if token_file.is_absolute() else REPO_ROOT / token_file
    if config.exists() and not force:
        print(f"config_exists={config}")
        print("use --force to replace it")
        return 1
    if resolved_token_file.exists() and not force:
        print(f"token_exists={resolved_token_file}")
        print("use --force to replace it")
        return 1
    token = token_urlsafe(36)
    config.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "host": host,
        "port": port,
        "token_file": str(token_file),
        "token_env": "QUAL_MONITOR_TOKEN",
        "allowed_remote_cidrs": allowed_cidr,
        "operator_label": "remote-monitor",
        "snapshot_ttl_seconds": 10,
    }
    config.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    resolved_token_file.parent.mkdir(parents=True, exist_ok=True)
    resolved_token_file.write_text(token + "\n")
    os.chmod(resolved_token_file, 0o600)
    print(f"config={config}")
    print(f"token_file={resolved_token_file}")
    print(f"monitor_url=http://{host}:{port}")
    if print_token:
        print(f"token={token}")
    else:
        print("token=<written; rerun with --print-token only when ready to paste into iPhone Shortcuts>")
    return 0


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except PermissionError:
        # Sandboxed local checks may not be allowed to signal a live detached
        # process. Treat EPERM as alive rather than reporting a false negative.
        return True
    except OSError:
        return False


def _read_pid() -> int | None:
    try:
        raw = PID_FILE.read_text().strip()
        return int(raw) if raw else None
    except Exception:
        return None


def _config_port(config: Path = DEFAULT_CONFIG) -> int:
    try:
        data = json.loads(config.read_text())
        return int(data.get("port") or 8765)
    except Exception:
        return 8765


def _listener_pids(port: int) -> list[int]:
    try:
        proc = subprocess.run(
            ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
            text=True,
            capture_output=True,
            timeout=3,
        )
    except Exception:
        return []
    pids: list[int] = []
    for line in proc.stdout.splitlines():
        try:
            pid = int(line.strip())
        except ValueError:
            continue
        if pid > 0 and _pid_alive(pid):
            pids.append(pid)
    return pids


def _effective_pid(config: Path = DEFAULT_CONFIG) -> int | None:
    pid = _read_pid()
    if pid and _pid_alive(pid):
        return pid
    listeners = _listener_pids(_config_port(config))
    if listeners:
        PID_FILE.write_text(str(listeners[0]))
        return listeners[0]
    return None


def status(config: Path = DEFAULT_CONFIG) -> int:
    pid = _effective_pid(config)
    running = bool(pid and _pid_alive(pid))
    print(f"remote_monitor_running={running}")
    print(f"pid={pid or '-'}")
    print(f"log={LOG_FILE}")
    return 0 if running else 1


def start(config: Path) -> int:
    REMOTE_ROOT.mkdir(parents=True, exist_ok=True)
    pid = _effective_pid(config)
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
    pid = _effective_pid()
    pids = [pid] if pid and _pid_alive(pid) else []
    for listener_pid in _listener_pids(_config_port()):
        if listener_pid not in pids:
            pids.append(listener_pid)
    if not pids:
        PID_FILE.unlink(missing_ok=True)
        print("not_running")
        return 0
    for target_pid in pids:
        try:
            os.killpg(os.getpgid(target_pid), signal.SIGTERM)
        except OSError:
            os.kill(target_pid, signal.SIGTERM)
    deadline = time.time() + 5
    while time.time() < deadline:
        if not any(_pid_alive(target_pid) for target_pid in pids):
            break
        time.sleep(0.2)
    for target_pid in pids:
        if _pid_alive(target_pid):
            try:
                os.killpg(os.getpgid(target_pid), signal.SIGKILL)
            except OSError:
                os.kill(target_pid, signal.SIGKILL)
    PID_FILE.unlink(missing_ok=True)
    print("stopped")
    return 0


def launchd_run(config: Path) -> int:
    REMOTE_ROOT.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))
    os.execvpe(
        sys.executable,
        [sys.executable, str(SERVER), "--config", str(config)],
        os.environ.copy(),
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Start/stop/status for the qual remote monitor server.")
    parser.add_argument("action", choices=["init", "start", "stop", "status", "launchd-run"])
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--allowed-cidr", action="append", default=[])
    parser.add_argument("--token-file", type=Path, default=Path(".codex/remote_monitor/token"))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--print-token", action="store_true")
    args = parser.parse_args()
    if args.action == "init":
        return init_config(
            args.config,
            host=args.host,
            port=args.port,
            allowed_cidr=list(args.allowed_cidr or []),
            token_file=args.token_file,
            force=args.force,
            print_token=args.print_token,
        )
    if args.action == "start":
        return start(args.config)
    if args.action == "stop":
        return stop()
    if args.action == "launchd-run":
        return launchd_run(args.config)
    return status(args.config)


if __name__ == "__main__":
    raise SystemExit(main())
