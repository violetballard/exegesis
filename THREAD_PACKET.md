## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Current branch tip used to regenerate this packet: `65a7e513067af91bceaba792e59ddd6f82928cce`
- Final HEAD SHA after this fixer commit: reported in the final fixer response.
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because this branch edits engine retrieval entrypoints/facades and approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Authoritative reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..65a7e513067af91bceaba792e59ddd6f82928cce`, plus this metadata-only packet correction commit.
- Reviewer-required post-`adfa8cda` range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..65a7e513067af91bceaba792e59ddd6f82928cce`; this range is explicitly included in re-review and contains all source/test commits after `adfa8cda`.
- Corrected traceability note: `6f4f8751cefec4b5ee12fa795b7c15fad41f388f` is source/test-bearing, not metadata-only. It changes `THREAD_PACKET.md`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. No integrator-locked files are edited in this handoff.

## Scope Completed

This packet supersedes earlier handoff packets for `codex/feat-retrieval-fts`. Earlier packets were stale because they described `378cf9a7..adfa8cda` while the branch tip had advanced to `65a7e513067af91bceaba792e59ddd6f82928cce`. Re-review must use the actual branch-tip range above, and must include every source/test commit after `adfa8cda`.

The branch implements the FTS-first retrieval MVP path. SQLite FTS remains the deterministic retrieval source of truth. PageIndex and embeddings remain compatibility-only fallback shims that fail closed and are not reintroduced as required retrieval paths. The branch hardens stable retrieval identity by preserving ordered excerpt lookup fingerprints, document and excerpt provenance, sparse context payload snapshots, citations, basket summaries, candidate-resolution snapshots, top-level context query/policy/manifest/summary snapshots, direct excerpt lookup audit identity, and fail-closed compatibility behavior.

Canonical demo-path step advanced: `retrieve relevant material`. The work makes that step more real by constructing deterministic FTS-first queries, returning document and excerpt hits with stable provenance, reconstructing sparse payload snapshots, and exposing ordered excerpt lookup fingerprints alongside excerpt IDs, text hashes, citations, candidate-resolution snapshots, and basket item fingerprints. It also supports `promote or gather context into the basket` because basket-facing summaries preserve auditable FTS lookup identity and candidate-set provenance.

## Tasks Completed

1. Canonical FTS retrieval path: added and exported the canonical retrieval query constructor, `retrieve_auto` helper, and FTS-first service behavior through both retrieval facades.
   Canonical demo-path step advanced: `retrieve relevant material`.
2. Stable retrieval provenance: emitted deterministic document/excerpt hits, citations, basket summaries, candidate-resolution snapshots, primary lookup fingerprints, ordered `excerpt_lookup_fingerprints`, and direct excerpt lookup audit identity in manifests, summaries, evidence, audit events, and result fingerprint payloads.
   Canonical demo-path step advanced: `retrieve relevant material`; supports `promote or gather context into the basket`.
3. Engine payload compatibility: normalized sparse retrieval source, summary, manifest, policy, provenance, excerpt identity, ordered identifier lists, and context payload snapshots for downstream engine flows, including top-level context bundle query, policy, manifest, summary, and citation status fields.
   Canonical demo-path step advanced: `retrieve relevant material`.
4. Shared regression coverage: extended approved shared retrieval tests for facade exports, payload reconstruction, citation/provenance helpers, FTS-only excerpt backfill, lookup fingerprints, direct excerpt lookup audit identity, and fail-closed compatibility behavior.
   Canonical demo-path step advanced: `retrieve relevant material`.

Post-`adfa8cda` source/test accounting: `git log --format='%H%x09%s' adfa8cdadd43747ffbcb612e4151e262b13e52ca..65a7e513067af91bceaba792e59ddd6f82928cce -- src/qual/retrieval src/qual/engine/retrieval tests/unit/test_unified_retrieval.py | wc -l` reports `403` source/test-bearing commits. They are included in the re-review range and grouped into the four task categories above; they are not claimed as metadata-only.

## Files Changed

Authoritative full branch-tip range: `378cf9a74a3658058079a32f186fcd254c4a4034..65a7e513067af91bceaba792e59ddd6f82928cce`.

- `.codex/kickoff_packets/feat-retrieval-fts.md` - lane kickoff metadata corrected during packet refreshes.
- `.codex/lane_meta/feat-retrieval-fts.json` - lane metadata corrected during packet refreshes.
- `THREAD_PACKET.md` - authoritative handoff packet for branch-tip review.
- `src/qual/engine/retrieval/__init__.py` - engine retrieval facade exports.
- `src/qual/engine/retrieval/fts_strategy.py` - FTS strategy integration behavior.
- `src/qual/engine/retrieval/payload.py` - deterministic retrieval payload, sparse snapshot normalization, and top-level context bundle reconstruction.
- `src/qual/retrieval/__init__.py` - retrieval facade exports.
- `src/qual/retrieval/service.py` - canonical FTS-first retrieval service, provenance, candidate-resolution citation snapshots, lookup fingerprint behavior, direct excerpt lookup audit identity, and context bundle packaging.
- `tests/unit/test_unified_retrieval.py` - approved shared-by-approval regression coverage for the retrieval contract, direct excerpt lookup audit identity, and context bundle copy safety.

Integrator-locked files: none.
Shared-by-approval files: `tests/unit/test_unified_retrieval.py`.

## Metadata Write Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this fixer pass. The sandbox rejected writes under `.codex/` during this pass, so `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` may still contain stale metadata and should not be used as the review source of truth.

## Diff Evidence

Command: `git diff --stat adfa8cdadd43747ffbcb612e4151e262b13e52ca..65a7e513067af91bceaba792e59ddd6f82928cce`

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |   36 +-
 .codex/lane_meta/feat-retrieval-fts.json     |  155 +++-
 THREAD_PACKET.md                             |  237 ++++--
 src/qual/engine/retrieval/__init__.py        |   63 +-
 src/qual/engine/retrieval/fts_strategy.py    |   59 +-
 src/qual/engine/retrieval/payload.py         | 1145 +++++++++++++++++++++++---
 src/qual/retrieval/__init__.py               |   11 +
 src/qual/retrieval/service.py                |  673 +++++++++++++--
 tests/unit/test_unified_retrieval.py         |  917 ++++++++++++++++++++-
 9 files changed, 2977 insertions(+), 319 deletions(-)
```

Command: `git diff --stat 378cf9a74a3658058079a32f186fcd254c4a4034..65a7e513067af91bceaba792e59ddd6f82928cce`

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |   36 +-
 .codex/lane_meta/feat-retrieval-fts.json     |  155 +++-
 THREAD_PACKET.md                             |  237 ++++--
 src/qual/engine/retrieval/__init__.py        |   63 +-
 src/qual/engine/retrieval/fts_strategy.py    |   59 +-
 src/qual/engine/retrieval/payload.py         | 1145 +++++++++++++++++++++++---
 src/qual/retrieval/__init__.py               |   11 +
 src/qual/retrieval/service.py                |  694 ++++++++++++++--
 tests/unit/test_unified_retrieval.py         |  955 ++++++++++++++++++++-
 9 files changed, 3005 insertions(+), 350 deletions(-)
```

Command: `git diff --name-status adfa8cdadd43747ffbcb612e4151e262b13e52ca..65a7e513067af91bceaba792e59ddd6f82928cce`

```text
M	.codex/kickoff_packets/feat-retrieval-fts.md
M	.codex/lane_meta/feat-retrieval-fts.json
M	THREAD_PACKET.md
M	src/qual/engine/retrieval/__init__.py
M	src/qual/engine/retrieval/fts_strategy.py
M	src/qual/engine/retrieval/payload.py
M	src/qual/retrieval/__init__.py
M	src/qual/retrieval/service.py
M	tests/unit/test_unified_retrieval.py
```

Command: `git show --stat 6f4f8751cefec4b5ee12fa795b7c15fad41f388f`

```text
 THREAD_PACKET.md                     | 30 +++++++++++++++---------------
 src/qual/retrieval/service.py        |  3 +++
 tests/unit/test_unified_retrieval.py | 35 +++++++++++++++++++++++++++++++++++
 3 files changed, 53 insertions(+), 15 deletions(-)
```

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File count for authoritative branch-tip range: `9 files changed`.
- Size accounting for post-`adfa8cda` source/test-inclusive range: `2977 insertions(+), 319 deletions(-)`.
- Size accounting for full branch-tip range from `378cf9a7`: `3005 insertions(+), 350 deletions(-)`.
- AGENTS high-risk file/size status: exceeds `<=8 files` and `<=300 net LOC`.
- Integrator exception status: no explicit high-risk size/file-count exception approval is present in this worktree. This packet does not claim high-risk size compliance; re-review must either reject for the missing exception or route to the integrator for explicit exception approval.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only fallback behavior; no active non-FTS retrieval path is introduced.
- Remaining risk: integration approval depends on accepting the documented high-risk size/file-count exception or requesting a split.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket` by surfacing stable FTS excerpt lookup identities, direct context-bundle retrieval snapshots, and promotion-ready basket references.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 145 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke tests, and 145 unit tests.

## Risks/Blockers

No implementation blocker is known. The branch-tip review range is now explicit and complete. The remaining approval blocker is procedural: no explicit integrator high-risk size/file-count exception approval is present in this worktree, and the actual reviewed range exceeds the AGENTS high-risk file and LOC limits.
