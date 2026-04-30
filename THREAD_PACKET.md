# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Merge candidate: branch tip after the latest fixer commit.
- Scope completed: command catalog contract hardening and regression coverage for canonical CLI parser tokens.
- Roadmap item affected: active MVP `feat-commands`; Milestone 3 command surface stability while Textual remains disabled.
- Vision capability affected: canonical engine contract and CLI compatibility through deterministic command catalog metadata.
- Routing/provider impact note: none. No routing, provider configuration, model selection, or core entrypoint behavior is changed.
- Proposed `README.md` patch text: none.

## Reviewer Required Fixes

1. Strengthened `command_cli_contract()` to reject exact parser-surface drift by comparing the accepted CLI token tuple and lookup table against the approved canonical parser surface.
2. Added regression coverage for a valid-but-unapproved parser alias resolving to `bootstrap`.
3. Updated this handoff packet to explicitly name the canonical demo-path steps advanced and the concrete blocker removed.
4. Kept the corrected implementation scope limited to `src/qual/commands/catalog.py` plus the approved shared command-catalog test file, with handoff metadata updates only.

## Tasks Completed

1. Tightened `command_cli_contract()` so the exact approved CLI parser token tuple and lookup table must match the canonical parser surface, in addition to requiring every canonical `command_names()` entry to appear as a canonical CLI parser token in catalog order.
   - Canonical demo-path step: `preview and apply/reject patch`.
   - Concrete blocker removed: unapproved aliases can no longer silently expand or reorder the parser surface while still resolving to an existing command, preserving `diff-preview` as the stable CLI fallback token for patch preview/review.
2. Added a regression test proving alias `diff` cannot replace canonical parser token `diff-preview`.
   - Canonical demo-path step: `preview and apply/reject patch`.
   - Why: prevents alias-only parser drift from hiding the canonical patch preview route.
3. Added a regression test proving alias `diff` cannot appear before canonical parser token `diff-preview`.
   - Canonical demo-path step: `preview and apply/reject patch`.
   - Why: keeps the parser surface ordered by canonical catalog entries before aliases.
4. Added a regression test proving an extra valid-but-unapproved alias resolving to `bootstrap` is rejected by `command_cli_contract()`.
   - Canonical demo-path step: `open project/document`.
   - Concrete blocker removed: prevents CLI project-open/bootstrap compatibility from broadening beyond the approved token surface while still resolving through the catalog.
5. Regenerated handoff metadata from the corrected branch tip without labeling implementation-changing commits as metadata-only.
   - Canonical demo-path step: `preview and apply/reject patch`.
   - Concrete blocker removed: gives reviewer/integrator an accurate packet naming the demo-path step and contract blocker removed by the corrected command-catalog merge candidate.

## Files Changed

- `THREAD.md` (handoff pointer metadata)
- `THREAD_PACKET.md` (handoff metadata)
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py` (approved shared command-catalog regression tests)

## Ownership And Scope

- Lane-owned implementation path changed: `src/qual/commands/catalog.py`.
- Shared-by-approval test path changed: `tests/unit/test_commands_catalog.py`.
- Packet metadata files changed: `THREAD.md`, `THREAD_PACKET.md`.
- Shared-by-approval approval note: `tests/unit/test_commands_catalog.py` is used only for command-catalog regression coverage.
- Integrator-locked files changed: none in the corrected merge candidate.
- Disabled Textual lane files changed: none in the corrected merge candidate.
- Protected metadata blocker resolution: not fully resolved. `.codex/packet_planner/state.json` remains protected from overwrite in this sandbox (`Operation not permitted`), so it cannot be restored here even though the corrected intended review surface is limited to command catalog, approved tests, and handoff metadata.

## Commands Run

- `python -m unittest tests.unit.test_commands_catalog`: passed; 46 tests.
- `python -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_unapproved_alias_to_existing_command tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_alias_replacing_canonical_token tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_matches_the_catalog_order`: passed; 3 tests.
- `make scope-check`: passed.
- `./quality-format.sh --check`: passed.
- `./quality-lint.sh`: passed.
- `./quality-test.sh`: failed outside the command-catalog slice after `tests/smoke.sh` passed; `tests/unit.sh` ran 313 tests with 1 failure and 2 import errors.
  - `tests/unit/test_mvp_migration.py` and `tests/unit/test_unified_retrieval.py` fail importing `src/qual/engine/retrieval/payload.py` because that file has `SyntaxError: unmatched ')'` at line 428.
  - `tests/unit/test_offline_handoff.py::OfflineHandoffConfigTests.test_live_router_config_uses_explicit_lms_provider` fails because protected local `.codex/packet_router/config.json` still has `["-p", "gpt-oss-120b-lms"]` instead of `["--oss", "--local-provider", "lmstudio"]`.
- `./typecheck-test.sh`: failed outside the command-catalog slice on the same `src/qual/engine/retrieval/payload.py` syntax error at line 428.
- `make ci`: failed after passing scope, format, and lint; `python3 -m compileall -q src` stops on the same `src/qual/engine/retrieval/payload.py` syntax error at line 428.

## Risks And Blockers

- Residual risk: full gates are red due off-lane retrieval syntax in `src/qual/engine/retrieval/payload.py` and protected local router config drift, both outside the command-catalog review surface.
- Blocker: `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` cannot pass in this worktree until the off-lane retrieval syntax error at `src/qual/engine/retrieval/payload.py:428` is fixed. `./quality-test.sh` also observes protected router config drift in `.codex/packet_router/config.json`.
- Blocker: `.codex/packet_planner/state.json` remains protected from overwrite in this sandbox, so this fixer could not remove that prior protected metadata delta from the branch history.

## Final Readiness Statement

This work makes the canonical demo-path steps `open project/document` and `preview and apply/reject patch` more real by preserving deterministic CLI parser tokens for `bootstrap` / `project-open` and `diff-preview` / `patch-review`. The concrete blocker removed is valid-but-unapproved parser alias drift: a new accepted token can no longer resolve to an existing command while hiding a changed parser surface from the contract, so the engine-first CLI fallback keeps the approved project-open and patch-review routes reachable while Textual remains disabled.
