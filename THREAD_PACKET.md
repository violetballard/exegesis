# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Review basis: `git show --stat --oneline --name-status f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Fixer prompt satisfied: `20260429T151533Z`

This packet is intentionally narrowed to the reviewed implementation slice `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`). It does not ask reviewers to evaluate later branch-tip commits as part of this handoff packet.

## Required-Fix Resolution

1. Each numbered completed task below names the exact canonical demo-path step it advances.
2. The final readiness statement names which canonical demo-path step is now more real and why parser/catalog drift blocked that step.
3. Ownership wording distinguishes lane-owned implementation files, the approved shared-test exception, and integrator-locked files.
4. Review scope remains narrowed to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.

## Implementation Commit

- `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` - `feat(commands): lock CLI contract to command catalog`

Changed files in this reviewed slice:

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Canonical Demo-Path Alignment

Canonical demo-path sequence from the lane packet: `open document`, `retrieve material`, `gather/promote context`, `plan/revise`, `preview/apply/reject patch`, `persist/save`, `continue`.

This command-catalog slice directly advances `retrieve material`, `gather/promote context`, `preview/apply/reject patch`, and `persist/save`. It does not claim to implement `open document`, `plan/revise`, or `continue`.

Parser/catalog drift was a direct blocker for the CLI-first Milestone 3 loop because the operator-facing parser and the command catalog could disagree about which command token belonged to a demo-path step. If `context-basket`, `diff-preview`/`diff`, or `terminal` parsed differently than the catalog described them, the loop could not reliably retrieve relevant material, promote gathered context, preview/apply/reject a patch, or persist the session through the CLI.

## Scope Completed

1. Added command-catalog coverage that keeps retrieval-oriented CLI tokens and catalog entries aligned.
   Canonical demo-path step advanced: `retrieve material`, because the retrieval-facing command surface must remain stable before the CLI can request relevant material.

2. Added command-catalog coverage for context basket command metadata.
   Canonical demo-path step advanced: `gather/promote context`, because context promotion depends on the CLI and catalog agreeing on the command that gathers selected material into the active working set.

3. Added command-catalog coverage for patch-review command metadata and aliases.
   Canonical demo-path step advanced: `preview/apply/reject patch`, because patch preview and review commands must remain discoverable and parseable under the same catalog contract.

4. Added command-catalog coverage for terminal/export command metadata.
   Canonical demo-path step advanced: `persist/save`, because session persistence depends on the terminal/export command staying present in the parser/catalog surface before handoff.

## Files Changed

From `git show --name-status f8d860ed9f6299f0169c4f21321ac5f37c949fd3`:

- `M src/qual/commands/catalog.py`
- `M tests/unit/test_commands_catalog.py`

Implementation files in scope:

- `src/qual/commands/catalog.py`

Tests in scope:

- `tests/unit/test_commands_catalog.py`

Handoff metadata in this fixer commit:

- `THREAD.md`
- `THREAD_PACKET.md`

## Ownership And Risk

- Lane-owned implementation file in the reviewed `f8d860e` slice: `src/qual/commands/catalog.py`.
- Shared-by-approval test file in the reviewed `f8d860e` slice: `tests/unit/test_commands_catalog.py`, used as the focused command-catalog regression surface.
- Integrator-locked files in the reviewed `f8d860e` slice: none. The slice does not edit `README.md`, `INTEGRATION.md`, `src/main.py`, `src/qual/cli.py`, or `src/qual/app.py`.
- Current fixer-slice edits: handoff metadata only in `THREAD.md` and `THREAD_PACKET.md`.
- Task budget: `4` high-risk tasks completed.
- Budget status: within high-risk task, file, and size limits for this fixer packet.

## Roadmap And Vision

- Roadmap: Milestone 3 "Real workflow loop," specifically CLI compatibility for command-driven retrieval, context gathering, patch review, and persistence.
- Roadmap adjacency: Milestone 5 "YC demo readiness," specifically reproducible command catalog behavior for the demo path.
- Product vision: `Exegesis Engine` remains the engine/runtime and CLI compatibility surface; the command catalog is part of the canonical engine contract consumed by CLI now and A2UI later.
- Routing/provider impact: none. This slice does not touch model routing or provider configuration.
- Proposed `README.md` patch text: none.

## Commands Run

- Fresh `20260429T151533Z` fixer rerun after narrowing the packet to `f8d860e` and correcting ownership/demo-path mapping:
  `make scope-check` passed for branch `codex/feat-commands`; `./quality-format.sh --check` passed; `./quality-lint.sh` passed; `./quality-test.sh` passed with smoke tests and `133` unit tests; `./typecheck-test.sh` passed by compiling Python sources in `src/`; `make ci` passed with scope-check, format, lint, typecheck, smoke tests, and `133` unit tests.

## Risks And Blockers

- Risk: `tests/unit/test_commands_catalog.py` is a shared-by-approval test file; this packet states that exception separately from integrator-locked files.
- Blockers: none known after the fresh gate rerun.

## Final Readiness Statement

This `f8d860e` command-catalog slice makes `retrieve material` more real by ensuring the CLI-facing retrieval command cannot silently drift away from the catalog contract. Parser/catalog drift was a direct blocker for that step because retrieval starts from a concrete command token; if the parser accepts one token while the catalog documents another, the demo path cannot reliably request relevant material from the CLI.
