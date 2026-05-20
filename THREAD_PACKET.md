## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Source commit(s): `f5db596e..HEAD`
- Scope goal: Correct the A2UI handoff packet so the review surface reflects this lane, the actual corrective commit range, and the current engine-first MVP boundary.
- Scope completed: Replaced the stale `feat-engine-runs` handoff metadata with an A2UI-specific metadata-only correction for `THREAD_PACKET.md`. The reviewed correction changes only this handoff packet and does not claim implementation-file changes.
- Roadmap item(s) affected (from `ROADMAP.md`): `Milestone 3: Real workflow loop`, specifically moving A2UI contracts into `shared` while keeping renderers outside `shared`, and the `feat-a2ui-contract` lane ownership of shared card/action contracts and selection models.
- Vision capability affected (from `PRODUCT_VISION.md`): `Shared UI contract (A2UI)`, specifically client-agnostic cards/actions/selection types in shared, rendering adapters outside shared, typed actions, validation, and unknown-card fallback.
- Canonical demo-path step advanced: supports the engine-side path from retrieved/contextual material to producing a plan or revision and previewing/applying/rejecting a patch by keeping the shared A2UI card/action/selection contract reviewable without activating Textual or UI-polish work.
- Shared/integrator-locked edits: `YES`
- Approval note: This fixer run was explicitly launched by the control-plane review packet to correct `THREAD_PACKET.md`; the edit is limited to the required metadata correction and does not change runtime, provider, routing, CLI, or lane implementation files.
- Ownership note: `THREAD_PACKET.md` is a control-plane handoff artifact. This commit corrects that artifact only because the required fixes explicitly target the incorrect packet contents.

## Reviewed source-range evidence

The reviewed correction range is `f5db596e..HEAD`.

- `git diff --name-only f5db596e..HEAD` lists exactly:
  - `THREAD_PACKET.md`
- No `.codex/kickoff_packets/**`, `src/qual/engine/**`, `src/qual/ui/**`, `shared/src/exegesis_shared/**`, or test files are claimed as changed by this metadata-only correction.

## Tasks completed

1. Corrected the branch name to `codex/feat-a2ui-contract`.
2. Corrected the source range to the A2UI packet correction range: `f5db596e..HEAD`.
3. Removed all `feat-engine-runs` source-range, roadmap, file, and task claims from this review surface.
4. Made the `Files changed` section match the reviewed correction range exactly.
5. Added the explicit approval and ownership note for the required `THREAD_PACKET.md` control-plane metadata correction.
6. Remapped the handoff to `ROADMAP.md` Milestone 3 `feat-a2ui-contract` scope and `PRODUCT_VISION.md` shared A2UI contract capability.
7. Stated the canonical demo-path step advanced under the current AGENTS.md engine-first demo path.

## Files changed

- `THREAD_PACKET.md`

## Commands run with results

- `make scope-check` -> failed: scope policy rejects `THREAD_PACKET.md` on `codex/feat-a2ui-contract`
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed; emitted the existing missing-file notice for `src/qual/ui/test_a2ui_fallback_safety.py` before completing successfully
- `./quality-test.sh` -> passed; 614 tests ran successfully
- `./typecheck-test.sh` -> passed
- `make ci` -> failed: CI stops at the same `THREAD_PACKET.md` scope-check rejection

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- The only changed file in the corrected review surface is `THREAD_PACKET.md`.
- `THREAD_PACKET.md` is a control-plane artifact and is expected to fail lane scope-check unless the control-plane/integrator path accepts this metadata-only correction.

## Routing/provider impact note

None. No model routing, provider configuration, runtime engine behavior, typed action handling, or CLI fallback behavior was changed.

## Risks / blockers

- Residual risk: `THREAD_PACKET.md` is a control-plane artifact, but the reviewer packet explicitly required this correction in the lane worktree.
