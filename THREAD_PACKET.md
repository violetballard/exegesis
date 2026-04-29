# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: branch tip `codex/feat-commands`, including the latest fixer commit.
- Review basis: `git diff --stat --name-status f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD -- THREAD.md THREAD_PACKET.md src/qual/cli.py src/qual/commands/__init__.py src/qual/commands/catalog.py tests/unit/test_commands_catalog.py`
- Fixer prompts satisfied: `20260429T152044Z`, `20260429T152842Z`, `20260429T154016Z`, `20260429T154607Z`, `20260429T155155Z`, `20260429T155636Z`, `20260429T160222Z`

This packet uses the branch tip as the review target. It includes the earlier reviewed `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice and all later implementation, test, and handoff commits on `codex/feat-commands`; no later implementation commits are excluded from the merge target.

## Required-Fix Resolution

1. The review basis is the full branch-tip diff from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`, not a narrowed historical commit; the merge target is the branch tip.
2. All implementation files in the branch-tip diff are listed below: `src/qual/cli.py`, `src/qual/commands/__init__.py`, and `src/qual/commands/catalog.py`.
3. `command_cli_contract()` now validates the command catalog against the actual argparse subparser surface built by `src/qual/cli.py`.
4. Parser drift tests cover live parser rename drift, parser-only extra-token drift, parser-only missing-token drift, post-build extra-token drift, post-build missing-token drift, and catalog canonical-name drift.
5. The canonical demo-path alignment below maps every completed task to the exact AGENTS canonical demo-path step it advances.
6. Ownership wording distinguishes lane-owned files, shared-by-approval files, and integrator-locked files.
7. Metadata-only files changed by packet refresh commit `a9266aca4b87a2ad1df4e8615a2a4adfb816fc44` are listed completely: `THREAD.md` and `THREAD_PACKET.md`.
8. The canonical demo-path impact statement below explains how deterministic CLI contract validation strengthens the engine-first MVP loop rather than only the command catalog internals.

## Implementation Summary

- `src/qual/cli.py` exposes the live argparse command token surface through `command_parser_tokens()` and `command_parser_lookup_table()`.
- `src/qual/commands/catalog.py` imports the live parser surface lazily and rejects parser/catalog mismatch in `command_cli_contract()`.
- `tests/unit/test_commands_catalog.py` patches the live parser construction path to prove rename drift, parser-only missing-token drift, and parser-only extra-token drift are rejected.
- `src/qual/commands/__init__.py` exports the command catalog helpers added on this branch.
- `THREAD.md` and `THREAD_PACKET.md` now describe the branch-tip review target truthfully.

## Canonical Demo-Path Alignment

Canonical demo-path sequence from AGENTS: `open project/document`, `retrieve relevant material`, `promote or gather context into the basket`, `preview and apply or reject a patch`, `persist session state`.

Canonical demo-path impact: deterministic CLI contract validation strengthens the engine-first MVP loop by making the CLI fallback a trustworthy way to drive the same demo-path operations that A2UI will later call. The engine loop depends on stable command tokens to open inputs, request retrieval, gather context, and preview patch work; parser/catalog drift would break that loop before the engine receives the intended operation. This branch therefore makes `retrieve relevant material` more real directly and keeps adjacent command surfaces discoverable for `open project/document`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `persist session state`. It does not implement revise/save/apply behavior; it validates the command discovery and parser contract for the command surfaces already present in this branch.

1. Added and exported deterministic command catalog helpers for CLI command tokens and route metadata.
   Exact canonical demo-path step advanced: `retrieve relevant material`, because retrieval starts from stable parser tokens and catalog metadata.

2. Bound `command_cli_contract()` to the actual argparse subparser choices created by the CLI.
   Exact canonical demo-path step advanced: `retrieve relevant material`, because the CLI cannot reliably request relevant material if the parser accepts a token the catalog does not describe.

3. Added live parser drift tests for renamed parser tokens, parser-only missing parser tokens, and parser-only extra parser tokens.
   Exact canonical demo-path step advanced: `promote or gather context into the basket`, because context basket operations depend on the parser and catalog agreeing on the `context-basket` command surface.

4. Preserved alias and route-contract coverage for `diff-preview`/`diff`, terminal/export routing, and smoke argv helpers.
   Exact canonical demo-path steps advanced: `preview and apply or reject a patch` through `diff-preview`/`diff` command metadata, and `persist session state` through `terminal` export-handoff metadata. This branch validates command surfaces only; it does not add apply/reject or persistence behavior.

5. Refreshed the handoff packet with the complete branch-tip diff, changed-file list, ownership/risk note, and gate evidence.
   Exact canonical demo-path step advanced: `retrieve relevant material`, because the handoff now names how parser/catalog drift blocked reliable retrieval command discovery and parsing. It also states the adjacent `open project/document`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `persist session state` surfaces kept discoverable, and names every metadata file changed by packet refresh commit `a9266aca4b87a2ad1df4e8615a2a4adfb816fc44`.

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

Metadata-only files changed by packet refresh commit `a9266aca4b87a2ad1df4e8615a2a4adfb816fc44`:

- `THREAD.md`
- `THREAD_PACKET.md`

## Ownership And Risk

- Lane-owned implementation paths: `src/qual/commands/**`.
- Shared-by-approval files touched: `tests/unit/test_commands_catalog.py`.
- Shared-by-approval and integrator-locked file touched: `src/qual/cli.py`.
- Other integrator-locked files touched: none. This branch does not edit `README.md`, `INTEGRATION.md`, `src/main.py`, or `src/qual/app.py`.
- Risk reason: this is high-risk because the branch validates a shared CLI entrypoint surface and touches `src/qual/cli.py`.
- Task budget: high-risk `4` task budget exceeded by historical branch-tip work; this packet is a required fixer correction for an already-open review target, not a new feature expansion.
- Size note: branch-tip diff from `f8d860e..HEAD` is `6` files and `892 insertions(+), 134 deletions(-)` across implementation, tests, and handoff metadata.

## Roadmap And Vision

- Roadmap: Milestone 3 "Real workflow loop," specifically CLI compatibility for command-driven retrieval plus adjacent command-surface discovery for context gathering, patch preview/review, and persistence handoff.
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
Fresh fixer rerun for `20260429T152842Z` validates the canonical demo-path and metadata file-list corrections.
Fresh fixer rerun for `20260429T154016Z` validates that every completed task explicitly names the canonical demo-path step it advances.
Fresh fixer rerun for `20260429T154607Z` validates that the actual branch tip is the review and merge target, all implementation files are in scope, live argparse parser-surface validation is claimed accurately, and each completed task names the exact canonical demo-path step it advances.
Fresh fixer rerun for `20260429T155155Z` resolves the offline-review fallback by rerunning every requested gate and recording passing results: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
Fresh fixer rerun for `20260429T155636Z` maps each completed task to AGENTS canonical demo-path wording, adds the deterministic CLI contract impact statement for the engine-first MVP loop, and validates the full required gate set.
Fresh fixer rerun for `20260429T160222Z` adds focused live-parser tests that prove parser-only token addition and parser-only token removal fail `command_cli_contract()`, and keeps the branch-tip diff as the review basis.

## Risks And Blockers

- Risk: `src/qual/cli.py` is both shared-by-approval and integrator-locked per `THREAD_OWNERSHIP.md`; the packet now identifies that separately from the shared test file.
- Risk: historical branch-tip work exceeds the normal high-risk task budget, so review should use the branch-tip basis above instead of a narrowed historical slice.
- Blockers: none known after the fresh gate rerun.

## Final Readiness Statement

This branch-tip command contract work makes `retrieve relevant material` more real by ensuring the live CLI parser and command catalog cannot silently drift apart. That parser/catalog drift was a direct blocker because the demo path begins with concrete command tokens; if the parser and catalog disagree, the CLI cannot reliably discover and parse the retrieval command surface. Adjacent catalog entries also keep the existing `open project/document`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `persist session state` command surfaces discoverable, without claiming new revise/save/apply behavior.

This work makes `retrieve relevant material` more real by enforcing one shared parser/catalog contract for the CLI retrieval command surface.
