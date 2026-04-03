# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Implementation commit(s):
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)

## Reviewer-fix resubmission note
- This fixer pass is docs-only and keeps the handoff on one coherent slice: the `command_cli_contract()` catalog hardening from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- The packet does not make any `diff_preview` claims.
- The implementation slice named below is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- The roadmap and vision mappings below use the exact labels from the current `ROADMAP.md` and `PRODUCT_VISION.md` in this worktree.
- The non-owned test path named in the approval note and in `Files changed` is the same file: `tests/unit/test_commands_catalog.py`.

## Scope goal
- Harden the CLI command contract so `command_cli_contract()` stays deterministic, uses the canonical command order, and fails fast if the parser surface drifts from the catalog.

## Scope completed
- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
- Reissued the handoff packet as a command-catalog-only slice so the review scope matches the claimed implementation files.

## Kickoff budget/limits compliance
- High-risk shared-file handoff: task budget `4`, time budget `30m`.
- The implementation slice stayed within the budget and remained limited to one owned command file plus one non-owned test file.

## Approved exception note
- Explicit non-owned test-file exception for `tests/unit/test_commands_catalog.py`.
- Approval basis: the local scope policy in `scripts/scope-check.sh` explicitly allows `tests/unit/test_commands_catalog.py` on `codex/feat-commands*`.

## Tasks completed (numbered)
1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Regenerated the packet so the branch metadata stays scoped to the command-catalog slice and uses the current canonical roadmap and vision labels from this worktree.

## Files changed
### Implementation files changed
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py` (explicit non-owned test-file exception for the implementation commit)

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
- `Milestone 1: Bootstrap Flow Stabilization (In Progress)` - command behavior hardening now includes locking the CLI command-catalog contract so parser drift is rejected deterministically.
- `Milestone 2: Test Hardening (In Progress)` - adds focused unit coverage for command-catalog alignment and parser-drift rejection.

### Vision capability affected
- `Operator-first control surface` - CLI remains a first-class operator surface, and this change keeps the exposed command contract deterministic instead of allowing silent parser/catalog drift.

### Routing/provider impact note
- None. This change only affects local command contract validation and focused command-catalog test coverage.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- The only non-owned implementation file named in this packet is `tests/unit/test_commands_catalog.py`.
- The approval note and `Files changed` section name the same non-owned test path.
- No integrator-locked file is claimed in the implementation slice.
- The current local scope policy in `scripts/scope-check.sh` explicitly allows `tests/unit/test_commands_catalog.py` on `codex/feat-commands*`, so this packet records that exact path as the non-owned-file approval note for review.
