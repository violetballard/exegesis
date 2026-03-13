---
name: status.report
description: Show current packet pipeline status per lane plus the richer daemon dashboard context.
---

Run from repo root:
- `python codex_packet_handoff/tools/status.py`
- `python codex_packet_handoff/tools/daemon_monitor.py`

Then summarize:
- filesystem truth per lane (`status.py`)
- daemon state, reviewer/integrator queues, and latest lane discussion (`daemon_monitor.py`)
- whether the pipeline is actively progressing, idle, or blocked

Reference:
- `PIPELINE_RUNBOOK.md`
- `ROADMAP.md`
- `PRODUCT_VISION.md`
- `ARCHITECTURE.md`
