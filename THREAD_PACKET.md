## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Move A2UI card/action/selection-adjacent contracts into the client-agnostic shared package while preserving compatibility imports and CLI fallback behavior.
- Scope completed: Review candidate `c45d0139664c5afc9f3940567ef122c2e99cdfbe` is source/runtime work, not metadata-only work. It moves A2UI capabilities, action refs, policy-gated action execution, primitive block validation, and generic-card validation into `shared/src/exegesis_shared/contracts/a2ui.py`; keeps `src/qual/shared/contracts/a2ui.py` as a forwarding compatibility module; and updates tests to import canonical shared contract definitions while continuing to validate UI adapter behavior.
- Authoritative source-bearing review range: `7e117a068bd0b9597c085eda8f96a9706aad477b..c45d0139664c5afc9f3940567ef122c2e99cdfbe`. This is the only submitted source/runtime review range for this re-review packet. It includes all source-bearing changes submitted here and the complete changed-files list below.
- Review commit scope note: commit `c45d0139664c5afc9f3940567ef122c2e99cdfbe` is the source/runtime review candidate, reviewed as the diff from parent `7e117a068bd0b9597c085eda8f96a9706aad477b` to `c45d0139664c5afc9f3940567ef122c2e99cdfbe`. Later commits through branch tip update only `THREAD_PACKET.md`; they do not change the submitted source/runtime review scope. This packet correction supersedes all prior inaccurate `b929fe6c7a1159c7882acedd247aca31a93cd123` / `d795e5f171b9284f4b16c3a24c5867bf8e4910d5` traceability claims, including stale `.codex/lane_meta/feat-a2ui-contract.json` metadata that still names that obsolete range.
- Canonical demo-path step advanced: AGENTS.md currently names `A2UI contracts with CLI fallback` as active MVP work; this makes that step more real by putting the contract in shared while preserving existing CLI fallback compatibility.
- High-risk kickoff/approval trail: shared contract files are in scope, so this handoff uses the AGENTS.md high-risk budget. `shared/src/exegesis_shared/**` and `src/qual/shared/**` are not listed as lane-owned for `codex/feat-a2ui-contract*` in `THREAD_OWNERSHIP.md`; they are included here as the explicit shared-path approval request for reviewer/integrator approval. No integrator-locked files from `THREAD_OWNERSHIP.md` were edited. The work is summarized as 4 meaningful tasks.
- Task summary:
  1. Moved canonical A2UI contract ownership to `shared/src/exegesis_shared/contracts/a2ui.py`.
  2. Kept `src/qual/shared/contracts/a2ui.py` as a forwarding compatibility surface for existing imports.
  3. Updated `tests/unit/test_a2ui_contract.py` imports to exercise shared contract definitions and UI adapter behavior.
  4. Rewrote this handoff packet to match the actual source/runtime review candidate, high-risk budget, changed files, risks, and roadmap/product mapping.
- Changed-files list for source/runtime review candidate `7e117a068bd0b9597c085eda8f96a9706aad477b..c45d0139664c5afc9f3940567ef122c2e99cdfbe`:
  - `shared/src/exegesis_shared/__init__.py`
  - `shared/src/exegesis_shared/contracts/__init__.py`
  - `shared/src/exegesis_shared/contracts/a2ui.py`
  - `src/qual/shared/contracts/a2ui.py`
  - `tests/unit/test_a2ui_contract.py`
- Branch-tip-only packet correction files after `c45d0139664c5afc9f3940567ef122c2e99cdfbe`:
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
  - Shared-path approval is required because `shared/src/exegesis_shared/**` and `src/qual/shared/**` are outside the lane-owned `src/qual/ui/**` path. The intended approval path is explicit reviewer/integrator acceptance of this high-risk handoff; no integrator-locked file exception is needed.
  - `src/qual/shared/**` remains only as a compatibility forwarding surface for existing `src.qual` imports; canonical A2UI contract ownership is under `shared/src/exegesis_shared/**`.
- Roadmap/vision mapping:
  - Roadmap item(s) affected: Milestone 5 A2UI Presentation Layer contract extraction into shared while keeping renderers outside shared; supports Milestone 3 product-readiness output-contract locking.
  - Vision capability affected: client-agnostic cards/actions contract shared by engine and clients, with rendering adapters outside shared.
  - Canonical demo-path step advanced: AGENTS.md active MVP work item `A2UI contracts with CLI fallback`.
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
