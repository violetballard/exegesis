## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Keep A2UI card/action/selection-adjacent contracts in a client-agnostic shared layer while preserving deterministic CLI fallback action ordering in the UI adapter.
- Scope completed: Corrected the branch-tip review candidate by moving A2UI capabilities, action refs, policy-gated action execution, primitive block validation, and generic-card validation into `src/qual/shared/contracts/a2ui.py`. `src/qual/ui/a2ui.py` now imports those shared contracts and retains only card materialization and terminal rendering adapter behavior, including deterministic materialized-action ordering.
- Review commit scope note: commit `e89daef4c` was not metadata-only; it changed `src/qual/ui/a2ui.py` runtime behavior and `THREAD_PACKET.md`. This packet supersedes that false traceability note and describes the current branch tip.
- Canonical demo-path step advanced: deterministic A2UI actions make the "preview and apply or reject a patch" CLI fallback step more reliable.
- Task summary:
  1. Restored A2UI contract ownership to `src/qual/shared/contracts/a2ui.py`.
  2. Kept `src/qual/ui/a2ui.py` as the rendering/materialization adapter with deterministic action ordering.
  3. Updated `tests/unit/test_a2ui_contract.py` to import shared contract definitions from the shared layer and UI adapter behavior from the UI module.
  4. Rewrote this handoff packet to match the actual review candidate, including runtime scope, changed files, risks, and roadmap/product mapping.
- Changed-files list:
  - `src/qual/shared/__init__.py`
  - `src/qual/shared/contracts/__init__.py`
  - `src/qual/shared/contracts/a2ui.py`
  - `src/qual/ui/a2ui.py`
  - `tests/unit/test_a2ui_contract.py`
  - `THREAD_PACKET.md`
- Commands run with results:
  - `make scope-check` -> passed for branch `codex/feat-a2ui-contract` (no policy configured; skipped policy and passed)
  - `python -m unittest tests.unit.test_a2ui_contract` -> passed, 6 tests
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed, 123 tests
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed, including scope-check, format, lint, typecheck, and 123 tests
- Risks/blockers:
  - No known source blockers. The reviewed runtime behavior is constrained to shared A2UI contract definitions plus deterministic UI adapter materialization for CLI fallback actions.
  - The shared package is new in this worktree because no existing `src/qual/shared` package was present.
- Roadmap/vision mapping:
  - Roadmap item(s) affected: A2UI contract extraction into shared while keeping renderers outside shared.
  - Vision capability affected: client-agnostic cards/actions contract shared by engine and clients, with rendering adapters outside shared.
  - Canonical demo-path step advanced: deterministic A2UI actions make the "preview and apply or reject a patch" CLI fallback step more reliable.
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
