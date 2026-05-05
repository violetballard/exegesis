---
name: milestone.report
description: "Show real milestone status as feature/capability closure, using live pipeline state only as evidence. Use when the user asks where the project truly stands, what features are closed, what remains open, or what blocks the MVP/demo path."
---

Run from repo root:
- `python codex_packet_handoff/tools/daemon_ctl.py status`
- `python codex_packet_handoff/tools/status.py`
- `python codex_packet_handoff/tools/daemon_monitor.py`
- Read:
  - `ROADMAP.md`
  - `docs/milestones.md`
  - `docs/TASKS.md`
  - `PRODUCT_VISION.md`
  - `AGENTS.md`

Optional branch evidence, only if needed to explain why a feature is not closed:
- `for b in codex/feat-context-storage codex/feat-commands codex/feat-retrieval-fts codex/feat-a2ui-contract codex/feat-engine-runs; do printf "%s -> " "$b"; git rev-parse --short "$b"; done`

Core reporting rule:
- Report milestone progress as feature/capability closure, not lane movement.
- The user does not want "lane X is active" as milestone status.
- Use lane/queue status only to explain evidence, blockers, or why a feature is not closed yet.

Use these as the source of truth:
1. `ROADMAP.md` and `docs/milestones.md` for milestone feature definitions and exit criteria
2. `docs/TASKS.md` for which implementation areas map to those features
3. `status.py` for whether packets are waiting, approved, or blocked
4. `daemon_monitor.py` for heartbeat, bottleneck, and active blocker evidence
5. `PRODUCT_VISION.md` for canonical capability names

When reporting milestone status:
- Start from milestone exit criteria and turn them into checkboxes.
- Each checkbox should be a user-visible feature or engine capability, for example:
  - persist project/document/basket/session state
  - retrieve structured results suitable for basket promotion
  - promote or gather context into the basket
  - produce plan/draft/revision through canonical app service
  - preview and apply/reject a patch
  - save and continue across sessions
- Mark a feature `[x]` only when it is actually closed/standing, not merely in progress on a lane.
- Use `[~]` for partially standing or scaffolded capabilities when useful, but explain the remaining gap.
- Use `[ ]` for open capabilities.
- Avoid saying "moving" unless immediately tied to a feature closure path.
- Avoid branch head/commit churn unless the user asks for implementation activity.
- Separate `mockup-real`, `engine-real`, and `product-real` when a feature exists in one layer but not another.
- If UI lanes are disabled, do not count UI mockup behavior as engine/product closure unless explicitly reporting mockup status.
- Treat Milestone 3 as closed only when the canonical engine loop is feature-complete enough to run through CLI/app service.
- Treat Milestone 4 as closed only when the same loop is durable enough for repeated real writing sessions.
- Treat Milestone 5 as not ready until there is a repeatable demo path, not just code churn.

Preferred output shape:
- `Feature Closure Snapshot`
- `Milestone 3 Checklist`
- `Milestone 4 Checklist`
- `Open Blockers`
- `Best Honest Read`

For Milestone 3 checklist, prefer these capability checkboxes unless roadmap wording changes:
- persist project/document/basket/session state
- retrieve/search FTS-first through canonical engine contract
- return structured retrieval results suitable for basket promotion
- promote/gather context into basket through engine path
- produce plan/draft/revision through canonical app service
- preview patch/revision proposal
- apply/reject patch through canonical service
- CLI can run the MVP loop while Textual remains disabled
- one engine-side retrieve -> basket -> plan/revise -> apply path works end to end

For Milestone 4 checklist, prefer these capability checkboxes unless roadmap wording changes:
- engine state survives repeated sessions
- workflow artifacts are durable/readable enough for real writing sessions
- save-to-project workflow output paths are stable
- minimal audit/proposal logging exists for traceability
- command palette/client actions have corresponding engine contracts
- future Textual client is unblocked by engine contract gaps
- dogfooding can proceed without hand-editing state or relying on mock-only behavior

If the user asks what changed over time:
- compare feature closure, not just branch commits.
- say which checkbox moved from open to partial/closed.
- mention lane commits only as supporting evidence.

Important honesty rules:
- say `closed`, `partially standing`, `scaffolded`, `contract-defined`, `engine-real`, `mockup-real`, or `open` deliberately.
- do not infer feature closure from active worker sessions, branch movement, or packet volume.
- queue state explains why closure is blocked; it is not itself milestone progress.
- prefer exact milestone names from `ROADMAP.md` over invented labels.
