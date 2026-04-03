# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Implementation commit(s):
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)

## Reviewer-fix resubmission note
- This fixer pass is docs-only and keeps the handoff on one coherent slice: the `command_cli_contract()` catalog hardening from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- This packet is the reviewer-fix resubmission artifact for the numbered fixes requested on `2026-04-02`, and it resolves them by keeping the handoff canonical, coherent, and limited to the command-catalog slice only.
- This packet was revalidated again on `2026-04-03` after a fresh full gate run in the lane worktree so the reviewer-fix handoff reflects the current branch state.
- The packet does not make any `diff_preview` claims.
- The implementation slice named below is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- Those implementation paths are the live files present at `HEAD` in this worktree.
- The roadmap and vision mappings below are rewritten to the exact canonical labels in this worktree's current `ROADMAP.md` and `PRODUCT_VISION.md`.
- The non-owned test path named in the approval note and in `Files changed` is the same file: `tests/unit/test_commands_catalog.py`.
- The reviewer packet is the source of truth for the required fix list; this resubmission keeps that named shared test path consistent throughout the handoff.
- The handoff mapping in this packet is intentionally limited to the command-contract hardening slice that matches this implementation.
- The required local gates were rerun in this worktree on `2026-04-03` before this handoff was finalized.
- This packet now reflects the completed `2026-04-03` gate rerun order exactly: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Scope goal
- Harden the CLI command contract so `command_cli_contract()` stays deterministic, uses the canonical command order, and fails fast if the parser surface drifts from the catalog.

## Lane/owned paths
- Owned runtime paths from `THREAD_OWNERSHIP.md`: `src/qual/commands/**`
- Approved non-owned test path for this handoff: `tests/unit/test_commands_catalog.py`
- The current `THREAD_OWNERSHIP.md` only marks `src/qual/cli.py` as shared-by-approval for `feat-commands`, so this handoff records `tests/unit/test_commands_catalog.py` separately as the approved non-owned test exception backed by the local scope policy allowlist.

## Scope completed
- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
- Reissued the handoff packet as a command-catalog-only slice so the review scope matches the claimed live implementation files at `HEAD`.

## Kickoff budget/limits compliance
- High-risk shared-file handoff: task budget `4`, time budget `30m`.
- The implementation slice remained limited to one owned command file plus one approved non-owned test file, so the handoff stays within the high-risk budget.

## Approved exception note
- Approved non-owned test exception for `tests/unit/test_commands_catalog.py`.
- This reviewer-fix handoff records that path consistently in the approval note, tasks, files changed list, and scope-check note.

## Scope-policy note
- `tests/unit/test_commands_catalog.py` is the only non-owned implementation file named in this handoff.
- The local scope policy in `scripts/scope-check.sh` explicitly allowlists that same path for `codex/feat-commands*`.
- `THREAD_OWNERSHIP.md` defines the owned runtime path as `src/qual/commands/**`, so this handoff keeps the non-owned test path called out separately instead of presenting it as lane-owned.

## Tasks completed (numbered)
1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Regenerated the packet so the branch metadata stays scoped to the command-catalog slice and uses the current worktree's canonical roadmap and vision labels for re-review.

## Files changed
### Implementation files changed
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py` (approved non-owned test exception; allowlisted by the local scope policy for this lane)

### Docs-only alignment files changed
- `THREAD_PACKET.md`

## Commands run with results
- Revalidated on this reviewer-fix pass in the current worktree.
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
- `Milestone 1: Bootstrap Flow Stabilization (In Progress)` - command behavior hardening includes keeping the CLI command contract deterministic so catalog/parser drift cannot change the surface silently.
- `Milestone 2: Test Hardening (In Progress)` - add focused unit coverage for the command-catalog slice and keep command-level probes for integration confidence.
- `Milestone 3: Product Readiness (Planned)` - define and lock user-facing output contracts by failing fast when parser/catalog drift would otherwise change the command surface implicitly.

### Vision capability affected
- `3. Auditable generation` - command-surface drift now fails explicitly instead of changing the operator-facing contract silently.
- `4. Operator-first control surface` - CLI remains a first-class surface with deterministic canonical ordering and a catalog-backed parser contract.

### Routing/provider impact note
- None. This change only affects local command contract validation and focused command-catalog test coverage.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` (non-owned test coverage only; no integrator-locked implementation files)
- The scope-policy note and `Files changed` section name the same non-owned test path: `tests/unit/test_commands_catalog.py`.
- No integrator-locked file is claimed in the implementation slice.
- `THREAD_OWNERSHIP.md` keeps `src/qual/commands/**` as the lane-owned path for `codex/feat-commands*` and only names `src/qual/cli.py` as shared-by-approval; this packet records `tests/unit/test_commands_catalog.py` separately as the approved non-owned test edit rather than presenting it as lane-owned.
- The current local scope policy in `scripts/scope-check.sh` explicitly allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`, which is the approval basis recorded for this non-owned test path in this worktree.
- This packet's implementation slice is coherent with the `Files changed` list: it is the command-catalog handoff only, not a mixed command-catalog and `diff_preview` handoff.
