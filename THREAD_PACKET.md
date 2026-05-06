## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval cache invalidation fixer handoff for the FTS-first retrieval lane.
- Reviewed implementation base: `1696a088d5c3c83de861d9b8b3e9bafafddd27ac`.
- Reviewed implementation head: `HEAD` after this fixer commit; final SHA is reported in the fixer response.
- Reviewed implementation range for re-review: `1696a088d5c3c83de861d9b8b3e9bafafddd27ac..HEAD`.
- Scope classification: high-risk because this lane includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files changed: none.

## Scope Completed

This fixer keeps SQLite FTS as the authoritative MVP retrieval path and makes the one-entry FTS strategy cache safe across document updates. `add_or_update_document` now clears cached FTS hits after the encrypted metadata and SQLite FTS entries are updated, so a repeated query cannot reuse stale excerpts from the pre-update index.

The cache remains narrow and deterministic for repeated unchanged retrieval runs, but index mutation now invalidates it explicitly. That keeps basket promotion and later revise/apply steps anchored to current FTS evidence while preserving the existing payload, provenance, and citation bundle shapes.

## Tasks Completed

1. Canonical demo-path step advanced: `retrieve relevant material`. FTS retrieval now invalidates cached hits immediately after document text updates rebuild the FTS index.
2. Canonical demo-path step supported: `promote or gather context into the basket`. Repeated queries after document mutation now gather current excerpts instead of stale cache-backed excerpts.
3. Existing retrieval regression coverage was re-run without widening PageIndex, embeddings, hybrid, or alternate retrieval behavior.

## Files Changed

Reviewed implementation range for re-review: `1696a088d5c3c83de861d9b8b3e9bafafddd27ac..HEAD`.

- `THREAD_PACKET.md` - authoritative handoff packet for this fixer pass.
- `src/qual/retrieval/service.py` - clears the FTS strategy cache after document text/index updates.
- `src/qual/engine/retrieval/fts_strategy.py` - exposes an explicit `clear_cache` hook for FTS index mutation.

## Budget/Risk

- Task budget: `3/4` high-risk task groups.
- File count for reviewed implementation handoff: `3 files changed`.
- Size accounting before packet rewrite: `7 insertions(+)` across production retrieval files.
- AGENTS file/size status: fits high-risk size limits of `<=8 files` and `<=300 net LOC`.
- Shared/integrator exception status: no shared-by-approval or integrator-locked files changed in this fixer pass. Earlier approved shared regression coverage in `tests/unit/test_unified_retrieval.py` remains part of the lane history.
- Routing/provider impact: none.
- PageIndex/embeddings impact: no PageIndex, embeddings, hybrid, or alternate retrieval path was added as a required MVP path.
- Remaining risks/blockers: none.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 4 FTS-first retrieval orchestration/source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket` by keeping cache-backed retrieval current after source updates.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

Commands run for this corrected branch-tip packet on the exact worktree state to be committed by this fixer pass:

- `python -m unittest tests.unit.test_unified_retrieval` - passed 56 retrieval tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 125 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 125 unit tests.

## Metadata Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this fixer pass. The reviewed implementation range intentionally covers `1696a088d5c3c83de861d9b8b3e9bafafddd27ac..HEAD` so this production retrieval cache-invalidation change is traceable from the prior branch tip.
