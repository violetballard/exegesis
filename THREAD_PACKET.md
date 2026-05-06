## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval feature hardening handoff for the FTS-first retrieval lane.
- Implementation base before this split: `48b006dc2da0884553615c74176dd48ab7ad57e5`.
- Final branch tip: reported in the final handoff after commit creation.
- Reviewed implementation range for this split: `48b006dc2da0884553615c74176dd48ab7ad57e5..FINAL_BRANCH_TIP`.
- Scope classification: high-risk under the retrieval kickoff packet because the lane carries approved shared regression coverage history; this split changes one lane-owned retrieval implementation file plus this required handoff packet.
- Integrator-locked files: none.

## Scope Completed

This split hardens final FTS hit ordering so the rank and score exposed in hit provenance are aligned with the final deduplicated, truncated output order. Retrieval can still run only through the SQLite FTS path, but downstream citation bundles, context bundles, and basket promotion items now consume post-merge ranks rather than any stale pre-deduplication ranks.

Canonical demo-path step advanced: `retrieve relevant material`. This also supports `promote or gather context into the basket` because basket promotion items and citation snapshots inherit deterministic final excerpt ranks that match the actual result order used by engine consumers.

## Tasks Completed

1. Final-rank hardening: added a canonical post-merge rank pass for deduplicated FTS hits.
2. Score alignment: recalculated hit scores from the final output rank so score and provenance rank cannot diverge after duplicate removal or truncation.
3. FTS-only preservation: kept the existing FTS-only strategy checks, PageIndex/embeddings fail-closed behavior, and retrieval payload shape intact.
4. Verification and handoff: re-ran the unified retrieval suite and all required local gates, then refreshed this handoff packet.

Final demo-path statement: retrieval output remains FTS-first, deterministic, and promotion-ready, with citation and basket promotion ranks now tied to the final result order the engine will consume.

## Files Changed

Implementation base before this split: `48b006dc2da0884553615c74176dd48ab7ad57e5`.

- `src/qual/retrieval/service.py` - final merged FTS hits are re-ranked after deduplication/truncation so provenance rank and score match final output order.
- `THREAD_PACKET.md` - handoff packet refreshed with required `INTEGRATION.md` fields.

## Diff Evidence

Command: `git diff --stat HEAD -- src/qual/retrieval/service.py`

```text
 src/qual/retrieval/service.py | 13 ++++++++++++-
 1 file changed, 12 insertions(+), 1 deletion(-)
```

Command: `git diff --numstat HEAD -- src/qual/retrieval/service.py`

```text
12	1	src/qual/retrieval/service.py
```

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File count for implementation change before packet refresh: `1 file changed`.
- Size accounting for implementation change before packet refresh: `12 insertions(+), 1 deletion(-)`, net `11 LOC`.
- AGENTS file/size status: fits high-risk limits of `<=8 files` and `<=300 net LOC`.
- Shared/integrator exception status: none needed; no shared regression or integrator-locked file changed in this split.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only/deferred identifiers; no PageIndex, embeddings, hybrid, or alternate retrieval path was added.
- Remaining risks/blockers: none known for this split.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 FTS-first retrieval orchestration/source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket`.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python3 -m unittest tests.unit.test_unified_retrieval -v` - passed, 81 tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, build, typecheck, smoke tests, and unit tests.

## Metadata Write Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this split. The final branch tip is intentionally reported in the final handoff after commit creation because embedding the commit SHA inside the commit would become stale immediately.
