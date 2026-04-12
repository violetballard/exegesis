# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Implementation commit(s):
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
- Docs-only alignment commit(s):
  - Current `2026-04-12` reviewer-fix packet refresh in this docs-only commit after rerunning the full required gate sequence in this lane worktree.

## Reviewer-fix resubmission note
- This fixer pass is docs-only and keeps the handoff on one coherent slice: the live `command_cli_contract()` catalog hardening in `src/qual/commands/catalog.py`.
- This packet resolves the reviewer's numbered fixes by describing the actual submitted implementation slice instead of the stale `diff_preview` narrative from the rejected packet.
- The implementation slice named below is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- The roadmap and vision mappings below use the current canonical labels from this worktree's `ROADMAP.md` and `PRODUCT_VISION.md`.
- The non-owned test path named in the approval note and in `Files changed` is the same file: `tests/unit/test_commands_catalog.py`.
- The required local gates were rerun in this worktree on `2026-04-12` before this handoff was finalized, in this order: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Scope goal
- Harden the CLI command contract so `command_cli_contract()` stays deterministic, uses the canonical command order, and fails fast if the parser surface drifts from the catalog.

## Lane/owned paths
- Owned runtime path in this worktree: `src/qual/commands/**`
- Approved non-owned test path for this handoff: `tests/unit/test_commands_catalog.py`

## Scope completed
- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
- Reissued the handoff packet as a command-catalog-only slice so the review scope matches the claimed implementation files and approval basis.

## Kickoff budget/limits compliance
- High-risk shared-file handoff: stayed within `4` tasks, `30m`, and the lane size limits.
- The implementation slice remained limited to one owned command file plus one focused non-owned test file, so the handoff stayed narrow and reviewable.

## Approved exception note
- `tests/unit/test_commands_catalog.py` is the only non-owned implementation file named in this handoff.
- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- This handoff records that path consistently in the task list, files changed list, and scope-check note as the only non-owned implementation edit.

## Scope-policy note
- `tests/unit/test_commands_catalog.py` is the only non-owned implementation file named in this handoff.
- The lane-owned runtime path in this worktree is `src/qual/commands/**`, so this handoff keeps the test path called out separately instead of presenting it as lane-owned.
- The reviewer packet required an explicit approval note for the actual shared test file, and this packet names the same path in the approval note and in `Files changed`.
- This handoff uses the explicit approved exception note in this packet for `tests/unit/test_commands_catalog.py` as the approval basis for the non-owned test edit and does not claim any other exception or local scope-policy expansion.

## Tasks completed (numbered)
1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Regenerated the packet so the branch metadata stays scoped to the command-catalog slice and uses the current worktree's canonical roadmap and product-vision capability names for re-review.

## Files changed
### Implementation files changed
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py` (non-owned test path; explicit approved exception recorded in this handoff)

### Docs-only alignment files changed
- `THREAD_PACKET.md`

## Commands run with results
- Revalidated on this reviewer-fix pass in the current worktree.
- Revalidation date: `2026-04-12`
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
- `Milestone 3: Real workflow loop` - preserve CLI compatibility while the package/layout migration lands by keeping the command-catalog contract deterministic and drift-resistant.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision capability affected
- `Canonical engine contract` - CLI compatibility remains stable while the command-catalog surface rejects parser drift before it can silently change the operator contract.
- `Auditable state and workflow` - the command surface now fails loudly on catalog/parser drift, making the operator-facing contract explicit and traceable.

### Routing/provider impact note
- None. This change only affects local command contract validation and focused command-catalog test coverage.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` (non-owned test path only; no integrator-locked implementation files)
- Non-owned implementation edit recorded explicitly: `tests/unit/test_commands_catalog.py`
- The scope-policy note and `Files changed` section name the same test path: `tests/unit/test_commands_catalog.py`.
- The approved exception note names that same non-owned test path explicitly.
- The approval basis for that non-owned test path is the explicit approved exception note in this handoff.
- No integrator-locked file is claimed in the implementation slice.
- The ownership map in this worktree keeps the lane-owned runtime path at `src/qual/commands/**` and does not present `tests/unit/test_commands_catalog.py` as owned, so this packet records that test path separately as an approved non-owned implementation edit rather than as lane-owned.
- This docs-only reviewer-fix pass does not change `scripts/scope-check.sh` or broaden the current local allowlist; it only records the reviewer packet's approved non-owned test exception for handoff accuracy.
- This packet's implementation slice is coherent with the `Files changed` list: it is the command-catalog handoff only, not a mixed command-catalog and `diff_preview` packet.
