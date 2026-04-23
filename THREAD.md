# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Re-review scope is pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`).
- Reviewed implementation files at that commit:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- The branch now carries later code-side fixes as well as the handoff refresh. This fixer pass keeps the reviewed implementation slice pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and updates the handoff text so it accurately describes that commit's narrower behavior: canonical command order and canonical-name consistency between `command_cli_lookup_table()` and `command_names()`, plus the direct Milestone 3 CLI mapping for demo-path step 3.
- Final fixer validation reran the required gate sequence from this worktree on `2026-04-23T21:35:16Z`; the metadata refresh below records that fresh verification on top of the already-landed code-side reviewer fixes.
- Exact canonical demo-path mapping for the reviewed slice:
  - direct step advanced: step 3 `preview and apply or reject a patch`
  - canonical demo-path step(s) advanced: step 3 `preview and apply or reject a patch`, because the reviewed CLI contract check fails fast when canonical command order or canonical-name resolution drifts away from the operator-visible patch preview/apply route while Textual remains disabled
  - out of scope: no new step 1 `open project/document` or step 2 `retrieve relevant material` workflow coverage is claimed by this command-catalog contract slice
- Concrete reason this is not second-order work:
  - at reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, `catalog.py` makes `command_cli_contract()` fail fast if the lookup-table-derived canonical command order no longer matches `command_names()`. That prevents the operator-visible patch preview/apply route from silently drifting away from the catalog order the CLI and smoke tests expect, so this remains direct Milestone 3 CLI-loop hardening rather than generic cleanup.
- Shared-file basis for the high-risk packet:
  - lane-owned implementation: `src/qual/commands/**`
  - shared test touched by the reviewed commit: `tests/unit/test_commands_catalog.py`
  - shared handoff metadata updated by this fixer: `THREAD.md`, `THREAD_PACKET.md`
