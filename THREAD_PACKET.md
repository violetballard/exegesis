# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Implementation commit(s):
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
- Docs-only alignment commit(s):
  - `17068409de03625c5c0f1cc06855ce6307e1455a` (`docs(commands): align feat-commands packet with contract hardening`)
  - `fc9939d1b8287488d16266884d6008e4fd93aa4b` (`docs(commands): resync feat-commands handoff packet`)
  - `e62d61d1771da5a221275f858d12c965abdae76d` (`docs(commands): resync feat-commands handoff packet`)
  - `775aa13361d295f9d78d00d8abcc0fe84fb0e160` (`docs(commands): canonicalize feat-commands packet fields`)
  - `411e456e0119a2a073ee1754dc18e7b2f0db4e14` (`docs(commands): tighten handoff scope note`)
  - `7b40979fcd8e7da9b9fd8161e414ef4e54e8db43` (`docs(commands): clarify re-review packet scope`)

## Scope goal
- Harden the CLI command contract so `command_cli_contract()` stays deterministic, uses the canonical command order, and fails fast if the parser surface drifts from the catalog. This keeps the CLI-first MVP surface stable while the engine contract settles.

## Scoped review slice
- This re-review packet is intentionally scoped to implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` only.
- Earlier branch groundwork such as `src/qual/commands/__init__.py` remains in the branch delta from prior command-surface work, but it is not part of the required-fix slice being re-submitted here.

## Lane/owned paths
- `src/qual/commands/**`
- Approved shared tests:
  - `tests/unit/test_commands_catalog.py`

## Scope completed
- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares the CLI lookup-table canonical names against `command_names()` and raises `ValueError` when the catalog and parser surface drift.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for the canonical-name alignment path and the drift rejection path.
- Kept this handoff scoped to the `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` command-catalog implementation slice only; it does not re-describe earlier route-catalog or diff-preview work on the branch.
- Added docs-only alignment commits so the handoff packet names the implementation commit separately from the metadata-only resyncs and keeps the re-review slice aligned to the current branch head.

## Kickoff budget/limits compliance
- High-risk shared-file handoff: task budget `4`, time budget `30m`.
- The submitted branch stays within lane-owned command code plus the approved `tests/unit/test_commands_catalog.py` shared test exception.

## Approved exception note
- Approved shared-file exception for `tests/unit/test_commands_catalog.py`.

## Tasks completed (numbered)
1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Regenerated and tightened the packet so the branch metadata records the implementation commit and docs-only resync commits separately, keeps the re-review scoped to the command-catalog slice, and uses canonical roadmap and vision labels.

## Files changed
### Implementation files changed
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py` (approved shared-file exception for the implementation commit)
### Docs-only alignment files changed
- `THREAD_PACKET.md`

## Scope boundary note
- This packet re-submits only the `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` command-catalog implementation slice plus docs-only alignment at the current head.
- It does not claim earlier branch groundwork as part of the reviewed implementation files for this re-review.

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
- CLI command compatibility now has a deterministic canonical-name contract so the parser surface cannot silently drift from the command catalog.

### Roadmap item(s) affected
- `Milestone 3: Real workflow loop` - preserve CLI compatibility while the package/layout migration lands by hardening the submitted command contract against silent parser/catalog drift.
- `feat-commands` - stable CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision capability affected
- `Canonical engine contract` - CLI compatibility remains stable while the command surface now rejects silent parser/catalog drift before it can reach operators.
- `Auditable state and workflow` - the command surface now fails loudly on drift, making the operator contract explicit and traceable.

### Routing/provider impact note
- None. This change only affects local command contract validation and focused command-catalog test coverage.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Approved shared-file exception covers `tests/unit/test_commands_catalog.py`.
- Approval basis: `scripts/scope-check.sh` explicitly permits `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`, and this packet only claims that one non-owned test file.
- Re-review mapping basis: the roadmap and vision fields above follow the reviewer-required canonical labels for this command-contract handoff slice.
