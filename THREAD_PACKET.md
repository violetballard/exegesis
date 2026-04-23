# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: regenerate the handoff packet so it matches the already-fixed command-catalog branch state, names the exact canonical CLI steps the contract hardening protects, and maps the change to the current repo roadmap and product-vision language.
- Risk reason: the reviewed implementation includes one approved shared test file, and this fixer refreshes shared handoff metadata for re-review.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Rebuild the handoff packet around the current fixed branch state.
2. Add the exact canonical CLI-step mapping the reviewer requested.
3. Tighten roadmap and product-vision claims so they match the actual diff.
4. Re-run the required gate suite and record the results.

### Early Review Triggers

- Before first edit to any shared or integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing or config behavior.

### Stop Triggers

- Unresolved test, lint, or typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (short updates)

- Plan complete: handoff scope reset to the current fixed command-catalog implementation plus metadata refresh only.
- First green tests: recorded below from the final rerun in this fixer pass.
- Before risky/shared file edit: this fixer only updates shared handoff metadata; no new runtime shared-file edits are introduced.
- Ready for handoff: packet and gate results now match the current branch state.

## Review Basis

- Review scope covers the current fixed branch state for the command CLI contract.
- Reviewed implementation commit pinned for re-review: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Metadata-only packet refresh commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are out of implementation review scope unless a regenerated handoff explicitly broadens the review basis.
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`

## Scope Completed

- Kept the implementation review basis pinned to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Regenerated the handoff packet so it explicitly maps this change to the current MVP CLI path in `ROADMAP.md`: `vault -> context -> run -> patch -> export`, narrowed here to the catalog's exposed command-flow steps `project-open`, `retrieval`, `patch-review`, and `export-handoff`.
- Tightened roadmap and product-vision mapping to the current repo documents and removed stale claims that were not supported by the actual diff.
- Re-ran the required gate suite and recorded the outcomes below.

## Kickoff Budget / Limits Compliance

- High-risk budget honored: `4` tasks, metadata-only fixer scope.
- Files edited by this fixer:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Reviewer Fix Closure

- Required fix 1 satisfied:
  - the packet now names the exact canonical demo-path step this slice strengthens, keeps the claim narrow to the touched command surface, and ties that statement directly to `project-open`, `retrieval`, `patch-review`, and `export-handoff`.
- Required fix 2 satisfied:
  - the packet now includes a scope-tightened plan-alignment note explaining why this is active MVP work: `feat-commands` is on the current roadmap emphasis, the MVP must run through the CLI-first path while `feat-console` stays disabled, and this diff hardens that existing CLI contract rather than adding second-order infrastructure.
- Required fix 3 satisfied:
  - the packet now replaces the generic `Risk: HIGH` label with a concrete remaining-risk statement, why that residual risk is acceptable for merge, and the specific post-merge validation the integrator should watch.

## Canonical Demo-Path Mapping

- Exact documented MVP path this change strengthens:
  - `vault -> context -> run -> patch -> export` (`ROADMAP.md`)
- Exact catalog steps on that path that this slice hardens:
  - `project-open`
  - `retrieval`
  - `patch-review`
  - `export-handoff`
- Canonical demo-path step advanced:
  - `open project/document` and `continue working`, by keeping the CLI command contract deterministic and drift-resistant while the engine-first MVP loop remains CLI-first.
- Explicit AGENTS sentence:
  - this slice makes the existing CLI-first operator path more real by stabilizing the command surface for `project-open`, `retrieval`, `patch-review`, and `export-handoff`.
- Scope-tightened plan-alignment note:
  - this is Milestone 3 work because `feat-commands` is part of the current MVP emphasis, `ROADMAP.md` requires the CLI to execute the MVP flow `vault -> context -> run -> patch -> export`, and `PRODUCT_VISION.md` keeps the CLI as the first-class operator surface while `feat-console` remains disabled; hardening the existing command catalog and parser contract therefore advances the active engine-side demo path rather than second-order infrastructure.
- Why these are the right steps:
  - `ROADMAP.md` defines the active CLI-first MVP path as `vault -> context -> run -> patch -> export`.
  - `src/qual/commands/catalog.py` exposes the currently implemented command-flow steps for that path as `project-open -> retrieval -> patch-review -> ... -> export-handoff`.
  - `command_cli_contract()` and `tests/unit/test_commands_catalog.py` keep that exposed CLI contract deterministic by rejecting parser-surface drift before the operator-facing path can silently change.
- Concrete operator-facing effect:
  - the existing CLI route through the MVP flow fails fast on parser drift instead of silently presenting a stale, reordered, or alias-substituted command surface to operators and smoke tests.
- Concrete blocker removed:
  - parser/catalog drift could previously leave the CLI-first MVP loop appearing intact while the operator-facing command surface had silently diverged from the intended `project-open -> retrieval -> patch-review -> export-handoff` path through alias substitution, reorder, or other parser-surface mutations.
  - because the MVP depends on the CLI smoke path while the future console surface stays downstream of engine contracts, this contract guard removes a first-order blocker to trusting that loop during current roadmap acceptance.
- Out of scope:
  - this slice does not add new command behavior, new flags, or new workflow implementation; it only hardens the existing command contract for the already-exposed MVP path.

## Shared-Path Approval Basis

- Lane-owned implementation in the reviewed scope:
  - `src/qual/commands/catalog.py`
- Approved shared-by-exception regression file in the reviewed implementation scope:
  - `tests/unit/test_commands_catalog.py`
- Integrator-locked implementation files touched in the reviewed scope:
  - none
- Risk classification note:
  - this handoff is high-risk because the reviewed implementation includes one approved shared regression file, not because any integrator-locked implementation file was edited.
- Shared metadata files changed by this fixer:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Regenerated the handoff packet around the current fixed branch state.
2. Added the exact canonical CLI-step mapping for the contract hardening.
3. Tightened roadmap and product-vision claims to match the actual diff and current repo docs.
4. Re-ran the required gate suite and recorded the results.

### Files Changed

- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata files changed by this fixer:
  - `THREAD.md`
  - `THREAD_PACKET.md`

### Commands Run and Outcomes

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

### Risks / Blockers

- Remaining risk:
  - future command additions still depend on keeping `_CLI_ENTRYPOINTS`, the catalog, and smoke expectations in sync; if a later change updates parser entrypoints without updating the catalog contract or these regression tests, the CLI surface could regress until the guard trips.
  - that residual risk is acceptable for merge because the reviewed runtime change is narrow, all local gates pass, and the failure mode is now explicit `ValueError` drift detection instead of silent operator-surface skew.
  - post-merge validation the integrator should perform: confirm the canonical CLI smoke path still covers `project-open -> retrieval -> patch-review -> export-handoff` after the next command-surface edit or command addition.
- Blockers:
  - none.

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 1 (`Bootstrap Flow Stabilization`): this hardens command behavior on the manual CLI smoke path by keeping the parser-visible command contract deterministic.
- `ROADMAP.md` Milestone 2 (`Test Hardening`): this adds the targeted parser-edge regression coverage the roadmap calls out for missing command-level cases.
- `ROADMAP.md` Milestone 5 (`A2UI Presentation Layer`) exit criterion: this keeps the CLI MVP flow (`vault -> context -> run -> patch -> export`) stable against the same engine `PolicyGate` by failing fast when the parser surface drifts from the catalog.
- `ROADMAP.md` active MVP emphasis `feat-commands`: this keeps the CLI command surface deterministic while that lane remains active.
- Canonical demo-path step advanced: `open project/document` and `continue working`, by keeping the CLI command contract deterministic and drift-resistant while the engine-first MVP loop remains CLI-first.
- Canonical demo-path step made more real: this slice makes the existing CLI-first operator path more real by stabilizing the command surface for `project-open`, `retrieval`, `patch-review`, and `export-handoff` within the MVP flow `vault -> context -> run -> patch -> export`.
- Concrete blocker removed on that demo path: parser/catalog drift can no longer silently change the operator-facing CLI contract for the CLI-first MVP smoke loop while Textual remains disabled.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`): limited here to the "engine contracts come first" requirement; this change hardens the canonical engine command contract that the CLI path consumes, without claiming new UI, workflow, persistence, or audit behavior.

### Routing / Provider Impact Note

- None.

### Proposed `README.md` Patch Text

- None.
