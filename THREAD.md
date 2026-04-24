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
- `2026-04-24T09:05:47Z UTC` gate rerun confirmed this packet correction matches the current branch state while the reviewed implementation basis remains pinned to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- High-risk kickoff context:
  - scope goal: make the canonical `preview and apply or reject a patch` step more real by keeping the operator-visible command contract locked to the parser/catalog boundary during the current engine-first CLI loop while Textual remains disabled
  - risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file
  - planned scope stayed within the high-risk 4-task cap for one owned command file, one approved shared test file, and packet-only handoff metadata
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation scope:
  - fail fast when the canonical command names derived from the live CLI lookup table drift from the declared command catalog
  - prove in shared tests that the command contract returns canonical catalog order and raises on drift
- Primary canonical demo-path step advanced:
  - `preview and apply or reject a patch`
- Required handoff field now called out explicitly:
  - `Canonical demo-path step advanced: preview and apply or reject a patch`
- Explicit re-review statement:
  - this slice advances the canonical `preview and apply or reject a patch` step by keeping the command contract catalog-locked inside the current engine-first Milestone 3 loop so deterministic CLI contract validation preserves the operator-facing command surface while the package/layout migration is in flight
- Scope note:
  - this packet advances the patch-review command contract only; deterministic CLI contract validation preserves the operator-facing command surface required by Milestone 3 while the package/layout migration is in flight, and it does not claim new retrieval, patch application, persistence, export, audit-path, or broader UI behavior
- Current engine-first MVP path statement:
  - the current CLI-first smoke route stays `project-open -> retrieval -> preview and apply or reject a patch -> persist -> export-handoff`
- Concrete blocker removed:
  - the active CLI fallback no longer allows the parser-derived canonical command order to diverge from the declared command catalog without an immediate contract failure at the patch-review step
- Roadmap / vision alignment for this reviewed slice:
  - `ROADMAP.md` MVP focus keeps `feat-commands` active in the current implementation push
  - `ROADMAP.md` Milestone 3 contribution is limited to preserving CLI compatibility while the package/layout migration lands for the current CLI loop `project-open -> retrieval -> preview and apply or reject a patch -> persist -> export-handoff`
  - `ROADMAP.md` lane mapping for this slice is `feat-commands`: `CLI compatibility and migration-safe entrypoints`
  - `PRODUCT_VISION.md` capability 3 `Canonical engine contract` is the only capability claimed here, specifically the requirement that `CLI compatibility is required while Textual remains disabled`
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
