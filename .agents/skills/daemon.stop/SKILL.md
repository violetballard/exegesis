---
name: daemon.stop
description: "Stop the event-driven coordinator daemon and clear stale pidfile."
---

Run from repo root:
- `python codex_packet_handoff/tools/daemon_ctl.py stop`

Then verify:
- `python codex_packet_handoff/tools/daemon_ctl.py status`

CLI-first note:
- run this from a Codex CLI session launched with `codex -p gpt-oss-20b-lms -C /Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual`
