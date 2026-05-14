## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main`
- Handoff type: corrected runtime-only re-review packet.
- Reviewed runtime scope: `b929fe6c7a1159c7882acedd247aca31a93cd123` (`fix(a2ui): canonicalize materialized action order`).
- Runtime files in scope:
  - `src/qual/ui/a2ui.py`
  - `tests/unit/test_a2ui_contract.py`
- Explicit canonical demo-path step advanced: `preview and apply or reject a patch`.

## Scope Correction

This corrected handoff withdraws the earlier control-plane/planner claims from the `feat-a2ui-contract` review.

Runtime review scope is only commit `b929fe6c7a1159c7882acedd247aca31a93cd123` and only these files:

- `src/qual/ui/a2ui.py`
- `tests/unit/test_a2ui_contract.py`

The following files are not part of this A2UI runtime handoff and should not be reviewed as `feat-a2ui-contract` source work:

- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`

No planner source behavior changes and no packet-planner regression coverage are claimed here. If planner/control-plane source changes are still needed, they require a separate high-risk control-plane review packet with lane ownership, approval basis, and a concrete Milestone 3 engine-loop blocker.

## Canonical Demo-Path Mapping

The runtime A2UI change strengthens `preview and apply or reject a patch` by keeping apply/reject/copy action materialization stable for CLI fallback consumers. Deterministic action ordering makes patch-preview action payloads predictable while preserving typed and allowlisted action filtering.

## Tasks Completed

1. Canonicalized materialized A2UI action ordering so filtered action payloads are stable for engine-facing CLI fallback consumers.
2. Preserved typed and allowlisted action filtering, including exclusion of unsupported action shapes from the A2UI contract surface.
3. Preserved CLI rendering fallback behavior and covered deterministic filtered action ordering in `tests/unit/test_a2ui_contract.py`.
4. Corrected this handoff packet to remove planner implementation and packet-planner test claims from the A2UI runtime review scope.

## Files Changed

Runtime review scope:

- `src/qual/ui/a2ui.py`
- `tests/unit/test_a2ui_contract.py`

Packet-only correction after review:

- `THREAD_PACKET.md`

## Commands Run And Outcomes

Required gates for the corrected handoff:

- `make scope-check` - passed for branch `codex/feat-a2ui-contract`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 511 unit tests, including `tests/unit/test_a2ui_contract.py`.
- `./typecheck-test.sh` - passed Python source compilation.
- `make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and 511 unit tests.

## Risks Or Blockers

- Runtime A2UI claims are limited to commit `b929fe6c7a1159c7882acedd247aca31a93cd123`.
- Planner source files and packet-planner tests are explicitly out of scope for this handoff.
- Any future planner/control-plane source work should be split into a separately owned high-risk review packet.
