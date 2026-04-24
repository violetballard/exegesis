# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Packet refresh status: metadata-only resubmission generated on 2026-04-24 so the handoff now points at the real implementation basis instead of the prior stale metadata commit.
- Exact implementation basis now approved:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
  - `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa` (`feat(commands): expose default workflow aliases`)
- Current packet refresh traceability:
  - this refresh is metadata-only and updates only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`
- Post-fixer verification note:
  - `2026-04-24T08:19:27Z UTC` gate rerun confirmed the packet still matches the current branch state and implementation tip `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa`
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/__init__.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation scope:
  - fail fast when the live review-step parser surface drifts from the command catalog, including the `diff-preview` removed / `diff` retained case
  - expose one default current-MVP workflow contract and trusted-surface alias set for the review/apply-or-reject branch
  - prove in shared tests that the public default aliases stay pinned to the current MVP contract
- Primary canonical demo-path step advanced:
  - `preview and apply or reject a patch`
- Required handoff field now called out explicitly:
  - `Canonical demo-path step advanced: preview and apply or reject a patch`
- Explicit re-review statement:
  - this slice advances the canonical `preview and apply or reject a patch` step by keeping the public `diff-preview` review entrypoint catalog-locked and by exposing one default current-MVP helper surface for the apply/reject branch
- Scope note:
  - this packet advances only the current patch-review command contract; it does not claim new retrieval, patch application, persistence, export, audit-path, or broader CLI behavior
- Current engine-first MVP path statement:
  - the current CLI-first smoke route stays `project-open -> retrieval -> preview and apply or reject a patch -> persist -> export-handoff`
- Concrete blocker removed:
  - the active CLI fallback no longer depends on callers picking demo-specific vs MVP-specific workflow helpers for the patch-review branch, and it no longer allows the public `diff-preview` token to disappear behind alias-only parser drift without an immediate contract failure
- Roadmap / vision alignment for this reviewed slice:
  - `ROADMAP.md` MVP focus keeps `feat-commands` active in the current implementation push
  - `ROADMAP.md` Milestone 3 contribution is limited to locking the user-facing command/workflow contract surface
  - `ROADMAP.md` Milestone 5 contribution is limited to keeping the CLI review/apply-or-reject step deterministic while the CLI fallback still carries the MVP flow
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface` is the only capability claimed here
- Ownership / scope note:
  - lane-owned implementation paths: `src/qual/commands/catalog.py`, `src/qual/commands/__init__.py`
  - approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
  - approval source: `scripts/scope-check.sh` `is_approved_shared_test()` allowlist for `codex/feat-commands*`
  - integrator-locked edits are not part of this slice
- Required gates for the reviewed slice:
  - `make scope-check`
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
