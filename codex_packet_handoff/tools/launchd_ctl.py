#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import plistlib
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parents[2]
LAUNCH_AGENT_DIR = Path.home() / "Library/LaunchAgents"
LABEL = "com.qual.packet-coordinator"
PLIST_PATH = LAUNCH_AGENT_DIR / f"{LABEL}.plist"
LAUNCHD_RUNTIME_DIR = Path.home() / ".codex/launchd" / LABEL
COORD_DIR = LAUNCHD_RUNTIME_DIR
DAEMON_CTL = REPO_ROOT / "codex_packet_handoff/tools/daemon_ctl.py"
LAUNCHD_WRAPPER = LAUNCHD_RUNTIME_DIR / "launchd_daemon.sh"
LOG_FILE = COORD_DIR / "daemon.log"
ERR_FILE = COORD_DIR / "daemon.err.log"


def _domain_target() -> str:
    return f"gui/{os.getuid()}"


def _label_target() -> str:
    return f"{_domain_target()}/{LABEL}"


def _run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=check)


def _plist_dict() -> Dict[str, Any]:
    return {
        "Label": LABEL,
        "ProgramArguments": ["/bin/zsh", str(LAUNCHD_WRAPPER)],
        "WorkingDirectory": str(LAUNCHD_RUNTIME_DIR),
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": str(LOG_FILE),
        "StandardErrorPath": str(ERR_FILE),
        "EnvironmentVariables": {
            "PYTHONUNBUFFERED": "1",
            "QUAL_REPO_ROOT": str(REPO_ROOT),
        },
    }


def _write_wrapper() -> None:
    LAUNCHD_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    wrapper_text = (
        "#!/bin/zsh\n"
        "set -euo pipefail\n\n"
        f"REPO_ROOT={str(REPO_ROOT)!r}\n"
        "cd \"$REPO_ROOT\"\n"
        f"exec /usr/bin/python3 {str(DAEMON_CTL)!r} launchd-run\n"
    )
    LAUNCHD_WRAPPER.write_text(wrapper_text, encoding="utf-8")
    LAUNCHD_WRAPPER.chmod(0o755)


def _write_plist() -> None:
    LAUNCH_AGENT_DIR.mkdir(parents=True, exist_ok=True)
    COORD_DIR.mkdir(parents=True, exist_ok=True)
    _write_wrapper()
    with PLIST_PATH.open("wb") as handle:
        plistlib.dump(_plist_dict(), handle, sort_keys=True)


def _bootout_if_loaded() -> None:
    subprocess.run(["launchctl", "bootout", _label_target()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)


def install() -> int:
    _write_plist()
    subprocess.run([sys.executable, str(DAEMON_CTL), "stop"], cwd=str(REPO_ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    _bootout_if_loaded()
    _run(["launchctl", "bootstrap", _domain_target(), str(PLIST_PATH)])
    _run(["launchctl", "enable", _label_target()], check=False)
    _run(["launchctl", "kickstart", "-k", _label_target()])
    print(f"installed label={LABEL}")
    print(f"plist={PLIST_PATH}")
    return 0


def uninstall() -> int:
    _bootout_if_loaded()
    if PLIST_PATH.exists():
        PLIST_PATH.unlink()
    print(f"removed label={LABEL}")
    return 0


def start() -> int:
    if not PLIST_PATH.exists():
        return install()
    _run(["launchctl", "bootstrap", _domain_target(), str(PLIST_PATH)], check=False)
    _run(["launchctl", "enable", _label_target()], check=False)
    _run(["launchctl", "kickstart", "-k", _label_target()])
    print(f"started label={LABEL}")
    return 0


def stop() -> int:
    _bootout_if_loaded()
    print(f"stopped label={LABEL}")
    return 0


def status() -> int:
    proc = subprocess.run(["launchctl", "print", _label_target()], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
    if proc.returncode != 0:
        print("loaded=False")
        print(f"plist={PLIST_PATH}")
        return 1
    print("loaded=True")
    print(f"plist={PLIST_PATH}")
    print(proc.stdout.strip())
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Install and control the packet coordinator LaunchAgent.")
    ap.add_argument("action", choices=["install", "uninstall", "start", "stop", "status"])
    args = ap.parse_args()
    return {
        "install": install,
        "uninstall": uninstall,
        "start": start,
        "stop": stop,
        "status": status,
    }[args.action]()


if __name__ == "__main__":
    raise SystemExit(main())
