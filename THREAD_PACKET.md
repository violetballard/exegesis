## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval date-range validation fixer handoff for the FTS-first retrieval lane.
- Reviewed implementation base: `d31c231eaa190fa363902ec28e3ad46f5e58ac77`.
- Reviewed implementation head: `HEAD` after this fixer commit; final SHA is reported in the fixer response.
- Reviewed implementation range for re-review: `d31c231eaa190fa363902ec28e3ad46f5e58ac77..HEAD`.
- Scope classification: high-risk because this lane includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files changed: none.

## Scope Completed

This fixer keeps SQLite FTS as the authoritative MVP retrieval path and makes date-range retrieval constraints fail fast when they are malformed or reversed. `RetrievalService.retrieve_fts` and the `retrieve_auto` alias now validate date-range bounds before FTS execution, so downstream retrieval payloads cannot silently represent invalid operator constraints as an empty evidence set.

The retrieval shape remains FTS-first and deterministic. PageIndex and embeddings remain deferred compatibility surfaces, while basket promotion and later revise/apply steps get a clearer contract: no-hit results are reserved for valid searches with no matching FTS evidence, not invalid date filters.

## Tasks Completed

1. Canonical demo-path step advanced: `retrieve relevant material`. FTS retrieval now rejects invalid date-range constraints before building evidence.
2. Canonical demo-path step supported: `promote or gather context into the basket`. Valid empty evidence and invalid operator constraints are now distinguishable for basket/context flows.
3. Added approved shared regression coverage for malformed and reversed date ranges on the canonical `retrieve_auto` path.

## Files Changed

Reviewed implementation range for re-review: `d31c231eaa190fa363902ec28e3ad46f5e58ac77..HEAD`.

- `THREAD_PACKET.md` - authoritative handoff packet for this fixer pass.
- `src/qual/retrieval/service.py` - validates date-range parseability and ordering before FTS retrieval.
- `tests/unit/test_unified_retrieval.py` - covers malformed and reversed date-range rejection on the canonical retrieval path.

## Budget/Risk

- Task budget: `3/4` high-risk task groups.
- File count for reviewed implementation handoff: `3 files changed`.
- Size accounting before packet rewrite: `24 insertions(+)` across retrieval service and approved shared regression coverage.
- AGENTS file/size status: fits high-risk size limits of `<=8 files` and `<=300 net LOC`.
- Shared/integrator exception status: uses the approved shared regression surface `tests/unit/test_unified_retrieval.py`; no integrator-locked files changed.
- Routing/provider impact: none.
- PageIndex/embeddings impact: no PageIndex, embeddings, hybrid, or alternate retrieval path was added as a required MVP path.
- Remaining risks/blockers: none.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 4 FTS-first retrieval orchestration/source-attribution/auditable deterministic retrieval; Milestone 3 generation provenance contract clarity for retrieved evidence.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and deterministic operator controls.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket` by preventing invalid date filters from producing misleading empty retrieval evidence.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

Commands run for this corrected branch-tip packet on the exact worktree state to be committed by this fixer pass:

- `python -m unittest tests.unit.test_unified_retrieval` - passed 57 retrieval tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 126 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 126 unit tests.

## Metadata Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this fixer pass. The reviewed implementation range intentionally covers `d31c231eaa190fa363902ec28e3ad46f5e58ac77..HEAD` so this production retrieval date-range validation change is traceable from the prior branch tip.
