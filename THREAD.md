# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Packet refresh status: reviewer-fix verification refresh aligned to the exact reviewed implementation slice.
- Reviewed implementation commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`).
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Canonical demo-path step advanced:
  - `open project/document`
- Active MVP operator path strengthened:
  - the CLI fallback path for `open project/document` while Textual remains disabled
- Concrete blocker removed for Milestone 3:
  - the CLI-first MVP no longer allows the parser-facing token surface for the `open project/document` entry step to drift away from the canonical command catalog without failing closed, so the first command a CLI operator uses in the demo loop cannot silently lose required entrypoints or aliases while the canonical-name tuple still appears stable.
- Scope-tightening note:
  - this reviewed slice hardens only the CLI fallback entry step above; it does not claim patch preview, apply or reject, or broader command-flow coverage
- Why this is milestone-worthy now:
  - Milestone 3 still depends on the CLI as the active operator surface while Textual remains disabled, so preventing silent contract drift at the demo-path entry step is direct operator-path hardening for the live CLI-first MVP loop rather than second-order cleanup.
- Roadmap / vision alignment for this reviewed slice:
  - `ROADMAP.md` Milestone 3: preserve CLI compatibility while the package/layout migration lands, specifically the requirement that the active operator surface keep stable, migration-safe entrypoints while Textual remains disabled
  - `PRODUCT_VISION.md` capability 3 `Canonical engine contract`: keep the CLI as a deterministic engine-facing operator surface that is stable enough to drive the demo path while Textual remains disabled
- Ownership / scope note:
  - lane-owned implementation path: `src/qual/commands/catalog.py`
  - approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
  - integrator-locked edits are not part of this slice
- Required gates for the reviewed slice:
  - `make scope-check`
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
