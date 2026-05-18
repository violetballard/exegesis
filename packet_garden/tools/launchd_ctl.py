#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import plistlib
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
LAUNCH_AGENT_DIR = Path.home() / "Library/LaunchAgents"
LAUNCHD_RUNTIME_ROOT = REPO_ROOT / ".codex/launchd"
PYTHON = sys.executable


@dataclass(frozen=True)
class Service:
    name: str
    label: str
    wrapper_name: str
    wrapper_text: str
    stdout_name: str = "stdout.log"
    stderr_name: str = "stderr.log"
    keep_alive: bool = True

    @property
    def runtime_dir(self) -> Path:
        return LAUNCHD_RUNTIME_ROOT / self.name

    @property
    def wrapper_path(self) -> Path:
        return self.runtime_dir / self.wrapper_name

    @property
    def plist_path(self) -> Path:
        return LAUNCH_AGENT_DIR / f"{self.label}.plist"

    @property
    def stdout_path(self) -> Path:
        return self.runtime_dir / self.stdout_name

    @property
    def stderr_path(self) -> Path:
        return self.runtime_dir / self.stderr_name


def _shell_wrapper() -> str:
    worktree = REPO_ROOT / ".codex/worktrees/client-textual/qual"
    venv_python = REPO_ROOT / ".codex/shell-venv/bin/python"
    textual = REPO_ROOT / ".codex/shell-venv/bin/textual"
    log_dir = REPO_ROOT / ".codex/shell"
    return f"""#!/bin/zsh
set -euo pipefail

REPO_ROOT={str(REPO_ROOT)!r}
WORKTREE={str(worktree)!r}
VENV_PYTHON={str(venv_python)!r}
TEXTUAL={str(textual)!r}
SHELL_DIR={str(log_dir)!r}
mkdir -p "$SHELL_DIR"
cd "$WORKTREE"
echo $$ > "$SHELL_DIR/server.pid"
echo $$ > "$SHELL_DIR/serve_parent.pid"
echo "$WORKTREE" > "$SHELL_DIR/source_worktree"
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$WORKTREE:$WORKTREE/client-textual/src"
exec "$TEXTUAL" serve -h 127.0.0.1 -p 8000 -t Exegesis -c "$VENV_PYTHON -m exegesis_textual.app.main"
"""


SERVICES: Dict[str, Service] = {
    "daemon": Service(
        name="daemon",
        label="com.exegesis.packet-coordinator",
        wrapper_name="run-daemon.sh",
        stdout_name="daemon.log",
        stderr_name="daemon.err.log",
        wrapper_text=f"""#!/bin/zsh
set -euo pipefail

REPO_ROOT={str(REPO_ROOT)!r}
cd "$REPO_ROOT"
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
exec {str(PYTHON)!r} "$REPO_ROOT/packet_garden/tools/daemon_ctl.py" launchd-run
""",
    ),
    "monitor": Service(
        name="monitor",
        label="com.exegesis.remote-monitor",
        wrapper_name="run-monitor.sh",
        stdout_name="monitor.log",
        stderr_name="monitor.err.log",
        wrapper_text=f"""#!/bin/zsh
set -euo pipefail

REPO_ROOT={str(REPO_ROOT)!r}
cd "$REPO_ROOT"
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
exec {str(PYTHON)!r} "$REPO_ROOT/packet_garden/tools/remote_monitor_ctl.py" launchd-run
""",
    ),
    "shell": Service(
        name="shell",
        label="com.exegesis.textual-shell",
        wrapper_name="run-shell.sh",
        stdout_name="shell.log",
        stderr_name="shell.err.log",
        wrapper_text=_shell_wrapper(),
    ),
}

# Clean up the pre-relocation daemon label if it was installed from the older helper.
LEGACY_LABELS = ("com.qual.packet-coordinator",)


def _domain_target() -> str:
    return f"gui/{os.getuid()}"


def _label_target(label: str) -> str:
    return f"{_domain_target()}/{label}"


def _run(args: list[str], *, check: bool = True, timeout: float | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=check,
        timeout=timeout,
    )


def _kickstart(label: str) -> None:
    try:
        _run(["launchctl", "kickstart", "-k", _label_target(label)], check=False, timeout=5)
    except subprocess.TimeoutExpired:
        print(f"kickstart_timeout label={label}; service may still be running")


def _bootout_label(label: str) -> None:
    subprocess.run(["launchctl", "bootout", _label_target(label)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)


def _plist_dict(service: Service) -> Dict[str, Any]:
    return {
        "Label": service.label,
        "ProgramArguments": ["/bin/zsh", str(service.wrapper_path)],
        "WorkingDirectory": str(service.runtime_dir),
        "RunAtLoad": True,
        "KeepAlive": service.keep_alive,
        "StandardOutPath": str(service.stdout_path),
        "StandardErrorPath": str(service.stderr_path),
        "EnvironmentVariables": {
            "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "QUAL_REPO_ROOT": str(REPO_ROOT),
            "QUAL_MANAGED_WORKTREE_ROOT": str(REPO_ROOT / ".codex/worktrees"),
        },
    }


def _write_service(service: Service) -> None:
    service.runtime_dir.mkdir(parents=True, exist_ok=True)
    service.wrapper_path.write_text(service.wrapper_text, encoding="utf-8")
    service.wrapper_path.chmod(0o755)
    LAUNCH_AGENT_DIR.mkdir(parents=True, exist_ok=True)
    with service.plist_path.open("wb") as handle:
        plistlib.dump(_plist_dict(service), handle, sort_keys=True)


def _services(selection: str) -> list[Service]:
    if selection == "all":
        return [SERVICES[name] for name in ("daemon", "monitor", "shell")]
    return [SERVICES[selection]]


def install(selection: str) -> int:
    for label in LEGACY_LABELS:
        _bootout_label(label)
    for service in _services(selection):
        _write_service(service)
        _bootout_label(service.label)
        _run(["launchctl", "bootstrap", _domain_target(), str(service.plist_path)])
        _run(["launchctl", "enable", _label_target(service.label)], check=False)
        _kickstart(service.label)
        print(f"installed service={service.name} label={service.label}")
        print(f"plist={service.plist_path}")
    return 0


def uninstall(selection: str) -> int:
    for service in _services(selection):
        _bootout_label(service.label)
        if service.plist_path.exists():
            service.plist_path.unlink()
        print(f"removed service={service.name} label={service.label}")
    return 0


def start(selection: str) -> int:
    for service in _services(selection):
        if not service.plist_path.exists():
            _write_service(service)
        _run(["launchctl", "bootstrap", _domain_target(), str(service.plist_path)], check=False)
        _run(["launchctl", "enable", _label_target(service.label)], check=False)
        _kickstart(service.label)
        print(f"started service={service.name} label={service.label}")
    return 0


def stop(selection: str) -> int:
    for service in _services(selection):
        _bootout_label(service.label)
        print(f"stopped service={service.name} label={service.label}")
    return 0


def status(selection: str) -> int:
    rc = 0
    for service in _services(selection):
        proc = subprocess.run(
            ["launchctl", "print", _label_target(service.label)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        loaded = proc.returncode == 0
        if not loaded:
            rc = 1
        print(f"service={service.name}")
        print(f"loaded={loaded}")
        print(f"label={service.label}")
        print(f"plist={service.plist_path}")
        if loaded:
            for line in proc.stdout.splitlines():
                stripped = line.strip()
                if stripped.startswith(("state =", "pid =", "last exit code =")):
                    print(stripped)
        print()
    return rc


def main() -> int:
    ap = argparse.ArgumentParser(description="Install and control Exegesis user LaunchAgents.")
    ap.add_argument("action", choices=["install", "uninstall", "start", "stop", "status"])
    ap.add_argument("service", choices=["daemon", "monitor", "shell", "all"], nargs="?", default="all")
    args = ap.parse_args()
    return {
        "install": install,
        "uninstall": uninstall,
        "start": start,
        "stop": stop,
        "status": status,
    }[args.action](args.service)


if __name__ == "__main__":
    raise SystemExit(main())
