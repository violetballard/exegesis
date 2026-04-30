## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Merge-base for this re-review: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4`
- Branch tip before this fixer commit: `0aea8aed679b4068f0b288fc434f466278288ee6`
- Final HEAD SHA: reported in this fixer deliverable after commit creation.
- Authoritative reviewed range / merge candidate: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`
- Scope classification: high-risk retrieval work because approved shared regression coverage in `tests/unit/test_unified_retrieval.py` is part of the reviewed range.

## Scope Completed

This packet regenerates the handoff against one merge candidate: the complete branch diff from merge-base `fd2ab6ca65ec2f93d1334c9b7df8512439725be4` through the final fixer commit recorded above. It includes every source, test, and packet metadata change present at that candidate tip; no source or test file is classified as metadata-only.

The stale reviewer ranges `378cf9a74..adfa8cdadd43747ffbcb612e4151e262b13e52ca`, `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`, and `adfa8cdadd43747ffbcb612e4151e262b13e52ca..3753d4baf4f9f98eb58615fc0e7f45be9ffdf24a` are not used for this re-review. The current merge candidate is `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`; work outside that range is intentionally excluded because `fd2ab6ca65ec2f93d1334c9b7df8512439725be4` is the merge-base with current `main`.

The merge candidate advances FTS-first retrieval by normalizing engine retrieval boolean constraints and required query text/scope snapshots, keeping FTS cache and query snapshots deterministic, carrying date-range constraints into derived FTS shortlist queries, preserving basket-promotion references and provenance, carrying promotion-ready excerpt text/title hints and query context into retrieval evidence fallbacks, invalidating stale FTS cache state on document updates, and falling back from invalid direct context snapshots to canonical source/payload reconstruction.

## Tasks Completed

1. `retrieve relevant material`: normalize engine facade query constraints, boolean flags, date ranges, doc types, required query text/scope snapshots, derived FTS shortlist snapshots, and cache keys so repeated FTS retrieval is deterministic.
2. `retrieve relevant material`: keep SQLite FTS authoritative for excerpt lookup, reject non-FTS excerpt normalization, preserve ranked IDs, document identities, confidentiality profiles, section hints, and excerpt provenance.
3. `retrieve relevant material`; supports `promote or gather context into the basket`: preserve basket-promotion refs, item IDs, citation refs, provenance fingerprints, source/context bundles, excerpt text, title hints, and query context during sparse payload and context-bundle reconstruction so retrieved material stays stable for downstream basket gathering.
4. `retrieve relevant material`; supports `promote or gather context into the basket`: harden cache invalidation and fallback reconstruction for document updates, sparse direct context snapshots, and generic context-bundle helpers while keeping PageIndex and embeddings fallback-only.

## Canonical Demo Path

- Primary step made more real: `retrieve relevant material`.
- Secondary step made more real: `promote or gather context into the basket`, where structured retrieval payloads now carry deterministic excerpt payloads, provenance fingerprints, source/context bundle refs, basket-promotion item refs, item IDs, query context, and citation metadata so downstream workflows can gather the same retrieved material without depending on PageIndex-only or embedding-only paths.

## Files Changed

Complete files-changed list for `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`:

- `src/qual/engine/retrieval/__init__.py` - lane-owned retrieval facade/export behavior via `src/qual/engine/retrieval/**`.
- `src/qual/engine/retrieval/fts_strategy.py` - lane-owned FTS retrieval strategy behavior via `src/qual/engine/retrieval/**`.
- `src/qual/engine/retrieval/payload.py` - lane-owned retrieval payload construction via `src/qual/engine/retrieval/**`.
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
- File budget: `6/8` high-risk files.
- Net LOC budget: source/test implementation changes are `5 files changed, 224 insertions(+), 49 deletions(-)`, or 273 net LOC, which remains within the `<=300` high-risk net LOC limit. Packet metadata accounts for the remaining documentation churn.
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

Required gates re-run on the exact final candidate after this packet correction:

- `python -m pytest tests/unit/test_unified_retrieval.py` BLOCKED because `/opt/homebrew/opt/python@3.14/bin/python3.14` has no `pytest` module installed; switched to repo-supported test commands.
- `python3 -m unittest tests.unit.test_unified_retrieval -v` PASS, 56 tests.
- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, 125 tests.
- `./typecheck-test.sh` PASS.
- `make ci` PASS, 125 tests.

## Risks/Blockers

Remaining risk is review risk from high-risk retrieval scope and approved shared test coverage. The candidate does not widen retrieval strategy scope, does not make PageIndex or embeddings required paths, does not touch model routing/provider configuration, and keeps Textual UI lanes disabled.
