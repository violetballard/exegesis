## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: low-risk lane-owned hardening handoff for the FTS-first retrieval lane.
- Authoritative reviewed implementation base: `0c2464e79`.
- Reviewed implementation head: final fixer commit created from this packet refresh.
- Reviewed implementation range: `0c2464e79..final fixer commit`.
- Scope classification: low-risk because this split changes only lane-owned retrieval code plus the required handoff packet.
- Approved shared-file note: none for this split; no shared regression file is edited.
- Integrator-locked files: none.

## Scope Completed

This split makes the FTS-first merge boundary fail closed when a non-FTS `StrategyRun` is passed into the canonical retrieval merge path. Hit-level source strategy checks already guarded payload contents; the run wrapper now has the same FTS-only invariant, so injected PageIndex or embeddings runs cannot be merged even if their hits are FTS-shaped.

Canonical demo-path step advanced: `retrieve relevant material`. This split also supports `promote or gather context into the basket` by keeping the retrieval result set restricted to the authoritative SQLite FTS run before downstream payload and basket promotion snapshots are built.

## Tasks Completed

1. FTS run-boundary guard: advances `retrieve relevant material` by rejecting non-FTS `StrategyRun` wrappers before hit merging.
2. Regression verification: re-runs the existing unified retrieval suite to confirm the canonical FTS result, provenance, excerpt lookup, and basket promotion contract still passes.
3. Handoff metadata refresh: records the reviewed implementation base/range, files changed, commands run, roadmap/vision mapping, and remaining risk status for this split.

Final demo-path statement: this work keeps retrieval outputs promotion-ready for basket/context flows without allowing PageIndex or embeddings runs into the active merge path.

## Files Changed

Authoritative reviewed implementation base: `0c2464e79`.

- `src/qual/retrieval/service.py` - canonical hit merging now rejects non-FTS `StrategyRun` wrappers before accepting hits.

Required packet refresh:

- `THREAD_PACKET.md` - handoff packet refreshed for this split with required INTEGRATION.md fields.

## Diff Evidence

Command: `git diff --stat 0c2464e79..HEAD`

```text
 THREAD_PACKET.md              | 66 +++++++++++++++++++++----------------------
 src/qual/retrieval/service.py |  2 ++
 2 files changed, 34 insertions(+), 34 deletions(-)
```

Command: `git diff --numstat 0c2464e79..HEAD`

```text
32	34	THREAD_PACKET.md
2	0	src/qual/retrieval/service.py
```

## Budget/Risk

- Task budget: `3/8` default task groups.
- File count for authoritative reviewed implementation range: `2 files changed`.
- Size accounting for authoritative reviewed implementation range: `34 insertions(+), 34 deletions(-)`, net `0 LOC`.
- AGENTS file/size status: fits `<=12 files` and `<=500 net LOC`.
- Integrator exception status: no shared-by-approval or integrator-locked files changed.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only/deferred; non-FTS strategy runs now fail before merge.
- Remaining risks/blockers: none known for this split.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 FTS-first retrieval orchestration/source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred and fail closed at the run merge boundary.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket`.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python -m unittest tests.unit.test_unified_retrieval -q` - passed, 79 tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 148 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke tests, and 148 unit tests.

## Metadata Write Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this split. Re-review should anchor implementation scope to the final fixer commit reported in the handoff and range `0c2464e79..final fixer commit`.
