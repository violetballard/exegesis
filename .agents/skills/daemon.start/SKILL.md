---
name: daemon.start
description: "Start the event-driven coordinator daemon and immediately verify the pipeline dashboard state."
---

Run from repo root:
- `python codex_packet_handoff/tools/daemon_ctl.py start`
- `python codex_packet_handoff/tools/daemon_ctl.py status`
- `python codex_packet_handoff/tools/status.py`
- `python codex_packet_handoff/tools/daemon_monitor.py`
- `ps -axo pid,etime,command | rg "codex exec|codex_packet_handoff/tools/agents_coordinator.py" || true`
- `for f in $(ls -1t .codex/feature_runner/logs/*.log 2>/dev/null | head -n 3); do echo "FILE:$f"; tail -n 20 "$f"; done`
- `tail -n 50 .codex/packet_coordinator/daemon.log 2>/dev/null || true`

CLI-first note:
- assume the operator launched Codex CLI with `codex --oss --local-provider lmstudio -m gpt-oss-20b -C /Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual`
- do not rely on app automations; use the Python scripts above as the source of control

Then print:
- whether it started or was already running
- daemon PID
- daemon log path
- the full queue truth from `status.py`
- the current `active_blocker` and heartbeat from `daemon_monitor.py`
- whether the queue is idle, active, or blocked
- whether reviewer and integrator sessions are present
- any important live-log lines that explain the current state
