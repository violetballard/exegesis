## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Source commit(s): `a889831415e9931291fe8b2f6d4a37fc7721b7b5..c0738069fe4a3bbe0944a47e33c29895e61c40ab`
- Scope goal: Correct the A2UI handoff packet so the review surface reflects this lane, the actual reviewed commit, and the current engine-first MVP boundary.
- Scope completed: Replaced the stale engine-run handoff metadata with an A2UI-specific metadata-only correction for `THREAD_PACKET.md`. The reviewed commit under this packet changes only the handoff packet and does not claim implementation-file changes.
- Roadmap item(s) affected (from `ROADMAP.md`): `Milestone 3: Engine-first MVP closure`, specifically `feat-a2ui-contract`: shared card/action contracts and selection models, and the milestone scope to move A2UI contracts into `shared` while keeping renderers outside `shared`.
- Vision capability affected (from `PRODUCT_VISION.md`): `Shared UI contract (A2UI)`, specifically client-agnostic cards/actions/selection types with renderers outside the shared layer, typed actions, validation, and unknown-card fallback.
- Canonical demo-path step advanced: supports the engine-side path from retrieved/contextual material to plan or revision and preview/apply/reject by keeping the shared card/action/selection contract reviewable without activating Textual or UI-polish work.
- Shared/integrator-locked edits: `YES`
- Approval note: This fixer run was explicitly launched by the control-plane review packet to correct `THREAD_PACKET.md`; the edit is limited to the required metadata correction and does not change runtime, provider, routing, or lane implementation files.
- Ownership note: `THREAD_PACKET.md` is a control-plane handoff artifact. This commit corrects that artifact only because the required fixes explicitly target the incorrect packet contents.

## Reviewed source-range evidence

The reviewed range is `a889831415e9931291fe8b2f6d4a37fc7721b7b5..c0738069fe4a3bbe0944a47e33c29895e61c40ab`.

- `git show --name-only c0738069fe4a3bbe0944a47e33c29895e61c40ab` lists exactly:
  - `THREAD_PACKET.md`
- No `.codex/kickoff_packets/**`, `src/qual/engine/**`, `src/qual/shared/**`, or test files are claimed as changed by the reviewed commit.

## Tasks completed

1. Corrected the branch name to `codex/feat-a2ui-contract`.
2. Corrected the source range to the actual reviewed A2UI packet commit: `a889831415e9931291fe8b2f6d4a37fc7721b7b5..c0738069fe4a3bbe0944a47e33c29895e61c40ab`.
3. Removed all `feat-engine-runs` source-range, roadmap, file, and task claims from this review surface.
4. Made the `Files changed` section match `git show --name-only c0738069fe4a3bbe0944a47e33c29895e61c40ab` exactly.
5. Added the explicit approval and ownership note for the required `THREAD_PACKET.md` control-plane metadata correction.
6. Remapped the handoff to the A2UI roadmap and product-vision scope.

## Files changed

- `THREAD_PACKET.md`

## Commands run with results

- `make scope-check` -> failed: scope policy rejects `THREAD_PACKET.md` on `codex/feat-a2ui-contract`
- `SCOPE_ALLOW_SHARED=1 make scope-check` -> failed: script still rejects `THREAD_PACKET.md` as a control-plane file before any shared-file allowance applies
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> failed: CI stops at the same `THREAD_PACKET.md` scope-check rejection

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- The only changed file in the corrected review surface is `THREAD_PACKET.md`.
- This metadata correction is included because the reviewer packet explicitly required replacing the incorrect handoff packet contents.

## Routing/provider impact note

None. No model routing, provider configuration, runtime engine behavior, or CLI contract was changed.

## Risks / blockers

- Residual risk: `THREAD_PACKET.md` is a control-plane artifact, but the control-plane review packet explicitly required this correction in the lane worktree.
