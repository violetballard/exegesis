---
name: daemon.resume_check
description: "Safely resume automation after a pause by starting daemon, verifying status, and printing the full pipeline dashboard."
---

Run from repo root:
- `python codex_packet_handoff/tools/daemon_resume_check.py`
- `python codex_packet_handoff/tools/daemon_ctl.py status`
- `python codex_packet_handoff/tools/status.py`
- `python codex_packet_handoff/tools/daemon_monitor.py`
- `ps -axo pid,etime,command | rg "codex exec|codex_packet_handoff/tools/agents_coordinator.py" || true`
- `for f in $(ls -1t .codex/feature_runner/logs/*.log 2>/dev/null | head -n 3); do echo "FILE:$f"; tail -n 20 "$f"; done`
- `for f in $(ls -1t .codex/packet_router/logs/*.log 2>/dev/null | head -n 3); do echo "FILE:$f"; tail -n 30 "$f"; done`
- `tail -n 60 .codex/packet_coordinator/daemon.log 2>/dev/null || true`

CLI-first note:
- assume the operator launched Codex CLI with `codex --oss --local-provider lmstudio -m gpt-oss-20b -C /Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual`
- use only the Python scripts above for resume/status control

This performs:
1. `daemon_ctl.py start`
2. `daemon_ctl.py status` (must show running)
3. `daemon_monitor.py`
4. `status.py`

After running, report:
- whether daemon resumed successfully
- the full queue truth from `status.py`
- whether the queue is idle or has work
- whether reviewer/integrator lanes are attached
- whether any manual feature sessions are also running
- the next blocking condition, if any
- the most relevant live-log evidence, clearly separated from queue truth

Reference:
- `PIPELINE_RUNBOOK.md`
