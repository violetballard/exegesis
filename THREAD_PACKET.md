# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Implementation commit(s):
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)

## Reviewer-fix resubmission note
- This fixer pass is docs-only and addresses the reviewer's required fixes by keeping the packet on one coherent command-catalog slice.
- The packet is anchored to implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, with `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py` as the only implementation files claimed by this re-review.
- The roadmap and vision mappings below use the exact canonical labels requested in the reviewer packet for re-review: `Milestone 3: Real workflow loop`, `feat-commands`, `Canonical engine contract`, and `Auditable state and workflow`.
- This resubmission reran the required gates in this lane worktree at `2026-04-03 00:13:28 PDT`, and all listed gates passed again before this docs-only fixer commit.

## Verification refresh
- Revalidated on `2026-04-03` in the current `codex/feat-commands` lane worktree with a docs-only handoff refresh; no implementation files were changed in this fixer pass.
- The reviewed implementation slice remains the same command-catalog hardening from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Latest required-gate verification run completed at `2026-04-03 00:13:28 PDT` in this worktree before this docs-only fixer commit.
- This packet keeps the reviewer-requested roadmap and vision labels intact for the re-review packet.
- This packet refresh supersedes the earlier docs-only reviewer-fix packet refreshes on this branch without changing the claimed implementation slice.

## Reviewer required fixes addressed
1. Rewrote the roadmap mapping to use the exact reviewer-requested canonical entries: `Milestone 3: Real workflow loop` and `feat-commands`.
2. Rewrote the vision mapping to use the exact reviewer-requested canonical `PRODUCT_VISION.md` capability names `Canonical engine contract` and `Auditable state and workflow`.
3. Kept the non-owned test approval note and the `Files changed` section aligned on the same actual test path: `tests/unit/test_commands_catalog.py`.
4. Re-issued the packet as one coherent slice only: the `command_cli_contract()` command-catalog hardening, without mixing in `diff_preview` or other earlier branch work.

## Scope goal
- Harden the CLI command contract so `command_cli_contract()` stays deterministic, uses the canonical command order, and fails fast if the parser surface drifts from the catalog. This keeps the CLI-first MVP surface stable while the engine contract settles.

## Scoped review slice
- This re-review packet is intentionally scoped to implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` only.
- This packet does not re-submit any `diff_preview` implementation or `tests/unit/test_diff_preview.py` coverage; the coherent review slice is the command-catalog contract only.
- The implementation files claimed below exist in the current tree at the same paths named in this packet.

## Lane/owned paths
- `src/qual/commands/**`
- Shared test path explicitly permitted by the current `scripts/scope-check.sh` policy for `codex/feat-commands*`:
  - `tests/unit/test_commands_catalog.py`

## Scope completed
- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares the CLI lookup-table canonical names against `command_names()` and raises `ValueError` when the catalog and parser surface drift.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for the canonical-name alignment path and the drift rejection path.
- Kept this handoff scoped to the `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` command-catalog implementation slice only and excluded earlier route-catalog or diff-preview branch work from the re-review packet.

## Kickoff budget/limits compliance
- High-risk shared-file handoff: task budget `4`, time budget `30m`.
- The submitted branch stays within lane-owned command code plus the single non-owned test path `tests/unit/test_commands_catalog.py`, which is explicitly permitted for `codex/feat-commands*` in `scripts/scope-check.sh`.

## Approved exception note
- Explicit shared-test approval for `tests/unit/test_commands_catalog.py` under the lane's current scope-check policy for `codex/feat-commands*`.
- No other shared-by-approval or integrator-locked path is claimed in this re-review packet.

## Tasks completed (numbered)
1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Regenerated and tightened the packet so the branch metadata stays scoped to the command-catalog slice and uses the reviewer-requested canonical roadmap and vision labels.

## Files changed
### Implementation files changed
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py` (explicit shared-by-approval test-file approval for the implementation commit)

### Docs-only alignment files changed
- `THREAD_PACKET.md`

## Scope boundary note
- This packet re-submits only the `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` command-catalog implementation slice plus docs-only alignment at the current head.
- It does not claim any `diff_preview` implementation or `tests/unit/test_diff_preview.py` coverage in this re-review packet.
- It names `tests/unit/test_commands_catalog.py` as the only shared-by-approval test path for the implementation slice in both the approval note and the files-changed list.

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
- `Milestone 3: Real workflow loop` - preserve CLI compatibility while the package/layout migration lands by keeping the command surface deterministic and smoke-testable.
- `feat-commands` - stable CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision capability affected
- `Canonical engine contract` - the command catalog now rejects parser drift before it can silently change the CLI-facing compatibility surface.
- `Auditable state and workflow` - the command surface fails loudly on drift, making operator-visible contract changes explicit and traceable.

### Routing/provider impact note
- None. This change only affects local command contract validation and focused command-catalog test coverage.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Approved shared-by-approval test file covers `tests/unit/test_commands_catalog.py`, which is also the only shared implementation file named in `Files changed`.
- Approval basis: `scripts/scope-check.sh` explicitly permits `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`.
- Re-review mapping basis: the roadmap and vision fields above use the exact canonical milestone and capability names requested in the reviewer packet for this command-contract handoff slice.
- Coherent-slice basis: this re-review packet covers the `command_cli_contract()` catalog hardening only and does not mix in earlier diff-preview or route-catalog branch work.
