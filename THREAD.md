# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow `feat-commands` CLI-contract hardening in `src/qual/commands/catalog.py`, plus focused regressions in `tests/unit/test_commands_catalog.py`.
- Canonical demo-path step advanced: `preview and apply or reject a patch`.
- Concrete canonical mapping: this slice makes the exact canonical step `preview and apply or reject a patch` more real inside `project-open/bootstrap -> retrieval -> plan-or-revise -> apply-or-reject -> export-handoff`, so the current engine-first MVP still reaches that review/apply step through deterministic `preview`, `apply`, and `reject` entrypoints while `feat-console` stays disabled and the operator must rely on the CLI fallback surface.
- Current MVP loop note: by hard-failing parser/catalog drift inside the existing command catalog, this change preserves the current CLI compatibility surface that operators use to review and then apply or reject a patch before continuing to persist/export.
- Concrete canonical-path blocker removed: the direct blocker on `preview and apply or reject a patch` was silent parser/catalog drift on the `preview`, `apply`, and `reject` CLI entrypoints, which could still look stable by canonical command name while routing the manual review/apply step away from the catalog-backed contract.
- Roadmap alignment note: this is Milestone 3 scope because it hardens the current manual CLI-first loop at `preview and apply or reject a patch`, keeping that review/apply engine contract deterministic and migration-safe while `feat-console` stays disabled and the MVP still depends on `A2UI contracts with CLI fallback`; it does not claim broader CLI polish, new workflow reachability, auditable-state progress, or extra engine behavior.
- Scope clarification: this is direct blocker-removal for the exact canonical step `preview and apply or reject a patch` through CLI compatibility and migration-safe entrypoint hardening in the existing engine-first loop. It does not add new commands, new engine behavior, persistence work, or new workflow reachability.
- Task accounting note: metadata-only packet refreshes are bookkeeping for the handoff and are not counted as completed implementation tasks.
- Risk reason: this is a high-risk/shared-file handoff because it hardens the public command contract in `src/qual/commands/catalog.py` and uses the explicitly approved shared regression path `tests/unit/test_commands_catalog.py`, so parser drift at patch-review entrypoints would directly weaken the current manual CLI smoke flow.
- Reviewed implementation evidence: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`
- Approval basis note: implementation approval remains pinned to those two files only; this pointer file is metadata-only.

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Required Gates

- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
