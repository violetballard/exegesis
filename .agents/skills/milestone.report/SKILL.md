---
name: milestone.report
description: "Show the real milestone and roadmap status by combining live pipeline state with ROADMAP.md, docs/milestones.md, and PRODUCT_VISION.md. Use when the user asks where the project truly stands, what changed against milestones, what is done versus just scaffolded, or what is blocking the MVP/demo path."
---

Run from repo root:
- `python codex_packet_handoff/tools/daemon_ctl.py status`
- `python codex_packet_handoff/tools/status.py`
- `python codex_packet_handoff/tools/daemon_monitor.py`
- `for b in codex/feat-context-storage codex/feat-commands codex/feat-retrieval-fts codex/feat-a2ui-contract codex/feat-engine-runs; do printf "%s -> " "$b"; git rev-parse --short "$b"; done`
- Read:
  - `ROADMAP.md`
  - `docs/milestones.md`
  - `PRODUCT_VISION.md`
  - `AGENTS.md`

If the user asks what changed over time:
- compare current lane heads with the last concrete baseline mentioned in the conversation or supplied by the user
- prefer exact commit deltas over vague statements
- be explicit when branch churn increased but queue stage did not change

Use these as the source of truth:
1. `status.py` for queue/lane stage truth
2. `daemon_monitor.py` for heartbeat, bottleneck, and live fixer/reviewer activity
3. `ROADMAP.md` and `docs/milestones.md` for milestone definitions
4. `PRODUCT_VISION.md` for canonical capability names

When reporting milestone status:
- separate `branch movement` from `queue-stage movement`
- separate `engine-real` from `UI-real`
- do not count scaffolding/docs/contracts alone as milestone completion
- if UI lanes are disabled, say that Milestones 1 and 2 are still not product-real
- if Milestone 3 lanes are active but still stuck in `waiting_feature_update`, call Milestone 3 `in progress` and explain that closure has not happened yet
- treat Milestone 4 as partially moving only when infra or engine durability work materially supports dogfooding
- treat Milestone 5 as not ready until there is a repeatable demo path, not just code churn

Preferred output shape:
- `Current Live State`
- `Milestone Scorecard`
- `What Is Done`
- `What Is Moving`
- `What Is Stuck`
- `Best Honest Read`

If the user wants the shortest founder-facing version, collapse to:
- `Green / Yellow / Red`
- one sentence on what is actually standing
- one sentence on the next real closure path

Important honesty rules:
- say `planned`, `scaffolded`, `contract-defined`, `in progress`, or `standing` deliberately
- do not infer milestone closure from commit count alone
- call out when local fallback produced lots of branch churn without queue advancement
- prefer exact milestone names from `ROADMAP.md` over invented labels
