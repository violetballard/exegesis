# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Packet refresh status: reviewer-fix packet refresh regenerated on 2026-04-24 for the exact reviewed implementation slice.
- Reviewed implementation commit: `86e7450a89c33ed158097c4fde9d5fc9edb023ab` (`feat(commands): normalize persist-and-continue`).
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
- Reviewed implementation scope:
  - deterministic CLI compatibility for the active fallback surface: fail-fast parser/catalog drift detection on the declared parser-facing command contract
- Primary canonical demo-path step advanced now:
  - `open project/document`
- Required handoff field now called out explicitly:
  - `Canonical demo-path step advanced: open project/document`
- Primary-step scope note:
  - this packet advances `open project/document` only
- One-line plan alignment:
  - this change makes `open project/document` more real by keeping the CLI fallback command contract deterministic and failing fast before that first operator step can run on a drifted parser/catalog surface
- `command_cli_contract()` dependency sentence:
  - deterministic `command_cli_contract()` behavior is necessary for `open project/document` because, while Textual remains disabled and the CLI must still execute the MVP loop, the operator cannot trust the very first demo-path command unless parser/catalog drift is rejected before command resolution
- Active MVP operator path strengthened:
  - the CLI fallback path for `open project/document` by keeping command ordering deterministic and failing fast before the first operator step runs if parser/catalog drift is introduced
- Direct plan-alignment statement:
  - this change makes `open project/document` more real by keeping the CLI command contract deterministic during the engine-first MVP loop and failing closed when parser/catalog drift is introduced
- Traceability note:
  - `86e7450a89c33ed158097c4fde9d5fc9edb023ab` is the actual implementation tip for this reviewed slice; later commits on the branch are packet-only refreshes
- Concrete blocker removed for Milestone 3:
  - the active CLI surface no longer allows the declared parser-facing token catalog to drift away from the canonical command catalog without failing closed, including the explicit reviewer-called case where the `diff` parser token disappears while the canonical-name tuple still appears stable; that removes a concrete reliability blocker before the CLI can safely begin the `open project/document` demo-path step.
- Scope-tightening note:
  - this reviewed slice hardens only deterministic command ordering plus fail-fast parser/catalog drift detection for the primary `open project/document` fallback step; it does not claim progress on retrieval, patch review, persistence, export, or any later demo-path step
- Why this is milestone-worthy now:
  - deterministic CLI command ordering is a required smoke-test guard for the active engine-first MVP loop while Textual remains disabled, so preventing silent contract drift in the declared command catalog is direct operator-surface hardening rather than second-order cleanup.
- Roadmap / vision alignment for this reviewed slice:
  - `ROADMAP.md` Milestone 3: preserve CLI compatibility while the package/layout migration lands, applied here as a deterministic CLI command catalog for the active `open project/document` fallback path
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: keep the CLI command catalog deterministic and fail-closed before the `open project/document` step begins
- Ownership / scope note:
  - lane-owned implementation path: `src/qual/commands/catalog.py`
  - approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
  - approval reference: this packet refresh in `THREAD.md` and `THREAD_PACKET.md`, tied to reviewed implementation commit `86e7450a89c33ed158097c4fde9d5fc9edb023ab`, is the in-tree approval record for that single shared-path test edit
  - integrator-locked edits are not part of this slice
- Required gates for the reviewed slice:
  - `make scope-check`
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
