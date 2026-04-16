# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Review target: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh commit: `fb6bf44449c4ad1ecb6b5fee6cd51abfe5d57283`
- Packet refresh role: `metadata-only reviewer-fix finalization`

## Review Basis

- This packet follows the reviewer packet exactly and keeps the approval basis limited to the reviewed implementation slice at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Later packet-refresh commits are treated as metadata-only for this handoff.
- Reviewer-required packet fixes addressed here:
  - add the explicit canonical demo-path mapping required by `AGENTS.md`
  - tighten the scope statement from generic CLI compatibility to the concrete operator-visible path it hardens
  - keep the approval basis limited to the original reviewed implementation slice

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Harden the CLI command contract so `command_cli_contract()` stays deterministic, preserves canonical command order, and fails fast if the parser surface drifts from the catalog.
- This slice specifically hardens the deterministic CLI contract for the current operator-visible path covering `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and `save/export handoff`.

## Canonical Demo-Path Mapping

- Explicit canonical demo-path steps advanced by this slice:
  - `open project/document`
  - `retrieve relevant material`
  - `preview and apply or reject a patch`
  - `save/export handoff`
- Concrete MVP impact: the CLI-first operator surface for those steps remains deterministic because the parser-facing command catalog now stays aligned with the canonical command order and rejects silent parser/catalog drift.
- Scope control: this slice does not add new workflow behavior; it only hardens the existing CLI compatibility contract used by the current engine-first MVP path.

## Definition Of Done Alignment

- Core engine actions remain reachable through stable commands.
- Command behavior remains deterministic and smoke-testable.
- Compatibility with the canonical engine contract is preserved while UI lanes stay disabled.
- Command handlers remain thin; this slice only tightens command-catalog contract validation.

## Lane / Ownership

- Owned runtime path: `src/qual/commands/**`
- Approved shared-test path: `tests/unit/test_commands_catalog.py`
- Shared/integrator-locked edits: `YES`
- Shared edit is limited to `tests/unit/test_commands_catalog.py`, the approved `feat-commands` shared-test path.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Kept the returned CLI contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
- Refreshed the handoff packet so the review scope, canonical demo-path mapping, and approval basis match the reviewed implementation slice.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on parser drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Regenerated the handoff packet so the branch metadata stays scoped to the reviewed command-catalog slice and names the exact canonical demo-path steps it advances.

## Kickoff Budget / Limits Compliance

- High-risk/shared-file handoff: stayed within the `4`-task cap, `30m` budget, and lane size limits.
- The implementation slice stayed limited to one owned command file plus one approved shared test file, so the handoff remains narrow and reviewable.

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

- Residual risk: low. The change remains confined to command-catalog contract validation and focused regression coverage.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` by preserving CLI compatibility for the current engine-first MVP loop.
- `feat-commands` by keeping the command-catalog contract deterministic and migration-safe for the CLI-first operator path.

### Vision capability affected

- `Canonical engine contract` because the CLI compatibility surface remains stable while Textual stays disabled.
- `Auditable state and workflow` because parser/catalog drift now fails loudly instead of silently changing the operator-facing contract.

### Routing/provider impact note

- None. This change only affects local command-contract validation and focused command-catalog test coverage.

### Proposed README.md patch text

- None.
