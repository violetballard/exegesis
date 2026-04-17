# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `1bf99c36f9a8759c043b314b6b9d84b534048334`
- Packet refresh role: `feature-fixer implementation-aligned reviewer-fix verification and gate rerun`

## Packet Traceability Note

- The implementation commit above refers to the current runtime fix commit for this lane, which carries the reviewer-required command-surface hardening and the current default `demo` / `mvp` command-flow contract on branch tip.
- This packet refresh keeps the handoff wording aligned with the current implementation and records the final required gate rerun for the reviewer-fix branch tip.
- Final verification refresh: re-ran the required gate suite on April 16, 2026 (America/Los_Angeles) after confirming the reviewer-required demo-path alignment is still present on this branch tip.
- Feature-fixer verification refresh: re-ran `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` on April 16, 2026 (America/Los_Angeles) to attach a fresh fixer commit to the reviewer-required packet alignment.
- Reviewer-fix follow-up scope: this refresh keeps the packet aligned with the actual branch tip, where the default `demo` / `mvp` command-flow helpers still cover `project-open`, `retrieval`, `patch-review`, and `export-handoff`, and where the reviewer-required fix is the explicit demo-path mapping in the handoff itself.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Harden the CLI command contract so `command_cli_contract()` stays deterministic, preserves the canonical command order for exposed commands, fails fast when the default parser surface drifts from the declared command catalog, and keeps the default `demo` / `mvp` helpers explicit and smoke-testable for the current CLI-first Milestone 3 loop.

## Priority Outcomes

1. Keep command behavior deterministic and easy to smoke-test.
2. Prefer thin command entrypoints over embedded business logic.
3. Preserve compatibility with the canonical engine contract while UI lanes stay disabled.

## Canonical Demo-Path Mapping

- Canonical demo-path steps advanced: `open project/document`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `save and continue`.
- Canonical demo-path step(s) this work now makes more real before handoff: `open project/document`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `save and continue`.
- Exact re-review claim: this slice advances only the deterministic CLI entrypoints that front those current command-backed loop steps, and nothing outside that command-backed surface is claimed as more complete by this handoff.
- Why these exact steps: the reviewed catalog covers the CLI entrypoints that currently front those steps (`bootstrap`, `context-basket`, `diff-preview`, and `terminal`), and this change only hardens the contract for invoking those commands deterministically and rejecting parser/catalog drift before the operator hits them.
- AGENTS alignment statement: this slice makes those CLI-first demo-path steps more real by keeping the fallback command surface explicit, canonically ordered, and smoke-testable while Textual remains disabled.
- Scope-tightening note: this is command-contract hardening for the existing CLI entrypoints only. It does not claim broader workflow execution, retrieval behavior, audit behavior, or UI capability expansion.
- Reviewer fix note: this section exists specifically to satisfy the requested re-review correction to name the exact canonical demo-path steps advanced by the handoff.

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

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the default catalog validates its declared CLI entrypoints against the canonical command list and raises `ValueError` when the exposed parser surface drifts, which keeps the CLI fallback trustworthy for the `open project/document`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `save and continue` steps of the current command-backed MVP loop.
- Kept the returned contract aligned with the canonical command order for CLI-exposed commands while treating alias substitution, missing canonical primary tokens, extra accepted entrypoints, and primary-token order drift as contract errors instead of silently accepting them, which keeps those operator-facing demo-path steps deterministic instead of silently changing underneath the user.
- Kept the default `demo` / `mvp` command-flow, route, smoke, and path helpers explicit on the current branch tip, including the `export-handoff` / `terminal` compatibility surface that supports the final `save and continue` step in the CLI-first loop.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment, missing canonical primary-token rejection, alias-substitution rejection, extra accepted-entrypoint drift rejection, and primary-token order drift rejection, which makes the CLI contract for those demo-path steps smoke-testable and explicit.
- Reissued the handoff packet as a command-catalog-only slice so the review scope matches the claimed implementation files and approval basis.
- Re-ran the full required gate suite on branch tip after confirming the reviewer-required code and test fixes were already present in the implementation commit.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute budget, and the lane size limits. The implementation slice stayed limited to one owned command file plus one focused non-owned test file, so the handoff remains narrow and reviewable.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`. It is the only non-owned implementation path in this handoff.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify the full default parser surface against the catalog and fail fast on alias substitution or extra-entrypoint drift.
   Canonical demo-path step(s) advanced: `open project/document`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `save and continue`, because the CLI fallback must reject silent parser drift before an operator invokes those entrypoints in the loop.
2. Preserved canonical command ordering in the CLI contract for CLI-exposed commands while keeping parser-surface validation explicit.
   Canonical demo-path step(s) advanced: `open project/document`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `save and continue`, because the active CLI surface must stay deterministic from run to run at each of those entrypoints.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment plus missing-primary-token, alias-substitution, extra accepted-entrypoint, and primary-token-order parser-surface drift rejection.
   Canonical demo-path step(s) advanced: `open project/document`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `save and continue`, because the smoke tests now prove the CLI contract for those entrypoints remains explicit and stable.
4. Kept the default `demo` / `mvp` helper contracts aligned with the actual branch-tip CLI route, including `terminal` for the current `export-handoff` compatibility surface.
   Canonical demo-path step(s) advanced: `open project/document`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `save and continue`, because the command-backed helper layer now matches the runtime surface the operator actually invokes.
5. Regenerated the handoff packet so the branch metadata stays scoped to the command-catalog slice, matches the current implementation commit, and names the exact command-backed loop steps protected by this slice.
   Canonical demo-path step(s) advanced: `open project/document`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `save and continue`, because the handoff now states exactly which existing command-backed loop steps this narrow contract-hardening slice protects.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff files

- `THREAD_PACKET.md`

## Commands Run and Outcomes

- `python -m unittest tests.unit.test_commands_catalog`: PASS
- `SCOPE_ALLOW_SHARED=1 make scope-check`: PASS for the reviewed implementation slice that includes the approved shared test `tests/unit/test_commands_catalog.py`.
- `SCOPE_ALLOW_SHARED=1 make ci`: PASS for the reviewed implementation slice that includes the approved shared test `tests/unit/test_commands_catalog.py`.
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Verification Note

- Re-verified on the current `codex/feat-commands` branch tip that the reviewer-required fixes are present in the implementation: `command_cli_contract()` now rejects default-catalog parser-surface drift, and `tests/unit/test_commands_catalog.py` covers missing-primary-token, alias-substitution, extra-entrypoint, and primary-token-order drift where canonical command order alone would still be insufficient.
- Re-verified that the default `demo` / `mvp` command-flow helpers on the current branch tip still include `export-handoff`, and that the packet now maps that `terminal` compatibility surface to the loop's `save and continue` step instead of claiming it was removed.
- This handoff refresh records both gate contexts explicitly: the reviewed implementation slice used `SCOPE_ALLOW_SHARED=1 make scope-check` and `SCOPE_ALLOW_SHARED=1 make ci` because it includes the approved shared test `tests/unit/test_commands_catalog.py`, while this metadata-only reviewer-fix follow-up commit also passes the standard `make scope-check` and `make ci` reruns on branch tip without broadening implementation scope.
- Feature-fixer note: this refresh exists only to record the final gate rerun and produce the requested new commit on top of the already-applied reviewer-required fixes.

## Risks / Blockers

- Risk: `HIGH`
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the command-catalog contract deterministic and drift-resistant, which removes a concrete blocker from the `open project/document`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `save and continue` demo-path steps: the operator-facing CLI surface can no longer silently drift underneath those live workflow entrypoints.
- feat-commands - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop, specifically the stable CLI fallback needed to keep the current demo path usable after each command invocation.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable while the command-catalog surface rejects parser drift before it can silently change the operator contract that the user relies on for `open project/document`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `save and continue`.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused command-catalog test coverage.

## Scope-check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail: lane-owned runtime edits stay in `src/qual/commands/**`, and the only non-owned implementation path is the approved shared test `tests/unit/test_commands_catalog.py`.
- Exact shared-scope invocations for the reviewed implementation slice: `SCOPE_ALLOW_SHARED=1 make scope-check` and `SCOPE_ALLOW_SHARED=1 make ci`.
- Exact scope-check invocation for this metadata-only reviewer-fix follow-up commit: `make scope-check`
- Approval basis: `THREAD_OWNERSHIP.md` lists `tests/unit/test_commands_catalog.py` as shared-by-approval for `codex/feat-commands*`, and the handoff keeps that exception limited to this one test file.
- Scope-tightening confirmation: no additional shared or integrator-locked implementation files are part of this reviewed slice.
