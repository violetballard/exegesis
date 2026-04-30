## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Merge-base for this re-review: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4`
- Branch tip before this packet-only fixer commit: `7e29e06368fbc9300bc0deaf66e8fe1a6b1da26d`
- Final reviewed commit: the HEAD commit containing this packet-regeneration update; final SHA is reported in the fixer deliverable after commit creation.
- Authoritative reviewed range / complete merge candidate: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`
- Authoritative pre-fixer merge candidate: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..7e29e06368fbc9300bc0deaf66e8fe1a6b1da26d`
- Scope classification: high-risk retrieval work because approved shared regression coverage in `tests/unit/test_unified_retrieval.py` is part of the reviewed range.

## Scope Completed

This packet regenerates the handoff against one merge candidate: the complete branch diff from merge-base `fd2ab6ca65ec2f93d1334c9b7df8512439725be4` through the final packet-only fixer commit recorded above. It includes every source, test, and packet metadata change present at that candidate tip; no source or test file is classified as metadata-only. The pre-fixer merge candidate is `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..7e29e06368fbc9300bc0deaf66e8fe1a6b1da26d`, explicitly including all retrieval implementation changes that landed after the stale `adfa8cdadd43747ffbcb612e4151e262b13e52ca` review anchor. The reviewer-cited non-metadata changes in `adfa8cdadd43747ffbcb612e4151e262b13e52ca..7e29e06368fbc9300bc0deaf66e8fe1a6b1da26d` are therefore inside the submitted merge candidate and are not excluded from review. Earlier packet refresh commits that modify runtime or test files, including `a5587120382486c956382fa8cf6741e79c134f46`, `b9eb05813e54c32638b0905b677e403df61b8d16`, and `5a3e75759750676f71e8b23b3d8eeff28dde90e5`, are part of the implementation candidate; they are not treated as metadata-only.

This fixer pass keeps `THREAD_PACKET.md` as the authoritative handoff packet required by `INTEGRATION.md`. The authoritative approval target is the merge-base-to-HEAD candidate, not any historical packet range.

This re-review fixer pass specifically satisfies the required stale-cache fix: `FTSStrategy` no longer stores a one-entry hit cache, `clear_cache` remains only as a mutation hook while retrieval is uncached, and `test_document_update_invalidates_fts_cache` proves that identical queries before and after a document update read the current SQLite FTS index with `cache_used=False` instead of a stale cached hit.

Historical-only ranges from prior packets are not submitted for approval: `378cf9a74..adfa8cdadd43747ffbcb612e4151e262b13e52ca`, `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`, and `adfa8cdadd43747ffbcb612e4151e262b13e52ca..3753d4baf4f9f98eb58615fc0e7f45be9ffdf24a`. They are stale review artifacts only and are not approval targets. The current merge candidate is `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`; the pre-fixer branch-tip candidate is `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..7e29e06368fbc9300bc0deaf66e8fe1a6b1da26d`. Work outside that merge-base-to-HEAD range is intentionally excluded because `fd2ab6ca65ec2f93d1334c9b7df8512439725be4` is the merge-base with current `main`.

This fixer pass adds one retrieval-owned source correction: sparse basket-promotion reconstruction now derives stable basket item IDs from `excerpt_id` when `item_id` is absent, while preserving order and deduplicating repeated references. That keeps sparse source/evidence bundles promotion-ready for downstream basket gathering without depending on PageIndex or embeddings.

The merge candidate advances FTS-first retrieval by normalizing engine retrieval boolean constraints and required query text/scope snapshots, keeping FTS cache and query snapshots deterministic, carrying date-range constraints into derived FTS shortlist queries and basket-promotion refs, preserving basket-promotion references and provenance, carrying promotion-ready excerpt text/title hints and query context into retrieval evidence fallbacks, backfilling sparse provenance from the canonical query snapshot, invalidating stale FTS cache state on document updates, falling back from invalid direct context snapshots to canonical source/payload reconstruction, normalizing reconstructed basket item IDs to stable text IDs for downstream basket gathering, and falling back to excerpt IDs for sparse promotion refs that do not carry item IDs.

## Tasks Completed

1. `retrieve relevant material`: normalize engine facade query constraints, boolean flags, date ranges, doc types, required query text/scope snapshots, and derived FTS shortlist snapshots so repeated FTS retrieval is deterministic without cached hit reuse.
2. `retrieve relevant material`: keep SQLite FTS authoritative for excerpt lookup, reject non-FTS excerpt normalization, preserve ranked IDs, document identities, confidentiality profiles, section hints, and excerpt provenance.
3. `retrieve relevant material`; supports `promote or gather context into the basket`: preserve basket-promotion refs, stable text item IDs, citation refs, provenance fingerprints, source/context bundles, excerpt text, title hints, query context, and date-range context during sparse payload, provenance, and context-bundle reconstruction so retrieved material stays stable for downstream basket gathering, including sparse excerpt promotion refs that omit `item_id`.
4. `retrieve relevant material`; supports `promote or gather context into the basket`: harden cache invalidation and fallback reconstruction for document updates, sparse direct context snapshots, and generic context-bundle helpers while keeping PageIndex and embeddings fallback-only. Identical queries after `add_or_update_document` now retrieve updated FTS material rather than stale cached excerpts.

## Canonical Demo Path

- Primary step made more real: `retrieve relevant material`.
- Secondary step made more real: `promote or gather context into the basket`, where structured retrieval payloads now carry deterministic excerpt payloads, provenance fingerprints, source/context bundle refs, basket-promotion item refs, stable text item IDs, query context, date-range context, and citation metadata so downstream workflows can gather the same retrieved material without depending on PageIndex-only or embedding-only paths.

## Files Changed

Complete files-changed list for `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`:

- `src/qual/engine/retrieval/__init__.py` - lane-owned retrieval facade/export behavior via `src/qual/engine/retrieval/**`.
- `src/qual/engine/retrieval/fts_strategy.py` - lane-owned FTS retrieval strategy behavior via `src/qual/engine/retrieval/**`.
- `src/qual/engine/retrieval/payload.py` - lane-owned retrieval payload construction and sparse basket item ID reconstruction via `src/qual/engine/retrieval/**`.
- `src/qual/retrieval/service.py` - lane-owned retrieval service behavior via `src/qual/retrieval/**`.
- `tests/unit/test_unified_retrieval.py` - shared-by-approval regression coverage for the canonical retrieval contract.
- `THREAD_PACKET.md` - authoritative handoff packet required by `INTEGRATION.md`.

Lane-owned source/test files in the reviewed candidate:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`

Shared-by-approval source/test files in the reviewed candidate:

- `tests/unit/test_unified_retrieval.py`

Integrator-locked files in the reviewed candidate:

- None.

Metadata-only handoff files in the reviewed candidate:

- `THREAD_PACKET.md`

Files absent from the reviewed candidate:

- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- File budget: `5/8` high-risk source/test files plus packet metadata file (`THREAD_PACKET.md`).
- Net LOC budget: source/test implementation changes are `5 files changed, 219 insertions(+), 86 deletions(-)`, or +133 net LOC, which remains within the `<=300` high-risk net LOC limit. Packet metadata accounts for the remaining documentation churn.
- Size exception required: none. The authoritative reviewed implementation range is within the high-risk limits when applying the file and net LOC budgets to source/test implementation files, and metadata-only handoff files are accounted separately.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py` only.
- Integrator-locked files: none.
- Routing/provider impact: none.
- PageIndex/embeddings impact: fallback-only; neither is reintroduced as a required retrieval path.
- Approval note: shared regression coverage in `tests/unit/test_unified_retrieval.py` is approved for this lane and applies to the full reviewed range because it exercises the canonical retrieval contract. `THREAD_PACKET.md` is handoff documentation, not runtime scope.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` MVP focus for FTS-first retrieval and Milestone 3 product-readiness provenance/output-contract work.
- Vision capabilities affected: `PRODUCT_VISION.md` capability 2 Retrieval-first context handling and capability 3 Auditable generation.
- Proposed `README.md` patch text: none.

## Commands Run

This fixer cycle re-submits the same single review target, `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`, with `7e29e06368fbc9300bc0deaf66e8fe1a6b1da26d` as the pre-fixer branch-tip candidate. The packet does not classify any runtime or test commit in that range as metadata-only.

Required gates re-run for the corrected merge candidate:

- `python -m unittest tests.unit.test_unified_retrieval` PASS, 56 tests.
- `make scope-check` PASS for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, 125 tests.
- `./typecheck-test.sh` PASS.
- `make ci` PASS, 125 tests; includes scope-check, format, lint, typecheck, and test gates. Scope-check passed for branch `codex/feat-retrieval-fts`.

## Risks/Blockers

Remaining risk is review risk from high-risk retrieval scope and approved shared test coverage. The candidate does not widen retrieval strategy scope, does not make PageIndex or embeddings required paths, does not touch model routing/provider configuration, and keeps Textual UI lanes disabled.
