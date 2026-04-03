# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Implementation commit(s):
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)

## Reviewer-fix resubmission note
- This fixer pass is docs-only and keeps the handoff on one coherent slice: the `command_cli_contract()` catalog hardening from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- The packet does not make any `diff_preview` claims.
- The implementation slice named below is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- The roadmap and vision mappings below use the exact milestone and capability labels from the current `ROADMAP.md` and `PRODUCT_VISION.md` in this worktree.
- The non-owned test path named in the scope note and in `Files changed` is the same file: `tests/unit/test_commands_catalog.py`.

## Scope goal
- Harden the CLI command contract so `command_cli_contract()` stays deterministic, uses the canonical command order, and fails fast if the parser surface drifts from the catalog.

## Scope completed
- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
- Reissued the handoff packet as a command-catalog-only slice so the review scope matches the claimed implementation files.

## Kickoff budget/limits compliance
- Default lane budget respected.
- The implementation slice remained limited to one owned command file plus one non-owned test file.

## Approved exception note
- Approved shared-file exception for `tests/unit/test_commands_catalog.py`.

## Scope-policy note
- `tests/unit/test_commands_catalog.py` is the only shared-by-approval implementation file named in this handoff.
- The local scope policy in `scripts/scope-check.sh` explicitly allowlists that same path on `codex/feat-commands*`.

## Tasks completed (numbered)
1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Regenerated the packet so the branch metadata stays scoped to the command-catalog slice and uses the current canonical roadmap and vision labels from this worktree.

## Files changed
### Implementation files changed
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py` (approved shared-file exception; allowlisted by the local scope policy for this lane)

### Docs-only alignment files changed
- `THREAD_PACKET.md`

## Commands run with results
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
- CLI command compatibility now has a deterministic canonical-name contract so the parser surface cannot silently drift from the command catalog.

### Roadmap item(s) affected
- `Milestone 3: Real workflow loop` - preserve CLI compatibility while the package/layout migration lands by keeping the command contract deterministic and rejecting parser/catalog drift.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision capability affected
- `3. Canonical engine contract` - CLI compatibility remains stable while Textual stays disabled, and the command surface now rejects parser/catalog drift before it reaches operators.
- `6. Auditable state and workflow` - parser/catalog drift now fails loudly instead of silently changing an operator-visible contract.

### Routing/provider impact note
- None. This change only affects local command contract validation and focused command-catalog test coverage.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` (`tests/unit/test_commands_catalog.py` only; approved shared-file exception)
- The scope-policy note and `Files changed` section name the same shared-by-approval test path.
- No integrator-locked file is claimed in the implementation slice.
- `THREAD_OWNERSHIP.md` keeps `src/qual/commands/**` as the lane-owned path for `codex/feat-commands*` and marks `tests/unit/test_commands_catalog.py` as shared by approval only, so this packet records that file as the one approved shared edit.
- The current local scope policy in `scripts/scope-check.sh` explicitly allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`, so this packet records that exact path consistently.
