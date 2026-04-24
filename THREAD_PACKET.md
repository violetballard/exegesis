# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `538095c47a6bc5f971e9811b83745571915e4268`
- Packet refresh role: `reviewer-fix packet refresh`
- Packet refresh basis: `updated on 2026-04-23 to satisfy the reviewer-required fixes by naming the exact canonical demo-path step advanced, narrowing the roadmap and vision claims to the deterministic CLI compatibility surface this slice actually affects, and keeping broader auditability or end-to-end workflow claims out of scope`
- Metadata-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: harden the declared parser-facing CLI command catalog so it stays in lockstep with the canonical command catalog and fails closed when parser-surface drift is introduced, including the reviewer-called `diff` token disappearance case.
- Risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (Completed)

1. Tighten the command contract wording and helper structure so the full declared parser surface remains the explicit validation target.
2. Add a regression that proves the contract fails when the `diff` parser token disappears from the accepted surface.
3. Refresh the handoff packet so it names the exact `open project/document` demo-path step advanced and narrows the roadmap and vision mapping to this deterministic CLI compatibility slice.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- Reviewed implementation commit: `538095c47a6bc5f971e9811b83745571915e4268` (`test(commands): cover diff parser surface drift`).
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation summary:
  - `command_cli_contract()` keeps the full parser-facing CLI entrypoint projection as the explicit validation target through a dedicated declared-entrypoint projection helper instead of relying on the deduplicated canonical-name projection.
  - focused regression tests now include the exact reviewer-called failure mode: the contract raises when the `diff` parser token disappears from the accepted `diff-preview` surface, alongside the broader canonical-name and parser-order drift cases.

## Scope Completed

- Added a fail-closed guard in `command_cli_contract()` so the parser-facing CLI contract cannot silently diverge from the canonical command catalog ordering.
- Added regression coverage proving the CLI contract matches the catalog in the normal case and raises if parser-surface drift is introduced, including explicit rejection when the `diff` parser token disappears.
- Kept the slice narrow: one command-catalog contract guard plus targeted tests, with no provider, routing, or broader workflow behavior changes.

## Canonical Demo-Path Mapping

- Canonical demo-path step advanced: `open project/document`.
- Active MVP operator path strengthened: the CLI fallback path for `open project/document` while Textual remains disabled, by ensuring the command surface fails closed before the first operator step runs if parser/catalog drift is introduced.
- Concrete blocker removed: before this guard, the active CLI surface could lose required parser tokens or aliases such as `diff` while the deduplicated canonical-name tuple still matched `command_names()`. That left the CLI command catalog able to drift silently, which is a concrete reliability blocker before the operator can safely start the `open project/document` demo-path step.
- Direct plan-alignment statement: this change makes the CLI fallback `open project/document` entry step more real by forcing the shared parser-facing command catalog to fail closed whenever it stops matching the canonical command catalog.
- Scope-tightening note: this handoff claims only deterministic CLI compatibility surface hardening for the active CLI fallback path, anchored to the `open project/document` entry step; it does not claim to harden patch preview, apply/reject, persistence, audit trails, or end-to-end command-flow behavior in this slice.
- Why this is milestone-worthy now instead of second-order cleanup: deterministic CLI command ordering is a required smoke-test guard for the active engine-first MVP loop while Textual remains disabled. `AGENTS.md` says contract work counts only when it removes a concrete blocker on the canonical demo path, and this guard does that by preventing silent command-catalog drift on the live CLI fallback path before the operator can begin `open project/document`.

## Approved Exception Note

- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approval basis: shared test coverage is required to prove the contract guard and remains the only non-lane-owned path in the reviewed slice.
- Scope-check allowance used: `SCOPE_ALLOW_SHARED=1`
- Integrator-locked edits in this slice: `none`

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Re-anchored the handoff packet to the exact reviewed implementation commit `538095c47a6bc5f971e9811b83745571915e4268`.
2. Kept the command-contract validation pinned to the full declared parser surface and named that surface explicitly in the implementation.
3. Added the reviewer-requested regression proving the contract fails when the `diff` parser token disappears from the accepted `diff-preview` surface.
4. Finalized the handoff packet so the reviewer-requested `open project/document` demo-path mapping and the narrower roadmap and vision claims are explicit in the approval basis.
5. Revalidated the full required gate set after the packet finalization so this handoff still reflects a green fixer-turn state.

### Files Changed

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD_PACKET.md`
- `THREAD.md`

### Commands Run and Outcomes

- `make scope-check`: `PASSED`
- `./quality-format.sh --check`: `PASSED`
- `./quality-lint.sh`: `PASSED`
- `./quality-test.sh`: `PASSED`
- `./typecheck-test.sh`: `PASSED`
- `make ci`: `PASSED`

### Risks / Blockers

- Risks:
  - future command additions still need regression coverage so the CLI contract keeps failing closed when parser/catalog drift is introduced
- Blockers:
  - none

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 3: preserve CLI compatibility while the package/layout migration lands, within the `feat-commands` lane for CLI compatibility and migration-safe entrypoints.
- This diff contributes only the deterministic CLI compatibility surface for the active `open project/document` fallback path by ensuring the declared parser-facing command catalog cannot drift away from the canonical command catalog without failing closed.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: the CLI remains the active operator surface, so the command catalog for the `open project/document` fallback step needs to stay deterministic and fail closed before that step begins.

### Routing / Provider Impact Note

- None. This diff only hardens local command-catalog validation and regression coverage.

### Scope-Check / Ownership Note

- Shared-by-approval edits: `YES`
- Shared-by-approval implementation path included: `tests/unit/test_commands_catalog.py`
- Integrator-locked edits: `NO`
- Integrator-locked implementation paths included: `none`
