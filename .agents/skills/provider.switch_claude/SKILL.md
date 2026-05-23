---
name: provider.switch_claude
description: "Switch Packet Garden cloud workers to Claude CLI while preserving local OpenCode/Gemma workers."
---

Run from repo root:
- `python packet_garden/tools/provider_switch.py claude --order claude codex --mark-codex-unavailable --reason "codex quota exhausted" --restart-daemon`
- `python packet_garden/tools/provider_switch.py status`
- `./packet_garden/tools/status_report.sh`

This switch preserves:
- local OpenCode/Gemma workers
- hybrid runtime mode
- lane enablement and lane priority
- normalized cloud profile names: `worker_cloud`, `worker_cloud_standard_medium`, `integrator_cloud`

Claude mapping:
- `worker_cloud`: Sonnet, low effort
- `worker_cloud_standard_medium`: Sonnet, medium effort
- `integrator_cloud`: Opus, high effort

Cloud failover:
- preferred order is Claude, then Codex
- when Codex quota is known exhausted, mark Codex unavailable with a retry cooldown instead of treating it as live
- if Claude quota/auth fails after Codex's cooldown expires, new cloud jobs may fall back to Codex
- if both cloud providers are unavailable, local Gemma/OpenCode remains active

Report:
- whether the switch command succeeded
- the active provider summary
- whether daemon restarted
- current runtime status and any immediate launch/auth failure
