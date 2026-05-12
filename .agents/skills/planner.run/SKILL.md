---
name: planner.run
description: "Emit feature→review packets into .codex by running the local planner."
---

Execute from repo root:
- `python codex_packet_handoff/tools/planner.py`

CLI-first note:
- run from a Codex CLI session launched with `codex --oss --local-provider lmstudio -m gpt-oss-20b -C /Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual`

Then summarize emitted packets (lane + filename). If none: "No packets emitted."
