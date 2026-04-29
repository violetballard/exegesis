# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: actual `codex/feat-commands` branch tip after the `20260429T024425Z` reviewer-fix pass.
- Previous implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Reviewer packet addressed: `20260429T024425Z`

## Packet Traceability Note

- Review the actual branch tip, not the narrow `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice.
- Commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are implementation-bearing, test-bearing, and metadata-bearing; they are included in this review basis.
- The branch-tip review basis includes command package exports, command-catalog contract validation, diff-preview command behavior, focused command tests, focused diff-preview tests, and this handoff metadata.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - persistence floor for document, basket, vault, and session state.
2. `feat-commands` - stable CLI control surface for the engine-first MVP loop.
3. `feat-retrieval-fts` - authoritative FTS-first retrieval feeding the engine loop.
4. `feat-engine-runs` - close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Harden the CLI command contract so `command_cli_contract()` stays deterministic, uses the canonical command order, and fails fast if the parser-visible surface drifts from the command catalog.

## Priority Outcomes

1. Keep command behavior deterministic and easy to smoke-test.
2. Prefer thin command entrypoints over embedded business logic.
3. Preserve compatibility with the canonical engine contract while UI lanes stay disabled.

## Definition Of Done For This Lane

- Core engine actions are reachable through stable commands.
- Command behavior is deterministic and smoke-testable.
- Compatibility shims keep old command surfaces working where required.
- Command handlers stay thin and delegate real behavior to engine code.

## Lane / Owned Paths

- `src/qual/commands/**`

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it validates the exact parser-visible CLI token surface before returning the contract.
- Preserved canonical command ordering by keeping `CommandCliContract.canonical_names` aligned with `command_names()`.
- Rejected parser/catalog drift across canonical tokens, grouped parser surface, declared surface, lookup-table shape, lookup-table order, and canonical command order.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for same-canonical parser drift, including `bootstrap` -> `open`, `diff-preview` -> `diff`, and `diff` -> `diff_preview`.
- Kept review accounting on the actual branch tip and separated approved shared-by-approval test edits from integrator-locked edits.

## Canonical Demo-Path Step Advanced

- This command contract hardening makes the CLI smoke path more real for `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch` by guaranteeing parser-visible tokens stay aligned with the command catalog before the contract is returned.
- Protected command steps:
  - `project-open`: `bootstrap` remains the only parser-visible project-open token.
  - `retrieval`: `context-basket` remains the parser-visible basket/retrieval token.
  - `patch-review`: `diff-preview` and compatibility alias `diff` remain the only parser-visible patch-review tokens.
  - `export-handoff`: `terminal` remains the parser-visible export/handoff token.

## Tasks Completed

1. Hardened `command_cli_contract()` to validate exact parser-visible tokens, grouped parser surface, declared surface, lookup-table shape/order, and canonical command order; this protects `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch`.
2. Preserved canonical command ordering by returning names aligned with `command_names()` for `bootstrap`, `diff-preview`, `context-basket`, and `terminal`; this protects deterministic CLI smoke execution for the same demo path.
3. Added regression coverage for same-canonical parser drift, including `bootstrap` -> `open`, `diff-preview` -> `diff`, and `diff` -> `diff_preview`, plus token additions, removals, ordering drift, and lookup-table drift; this protects the `project-open` and `patch-review` command routes from silent parser drift.
4. Regenerated this handoff packet with one branch-tip review basis, explicit demo-path mapping, and unambiguous ownership accounting for shared-by-approval tests versus integrator-locked files.

## Files Changed

### Reviewed Implementation Files

- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

### Metadata-Only Handoff Files

- `THREAD.md`
- `THREAD_PACKET.md`

## Ownership Accounting

- Lane-owned implementation edits: `src/qual/commands/**`.
- Approved shared-by-approval test edits: `tests/unit/test_commands_catalog.py`, `tests/unit/test_diff_preview.py`.
- Shared-by-approval edits: YES.
- Integrator-locked edits: NO.
- Gate-policy edits: NO.

## Required Fixes Addressed From Reviewer Packet `20260429T024425Z`

1. One review basis: this packet uses the actual `codex/feat-commands` branch tip and includes post-`f8d860ed9f6299f0169c4f21321ac5f37c949fd3` implementation/test commits.
2. Parser-surface validation: `command_cli_contract()` validates exact parser-visible tokens and lookup-table shape/order, not only de-duplicated canonical names.
3. Same-canonical regressions: tests cover accepted alias substitution including `diff-preview` -> `diff`, `bootstrap` -> `open`, and `diff` -> `diff_preview`.
4. Demo-path mapping: every completed task names the canonical demo-path command steps it protects or advances.
5. Ownership fields: approved shared-by-approval test edits are separated from integrator-locked edits, and integrator-locked edits are `NO`.
6. Required gates: final results are recorded below after rerun on this branch-tip state.

## Commands Run + Outcomes

- `make scope-check`: PASS for branch `codex/feat-commands`.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS; ran smoke tests and 150 unit tests, including same-canonical parser drift regressions for `bootstrap` -> `open`, `diff-preview` -> `diff`, and `diff` -> `diff_preview`.
- `./typecheck-test.sh`: PASS; compiled Python sources in `src/`.
- `make ci`: PASS; ran scope-check, format, lint, compileall/typecheck, and full quality tests.

## Risks / Blockers

- Risk: `HIGH`, because command-surface contract behavior and shared test coverage are in scope.
- Blockers: none.

## Required Handoff Fields

### Branch Name

- `codex/feat-commands`

### Roadmap Item(s) Affected

- Milestone 3: real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the command-catalog contract deterministic and drift-resistant.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision Capability Affected

- Canonical engine contract - CLI compatibility remains stable while the command-catalog surface rejects parser drift before it can silently change the operator contract.
- Auditable state and workflow - the command surface fails loudly on catalog/parser drift, making the operator-facing contract explicit and traceable.

### Routing / Provider Impact Note

- None. This change only affects local command contract validation and focused command-catalog test coverage.
