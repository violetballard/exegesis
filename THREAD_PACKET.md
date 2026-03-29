# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `cf6e4984d3d0f154d2be69c58f582868c9549585`
- Reviewed commit(s):
  - `cf6e4984d3d0f154d2be69c58f582868c9549585`

## Scope goal
- Keep the `feat-commands` handoff aligned with the command-catalog, canonical mapping, and diff-preview CLI contract work already present on the branch, plus the two explicitly approved shared tests.

## Lane/owned paths
- `src/qual/commands/**`
- Approved shared tests:
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`

## Scope completed
- Restored the command-catalog surface under `src/qual/commands/**` and added spec-aware lookup helpers plus canonical command mapping.
- Hardened diff-preview output contracts so the emitted SHA-256 is derived from the exact payload users receive after labels, header suppression, truncation, and summary-only handling.
- Added focused coverage for the command-catalog, canonical mapping, and diff-preview contracts.
- Regenerated the handoff packet and lane metadata so the review evidence matches the submitted code/test delta and keeps the shared-file approvals explicit.

## Kickoff budget/limits compliance
- High-risk shared-test handoff: task budget `4`, time budget `30m`, size limits `<=8 files` and `<=300 net LOC`.
- The reviewed implementation spans 6 lane-owned or approved test files, including `src/qual/commands/canonical.py` and the two approved shared tests.
- The handoff stays centered on the command-catalog, canonical mapping, and diff-preview contract work already present on the branch.

## Approved exception note
- Approved shared-file exception for `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`.

## Tasks completed (numbered)
1. Restored the command-catalog surface and added spec-aware lookup helpers plus canonical command mapping under `src/qual/commands/**`.
2. Hardened diff-preview output contracts so the fingerprint covers the exact emitted payload after labels, header suppression, truncation, and summary-only handling.
3. Added focused coverage for the command-catalog, canonical mapping, and diff-preview contract paths.
4. Regenerated the handoff packet and lane metadata so the review evidence matches the actual code/test delta and keeps the shared-file approvals explicit.

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
- Risk: `HIGH`
- Blockers: none

## Required handoff fields
### Roadmap item(s) affected
- Milestone 3 - Product Readiness (Planned): lock the command-catalog and diff-preview CLI contracts so the operator-facing command surface stays deterministic, auditable, and ready for CLI-first use.

### Vision capability affected
- 3. Auditable generation - the emitted fingerprint verifies the exact diff payload users receive, including label application and truncation behavior.
- 4. Operator-first control surface - CLI review gates stay aligned with the command-catalog, canonical mapping, and diff-preview contract surface plus the approved shared tests.

### Routing/provider impact note
- None. This change only affects local packet metadata and command-contract test coverage; no routing/provider files change.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
