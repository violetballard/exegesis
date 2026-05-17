---
name: router.run
description: "Route pending packets through reviewer/integrator once (automation-friendly)."
---

Execute from repo root:
- `python codex_packet_handoff/tools/router.py`

Access path selection:
- This is a local-only direct script skill.
- If this session is remote over VPN and local scripts are unavailable, do not run router remotely.
- Use `python codex_packet_handoff/tools/remote_monitor_client.py kick` only when the goal is to wake the daemon for one reconcile cycle.

CLI-first note:
- run from a Codex CLI session launched with `codex --oss --local-provider lmstudio -m gpt-oss-20b -C /Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual`
- this script is the direct control surface for one routing pass

Then summarize what was processed.
