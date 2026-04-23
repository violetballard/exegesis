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
- Canonical demo-path step advanced:
  - `open project/document` and `continue working`, by keeping the CLI command contract deterministic and drift-resistant while the engine-first MVP loop remains CLI-first.
- Explicit AGENTS sentence:
  - this slice makes the existing CLI-first operator path more real by stabilizing the command surface for `project-open`, `retrieval`, `patch-review`, and `export-handoff`.
- Scope-tightened plan-alignment note:
  - this is Milestone 3 work because `feat-commands` is part of the current MVP emphasis and `ROADMAP.md` requires the CLI to execute the MVP flow `vault -> context -> run -> patch -> export` while `feat-console` remains inactive; hardening the existing command catalog and parser contract is therefore direct CLI-compatibility work for the active engine path, not second-order infrastructure.
- Concrete blocker removed on that path:
  - parser/catalog drift can no longer silently change the operator-facing CLI command surface for `project-open`, `retrieval`, `patch-review`, and `export-handoff` in the active MVP smoke loop while Textual remains disabled.
- Plan-aligned roadmap and vision grounding:
  - `ROADMAP.md` Milestone 1 (`Bootstrap Flow Stabilization`): hardens command behavior on the manual CLI smoke path by keeping the parser-visible command contract deterministic.
  - `ROADMAP.md` Milestone 2 (`Test Hardening`): adds the targeted parser-edge regression coverage the roadmap calls out for missing command-level cases.
  - `ROADMAP.md` Milestone 5 (`A2UI Presentation Layer`) exit criterion: keeps the CLI MVP flow (`vault -> context -> run -> patch -> export`) stable against the same engine `PolicyGate` by failing fast when the parser surface drifts from the catalog.
  - `ROADMAP.md` active MVP emphasis `feat-commands`: keeps the CLI command surface deterministic while that lane is active.
  - `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`): limited here to the "engine contracts come first" requirement, not to any new UI, workflow, persistence, or audit behavior.
- Shared-file basis for this high-risk handoff:
  - lane-owned implementation: `src/qual/commands/**`
  - approved shared-by-exception regression file in reviewed implementation scope: `tests/unit/test_commands_catalog.py`
  - integrator-locked implementation files in reviewed scope: none
  - risk stays high because of the approved shared regression file only, not because any integrator-locked implementation file was edited
  - remaining regression risk: later command additions still need `_CLI_ENTRYPOINTS`, the catalog, and smoke expectations to move together; if a follow-up edits only one of those surfaces, operators will now see an explicit contract failure on the CLI-first path instead of silent drift
  - why acceptable for merge: the current diff is narrow, all required local gates pass, and the new failure mode is loud and reviewable at the same CLI boundary the MVP currently relies on
  - post-merge validation to watch: integrator should confirm the canonical CLI smoke path still covers `project-open -> retrieval -> patch-review -> export-handoff` after the next command-surface edit
  - metadata files refreshed by this fixer: `THREAD.md`, `THREAD_PACKET.md`
