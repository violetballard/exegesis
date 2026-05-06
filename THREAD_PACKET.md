## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Reviewed implementation head: `6b2dca35224887b913d27a95bed144743669c6cc`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..6b2dca35224887b913d27a95bed144743669c6cc`
- Packet refresh note: this packet intentionally regenerates the merge-candidate range around the actual source-bearing branch tip. Re-review should inspect the full range above, including `cdcad7ffd7b6a048c0603a8db712a028bbc2b9e5` and `6b2dca35224887b913d27a95bed144743669c6cc`; the final fixer commit created from this packet refresh is packet-only and its SHA is reported in the fixer response.
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because the full range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py` plus packet-planner metadata support.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` are included because earlier packet traceability fixes changed the handoff tooling/tests that generated this lane packet.

## Scope Completed

The regenerated handoff covers every retrieval source/test change through `6b2dca35224887b913d27a95bed144743669c6cc`, including the reviewer-cited source-bearing `cdcad7ffd7b6a048c0603a8db712a028bbc2b9e5` context-bundle source identity backfill. The complete range ships an FTS-first retrieval MVP: SQLite FTS stays authoritative, PageIndex and embeddings remain deferred compatibility shims, retrieval query construction and `retrieve_auto` are exported through both retrieval facades, and payload/provenance snapshots are deterministic for downstream engine flows.

The complete range also hardens basket/workflow promotion evidence. It preserves canonical source bundles, context bundles, basket refs, excerpt lookup fingerprints, date ranges, doc scopes, and doc-hit top-excerpt lookup fingerprints through canonical retrieval results and engine-side sparse payload reconstruction.

The full branch-tip source range additionally hardens sparse context-bundle reconstruction so rebuilt basket promotion refs preserve source identity, `excerpt_lookup_fingerprint`, basket lookup fingerprints, and doc-hit top-excerpt lookup fingerprints before later engine steps promote context into basket/workflow state.

Canonical demo-path step advanced: `retrieve relevant material` for basket/workflow promotion. The branch makes that step more real by giving downstream engine and basket flows deterministic FTS doc/excerpt evidence, lookup fingerprints, and promotion-ready refs instead of ambiguous PageIndex or embedding fallbacks.

## Tasks Completed

1. Made FTS the authoritative retrieval path, kept PageIndex/embeddings as fail-closed compatibility shims, and exported the canonical query builder, `retrieve_auto`, excerpt lookup helpers, and retrieval facades through engine and package surfaces.
2. Canonicalized retrieval payload reconstruction for sparse source/context bundles, query constraints, date ranges, doc scopes, basket refs, source-bundle identity backfill, lookup-fingerprint preservation, and policy/provenance snapshots.
3. Propagated deterministic excerpt/doc lookup fingerprints, basket promotion refs, doc citation/evidence fields, summary/manifest snapshots, and result fingerprint inputs.
4. Added and expanded approved shared regression coverage for the canonical retrieval contract, FTS-only excerpt backfills, sparse payload rehydration, facade exports, and packet-planner handoff traceability.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md` - regenerated lane kickoff metadata for the full code-bearing range.
- `.codex/lane_meta/feat-retrieval-fts.json` - regenerated machine-readable lane metadata for the full code-bearing range.
- `THREAD_PACKET.md` - regenerated handoff packet for the full code-bearing range.
- `codex_packet_handoff/tools/planner.py` - packet planner support for reviewed implementation range/head metadata.
- `src/qual/engine/retrieval/__init__.py` - engine retrieval facade exports and canonical helper surface.
- `src/qual/engine/retrieval/embeddings_strategy.py` - deferred/fail-closed embeddings compatibility shim.
- `src/qual/engine/retrieval/fts_strategy.py` - FTS cache isolation and scope/query normalization.
- `src/qual/engine/retrieval/pageindex_strategy.py` - deferred/fail-closed PageIndex compatibility shim.
- `src/qual/engine/retrieval/payload.py` - sparse retrieval payload, source/context bundle, basket, policy, query, provenance normalization, lookup-fingerprint preservation, context-bundle source identity backfill, and sparse basket ref lookup fingerprint reconstruction.
- `src/qual/retrieval/__init__.py` - package retrieval facade exports and canonical helper surface.
- `src/qual/retrieval/service.py` - FTS retrieval service, excerpt lookup, evidence, citation, manifest, doc-hit lookup identity, and basket promotion provenance fingerprinting.
- `tests/unit/test_packet_planner.py` - packet traceability metadata tests.
- `tests/unit/test_unified_retrieval.py` - approved shared retrieval regression coverage, including sparse payload/context backfills and basket lookup fingerprint preservation.

Integrator-locked files: none identified in this packet. Shared-by-approval files in the full range: `tests/unit/test_unified_retrieval.py`; packet tooling/test edits are included explicitly in this regenerated range.

## Budget/Risk

- Task budget: `4/4` high-risk task groups. This packet is a regenerated cumulative branch-tip handoff after reviewer traceability feedback; the four groups above account for the full source-bearing range.
- File budget: `13` files changed across the full reviewed range, exceeding the high-risk `<=8 files` checkpoint and requiring re-review against this full packet.
- Net LOC: `3836 insertions(+), 312 deletions(-)` across the full reviewed range, exceeding the high-risk `<=300 net LOC` checkpoint and requiring re-review against this full packet.
- Routing/provider impact: none.
- PageIndex/embeddings impact: compatibility-only shims remain fail-closed and are not active retrieval paths.
- Remaining risk: the full range is large and crosses packet tooling plus approved shared retrieval tests; reviewers should inspect the regenerated full range rather than any stale narrowed subset.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 real workflow loop and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-first context handling and auditable workflow state.
- Canonical demo-path mapping: advances `retrieve relevant material` for basket/workflow promotion by tying doc-level hits, excerpt citations, lookup fingerprints, and basket refs to the canonical FTS retrieval identity.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_context_bundle_helper_rebuilds_sparse_basket_refs_from_excerpt_hits` - passed.
- `python -m unittest tests.unit.test_unified_retrieval` - passed 71 unified retrieval tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke plus 140 unit tests, including unified retrieval and packet planner coverage.
- `./typecheck-test.sh` - passed; compiled Python sources in `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, and quality tests.

## Risks/Blockers

No current blockers. This branch-tip fixer stays in owned retrieval payload/service paths, approved shared retrieval regression coverage, and the `THREAD_PACKET.md` handoff surface. Re-review should inspect `d7fd5d200358287fa42a18d39e2b277463b9b69f..6b2dca35224887b913d27a95bed144743669c6cc` for the cumulative retrieval implementation, including the reviewer-cited `cdcad7ffd7b6a048c0603a8db712a028bbc2b9e5` source change and the later branch-tip basket lookup-fingerprint hardening.
