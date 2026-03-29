## Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Final HEAD SHA: `ff2b3d0e2a21873f8b8b2c4170da828c9cb9c780`
- Reviewed implementation commit(s):
  - `3b4de0153788cfe2f35a761759d052dc2789fdf2`
  - `4f1c25fa61974359518ca05eb5c9bb3ddb927427`
  - `3378e905fab4653d38070b8e272ce4e4c6d22908`
  - `e53af6696629a9cccda27ac1b344825bae8dc858`
  - `1d07cbfc371f677959d26a60f3140888d8142eb3`

## Scope goal

Harden the `feat-commands` command surface so catalog lookups and `diff_preview` output stay deterministic, verifiable, and suitable for CLI-first operator use.

## Scope completed

- Corrected `diff_preview` fingerprint semantics so the reported SHA-256 hashes the exact emitted payload after label application, header suppression, truncation, and summary-only handling.
- Added focused command-contract tests for JSON output, no-diff JSON shape, custom labels, and fingerprint correctness.
- Added spec-aware command catalog helper coverage for lookup aliases and manifest projections.
- Regenerated the handoff packet from the real `main..codex/feat-commands` delta so the review packet maps to the branch state actually being submitted.
- Documented explicit shared-file approval for `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`.

## Files changed

- `src/qual/commands/__init__.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`
- `THREAD_PACKET.md`

## Tasks completed

1. Corrected `diff_preview` fingerprinting to hash the exact emitted diff payload.
2. Added focused unit coverage for JSON output, no-diff shape, labels, and fingerprints.
3. Added command-catalog contract coverage for the spec-aware lookup helpers.
4. Regenerated the handoff packet so it cites the real implementation commits and shared-file approvals.

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
- Approved shared-file exception: `tests/unit/test_commands_catalog.py`, `tests/unit/test_diff_preview.py`
