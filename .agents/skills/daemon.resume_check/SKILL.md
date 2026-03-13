---
name: daemon.resume_check
description: Safely resume automation after a pause by starting daemon, verifying status, and printing the full pipeline dashboard.
---

Run from repo root:
- `python codex_packet_handoff/tools/daemon_resume_check.py`
- `python codex_packet_handoff/tools/status.py`
- `python codex_packet_handoff/tools/daemon_monitor.py`
- `ps -axo pid,etime,command | rg "codex exec|codex_packet_handoff/tools/agents_coordinator.py" || true`

This performs:
1. `daemon_ctl.py start`
2. `daemon_ctl.py status` (must show running)
3. `daemon_monitor.py`
4. `status.py`

After running, report:
- whether daemon resumed successfully
- whether the queue is idle or has work
- whether reviewer/integrator lanes are attached
- whether any manual feature sessions are also running
- the next blocking condition, if any

Reference:
- `PIPELINE_RUNBOOK.md`
