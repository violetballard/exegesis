# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `d5c6fc70674068b3bde2bc7616984c6e54faeee6`

## Scope goal
- Tighten the `feat-commands` handoff so the submitted scope is limited to `src/qual/commands/**` plus the explicitly approved shared tests.

## Lane/owned paths
- `src/qual/commands/**`
- Approved shared tests:
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`

## Scope completed
- Added the command catalog surface and diff-preview contract helpers under `src/qual/commands/**`.
- Hardened diff-preview output contracts so the emitted SHA-256 matches the exact payload users receive.
- Added focused coverage for the command catalog and diff-preview contracts.
- Regenerated the handoff packet and lane metadata so the review evidence only names the owned command paths plus the approved shared tests.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The submitted scope is 6 files total: 4 command files and 2 shared tests.
- The change stays centered on the command-catalog and diff-preview contract work already present on the branch and keeps the review packet truthful.

## Approved exception note
- Approved shared-file exception for `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`.

## Tasks completed (numbered)
1. Added the command catalog surface and supporting lookup helpers under `src/qual/commands/**`.
2. Hardened diff-preview output contracts so the fingerprint covers the exact emitted payload.
3. Added focused coverage for the command catalog and diff-preview contract paths.
4. Regenerated the handoff packet and lane metadata so the review evidence matches the owned command scope and approved shared tests.

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
- Shared/integrator-locked edits: `YES`
