## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main`
- Handoff type: corrected re-review packet for branch-tip metadata/control-plane refresh.
- Branch-tip review range: `main..HEAD`
- Explicit canonical demo-path step advanced by the underlying runtime A2UI work: `produce a plan or revision` and `preview and apply or reject a patch`.

## Review Range Traceability

Current branch diff against `main` is metadata/control-plane only:

- `.codex/kickoff_packets/feat-a2ui-contract.md`
- `.codex/packet_planner/state.json`
- `THREAD_PACKET.md`

This branch-tip review range does not include source changes to `src/qual/ui/a2ui.py`, `tests/unit/test_a2ui_contract.py`, `codex_packet_handoff/tools/planner.py`, or `tests/unit/test_packet_planner.py`.

The earlier runtime-only A2UI implementation evidence remains:

- Runtime commit: `b929fe6c7a1159c7882acedd247aca31a93cd123` (`fix(a2ui): canonicalize materialized action order`)
- Runtime files changed in that commit only:
  - `src/qual/ui/a2ui.py`
  - `tests/unit/test_a2ui_contract.py`

No planner source behavior changes and no packet-planner regression coverage are claimed in this handoff; `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` are removed from this feature handoff scope.

## Tasks Completed In Current Review Range

1. Corrected the `feat-a2ui-contract` handoff packet so branch-tip files changed, task count, review range, and gate evidence match the actual `main..HEAD` metadata/control-plane diff.
2. Kept the runtime A2UI implementation evidence separate from the metadata refresh by naming its exact standalone commit and files.
3. Removed planner implementation and packet-planner test claims from the handoff.

## Files Changed In Current Review Range

- `.codex/kickoff_packets/feat-a2ui-contract.md` - lane kickoff/control metadata.
- `.codex/packet_planner/state.json` - packet-planner control metadata.
- `THREAD_PACKET.md` - corrected authoritative handoff packet for re-review.

## Runtime-Only Review Option

If the integrator reviews only the runtime A2UI change, use exactly this review target:

- Commit: `b929fe6c7a1159c7882acedd247aca31a93cd123`
- Files changed:
  - `src/qual/ui/a2ui.py`
  - `tests/unit/test_a2ui_contract.py`
- Tasks completed:
  1. Canonicalized materialized A2UI action ordering so filtered action payloads are stable for engine-facing consumers.
  2. Preserved typed and allowlisted action filtering, including exclusion of unsupported action shapes from the A2UI contract surface.
  3. Preserved CLI rendering fallback behavior and covered deterministic filtered action ordering in `tests/unit/test_a2ui_contract.py`.

## High-Risk And Shared Scope Note

The current `main..HEAD` review range includes `.codex` control metadata. It does not include planner source files, runtime implementation files, provider routing, model routing, retrieval routing, storage, core engine entrypoints, or Textual/UI implementation.

Because no planner/control-plane source changes are part of this handoff, no high-risk planner-source approval is claimed. The earlier `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` claims are explicitly withdrawn, so this handoff keeps review scoped to the runtime A2UI delta at `b929fe6c7a1159c7882acedd247aca31a93cd123` plus the branch-tip metadata packet listed above. If the integrator treats `.codex/packet_planner/state.json` as shared control-plane metadata requiring high-risk framing, this corrected packet caps the current review range at three tasks and requests review of only the exact metadata files listed above.

## Commands Run And Outcomes

Required final gates for this fixer pass:

- `make scope-check` - passed for branch `codex/feat-a2ui-contract`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 511 unit tests, including `tests/unit/test_a2ui_contract.py`.
- `./typecheck-test.sh` - passed Python source compilation.
- `make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and 511 unit tests.

## Risks Or Blockers

- The current branch-tip review range is metadata/control-plane only and should not be reviewed as a runtime A2UI implementation diff.
- Runtime A2UI claims are limited to commit `b929fe6c7a1159c7882acedd247aca31a93cd123`.
- Planner source files and packet-planner tests are explicitly out of scope for this handoff.
