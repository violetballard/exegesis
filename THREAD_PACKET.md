## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main`
- Handoff type: A2UI contract/CLI fallback handoff.
- Canonical demo-path step advanced before handoff: `plan or revise` and `apply or reject a patch` are strengthened by deterministic, typed A2UI action ordering for engine-facing command surfaces.
- Lane-owned paths: `src/qual/ui/**`, `tests/unit/test_a2ui_contract.py`.
- Shared or integrator-locked files changed: none.
- Runtime A2UI commit under review: `b929fe6c7a1159c7882acedd247aca31a93cd123` (`fix(a2ui): canonicalize materialized action order`).
- Runtime A2UI files changed: `src/qual/ui/a2ui.py`, `tests/unit/test_a2ui_contract.py`.
- Metadata-only packet refresh commits after the runtime commit: handoff packet updates only, including this commit.

## Scope Completed

1. Canonicalized materialized A2UI action ordering so filtered action payloads are stable for engine-facing consumers.
2. Preserved typed and allowlisted action filtering; unsupported action shapes remain excluded from the A2UI contract surface.
3. Preserved CLI rendering fallback behavior while tightening the shared A2UI contract.
4. Added unit coverage in `tests/unit/test_a2ui_contract.py` for the deterministic filtered action ordering.
5. Corrected this `THREAD_PACKET.md` so the handoff metadata describes `codex/feat-a2ui-contract` and the A2UI runtime target, not an unrelated retrieval-lane packet.

## Traceability

The source-bearing implementation commit for review is:

`b929fe6c7a1159c7882acedd247aca31a93cd123`

That commit modifies only:

- `src/qual/ui/a2ui.py`
- `tests/unit/test_a2ui_contract.py`

Packet-refresh commits after `b929fe6c7a1159c7882acedd247aca31a93cd123` are metadata-only unless their diff shows otherwise. They must not be confused with retrieval-lane work. This packet is the authoritative branch-tip handoff metadata for `codex/feat-a2ui-contract`.

## Files Changed

- `src/qual/ui/a2ui.py` - canonicalizes materialized filtered action order while preserving typed/allowlisted filtering and CLI fallback compatibility.
- `tests/unit/test_a2ui_contract.py` - covers canonical filtered action ordering and existing A2UI contract behavior.
- `THREAD_PACKET.md` - records the A2UI handoff, traceability, roadmap/product mapping, commands, and risks for re-review.

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
- No shared or integrator-locked file edits are required for the runtime A2UI change.
- The previous review blocker was invalid traceability from stale retrieval-lane handoff metadata. This packet corrects the branch, lane, files changed, roadmap/product mapping, commands, and risk accounting for `feat-a2ui-contract`.

## Roadmap And Vision Mapping

- Roadmap items affected: `ROADMAP.md` Milestone 3 Real workflow loop, specifically the stable A2UI contract/CLI fallback surface needed for engine-side plan/revise and apply/reject interactions.
- Vision capability affected: `PRODUCT_VISION.md` shared UI contract boundaries for engine-authoritative actions with CLI fallback, without expanding into Textual implementation or UI polish.
- Canonical demo-path step made more real: the engine loop can expose deterministic A2UI actions for plan/revise and patch apply/reject decisions while keeping the CLI fallback path stable.

## Routing And Provider Impact

None. This handoff does not touch provider configuration, model routing, retrieval routing, or core app entrypoints.
