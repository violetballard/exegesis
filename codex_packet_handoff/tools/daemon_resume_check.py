#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys


def _run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.stdout or ""
    if out:
        print(out, end="" if out.endswith("\n") else "\n")
    return p.returncode, out


def main() -> int:
    print("=== RESUME CHECK: START ===")
    _run([sys.executable, "codex_packet_handoff/tools/daemon_ctl.py", "start"])

    print("=== RESUME CHECK: STATUS ===")
    status_rc, status_out = _run([sys.executable, "codex_packet_handoff/tools/daemon_ctl.py", "status"])
    if "daemon_running=True" not in status_out:
        print("[resume-check] daemon is not running after start; aborting checks")
        return 1 if status_rc == 0 else status_rc

    print("=== RESUME CHECK: MONITOR ===")
    _run([sys.executable, "codex_packet_handoff/tools/daemon_monitor.py"])

    print("=== RESUME CHECK: PIPELINE STATUS ===")
    _run([sys.executable, "codex_packet_handoff/tools/status.py"])

    print("=== RESUME CHECK: DONE ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
