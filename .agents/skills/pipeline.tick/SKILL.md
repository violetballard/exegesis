---
name: pipeline.tick
description: Run a bounded loop to simulate 1-min router + 10-min planner cadence inside an hourly Codex Automation.
---

Run from repo root:
- `python codex_packet_handoff/tools/agents_coordinator.py`

Summarize:
- Any packets emitted by planner (lane + filename)
- Any packets processed by router
- If nothing happened, say so.


Note: lane_meta is not required in inference mode.
Phase 1 migration note: this coordinator preserves existing planner/router packet contracts.
