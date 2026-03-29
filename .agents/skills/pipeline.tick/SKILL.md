---
name: pipeline.tick
description: "Run the event-driven coordinator to process planner/review/fix/integrate handoffs until idle."
---

Run from repo root:
- `python codex_packet_handoff/tools/agents_coordinator.py --once`
- `python codex_packet_handoff/tools/status.py`
- `python codex_packet_handoff/tools/daemon_monitor.py`
- `tail -n 60 .codex/packet_coordinator/daemon.log 2>/dev/null || true`
- `for f in $(ls -1t .codex/packet_router/logs/*.log 2>/dev/null | head -n 3); do echo "FILE:$f"; tail -n 30 "$f"; done`

CLI-first note:
- assume the operator launched Codex CLI with `codex --oss --local-provider lmstudio -m gpt-oss-20b -C /Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual`
- this skill should call the Python coordinator directly rather than using app-side automation features

Summarize:
- Any packets emitted by planner (lane + filename)
- Any packets processed by router
- The post-tick queue truth from `status.py`
- Any live-log evidence that explains slow local fallback or router/integrator behavior
- If nothing happened, say so.


Mode notes:
- Default is direct event-driven orchestration (`--execution-mode direct`).
- Use daemon for continuous orchestration:
- `python codex_packet_handoff/tools/agents_coordinator.py --daemon`
- Use subprocess mode only for break-glass fallback:
- `python codex_packet_handoff/tools/agents_coordinator.py --execution-mode subprocess`
