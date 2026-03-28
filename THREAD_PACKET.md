# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `d5c6fc70674068b3bde2bc7616984c6e54faeee6`

## Scope goal
- Reissue the `feat-commands` handoff packet so the metadata matches the current branch delta from `main`.

## Lane/owned paths
- `src/qual/commands/**`
- Approved shared tests:
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
- Shared policy support:
  - `scripts/scope-check.sh`

## Scope completed
- Added the command catalog surface and diff-preview contract helpers under `src/qual/commands/**`.
- Hardened diff-preview output contracts so the emitted SHA-256 matches the exact payload users receive.
- Added focused coverage for the command catalog and diff-preview contracts, and aligned the scope-check policy for the approved shared regression.
- Regenerated the handoff packet and lane metadata from the real `main..HEAD` delta.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The branch delta changes 10 files total: 4 command files, 1 policy file, 2 shared tests, and 3 packet/metadata files.
- The change stays centered on the command-catalog and diff-preview contract work already present on the branch and keeps the review packet truthful.

## Approved exception note
- Approved shared-file exception for `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`; matching scope-check policy allowance restored in `scripts/scope-check.sh`.

## Tasks completed (numbered)
1. Added the command catalog surface and supporting lookup helpers under `src/qual/commands/**`.
2. Hardened diff-preview output contracts so the fingerprint covers the exact emitted payload.
3. Added focused coverage for the command catalog and diff-preview contract paths.
4. Regenerated the handoff packet and lane metadata so the review evidence matches the real `main..HEAD` delta.

## Files changed
- `.codex/kickoff_packets/feat-commands.md`
- `.codex/lane_meta/feat-commands.json`
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
- Risk: `LOW`
- Blockers: none

## Required handoff fields
### Roadmap item(s) affected
- Milestone 3 - Product Readiness (Planned): keep the `feat-commands` handoff packet aligned with the actual submitted branch delta so review evidence remains truthful.

### Vision capability affected
- 4. Operator-first control surface - CLI review gates stay aligned with the current branch metadata so the lane can be reviewed without stale scope claims.

### Routing/provider impact note
- None. This change only affects local packet metadata and scope-check policy for the approved shared tests; no routing/provider files change.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
