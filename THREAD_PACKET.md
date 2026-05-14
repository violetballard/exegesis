## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Move A2UI card/action/selection-adjacent contracts into the client-agnostic shared package while preserving compatibility imports and CLI fallback behavior.
- Scope completed: Review candidate `c45d0139664c5afc9f3940567ef122c2e99cdfbe` is source/runtime work, not metadata-only work. It moves A2UI capabilities, action refs, policy-gated action execution, primitive block validation, and generic-card validation into `shared/src/exegesis_shared/contracts/a2ui.py`; keeps `src/qual/shared/contracts/a2ui.py` as a forwarding compatibility module; and updates tests to import canonical shared contract definitions while continuing to validate UI adapter behavior.
- Review commit scope note: commit `c45d0139664c5afc9f3940567ef122c2e99cdfbe` is the source/runtime review candidate. This packet correction supersedes the prior inaccurate planner/default-packet maintenance description.
- Canonical demo-path step advanced: AGENTS.md currently names `A2UI contracts with CLI fallback` as active MVP work; this makes that step more real by putting the contract in shared while preserving existing CLI fallback compatibility.
- High-risk kickoff/approval trail: shared contract files are in scope, so this handoff uses the AGENTS.md high-risk budget. No exception is requested; the work is summarized as 4 meaningful tasks.
- Task summary:
  1. Moved canonical A2UI contract ownership to `shared/src/exegesis_shared/contracts/a2ui.py`.
  2. Kept `src/qual/shared/contracts/a2ui.py` as a forwarding compatibility surface for existing imports.
  3. Updated `tests/unit/test_a2ui_contract.py` imports to exercise shared contract definitions and UI adapter behavior.
  4. Rewrote this handoff packet to match the actual source/runtime review candidate, high-risk budget, changed files, risks, and roadmap/product mapping.
- Changed-files list:
  - `shared/src/exegesis_shared/__init__.py`
  - `shared/src/exegesis_shared/contracts/__init__.py`
  - `shared/src/exegesis_shared/contracts/a2ui.py`
  - `src/qual/shared/contracts/a2ui.py`
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
  - `src/qual/shared/**` remains only as a compatibility forwarding surface for existing `src.qual` imports; canonical A2UI contract ownership is under `shared/src/exegesis_shared/**`.
- Roadmap/vision mapping:
  - Roadmap item(s) affected: Milestone 5 A2UI Presentation Layer contract extraction into shared while keeping renderers outside shared; supports Milestone 3 product-readiness output-contract locking.
  - Vision capability affected: client-agnostic cards/actions contract shared by engine and clients, with rendering adapters outside shared.
  - Canonical demo-path step advanced: AGENTS.md active MVP work item `A2UI contracts with CLI fallback`.
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
