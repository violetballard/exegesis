---
name: daemon.start
description: Start the event-driven coordinator daemon and immediately verify the pipeline dashboard state.
---

Run from repo root:
- `python codex_packet_handoff/tools/daemon_ctl.py start`
- `python codex_packet_handoff/tools/status.py`
- `python codex_packet_handoff/tools/daemon_monitor.py`

Then print:
- whether it started or was already running
- daemon PID
- daemon log path
- whether the queue is idle, active, or blocked
- whether reviewer and integrator sessions are present
