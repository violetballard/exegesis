---
name: daemon.monitor
description: "Show the full live pipeline dashboard: daemon state, queue truth, reviewer/integrator status, lane summaries, and manual feature-session activity."
---

Run from repo root:
- `python codex_packet_handoff/tools/status.py`
- `python codex_packet_handoff/tools/daemon_monitor.py`
- `ps -axo pid,etime,command | rg "codex exec|codex_packet_handoff/tools/agents_coordinator.py" || true`
- `for f in $(ls -1t .codex/feature_runner/logs/*.log 2>/dev/null | head -n 5); do echo "FILE:$f"; tail -n 30 "$f"; done`

CLI-first note:
- assume the operator launched Codex CLI with `codex -p gpt-oss-20b-lms -C /Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual`
- use the Python scripts above; do not infer daemon state from chat history alone

If daemon is not running, also run:
- `python codex_packet_handoff/tools/daemon_ctl.py status`

Then summarize all of these together:
- filesystem truth per lane from `status.py`
- daemon running/stopped state
- backlog bottleneck
- reviewer lane state for all five lanes
- reviewer thread ids and integrator thread id
- latest live discussion summary for reviewer, integrator, and each feature lane
- whether manual feature sessions are running outside daemon
- whether the system is actively progressing, idle, or blocked

Reference:
- `PIPELINE_RUNBOOK.md`
- `ROADMAP.md`
- `PRODUCT_VISION.md`
- `ARCHITECTURE.md`
