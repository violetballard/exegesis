# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: `feat-commands` command-catalog CLI-contract hardening in `src/qual/commands/catalog.py`, with the approved shared regression coverage in `tests/unit/test_commands_catalog.py`.
- Canonical demo-path step advanced: `open project/document and continue working`.
- Concrete canonical mapping: this slice makes the canonical CLI/operator step `open project/document and continue working` more real inside `project-open/bootstrap -> retrieval -> patch-review -> apply-or-reject -> persist -> export-handoff`, because the current engine-first MVP can now reject parser/catalog drift before the operator relies on the command surface that carries the session forward while `feat-console` stays disabled and the CLI fallback remains authoritative.
- Milestone 3 exit-criterion mapping: this slice keeps the CLI/operator fallback able to execute the current MVP loop while Textual remains disabled by making the `bootstrap`, `preview`, `apply`, and `reject` command surface deterministic and drift-checked.
- Current MVP loop note: by hard-failing parser/catalog drift inside the existing command catalog, this change preserves the canonical engine contract and the CLI compatibility layer that operators use to open a project/document and continue working through the current manual loop.
- Concrete canonical-path blocker removed: the direct blocker on `open project/document and continue working` was silent parser/catalog drift on the `bootstrap`, `preview`, `apply`, and `reject` CLI entrypoints, including alias-level or ordering drift that could preserve canonical names while still changing the parser surface. This slice removes that blocker by forcing the operator-facing CLI contract to fail fast on drift without adding new engine behavior.
- Roadmap alignment note: this is Milestone 3 scope because it supports the CLI compatibility exit of the current manual loop while `feat-console` stays disabled, keeping the command surface deterministic for the active MVP path and narrowing the claim to `Canonical engine contract` rather than broader workflow or audit progress.
- Scope clarification: this is direct blocker-removal for the canonical `open project/document and continue working` operator step through command-catalog CLI compatibility and migration-safe entrypoint hardening in the existing engine-first loop. It does not add new engine behavior, persistence work, new workflow branches, or new public wrapper surfaces.
- Task accounting note: metadata-only packet refreshes are bookkeeping for the handoff and are not counted as completed implementation tasks.
- Risk reason: this is a high-risk/shared-file handoff because it hardens the public command contract in `src/qual/commands/catalog.py` and uses the explicitly approved shared regression path `tests/unit/test_commands_catalog.py`, so drift at operator-facing CLI entrypoints would directly weaken the current manual CLI smoke flow.
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
