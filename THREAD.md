# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Packet refresh status: fixer corrected the packet after the reviewer flagged missing canonical demo-path wording, scope overclaiming beyond the parser-surface guard, and missing evidence for full parser-surface drift detection.
- Exact implementation basis for re-review:
  - `8e747334f4da2d5486e15088979a36184c8c9116` (`feat(commands): validate full CLI token projection`)
- Approval basis pin for re-review:
  - Only `8e747334f4da2d5486e15088979a36184c8c9116`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py` are part of the implementation approval basis.
  - The packet-refresh commit is metadata-only and must not be treated as widening the implementation scope.
- Current packet refresh traceability:
  - the packet-refresh commit updates only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`
- Post-fixer verification note:
- `2026-04-24T10:34:02Z UTC` gate rerun confirmed this packet correction matches the current branch state while the reviewed implementation basis remains pinned to `8e747334f4da2d5486e15088979a36184c8c9116`
- High-risk kickoff context:
  - scope goal: make the canonical `preview and apply or reject a patch` step more real by keeping the operator-visible command contract locked to the parser/catalog boundary so the CLI fallback stays deterministic while interactive clients stay secondary
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
- Primary canonical demo-path step(s) advanced:
  - `open project/document`
  - `retrieve`
  - `preview and apply or reject a patch`
- Roadmap loop mapping for the same steps:
  - `open project/document` maps to the MVP loop's `vault` and `context` entry boundary through `project-open`
  - `retrieve` maps to the MVP loop's `context` and `run` handoff boundary through `retrieval`
  - `preview and apply or reject a patch` maps to the MVP loop's `patch` boundary through `patch-review`
- Required handoff field now called out explicitly:
  - `Explicit CLI smoke-path mapping: open project/document, retrieve, preview and apply or reject a patch`
- Explicit re-review statement:
  - this slice advances the canonical `open project/document`, `retrieve`, and `preview and apply or reject a patch` steps by hardening the current CLI "continue working" fallback path while Textual remains disabled, so deterministic contract validation protects that operator surface from silent parser drift at those steps
- AGENTS compliance note:
  - this packet stays within the high-risk 4-task cap, records the shared-test exception, and includes the required handoff fields from `INTEGRATION.md`
- Per-task canonical demo-path mapping for re-review:
  - task 1 `open project/document`, `retrieve`, `preview and apply or reject a patch`: lock the live CLI smoke-surface command contract to the command catalog so parser-surface drift fails closed before the operator reaches the `project-open`, `retrieval`, or `patch-review` verb sets
  - task 2 `open project/document`, `retrieve`, `preview and apply or reject a patch`: add focused regression coverage proving parser-surface alignment and command-catalog drift rejection for the `project-open` / `retrieval` / `patch-review` CLI smoke surface
  - task 3 `open project/document`, `retrieve`, `preview and apply or reject a patch`: regenerate the handoff packet so the re-review basis, roadmap/vision scope, and explicit demo-path mapping stay aligned to the reviewed implementation slice
  - task 4 `open project/document`, `retrieve`, `preview and apply or reject a patch`: rerun the required gates and record the outcomes against the same reviewed implementation scope
- Scope note:
  - this packet advances the CLI smoke-surface contract for `open project/document`, `retrieve`, and `preview and apply or reject a patch`; deterministic CLI contract validation preserves the operator-facing command surface needed for the current CLI "continue working" fallback at those steps while Textual remains disabled, and it does not claim new patch application, persistence, export, audit-path, or broader UI behavior
  - the CLI-first MVP loop claim is intentionally narrowed to the tested `project-open` / `retrieval` / `patch-review` route coverage in `tests/unit/test_commands_catalog.py`, not to a broader workflow-loop completion claim
  - `terminal` and `export-handoff` are outside the approval basis for this packet
- Concrete blocker removed:
  - the active CLI fallback no longer allows the parser-derived command surface to diverge from the declared `(token, canonical_name)` command catalog projection, including token-level reorderings, dropped canonical entrypoints, extra accepted aliases, or lookup-table substitutions, without an immediate contract failure on the `project-open` / `retrieval` / `patch-review` smoke path
- Roadmap / vision alignment for this reviewed slice:
  - `ROADMAP.md` active lane keeps `feat-commands` in the current implementation push
  - `ROADMAP.md` Milestone 1 narrows this slice to `Command and diff-preview behavior hardening`
  - `ROADMAP.md` Milestone 2 remaining work explicitly includes `Add missing targeted cases identified during reviews (parser edges, persistence edge cases)`
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface` is the only capability claimed here, specifically `CLI remains a first-class surface for development and reliability`
  - this packet does not claim A2UI payloads, persistence, audit hooks, auditable generation, retrieval progress, or broader workflow trace records
- Ownership / scope note:
  - lane-owned implementation path: `src/qual/commands/catalog.py`
  - approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
  - approval source: `THREAD_OWNERSHIP.md` keeps the test outside the lane-owned path and `scripts/scope-check.sh` `is_approved_shared_test()` allowlists it for `codex/feat-commands*`
  - integrator-locked edits are not part of this slice
- Required gates for the reviewed slice:
  - `make scope-check`
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
