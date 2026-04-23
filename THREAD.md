# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Reviewed implementation base previously approved for comparison: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Reviewed implementation commits included in this re-review:
  - `06540160de4cf0d452c1ed9b4d4926c205888be9` (`fix(commands): preserve demo flow steps for shim tokens`)
  - `7fe699292035b6671bd17a3c5defa1659819c6fa` (`feat(commands): canonicalize demo argv workflow tokens`)
- Current handoff packet is a metadata-only refresh on top of that reviewed implementation range.
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation behavior:
  - `command_cli_contract()` rejects parser-surface drift, including alias substitution, token removal, token addition, and parser-surface reorder cases that leave canonical command names unchanged
  - shim-backed demo-loop tokens now keep their logical flow-step identity in the canonical CLI MVP workflow contract
  - canonical demo-path argv now map back to the stable workflow token instead of inheriting the fallback canonical command name for shim-backed terminal actions
  - `apply-patch`, `reject-patch`, and `persist` no longer collapse to `export-handoff` inside workflow, trusted-surface, compatibility, and next-action metadata
  - regression coverage now locks that corrected metadata for the `project-open -> retrieval -> patch-review -> apply/reject -> persist -> export-handoff` demo path
- Exact existing CLI demo-path commands this work hardens:
  - `project-open`
  - `retrieval`
  - `patch-review`
  - `apply-patch`
  - `reject-patch`
  - `persist`
  - `export-handoff`
- Roadmap / vision alignment:
  - `ROADMAP.md` Milestone 1 (`Bootstrap Flow Stabilization`): hardens the CLI-first workflow contract used by the current smoke path
  - `ROADMAP.md` Milestone 2 (`Test Hardening`): adds focused regression coverage for the shim-backed command metadata
  - `ROADMAP.md` active MVP emphasis `feat-commands`: keeps the demo-path command surface deterministic for the engine-first MVP
  - `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`): preserves a stable CLI command contract for the operator-facing MVP loop
- Scope / risk note:
  - lane-owned implementation: `src/qual/commands/catalog.py`
  - approved shared regression file: `tests/unit/test_commands_catalog.py`
  - integrator-locked files touched: none
  - canonical demo-path step advanced: `preview and apply or reject a patch`
  - concrete blocker removed: shim-backed terminal commands no longer inherit the base `export-handoff` flow-step label when the logical command is `apply-patch`, `reject-patch`, or `persist`, canonical demo argv now resolve back to those stable workflow tokens, and parser-surface drift on `command_cli_contract()` now fails fast instead of silently preserving only canonical-name order
  - required gates passed: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, `make ci`
  - metadata refreshed for this handoff: `THREAD.md`, `THREAD_PACKET.md`
