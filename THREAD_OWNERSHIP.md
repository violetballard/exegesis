# Thread Ownership Map

Use these branch lanes to avoid duplicate work and keep the staged migration coherent.

Detailed task breakdown lives in `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/docs/TASKS.md`.

## Active engine lanes

- `codex/feat-commands*`
  - Owned paths:
    - `src/qual/commands/**`
  - Shared by approval only:
    - `src/main.py`
    - `src/qual/cli.py`
    - `src/qual/app.py`
    - `tests/unit/test_commands_catalog.py`
    - `tests/unit/test_diff_preview.py`
    - `tests/unit/test_router_quota_fallback.py`
    - `tests/unit/test_lane_profiles.py`

- `codex/feat-context-storage*`
  - Owned paths:
    - `src/qual/context/**`
    - `src/qual/storage/**`
    - `engine/src/exegesis_engine/state/**`
    - `engine/src/exegesis_engine/storage/**`
  - Shared by approval only:
    - `src/qual/config.py`

- `codex/feat-retrieval-fts*`
  - Owned paths:
    - `src/qual/retrieval/**`
    - `src/qual/engine/retrieval/**`
    - `engine/src/exegesis_engine/retrieval/**`
  - Shared by approval only:
    - `tests/unit/test_unified_retrieval.py`

- `codex/feat-a2ui-contract*`
  - Owned paths:
    - `src/qual/ui/a2ui.py`
    - `shared/src/exegesis_shared/contracts/**`
    - `shared/src/exegesis_shared/models/**`
    - `shared/src/exegesis_shared/types/**`

- `codex/feat-engine-runs*`
  - Owned paths:
    - `src/qual/engine/**`
    - `src/qual/drafting/**`
    - `engine/src/exegesis_engine/api/**`
    - `engine/src/exegesis_engine/workflow/**`
    - `engine/src/exegesis_engine/patches/**`
    - `engine/src/exegesis_engine/audit/**`
    - `engine/src/exegesis_engine/services/**`

## Defined but disabled UI lanes

- `codex/feat-console-shell*`
  - Owned paths:
    - `client-textual/src/exegesis_textual/app/**`
    - `client-textual/src/exegesis_textual/layout/**`
    - `client-textual/src/exegesis_textual/panes/**`
    - `client-textual/src/exegesis_textual/commands/**`
    - `client-textual/src/exegesis_textual/shortcuts/**`
    - `client-textual/src/exegesis_textual/inspectors/**`
    - `client-textual/src/exegesis_textual/theme/**`
  - Current status:
    - disabled until the Textual dependency is intentionally added

- `codex/feat-console-workflow*`
  - Owned paths:
    - `client-textual/src/exegesis_textual/workflow/**`
    - `client-textual/src/exegesis_textual/cards/**`
    - `client-textual/src/exegesis_textual/events/**`
  - Current status:
    - disabled until the Textual dependency is intentionally added

## Retired planning targets

- `codex/feat-ux-flow*`
- `codex/feat-console*`

These legacy lanes are superseded by the staged `engine / client-textual / shared` split and should not be restarted.

## Integrator-locked files

Only integrator/release work should edit these unless explicitly approved:
- `README.md`
- `INTEGRATION.md`
- `ROADMAP.md`
- `ARCHITECTURE.md`
- `PRODUCT_VISION.md`
- `THREAD_OWNERSHIP.md`
- `src/main.py`
- `src/qual/cli.py`
- `src/qual/app.py`

## Enforcement

- Run `make scope-check` before handoff.
- `make ci` runs scope-check automatically.
- Shared-file exceptions for approved edits can be passed as:
  - `SCOPE_ALLOW_SHARED=1 make scope-check`
