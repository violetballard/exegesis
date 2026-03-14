---
name: pipeline.tick
description: "Run the event-driven coordinator to process planner/review/fix/integrate handoffs until idle."
---

Run from repo root:
- `python codex_packet_handoff/tools/agents_coordinator.py --once`

Summarize:
- Any packets emitted by planner (lane + filename)
- Any packets processed by router
- If nothing happened, say so.


Mode notes:
- Default is direct event-driven orchestration (`--execution-mode direct`).
- Use daemon for continuous orchestration:
- `python codex_packet_handoff/tools/agents_coordinator.py --daemon`
- Use subprocess mode only for break-glass fallback:
- `python codex_packet_handoff/tools/agents_coordinator.py --execution-mode subprocess`
