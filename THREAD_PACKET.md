## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Previous reviewed source/test implementation head before this packet-only fixer pass: `e09c3be72e65f399889512a1914f719d670c6da8`
- Current branch HEAD before this packet-only fixer pass: `9dc7ed4f55fbb3d487d47a91171e8255fed29c82`.
- Final HEAD SHA after this packet-only fixer commit: reported in the final fixer response.
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because this branch edits engine retrieval entrypoints/facades and approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Authoritative reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..9dc7ed4f55fbb3d487d47a91171e8255fed29c82`.
- Actual merge-candidate range against current `main`: `9511a016c20f09b43c6e7a571e0a8a49f90ea209..9dc7ed4f55fbb3d487d47a91171e8255fed29c82`, plus this packet-only fixer commit through the final HEAD reported in the final fixer response.
- Reviewer-required post-`adfa8cda` source/test-bearing range included in review scope: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..9dc7ed4f55fbb3d487d47a91171e8255fed29c82`.
- Traceability correction: no source/test-changing commit after `adfa8cda` is classified as metadata-only. Commits including `2114d026ad9bd68cea6fb63a538771a21d17f816`, `9ca591791ae84e4f86d0b4b3e37b5bffbce09913`, `9609b4cc7d53d03668b96117ed4db1bb14f5ea4f`, `340b2b1f445391cf424f9a73bb1b7abc5fa07102`, `e746e57856d91c90b13207365a232401e4a65500`, `5cc7a8c7bc203f089927b9556c2075251c048899`, `4c748b49a7fa631dd338661802cde03fd93091f7`, `e09c3be72e65f399889512a1914f719d670c6da8`, and `9dc7ed4f55fbb3d487d47a91171e8255fed29c82` are implementation commits and are included in the reviewed range above.
- This finalization commit updates packet metadata only; it does not change source or tests.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. No integrator-locked files are edited in this handoff.

## Scope Completed

This packet supersedes earlier handoff packets for `codex/feat-retrieval-fts`. Earlier packets were stale because they described narrowed implementation ranges while the branch tip had advanced through source/test-bearing retrieval commits. Re-review must use the actual implementation range above and must include every source/test commit after `adfa8cda` through `9dc7ed4f55fbb3d487d47a91171e8255fed29c82`.

The branch implements the FTS-first retrieval MVP path. SQLite FTS remains the deterministic retrieval source of truth. PageIndex and embeddings remain compatibility-only fallback shims that fail closed and are not reintroduced as required retrieval paths. The branch hardens stable retrieval identity by preserving ordered excerpt lookup fingerprints, document and excerpt provenance, sparse context payload snapshots, citations, basket summaries, candidate-resolution snapshots, top-level context query/policy/manifest/summary snapshots, direct excerpt lookup audit identity, section-hint normalization, and fail-closed compatibility behavior.

The final source-bearing delta before this packet refresh keeps sparse source-bundle diagnostic reconstruction aligned with canonical `max_results` semantics. Boolean values no longer become integer retrieval limits in sparse query snapshots, which prevents rehydrated fingerprints and FTS diagnostic limits from drifting through Python bool/int coercion when downstream engine flows rebuild diagnostics from source bundles.

The post-`adfa8cda` implementation deltas are explicitly included in review scope. They preserve sparse basket-promotion identity when snapshots retain `basket_item_id`, reject boolean `max_results` values before Python bool/int coercion can affect retrieval limits, reject bool and non-int `max_results` values at the canonical `RetrievalConstraints` boundary, propagate result fingerprints onto document hits, carry document identity fingerprints into excerpt citation/evidence/basket surfaces, and normalize retrieval section hints without requiring non-FTS retrieval paths.

Canonical demo-path step advanced: `retrieve relevant material`. The work makes that step more real by constructing deterministic FTS-first queries, returning document and excerpt hits with stable provenance, reconstructing sparse payload snapshots, and exposing ordered excerpt lookup fingerprints alongside excerpt IDs, text hashes, citations, candidate-resolution snapshots, basket item fingerprints, document-level result fingerprints, and normalized section hints. It also supports `promote or gather context into the basket` because basket-facing summaries preserve auditable FTS lookup identity and candidate-set provenance.

## Tasks Completed

1. Canonical FTS retrieval path: added and exported the canonical retrieval query constructor, `retrieve_auto` helper, and FTS-first service behavior through both retrieval facades.
2. Stable retrieval provenance: emitted deterministic document/excerpt hits, citations, basket summaries, candidate-resolution snapshots, primary lookup fingerprints, ordered `excerpt_lookup_fingerprints`, direct excerpt lookup audit identity, document identity fingerprints on excerpt citation/evidence surfaces, normalized section hints, and document-level result fingerprints in manifests, summaries, evidence, audit events, and result fingerprint payloads.
3. Engine payload compatibility: normalized sparse retrieval source, summary, manifest, policy, provenance, excerpt identity, ordered identifier lists, context payload snapshots, and reconstructed sparse diagnostics for downstream engine flows, including top-level context bundle query, policy, manifest, summary, citation status fields, and bool-safe canonical `max_results` normalization for FTS shortlist sizing.
4. Shared regression coverage: extended approved shared retrieval tests for facade exports, payload reconstruction, citation/provenance helpers, FTS-only excerpt backfill, lookup fingerprints, direct excerpt lookup audit identity, context bundle copy safety, bool and non-int constraint rejection, result fingerprint propagation, section-hint normalization, and fail-closed compatibility behavior.

## Files Changed

Authoritative source/test implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..9dc7ed4f55fbb3d487d47a91171e8255fed29c82`.

- `.codex/kickoff_packets/feat-retrieval-fts.md` - lane kickoff metadata corrected during packet refreshes.
- `.codex/lane_meta/feat-retrieval-fts.json` - lane metadata corrected during packet refreshes.
- `THREAD_PACKET.md` - authoritative handoff packet for branch-tip review.
- `src/qual/engine/retrieval/__init__.py` - engine retrieval facade exports and canonical query constraint normalization, including bool `max_results` rejection and section-hint normalization.
- `src/qual/engine/retrieval/fts_strategy.py` - FTS strategy integration behavior.
- `src/qual/engine/retrieval/payload.py` - deterministic retrieval payload, sparse snapshot normalization, and top-level context bundle reconstruction.
- `src/qual/retrieval/__init__.py` - retrieval facade exports.
- `src/qual/retrieval/service.py` - canonical FTS-first retrieval service, provenance, candidate-resolution citation snapshots, lookup fingerprint behavior, direct excerpt lookup audit identity, context bundle packaging, document-level result fingerprint propagation, document identity propagation, and canonical `max_results` type validation.
- `tests/unit/test_unified_retrieval.py` - approved shared-by-approval regression coverage for the retrieval contract, direct excerpt lookup audit identity, context bundle copy safety, bool and non-int constraint rejection, document-hit result fingerprints, document identity propagation, and section-hint normalization.

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

Command: `git diff --stat 378cf9a74a3658058079a32f186fcd254c4a4034..9dc7ed4f55fbb3d487d47a91171e8255fed29c82`

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |   36 +-
 .codex/lane_meta/feat-retrieval-fts.json     |  155 +++-
 THREAD_PACKET.md                             |  218 +++--
 src/qual/engine/retrieval/__init__.py        |   84 +-
 src/qual/engine/retrieval/fts_strategy.py    |   59 +-
 src/qual/engine/retrieval/payload.py         | 1168 +++++++++++++++++++++++---
 src/qual/retrieval/__init__.py               |   11 +
 src/qual/retrieval/service.py                |  781 +++++++++++++++--
 tests/unit/test_unified_retrieval.py         | 1046 ++++++++++++++++++++++-
 9 files changed, 3212 insertions(+), 346 deletions(-)
```

Command: `git diff --stat 9511a016c20f09b43c6e7a571e0a8a49f90ea209..9dc7ed4f55fbb3d487d47a91171e8255fed29c82`

```text
 THREAD_PACKET.md                      | 247 ++++++++++----------
 src/qual/engine/retrieval/__init__.py |  21 +-
 src/qual/engine/retrieval/payload.py  | 409 +++++++++++++++++++++++++++-------
 src/qual/retrieval/service.py         | 232 ++++++++++++++++---
 tests/unit/test_unified_retrieval.py  | 332 ++++++++++++++++++++++++++++
 5 files changed, 996 insertions(+), 245 deletions(-)
```

Command: `git show --stat --name-status --oneline 9609b4cc7d53d03668b96117ed4db1bb14f5ea4f..4c748b49a7fa631dd338661802cde03fd93091f7 -- THREAD_PACKET.md src/qual/engine/retrieval/__init__.py src/qual/retrieval/service.py tests/unit/test_unified_retrieval.py`

```text
4c748b49a Harden retrieval section hint normalization
M	src/qual/engine/retrieval/__init__.py
5cc7a8c7b Propagate retrieval doc identity in excerpt evidence
M	THREAD_PACKET.md
M	src/qual/retrieval/service.py
M	tests/unit/test_unified_retrieval.py
dc4fa25c3 fix(retrieval): restamp fts handoff gate evidence
M	THREAD_PACKET.md
e5a6741bb Finalize retrieval FTS handoff packet
M	THREAD_PACKET.md
e746e5785 Harden retrieval constraint limits
M	src/qual/retrieval/service.py
M	tests/unit/test_unified_retrieval.py
340b2b1f4 Propagate retrieval result fingerprints to doc hits
M	src/qual/retrieval/service.py
M	tests/unit/test_unified_retrieval.py
```

Current packet-only fixer delta before commit:

Command: `git diff --stat`

```text
Packet metadata only; see final fixer response for the committed SHA.
```

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File count for authoritative source/test implementation range: `9 files changed`.
- Size accounting for authoritative source/test implementation range: `3212 insertions(+), 346 deletions(-)`.
- File count for actual merge-candidate retrieval range against current `main`: `5 files changed` before this packet-only fixer commit.
- Size accounting for actual merge-candidate retrieval range against current `main`: `996 insertions(+), 245 deletions(-)` before this packet-only fixer commit.
- AGENTS high-risk file/size status: exceeds `<=8 files` and `<=300 net LOC` in the authoritative review range, and exceeds `<=300 net LOC` in the actual merge-candidate range.
- Integrator exception status: no explicit high-risk size/file-count exception approval is present in this worktree. This packet does not claim high-risk size compliance; re-review must either reject for the missing exception or route to the integrator for explicit exception approval.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only fallback behavior; no active non-FTS retrieval path is introduced.
- Remaining risk: integration approval depends on accepting the documented high-risk size/file-count exception or requesting a split.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred and fail closed.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket` by surfacing stable FTS excerpt lookup identities, direct context-bundle retrieval snapshots, promotion-ready basket references, and document-hit result fingerprints.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check` - passed as part of `make ci` for branch `codex/feat-retrieval-fts`.
- `python -m pytest tests/unit/test_unified_retrieval.py -q` - failed because the active Python environment has no `pytest` module installed.
- `python -m unittest tests.unit.test_unified_retrieval -q` - passed 78 retrieval tests.
- `python - <<'PY' ... _normalize_query_snapshot(...)` - passed; bool `max_results` values normalize to the default limit `10`, while text `"7"` remains an int-like limit `7`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 147 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke tests, and 147 unit tests.

## Metadata Write Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this fixer pass. This root packet corrects stale claims by explicitly including the actual source/test-bearing range through `9dc7ed4f55fbb3d487d47a91171e8255fed29c82`. This final fixer commit is packet metadata only.

## Risks/Blockers

No implementation blocker is known. The branch-tip review range is now explicit and complete in `THREAD_PACKET.md`. The remaining approval blockers are procedural: no explicit integrator high-risk size/file-count exception approval is present in this worktree, and the actual reviewed range exceeds the AGENTS high-risk file and LOC limits.
