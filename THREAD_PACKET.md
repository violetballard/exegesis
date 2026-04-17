# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Reviewed implementation commit: `e724470e3d3305b7f7ec38f1e818602aa6d9485a`
- Packet refresh role: `reviewer-fix scope/traceability refresh`

## Packet Traceability Note

- The reviewed implementation scope is the real branch-tip command change at `e724470e3d3305b7f7ec38f1e818602aa6d9485a`.
- That implementation commit is not metadata-only: it changes `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- This packet refresh commit is metadata-only and exists only to correct the review traceability, scope summary, and roadmap/vision mapping around that implementation commit.
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

- Stabilize the canonical demo-path command shims so the exported demo-path contract reports each surface token's parser-ready invocation and validates that those shim invocations stay aligned with the smoke contract.

## Priority Outcomes

1. Keep command behavior deterministic and easy to smoke-test.
2. Prefer thin command entrypoints over embedded business logic.
3. Preserve compatibility with the canonical engine contract while UI lanes stay disabled.

## Canonical Demo-Path Mapping

- Explicit AGENTS demo-path step advanced: `preview and apply or reject a patch`.
- Supporting CLI-fallback coverage kept explicit for adjacent steps on the same operator path: `open project/document`, `retrieve relevant material`, and `save and continue`.
- AGENTS alignment statement: this slice makes the canonical demo path more real by exposing the exact parser-ready argv generated for each canonical surface token, including the patch-review and export-handoff shims that operators depend on while Textual remains disabled.
- Concrete blocker removed: before this slice, `command_demo_path_contract()` described parser-ready smoke argv for each canonical step, but it did not expose or validate the per-surface shim invocations that map aliases like `patch-review`, `apply-patch`, and `reject-patch` back to the parser entrypoints. This change makes those shim rewrites explicit and testable instead of implicit.

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
- Hardened `_validate_command_demo_path_contract()` so the demo-path contract now rejects drift between the advertised surface tokens and the exported shim invocation table.
- Updated `command_demo_path_contract()` to collect the per-step shim invocations from `command_cli_shim_catalog()` and attach them to each demo-path entry.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` that verifies the parser-ready invocation map for patch-review and export-handoff aliases, including `diff`, `review-patch`, `apply-patch`, and `reject-patch`.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute budget, and the lane size limits.
- The reviewed implementation slice stayed limited to one owned command file plus one focused non-owned test file.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`; approval source: `scripts/scope-check.sh` records that exact file as the allowed shared test for `codex/feat-commands`.
- It is the only non-owned implementation path in the reviewed implementation commit.

## Tasks Completed

1. Added demo-path contract support for explicit surface-token invocation mappings.
2. Validated that demo-path surface invocations stay aligned with the smoke contract surface.
3. Added regression coverage for parser-ready patch-review and export-handoff shim invocations.
4. Refreshed the handoff packet so the reviewed implementation commit, roadmap/vision mapping, and traceable shared-test approval reference match the actual branch state.

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
- Residual risk rationale: the change is limited to command-contract metadata and tests, and the new assertions only tighten the deterministic shim surface already exercised by the existing command catalog.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` - strengthens the canonical demo-path step `preview and apply or reject a patch` by making its CLI shim surface explicit and verifiable while Textual remains disabled.
- `feat-commands` - keeps the migration-safe CLI entrypoints for that demo-path step deterministic and smoke-testable inside the engine-first MVP loop.

### Vision capability affected

- `Canonical engine contract` - the exported demo-path contract now includes the parser-ready shim invocations for `preview and apply or reject a patch`, keeping that CLI compatibility surface explicit instead of implicit.
- `Auditable state and workflow` - the command contract now fails loudly if the advertised demo-path surface tokens for that operator path diverge from the shim invocation table used to drive the CLI-first flow.

### Routing/provider impact note

- None. This change only affects local command-contract metadata and focused command-catalog test coverage.
