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
- Exact documented MVP path this work strengthens:
  - `vault -> context -> run -> patch -> export`
- Exact catalog steps on that path advanced by this work:
  - `project-open`
  - `retrieval`
  - `patch-review`
  - `export-handoff`
- Exact canonical demo-path steps strengthened by this work:
  - `vault` entry via `project-open`
  - `context` via `retrieval`
  - `patch` via `patch-review`
  - `export` via `export-handoff`
- Explicit AGENTS sentence:
  - this slice makes the canonical CLI demo-path steps `vault -> context -> patch -> export` more real by stabilizing the exposed commands `project-open`, `retrieval`, `patch-review`, and `export-handoff`.
- Scope-tightened plan-alignment note:
  - this is Milestone 3 work because `ROADMAP.md:54` calls for locking user-facing output contracts, `ROADMAP.md:65` requires contract changes to be documented and intentional, `ROADMAP.md:105` keeps the CLI MVP path active, and `PRODUCT_VISION.md:37-40` keeps the CLI as the first-class operator surface while `feat-console` remains inactive. Hardening the existing command catalog and parser contract is therefore direct CLI-compatibility work for the active engine path, not second-order infrastructure.
- Concrete blocker removed on that path:
  - parser/catalog drift can no longer silently change the operator-facing CLI command surface for `project-open`, `retrieval`, `patch-review`, and `export-handoff` in the active MVP smoke loop while Textual remains disabled.
- Plan-aligned roadmap and vision grounding:
  - `ROADMAP.md` Milestone 3 (`Product Readiness`): this is user-facing contract-locking work on the CLI surface, keeping command-surface changes documented, intentional, and deterministic before publish.
  - `ROADMAP.md` CLI MVP flow exit criterion: keeps the required CLI path `vault -> context -> run -> patch -> export` executable against the engine by preventing silent command-surface drift on the exposed steps this lane owns.
  - `ROADMAP.md` active MVP emphasis `feat-commands`: keeps the CLI command surface deterministic while that lane is active.
  - `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`): limited here to the "engine contracts come first" requirement, not to any new UI, workflow, persistence, or audit behavior.
- Shared-file basis for this high-risk handoff:
  - lane-owned implementation: `src/qual/commands/**`
  - approved shared-by-exception regression file in reviewed implementation scope: `tests/unit/test_commands_catalog.py`
  - integrator-locked implementation files in reviewed scope: none
  - risk stays high because of the approved shared regression file only, not because any integrator-locked implementation file was edited
  - remaining regression risk: a later command-surface expansion could change parser entrypoints without updating `_CLI_ENTRYPOINTS`, the catalog contract, and smoke expectations together, which would break the CLI-first demo path at the command boundary for `project-open`, `retrieval`, `patch-review`, or `export-handoff`
  - why acceptable for merge: the current diff is narrow, all required local gates pass, and the new failure mode is loud and reviewable at the same CLI boundary the MVP currently relies on
  - post-merge validation to watch: integrator should confirm the canonical CLI smoke path still covers `project-open -> retrieval -> patch-review -> export-handoff` after the next command-surface edit
  - metadata files refreshed by this fixer: `THREAD.md`, `THREAD_PACKET.md`
