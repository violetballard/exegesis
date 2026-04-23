# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Reviewed implementation commit pinned for re-review: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Metadata-only packet refresh commits after that implementation commit are out of review scope unless a regenerated handoff says otherwise.
- Reviewed implementation files for the fixed branch state:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- The fixed branch behavior under review:
  - `command_cli_contract()` now rejects parser-surface drift, including token add, remove, alias substitution, or reorder cases that would otherwise leave canonical command names unchanged.
  - the regression coverage proves that rejected drift behavior on the canonical CLI command surface.
- Exact canonical CLI steps advanced by this work:
  - `project-open`
  - `retrieval`
  - `patch-review`
  - `export-handoff`
- Plan-aligned roadmap and vision grounding:
  - `ROADMAP.md` Milestone 2 (`Test Hardening`): adds targeted parser-edge regressions identified during review.
  - `ROADMAP.md` Milestone 3 (`Product Readiness`): supports locking intentional user-facing command contracts.
  - `ROADMAP.md` active MVP emphasis `feat-commands`: keeps the CLI command surface deterministic while that lane is active.
  - `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`): preserves a stable CLI operator surface.
- Shared-file basis for this high-risk handoff:
  - lane-owned implementation: `src/qual/commands/**`
  - approved shared regression file in reviewed scope: `tests/unit/test_commands_catalog.py`
  - metadata files refreshed by this fixer: `THREAD.md`, `THREAD_PACKET.md`
