# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `8e747334f4da2d5486e15088979a36184c8c9116`
- Packet refresh role: `fixer reviewer packet verification refresh`
- Packet refresh basis: `preserved the narrowed reviewer-fix packet wording, then reran the full required gate set and refreshed the metadata-only handoff timestamps without widening the reviewed implementation scope`
- Post-fixer verification: `2026-04-24T11:07:42Z UTC full required gate rerun confirmed this packet correction still matches the current branch state; the current refresh is metadata-only and keeps the reviewed implementation scope pinned to 8e747334f4da2d5486e15088979a36184c8c9116`
- Packet-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `handoff_packets/feat-commands.md`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: make the canonical `continue working without losing context` step more real by removing a concrete blocker at the CLI fallback boundary: silent parser/catalog drift on the operator-visible `project-open` / `retrieval` / `patch-review` command surface. The reviewed evidence stays limited to those supporting smoke-path steps while interactive clients remain secondary.
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

- Shared-test exception reason: the regression proving contract drift rejection for the `continue working without losing context` step lives in `tests/unit/test_commands_catalog.py`, because that shared test is where the supporting `project-open` / `retrieval` / `patch-review` smoke path is pinned to the catalog-locked CLI surface.
- Shared-test exception statement: the only non-owned edit stays justified by that same mapping and blocker removal, because `tests/unit/test_commands_catalog.py` is the evidence that the supporting smoke path remains deterministic on the CLI fallback route instead of silently drifting away from `continue working without losing context`.
- Command-contract risk reason: this slice hardens the operator-visible parser/catalog boundary in `src/qual/commands/catalog.py`, so the stricter high-risk kickoff template applied even though the code change stayed narrow.
- Auditability result: the risk reason, early review triggers, stop triggers, scope goal, 4-task cap, and approval basis are now all recorded directly in the handoff artifacts for re-review.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- Exact implementation basis for re-review:
  - `8e747334f4da2d5486e15088979a36184c8c9116` (`feat(commands): validate full CLI token projection`)
- Approval basis pin for re-review:
  - Only `8e747334f4da2d5486e15088979a36184c8c9116`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py` are part of the implementation approval basis.
  - The current packet-refresh commit is metadata-only and must not be treated as widening the reviewed implementation scope.
- Current packet refresh traceability: the current packet-refresh commit is metadata-only and updates only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`.
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation summary:
  - `command_cli_contract()` now validates that the live parser entrypoint projection stays identical to the declared command catalog projection, then derives the expected token sequence and lookup table from that same authoritative surface.
  - Regression coverage proves the command contract stays aligned to the declared parser surface and fails fast if extra accepted aliases, missing canonical tokens, lookup-table substitutions, or reordered entrypoints are introduced.

## Scope Completed

- Hardened `command_cli_contract()` so the live CLI parser entrypoint projection must match the declared command catalog projection.
- Added focused regressions for parser-surface alignment and command-catalog drift rejection.
- Kept the slice narrow: command-contract hardening and targeted tests only. No provider, routing, persistence, retrieval, or UI-surface behavior changed.

## Canonical Demo-Path Mapping

- Primary canonical demo-path step advanced: `continue working without losing context`.
- Supporting smoke-path steps strengthened for that primary step:
  - `open project/document` corresponds to the current MVP loop's `vault` and `context` entry boundary via `project-open`.
  - `retrieve relevant material` corresponds to the current MVP loop's `context` and `run` handoff boundary via `retrieval`.
  - `preview and apply or reject a patch` corresponds to the current MVP loop's `patch` boundary via `patch-review`.
- Required packet statement: this change makes `continue working without losing context` more real by forcing the operator-visible `project-open` / `retrieval` / `patch-review` command surface to stay catalog-locked and fail closed instead of silently drifting while Textual remains disabled.
- Concrete blocker removed: parser-surface drift between the live parser entrypoints and the declared catalog can no longer pass silently. That removes the concrete blocker on `continue working without losing context`: a CLI fallback session can no longer quietly switch to the wrong bootstrap, retrieval, or patch-review verb set because of extra accepted aliases, dropped canonical tokens, lookup-table substitutions, or token reorderings.
- `AGENTS.md` compliance note: every active lane task in this packet now names the exact canonical demo-path step it advances, and this handoff states the concrete blocker removed at that step.
- Scope-tightening statement: this slice claims command-contract hardening for the current engine-first `project-open` / `retrieval` / `patch-review` smoke path only. That is the supporting evidence for `continue working without losing context` on the CLI fallback path while Textual remains disabled, and it does not claim new retrieval internals, patch application, persistence, audit-path, export, or broader workflow behavior.
- Review-basis exclusion: `terminal` and `export-handoff` remain outside this packet's approval basis; they are mentioned only because the shared command catalog still contains those aliases, not because this slice proves their runtime behavior.
- Smoke-test evidence:
  - `tests/unit/test_commands_catalog.py` proves `command_cli_contract()` returns the declared parser surface and fails fast when parser-surface drift is introduced at the token, canonical-entrypoint, or lookup-table level.
  - `tests/unit/test_commands_catalog.py` also proves the command route coverage stays pinned to the smoke route entry for patch review: `("patch-review", "diff-preview", ("diff-preview", "diff"))` in `test_command_cli_route_summary_tracks_the_smoke_route()` and `test_command_cli_route_contract_tracks_the_smoke_surface()`.
- Plan-alignment note: this slice keeps the explicit smoke-path mapping requested by review while aligning the packet to the current repo truth sources. `ROADMAP.md` keeps `feat-commands` in the active implementation emphasis, Milestone 1 calls for command and diff-preview hardening, and Milestone 2 explicitly calls out missing targeted parser-edge cases from review. This guard removes a concrete blocker by failing fast if parser or catalog drift would silently change the CLI verb surface along the current `project-open` / `retrieval` / `patch-review` smoke path.

## Approved Exception Note

- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approval owner: the integrator-managed branch policy for `codex/feat-commands`
- Approval mechanism: `scripts/scope-check.sh` `is_approved_shared_test()` branch allowlist for `codex/feat-commands*`
- Approval source: `THREAD_OWNERSHIP.md` keeps lane ownership on `src/qual/commands/**`; the non-owned test edit is a shared-by-approval exception with the explicit branch allowlist approval above, not an integrator-locked edit
- Approval basis: shared regression coverage is required to prove the same `continue working without losing context` mapping claimed by this packet, specifically that the supporting `project-open` / `retrieval` / `patch-review` smoke path stays catalog-locked on the CLI fallback route while Textual remains disabled
- Scope-check allowance used: `not required`
- Integrator-locked edits in this slice: `none`

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. `continue working without losing context`: locked the live CLI command contract to the command catalog so parser-surface drift fails closed before the operator reaches the wrong `project-open`, `retrieval`, or `patch-review` verb sets on the active CLI fallback path.
2. `continue working without losing context`: added focused regression coverage for parser-surface alignment and command-catalog drift rejection in `tests/unit/test_commands_catalog.py`, with evidence scoped to the supporting `open project/document` / `retrieve relevant material` / `preview and apply or reject a patch` smoke surface.
3. `continue working without losing context`: regenerated the handoff packet so the re-review basis points to commit `8e747334f4da2d5486e15088979a36184c8c9116`, the roadmap or vision mapping stays narrow, and the exact canonical demo-path step plus blocker removal are stated explicitly per reviewer request.
4. `continue working without losing context`: re-ran the required gates and recorded the outcomes against the current reviewed implementation scope so the packet stays tied to a verified command-contract slice.

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
- Gate attribution note: these gates were rerun at `2026-04-24T11:07:42Z UTC` against the current branch state while the reviewed implementation scope remains pinned to `8e747334f4da2d5486e15088979a36184c8c9116`; the current packet refresh itself is metadata-only.

### Risks / Blockers

- Risks:
  - future command-surface changes must keep `_CLI_ENTRYPOINTS` and the shared regression suite aligned or the contract will fail fast by design
- Blockers:
  - none

## Required Handoff Fields

### Explicit CLI smoke-path mapping

- Primary step: `continue working without losing context`
- Supporting tested steps: `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`
- This change makes `continue working without losing context` more real by keeping the supporting `project-open` / `retrieval` / `patch-review` command surface catalog-locked instead of letting parser-surface drift pass silently on the current engine-first CLI fallback path.
- Concrete blocker removal: downstream CLI fallback consumers can no longer silently accept a contract where the parser-derived command surface diverges from the declared `(token, canonical_name)` command catalog projection, including extra accepted aliases, dropped canonical tokens, lookup-table substitutions, or token reorderings, which removes a concrete blocker on `continue working without losing context`.
- Smoke-test evidence for the supporting steps is explicit in `tests/unit/test_commands_catalog.py`: the command contract now matches the declared parser surface and raises immediately when parser-surface drift is introduced.

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 3 `Real workflow loop`
- `ROADMAP.md` lane mapping: `feat-commands` is the CLI compatibility and migration-safe entrypoint lane
- `ROADMAP.md` exit criterion: `CLI can still execute the MVP loop while Textual remains disabled`
- Scope-tightening statement: this is CLI command-contract hardening for the supporting `open project/document` / `retrieve relevant material` / `preview and apply or reject a patch` smoke path, used here only as evidence for `continue working without losing context` rather than as a broader workflow claim.
- Proven command-surface level only: the claim is limited to the tested smoke-route entries `project-open -> bootstrap`, `retrieval -> context-basket`, and `patch-review -> diff-preview/diff`.
- Explicit exclusion: `terminal` and `export-handoff` are not part of the approval basis for this packet.

### Vision capability affected

- `PRODUCT_VISION.md` capability 3 `Canonical engine contract`
- Exact requirement advanced: `CLI compatibility is required while Textual remains disabled.`
- This slice narrows to the `project-open` / `retrieval` / `patch-review` command contract only. It does not claim A2UI payload generation, persistence, audit hooks, retrieval internals, or broader workflow traceability progress.
- Evidence anchor: the claimed product-surface support is the tested CLI route coverage for those smoke-path steps in `tests/unit/test_commands_catalog.py`, not an unproven broader engine-loop claim.

### Routing / Provider Impact Note

- None. This diff only hardens local command-contract behavior for the current MVP `project-open` / `retrieval` / `patch-review` smoke surface.

### Scope-Check / Ownership Note

- Shared-by-approval edits: `YES`
- Shared-by-approval path included: `tests/unit/test_commands_catalog.py`
- Shared-file approval basis: `THREAD_OWNERSHIP.md` limits lane-owned edits for `codex/feat-commands*` to `src/qual/commands/**`, so `tests/unit/test_commands_catalog.py` stays outside the owned path. The explicit approval mechanism is `scripts/scope-check.sh` `is_approved_shared_test()`, which branch-allowlists that shared test file for `codex/feat-commands*`. The exception is used only because that shared regression is the proof for the same `continue working without losing context` mapping claimed above: it keeps the supporting `project-open` / `retrieval` / `patch-review` smoke path catalog-locked while Textual remains disabled.
- Integrator-locked edits: `NO`
- Integrator-locked paths included: `none`
