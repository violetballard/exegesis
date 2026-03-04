# Thread Ownership Map

Use these branch lanes to avoid duplicate work and merge conflicts.

## Feature Lanes

- `codex/feat-commands*`
  - Owned paths:
    - `src/qual/commands/**`
  - Shared by approval only:
    - `src/qual/cli.py`

- `codex/feat-context-storage*`
  - Owned paths:
    - `src/qual/context/**`
    - `src/qual/storage/**`
  - Shared by approval only:
    - `src/qual/config.py`

- `codex/feat-ux-flow*`
  - Owned paths:
    - `src/qual/ui/**`
    - `src/qual/drafting/**`
    - `src/qual/engine/**`
  - Shared by approval only:
    - `src/qual/app.py`

- `codex/feat-webconsole*`
  - Owned paths:
    - `src/qual/webconsole/**`
  - Shared by approval only:
    - `WEB_CONSOLE_SPEC.md`
    - `PROVIDER_COMPAT_PROBE_SPEC.md`

## Integrator-Locked Files

Only integrator/release lanes should edit these unless explicitly approved:

- `README.md`
- `INTEGRATION.md`
- `src/main.py`
- `src/qual/cli.py`
- `src/qual/app.py`

## How Enforcement Works

- Run `make scope-check` before handoff.
- `make ci` runs scope-check automatically.
- Shared-file exceptions for approved edits can be passed as:
  - `SCOPE_ALLOW_SHARED=1 make scope-check`
