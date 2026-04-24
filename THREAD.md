# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow `feat-commands` CLI-contract hardening in `src/qual/commands/catalog.py`, plus focused regressions in `tests/unit/test_commands_catalog.py`.
- Canonical demo-path step advanced: the Milestone 3 CLI/operator-contract bridge that keeps the engine-first loop reachable through deterministic, migration-safe entrypoints while Textual remains disabled, specifically `produce a plan or revision` -> `preview and apply or reject a patch`.
- Concrete canonical mapping: this slice makes the Milestone 3 contract-locking step more real by keeping `project-open/bootstrap -> retrieval -> plan-or-revise -> apply-or-reject -> export-handoff` reachable through deterministic, migration-safe CLI entrypoints, so the engine-first loop does not silently drift before `Exegesis Console` replaces the current operator path.
- Current MVP loop note: by hard-failing parser/catalog drift inside the existing command catalog, this change preserves the current CLI compatibility surface that operators use to run the engine-first loop end to end while Textual remains disabled.
- Concrete canonical-path blocker removed: parser/catalog drift can no longer silently change the migration-safe CLI entrypoints that bridge the current operator flow to future console consumption, removing a Milestone 3 contract-risk at the existing review/apply boundary.
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
