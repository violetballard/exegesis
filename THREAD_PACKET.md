# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `dad3916f`
- Reviewed commit(s):
  - `e78f6b24` (`fix(commands): restore command catalog`)
  - `b2a0a2d1` (`feat(commands): add CLI route summary helper`)
  - `dad3916f` (`Strengthen command CLI entrypoint contract`)
  - `4807235d` (`fix(commands): clarify diff_preview fingerprint payload`)
  - `2afa0f7f` (`fix(commands): restore diff preview scope allowance`)
  - `3dfd0146` (`fix(commands): harden diff preview handoff`)

## Scope goal
- Harden the CLI command surface so catalog-backed entrypoints, route summaries, and diff-preview output contracts stay deterministic for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`
- Approved shared tests:
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`

## Scope completed
- Added the deterministic command catalog and route contract surface in `src/qual/commands/catalog.py`, including alias resolution, flow-step ordering, CLI lookup tables, route summaries, and the canonical surface contract.
- Re-exported the catalog helpers from `src/qual/commands/__init__.py` and routed `canonical_command` through the catalog module in `src/qual/commands/canonical.py`.
- Hardened `src/qual/commands/diff_preview.py` so emitted diff payloads and SHA-256 fingerprints stay aligned after label application, header suppression, truncation, and summary-only collapsing.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical aliases, CLI route summaries, flow contracts, and validation errors, plus focused coverage in `tests/unit/test_diff_preview.py` for labeled JSON output and fingerprint behavior.
- Updated `scripts/scope-check.sh` so the approved `tests/unit/test_commands_catalog.py` shared test is allowed on `feat-commands`.
- Regenerated this packet so the review evidence matches the actual branch delta instead of the older diff-preview-only slice.

## Kickoff budget/limits compliance
- High-risk shared-file handoff: task budget `4`, time budget `30m`.
- The submitted branch combines the command catalog surface, diff-preview contract hardening, and the scope-check allowance needed for the approved shared files.

## Approved exception note
- Approved shared-file exception for `scripts/scope-check.sh`, `tests/unit/test_commands_catalog.py`, and `tests/unit/test_diff_preview.py`.

## Tasks completed (numbered)
1. Added the command catalog and CLI route contract surface for deterministic command lookup and flow ordering.
2. Re-exported the catalog helpers and kept `canonical_command` and `diff_preview` aligned with the catalog-backed command surface.
3. Added focused unit coverage for command catalog contracts and diff-preview fingerprint behavior.
4. Updated scope-check and regenerated the packet so the submitted branch description matches the actual net diff and explicit shared-file approvals.

## Files changed
- `THREAD_PACKET.md`
- `scripts/scope-check.sh`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

## Commands run and outcomes
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers
- Risk: `HIGH`
- Blockers: none

## Required handoff fields
### Scope completed

- Hardened the CLI command surface so catalog-backed entrypoints, route summaries, and diff-preview output contracts stay deterministic for CLI-first operator use.

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` - keep CLI compatibility and migration-safe entrypoints stable while the command catalog, route summaries, and diff-preview contract harden for the MVP loop.

### Vision capability affected

- `Canonical engine contract` - CLI compatibility remains stable while the command surface exposes a deterministic catalog, aliases, and route summaries.
- `Auditable state and workflow` - the diff-preview fingerprint now verifies the exact emitted diff payload after normalization and summary-only collapsing.

### Routing/provider impact note

- None. This change only affects the local command surface, diff-preview formatting, and the scope-check allowance for the approved shared files.

### Proposed README patch text

- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Approved shared-file exception covers `scripts/scope-check.sh`, `tests/unit/test_commands_catalog.py`, and `tests/unit/test_diff_preview.py`.
