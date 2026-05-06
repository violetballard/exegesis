## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: shared/high-risk hardening handoff for the FTS-first retrieval lane.
- Authoritative reviewed implementation base: `38e13150dc2e5ae44734bd2473ae226d7f1b997d`.
- Reviewed implementation head: final fixer commit created from this packet.
- Reviewed implementation range: `38e13150dc2e5ae44734bd2473ae226d7f1b997d..final fixer commit`.
- Scope classification: high-risk because this split edits approved shared regression coverage in `tests/unit/test_unified_retrieval.py`; the 4-task cap applies.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` remains the approved shared-by-approval regression surface for `feat-retrieval-fts`.
- Integrator-locked files: none.

## Scope Completed

This split makes sparse retrieval payload policy rehydration fail closed when deferred strategy identities drift away from the canonical MVP tuple: `pageindex`, `embeddings`. Missing deferred strategy values still default to the FTS-first policy snapshot, but reordered, stale, or expanded values are rejected before downstream source/provenance/context bundles can treat them as valid retrieval policy.

Canonical demo-path step advanced: `retrieve relevant material`. This split also supports `promote or gather context into the basket` by keeping sparse retrieval snapshots policy-stable before basket promotion items and context bundles are rebuilt for later revise/apply steps.

## Tasks Completed

1. Deferred-strategy policy guard: enforces the canonical MVP deferred strategy identity during sparse payload normalization.
2. Shared regression coverage: adds a unified retrieval test proving reordered deferred strategy identities fail closed.
3. Verification: re-runs the unified retrieval suite and required local gates.
4. Handoff metadata refresh: records branch, scope, files, commands, roadmap/vision mapping, and residual risk status.

Final demo-path statement: retrieval output remains FTS-first, deterministic, and promotion-ready without allowing PageIndex or embeddings policy drift into engine-facing payloads.

## Files Changed

Authoritative reviewed implementation base: `38e13150dc2e5ae44734bd2473ae226d7f1b997d`.

- `src/qual/engine/retrieval/payload.py` - sparse payload policy normalization now requires deferred strategy ids to remain `pageindex`, `embeddings`.
- `tests/unit/test_unified_retrieval.py` - approved shared regression verifies deferred strategy drift is rejected.
- `THREAD_PACKET.md` - handoff packet refreshed with required `INTEGRATION.md` fields.

## Diff Evidence

Command: `git diff --stat 38e13150dc2e5ae44734bd2473ae226d7f1b997d -- src/qual/engine/retrieval/payload.py tests/unit/test_unified_retrieval.py`

```text
 src/qual/engine/retrieval/payload.py |  6 +++++-
 tests/unit/test_unified_retrieval.py | 24 ++++++++++++++++++++++++
 2 files changed, 29 insertions(+), 1 deletion(-)
```

Command: `git diff --numstat 38e13150dc2e5ae44734bd2473ae226d7f1b997d -- src/qual/engine/retrieval/payload.py tests/unit/test_unified_retrieval.py`

```text
5	1	src/qual/engine/retrieval/payload.py
24	0	tests/unit/test_unified_retrieval.py
```

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File count for authoritative reviewed implementation range before packet refresh: `2 files changed`.
- Size accounting for authoritative reviewed implementation range before packet refresh: `29 insertions(+), 1 deletion(-)`, net `28 LOC`.
- AGENTS file/size status: fits high-risk limits of `<=8 files` and `<=300 net LOC`.
- Integrator exception status: approved shared regression coverage in `tests/unit/test_unified_retrieval.py`; no integrator-locked files changed.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only/deferred identifiers; sparse payloads now reject deferred-strategy identity drift instead of accepting it.
- Remaining risks/blockers: none known for this split.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 FTS-first retrieval orchestration/source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred and fail closed if sparse payload policy identity drifts.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket`.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python -m pytest tests/unit/test_unified_retrieval.py` - failed because the active Python 3.14 interpreter does not have `pytest` installed.
- `python3 -m unittest tests.unit.test_unified_retrieval -v` - passed, 80 tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 149 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, build, typecheck, smoke tests, and 149 unit tests.

## Metadata Write Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this split. Re-review should anchor implementation scope to the final fixer commit reported in the handoff and range `38e13150dc2e5ae44734bd2473ae226d7f1b997d..final fixer commit`.
