# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Packet refresh status: fixer resubmission regenerated against the current reviewed implementation basis after the reviewer requested stronger parser-surface validation and matching regression evidence.
- Exact implementation basis for re-review:
  - `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa` (`feat(commands): expose default workflow aliases`)
  - reviewer-requested parser-surface fixes are included in the reviewed ancestry:
    - `dbb8e0156f3520c759d4d29e2cbbb186013f6df7` (`fix(commands): harden parser surface drift checks`)
    - `6890b8c6d81c7700e84b6cbf9402177d0bafab4f` (`test(commands): lock parser drift regressions to live entrypoints`)
    - `bd118a6c0d7693d58882f74efc8066387bc82189` (`test(commands): cover cached parser surface drift`)
- Current packet refresh traceability:
  - later `docs(commands)` commits update only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`
- Post-fixer verification note:
- `2026-04-24T08:48:39Z UTC` gate rerun confirmed this packet matches the current branch state while the reviewed implementation basis remains pinned to `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa`
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation scope:
  - fail fast when the live review-step parser surface drifts from the declared command catalog, including the `diff-preview` removed / `diff` retained case
  - reject alias-only substitution, reordered parser surface, and unexpected extra parser entrypoints for the review-step token surface
  - prove in shared tests that the review-step parser surface still fails fast after cache warmup
  - expose the default workflow and trusted-surface aliases as direct forwards to the current MVP contracts without changing provider, retrieval, persistence, or UI behavior
- Primary canonical demo-path step advanced:
  - `preview and apply or reject a patch`
- Required handoff field now called out explicitly:
  - `Canonical demo-path step advanced: preview and apply or reject a patch`
- Explicit re-review statement:
  - this slice advances the canonical `preview and apply or reject a patch` step by keeping the public `diff-preview` review entrypoint catalog-locked inside the current engine-first Milestone 3 loop so deterministic CLI contract validation preserves the operator-facing command surface while the package/layout migration is in flight
- Scope note:
  - this packet advances the patch-review command contract and adds alias-forwarding helpers that mirror the current engine-first MVP workflow/trusted surface; deterministic CLI contract validation preserves the operator-facing command surface required by Milestone 3 while the package/layout migration is in flight, and it does not claim new retrieval, patch application, persistence, export, audit-path, or broader UI behavior
- Current engine-first MVP path statement:
  - the current CLI-first smoke route stays `project-open -> retrieval -> preview and apply or reject a patch -> persist -> export-handoff`
- Concrete blocker removed:
  - the active CLI fallback no longer allows the public `diff-preview` token to disappear, reorder, or expand unexpectedly behind parser drift without an immediate contract failure at the patch-review step
- Roadmap / vision alignment for this reviewed slice:
  - `ROADMAP.md` MVP focus keeps `feat-commands` active in the current implementation push
  - `ROADMAP.md` Milestone 3 contribution is limited to locking the user-facing command contract for the current CLI loop `project-open -> retrieval -> preview and apply or reject a patch -> persist -> export-handoff`
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface` is the only capability claimed here, specifically the engine-contract requirement that structured outputs stay consumable by CLI now and `Exegesis Console` next
  - this packet does not claim `PRODUCT_VISION.md` capability 3 `Auditable generation` because the reviewed diff does not add persistence, audit hooks, or workflow trace records
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
