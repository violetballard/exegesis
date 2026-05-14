## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Corrected cherry-pick-only re-review packet for the deterministic A2UI materialized action-order fix.

## Traceability

- Authoritative review target: only commit `b929fe6c7a1159c7882acedd247aca31a93cd123` (`fix(a2ui): stabilize materialized action order`).
- Review range for reviewer: `b929fe6c7a1159c7882acedd247aca31a93cd123^..b929fe6c7a1159c7882acedd247aca31a93cd123`.
- Selected integration target: cherry-pick `b929fe6c7a1159c7882acedd247aca31a93cd123`.
- Explicit non-targets: do not review or merge the branch tip for this packet, and do not review the full branch range from `b929fe6c7a1159c7882acedd247aca31a93cd123` through branch tip.
- Merge instruction: integrator must cherry-pick `b929fe6c7a1159c7882acedd247aca31a93cd123` and must not merge branch `codex/feat-a2ui-contract` or its tip. Later branch commits contain additional runtime, test, planner, packet, and generated metadata changes that are outside this packet.
- Merge-base baseline for branch context only: `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27`.
- This is a fixer packet for the reviewer-required integration-block response, not a new feature expansion.
- The previous packet was rejected because it mixed a cherry-pick intent with a branch-tip submission. This packet names one integration target only.
- No commit that changes executable source or tests is classified as metadata-only in this packet. At the start of this fixer pass, branch tip commit `cd3fc7a9ef51b297d2920668c1d63ee079a47f5a` was packet-only fixer work and was not a selected integration target. Prior non-target branch commits include runtime, test, planner, packet, and generated metadata work outside this packet.

## Scope Completed

- Canonicalized materialized A2UI action order in `src/qual/ui/a2ui.py` so equivalent supported action payloads render deterministically in CLI fallback output.
- Updated unit coverage in `tests/unit/test_a2ui_contract.py` to assert the full canonicalized action list instead of only action ids.
- Preserved CLI fallback behavior as the active renderer path while keeping action handling typed, allowlisted, and engine-authored.
- Did not add Textual, Exegesis Console, Studio renderer, provider routing, or core engine entrypoint work.

## Files Changed For Selected Review Target

Runtime implementation:
- `src/qual/ui/a2ui.py`

Tests:
- `tests/unit/test_a2ui_contract.py`

Packet/planner maintenance:
- None in selected review target.

Generated packet/router metadata:
- None in selected review target.

## Branch Context Not In Selected Review Target

- Runtime implementation outside this packet: `src/qual/ui/__init__.py`, `src/qual/ui/a2ui.py`, `src/qual/ui/shell.py`.
- Tests outside this packet: `src/qual/ui/test_a2ui_fallback_safety.py`, `tests/unit.sh`, `tests/unit/test_a2ui_contract.py`, `tests/unit/test_packet_planner.py`, `tests/unit/test_ui_shell.py`.
- Packet/planner maintenance outside this packet: `THREAD_PACKET.md`, `codex_packet_handoff/tools/planner.py`.
- Generated packet/router metadata outside this packet: `.codex/kickoff_packets/feat-a2ui-contract.md`, `.codex/lane_meta/feat-a2ui-contract.json`, `.codex/packet_planner/state.json`, `.codex/packets/lanes/feat-a2ui-contract/inbox/feature/F__codex-feat-a2ui-contract__aa875cd03ea2a8e092f527610640827baa7b7b5a__20260320T210541Z.md`.
- Branch-tip classification: at the start of this fixer pass, branch tip `cd3fc7a9ef51b297d2920668c1d63ee079a47f5a` (`fix(a2ui): correct cherry-pick handoff target`) was packet-only fixer work and was not merge-ready; prior non-target branch commits include runtime plus test work and require separate review packets.

## Plan Alignment

- Roadmap item(s) affected: `ROADMAP.md` Milestone 3: Real workflow loop.
- MVP task anchor: `AGENTS.md` active MVP item `A2UI contracts with CLI fallback`.
- Vision capability affected: `PRODUCT_VISION.md` Capability 4: Shared UI contract / operator-first control surface.
- Canonical demo-path step advanced: deterministic A2UI action ordering keeps the CLI fallback demo path stable when equivalent engine-authored action payloads arrive in different input orders, so the operator-facing action list and unit snapshot agree.
- Budget classification for selected target: high-risk-compatible narrow packet with `2` completed tasks, under the `4` task cap even if reviewer treats A2UI contract/runtime paths as shared.
- Explicitly deferred: Textual implementation, Exegesis Console renderer work, Studio renderer work, provider routing changes, and core engine policy changes.

## Tasks Completed

1. Updated `src/qual/ui/a2ui.py` to sort filtered materialized actions by canonical JSON identity before returning card actions.
   - Canonical demo-path step advanced: CLI fallback rendering of engine-authored materialized actions is stable when equivalent supported action payloads arrive in different input orders.
2. Updated `tests/unit/test_a2ui_contract.py` to cover canonical action ordering for supported filtered actions.
   - Canonical demo-path step advanced: the A2UI contract test now proves the CLI fallback action list remains deterministic for engine-authored supported actions.

## Required Handoff Fields

- Roadmap item(s) affected: `ROADMAP.md` Milestone 3: Real workflow loop; current MVP `A2UI contracts with CLI fallback` canonical path.
- Vision capability affected: `PRODUCT_VISION.md` Capability 4: Shared UI contract / operator-first control surface.
- Canonical demo-path step advanced: deterministic A2UI action ordering for the CLI fallback demo path, preserving stable action rendering for equivalent engine-authored payloads.
- Routing/provider impact note: None.
- Size-budget status: Within fixer scope. The selected review range changes 2 source/test files with 5 insertions and 3 deletions.
- Scope / approval note: This packet requests re-review of the cherry-pick target only. The branch tip and the full range after `b929fe6c7a1159c7882acedd247aca31a93cd123` are not merge targets for this packet because they include additional runtime, test, planner, packet, and generated metadata work outside the narrow deterministic action-order fix.
- Selected integration target: cherry-pick `b929fe6c7a1159c7882acedd247aca31a93cd123`; do not merge `codex/feat-a2ui-contract`.
- Shared/integrator-locked impact: None for the selected review target; `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py` are lane-owned A2UI contract/runtime test paths for this packet.

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
