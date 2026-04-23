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
- Regenerated the handoff packet so it explicitly names the canonical demo-path steps from `AGENTS.md` that this command-catalog hardening strengthens, without broadening the implementation claim beyond existing CLI entrypoints.
- Tightened roadmap and product-vision mapping to the current repo documents and removed stale claims that were not supported by the actual diff.
- Re-ran the required gate suite and recorded the outcomes below.

## Kickoff Budget / Limits Compliance

- High-risk budget honored: `4` tasks, metadata-only fixer scope.
- Files edited by this fixer:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Reviewer Fix Closure

- Required fix 1 satisfied:
  - the packet now explicitly maps this slice to the current CLI MVP flow in `ROADMAP.md` (`vault -> context -> run -> patch -> export`) and names the exact canonical demo-path stages it strengthens through the existing entrypoints `project-open`, `retrieval`, `patch-review`, and `export-handoff`.
- Required fix 2 satisfied:
  - the packet now states the concrete blocker removed on that path: parser and catalog drift could silently mutate the operator-facing CLI smoke loop while still leaving canonical command names looking valid, which risks running the wrong parser surface in the active MVP loop before export handoff.
- Required fix 3 satisfied:
  - the packet now keeps the risk and scope framing exact to the reviewed slice: one lane-owned command-catalog file plus one approved shared regression file, with no routing, provider, or broader CLI entrypoint behavior changes.

## Canonical Demo-Path Mapping

- Exact existing CLI entrypoints this slice hardens:
  - `project-open`
  - `retrieval`
  - `patch-review`
  - `export-handoff`
- Exact CLI MVP flow alignment:
  - `ROADMAP.md` requires the current CLI MVP flow `vault -> context -> run -> patch -> export`.
  - In this lane-owned slice, those operator stages stay executable through `project-open` for open/bootstrap, `retrieval` for context gathering, `patch-review` for review before apply or reject, and `export-handoff` for the export stage after persist.
- Explicit AGENTS sentence:
  - this slice makes the canonical demo-path steps `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and `save and continue` more real by keeping the existing CLI entrypoints `project-open`, `retrieval`, `patch-review`, and `export-handoff` deterministic and drift-resistant.
- Scope-tightened plan-alignment note:
  - this is direct CLI contract work for the active `feat-commands` lane because `ROADMAP.md` requires the MVP CLI flow to remain executable and `PRODUCT_VISION.md` keeps the CLI as a first-class operator surface; this slice only hardens the existing command catalog and parser contract for already-exposed entrypoints in that loop.
- Why these are the right steps:
  - `AGENTS.md` defines the canonical demo path in operator terms, including `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and `save and continue`.
  - `src/qual/commands/catalog.py` exposes the existing operator-visible CLI entrypoints that cover those stages as `project-open`, `retrieval`, `patch-review`, and `export-handoff`.
  - `command_cli_contract()` and `tests/unit/test_commands_catalog.py` keep that exposed CLI contract deterministic by rejecting parser-surface drift before the operator-facing path can silently change.
- Concrete operator-facing effect:
  - the existing CLI route through the MVP flow fails fast on parser drift instead of silently presenting a stale, reordered, or alias-substituted command surface to operators and smoke tests.
- Concrete blocker removed:
  - parser and catalog drift could previously leave the CLI-first MVP loop appearing intact while the operator-facing command surface had silently diverged through alias substitution, reorder, or other parser-surface mutations.
  - that failure mode is a real blocker on the current `vault -> context -> run -> patch -> export` loop because smoke checks and operators could hit a stale parser surface at `project-open`, `retrieval`, `patch-review`, or `export-handoff` without an immediate contract failure.
  - this contract guard removes that blocker by failing fast at the command boundary the current CLI smoke path depends on.
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
  - this handoff is high-risk only because the reviewed implementation includes one approved shared regression file; the implementation slice itself remains one lane-owned command-catalog file plus that shared test file, with no routing, provider, or broader CLI entrypoint changes.
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
  - the remaining regression risk is future command-surface expansion: a follow-up could add or rename parser entrypoints without updating `_CLI_ENTRYPOINTS`, the catalog contract, and the smoke expectations together.
  - that residual risk is acceptable for merge because this diff is intentionally narrow, every required local gate passes, and the guarded failure mode is now an immediate contract error during CLI validation rather than silent operator-facing drift in the active MVP path.
  - post-merge validation the integrator should perform: after the next command-surface edit, run the CLI smoke path and confirm the existing entrypoints still resolve without contract drift.
- Blockers:
  - none.

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 3 (`Product Readiness`): this is user-facing contract-locking work on the CLI surface, specifically keeping command-surface changes documented, intentional, and deterministic before publish.
- `ROADMAP.md` active MVP emphasis `feat-commands`: this keeps the CLI command surface deterministic while that lane remains active.
- `ROADMAP.md` MVP CLI flow exit criterion: keeps the current `vault -> context -> run -> patch -> export` loop executable against the same engine-facing command surface by preventing silent parser/catalog drift on the entrypoints this lane owns.
- Canonical demo-path steps advanced: `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and `save and continue`, via the existing CLI entrypoints `project-open`, `retrieval`, `patch-review`, and `export-handoff`.
- Canonical demo-path step made more real: this slice makes those existing operator-facing CLI steps more reliable by preventing silent parser/catalog drift in the current CLI MVP loop.
- Concrete blocker removed on that demo path: parser/catalog drift can no longer silently change the operator-facing CLI contract for the current `vault -> context -> run -> patch -> export` smoke path.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`): limited here to the "engine contracts come first" requirement; this change hardens the canonical engine command contract that the CLI path consumes, without claiming new UI, workflow, persistence, or audit behavior.

### Routing / Provider Impact Note

- None.

### Proposed `README.md` Patch Text

- None.
