# Feature -> Review Packet

## Thread Kickoff (High-Risk, Invalidated By Actual Scope)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: harden the active `feat-commands` CLI operator surface across the canonical demo path while Textual remains disabled.
- Risk reason: the reviewed basis includes shared test coverage and broad command-surface behavior changes.

### Submitted Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Budget Reconciliation Against The True Reviewed Basis

- Reviewed implementation base previously approved for comparison: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Reviewed implementation range in this resubmission: the full branch delta through `5ea27f3d960f2f2876347f2b8ce616223227a713`
- Files changed in the true reviewed basis: `9`
- Delta size in the true reviewed basis: `+9652/-485`
- Result: this is not a valid `AGENTS.md` high-risk `4`-task handoff because it exceeds the `<=8 files` and `<=300 net LOC` limits
- Required follow-up for integration promotion: split this implementation into smaller reviewable packets before promotion

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- This resubmission is not metadata-only.
- The true reviewed basis includes non-doc implementation across:
  - `scripts/scope-check.sh`
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/canonical.py`
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/diff_preview.py`
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Scope Completed

- Hardened parser-surface and command-catalog behavior, including projection-drift rejection, lookup helpers, parser-ready argv helpers, smoke argv helpers, trusted-surface helpers, and CLI shim contract support.
- Expanded demo token and shim resolution behavior so workflow, compatibility, and next-action metadata stay stable for:
  - `project-open`
  - `retrieval`
  - `patch-review`
  - `apply-patch`
  - `reject-patch`
  - `persist`
  - `export-handoff`
- Added legacy alias normalization and compatibility handling for retrieval and document-open style entrypoints.
- Stabilized diff-preview truncation, fingerprint, and no-diff payload behavior.
- Expanded regression coverage for parser surfaces, trusted/demo workflow tables, compatibility aliases, next-action metadata, and diff-preview behavior.
- Regenerated the handoff packet so its review basis, scope, budget statement, and roadmap mapping match the actual reviewed range.

## Canonical Demo-Path Mapping

- Canonical demo-path steps advanced by the true reviewed basis:
  - `open project/document`
  - `retrieval`
  - `patch-review`
  - `apply-patch`
  - `reject-patch`
  - `persist`
  - `export-handoff`
- Explicit handoff statement for `AGENTS.md`:
  - The true reviewed range hardens the CLI-first MVP route across the canonical demo path while Textual remains disabled.
- Concrete roadmap / vision mapping for the real scope:
  - `ROADMAP.md` Milestone 1 (`Bootstrap Flow Stabilization`) scope item `Command and diff-preview behavior hardening`
  - `ROADMAP.md` Milestone 2 (`Test Hardening`) scope item `Add focused unit coverage for core behaviors`
  - `ROADMAP.md` Milestone 2 (`Test Hardening`) scope item `Keep command-level probes for integration confidence`
  - `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`)
- Scope truth note:
  - this packet covers the broader command/demo/shim/diff-preview range through `5ea27f3d960f2f2876347f2b8ce616223227a713`; it does not claim the branch is command-catalog-only

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Restated the true implementation basis as the full `f8d860ed..5ea27f3d` branch delta instead of a metadata-only refresh on top of two commits.
2. Tightened the packet scope so it explicitly includes parser-surface, demo token, shim, apply/reject/persist/export-handoff, and diff-preview behavior changes.
3. Recomputed the budget and documented that the actual range is not a valid high-risk `4`-task slice under `AGENTS.md`.
4. Re-ran the required local gate suite for the true reviewed basis and refreshed the roadmap / vision mapping to match the real command surface being advanced.

### Files Changed

- `THREAD.md`
- `THREAD_PACKET.md`
- `scripts/scope-check.sh`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

### Commands Run and Outcomes

- `make scope-check`: `PASSED` (`[devex] scope-check: passed for branch 'codex/feat-commands'`)
- `./quality-format.sh --check`: `PASSED` (`[format] check passed`)
- `./quality-lint.sh`: `PASSED` (`[lint] passed`)
- `./quality-test.sh`: `PASSED` (`smoke passed`; `Ran 203 tests ... OK`)
- `./typecheck-test.sh`: `PASSED` (exit code `0`; output: `[typecheck] compiling Python sources in src/`)
- `make ci`: `PASSED` (`[devex] CI entrypoint completed`)

### Risks / Blockers

- Risks:
  - future command-surface expansion could regress parser-entrypoint invariants, logical flow-step labels, or diff-preview payload guarantees if new shim-backed tokens land without corresponding contract tests.
- Blockers:
  - the true reviewed basis exceeds the submitted high-risk budget and should be split into smaller reviewable packets before integration promotion.

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 1 (`Bootstrap Flow Stabilization`) scope item `Command and diff-preview behavior hardening`
- `ROADMAP.md` Milestone 2 (`Test Hardening`) scope item `Add focused unit coverage for core behaviors`
- `ROADMAP.md` Milestone 2 (`Test Hardening`) scope item `Keep command-level probes for integration confidence`
- Canonical demo-path steps advanced: `open project/document`, `retrieval`, `patch-review`, `apply-patch`, `reject-patch`, `persist`, and `export-handoff`
- Explicit statement of what this work makes more real: it hardens the CLI-first operator route across the current MVP demo path while Textual remains disabled.
- Concrete blocker removed on that path: it prevents parser/catalog drift, shim-token collapse, and diff-preview instability from silently changing the CLI-visible MVP command flow.
- Scope guard: this packet now describes the full reviewed branch basis truthfully; it does not represent the range as a narrow command-catalog-only slice.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`): CLI remains the first-class operator surface for the MVP, so the command contracts and diff-preview outputs in this range must stay deterministic and auditable.

### Routing / Provider Impact Note

- None.

### Proposed `README.md` Patch Text

- None.
