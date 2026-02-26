---
name: daemon.stop
description: Stop the event-driven coordinator daemon and clear stale pidfile.
---

Run from repo root:
- `python codex_packet_handoff/tools/daemon_ctl.py stop`

Then verify:
- `python codex_packet_handoff/tools/daemon_ctl.py status`
