# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `fixer reviewer packet correction`
- Packet refresh basis: `realigned the handoff to the actual reviewed implementation slice after the reviewer flagged inconsistent traceability, stale roadmap or vision mapping, and a missing explicit patch-step mapping`
- Post-fixer verification: `2026-04-24T10:07:45Z UTC gate rerun confirmed this packet correction matches the current branch state; the current refresh is metadata-only and keeps the reviewed implementation scope pinned to f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `handoff_packets/feat-commands.md`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: make the canonical `open project/document`, `retrieve`, and `preview and apply or reject a patch` steps more real by keeping the operator-visible command contract locked to the parser/catalog boundary, so deterministic CLI contract validation protects the current engine-first CLI fallback across the `project-open` / `retrieval` / `patch-review` smoke path while interactive clients stay secondary.
- Risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Lock the live CLI parser surface to the command catalog so parser-surface drift fails closed instead of silently changing the operator-facing contract.
2. Add regression coverage for parser-surface alignment and catalog-drift rejection in the command contract tests.
3. Regenerate the handoff packet so the re-review basis points to the actual implementation commit, the canonical demo-path mapping is explicit, and the roadmap or vision mapping stays narrow.
4. Re-run the required gates and record the outcomes against the unchanged reviewed implementation scope.

### Early Review Triggers

- before first edit to any shared or integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing or config behavior

### Stop Triggers

- unresolved test, lint, or typecheck failure after `2` focused fix attempts
- unresolved `make scope-check`
- budget, size, or time limit hit

### High-Risk Audit Note

- Shared-test exception reason: the regression proving contract drift rejection lives in `tests/unit/test_commands_catalog.py`, which is shared-by-approval rather than lane-owned.
- Command-contract risk reason: this slice hardens the operator-visible parser/catalog boundary in `src/qual/commands/catalog.py`, so the stricter high-risk kickoff template applied even though the code change stayed narrow.
- Auditability result: the risk reason, early review triggers, stop triggers, scope goal, 4-task cap, and approval basis are now all recorded directly in the handoff artifacts for re-review.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- Exact implementation basis for re-review:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
- Approval basis pin for re-review:
  - Only `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py` are part of the implementation approval basis.
  - Later `docs(commands)` commits are packet-refresh metadata only and must not be treated as widening the reviewed implementation scope.
- Current packet refresh traceability: later `docs(commands)` commits are metadata-only and update only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`.
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation summary:
  - `command_cli_contract()` now validates that the live parser entrypoint projection stays identical to the declared command catalog projection, and raises `ValueError` when the parser surface drifts from the catalog.
  - Regression coverage proves the command contract stays aligned to the declared parser surface and fails fast if extra accepted aliases, missing canonical tokens, or reordered entrypoints are introduced.

## Scope Completed

- Hardened `command_cli_contract()` so the live CLI parser entrypoint projection must match the declared command catalog projection.
- Added focused regressions for parser-surface alignment and command-catalog drift rejection.
- Kept the slice narrow: command-contract hardening and targeted tests only. No provider, routing, persistence, retrieval, or UI-surface behavior changed.

## Canonical Demo-Path Mapping

- Canonical demo-path step(s) advanced: `open project/document`, `retrieve`, and `preview and apply or reject a patch`.
- Roadmap loop mapping for those same steps:
  - `open project/document` corresponds to the current MVP loop's `vault` and `context` entry boundary via `project-open`.
  - `retrieve` corresponds to the current MVP loop's `context` and `run` handoff boundary via `retrieval`.
  - `preview and apply or reject a patch` corresponds to the current MVP loop's `patch` boundary via `patch-review`.
- Required packet statement: this change makes `open project/document`, `retrieve`, and `preview and apply or reject a patch` more real by forcing the command contract to stay catalog-locked and fail closed before the operator reaches the wrong CLI verb set on the current engine-first `project-open` / `retrieval` / `patch-review` smoke path.
- Concrete blocker removed: parser-surface drift between the live parser entrypoints and the declared catalog can no longer pass silently. That removes the concrete CLI-fallback blocker where silent parser drift, including extra accepted aliases, could change the `project-open` / `retrieval` / `patch-review` operator contract.
- `AGENTS.md` compliance note: every active lane task in this packet now names the exact canonical demo-path step it advances, and this handoff states the concrete blocker removed at that step.
- Scope-tightening statement: this slice claims command-contract hardening for the current engine-first `project-open` / `retrieval` / `patch-review` smoke path only. Deterministic CLI contract validation preserves the operator-facing bootstrap, context-basket, and diff-preview surfaces needed by the current CLI fallback while Textual remains disabled, and it does not claim new retrieval internals, patch application, persistence, audit-path, export, or broader workflow behavior.
- Review-basis exclusion: `terminal` and `export-handoff` remain outside this packet's approval basis; they are mentioned only because the shared command catalog still contains those aliases, not because this slice proves their runtime behavior.
- Smoke-test evidence:
  - `tests/unit/test_commands_catalog.py` proves `command_cli_contract()` returns the declared parser surface and fails fast when parser-surface drift is introduced.
  - `tests/unit/test_commands_catalog.py` also proves the command route coverage stays pinned to the smoke route entry for patch review: `("patch-review", "diff-preview", ("diff-preview", "diff"))` in `test_command_cli_route_summary_tracks_the_smoke_route()` and `test_command_cli_route_contract_tracks_the_smoke_surface()`.
- Plan-alignment note: this slice keeps the explicit smoke-path mapping requested by review while aligning the packet to the current repo truth sources. `ROADMAP.md` keeps `feat-commands` in the active implementation emphasis, Milestone 1 calls for command and diff-preview hardening, and Milestone 2 explicitly calls out missing targeted parser-edge cases from review. This guard removes a concrete blocker by failing fast if parser or catalog drift would silently change the CLI verb surface along the current `project-open` / `retrieval` / `patch-review` smoke path.

## Approved Exception Note

- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approval owner: the integrator-managed branch policy for `codex/feat-commands`
- Approval source: `scripts/scope-check.sh` `is_approved_shared_test()` branch allowlist for `codex/feat-commands*`
- Additional ownership source: `THREAD_OWNERSHIP.md` keeps lane ownership on `src/qual/commands/**`; the non-owned test edit is a shared-by-approval exception with explicit branch allowlist approval, not an integrator-locked edit
- Approval basis: shared regression coverage is required to prove the review-step parser contract
- Scope-check allowance used: `not required`
- Integrator-locked edits in this slice: `none`

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. `open project/document`, `retrieve`, `preview and apply or reject a patch`: locked the live CLI command contract to the command catalog so parser-surface drift fails closed before the operator reaches the `project-open`, `retrieval`, or `patch-review` verb sets.
2. `open project/document`, `retrieve`, `preview and apply or reject a patch`: added focused regression coverage for parser-surface alignment and command-catalog drift rejection in `tests/unit/test_commands_catalog.py` so the CLI smoke surface for those steps stays deterministic.
3. `open project/document`, `retrieve`, `preview and apply or reject a patch`: regenerated the handoff packet so the re-review basis points to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, the roadmap or vision mapping stays narrow, and the canonical demo-path steps are stated explicitly per reviewer request.
4. `open project/document`, `retrieve`, `preview and apply or reject a patch`: re-ran the required gates and recorded the outcomes against the current reviewed implementation scope so the packet stays tied to a verified command-contract slice.

### Files Changed

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

### Commands Run and Outcomes

- `make scope-check`: `PASSED`
- `./quality-format.sh --check`: `PASSED`
- `./quality-lint.sh`: `PASSED`
- `./quality-test.sh`: `PASSED`
- `./typecheck-test.sh`: `PASSED`
- `make ci`: `PASSED`
- Gate attribution note: these gates were rerun at `2026-04-24T10:07:45Z UTC` against the current branch state while the reviewed implementation scope remains pinned to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; the current packet refresh itself is metadata-only.

### Risks / Blockers

- Risks:
  - future command-surface changes must keep `_CLI_ENTRYPOINTS` and the shared regression suite aligned or the contract will fail fast by design
- Blockers:
  - none

## Required Handoff Fields

### Explicit CLI smoke-path mapping

- `open project/document`
- `retrieve`
- `preview and apply or reject a patch`
- This change makes those steps more real by keeping the command contract catalog-locked instead of letting parser-surface drift pass silently in the current engine-first CLI fallback path from `project-open` through `retrieval` to `patch-review`.
- Concrete blocker removal: downstream CLI fallback consumers can no longer silently accept a contract where the parser-derived command surface diverges from the declared command catalog, including extra accepted aliases, which keeps the `project-open` / `retrieval` / `patch-review` smoke path deterministic.
- Smoke-test evidence for these steps is explicit in `tests/unit/test_commands_catalog.py`: the command contract now matches the declared parser surface and raises immediately when parser-surface drift is introduced.

### Roadmap item(s) affected

- `ROADMAP.md` active implementation emphasis: `feat-commands`
- `ROADMAP.md` Milestone 1 scope: `Command and diff-preview behavior hardening`
- `ROADMAP.md` Milestone 2 remaining work: `Add missing targeted cases identified during reviews (parser edges, persistence edge cases)`
- Scope-tightening statement: this is CLI command-contract hardening for the `project-open` / `retrieval` / `patch-review` smoke path, preserving the operator-facing bootstrap, context-basket, and diff-preview verb surface rather than broadening workflow behavior.
- Proven command-surface level only: the claim is limited to the tested smoke-route entries `project-open -> bootstrap`, `retrieval -> context-basket`, and `patch-review -> diff-preview/diff`.
- Explicit exclusion: `terminal` and `export-handoff` are not part of the approval basis for this packet.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 `Operator-first control surface`
- Exact requirement advanced: `CLI remains a first-class surface for development and reliability.`
- This slice narrows to the `project-open` / `retrieval` / `patch-review` command contract only. It does not claim A2UI payload generation, persistence, audit hooks, auditable generation, retrieval internals, or broader workflow traceability progress.
- Evidence anchor: the claimed product-surface support is the tested CLI route coverage for those smoke-path steps in `tests/unit/test_commands_catalog.py`, not an unproven broader engine-loop claim.

### Routing / Provider Impact Note

- None. This diff only hardens local command-contract behavior for the current MVP `project-open` / `retrieval` / `patch-review` smoke surface.

### Scope-Check / Ownership Note

- Shared-by-approval edits: `YES`
- Shared-by-approval path included: `tests/unit/test_commands_catalog.py`
- Shared-file approval basis: `THREAD_OWNERSHIP.md` leaves `tests/unit/test_commands_catalog.py` outside the lane-owned path, and `scripts/scope-check.sh` `is_approved_shared_test()` allowlists that shared test file for `codex/feat-commands*`
- Integrator-locked edits: `NO`
- Integrator-locked paths included: `none`
