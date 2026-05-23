---
name: provider.switch_codex
description: "Switch Packet Garden active cloud workers back to Codex/OpenAI while preserving Claude as failover and local OpenCode/Gemma workers."
---

Run from repo root:
- `python packet_garden/tools/provider_switch.py codex --order claude codex --restart-daemon`
- `python packet_garden/tools/provider_switch.py status`
- `./packet_garden/tools/status_report.sh`

This switch preserves:
- local OpenCode/Gemma workers
- hybrid runtime mode
- lane enablement and lane priority
- normalized cloud profile names: `worker_cloud`, `worker_cloud_standard_medium`, `integrator_cloud`

Codex mapping:
- `worker_cloud`: GPT 5.5, low reasoning
- `worker_cloud_standard_medium`: GPT 5.5, medium reasoning
- `integrator_cloud`: GPT 5.5, high reasoning

Cloud failover:
- active provider is Codex, useful while draining or exhausting current Codex quota
- preferred order remains Claude, then Codex for future cutover/failover policy
- if Codex quota fails while active, new cloud jobs may switch to Claude before dropping to local-only

Report:
- whether the switch command succeeded
- the active provider summary
- whether daemon restarted
- current runtime status and any immediate launch/auth failure
