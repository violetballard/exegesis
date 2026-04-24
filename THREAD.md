# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: `feat-commands` catalog/parser determinism hardening for the existing CLI contract in `src/qual/commands/catalog.py`, evidenced at `src/qual/cli.py::parse_args()` from `src/main.py::_dispatch()` with focused regression coverage in `tests/unit/test_commands_catalog.py`.
- Scope / plan alignment: this handoff directly advances the canonical demo-path step `preview and apply or reject a patch` by proving the current CLI fallback rejects catalog/parser drift before the operator reaches the existing `preview`, `apply`, or `reject` entrypoints.
- High-risk planned-task framing: each completed task in the packet is explicitly tied to the canonical demo-path step `preview and apply or reject a patch`: prove the real operator path exercises the existing `parse_args()` guard, keep `src/qual/commands/catalog.py` authoritative for canonical command ordering and parser-surface drift detection, add focused regression coverage for alias/token-surface drift rejection, and rerun the required gates for this narrow CLI-compatibility slice.
- Per-task canonical mapping note: `THREAD_PACKET.md` now includes an explicit task-by-task mapping section showing how tasks 1-4 each advance the same canonical step `preview and apply or reject a patch`, so the handoff no longer relies on implication.
- Canonical demo-path step advanced: `preview and apply or reject a patch`.
- Concrete canonical mapping: this slice makes `preview and apply or reject a patch` more reliable by proving the catalog-defined parser surface and ordering are rejected when they drift from `src/main.py::_dispatch()` through `src/qual/cli.py::parse_args()` before the operator reaches the existing `preview`, `apply`, or `reject` entrypoints.
- Milestone 3 exit-criterion mapping: this is a narrow CLI-compatibility safeguard for the Milestone 3 loop because it keeps the `preview`, `apply`, and `reject` entrypoints deterministic and drift-checked on the real operator path while Textual remains disabled.
- Current MVP loop note: by proving the existing `parse_args()` guard fires from the top-level `_dispatch()` operator entrypoint using the command catalog as the contract source, this change preserves the active CLI compatibility layer for the patch-review step without claiming new workflow or persistence behavior.
- Concrete canonical-path blocker removed: the direct blocker on `preview and apply or reject a patch` was missing proof that silent catalog/parser drift on the `preview`, `apply`, and `reject` CLI entrypoints would be rejected from the real operator path, including alias-level or ordering drift that could preserve canonical names while still changing the parser surface. This slice removes that blocker by proving the existing `parse_args()` enforcement fails fast from `_dispatch()` without adding new engine behavior.
- Reviewer example coverage note: the current regression slice now explicitly covers the reviewer-called parser-surface mutations of dropping `diff`, adding `context`, and reordering or altering the explicit CLI entrypoint list while canonical command names remain unchanged.
- Roadmap alignment note: this is accepted current MVP CLI-compatibility work under `AGENTS.md` because the active MVP note requires `A2UI contracts with CLI fallback`, `feat-console` remains disabled, and this slice hardens the current manual CLI-first loop exactly at `preview and apply or reject a patch`. The Milestone 3 linkage is limited to catalog/parser determinism for the existing review/apply CLI surface, not broader command-surface completion.
- Reviewer-fix satisfaction note: the handoff now names one exact canonical demo-path step and limits the product-vision claim to narrow CLI compatibility for the existing operator surface; it does not claim workflow/audit progress.
- Scope clarification: this is direct blocker-removal for the exact canonical step `preview and apply or reject a patch` through command-catalog CLI compatibility and migration-safe entrypoint hardening in the existing engine-first loop. It does not add new engine behavior, persistence work, new workflow branches, or new public wrapper surfaces.
- Reissue note: this pointer and `THREAD_PACKET.md` are reissued in the final fixer pass to keep the handoff aligned with the landed operator-path proof, the explicit canonical demo-path step statement, and the clean required-gate rerun re-verified on `2026-04-24` at pre-commit HEAD `ab52aaa2b`.
- Final revalidation note: this fixer refresh added one focused regression in `tests/unit/test_commands_catalog.py` for the reviewer-called `context` alias drift case, then reran `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` at pre-commit HEAD `ab52aaa2b`.
- Current fixer rerun status: the required gate sequence passed again on `2026-04-24` at pre-commit HEAD `ab52aaa2b`, and this metadata-only refresh exists to bind that clean rerun to the new final fixer HEAD without broadening the reviewed implementation claim.
- Task accounting note: metadata-only packet refreshes are bookkeeping for the handoff and are not counted as completed implementation tasks.
- Risk reason: this remains a high-risk command-contract handoff because drift at operator-facing patch-review entrypoints would directly weaken the current manual CLI smoke flow, and the proof now relies on the real operator path rather than only helper-level contract access.
- Reviewed implementation evidence: `src/main.py`, `src/qual/cli.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`
- Approval basis note: implementation approval remains pinned to those files only; this fixer pass adds one more parser-surface regression test and packet wording refreshes, while the runtime enforcement continues to live in the existing `src/qual/cli.py::parse_args()` guard.

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
