## Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Final HEAD SHA: `54314b4debf4bc61a012bcc002f6f511a0a97b92`
- Reviewed implementation commit(s):
  - `54314b4debf4bc61a012bcc002f6f511a0a97b92`
  - `e78f6b247c3c70590ef32cca0d8902ddcf2e32a9`
  - `1d07cbfc371f677959d26a60f3140888d8142eb3`
  - `4f1c25fa61974359518ca05eb5c9bb3ddb927427`
  - `3b4de0153788cfe2f35a761759d052dc2789fdf2`

## Scope goal

Harden the `feat-commands` command surface so catalog lookups and `diff_preview` output stay deterministic, verifiable, and suitable for CLI-first operator use.

## Scope completed

- Corrected `diff_preview` fingerprint semantics so the reported SHA-256 hashes the exact emitted payload after label application, header suppression, truncation, and summary-only handling.
- Added focused command-contract tests for JSON output, no-diff JSON shape, custom labels, and fingerprint correctness.
- Added spec-aware command catalog helper coverage for lookup aliases and manifest projections, plus the `canonical.py` re-export used by the public command surface.
- Regenerated the handoff packet from the real `main...codex/feat-commands` delta so the review packet maps to the branch tip actually being submitted.
- Documented the integrator-approved shared-test exceptions and the policy-support `scripts/scope-check.sh` edit that keeps `make scope-check` aligned with the branch's allowed shared files.

## Files changed

- `src/qual/commands/__init__.py` (lane-owned)
- `src/qual/commands/canonical.py` (lane-owned)
- `src/qual/commands/catalog.py` (lane-owned)
- `src/qual/commands/diff_preview.py` (lane-owned)
- `tests/unit/test_commands_catalog.py` (integrator-approved shared file)
- `tests/unit/test_diff_preview.py` (integrator-approved shared file)
- `scripts/scope-check.sh` (policy-support edit for the approved shared tests)
- `THREAD_PACKET.md` (handoff artifact)

## Tasks completed

1. Corrected `diff_preview` fingerprinting to hash the exact emitted diff payload.
2. Added focused unit coverage for JSON output, no-diff shape, labels, and fingerprints.
3. Added command-catalog contract coverage for the spec-aware lookup helpers and the canonical-command re-export.
4. Regenerated the handoff packet so it cites the real branch tip, the shared-test approvals, and the policy-support scope-check edit.

## Commands run and outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers

- Risk: `LOW`
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- Milestone 1 - Bootstrap Flow Stabilization: keep the command surface deterministic so CLI operators get stable catalog and diff-preview behavior.
- Milestone 2 - Test Hardening: cover the command surface with focused contract tests for JSON output, no-diff shape, and fingerprint verification.
- Milestone 3 - Product Readiness: lock the emitted diff fingerprint semantics to the exact user-visible artifact so downstream automation can verify what the command returned.

### Vision capability affected

- Capability 3 - Auditable generation: the emitted SHA-256 fingerprint now verifies the exact diff payload returned by the command.
- Capability 4 - Operator-first control surface: the CLI-facing command contract stays stable while exposing deterministic JSON output for automation.

### Routing/provider impact note

- None. This change only affects local command formatting, verification metadata, and focused command-contract test coverage.

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- Integrator-approved shared-file exceptions: `tests/unit/test_commands_catalog.py`, `tests/unit/test_diff_preview.py`
- Policy-support edit: `scripts/scope-check.sh` keeps the feat-commands lane's approved shared-test set enforceable during `make scope-check`.
