# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Current branch tip carries the required code-side reviewer fixes for the command CLI contract and the matching regression coverage.
- Reviewed implementation files for the fixed branch state:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- This fixer pass updates the handoff text so it matches the actual branch behavior: `command_cli_contract()` now rejects full parser-surface drift, including token add, remove, alias substitution, or reorder changes that would otherwise leave canonical command names unchanged.
- Final fixer validation reran the required gate sequence from this worktree on `2026-04-23T22:05:45Z`; the metadata refresh below records that fresh verification for the full fixed branch state.
- Exact canonical demo-path mapping for the fixed branch state:
  - operator terms: this hardens the stable CLI command surface used to reach `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and existing CLI handoff or export flows without silent parser or catalog drift
  - direct step advanced: `preview and apply or reject a patch`
  - explicit step sentence: this change directly strengthens `preview and apply or reject a patch` in the CLI-first MVP loop because it fails fast when the accepted CLI token surface for that route drifts away from the approved command catalog while Textual remains disabled
  - AGENTS-required handoff statement: the canonical demo-path step this work makes more real is `preview and apply or reject a patch`
  - out of scope: no new workflow implementation for `open project/document`, `retrieve relevant material`, or export is claimed by this command-catalog contract slice
- Concrete reason this is not second-order work:
  - `catalog.py` now makes `command_cli_contract()` fail fast if the parser surface for an accepted CLI route drifts away from the declared catalog, even when the canonical command tuple is unchanged. That removes the blocker where smoke tests could still resolve the same canonical command name while the operator-facing patch route had silently lost or reordered accepted tokens.
- Shared-file basis for the high-risk packet:
  - lane-owned implementation: `src/qual/commands/**`
  - shared test touched by the fixed branch state: `tests/unit/test_commands_catalog.py`
  - shared handoff metadata updated by this fixer: `THREAD.md`, `THREAD_PACKET.md`
  - approval provenance: `scripts/scope-check.sh` records `tests/unit/test_commands_catalog.py` as an approved shared test for `codex/feat-commands*`, and `make scope-check` passes under that repo policy
