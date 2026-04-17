# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `3e97d729b07a4cdcd71324ae4f6eb3ad534043ea`
- Packet refresh role: `feature-fixer required-fixes verification refresh v4`

## Packet Traceability Note

- The implementation commit above refers to the current runtime fix commit for this lane, which carries the reviewer-required command-surface hardening and the current default `demo` / `mvp` command-flow contract on branch tip.
- This packet refresh keeps the handoff wording aligned with the current implementation and records a fresh required-fixes verification rerun for the reviewer-fix branch tip.
- Final verification refresh: re-ran the required gate suite on April 16, 2026 (America/Los_Angeles) after confirming the reviewer-required demo-path alignment remains explicit in this branch-tip handoff.
- Feature-fixer verification refresh v4: re-ran the full required gate suite on April 16, 2026 at 20:00:25 PDT and confirmed the branch tip already contains the reviewer-required parser-surface drift guard, alias-only drift coverage, and explicit `open project/document` demo-path mapping.
- Feature-fixer rerun refresh: revalidated the explicit `open project/document` demo-path mapping on April 16, 2026 at 19:53:58 PDT before rerunning the required gate suite for this handoff.
- Feature-fixer packet refresh: this follow-up exists to make the blocker removal explicit in the handoff itself, so re-review does not have to infer how the command-catalog hardening advances the live MVP loop.
- Reviewer-fix follow-up scope: this refresh keeps the packet aligned with the actual branch tip, where the default `demo` / `mvp` command-flow helpers still cover `project-open`, `retrieval`, `patch-review`, and `export-handoff`, and where the reviewer-required fix is the explicit demo-path mapping plus the concrete blocker-removal statement in the handoff itself.
- Commit traceability note: this `v3` refresh exists only to attach a fresh fixer commit and gate rerun to the already-applied reviewer-required packet alignment.

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

- Canonical demo-path step advanced: `open project/document`.
- Canonical demo-path step this work now makes more real before handoff: `open project/document`.
- Exact re-review claim: this slice hardens the deterministic CLI contract around the `bootstrap` entrypoint that fronts the current `open project/document` step, and it does not claim broader workflow completion outside that command-contract surface.
- Why this exact step: `bootstrap` is the command-backed entrypoint for `open project/document`, and this change keeps that operator-facing surface canonical, drift-resistant, and smoke-testable while Textual remains disabled.
- AGENTS alignment statement: this slice makes `open project/document` more real by keeping the fallback CLI entrypoint explicit, canonically ordered, and safe from silent parser/catalog drift.
- Concrete blocker removed: before this hardening, parser/catalog drift could silently change which canonical command surface backed `bootstrap`; after this hardening, that drift fails fast instead of weakening the operator-facing `open project/document` step.
- Scope-tightening note: this is command-contract hardening only. It does not claim broader retrieval behavior, patch workflow behavior, audit behavior, or UI capability expansion.
- Reviewer fix note: this section exists specifically to satisfy the requested re-review correction to name the exact canonical demo-path step advanced by the handoff.

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

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the default catalog validates its declared CLI entrypoints against the canonical command list and raises `ValueError` when the exposed parser surface drifts, which keeps the CLI fallback trustworthy for the `open project/document` step fronted by `bootstrap`.
- Kept the returned contract aligned with the canonical command order for CLI-exposed commands while treating alias substitution, missing canonical primary tokens, extra accepted entrypoints, and primary-token order drift as contract errors instead of silently accepting them, which keeps the `bootstrap`-backed operator entrypoint deterministic instead of silently changing underneath the user.
- Kept the default `demo` / `mvp` command-flow, route, smoke, and path helpers explicit on the current branch tip so the CLI-first contract around `bootstrap` remains clear and migration-safe.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment, missing canonical primary-token rejection, alias-substitution rejection, extra accepted-entrypoint drift rejection, and primary-token order drift rejection, which makes the CLI contract for `open project/document` smoke-testable and explicit.
- Reissued the handoff packet as a command-catalog-only slice so the review scope matches the claimed implementation files and approval basis.
- Re-ran the full required gate suite on branch tip after confirming the reviewer-required code and test fixes were already present in the implementation commit.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute budget, and the lane size limits. The implementation slice stayed limited to one owned command file plus one focused non-owned test file, so the handoff remains narrow and reviewable.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`. It is the only non-owned implementation path in this handoff.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify the full default parser surface against the catalog and fail fast on alias substitution or extra-entrypoint drift.
   Canonical demo-path step advanced: `open project/document`, because the `bootstrap` CLI fallback must reject silent parser drift before an operator invokes the first live step of the MVP loop.
2. Preserved canonical command ordering in the CLI contract for CLI-exposed commands while keeping parser-surface validation explicit.
   Canonical demo-path step advanced: `open project/document`, because the active `bootstrap` surface must stay deterministic from run to run.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment plus missing-primary-token, alias-substitution, extra accepted-entrypoint, and primary-token-order parser-surface drift rejection.
   Canonical demo-path step advanced: `open project/document`, because the smoke tests now prove the `bootstrap` command contract remains explicit and stable.
4. Kept the default `demo` / `mvp` helper contracts aligned with the actual branch-tip CLI route so the `bootstrap` compatibility surface remains consistent with the runtime command catalog.
   Canonical demo-path step advanced: `open project/document`, because the command-backed helper layer now matches the runtime surface the operator actually invokes for the first loop step.
5. Regenerated the handoff packet so the branch metadata stays scoped to the command-catalog slice, matches the current implementation commit, and names the exact command-backed loop steps protected by this slice.
   Canonical demo-path step advanced: `open project/document`, because the handoff now states exactly which existing command-backed step this narrow contract-hardening slice protects.

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
- Re-verified that the packet’s roadmap and vision mapping now stays anchored to the `bootstrap` entrypoint and the `open project/document` demo-path step instead of making broader workflow claims.
- Re-verified that the packet itself answers the reviewer’s numbered asks directly by naming the canonical demo-path step advanced and explaining why deterministic command validation makes that step more real in the CLI-first MVP loop.
- This handoff refresh records both gate contexts explicitly: the reviewed implementation slice used `SCOPE_ALLOW_SHARED=1 make scope-check` and `SCOPE_ALLOW_SHARED=1 make ci` because it includes the approved shared test `tests/unit/test_commands_catalog.py`, while this metadata-only reviewer-fix follow-up commit also passes the standard `make scope-check` and `make ci` reruns on branch tip without broadening implementation scope.
- Feature-fixer note: this refresh exists only to record the fresh required-fixes gate rerun on branch tip and make the reviewer-requested blocker-removal statement explicit on top of the already-applied reviewer-required fixes.
- Verification refresh v4 note: no runtime implementation paths changed in this follow-up; it records that the current branch tip still satisfies the numbered reviewer fixes and passes the required gates.

## Risks / Blockers

- Risk: `HIGH`
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the command-catalog contract deterministic and drift-resistant, which removes a concrete blocker from the `open project/document` demo-path step because the operator-facing `bootstrap` CLI surface can no longer silently drift.
- feat-commands - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop, specifically the stable CLI fallback needed to keep the current demo path usable after each command invocation.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable while the command-catalog surface rejects parser drift before it can silently change the `bootstrap` operator contract that the user relies on for `open project/document`.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused command-catalog test coverage.

## Scope-check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail: lane-owned runtime edits stay in `src/qual/commands/**`, and the only non-owned implementation path is the approved shared test `tests/unit/test_commands_catalog.py`.
- Exact shared-scope invocations for the reviewed implementation slice: `SCOPE_ALLOW_SHARED=1 make scope-check` and `SCOPE_ALLOW_SHARED=1 make ci`.
- Exact scope-check invocation for this metadata-only reviewer-fix follow-up commit: `make scope-check`
- Approval basis: `THREAD_OWNERSHIP.md` lists `tests/unit/test_commands_catalog.py` as shared-by-approval for `codex/feat-commands*`, and the handoff keeps that exception limited to this one test file.
- Scope-tightening confirmation: no additional shared or integrator-locked implementation files are part of this reviewed slice.
