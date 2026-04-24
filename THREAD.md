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
  - `command_cli_contract()` rejects catalog-entrypoint projection drift, including alias substitution, token removal, token addition, and catalog-entrypoint projection reorder cases that leave canonical command names unchanged
  - shim-backed demo-loop tokens now keep their logical flow-step identity in the canonical CLI MVP workflow contract
  - canonical demo-path argv now map back to the stable workflow token instead of inheriting the fallback canonical command name for shim-backed terminal actions
  - `apply-patch`, `reject-patch`, and `persist` no longer collapse to `export-handoff` inside workflow, trusted-surface, compatibility, and next-action metadata
  - regression coverage now locks that corrected metadata for the `project-open -> retrieval -> patch-review -> apply/reject -> persist -> export-handoff` demo path
  - this is first-order MVP contract work, not second-order catalog cleanup, because the CLI remains the active operator surface while Textual stays disabled
- Exact existing CLI demo-path commands this work hardens:
  - `project-open`
  - `retrieval`
  - `patch-review`
  - `apply-patch`
  - `reject-patch`
  - `persist`
  - `export-handoff`
- Roadmap / vision alignment:
  - `ROADMAP.md` Milestone 3 (`Product Readiness`) scope item `Define and lock user-facing output contracts`: hardens deterministic CLI contract validation and migration-safe command entrypoints for `project-open`
  - `ROADMAP.md` active MVP emphasis `feat-commands`: keeps deterministic CLI contract validation in the lane-owned command catalog without broadening into engine workflow behavior claims
  - `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`): preserves the required CLI compatibility for `open project/document` and the rest of the MVP loop while Textual remains disabled and CLI remains the first-class operator surface
- Scope / risk note:
  - lane-owned implementation: `src/qual/commands/catalog.py`
  - approved shared regression file: `tests/unit/test_commands_catalog.py`
  - integrator-locked files touched: none
  - canonical demo-path step advanced: `open project/document` via the `project-open` operator token
  - concrete blocker removed on that step: this prevents parser/catalog drift from silently changing the CLI contract for the migration-safe `project-open` entrypoint used for `open project/document`
  - scope guard: this handoff is limited to deterministic CLI contract validation and migration-safe command entrypoints; it does not claim engine workflow behavior changes
  - required gates passed: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, `make ci`
  - metadata refreshed for this handoff: `THREAD.md`, `THREAD_PACKET.md`
