---
name: status.report
description: Show the real full status report for daemon, reviewer lanes, integrator, and feature-lane activity.
---

Run from repo root:
- `python codex_packet_handoff/tools/status.py`
- `python codex_packet_handoff/tools/daemon_monitor.py`
- `ps -axo pid,etime,command | rg "codex exec|codex_packet_handoff/tools/agents_coordinator.py" || true`
- `for f in $(ls -1t .codex/feature_runner/logs/*.log 2>/dev/null | head -n 5); do echo "FILE:$f"; tail -n 20 "$f"; done`

Then summarize:
- filesystem truth per lane (`status.py`)
- daemon state, reviewer/integrator queues, and latest lane discussion (`daemon_monitor.py`)
- manual feature-lane Codex activity from process list / feature runner logs
- whether the pipeline is actively progressing, idle, or blocked
- whether any stale fixer/log noise should be ignored because the queue is clean

Reference:
- `PIPELINE_RUNBOOK.md`
- `ROADMAP.md`
- `PRODUCT_VISION.md`
- `ARCHITECTURE.md`
