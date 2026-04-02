# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Implementation commit(s):
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
- Docs-only alignment commit(s):
  - `17068409de03625c5c0f1cc06855ce6307e1455a` (`docs(commands): align feat-commands packet with contract hardening`)

## Scope goal
- Harden the CLI command contract so `command_cli_contract()` stays deterministic, uses the canonical command order, and fails fast if the parser surface drifts from the catalog. This keeps the CLI-first MVP surface stable while the engine contract settles.

## Lane/owned paths
- `src/qual/commands/**`
- Approved shared tests:
  - `tests/unit/test_commands_catalog.py`

## Scope completed
- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares the CLI lookup-table canonical names against `command_names()` and raises `ValueError` when the catalog and parser surface drift.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for the canonical-name alignment path and the drift rejection path.
- Added a docs-only alignment commit so the handoff packet names the implementation commit separately from the metadata-only resync.

## Kickoff budget/limits compliance
- High-risk shared-file handoff: task budget `4`, time budget `30m`.
- The submitted branch stays within lane-owned command code plus the approved `tests/unit/test_commands_catalog.py` shared test exception.

## Approved exception note
- Approved shared-file exception for `tests/unit/test_commands_catalog.py`.

## Tasks completed (numbered)
1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Regenerated the packet so the branch metadata records the implementation commit and the docs-only resync separately.

## Files changed
### Implementation files changed
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py` (approved shared-file exception for the implementation commit)
### Docs-only alignment files changed
- `THREAD_PACKET.md`

## Commands run and outcomes
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers
- Risk: `MEDIUM`
- Blockers: none

## Required handoff fields
### Scope completed
- CLI command compatibility now has a deterministic canonical-name contract so the parser surface cannot silently drift from the command catalog.

### Roadmap item(s) affected
- `Milestone 3: Real workflow loop` - preserve CLI compatibility and migration-safe entrypoints while the CLI contract is hardened against catalog drift.
- `feat-commands` - stable CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision capability affected
- `Canonical engine contract` - CLI compatibility remains stable while the command surface now rejects parser/catalog drift before it can reach operators.
- `Auditable state and workflow` - the command surface now fails loudly on drift, making the operator contract explicit and traceable.

### Routing/provider impact note
- None. This change only affects local command contract validation and focused command-catalog test coverage.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Approved shared-file exception covers `tests/unit/test_commands_catalog.py`.
