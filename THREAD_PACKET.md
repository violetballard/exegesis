# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: actual `codex/feat-commands` branch tip after the `20260429T032302Z` reviewer-fix pass.
- Previous implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Reviewer packet addressed: `20260429T032302Z`
- Final verifier tip: the branch-tip reviewer-fix commit containing this packet restamp, with the actual `codex/feat-commands` branch tip as the only review basis.

## Packet Traceability Note

- Review the actual branch tip, not the narrow `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice.
- Commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are implementation-bearing, test-bearing, and metadata-bearing; they are included in this review basis.
- The effective changed-file list from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` to the final branch tip is the file list in this packet. `scripts/scope-check.sh` is included as a gate-policy cleanup file because this fixer pass removes prior scope-policy additions from the final branch state.
- The branch-tip review basis includes command-catalog contract validation, focused command-catalog tests, and this handoff metadata.

## Effective Review Diff From Previous Anchor

- `THREAD.md`
- `THREAD_PACKET.md`
- `scripts/scope-check.sh`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Post-Anchor Implementation / Metadata Accounting

- Implementation-bearing effective files after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`: `src/qual/commands/catalog.py`, `tests/unit/test_commands_catalog.py`.
- Metadata-bearing effective files after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`: `THREAD.md`, `THREAD_PACKET.md`.
- Gate-policy cleanup file after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`: `scripts/scope-check.sh`; the final branch state removes prior scope-policy additions instead of relying on them for this lane.
- Branch-tip commit list is intentionally reviewed through the effective diff above because the post-anchor history contains many repeated metadata restamps. The review basis is still the actual branch tip, and the changed-file list is complete for that basis.

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
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for same-canonical parser drift, including self-consistent parser replacements for `bootstrap` -> `open` and `diff-preview` -> `diff`, plus `diff` -> `diff_preview`.
- Removed prior `scripts/scope-check.sh` gate-policy additions from the final branch state so the command lane no longer depends on a scope-policy expansion.
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
3. Added regression coverage for same-canonical parser drift, including self-consistent parser replacements for `bootstrap` -> `open` and `diff-preview` -> `diff`, plus `diff` -> `diff_preview`, token additions, removals, ordering drift, and lookup-table drift; this protects the `project-open` and `patch-review` command routes from silent parser drift.
4. Regenerated this handoff packet with one branch-tip review basis, explicit demo-path mapping, and unambiguous ownership accounting for shared-by-approval tests versus integrator-locked files.

## Files Changed

### Reviewed Implementation Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-Only Handoff Files

- `THREAD.md`
- `THREAD_PACKET.md`

### Gate-Policy Cleanup File

- `scripts/scope-check.sh`

## Ownership Accounting

- Lane-owned implementation edits: `src/qual/commands/**`.
- Approved shared-by-approval test edits: `tests/unit/test_commands_catalog.py`.
- Shared-by-approval edits: YES.
- Integrator-locked edits: NO.
- Gate-policy cleanup edits: YES, limited to removing prior `scripts/scope-check.sh` scope-policy additions from the final branch state.
- Gate-policy approval / risk rationale: approved as a cleanup-only fixer change required by reviewer traceability; it narrows the final branch policy surface rather than expanding command-lane permissions, and `scripts/scope-check.sh` is not listed as integrator-locked in `THREAD_OWNERSHIP.md`.

## Required Fixes Addressed From Reviewer Packet `20260429T025119Z`

1. One review basis: this packet uses the actual `codex/feat-commands` branch tip and includes post-`f8d860ed9f6299f0169c4f21321ac5f37c949fd3` implementation/test commits.
2. Parser-surface validation: `command_cli_contract()` validates exact parser-visible tokens and lookup-table shape/order, not only de-duplicated canonical names.
3. Same-canonical regressions: tests cover accepted alias substitution including self-consistent `diff-preview` -> `diff` and `bootstrap` -> `open` replacements, plus `diff` -> `diff_preview`.
4. Demo-path mapping: every completed task names the canonical demo-path command steps it protects or advances.
5. Ownership fields: approved shared-by-approval test edits are separated from integrator-locked edits, and integrator-locked edits are `NO`.
6. Required gates: final results are recorded below after rerun on this branch-tip state for the current reviewer packet.

## Required Fixes Addressed From Reviewer Packet `20260429T025923Z`

1. One review basis: this packet uses the actual final `codex/feat-commands` branch tip.
2. Complete changed-file accounting: the effective review diff from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` contains `THREAD.md`, `THREAD_PACKET.md`, `scripts/scope-check.sh`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
3. Scope policy removal: `scripts/scope-check.sh` is listed as a cleanup-only gate-policy edit because this fixer pass removes prior scope-policy additions from the final branch state.
4. Demo-path mapping: every completed task names the canonical demo-path command steps it protects or advances.
5. Required gates: final results are recorded below after rerun on the same final branch-tip review basis named in this packet.

## Required Fixes Addressed From Reviewer Packet `20260429T030236Z`

1. One truthful review basis: this packet uses the actual final `codex/feat-commands` branch tip, not the narrow `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` implementation slice.
2. Complete changed-file accounting: the effective review diff from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` contains `THREAD.md`, `THREAD_PACKET.md`, `scripts/scope-check.sh`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
3. Packet refresh claim corrected: no post-anchor commit is described as metadata-only unless it is metadata-only in the final branch-tip review basis; post-anchor implementation and test changes are included in the review basis.
4. Ownership accounting corrected: `tests/unit/test_commands_catalog.py` is treated as an approved shared-by-approval test edit, integrator-locked edits are `NO`, and `scripts/scope-check.sh` is explicitly called out as a cleanup-only gate-policy edit with approval/risk rationale.
5. Required gates: final results are recorded below after rerun on the same final branch-tip review basis named in this packet.

## Required Fixes Addressed From Reviewer Packet `20260429T030532Z`

1. Exact parser-visible validation: `command_cli_contract()` validates declared CLI tokens, `_CLI_ENTRYPOINTS`, grouped parser surface, lookup-table shape/order, and canonical-name order so same-canonical substitutions, additions, removals, and ordering changes raise.
2. Regression coverage: `tests/unit/test_commands_catalog.py` patches `_CLI_ENTRYPOINTS` for `bootstrap` -> `open`, `diff-preview` -> `diff`, token removal, token addition, and token order drift, with additional lookup-table and declared-surface drift coverage.
3. Truthful review basis: this handoff uses the actual final `codex/feat-commands` branch tip and lists `scripts/scope-check.sh` as a cleanup-only gate-policy file instead of treating it as metadata.
4. Demo-path mapping: every completed task names the canonical demo-path command steps it protects or advances.
5. Required gates: final results are recorded below after rerun on the same final branch-tip review basis named in this packet.

## Required Fixes Addressed From Reviewer Packet `20260429T030847Z`

1. One truthful review basis: this packet uses the actual final `codex/feat-commands` branch tip after this fixer pass, not the narrow `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` implementation slice.
2. False metadata-only claim removed: post-anchor implementation and test changes are included in the branch-tip review basis, and only `THREAD.md` / `THREAD_PACKET.md` are described as metadata-only handoff files.
3. Complete changed-file accounting: the effective review diff from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` contains `THREAD.md`, `THREAD_PACKET.md`, `scripts/scope-check.sh`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
4. Demo-path mapping: every completed task names the canonical demo-path command steps it protects or advances, including project open, retrieval/context basket, patch preview/apply/reject, and export/handoff.
5. Ownership accounting split: lane-owned command edits, approved shared-by-approval test edits, integrator-locked edits, and cleanup/policy edits are reported separately.
6. Required gates: final results are recorded below after rerun on the same final branch-tip review basis named in this packet.

## Required Fixes Addressed From Reviewer Packet `20260429T031136Z`

1. Exact parser-visible validation is present in `command_cli_contract()`: it checks canonical CLI tokens, declared grouped surface, lookup-table shape/order, parser token order, and canonical-name order before returning the contract.
2. Regression coverage is present for same-canonical substitutions such as `bootstrap` -> `open`, `diff-preview` -> `diff`, and `diff` -> `diff_preview`, plus token additions, removals, ordering drift, lookup-table drift, and declared-surface drift.
3. Demo-path mapping is explicit: the hardened command contract protects project/document open, retrieval/context basket, patch preview/apply/reject, and export/handoff smoke steps.
4. Ownership accounting is split between lane-owned command edits, approved shared-by-approval test edits, integrator-locked edits, and cleanup/policy edits.
5. Required gates are recorded below after rerun on the same final branch-tip review basis named in this packet.

## Required Fixes Addressed From Reviewer Packet `20260429T031430Z`

1. One truthful review basis: this packet uses the actual final `codex/feat-commands` branch tip after this fixer pass, not the narrow `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` implementation slice.
2. Complete changed-file accounting: the effective review diff from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` contains `THREAD.md`, `THREAD_PACKET.md`, `scripts/scope-check.sh`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
3. Gate-policy accounting: `scripts/scope-check.sh` is listed as a cleanup-only gate-policy file; the packet documents why it remains in the effective review diff and states that it narrows prior scope-policy additions instead of expanding command-lane authority.
4. Ownership accounting split: shared-by-approval test edits are reported separately from integrator-locked edits; integrator-locked edits are `NO`.
5. Demo-path mapping: every completed task names the canonical demo-path command steps it protects or advances, including project open, retrieval/context basket, patch preview/apply/reject, and export/handoff.
6. Required gates: final results are recorded below after rerun on the same final branch-tip review basis named in this packet.

## Required Fixes Addressed From Reviewer Packet `20260429T031719Z`

1. One truthful review basis: this packet uses the actual final `codex/feat-commands` branch tip after this fixer pass, not the narrow `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` implementation slice.
2. Exact parser-visible validation: `command_cli_contract()` validates expected CLI tokens, lookup-table shape/order, grouped canonical surface, declared grouped surface, and canonical-name order before returning the contract.
3. Regression coverage: tests include same-canonical parser drift for `bootstrap` -> `open`, `diff-preview` -> `diff`, and `diff` -> `diff_preview`, plus token removal, addition, reordering, lookup-table substitution, and lookup-table ordering drift.
4. Demo-path mapping: every completed task names the canonical demo-path command steps it protects or advances, including project open, retrieval/context basket, patch preview/apply/reject, and export/handoff.
5. Required gates: final results are recorded below after rerun on the same final branch-tip review basis named in this packet.

## Required Fixes Addressed From Reviewer Packet `20260429T032011Z`

1. One truthful review basis: this packet uses the actual final `codex/feat-commands` branch tip after this fixer pass, not the narrow `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` implementation slice.
2. Complete effective changed-file accounting: the review diff from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` through the final branch tip includes `THREAD.md`, `THREAD_PACKET.md`, `scripts/scope-check.sh`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
3. Gate-policy accounting: `scripts/scope-check.sh` is documented as a cleanup-only gate-policy file because the final branch state removes prior scope-policy additions instead of expanding command-lane authority.
4. Ownership accounting: shared-by-approval test edits are separated from integrator-locked edits, and integrator-locked edits are `NO`.
5. Demo-path mapping: every completed task stays scoped to Milestone 3 CLI compatibility and names the canonical demo-path command steps it protects, including project/document open, retrieval/context basket, patch preview/apply/reject, and save/continue support through the CLI operator surface.
6. Required gates: final results are recorded below after rerun on the same final branch-tip review basis named in this packet.

## Required Fixes Addressed From Reviewer Packet `20260429T032302Z`

1. One review basis: this packet uses the actual final `codex/feat-commands` branch tip after this fixer pass, and does not describe implementation-bearing commits as metadata-only.
2. Complete changed-file accounting: the effective review diff from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` through the final branch tip includes `THREAD.md`, `THREAD_PACKET.md`, `scripts/scope-check.sh`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
3. Exact parser-visible validation: `command_cli_contract()` validates token additions, removals, replacements, ordering, lookup-table substitutions, lookup-table ordering, grouped surface drift, declared surface drift, and canonical-name ordering before returning the contract.
4. Same-canonical drift coverage: tests lock replacements and aliases including `bootstrap` -> `open`, `diff-preview` -> `diff`, and `diff` -> `diff_preview`, plus token additions/removals/reordering and lookup-table drift.
5. Demo-path mapping: every completed task names the canonical demo-path steps protected by this command-catalog work, including project/document open, retrieval/context basket, patch preview/apply/reject, and export/handoff.

## Commands Run + Outcomes

- `make scope-check`: PASS for branch `codex/feat-commands`.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS; ran smoke tests and 152 unit tests, including same-canonical parser drift regressions for `bootstrap` -> `open`, `diff-preview` -> `diff`, and `diff` -> `diff_preview`.
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
