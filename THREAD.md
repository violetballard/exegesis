# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Re-review scope is pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`).
- Reviewed implementation files at that commit:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- This fixer pass is metadata-only. It does not change the reviewed implementation slice; it regenerates the handoff as a completed high-risk AGENTS packet and adds the missing canonical demo-path mapping required by review.
- Exact canonical demo-path mapping for the reviewed slice:
  - direct step advanced: step 2 `retrieve relevant material`
  - immediate follow-on step hardened: step 3 `preview and apply or reject a patch`
  - out of scope: no new step 1 `open project/document` workflow coverage is claimed beyond preserving the existing CLI entrypoint into the retrieval path
- Concrete reason this is not second-order work:
  - the `catalog.py` contract check added at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` prevents parser and catalog drift from silently changing the operator-visible CLI command surface used to reach retrieval and its immediate preview/apply follow-on. That keeps the deterministic CLI loop smoke-testable instead of allowing the MVP operator path to drift unnoticed.
- Shared-file basis for the high-risk packet:
  - lane-owned implementation: `src/qual/commands/**`
  - shared test touched by the reviewed commit: `tests/unit/test_commands_catalog.py`
  - shared handoff metadata updated by this fixer: `THREAD.md`, `THREAD_PACKET.md`
