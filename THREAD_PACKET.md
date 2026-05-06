## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk split retrieval handoff for the FTS-first retrieval lane.
- Reviewed implementation base: `378cf9a74a3658058079a32f186fcd254c4a4034`.
- Reviewed implementation head: `HEAD` after this fixer commit; final SHA is reported in the fixer response.
- Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`.
- Scope classification: high-risk because this lane touches retrieval service behavior and approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files changed: none.

## Scope Completed

This fixer split the branch-tip merge candidate back to the smaller `adfa8cdadd43747ffbcb612e4151e262b13e52ca` implementation slice plus corrected packet metadata. Production and test changes that appeared after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` were removed from the current merge candidate because no explicit integrator-approved high-risk file/LOC exception exists in the worktree evidence.

The reviewed branch-tip implementation keeps SQLite FTS as the authoritative excerpt lookup path for the MVP. It removes PageIndex fallback from excerpt fetching, fails closed for PageIndex-only or non-FTS excerpt identifiers, and keeps regression coverage tied to the FTS-only lookup behavior.

Before re-review: this work makes `retrieve relevant material` more real by ensuring excerpt lookup resolves through the FTS-backed retrieval path instead of silently falling back to PageIndex-only data. It supports `promote or gather context into the basket` by keeping the retrieved excerpt source deterministic before later basket-promotion metadata hardening is split into a separate handoff.

## Tasks Completed

1. Canonical demo-path step advanced: `retrieve relevant material`. FTS-only excerpt lookup now rejects PageIndex-only or non-FTS excerpt identifiers instead of using PageIndex fallback behavior.
2. Canonical demo-path step advanced: `retrieve relevant material`; supports `promote or gather context into the basket`. Regression coverage verifies FTS-backed excerpt lookup and fail-closed fallback behavior so downstream basket promotion starts from an auditable retrieval source.

## Files Changed

Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`.

- `.codex/kickoff_packets/feat-retrieval-fts.md` - protected lane kickoff metadata changed by earlier packet commits; root `THREAD_PACKET.md` is authoritative for re-review.
- `.codex/lane_meta/feat-retrieval-fts.json` - protected lane metadata changed by earlier packet commits; root `THREAD_PACKET.md` is authoritative for re-review.
- `THREAD_PACKET.md` - authoritative handoff packet corrected to the actual branch-tip split candidate.
- `src/qual/retrieval/service.py` - FTS-only excerpt lookup behavior for the reviewed split slice.
- `tests/unit/test_unified_retrieval.py` - shared regression coverage for FTS-only excerpt lookup and fail-closed fallback behavior.

## Reviewer Required Fixes Addressed

1. Regenerated this packet against the actual intended merge candidate range: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`.
2. Removed the false traceability claim that later packet-refresh commits were metadata-only. Commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` included production/test changes, so those production/test changes were removed from this merge candidate by the split.
3. Resolved the high-risk budget overage by splitting the branch-tip candidate down to 5 changed files and net 173 LOC, which fits the high-risk limits of `<=8 files` and `<=300 net LOC`.
4. Re-ran the required gates on the corrected branch-tip target; outcomes are listed under `Commands Run`.
5. Kept the demo-path mapping explicit in `Scope Completed` and `Tasks Completed`.

## Traceability Corrections

- The reviewed implementation range is `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`; it covers the actual branch tip after this splitter/fixer commit.
- `adfa8cdadd43747ffbcb612e4151e262b13e52ca` is the retained implementation slice.
- Production/test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` were implementation work, not metadata-only packet refreshes, and are no longer part of this merge candidate.
- The protected `.codex` metadata files may still contain stale historical wording because this worktree cannot write those Box-backed paths, but they are listed in the changed-file accounting and superseded by this root packet.

## Diff Evidence

Command to verify final review size:

```text
git diff --stat 378cf9a74a3658058079a32f186fcd254c4a4034..HEAD
```

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |  36 ++++++-
 .codex/lane_meta/feat-retrieval-fts.json     | 155 ++++++++++++++++++++++++---
 THREAD_PACKET.md                             | 143 +++++++++++++-----------
 src/qual/retrieval/service.py                |  21 +---
 tests/unit/test_unified_retrieval.py         |  38 ++++---
 5 files changed, 283 insertions(+), 110 deletions(-)
```

## Budget/Risk

- Task budget: `2/4` high-risk task groups.
- File count for reviewed implementation handoff: `5 files changed`.
- Size accounting for reviewed implementation handoff: `283 insertions(+), 110 deletions(-)`, net `173 LOC`.
- AGENTS file/size status: fits high-risk size limits of `<=8 files` and `<=300 net LOC`.
- Shared/integrator exception status: `tests/unit/test_unified_retrieval.py` is approved shared regression coverage for the retrieval lane; no integrator-locked files changed.
- Routing/provider impact: none.
- PageIndex/embeddings impact: no PageIndex, embeddings, hybrid, or alternate retrieval path was added as a required MVP path.
- Remaining risks/blockers: protected `.codex` metadata files could not be rewritten in this worktree; the root `THREAD_PACKET.md` is the authoritative review packet.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 4 FTS-first retrieval orchestration/source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket`.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

Commands re-run for this corrected branch-tip packet on the exact worktree state committed by this fixer pass:

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 124 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 124 unit tests.

## Metadata Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this fixer pass. The reviewed implementation range intentionally covers `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` so all production and test changes present at the branch tip are traceable.
