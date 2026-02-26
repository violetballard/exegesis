# Codex self-contained automations: planner + router

This package is meant to be run via **Codex App Automations** so everything stays inside Codex.

## One-time setup
From repo root:

```bash
python codex_packet_handoff/tools/setup.py
python codex_packet_handoff/tools/init_lane_meta.py
cp .codex/packet_router/example.json .codex/packet_router/config.json
```

Fill each `.codex/lane_meta/<lane>.json` with required fields (roadmap items, vision capabilities, tasks completed, etc.).
Planner refuses to emit if those are missing.

## What runs on a schedule
- Planner: `python codex_packet_handoff/tools/planner.py`
- Router:  `python codex_packet_handoff/tools/router.py` (process once and exit)
- Coordinator (Phase 1 wrapper): `python codex_packet_handoff/tools/agents_coordinator.py`

Reviewer is enforced **read-only**; Integrator is **workspace-write**.

## Add the skills (so automations are 1-liners)
This zip includes skills under:
`codex_packet_handoff/.agents/skills/{planner.run,router.run}`

Copy the `.agents/skills/...` folders into your repo's `.agents/skills/`.

## Create Codex Automations (Desktop)
Create two recurring automations:

### Automation 1 (Planner)
Schedule: every 5–10 minutes  
Prompt: `Run the skill planner.run`

### Automation 2 (Router)
Schedule: every 1–2 minutes  
Prompt: `Run the skill router.run`

Tip: run Router more frequently than Planner. Planner is heavier (runs gates).

## Coordinator-first automation (required)

Use a single automation prompt:

`Run the skill pipeline.tick`

The skill runs `agents_coordinator.py` in direct mode by default:
- planner execution is orchestrated by coordinator
- reviewer/fixer/integrator routing uses a persistent direct session context
- packet/state formats remain compatible with existing lane files

Fallback mode exists for incident response only:
- `python codex_packet_handoff/tools/agents_coordinator.py --execution-mode subprocess`

## Notes
Planner switches branches inside the automation's dedicated background worktree, so it won't disturb your interactive worktrees.
