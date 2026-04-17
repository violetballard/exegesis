# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Reviewed implementation commit: `b644f9ce04a7037ce96f3fe3790f338f03940520`
- Packet refresh role: `reviewer-fix scope/traceability refresh`

## Packet Traceability Note

- The reviewed implementation scope remains the real command change at `b644f9ce04a7037ce96f3fe3790f338f03940520`.
- That implementation commit is not metadata-only: it captures the parser-ready retrieval shim hardening layered on top of the earlier command-shim contract work in this branch.
- The current branch tip is a metadata-only packet refresh that exists only to correct the review traceability, parser-surface scope statement, and roadmap/vision mapping around that reviewed implementation tip.
- The approved shared-test exception remains limited to `tests/unit/test_commands_catalog.py`, the exact `feat-commands` shared-test path recorded in `scripts/scope-check.sh`.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Stabilize the canonical demo-path retrieval CLI shims so retrieval aliases export parser-ready argv and the declared parser surface stays deterministic under the smoke contract.

## Priority Outcomes

1. Keep command behavior deterministic and easy to smoke-test.
2. Prefer thin command entrypoints over embedded business logic.
3. Preserve compatibility with the canonical engine contract while UI lanes stay disabled.

## Canonical Demo-Path Mapping

- Single canonical demo-path step advanced: `retrieve relevant material`.
- Why this exact step: the reviewed implementation only tightens the retrieval shim/export contract and the command-catalog parser-surface validation around parser-ready retrieval invocations; it does not claim new behavior for `open project/document`, `preview and apply or reject a patch`, or `save and continue`.
- AGENTS alignment statement: this slice makes `retrieve relevant material` more real by exporting parser-ready retrieval shim argv for surface tokens like `retrieval` and `retrieve`, then validating both those shim invocations and the declared parser entrypoint mapping so the retrieval CLI fallback cannot silently drift.
- Concrete blocker removed for that step: before this slice, retrieval aliases could be advertised without exporting the parser-ready `context-basket list` invocation they actually need, and parser-surface drift checks were too weak to describe that exact contract. The reviewed implementation makes the retrieval parser entrypoint explicit, smoke-testable, and drift-resistant.
- Why this is not second-order work: the current MVP loop depends on a stable CLI fallback while Textual remains disabled, and `retrieve relevant material` is one of the canonical demo-path steps. Tightening the exported shim contract for that exact step removes a concrete smoke-test blind spot instead of broadening the command surface.

## Definition of Done for This Lane

- Core engine actions are reachable through stable commands.
- Command behavior is deterministic and smoke-testable.
- Compatibility shims keep old command surfaces working where required.
- Command handlers stay thin and delegate real behavior to engine code.

## Do Not Spend Time On

- Fancy CLI UX that does not support the MVP loop.
- New command flags that do not help open, retrieve, basket, revise, patch, or save.
- Embedding engine behavior directly in command handlers.

## Lane / Owned Paths

- `src/qual/commands/**`

## High-Risk Rationale

- This handoff uses the high-risk template because it tightens the public CLI contract and includes `tests/unit/test_commands_catalog.py`, the shared test explicitly approved for `codex/feat-commands` in `scripts/scope-check.sh`.
- Scope remains narrow: command-catalog demo-path shim metadata and validation only.
- Non-goals confirmed: no engine logic changes, no routing/provider changes, and no broader CLI UX expansion.

## Scope Completed

- Extended `CommandDemoPathEntry` in `src/qual/commands/catalog.py` with `surface_invocations` so the canonical demo-path contract exposes the parser-ready argv produced for every surface token in each flow step.
- Hardened `_validate_command_demo_path_contract()` so the demo-path contract rejects drift between the advertised surface tokens and the exported shim invocation table.
- Hardened `command_cli_contract()` so it validates the declared CLI entrypoint mapping and rejects parser-surface drift instead of checking only canonical command-order alignment.
- Added per-command `surface_argv` and taught `command_cli_shim_catalog()` to export parser-ready default argv, so retrieval aliases now map to `context-basket list` instead of a bare `context-basket` token.
- Pinned terminal shim `--operation-kind` defaults and normalized repeated explicit shim options so compatibility shims for `persist`, `apply-patch`, and `reject-patch` stay deterministic while the retrieval step remains parser-ready.
- Expanded regression coverage in `tests/unit/test_commands_catalog.py` for parser-surface drift rejection, retrieval shim argv, terminal shim pinning, duplicate option normalization, and demo-path surface invocation export.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute budget, and the lane size limits.
- The reviewed implementation slice stayed limited to one owned command file plus one focused non-owned test file.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`; approval source: `scripts/scope-check.sh` records that exact file as the allowed shared test for `codex/feat-commands`.
- It is the only non-owned implementation path in the reviewed implementation commit.

## Tasks Completed

1. Added demo-path contract support for explicit surface-token invocation mappings and drift validation.
2. Hardened the command catalog so declared CLI entrypoints reject parser-surface drift instead of relying on canonical-name order alone.
3. Made retrieval aliases export parser-ready `context-basket list` argv and pinned terminal shim operation kinds so adjacent compatibility shims stay deterministic.
4. Refreshed the handoff packet so the reviewed implementation commit, demo-path scope, and traceable shared-test approval reference match the actual branch state.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff files

- `THREAD_PACKET.md`

## Commands Run and Outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / Blockers

- Risk: `LOW`
- Residual risk rationale: the change is limited to command-contract metadata and tests, and the new assertions only tighten the deterministic parser/shim surface already exercised by the existing command catalog.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` - strengthens the canonical demo-path step `retrieve relevant material` by making its retrieval CLI shim surface parser-ready and verifiable while Textual remains disabled.
- `feat-commands` - keeps the migration-safe CLI entrypoints for that retrieval step deterministic and smoke-testable inside the engine-first MVP loop.

### Vision capability affected

- `Canonical engine contract` - the exported demo-path contract now includes the parser-ready retrieval shim invocations for `retrieve relevant material`, keeping that CLI compatibility surface explicit instead of implicit while Textual remains disabled.
- `Retrieval-first context handling` - retrieval aliases now normalize to the parser-ready `context-basket list` entrypoint instead of a bare command token, keeping the FTS-first context surface deterministic and auditable for CLI smoke paths.

### Routing/provider impact note

- None. This change only affects local command-contract metadata and focused command-catalog test coverage.
