# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Current branch tip carries the required code-side reviewer fixes for the command CLI contract and the matching regression coverage, including explicit assertions that parser-surface drift is rejected even when canonical names still match.
- Reviewed implementation commit pinned for re-review: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Metadata-only packet refresh commits after that implementation commit are out of review scope unless a regenerated handoff says otherwise.
- Reviewed implementation files for the fixed branch state:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- This fixer pass updates the handoff text so it matches the actual branch behavior already present at the current branch tip: `command_cli_contract()` now rejects full parser-surface drift, including token add, remove, alias substitution, or reorder changes that would otherwise leave canonical command names unchanged.
- Final fixer validation reran the required gate sequence from this worktree on `2026-04-23T22:55:41Z`; the metadata refresh below records that fresh verification for the full fixed branch state.
- Exact canonical demo-path mapping for the fixed branch state:
  - operator terms: this hardens the stable CLI command surface used to reach `open project/document` without silent parser or catalog drift while the CLI remains the active operator surface
  - direct step advanced: `open project/document`
  - canonical demo-path step advanced: this work makes `open project/document` more real in the CLI-first MVP loop
  - explicit step sentence: this change directly strengthens `open project/document` because deterministic CLI contract enforcement keeps the Milestone 3 compatibility entrypoint stable while Textual remains disabled, instead of letting the project-opening route appear healthy under a stale parser surface
  - operator-visible CLI path now more reliable: the project-opening command entrypoint now fails contract validation immediately instead of silently presenting a stale accepted-token surface
  - AGENTS-required handoff statement: the canonical demo-path step this work makes more real is `open project/document`
  - out of scope: no new workflow implementation for retrieval, patch review, or export is claimed by this command-catalog contract slice
- Roadmap and vision grounding for that step:
  - roadmap hardening scope: this aligns with `ROADMAP.md` Milestone 3 `Product Readiness`, specifically the requirement to define and lock user-facing output contracts, because this slice keeps the project-opening CLI entrypoint intentional and deterministic instead of allowing silent parser drift under the same canonical command name
  - roadmap MVP-loop relevance: this supports the active `feat-commands` CLI-compatibility lane by keeping the operator-facing command entrypoint stable while Textual remains disabled
  - vision capability: this serves `PRODUCT_VISION.md` capability 4 `Operator-first control surface` by keeping the CLI project-opening step stable as the active operator surface before `Exegesis Console` is brought online on top of the same engine-facing contracts
- Concrete reason this is not second-order work:
  - `catalog.py` now makes `command_cli_contract()` fail fast if the parser surface for an accepted CLI route drifts away from the declared catalog, even when the canonical command tuple is unchanged. That removes the concrete blocker where the CLI-first project-opening step could still appear available while the operator-facing entrypoint had silently lost or reordered accepted tokens.
- Shared-file basis for the high-risk packet:
  - lane-owned implementation: `src/qual/commands/**`
  - shared test touched by the fixed branch state: `tests/unit/test_commands_catalog.py`
  - shared handoff metadata updated by this fixer: `THREAD.md`, `THREAD_PACKET.md`
  - approval provenance: `scripts/scope-check.sh` records `tests/unit/test_commands_catalog.py` as an approved shared test for `codex/feat-commands*`, and `make scope-check` passes under that repo policy
