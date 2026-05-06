## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Current branch tip used to regenerate this packet: `669e6933692ef83f76875b64565b1a33a75cff2e`
- Final HEAD SHA after this fixer commit: reported in the final fixer response.
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because this branch edits engine retrieval entrypoints/facades and approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Authoritative reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..669e6933692ef83f76875b64565b1a33a75cff2e`, plus this source-bearing fixer commit through the final HEAD reported in the final fixer response.
- Reviewer-required post-`adfa8cda` range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..669e6933692ef83f76875b64565b1a33a75cff2e`, plus this source-bearing fixer commit through the final HEAD reported in the final fixer response; this range is explicitly included in re-review and contains every source/test-bearing commit after `adfa8cda`.
- Corrected traceability note: `2114d026ad9bd68cea6fb63a538771a21d17f816` and `9ca591791ae84e4f86d0b4b3e37b5bffbce09913` are source/test-bearing retrieval commits, not metadata-only packet refreshes. They change `THREAD_PACKET.md`, `src/qual/engine/retrieval/payload.py`, and `tests/unit/test_unified_retrieval.py`. Earlier source/test-bearing commits after `adfa8cda`, including `6f4f8751cefec4b5ee12fa795b7c15fad41f388f`, are also included in the reviewed range.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. No integrator-locked files are edited in this handoff.

## Scope Completed

This packet supersedes earlier handoff packets for `codex/feat-retrieval-fts`. Earlier packets were stale because they described narrowed implementation ranges while the branch tip had advanced through source/test-bearing retrieval commits. Re-review must use the actual branch-tip range above, and must include every source/test commit after `adfa8cda` through the final HEAD reported in the final fixer response.

The branch implements the FTS-first retrieval MVP path. SQLite FTS remains the deterministic retrieval source of truth. PageIndex and embeddings remain compatibility-only fallback shims that fail closed and are not reintroduced as required retrieval paths. The branch hardens stable retrieval identity by preserving ordered excerpt lookup fingerprints, document and excerpt provenance, sparse context payload snapshots, citations, basket summaries, candidate-resolution snapshots, top-level context query/policy/manifest/summary snapshots, direct excerpt lookup audit identity, and fail-closed compatibility behavior.

Canonical demo-path step advanced: `retrieve relevant material`. The work makes that step more real by constructing deterministic FTS-first queries, returning document and excerpt hits with stable provenance, reconstructing sparse payload snapshots, and exposing ordered excerpt lookup fingerprints alongside excerpt IDs, text hashes, citations, candidate-resolution snapshots, and basket item fingerprints. It also supports `promote or gather context into the basket` because basket-facing summaries preserve auditable FTS lookup identity and candidate-set provenance.

The source-bearing commits through `9ca591791ae84e4f86d0b4b3e37b5bffbce09913` make real retrieval code changes: sparse retrieval payload normalization treats `basket_item_id` as the same FTS excerpt identity as `item_id` and `excerpt_id`, canonicalizes that identity back onto rehydrated basket-promotion item snapshots, and keeps sparse basket counts stable when downstream context snapshots retain only the basket-facing identifier.

This fixer pass adds one owned source-bearing retrieval facade hardening change after `669e6933692ef83f76875b64565b1a33a75cff2e`: canonical query construction now rejects boolean `max_results` values instead of accepting Python's `bool`-as-`int` coercion. That keeps result limits explicit and prevents accidental one-result or zero-result retrieval contracts from loose engine payloads.

## Tasks Completed

1. Canonical FTS retrieval path: added and exported the canonical retrieval query constructor, `retrieve_auto` helper, and FTS-first service behavior through both retrieval facades.
   Canonical demo-path step advanced: `retrieve relevant material`.
2. Stable retrieval provenance: emitted deterministic document/excerpt hits, citations, basket summaries, candidate-resolution snapshots, primary lookup fingerprints, ordered `excerpt_lookup_fingerprints`, and direct excerpt lookup audit identity in manifests, summaries, evidence, audit events, and result fingerprint payloads.
   Canonical demo-path step advanced: `retrieve relevant material`; supports `promote or gather context into the basket`.
3. Engine payload compatibility: normalized sparse retrieval source, summary, manifest, policy, provenance, excerpt identity, ordered identifier lists, and context payload snapshots for downstream engine flows, including top-level context bundle query, policy, manifest, summary, and citation status fields.
   Canonical demo-path step advanced: `retrieve relevant material`.
4. Shared regression coverage: extended approved shared retrieval tests for facade exports, payload reconstruction, citation/provenance helpers, FTS-only excerpt backfill, lookup fingerprints, direct excerpt lookup audit identity, and fail-closed compatibility behavior.
   Canonical demo-path step advanced: `retrieve relevant material`.

Latest source-bearing task: preserved sparse basket-promotion identity when snapshots retain `basket_item_id` without `item_id`/`excerpt_id`, so promotion-ready context snapshots still deduplicate and count the same FTS excerpt once.

Current source-bearing fixer task: tightened canonical retrieval query normalization so boolean `max_results` values fail closed before retrieval execution.

Source/test accounting for the corrected review range: `git log --format='%H%x09%s' 378cf9a74a3658058079a32f186fcd254c4a4034..9ca591791ae84e4f86d0b4b3e37b5bffbce09913 -- src/qual/retrieval src/qual/engine/retrieval tests/unit/test_unified_retrieval.py | wc -l` reports `407` source/test-bearing commits before the later retrieval facade hardening passes. They are included in the re-review range and grouped into the four task categories above; they are not claimed as metadata-only.

## Files Changed

Authoritative full branch-tip range: `378cf9a74a3658058079a32f186fcd254c4a4034..669e6933692ef83f76875b64565b1a33a75cff2e`, plus this source-bearing fixer commit through the final HEAD reported in the final fixer response.

- `.codex/kickoff_packets/feat-retrieval-fts.md` - lane kickoff metadata corrected during packet refreshes.
- `.codex/lane_meta/feat-retrieval-fts.json` - lane metadata corrected during packet refreshes.
- `THREAD_PACKET.md` - authoritative handoff packet for branch-tip review.
- `src/qual/engine/retrieval/__init__.py` - engine retrieval facade exports and canonical query constraint normalization.
- `src/qual/engine/retrieval/fts_strategy.py` - FTS strategy integration behavior.
- `src/qual/engine/retrieval/payload.py` - deterministic retrieval payload, sparse snapshot normalization, and top-level context bundle reconstruction.
- `src/qual/retrieval/__init__.py` - retrieval facade exports.
- `src/qual/retrieval/service.py` - canonical FTS-first retrieval service, provenance, candidate-resolution citation snapshots, lookup fingerprint behavior, direct excerpt lookup audit identity, and context bundle packaging.
- `tests/unit/test_unified_retrieval.py` - approved shared-by-approval regression coverage for the retrieval contract, direct excerpt lookup audit identity, and context bundle copy safety.

Latest source-bearing delta from `2114d026ad9bd68cea6fb63a538771a21d17f816..9ca591791ae84e4f86d0b4b3e37b5bffbce09913`:

- `THREAD_PACKET.md` - authoritative handoff packet refreshed for this pass.
- `src/qual/engine/retrieval/payload.py` - sparse basket-promotion item identity now recognizes `basket_item_id` alongside `item_id` and `excerpt_id`, and canonicalizes that identity for reconstructed downstream payloads.
- `tests/unit/test_unified_retrieval.py` - approved shared regression coverage for deduping sparse basket-promotion item snapshots that only preserve the basket-facing identifier.

Integrator-locked files: none.
Shared-by-approval files: `tests/unit/test_unified_retrieval.py`.

Current source-bearing fixer delta from `669e6933692ef83f76875b64565b1a33a75cff2e`:

- `THREAD_PACKET.md` - authoritative handoff packet refreshed for this pass.
- `src/qual/engine/retrieval/__init__.py` - reject boolean `max_results` values in canonical query construction so loose payloads cannot rely on bool/int coercion.

## Metadata Write Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this fixer pass. Writes to `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are blocked in this worktree by protected `com.apple.provenance` metadata (`Operation not permitted` from both `apply_patch` and direct file writes), so those `.codex` files still contain stale packet metadata and must not be used as the review source of truth. This packet corrects their stale claims by explicitly including the actual source-bearing branch-tip range.

## Diff Evidence

Command: `git diff --stat 378cf9a74a3658058079a32f186fcd254c4a4034..9ca591791ae84e4f86d0b4b3e37b5bffbce09913`

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |   36 +-
 .codex/lane_meta/feat-retrieval-fts.json     |  155 +++-
 THREAD_PACKET.md                             |  236 ++++--
 src/qual/engine/retrieval/__init__.py        |   63 +-
 src/qual/engine/retrieval/fts_strategy.py    |   59 +-
 src/qual/engine/retrieval/payload.py         | 1158 +++++++++++++++++++++++---
 src/qual/retrieval/__init__.py               |   11 +
 src/qual/retrieval/service.py                |  757 +++++++++++++++--
 tests/unit/test_unified_retrieval.py         | 1022 ++++++++++++++++++++++-
 9 files changed, 3147 insertions(+), 350 deletions(-)
```

Command: `git diff --stat 378cf9a74a3658058079a32f186fcd254c4a4034..9ca591791ae84e4f86d0b4b3e37b5bffbce09913 -- src/qual/engine/retrieval src/qual/retrieval tests/unit/test_unified_retrieval.py`

```text
 src/qual/engine/retrieval/__init__.py     |   63 +-
 src/qual/engine/retrieval/fts_strategy.py |   59 +-
 src/qual/engine/retrieval/payload.py      | 1158 ++++++++++++++++++++++++++---
 src/qual/retrieval/__init__.py            |   11 +
 src/qual/retrieval/service.py             |  757 +++++++++++++++++--
 tests/unit/test_unified_retrieval.py      | 1022 ++++++++++++++++++++++++-
 6 files changed, 2819 insertions(+), 251 deletions(-)
```

Command: `git diff --name-status 378cf9a74a3658058079a32f186fcd254c4a4034..9ca591791ae84e4f86d0b4b3e37b5bffbce09913`

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

Command: `git show --stat 2114d026ad9bd68cea6fb63a538771a21d17f816`

```text
 src/qual/engine/retrieval/__init__.py     |  63 +++++++-
 src/qual/engine/retrieval/fts_strategy.py |  21 ++-
 src/qual/engine/retrieval/payload.py      | 274 ++++++++++++++++++++++++++------
 src/qual/retrieval/__init__.py            |  11 ++
 src/qual/retrieval/service.py             | 251 ++++++++++++++++++++++++++---
 tests/unit/test_unified_retrieval.py      | 195 ++++++++++++++++++++++-
 6 files changed, 738 insertions(+), 77 deletions(-)
```

Command: `git diff --stat 669e6933692ef83f76875b64565b1a33a75cff2e -- THREAD_PACKET.md src/qual/engine/retrieval/__init__.py`

```text
 THREAD_PACKET.md                      | 40 ++++++++++++++++++++++++++++-------
 src/qual/engine/retrieval/__init__.py |  2 ++
 2 files changed, 34 insertions(+), 8 deletions(-)
```

Command: `git diff --name-status 669e6933692ef83f76875b64565b1a33a75cff2e -- THREAD_PACKET.md src/qual/engine/retrieval/__init__.py`

```text
M	THREAD_PACKET.md
M	src/qual/engine/retrieval/__init__.py
```

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File count for authoritative branch-tip range: `9 files changed`.
- Size accounting for reviewed source/test files from `378cf9a7`: `2819 insertions(+), 251 deletions(-)`.
- Size accounting for full branch-tip range from `378cf9a7`: `3147 insertions(+), 350 deletions(-)` before the later retrieval facade hardening passes.
- Current source-bearing fixer size accounting from `669e6933`: `2 files changed, 34 insertions(+), 8 deletions(-)` including this packet refresh.
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
- `python - <<'PY' ... build_retrieval_query(... constraints={'max_results': True}) ... PY` - passed; raised `TypeError: integer retrieval constraints must be int-like values, not bool`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 146 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke tests, and 146 unit tests.
- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check && ./quality-lint.sh && ./quality-test.sh && ./typecheck-test.sh && make ci && make scope-check` - passed final rerun after the handoff packet refresh.
- `python -m unittest tests.unit.test_unified_retrieval` - passed 77 focused retrieval tests.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_context_bundle_helper_deduplicates_sparse_basket_items` - passed.
- `python -m pytest tests/unit/test_unified_retrieval.py` - blocked because the active Python 3.14 environment has no `pytest` module; the documented shell and unittest gates above passed.

## Risks/Blockers

No implementation blocker is known. The branch-tip review range is now explicit and complete. The remaining approval blocker is procedural: no explicit integrator high-risk size/file-count exception approval is present in this worktree, and the actual reviewed range exceeds the AGENTS high-risk file and LOC limits.
