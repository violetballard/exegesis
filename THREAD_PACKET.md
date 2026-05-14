## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Fix the A2UI contract handoff metadata so the integration target is traceable.
- Selected integration target: current branch tip after this fixer commit.
- Target type: metadata-only handoff correction. No runtime, shell, planner, or packet-planner source/test changes are part of this reviewed target.
- Canonical demo-path step advanced: `preview and apply or reject a patch`, by keeping the A2UI contract lane aligned to deterministic shared card/action contracts for CLI fallback.

## Required Fix Status

1. `.codex/kickoff_packets/feat-a2ui-contract.md` and `.codex/packet_planner/state.json` are still residual merge-target deltas. Both `git restore --source=main -- ...` and direct writes are blocked in this sandbox by `Operation not permitted`.
2. Stale Milestone 5 / capability 5 claims are not retained in this handoff packet. The current mapping is Milestone 3 / capability 4.
3. This packet resubmits one integration target: the current branch tip after this fixer commit.
4. Packet-planner source/test coverage claims are removed; no `tests/unit/test_packet_planner.py` change is included in this target.

## Files Changed For This Target

- `THREAD_PACKET.md`

Residual protected lane-state paths still present in `git diff --name-status main...HEAD` because filesystem and git-index permissions block restoration:

- `.codex/kickoff_packets/feat-a2ui-contract.md`
- `.codex/packet_planner/state.json`

## Explicitly Not Included In This Handoff

- `codex_packet_handoff/tools/planner.py`
- `src/qual/ui/__init__.py`
- `src/qual/ui/a2ui.py`
- `src/qual/ui/shell.py`
- `src/qual/ui/test_a2ui_fallback_safety.py`
- `tests/unit.sh`
- `tests/unit/test_a2ui_contract.py`
- `tests/unit/test_packet_planner.py`
- `tests/unit/test_ui_shell.py`

## Plan Alignment

- Roadmap item affected: `ROADMAP.md` Milestone 3, `feat-a2ui-contract`: shared card/action contracts and selection models.
- Product vision capability affected: `PRODUCT_VISION.md` capability 4, Shared UI contract (`A2UI`): cards/actions/selection types live in a client-agnostic shared layer, while rendering adapters stay outside shared.
- Canonical demo-path step: `preview and apply or reject a patch`.
- Routing/provider impact note: none.
- Shared/integrator-locked impact: none intended in this metadata-only fixer target.

## Tasks Completed

1. Re-read the rejection packet and used it as the source of truth.
2. Attempted to restore residual `.codex` lane-state files to `main` content.
3. Rewrote this handoff packet to match the actual branch diff and current Milestone 3 / capability 4 canon.
4. Re-ran required gates after the packet correction.

## Commands Run And Outcomes

- `git status --short --branch`: PASS; branch `codex/feat-a2ui-contract`.
- `git diff --name-status main...HEAD`: PARTIAL; `THREAD_PACKET.md` plus residual protected `.codex` metadata paths remain.
- `git restore --source=main -- .codex/kickoff_packets/feat-a2ui-contract.md .codex/packet_planner/state.json`: FAIL; `Operation not permitted` creating worktree index lock.
- Direct write to `.codex/kickoff_packets/feat-a2ui-contract.md`: FAIL; `Operation not permitted`.
- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS.

## Risks / Blockers

- Runtime behavior risk: low. This target only corrects handoff metadata and does not change executable A2UI code.
- Blocker: residual `.codex` merge-target deltas remain because both git restoration and direct file writes are blocked by filesystem permissions in this sandbox.
