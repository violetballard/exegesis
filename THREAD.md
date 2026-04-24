# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Packet refresh status: fixer corrected the packet after the reviewer flagged inconsistent traceability, overbroad roadmap or vision mapping, and a missing explicit canonical demo-path statement.
- Exact implementation basis for re-review:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
- Current packet refresh traceability:
  - later `docs(commands)` commits update only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`
- Post-fixer verification note:
- `2026-04-24T09:28:18Z UTC` gate rerun confirmed this packet correction matches the current branch state while the reviewed implementation basis remains pinned to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- High-risk kickoff context:
  - scope goal: make the roadmap MVP flow step `patch` more real by keeping the operator-visible command contract locked to the parser/catalog boundary for the CLI patch-review surface
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
- Primary canonical demo-path step advanced:
  - roadmap MVP flow step `patch`
- Required handoff field now called out explicitly:
  - `Canonical demo-path step advanced: patch`
- Explicit re-review statement:
  - this slice advances the roadmap MVP flow step `patch` by keeping the CLI patch-review command contract catalog-locked, so deterministic contract validation protects the operator path that the current CLI fallback uses to carry the demo flow
- Per-task canonical demo-path mapping for re-review:
  - task 1 `patch`: lock the live CLI command contract to the command catalog so canonical-name drift fails closed before the operator reaches the patch-review verb set
  - task 2 `patch`: add focused regression coverage proving canonical-order alignment and command-catalog drift rejection for the patch-review CLI surface
  - task 3 `patch`: regenerate the handoff packet so the re-review basis, roadmap/vision scope, and explicit demo-path mapping stay aligned to the reviewed implementation slice
  - task 4 `patch`: rerun the required gates and record the outcomes against the same reviewed implementation scope
- Scope note:
  - this packet advances the patch-review command contract only; deterministic CLI contract validation preserves the CLI operator-facing command surface needed for the roadmap MVP flow step `patch`, and it does not claim new retrieval, patch application, persistence, export, audit-path, or broader UI behavior
  - the CLI-first MVP loop claim is intentionally narrowed to the tested patch-review route coverage in `tests/unit/test_commands_catalog.py`, not to a broader workflow-loop completion claim
- Current engine-first MVP path statement:
  - the roadmap MVP flow stays `vault -> context -> run -> patch -> export`; the current CLI smoke route expression for that `patch` step stays `project-open -> retrieval -> preview and apply or reject a patch -> persist -> export-handoff`
- Concrete blocker removed:
  - the active CLI fallback no longer allows the parser-derived canonical command order to diverge from the declared command catalog without an immediate contract failure at the patch-review step
- Roadmap / vision alignment for this reviewed slice:
  - `ROADMAP.md` current MVP focus keeps `feat-commands` active in the current implementation push
  - `ROADMAP.md` Milestone 5 contribution is limited to the exit-criteria requirement that `CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate`
  - `ROADMAP.md` current lane kickoff for this slice is the `feat-commands` scope goal to keep the CLI reliable for the A2UI demo flow `project open/bootstrap, retrieval invocation, patch review, and export handoff`
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface` is the only capability claimed here, specifically the requirement that `CLI remains a first-class surface for development and reliability.`
  - this packet does not claim persistence, audit hooks, or workflow trace records
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
