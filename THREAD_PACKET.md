## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Authoritative reviewed range / merge candidate: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`
- Merge-base: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4`
- Candidate classification: high-risk retrieval work, because the candidate changes retrieval behavior and approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.

## Scope Completed

This handoff covers exactly one merge candidate: the complete branch diff from merge-base `fd2ab6ca65ec2f93d1334c9b7df8512439725be4` through `HEAD`.

The candidate advances FTS-first retrieval by normalizing engine retrieval boolean constraints and required query text/scope snapshots, keeping FTS cache and query snapshots deterministic, preserving basket-promotion references and provenance, invalidating stale FTS cache state on document updates, and falling back from invalid direct context snapshots to canonical source/payload reconstruction.

## Tasks Completed

1. `retrieve relevant material`: normalize engine facade query constraints, boolean flags, date ranges, doc types, required query text/scope snapshots, and cache keys so repeated FTS retrieval is deterministic.
2. `retrieve relevant material`: keep SQLite FTS authoritative for excerpt lookup, reject non-FTS excerpt normalization, preserve ranked IDs, document identities, confidentiality profiles, section hints, and excerpt provenance.
3. `retrieve relevant material`; supports `promote or gather context into the basket`: preserve basket-promotion refs, item IDs, citation refs, provenance fingerprints, and source/context bundles during sparse payload and context-bundle reconstruction so retrieved material stays stable for downstream basket gathering.
4. `retrieve relevant material`; supports `promote or gather context into the basket`: harden cache invalidation and fallback reconstruction for document updates, sparse direct context snapshots, and generic context-bundle helpers while keeping PageIndex and embeddings fallback-only.

## Canonical Demo Path

- Primary step made more real: `retrieve relevant material`.
- Secondary step made more real: `promote or gather context into the basket`, because structured retrieval payloads now carry deterministic excerpt payloads, provenance fingerprints, source/context bundle refs, basket-promotion item refs, item IDs, and citation metadata so downstream workflows can gather the same retrieved material without depending on PageIndex-only or embedding-only paths.

## Files Changed

Authoritative files-changed list for `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`:

- `THREAD_PACKET.md` - non-runtime handoff metadata required by `INTEGRATION.md`.
- `src/qual/engine/retrieval/__init__.py` - lane-owned retrieval facade/export behavior via `src/qual/engine/retrieval/**`.
- `src/qual/engine/retrieval/fts_strategy.py` - lane-owned FTS retrieval strategy behavior via `src/qual/engine/retrieval/**`.
- `src/qual/engine/retrieval/payload.py` - lane-owned retrieval payload construction via `src/qual/engine/retrieval/**`.
- `src/qual/retrieval/service.py` - lane-owned retrieval service behavior via `src/qual/retrieval/**`.
- `tests/unit/test_unified_retrieval.py` - shared-by-approval regression coverage for the canonical retrieval contract.

The candidate shortstat is `6 files changed, 263 insertions(+), 118 deletions(-)`.

Files not present in this authoritative candidate range and not part of this handoff:

- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- File budget: `6/8` high-risk files.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py` only.
- Integrator-locked files: none.
- Routing/provider impact: none.
- PageIndex/embeddings impact: fallback-only; neither is reintroduced as a required retrieval path.
- Approval note: shared regression coverage in `tests/unit/test_unified_retrieval.py` is approved for this lane and applies to the full reviewed range because it exercises the canonical retrieval contract. `THREAD_PACKET.md` is handoff documentation, not runtime scope.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` MVP focus for FTS-first retrieval and Milestone 3 product-readiness provenance/output-contract work.
- Vision capabilities affected: `PRODUCT_VISION.md` capability 2 Retrieval-first context handling and capability 6 Auditable state and workflow.
- Proposed `README.md` patch text: none.

## Commands Run

Required gates re-run against the exact candidate `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`:

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS.
- `./typecheck-test.sh` PASS.
- `make ci` PASS.

## Risks/Blockers

Remaining risk is review risk from high-risk retrieval scope and approved shared test coverage. The candidate does not widen retrieval strategy scope, does not make PageIndex or embeddings required paths, does not touch model routing/provider configuration, and keeps Textual UI lanes disabled.
