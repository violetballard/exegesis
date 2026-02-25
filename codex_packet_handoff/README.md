# Codex packet handoff (inference mode + worktree-safe planner)

- Planner emits minimal packets (no lane_meta).
- Reviewer infers/enforces plan mapping using ROADMAP.md / PRODUCT_VISION.md / ARCHITECTURE.md and rejects if unclear.
- Planner uses detached checkout at the branch SHA so it won't conflict with Codex worktrees.

## Setup
```bash
python codex_packet_handoff/tools/setup.py
cp .codex/packet_router/example.json .codex/packet_router/config.json
```

## Codex Automations (hourly-only UI)
Create an hourly automation with prompt:
- `Run the skill pipeline.tick`

That runs 25 minutes:
- router every 1 minute
- planner every 10 minutes


(Updated router now uses MCP tools `codex` and `codex-reply` via `tools/call`, which matches current Codex MCP server behavior.)


## Status report (pause-and-peek)
Run:
- `python codex_packet_handoff/tools/status.py`

Or in Codex, run the skill:
- `status.report`

This summarizes per lane what is pending, in review, approved, and latest integrator output.
