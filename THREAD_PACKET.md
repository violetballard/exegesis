## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main`
- Handoff type: corrected A2UI runtime/shared-contract fixer re-review packet.
- Corrected review scope: reviewed A2UI runtime slice from `b929fe6c7a1159c7882acedd247aca31a93cd123`, the restored shared A2UI contract/model/type package deleted by `88afea2e81d44cee13d0f85e325cff5ad9dfb056`, and this corrected handoff packet.
- Explicit canonical demo-path step advanced: `preview and apply or reject a patch`.

## Scope Correction

The previous branch tip incorrectly described the post-`b929fe6c7` delta as metadata-only. It was not metadata-only: it included Textual, engine, shared contracts, docs, automation/tooling, quality-script, `.agents`, and `.codex` changes outside this A2UI runtime lane.

This fixer keeps the reviewed A2UI runtime slice and restores the canonical shared A2UI package required by `ROADMAP.md`, `PRODUCT_VISION.md`, and `ARCHITECTURE.md`. The previous deletion commit was source-bearing, not metadata-only, because it removed shared contract/model/type modules.

No planner or packet-planner test maintenance is claimed in this packet. `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` are not part of this corrected merge candidate.

## Canonical Demo-Path Mapping

This A2UI slice advances `preview and apply or reject a patch`.

The runtime change keeps apply/reject/copy action materialization stable for CLI fallback consumers. Deterministic action ordering makes patch-preview action payloads predictable while preserving typed and allowlisted action filtering.

## Tasks Completed

1. Canonicalized materialized A2UI action ordering so filtered action payloads stay stable for engine-facing CLI fallback consumers.
2. Preserved typed and allowlisted action filtering, including exclusion of unsupported action shapes from the A2UI contract surface.
3. Preserved CLI rendering fallback behavior and covered deterministic filtered action ordering in `tests/unit/test_a2ui_contract.py`.
4. Restored shared A2UI action/card contracts, selection model, object types, and package exports deleted by `88afea2e81d44cee13d0f85e325cff5ad9dfb056`.
5. Corrected this handoff packet so it describes `feat-a2ui-contract`, documents the source-bearing shared restoration, and removes unsupported planner/test claims.

## Files Changed

Runtime review files:

- `src/qual/ui/a2ui.py`
- `tests/unit/test_a2ui_contract.py`

Restored shared contract/model/type files:

- `exegesis_shared/__init__.py`
- `shared/src/exegesis_shared/__init__.py`
- `shared/src/exegesis_shared/contracts/__init__.py`
- `shared/src/exegesis_shared/contracts/actions.py`
- `shared/src/exegesis_shared/contracts/cards.py`
- `shared/src/exegesis_shared/models/__init__.py`
- `shared/src/exegesis_shared/models/selection.py`
- `shared/src/exegesis_shared/types/__init__.py`
- `shared/src/exegesis_shared/types/object_types.py`
- `shared/src/exegesis_shared/utils/__init__.py`

Corrective handoff file:

- `THREAD_PACKET.md`

## Shared/Integrator-Locked Impact

Shared edits: yes. This fixer restores the shared A2UI modules that were deleted by `88afea2e81d44cee13d0f85e325cff5ad9dfb056`.

Justification: the current Milestone 3/MVP narrowing requires A2UI cards/actions/selection contracts to remain in a client-agnostic shared layer with CLI fallback. Restoring these files keeps existing engine/shared imports valid and aligns the branch with the documented A2UI contract ownership.

## Routing/Provider Impact

None. The intended A2UI runtime change does not touch model routing, provider configuration, or provider selection behavior.

## Commands Run And Outcomes

Required gates for this corrected fixer handoff:

- `make scope-check` - passed; reported no tracked changed files before staging restored shared files.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 156 unit tests.
- `./typecheck-test.sh` - passed Python source compilation.
- `make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and 156 unit tests.

## Risks Or Blockers

- Runtime A2UI claims are limited to deterministic materialized action ordering and restored shared contract availability for `preview and apply or reject a patch`.
- This packet does not claim planner changes or `tests/unit/test_packet_planner.py` coverage.
