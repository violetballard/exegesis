---
name: planner.run
description: "Emit feature→review packets into .codex by running the local planner."
---

Execute from repo root:
- `python packet_garden/tools/planner.py`

Access path selection:
- This is a local-only direct script skill.
- If this session is remote over VPN and local scripts are unavailable, do not run planner remotely.
- Use `python packet_garden/tools/remote_monitor_client.py kick` only to wake the already-running daemon; remote monitor intentionally does not expose direct planner execution.

CLI-first note:
- run from a Codex CLI session launched with `codex --oss --local-provider lmstudio -m gpt-oss-20b -C /Users/doctor-violet/projects/exegesis`

Then summarize emitted packets (lane + filename). If none: "No packets emitted."
