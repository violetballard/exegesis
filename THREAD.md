# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: `feat-commands` parser/catalog drift hardening at the real CLI enforcement point `src/qual/cli.py::parse_args()`, now evidenced from the top-level operator path `src/main.py::_dispatch()` through the approved shared regression coverage in `tests/unit/test_commands_catalog.py`, with `src/qual/commands/catalog.py` remaining the contract source.
- Canonical demo-path step advanced: `preview and apply or reject a patch`.
- Concrete canonical mapping: this slice makes the exact canonical step `preview and apply or reject a patch` more real inside `project-open/bootstrap -> retrieval -> plan-or-revise -> apply-or-reject -> export-handoff`, because the current engine-first MVP now proves parser/catalog drift is rejected from `src/main.py::_dispatch()` through `src/qual/cli.py::parse_args()` before the operator reaches the review/apply entrypoints, while `feat-console` stays disabled and the operator must rely on the CLI fallback surface.
- Milestone 3 exit-criterion mapping: this slice keeps the CLI/operator fallback able to execute the current MVP review/apply loop while Textual remains disabled by proving the `preview`, `apply`, and `reject` command surface is deterministic and drift-checked from the real operator path.
- Current MVP loop note: by proving the existing `parse_args()` guard fires from the top-level `_dispatch()` operator entrypoint using the command catalog as the contract source, this change preserves the canonical engine contract and the CLI compatibility layer that operators use to review and then apply or reject a patch before continuing to persist/export.
- Concrete canonical-path blocker removed: the direct blocker on `preview and apply or reject a patch` was missing proof that silent parser/catalog drift on the `preview`, `apply`, and `reject` CLI entrypoints would be rejected from the real operator path, including alias-level or ordering drift that could preserve canonical names while still changing the parser surface. This slice removes that blocker by proving the existing `parse_args()` enforcement fails fast from `_dispatch()` without adding new engine behavior.
- Roadmap alignment note: this is accepted current MVP CLI-compatibility work under `AGENTS.md` because the active MVP note requires `A2UI contracts with CLI fallback`, `feat-console` remains disabled, and this slice hardens the current manual CLI-first loop exactly at `preview and apply or reject a patch`. That keeps the review/apply step deterministic and migration-safe without drifting into broader workflow, audit, or new-engine behavior claims.
- Reviewer-fix satisfaction note: the handoff now names the exact canonical demo-path step it advances and limits the product-vision claim to the operator-first CLI compatibility surface only; it does not claim `Auditable state and workflow`.
- Scope clarification: this is direct blocker-removal for the exact canonical step `preview and apply or reject a patch` through command-catalog CLI compatibility and migration-safe entrypoint hardening in the existing engine-first loop. It does not add new engine behavior, persistence work, new workflow branches, or new public wrapper surfaces.
- Reissue note: this pointer and `THREAD_PACKET.md` are reissued in the final fixer pass to keep the handoff aligned with the landed operator-path proof, the explicit canonical demo-path step statement, and the clean gate rerun recorded at the current branch tip.
- Task accounting note: metadata-only packet refreshes are bookkeeping for the handoff and are not counted as completed implementation tasks.
- Risk reason: this remains a high-risk command-contract handoff because drift at operator-facing patch-review entrypoints would directly weaken the current manual CLI smoke flow, and the proof now relies on the real operator path rather than only helper-level contract access.
- Reviewed implementation evidence: `src/main.py`, `src/qual/cli.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`
- Approval basis note: implementation approval remains pinned to those files only; this fixer pass adds operator-path proof in tests and metadata refreshes, while the runtime enforcement continues to live in the existing `src/qual/cli.py::parse_args()` guard.

## Reviewed Files

- `src/main.py`
- `src/qual/commands/catalog.py`
- `src/qual/cli.py`
- `tests/unit/test_commands_catalog.py`

## Required Gates

- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
