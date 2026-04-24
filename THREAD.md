# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow `feat-commands` CLI-contract hardening in `src/qual/commands/catalog.py`, plus focused regressions in `tests/unit/test_commands_catalog.py`.
- Canonical demo-path step advanced: `preview and apply or reject a patch`.
- Concrete canonical mapping: this slice hardens the existing patch-review/apply CLI surface inside `project-open/bootstrap -> retrieval -> plan-or-revise -> apply-or-reject -> export-handoff`, so the current engine-first loop still reaches the review/apply step through the intended entrypoints while Textual remains disabled.
- Current MVP loop note: by hard-failing parser/catalog drift inside the existing command catalog, this change preserves the current CLI compatibility surface that operators use to review and then apply or reject a patch before continuing to persist/export.
- Concrete canonical-path blocker removed: the review/apply CLI entrypoints can no longer silently drift at the alias or token level while still looking stable by canonical command name, removing a Milestone 3 blocker on the current `preview and apply or reject a patch` step.
- Roadmap alignment note: this is Milestone 3 scope because it locks an intentional user-facing CLI contract for the engine-first loop and keeps the shared command/config surface migration-safe for the upcoming console client; it does not claim broader CLI polish, new workflow reachability, or extra engine behavior.
- Scope clarification: this is CLI compatibility and migration-safe entrypoint hardening for the existing engine-first loop, centered on the `plan-or-revise` -> `apply-or-reject` operator contract. It does not add new commands, new engine behavior, persistence work, or new workflow reachability.
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
