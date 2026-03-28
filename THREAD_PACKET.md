# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `e53af6696629a9cccda27ac1b344825bae8dc858`

## Scope goal
- Harden the command surface for the CLI-first operator flow so command lookup helpers, diff-preview output, and emitted fingerprints stay deterministic and verifiable.

## Lane/owned paths
- `src/qual/commands/**`
- Approved shared test coverage:
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`

## Approved exception note
- Approved shared-file exceptions for `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` to add focused contract coverage required by review.

## Scope completed
- Added spec-aware command catalog helpers, canonical lookup surfaces, and deterministic flow projections so command metadata resolves consistently for the CLI surface.
- Hardened `diff_preview` output contracts so the SHA-256 fingerprint is derived from the exact emitted diff payload after label application, header suppression, truncation, and summary-only handling.
- Added focused unit coverage for command lookup and flow projections plus diff-preview JSON/text contracts, including the no-diff shapes and fingerprint correctness paths the reviewer requested.
- Realigned the kickoff packet and lane metadata, then regenerated this handoff packet so the submitted branch state matches the actual `feat-commands` delta from `main`.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The branch delta is 9 files changed and remains within the lane size limits.

## Tasks completed (numbered)
1. Added spec-aware command catalog helpers and exports so command metadata resolves deterministically.
2. Hardened `diff_preview` fingerprint semantics so the reported digest matches the emitted artifact after labels, suppression, truncation, and summary-only handling.
3. Added focused unit tests for command-catalog projections, diff-preview JSON output, no-diff payloads, and fingerprint correctness.
4. Realigned the handoff packet with the actual `feat-commands` branch delta and the approved shared test files.

## Files changed for this turn
- `.codex/kickoff_packets/feat-commands.md`
- `.codex/lane_meta/feat-commands.json`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`
- `THREAD_PACKET.md`

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
- Milestone 1 - Bootstrap Flow Stabilization: keep the command surface deterministic for CLI-first operator flows.
- Milestone 2 - Test Hardening: add focused contract coverage for command lookup helpers, flow sequencing, diff-preview output, and fingerprint handling.
- Milestone 5 - A2UI Presentation Layer: preserve the CLI fallback surface that feeds the same engine/A2UI command contracts.

### Vision capability affected
- Capability 3 - Auditable generation: the emitted SHA-256 fingerprint now verifies the exact diff payload returned by `diff_preview`.
- Capability 4 - Operator-first control surface: command lookup helpers now resolve canonical command metadata deterministically for the CLI surface.
- Capability 5 - Agent-to-UI protocol (`A2UI`): the command contract remains stable for downstream structured UI routing.

### Routing/provider impact note
- None. This change only affects local command lookup behavior, diff-preview output formatting, and command-surface contract coverage; no routing/provider files change.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` (approved exceptions for `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`)
