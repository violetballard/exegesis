---
name: daemon.start
description: "Start the event-driven coordinator daemon and immediately verify the pipeline dashboard state."
---

Run from repo root:
- `python codex_packet_handoff/tools/daemon_ctl.py start`
- `python codex_packet_handoff/tools/status.py`
- `python codex_packet_handoff/tools/daemon_monitor.py`

CLI-first note:
- assume the operator launched Codex CLI with `codex -p gpt-oss-20b-lms -C /Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual`
- do not rely on app automations; use the Python scripts above as the source of control

Then print:
- whether it started or was already running
- daemon PID
- daemon log path
- whether the queue is idle, active, or blocked
- whether reviewer and integrator sessions are present
