## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Cherry-pick-only re-review for the deterministic A2UI materialized action-order fix.

## Traceability

- Authoritative review target: cherry-pick commit `b929fe6c7a1159c7882acedd247aca31a93cd123` (`fix(a2ui): stabilize materialized action order`).
- Review range: `b929fe6c7a1159c7882acedd247aca31a93cd123^..b929fe6c7a1159c7882acedd247aca31a93cd123`.
- Merge instruction: integrator must cherry-pick `b929fe6c7a1159c7882acedd247aca31a93cd123` and must not merge branch `codex/feat-a2ui-contract` or its current tip. Later branch commits contain additional source/test changes that are outside this packet.
- Merge-base baseline for branch context only: `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27`.
- This is a fixer packet for the reviewer-required integration-block response, not a new feature expansion.
- The previous packet was rejected because it mixed a cherry-pick intent with a branch-tip submission. This packet names one integration target only.

## Scope Completed

- Canonicalized materialized A2UI action order in `src/qual/ui/a2ui.py` so equivalent supported action payloads render deterministically in CLI fallback output.
- Updated unit coverage in `tests/unit/test_a2ui_contract.py` to assert the full canonicalized action list instead of only action ids.
- Preserved CLI fallback behavior as the active renderer path while keeping action handling typed, allowlisted, and engine-authored.
- Did not add Textual, Exegesis Console, Studio renderer, provider routing, or core engine entrypoint work.

## Files Changed

- `src/qual/ui/a2ui.py`
- `tests/unit/test_a2ui_contract.py`

## Plan Alignment

- Roadmap item(s) affected: `ROADMAP.md` Milestone 3: Real workflow loop.
- MVP task anchor: `AGENTS.md` active MVP item `A2UI contracts with CLI fallback`.
- Vision capability affected: `PRODUCT_VISION.md` Capability 4: Shared UI contract / operator-first control surface.
- Canonical demo-path step advanced: deterministic A2UI action ordering removes a concrete CLI fallback snapshot and contract-consumer mismatch.
- Explicitly deferred: Textual implementation, Exegesis Console renderer work, Studio renderer work, provider routing changes, and core engine policy changes.

## Tasks Completed

1. Updated `src/qual/ui/a2ui.py` to sort filtered materialized actions by canonical JSON identity before returning card actions.
2. Updated `tests/unit/test_a2ui_contract.py` to cover canonical action ordering for supported filtered actions.
3. Reproduced the required lane gates locally in this worktree.
4. Regenerated this handoff packet so `Traceability`, `Scope Completed`, `Files Changed`, `Tasks Completed`, and `Commands Run` describe only the cherry-pick review target.

## Required Handoff Fields

- Roadmap item(s) affected: `ROADMAP.md` Milestone 3: Real workflow loop; current MVP `A2UI contracts with CLI fallback` canonical path.
- Vision capability affected: `PRODUCT_VISION.md` Capability 4: Shared UI contract / operator-first control surface.
- Canonical demo-path step advanced: deterministic A2UI action ordering for CLI fallback.
- Routing/provider impact note: None.
- Size-budget status: Within fixer scope. The selected review range changes 2 source/test files with 5 insertions and 3 deletions.
- Scope / approval note: This packet requests re-review of the cherry-pick target only. The current branch tip is not a merge target for this packet.
- Selected integration target: cherry-pick `b929fe6c7a1159c7882acedd247aca31a93cd123`; do not merge `codex/feat-a2ui-contract`.

## Commands Run And Outcomes

- Fixer verification pass completed on 2026-05-14 for the cherry-pick-only review target.
- `make scope-check`: PASS on 2026-05-14 (`[devex] scope-check: passed for branch 'codex/feat-a2ui-contract'`).
- `./quality-format.sh --check`: PASS on 2026-05-14 (`[format] check passed`).
- `./quality-lint.sh`: PASS on 2026-05-14 (`[lint] passed`).
- `./quality-test.sh`: PASS on 2026-05-14 (smoke passed; all 11 unit modules passed).
- `./typecheck-test.sh`: PASS on 2026-05-14 (`[typecheck] compiling Python sources in src/`).
- `make ci`: PASS on 2026-05-14 (scope, format, lint, typecheck, and tests passed; `[devex] CI entrypoint completed`).

## Risks / Blockers

- Risk: `LOW` for the selected narrow cherry-pick target.
- Blockers: none for narrow re-review. The larger branch history remains outside this packet and requires a separate split or explicit integrator approval before any full-branch review.
