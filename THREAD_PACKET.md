# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Reviewed commit(s):
  - `e78f6b247c3c70590ef32cca0d8902ddcf2e32a9`
  - `e53af6696629a9cccda27ac1b344825bae8dc858`
  - `3dfd014632493cdd66b363c637846596d490e7af`

## Scope goal
- Harden the command catalog and diff-preview contracts so lookup helpers, labeled/text output, JSON responses, and emitted fingerprints stay deterministic and verifiable for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`
- Approved shared tests:
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`

## Scope completed
- Restored the command catalog surface under `src/qual/commands/**` and added spec-aware lookup helpers.
- Hardened diff-preview output contracts so the emitted SHA-256 is derived from the exact payload users receive after labels, suppression, truncation, and summary-only handling.
- Added focused coverage for the command catalog and diff-preview contracts.
- Regenerated the handoff packet and lane metadata so the review evidence now matches the actual code/test delta and excludes the out-of-lane scope-check script edit.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The reviewed implementation spans 6 lane-owned or approved test files.
- The handoff stays centered on the command-catalog and diff-preview contract work already present on the branch and keeps the review packet truthful.

## Approved exception note
- Approved shared-file exception for `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`.

## Tasks completed (numbered)
1. Restored the command catalog surface and added spec-aware lookup helpers under `src/qual/commands/**`.
2. Hardened diff-preview output contracts so the fingerprint covers the exact emitted payload after labels, header suppression, truncation, and summary-only handling.
3. Added focused coverage for the command catalog and diff-preview contract paths.
4. Regenerated the handoff packet and lane metadata so the review evidence matches the actual code/test delta and excludes the out-of-lane scope-check script edit.

## Files changed
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
- Risk: `LOW`
- Blockers: none

## Required handoff fields
### Roadmap item(s) affected
- Milestone 3 - Product Readiness (Planned): keep the `feat-commands` handoff packet aligned with the owned command-contract changes and approved shared tests.

### Vision capability affected
- 3. Auditable generation - the emitted fingerprint verifies the exact diff payload users receive.
- 4. Operator-first control surface - CLI review gates stay aligned with the command-contract surface and approved shared tests.

### Routing/provider impact note
- None. This change only affects local packet metadata and command-contract test coverage; no routing/provider files change.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `NO`
