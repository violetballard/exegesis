# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Authoritative review target: isolated command-catalog slice `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` plus this fixer pass.
- Current fixer packet satisfied: `fixer__feat-commands__20260429T234833Z`.
- Integration instruction: review cannot proceed yet. `THREAD.md`, `THREAD_PACKET.md`, and this submitted packet all name the same intended f8-only command-catalog target, but protected `.agents/**` and `.codex/**` metadata still remains in `main..HEAD`.
- Scope correction status: unrelated writable engine, router, docs, config, automation, and disabled Textual lane changes from the previous branch tip are restored to `main`. Protected `.agents/**` and `.codex/**` metadata could not be rewritten from this sandbox, so the branch-tip merge diff is not fully isolated yet.
- Risk classification: blocked isolation. The intended normal `feat-commands` target has one shared-by-approval unit-test edit and no routing, provider, core entrypoint, disabled Textual, or integrator-locked files, but protected metadata still prevents a clean review target.

## Required Handoff Fields

- Branch name: `codex/feat-commands`
- Scope completed: command catalog contract hardening and regression coverage for canonical CLI parser tokens.
- Implementation review basis: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` plus this fixer pass that removes unrelated merge-diff scope and refreshes packet metadata.
- Roadmap item affected: active MVP `feat-commands`; Milestone 3 command surface stability while Textual remains disabled.
- Vision capability affected: canonical engine contract and CLI compatibility through deterministic command catalog metadata.
- Exact canonical demo-path step advanced: `preview and apply/reject patch`.
- Canonical demo-path mapping: the command contract keeps `diff-preview` / `patch-review` available as the exact CLI fallback route for previewing patch output and preserving the apply/reject step while Textual remains disabled. The same route contract also keeps smoke coverage aligned for `open project/document` (`bootstrap` / `project-open`), `retrieve relevant material` (`retrieval`), `promote or gather context` (`context-basket`), and `save and continue` (`terminal` / `export-handoff`).
- Budget and size compliance: not yet compliant because protected `.agents/**` and `.codex/**` metadata still appears in `main..HEAD`.
- Routing/provider impact note: none. No routing, provider configuration, model selection, or core entrypoint behavior is changed.
- Proposed `README.md` patch text: none.

## Tasks Completed

1. Tightened `command_cli_contract()` so every canonical `command_names()` entry must appear as a canonical CLI parser token in catalog order.
2. Added a regression test proving alias `diff` cannot replace canonical parser token `diff-preview`.
3. Added a regression test proving alias `diff` cannot appear before canonical parser token `diff-preview`.
4. Refreshed `THREAD.md` and `THREAD_PACKET.md` so both name the same f8-only command-catalog review target.
5. Removed unrelated writable branch-tip scope from the reviewable merge diff by restoring non-command engine, router, docs, config, automation, and disabled Textual paths to `main`.
6. Added explicit canonical demo-path mapping for `preview and apply/reject patch`, with supporting CLI route coverage for open, retrieve, basket, and save/continue steps.

## Complete Corrected File List

The intended corrected review target is limited to:

- `THREAD.md`
- `THREAD_PACKET.md`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

Residual protected metadata still present in `main..HEAD`:

- `.agents/**`
- `.codex/**`

## Ownership And Scope

- Lane-owned implementation path changed: `src/qual/commands/catalog.py`.
- Shared-by-approval test path changed: `tests/unit/test_commands_catalog.py`.
- Packet metadata files changed: `THREAD.md`, `THREAD_PACKET.md`.
- Shared-by-approval files changed: approved exception for `tests/unit/test_commands_catalog.py` to cover the command-catalog alias regression.
- Integrator-locked files changed: none in the corrected target.
- Disabled Textual lane files changed: none in the corrected target.
- Routing/provider impact: none.

## Commands To Run

- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh` fails while protected `.codex/packet_router/config.json` remains unreverted.
- `./typecheck-test.sh`
- `make ci` fails for the same `test_live_router_config_uses_explicit_lms_provider` assertion.

## Risks And Blockers

- Risk: the normal Git index and protected `.agents/**` / `.codex/**` paths are outside the writable sandbox for this worktree.
- Blocker: protected metadata cannot be restored to `main` from this sandbox. Shell writes, `git restore`, `git checkout`, `git update-index`, `git fast-import`, and the approved `lane_repo_commit.py` path could not produce the needed protected-metadata restoration.

## Final Readiness Statement

This packet records the intended authoritative target: the f8-only command-catalog slice plus this fixer pass. The command work makes the canonical demo-path step `preview and apply/reject patch` more real by preserving deterministic CLI parser tokens for `diff-preview` / `patch-review`, so the engine-first CLI fallback can still preview patch output and keep apply/reject flow reachable while Textual remains disabled. Re-review should wait until protected `.agents/**` and `.codex/**` metadata is restored outside this sandbox.
