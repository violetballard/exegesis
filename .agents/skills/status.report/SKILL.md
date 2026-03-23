---
name: status.report
description: "Show the real full status report for daemon, reviewer lanes, integrator, and feature-lane activity."
---

Run from repo root:
- `python codex_packet_handoff/tools/status.py`
- `python codex_packet_handoff/tools/daemon_monitor.py`
- `ps -axo pid,etime,command | rg "codex exec|codex_packet_handoff/tools/agents_coordinator.py" || true`
- `for f in $(ls -1t .codex/feature_runner/logs/*.log 2>/dev/null | head -n 5); do echo "FILE:$f"; tail -n 20 "$f"; done`

CLI-first note:
- assume the operator launched Codex CLI with `codex --oss --local-provider lmstudio -m gpt-oss-20b -C /Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual`
- use the Python scripts above as the authoritative status sources

Then summarize:
- filesystem truth per lane (`status.py`)
- daemon state, reviewer/integrator queues, `active_blocker`, and latest lane discussion (`daemon_monitor.py`)
- manual feature-lane Codex activity from process list / feature runner logs
- whether the pipeline is actively progressing, idle, or blocked
- whether any stale fixer/log noise should be ignored because the queue is clean

Reading order:
1. Start with `status.py` totals and lane states.
2. Use `daemon_monitor.py` to read `bottleneck` and `active_blocker`.
3. Only then read reviewer/integrator/lane discussion and daemon-log tail.
4. If daemon-log tail conflicts with queue truth, say so explicitly and prefer queue truth.
5. If `scope-check` appears only in daemon-log tail, call it stale unless queue state points to a current scope-driven stop.

Reference:
- `PIPELINE_RUNBOOK.md`
- `ROADMAP.md`
- `PRODUCT_VISION.md`
- `ARCHITECTURE.md`
