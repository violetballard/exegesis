## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Merge-base for this re-review: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4`
- Branch tip before this fixer commit: `afe3b9d18191a12b8404b74836a6d5c8b9b3b9c0`
- Final merge candidate: this fixer commit on top of `afe3b9d18191a12b8404b74836a6d5c8b9b3b9c0`; final HEAD SHA is reported in the fixer deliverable.
- Accurate reviewed range for the actual merge candidate: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD` after this fixer commit is created.
- Required reviewer correction: the range `adfa8cdadd43747ffbcb612e4151e262b13e52ca..afe3b9d18191a12b8404b74836a6d5c8b9b3b9c0` is included in this handoff and is not classified as metadata-only. That subrange contains source/test changes in `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`.
- Scope classification: high-risk retrieval work because approved shared regression coverage in `tests/unit/test_unified_retrieval.py` remains in the reviewed range.

## Scope Completed

This packet regenerates the handoff against the actual branch tip intended for merge. The reviewed candidate is the complete branch diff from `fd2ab6ca65ec2f93d1334c9b7df8512439725be4` through the final fixer commit, including all implementation, test, and packet metadata changes that are present at the merge candidate tip.

The merge candidate advances FTS-first retrieval by normalizing engine retrieval boolean constraints and required query text/scope snapshots, keeping FTS cache and query snapshots deterministic, preserving basket-promotion references and provenance, invalidating stale FTS cache state on document updates, and falling back from invalid direct context snapshots to canonical source/payload reconstruction.

## Tasks Completed

1. `retrieve relevant material`: normalize engine facade query constraints, boolean flags, date ranges, doc types, required query text/scope snapshots, and cache keys so repeated FTS retrieval is deterministic.
2. `retrieve relevant material`: keep SQLite FTS authoritative for excerpt lookup, reject non-FTS excerpt normalization, preserve ranked IDs, document identities, confidentiality profiles, section hints, and excerpt provenance.
3. `retrieve relevant material`; supports `promote or gather context into the basket`: preserve basket-promotion refs, item IDs, citation refs, provenance fingerprints, and source/context bundles during sparse payload and context-bundle reconstruction so retrieved material stays stable for downstream basket gathering.
4. `retrieve relevant material`; supports `promote or gather context into the basket`: harden cache invalidation and fallback reconstruction for document updates, sparse direct context snapshots, and generic context-bundle helpers while keeping PageIndex and embeddings fallback-only.

## Canonical Demo Path

- Primary step made more real: `retrieve relevant material`.
- Basket/context step made more real: `promote or gather context into the basket`, where structured retrieval payloads now carry deterministic excerpt payloads, provenance fingerprints, source/context bundle refs, basket-promotion item refs, item IDs, and citation metadata so downstream workflows can gather the same retrieved material without depending on PageIndex-only or embedding-only paths.

## Files Changed

Complete files-changed list for `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD` after this fixer commit is created:

- `THREAD_PACKET.md` - authoritative handoff packet required by `INTEGRATION.md`.
- `src/qual/engine/retrieval/__init__.py` - lane-owned retrieval facade/export behavior via `src/qual/engine/retrieval/**`.
- `src/qual/engine/retrieval/fts_strategy.py` - lane-owned FTS retrieval strategy behavior via `src/qual/engine/retrieval/**`.
- `src/qual/engine/retrieval/payload.py` - lane-owned retrieval payload construction via `src/qual/engine/retrieval/**`.
- `src/qual/retrieval/service.py` - lane-owned retrieval service behavior via `src/qual/retrieval/**`.
- `tests/unit/test_unified_retrieval.py` - shared-by-approval regression coverage for the canonical retrieval contract.

The reviewed candidate reports `6 files changed, 270 insertions(+), 116 deletions(-)` from merge-base to the corrected working tree before this fixer commit is created.

Out-of-scope files absent from the actual reviewed candidate range:

- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`

Packet mirror files may contain historical trace notes but are not authoritative for this fixer pass:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`

Treat `THREAD_PACKET.md` as the authoritative corrected handoff packet for this re-review.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- File budget: `6/8` high-risk files.
- Net LOC budget: source/test implementation changes are `5 files changed, 214 insertions(+), 49 deletions(-)` from merge-base to the corrected working tree before this fixer commit is created, within `<=300` high-risk net LOC; packet metadata accounts for the remaining documentation churn.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py` only.
- Integrator-locked files: none.
- Routing/provider impact: none.
- High-risk classification retained because `tests/unit/test_unified_retrieval.py` remains in the reviewed range.
- Approval note: shared regression coverage in `tests/unit/test_unified_retrieval.py` is approved for this lane and applies to the full reviewed range because it exercises the canonical retrieval contract. The packet metadata file is required handoff documentation, not runtime scope.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` MVP focus for FTS-first retrieval and Milestone 3 product-readiness provenance/output-contract work.
- Vision capabilities affected: `PRODUCT_VISION.md` capability 2 Retrieval-first context handling and capability 6 Auditable state and workflow.
- Proposed `README.md` patch text: none.

## Commands Run

Required gates re-run on the exact final candidate after this packet correction:

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, 125 tests.
- `./typecheck-test.sh` PASS.
- `make ci` PASS, 125 tests.

## Risks/Blockers

Remaining risk is review risk from high-risk retrieval scope and approved shared test coverage. The candidate does not widen retrieval strategy scope, does not make PageIndex or embeddings required paths, does not touch model routing/provider configuration, and keeps Textual UI lanes disabled.
