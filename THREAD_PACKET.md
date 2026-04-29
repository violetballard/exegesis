# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: branch tip `codex/feat-commands`, including this fixer commit.
- Review basis: `git diff --stat --name-status f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD -- THREAD.md THREAD_PACKET.md src/qual/cli.py src/qual/commands/__init__.py src/qual/commands/catalog.py tests/unit/test_commands_catalog.py`
- Fixer prompt satisfied: `20260429T152044Z`

This packet uses the branch tip as the review target. It includes the earlier reviewed `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice and all later implementation, test, and handoff commits on `codex/feat-commands`.

## Required-Fix Resolution

1. The review basis is the full branch-tip diff from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`, not a narrowed historical commit.
2. `command_cli_contract()` now validates the command catalog against the actual argparse subparser surface built by `src/qual/cli.py`.
3. Parser drift tests cover live parser rename drift, extra-token drift, missing-token drift, and catalog canonical-name drift.
4. Each numbered completed task below states the exact canonical demo-path step it advances.
5. Ownership wording distinguishes lane-owned files, shared-by-approval files, and integrator-locked files.

## Implementation Summary

- `src/qual/cli.py` exposes the live argparse command token surface through `command_parser_tokens()` and `command_parser_lookup_table()`.
- `src/qual/commands/catalog.py` imports the live parser surface lazily and rejects parser/catalog mismatch in `command_cli_contract()`.
- `tests/unit/test_commands_catalog.py` patches the live parser construction path to prove rename, missing-token, and extra-token drift are rejected.
- `src/qual/commands/__init__.py` exports the command catalog helpers added on this branch.
- `THREAD.md` and `THREAD_PACKET.md` now describe the branch-tip review target truthfully.

## Canonical Demo-Path Alignment

Canonical demo-path sequence: `open document`, `retrieve relevant material`, `gather context`, `plan/revise`, `apply/reject patch`, `save/continue`.

1. Added and exported deterministic command catalog helpers for CLI command tokens and route metadata.
   Canonical demo-path step advanced: `retrieve relevant material`, because retrieval starts from stable parser tokens and catalog metadata.

2. Bound `command_cli_contract()` to the actual argparse subparser choices created by the CLI.
   Canonical demo-path step advanced: `retrieve relevant material`, because the CLI cannot reliably request relevant material if the parser accepts a token the catalog does not describe.

3. Added live parser drift tests for renamed parser tokens, missing parser tokens, and extra parser tokens.
   Canonical demo-path step advanced: `gather context`, because context basket operations depend on the parser and catalog agreeing on the `context-basket` command surface.

4. Preserved alias and route-contract coverage for `diff-preview`/`diff`, terminal/export routing, and smoke argv helpers.
   Canonical demo-path step advanced: `apply/reject patch`, because patch preview and review commands must stay discoverable and parseable under the same contract.

5. Refreshed the handoff packet with the complete branch-tip diff, changed-file list, ownership/risk note, and gate evidence.
   Canonical demo-path step advanced: `save/continue`, because the handoff now preserves enough accurate state for review and later continuation.

## Files Changed In Review Target

From `git diff --name-status f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`:

- `M THREAD.md`
- `M THREAD_PACKET.md`
- `M src/qual/cli.py`
- `M src/qual/commands/__init__.py`
- `M src/qual/commands/catalog.py`
- `M tests/unit/test_commands_catalog.py`

Implementation files:

- `src/qual/cli.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/catalog.py`

Tests:

- `tests/unit/test_commands_catalog.py`

Handoff metadata:

- `THREAD.md`
- `THREAD_PACKET.md`

## Ownership And Risk

- Lane-owned implementation paths: `src/qual/commands/**`.
- Shared-by-approval files touched: `tests/unit/test_commands_catalog.py`.
- Shared-by-approval and integrator-locked file touched: `src/qual/cli.py`.
- Other integrator-locked files touched: none. This branch does not edit `README.md`, `INTEGRATION.md`, `src/main.py`, or `src/qual/app.py`.
- Risk reason: this is high-risk because the branch validates a shared CLI entrypoint surface and touches `src/qual/cli.py`.
- Task budget: high-risk `4` task budget exceeded by historical branch-tip work; this packet is a required fixer correction for an already-open review target, not a new feature expansion.
- Size note: branch-tip diff from `f8d860e..HEAD` is `6` files and `826 insertions(+), 134 deletions(-)` across implementation, tests, and handoff metadata.

## Roadmap And Vision

- Roadmap: Milestone 3 "Real workflow loop," specifically CLI compatibility for command-driven retrieval, context gathering, patch preview/review, and persistence.
- Roadmap adjacency: Milestone 5 "YC demo readiness," specifically reproducible command behavior on the canonical demo path.
- Product vision: `Exegesis Engine` remains the engine/runtime and CLI compatibility surface; the command catalog is the deterministic command contract consumed by CLI now and A2UI later.
- Routing/provider impact: none. This branch does not touch model routing or provider configuration.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

Fresh fixer rerun for `20260429T152044Z` validates the corrected branch-tip review target.

## Risks And Blockers

- Risk: `src/qual/cli.py` is both shared-by-approval and integrator-locked per `THREAD_OWNERSHIP.md`; the packet now identifies that separately from the shared test file.
- Risk: historical branch-tip work exceeds the normal high-risk task budget, so review should use the branch-tip basis above instead of a narrowed historical slice.
- Blockers: none known after the fresh gate rerun.

## Final Readiness Statement

This branch-tip command contract work makes `retrieve relevant material` more real by ensuring the live CLI parser and command catalog cannot silently drift apart. That parser/catalog drift was a direct blocker because the demo path begins with concrete command tokens; if the parser and catalog disagree, the CLI cannot reliably retrieve relevant material, gather context, preview or apply/reject patches, or save/continue the workflow.
