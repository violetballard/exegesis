## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main`
- Handoff type: retargeted single-commit runtime review packet.
- Review target: exact commit `b929fe6c7a1159c7882acedd247aca31a93cd123` (`fix(a2ui): canonicalize materialized action order`).
- Review range: `b929fe6c7a1159c7882acedd247aca31a93cd123^..b929fe6c7a1159c7882acedd247aca31a93cd123`.
- Branch-tip note: later commits after `b929fe6c7a1159c7882acedd247aca31a93cd123`, including packet correction commits, are handoff metadata only and must not be reviewed as part of the A2UI runtime delta.
- Packet correction scope: documentation-only handoff metadata for re-review.
- Runtime files in scope:
  - `src/qual/ui/a2ui.py`
  - `tests/unit/test_a2ui_contract.py`
- Explicit canonical demo-path step advanced: `preview and apply or reject a patch`.

## Scope Correction

This corrected handoff withdraws the earlier branch-wide submission and retargets review to the exact narrow runtime commit. The branch-wide range after `b929fe6c7a1159c7882acedd247aca31a93cd123` is explicitly not the requested review scope.

Runtime review scope is only range `b929fe6c7a1159c7882acedd247aca31a93cd123^..b929fe6c7a1159c7882acedd247aca31a93cd123` and only these files:

- `src/qual/ui/a2ui.py`
- `tests/unit/test_a2ui_contract.py`

No Textual implementation work, engine work, packet tooling, `.agents`, `.codex`, docs, or shared-contract changes are submitted by this packet. Those branch-wide changes are withdrawn from the `feat-a2ui-contract` runtime review scope and require a separate high-risk packet with lane ownership, approval basis, all changed files, tasks, roadmap/vision mapping, and risks before review.

Required-fix disposition:

- Required fix 1: the submitted review scope is the single runtime commit `b929fe6c7a1159c7882acedd247aca31a93cd123`; the only review-target files are `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`.
- Required fix 2: unsupported planner and packet-planner claims are removed. `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` are not submitted for this runtime review.
- Required fix 3: not applicable to this runtime-only packet because shared/integrator-locked impact is `None`; no high-risk/shared exception is claimed.
- Required fix 4: the canonical demo-path step advanced is explicitly stated below as `preview and apply or reject a patch`.
- Required fix 5: required handoff fields are aligned below with branch, scope completed, files changed, commands run, risks/blockers, roadmap item, vision capability, and routing/provider impact.

## Canonical Demo-Path Mapping

The runtime A2UI change strengthens `preview and apply or reject a patch` by keeping apply/reject/copy action materialization stable for CLI fallback consumers. Deterministic action ordering makes patch-preview action payloads predictable while preserving typed and allowlisted action filtering.

Roadmap/product mapping:

- `ROADMAP.md`: Milestone 3 real workflow loop, narrowed to CLI fallback determinism for already-materialized A2UI actions while preserving CLI compatibility.
- `PRODUCT_VISION.md`: Canonical engine contract and shared UI contract (`A2UI`), narrowed to deterministic action identity in client-agnostic runtime payloads. This packet does not claim new shared card/action/selection types or planner canonicalization, and renderers remain outside shared.
- `ARCHITECTURE.md`: A2UI card/action contracts with typed action handling and CLI fallback preserved.

## Tasks Completed

1. Canonicalized materialized A2UI action ordering so filtered action payloads are stable for engine-facing CLI fallback consumers.
2. Preserved typed and allowlisted action filtering, including exclusion of unsupported action shapes from the A2UI contract surface.
3. Preserved CLI rendering fallback behavior and covered deterministic filtered action ordering in `tests/unit/test_a2ui_contract.py`.
4. Removed unsubmitted planner/handoff-tooling claims from the packet scope; `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`, and broad `THREAD_PACKET.md` maintenance are not runtime review-target files.

Each runtime task above advances the canonical demo-path step `preview and apply or reject a patch` by making apply/reject/copy action payloads deterministic for CLI fallback rendering. The packet-maintenance task advances re-review readiness only and is not submitted as runtime product work.

## Scope Completed

Runtime-only A2UI contract review for deterministic materialized action ordering in commit `b929fe6c7a1159c7882acedd247aca31a93cd123`. Shared, planner, packet-tooling, Textual, engine, routing, provider, and broader branch-tip changes are outside this handoff.

## Files Changed

Review-target files changed in `b929fe6c7a1159c7882acedd247aca31a93cd123^..b929fe6c7a1159c7882acedd247aca31a93cd123`:

- `src/qual/ui/a2ui.py`
- `tests/unit/test_a2ui_contract.py`

Textual implementation files are not in scope for this retargeted review.

No planner or packet-planner test files are in scope. In particular, this packet makes no review claim for `codex_packet_handoff/tools/planner.py` or `tests/unit/test_packet_planner.py`.

## Shared/Integrator-Locked Impact

None for the runtime review target. Commit `b929fe6c7a1159c7882acedd247aca31a93cd123` changes only lane-owned `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`; it does not edit shared-by-approval or integrator-locked files.

## Routing/Provider Impact

None. This runtime-only A2UI contract change does not touch model routing, provider configuration, or provider selection behavior.

## Commands Run And Outcomes

Required gates for the corrected handoff:

- `make scope-check` - passed for branch `codex/feat-a2ui-contract`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 511 unit tests, including `tests/unit/test_a2ui_contract.py`.
- `./typecheck-test.sh` - passed Python source compilation.
- `make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and 511 unit tests.

## Risks Or Blockers

- Runtime A2UI claims are limited to exact commit `b929fe6c7a1159c7882acedd247aca31a93cd123`.
- The branch-wide range after that commit includes out-of-scope work and is withdrawn from this review packet.
- Any future non-runtime source work must be split into a separately owned high-risk review packet.
