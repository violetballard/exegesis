# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Review target: current branch tip
- Implementation commits in scope:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` - `feat(commands): lock CLI contract to command catalog`
  - `4c5bc5386b48bdf9429530d17b7353562592e7ff` - `Fix diff preview summary fingerprint contract`
- Packet refresh commit: pending current handoff refresh
- Packet refresh role: `reviewer-fix packet regeneration`

## Review Basis

- This packet is regenerated against the actual merge candidate on `codex/feat-commands`, not a single earlier implementation commit.
- The branch includes two implementation slices in `src/qual/commands/**`:
  - deterministic `command_cli_contract()` validation in the command catalog
  - diff-preview fingerprint hardening so summary-only output still fingerprints the reviewed diff payload
- Reviewer-required packet fixes addressed here:
  - correct the traceability story so the handoff matches the real branch tip
  - include the full implementation scope, files, tasks, and shared-file approvals
  - state the exact canonical demo-path step this branch makes more real

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Harden the CLI command surface so catalog-backed command routing stays deterministic and smoke-testable for the current engine-first MVP loop.
- Keep diff-preview output auditable by ensuring summary-only fingerprint reporting still identifies the reviewed diff payload rather than the collapsed emitted text.

## Canonical Demo-Path Mapping

- Explicit canonical demo-path step advanced by this branch: `preview and apply or reject a patch`.
- Concrete blocker removed: the CLI-facing command contract now rejects parser/catalog drift, and the `diff-preview` summary-only surface now fingerprints the reviewed diff payload, so patch-review commands stay deterministic and auditable for the current operator path.
- Secondary covered steps through the stable command surface:
  - `open project/document`
  - `retrieve relevant material`
  - `save/export handoff`

## Definition Of Done Alignment

- Core engine actions remain reachable through stable commands.
- Command behavior remains deterministic and smoke-testable.
- Compatibility with the canonical engine contract is preserved while UI lanes stay disabled.
- Command handlers remain thin; both changes stay in command-surface validation or presentation integrity rather than embedded engine business logic.

## Lane / Ownership

- Owned runtime paths: `src/qual/commands/**`
- Approved shared-test paths:
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
- Shared/integrator-locked edits: `YES`
- Shared edits are limited to the approved `feat-commands` shared-test paths listed above.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Kept the returned CLI contract aligned with canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Updated `src/qual/commands/diff_preview.py` so summary-only fingerprint reporting hashes the reviewed diff payload, while non-summary output still fingerprints the emitted rendered diff.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` for command-order drift rejection and summary-only fingerprint correctness.
- Regenerated the handoff packet so the review scope and handoff fields match the actual branch tip.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on parser drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Fixed summary-only diff fingerprinting so the command still identifies the reviewed diff payload when the rendered output is collapsed.
4. Added focused regression coverage for both the catalog contract and the diff-preview fingerprint contract.

## Kickoff Budget / Limits Compliance

- High-risk/shared-file handoff: stayed within the `4`-task cap, `30m` budget, and lane size limits for this reviewed slice.
- Implementation remained confined to two owned command files plus two approved shared test files, keeping the branch narrow enough for review.

## Files Changed

### Implementation files

- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

### Metadata-only handoff file

- `THREAD_PACKET.md`

## Commands Run With Results

- `make scope-check`: FAIL - rejected `tests/unit/test_diff_preview.py` as a disallowed shared-file change on `codex/feat-commands`.
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: FAIL - stops at the same `scope-check` rejection for `tests/unit/test_diff_preview.py`.

## Risks / Blockers

- Residual risk: low in the code paths touched; the branch remains confined to CLI command-surface determinism and diff-preview output integrity.
- Blocker: `scripts/scope-check.sh` currently allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands` but not `tests/unit/test_diff_preview.py`, so `make scope-check` and `make ci` fail even though the handoff treats that test file as an approved shared path.

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` by preserving CLI compatibility while the package/layout migration lands.
- `feat-commands` by keeping migration-safe command entrypoints deterministic and auditable for the engine-first MVP loop.

### Vision capability affected

- `Canonical engine contract` because the CLI compatibility surface remains stable while Textual stays disabled.
- `Auditable state and workflow` because both parser/catalog drift and summary-only diff fingerprint reporting now fail or report in ways that keep the operator-facing contract explicit.

### Routing/provider impact note

- None. This branch only affects local command-surface validation and diff-preview output integrity.

### Proposed README.md patch text

- None.
