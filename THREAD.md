# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Packet refresh status: fixer corrected the packet after the reviewer flagged inconsistent traceability, stale roadmap or vision mapping, and a missing explicit patch-step mapping.
- Exact implementation basis for re-review:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
- Current packet refresh traceability:
  - later `docs(commands)` commits update only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`
- Post-fixer verification note:
- `2026-04-24T09:40:00Z UTC` gate rerun confirmed this packet correction matches the current branch state while the reviewed implementation basis remains pinned to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
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
  - fail fast when the canonical command names derived from the live CLI lookup table drift from the declared command catalog
  - prove in shared tests that the command contract returns canonical catalog order and raises on drift
  - prove in shared tests that the smoke-route patch-review entry remains `("patch-review", "diff-preview", ("diff-preview", "diff"))`
- Primary canonical demo-path step(s) advanced:
  - `open project/document`
  - `retrieve`
  - `preview and apply or reject a patch`
- Required handoff field now called out explicitly:
  - `Explicit canonical demo-path mapping: open project/document, retrieve, preview and apply or reject a patch`
- Explicit re-review statement:
  - this slice advances the canonical `open project/document`, `retrieve`, and `preview and apply or reject a patch` steps by keeping the CLI smoke-surface contract catalog-locked, so deterministic contract validation protects the current engine-first operator path from silent parser drift at those steps
- AGENTS compliance note:
  - every active lane task in this packet now names the exact canonical demo-path step it advances, and the handoff states the concrete blocker removed at that step
- Per-task canonical demo-path mapping for re-review:
  - task 1 `open project/document`, `retrieve`, `preview and apply or reject a patch`: lock the live CLI smoke-surface command contract to the command catalog so canonical-name drift fails closed before the operator reaches the `project-open`, `retrieval`, or `patch-review` verb sets
  - task 2 `open project/document`, `retrieve`, `preview and apply or reject a patch`: add focused regression coverage proving canonical-order alignment and command-catalog drift rejection for the `project-open` / `retrieval` / `patch-review` CLI smoke surface
  - task 3 `open project/document`, `retrieve`, `preview and apply or reject a patch`: regenerate the handoff packet so the re-review basis, roadmap/vision scope, and explicit demo-path mapping stay aligned to the reviewed implementation slice
  - task 4 `open project/document`, `retrieve`, `preview and apply or reject a patch`: rerun the required gates and record the outcomes against the same reviewed implementation scope
- Scope note:
  - this packet advances the CLI smoke-surface contract for `open project/document`, `retrieve`, and `preview and apply or reject a patch`; deterministic CLI contract validation preserves the operator-facing command surface needed for the current engine-first CLI fallback at those steps while Textual remains disabled, and it does not claim new patch application, persistence, export, audit-path, or broader UI behavior
  - the CLI-first MVP loop claim is intentionally narrowed to the tested `project-open` / `retrieval` / `patch-review` route coverage in `tests/unit/test_commands_catalog.py`, not to a broader workflow-loop completion claim
  - `terminal` and `export-handoff` are outside the approval basis for this packet
- Concrete blocker removed:
  - the active CLI fallback no longer allows the parser-derived canonical command order to diverge from the declared command catalog without an immediate contract failure on the `project-open` / `retrieval` / `patch-review` smoke path
- Roadmap / vision alignment for this reviewed slice:
  - `ROADMAP.md` active lane keeps `feat-commands` in the current implementation push
  - `ROADMAP.md` Milestone 1 still includes `Command and diff-preview behavior hardening`
  - `AGENTS.md` operational narrowing rules require each active lane task to name which canonical demo-path step it advances and to state that step explicitly before handoff
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface` and capability 5 `Agent-to-UI protocol (A2UI)` are the only capabilities claimed here, specifically `CLI remains a first-class surface for development and reliability` and `CLI remains able to render a text fallback of the same underlying artifacts`
  - this packet does not claim persistence, audit hooks, retrieval progress, or broader workflow trace records
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
