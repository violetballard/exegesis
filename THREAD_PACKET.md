# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh commit: `HEAD`
- Packet refresh role: `reviewer-fix packet alignment`

## Packet traceability note

- The current branch tip is a packet-only refresh for reviewer-required handoff alignment.
- Review the command-catalog implementation at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, and treat this packet refresh as metadata-only.
- This refresh does not widen scope beyond the implementation files and behavior already claimed for that commit.

## Current program focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current engine execution order

- 1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
- 2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
- 3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
- 4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
- 5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope goal

- Harden the CLI command contract so `command_cli_contract()` stays deterministic, uses the canonical command order, and fails fast if the parser surface drifts from the catalog.
- Canonical demo-path step advanced: `preview and apply or reject a patch`.
- Why this is first-order MVP work: it keeps the live `diff-preview` / `patch-review` command surface deterministic and smoke-testable while the CLI remains the active operator surface.

## Priority outcomes

1. Keep command behavior deterministic and easy to smoke-test.
2. Prefer thin command entrypoints over embedded business logic.
3. Preserve compatibility with the canonical engine contract while UI lanes stay disabled.

## Definition of done for this lane

- Core engine actions are reachable through stable commands.
- Command behavior is deterministic and smoke-testable.
- Compatibility shims keep old command surfaces working where required.
- Command handlers stay thin and delegate real behavior to engine code.

## Do not spend time on

- Fancy CLI UX that does not support the MVP loop.
- New command flags that do not help open, retrieve, basket, revise, patch, or save.
- Embedding engine behavior directly in command handlers.

## Lane/owned paths

- `src/qual/commands/**`

## Scope completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Preserved the canonical `patch-review` command ordering in the CLI contract by returning the validated canonical names tuple directly.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
- This slice makes the canonical demo-path step `preview and apply or reject a patch` more real by preventing silent drift in the live `diff-preview` CLI contract.
- Reissued the handoff packet as a command-catalog-only slice so the review scope matches the claimed implementation files, demo-path mapping, and approval basis.

## Kickoff budget/limits compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute budget, and the lane size limits.
- The implementation slice stayed limited to one owned command file plus one focused non-owned test file, so the handoff remains narrow and reviewable.

## Approved exception note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`. It is the only non-owned implementation path in this handoff.

## Tasks completed (numbered)

1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on parser drift for the `preview and apply or reject a patch` CLI step.
2. Preserved canonical command ordering in the CLI contract for the live `patch-review` surface by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection on that same `patch-review` command surface.
4. Regenerated the handoff packet so the branch metadata stays scoped to the command-catalog slice and explicitly maps the work to `preview and apply or reject a patch`.

## Files changed

### Reviewed implementation files
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff files
- `THREAD_PACKET.md`

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

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the command-catalog contract deterministic and drift-resistant.
- feat-commands - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable while the command-catalog surface rejects parser drift before it can silently change the operator contract.
- Auditable state and workflow - the command surface now fails loudly on catalog/parser drift, making the operator-facing contract explicit and traceable.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused command-catalog test coverage.

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
