# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Review target: final fixer commit reported in the fixer response.
- Pre-fix branch tip: `d8044a993d9d5e766181740acbeb39d2919394e6`
- Corrected reviewed implementation head before this fixer: `d8044a993d9d5e766181740acbeb39d2919394e6`
- Corrected reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..final fixer commit reported in response`
- Post-`adfa8cda` code included in scope: yes.
- Handoff type: high-risk retrieval fixer re-review.

## Scope Goal

Keep the canonical demo-path step tied to `retrieve relevant material` for basket/workflow promotion by preserving the FTS-first retrieval path, deterministic retrieval payloads, and fail-closed compatibility shims without adding PageIndex or embeddings as required runtime paths.

## Scope Completed

This packet is regenerated against the actual merge candidate instead of the stale `adfa8cda` slice. The branch includes the original FTS-only excerpt lookup work plus later retrieval code through `d8044a993`: basket promotion snapshots, provenance/fingerprint normalization, deterministic policy/source/context bundles, and FTS-first lookup payloads in `src/qual/retrieval/service.py` and `src/qual/engine/retrieval/payload.py`. This fixer adds focused basket-promotion regression coverage for deterministic service bundles and payload reconstruction helpers. PageIndex and embeddings remain compatibility-only/deferred paths; they are not required runtime paths for the canonical retrieval flow.

## Canonical Demo-Path Step Advanced

- Step: `retrieve relevant material`
- The actual branch tip supports promotion of retrieved basket/workflow material with stable FTS-backed provenance, source bundles, policy snapshots, and fingerprints. The runtime contract remains FTS-first; PageIndex-only excerpt IDs fail closed under shared regression coverage and PageIndex/embeddings are not promoted to required runtime paths.

## Budget And Ownership

- Risk: `HIGH`
- High-risk reason: the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py` and packet/planner support files outside lane-owned runtime paths.
- Task count: `4`
- Task budget: `4`
- Size accounting for actual merge candidate before final commit: `13 files changed, 2116 insertions(+), 288 deletions(-)` for `d7fd5d200358287fa42a18d39e2b277463b9b69f..working tree`.
- Size limit note: the cumulative branch exceeds the AGENTS size budget (`>12 files` and `>500` net LOC). This packet reports the actual state for re-review instead of falsely narrowing the range.
- Owned runtime paths touched: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Approved shared-by-approval edit: `tests/unit/test_unified_retrieval.py`
- Packet/planner artifacts touched: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, `THREAD_PACKET.md`, `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`
- Integrator-locked files touched: none

## Tasks Completed

1. Made excerpt lookup FTS-first and fail-closed for PageIndex-only excerpt IDs, with shared regression coverage.
2. Exported and stabilized canonical retrieval query/facade behavior for engine retrieval flows while keeping deferred strategies compatibility-only.
3. Normalized retrieval payloads, source/context bundles, citations, provenance, policy snapshots, and sparse lookup reconstruction for deterministic downstream use.
4. Added basket/workflow promotion provenance, snapshots, fingerprints, and focused deterministic reconstruction tests through the actual branch tip so promoted material can be audited as retrieved FTS-backed evidence.

## Complete Files Changed

Actual merge-candidate diff `d7fd5d200358287fa42a18d39e2b277463b9b69f..final fixer commit reported in response`:

```text
.codex/kickoff_packets/feat-retrieval-fts.md
.codex/lane_meta/feat-retrieval-fts.json
THREAD_PACKET.md
codex_packet_handoff/tools/planner.py
src/qual/engine/retrieval/__init__.py
src/qual/engine/retrieval/embeddings_strategy.py
src/qual/engine/retrieval/fts_strategy.py
src/qual/engine/retrieval/pageindex_strategy.py
src/qual/engine/retrieval/payload.py
src/qual/retrieval/__init__.py
src/qual/retrieval/service.py
tests/unit/test_packet_planner.py
tests/unit/test_unified_retrieval.py
```

Post-`adfa8cda` files still included in the current branch tip:

```text
.codex/kickoff_packets/feat-retrieval-fts.md
.codex/lane_meta/feat-retrieval-fts.json
THREAD_PACKET.md
src/qual/engine/retrieval/payload.py
src/qual/retrieval/service.py
tests/unit/test_unified_retrieval.py
```

## Merge-Facing Diff / Stat

Actual candidate stat:

```text
git diff --stat d7fd5d200358287fa42a18d39e2b277463b9b69f
```

Result:

```text
.codex/kickoff_packets/feat-retrieval-fts.md     |  55 +-
.codex/lane_meta/feat-retrieval-fts.json         | 162 ++++-
THREAD_PACKET.md                                 | 223 ++++---
codex_packet_handoff/tools/planner.py            |  49 +-
src/qual/engine/retrieval/__init__.py            |  56 +-
src/qual/engine/retrieval/embeddings_strategy.py |  24 +
src/qual/engine/retrieval/fts_strategy.py        |  57 ++
src/qual/engine/retrieval/pageindex_strategy.py  |  33 +
src/qual/engine/retrieval/payload.py             | 790 ++++++++++++++++++++---
src/qual/retrieval/__init__.py                   |  94 ++-
src/qual/retrieval/service.py                    | 208 ++++--
tests/unit/test_packet_planner.py                |  72 +++
tests/unit/test_unified_retrieval.py             | 581 ++++++++++++++++-
13 files changed, 2116 insertions(+), 288 deletions(-)
```

## Commands Run And Outcomes

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `pytest tests/unit/test_unified_retrieval.py -k "basket_promotion or fetch_excerpt_requires_an_fts_lookup_hit or rejects_pageindex_excerpt_payloads"`: not runnable in this environment (`pytest` not found).
- `python -m pytest tests/unit/test_unified_retrieval.py -k "basket_promotion or fetch_excerpt_requires_an_fts_lookup_hit or rejects_pageindex_excerpt_payloads"`: not runnable in this environment (`No module named pytest`).
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_context_bundle_includes_deterministic_basket_promotion tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_basket_promotion_reconstructs_from_payload_helpers tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_fetch_excerpt_requires_an_fts_lookup_hit tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_service_rejects_pageindex_excerpt_payloads -v`: PASS (`4` focused retrieval tests).
- `./quality-test.sh`: PASS (`126` unit tests plus smoke).
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS.

## Roadmap Items Affected

- `ROADMAP.md`: MVP focus on `feat-retrieval-fts`.
- `ROADMAP.md`: Milestone 3 product readiness item for generation provenance contract and real workflow loop retrieval evidence.

## Vision Capabilities Affected

- `PRODUCT_VISION.md`: retrieval-backed context, FTS-first for the current MVP.
- `PRODUCT_VISION.md`: auditable state and workflow.

## Routing / Provider Impact

None. This handoff does not touch model routing, provider configuration, or core provider entrypoints.

## Metadata-Only Claim Correction

The previous packet’s metadata-only claim for `ed5d0450e236215a6e6f13ce3b2cbeb04cc6a70b` was false. That commit changes retrieval code in `src/qual/engine/retrieval/payload.py` and `src/qual/retrieval/service.py`; it is included in this corrected reviewed range. The final fixer commit is also source/test changing and is included in the reviewed range reported above.

## Risks / Blockers

- Remaining risk: the actual cumulative branch exceeds AGENTS size limits and includes shared regression coverage, so the handoff remains high-risk.
- Scope risk: basket promotion provenance/fingerprint code after `adfa8cda` is included for review instead of being treated as metadata-only or removed.
- Blockers: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` could not be rewritten in this sandbox (`Operation not permitted`), so `THREAD_PACKET.md` is the corrected handoff packet for this fixer pass.
