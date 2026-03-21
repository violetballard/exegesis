## Thread Handoff Packet

- Branch name: `codex/feat-context-storage`
- Commit: `1abd90ef71ae0c37f8da5c71b153e26530fa4972`
- Review path: tooling/integration cleanup

## Scope goal
- Resubmit the actual mixed-scope cleanup commit as tooling/integration work: stop hiding planner-state changes from diff-based file reporting and align the lane metadata exception note with the approved shared-file exception wording.

## Scope completed
- The planner now reports every changed file, including `.codex/packet_planner/state.json`, instead of suppressing that path as noise.
- The lane metadata exception note now matches the approved test-file exception wording.
- The handoff packet is now described as cleanup/tooling work, not as a storage-feature implementation handoff.

## Tasks completed (numbered)
1. Removed the packet-planner noise filter for `.codex/packet_planner/state.json` so the planner's file list reflects the real diff.
2. Reworded the approved shared-file exception note in `.codex/lane_meta/feat-context-storage.json` to match the actual recovery-test exception wording.
3. Reframed the handoff packet so it matches the commit's true tooling/integration scope instead of the stale storage-hardening narrative.

## Files changed
- `.codex/lane_meta/feat-context-storage.json`
- `.codex/packet_planner/state.json`
- `codex_packet_handoff/tools/planner.py`

## Commands run and outcomes
- `make scope-check` -> PASS
- `./quality-format.sh --check` -> PASS
- `./quality-lint.sh` -> PASS
- `./quality-test.sh` -> PASS
- `./typecheck-test.sh` -> PASS
- `make ci` -> PASS

## Risks / blockers
- Risk: `LOW`
- Blockers: none
- This commit belongs in tooling/integration review, not storage feature review.

## Required handoff fields
### Roadmap item(s) affected
- Milestone 0 - Foundation: Ownership and integration runbooks
- Milestone 1 - Bootstrap Flow Stabilization: Integrator promotion from approved feature lanes
### Vision capability affected
- Capability 4 - Operator-first control surface
### Routing/provider impact note
- None
### Proposed README patch text
- None

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Shared-by-approval source edits: `NO`
- Integrator-locked edits: `NO`
