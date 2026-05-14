## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main`
- Handoff type: corrected A2UI runtime fixer re-review packet.
- Corrected review scope: reviewed A2UI runtime slice from `b929fe6c7a1159c7882acedd247aca31a93cd123` and this corrected handoff packet.
- Explicit canonical demo-path step advanced: `preview and apply or reject a patch`.

## Scope Correction

The previous branch tip incorrectly claimed planner/tooling and packet-planner regression coverage that are not present in the reviewed runtime implementation evidence.

This corrected packet limits the merge candidate to the reviewed runtime commit `b929fe6c7a1159c7882acedd247aca31a93cd123`, which changes only `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`, plus this handoff packet correction.

No planner or packet-planner test maintenance is claimed in this packet. `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` are not part of this corrected merge candidate.

## Canonical Demo-Path Mapping

This A2UI runtime slice advances `preview and apply or reject a patch`.

The runtime change keeps apply/reject/copy action materialization stable for CLI fallback consumers. Deterministic action ordering makes patch-preview action payloads predictable while preserving typed and allowlisted action filtering.

## Tasks Completed

1. Canonicalized materialized A2UI action ordering so filtered action payloads stay stable for engine-facing CLI fallback consumers.
2. Preserved typed and allowlisted action filtering, including exclusion of unsupported action shapes from the A2UI contract surface.
3. Preserved CLI rendering fallback behavior and covered deterministic filtered action ordering in `tests/unit/test_a2ui_contract.py`.
4. Corrected this handoff packet so it describes only the reviewed `feat-a2ui-contract` runtime slice and removes unsupported planner/test claims.

## Files Changed

Runtime review files:

- `src/qual/ui/a2ui.py`
- `tests/unit/test_a2ui_contract.py`

Corrective handoff file:

- `THREAD_PACKET.md`

## Shared/Integrator-Locked Impact

Shared edits: none claimed for this corrected runtime handoff.

Planner/tooling edits: none claimed. If planner/tooling work is needed later, it should be submitted separately as explicitly approved out-of-lane/high-risk scope with accurate changed files, tests, and ownership exception.

## Routing/Provider Impact

None. The intended A2UI runtime change does not touch model routing, provider configuration, or provider selection behavior.

## Commands Run And Outcomes

Required gates for this corrected fixer handoff:

- `make scope-check` - passed for branch `codex/feat-a2ui-contract`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 156 unit tests.
- `./typecheck-test.sh` - passed Python source compilation.
- `make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and 156 unit tests.

## Risks Or Blockers

- Runtime A2UI claims are limited to deterministic materialized action ordering for `preview and apply or reject a patch`.
- This packet does not claim planner changes or `tests/unit/test_packet_planner.py` coverage.
