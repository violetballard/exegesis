## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Branch HEAD before this source-bearing fixer pass: `dfd82ab84`.
- Final HEAD SHA after this source-bearing fixer pass: reported in the final fixer response.
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because this branch edits engine retrieval entrypoints/facades and approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Actual review scope for re-review: narrowed to `378cf9a74a3658058079a32f186fcd254c4a4034..final HEAD reported in the final fixer response`.
- Source/test-bearing implementation range inside that review scope: `378cf9a74a3658058079a32f186fcd254c4a4034..final HEAD reported in the final fixer response`.
- Actual merge-candidate range against current `main`: `9511a016c20f09b43c6e7a571e0a8a49f90ea209..final HEAD reported in the final fixer response`.
- Reviewer-required post-`adfa8cda` source/test-bearing range included in review scope: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..final HEAD reported in the final fixer response`.
- Traceability correction: no source/test-changing commit after `adfa8cda` is classified as metadata-only. Commits including `2114d026ad9bd68cea6fb63a538771a21d17f816`, `9ca591791ae84e4f86d0b4b3e37b5bffbce09913`, `9609b4cc7d53d03668b96117ed4db1bb14f5ea4f`, `340b2b1f445391cf424f9a73bb1b7abc5fa07102`, `e746e57856d91c90b13207365a232401e4a65500`, `5cc7a8c7bc203f089927b9556c2075251c048899`, `4c748b49a7fa631dd338661802cde03fd93091f7`, `e09c3be72e65f399889512a1914f719d670c6da8`, `9dc7ed4f55fbb3d487d47a91171e8255fed29c82`, and `8a3fbcfc5` are implementation commits and are included in the reviewed range above.
- This source-bearing fixer pass changes the engine retrieval facade and root packet metadata only; it does not change tests or introduce any non-FTS retrieval path.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. No integrator-locked files are edited in this handoff.

## Scope Completed

This packet supersedes earlier handoff packets for `codex/feat-retrieval-fts`. Earlier packets were stale because they described narrowed implementation ranges while the branch tip had advanced through source/test-bearing retrieval commits. Re-review must use the actual review scope above and must include every source/test commit after `adfa8cda` through the final HEAD reported in the final fixer response.

The branch implements the FTS-first retrieval MVP path. SQLite FTS remains the deterministic retrieval source of truth. PageIndex and embeddings remain compatibility-only fallback shims that fail closed and are not reintroduced as required retrieval paths. The branch hardens stable retrieval identity by preserving ordered excerpt lookup fingerprints, document and excerpt provenance, sparse context payload snapshots, citations, basket summaries, candidate-resolution snapshots, top-level context query/policy/manifest/summary snapshots, direct excerpt lookup audit identity, section-hint normalization, and fail-closed compatibility behavior.

This source-bearing fixer pass aligns mapping-shaped engine retrieval facade constraints with the canonical `RetrievalConstraints` boundary. Facade callers now reject bool and other non-int `max_results` values instead of coercing text or floats through `int(...)`, keeping engine-facing FTS query construction deterministic before provenance fingerprints and shortlist diagnostics are derived.

The final source-bearing delta before this packet refresh keeps sparse source-bundle diagnostic reconstruction aligned with canonical `max_results` semantics. Boolean values no longer become integer retrieval limits in sparse query snapshots, which prevents rehydrated fingerprints and FTS diagnostic limits from drifting through Python bool/int coercion when downstream engine flows rebuild diagnostics from source bundles.

This final source-bearing fixer pass also adds the canonical top-level `excerpt_text_hash` alias to direct FTS excerpt lookup payloads. That keeps `retrieve_fts_excerpt`/`fetch_excerpt` aligned with retrieval hit, citation, evidence, basket item, and audit surfaces without introducing any non-FTS retrieval path.

This branch-tip source-bearing fixer pass makes basket promotion refs explicitly carry `basket_item_id` wherever canonical retrieval results, evidence, citation bundles, and direct FTS excerpt lookup payloads expose promotion-ready excerpt items. The alias is equal to the excerpt `item_id`, so downstream basket/context flows can consume promotion refs without inferring identity from whichever sparse snapshot shape survived rehydration.

This source-bearing candidate-resolution provenance correction records the normalized query filters inside the FTS candidate-resolution snapshot. Downstream basket/context consumers can now audit which doc type, date, section-hint, exact-match, and citation constraints shaped the candidate set without inferring that context from separate query fields or invoking any non-FTS retrieval path.

This branch-tip source-bearing candidate-resolution identity correction makes the candidate-resolution snapshot self-identifying by adding the canonical query fingerprint, query scope, query intent, max-results filter, and confidentiality profile. Downstream basket/context consumers can now carry the candidate-set provenance independently of the surrounding payload while still proving it belongs to the same FTS-first query snapshot.

The prior source-bearing query-fingerprint correction computes the FTS hit query fingerprint once per FTS row materialization pass and reuses that stable value for every excerpt provenance record in the run. That keeps excerpt evidence aligned to one canonical query snapshot while preserving SQLite FTS as the only active retrieval backend.

The post-`adfa8cda` implementation deltas are explicitly included in review scope. They preserve sparse basket-promotion identity when snapshots retain `basket_item_id`, reject boolean `max_results` values before Python bool/int coercion can affect retrieval limits, reject bool and non-int `max_results` values at the canonical `RetrievalConstraints` boundary, propagate result fingerprints onto document hits, carry document identity fingerprints into excerpt citation/evidence/basket surfaces, and normalize retrieval section hints without requiring non-FTS retrieval paths.

Canonical demo-path step advanced: `retrieve relevant material`. This work makes the `retrieve relevant material` canonical demo-path step more real by making excerpt lookup FTS-only, deterministic, and auditable for downstream basket/workflow use. It also supports `promote or gather context into the basket` because basket-facing summaries preserve auditable FTS lookup identity and candidate-set provenance.

## Tasks Completed

1. Canonical FTS retrieval path: advances `retrieve relevant material` by adding and exporting the canonical retrieval query constructor, `retrieve_auto` helper, FTS-first service behavior through both retrieval facades, and strict facade `max_results` validation aligned with the canonical service dataclass.
2. Stable retrieval provenance: advances `retrieve relevant material` by emitting deterministic document/excerpt hits, citations, basket summaries, candidate-resolution snapshots, primary lookup fingerprints, ordered `excerpt_lookup_fingerprints`, direct excerpt lookup audit identity, document identity fingerprints on excerpt citation/evidence surfaces, normalized section hints, and document-level result fingerprints in manifests, summaries, evidence, audit events, and result fingerprint payloads.
3. Engine payload compatibility: advances `retrieve relevant material` and supports `promote or gather context into the basket` by normalizing sparse retrieval source, summary, manifest, policy, provenance, excerpt identity, ordered identifier lists, context payload snapshots, and reconstructed sparse diagnostics for downstream engine flows, including top-level context bundle query, policy, manifest, summary, citation status fields, bool-safe canonical `max_results` normalization for FTS shortlist sizing, strict facade-side `max_results` validation for new FTS queries, canonical top-level excerpt text hashes on direct FTS excerpt lookup payloads, explicit `basket_item_id` aliases on promotion-ready excerpt refs, and self-identifying query-filter snapshots in candidate-resolution provenance.
4. Shared regression coverage: advances `retrieve relevant material` and supports `promote or gather context into the basket` by extending approved shared retrieval tests for facade exports, payload reconstruction, citation/provenance helpers, FTS-only excerpt backfill, lookup fingerprints, direct excerpt lookup audit identity, context bundle copy safety, bool and non-int constraint rejection, result fingerprint propagation, section-hint normalization, and fail-closed compatibility behavior.

## Files Changed

Actual review scope: `378cf9a74a3658058079a32f186fcd254c4a4034..final HEAD reported in the final fixer response`.

Source/test-bearing implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..final HEAD reported in the final fixer response`.

- `.codex/kickoff_packets/feat-retrieval-fts.md` - lane kickoff metadata corrected during packet refreshes.
- `.codex/lane_meta/feat-retrieval-fts.json` - lane metadata corrected during packet refreshes.
- `THREAD_PACKET.md` - authoritative handoff packet for branch-tip review, refreshed for this source-bearing facade validation correction.
- `src/qual/engine/retrieval/__init__.py` - engine retrieval facade exports and canonical query constraint normalization, including bool and non-int `max_results` rejection and section-hint normalization.
- `src/qual/engine/retrieval/fts_strategy.py` - FTS strategy integration behavior.
- `src/qual/engine/retrieval/payload.py` - deterministic retrieval payload, sparse snapshot normalization, and top-level context bundle reconstruction.
- `src/qual/retrieval/__init__.py` - retrieval facade exports.
- `src/qual/retrieval/service.py` - canonical FTS-first retrieval service, provenance, candidate-resolution citation snapshots, self-identifying candidate query-filter provenance, lookup fingerprint behavior, direct excerpt lookup audit identity, top-level excerpt text hash lookup payloads, context bundle packaging, document-level result fingerprint propagation, document identity propagation, explicit basket item aliases, canonical `max_results` type validation, and per-pass query fingerprint reuse for FTS excerpt provenance.
- `tests/unit/test_unified_retrieval.py` - approved shared-by-approval regression coverage for the retrieval contract, direct excerpt lookup audit identity, context bundle copy safety, bool and non-int constraint rejection, document-hit result fingerprints, document identity propagation, section-hint normalization, and explicit basket item aliases.

Implementation deltas after `adfa8cda` that are explicitly included in review scope:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- The final source-bearing facade validation correction changes `src/qual/engine/retrieval/__init__.py` and `THREAD_PACKET.md`.

Integrator-locked files: none.
Shared-by-approval files: `tests/unit/test_unified_retrieval.py`.

## Diff Evidence

Command: `git diff --stat 378cf9a74a3658058079a32f186fcd254c4a4034..319f72631e085999228d8541cbea3fdd356fb5c9`

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |   36 +-
 .codex/lane_meta/feat-retrieval-fts.json     |  155 +++-
 THREAD_PACKET.md                             |  242 ++++--
 src/qual/engine/retrieval/__init__.py        |   84 +-
 src/qual/engine/retrieval/fts_strategy.py    |   59 +-
 src/qual/engine/retrieval/payload.py         | 1168 +++++++++++++++++++++++---
 src/qual/retrieval/__init__.py               |   11 +
 src/qual/retrieval/service.py                |  807 ++++++++++++++++--
 tests/unit/test_unified_retrieval.py         | 1059 ++++++++++++++++++++++-
 9 files changed, 3274 insertions(+), 347 deletions(-)
```

Command: `git diff --stat 9511a016c20f09b43c6e7a571e0a8a49f90ea209..319f72631e085999228d8541cbea3fdd356fb5c9`

```text
 THREAD_PACKET.md                      | 259 +++++++++++----------
 src/qual/engine/retrieval/__init__.py |  21 +-
 src/qual/engine/retrieval/payload.py  | 409 +++++++++++++++++++++++++++-------
 src/qual/retrieval/service.py         | 264 +++++++++++++++++++---
 tests/unit/test_unified_retrieval.py  | 345 ++++++++++++++++++++++++++++
 5 files changed, 1055 insertions(+), 243 deletions(-)
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

Current source-bearing fixer delta before commit:

- `src/qual/engine/retrieval/__init__.py` - rejects bool and non-int mapping-shaped `max_results` values before constructing canonical FTS retrieval queries.
- `THREAD_PACKET.md` - re-emits the authoritative packet with internally consistent source-bearing scope, file list, budget accounting, and demo-path mapping. The `.codex` packet mirror files remain stale because this sandbox returns `Operation not permitted` when writing under `.codex/`.

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File count for source/test-bearing implementation range: `9 files changed`.
- Size accounting for source/test-bearing implementation range through `319f72631e085999228d8541cbea3fdd356fb5c9`: `3274 insertions(+), 347 deletions(-)`.
- File count for actual merge-candidate retrieval range against current `main`: `5 files changed` before this packet refresh.
- Size accounting for actual merge-candidate retrieval range against current `main` through `319f72631e085999228d8541cbea3fdd356fb5c9`: `1055 insertions(+), 243 deletions(-)` before this packet refresh.
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

- Current source-bearing fixer pass:
- `python - <<'PY' ... build_retrieval_query(...)` - passed; facade rejects bool, string, and float `max_results` values.
- `python -m unittest tests.unit.test_unified_retrieval -q` - passed 78 retrieval tests.
- `make scope-check` - passed as part of `make ci` for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 147 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke tests, and 147 unit tests.

Previous source-bearing verification:
- `make scope-check` - passed as part of `make ci` for branch `codex/feat-retrieval-fts`.
- `python -m pytest tests/unit/test_unified_retrieval.py -q` - failed because the active Python environment has no `pytest` module installed.
- `python -m unittest tests.unit.test_unified_retrieval -q` - passed 78 retrieval tests.
- `python - <<'PY' ... _normalize_query_snapshot(...)` - passed; bool `max_results` values normalize to the default limit `10`, while text `"7"` remains an int-like limit `7`.
- `python -m unittest tests.unit.test_unified_retrieval.TestUnifiedRetrieval... -q` - failed; incorrect test class selector, no tests executed.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_fts_excerpt_returns_canonical_fts_payload tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_fts_excerpt_lookup_fingerprint_is_stable tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_fts_excerpt_audit_records_stable_lookup_identity -q` - passed 3 direct FTS excerpt lookup tests.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_downstream_payload_exposes_policy_and_diagnostics_snapshot tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_fts_excerpt_returns_canonical_fts_payload tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_auto_citation_bundle_matches_result_snapshot -q` - initially failed because `citation_bundle()` exposed basket item IDs/fingerprints but not full `basket_promotion_items`; passed after the citation bundle was aligned with canonical promotion refs.
- `python -m unittest tests.unit.test_unified_retrieval -q` - passed 78 retrieval tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 147 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke tests, and 147 unit tests.

## Metadata Write Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this fixer pass. This root packet corrects stale claims by explicitly choosing the review scope `378cf9a74a3658058079a32f186fcd254c4a4034..final HEAD reported in the final fixer response`, listing every changed implementation/test/metadata file in that scope, and including all source/test-bearing commits through the final HEAD reported in the final fixer response.

## Risks/Blockers

No implementation blocker is known. The branch-tip review range is now explicit and complete in `THREAD_PACKET.md`. The `.codex` packet mirror files could not be updated in this sandbox because writes under `.codex/` fail with `Operation not permitted`; use `THREAD_PACKET.md` as the authoritative regenerated handoff packet. The remaining approval blockers are procedural: no explicit integrator high-risk size/file-count exception approval is present in this worktree, and the actual reviewed range exceeds the AGENTS high-risk file and LOC limits.
