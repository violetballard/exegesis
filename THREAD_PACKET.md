## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Move A2UI card/action/selection-adjacent contracts into the client-agnostic shared package while preserving compatibility imports and CLI fallback behavior.
- Authoritative source-bearing review range: `7e117a068bd0b9597c085eda8f96a9706aad477b..c45d0139664c5afc9f3940567ef122c2e99cdfbe`.
- Review scope: This is the only submitted source/runtime review range for this re-review packet. Later commits through branch tip are packet-only corrections and do not change the source/runtime review scope.
- Scope completed: Review candidate `c45d0139664c5afc9f3940567ef122c2e99cdfbe` moves A2UI capabilities, action refs, policy-gated action execution, primitive block validation, and generic-card validation into `shared/src/exegesis_shared/contracts/a2ui.py`; keeps `src/qual/shared/contracts/a2ui.py` as a forwarding compatibility module; and updates tests to import canonical shared contract definitions while continuing to validate UI adapter behavior.
- Canonical demo-path step advanced: AGENTS.md active MVP item `A2UI contracts with CLI fallback`.
- High-risk/shared-path approval request: `shared/src/exegesis_shared/**` and `src/qual/shared/**` are outside the lane-owned `src/qual/ui/**` path for this lane and are included here for explicit reviewer/integrator approval. No integrator-locked files from `THREAD_OWNERSHIP.md` were edited in the source-bearing review range.

### Tasks Completed

1. Moved canonical A2UI contract ownership to `shared/src/exegesis_shared/contracts/a2ui.py`.
2. Kept `src/qual/shared/contracts/a2ui.py` as a forwarding compatibility surface for existing imports.
3. Updated `tests/unit/test_a2ui_contract.py` imports to exercise shared contract definitions and UI adapter behavior.
4. Rewrote this handoff packet to match the actual source/runtime review candidate, high-risk budget, changed files, risks, and roadmap/product mapping.

### Files Changed

Changed-files list for source/runtime review candidate `7e117a068bd0b9597c085eda8f96a9706aad477b..c45d0139664c5afc9f3940567ef122c2e99cdfbe`:

- `M THREAD_PACKET.md`
- `A shared/src/exegesis_shared/__init__.py`
- `A shared/src/exegesis_shared/contracts/__init__.py`
- `A shared/src/exegesis_shared/contracts/a2ui.py`
- `M src/qual/shared/contracts/a2ui.py`
- `M tests/unit/test_a2ui_contract.py`

Branch-tip-only packet correction files after `c45d0139664c5afc9f3940567ef122c2e99cdfbe`:

- `THREAD_PACKET.md`

### Commands Run

- `make scope-check` -> passed for branch `codex/feat-a2ui-contract`.
- `./quality-format.sh --check` -> passed.
- `./quality-lint.sh` -> passed shell syntax and trailing-whitespace checks.
- `./quality-test.sh` -> passed smoke tests and 123 unit tests.
- `./typecheck-test.sh` -> passed Python source compilation under `src/`.
- `make ci` -> passed setup, scope-check, format, lint, typecheck, smoke tests, and 123 unit tests.

### Risks/Blockers

- Shared-path approval is required because `shared/src/exegesis_shared/**` and `src/qual/shared/**` are outside the lane-owned `src/qual/ui/**` path. The intended approval path is explicit reviewer/integrator acceptance of this high-risk handoff.
- `src/qual/shared/**` remains only as a compatibility forwarding surface for existing `src.qual` imports; canonical A2UI contract ownership is under `shared/src/exegesis_shared/**`.
- This packet intentionally makes no packet-planner, retrieval, provider-routing, or broad branch-tip runtime claims. Those changes are outside the authoritative source-bearing review range named above.

### Roadmap/Vision Mapping

- Roadmap item affected: Milestone 5 A2UI Presentation Layer contract extraction into shared while keeping renderers outside shared.
- Vision capability affected: client-agnostic cards/actions contract shared by engine and clients, with rendering adapters outside shared.
- Canonical demo-path step advanced: AGENTS.md active MVP work item `A2UI contracts with CLI fallback`.

### Routing/Provider Impact

None. No model routing or provider configuration was touched in the source-bearing review range.

### Proposed `README.md` Patch Text

None.
