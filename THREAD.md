# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: `feat-commands` CLI-contract hardening in `src/qual/commands/catalog.py` plus the public workflow next-action surface wrappers exported from `src/qual/commands/workflow.py` and `src/qual/commands/__init__.py`, with focused regressions in `tests/unit/test_commands_catalog.py`.
- Canonical demo-path step advanced: `preview and apply or reject a patch`.
- Concrete canonical mapping: this slice makes the exact canonical step `preview and apply or reject a patch` more real inside `project-open/bootstrap -> retrieval -> plan-or-revise -> apply-or-reject -> export-handoff`, because the current engine-first MVP can now both validate the parser-backed `preview`/`apply`/`reject` contract and ask the public commands surface which follow-up verb is valid next after `review`, `apply`, and `save`, while `feat-console` stays disabled and the operator must rely on the CLI fallback surface.
- Current MVP loop note: by hard-failing parser/catalog drift inside the existing command catalog and exporting deterministic workflow next-action lookup helpers from the public `src/qual.commands` surface, this change preserves the canonical engine contract and the CLI compatibility layer that operators use to review and then apply or reject a patch before continuing to persist/export.
- Concrete canonical-path blocker removed: the direct blocker on `preview and apply or reject a patch` was twofold: silent parser/catalog drift on the `preview`, `apply`, and `reject` CLI entrypoints, and the lack of a stable public lookup surface for the follow-up actions after `review`, `apply`, and `save`. This slice removes that blocker by forcing the review/apply CLI contract to fail fast on drift and by exposing the deterministic next-action wrappers that map the canonical loop onto preferred CLI verbs without adding new engine behavior.
- Roadmap alignment note: this is Milestone 3 scope because it hardens the current manual CLI-first loop at `preview and apply or reject a patch`, keeping the review/apply step and its immediate follow-up verbs deterministic and migration-safe while `feat-console` stays disabled and the MVP still depends on `A2UI contracts with CLI fallback`; it does not claim broader CLI polish, new workflow reachability, auditable-state progress, or extra engine behavior.
- Scope clarification: this is direct blocker-removal for the exact canonical step `preview and apply or reject a patch` through CLI compatibility, migration-safe entrypoint hardening, and public workflow next-action wrappers in the existing engine-first loop. It does not add new engine behavior, persistence work, or new workflow branches beyond surfacing existing canonical next steps.
- Task accounting note: metadata-only packet refreshes are bookkeeping for the handoff and are not counted as completed implementation tasks.
- Risk reason: this is a high-risk/shared-file handoff because it hardens the public command contract in `src/qual/commands/catalog.py`, adds public wrapper exports in `src/qual/commands/workflow.py` and `src/qual/commands/__init__.py`, and uses the explicitly approved shared regression path `tests/unit/test_commands_catalog.py`, so drift at patch-review entrypoints or their published next-action lookup surface would directly weaken the current manual CLI smoke flow.
- Reviewed implementation evidence: `src/qual/commands/catalog.py`, `src/qual/commands/workflow.py`, `src/qual/commands/__init__.py`, and `tests/unit/test_commands_catalog.py`
- Approval basis note: implementation approval remains pinned to those four files only; this pointer file is metadata-only.

## Reviewed Files

- `src/qual/commands/catalog.py`
- `src/qual/commands/workflow.py`
- `src/qual/commands/__init__.py`
- `tests/unit/test_commands_catalog.py`

## Required Gates

- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
