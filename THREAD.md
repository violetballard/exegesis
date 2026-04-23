# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Re-review scope is pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`).
- Reviewed implementation files at that commit:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- The branch now carries later code-side fixes as well as the handoff refresh. This fixer pass keeps the reviewed implementation slice pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and updates the handoff text so it accurately describes that commit's narrower behavior: canonical command order and canonical-name consistency between `command_cli_lookup_table()` and `command_names()`, plus the explicit operator-path mapping for the stable CLI control surface and its direct impact on `preview and apply or reject a patch`.
- Final fixer validation reran the required gate sequence from this worktree on `2026-04-23T21:42:16Z`; the metadata refresh below records that fresh verification on top of the already-landed code-side reviewer fixes.
- Exact canonical demo-path mapping for the reviewed slice:
  - operator terms: this hardens the stable CLI command surface used to reach `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and existing CLI handoff or export flows without silent parser or catalog drift
  - direct step advanced: `preview and apply or reject a patch`
  - explicit step sentence: this change directly strengthens `preview and apply or reject a patch` in the CLI-first MVP loop because it fails fast when canonical command order or canonical-name consistency drifts away from the catalog the operator-facing patch route depends on while Textual remains disabled
  - out of scope: no new workflow implementation for `open project/document`, `retrieve relevant material`, or export is claimed by this command-catalog contract slice
- Concrete reason this is not second-order work:
  - at reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, `catalog.py` makes `command_cli_contract()` fail fast if the lookup-table-derived canonical command order no longer matches `command_names()`. That prevents the operator-visible patch preview/apply route from silently drifting away from the catalog order the CLI and smoke tests expect, so this remains direct Milestone 3 CLI-loop hardening rather than generic cleanup.
- Shared-file basis for the high-risk packet:
  - lane-owned implementation: `src/qual/commands/**`
  - shared test touched by the reviewed commit: `tests/unit/test_commands_catalog.py`
  - shared handoff metadata updated by this fixer: `THREAD.md`, `THREAD_PACKET.md`
