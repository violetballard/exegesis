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
  - `ROADMAP.md` Milestone 1 (`Bootstrap Flow Stabilization`): hardens the `open project/document` entrypoint and the broader CLI-first workflow contract used by the current smoke path
  - `ROADMAP.md` Milestone 2 (`Test Hardening`): adds focused regression coverage for the shim-backed command metadata
  - `ROADMAP.md` Milestone 5 (`A2UI Presentation Layer`) exit criterion: supports `CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate` by keeping the CLI-first command surface deterministic while Textual remains disabled
  - `ROADMAP.md` active MVP emphasis `feat-commands`: keeps the demo-path command surface deterministic for the engine-first MVP while Textual remains disabled
  - `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`): preserves the required CLI compatibility for `open project/document` and the rest of the MVP loop while Textual remains disabled
- Scope / risk note:
  - lane-owned implementation: `src/qual/commands/catalog.py`
  - approved shared regression file: `tests/unit/test_commands_catalog.py`
  - integrator-locked files touched: none
  - canonical demo-path step advanced: `open project/document` via the `project-open` operator token
  - concrete blocker removed on that step: this prevents parser/catalog drift from silently changing the operator command surface for the CLI-first MVP loop, because `command_cli_contract()` now rejects catalog-entrypoint projection drift in the accepted CLI entrypoints for `project-open` and the rest of the exposed CLI surface instead of allowing alias-only substitutions, token additions/removals, or entrypoint reorder to pass behind unchanged canonical command names
  - broader CLI MVP loop context preserved: shim-backed workflow metadata for `apply-patch`, `reject-patch`, `persist`, and `export-handoff` remains explicit while Textual stays disabled
  - required gates passed: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, `make ci`
  - metadata refreshed for this handoff: `THREAD.md`, `THREAD_PACKET.md`
