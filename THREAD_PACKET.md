## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main`
- Handoff type: runtime-only A2UI fixer re-review packet.
- Intended merge candidate: branch tip after this fixer commit.
- Authoritative intended merge scope against `main`: runtime A2UI scope only, plus this handoff packet.
- Runtime files in scope:
  - `src/qual/ui/a2ui.py`
  - `tests/unit/test_a2ui_contract.py`
- Explicit canonical demo-path step advanced: `preview and apply or reject a patch`.

## Scope Correction

This packet replaces the earlier inconsistent handoff. The intended review candidate is runtime-only A2UI contract work for deterministic materialized action ordering. Out-of-scope planning, docs, `.codex`, and lane-profile changes are not part of the intended runtime merge. The visible docs, planning, and lane-profile files have been reverted in this fixer working tree; the two hidden `.codex` files remain a filesystem-permission blocker noted below.

Current reviewer required-fix disposition:

- Required fix 1: the authoritative intended candidate is this branch tip against current `main`; the packet text and file list now describe the runtime-only candidate and the remaining `.codex` filesystem blocker.
- Required fix 2: runtime A2UI scope is limited to `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`.
- Required fix 3: docs/planner/lane-profile changes are not intended to merge in this packet. If needed later, they require a separate high-risk packet with ownership, approval basis, file list, tasks completed, roadmap/product mapping, risks, and passing gates.
- Required fix 4: this packet uses one runtime-only scope statement for files changed, shared/integrator impact, tasks completed, and runtime scope.
- Required fix 5: required gates are rerun and reported below.

## Canonical Demo-Path Mapping

The runtime A2UI change strengthens `preview and apply or reject a patch` by keeping apply/reject/copy action materialization stable for CLI fallback consumers. Deterministic action ordering makes patch-preview action payloads predictable while preserving typed and allowlisted action filtering.

Roadmap/product mapping:

- `ROADMAP.md`: Milestone 3 real workflow loop, narrowed to CLI fallback determinism for already-materialized A2UI actions while preserving CLI compatibility.
- `PRODUCT_VISION.md`: Canonical engine contract and shared UI contract (`A2UI`), narrowed to deterministic action identity in client-agnostic runtime payloads.
- `ARCHITECTURE.md`: A2UI card/action contracts with typed action handling and CLI fallback preserved.

## Tasks Completed

1. Canonicalized materialized A2UI action ordering so filtered action payloads are stable for engine-facing CLI fallback consumers. Canonical demo-path step advanced: `preview and apply or reject a patch`.
2. Preserved typed and allowlisted action filtering, including exclusion of unsupported action shapes from the A2UI contract surface. Canonical demo-path step advanced: `preview and apply or reject a patch`.
3. Preserved CLI rendering fallback behavior and covered deterministic filtered action ordering in `tests/unit/test_a2ui_contract.py`. Canonical demo-path step advanced: `preview and apply or reject a patch`.

## Scope Completed

Runtime-only A2UI contract review for deterministic materialized action ordering. Shared, automation/tooling, Textual, engine, routing, provider, and broader plan/doc changes are outside this handoff.

## Files Changed

Runtime review files:

- `src/qual/ui/a2ui.py`
- `tests/unit/test_a2ui_contract.py`

Handoff metadata:

- `THREAD_PACKET.md`

No Textual implementation files are in scope. No automation/tooling source or test files are in scope. No docs or lane-profile changes are in scope for this runtime A2UI review.

Filesystem-blocked out-of-scope metadata still visible in `main..HEAD` until the sandbox permits writes under `.codex`:

- `.codex/kickoff_packets/feat-a2ui-contract.md`
- `.codex/packet_planner/state.json`

## Shared/Integrator-Locked Impact

Shared/integrator-locked edits: None for the runtime A2UI candidate.

The runtime files are lane-owned or test coverage for the A2UI contract behavior under review. This packet does not submit shared-by-approval or integrator-locked file edits.

## Routing/Provider Impact

None. This runtime-only A2UI contract change does not touch model routing, provider configuration, or provider selection behavior.

## Commands Run And Outcomes

Required gates for this corrected fixer handoff:

- `make scope-check` - passed for branch `codex/feat-a2ui-contract`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 511 unit tests, including `tests/unit/test_a2ui_contract.py`.
- `./typecheck-test.sh` - passed Python source compilation.
- `make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and 511 unit tests.

## Risks Or Blockers

- Runtime A2UI claims are limited to deterministic materialized action ordering for `preview and apply or reject a patch`.
- Any future non-runtime source, docs, planner, or lane-profile work must be split into a separate high-risk review packet.
- Blocker: this sandbox cannot write the two `.codex` files listed above, so they could not be reverted here despite being out of scope.
