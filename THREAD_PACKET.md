## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main`
- Handoff type: corrected A2UI runtime fixer re-review packet.
- Corrected review scope: reviewed A2UI runtime slice from `b929fe6c7a1159c7882acedd247aca31a93cd123`, plus this handoff packet and the narrowing commit that removes writable out-of-scope files added after that runtime slice.
- Explicit canonical demo-path step advanced: `preview and apply or reject a patch`.

## Scope Correction

The previous branch tip incorrectly described the post-`b929fe6c7` delta as metadata-only. It was not metadata-only: it included Textual, engine, shared contracts, docs, automation/tooling, quality-script, `.agents`, and `.codex` changes outside this A2UI runtime lane.

This fixer narrows the writable worktree back to the reviewed A2UI runtime slice. The intended runtime review remains limited to deterministic materialized action ordering in `src/qual/ui/a2ui.py` and its focused contract coverage in `tests/unit/test_a2ui_contract.py`.

Hidden `.agents/**` and `.codex/**` paths are not writable in this sandbox, so those branch-tip metadata/automation deltas could not be mechanically reverted here. They are explicitly not part of the intended A2UI runtime merge candidate and must be split to their owning lanes if they remain visible to the integrator.

## Canonical Demo-Path Mapping

This A2UI slice advances `preview and apply or reject a patch`.

The runtime change keeps apply/reject/copy action materialization stable for CLI fallback consumers. Deterministic action ordering makes patch-preview action payloads predictable while preserving typed and allowlisted action filtering.

## Tasks Completed

1. Canonicalized materialized A2UI action ordering so filtered action payloads stay stable for engine-facing CLI fallback consumers.
2. Preserved typed and allowlisted action filtering, including exclusion of unsupported action shapes from the A2UI contract surface.
3. Preserved CLI rendering fallback behavior and covered deterministic filtered action ordering in `tests/unit/test_a2ui_contract.py`.
4. Removed writable out-of-scope post-`b929fe6c7` changes from this branch worktree so Textual, engine, shared, docs, tooling, and quality-script changes are no longer submitted by this lane commit.

## Files Changed

Runtime review files:

- `src/qual/ui/a2ui.py`
- `tests/unit/test_a2ui_contract.py`

Corrective handoff/narrowing file:

- `THREAD_PACKET.md`

The branch still has historical hidden-path deltas under `.agents/**` and `.codex/**` relative to `b929fe6c7`; this sandbox reports `Operation not permitted` when writing those directories. Those hidden paths are excluded from this corrected runtime packet.

## Shared/Integrator-Locked Impact

Shared/integrator-locked edits: none for the intended A2UI runtime candidate.

This packet does not submit Textual implementation, provider routing, engine, shared-contract, quality-script, or automation/tooling source changes as part of the A2UI runtime review.

## Routing/Provider Impact

None. The intended A2UI runtime change does not touch model routing, provider configuration, or provider selection behavior.

## Commands Run And Outcomes

Required gates for this corrected fixer handoff:

- `make scope-check` - passed for branch `codex/feat-a2ui-contract`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 156 unit tests after restoring the exact reviewed A2UI runtime files from `b929fe6c7`.
- `./typecheck-test.sh` - passed Python source compilation.
- `make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and 156 unit tests.

## Risks Or Blockers

- Runtime A2UI claims are limited to deterministic materialized action ordering for `preview and apply or reject a patch`.
- Hidden `.agents/**` and `.codex/**` branch-tip deltas could not be reverted in this sandbox because those directories are not writable. If the integrator requires a branch tip with literally no hidden metadata/automation delta, that cleanup must run in an environment with write access to those paths or be split to the proper automation/metadata lane.
