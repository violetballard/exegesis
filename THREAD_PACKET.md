## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: shared/high-risk hardening handoff for the FTS-first retrieval lane.
- Authoritative reviewed implementation base: `e40dfcb3adde628551f54f66710b232c67ad6fe7`.
- Reviewed implementation head: `1f825ff2caf97956fa04d111adcc7f7935c2a1f2`.
- Reviewed implementation range: `e40dfcb3adde628551f54f66710b232c67ad6fe7..1f825ff2caf97956fa04d111adcc7f7935c2a1f2`.
- Scope classification: high-risk because this split edits approved shared regression coverage in `tests/unit/test_unified_retrieval.py`; the 4-task cap applies.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` remains the approved shared-by-approval regression surface for `feat-retrieval-fts`.
- Integrator-locked files: none.

## Scope Completed

This split makes sparse retrieval payload rehydration fail closed when backend or mode fields drift away from the canonical FTS-first MVP contract. Policy normalization now shares explicit backend and mode validators, source bundle rehydration validates copied top-level/summary/provenance/citation backend fields, diagnostics rebuilt from sparse source bundles validate backend and mode, and provenance rehydration validates stale provenance-level backend/mode values before downstream consumers can treat them as canonical.

Canonical demo-path step advanced: `retrieve relevant material`. This split also supports `promote or gather context into the basket` by keeping sparse source/provenance/context snapshots FTS-stable before basket promotion items and later revise/apply context bundles are rebuilt.

## Tasks Completed

1. Backend/mode drift guard: enforces `sqlite_fts` and `fts_first` for sparse source bundle, diagnostics, provenance, and policy normalization.
2. Shared regression coverage: adds a unified retrieval test proving stale sparse backend and mode values fail closed.
3. Verification: re-runs the unified retrieval suite and required local gates.
4. Handoff metadata refresh: records branch, scope, files, commands, roadmap/vision mapping, and residual risk status.

Final demo-path statement: retrieval output remains FTS-first, deterministic, and promotion-ready without allowing PageIndex, hybrid, or other stale backend/mode identities into engine-facing payloads.

## Files Changed

Authoritative reviewed implementation base: `e40dfcb3adde628551f54f66710b232c67ad6fe7`.

- `src/qual/engine/retrieval/payload.py` - sparse payload policy/source/provenance/diagnostics normalization now requires backend `sqlite_fts` and mode `fts_first`.
- `tests/unit/test_unified_retrieval.py` - approved shared regression verifies sparse backend/mode drift is rejected.
- `THREAD_PACKET.md` - handoff packet refreshed with required `INTEGRATION.md` fields.

## Diff Evidence

Command: `git diff --stat e40dfcb3adde628551f54f66710b232c67ad6fe7..1f825ff2caf97956fa04d111adcc7f7935c2a1f2 -- src/qual/engine/retrieval/payload.py tests/unit/test_unified_retrieval.py`

```text
 src/qual/engine/retrieval/payload.py | 94 ++++++++++++++++++++++++------------
 tests/unit/test_unified_retrieval.py | 33 +++++++++++++
 2 files changed, 96 insertions(+), 31 deletions(-)
```

Command: `git diff --numstat e40dfcb3adde628551f54f66710b232c67ad6fe7..1f825ff2caf97956fa04d111adcc7f7935c2a1f2 -- src/qual/engine/retrieval/payload.py tests/unit/test_unified_retrieval.py`

```text
63	31	src/qual/engine/retrieval/payload.py
33	0	tests/unit/test_unified_retrieval.py
```

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File count for authoritative reviewed implementation range before packet refresh: `2 files changed`.
- Size accounting for authoritative reviewed implementation range before packet refresh: `96 insertions(+), 31 deletions(-)`, net `65 LOC`.
- AGENTS file/size status: fits high-risk limits of `<=8 files` and `<=300 net LOC`.
- Integrator exception status: approved shared regression coverage in `tests/unit/test_unified_retrieval.py`; no integrator-locked files changed.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only/deferred identifiers; sparse payloads now reject backend/mode drift instead of accepting stale PageIndex or hybrid identities.
- Remaining risks/blockers: none known for this split.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 FTS-first retrieval orchestration/source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred and stale backend/mode identities fail closed in sparse rehydration.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket`.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python3 -m unittest tests.unit.test_unified_retrieval -v` - passed, 81 tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 150 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, build, typecheck, smoke tests, and 150 unit tests.

## Metadata Write Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this split. Re-review should anchor implementation scope to `1f825ff2caf97956fa04d111adcc7f7935c2a1f2` and range `e40dfcb3adde628551f54f66710b232c67ad6fe7..1f825ff2caf97956fa04d111adcc7f7935c2a1f2`. This packet refresh does not move the reviewed implementation range; use the final fixer handoff for the packet-refresh branch tip.
