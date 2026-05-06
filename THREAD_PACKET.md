## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Current source/test implementation head: `e746e57856d91c90b13207365a232401e4a65500`
- Final HEAD SHA after this packet finalization commit: reported in the final fixer response.
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because this branch edits engine retrieval entrypoints/facades and approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Authoritative reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..e746e57856d91c90b13207365a232401e4a65500`.
- Actual merge-candidate range against current `main`: `9511a016c20f09b43c6e7a571e0a8a49f90ea209..e746e57856d91c90b13207365a232401e4a65500`, plus this packet finalization commit through the final HEAD reported in the final fixer response.
- Reviewer-required post-`adfa8cda` range included in review scope: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..e746e57856d91c90b13207365a232401e4a65500`.
- Traceability correction: no source/test-changing commit after `adfa8cda` is classified as metadata-only. Commits including `2114d026ad9bd68cea6fb63a538771a21d17f816`, `9ca591791ae84e4f86d0b4b3e37b5bffbce09913`, `9609b4cc7d53d03668b96117ed4db1bb14f5ea4f`, `340b2b1f445391cf424f9a73bb1b7abc5fa07102`, and `e746e57856d91c90b13207365a232401e4a65500` are implementation commits and are included in the reviewed range above.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. No integrator-locked files are edited in this handoff.

## Scope Completed

This packet supersedes earlier handoff packets for `codex/feat-retrieval-fts`. Earlier packets were stale because they described narrowed implementation ranges while the branch tip had advanced through source/test-bearing retrieval commits. Re-review must use the actual implementation range above and must include every source/test commit after `adfa8cda` through `e746e57856d91c90b13207365a232401e4a65500`.

The branch implements the FTS-first retrieval MVP path. SQLite FTS remains the deterministic retrieval source of truth. PageIndex and embeddings remain compatibility-only fallback shims that fail closed and are not reintroduced as required retrieval paths. The branch hardens stable retrieval identity by preserving ordered excerpt lookup fingerprints, document and excerpt provenance, sparse context payload snapshots, citations, basket summaries, candidate-resolution snapshots, top-level context query/policy/manifest/summary snapshots, direct excerpt lookup audit identity, and fail-closed compatibility behavior.

Canonical demo-path step advanced: `retrieve relevant material`. The work makes that step more real by constructing deterministic FTS-first queries, returning document and excerpt hits with stable provenance, reconstructing sparse payload snapshots, and exposing ordered excerpt lookup fingerprints alongside excerpt IDs, text hashes, citations, candidate-resolution snapshots, basket item fingerprints, and document-level result fingerprints. It also supports `promote or gather context into the basket` because basket-facing summaries preserve auditable FTS lookup identity and candidate-set provenance.

The source-bearing commits after `adfa8cda` are part of the implementation scope. They preserve sparse basket-promotion identity when snapshots retain `basket_item_id`, reject boolean `max_results` values before Python bool/int coercion can affect retrieval limits, reject bool and non-int `max_results` values at the canonical `RetrievalConstraints` boundary, and propagate result fingerprints onto document hits so document-level evidence has the same stable identity as the top-level result payload.

## Tasks Completed

1. Canonical FTS retrieval path: added and exported the canonical retrieval query constructor, `retrieve_auto` helper, and FTS-first service behavior through both retrieval facades.
   Canonical demo-path step advanced: `retrieve relevant material`.
2. Stable retrieval provenance: emitted deterministic document/excerpt hits, citations, basket summaries, candidate-resolution snapshots, primary lookup fingerprints, ordered `excerpt_lookup_fingerprints`, direct excerpt lookup audit identity, and document-level result fingerprints in manifests, summaries, evidence, audit events, and result fingerprint payloads.
   Canonical demo-path step advanced: `retrieve relevant material`; supports `promote or gather context into the basket`.
3. Engine payload compatibility: normalized sparse retrieval source, summary, manifest, policy, provenance, excerpt identity, ordered identifier lists, and context payload snapshots for downstream engine flows, including top-level context bundle query, policy, manifest, summary, and citation status fields.
   Canonical demo-path step advanced: `retrieve relevant material`.
4. Shared regression coverage: extended approved shared retrieval tests for facade exports, payload reconstruction, citation/provenance helpers, FTS-only excerpt backfill, lookup fingerprints, direct excerpt lookup audit identity, bool and non-int constraint rejection, result fingerprint propagation, and fail-closed compatibility behavior.
   Canonical demo-path step advanced: `retrieve relevant material`.

## Files Changed

Authoritative source/test implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..e746e57856d91c90b13207365a232401e4a65500`.

- `.codex/kickoff_packets/feat-retrieval-fts.md` - lane kickoff metadata corrected during packet refreshes.
- `.codex/lane_meta/feat-retrieval-fts.json` - lane metadata corrected during packet refreshes.
- `THREAD_PACKET.md` - authoritative handoff packet for branch-tip review.
- `src/qual/engine/retrieval/__init__.py` - engine retrieval facade exports and canonical query constraint normalization, including bool `max_results` rejection.
- `src/qual/engine/retrieval/fts_strategy.py` - FTS strategy integration behavior.
- `src/qual/engine/retrieval/payload.py` - deterministic retrieval payload, sparse snapshot normalization, and top-level context bundle reconstruction.
- `src/qual/retrieval/__init__.py` - retrieval facade exports.
- `src/qual/retrieval/service.py` - canonical FTS-first retrieval service, provenance, candidate-resolution citation snapshots, lookup fingerprint behavior, direct excerpt lookup audit identity, context bundle packaging, document-level result fingerprint propagation, and canonical `max_results` type validation.
- `tests/unit/test_unified_retrieval.py` - approved shared-by-approval regression coverage for the retrieval contract, direct excerpt lookup audit identity, context bundle copy safety, bool and non-int constraint rejection, and document-hit result fingerprints.

Implementation deltas after `adfa8cda` that are explicitly included in review scope:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Integrator-locked files: none.
Shared-by-approval files: `tests/unit/test_unified_retrieval.py`.

## Diff Evidence

Command: `git diff --stat 378cf9a74a3658058079a32f186fcd254c4a4034..e746e57856d91c90b13207365a232401e4a65500`

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |   36 +-
 .codex/lane_meta/feat-retrieval-fts.json     |  155 +++-
 THREAD_PACKET.md                             |  244 ++++--
 src/qual/engine/retrieval/__init__.py        |   65 +-
 src/qual/engine/retrieval/fts_strategy.py    |   59 +-
 src/qual/engine/retrieval/payload.py         | 1158 +++++++++++++++++++++++---
 src/qual/retrieval/__init__.py               |   11 +
 src/qual/retrieval/service.py                |  779 +++++++++++++++--
 tests/unit/test_unified_retrieval.py         | 1033 ++++++++++++++++++++++-
 9 files changed, 3200 insertions(+), 340 deletions(-)
```

Command: `git diff --stat 9511a016c20f09b43c6e7a571e0a8a49f90ea209..e746e57856d91c90b13207365a232401e4a65500`

```text
 THREAD_PACKET.md                      | 271 ++++++++++++-----------
 src/qual/engine/retrieval/__init__.py |   2 +
 src/qual/engine/retrieval/payload.py  | 399 +++++++++++++++++++++++++++-------
 src/qual/retrieval/service.py         | 230 +++++++++++++++++---
 tests/unit/test_unified_retrieval.py  | 319 +++++++++++++++++++++++++++
 5 files changed, 983 insertions(+), 238 deletions(-)
```

Command: `git show --stat --name-status 340b2b1f445391cf424f9a73bb1b7abc5fa07102..e746e57856d91c90b13207365a232401e4a65500`

```text
commit e746e57856d91c90b13207365a232401e4a65500
M	src/qual/retrieval/service.py
M	tests/unit/test_unified_retrieval.py
```

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File count for authoritative source/test implementation range: `9 files changed`.
- Size accounting for authoritative source/test implementation range: `3200 insertions(+), 340 deletions(-)`.
- File count for actual merge-candidate range against current `main`: `5 files changed`.
- Size accounting for actual merge-candidate range against current `main`: `983 insertions(+), 238 deletions(-)` before this packet finalization commit.
- AGENTS high-risk file/size status: exceeds `<=8 files` and `<=300 net LOC` in the authoritative review range, and exceeds `<=300 net LOC` in the actual merge-candidate range.
- Integrator exception status: no explicit high-risk size/file-count exception approval is present in this worktree. This packet does not claim high-risk size compliance; re-review must either reject for the missing exception or route to the integrator for explicit exception approval.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only fallback behavior; no active non-FTS retrieval path is introduced.
- Remaining risk: integration approval depends on accepting the documented high-risk size/file-count exception or requesting a split.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket` by surfacing stable FTS excerpt lookup identities, direct context-bundle retrieval snapshots, promotion-ready basket references, and document-hit result fingerprints.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`; scope-check reported no branch policy and skipped policy-specific checks, then passed.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_constraints_reject_bool_and_non_int_max_results` - passed.
- `python -m unittest tests.unit.test_unified_retrieval` - passed 78 focused retrieval tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 147 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke tests, and 147 unit tests.

## Metadata Write Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this fixer pass. The patch tool allowed writes to the root packet but rejected writes under `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` as outside the project, so those `.codex` packet surfaces still contain stale metadata and must not be used as review source of truth. This root packet corrects their stale claims by explicitly including the actual source/test-bearing range through `e746e57856d91c90b13207365a232401e4a65500`.

## Risks/Blockers

No implementation blocker is known. The branch-tip review range is now explicit and complete in `THREAD_PACKET.md`. The remaining approval blockers are procedural: no explicit integrator high-risk size/file-count exception approval is present in this worktree, the actual reviewed range exceeds the AGENTS high-risk file and LOC limits, and `.codex` packet surfaces could not be updated by the available patch tool.
