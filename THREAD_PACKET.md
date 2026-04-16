# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Review target: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Implementation commits in scope:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` - `feat(commands): lock CLI contract to command catalog`
- Packet refresh commit: pending current final handoff commit
- Packet refresh role: `reviewer-fix finalization`

## Packet Traceability Note

- This packet is intentionally scoped to the reviewed command-catalog implementation at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Later packet-refresh commits are metadata-only for re-review and do not broaden the implementation scope.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Harden the CLI command contract so `command_cli_contract()` stays deterministic, uses the canonical command order, and fails fast if the parser surface drifts from the catalog.

## Canonical Demo-Path Mapping

- Explicit canonical demo-path step advanced by this change: `preview and apply or reject a patch`.
- Concrete blocker removed: the patch-review command surface now rejects parser/catalog drift before the CLI contract can silently change, which keeps the operator-facing patch-review step deterministic and auditable while Textual remains disabled.

## Definition Of Done Alignment

- Core engine actions remain reachable through stable commands.
- Command behavior remains deterministic and smoke-testable.
- Compatibility with the canonical engine contract is preserved while UI lanes stay disabled.
- Command handlers remain thin and delegate real behavior to engine code.

## Lane / Ownership

- Owned runtime paths: `src/qual/commands/**`
- Approved shared-test path:
  - `tests/unit/test_commands_catalog.py`
- Shared/integrator-locked edits: `YES`
- Shared edits are limited to the approved `feat-commands` shared-test path listed above.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
- Regenerated the handoff packet so re-review stays scoped to the command-catalog implementation commit.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on parser drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Regenerated the handoff packet so the branch metadata stays scoped to the command-catalog slice and includes the required canonical demo-path mapping.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the `4`-task cap, `30m` budget, and the lane size limits.
- The implementation slice remained limited to one owned command file plus one approved shared test file, so the handoff remains narrow and reviewable.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff file

- `THREAD_PACKET.md`

## Commands Run With Results

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / Blockers

- Residual risk: low; this slice stays confined to CLI command-contract validation and focused regression coverage.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` by preserving CLI compatibility while the package/layout migration lands.
- `feat-commands` by keeping migration-safe command entrypoints deterministic and drift-resistant for the engine-first MVP loop.

### Vision capability affected

- `Canonical engine contract` because the CLI compatibility surface remains stable while Textual stays disabled.
- `Auditable state and workflow` because the command surface now fails loudly on parser/catalog drift instead of silently changing the operator contract.

### Routing/provider impact note

- None. This change only affects local command-contract validation and focused command-catalog test coverage.

### Proposed README.md patch text

- None.
