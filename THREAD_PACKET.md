# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `4318eb83c89b9e7292a40d303154d1b7257e525a`
- Packet refresh role: `reviewer-required gate rerun and finalization`

## Packet Traceability Note

- The implementation commit above is the reviewed command-surface hardening commit that satisfies the reviewer-required runtime behavior.
- This packet refresh keeps the handoff wording aligned with the current implementation and records the final required gate rerun for the reviewer-fix branch tip.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Harden the CLI command contract so `command_cli_contract()` stays deterministic, preserves the canonical command order for exposed commands, and fails fast when the default parser surface drifts from the declared command catalog.

## Priority Outcomes

1. Keep command behavior deterministic and easy to smoke-test.
2. Prefer thin command entrypoints over embedded business logic.
3. Preserve compatibility with the canonical engine contract while UI lanes stay disabled.

## Canonical Demo-Path Mapping

- Canonical demo-path steps advanced: `open project/document`, `promote or gather context into the basket`, and `preview and apply or reject a patch`.
- Why these exact steps: the reviewed catalog covers the CLI entrypoints that currently front those steps (`bootstrap`, `context-basket`, and `diff-preview`), and this change only hardens the contract for invoking those commands deterministically and rejecting parser/catalog drift before the operator hits them.
- AGENTS alignment statement: this slice makes those three CLI-first demo-path steps more real by keeping the fallback command surface explicit, canonically ordered, and smoke-testable while Textual remains disabled.
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

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the default catalog validates its declared CLI entrypoints against the canonical command list and raises `ValueError` when the exposed parser surface drifts, which keeps the CLI fallback trustworthy for the `open project/document`, `promote or gather context into the basket`, and `preview and apply or reject a patch` steps of the canonical MVP loop.
- Kept the returned contract aligned with the canonical command order for CLI-exposed commands while treating alias substitution, missing canonical primary tokens, extra accepted entrypoints, and primary-token order drift as contract errors instead of silently accepting them, which keeps those operator-facing demo-path steps deterministic instead of silently changing underneath the user.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment, missing canonical primary-token rejection, alias-substitution rejection, extra accepted-entrypoint drift rejection, and primary-token order drift rejection, which makes the CLI contract for those demo-path steps smoke-testable and explicit.
- Reissued the handoff packet as a command-catalog-only slice so the review scope matches the claimed implementation files and approval basis.
- Re-ran the full required gate suite on branch tip after confirming the reviewer-required code and test fixes were already present in the implementation commit.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute budget, and the lane size limits. The implementation slice stayed limited to one owned command file plus one focused non-owned test file, so the handoff remains narrow and reviewable.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`. It is the only non-owned implementation path in this handoff.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify the full default parser surface against the catalog and fail fast on alias substitution or extra-entrypoint drift.
   Demo-path steps: `open project/document`, `promote or gather context into the basket`, and `preview and apply or reject a patch`, because the CLI fallback must reject silent parser drift before an operator invokes those entrypoints in the loop.
2. Preserved canonical command ordering in the CLI contract for CLI-exposed commands while keeping parser-surface validation explicit.
   Demo-path steps: `open project/document`, `promote or gather context into the basket`, and `preview and apply or reject a patch`, because the active CLI surface must stay deterministic from run to run at each of those entrypoints.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment plus missing-primary-token, alias-substitution, extra accepted-entrypoint, and primary-token-order parser-surface drift rejection.
   Demo-path steps: `open project/document`, `promote or gather context into the basket`, and `preview and apply or reject a patch`, because the smoke tests now prove the CLI contract for those entrypoints remains explicit and stable.
4. Regenerated the handoff packet so the branch metadata stays scoped to the command-catalog slice and uses the current roadmap and vision labels.
   Demo-path steps: `open project/document`, `promote or gather context into the basket`, and `preview and apply or reject a patch`, because the handoff now states exactly which existing command-backed loop steps this narrow contract-hardening slice protects.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff files

- `THREAD_PACKET.md`

## Commands Run and Outcomes

- `python -m unittest tests.unit.test_commands_catalog`: PASS
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Verification Note

- Re-verified on the current `codex/feat-commands` branch tip that the reviewer-required fixes are present in the implementation: `command_cli_contract()` now rejects default-catalog parser-surface drift, and `tests/unit/test_commands_catalog.py` covers missing-primary-token, alias-substitution, extra-entrypoint, and primary-token-order drift where canonical command order alone would still be insufficient.
- This handoff refresh is tied to a fresh full gate rerun on the current packet-refresh branch tip, using the standard `make scope-check` invocation because this follow-up commit only adjusts packet metadata and does not expand the reviewed implementation scope beyond the already-approved shared test exception.

## Risks / Blockers

- Risk: `HIGH`
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the command-catalog contract deterministic and drift-resistant, which removes a concrete blocker from the `open project/document`, `promote or gather context into the basket`, and `preview and apply or reject a patch` demo-path steps: the operator-facing CLI surface can no longer silently drift underneath those live workflow entrypoints.
- feat-commands - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop, specifically the stable CLI fallback needed to keep the current demo path usable after each command invocation.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable while the command-catalog surface rejects parser drift before it can silently change the operator contract that the user relies on for `open project/document`, `promote or gather context into the basket`, and `preview and apply or reject a patch`.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused command-catalog test coverage.

## Scope-check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail: lane-owned runtime edits stay in `src/qual/commands/**`, and the only non-owned implementation path is the approved shared test `tests/unit/test_commands_catalog.py`.
- Exact scope-check invocation for this reviewer-fix follow-up: `make scope-check`
- Approval basis: `THREAD_OWNERSHIP.md` lists `tests/unit/test_commands_catalog.py` as shared-by-approval for `codex/feat-commands*`, and the handoff keeps that exception limited to this one test file.
- Scope-tightening confirmation: no additional shared or integrator-locked implementation files are part of this reviewed slice.
