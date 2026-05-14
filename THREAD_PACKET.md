## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main`
- Handoff type: split re-review packet: A2UI runtime slice plus corrective handoff metadata refresh.
- Canonical demo-path step advanced before handoff: `produce a plan or revision` and `preview and apply or reject a patch` are strengthened by deterministic, typed A2UI action ordering for engine-facing command surfaces.
- Lane-owned paths: `src/qual/ui/**`, `tests/unit/test_a2ui_contract.py`.
- Shared/integrator-locked edits: NO. The reviewed runtime commit touched only lane-owned `src/qual/ui/a2ui.py` plus the approved lane test exception `tests/unit/test_a2ui_contract.py`; branch-tip `.codex` deltas are control metadata accounted for below, not source/runtime edits.
- Budget framing: normal lane runtime scope with three meaningful completed tasks. The corrective metadata-only refresh is split out in its own review range and is not counted as an additional runtime task.

## Authoritative Review Ranges

Source-bearing implementation range:

- `b929fe6c7a1159c7882acedd247aca31a93cd123` (`fix(a2ui): canonicalize materialized action order`)

Corrective packet-refresh range for this re-review:

- `ad06526fd4ba8fdb982f3886b03b1d2a49093f14..HEAD`

This packet is authoritative for the branch-tip merge candidate. The implementation range contains the runtime A2UI source and unit-test change. The corrective packet-refresh range changes only `THREAD_PACKET.md`. Earlier branch history includes other lane/control-plane commits and is not part of this A2UI implementation review. This handoff does not claim planner source behavior changes or packet-planner regression coverage.

## Scope Completed

1. Canonicalized materialized A2UI action ordering so filtered action payloads are stable for engine-facing consumers.
2. Preserved typed and allowlisted action filtering, including exclusion of unsupported action shapes from the A2UI contract surface.
3. Preserved CLI rendering fallback behavior and covered deterministic filtered action ordering in `tests/unit/test_a2ui_contract.py`.

No planner behavior changes are included in the reviewed implementation range. No packet-planner regression coverage is claimed by this handoff.

Corrective metadata refresh, split for re-review:

1. Corrected handoff metadata so the reviewed branch, implementation commit, control-metadata range, files changed, commands, risks, budget framing, and canonical demo-path step are traceable for `feat-a2ui-contract`.

## Tasks Completed

1. Implemented deterministic canonical ordering for materialized filtered A2UI actions in `src/qual/ui/a2ui.py`.
2. Verified the A2UI contract with focused unit coverage in `tests/unit/test_a2ui_contract.py`.
3. Refreshed handoff/control metadata for re-review without expanding runtime scope.

## Files Changed

Implementation range `b929fe6c7a1159c7882acedd247aca31a93cd123`:

- `src/qual/ui/a2ui.py` - canonicalizes materialized filtered action order while preserving typed/allowlisted filtering and CLI fallback compatibility.
- `tests/unit/test_a2ui_contract.py` - covers canonical filtered action ordering and existing A2UI contract behavior.

Current branch metadata delta includes:

- `.codex/kickoff_packets/feat-a2ui-contract.md` - lane kickoff/control metadata, not runtime source.
- `.codex/packet_planner/state.json` - packet-planner control metadata, not runtime source.
- `THREAD_PACKET.md` - authoritative handoff packet and traceability record for re-review.

The `.codex` files above are explicitly accounted for as control metadata in the merge candidate. They do not represent planner source changes.

Corrective packet-refresh range `ad06526fd4ba8fdb982f3886b03b1d2a49093f14..HEAD`:

- `THREAD_PACKET.md` - narrows the handoff text to the reviewed A2UI implementation commit, removes planner-behavior claims, and explicitly accounts for branch-tip `.codex` metadata.

## Commands Run And Outcomes

Required final gates for this fixer pass:

- `make scope-check` - passed for branch `codex/feat-a2ui-contract`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 511 unit tests, including `tests/unit/test_a2ui_contract.py`.
- `./typecheck-test.sh` - passed Python source compilation.
- `make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and 511 unit tests.

Prior A2UI-focused evidence from the reviewed runtime target:

- Runtime change reviewed as `b929fe6c7a1159c7882acedd247aca31a93cd123`.
- Reviewer confirmed the runtime delta is narrow and plan-aligned, changing only `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`.

## Risks Or Blockers

- No provider routing, model routing, storage, retrieval, or core engine entrypoints are touched by the A2UI runtime commit.
- Shared/integrator-locked edits are not present in the reviewed runtime change, so the handoff is submitted under the normal lane budget with three completed tasks rather than the high-risk budget.
- Branch-tip metadata includes `.codex/kickoff_packets/feat-a2ui-contract.md` and `.codex/packet_planner/state.json`; they are accounted for above as control metadata, not source-bearing planner changes, and are split from the A2UI runtime task count.

## Roadmap And Vision Mapping

- Roadmap items affected: `ROADMAP.md` Milestone 3 real workflow loop dependency on stable A2UI contract/CLI fallback surfaces for engine-side plan/revise and apply/reject interactions.
- Vision capability affected: `PRODUCT_VISION.md` shared UI contract boundaries for engine-authoritative actions with CLI fallback, without expanding into Textual implementation or UI polish.
- Canonical demo-path step made more real: the engine loop can expose deterministic A2UI actions for plan/revise and patch apply/reject decisions while keeping the CLI fallback path stable.

## Routing And Provider Impact

None. This handoff does not touch provider configuration, model routing, retrieval routing, or core app entrypoints.
