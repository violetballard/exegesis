# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Implementation commit(s):
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
- Docs-only alignment commit(s) before this fixer pass:
  - `5f3de6da3017f034d0f5c517c5de41935690ef89` (`docs(commands): record reviewer-fix gate rerun`)
  - `69f4f4a0f010761ffebdb629ab74bd1e9256b9d4` (`docs(commands): tighten reviewer-fix handoff packet`)

## Reviewer-fix resubmission note
- This fixer pass is docs-only and addresses the reviewer's required fixes by keeping the packet on one coherent command-catalog slice, using the exact roadmap and vision labels from this worktree, and naming the actual approved shared test consistently.
- This resubmission reran the required local gates on `2026-04-02` so the packet's pass/fail claims match the current branch head for this fixer commit.
- The reviewed implementation slice remains commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, with `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py` as the only implementation files claimed by this re-review.

## Scope goal
- Harden the CLI command contract so `command_cli_contract()` stays deterministic, uses the canonical command order, and fails fast if the parser surface drifts from the catalog. This keeps the CLI-first MVP surface stable while the engine contract settles.

## Scoped review slice
- This re-review packet is intentionally scoped to implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` only.
- Earlier branch groundwork such as `src/qual/commands/__init__.py` remains in the branch delta from prior command-surface work, but it is not part of the required-fix slice being re-submitted here.
- This packet does not re-submit any `diff_preview` implementation or `tests/unit/test_diff_preview.py` coverage; the coherent review slice is the command-catalog contract only.

## Lane/owned paths
- `src/qual/commands/**`
- Approved shared tests:
  - `tests/unit/test_commands_catalog.py`

## Scope completed
- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares the CLI lookup-table canonical names against `command_names()` and raises `ValueError` when the catalog and parser surface drift.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for the canonical-name alignment path and the drift rejection path.
- Kept this handoff scoped to the `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` command-catalog implementation slice only; it does not re-describe earlier route-catalog or diff-preview work on the branch.
- Kept docs-only packet alignment separate from the implementation commit so this re-review remains tied to the command-catalog slice instead of accumulating unrelated metadata history.

## Kickoff budget/limits compliance
- High-risk shared-file handoff: task budget `4`, time budget `30m`.
- The submitted branch stays within lane-owned command code plus the approved `tests/unit/test_commands_catalog.py` shared test exception.

## Approved exception note
- Approved shared-file exception for `tests/unit/test_commands_catalog.py`.
- No other shared-by-approval path is claimed in this re-review packet.

## Tasks completed (numbered)
1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Regenerated and tightened the packet so the branch metadata stays scoped to the command-catalog slice and uses canonical roadmap and vision labels without depending on a long stale docs-only commit ledger.

## Files changed
### Implementation files changed
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py` (approved shared-file exception for the implementation commit)
### Docs-only alignment files changed
- `THREAD_PACKET.md`

## Scope boundary note
- This packet re-submits only the `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` command-catalog implementation slice plus docs-only alignment at the current head.
- It does not claim earlier branch groundwork as part of the reviewed implementation files for this re-review.
- It does not claim any `diff_preview` implementation or `tests/unit/test_diff_preview.py` coverage in this re-review packet.

## Commands run and outcomes
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS
- Verification date: `2026-04-02`

## Risks / blockers
- Risk: `HIGH`
- Blockers: none

## Required handoff fields
### Scope completed
- CLI command compatibility now has a deterministic canonical-name contract so the parser surface cannot silently drift from the command catalog.

### Roadmap item(s) affected
- `Milestone 1: Bootstrap Flow Stabilization (In Progress)` - command behavior hardening for the CLI surface.
- `Milestone 2: Test Hardening (In Progress)` - focused unit coverage for the command-catalog drift checks added in this slice.

### Vision capability affected
- `Operator-first control surface` - CLI remains a first-class surface, and the command catalog now rejects silent parser/catalog drift before it can affect operators.
- `Auditable generation` - the deterministic CLI contract makes parser/catalog drift explicit instead of leaving the operator surface to fail ambiguously.

### Routing/provider impact note
- None. This change only affects local command contract validation and focused command-catalog test coverage.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Approved shared-file exception covers `tests/unit/test_commands_catalog.py`, which is also the only shared test named in `Files changed`.
- Approval basis: `scripts/scope-check.sh` explicitly permits `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`, and this packet only claims that one non-owned test file.
- Re-review mapping basis: the roadmap and vision fields above use the exact canonical milestone and capability names from this worktree's `ROADMAP.md` and `PRODUCT_VISION.md` for this command-contract handoff slice.
- Coherent-slice basis: this re-review packet covers the `command_cli_contract()` catalog hardening only and does not mix in earlier diff-preview or route-catalog branch work.
