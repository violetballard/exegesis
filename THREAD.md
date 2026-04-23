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
- Exact existing CLI entrypoints this work hardens:
  - `project-open`
  - `retrieval`
  - `patch-review`
  - `export-handoff`
- Primary AGENTS plan-alignment statement:
  - this slice advances the broader CLI operator path that currently stands in for the MVP demo loop while Textual remains disabled, by keeping the existing parser-facing entrypoints `project-open`, `retrieval`, `patch-review`, and `export-handoff` deterministic for the `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and `save and continue` steps.
- Scope-tightened plan-alignment note:
  - this is direct CLI contract work for the active `feat-commands` lane because `ROADMAP.md` requires the MVP CLI flow `vault -> context -> run -> patch -> export` to stay executable and `PRODUCT_VISION.md` keeps the CLI as a first-class operator surface. It does not add new command behavior.
- Concrete blocker removed on that path:
  - parser/catalog drift can no longer silently swap, reorder, or alias-substitute the operator-facing CLI parser surface in the active `vault -> context -> run -> patch -> export` smoke loop while canonical command names still appear valid.
- Plan-aligned roadmap and vision grounding:
  - `ROADMAP.md` Milestone 3 (`Product Readiness`): this is user-facing contract-locking work on the CLI surface, keeping command-surface changes documented, intentional, and deterministic before publish.
  - `ROADMAP.md` CLI MVP flow exit criterion: keeps the required CLI path `vault -> context -> run -> patch -> export` executable against the engine by preventing silent command-surface drift on the exposed steps this lane owns.
  - `ROADMAP.md` active MVP emphasis `feat-commands`: keeps the CLI command surface deterministic while that lane is active.
  - `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`): limited here to the "engine contracts come first" requirement, not to any new UI, workflow, persistence, or audit behavior.
- Shared-file basis for this high-risk handoff:
  - lane-owned implementation: `src/qual/commands/**`
  - approved shared-by-exception regression file in reviewed implementation scope: `tests/unit/test_commands_catalog.py`
  - integrator-locked implementation files in reviewed scope: none
  - risk stays high because of the approved shared regression file only; the implementation slice remains one lane-owned command-catalog file plus that shared test file, with no routing, provider, or broader CLI entrypoint changes
  - remaining regression risk: a later command-surface expansion could change parser entrypoints without updating `_CLI_ENTRYPOINTS`, the catalog contract, and smoke expectations together
  - why acceptable for merge: the current diff is narrow, all required local gates pass, and the new failure mode is loud and reviewable at the same CLI boundary the MVP currently relies on
  - post-merge validation to watch: integrator should confirm the canonical CLI smoke path still resolves the existing entrypoints after the next command-surface edit
  - metadata files refreshed by this fixer: `THREAD.md`, `THREAD_PACKET.md`
