# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Re-review scope is pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`).
- Reviewed implementation files at that commit:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- The branch now carries the code-side reviewer fixes as well as the handoff refresh. This fixer pass keeps the implementation slice untouched and updates the handoff text so it accurately describes the parser-surface validation, alias-drift regressions, and the narrow Milestone 3 CLI-compatibility hardening mapping now present on the branch rather than generic infra work.
- Final fixer validation reran the required gate sequence from this worktree on `2026-04-23T21:23:51Z`; the metadata refresh below records that fresh verification on top of the already-landed code-side reviewer fixes.
- Exact canonical demo-path mapping for the reviewed slice:
  - direct step advanced: step 3 `preview and apply or reject a patch`
  - canonical demo-path step(s) advanced: step 3 `preview and apply or reject a patch`, because the CLI command contract now fails fast on parser/catalog drift instead of silently changing the operator-visible patch preview/apply surface while Textual remains disabled
  - out of scope: no new step 1 `open project/document` or step 2 `retrieve relevant material` workflow coverage is claimed by this command-catalog contract slice
- Concrete reason this is not second-order work:
  - the `catalog.py` CLI contract now validates the full declared parser surface instead of only the deduplicated canonical-name projection. That prevents alias-level parser drift from silently changing the operator-visible CLI command surface used for patch preview/apply handling, so the deterministic Milestone 3 CLI loop stays smoke-testable instead of drifting unnoticed.
- Shared-file basis for the high-risk packet:
  - lane-owned implementation: `src/qual/commands/**`
  - shared test touched by the reviewed commit: `tests/unit/test_commands_catalog.py`
  - shared handoff metadata updated by this fixer: `THREAD.md`, `THREAD_PACKET.md`
