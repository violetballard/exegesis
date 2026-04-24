# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Packet refresh status: fixer committed the reviewer-required parser-surface guard and is refreshing the packet metadata so re-review points to one exact implementation commit.
- Exact implementation basis for re-review:
  - `744c0fefcbd69ff3a128df512b6786fd2dba8023` (`feat(commands): fail on parser surface drift`)
- Approval basis pin for re-review:
  - Only `744c0fefcbd69ff3a128df512b6786fd2dba8023`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py` are part of the implementation approval basis.
  - The packet-refresh commit is metadata-only and must not be treated as widening the implementation scope.
- Current packet refresh traceability:
  - the packet-refresh commit updates only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`
- Post-fixer verification note:
- `2026-04-24T11:16:57Z UTC` full required gate rerun confirmed this packet refresh matches the current branch state while the reviewed implementation basis remains pinned to `744c0fefcbd69ff3a128df512b6786fd2dba8023`
- High-risk kickoff context:
  - scope goal: make the canonical `continue working without losing context` step more real by removing a concrete blocker at the CLI fallback boundary: silent parser/catalog drift on the operator-visible `project-open` / `retrieval` / `patch-review` command surface
  - risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file
  - planned scope stayed within the high-risk 4-task cap for one owned command file, one approved shared test file, and packet-only handoff metadata
  - early review triggers: before first edit to any shared/integrator-locked file, before changing public interfaces or command contracts, and before touching provider routing/config behavior
  - stop triggers: unresolved test/lint/typecheck after 2 focused fix attempts, unresolved `make scope-check`, or budget/size/time limit hit
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation scope:
  - fail fast when the live CLI parser surface drifts from the declared command catalog, including extra accepted aliases or reordered parser entrypoints
  - prove in shared tests that the command contract returns the declared parser surface and raises on parser-surface drift
  - prove in shared tests that the smoke-route patch-review entry remains `("patch-review", "diff-preview", ("diff-preview", "diff"))`
- Primary canonical demo-path step advanced:
  - `continue working without losing context`
- Supporting smoke-path steps strengthened for that primary step:
  - `open project/document` maps to the MVP loop's `vault` and `context` entry boundary through `project-open`
  - `retrieve relevant material` maps to the MVP loop's `context` and `run` handoff boundary through `retrieval`
  - `preview and apply or reject a patch` maps to the MVP loop's `patch` boundary through `patch-review`
- Required handoff field now called out explicitly:
  - `Primary canonical demo-path step: continue working without losing context`
- Explicit re-review statement:
  - this slice advances the canonical `continue working without losing context` step by hardening the supporting `project-open` / `retrieval` / `patch-review` command surface on the current CLI fallback path while Textual remains disabled, so deterministic contract validation protects that operator surface from silent parser drift
  - reviewer wording trace: this work makes `open project/document` and the broader CLI operator path more real by preventing silent command-surface drift while Textual remains disabled
- AGENTS compliance note:
  - this packet stays within the high-risk 4-task cap, records the shared-test exception, and includes the required handoff fields from `INTEGRATION.md`
- Per-task canonical demo-path mapping for re-review:
  - task 1 `continue working without losing context`: lock the live CLI smoke-surface command contract to the command catalog so parser-surface drift fails closed before the operator reaches the wrong `project-open`, `retrieval`, or `patch-review` verb sets on the active CLI fallback path
  - task 2 `continue working without losing context`: add focused regression coverage proving parser-surface alignment and command-catalog drift rejection for the supporting `project-open` / `retrieval` / `patch-review` CLI smoke surface
  - task 3 `continue working without losing context`: regenerate the handoff packet so the re-review basis, roadmap/vision scope, and explicit demo-path mapping stay aligned to the reviewed implementation slice
  - task 4 `continue working without losing context`: rerun the required gates and record the outcomes against the same reviewed implementation scope
- Scope note:
  - this packet advances `continue working without losing context` by hardening the supporting CLI smoke-surface contract for `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch`; it does not claim new patch application, persistence, export, audit-path, or broader UI behavior
  - the CLI-first MVP loop claim is intentionally narrowed to the tested `project-open` / `retrieval` / `patch-review` route coverage in `tests/unit/test_commands_catalog.py`, not to a broader workflow-loop completion claim
  - `terminal` and `export-handoff` are outside the approval basis for this packet
- Concrete blocker removed:
  - the active CLI fallback no longer allows the parser-derived command surface to diverge from the declared `(token, canonical_name)` command catalog projection, including token-level reorderings, dropped canonical entrypoints, extra accepted aliases, or lookup-table substitutions, without an immediate contract failure on the supporting `project-open` / `retrieval` / `patch-review` smoke path that underpins `continue working without losing context`
- Roadmap / vision alignment for this reviewed slice:
  - `ROADMAP.md` Milestone 3 `Real workflow loop` is the active milestone for this lane
  - `ROADMAP.md` lane mapping keeps `feat-commands` scoped to CLI compatibility and migration-safe entrypoints
  - `ROADMAP.md` exit criterion claimed here is limited to `CLI can still execute the MVP loop while Textual remains disabled`
  - `PRODUCT_VISION.md` capability 3 `Canonical engine contract` is the only capability claimed here, specifically `CLI compatibility is required while Textual remains disabled`
  - this packet does not claim A2UI payloads, persistence, audit hooks, retrieval progress, or broader workflow trace records
- Ownership / scope note:
  - lane-owned implementation path: `src/qual/commands/catalog.py`
  - approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
  - approval owner: the repo branch policy for `codex/feat-commands*`
  - approval mechanism: `scripts/scope-check.sh` `is_approved_shared_test()` allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`
  - approval source: `THREAD_OWNERSHIP.md` limits lane-owned edits for `codex/feat-commands*` to `src/qual/commands/**`, so the test stays outside the owned path, and the branch-specific shared-test allowlist above is the explicit approval source for this shared-file exception
  - approval mechanism note: the branch allowlist is the approved mechanism covering this shared test edit; no separate ad hoc exception was used
  - approval reason: the shared regression is the evidence for the same `continue working without losing context` mapping claimed in this packet, because it proves the supporting `project-open` / `retrieval` / `patch-review` smoke path stays locked to the declared CLI contract
  - integrator-locked edits are not part of this slice
- Required gates for the reviewed slice:
  - `make scope-check`
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
