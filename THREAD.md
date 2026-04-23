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
- Final fixer validation reran the required gate sequence from this worktree on `2026-04-23T22:53:09Z`; the metadata refresh below records that fresh verification for the full fixed branch state.
- Exact canonical demo-path mapping for the fixed branch state:
  - operator terms: this hardens the stable CLI command surface used to reach `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and existing CLI handoff or export flows without silent parser or catalog drift
  - direct step advanced: `preview and apply or reject a patch`
  - canonical demo-path step advanced: this work makes `preview and apply or reject a patch` more real in the CLI-first MVP loop
  - explicit step sentence: this change directly strengthens `preview and apply or reject a patch` in the CLI-first MVP loop because it fails fast when the accepted CLI token surface for that route drifts away from the approved command catalog the patch-review route depends on while the CLI remains the active operator surface, instead of letting the `patch` step appear healthy under a stale parser surface
  - operator-visible CLI path now more reliable: the `patch-review` route and its branch into `apply-patch` or `reject-patch` now fail contract validation immediately instead of silently presenting a stale accepted-token surface
  - AGENTS-required handoff statement: the canonical demo-path step this work makes more real is `preview and apply or reject a patch`
  - out of scope: no new workflow implementation for `open project/document`, `retrieve relevant material`, or export is claimed by this command-catalog contract slice
- Roadmap and vision grounding for that step:
  - roadmap hardening scope: this aligns with `ROADMAP.md` Milestone 1 `Bootstrap Flow Stabilization`, which explicitly includes command behavior hardening, because this slice hardens the accepted CLI token surface for the patch-review route instead of allowing silent drift under the same canonical command name
  - roadmap MVP-loop relevance: this also satisfies `ROADMAP.md` Milestone 5 `A2UI Presentation Layer`, whose exit criteria require the CLI to execute the MVP flow `(vault -> context -> run -> patch -> export)` against the same engine `PolicyGate`; this slice keeps the `patch` step deterministic and smoke-testable in that exact CLI-first loop
  - vision capability: this serves `PRODUCT_VISION.md` capability 4 `Operator-first control surface` by keeping the CLI patch-review step stable as the active operator surface before `Exegesis Console` is brought online on top of the same engine-facing contracts
- Concrete reason this is not second-order work:
  - `catalog.py` now makes `command_cli_contract()` fail fast if the parser surface for an accepted CLI route drifts away from the declared catalog, even when the canonical command tuple is unchanged. That removes the concrete blocker where the CLI-first patch-review step could still appear available while the operator-facing route had silently lost or reordered accepted tokens.
- Shared-file basis for the high-risk packet:
  - lane-owned implementation: `src/qual/commands/**`
  - shared test touched by the fixed branch state: `tests/unit/test_commands_catalog.py`
  - shared handoff metadata updated by this fixer: `THREAD.md`, `THREAD_PACKET.md`
  - approval provenance: `scripts/scope-check.sh` records `tests/unit/test_commands_catalog.py` as an approved shared test for `codex/feat-commands*`, and `make scope-check` passes under that repo policy
