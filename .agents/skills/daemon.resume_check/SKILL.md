---
name: daemon.resume_check
description: Safely resume automation after a pause by starting daemon, verifying status, and printing live monitor + queue summary.
---

Run from repo root:
- `python codex_packet_handoff/tools/daemon_resume_check.py`

This performs:
1. `daemon_ctl.py start`
2. `daemon_ctl.py status` (must show running)
3. `daemon_monitor.py`
4. `status.py`
