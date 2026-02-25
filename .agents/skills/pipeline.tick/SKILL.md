---
name: pipeline.tick
description: Run a bounded loop to simulate 1-min router + 10-min planner cadence inside an hourly Codex Automation.
---

Run from repo root:
- `python codex_packet_handoff/tools/automation_tick.py`

Summarize:
- Any packets emitted by planner (lane + filename)
- Any packets processed by router
- If nothing happened, say so.


Note: lane_meta is not required in inference mode.
