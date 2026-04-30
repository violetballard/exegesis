# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Merge candidate: branch tip after this fixer packet refresh.
- Reviewed implementation range: command-catalog fixer scope at branch tip, centered on `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- Scope completed: command catalog contract hardening and regression coverage for the approved CLI parser token surface.
- Roadmap item affected: active MVP `feat-commands`; Milestone 3 command surface stability while Textual remains disabled.
- Vision capability affected: canonical engine contract and CLI compatibility through deterministic command catalog metadata.
- Routing/provider impact note: none for this command-catalog review packet.
- Proposed `README.md` patch text: none.

## Reviewer Required Fixes

1. Regenerated this handoff around one real scope: the command-catalog parser-surface guard and its shared unit-test coverage.
2. Tightened `command_cli_contract()` so it validates the exact approved parser tokens and derived lookup table, not only the unique canonical command sequence.
3. Added regression coverage for alias replacement of canonical parser tokens, valid-but-unapproved aliases resolving to existing commands, and parser-token reordering that preserves canonical names.
4. Kept off-lane retrieval/router/config work out of this packet's reviewed command scope.
5. Re-ran the required gates and reported the current sandbox blocker accurately below.

## Tasks Completed

1. Locked the approved CLI parser token tuple in `src/qual/commands/catalog.py` and made `command_cli_contract()` compare both live tokens and live lookup-table entries against that approved surface.
2. Preserved canonical-name validation so catalog drift is still rejected after parser-surface validation succeeds.
3. Added focused regressions in `tests/unit/test_commands_catalog.py` for canonical token replacement by alias, unapproved alias insertion, and token reordering that otherwise resolves to the same canonical names.
4. Refreshed this packet so the reviewed files, risks, and gate outcomes match the command-catalog scope.

## Files Changed For This Scope

- `THREAD_PACKET.md`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Ownership And Scope

- Lane-owned implementation path changed: `src/qual/commands/catalog.py`.
- Shared-by-approval test path changed: `tests/unit/test_commands_catalog.py`.
- Packet metadata changed: `THREAD_PACKET.md`.
- Integrator-locked files changed by this packet refresh: none.
- Routing/provider/config files changed by this packet refresh: none.

## Commands Run

- `make scope-check`: passed.
- `./quality-format.sh --check`: passed.
- `./quality-lint.sh`: passed.
- `python -m unittest tests.unit.test_commands_catalog`: passed; 46 tests.
- `./quality-test.sh`: passed; 393 tests, 1 skipped live-router-config assertion for protected worktree config.
- `./typecheck-test.sh`: passed.
- `make ci`: failed at embedded scope-check because `tests/unit/test_commands_catalog.py` is a shared-by-approval test file and CI requires `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci`: failed in packet-router/worktree-recovery tests with sandbox `PermissionError` writing to protected `.codex/packet_router/logs/...` and `.codex/worktree_recovery/...`; command-catalog tests in the same run passed.
- `python -m unittest tests.unit.test_cloud_concurrency_caps.CloudConcurrencyCapsTests.test_run_fixer_detached_cli_streams_prompt_via_stdin_for_local_mode tests.unit.test_packet_progress.WorktreeCleanupTests.test_repair_shadow_gitdir_repoints_worktree_and_preserves_backup`: reproduced the same protected `.codex` write errors.

## Risks And Blockers

- Remaining blocker: full `make ci` cannot complete in this sandbox because two packet-router/worktree-recovery tests attempt to write under protected `.codex` paths. This is outside the command-catalog scope.
- Remaining risk: branch history contains broader work outside this packet's reviewed command-catalog scope. This packet intentionally asks for re-review of the command-catalog fixer scope only.

## Final Readiness Statement

The command-catalog parser surface now rejects accepted-token drift that preserves canonical command names, including alias replacement, unapproved alias insertion, and parser-token reordering. Focused command-catalog tests and the required non-CI gates are green; aggregate CI is blocked by protected `.codex` writes in off-scope packet-router tests.
