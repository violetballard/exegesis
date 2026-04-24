# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `86e7450a89c33ed158097c4fde9d5fc9edb023ab`
- Packet refresh role: `reviewer-fix packet refresh`
- Packet refresh basis: `regenerated on 2026-04-24 for re-review against the actual implementation tip 86e7450a89c33ed158097c4fde9d5fc9edb023ab, with the scope wording narrowed to one primary canonical demo-path step, deterministic CLI compatibility for that fallback surface, and an explicit blocker-removal sentence`
- Metadata-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: make the canonical `open project/document` CLI fallback step more real as the primary step advanced by this slice, by locking the declared parser-facing command ordering to the canonical command catalog and failing fast when parser/catalog drift is introduced, including the reviewer-called `diff` token disappearance case.
- Risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (Completed)

1. Tighten the command contract wording and helper structure so the full declared parser surface remains the explicit validation target.
2. Add a regression that proves the contract fails when the `diff` parser token disappears from the accepted surface.
3. Regenerate the handoff packet with a direct `open project/document` demo-path mapping sentence and wording limited to deterministic command ordering plus fail-fast parser/catalog drift detection for this compatibility slice.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- Reviewed implementation commit: `86e7450a89c33ed158097c4fde9d5fc9edb023ab` (`feat(commands): normalize persist-and-continue`).
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation summary:
  - `command_cli_contract()` keeps the full parser-facing CLI entrypoint projection as the explicit validation target through a dedicated declared-entrypoint projection helper instead of relying on the deduplicated canonical-name projection.
  - focused regression tests include the exact reviewer-called failure mode: the contract raises when the `diff` parser token disappears from the accepted `diff-preview` surface, alongside broader parser-surface ordering and alias-drift cases.
  - terminal compatibility shims normalize the `persist-and-continue` surface back onto the existing `persist` flow so the active fallback loop keeps one deterministic routing target instead of a silent alias split.

## Scope Completed

- Hardened the `open project/document` CLI fallback entry step by adding a fail-fast guard in `command_cli_contract()` so the parser-facing command surface cannot silently diverge from the canonical command catalog ordering before the operator can start the demo path.
- Added regression coverage proving that `open project/document` entry surface stays trustworthy in the normal case and raises on parser/catalog drift, including explicit rejection when the `diff` parser token disappears from the accepted parser-facing surface.
- Secondary compatibility benefit only: normalizing the `persist-and-continue` compatibility verb onto the existing terminal `persist` flow keeps the reviewed command catalog deterministic, but this handoff does not claim the `persist` step as the demo-path advancement for this slice.
- Kept the slice narrow: concrete blocker removal for the `open project/document` fallback entry step through command-surface compatibility hardening plus targeted tests, with no provider, routing, or broader workflow behavior changes.

## Canonical Demo-Path Mapping

- Primary canonical demo-path step advanced now: `open project/document`.
- Primary-step scope note: this packet advances `open project/document` only; any downstream persistence compatibility value is secondary context rather than a second canonical demo-path-step claim.
- One-line plan alignment: this change makes `open project/document` more real by keeping the CLI fallback command contract deterministic and failing fast before that first operator step can run on a drifted parser/catalog surface.
- `command_cli_contract()` dependency sentence: deterministic `command_cli_contract()` behavior is necessary for `open project/document` because, while Textual remains disabled and the CLI must still execute the MVP loop, the operator cannot trust the very first demo-path command unless parser/catalog drift is rejected before command resolution.
- Active MVP operator path strengthened: the CLI fallback path for `open project/document` while Textual remains disabled, by ensuring the command surface fails closed before the first operator step runs if parser/catalog drift is introduced.
- Concrete blocker removed: before this guard, the active CLI surface could lose required parser tokens or aliases such as `diff` while the deduplicated canonical-name tuple still matched `command_names()`. That left the CLI command catalog able to drift silently, which is a concrete reliability blocker before the operator can safely start the `open project/document` demo-path step.
- Direct plan-alignment statement: this change makes the `open project/document` CLI fallback entry step more real by keeping command ordering deterministic and failing fast whenever the parser-facing catalog drifts from the canonical command catalog.
- Scope-tightening note: this handoff claims only deterministic command ordering plus fail-fast parser/catalog drift detection for the primary `open project/document` CLI fallback step; any value for retrieval, patch review, persistence, or other later demo-path steps is secondary and not part of the primary scope claim for this slice.
- Traceability note: `86e7450a89c33ed158097c4fde9d5fc9edb023ab` is the actual implementation tip for this reviewed slice. Later branch commits are packet-only refreshes in `THREAD.md` and `THREAD_PACKET.md`.
- Why this is milestone-worthy now instead of second-order cleanup: deterministic CLI command ordering is a required smoke-test guard for the active engine-first MVP loop while Textual remains disabled. `AGENTS.md` says contract work counts only when it removes a concrete blocker on the canonical demo path, and this guard does that by preventing silent command-catalog drift on the live CLI fallback path before the operator can begin `open project/document`.

## Approved Exception Note

- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approval reference: this reviewer-fix packet refresh in `THREAD_PACKET.md` and `THREAD.md`, tied to reviewed implementation commit `86e7450a89c33ed158097c4fde9d5fc9edb023ab`, is the traceable in-tree approval record for the single shared-path test edit in this slice.
- Approval basis: shared test coverage is required to prove the contract guard and remains the only non-lane-owned path in the reviewed slice.
- Scope-check allowance used: `SCOPE_ALLOW_SHARED=1`
- Integrator-locked edits in this slice: `none`

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Re-anchored the handoff packet to the actual reviewed implementation tip `86e7450a89c33ed158097c4fde9d5fc9edb023ab`.
2. Kept the command-contract validation pinned to the full declared parser surface and named that surface explicitly in the implementation.
3. Added the reviewer-requested regression proving the contract fails when the `diff` parser token disappears from the accepted `diff-preview` surface.
4. Preserved deterministic compatibility for `persist-and-continue` as secondary support for the same reviewed command catalog, without changing the packet's primary demo-path claim away from `open project/document`.
5. Finalized the handoff packet so the reviewer-requested `open project/document` demo-path mapping, actual implementation tip, and narrowed compatibility-surface wording are explicit in the approval basis.
6. Revalidated the full required gate set after the packet finalization so this handoff still reflects a green fixer-turn state.

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

### Canonical demo-path step advanced

- `open project/document`
- This change makes `open project/document` more real by keeping the CLI fallback command contract deterministic and failing fast if the parser-facing surface drifts from the canonical command catalog before the first operator step runs.

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
- Shared-file approval trace: see the `Approved Exception Note` above in this packet and the mirrored ownership note in `THREAD.md`; both bind the approval record to reviewed implementation commit `86e7450a89c33ed158097c4fde9d5fc9edb023ab`.
- Integrator-locked edits: `NO`
- Integrator-locked implementation paths included: `none`
